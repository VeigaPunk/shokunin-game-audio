#!/usr/bin/env python3
"""r87 scout harness — pw-cat/pw-play/pw-midi*/pw-cli binding + remote-sink surface.

Own harness (never imports corpus/fixtures). All legs write under
corpus/live/r87-scout/. Seat-owned objects tagged r87*. Triple-bounded legs.
"""
import json
import math
import os
import re
import signal
import struct
import subprocess
import sys
import tempfile
import threading
import time
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"
GEN = ROOT / "gen"
RECEIPTS = ROOT / "receipts"
for d in (RUNS, GEN, RECEIPTS):
    d.mkdir(parents=True, exist_ok=True)

TAG = "r87"
TONE = GEN / "tone.wav"
SMF = GEN / "r87.mid"
RATE = 48000
PWCLI_WARM_S = 1.4
DUMP_RETRIES = 6


# ---------- primitives ----------

def sh(args, timeout=20, stdin=None, env=None):
    """Bounded run -> dict(rc,out,err,elapsed_ms)."""
    e = dict(os.environ)
    if env:
        e.update(env)
    t0 = time.time()
    try:
        p = subprocess.run(args, capture_output=True, timeout=timeout,
                           stdin=stdin, env=e)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as x:
        rc, out, err = "timeout", x.stdout or b"", x.stderr or b""
    return {"rc": rc, "out": out.decode(errors="replace"),
            "err": err.decode(errors="replace"),
            "elapsed_ms": int((time.time() - t0) * 1000)}


def norm(s):
    """ASLR/pid/id scrub for cross-rep byte stability."""
    s = re.sub(r"0x[0-9a-fA-F]+", "0xPTR", s)
    s = re.sub(r"\bpid\s*[=:]?\s*\d+", "pid=N", s)
    s = re.sub(r"\b\d{5,}\b", "N", s)
    return s


def pw_dump():
    for _ in range(DUMP_RETRIES):
        r = sh(["pw-dump"], timeout=15)
        if r["rc"] == 0 and r["out"].strip():
            try:
                return json.loads(r["out"])
            except json.JSONDecodeError:
                time.sleep(0.2)
    return []


def nodes_by_name(name, dump=None):
    d = dump if dump is not None else pw_dump()
    return [o for o in d if o.get("type") == "PipeWire:Interface:Node"
            and o.get("info", {}).get("props", {}).get("node.name") == name]


def object_by_id(oid, dump=None):
    d = dump if dump is not None else pw_dump()
    for o in d:
        if o.get("id") == oid:
            return o
    return None


def links_for(name):
    """pw-link -l -> {my_port: [peer_ports]} for ports whose owner is node `name`."""
    r = sh(["pw-link", "-l"], timeout=15)
    links = {}
    cur = None
    for line in r["out"].splitlines():
        m = re.match(r"^(\S+)", line)
        if m and not line.startswith((" ", "\t", "|")):
            cur = m.group(1)
            continue
        t = line.strip()
        if t.startswith("|->") or t.startswith("|<-"):
            peer = t[3:].strip()
            if cur and cur.startswith(name + ":"):
                links.setdefault(cur, []).append(peer)
            elif peer.startswith(name + ":"):
                links.setdefault(peer, []).append(cur)
    return links


def all_links_involving(name):
    """All (a->b) link pairs touching node's ports, from pw-link -l."""
    r = sh(["pw-link", "-l"], timeout=15)
    pairs = set()
    cur = None
    for line in r["out"].splitlines():
        if line.startswith((" ", "\t")):
            t = line.strip()
            if t.startswith("|->") and cur:
                b = t[3:].strip()
                if name in cur or name in b:
                    pairs.add((cur, "->", b))
            continue
        cur = line.strip()
    return sorted(pairs)


def port_inventory(dump=None):
    d = dump if dump is not None else pw_dump()
    out = []
    for o in d:
        if o.get("type") == "PipeWire:Interface:Port":
            p = o.get("info", {}).get("props", {})
            out.append({"id": o["id"], "name": p.get("port.name"),
                        "alias": p.get("port.alias"),
                        "direction": p.get("port.direction"),
                        "node_id": str(p.get("node.id"))})
    return out


def spawn(args, env=None, keep_stdout=False):
    e = dict(os.environ)
    if env:
        e.update(env)
    return subprocess.Popen(
        args,
        stdout=subprocess.PIPE if keep_stdout else subprocess.DEVNULL,
        stderr=subprocess.STDOUT if keep_stdout else subprocess.PIPE,
        env=e)


def stop(p, sig=signal.SIGTERM, wait=4):
    if p.poll() is None:
        try:
            p.send_signal(sig)
        except OSError:
            pass
    try:
        rc = p.wait(timeout=wait)
    except subprocess.TimeoutExpired:
        p.kill()
        rc = p.wait(timeout=3)
    err = b""
    if p.stderr:
        try:
            err = p.stderr.read() or b""
        except OSError:
            pass
    return rc, err.decode(errors="replace")


