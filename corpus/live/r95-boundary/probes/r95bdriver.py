#!/usr/bin/env python3
"""r95-boundary driver — attack the r95-scout JACK<->PipeWire laws.

Seat namespace: r95b_* only. Fresh process per rep. Two conditions:
  h = 14 own CPU hogs running (>=12 required), loadavg recorded per stage
  q = no own hogs (foreign load still recorded and disclosed)

Ownership: every module id and PID this driver creates is tracked; sweep()
kills ONLY tracked PIDs plus namespace-verified r95b strays (basename in the
seat binary set AND 'r95b' in cmdline). No namespace-blind sweeps (r95
incident precedent: a sweep matching bare `pw-record` killed r85-boundary
legs). No pactl set-default-*. Null sinks carry state.restore-props=false.

Stages: env shape xconnect liveness bytepath quantum global xrun latency
        rtprio transport metadata nameproj flags defaultnode sibling verify
Usage: r95bdriver.py <stage|all> [--cond h|q] [--reps N] [--hogs N]
"""
import hashlib
import json
import math
import os
import re
import resource
import signal
import struct
import subprocess
import sys
import time
import wave

SEAT = "r95b"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                 # corpus/live/r95-boundary
RECEIPTS = os.path.join(ROOT, "receipts")
RUNS = os.path.join(ROOT, "runs")
SCRATCH = os.path.join(ROOT, "scratch")
PROBE = os.path.join(HERE, "r95bjack")
FREQ = 997.0
RATE = 48000
DEFAULT_WALL = 25.0
BYTE_CAP = 8 << 20
HOG_N = 14

OWN = {"pids": set(), "modules": []}


def _ncore():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


