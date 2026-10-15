#!/usr/bin/env python3
"""r99-scout harness — native PipeWire RTP transport surface (module-rtp-sink /
module-rtp-source / module-rtp-sap) on a PRIVATE core + private WirePlumber.

Never touches the shared daemons: separate runtime dir => separate socket.
Every object is r99s_*; every module lives in the private core only.

Stages:
  a  census: module/package/man availability (no core)
  b  sink -> python UDP receiver, unicast loopback (packets + content + props)
  c  sink -> multicast on lo (packets) with an enp7s0-joined control receiver
  d  source <- crafted RTP, multicast on lo (capture path)
  d2 native end-to-end: rtp-sink -> rtp-source over multicast on lo
  e  source unicast: source.port=0 (unconnected) vs source.port=P (connected)
  f  refusal/error lattice
  h  packetization lattice (mtu / ptime -> framecount / packet size)
"""
import argparse, json, os, re, shutil, signal, socket, struct, subprocess, sys, time

SEAT = os.path.dirname(os.path.abspath(__file__))  # this file lives in the seat root
RUN = os.path.join(SEAT, "run")
RAW = os.path.join(SEAT, "raw")
REC = os.path.join(SEAT, "receipts")
TONE = os.path.join(SEAT, "scratch", "tone997_s16_48k_st.wav")
CONF = os.path.join(SEAT, "conf", "pw", "r99s-pipewire.conf")
FRAG = os.path.join(SEAT, "conf", "pw", "r99s-pipewire.conf.d", "10-r99s.conf")
ENV = dict(os.environ,
           PIPEWIRE_RUNTIME_DIR=RUN, XDG_RUNTIME_DIR=RUN,
           XDG_CONFIG_HOME=os.path.join(SEAT, "conf", "xdg-config"),
           XDG_STATE_HOME=os.path.join(SEAT, "conf", "xdg-state"),
           XDG_DATA_HOME=os.path.join(SEAT, "conf", "xdg-data"),
           PIPEWIRE_DEBUG="3", WIREPLUMBER_DEBUG="2")
CORE_PID = os.path.join(RUN, "core.pid")
WP_PID = os.path.join(RUN, "wp.pid")


def sh(cmd, timeout=10.0, env=None, stdin=None):
    try:
        p = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True,
                           timeout=timeout, env=env or ENV, input=stdin)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        return "timeout", (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or ""), \
               (e.stderr or b"").decode() if isinstance(e.stderr, bytes) else (e.stderr or "")


def pwcli(lines, timeout=8.0):
    return sh(["pw-cli"], timeout=timeout, stdin="\n".join(lines) + "\nquit\n")


def write_fragment(modules, objects=None):
    os.makedirs(os.path.dirname(FRAG), exist_ok=True)
    body = ["## r99-scout leg fragment (regenerated per leg; modules below are seat-owned)",
            "context.properties = { module.rt = false module.profiler = false module.portal = false }",
            "context.modules = ["]
    for name, args in modules:
        body.append('  { name = %s' % name)
        body.append('    args = %s' % args)
        body.append('  }')
    body.append("]")
    if objects:
        body.append("context.objects = [")
        for o in objects:
            body.append("  " + o)
        body.append("]")
    open(FRAG, "w").write("\n".join(body) + "\n")


NULL_SINK_OBJ = ('{ factory = adapter args = { factory.name = support.null-audio-sink '
                 'node.name = r99s_ns media.class = Audio/Sink object.linger = true '
                 'audio.position = [ FL FR ] } }')


def core_down():
    sh([sys.executable, os.path.join(SEAT, "probes", "killseat.py")], timeout=20)
    for n in ("pipewire-0", "pipewire-0-manager"):
        p = os.path.join(RUN, n)
        if os.path.exists(p):
            try:
                os.remove(p)
            except OSError:
                pass
    time.sleep(0.2)


