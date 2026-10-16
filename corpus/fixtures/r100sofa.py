#!/usr/bin/env python3
"""r100a — the sofa/spatializer HRTF rig (fixture source; round 100 author).

One leg per process:

    python3 r100sofa.py --leg <name> --scratch <dir> [axis options]

prints exactly one `R100AJSON {json}` line on stdout and exits 0 (2 when the
leg itself could not be armed — the JSON is still emitted). The
`--probe-sofa-r100` family in `measure_audio.py` drives this rig and owns the
law arming; this file owns the arming shape, the capture, the analysis and the
teardown.

Self-contained on purpose. It does NOT import the r92-scout `pwlib` scratch
helper (an untracked live file) that the r100 scout and boundary rigs both
imported: a verifier must be able to run this rig from tracked bytes alone.
The bounded-child, pw-cli session, WAV I/O and DSP helpers are re-implemented
here with the same semantics (own session per child, `RLIMIT_CORE=0` so a
pw-cli abort cannot drop a core file, SIGTERM -> SIGKILL process-group
escalation).

Discipline inherited from the r95 family (the r95 sweep incident precedent):

* every created object is `<ns>_*`, with `--ns` supplied by the family
  (`r100a_<family pid>`); foreign objects are CENSUSED, never touched;
* the module/sink unload re-reads the module table immediately before firing
  and unloads only the index whose own args carry our token — a captured id is
  never fired blindly (index recycling is immediate on this host);
* `pactl set-default-sink` / `set-default-source` is never issued;
* every child is its own session leader and dies by process-group escalation.

The `pw-cli`-loaded filter chain lives in that client's context (its module
var is addressable only from that session), so the leg keeps one `pw-cli`
session open for its whole life and unloads through it, then closes it.
"""

import argparse
import hashlib
import itertools
import json
import math
import os
import re
import resource
import select
import signal
import struct
import subprocess
import sys
import time
import wave

SOFA = "/usr/share/libmysofa/MIT_KEMAR_normal_pinna.sofa"
DEFAULT_SOFA = "/usr/share/libmysofa/default.sofa"
FC_MODULE = "libpipewire-module-filter-chain"

TOOL_COMMS = ("pw-play", "pw-record", "pw-cli", "pw-link", "pw-dump",
              "pw-cat", "pactl", "pipewire")

JSON_PREFIX = "R100AJSON "
WALL_DEFAULT = 8.0
BYTE_CAP = 8 << 20

# Set from --pw-env: when present, every PipeWire child of this leg runs
# against a SEAT-OWNED private core (PIPEWIRE_RUNTIME_DIR / XDG_* redirected),
# and the driver sink is created with `pw-cli create-node adapter` instead of
# `pactl load-module` (a private core has no pulse server). The parent owns the
# core + session-manager lifecycle; this rig only uses the socket.
PW_ENV = {}
PRIVATE = False
DRIVER = "pactl"

# Every bounded child call is timed (the report's own slowness evidence, and
# the reason a leg costs what it costs).
CALLS = []
DEBUG_LEVEL = 3        # PIPEWIRE_DEBUG for the pw-cli client (plugin log lines)


def _env(extra=None):
    e = dict(os.environ)
    e.update(PW_ENV)
    if extra:
        e.update(extra)
    return e


def _ncore():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


# ------------------------------------------------------------------ children
class Bounded:
    """One child with wall/byte bounds, its own session, no core files."""

    def __init__(self, argv, wall=WALL_DEFAULT, env=None, stdin_data=None):
        self.argv = [str(a) for a in argv]
        self.timed_out = False
        self.byte_capped = False
        self.rc = None
        self.spawn_error = None
        e = _env(env)
        t0 = time.time()
        try:
            p = subprocess.Popen(
                self.argv,
                stdin=subprocess.PIPE if stdin_data is not None
                else subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                start_new_session=True, preexec_fn=_ncore, env=e)
        except OSError as exc:
            self.spawn_error = str(exc)[:160]
            self.out = self.err = ""
            self.dur = time.time() - t0
            return
        self.pid = p.pid
        try:
            out, err = p.communicate(input=stdin_data, timeout=wall)
            self.rc = p.returncode
        except subprocess.TimeoutExpired:
            self.timed_out = True
            self._killpg(signal.SIGKILL)
            try:
                out, err = p.communicate(timeout=4)
            except subprocess.TimeoutExpired:
                out, err = b"", b""
            self.rc = p.returncode
        self.dur = time.time() - t0
        if len(CALLS) < 500:
            CALLS.append({"argv": " ".join(self.argv[:4])[:120],
                          "dur": round(self.dur, 3), "rc": self.rc,
                          "timed_out": self.timed_out})
        self.out = out.decode("utf-8", "replace")
        self.err = err.decode("utf-8", "replace")
        if len(self.out) > BYTE_CAP:
            self.byte_capped = True
            self.out = self.out[:BYTE_CAP]

    def _killpg(self, sig):
        try:
            os.killpg(os.getpgid(self.pid), sig)
        except (ProcessLookupError, PermissionError, OSError):
            pass

    def as_dict(self, keep=600):
        return {"argv": self.argv, "rc": self.rc,
                "dur": round(self.dur, 3), "timed_out": self.timed_out,
                "spawn_error": self.spawn_error,
                "out": self.out[-keep:], "err": self.err[-keep:]}


def run(argv, wall=WALL_DEFAULT, env=None):
    return Bounded(argv, wall=wall, env=env)