class Bounded:
    def __init__(self, argv, wall=DEFAULT_WALL, byte_cap=BYTE_CAP, env=None,
                 wait=True, track=True):
        e = dict(os.environ)
        if env:
            e.update(env)
        self.argv = argv
        self.byte_cap = byte_cap
        self.t0 = time.time()
        self.timed_out = False
        p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             stdin=subprocess.DEVNULL, start_new_session=True,
                             preexec_fn=_ncore, env=e)
        self.p = p
        self.pid = p.pid
        if track:
            OWN["pids"].add(p.pid)
        self.rc = None
        self.out = ""
        self.err = ""
        self.dur = None
        if wait:
            self.finish(wall)

    def _decode(self, out, err):
        self.out = out.decode("utf-8", "replace")
        self.err = err.decode("utf-8", "replace")
        if len(self.out) > self.byte_cap:
            self.out = self.out[:self.byte_cap]

    def finish(self, wall=DEFAULT_WALL):
        try:
            out, err = self.p.communicate(timeout=wall)
            self.rc = self.p.returncode
        except subprocess.TimeoutExpired:
            self.timed_out = True
            try:
                os.killpg(os.getpgid(self.pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
            out, err = self.p.communicate()
            self.rc = self.p.returncode
        self.dur = time.time() - self.t0
        self._decode(out, err)
        OWN["pids"].discard(self.pid)
        return self.rc, self.out, self.err

    def term(self, grace=4.0):
        try:
            os.killpg(os.getpgid(self.pid), signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            pass
        try:
            out, err = self.p.communicate(timeout=grace)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(self.pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
            out, err = self.p.communicate()
        self.rc = self.p.returncode
        self.dur = time.time() - self.t0
        self._decode(out, err)
        OWN["pids"].discard(self.pid)
        return self.rc, self.out, self.err


def sh(argv, wall=10.0, env=None):
    return Bounded(argv, wall=wall, env=env)


def parse_jack(out):
    rows = [l for l in out.splitlines() if l.startswith("R95JSON ")]
    if not rows:
        return None
    try:
        return json.loads(rows[-1][len("R95JSON "):])
    except json.JSONDecodeError as ex:
        return {"_json_error": str(ex), "_raw": rows[-1][:400]}


def jack_json(argv, wall=DEFAULT_WALL, env=None, wait=True):
    b = Bounded(argv, wall=wall, env=env, wait=wait)
    if not wait:
        return None, b
    return parse_jack(b.out), b


# ------------------------------------------------------------- ownership

def load_null(name, desc_form="restore"):
    """Load a seat null sink; track the module id. desc_form='plain' uses
    device.description only (leaves a stream-properties row - disclosed)."""
    if desc_form == "restore":
        props = "state.restore-props=false,device.description=" + name
    else:
        props = "device.description=" + name
    b = sh(["pactl", "load-module", "module-null-sink", "sink_name=" + name,
            "channels=1", "sink_properties=" + props])
    m = re.match(r"(\d+)\s*$", b.out.strip())
    mid = int(m.group(1)) if m else None
    if mid is not None:
        OWN["modules"].append(mid)
    return mid


def unload_module(mid):
    if mid is None:
        return None
    if mid not in OWN["modules"]:
        return None                       # never unload a module we did not load
    b = sh(["pactl", "unload-module", str(mid)])
    OWN["modules"].remove(mid)
    return b


def modules_matching(pat):
    b = sh(["pactl", "list", "modules", "short"], wall=12)
    rows = []
    for line in b.out.splitlines():
        if pat in line:                   # whole line: name + argument
            m = re.match(r"^(\d+)\t([^\t]+)\t(.*)$", line)
            if m:
                rows.append((int(m.group(1)), m.group(2), m.group(3)))
    return rows


def procs_matching(pat):
    """Namespace-verified only: argv[0] basename must be one of the seat's own
    binaries AND the cmdline must carry `pat`."""
    out = []
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as f:
                raw = f.read()
        except OSError:
            continue
        argv = raw.split(b"\0")
        if not argv or not argv[0]:
            continue
        cmdline = b" ".join(argv).decode("utf-8", "replace").strip()
        a0 = os.path.basename(argv[0].decode("utf-8", "replace"))
        if a0.startswith(("r95bjack", "pw-record", "pw-play", "pw-cat")) and pat in cmdline:
            out.append((int(pid), cmdline))
    return out


def sweep():
    killed = []
    for pid in sorted(OWN["pids"]):
        try:
            os.kill(pid, signal.SIGKILL)
            killed.append(pid)
        except ProcessLookupError:
            pass
        except PermissionError:
            pass
    OWN["pids"].clear()
    for pid, cmd in procs_matching("r95b"):
        try:
            os.kill(pid, signal.SIGKILL)
            killed.append(pid)
        except (ProcessLookupError, PermissionError):
            pass
    unloaded = []
    for idx, name, args in modules_matching("r95b"):
        b = sh(["pactl", "unload-module", str(idx)])
        unloaded.append((idx, name, args, b.rc))
        if idx in OWN["modules"]:
            OWN["modules"].remove(idx)
    return {"killed": killed, "unloaded": unloaded}


class Hogs:
    def __init__(self, n=HOG_N):
        self.n = n
        self.pids = []

    def start(self):
        for i in range(self.n):
            p = subprocess.Popen(
                ["bash", "-c", f"exec -a r95b_hog_{i:02d} yes > /dev/null"],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, start_new_session=True)
            self.pids.append(p.pid)
        return self.count()

    def count(self):
        live = []
        for pid in self.pids:
            try:
                with open(f"/proc/{pid}/cmdline", "rb") as f:
                    raw = f.read()
                if b"r95b_hog" in raw:
                    live.append(pid)
            except OSError:
                pass
        return len(live)

    def stop(self):
        for pid in self.pids:
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        time.sleep(0.5)
        for pid in self.pids:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        self.pids = []


def loadavg():
    la = os.getloadavg()
    running = total = None
    try:
        with open("/proc/loadavg") as f:
            parts = f.read().split()
        running, total = parts[3], parts[4]
    except OSError:
        pass
    return {"load1": la[0], "load5": la[1], "load15": la[2],
            "procs": running, "last_pid": total}


def foreign_census():
    """Read-only: which known sibling namespaces are live right now."""
    pats = {"r92b": 0, "r99": 0, "r90a": 0, "r97b": 0, "game-dev": 0,
            "yes": 0, "godot": 0, "shm_probe": 0, "run_battery": 0}
    rows = []
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as f:
                raw = f.read()
        except OSError:
            continue
        cmdline = b" ".join(raw.split(b"\0")).decode("utf-8", "replace").strip()
        for p in pats:
            if p in cmdline:
                pats[p] += 1
                if p != "yes":
                    rows.append((int(pid), cmdline[:180]))
    return {"counts": pats, "rows": rows[:40]}


# ------------------------------------------------------------- probes

def graph_snapshot(pat="r95b"):
    b = sh(["pw-dump"], wall=30)
    try:
        d = json.loads(b.out)
    except json.JSONDecodeError:
        return {"_error": "pw-dump parse", "_raw": b.out[:200]}
    nodes, clients, ports, meta = {}, {}, {}, []
    seat_nodes = set()
    all_node_names, foreign_nodes = [], []
    for o in d:
        if o.get("type") == "PipeWire:Interface:Node":
            p = (o.get("info") or {}).get("props") or {}
            nm = str(p.get("node.name", ""))
            all_node_names.append(nm)
            if pat in nm or "jack" == str(p.get("client.api", "")):
                seat_nodes.add(o["id"])
            elif nm:
                foreign_nodes.append(nm)
    for o in d:
        t = o.get("type")
        info = o.get("info") or {}
        p = info.get("props") or {}
        if t == "PipeWire:Interface:Node" and o["id"] in seat_nodes:
            nodes[o["id"]] = {k: p.get(k) for k in (
                "node.name", "client.api", "node.description", "node.nick",
                "media.class", "media.category", "media.role", "node.group",
                "node.always-process", "node.force-quantum", "node.force-rate",
                "node.latency", "node.pause-on-idle", "node.passive",
                "application.name", "object.serial", "target.object")}
        if t == "PipeWire:Interface:Client" and pat in str(p.get("client.name", "")):
            clients[o["id"]] = {k: p.get(k) for k in (
                "client.name", "client.api", "application.name",
                "application.process.binary", "pipewire.sec.pid")}
        if t == "PipeWire:Interface:Port":
            alias = str(p.get("port.alias", ""))
            path = str(p.get("object.path", ""))
            if p.get("node.id") in seat_nodes or pat in alias or pat in path:
                ports[o["id"]] = {k: p.get(k) for k in (
                    "port.name", "port.alias", "object.path", "port.direction",
                    "format.dsp", "port.physical", "port.terminal", "port.extra",
                    "node.id")}
        if t == "PipeWire:Interface:Metadata":
            mp = o.get("props") or {}
            name = mp.get("metadata.name")
            keep = ("clock.quantum", "clock.force-quantum", "clock.force-rate",
                    "clock.rate", "clock.allowed-rates", "default.audio.sink",
                    "default.audio.source", "default.configured.audio.sink")
            rows = []
            for r in (o.get("metadata") or []):
                key = str(r.get("key", ""))
                if pat in key or (r.get("subject") == 0 and key in keep):
                    rows.append({"subject": r.get("subject"), "key": key,
                                 "type": r.get("type"), "value": r.get("value")})
            meta.append({"id": o["id"], "name": name, "rows": rows[:80]})
    return {"nodes": nodes, "clients": clients, "ports": ports, "metadata": meta,
            "all_node_count": len(all_node_names),
            "foreign_nodes": sorted(set(n for n in foreign_nodes if n))[:40]}


def pw_link_l():
    return sh(["pw-link", "-l"], wall=15).out


def link_lines_for(pat):
    return [l.strip() for l in pw_link_l().splitlines() if pat in l]


def pw_metadata(name):
    b = sh(["pw-metadata", "-n", name], wall=12)
    rows = {}
    for line in b.out.splitlines():
        m = re.match(r"update: id:(\d+) key:'(.*?)' value:'(.*?)' type:'(.*?)'", line)
        if m:
            rows[(int(m.group(1)), m.group(2))] = {"value": m.group(3), "type": m.group(4)}
    return rows


def defaults():
    b = sh(["pactl", "info"], wall=12)
    d = {}
    for line in b.out.splitlines():
        if line.startswith("Default Sink:") or line.startswith("Default Source:"):
            k, v = line.split(":", 1)
            d[k.strip()] = v.strip()
    return d


def settings_rows():
    return {f"{k[0]}:{k[1]}": v for k, v in pw_metadata("settings").items()}


def tone_wav(path, dur=1.5, freq=FREQ, amp=0.5, rate=RATE):
    n = int(rate * dur)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"".join(
            struct.pack("<h", int(amp * 32767 * math.sin(2 * math.pi * freq * i / rate)))
            for i in range(n)))
    return n


def silent_wav(path, dur=1.5, rate=RATE):
    n = int(rate * dur)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"\x00\x00" * n)
    return n


def analyze_wav(path, freq=FREQ):
    with wave.open(path, "rb") as w:
        n = w.getnframes()
        fr = w.getframerate()
        ch = w.getnchannels()
        data = w.readframes(n)
    if not data:
        return {"frames": 0, "bytes": 0, "rms": 0.0, "goertzel_mag2": 0.0, "peak": 0.0}
    s = struct.unpack("<%dh" % (len(data) // 2), data)
    N = len(s)
    peak = max(abs(x) for x in s) / 32768.0
    rms = math.sqrt(sum(x * x for x in s) / N) / 32768.0
    coef = 2.0 * math.cos(2.0 * math.pi * freq / fr)
    g1 = g2 = 0.0
    for x in s:
        y = x / 32768.0 + coef * g1 - g2
        g2 = g1
        g1 = y
    mag2 = g1 * g1 + g2 * g2 - coef * g1 * g2
    return {"frames": n, "rate": fr, "channels": ch, "bytes": len(data),
            "rms": rms, "peak": peak, "goertzel_mag2": mag2}


def pw_top_snapshot():
    b = sh(["pw-top", "-b", "-n", "1"], wall=10)
    rows = []
    for line in b.out.splitlines():
        parts = line.split()
        if len(parts) >= 9 and parts[0] in ("S", "C", "I") and parts[1].isdigit():
            rows.append({"status": parts[0], "id": parts[1], "quant": parts[2],
                         "rate": parts[3], "err": parts[6], "name": " ".join(parts[9:]) or parts[-1]})
    return rows


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def write_receipt(stage, cond, data):
    os.makedirs(RECEIPTS, exist_ok=True)
    path = os.path.join(RECEIPTS, f"{cond}_{stage}.json")
    data["_stage"] = stage
    data["_cond"] = cond
    data["_ts"] = now()
    with open(path, "w") as f:
        json.dump(data, f, indent=1, sort_keys=True)
    return path


def owned_null_desc(desc_name):
    """Rendered JACK name of a seat null sink = node.description:playback_MONO."""
    for n in graph_snapshot()["nodes"].values():
        if n.get("node.name") == desc_name:
            return (n.get("node.description") or desc_name) + ":playback_MONO"
    return desc_name + ":playback_MONO"


def stage_header(cond, reps):
    return {"cond": cond, "reps": reps, "loadavg_start": loadavg(),
            "foreign_start": foreign_census(), "hogs": HOGS.count()}


# ------------------------------------------------------------- stages

def stage_env(cond, reps):
    rec = stage_header(cond, reps)
    which = {}
    for tool in ("jackd", "jack_lsp", "jack_connect", "jackdbus", "pw-jack",
                 "pw-metadata", "pw-top", "pw-dump", "pw-link", "valgrind"):
        b = sh(["bash", "-lc", f"command -v {tool} || true"], wall=8)
        which[tool] = b.out.strip() or None
    pkgs = {}
    for p in ("pipewire-jack", "jack2", "pipewire"):
        b = sh(["bash", "-lc", f"pacman -Q {p} 2>&1 || true"], wall=8)
        pkgs[p] = b.out.strip()
    libjack = "/usr/lib/libjack.so.0.3.1608"
    lib = {"path": libjack,
           "sha256": sha256(libjack) if os.path.exists(libjack) else None,
           "size": os.path.getsize(libjack) if os.path.exists(libjack) else None}
    b = sh(["bash", "-lc", f"nm -D {libjack} 2>/dev/null | grep -c ' T jack_' || true"], wall=10)
    n_export = int(b.out.strip() or 0)
    b = sh(["bash", "-lc",
            "grep -hoE 'jack_[a-z0-9_]+[[:space:]]*\\(' /usr/include/jack/*.h | "
            "sed 's/[[:space:]]*(//' | sort -u"], wall=10)
    loose = b.out.split()
    strict = sorted(set(n for n in loose if n != "jack_port_t"))
    b = sh(["bash", "-lc", f"nm -D {libjack} | grep ' T jack_' | awk '{{print $3}}' | sort -u"], wall=10)
    exports = b.out.split()
    missing = sorted(set(strict) - set(exports))
    b = sh(["bash", "-lc",
            "sha256sum /usr/share/pipewire/jack.conf /usr/bin/pw-jack; "
            "man -w pw-jack; man -w pipewire-jack 2>&1; true"], wall=10)
    lines = [l for l in b.out.splitlines() if l.strip()]
    b = sh(["bash", "-lc", "grep -oE 'jack_client_(real_time_priority|max_real_time_priority)' "
                           "/usr/include/jack/*.h | sort -u"], wall=8)
    rt_decl = b.out.split()
    sp = os.path.expanduser("~/.local/state/wireplumber/stream-properties")
    sp_rows = []
    if os.path.exists(sp):
        with open(sp, "r", errors="replace") as f:
            for line in f:
                if "r95s" in line or "r95b" in line:
                    sp_rows.append(line.strip()[:120])
    rec.update({
        "which": which, "packages": pkgs, "libjack": lib,
        "symbols": {"exports": n_export, "declared_loose": len(loose),
                    "declared_strict_functions": len(strict),
                    "type_captured_by_regex": [n for n in loose if n not in strict],
                    "declared_not_exported": missing,
                    "declared_not_exported_count": len(missing)},
        "rt_priority_declared_in_headers": rt_decl,
        "config_and_man": lines,
        "settings_metadata": settings_rows(),
        "defaults": defaults(),
        "stream_properties_r95_rows": sp_rows,
        "graph": graph_snapshot(),
        "top": pw_top_snapshot(),
    })
    write_receipt("env", cond, rec)
    return rec


def stage_shape(cond, reps):
    rec = stage_header(cond, reps)
    rec["reps_data"] = []
    for r in range(reps):
        sweep()
        mid = load_null("r95b_ns")
        time.sleep(0.6)
        b = Bounded([PROBE, "shape", "1.6"], wait=False)
        time.sleep(0.5)
        snap = graph_snapshot()
        links = link_lines_for("r95b_shape")
        top = pw_top_snapshot()
        b.finish(wall=10)
        d = parse_jack(b.out)
        rec["reps_data"].append({
            "rep": r, "nullsink_module": mid, "rc": b.rc, "dur": round(b.dur, 3),
            "json": d, "graph": snap, "links_while_running": links, "top": top,
            "stderr": b.err[:300], "loadavg": loadavg(),
        })
        unload_module(mid)
        time.sleep(0.3)
    rec["sweep_after"] = sweep()
    write_receipt("shape", cond, rec)
    return rec


def stage_xconnect(cond, reps):
    rec = stage_header(cond, reps)
    rec["arms"] = {}
    env_alias = {"PIPEWIRE_PROPS": "{ jack.fill-aliases = true }"}
    for arm in ("rendered", "native", "fillalias"):
        rows = []
        for r in range(reps):
            sweep()
            mid = load_null("r95b_ns")
            time.sleep(0.6)
            snap0 = graph_snapshot()
            desc = None
            for n in snap0["nodes"].values():
                if n.get("node.name") == "r95b_ns":
                    desc = n.get("node.description")
            rendered = (desc or "r95b_ns") + ":playback_MONO"
            target = {"rendered": rendered,
                      "native": "r95b_ns:playback_MONO",
                      "fillalias": "r95b_ns:playback_0"}[arm]
            env = env_alias if arm == "fillalias" else None
            b = Bounded([PROBE, "shape", "1.8", target, "disconnect"], env=env, wait=False)
            time.sleep(0.9)
            links = link_lines_for("r95b_shape")
            top = pw_top_snapshot()
            b.finish(wall=10)
            d = parse_jack(b.out)
            rows.append({"rep": r, "arm": arm, "target": target, "desc": desc,
                         "rc": b.rc, "json": d, "links_while_running": links,
                         "top": top, "stderr": b.err[:300], "loadavg": loadavg()})
            unload_module(mid)
            time.sleep(0.3)
        rec["arms"][arm] = rows
    rec["sweep_after"] = sweep()
    write_receipt("xconnect", cond, rec)
    return rec


def stage_liveness(cond, reps):
    """driver_present (null sink, no links) vs no_driver (no seat sink)."""
    rec = stage_header(cond, reps)
    rec["driver_present"] = []
    rec["no_driver"] = []
    for r in range(reps):
        sweep()
        mid = load_null("r95b_ns")
        time.sleep(0.6)
        b = Bounded([PROBE, "tone", "1.6"], wait=False)
        time.sleep(0.6)
        links = link_lines_for("r95b_probe")
        top = pw_top_snapshot()
        b.finish(wall=10)
        d = parse_jack(b.out)
        rec["driver_present"].append({"rep": r, "nullsink_module": mid, "rc": b.rc,
                                      "json": d, "links_while_running": links,
                                      "top": top, "loadavg": loadavg()})
        unload_module(mid)
        time.sleep(0.4)
    for r in range(reps):
        sweep()
        time.sleep(0.4)
        snap = graph_snapshot()
        b = Bounded([PROBE, "tone", "1.6"], wait=False)
        tops = []
        for t in range(4):
            time.sleep(0.35)
            tops.append({"t": round(t * 0.35, 2), "top": pw_top_snapshot(),
                         "links": link_lines_for("r95b_probe")})
        b.finish(wall=10)
        d = parse_jack(b.out)
        rec["no_driver"].append({"rep": r, "rc": b.rc, "json": d,
                                 "top_samples": tops,
                                 "graph_foreign": snap["foreign_nodes"],
                                 "all_links_sample": [l.strip() for l in pw_link_l().splitlines()][:40],
                                 "loadavg": loadavg()})
    rec["sweep_after"] = sweep()
    write_receipt("liveness", cond, rec)
    return rec


def stage_bytepath(cond, reps):
    rec = stage_header(cond, reps)
    rec["jack2pw"] = []
    rec["pw2jack"] = []
    tone = os.path.join(SCRATCH, "tone997.wav")
    if not os.path.exists(tone):
        tone_wav(tone)
    rec["tone_file"] = {"path": tone, "sha256": sha256(tone)}
    for r in range(reps):
        sweep()
        mid = load_null("r95b_ns")
        time.sleep(0.6)
        target = owned_null_desc("r95b_ns")
        wav = os.path.join(SCRATCH, f"c1_rep{r}.wav")
        if os.path.exists(wav):
            os.remove(wav)
        rb = Bounded(["pw-record", "-P", "stream.capture.sink=true",
                      "-P", "node.name=r95b_rec", "-P", "state.restore-props=false",
                      "--target", "r95b_ns", "--rate", "48000", "--channels", "1", wav],
                     wall=14, wait=False)
        time.sleep(0.7)
        tb = Bounded([PROBE, "tone", "2.5", "0", "0", target], wait=False)
        time.sleep(1.0)
        links = link_lines_for("r95b")
        top = pw_top_snapshot()
        snap = graph_snapshot()
        tb.finish(wall=10)
        d = parse_jack(tb.out)
        time.sleep(0.4)
        rb.term(grace=5)
        time.sleep(0.4)
        analysis = analyze_wav(wav) if os.path.exists(wav) else None
        rec["jack2pw"].append({"rep": r, "nullsink_module": mid, "rc": tb.rc,
                               "json": d, "target": target, "links_while_running": links,
                               "top": top, "graph_nodes": len(snap["nodes"]),
                               "wav": analysis,
                               "wav_sha256": sha256(wav) if os.path.exists(wav) else None,
                               "loadavg": loadavg()})
        unload_module(mid)
        time.sleep(0.3)
    for r in range(reps):
        sweep()
        jb = Bounded([PROBE, "tone", "3.2"], wall=16, wait=False)
        time.sleep(0.7)
        pb = Bounded(["pw-play", "-P", "node.autoconnect=false", "-P", "node.name=r95b_play",
                      "-P", "state.restore-props=false", "--channels", "1", "--rate", "48000", tone],
                     wall=12, wait=False)
        time.sleep(0.6)
        link1 = sh(["pw-link", "r95b_play:output_MONO", "r95b_probe:in"], wall=10)
        links = link_lines_for("r95b_play")
        top = pw_top_snapshot()
        deadline = time.time() + 7
        while time.time() < deadline and jb.p.poll() is None:
            time.sleep(0.2)
        if jb.p.poll() is None:
            try:
                os.killpg(os.getpgid(jb.pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
        jb.finish(wall=6)
        jd = parse_jack(jb.out)
        rec["pw2jack"].append({"rep": r, "pw_link_rc": link1.rc,
                               "pw_link_err": link1.err.strip()[:200],
                               "links_while_running": links, "jack_json": jd,
                               "pw_play_rc": pb.rc,
                               "pw_play_stderr": pb.err.strip()[:300],
                               "top": pw_top_snapshot(), "loadavg": loadavg()})
        try:
            os.killpg(os.getpgid(pb.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        time.sleep(0.3)
    rec["sweep_after"] = sweep()
    write_receipt("bytepath", cond, rec)
    return rec


def stage_quantum(cond, reps):
    rec = stage_header(cond, reps)
    rec["per_client"] = []
    rec["env_arms"] = {}
    rec["pwjack_arms"] = {}
    rec["cross"] = []
    for r in range(reps):
        sweep()
        mid = load_null("r95b_ns")
        time.sleep(0.6)
        b = Bounded([PROBE, "bufsize", "1.4", "2048", "512"], wait=False)
        time.sleep(0.7)
        snap = graph_snapshot()
        meta = settings_rows()
        top = pw_top_snapshot()
        b.finish(wall=10)
        d = parse_jack(b.out)
        rec["per_client"].append({"rep": r, "nullsink_module": mid, "rc": b.rc,
                                  "json": d, "graph": snap, "settings": meta,
                                  "top": top, "loadavg": loadavg()})
        unload_module(mid)
        time.sleep(0.3)
    for tag, q in (("512_48000", "512/48000"), ("256_48000", "256/48000"),
                   ("2048_48000", "2048/48000"), ("512_44100", "512/44100"),
                   ("512_96000", "512/96000")):
        rows = []
        for r in range(reps):
            sweep()
            mid = load_null("r95b_ns")
            time.sleep(0.5)
            b = Bounded([PROBE, "info", "0.8"], env={"PIPEWIRE_QUANTUM": q}, wait=False)
            time.sleep(0.35)
            snap = graph_snapshot()
            top = pw_top_snapshot()
            b.finish(wall=10)
            d = parse_jack(b.out)
            rows.append({"rep": r, "rc": b.rc, "json": d, "graph": snap, "top": top,
                         "settings_after": settings_rows(), "loadavg": loadavg()})
            unload_module(mid)
            time.sleep(0.3)
        rec["env_arms"][tag] = rows
    for tag, argv in (("sep", ["pw-jack", "-p", "512", PROBE, "info", "0.8"]),
                      ("attached", ["pw-jack", "-p512", PROBE, "info", "0.8"]),
                      ("order_neg", ["pw-jack", PROBE, "-p", "512"])):
        rows = []
        for r in range(reps):
            sweep()
            mid = load_null("r95b_ns")
            time.sleep(0.5)
            b = Bounded(argv, wait=False)
            time.sleep(0.35)
            snap = graph_snapshot()
            b.finish(wall=10)
            d = parse_jack(b.out)
            rows.append({"rep": r, "rc": b.rc, "json": d, "graph": snap,
                         "stderr": b.err[:200], "loadavg": loadavg()})
            unload_module(mid)
            time.sleep(0.3)
        rec["pwjack_arms"][tag] = rows
    for r in range(reps):
        sweep()
        mid = load_null("r95b_ns")
        time.sleep(0.6)
        ab = Bounded([PROBE, "bufsize", "1.8", "2048", "0"], wait=False)
        time.sleep(0.7)
        snap = graph_snapshot()
        top = pw_top_snapshot()
        db, bb = jack_json([PROBE, "info", "0.4"], wall=12)
        ab.finish(wall=10)
        a_json = parse_jack(ab.out)
        rec["cross"].append({"rep": r, "a_json": a_json, "b_json": db, "b_rc": bb.rc,
                             "graph": snap, "top": top, "loadavg": loadavg()})
        unload_module(mid)
        time.sleep(0.3)
    rec["sweep_after"] = sweep()
    write_receipt("quantum", cond, rec)
    return rec


def stage_global(cond, reps):
    """jack.global-buffer-size=true -> settings clock.force-quantum. Disclosed
    host mutation; restored via set_buffer_size(1) and verified per rep."""
    rec = stage_header(cond, reps)
    rec["disclosure"] = ("clock.force-quantum set to 512 for <3 s per rep, then restored "
                         "to 0 via jack_set_buffer_size(1) and verified; sibling seats may "
                         "observe the window (timestamps recorded)")
    rec["reps_data"] = []
    env = {"PIPEWIRE_PROPS": "{ jack.global-buffer-size = true }"}
    for r in range(reps):
        sweep()
        mid = load_null("r95b_ns")
        time.sleep(0.6)
        before = settings_rows()
        ab = Bounded([PROBE, "bufsize", "2.2", "512", "0"], env=env, wait=False)
        t_during = now()
        time.sleep(0.8)
        during = settings_rows()
        during_top = pw_top_snapshot()
        db, bb = jack_json([PROBE, "info", "0.4"], wall=12)
        time.sleep(0.4)
        ab.finish(wall=10)
        a_json = parse_jack(ab.out)
        after_a = settings_rows()
        rb = Bounded([PROBE, "bufsize", "0.4", "1", "0"], wall=10, env=env)
        time.sleep(0.5)
        restored = settings_rows()
        retry = None
        if restored.get("0:clock.force-quantum", {}).get("value") != "0":
            rb2 = Bounded([PROBE, "bufsize", "0.4", "1", "0"], wall=10, env=env)
            time.sleep(0.5)
            retry = {"rc": rb2.rc, "settings": settings_rows()}
        final = settings_rows()
        rec["reps_data"].append({
            "rep": r, "nullsink_module": mid, "t_during": t_during,
            "settings_before": {k: v for k, v in before.items() if "quantum" in k or "rate" in k},
            "settings_during": {k: v for k, v in during.items() if "quantum" in k or "rate" in k},
            "settings_after_client_exit": {k: v for k, v in after_a.items() if "quantum" in k or "rate" in k},
            "settings_restored": {k: v for k, v in restored.items() if "quantum" in k or "rate" in k},
            "settings_final": {k: v for k, v in final.items() if "quantum" in k or "rate" in k},
            "a_json": a_json, "b_json": db, "b_rc": bb.rc,
            "top_during": during_top, "restore_retry": retry, "loadavg": loadavg(),
        })
        unload_module(mid)
        time.sleep(0.3)
    rec["sweep_after"] = sweep()
    write_receipt("global", cond, rec)
    return rec


def stage_xrun(cond, reps):
    rec = stage_header(cond, reps)
    rec["reps_data"] = []
    for r in range(reps):
        sweep()
        mid = load_null("r95b_ns")
        time.sleep(0.6)
        target = owned_null_desc("r95b_ns")
        ctl, cb = jack_json([PROBE, "tone", "2.0", "0", "0", target], wall=16)
        st, sb = jack_json([PROBE, "stall", "2.0", "4", "150000", target], wall=18)
        st2, sb2 = jack_json([PROBE, "stall", "2.0", "2", "60000", target], wall=18)
        rec["reps_data"].append({"rep": r, "control": ctl, "control_rc": cb.rc,
                                 "stall_150x4": st, "stall_rc": sb.rc,
                                 "stall_60x2": st2, "stall2_rc": sb2.rc,
                                 "top": pw_top_snapshot(), "loadavg": loadavg()})
        unload_module(mid)
        time.sleep(0.3)
    rec["sweep_after"] = sweep()
    write_receipt("xrun", cond, rec)
    return rec


def stage_latency(cond, reps):
    rec = stage_header(cond, reps)
    rec["reps_data"] = []
    for r in range(reps):
        sweep()
        d, b = jack_json([PROBE, "latency", "0.6"], wall=12)
        rec["reps_data"].append({"rep": r, "rc": b.rc, "json": d, "loadavg": loadavg()})
    rec["sweep_after"] = sweep()
    write_receipt("latency", cond, rec)
    return rec


def stage_rtprio(cond, reps):
    rec = stage_header(cond, reps)
    rec["rtprio"] = []
    rec["poison"] = []
    for r in range(reps):
        sweep()
        d, b = jack_json([PROBE, "rtprio"], wall=12)
        rec["rtprio"].append({"rep": r, "rc": b.rc, "json": d, "loadavg": loadavg()})
    for r in range(reps):
        sweep()
        d, b = jack_json([PROBE, "rtprio_poison"], wall=12)
        rec["poison"].append({"rep": r, "rc": b.rc, "json": d, "loadavg": loadavg()})
    rec["sweep_after"] = sweep()
    write_receipt("rtprio", cond, rec)
    return rec


def stage_transport(cond, reps):
    rec = stage_header(cond, reps)
    rec["reps_data"] = []
    for r in range(reps):
        sweep()
        mid = load_null("r95b_ns")
        time.sleep(0.6)
        target = owned_null_desc("r95b_ns")
        t0 = time.time()
        b = Bounded([PROBE, "transport", "1.6", target], wait=False)
        time.sleep(0.5)
        top = pw_top_snapshot()
        snap = graph_snapshot()
        b.finish(wall=10)
        d = parse_jack(b.out)
        rec["reps_data"].append({"rep": r, "nullsink_module": mid, "rc": b.rc,
                                 "json": d, "target": target, "top": top,
                                 "graph_nodes": len(snap["nodes"]),
                                 "wall_s": round(time.time() - t0, 3),
                                 "stderr": b.err[:300], "loadavg": loadavg()})
        unload_module(mid)
        time.sleep(0.3)
    rec["sweep_after"] = sweep()
    write_receipt("transport", cond, rec)
    return rec


def stage_metadata(cond, reps):
    rec = stage_header(cond, reps)
    rec["reps_data"] = []
    for r in range(reps):
        sweep()
        jb = Bounded([PROBE, "metadata", "1.6"], wait=False)
        time.sleep(0.7)
        default_rows = pw_metadata("default")
        snap = graph_snapshot()
        deadline = time.time() + 6
        while time.time() < deadline and jb.p.poll() is None:
            time.sleep(0.2)
        jb.finish(wall=6)
        jd = parse_jack(jb.out)
        time.sleep(0.5)
        after_rows = pw_metadata("default")
        own_id = own_serial = None
        for nid, n in snap["nodes"].items():
            if n.get("node.name") == "r95b_meta":
                own_id = int(nid)
                own_serial = n.get("object.serial")
        during_own = {f"{k[0]}:{k[1]}": v for k, v in default_rows.items()
                      if own_id is not None and k[0] == own_id}
        after_own = {f"{k[0]}:{k[1]}": v for k, v in after_rows.items()
                     if own_id is not None and k[0] == own_id}
        rec["reps_data"].append({"rep": r, "json": jd, "own_registry_id": own_id,
                                 "own_object_serial": own_serial,
                                 "default_metadata_during": during_own,
                                 "default_metadata_after_exit": after_own,
                                 "top": pw_top_snapshot(), "loadavg": loadavg()})
        time.sleep(0.3)
    rec["sweep_after"] = sweep()
    write_receipt("metadata", cond, rec)
    return rec


def stage_nameproj(cond, reps):
    rec = stage_header(cond, reps)
    arms = {"control_prop": "{ mem.warn-mlock = false }",
            "description_override": '{ node.description = "r95b_forced" }',
            "description_same": '{ node.description = "r95b_info" }',
            "nodename_override": '{ node.name = "r95b_forced_name" }',
            "nick_override": '{ node.nick = "r95b_forced_nick" }'}
    rec["arms"] = {}
    for arm, props in arms.items():
        rows = []
        for r in range(reps):
            sweep()
            d, b = jack_json([PROBE, "info", "0.3"], wall=10,
                             env={"PIPEWIRE_PROPS": props})
            rows.append({"rep": r, "arm": arm, "props": props, "rc": b.rc,
                         "json": d, "stderr": b.err[:200], "loadavg": loadavg()})
            time.sleep(0.2)
        rec["arms"][arm] = rows
    # duplicate-name arm: two live clients, same requested name
    dup = []
    for r in range(reps):
        sweep()
        a = Bounded([PROBE, "info", "1.5"], wait=False)
        time.sleep(0.6)
        d, b = jack_json([PROBE, "info", "0.3"], wall=10)
        a.finish(wall=8)
        dup.append({"rep": r, "second_rc": b.rc, "second_json": d,
                    "second_stderr": b.err[:200], "loadavg": loadavg()})
        time.sleep(0.3)
    rec["duplicate_name"] = dup
    rec["sweep_after"] = sweep()
    write_receipt("nameproj", cond, rec)
    return rec


def stage_flags(cond, reps):
    rec = stage_header(cond, reps)
    rec["arms"] = {}
    # 1. pw-play property-flag order (before vs after the positional file)
    tone = os.path.join(SCRATCH, "tone997.wav")
    if not os.path.exists(tone):
        tone_wav(tone)
    for tag, argv in (
            ("props_before", ["pw-play", "-P", "node.name=r95b_f1", "-P",
                              "state.restore-props=false", "--target", "r95b_ns",
                              "--channels", "1", tone]),
            ("props_after", ["pw-play", "--channels", "1", tone, "--target", "r95b_ns",
                             "-P", "node.name=r95b_f2", "-P", "state.restore-props=false"])):
        rows = []
        for r in range(reps):
            sweep()
            mid = load_null("r95b_ns")
            time.sleep(0.5)
            pb = Bounded(argv, wall=10, wait=False)
            time.sleep(0.9)
            links = link_lines_for("r95b_f")
            top = pw_top_snapshot()
            snap = graph_snapshot()
            alive = pb.p.poll() is None
            rc, out, err = pb.term(grace=4)
            rows.append({"rep": r, "rc": rc, "alive_at_census": alive,
                         "links_while_running": links,
                         "top": top, "stderr": err[:200],
                         "seat_nodes": {k: {kk: v.get(kk) for kk in
                                            ("node.name", "application.name", "target.object")}
                                        for k, v in snap["nodes"].items()
                                        if str(v.get("node.name", "")).startswith("r95b_f")},
                         "loadavg": loadavg()})
            unload_module(mid)
            time.sleep(0.3)
        rec["arms"][tag] = rows
    # 2. pw-record property-flag order
    for tag, argv in (
            ("rec_props_before", ["pw-record", "-P", "node.name=r95b_fr1",
                                  "-P", "stream.capture.sink=true",
                                  "-P", "state.restore-props=false", "--target", "r95b_ns",
                                  "--rate", "48000", "--channels", "1",
                                  os.path.join(SCRATCH, "fl1.wav")]),
            ("rec_props_after", ["pw-record", "--rate", "48000", "--channels", "1",
                                 os.path.join(SCRATCH, "fl2.wav"), "--target", "r95b_ns",
                                 "-P", "node.name=r95b_fr2", "-P",
                                 "stream.capture.sink=true",
                                 "-P", "state.restore-props=false"])):
        rows = []
        for r in range(reps):
            sweep()
            mid = load_null("r95b_ns")
            time.sleep(0.5)
            rb = Bounded(argv, wall=10, wait=False)
            time.sleep(0.9)
            links = link_lines_for("r95b_fr")
            alive = rb.p.poll() is None
            rc, out, err = rb.term(grace=4)
            rows.append({"rep": r, "rc": rc, "alive_at_census": alive,
                         "links_while_running": links,
                         "stderr": err[:200], "loadavg": loadavg()})
            unload_module(mid)
            time.sleep(0.3)
        rec["arms"][tag] = rows
    # 3. pw-link argument order
    rows = []
    for r in range(reps):
        sweep()
        jb = Bounded([PROBE, "tone", "3.0"], wall=14, wait=False)
        time.sleep(0.7)
        pb = Bounded(["pw-play", "-P", "node.autoconnect=false", "-P", "node.name=r95b_fl",
                      "-P", "state.restore-props=false", "--channels", "1", tone],
                     wall=10, wait=False)
        time.sleep(0.6)
        good = sh(["pw-link", "r95b_fl:output_MONO", "r95b_probe:in"], wall=8)
        bad = sh(["pw-link", "r95b_probe:in", "r95b_fl:output_MONO"], wall=8)
        links = link_lines_for("r95b_fl")
        jb.finish(wall=8)
        jd = parse_jack(jb.out)
        rows.append({"rep": r, "good_rc": good.rc, "bad_rc": bad.rc,
                     "bad_err": bad.err.strip()[:200], "links": links,
                     "in_nonzero": (jd or {}).get("in_nonzero"), "loadavg": loadavg()})
        try:
            os.killpg(os.getpgid(pb.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        time.sleep(0.3)
    rec["arms"]["pwlink_order"] = rows
    # 4. pactl load-module argument order
    rows = []
    for r in range(reps):
        sweep()
        b1 = sh(["pactl", "load-module", "module-null-sink", "channels=1",
                 "sink_name=r95b_ord1",
                 "sink_properties=state.restore-props=false,device.description=r95b_ord1"])
        m1 = re.match(r"(\d+)\s*$", b1.out.strip())
        m1 = int(m1.group(1)) if m1 else None
        if m1:
            OWN["modules"].append(m1)
        b2 = sh(["pactl", "load-module", "module-null-sink",
                 "sink_properties=state.restore-props=false,device.description=r95b_ord2",
                 "channels=1", "sink_name=r95b_ord2"])
        m2 = re.match(r"(\d+)\s*$", b2.out.strip())
        m2 = int(m2.group(1)) if m2 else None
        if m2:
            OWN["modules"].append(m2)
        time.sleep(0.6)
        snap = graph_snapshot()
        nodes = {v.get("node.name"): {"desc": v.get("node.description"),
                                      "media.class": v.get("media.class")}
                 for v in snap["nodes"].values()
                 if v.get("node.name") in ("r95b_ord1", "r95b_ord2")}
        rows.append({"rep": r, "rc1": b1.rc, "rc2": b2.rc, "nodes": nodes,
                     "loadavg": loadavg()})
        unload_module(m1)
        unload_module(m2)
        time.sleep(0.3)
    rec["arms"]["pactl_order"] = rows
    rec["sweep_after"] = sweep()
    write_receipt("flags", cond, rec)
    return rec


def parse_links(raw):
    """pw-link -l -> [(upstream, downstream)] pairs."""
    pairs = []
    cur = None
    for line in raw.splitlines():
        if line and not line.startswith(" "):
            cur = line.strip()
        elif line.strip().startswith("|<-") and cur:
            pairs.append((line.strip()[3:].strip(), cur))
    return pairs


def stage_defaultnode(cond, reps):
    """Process-scoped default-node variation. All stimuli are SILENT (no audible
    content) so that a control arm linking to the host default sink is harmless.
    pw-play is a native client (env ignored); paplay is the Pulse-ABI client."""
    rec = stage_header(cond, reps)
    sil = os.path.join(SCRATCH, "silent.wav")
    if not os.path.exists(sil):
        silent_wav(sil)
    rec["silent_file"] = {"path": sil, "sha256": sha256(sil)}
    rec["defaults_before"] = defaults()
    rec["default_metadata_before"] = {f"{k[0]}:{k[1]}": v for k, v in pw_metadata("default").items()
                                      if "default" in k[1]}
    rec["arms"] = {}
    for tag, env, target, client in (
            ("pwplay_explicit_target", None, "r95b_ns2", "pw-play"),
            ("pwplay_no_env_control", None, None, "pw-play"),
            ("pwplay_pulse_sink_env", {"PULSE_SINK": "r95b_ns2"}, None, "pw-play"),
            ("paplay_pulse_sink_env", {"PULSE_SINK": "r95b_ns2"}, None, "paplay"),
            ("paplay_no_env_control", None, None, "paplay")):
        rows = []
        for r in range(reps):
            sweep()
            mid = load_null("r95b_ns2")
            time.sleep(0.6)
            name = "r95b_dn"
            if client == "pw-play":
                argv = ["pw-play", "-P", "node.name=r95b_dn", "-P",
                        "state.restore-props=false", "--channels", "1"]
                if target:
                    argv += ["--target", target]
            else:
                argv = ["paplay", "--stream-name=r95b_dn",
                        "--client-name=r95b_dn_client", "--channels=1", "--rate=48000"]
            argv.append(sil)
            pb = Bounded(argv, wall=10, wait=False, env=env)
            time.sleep(1.2)
            raw = pw_link_l()
            pairs = parse_links(raw)
            mypairs = [p for p in pairs if name in p[0] or name in p[1]]
            hostpairs = [p for p in pairs if "SPDIF" in p[0] or "SPDIF" in p[1]]
            myhost = [p for p in mypairs if "SPDIF" in p[0] or "SPDIF" in p[1]]
            myns = [p for p in mypairs if "r95b_ns2" in p[0] or "r95b_ns2" in p[1]]
            top = pw_top_snapshot()
            alive = pb.p.poll() is None
            rc, out, err = pb.term(grace=4)
            rows.append({"rep": r, "client": client, "env": env, "target": target,
                         "rc": rc, "alive_at_census": alive,
                         "my_links": mypairs, "host_default_links": hostpairs,
                         "my_links_to_host_default": myhost, "my_links_to_seat_sink": myns,
                         "top": top, "stderr": err[:200], "loadavg": loadavg()})
            unload_module(mid)
            time.sleep(0.3)
        rec["arms"][tag] = rows
    rec["defaults_after"] = defaults()
    rec["default_metadata_after"] = {f"{k[0]}:{k[1]}": v for k, v in pw_metadata("default").items()
                                     if "default" in k[1]}
    rec["sweep_after"] = sweep()
    write_receipt("defaultnode", cond, rec)
    return rec


def stage_sibling(cond, reps):
    """Record foreign-seat presence and replay two armed cells while they run."""
    rec = stage_header(cond, reps)
    rec["snapshots"] = []
    for r in range(reps):
        pre = {"foreign": foreign_census(), "loadavg": loadavg(),
               "top": pw_top_snapshot(), "graph": graph_snapshot()}
        sweep()
        mid = load_null("r95b_ns")
        time.sleep(0.6)
        target = owned_null_desc("r95b_ns")
        b = Bounded([PROBE, "shape", "1.6", target, "disconnect"], wait=False)
        time.sleep(0.9)
        links = link_lines_for("r95b_shape")
        b.finish(wall=10)
        d = parse_jack(b.out)
        post = {"foreign": foreign_census(), "loadavg": loadavg(),
                "top": pw_top_snapshot()}
        rec["snapshots"].append({"rep": r, "pre": pre, "shape": d, "rc": b.rc,
                                 "links": links, "post": post})
        unload_module(mid)
        time.sleep(0.3)
    rec["sweep_after"] = sweep()
    write_receipt("sibling", cond, rec)
    return rec


def full_node_map():
    """id -> node props incl. node.driver / node.driver-id (who schedules whom)."""
    b = sh(["pw-dump"], wall=30)
    try:
        d = json.loads(b.out)
    except json.JSONDecodeError:
        return {}
    m = {}
    for o in d:
        if o.get("type") == "PipeWire:Interface:Node":
            p = (o.get("info") or {}).get("props") or {}
            m[o["id"]] = {"name": p.get("node.name"), "driver": p.get("node.driver"),
                          "prio": p.get("priority.driver"), "want_driver": p.get("node.want-driver"),
                          "always_process": p.get("node.always-process"),
                          "client_api": p.get("client.api"),
                          "driver_id": p.get("node.driver-id")}
    return m


def stage_corner(cond, reps):
    """Addressing corner: a null sink whose node.description == node.name exactly
    (space-separated sink_properties, which parse correctly). The rendered JACK
    name and the native node.name:port form then coincide - does 'native' resolve?"""
    rec = stage_header(cond, reps)
    rec["note"] = ("sink_properties with SPACE separator parses state.restore-props=false "
                   "and device.description properly; the comma form used elsewhere in this "
                   "seat's battery is mis-parsed into one string value (see report).")
    rec["reps_data"] = []
    for r in range(reps):
        sweep()
        b = sh(["pactl", "load-module", "module-null-sink", "sink_name=r95b_t4",
                "channels=1",
                "sink_properties=state.restore-props=false device.description=r95b_t4"])
        m = re.match(r"(\d+)\s*$", b.out.strip())
        mid = int(m.group(1)) if m else None
        if mid is not None:
            OWN["modules"].append(mid)
        time.sleep(0.7)
        snap = graph_snapshot()
        node = {v.get("node.name"): {"desc": v.get("node.description"),
                                     "nick": v.get("node.nick")}
                for v in snap["nodes"].values() if v.get("node.name") == "r95b_t4"}
        out = {}
        for tag, target in (("rendered_eq_native", "r95b_t4:playback_MONO"),):
            bb = Bounded([PROBE, "shape", "1.4", target, "disconnect"], wait=False)
            time.sleep(0.8)
            links = link_lines_for("r95b_shape")
            bb.finish(wall=10)
            d = parse_jack(bb.out)
            out[tag] = {"target": target, "rc": bb.rc, "json": d, "links": links}
        rec["reps_data"].append({"rep": r, "module": mid, "node": node, "arms": out,
                                 "loadavg": loadavg()})
        unload_module(mid)
        time.sleep(0.3)
    rec["sweep_after"] = sweep()
    write_receipt("corner", cond, rec)
    return rec


def stage_driverid(cond, reps):
    """Who drives an unlinked JACK client when no seat driver exists?
    Runs with NO seat null sink; samples node.driver-id + driver-row activity."""
    rec = stage_header(cond, reps)
    rec["reps_data"] = []
    for r in range(reps):
        sweep()
        time.sleep(0.4)
        pre = full_node_map()
        b = Bounded([PROBE, "tone", "2.5"], wait=False)
        samples = []
        for t in range(3):
            time.sleep(0.5)
            nm = full_node_map()
            own = {k: v for k, v in nm.items()
                   if str(v.get("name", "")).startswith("r95b_probe")}
            drivers = {}
            for cid, cv in own.items():
                did = cv.get("driver_id")
                dnode = None
                try:
                    dnode = nm.get(int(did)) if did is not None else None
                except (TypeError, ValueError):
                    dnode = None
                drivers[str(cid)] = {"driver_id": did,
                                     "driver_name": (dnode or {}).get("name"),
                                     "driver_is_driver": (dnode or {}).get("driver"),
                                     "driver_prio": (dnode or {}).get("prio")}
            active_top = [t2 for t2 in pw_top_snapshot() if t2["quant"] not in ("0",)]
            samples.append({"t": round(t * 0.5 + 0.5, 2), "own_nodes": own,
                            "driver_map": drivers, "active_top": active_top})
        b.finish(wall=12)
        d = parse_jack(b.out)
        rec["reps_data"].append({"rep": r, "rc": b.rc, "json": d, "samples": samples,
                                 "pre_seat_nodes": {k: v for k, v in pre.items()
                                                    if str(v.get("name", "")).startswith("r95b")},
                                 "loadavg": loadavg()})
    rec["sweep_after"] = sweep()
    write_receipt("driverid", cond, rec)
    return rec


def stage_bufsize1(cond, reps):
    """Labrat nuance H3: nframes==1 -> '0' only on the metadata path; the
    node-props path writes the raw value. Arm: set_buffer_size(1) with no
    jack.global-buffer-size -> node.force-quantum value?"""
    rec = stage_header(cond, reps)
    rec["reps_data"] = []
    for r in range(reps):
        sweep()
        mid = load_null("r95b_ns")
        time.sleep(0.5)
        b = Bounded([PROBE, "bufsize", "1.2", "1", "0"], wait=False)
        time.sleep(0.7)
        snap = graph_snapshot()
        b.finish(wall=10)
        d = parse_jack(b.out)
        rec["reps_data"].append({"rep": r, "rc": b.rc, "json": d, "graph": snap,
                                 "loadavg": loadavg()})
        unload_module(mid)
        time.sleep(0.3)
    rec["sweep_after"] = sweep()
    write_receipt("bufsize1", cond, rec)
    return rec


def stage_verify(cond, reps):
    rec = stage_header(cond, reps)
    rec["settings"] = settings_rows()
    rec["defaults"] = defaults()
    rec["modules_r95b"] = modules_matching("r95b")
    rec["procs_r95b"] = procs_matching("r95b")
    rec["graph"] = graph_snapshot()
    rec["top"] = pw_top_snapshot()
    rec["stream_properties_r95_rows"] = []
    sp = os.path.expanduser("~/.local/state/wireplumber/stream-properties")
    if os.path.exists(sp):
        with open(sp, "r", errors="replace") as f:
            for line in f:
                if "r95s" in line or "r95b" in line:
                    rec["stream_properties_r95_rows"].append(line.strip()[:120])
    write_receipt("verify", cond, rec)
    return rec


STAGES = {
    "env": stage_env, "shape": stage_shape, "xconnect": stage_xconnect,
    "liveness": stage_liveness, "bytepath": stage_bytepath, "quantum": stage_quantum,
    "global": stage_global, "xrun": stage_xrun, "latency": stage_latency,
    "rtprio": stage_rtprio, "transport": stage_transport, "metadata": stage_metadata,
    "nameproj": stage_nameproj, "flags": stage_flags, "defaultnode": stage_defaultnode,
    "sibling": stage_sibling, "bufsize1": stage_bufsize1, "driverid": stage_driverid,
    "corner": stage_corner, "verify": stage_verify,
}

BATTERY = ["env", "shape", "xconnect", "liveness", "bytepath", "quantum",
           "xrun", "latency", "rtprio", "transport", "metadata", "nameproj"]

HOGS = Hogs()


def main():
    args = [a for a in sys.argv[1:]]
    cond = "q"
    reps = 3
    hogs = HOG_N
    stage_args = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--cond":
            cond = args[i + 1]
            i += 2
        elif a == "--reps":
            reps = int(args[i + 1])
            i += 2
        elif a == "--hogs":
            hogs = int(args[i + 1])
            i += 2
        else:
            stage_args.append(a)
            i += 1
    if not stage_args:
        print("stages:", " ".join(STAGES), "| all")
        return 2
    os.makedirs(RECEIPTS, exist_ok=True)
    os.makedirs(RUNS, exist_ok=True)
    os.makedirs(SCRATCH, exist_ok=True)
    HOGS.n = hogs
    t0 = time.time()
    started = None
    try:
        if cond == "h":
            started = HOGS.start()
            time.sleep(3)
        stages = BATTERY if stage_args[0] == "all" else stage_args
        for s in stages:
            if s not in STAGES:
                print("unknown stage", s)
                return 2
            st = time.time()
            rec = STAGES[s](cond, reps)
            print(json.dumps({"_stage": s, "_cond": cond, "_reps": reps,
                              "_wall_s": round(time.time() - st, 1),
                              "_load": loadavg(), "_hogs": HOGS.count()}))
            sys.stdout.flush()
    finally:
        if started is not None:
            HOGS.stop()
        final = sweep()
        print(json.dumps({"_sweep_final": final, "_wall_total_s": round(time.time() - t0, 1),
                          "_load_end": loadavg()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