def core_up(with_wp=True, timeout=15.0):
    core_down()
    time.sleep(0.2)
    open(os.path.join(SEAT, "runs", "core.log"), "w").close()
    env = dict(ENV)
    p = subprocess.Popen(["pipewire", "-c", CONF], env=env,
                         stdout=open(os.path.join(SEAT, "runs", "core.log"), "ab"),
                         stderr=subprocess.STDOUT, start_new_session=True)
    open(CORE_PID, "w").write(str(p.pid))
    t0 = time.time()
    while time.time() - t0 < timeout:
        if p.poll() is not None:
            return False, "core died rc=%s" % p.returncode
        if os.path.exists(os.path.join(RUN, "pipewire-0")):
            rc, out, err = sh(["pw-cli", "info", "0"], timeout=5)
            if rc == 0:
                break
        time.sleep(0.2)
    else:
        return False, "core did not answer"
    if with_wp:
        w = subprocess.Popen(["wireplumber", "-c", "wireplumber.conf", "-p", "main"], env=env,
                             stdout=open(os.path.join(SEAT, "runs", "wp.log"), "ab"),
                             stderr=subprocess.STDOUT, start_new_session=True)
        open(WP_PID, "w").write(str(w.pid))
        t0 = time.time()
        while time.time() - t0 < timeout:
            rc, out, err = sh(["wpctl", "status"], timeout=5)
            if rc == 0:
                return True, "core+wp up"
            time.sleep(0.2)
        return False, "wp did not answer"
    return True, "core up"


def nodes():
    rc, out, err = sh(["pw-dump"], timeout=10)
    if rc != 0:
        return []
    try:
        d = json.loads(out)
    except Exception:
        return []
    res = []
    for o in d:
        if o["type"].endswith("Node"):
            i = o.get("info", {})
            res.append({"id": o["id"], "state": i.get("state"),
                        "n_in": i.get("n-input-ports"), "n_out": i.get("n-output-ports"),
                        "props": i.get("props", {})})
    return res


def node_by_name(name):
    for n in nodes():
        if n["props"].get("node.name") == name:
            return n
    return None


def node_props(name, keys=None):
    n = node_by_name(name)
    if not n:
        return None
    p = n["props"]
    if keys:
        p = {k: v for k, v in p.items() if any(k.startswith(x) for x in keys)}
    return {"id": n["id"], "state": n["state"], "n_in": n["n_in"], "n_out": n["n_out"], "props": p}


def receiver(out, port, seconds, group=None, ifname="lo", maxpkts=20000):
    cmd = [sys.executable, os.path.join(SEAT, "probes", "r99udp.py"), "recv", "--port", str(port),
           "--seconds", str(seconds), "--out", out, "--maxpkts", str(maxpkts)]
    if group:
        cmd += ["--group", group, "--ifname", ifname]
    return subprocess.Popen(cmd, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)


def sender(port, seconds, host="127.0.0.1", from_port=0, count=3000, group=None, ifname="lo",
           freq=997.0, frames=48, ssrc=0x99C0FFEE, ts0=1000000):
    cmd = [sys.executable, os.path.join(SEAT, "probes", "r99udp.py"), "send", "--port", str(port),
           "--seconds", str(seconds), "--host", host, "--count", str(count), "--freq", str(freq),
           "--frames", str(frames), "--ssrc", hex(ssrc), "--ts0", str(ts0)]
    if from_port:
        cmd += ["--from-port", str(from_port)]
    if group:
        cmd += ["--group", group, "--ifname", ifname]
    return subprocess.Popen(cmd, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)


def play(target, seconds=4.0, node_name=None):
    cmd = ["pw-play", TONE]
    if target:
        cmd += ["--target", str(target)]
    if node_name:
        cmd += ["-P", "node.name=%s" % node_name]
    return subprocess.Popen(cmd, env=ENV, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, start_new_session=True)


def record(out_wav, target, seconds=4.0):
    cmd = ["pw-record", "--rate", "48000", "--channels", "2", "--format", "s16", out_wav]
    if target:
        cmd += ["--target", str(target)]
    return subprocess.Popen(cmd, env=ENV, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, start_new_session=True)


def kill(p, grace=0.5):
    if p is None:
        return
    try:
        p.terminate()
        p.wait(timeout=grace)
    except Exception:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except Exception:
            pass