class Bg:
    """A background child (player / recorder) with group escalation."""

    def __init__(self, argv, env=None):
        self.argv = [str(a) for a in argv]
        e = _env(env)
        self.spawn_error = None
        self.p = None
        try:
            self.p = subprocess.Popen(
                self.argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL, start_new_session=True,
                preexec_fn=_ncore, env=e)
        except OSError as exc:
            self.spawn_error = str(exc)[:160]

    @property
    def pid(self):
        return self.p.pid if self.p else None

    def stop(self, sig=signal.SIGTERM):
        """SIGTERM the group, SIGKILL on the bound; the real exit code is
        read off the Popen object after communicate() consumed the pipes."""
        if self.p is None:
            return {"argv": self.argv, "spawn_error": self.spawn_error}
        proc = self.p
        try:
            os.killpg(os.getpgid(proc.pid), sig)
        except (ProcessLookupError, PermissionError, OSError):
            pass
        try:
            out, err = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError, OSError):
                pass
            try:
                out, err = proc.communicate(timeout=4)
            except subprocess.TimeoutExpired:
                out, err = b"", b""
        self.p = None
        return {"argv": self.argv, "rc": proc.returncode,
                "out": out.decode("utf-8", "replace")[-300:],
                "err": err.decode("utf-8", "replace")[-300:]}


