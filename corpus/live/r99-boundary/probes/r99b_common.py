#!/usr/bin/env python3
"""r99-boundary shared harness: private core + private WirePlumber, r99b_* only.

Discipline (r95 namespace-blind-sweep precedent):
  * every child is started with start_new_session=True and killed via its own
    pid/pidfile; kills re-verify the marker (r99b_ / our conf path / hog argv)
    before signalling.
  * no `pkill -f`, no sweep by pattern that could match a foreign object.
"""
import array, json, math, os, re, signal, socket, struct, subprocess, sys, time

SEAT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.join(SEAT, "run")
RAW = os.path.join(SEAT, "raw")
REC = os.path.join(SEAT, "receipts")
CONF = os.path.join(SEAT, "conf", "pw", "r99b-pipewire.conf")
FRAG = os.path.join(SEAT, "conf", "pw", "r99b-pipewire.conf.d", "10-r99b.conf")
UDP = os.path.join(SEAT, "probes", "r99b_udp.py")
HOG = os.path.join(SEAT, "probes", "r99b_hog.py")
TONE = os.path.join(SEAT, "scratch", "tone997_s16_48k_st.wav")
CORE_PID = os.path.join(RUN, "core.pid")
WP_PID = os.path.join(RUN, "wp.pid")
ENV = dict(os.environ,
           PIPEWIRE_RUNTIME_DIR=RUN, XDG_RUNTIME_DIR=RUN,
           XDG_CONFIG_HOME=os.path.join(SEAT, "conf", "xdg-config"),
           XDG_STATE_HOME=os.path.join(SEAT, "conf", "xdg-state"),
           XDG_DATA_HOME=os.path.join(SEAT, "conf", "xdg-data"),
           PIPEWIRE_DEBUG="3", WIREPLUMBER_DEBUG="2")
ENV_NO_RT = dict(ENV, PIPEWIRE_RUNTIME_DIR=RUN)

for d in (RUN, RAW, REC, os.path.join(SEAT, "runs"), os.path.join(SEAT, "scratch")):
    os.makedirs(d, exist_ok=True)


# ------------------------------------------------------------------ process
def sh(cmd, timeout=15.0, env=None, stdin=None):
    try:
        p = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True,
                           timeout=timeout, env=env or ENV, input=stdin)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        return "timeout", (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or ""), \
               (e.stderr or b"").decode() if isinstance(e.stderr, bytes) else (e.stderr or "")


def sh_shared(cmd, timeout=15.0, stdin=None):
    """Run against the SHARED core (operator's runtime dir)."""
    env = dict(os.environ, PIPEWIRE_RUNTIME_DIR="/run/user/1000", XDG_RUNTIME_DIR="/run/user/1000")
    return sh(cmd, timeout=timeout, env=env, stdin=stdin)


def pwcli(lines, timeout=20.0, env=None):
    return sh(["pw-cli"], timeout=timeout, env=env or ENV, stdin="\n".join(lines) + "\nquit\n")


def pid_alive(p):
    try:
        os.kill(p, 0)
        return True
    except OSError:
        return False


def proc_cmdline(pid):
    try:
        return open("/proc/%d/cmdline" % pid, "rb").read().replace(b"\0", b" ").decode(errors="replace")
    except OSError:
        return ""


def kill_tree(pid, grace=0.6, marker=None):
    """Kill exactly this pid (and its process group if the marker still matches)."""
    if not pid or not pid_alive(pid):
        return False
    if marker and marker not in proc_cmdline(pid):
        return False  # marker mismatch -> not ours, never signal
    try:
        os.killpg(os.getpgid(pid), signal.SIGTERM)
    except OSError:
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            return False
    t0 = time.time()
    while time.time() - t0 < grace and pid_alive(pid):
        time.sleep(0.05)
    if pid_alive(pid):
        try:
            os.killpg(os.getpgid(pid), signal.SIGKILL)
        except OSError:
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
    return True


def kill(p, grace=0.5):
    if p is None:
        return
    kill_tree(p.pid, grace)


def loadavg():
    try:
        return [float(x) for x in open("/proc/loadavg").read().split()[:3]]
    except OSError:
        return [None, None, None]


def procs_running():
    try:
        for line in open("/proc/stat"):
            if line.startswith("procs_running"):
                return int(line.split()[1])
    except OSError:
        pass
    return None