def read_json(path):
    try:
        return json.load(open(path))
    except Exception:
        return None


def wav_analyze(path):
    """own RIFF reader + Goertzel; returns None if the file is missing/short."""
    import array, math
    if not os.path.exists(path) or os.path.getsize(path) < 45:
        return None
    b = open(path, "rb").read()
    if b[:4] != b"RIFF":
        return {"error": "not RIFF", "size": len(b)}
    # find fmt and data chunks
    pos, fmt, data = 12, None, None
    while pos + 8 <= len(b):
        cid, sz = b[pos:pos + 4], struct.unpack("<I", b[pos + 4:pos + 8])[0]
        if cid == b"fmt ":
            fmt = struct.unpack("<HHIIHH", b[pos + 8:pos + 8 + 16])
        elif cid == b"data":
            data = b[pos + 8:pos + 8 + sz]
        pos += 8 + sz + (sz & 1)
    if fmt is None or data is None:
        return {"error": "no fmt/data", "size": len(b)}
    nch = fmt[1]
    a = array.array("h")
    a.frombytes(data[: len(data) - (len(data) % 2)])
    if sys.byteorder == "little":
        pass  # wav s16 is little-endian; array 'h' is native little on x86
    fl = [v / 32768.0 for v in a[0::nch]]
    fr = [v / 32768.0 for v in a[1::nch]] if nch > 1 else fl

    def gso(x, f, sr=48000):
        n = len(x)
        if n == 0:
            return 0.0
        k = int(0.5 + n * f / sr)
        w = 2 * math.pi * k / n
        c, s = math.cos(w), math.sin(w)
        coeff = 2 * c
        q1 = q2 = 0.0
        for v in x:
            q0 = coeff * q1 - q2 + v
            q2, q1 = q1, q0
        return q1 * q1 + q2 * q2 - coeff * q1 * q2
    return {"bytes": len(b), "frames": len(fl), "rate": fmt[2], "channels": nch,
            "peak_l": round(max(abs(v) for v in fl), 6) if fl else 0.0,
            "peak_r": round(max(abs(v) for v in fr), 6) if fr else 0.0,
            "goertzel_L": {str(f): round(gso(fl, f), 1) for f in (440, 997, 2000)},
            "goertzel_R": {str(f): round(gso(fr, f), 1) for f in (440, 997, 2000)}}


def ss_udp(pid):
    rc, out, err = sh(["ss", "-unp"], timeout=6)
    rows = []
    for line in out.splitlines():
        if ("pid=%d," % pid) in line or line.rstrip().endswith("pid=%d" % pid):
            rows.append(" ".join(line.split()))
    return rows


def sink_args(dest_ip="127.0.0.1", dest_port=46100, fmt="S16BE", minp=1, maxp=1, mtu=None,
              ifname=None, loop=None, node="r99s_sink", extra_props="", extra_module=""):
    a = ['{ destination.ip = "%s"' % dest_ip, "destination.port = %d" % dest_port]
    if mtu:
        a.append("net.mtu = %d" % mtu)
    if ifname:
        a.append('local.ifname = "%s"' % ifname)
    if loop is not None:
        a.append("net.loop = %s" % ("true" if loop else "false"))
    a.append("sess.min-ptime = %s" % minp)
    a.append("sess.max-ptime = %s" % maxp)
    a.append('audio.format = "%s"' % fmt)
    a.append("audio.rate = 48000")
    a.append("audio.channels = 2")
    a.append("stream.props = { node.name = \"%s\" media.class = \"Audio/Sink\" node.virtual = false "
             "node.always-process = true %s }" % (node, extra_props))
    if extra_module:
        a.append(extra_module)
    a.append("}")
    return " ".join(a)
    return " ".join(a)


def source_args(src_ip="239.255.42.99", src_port=46101, fmt="S16BE", ifname="lo", node="r99s_src",
                latency=100, extra_props=""):
    a = ['{ source.ip = "%s"' % src_ip, "source.port = %d" % src_port]
    if ifname:
        a.append('local.ifname = "%s"' % ifname)
    a.append("sess.latency.msec = %s" % latency)
    a.append('audio.format = "%s"' % fmt)
    a.append("audio.rate = 48000")
    a.append("audio.channels = 2")
    a.append('stream.props = { node.name = "%s" media.class = "Audio/Source" node.virtual = false %s }'
             % (node, extra_props))
    a.append("}")
    return " ".join(a)


