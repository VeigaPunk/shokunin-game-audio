#!/usr/bin/env python3
"""r87b boundary harness library — primitives (seat-owned).

Falsification seat for round-87 scout claims. Every audio object this seat
creates is named r87b_*. Own code; shape adapted from the r87 scout harness
(same host, same PipeWire 1.6.8). No tracked writes; no imports from
corpus/fixtures. Kill discipline: only pids this seat started are ever
signalled (OWN_PROCS / HOGS registries), never a blind pattern sweep.
"""
import json
import math
import os
import re
import signal
import struct
import subprocess
import threading
import time
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"
GEN = ROOT / "gen"
RECEIPTS = ROOT / "receipts"
for _d in (RUNS, GEN, RECEIPTS):
    _d.mkdir(parents=True, exist_ok=True)

TAG = "r87b"
NS = TAG + "_ns"
NS2 = TAG + "_ns2"
TONE = GEN / "tone.wav"
SMF = GEN / "r87b.mid"
RATE = 48000
PWCLI_WARM_S = 1.4
DUMP_RETRIES = 6

# registry of every process this seat starts (never foreign)
OWN_PROCS = []
HOGS = []


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
    """ASLR/pid/id scrub for cross-rep byte stability (scout-compatible)."""
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


def props_of(o):
    return (o.get("info", {}) or {}).get("props", {}) or {}


def nodes_by_name(name, dump=None):
    d = dump if dump is not None else pw_dump()
    return [o for o in d if o.get("type") == "PipeWire:Interface:Node"
            and props_of(o).get("node.name") == name]


def node_info(name, dump=None):
    nds = nodes_by_name(name, dump)
    if not nds:
        return None
    p = props_of(nds[0])
    return {"id": nds[0]["id"], "serial": p.get("object.serial"),
            "class": p.get("media.class"), "state": (nds[0].get("info", {})
                                                      .get("state")),
            "client": p.get("client.id")}


def all_node_names(dump=None):
    d = dump if dump is not None else pw_dump()
    out = []
    for o in d:
        if o.get("type") == "PipeWire:Interface:Node":
            p = props_of(o)
            out.append({"id": o["id"], "name": p.get("node.name"),
                        "class": p.get("media.class"),
                        "serial": p.get("object.serial"),
                        "client": p.get("client.id")})
    return out


def port_inventory(dump=None):
    d = dump if dump is not None else pw_dump()
    out = []
    for o in d:
        if o.get("type") == "PipeWire:Interface:Port":
            p = props_of(o)
            out.append({"id": o["id"], "name": p.get("port.name"),
                        "alias": p.get("port.alias"),
                        "direction": p.get("port.direction"),
                        "node_id": str(p.get("node.id"))})
    return out


def links_for(name):
    """pw-link -l -> {port: [peer ports]} for ports owned by node `name`.

    One entry per real link (peer lines only; the header line is skipped)."""
    r = sh(["pw-link", "-l"], timeout=15)
    links = {}
    cur = None
    for line in r["out"].splitlines():
        if not line.startswith((" ", "\t")):
            cur = line.strip() or None
            continue
        t = line.strip()
        if t.startswith(("|->", "|<-")):
            peer = t[3:].strip()
            if not cur:
                continue
            if cur.startswith(name + ":"):
                links.setdefault(cur, []).append(peer)
            elif peer.startswith(name + ":"):
                links.setdefault(peer, []).append(cur)
    return links


def link_pairs(name):
    """All (a -> b) link pairs touching node `name`'s ports."""
    r = sh(["pw-link", "-l"], timeout=15)
    pairs = set()
    cur = None
    for line in r["out"].splitlines():
        if not line.startswith((" ", "\t")):
            cur = line.strip() or None
            continue
        t = line.strip()
        if t.startswith("|->") and cur:
            b = t[3:].strip()
            if name in cur or name in b:
                pairs.add((cur, "->", b))
    return sorted(pairs)