# ------------------------------------------------------------------ core
def write_fragment(modules=(), extra_props="", objects=None, rate=None, quantum=None):
    os.makedirs(os.path.dirname(FRAG), exist_ok=True)
    props = ["module.rt = false", "module.profiler = false", "module.portal = false"]
    if rate:
        props.append("default.clock.rate = %d" % rate)
    if quantum:
        props.append("default.clock.quantum = %d" % quantum)
    body = ["## r99-boundary leg fragment (regenerated per leg; r99b_* only)",
            "context.properties = { %s }" % " ".join(props + ([extra_props] if extra_props else [])),
            "context.modules = ["]
    for name, args in modules:
        body.append("  { name = %s" % name)
        body.append("    args = %s" % args)
        body.append("  }")
    body.append("]")
    if objects:
        body.append("context.objects = [")
        for o in objects:
            body.append("  " + o)
        body.append("]")
    open(FRAG, "w").write("\n".join(body) + "\n")


def core_down(verbose=False):
    for f in (CORE_PID, WP_PID):
        if os.path.exists(f):
            try:
                pid = int(open(f).read().strip())
            except ValueError:
                pid = 0
            marker = CONF if f == CORE_PID else "wireplumber"
            if pid and kill_tree(pid, marker=marker) and verbose:
                print("killed %s pid=%d" % (os.path.basename(f), pid))
            try:
                os.remove(f)
            except OSError:
                pass
    for n in ("pipewire-0", "pipewire-0-manager"):
        p = os.path.join(RUN, n)
        if os.path.exists(p):
            try:
                os.remove(p)
            except OSError:
                pass
    time.sleep(0.25)


def core_up(with_wp=True, timeout=25.0, extra_env=None):
    core_down()
    time.sleep(0.2)
    open(os.path.join(SEAT, "runs", "core.log"), "w").close()
    env = dict(ENV)
    if extra_env:
        env.update(extra_env)
    p = subprocess.Popen(["pipewire", "-c", CONF], env=env,
                         stdout=open(os.path.join(SEAT, "runs", "core.log"), "ab"),
                         stderr=subprocess.STDOUT, start_new_session=True)
    open(CORE_PID, "w").write(str(p.pid))
    t0 = time.time()
    ok = False
    while time.time() - t0 < timeout:
        if p.poll() is not None:
            return False, "core died rc=%s" % p.returncode
        if os.path.exists(os.path.join(RUN, "pipewire-0")):
            rc, out, err = sh(["pw-cli", "info", "0"], timeout=8)
            if rc == 0:
                ok = True
                break
        time.sleep(0.2)
    if not ok:
        return False, "core did not answer"
    if with_wp:
        w = subprocess.Popen(["wireplumber", "-c", "wireplumber.conf", "-p", "main"], env=env,
                             stdout=open(os.path.join(SEAT, "runs", "wp.log"), "ab"),
                             stderr=subprocess.STDOUT, start_new_session=True)
        open(WP_PID, "w").write(str(w.pid))
        t0 = time.time()
        while time.time() - t0 < timeout:
            rc, out, err = sh(["wpctl", "status"], timeout=8)
            if rc == 0:
                return True, "core+wp up"
            time.sleep(0.2)
        return False, "wp did not answer"
    return True, "core up"


def core_log(lines=0):
    try:
        data = open(os.path.join(SEAT, "runs", "core.log")).read().splitlines()
    except OSError:
        return []
    return data[-lines:] if lines else data


# ------------------------------------------------------------------ graph
def nodes():
    rc, out, err = sh(["pw-dump"], timeout=25)
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


def node_props(name, prefixes=None):
    n = node_by_name(name)
    if not n:
        return None
    p = n["props"]
    if prefixes:
        p = {k: v for k, v in p.items() if any(k.startswith(x) for x in prefixes)}
    return {"id": n["id"], "state": n["state"], "n_in": n["n_in"], "n_out": n["n_out"], "props": p}


def shared_census(marker="r99b"):
    """Read-only census of the SHARED graph for our namespace."""
    rc, out, err = sh_shared(["pw-dump"], timeout=30)
    hits = []
    if rc == 0:
        try:
            for o in json.loads(out):
                p = o.get("info", {}).get("props", {}) or {}
                blob = json.dumps(p)
                if marker in blob:
                    hits.append({"type": o.get("type"), "id": o.get("id"),
                                 "name": p.get("node.name") or p.get("module.name") or p.get("application.name")})
        except Exception:
            pass
    rc2, out2, _ = sh_shared(["ss", "-unp"], timeout=15)
    socks = [l for l in out2.splitlines() if "r99b" in l]
    return {"objects": hits, "sockets_named_r99b": socks}