def leg_write(stage, rep, data):
    os.makedirs(os.path.join(RAW, stage), exist_ok=True)
    json.dump(data, open(os.path.join(RAW, stage, "rep%d.json" % rep), "w"), indent=1, default=str)


# ---------------------------------------------------------------- stages

def stage_a():
    """census: what network transport is available on this host, and what is not."""
    r = {}
    rc, out, err = sh("ls /usr/lib/pipewire-0.3/ | grep -E 'rtp|roc|zeroconf|vban|netjack|tunnel|avb|sap' | sort")
    r["native_modules_matching"] = out.split()
    rc, out, err = sh("ls /usr/lib/pipewire-0.3/libpipewire-module-*.so | wc -l")
    r["native_module_count"] = out.strip()
    rc, out, err = sh("pacman -Q pipewire pipewire-audio 2>&1; pacman -Q pipewire-zeroconf roc-toolkit snapcast jack-trip 2>&1")
    r["packages"] = out.strip().splitlines()
    rc, out, err = sh("command -v snapcast snapclient roc-send roc-recv jack-trip 2>&1; echo rc=$?")
    r["absent_tools"] = out.strip().splitlines()
    rc, out, err = sh("man -w pipewire-rtp-sink pipewire-rtp-source pipewire-rtp-sap 2>&1")
    r["man_pages"] = out.strip().splitlines()
    rc, out, err = sh("systemctl is-active avahi-daemon 2>&1; pacman -Q avahi 2>&1")
    r["avahi"] = out.strip().splitlines()
    rc, out, err = sh("file /usr/bin/pipewire-aes67; strings -a /usr/bin/pipewire-aes67 | grep -c PIPEWIRE_INTERNAL")
    r["aes67_wrapper"] = out.strip().splitlines()
    rc, out, err = sh("grep -c 'rtp\\|aes67' /usr/share/pipewire/pipewire.conf /usr/share/pipewire/pipewire-pulse.conf")
    r["shipped_conf_mentions"] = out.strip().splitlines()
    rc, out, err = sh("ls /usr/share/pipewire/*.conf /usr/share/pipewire/*.conf.avail")
    r["shipped_confs"] = out.split()
    rc, out, err = sh("pacman -Ql pipewire-audio | grep -E 'aes67|avb' ")
    r["aes67_avb_files"] = out.strip().splitlines()
    # what does the library advertise for the three modules?
    r["module_strings"] = {}
    for m in ("rtp-sink", "rtp-source", "rtp-sap"):
        rc, out, err = sh("strings -a /usr/lib/pipewire-0.3/libpipewire-module-%s.so | grep -c ''" % m)
        r["module_strings"][m] = out.strip()
    return r


def stage_b(reps=3):
    out = []
    for rep in range(reps):
        write_fragment([("libpipewire-module-rtp-sink", sink_args())])
        ok, msg = core_up()
        if not ok:
            out.append({"rep": rep, "error": msg})
            continue
        rec_out = os.path.join(RAW, "b", "rep%d.recv.json" % rep)
        os.makedirs(os.path.dirname(rec_out), exist_ok=True)
        p_recv = receiver(rec_out, 46100, 3.5)
        time.sleep(0.6)
        p_play = play("r99s_sink", node_name="r99s_play")
        time.sleep(3.6)
        kill(p_play)
        p_recv.wait(timeout=6)
        kill(p_recv)
        core_pid = int(open(CORE_PID).read())
        d = {"rep": rep, "sink_props": node_props("r99s_sink", ["rtp.", "sess.", "net.", "node.", "audio.", "media."]),
             "play_node": node_props("r99s_play", ["node.", "media."]),
             "links": sh("pw-link -l", timeout=6)[1].strip().splitlines(),
             "udp_sockets": ss_udp(core_pid),
             "recv": read_json(rec_out)}
        leg_write("b", rep, d)
        out.append(d)
        core_down()
    return out