def spawn(args, env=None, keep_stdout=False):
    e = dict(os.environ)
    if env:
        e.update(env)
    p = subprocess.Popen(
        args,
        stdout=subprocess.PIPE if keep_stdout else subprocess.DEVNULL,
        stderr=subprocess.STDOUT if keep_stdout else subprocess.PIPE,
        env=e)
    OWN_PROCS.append(p)
    return p


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
    """Feed commands to pw-cli with warmup + per-cmd pacing; return raw log."""
    script = [("sleep", warm_s)]
    for pre, c in cmds:
        if pre:
            script.append(("sleep", pre))
        script.append(("cmd", c))
    script.append(("sleep", 0.35))
    script.append(("cmd", "quit"))

    proc = subprocess.Popen(["pw-cli"], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    OWN_PROCS.append(proc)
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
    t.join(timeout=feed_total)
    try:
        rc = proc.wait(timeout=wait_s)
    except subprocess.TimeoutExpired:
        proc.kill()
        rc = "timeout"
        proc.wait(timeout=3)
    rd.join(timeout=3)
    text = b"".join(chunks).decode(errors="replace")
    if label:
        (RUNS / (label + ".pwcli")).write_text(text)
    return {"rc": rc, "log": text, "marks": marks}


_CMD_RE = re.compile(
    r"^\s*(?:pipewire-0>>\s*)?"
    r"(info|enum-params|set-param|send-command|destroy|create-node|create-device|"
    r"get-permissions|list-remotes|load-module|connect|permissions|quit)\b")


def pwcli_split(log):
    """Split a pw-cli log into [(cmd, response_segment)] by command echoes."""
    out = []
    cur, seg = None, []
    for line in log.splitlines():
        m = _CMD_RE.match(line)
        if m:
            if cur is not None:
                out.append((cur, "\n".join(seg)))
            cur = line.strip()
            seg = []
        else:
            if cur is not None:
                seg.append(line)
    if cur is not None:
        out.append((cur, "\n".join(seg)))
    return out


def pwcli_errors(log):
    return re.findall(r'Error: "([^"]+)"', log)


def parse_props_volume(segment):
    m = re.search(r"Props:volume \(65539\).*?\n\s*Float ([0-9.]+)", segment)
    return float(m.group(1)) if m else None


def parse_format(segment):
    rate = re.search(r"Props:Format:Audio:rate \(65539\).*?\n\s*(?:Int|Choice[^\n]*\n\s*Int) (\d+)",
                     segment)
    fmt = re.search(r"Props:Format:Audio:format \(65537\).*?\n\s*(?:Choice[^\n]*\n\s*)?Id (\d+)",
                    segment)
    return {"rate": int(rate.group(1)) if rate else None,
            "format_id": int(fmt.group(1)) if fmt else None}


def mod_lines():
    r = sh(["pactl", "list", "short", "modules"], timeout=15)
    return [l for l in r["out"].splitlines() if l.strip()]


def own_module_idx(sink_name):
    for line in mod_lines():
        if "module-null-sink" in line and ("sink_name=" + sink_name) in line:
            return int(line.split()[0])
    return None


def load_own_sink(name, extra=""):
    args = (f"sink_name={name} sink_properties=device.description={name} "
            f"rate={RATE} channels=2 {extra}").split()
    r = sh(["pactl", "load-module", "module-null-sink"] + args, timeout=15)
    idx = None
    if r["rc"] == 0 and r["out"].strip().isdigit():
        idx = int(r["out"].strip())
    time.sleep(0.5)
    return idx


def unload_own_sink(name):
    idx = own_module_idx(name)
    if idx is None:
        return {"rc": "no-such", "out": "", "err": "", "elapsed_ms": 0}
    line = [l for l in mod_lines() if l.split() and l.split()[0] == str(idx)]
    if not line or ("sink_name=" + name) not in line[0]:
        return {"rc": "refused-not-verified", "out": "", "err": "",
                "elapsed_ms": 0}
    return sh(["pactl", "unload-module", str(idx)], timeout=15)


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
    """SMF fmt0 480tpq: C4 on/off; E4 on/off (~4 s at 120 bpm)."""
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


def rms_ratio(a, b):
    if a is None or b in (None, 0):
        return None
    return round(a / b, 4)


# ---------- load + contention ----------

def hog_start(n=24):
    for _ in range(n):
        p = subprocess.Popen(["python3", "-c", "while True: pass"],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        HOGS.append(p)
    time.sleep(1.0)
    return [p.pid for p in HOGS]


def hog_stop():
    pids = [p.pid for p in HOGS]
    for p in HOGS:
        if p.poll() is None:
            p.terminate()
    for p in HOGS:
        try:
            p.wait(timeout=3)
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait(timeout=3)
    HOGS.clear()
    return pids


def loadavg():
    try:
        return open("/proc/loadavg").read().strip()
    except OSError:
        return None


def proc_snapshot():
    out = []
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            cmd = open(f"/proc/{pid}/cmdline", "rb").read().decode(
                errors="replace").replace("\0", " ").strip()
        except OSError:
            continue
        if cmd:
            out.append({"pid": int(pid), "cmd": cmd[:300]})
    return out


def contention_snapshot():
    """Foreign audio actors (never my own r87b_* seat)."""
    pat = re.compile(r"(\br\d\d|paplay|pw-cat|pw-play|pw-record|pw-midi|aplaymidi|parec)")
    skip = re.compile(r"r87b|r87b_probe|r87b_lib")
    res = []
    for e in proc_snapshot():
        if skip.search(e["cmd"]):
            continue
        if pat.search(e["cmd"]):
            res.append(e)
    d = pw_dump()
    names = sorted({p["name"] for p in all_node_names(d)
                    if p["name"] and not str(p["name"]).startswith("r87b")
                    and re.match(r"r\d\d", str(p["name"]))})
    return {"procs": res, "foreign_prefix_nodes": names,
            "default_sink": sh(["pactl", "get-default-sink"])["out"].strip(),
            "loadavg": loadavg()}


# ---------- legs ----------

def play_leg(name, args, env=None, observe_s=(0.9, 1.6), keep_stdout=False):
    p = spawn(args, env=env, keep_stdout=keep_stdout)
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
                     for q in port_inventory(d)
                     if q["node_id"] == str(node["id"])]
        snaps.append({"at": round(time.time() - t0, 3),
                      "node_present": node is not None,
                      "state": (node or {}).get("info", {}).get("state"),
                      "media_class": props_of(node or {}).get("media.class"),
                      "ports": ports,
                      "links": links_for(name)})
    rc, err = stop(p)
    return {"argv": args, "node_name": name, "rc": rc,
            "stderr": norm(err.strip())[-400:], "snaps": snaps}


def nowarm_info(oid):
    """Zero-warmup pw-cli info <oid> (cold-registry probe)."""
    p = subprocess.Popen(["pw-cli"], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    OWN_PROCS.append(p)
    try:
        out, _ = p.communicate(f"info {oid}\nquit\n".encode(), timeout=10)
    except subprocess.TimeoutExpired:
        p.kill()
        out = b""
    return {"rc": p.returncode, "oid": oid,
            "log": out.decode(errors="replace")[-800:]}