def pw_cli(cmds, wait_s=6.0, warm_s=PWCLI_WARM_S, label=None):
    """Feed commands to pw-cli with warmup + per-cmd pacing; return raw log.

    cmds: list of (pre_sleep_s, command_string). Returns marks: monotonic
    times each command was written (relative to pw-cli spawn)."""
    script = []
    script.append(("sleep", warm_s))
    for pre, c in cmds:
        if pre:
            script.append(("sleep", pre))
        script.append(("cmd", c))
    script.append(("sleep", 0.35))
    script.append(("cmd", "quit"))

    proc = subprocess.Popen(["pw-cli"], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    t0 = time.time()
    marks = []

    def feed():
        try:
            for kind, v in script:
                if kind == "sleep":
                    time.sleep(v)
                else:
                    proc.stdin.write(v.encode() + b"\n")
                    proc.stdin.flush()
                    marks.append({"t": round(time.time() - t0, 3), "cmd": v})
        except (BrokenPipeError, OSError, ValueError):
            pass
        try:
            proc.stdin.close()
        except OSError:
            pass

    chunks = []

    def drain():
        try:
            while True:
                b = proc.stdout.read(65536)
                if not b:
                    return
                chunks.append(b)
        except (OSError, ValueError):
            return

    rd = threading.Thread(target=drain, daemon=True)
    rd.start()
    t = threading.Thread(target=feed, daemon=True)
    t.start()
    feed_total = warm_s + sum(p for p, _ in cmds) + 1.0
    t.join(timeout=feed_total)          # let every command land first
    try:
        rc = proc.wait(timeout=wait_s)  # trailing 'quit' ends the session
    except subprocess.TimeoutExpired:
        proc.kill()
        rc = "timeout"
        proc.wait(timeout=3)
    rd.join(timeout=3)
    out = b"".join(chunks)
    text = out.decode(errors="replace")
    if label:
        (RUNS / (label + ".pwcli")).write_text(text)
    return {"rc": rc, "log": text, "marks": marks}


def pwcli_events(log):
    """Split pw-cli log into command responses vs async events."""
    return {"errors": re.findall(r'Error: "([^"]+)"', log),
            "responses": [l for l in log.splitlines()
                          if l.strip() and not l.startswith(("remote 0", " ", "\t"))]}


def module_idx_of_sink(name):
    r = sh(["pactl", "list", "short", "modules"], timeout=15)
    for line in r["out"].splitlines():
        if "module-null-sink" in line and ("sink_name=" + name) in line:
            return int(line.split()[0])
    return None


def unload_own_sink(name):
    idx = module_idx_of_sink(name)
    if idx is not None:
        return sh(["pactl", "unload-module", str(idx)], timeout=15)
    return {"rc": "no-such", "out": "", "err": "", "elapsed_ms": 0}


def load_own_sink(name, extra=""):
    args = (f"sink_name={name} sink_properties=device.description={name} "
            f"rate={RATE} channels=2 {extra}").split()
    r = sh(["pactl", "load-module", "module-null-sink"] + args, timeout=15)
    idx = None
    if r["rc"] == 0 and r["out"].strip().isdigit():
        idx = int(r["out"].strip())
    time.sleep(0.5)
    return idx


def gen_tone(path=TONE, dur_s=8.0, amp_l=12000, amp_r=9000,
             f_l=1000, f_r=1500, rate=RATE):
    n = int(dur_s * rate)
    w = wave.open(str(path), "wb")
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(rate)
    frames = bytearray()
    for i in range(n):
        frames += struct.pack("<hh",
                              int(amp_l * math.sin(2 * math.pi * f_l * i / rate)),
                              int(amp_r * math.sin(2 * math.pi * f_r * i / rate)))
    w.writeframes(bytes(frames))
    w.close()
    return path


def _vlq(n):
    b = [n & 0x7f]
    n >>= 7
    while n:
        b.append((n & 0x7f) | 0x80)
        n >>= 7
    return bytes(reversed(b))


def gen_smf(path=SMF, hold_ticks=1920, tail_ticks=960):
    """SMF fmt0 480tpq: C4 on, off; E4 on, off. ~4s at 120bpm."""
    trk = b""
    trk += _vlq(0) + b"\xff\x51\x03" + struct.pack(">I", 500000)[1:]
    trk += _vlq(0) + bytes([0x90, 60, 96])
    trk += _vlq(hold_ticks) + bytes([0x80, 60, 0])
    trk += _vlq(tail_ticks) + bytes([0x90, 64, 96])
    trk += _vlq(tail_ticks) + bytes([0x80, 64, 0])
    trk += _vlq(0) + b"\xff\x2f\x00"
    smf = (b"MThd" + struct.pack(">IHHH", 6, 0, 1, 480)
           + b"MTrk" + struct.pack(">I", len(trk)) + trk)
    Path(path).write_bytes(smf)
    return path


def wav_window_rms(path, t0, t1, chan=0):
    w = wave.open(str(path), "rb")
    nch, sw, rate = w.getnchannels(), w.getsampwidth(), w.getframerate()
    a, b = int(t0 * rate), min(int(t1 * rate), w.getnframes())
    w.setpos(a)
    raw = w.readframes(b - a)
    w.close()
    if sw != 2 or not raw:
        return None
    vals = struct.unpack("<%dh" % (len(raw) // 2), raw)
    sel = vals[chan::nch]
    if not sel:
        return None
    return math.sqrt(sum(v * v for v in sel) / len(sel))


# ---------- sections ----------

def s0_inventory():
    d = pw_dump()
    inv = {"time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "unames": sh(["uname", "-r"])["out"].strip(),
           "versions": {t: sh([t, "--version"], timeout=10)["out"].strip().splitlines()
                        for t in ("pw-cat", "pw-cli", "pw-dump")},
           "pactl": sh(["pactl", "--version"], timeout=10)["out"].strip().splitlines()[:2],
           "symlinks": {t: os.path.realpath("/usr/bin/" + t)
                        for t in ("pw-play", "pw-record", "pw-midiplay",
                                  "pw-midirecord", "pw-mididump")},
           "default_sink": sh(["pactl", "get-default-sink"])["out"].strip(),
           "default_source": sh(["pactl", "get-default-source"])["out"].strip(),
           "nodes": [{"id": o["id"],
                      "name": o["info"]["props"].get("node.name"),
                      "class": o["info"]["props"].get("media.class"),
                      "serial": o["info"]["props"].get("object.serial"),
                      "client": o["info"]["props"].get("client.id")}
                     for o in d if o.get("type") == "PipeWire:Interface:Node"],
           "clients": [{"id": o["id"],
                        "app": o["info"]["props"].get("application.name"),
                        "pid": o["info"]["props"].get("application.process.id")}
                       for o in d if o.get("type") == "PipeWire:Interface:Client"],
           "modules_pulse": [l for l in sh(["pactl", "list", "short", "modules"])["out"].splitlines()],
           "native_module_dir": sorted(os.listdir("/usr/lib/pipewire-0.3")),
           "remote_named_objects": [o["id"] for o in d
                                    if "remote" in str(o.get("info", {}).get("name", "")).lower()],
           "avahi": sh(["pgrep", "-a", "avahi-daemon"])["out"].strip().splitlines()}
    json.dump(inv, open(RECEIPTS / "s0-inventory.json", "w"), indent=1)
    return inv


def play_leg(name, args, env=None, observe_s=(0.9, 1.6)):
    """Spawn a playback/mode leg, snapshot links+node, then TERM."""
    p = spawn(args, env=env)
    t0 = time.time()
    snaps = []
    for t in observe_s:
        time.sleep(max(0.0, t - (time.time() - t0)))
        d = pw_dump()
        nds = nodes_by_name(name, d)
        node = nds[0] if nds else None
        ports = []
        if node:
            ports = [{"name": q["name"], "direction": q["direction"]}
                     for q in port_inventory(d) if q["node_id"] == node["id"]]
        snaps.append({"at": round(time.time() - t0, 3),
                      "node_present": node is not None,
                      "state": (node or {}).get("info", {}).get("state"),
                      "media_class": (node or {}).get("info", {}).get("props", {}).get("media.class"),
                      "ports": ports,
                      "links": links_for(name)})
    rc, err = stop(p)
    return {"argv": args, "node_name": name, "rc": rc,
            "stderr": norm(err.strip())[-400:], "snaps": snaps}


def record_leg(name, args, env=None, observe_s=(0.9,)):
    return play_leg(name, args, env=env, observe_s=observe_s)


def s1_target_lattice(sink="r87_ns"):
    res = {}
    defs = sh(["pactl", "get-default-sink"])["out"].strip()
    nid = None
    nds = nodes_by_name(sink)
    if nds:
        p = nds[0]["info"]["props"]
        nid = {"id": nds[0]["id"], "serial": p.get("object.serial")}
    legs = [
        ("p_own", ["pw-play", "-P", f"node.name={TAG}p_own",
                   "--target", sink, str(TONE)], None),
        ("p_cat_flag", ["pw-cat", "--playback", "-P", f"node.name={TAG}p_catflag",
                        "--target", sink, str(TONE)], None),
        ("p_cat_noflag", ["pw-cat", "-P", f"node.name={TAG}p_catnf",
                          "--target", sink, str(TONE)], None),
        ("p_garbage", ["pw-play", "-P", f"node.name={TAG}p_garb",
                       "--target", "r87_no_such_target", str(TONE)], None),
        ("p_prop_beats_flag1", ["pw-play", "-P", f"node.name={TAG}p_pb1",
                                "-P", "target.object=r87_no_such_target",
                                "--target", sink, str(TONE)], None),
        ("p_prop_beats_flag2", ["pw-play", "-P", f"node.name={TAG}p_pb2",
                                "-P", f"target.object={sink}",
                                "--target", "r87_no_such_target", str(TONE)], None),
        ("p_nodetarget", ["pw-play", "-P", f"node.name={TAG}p_nt",
                          "-P", f"node.target={sink}", str(TONE)], None),
        ("p_zero", ["pw-play", "-P", f"node.name={TAG}p_zero",
                    "--target", "0", str(TONE)], None),
        ("p_monitor_suffix", ["pw-play", "-P", f"node.name={TAG}p_mon",
                              "--target", sink + ".monitor", str(TONE)], None),
        ("p_source_name", ["pw-play", "-P", f"node.name={TAG}p_src",
                           "--target",
                           "alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source",
                           str(TONE)], None),
        ("p_capsink_prop", ["pw-play", "-P", f"node.name={TAG}p_cs",
                            "-P", "stream.capture.sink=true",
                            "--target", "r87_no_such_target", str(TONE)], None),
        ("p_env_props", ["pw-play", "-P", f"node.name={TAG}p_env",
                         "--target", "r87_no_such_target", str(TONE)],
                        {"PIPEWIRE_PROPS": "{ target.object = r87_ns }"}),
        ("p_mediarole", ["pw-play", "-P", f"node.name={TAG}p_mr",
                         "--media-role", "Communication",
                         "--target", "r87_no_such_target", str(TONE)], None),
    ]
    if nid:
        legs += [
            ("p_serial", ["pw-play", "-P", f"node.name={TAG}p_ser",
                          "--target", str(nid["serial"]), str(TONE)], None),
            ("p_objid", ["pw-play", "-P", f"node.name={TAG}p_oid",
                         "--target", str(nid["id"]), str(TONE)], None),
        ]
    for leg, args, env in legs:
        names = [a.split("=", 1)[1] for a in args if a.startswith("node.name=")]
        res[leg] = play_leg(names[0] if names else leg, args, env=env)
        res[leg]["default_sink"] = defs
    json.dump(res, open(RECEIPTS / "s1-target-lattice.json", "w"), indent=1)
    return res


def s2_mode_flags(sink="r87_ns"):
    res = {}
    legs = [
        ("m_capture_long", ["pw-cat", "--capture", str(TONE)]),
        ("m_duplex_long", ["pw-cat", "--duplex", str(TONE)]),
        ("m_record_long", ["pw-cat", "--record", "-P", f"node.name={TAG}m_recl",
                           "-P", "stream.capture.sink=true",
                           "--target", sink, "-n", "48000",
                           str(RUNS / "m_recl.wav")]),
        ("m_p_then_r", ["pw-cat", "-p", "-r", "-P", f"node.name={TAG}m_pr",
                        "-P", "stream.capture.sink=true",
                        "--target", sink, "-n", "48000",
                        str(RUNS / "m_pr.wav")]),
        ("m_r_then_p", ["pw-cat", "-r", "-p", "-P", f"node.name={TAG}m_rp",
                        "--target", sink, str(TONE)]),
        ("m_play_argv0_r", ["pw-play", "-r", "-P", f"node.name={TAG}m_playr",
                            "-P", "stream.capture.sink=true",
                            "--target", sink, "-n", "48000",
                            str(RUNS / "m_playr.wav")]),
        ("m_record_argv0_p", ["pw-record", "-p", "-P", f"node.name={TAG}m_recp",
                              "--target", sink, str(TONE)]),
        ("m_cat_midi_flag", ["pw-cat", "-m", "-P", f"node.name={TAG}m_midif",
                             str(SMF)]),
    ]
    for leg, args in legs:
        names = [a.split("=", 1)[1] for a in args
                 if a.startswith("node.name=")]
        nm = names[0] if names else leg
        res[leg] = play_leg(nm, args, observe_s=(0.9,))
    json.dump(res, open(RECEIPTS / "s2-mode-flags.json", "w"), indent=1)
    return res


def s3_cli_mutation(sink="r87_ns"):
    """pw-cli set-param on a live stream node + monitor capture witness."""
    res = {}
    mon = RUNS / "s3_monitor.wav"
    frames = 11 * RATE
    rec_t0 = time.time()
    rp = spawn(["pw-record", "-P", f"node.name={TAG}mon",
                "-P", "stream.capture.sink=true",
                "--target", sink, "-n", str(frames), str(mon)])
    time.sleep(0.8)
    play_t0 = time.time() - rec_t0
    pp = spawn(["pw-play", "-P", f"node.name={TAG}mut",
                "--target", sink, str(TONE)])
    time.sleep(1.0)
    cli_t0 = time.time() - rec_t0
    d = pw_dump()
    nds = nodes_by_name(f"{TAG}mut", d)
    stream_id = nds[0]["id"] if nds else None
    res["stream_node_id"] = stream_id
    cmds = []
    if stream_id is not None:
        # t marks are relative to pw-cli start (~t0+2.2s after play start).
        cmds = [
            (0.0, f"info {stream_id}"),
            (0.4, f"enum-params {stream_id} Props"),
            (0.5, f"set-param {stream_id} Props {{ volume: 0.25 }}"),   # ~t3.1
            (0.9, f"enum-params {stream_id} Props"),
            (0.6, f"set-param {stream_id} Props {{ volume: 1.0 }}"),    # ~t5.0
            (0.9, f"set-param {stream_id} Props {{ mute: true }}"),     # ~t5.9
            (0.9, f"set-param {stream_id} Props {{ mute: false }}"),    # ~t6.8
            (0.7, f"set-param {stream_id} NoSuchType {{ }}"),
            (0.3, f"set-param {stream_id} Props {{ no_such_prop: 3 }}"),
            (0.5, f"enum-params {stream_id} Format"),
            (0.4, f"set-param {stream_id} Format "
                  "{{ mediaType: audio, mediaSubtype: raw, "
                  "format: S16LE, rate: 96000, channels: 2 }}"),
            (0.5, f"enum-params {stream_id} Format"),
            (0.3, f"send-command {stream_id}"),
        ]
    cli = pw_cli(cmds, wait_s=14, label="s3-mutate")
    res["cli"] = pwcli_events(cli["log"])
    res["cli_marks"] = cli["marks"]
    res["record_start"] = rec_t0
    res["play_start"] = play_t0
    res["cli_spawn"] = cli_t0
    rc_p, err_p = stop(pp)
    rc_r, err_r = stop(rp)
    res["play"] = {"rc": rc_p, "stderr": norm(err_p)[-300:]}
    res["record"] = {"rc": rc_r, "stderr": norm(err_r)[-300:],
                     "bytes": mon.stat().st_size if mon.exists() else 0}
    if mon.exists() and mon.stat().st_size > 4096:
        wins = {"silence_head": (0.1, 0.5), "tone_v1": (2.8, 3.2),
                "tone_v025": (4.7, 5.3), "tone_restored": (6.0, 6.5),
                "tone_muted": (7.0, 7.4), "tone_unmuted": (7.9, 8.3),
                "post_format": (9.7, 10.1)}
        res["windows_L"] = {k: wav_window_rms(mon, a, b, 0)
                            for k, (a, b) in wins.items()}
        res["windows_R"] = {k: wav_window_rms(mon, a, b, 1)
                            for k, (a, b) in wins.items()}
    # destroy-own-node leg on a fresh stream
    pp = spawn(["pw-play", "-P", f"node.name={TAG}kst",
                "--target", sink, str(TONE)])
    time.sleep(1.0)
    nds = nodes_by_name(f"{TAG}kst")
    kid = nds[0]["id"] if nds else None
    res["destroy_leg"] = {"node_id": kid}
    if kid is not None:
        cli2 = pw_cli([(0, f"destroy {kid}"), (0.6, f"info {kid}")],
                      wait_s=6, label="s3-destroy")
        res["destroy_leg"]["cli"] = pwcli_events(cli2["log"])
    time.sleep(0.8)
    res["destroy_leg"]["play_rc_after"] = pp.poll()
    res["destroy_leg"]["node_after"] = bool(nodes_by_name(f"{TAG}kst"))
    rc_p2, err_p2 = stop(pp)
    res["destroy_leg"]["play_rc"] = rc_p2
    res["destroy_leg"]["play_stderr"] = norm(err_p2)[-300:]
    # destroy on a module-owned node: pactl-created sink owned by the
    # pulse-server client — destroy by id, watch node + module fate
    kidx = load_own_sink("r87_kill")
    time.sleep(0.5)
    d = pw_dump()
    kn = nodes_by_name("r87_kill", d)
    res["destroy_sink"] = {"module_idx": kidx,
                           "node_id": kn[0]["id"] if kn else None}
    if kn:
        cli3 = pw_cli([(0, f"destroy {kn[0]['id']}"),
                       (0.5, f"info {kn[0]['id']}")], wait_s=6,
                      label="s3-destroy-sink")
        res["destroy_sink"]["cli"] = pwcli_events(cli3["log"])
    time.sleep(0.6)
    res["destroy_sink"]["node_after"] = bool(nodes_by_name("r87_kill"))
    res["destroy_sink"]["module_after"] = module_idx_of_sink("r87_kill")
    unload_own_sink("r87_kill")
    json.dump(res, open(RECEIPTS / "s3-cli-mutation.json", "w"), indent=1)
    return res


def s4_foreign():
    res = {"note": "foreign nodes resolved live; identical-value writes only"}
    d = pw_dump()
    foreign = [o for o in d if o.get("type") == "PipeWire:Interface:Node"
               and o.get("info", {}).get("props", {}).get("node.name", "")
               not in (None,)
               and not str(o["info"]["props"].get("node.name", "")).startswith(TAG)
               and o["info"]["props"].get("media.class") == "Audio/Sink"]
    res["foreign_sinks"] = [{"id": o["id"],
                             "name": o["info"]["props"].get("node.name")}
                            for o in foreign]
    cmds = [(0, "list-remotes")]
    fid = foreign[0]["id"] if foreign else None
    fname = foreign[0]["info"]["props"].get("node.name") if foreign else None
    res["foreign_target"] = {"id": fid, "name": fname}
    if fid is not None:
        cmds += [(0.2, f"info {fid}"),
                 (0.4, f"enum-params {fid} Props"),
                 (0.5, f"enum-params {fid} Format"),
                 (0.5, f"enum-params {fid} PropInfo"),
                 (0.4, f"set-param {fid} Props {{ no_such_prop: 3 }}"),
                 (0.3, f"set-param {fid} BogusType {{ }}")]
    cmds += [(0.3, "info 99999999"),
             (0.3, "enum-params 99999999 Props"),
             (0.3, "set-param 99999999 Props { volume: 0.5 }"),
             (0.3, "create-node nonexistent_factory_x"),
             (0.3, "create-device nonexistent_factory_x"),
             (0.3, 'create-node adapter { node.name = "r87_adp" '
                  'media.class = "Audio/Source/Virtual" }'),
             (0.8, "destroy 99999999"),
             (0.3, "get-permissions 33"),
             (0.3, "get-permissions 99999999")]
    cli = pw_cli(cmds, wait_s=14, label="s4-foreign")
    res["cli"] = pwcli_events(cli["log"])
    (RECEIPTS / "s4-foreign.raw.txt").write_text(cli["log"])
    # identical-value write on the foreign sink (post-enum)
    vol = None
    m = re.search(r"object %d param 2 index 0.*?Props:volume \(65539\).*?\n\s*Float ([0-9.]+)"
                  % fid if fid else r"$^", cli["log"], re.S)
    if m:
        vol = float(m.group(1))
    res["foreign_volume_seen"] = vol
    if fid is not None and vol is not None:
        cli2 = pw_cli([(0, f"set-param {fid} Props {{ volume: {vol} }}"),
                       (0.5, f"enum-params {fid} Props")],
                      wait_s=6, label="s4-foreign-samevalue")
        res["samevalue_write"] = pwcli_events(cli2["log"])
        (RECEIPTS / "s4-foreign-samevalue.raw.txt").write_text(cli2["log"])
    # create-node adapter roundtrip: did r87_adp appear? destroy it.
    adp = nodes_by_name("r87_adp")
    res["created_adapter"] = {"present": bool(adp),
                              "id": adp[0]["id"] if adp else None}
    if adp:
        cli3 = pw_cli([(0, f"destroy {adp[0]['id']}"),
                       (0.4, f"info {adp[0]['id']}")], wait_s=5,
                      label="s4-destroy-own-created")
        res["created_adapter"]["destroy_cli"] = pwcli_events(cli3["log"])
        time.sleep(0.4)
        res["created_adapter"]["present_after"] = bool(nodes_by_name("r87_adp"))
    json.dump(res, open(RECEIPTS / "s4-foreign.json", "w"), indent=1)
    return res


def s5_midi():
    res = {}
    gen_smf()
    # inventory of midi surface
    res["midi_ports"] = [p for p in port_inventory()
                         if p["alias"] and ("idi" in p["alias"])]
    # 1. plain midiplay (no target) — autoconnect where?
    res["m_play_default"] = play_leg(f"{TAG}mp_def",
                                   ["pw-midiplay", "-P",
                                    f"node.name={TAG}mp_def", str(SMF)],
                                   observe_s=(0.8, 1.8))
    # 2. --target variants (name, serial, id, bridge name, bluez, garbage)
    d = pw_dump()
    bridge = nodes_by_name("Midi-Bridge", d)
    bs = bridge[0]["info"]["props"].get("object.serial") if bridge else None
    bid = bridge[0]["id"] if bridge else None
    legs = [("m_t_bridge_name", ["pw-midiplay", "-P", f"node.name={TAG}mp_bn",
                                "--target", "Midi-Bridge", str(SMF)]),
            ("m_t_midi_through", ["pw-midiplay", "-P", f"node.name={TAG}mp_mt",
                                  "--target", "Midi Through", str(SMF)]),
            ("m_t_bluez", ["pw-midiplay", "-P", f"node.name={TAG}mp_bz",
                           "--target", "bluez_midi.server", str(SMF)]),
            ("m_t_garbage", ["pw-midiplay", "-P", f"node.name={TAG}mp_gb",
                             "--target", "r87_no_such", str(SMF)]),
            ("m_t_zero_pin", ["pw-midiplay", "-P", f"node.name={TAG}mp_zp",
                              "--target", "0", str(SMF)]),
            ("m_t_zero_pin_link", ["pw-midiplay", "-P", f"node.name={TAG}mp_zl",
                                   "--target", "0", str(SMF)])]
    if bs:
        legs.append(("m_t_bridge_serial",
                     ["pw-midiplay", "-P", f"node.name={TAG}mp_bs",
                      "--target", str(bs), str(SMF)]))
    if bid:
        legs.append(("m_t_bridge_objid",
                     ["pw-midiplay", "-P", f"node.name={TAG}mp_bi",
                      "--target", str(bid), str(SMF)]))
    for leg, args in legs:
        nm = [a.split("=", 1)[1] for a in args if a.startswith("node.name=")][0]
        res[leg] = play_leg(nm, args, observe_s=(0.8, 1.8))
        if leg == "m_t_zero_pin_link" and res[leg]["snaps"]:
            # manual pin: my midi out port -> bridge's in-direction port.
            # pw-link names are `<node.name>:<port.name>` (may contain spaces).
            d = pw_dump()
            mynode = nodes_by_name(f"{TAG}mp_zl", d)
            brnode = nodes_by_name("Midi-Bridge", d)
            ports = port_inventory(d)
            myp = [p for p in ports if mynode
                   and p["node_id"] == mynode[0]["id"]
                   and p["direction"] == "out"]
            brp = [p for p in ports if brnode
                   and p["node_id"] == brnode[0]["id"]
                   and p["direction"] == "in"]
            res["pin_attempt"] = {"my_port": myp, "bridge_in": brp}
            if myp and brp:
                lk = sh(["pw-link", f"{TAG}mp_zl:{myp[0]['name']}",
                         f"Midi-Bridge:{brp[0]['name']}"], timeout=10)
                res["pin_attempt"]["pwlink_rc"] = lk["rc"]
                res["pin_attempt"]["pwlink_err"] = norm(lk["err"])[-200:]
                time.sleep(0.4)
                res["pin_attempt"]["links_after"] = links_for(f"{TAG}mp_zl")
    # 3. pw-mididump — bare (live-graph node?) and offline FILE parse
    dp = spawn(["pw-mididump"], keep_stdout=True)
    time.sleep(1.2)
    d = pw_dump()
    res["mididump_live"] = {
        "alive_after_1s": dp.poll() is None,
        "nodes": [{"id": o["id"], "props": o["info"]["props"].get("media.class")}
                  for o in d if o.get("type") == "PipeWire:Interface:Node"
                  and "mididump" in str(o["info"]["props"].get("node.name", "")).lower()],
        "ports": [p for p in port_inventory(d)
                  if p["alias"] and "mididump" in str(p["alias"])]}
    rc_dp, err_dp = stop(dp)
    try:
        out_dp = dp.stdout.read().decode(errors="replace") if dp.stdout else ""
    except OSError:
        out_dp = ""
    res["mididump_live"]["rc"] = rc_dp
    res["mididump_live"]["stdout"] = norm(out_dp)[-400:]
    od = sh(["pw-mididump", str(SMF)], timeout=10)
    res["mididump_file"] = {"rc": od["rc"],
                            "stdout_head": norm(od["out"])[:500]}
    # 4. pw-midirecord --target bridge, concurrent aplaymidi injection
    rec = RUNS / "midirec1.mid"
    mp = spawn(["pw-midirecord", "-P", f"node.name={TAG}mr_br",
                "--target", "Midi-Bridge", str(rec)])
    time.sleep(1.0)
    res["midirec_links"] = links_for(f"{TAG}mr_br")
    inj = sh(["aplaymidi", "-p", "14:0", str(SMF)], timeout=15)
    res["aplaymidi"] = {"rc": inj["rc"], "err": norm(inj["err"])[-200:]}
    time.sleep(1.2)
    res["midirec_links2"] = links_for(f"{TAG}mr_br")
    rc_m, err_m = stop(mp)
    res["midirecord_bridge"] = {"rc": rc_m, "stderr": norm(err_m)[-300:],
                                "bytes": rec.stat().st_size if rec.exists() else 0}
    if rec.exists():
        res["midirecord_bridge"]["head"] = rec.read_bytes()[:64].hex()
    # 4b. pw-midirecord --target 0 + manual pin from bridge capture port
    rec_p = RUNS / "midirec_pin.mid"
    mp = spawn(["pw-midirecord", "-P", f"node.name={TAG}mr_pin",
                "--target", "0", str(rec_p)])
    time.sleep(1.0)
    d = pw_dump()
    mnode = nodes_by_name(f"{TAG}mr_pin", d)
    bnode = nodes_by_name("Midi-Bridge", d)
    ports = port_inventory(d)
    myin = [p for p in ports if mnode
            and p["node_id"] == str(mnode[0]["id"])
            and p["direction"] == "in"]
    brout = [p for p in ports if bnode
             and p["node_id"] == str(bnode[0]["id"])
             and p["direction"] == "out"]
    res["midirec_pin"] = {"my_in": myin, "bridge_out": brout}
    if myin and brout:
        lk = sh(["pw-link", f"Midi-Bridge:{brout[0]['name']}",
                 f"{TAG}mr_pin:{myin[0]['name']}"], timeout=10)
        res["midirec_pin"]["pwlink_rc"] = lk["rc"]
        res["midirec_pin"]["pwlink_err"] = norm(lk["err"])[-200:]
        time.sleep(0.4)
        res["midirec_pin"]["links_after"] = links_for(f"{TAG}mr_pin")
        inj2 = sh(["aplaymidi", "-p", "14:0", str(SMF)], timeout=15)
        res["midirec_pin"]["aplaymidi_rc"] = inj2["rc"]
        time.sleep(1.0)
    rc_m2, err_m2 = stop(mp)
    res["midirec_pin"]["rc"] = rc_m2
    res["midirec_pin"]["stderr"] = norm(err_m2)[-300:]
    res["midirec_pin"]["bytes"] = rec_p.stat().st_size if rec_p.exists() else 0
    if rec_p.exists():
        res["midirec_pin"]["head"] = rec_p.read_bytes()[:80].hex()
    # 5. midirecord --target garbage -> class
    rec2 = RUNS / "midirec_g.mid"
    g = sh(["pw-midirecord", "-P", f"node.name={TAG}mr_gb",
            "--target", "r87_no_such", str(rec2)], timeout=8)
    res["midirecord_garbage"] = {"rc": g["rc"], "err": norm(g["err"])[-300:],
                                 "bytes": rec2.stat().st_size if rec2.exists() else None}
    json.dump(res, open(RECEIPTS / "s5-midi.json", "w"), indent=1)
    return res


def s6_remote():
    res = {}
    def trip(cmd, n=3):
        outs = []
        for _ in range(n):
            outs.append(sh(cmd, timeout=15))
        return [{"rc": o["rc"], "out": norm(o["out"])[-240:],
                 "err": norm(o["err"])[-240:]} for o in outs]
    res["pactl_raop_discover"] = trip(["pactl", "load-module", "module-raop-discover"])
    res["pactl_zeroconf_discover"] = trip(["pactl", "load-module", "module-zeroconf-discover"])
    res["pactl_raop_sink"] = trip(["pactl", "load-module", "module-raop-sink"], n=1)
    res["pactl_bogus"] = trip(["pactl", "load-module", "module-totally-bogus-r87"], n=1)
    res["pwcat_remote_bogus"] = trip(
        ["pw-cat", "-R", "r87_no_such_remote", "-p", str(TONE)], n=3)
    res["pwcat_remote_ok"] = trip(
        ["pw-cat", "-R", "pipewire-0", "-p", "--target", "0",
         "-n", "48000", str(TONE)], n=1)
    # env remote via subprocess env
    env = dict(os.environ, PIPEWIRE_REMOTE="r87_no_such_remote")
    o = []
    for _ in range(3):
        o.append(sh(["pw-play", str(TONE)], timeout=15, env=env))
    res["pwplay_env_remote"] = [{"rc": x["rc"], "err": norm(x["err"])[-240:]}
                                for x in o]
    cli = pw_cli([(0, "list-remotes"),
                  (0.3, "load-module libpipewire-module-raop-discover"),
                  (0.5, "load-module libpipewire-module-raop-discover"),
                  (0.5, "load-module libpipewire-module-zeroconf-discover"),
                  (0.5, "load-module libpipewire-module-null-sink"),
                  (0.5, "load-module module-null-sink"),
                  (0.5, "connect r87_no_such_remote"),
                  (0.5, "list-remotes")],
                 wait_s=10, label="s6-remote")
    res["pwcli"] = pwcli_events(cli["log"])
    (RECEIPTS / "s6-remote.raw.txt").write_text(cli["log"])
    json.dump(res, open(RECEIPTS / "s6-remote.json", "w"), indent=1)
    return res


def s7_stability_reps(sink="r87_ns"):
    """fresh-process x3 on the verdict-bearing legs."""
    res = {}
    for i in range(3):
        res[f"p_own_{i}"] = play_leg(f"{TAG}s7_own{i}",
                                     ["pw-play", "-P", f"node.name={TAG}s7_own{i}",
                                      "--target", sink, str(TONE)],
                                     observe_s=(0.9,))
        res[f"p_garbage_{i}"] = play_leg(
            f"{TAG}s7_gb{i}",
            ["pw-play", "-P", f"node.name={TAG}s7_gb{i}",
             "--target", "r87_no_such_target", str(TONE)], observe_s=(0.9,))
    for i in range(3):
        r = sh(["pw-cat", "--capture", str(TONE)], timeout=10)
        res[f"m_capture_{i}"] = {"rc": r["rc"], "err": norm(r["err"])[-200:]}
        r = sh(["pw-cat", "--duplex", str(TONE)], timeout=10)
        res[f"m_duplex_{i}"] = {"rc": r["rc"], "err": norm(r["err"])[-200:]}
    for i in range(3):
        cli = pw_cli([(0, "info 99999999")], wait_s=5, label=f"s7-cold{i}")
        res[f"cli_cold_{i}"] = pwcli_events(cli["log"])
    # cold-start artifact: zero-warmup pw-cli on a live id
    live = nodes_by_name(sink)
    oid = live[0]["id"] if live else 1
    p = subprocess.Popen(["pw-cli"], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, _ = p.communicate(f"info {oid}\nquit\n".encode(), timeout=8)
    res["cli_nowarm"] = {"rc": p.returncode, "id_used": oid,
                         "log": out.decode(errors="replace")[-600:]}
    json.dump(res, open(RECEIPTS / "s7-stability.json", "w"), indent=1)
    return res


def main():
    gen_tone(dur_s=12.0)
    gen_smf()
    inv = s0_inventory()
    out = {"inventory": inv}
    have_sink = bool(nodes_by_name("r87_ns"))
    if not have_sink:
        load_own_sink("r87_ns")
    try:
        out["s1"] = s1_target_lattice()
        out["s2"] = s2_mode_flags()
        out["s3"] = s3_cli_mutation()
        out["s4"] = s4_foreign()
        out["s5"] = s5_midi()
        out["s6"] = s6_remote()
        out["s7"] = s7_stability_reps()
    finally:
        for nm in ("r87_ns", "r87_kill"):
            unload_own_sink(nm)
        d = pw_dump()
        left = [o["info"]["props"].get("node.name")
                for o in d if o.get("type") == "PipeWire:Interface:Node"
                and str(o["info"]["props"].get("node.name", "")).startswith(TAG)]
        out["leftover_nodes"] = left
        json.dump(out, open(RECEIPTS / "summary.json", "w"), indent=1)
    print("done; leftover:", out["leftover_nodes"])


if __name__ == "__main__":
    main()