def stage_c(reps=3):
    out = []
    for rep in range(reps):
        write_fragment([("libpipewire-module-rtp-sink",
                         sink_args(dest_ip="239.255.42.99", dest_port=46101, ifname="lo", loop=True))])
        ok, msg = core_up()
        if not ok:
            out.append({"rep": rep, "error": msg})
            continue
        os.makedirs(os.path.join(RAW, "c"), exist_ok=True)
        lo_out = os.path.join(RAW, "c", "rep%d.lo.json" % rep)
        en_out = os.path.join(RAW, "c", "rep%d.en.json" % rep)
        p_lo = receiver(lo_out, 46101, 3.0, group="239.255.42.99", ifname="lo")
        p_en = receiver(en_out, 46101, 3.0, group="239.255.42.99", ifname="enp7s0")
        time.sleep(0.5)
        p_play = play("r99s_sink", node_name="r99s_play")
        time.sleep(3.0)
        kill(p_play)
        for p in (p_lo, p_en):
            p.wait(timeout=6)
            kill(p)
        d = {"rep": rep, "sink_props": node_props("r99s_sink", ["rtp.", "node.", "media."]),
             "lo_recv": read_json(lo_out), "enp7s0_recv": read_json(en_out)}
        leg_write("c", rep, d)
        out.append(d)
        core_down()
    return out


def stage_d(reps=3):
    """source <- crafted RTP over multicast-on-lo, recorded with pw-record."""
    out = []
    for rep in range(reps):
        write_fragment([("libpipewire-module-rtp-source", source_args())])
        ok, msg = core_up()
        if not ok:
            out.append({"rep": rep, "error": msg})
            continue
        os.makedirs(os.path.join(RAW, "d"), exist_ok=True)
        wav = os.path.join(RAW, "d", "rep%d.wav" % rep)
        p_rec = record(wav, "r99s_src", seconds=4.5)
        time.sleep(1.2)
        p_send = sender(46101, 2.5, group="239.255.42.99", ifname="lo", count=2500)
        p_send.wait(timeout=8)
        time.sleep(1.0)
        kill(p_rec)
        time.sleep(0.3)
        d = {"rep": rep, "src_props": node_props("r99s_src", ["rtp.", "sess.", "node.", "media.", "audio."]),
             "rec_node": node_props("r99s_record", ["node.", "media."]),
             "links": sh("pw-link -l", timeout=6)[1].strip().splitlines(),
             "send": (p_send.stdout.read().decode().strip() if p_send.stdout else ""),
             "wav": wav_analyze(wav)}
        leg_write("d", rep, d)
        out.append(d)
        core_down()
    return out


def stage_d0(reps=3):
    """crafted RTP with ts0=0 (receiver graph clock starts near 0) — ts-alignment law."""
    out = []
    for rep in range(reps):
        write_fragment([("libpipewire-module-rtp-source", source_args())])
        ok, msg = core_up()
        if not ok:
            out.append({"rep": rep, "error": msg})
            continue
        os.makedirs(os.path.join(RAW, "d0"), exist_ok=True)
        wav = os.path.join(RAW, "d0", "rep%d.wav" % rep)
        p_rec = record(wav, "r99s_src", seconds=4.5)
        time.sleep(1.2)
        p_send = sender(46101, 2.5, group="239.255.42.99", ifname="lo", count=2500, ts0=0)
        p_send.wait(timeout=8)
        time.sleep(1.0)
        kill(p_rec)
        time.sleep(0.3)
        d = {"rep": rep, "src_props": node_props("r99s_src", ["rtp.", "node."]),
             "links": sh("pw-link -l", timeout=6)[1].strip().splitlines(),
             "send": (p_send.stdout.read().decode().strip() if p_send.stdout else ""),
             "wav": wav_analyze(wav)}
        json.dump(d, open(os.path.join(RAW, "d0", "rep%d.json" % rep), "w"), indent=1, default=str)
        out.append(d)
        core_down()
    return out