def ss_udp(pid):
    if not pid:
        return []
    rc, out, err = sh(["ss", "-unp"], timeout=15)
    rows = []
    for line in out.splitlines():
        if ("pid=%d," % pid) in line or line.rstrip().endswith("pid=%d" % pid):
            rows.append(" ".join(line.split()))
    return rows


# ------------------------------------------------------------------ children
def recv_child(out, port, seconds, group=None, ifname="lo", bufsize=65535, maxpkts=200000):
    cmd = [sys.executable, UDP, "recv", "--port", str(port), "--seconds", str(seconds),
           "--out", out, "--bufsize", str(bufsize), "--maxpkts", str(maxpkts)]
    if group:
        cmd += ["--group", group, "--ifname", ifname]
    return subprocess.Popen(cmd, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            start_new_session=True)


def send_child(port, seconds, host="127.0.0.1", group=None, ifname="lo", from_port=0,
               count=3000, frames=48, freq=997.0, ssrc=0x99C0FFEE, ts0=1000000, rate=48000):
    cmd = [sys.executable, UDP, "send", "--port", str(port), "--seconds", str(seconds),
           "--count", str(count), "--freq", str(freq), "--frames", str(frames),
           "--ssrc", hex(ssrc), "--ts0", str(ts0), "--rate", str(rate), "--host", host]
    if group:
        cmd += ["--group", group, "--ifname", ifname]
    if from_port:
        cmd += ["--from-port", str(from_port)]
    return subprocess.Popen(cmd, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            start_new_session=True)


def play(target=None, seconds=None, node_name=None, tone=None, env=None, args_first=True):
    """pw-play; args_first controls flag order (axis AX-ORDER)."""
    cmd = ["pw-play"]
    flags = []
    if target:
        flags += ["--target", str(target)]
    if node_name:
        flags += ["-P", "node.name=%s" % node_name]
    if args_first:
        cmd += flags + [tone or TONE]
    else:
        cmd += [tone or TONE] + flags
    return subprocess.Popen(cmd, env=env or ENV, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                            start_new_session=True)


def record(out_wav, target=None, seconds=5.0, node_name=None):
    cmd = ["pw-record", "--rate", "48000", "--channels", "2", "--format", "s16", out_wav]
    if target:
        cmd += ["--target", str(target)]
    if node_name:
        cmd += ["-P", "node.name=%s" % node_name]
    return subprocess.Popen(cmd, env=ENV, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                            start_new_session=True)


def wav_analyze(path):
    if not os.path.exists(path) or os.path.getsize(path) < 45:
        return None
    b = open(path, "rb").read()
    if b[:4] != b"RIFF":
        return {"error": "not RIFF", "size": len(b)}
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


# ------------------------------------------------------------------ hogs
HOGS = []


def start_hogs(n=14, seconds=1800.0, tag="r99b_hog"):
    """Start n own CPU hogs; returns list of Popen. All argv-marked r99b_hog."""
    for i in range(n):
        p = subprocess.Popen([sys.executable, HOG, str(seconds), "%s%d" % (tag, i)],
                             env=dict(os.environ), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                             start_new_session=True)
        HOGS.append(p)
    for p in HOGS:  # wait for the readiness line
        try:
            p.stdout.readline()
        except Exception:
            pass
    return HOGS


def stop_hogs():
    out = []
    for p in HOGS:
        marker_ok = "r99b_hog" in proc_cmdline(p.pid)
        alive = pid_alive(p.pid)
        killed = kill_tree(p.pid, marker="r99b_hog")
        out.append({"pid": p.pid, "marker_ok": marker_ok, "alive_before": alive, "killed": killed})
    HOGS.clear()
    return out


def hog_census():
    """Read-only census of r99b_hog processes (own namespace only)."""
    hits = []
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        cl = proc_cmdline(int(pid))
        if "r99b_hog.py" in cl:
            hits.append({"pid": int(pid), "cmdline": cl.strip()})
    return hits


# ------------------------------------------------------------------ io
def leg_write(stage, name, rep, data):
    d = os.path.join(RAW, stage)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "%s-rep%d.json" % (name, rep))
    json.dump(data, open(path, "w"), indent=1, default=str)
    return path


def read_json(path):
    try:
        return json.load(open(path))
    except Exception:
        return None


def receipt(name, data):
    os.makedirs(REC, exist_ok=True)
    path = os.path.join(REC, name)
    json.dump(data, open(path, "w"), indent=1, default=str)
    return path