class PwCli:
    """Interactive pw-cli over a pipe (module load/unload inside one session)."""

    def __init__(self, env=None, idle=0.5, hard=6.0):
        self.idle = idle
        self.hard = hard
        self.log = []
        e = _env(env)
        self.spawn_error = None
        self.p = None
        try:
            self.p = subprocess.Popen(
                ["pw-cli"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, start_new_session=True, bufsize=0,
                env=e, preexec_fn=_ncore)
        except OSError as exc:
            self.spawn_error = str(exc)[:160]
            return
        self._read_until_idle()

    def _read_until_idle(self, idle=None, hard=None):
        idle = self.idle if idle is None else idle
        hard = self.hard if hard is None else hard
        buf = b""
        t0 = time.time()
        last = time.time()
        try:
            while time.time() - t0 < hard:
                r, _, _ = select.select([self.p.stdout], [], [], 0.15)
                if r:
                    chunk = os.read(self.p.stdout.fileno(), 65536)
                    if not chunk:
                        break
                    buf += chunk
                    last = time.time()
                elif time.time() - last > idle:
                    break
        except (OSError, ValueError):
            pass
        txt = buf.decode("utf-8", "replace")
        self.log.append(txt)
        return txt

    def cmd(self, line, idle=None, hard=None):
        if self.p is None:
            return ""
        try:
            self.p.stdin.write((line + "\n").encode())
            self.p.stdin.flush()
        except (BrokenPipeError, OSError, ValueError):
            return ""
        return self._read_until_idle(idle=idle, hard=hard)

    def load(self, module, args):
        out = self.cmd("load-module %s %s" % (module, args))
        var = None
        for line in out.splitlines():
            line = line.strip()
            if "= @module:" in line:
                try:
                    var = int(line.split("=")[0].strip())
                except ValueError:
                    pass
        return out, var

    def drain(self, idle=0.3, hard=2.0):
        """Read whatever the client has buffered. The filter chain's plugin
        log lines (`plugin_sofa.c` instantiate) are emitted when the graph is
        ACTIVATED, i.e. after the load returned — without an explicit drain
        they are lost with the session."""
        if self.p is None:
            return ""
        return self._read_until_idle(idle=idle, hard=hard)

    def close(self):
        if self.p is None:
            return self.log
        self.drain()
        try:
            self.p.stdin.write(b"quit\n")
            self.p.stdin.flush()
        except (BrokenPipeError, OSError, ValueError):
            pass
        try:
            self.p.wait(timeout=3)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(self.p.pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError, OSError):
                pass
            try:
                self.p.wait(timeout=2)
            except (subprocess.TimeoutExpired, OSError):
                pass
        self.p = None
        return self.log


# ------------------------------------------------------------------ host census
def loadavg():
    try:
        with open("/proc/loadavg") as f:
            p = f.read().split()
        return {"l1": float(p[0]), "l5": float(p[1]), "l15": float(p[2]),
                "running": p[3]}
    except (OSError, ValueError, IndexError):
        return {}


def _own_procs(ns):
    """Own-namespace processes, read from /proc (never `ps`): a pid whose
    cmdline carries our token AND whose comm is a PipeWire tool. The parent's
    private core/session manager never carry the token (and `wireplumber` is
    not in the tool set), so they can never be swept by a leg."""
    out = []
    try:
        pids = [d for d in os.listdir("/proc") if d.isdigit()]
    except OSError:
        return out
    for pid in pids:
        try:
            with open("/proc/%s/cmdline" % pid, "rb") as f:
                argv = f.read().decode("utf-8", "replace").split("\0")
            with open("/proc/%s/comm" % pid) as f:
                comm = f.read().strip()
        except OSError:
            continue
        line = " ".join(a for a in argv if a)
        if ns in line and comm in TOOL_COMMS and "pipewire.conf" not in line:
            out.append({"pid": int(pid), "comm": comm, "argv": line[:160]})
    return sorted(out, key=lambda r: r["pid"])


def modules_short():
    """`pactl list modules short` rows: (index, name, args). Empty in private
    mode — a seat-owned core has no pulse server, and a pw-cli-loaded module
    never appears in the pactl table anyway."""
    if PRIVATE:
        return []
    res = run(["pactl", "list", "modules", "short"], wall=10.0)
    rows = []
    for line in res.out.splitlines():
        parts = line.split("\t")
        if len(parts) >= 3 and parts[0].strip().isdigit():
            rows.append((int(parts[0].strip()), parts[1].strip(),
                         "\t".join(parts[2:])))
    return rows


def module_index_own(field, value):
    """The index whose OWN args carry `field=value`, re-read right now."""
    for idx, _name, args in modules_short():
        if ("%s=%s" % (field, value)) in args:
            return idx
    return None


def pw_objects():
    res = run(["pw-dump"], wall=15.0)
    try:
        return json.loads(res.out)
    except (ValueError, TypeError):
        return []


def own_nodes(ns):
    """Own-namespace PipeWire nodes: {name: {"id", "state"}}."""
    found = {}
    for obj in pw_objects():
        if not str(obj.get("type", "")).startswith("PipeWire:Interface:Node"):
            continue
        info = obj.get("info") or {}
        props = info.get("props") or {}
        nm = str(props.get("node.name") or "")
        if nm.startswith(ns):
            found[nm] = {"id": obj.get("id"), "state": info.get("state")}
    return found


def own_modules(ns):
    """Own-namespace PipeWire modules (pw-dump, not pactl: a pw-cli-loaded
    module never appears in the pactl table)."""
    found = []
    for obj in pw_objects():
        if not str(obj.get("type", "")).startswith("PipeWire:Interface:Module"):
            continue
        info = obj.get("info") or {}
        blob = "%s %s" % (info.get("name") or "", info.get("args") or "")
        if ns in blob:
            found.append({"id": obj.get("id"), "name": info.get("name"),
                          "args": (info.get("args") or "")[:200]})
    return found


def live(ns):
    nodes = own_nodes(ns)
    return {"nodes": sorted(nodes),
            "node_states": {k: v["state"] for k, v in nodes.items()},
            "modules": own_modules(ns),
            "pactl_modules": [r[0] for r in modules_short()
                              if ns in r[2]],
            "procs": _own_procs(ns)}


def foreign_census():
    """Observation only: other seats' r##[a-z]_ objects and foreign tools."""
    foreign = []
    for obj in pw_objects():
        if not str(obj.get("type", "")).startswith("PipeWire:Interface:Node"):
            continue
        nm = str(((obj.get("info") or {}).get("props") or {})
                 .get("node.name") or "")
        if re.match(r"r\d+[a-z]?_", nm):
            foreign.append(nm)
    return {"foreign_nodes": sorted(set(foreign))[:40]}


def sink_create(ns, name, rate):
    """The driver sink. Shared graph: `pactl load-module module-null-sink`
    (space-separated `sink_properties` — the r95 F4 artifact: the comma form
    parses as ONE property and leaves a wireplumber stream-properties row).
    Private core: `pw-cli create-node adapter` with `object.linger=true`, the
    r100b sandbox shape (a seat-owned core has no pulse server)."""
    if not PRIVATE:
        res = run(["pactl", "load-module", "module-null-sink",
                   "sink_name=%s" % name,
                   "channels=1", "rate=%d" % rate,
                   "sink_properties=state.restore-props=false"], wall=12.0)
        mid = None
        try:
            mid = int(res.out.strip().split()[-1])
        except (ValueError, IndexError):
            pass
        return {"driver": "pactl", "rc": res.rc, "module_id": mid,
                "node_id": None, "out": res.out.strip(),
                "err": res.err.strip()[-160:]}
    arg = ("{ factory.name=support.null-audio-sink node.name=%s "
           "media.class=Audio/Sink object.linger=true "
           "audio.position=[MONO] }" % name)
    res = run(["pw-cli", "create-node", "adapter", arg], wall=20.0)
    node = None
    for _ in range(12):
        node = own_nodes(ns).get(name)
        if node:
            break
        time.sleep(0.4)
    return {"driver": "pw-cli", "rc": res.rc, "module_id": None,
            "node_id": (node or {}).get("id"), "out": res.out.strip()[-200:],
            "err": res.err.strip()[-160:]}


def sink_destroy(ns, name, handle):
    """Name-verified teardown of the driver. Shared graph: the index must come
    from a fresh table read and carry our own `sink_name=` (a captured id is
    never fired blindly — index recycling is immediate on this host). Private
    core: the node id must still map to our own node name."""
    if not PRIVATE:
        idx = module_index_own("sink_name", name)
        res = {"value": name, "captured": (handle or {}).get("module_id"),
               "verified_index": idx}
        if idx is None:
            res["skipped"] = "not_listed"
            return res
        res["recycled"] = (handle.get("module_id") is not None
                           and idx != handle["module_id"])
        res["rc"] = run(["pactl", "unload-module", str(idx)], wall=12.0).rc
        return res
    cur = own_nodes(ns).get(name) or {}
    res = {"value": name, "captured": (handle or {}).get("node_id"),
           "verified_index": cur.get("id")}
    if cur.get("id") is None:
        res["skipped"] = "not_listed"
        return res
    res["recycled"] = (handle.get("node_id") is not None
                       and cur["id"] != handle["node_id"])
    res["rc"] = run(["pw-cli", "destroy", str(cur["id"])], wall=12.0).rc
    return res


def sweep(ns):
    """Unload/destroy/kill ONLY own-namespace objects. Foreign objects are
    counted, never signalled."""
    before = live(ns)
    unloaded = []
    for idx, name, args in modules_short():
        if ns in args:
            unloaded.append({"index": idx, "name": name,
                             "rc": run(["pactl", "unload-module", str(idx)],
                                       wall=10.0).rc})
    killed = []
    for p in before["procs"]:
        try:
            os.kill(int(p["pid"]), signal.SIGKILL)
            killed.append(p["pid"])
        except (ProcessLookupError, PermissionError, OSError):
            pass
    destroyed = []
    for nm, meta in sorted(own_nodes(ns).items()):
        if meta.get("id") is None:
            continue
        destroyed.append({"name": nm, "id": meta["id"],
                          "rc": run(["pw-cli", "destroy", str(meta["id"])],
                                    wall=10.0).rc})
    for m in before["modules"]:
        if m.get("id") is None:
            continue
        destroyed.append({"module": m["name"], "id": m["id"],
                          "rc": run(["pw-cli", "unload-module", str(m["id"])],
                                    wall=10.0).rc})
    time.sleep(0.5)
    after = live(ns)
    return {"before": before, "unloaded": unloaded, "killed": killed,
            "destroyed": destroyed, "after": after,
            "clean": not (after["nodes"] or after["modules"]
                          or after["procs"] or after["pactl_modules"])}


def clock_witness():
    """The live graph clock. `pw-cli info 0` gives the core's declared clock
    keys; `pw-metadata -n settings` gives the RUNNING graph's clock rows
    (clock.rate / clock.quantum / force-*), which is what witnesses a
    quantum/rate variant while the graph is actually streaming."""
    res = {"core": {}, "drivers": [], "settings": {}}
    meta = run(["pw-metadata", "-n", "settings"], wall=12.0)
    res["settings_rc"] = meta.rc
    for line in meta.out.splitlines():
        # the rows read `update: id:0 key:'clock.quantum' value:'1024' type:''`
        m = re.search(r"key:'([^']+)'\s+value:'([^']*)'", line)
        if m and m.group(1) in ("clock.rate", "clock.quantum",
                                "clock.force-rate", "clock.force-quantum",
                                "clock.allowed-rates", "clock.min-quantum",
                                "clock.max-quantum"):
            res["settings"][m.group(1)] = m.group(2)
    r = run(["pw-cli", "info", "0"], wall=25.0)
    res["core_rc"] = r.rc
    for line in r.out.splitlines():
        s = line.strip().lstrip("*").strip()
        for k in ("default.clock.rate", "default.clock.quantum",
                  "default.clock.allowed-rates"):
            if s.startswith(k):
                res["core"][k] = s.split("=", 1)[1].strip().strip('"')
    for obj in pw_objects():
        if not str(obj.get("type", "")).startswith("PipeWire:Interface:Node"):
            continue
        info = obj.get("info") or {}
        props = info.get("props") or {}
        if props.get("node.driver") in (True, "true"):
            res["drivers"].append({"name": props.get("node.name"),
                                   "state": info.get("state"),
                                   "clock.rate": props.get("clock.rate"),
                                   "clock.quantum": props.get("clock.quantum")})
    return res


# ------------------------------------------------------------------ WAV + DSP
def write_wav(path, samples, rate=48000, ch=1):
    with wave.open(path, "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(2)
        w.setframerate(rate)
        frames = bytearray()
        if ch == 1:
            for s in samples:
                frames += struct.pack(
                    "<h", int(max(-1.0, min(1.0, s)) * 32767))
        else:
            for tup in samples:
                for s in tup:
                    frames += struct.pack(
                        "<h", int(max(-1.0, min(1.0, s)) * 32767))
        w.writeframes(bytes(frames))


def read_wav(path):
    with wave.open(path, "rb") as w:
        rate = w.getframerate()
        ch = w.getnchannels()
        sw = w.getsampwidth()
        n = w.getnframes()
        raw = w.readframes(n)
    if sw != 2:
        raise ValueError("sampwidth %d" % sw)
    vals = struct.unpack("<%dh" % (len(raw) // 2), raw)
    if ch > 1:
        chans = [vals[i::ch] for i in range(ch)]
    else:
        chans = [list(vals)]
    return {"rate": rate, "ch": ch, "sw": sw, "frames": n,
            "x": [[v / 32768.0 for v in c] for c in chans]}


def sha256_file(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
    except OSError:
        return None
    return h.hexdigest()


def best_window(x, win, stride, acc=None):
    """Max-energy window: returns (offset, rms).

    `stride` is the whole point of the r100 boundary's §3.1 falsification: the
    coarse recipe's `win // 10` stride is what makes the scout's published rms
    scatter at ~3e-5 across fresh processes, while stride 1 reproduces to ~1e-7.
    The scan is O(n) through prefix sums of squares (a naive stride-1 scan is
    O(n*win) and took 100 s per leg in pure Python), which selects the same
    argmax as the naive loop.
    """
    n = len(x)
    if n <= win:
        return 0, _rms(x)
    if acc is None:
        acc = list(itertools.accumulate((v * v for v in x), initial=0.0))
    best_e, bi = -1.0, 0
    for i in range(0, n - win + 1, stride):
        e = (acc[i + win] - acc[i]) / win
        if e > best_e:
            best_e, bi = e, i
    return bi, math.sqrt(max(0.0, best_e))


def _rms(x):
    if not x:
        return 0.0
    return math.sqrt(sum(v * v for v in x) / len(x))


def goertzel(x, f, rate):
    if not x:
        return 0.0
    w = 2 * math.pi * f / rate
    c = 2 * math.cos(w)
    s1 = s2 = 0.0
    for v in x:
        s0 = v + c * s1 - s2
        s2, s1 = s1, s0
    p = s1 * s1 + s2 * s2 - c * s1 * s2
    return 2.0 * math.sqrt(max(0.0, p)) / len(x)


def ild_db(l, r):
    return round(20 * math.log10(max(1e-12, l) / max(1e-12, r)), 4)


def _chan_metric(x, win, stride, tone, file_rate, acc=None):
    off, rms = best_window(x, win, stride, acc=acc)
    seg = x[off:off + win]
    return {"rms": round(rms, 8), "win_offset": off, "win": win,
            "stride": stride, "peak": round(max((abs(v) for v in x),
                                                default=0.0), 6),
            "tone": round(goertzel(seg, tone, file_rate), 8)}


def analyze(path, fc_rate, tone=440.0):
    """Three recipes, all recorded (the boundary's §3.1 lesson: never arm the
    coarse `best_window` rms, and never claim a cross-process bound on it):

    * `scout_coarse` — win = 0.4 s of the FILTER-CHAIN rate, stride = win//10:
      the r100 scout's published recipe (spread ~3e-5 across fresh processes);
    * `scout_fine`   — the same win, stride 1: the robust pin (~1e-7);
    * `file_coarse`  — win = 0.4 s of the FILE rate, stride = win//10 (the
      r100 boundary's `channels` recipe, kept as a cross-witness).
    """
    if not os.path.exists(path):
        return {"bytes": 0, "missing": True}
    w = read_wav(path)
    file_rate = w["rate"]
    res = {"bytes": os.path.getsize(path), "frames": w["frames"],
           "ch": w["ch"], "file_rate": file_rate,
           "sha256": sha256_file(path)}
    accs = [list(itertools.accumulate((v * v for v in x), initial=0.0))
            for x in w["x"]]
    win_fc = min(int(0.4 * fc_rate), max(1, w["frames"]))
    win_file = min(int(0.4 * file_rate), max(1, w["frames"]))
    recipes = (("scout_coarse", win_fc, max(1, win_fc // 10)),
               ("scout_fine", win_fc, 1),
               ("file_coarse", win_file, max(1, win_file // 10)))
    for tag, win, stride in recipes:
        res[tag] = {"win": win, "stride": stride, "channels": [
            _chan_metric(x, win, stride, tone, file_rate, acc=acc)
            for x, acc in zip(w["x"], accs)]}
        chans = res[tag]["channels"]
        if len(chans) >= 2:
            res[tag]["ild_db"] = ild_db(chans[0]["rms"], chans[1]["rms"])
            res[tag]["tone_ratio_db"] = round(
                20 * math.log10(max(1e-12, chans[0]["tone"])
                                / max(1e-12, chans[1]["tone"])), 4)
    res["peak"] = max((c["peak"] for c in res["scout_fine"]["channels"]),
                      default=0.0)
    res["nonzero"] = [sum(1 for v in x if v != 0.0) for x in w["x"]]
    return res


def analyze_series(path, win_ms=100):
    if not os.path.exists(path):
        return {"missing": True}
    w = read_wav(path)
    win = max(1, int(w["rate"] * win_ms / 1000.0))
    series = []
    for off in range(0, max(1, w["frames"] - win + 1), win):
        seg = [c[off:off + win] for c in w["x"]]
        rms = [_rms(s) for s in seg]
        series.append({"ms": round(off * 1000.0 / w["rate"], 1),
                       "rms": [round(v, 8) for v in rms],
                       "ild": ild_db(rms[0], rms[1]) if len(rms) >= 2 else None})
    return {"frames": w["frames"], "file_rate": w["rate"], "win_ms": win_ms,
            "series": series}


# ------------------------------------------------------------------ arming
def node_tok(rate, az=None, el=None, radius=None, filename=SOFA,
             extra_cfg=None, quote=False, ctl_order="config_first",
             no_config=False):
    if no_config:
        return "{type=sofa,name=s0,label=spatializer}"
    cfg = {"filename": filename}
    if extra_cfg:
        cfg.update(extra_cfg)
    ctl = {}
    if az is not None:
        ctl["Azimuth"] = az
    if el is not None:
        ctl["Elevation"] = el
    if radius is not None:
        ctl["Radius"] = radius
    q = '"' if quote else ""
    cfg_s = ",".join("%s%s%s=%s%s%s" % (q, k, q, q, v, q)
                     for k, v in cfg.items())
    ctl_s = ",".join("%s%s%s=%s%s%s" % (q, k, q, q, v, q)
                     for k, v in ctl.items())
    parts = ["config={%s}" % cfg_s, "control={%s}" % ctl_s]
    if ctl_order == "control_first":
        parts = list(reversed(parts))
    return "{type=sofa,name=s0,label=spatializer," + ",".join(parts) + "}"


def args_token(rate, ns, tok, order="base"):
    """The r92/r100 arming shape: inputs/outputs omitted (the plugin's own
    1-in/2-out ports), capture mono / playback stereo, no autoconnect."""
    base = [("node.description=%s_sofa" % ns, "nd"),
            ("filter.graph={nodes=[%s]}" % tok, "fg"),
            ("audio.channels=1", "ac"),
            ("audio.position=[MONO]", "ap"),
            ("audio.rate=%d" % rate, "ar"),
            ("capture.props={node.name=%s_sofa_in,node.autoconnect=false,"
             "media.class=Audio/Sink}" % ns, "cp"),
            ("playback.props={node.name=%s_sofa_out,node.autoconnect=false,"
             "audio.channels=2,audio.position=[FL,FR]}" % ns, "pp")]
    if order == "reversed":
        seq = list(reversed(base))
    elif order == "graph_last":
        seq = [t for t in base if t[1] != "fg"] + \
              [t for t in base if t[1] == "fg"]
    else:
        seq = base
    return ",".join(t[0] for t in seq)


def ports_of(node_name, env=None):
    out = (run(["pw-link", "-o"], wall=8.0, env=env).out
           + run(["pw-link", "-i"], wall=8.0, env=env).out)
    return sorted({l.strip() for l in out.splitlines() if node_name in l})


def node_id(name):
    for obj in pw_objects():
        if not str(obj.get("type", "")).startswith("PipeWire:Interface:Node"):
            continue
        if ((obj.get("info") or {}).get("props") or {}).get("node.name") == name:
            return obj.get("id")
    return None


def enum_props(name):
    nid = node_id(name)
    if nid is None:
        return {"node": name, "id": None, "error": "node not found"}
    out = run(["pw-cli", "enum-params", str(nid), "Props"], wall=12.0)
    txt = out.out
    res = {"node": name, "id": nid, "rc": out.rc, "bytes": len(txt),
           "has_azimuth": "Azimuth" in txt,
           "has_elevation": "Elevation" in txt,
           "has_radius": "Radius" in txt,
           "values": _ctl_values(txt)}
    keep = [l.strip()[:160] for l in txt.splitlines()
            if any(k in l for k in ("Azimuth", "Elevation", "Radius",
                                    "spatializer"))]
    res["lines"] = keep[:24]
    return res


def _ctl_values(txt):
    """Parse the `s0:Azimuth` control block out of an enum-params dump."""
    if not txt:
        return None
    lines = [l.strip() for l in txt.splitlines()]
    out = {}
    for i, l in enumerate(lines):
        m = re.match(r'^String "(s\d+):(Azimuth|Elevation|Radius)"$', l)
        if m and i + 1 < len(lines):
            mm = re.match(r"^(Float|Int|Double) ([-\d.eE+]+)$",
                          lines[i + 1])
            if mm:
                out["%s:%s" % (m.group(1), m.group(2))] = float(mm.group(2))
    return out


def set_ctl(name, key, value):
    """The boundary's accepted form: `{ params = [ "s0:<Key>" <v> ] }`."""
    nid = node_id(name)
    if nid is None:
        return {"node": name, "id": None, "error": "node not found"}
    before = enum_props(name)
    r = run(["pw-cli", "set-param", str(nid), "Props",
             '{ params = [ "s0:%s" %s ] }' % (key, value)], wall=12.0)
    after = enum_props(name)
    return {"node": name, "id": nid, "argv": r.argv, "rc": r.rc,
            "err": r.err.strip()[-200:], "values_before": before.get("values"),
            "values_after": after.get("values")}


def link(a, b, tries=12, env=None):
    last = None
    for i in range(tries):
        r = run(["pw-link", a, b], wall=6.0, env=env)
        last = r
        if r.rc == 0:
            return {"argv": [a, b], "rc": 0, "tries": i + 1}
        if "File exists" in r.err:
            return {"argv": [a, b], "rc": 0, "tries": i + 1, "note": "already"}
        time.sleep(0.25)
    return {"argv": [a, b], "rc": last.rc, "tries": tries,
            "err": last.err.strip()[-200:]}


def unlink(a, b):
    r = run(["pw-link", "-d", a, b], wall=6.0)
    return {"argv": ["-d", a, b], "rc": r.rc, "err": r.err.strip()[-160:]}


def fc_log_lines(log):
    keep = []
    for l in "\n".join(log).splitlines():
        low = l.lower()
        if any(k in low for k in ("spatializer", "sofa", "sampling rate",
                                  "using n_samples", "can't start graph",
                                  "error")):
            keep.append(l.strip()[:300])
    return keep[-40:]


def n_samples_of(log):
    for l in "\n".join(log).splitlines():
        m = re.search(r"using n_samples:(\d+)", l)
        if m:
            return int(m.group(1))
    return None


def rate_string_seen(log):
    return any("Only the same sampling rate supported" in l for l in log)


# ------------------------------------------------------------------ the leg
def run_leg(spec):
    ns = spec["ns"]
    scratch = spec["scratch"]
    rate = spec["rate"]
    os.makedirs(scratch, exist_ok=True)
    tag = spec.get("tag") or spec["leg"]
    row = {"leg": spec["leg"], "tag": tag, "ns": ns,
           "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "rate": rate, "azimuth": spec.get("az"), "elevation": spec.get("el"),
           "radius": spec.get("radius"), "quote": spec.get("quote", False),
           "swap_channels": spec.get("swap", False),
           "ref_tap": spec.get("ref_tap", False),
           "play": spec.get("play", "bg"),
           "tone": {"freq": spec.get("tone_hz", 440.0),
                    "secs": spec.get("tone_secs", 1.6),
                    "amp": spec.get("tone_amp", 0.5)},
           "post": spec.get("post"),
           "loadavg_start": loadavg()}
    pre = sweep(ns)
    row["pre_sweep"] = pre
    row["foreign_at_start"] = foreign_census()
    tok = node_tok(rate, az=spec.get("az"), el=spec.get("el"),
                   radius=spec.get("radius"),
                   filename=spec.get("filename", SOFA),
                   extra_cfg=spec.get("extra_cfg"),
                   quote=spec.get("quote", False),
                   ctl_order=spec.get("ctl_order", "config_first"),
                   no_config=spec.get("no_config", False))
    row["node_tok"] = tok
    row["argv_args"] = args_token(rate, ns, tok, order=spec.get("argv_order",
                                                               "base"))
    sink_name = "%s_in" % ns
    sink = sink_create(ns, sink_name, rate)
    sink_id = sink.get("module_id") or sink.get("node_id")
    row["sink"] = sink
    if sink_id is None:
        row["leg_error"] = "driver sink never enumerated"
        row["post_sweep"] = sweep(ns)
        row["loadavg_end"] = loadavg()
        return row
    cli = PwCli(env={"PIPEWIRE_DEBUG": str(DEBUG_LEVEL)}, idle=0.5,
                hard=4.0)
    if cli.p is None:
        row["leg_error"] = "pw-cli did not start: %s" % cli.spawn_error
        row["sink_unload"] = sink_destroy(ns, sink_name, sink)
        row["post_sweep"] = sweep(ns)
        row["loadavg_end"] = loadavg()
        return row
    out_wav = os.path.join(scratch, "cap_%s.wav" % tag)
    if os.path.exists(out_wav):
        os.unlink(out_wav)
    recp = refp = playp = None
    t0 = time.time()
    try:
        out, var = cli.load(FC_MODULE, row["argv_args"])
        row["load_out"] = out.strip()[-700:]
        row["module_var"] = var
        time.sleep(0.8)
        cli.drain()
        row["nodes_now"] = sorted(own_nodes(ns))
        row["ports_fc_in"] = ports_of("%s_sofa_in" % ns)
        row["ports_fc_out"] = ports_of("%s_sofa_out" % ns)
        recp = Bg(["pw-record", "--channels", "2",
                   "-P", "node.name=%s_rec" % ns,
                   "-P", "node.autoconnect=false", out_wav])
        time.sleep(0.8)
        row["ports_rec"] = ports_of("%s_rec" % ns)
        if spec.get("ref_tap"):
            refp = Bg(["pw-record", "--channels", "1",
                       "-P", "node.name=%s_ref" % ns,
                       "-P", "node.autoconnect=false",
                       os.path.join(scratch, "ref_%s.wav" % tag)])
            time.sleep(0.7)
            row["ports_ref"] = ports_of("%s_ref" % ns)
        row["links"] = []
        row["links"].append(link("%s:monitor_MONO" % sink_name,
                                 "%s_sofa_in:playback_MONO" % ns))
        if refp is not None:
            row["links"].append(link("%s:monitor_MONO" % sink_name,
                                     "%s_ref:input_MONO" % ns))
        pairs = ([("FL", "FR"), ("FR", "FL")] if spec.get("swap")
                 else [("FL", "FL"), ("FR", "FR")])
        for src, dst in pairs:
            row["links"].append(link("%s_sofa_out:output_%s" % (ns, src),
                                     "%s_rec:input_%s" % (ns, dst)))
        if spec.get("play", "bg") != "none":
            tone_path = os.path.join(scratch, "tone_%s_%s.wav"
                                     % (spec.get("tone_hz", 440.0), rate))
            if not os.path.exists(tone_path):
                n = int(rate * row["tone"]["secs"])
                write_wav(tone_path,
                          [row["tone"]["amp"] * math.sin(
                              2 * math.pi * row["tone"]["freq"] * i / rate)
                           for i in range(n)], rate=rate, ch=1)
            row["tone_file"] = tone_path
            tw = read_wav(tone_path)
            row["tone_file_rms"] = round(_rms(tw["x"][0]), 8)
            playp = Bg(["pw-play", "--target", sink_name,
                        "-P", "node.name=%s_play" % ns,
                        "-P", "node.autoconnect=false", tone_path])
            time.sleep(0.6)
            row["ports_play"] = ports_of("%s_play" % ns)
            pre_links = run(["pw-link", "-l"], wall=8.0).out
            policy = any(("%s_play" % ns) in l and sink_name in l
                         for l in pre_links.splitlines())
            row["play_link_origin"] = "policy" if policy else "manual"
            if not policy:
                row["links"].append(link("%s_play:output_MONO" % ns,
                                         "%s:playback_MONO" % sink_name,
                                         tries=4))
            row["clock_mid"] = clock_witness()
            evs = []
            t_play = time.time()
            for act in sorted(spec.get("post") or [],
                              key=lambda a: a.get("t", 0)):
                wait = t_play + float(act.get("t", 0)) - time.time()
                if wait > 0:
                    time.sleep(wait)
                evs.append(_post_action(act, row, ns, sink_name, sink))
            row["post_events"] = evs
            rec_secs = spec.get("rec_secs", 2.6)
            time.sleep(max(0.0, rec_secs - (time.time() - t_play)))
            row["play_stop"] = playp.stop()
            playp = None
        else:
            rec_secs = spec.get("rec_secs", 2.0)
            time.sleep(rec_secs)
        time.sleep(0.5)
        if recp is not None:
            row["rec"] = recp.stop()
            recp = None
        if refp is not None:
            row["ref"] = refp.stop()
            refp = None
        cli.drain()          # the plugin's activation log lines live here
        row["analysis"] = analyze(out_wav, rate,
                                  tone=spec.get("tone_hz", 440.0))
        if spec.get("ref_tap"):
            row["ref_analysis"] = analyze(
                os.path.join(scratch, "ref_%s.wav" % tag), rate,
                tone=spec.get("tone_hz", 440.0))
        if spec.get("series"):
            row["series"] = analyze_series(out_wav)
        row["links_after"] = [l.strip() for l in
                              run(["pw-link", "-l"], wall=8.0).out.splitlines()
                              if ns in l]
        row["props_enum_in"] = enum_props("%s_sofa_in" % ns)
        row["props_enum_out"] = enum_props("%s_sofa_out" % ns)
        # --- verified unload: re-read the module table, require OUR token
        #     on the captured index, unload only then.
        if var is not None:
            # A pw-cli-loaded module is CLIENT-LOCAL: it never appears in the
            # global registry (pw-dump / `pw-cli ls Module` list only the
            # daemon's own modules), so the index cannot be re-verified against
            # a global table — it is verified against the SESSION that loaded it
            # plus the own-namespace nodes the module created, and the unload's
            # effect is re-measured.
            before_nodes = sorted(own_nodes(ns))
            row["module_unload_verified"] = {
                "captured": var, "client_local": True,
                "global_registry_seen": sorted(m.get("id")
                                               for m in own_modules(ns)),
                "own_nodes_before": before_nodes,
                "matched": bool(before_nodes)}
            if before_nodes:
                try:
                    row["unload"] = cli.cmd(
                        "unload-module %d" % var, idle=0.4, hard=3.0)[-300:]
                except Exception as exc:            # a dead pw-cli must not
                    row["unload"] = {"error": repr(exc)}  # kill the leg
                time.sleep(0.4)
                row["module_unload_verified"]["own_nodes_after"] = \
                    sorted(own_nodes(ns))
            else:
                row["unload"] = {"skipped": "no own nodes to verify against"}
    except Exception as exc:
        row["leg_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        for p in (recp, refp, playp):
            if p is not None:
                row.setdefault("cleanup_stops", []).append(p.stop())
        full = cli.close()
        row["fc_log"] = fc_log_lines(full)
        row["fc_log_all_tail"] = [l.strip()[:200] for l in
                                  "\n".join(full).splitlines()][-80:]
        row["n_samples"] = n_samples_of(full)
        row["rate_string_seen"] = rate_string_seen(full)
        row["sink_unload"] = sink_destroy(ns, sink_name, sink)
        time.sleep(0.4)
        row["post_sweep"] = sweep(ns)
    row["loadavg_end"] = loadavg()
    row["wall_s"] = round(time.time() - t0, 2)
    row["calls"] = {"n": len(CALLS),
                    "timed_out": [c for c in CALLS if c["timed_out"]],
                    "slowest": sorted(CALLS, key=lambda c: -c["dur"])[:10]}
    return row


def _post_action(act, row, ns, sink_name, sink):
    key = act.get("do")
    at = act.get("t")
    if key == "set_azimuth":
        return {"at": at, "action": key,
                "result": set_ctl(act.get("node") or ("%s_sofa_in" % ns),
                                  act.get("key", "Azimuth"),
                                  act.get("value", 90.0))}
    if key == "relink_out":
        u = unlink("%s_sofa_out:output_FL" % ns, "%s_rec:input_FL" % ns)
        time.sleep(0.35)
        r = link("%s_sofa_out:output_FL" % ns, "%s_rec:input_FL" % ns)
        return {"at": at, "action": key, "unlink": u, "relink": r}
    return {"at": at, "action": key, "result": "unknown-action"}


# ------------------------------------------------------------------ main
def build_spec(args):
    spec = {"leg": args.leg, "ns": args.ns, "scratch": args.scratch,
            "rate": args.rate, "az": args.az, "el": args.el,
            "radius": args.radius, "filename": args.filename,
            "quote": args.quote, "swap": args.swap, "ref_tap": args.ref_tap,
            "no_config": args.no_config,
            "play": args.play, "tone_hz": args.tone_hz,
            "tone_secs": args.tone_secs, "tone_amp": args.tone_amp,
            "rec_secs": args.rec_secs, "series": args.series,
            "argv_order": args.argv_order, "ctl_order": args.ctl_order,
            "tag": args.tag}
    if args.extra_cfg:
        spec["extra_cfg"] = json.loads(args.extra_cfg)
    if args.post:
        spec["post"] = json.loads(args.post)
    return spec


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--leg", required=True)
    ap.add_argument("--ns", default="r100a_%d" % os.getpid())
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--tag", default=None)
    ap.add_argument("--rate", type=int, default=44100)
    ap.add_argument("--az", type=float, default=None)
    ap.add_argument("--el", type=float, default=None)
    ap.add_argument("--radius", type=float, default=None)
    ap.add_argument("--filename", default=SOFA)
    ap.add_argument("--extra-cfg", default=None,
                    help="JSON object merged into the plugin config token")
    ap.add_argument("--no-config", action="store_true",
                    help="the bare {type=sofa,name=s0,label=spatializer} token "
                         "(the silent-failure class: refused at ACTIVATION)")
    ap.add_argument("--quote", action="store_true",
                    help="the quoted token form (the boundary's silent "
                         "control-drop falsifier)")
    ap.add_argument("--swap", action="store_true",
                    help="cross the FC outputs into the recorder ports")
    ap.add_argument("--ref-tap", action="store_true",
                    help="also record the sink monitor (the FC's real input)")
    ap.add_argument("--play", choices=("bg", "none"), default="bg")
    ap.add_argument("--tone-hz", type=float, default=440.0)
    ap.add_argument("--tone-secs", type=float, default=1.6)
    ap.add_argument("--tone-amp", type=float, default=0.5)
    ap.add_argument("--rec-secs", type=float, default=2.6)
    ap.add_argument("--series", action="store_true")
    ap.add_argument("--argv-order", default="base")
    ap.add_argument("--ctl-order", default="config_first")
    ap.add_argument("--post", default=None, help="JSON list of mid-stream actions")
    ap.add_argument("--debug", type=int, default=3,
                    help="PIPEWIRE_DEBUG for the pw-cli client")
    ap.add_argument("--pw-env", default=None,
                    help="JSON object of env vars for every PipeWire child; "
                         "its presence selects the seat-owned private core "
                         "(pw-cli driver sink, no pactl)")
    args = ap.parse_args(argv)
    global PW_ENV, PRIVATE, DRIVER, DEBUG_LEVEL
    DEBUG_LEVEL = args.debug
    if args.pw_env:
        PW_ENV = json.loads(args.pw_env)
        PRIVATE = True
        DRIVER = "pw-cli"
    row = run_leg(build_spec(args))
    attempts = 1
    while (not row.get("leg_error")
           and (row.get("analysis") or {}).get("frames") == 0
           and attempts < 2):
        # the r100 boundary's retry rule: a ZERO-FRAME capture is rig flake
        # (10/136 legs there) and gets one fresh process; an rms of 0 with
        # frames > 0 is a legitimate reading (the no-config cell) and is never
        # retried.
        attempts += 1
        row = run_leg(build_spec(args))
    row["attempts"] = attempts
    row["mode"] = {"private_core": PRIVATE, "driver": DRIVER,
                   "pw_env_keys": sorted(PW_ENV)}
    row["host"] = {"pipewire": run(["pw-cli", "--version"], wall=8.0)
                   .out.strip()[:80],
                   "sofa_sha256": sha256_file(SOFA),
                   "default_sofa_sha256": sha256_file(DEFAULT_SOFA),
                   "sofa_is_symlink": os.path.islink(DEFAULT_SOFA),
                   "default_sofa_realpath": (os.path.realpath(DEFAULT_SOFA)
                                             if os.path.exists(DEFAULT_SOFA)
                                             else None)}
    print(JSON_PREFIX + json.dumps(row, allow_nan=False))
    return 0 if not row.get("leg_error") else 2


if __name__ == "__main__":
    sys.exit(main())