def stage_d2(reps=3):
    """native end-to-end: rtp-sink (multicast on lo) -> rtp-source (join on lo)."""
    out = []
    for rep in range(reps):
        write_fragment([
            ("libpipewire-module-rtp-sink", sink_args(dest_ip="239.255.42.99", dest_port=46101, ifname="lo", loop=True)),
            ("libpipewire-module-rtp-source", source_args()),
        ])
        ok, msg = core_up()
        if not ok:
            out.append({"rep": rep, "error": msg})
            continue
        os.makedirs(os.path.join(RAW, "d2"), exist_ok=True)
        wav = os.path.join(RAW, "d2", "rep%d.wav" % rep)
        tap = os.path.join(RAW, "d2", "rep%d.tap.json" % rep)
        p_rec = record(wav, "r99s_src", seconds=5.0)
        p_tap = receiver(tap, 46101, 4.5, group="239.255.42.99", ifname="lo")
        time.sleep(1.2)
        p_play = play("r99s_sink", node_name="r99s_play")
        time.sleep(4.0)
        kill(p_play)
        time.sleep(0.5)
        kill(p_rec)
        kill(p_tap)
        d = {"rep": rep, "sink_props": node_props("r99s_sink", ["rtp.", "node."]),
             "src_props": node_props("r99s_src", ["rtp.", "sess.", "node."]),
             "tap": read_json(tap), "wav": wav_analyze(wav)}
        leg_write("d2", rep, d)
        out.append(d)
        core_down()
    return out


def stage_e(reps=3):
    """unicast source: source.port=0 (unconnected socket) vs source.port=P (connected)."""
    out = []
    for arm in ("port0", "portP"):
        for rep in range(reps):
            port = 0 if arm == "port0" else 46102
            write_fragment([("libpipewire-module-rtp-source",
                             source_args(src_ip="127.0.0.1", src_port=port, ifname=None, node="r99s_src",
                                         extra_props='node.always-process = true'))])
            ok, msg = core_up()
            if not ok:
                out.append({"arm": arm, "rep": rep, "error": msg})
                continue
            os.makedirs(os.path.join(RAW, "e"), exist_ok=True)
            wav = os.path.join(RAW, "e", "%s-rep%d.wav" % (arm, rep))
            p_rec = record(wav, "r99s_src", seconds=4.0)
            time.sleep(1.2)
            core_pid = int(open(CORE_PID).read())
            socks = ss_udp(core_pid)
            bound = None
            for s in socks:
                m = re.search(r"0\.0\.0\.0:(\d+)\s+127\.0\.0\.1:(\d+)", s)
                if m:
                    bound = (int(m.group(1)), int(m.group(2)))
            if bound:
                p_send = sender(bound[0], 2.0, count=1500)
                p_send.wait(timeout=6)
                sent = (p_send.stdout.read().decode().strip() if p_send.stdout else "")
            else:
                sent = "no-bound-socket"
            time.sleep(0.8)
            kill(p_rec)
            log = open(os.path.join(SEAT, "runs", "core.log")).read().splitlines()
            witness = [l for l in log if ("sync to timestamp" in l or "resume RTP source" in l or
                                          "unexpected seq" in l or "receiver read" in l or
                                          "expected" in l and "actual" in l)]
            d = {"arm": arm, "rep": rep, "requested_port": port, "udp_sockets": socks,
                 "bound": bound, "send": sent, "src_props": node_props("r99s_src", ["rtp.", "node."]),
                 "recv_witness": witness[-6:], "wav": wav_analyze(wav)}
            leg_write("e", rep if arm == "port0" else 100 + rep, d)
            out.append(d)
            core_down()
    return out


def stage_f(reps=3):
    """refusal / error lattice for the two modules."""
    out = []
    cases = [
        ("bad_dest_ip", [("libpipewire-module-rtp-sink", sink_args(dest_ip="999.1.2.3"))]),
        ("bad_ifname", [("libpipewire-module-rtp-sink", sink_args(ifname="r99s_nosuchif"))]),
        ("bad_format", [("libpipewire-module-rtp-sink", sink_args(fmt="F32LE"))]),
        ("bad_media", [("libpipewire-module-rtp-sink", sink_args(extra_module='sess.media = "r99s_bogus"'))]),
        ("tiny_mtu", [("libpipewire-module-rtp-sink", sink_args(mtu=64))]),
        ("sap_no_ifname", [("libpipewire-module-rtp-sap", '{ sap.ip = "239.255.255.255" sap.port = 9875 }')]),
    ]
    for name, mods in cases:
        for rep in range(reps):
            write_fragment(mods)
            ok, msg = core_up(with_wp=False)
            core_pid = None
            try:
                core_pid = int(open(CORE_PID).read())
            except Exception:
                pass
            d = {"case": name, "rep": rep, "core_up": ok, "msg": msg,
                 "module_globals": [n["props"].get("module.name") for n in nodes()] if ok else [],
                 "node": node_props("r99s_sink", ["rtp.", "node."]) if ok else None,
                 "udp_sockets": ss_udp(core_pid) if core_pid else [],
                 "core_log_tail": open(os.path.join(SEAT, "runs", "core.log")).read().strip().splitlines()[-4:]}
            os.makedirs(os.path.join(RAW, "f"), exist_ok=True)
            leg_write("f", rep, d) if False else None
            json.dump(d, open(os.path.join(RAW, "f", "%s-rep%d.json" % (name, rep)), "w"), indent=1, default=str)
            out.append(d)
            core_down()
    return out


def stage_h(reps=2):
    """packetization lattice: mtu/ptime -> framecount, ptime, packet size."""
    out = []
    variants = [
        ("mtu1280_p1", dict(mtu=1280, minp=1, maxp=1)),
        ("mtu200_p1", dict(mtu=200, minp=1, maxp=1)),
        ("mtu8000_p1", dict(mtu=8000, minp=1, maxp=1)),
        ("mtu1280_pmin2", dict(mtu=1280, minp=2, maxp=20)),
        ("mtu1280_pmin10", dict(mtu=1280, minp=10, maxp=20)),
        ("mtu1280_pmin50", dict(mtu=1280, minp=50, maxp=100)),
    ]
    for name, kw in variants:
        for rep in range(reps):
            write_fragment([("libpipewire-module-rtp-sink", sink_args(dest_port=46103, **kw))])
            ok, msg = core_up()
            if not ok:
                out.append({"case": name, "rep": rep, "error": msg})
                continue
            os.makedirs(os.path.join(RAW, "h"), exist_ok=True)
            rec_out = os.path.join(RAW, "h", "%s-rep%d.json" % (name, rep))
            p_recv = receiver(rec_out, 46103, 2.0)
            time.sleep(0.5)
            p_play = play("r99s_sink", node_name="r99s_play")
            time.sleep(2.0)
            kill(p_play)
            p_recv.wait(timeout=6)
            kill(p_recv)
            d = {"case": name, "rep": rep, "kw": kw, "sink_props": node_props("r99s_sink", ["rtp.", "net.", "node."]),
                 "recv": read_json(rec_out)}
            json.dump(d, open(os.path.join(RAW, "h", "%s-rep%d.meta.json" % (name, rep)), "w"), indent=1, default=str)
            out.append(d)
            core_down()
    return out


STAGES = {"a": stage_a, "b": stage_b, "c": stage_c, "d": stage_d, "d0": stage_d0, "d2": stage_d2,
          "e": stage_e, "f": stage_f, "h": stage_h}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("stage")
    ap.add_argument("--reps", type=int, default=3)
    a = ap.parse_args()
    os.makedirs(REC, exist_ok=True)
    os.makedirs(RAW, exist_ok=True)
    os.makedirs(os.path.join(SEAT, "runs"), exist_ok=True)
    fn = STAGES[a.stage]
    try:
        res = fn(a.reps) if a.stage != "a" else fn()
    finally:
        core_down()
    json.dump(res, open(os.path.join(REC, "stage-%s.json" % a.stage), "w"), indent=1, default=str)
    print("stage %s done: %d legs" % (a.stage, len(res) if isinstance(res, list) else 1))
