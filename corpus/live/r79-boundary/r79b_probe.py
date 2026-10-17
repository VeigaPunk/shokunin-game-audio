#!/usr/bin/env python3
"""R79 BOUNDARY harness — the pw-loopback edges the r79 arms did not probe.

Self-contained: own tone, own graph reader, own classifier. Never imports,
reads or executes `corpus/fixtures/measure_audio.py` (sibling-owned, dirty).

Contamination discipline (the r79 scout's fail-closed rule):
  * tone only ever enters probe-owned null sinks (`r79b_<pid>_ns_*`);
  * any leg whose effective destination can be the shared default sink runs
    with NO tone (silence / topology witness only);
  * every leg is bounded (outer `timeout -s KILL`), torn down in a `finally`,
    and the run ends with a verification that no `r79b_` object survives.

Groups (subcommand = g1..g7):
  g1 both -C and -P in one client (resolvable / unresolvable mixes)
  g2 kill the loopback client mid-capture (teardown + attached consumer)
  g3 two loopbacks targeting each other (cycle / recirculation)
  g4 target props written with pw-cli set-param mid-stream
  g5 pw-record / pw-loopback numeric (serial / id) vs name targets
  g6 loopback against a suspended target (idle, mid-route, at spawn)
  g7 target.object at the loopback's own peer (self-binding)
"""
import json
import math
import os
import signal
import subprocess
import sys
import time
import wave
from pathlib import Path

import numpy as np

SEAT = Path(__file__).resolve().parent
RAW = SEAT / "raw"
SCRATCH = SEAT / "scratch"
for _d in (RAW, SCRATCH):
    _d.mkdir(parents=True, exist_ok=True)

PID = os.getpid()
PREFIX = f"r79b_{PID}"
RATE = 48000
TONE_AMP = 8192
L_HZ, R_HZ = 1000.0, 1500.0
TONE_WAV = SCRATCH / f"tone_{PID}.wav"
BURST_WAV = SCRATCH / f"burst_{PID}.wav"
BURST_S = 0.25

PROCS = []          # (label, Popen)
SINKS = {}          # name -> module id


# --------------------------------------------------------------- subprocess

def sh(argv, timeout=15.0, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    t0 = time.monotonic()
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout, env=e)
        return {"rc": p.returncode, "out": p.stdout.decode(errors="replace"),
                "err": p.stderr.decode(errors="replace"),
                "wall": round(time.monotonic() - t0, 3), "timeout": False,
                "argv": list(argv)}
    except subprocess.TimeoutExpired as exc:
        return {"rc": None, "out": (exc.stdout or b"").decode(errors="replace"),
                "err": (exc.stderr or b"").decode(errors="replace"),
                "wall": round(time.monotonic() - t0, 3), "timeout": True,
                "argv": list(argv)}
    except OSError as exc:
        return {"rc": None, "out": "", "err": f"spawn failed: {exc}",
                "wall": round(time.monotonic() - t0, 3), "timeout": False,
                "argv": list(argv)}


def spawn(argv, label="proc"):
    p = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                         stderr=subprocess.PIPE, start_new_session=True)
    PROCS.append((label, p))
    return p


def kill(p, sig=signal.SIGKILL):
    if p is None:
        return
    try:
        os.killpg(os.getpgid(p.pid), sig)
    except (ProcessLookupError, PermissionError):
        pass
    try:
        p.wait(timeout=3)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
        p.wait(timeout=3)


def popen_err(p):
    try:
        return (p.stderr.read() or b"").decode(errors="replace") if p.stderr else ""
    except Exception as exc:
        return f"<stderr read failed: {exc}>"


def reap(p, wait=8.0):
    t0 = time.monotonic()
    try:
        p.wait(timeout=wait)
    except subprocess.TimeoutExpired:
        pass
    kill(p)
    return {"wall_s": round(time.monotonic() - t0, 2), "rc": p.returncode,
            "stderr": popen_err(p)[:600]}


# ------------------------------------------------------------------- graph

def pw_dump():
    r = sh(["pw-dump"], timeout=15.0)
    if r["rc"] != 0:
        return None
    try:
        return json.loads(r["out"])
    except json.JSONDecodeError:
        return None


def graph_now(tries=6, pause=0.4):
    for _ in range(tries):
        objs = pw_dump()
        if objs is not None:
            return Graph(objs)
        time.sleep(pause)
    return Graph([])


class Graph:
    def __init__(self, objs):
        self.nodes, self.by_id, self.ports, self.links, self.clients = {}, {}, {}, [], {}
        for o in objs or []:
            t = o.get("type", "").split(":")[-1]
            info = o.get("info", {}) or {}
            props = info.get("props", {}) or {}
            if t == "Node":
                nm = props.get("node.name", "")
                self.nodes[nm] = {
                    "id": o["id"], "serial": props.get("object.serial"),
                    "class": props.get("media.class", ""),
                    "state": info.get("state"),
                    "props": props, "in": [], "out": []}
                self.by_id[o["id"]] = nm
            elif t == "Port":
                self.ports[o["id"]] = {
                    "node_id": props.get("node.id"),
                    "name": props.get("port.name", ""),
                    "dir": info.get("direction", "")}
            elif t == "Client":
                self.clients[o["id"]] = props
        for o in objs or []:
            if o.get("type", "").endswith("Link"):
                i = o.get("info", {}) or {}
                on = self.by_id.get(i.get("output-node-id"))
                op = self.ports.get(i.get("output-port-id"), {})
                inn = self.by_id.get(i.get("input-node-id"))
                ip = self.ports.get(i.get("input-port-id"), {})
                self.links.append({"out_node": on, "out_port": op.get("name"),
                                   "in_node": inn, "in_port": ip.get("name"),
                                   "state": i.get("state")})
        for o in objs or []:
            if o.get("type", "").endswith("Port"):
                p = self.ports[o["id"]]
                nm = self.by_id.get(p["node_id"])
                if nm in self.nodes:
                    (self.nodes[nm]["in"] if p["dir"] == "input"
                     else self.nodes[nm]["out"]).append((p["name"], o["id"]))

    def node(self, name):
        return self.nodes.get(name)

    def brief(self, name):
        n = self.nodes.get(name)
        if not n:
            return {"present": False}
        return {"present": True, "id": n["id"], "serial": n["serial"],
                "class": n["class"], "state": n["state"],
                "target_object": n["props"].get("target.object"),
                "autoconnect": n["props"].get("node.autoconnect"),
                "ports_in": [p[0] for p in n["in"]],
                "ports_out": [p[0] for p in n["out"]]}

    def edges(self, substr):
        out = []
        for l in self.links:
            if substr in (l["out_node"] or "") or substr in (l["in_node"] or ""):
                out.append(f"{l['out_node']}:{l['out_port']} -> "
                           f"{l['in_node']}:{l['in_port']}")
        return sorted(out)

    def peers(self, node, side):
        src, dst = set(), set()
        for l in self.links:
            if l["out_node"] == node:
                dst.add(f"{l['in_node']}:{l['in_port']}")
            if l["in_node"] == node:
                src.add(f"{l['out_node']}:{l['out_port']}")
        return sorted(src if side == "in" else dst)

    def find(self, substr):
        return sorted(n for n in self.nodes if substr in n)


def nodes_with_prefix(g, prefix=PREFIX):
    return [n for n in g.nodes if prefix in n]


def find_by_serial(g, serial):
    for nm, n in g.nodes.items():
        if str(n.get("serial")) == str(serial):
            return nm
    return None


# --------------------------------------------------------------- metadata

def metadata():
    r = sh(["pw-metadata", "-n", "default", "0"], timeout=8.0)
    keys = {}
    for line in r["out"].splitlines():
        if "key:'" not in line:
            continue
        key = line.split("key:'", 1)[1].split("'", 1)[0]
        val = line.split("value:'", 1)[1].split("'", 1)[0] if "value:'" in line else ""
        keys[key] = val
    return keys


def host_snapshot():
    g = Graph(pw_dump())
    r = sh(["pgrep", "-af", "measure_audio|pw-loopback|pw-record|parec|pw-cat"],
           timeout=8.0)
    foreign = [l for l in r["out"].splitlines()
               if l.strip() and f" {PREFIX}" not in l and "r79b_" not in l]
    md = metadata()
    return {"t": round(time.time(), 3),
            "default_sink": md.get("default.audio.sink"),
            "default_source": md.get("default.audio.source"),
            "nodes_total": len(g.nodes),
            "foreign_r7x_nodes": sorted(n for n in g.nodes if n.startswith(("r78", "r79", "r8"))),
            "foreign_procs": foreign[:12]}


# --------------------------------------------------------------- null sinks

def null_sink(name):
    r = sh(["pactl", "load-module", "module-null-sink", f"sink_name={name}"],
           timeout=10.0)
    mid = None
    if r["rc"] == 0 and r["out"].strip().isdigit():
        mid = int(r["out"].strip())
    SINKS[name] = mid
    return {"name": name, "module_id": mid, "rc": r["rc"], "err": r["err"].strip()}


def null_sink_unload(name):
    mid = SINKS.pop(name, None)
    if mid is None:
        return {"rc": None, "err": "no module id"}
    return sh(["pactl", "unload-module", str(mid)], timeout=10.0)


def sink_state(name):
    r = sh(["pactl", "list", "sinks", "short"], timeout=8.0)
    for line in r["out"].splitlines():
        parts = line.split("\t")
        if len(parts) >= 6 and parts[1] == name:
            return {"index": parts[0], "state": parts[5]}
    return {"index": None, "state": "absent"}


# ---------------------------------------------------------------- tone/rec

def make_wavs():
    n = int(RATE * 20)
    t = np.arange(n) / RATE
    L = (TONE_AMP * np.sin(2 * np.pi * L_HZ * t)).astype("<i2")
    R = (TONE_AMP * np.sin(2 * np.pi * R_HZ * t)).astype("<i2")
    _write(TONE_WAV, np.stack([L, R], axis=1))
    n2 = int(RATE * 9)
    t2 = np.arange(n2) / RATE
    L2 = (TONE_AMP * np.sin(2 * np.pi * L_HZ * t2)).astype("<i2")
    R2 = (TONE_AMP * np.sin(2 * np.pi * R_HZ * t2)).astype("<i2")
    m = t2 >= BURST_S
    L2[m], R2[m] = 0, 0
    _write(BURST_WAV, np.stack([L2, R2], axis=1))


def _write(path, a):
    w = wave.open(str(path), "wb")
    w.setnchannels(a.shape[1])
    w.setsampwidth(2)
    w.setframerate(RATE)
    w.writeframes(a.astype("<i2").tobytes())
    w.close()


def _tone(seconds, hz, amp=TONE_AMP):
    n = int(RATE * seconds)
    t = np.arange(n) / RATE
    x = (amp * np.sin(2 * np.pi * hz * t)).astype("<i2")
    return np.stack([x, x], axis=1)


def tone_start(sink, tag, burst=False, seconds=None, wav=None):
    argv = ["pw-cat", "-p", "-P", f"node.name={tag}",
            "--target", sink, str(wav or (BURST_WAV if burst else TONE_WAV))]
    if seconds:
        argv = ["timeout", "-s", "KILL", str(seconds)] + argv
    return spawn(argv, tag)


def rec_run(target, path, frames, tag, capture_sink=False, timeout=20.0):
    argv = ["pw-record", "-P", f"node.name={tag}"]
    if capture_sink:
        argv += ["-P", "stream.capture.sink=true"]
    argv += ["--target", target, "-n", str(frames), str(path)]
    r = sh(argv, timeout=timeout)
    r.update({"path": str(path), "exists": os.path.exists(path),
              "bytes": os.path.getsize(path) if os.path.exists(path) else 0})
    return r


def rec_start(target, path, frames, tag, capture_sink=False):
    argv = ["pw-record", "-P", f"node.name={tag}"]
    if capture_sink:
        argv += ["-P", "stream.capture.sink=true"]
    argv += ["--target", target, "-n", str(frames), str(path)]
    p = spawn(argv, tag)
    return {"proc": p, "path": str(path), "argv": argv, "tag": tag}


# --------------------------------------------------------------- analysis

def wav_error(path):
    if not os.path.exists(path):
        return "missing"
    try:
        w = wave.open(str(path))
        w.getnframes()
        w.close()
        return None
    except Exception as exc:
        return f"{type(exc).__name__}: {exc}"


def analyze(path):
    res = {"path": str(path), "exists": os.path.exists(path)}
    if not res["exists"]:
        return res
    try:
        w = wave.open(str(path))
    except Exception as exc:
        res["error"] = f"wave: {exc}"
        return res
    n, ch, sw, rate = (w.getnframes(), w.getnchannels(), w.getsampwidth(),
                       w.getframerate())
    raw = w.readframes(n)
    res.update(frames=n, ch=ch, rate=rate, bytes=os.path.getsize(path))
    if sw != 2 or n == 0:
        res["class"] = "non_s16" if sw != 2 else "empty"
        return res
    a = np.frombuffer(raw, dtype="<i2").astype(np.float64)
    a = a[:(len(a) // ch) * ch].reshape(-1, ch)
    res["peak"] = [int(np.abs(a[:, c]).max()) for c in range(ch)]
    res["rms"] = [round(float(np.sqrt((a[:, c] ** 2).mean())), 1)
                  for c in range(ch)]
    mid = a[len(a) // 4: len(a) // 4 + min(len(a) // 2, rate)]
    dom = []
    for c in range(ch):
        if len(mid) < 256:
            dom.append({"hz": None, "amp": 0.0})
            continue
        win = mid[:, c] * np.hanning(len(mid))
        sp = np.abs(np.fft.rfft(win))
        k = int(np.argmax(sp))
        dom.append({"hz": round(k * rate / len(mid), 1),
                    "amp": round(float(sp[k]) * 2 / np.hanning(len(mid)).sum(), 1)})
    res["dom"] = dom
    cls = []
    for c in range(ch):
        pk = res["peak"][c]
        hz, amp = dom[c]["hz"], dom[c]["amp"]
        if pk <= 64:
            cls.append("silence")
        elif hz is not None and abs(hz - L_HZ) <= 30 and amp > 0.15 * TONE_AMP:
            cls.append("tone1k")
        elif hz is not None and abs(hz - R_HZ) <= 30 and amp > 0.15 * TONE_AMP:
            cls.append("tone1.5k")
        elif pk >= 200:
            cls.append(f"foreign@{hz}Hz")
        else:
            cls.append(f"noise@{hz}Hz")
    res["class"] = cls
    res["carries_tone"] = any(c.startswith("tone") for c in cls)
    return res


def gamp(x, hz):
    n = len(x)
    if n < 32:
        return 0.0
    t = np.arange(n) / RATE
    re = float(np.dot(x, np.cos(2 * np.pi * hz * t))) * 2 / n
    im = float(np.dot(x, np.sin(2 * np.pi * hz * t))) * 2 / n
    return math.hypot(re, im)


def tone_timeline(path, hz=L_HZ, win_ms=50, step_ms=25):
    """[(t_s, amp)] of a Goertzel scan over channel 0 ([] if unreadable)."""
    if not os.path.exists(path):
        return []
    try:
        w = wave.open(str(path))
    except Exception:
        return []
    n, ch = w.getnframes(), w.getnchannels()
    a = np.frombuffer(w.readframes(n), dtype="<i2").astype(np.float64)
    a = a[:(len(a) // ch) * ch].reshape(-1, ch)[:, 0]
    w.close()
    win, step = int(RATE * win_ms / 1000), int(RATE * step_ms / 1000)
    out = []
    for s in range(0, max(len(a) - win, 1), step):
        out.append((round(s / RATE, 3), round(gamp(a[s:s + win], hz), 1)))
    return out


def tone_span(path, hz=L_HZ, thr=1024):
    tl = tone_timeline(path, hz=hz)
    on = [t for t, a in tl if a > thr]
    return {"windows": len(tl), "first_tone_s": on[0] if on else None,
            "last_tone_s": on[-1] if on else None,
            "tone_windows": len(on),
            "max_amp": max((a for _, a in tl), default=0.0)}


def tone_timeline2(path, hzs, win_ms=50, step_ms=50):
    """[(t, amp@hz0, amp@hz1, ...)] over channel 0."""
    if not os.path.exists(path):
        return []
    try:
        w = wave.open(str(path))
    except Exception:
        return []
    n, ch = w.getnframes(), w.getnchannels()
    a = np.frombuffer(w.readframes(n), dtype="<i2").astype(np.float64)
    a = a[:(len(a) // ch) * ch].reshape(-1, ch)[:, 0]
    w.close()
    win, step = int(RATE * win_ms / 1000), int(RATE * step_ms / 1000)
    out = []
    for s in range(0, max(len(a) - win, 1), step):
        seg = a[s:s + win]
        out.append([round(s / RATE, 3)] + [round(gamp(seg, hz), 1) for hz in hzs])
    return out


def _tail_stats(path, lo, hi):
    if not os.path.exists(path):
        return {"exists": False}
    try:
        w = wave.open(str(path))
    except Exception as exc:
        return {"exists": True, "wav_error": f"{type(exc).__name__}: {exc}"}
    n, ch = w.getnframes(), w.getnchannels()
    a = np.frombuffer(w.readframes(n), dtype="<i2").astype(np.float64)
    a = a[:(len(a) // ch) * ch].reshape(-1, ch)
    w.close()
    seg = a[int(lo * RATE):int(hi * RATE)]
    return {"exists": True, "frames": n, "window_s": [lo, hi],
            "peak": [int(np.abs(seg[:, c]).max()) if len(seg) else 0
                     for c in range(ch)],
            "rms": [round(float(np.sqrt((seg[:, c] ** 2).mean())), 1) if len(seg)
                    else 0.0 for c in range(ch)]}


# ------------------------------------------------------------------- legs

def lb_start(name, args, secs=14):
    return spawn(["timeout", "-s", "KILL", str(secs), "pw-loopback",
                  "-n", name] + list(args), name)


def wait_two(name, timeout=6.0):
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        g = Graph(pw_dump())
        if f"input.{name}" in g.nodes and f"output.{name}" in g.nodes:
            return g, round(time.monotonic() - t0, 3)
        time.sleep(0.15)
    return Graph(pw_dump()), round(time.monotonic() - t0, 3)


def lb_sample(g, name, sinks=()):
    in_n, out_n = f"input.{name}", f"output.{name}"
    ed = g.edges(name)
    return {"input": g.brief(in_n), "output": g.brief(out_n),
            "input_in_peers": g.peers(in_n, "in"),
            "input_out_peers": g.peers(in_n, "out"),
            "output_out_peers": g.peers(out_n, "out"),
            "output_in_peers": g.peers(out_n, "in"),
            "links": ed,
            "self_link": any(in_n in l and out_n in l for l in ed),
            "sinks_present": {s: (s in g.nodes) for s in sinks},
            "default_sink": metadata().get("default.audio.sink"),
            "default_source": metadata().get("default.audio.source")}


def run_leg(leg_id, args, *, sinks=(), tone=None, tap=None, samples=(1.2, 2.4),
            secs=14, extra=None, note=None):
    """One bounded pw-loopback leg + optional probe-owned tone/tap."""
    name = f"{PREFIX}_{leg_id}"
    rec = {"leg": leg_id, "name": name, "argv": list(args),
           "tone_into": tone, "tap_sink": tap, "note": note}
    if tone is not None and tone not in SINKS:
        raise RuntimeError(f"{leg_id}: tone sink {tone!r} is not probe-owned")
    lb = lb_start(name, args, secs)
    try:
        g, wait_s = wait_two(name)
        rec["wait_s"] = wait_s
        rec["nodes_seen"] = [n for n in (f"input.{name}", f"output.{name}")
                             if n in g.nodes]
        if len(rec["nodes_seen"]) < 2:
            rec["error"] = "loopback nodes did not both appear"
            rec.update(reap(lb, wait=2.0))
            return rec
        tone_p = tone_start(tone, f"{PREFIX}_{leg_id}_tone") if tone else None
        try:
            t0 = time.monotonic()
            rec["samples"] = {}
            for at in samples:
                dt = at - (time.monotonic() - t0)
                if dt > 0:
                    time.sleep(dt)
                rec["samples"][f"t{at}"] = lb_sample(Graph(pw_dump()), name, sinks)
            if tap:
                p = RAW / f"{leg_id}_{PREFIX}_tap.wav"
                rr = rec_run(tap, p, int(RATE * 1.0),
                             f"{PREFIX}_{leg_id}_rec", capture_sink=True)
                rec["tap"] = {"target": tap, "record": {
                    "rc": rr["rc"], "bytes": rr["bytes"],
                    "err": rr["err"][:200]}, "content": analyze(p)}
        finally:
            if tone_p is not None:
                kill(tone_p)
        rec["alive_before_reap"] = lb.poll() is None
        rec.update(reap(lb, wait=2.0))
        if extra:
            rec["extra"] = extra
        return rec
    finally:
        kill(lb)


def write_out(group, payload):
    p = SEAT / f"{group}.json"
    p.write_text(json.dumps(payload, indent=1) + "\n")
    return str(p)


def host_line(group):
    return {"group": group, "host_start": host_snapshot()}


# ---------------------------------------------------------------- group g1

def g1():
    out = host_line("g1-both-sides")
    ns_a = f"{PREFIX}_ns_a"
    ns_b = f"{PREFIX}_ns_b"
    ns_c = f"{PREFIX}_ns_c"
    for n in (ns_a, ns_b, ns_c):
        out.setdefault("sinks", []).append(null_sink(n))
    time.sleep(0.8)
    out["legs"] = []
    out["legs"].append(run_leg(
        "g1a-both-honored", ["-C", ns_a, "-i", "stream.capture.sink=true",
                             "-P", ns_b],
        sinks=(ns_a, ns_b), tone=ns_a, tap=ns_b,
        note="control: both sides resolvable"))
    out["legs"].append(run_leg(
        "g1b-capture-honored-playback-fallback",
        ["-C", ns_a, "-i", "stream.capture.sink=true",
         "-P", f"no_such_sink_{PID}"],
        sinks=(ns_a, ns_b), tone=None, tap=None,
        note="capture resolvable, playback garbage; no tone (playback may fall "
             "back to the shared default sink)"))
    out["legs"].append(run_leg(
        "g1c-capture-fallback-playback-honored",
        ["-C", f"no_such_node_{PID}", "-i", "stream.capture.sink=true",
         "-P", ns_b],
        sinks=(ns_a, ns_b), tone=None, tap=None,
        note="capture garbage+prop, playback resolvable; no tone"))
    out["legs"].append(run_leg(
        "g1d-both-fallback-noprop",
        ["-C", f"no_such_node_{PID}", "-P", f"no_such_sink_{PID}"],
        sinks=(ns_a, ns_b), tone=None, tap=None,
        note="both garbage, no prop; capture falls to the source domain "
             "(unnegotiated when no default source), playback to the default sink"))
    out["legs"].append(run_leg(
        "g1e-both-fallback-prop-pair",
        ["-C", f"no_such_node_{PID}", "-i", "stream.capture.sink=true",
         "-P", f"no_such_sink_{PID}"],
        sinks=(ns_a, ns_b), tone=None, tap=None, secs=8,
        samples=(1.2, 2.4, 4.0),
        note="both garbage + prop: capture -> default sink monitor, playback -> "
             "default sink; watch for a self-loop through the shared sink"))
    out["legs"].append(run_leg(
        "g1f-playback-prop-overrides-flag",
        ["-C", ns_a, "-i", "stream.capture.sink=true", "-P", ns_b,
         "-o", f"target.object={ns_c}"],
        sinks=(ns_a, ns_b, ns_c), tone=ns_a, tap=ns_c,
        note="both flags resolvable + playback prop to a third probe sink"))
    out["legs"].append(run_leg(
        "g1g-long-flags-both-honored",
        ["--capture", ns_a, "--capture-props", "stream.capture.sink=true",
         "--playback", ns_b],
        sinks=(ns_a, ns_b), tone=ns_a, tap=ns_b,
        note="long-form flags equivalence"))
    out["host_end"] = host_snapshot()
    return out


# ---------------------------------------------------------------- group g2

def g2():
    out = host_line("g2-kill-mid-capture")
    ns_a = f"{PREFIX}_ns_a"
    ns_b = f"{PREFIX}_ns_b"
    for n in (ns_a, ns_b):
        out.setdefault("sinks", []).append(null_sink(n))
    time.sleep(0.8)
    out["legs"] = []
    tone_a = SCRATCH / f"tone1k_{PID}.wav"
    tone_b = SCRATCH / f"tone1_5k_{PID}.wav"
    _write(tone_a, _tone(20, 1000.0))
    _write(tone_b, _tone(20, 1500.0))

    # ---- g2a SIGKILL mid-capture, with a consumer attached to the node
    name = f"{PREFIX}_g2a"
    lb = lb_start(name, ["-C", ns_a, "-i", "stream.capture.sink=true",
                         "-P", ns_b], secs=20)
    leg = {"leg": "g2a-kill", "name": name}
    try:
        g, wait_s = wait_two(name)
        leg["wait_s"] = wait_s
        leg["nodes_seen"] = [n for n in (f"input.{name}", f"output.{name}")
                             if n in g.nodes]
        tone_p = tone_start(ns_a, f"{PREFIX}_g2a_tone")
        tap_b = rec_start(ns_b, RAW / "g2a_tap_b.wav", int(RATE * 7),
                          f"{PREFIX}_g2a_tapb", capture_sink=True)
        tap_out = rec_start(f"output.{name}", RAW / "g2a_tap_out.wav",
                            int(RATE * 7), f"{PREFIX}_g2a_tapout")
        time.sleep(2.0)
        g = Graph(pw_dump())
        leg["pre"] = {"sample": lb_sample(g, name, (ns_a, ns_b)),
                      "tap_b_node": g.brief(f"{PREFIX}_g2a_tapb"),
                      "tap_out_node": g.brief(f"{PREFIX}_g2a_tapout"),
                      "tap_out_peers": g.peers(f"{PREFIX}_g2a_tapout", "in"),
                      "clients": {cid: p.get("application.name")
                                  for cid, p in g.clients.items()
                                  if "loopback" in str(p.get("application.name"))}}
        t_kill = time.monotonic()
        try:
            os.killpg(os.getpgid(lb.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
        leg["kill"] = {"signal": "SIGKILL", "t": round(t_kill, 3)}
        post = []
        for dt in (0.1, 0.3, 0.6, 1.2, 2.0):
            time.sleep(dt - (post[-1]["dt"] if post else 0.0))
            g = Graph(pw_dump())
            post.append({"dt": dt,
                         "nodes": [n for n in (f"input.{name}", f"output.{name}")
                                   if n in g.nodes],
                         "links": g.edges(name),
                         "tap_b_state": g.brief(f"{PREFIX}_g2a_tapb").get("state"),
                         "tap_out_state": g.brief(f"{PREFIX}_g2a_tapout").get("state"),
                         "tap_out_present": f"{PREFIX}_g2a_tapout" in g.nodes,
                         "links_touching_taps": [
                             l for l in g.links
                             if l["out_node"] == f"output.{name}"
                             or l["in_node"] == f"{PREFIX}_g2a_tapout"]})
        leg["post"] = post
        leg["lb_rc"] = lb.wait(timeout=5)
        leg["tone"] = reap(tone_p, wait=3.0)
        leg["tap_b"] = reap(tap_b["proc"], wait=10.0)
        leg["tap_b"]["content"] = analyze(tap_b["path"])
        leg["tap_b"]["tone_span"] = tone_span(tap_b["path"])
        leg["tap_b"]["tail"] = _tail_stats(tap_b["path"], 4.0, 6.9)
        leg["tap_out"] = reap(tap_out["proc"], wait=10.0)
        leg["tap_out"]["content"] = analyze(tap_out["path"])
        leg["tap_out"]["tone_span"] = tone_span(tap_out["path"])
        leg["tap_out"]["tail"] = _tail_stats(tap_out["path"], 4.0, 6.9)
        leg["tap_out"]["wav_error"] = wav_error(tap_out["path"])
        last = leg["tap_b"]["tone_span"].get("last_tone_s")
        if last is not None:
            leg["teardown"] = {"kill_at_tap_s": 2.0, "last_tone_in_tap_s": last,
                               "silence_after_kill_s": round(2.0 - last, 3)}
    finally:
        kill(lb)
    out["legs"].append(leg)

    # ---- g2b SIGSTOP the loopback mid-capture, tone-swap marker
    name = f"{PREFIX}_g2b"
    lb = lb_start(name, ["-C", ns_a, "-i", "stream.capture.sink=true",
                         "-P", ns_b], secs=30)
    leg = {"leg": "g2b-freeze-loopback", "name": name}
    try:
        g, wait_s = wait_two(name)
        leg["wait_s"] = wait_s
        leg["nodes_seen"] = [n for n in (f"input.{name}", f"output.{name}")
                             if n in g.nodes]
        t1 = tone_start(ns_a, f"{PREFIX}_g2b_t1", wav=tone_a)
        tap = rec_start(ns_b, RAW / "g2b_tap_b.wav", int(RATE * 9),
                        f"{PREFIX}_g2b_tap", capture_sink=True)
        time.sleep(2.0)
        os.killpg(os.getpgid(lb.pid), signal.SIGSTOP)
        leg["stop_wall"] = round(time.monotonic(), 3)
        leg["swap1"] = "1k -> 1.5k at the stop instant"
        kill(t1)
        t2 = tone_start(ns_a, f"{PREFIX}_g2b_t2", wav=tone_b)
        time.sleep(2.5)
        leg["swap2"] = "1.5k -> 1k while still stopped"
        kill(t2)
        t3 = tone_start(ns_a, f"{PREFIX}_g2b_t3", wav=tone_a)
        time.sleep(2.0)
        leg["ps_during_stop"] = sh(
            ["ps", "-o", "pid,stat,nlwp,cmd", "-g",
             str(os.getpgid(lb.pid))])["out"].strip()
        leg["links_during_stop"] = lb_sample(Graph(pw_dump()), name, (ns_a, ns_b))
        os.killpg(os.getpgid(lb.pid), signal.SIGCONT)
        leg["cont_wall"] = round(time.monotonic(), 3)
        time.sleep(1.5)
        leg["alive"] = lb.poll() is None
        kill(t3)
        leg["tap"] = reap(tap["proc"], wait=14.0)
        leg["tap"]["timeline"] = tone_timeline2(tap["path"], (1000.0, 1500.0))
        leg["tap"]["content"] = analyze(tap["path"])
    finally:
        kill(lb)
    out["legs"].append(leg)

    # ---- g2c control: SIGSTOP a plain pw-cat SOURCE
    leg = {"leg": "g2c-freeze-source-pwcat", "name": f"{PREFIX}_g2c"}
    t = tone_start(ns_a, f"{PREFIX}_g2c_t", wav=tone_a)
    tap = rec_start(ns_a, RAW / "g2c_tap_a.wav", int(RATE * 7),
                    f"{PREFIX}_g2c_tap", capture_sink=True)
    try:
        time.sleep(2.0)
        os.killpg(os.getpgid(t.pid), signal.SIGSTOP)
        leg["ps"] = sh(["ps", "-o", "pid,stat,cmd", "-g",
                        str(os.getpgid(t.pid))])["out"].strip()
        time.sleep(2.5)
        os.killpg(os.getpgid(t.pid), signal.SIGCONT)
        time.sleep(1.0)
    finally:
        kill(t)
    leg["tap"] = reap(tap["proc"], wait=10.0)
    leg["tap"]["timeline"] = tone_timeline(tap["path"])
    out["legs"].append(leg)

    # ---- g2d control: SIGSTOP a plain pw-record CONSUMER
    leg = {"leg": "g2d-freeze-consumer-pwrecord", "name": f"{PREFIX}_g2d"}
    t = tone_start(ns_b, f"{PREFIX}_g2d_t", wav=tone_a)
    p = RAW / "g2d_tap_b.wav"
    rec = rec_start(ns_b, p, int(RATE * 9), f"{PREFIX}_g2d_tap",
                    capture_sink=True)
    try:
        time.sleep(2.0)
        s_pre = os.path.getsize(p) if os.path.exists(p) else -1
        os.killpg(os.getpgid(rec["proc"].pid), signal.SIGSTOP)
        sizes = []
        for _ in range(5):
            time.sleep(0.5)
            sizes.append(os.path.getsize(p) if os.path.exists(p) else -1)
        os.killpg(os.getpgid(rec["proc"].pid), signal.SIGCONT)
        s_post = []
        for _ in range(4):
            time.sleep(0.5)
            s_post.append(os.path.getsize(p) if os.path.exists(p) else -1)
        leg.update({"size_pre": s_pre, "size_during": sizes,
                    "size_after": s_post})
    finally:
        kill(t)
    leg["tap"] = reap(rec["proc"], wait=12.0)
    leg["tap"]["content"] = analyze(p)
    out["legs"].append(leg)
    out["host_end"] = host_snapshot()
    return out


# ---------------------------------------------------------------- group g3

def g3():
    out = host_line("g3-two-loopbacks-cycle")
    ns_a = f"{PREFIX}_ns_a"
    ns_b = f"{PREFIX}_ns_b"
    for n in (ns_a, ns_b):
        out.setdefault("sinks", []).append(null_sink(n))
    time.sleep(0.8)
    out["legs"] = []

    def cycle_leg(leg_id, capture_prop):
        l1 = f"{PREFIX}_{leg_id}_l1"
        l2 = f"{PREFIX}_{leg_id}_l2"
        cap = ["-i", "stream.capture.sink=true"] if capture_prop else []
        p1 = lb_start(l1, ["-C", ns_a, *cap, "-P", ns_b], secs=20)
        p2 = lb_start(l2, ["-C", ns_b, *cap, "-P", ns_a], secs=20)
        leg = {"leg": leg_id, "capture_prop": capture_prop, "l1": l1, "l2": l2}
        try:
            g1_, w1 = wait_two(l1)
            g2_, w2 = wait_two(l2)
            leg["wait_s"] = [w1, w2]
            leg["nodes_seen"] = [n for n in (f"input.{l1}", f"output.{l1}",
                                             f"input.{l2}", f"output.{l2}")
                                 if n in g2_.nodes]
            time.sleep(1.0)
            g = Graph(pw_dump())
            leg["pre"] = {"l1": lb_sample(g, l1, (ns_a, ns_b)),
                          "l2": lb_sample(g, l2, (ns_a, ns_b)),
                          "all_links": sorted(set(g.edges(l1)) | set(g.edges(l2)))}
            tap = rec_start(ns_b, RAW / f"{leg_id}_tap_b.wav", int(RATE * 6),
                            f"{PREFIX}_{leg_id}_tap", capture_sink=True)
            time.sleep(0.4)
            burst = tone_start(ns_a, f"{PREFIX}_{leg_id}_burst", burst=True)
            t_burst = time.monotonic()
            leg["burst"] = {"into": ns_a, "seconds": BURST_S}
            time.sleep(2.5)
            g = Graph(pw_dump())
            leg["mid"] = {"l1": lb_sample(g, l1, (ns_a, ns_b)),
                          "l2": lb_sample(g, l2, (ns_a, ns_b)),
                          "l1_alive": p1.poll() is None,
                          "l2_alive": p2.poll() is None}
            leg["burst_reap"] = reap(burst, wait=12.0)
            leg["tap"] = reap(tap["proc"], wait=12.0)
            leg["tap"]["content"] = analyze(tap["path"])
            leg["tap"]["tone_span"] = tone_span(tap["path"])
            tl = tone_timeline(tap["path"])
            leg["tap"]["timeline"] = tl
            # recirculation: tone windows AFTER the burst file ended (0.25 s)
            after = [a for t, a in tl if t > 0.6]
            leg["recirculation"] = {
                "burst_end_s": BURST_S,
                "tone_windows_after_0.6s": sum(1 for a in after if a > 1024),
                "max_amp_after_0.6s": max(after, default=0.0),
                "amp_trend": [round(a, 1) for a in after[::10]]}
            leg["post"] = {"l1": lb_sample(Graph(pw_dump()), l1, (ns_a, ns_b)),
                           "l2": lb_sample(Graph(pw_dump()), l2, (ns_a, ns_b))}
            # control: kill L2 (the return leg) -> the recirculation must stop
            kill(p2)
            time.sleep(1.0)
            tap2 = rec_start(ns_b, RAW / f"{leg_id}_after_kill_l2.wav",
                             int(RATE * 2), f"{PREFIX}_{leg_id}_tap2",
                             capture_sink=True)
            leg["control_kill_l2"] = reap(tap2["proc"], wait=8.0)
            leg["control_kill_l2"]["content"] = analyze(tap2["path"])
            leg["control_kill_l2"]["tone_span"] = tone_span(tap2["path"])
            leg["links_after_kill_l2"] = Graph(pw_dump()).edges(l1)
        finally:
            kill(p1)
            kill(p2)
        return leg

    out["legs"].append(cycle_leg("g3a-cycle-prop", True))
    out["legs"].append(cycle_leg("g3b-cycle-noprop", False))
    out["host_end"] = host_snapshot()
    return out


# ---------------------------------------------------------------- group g4

def g4():
    out = host_line("g4-set-param-midstream")
    ns_a = f"{PREFIX}_ns_a"
    ns_b = f"{PREFIX}_ns_b"
    ns_c = f"{PREFIX}_ns_c"
    for n in (ns_a, ns_b, ns_c):
        out.setdefault("sinks", []).append(null_sink(n))
    time.sleep(0.8)
    out["legs"] = []
    name = f"{PREFIX}_g4"
    lb = lb_start(name, ["-C", ns_a, "-i", "stream.capture.sink=true",
                         "-P", ns_b], secs=40)
    leg = {"leg": "g4-setparam", "name": name}
    try:
        g, wait_s = wait_two(name)
        leg["wait_s"] = wait_s
        leg["nodes_seen"] = [n for n in (f"input.{name}", f"output.{name}")
                             if n in g.nodes]
        g = Graph(pw_dump())
        in_id, out_id = g.node(f"input.{name}")["id"], g.node(f"output.{name}")["id"]
        leg["ids"] = {"input": in_id, "output": out_id,
                      "input_serial": g.node(f"input.{name}")["serial"],
                      "output_serial": g.node(f"output.{name}")["serial"]}
        tone_p = tone_start(ns_a, f"{PREFIX}_g4_tone")
        time.sleep(1.0)
        p = RAW / "g4_pre_tap.wav"
        rr = rec_run(ns_b, p, int(RATE * 0.8), f"{PREFIX}_g4_pre", capture_sink=True)
        leg["pre"] = {"tap_b": analyze(p), "record_rc": rr["rc"],
                      "sample": lb_sample(Graph(pw_dump()), name, (ns_a, ns_b, ns_c))}

        def apply(tag, node_id, json_text, *, silence_note=None):
            r = sh(["pw-cli", "set-param", str(node_id), "Props", json_text],
                   timeout=10.0)
            time.sleep(0.7)
            g = Graph(pw_dump())
            got = {"tag": tag, "node_id": node_id, "json": json_text,
                   "rc": r["rc"], "out": r["out"][:200], "err": r["err"][:200],
                   "readback_output": g.brief(f"output.{name}"),
                   "readback_input": g.brief(f"input.{name}"),
                   "links": g.edges(name),
                   "sample": lb_sample(g, name, (ns_a, ns_b, ns_c))}
            return got

        leg["steps"] = []
        leg["steps"].append(apply("output-target-to-ns_c", out_id,
                                  f'{{ "target.object": "{ns_c}" }}'))
        # where did the tone go now?
        p_b = RAW / "g4_after_move_tap_b.wav"
        rr1 = rec_run(ns_b, p_b, int(RATE * 0.8), f"{PREFIX}_g4_pb", capture_sink=True)
        p_c = RAW / "g4_after_move_tap_c.wav"
        rr2 = rec_run(ns_c, p_c, int(RATE * 0.8), f"{PREFIX}_g4_pc", capture_sink=True)
        leg["after_move"] = {"tap_b": analyze(p_b), "tap_c": analyze(p_c),
                             "tap_b_record": rr1["rc"], "tap_c_record": rr2["rc"]}
        leg["steps"].append(apply("output-target-garbage", out_id,
                                  f'{{ "target.object": "no_such_node_{PID}" }}'))
        leg["steps"].append(apply("output-autoconnect-false", out_id,
                                  '{ "node.autoconnect": false }'))
        leg["steps"].append(apply("input-target-to-ns_c", in_id,
                                  f'{{ "target.object": "{ns_c}" }}'))
        leg["steps"].append(apply("input-capture-sink-false", in_id,
                                  '{ "stream.capture.sink": false }'))
        # tone still flowing? final taps on b and c
        p = RAW / "g4_final_tap_b.wav"
        rr3 = rec_run(ns_b, p, int(RATE * 0.8), f"{PREFIX}_g4_fb", capture_sink=True)
        leg["final_tap_b"] = analyze(p)
        leg["final_tap_b_rc"] = rr3["rc"]
        leg["tone_reap"] = reap(tone_p, wait=3.0)
        leg["alive"] = lb.poll() is None
    finally:
        kill(lb)
    out["legs"].append(leg)
    out["host_end"] = host_snapshot()
    return out


# ---------------------------------------------------------------- group g5

def g5():
    out = host_line("g5-serial-vs-name")
    ns_a = f"{PREFIX}_ns_a"
    ns_b = f"{PREFIX}_ns_b"
    for n in (ns_a, ns_b):
        out.setdefault("sinks", []).append(null_sink(n))
    time.sleep(0.8)
    out["legs"] = []
    name = f"{PREFIX}_g5"
    lb = lb_start(name, ["-C", ns_a, "-i", "stream.capture.sink=true",
                         "-P", ns_b], secs=60)
    leg = {"leg": "g5-record-targets", "name": name, "records": []}
    try:
        g, wait_s = wait_two(name)
        leg["wait_s"] = wait_s
        leg["nodes_seen"] = [n for n in (f"input.{name}", f"output.{name}")
                             if n in g.nodes]
        g = Graph(pw_dump())
        leg["ids"] = {"input": g.node(f"input.{name}")["id"],
                      "output": g.node(f"output.{name}")["id"],
                      "input_serial": g.node(f"input.{name}")["serial"],
                      "output_serial": g.node(f"output.{name}")["serial"],
                      "ns_a_id": g.node(ns_a)["id"], "ns_a_serial": g.node(ns_a)["serial"],
                      "ns_b_id": g.node(ns_b)["id"], "ns_b_serial": g.node(ns_b)["serial"]}
        tone_p = tone_start(ns_a, f"{PREFIX}_g5_tone")
        time.sleep(1.0)

        def record(leg_id, target, capture_sink=False, frames=1.2):
            tag = f"{PREFIX}_{leg_id}"
            p = RAW / f"{leg_id}.wav"
            st = rec_start(target, p, int(RATE * frames), tag,
                           capture_sink=capture_sink)
            time.sleep(0.6)                      # sample WHILE the stream lives
            g = Graph(pw_dump())
            live = {"producers": g.peers(tag, "in"), "state": g.brief(tag),
                    "target_present": target.split(".")[-1] in str(g.find(target))
                    if not target.isdigit() else None}
            rr = reap(st["proc"], wait=6.0)
            time.sleep(0.3)
            g = Graph(pw_dump())
            return {"leg": leg_id, "target": target, "capture_sink": capture_sink,
                    "live": live, "record": rr, "content": analyze(p),
                    "after": {"state": g.brief(tag), "producers": g.peers(tag, "in")}}

        leg["records"].append(record("g5a-name-output", f"output.{name}"))
        leg["records"].append(record("g5b-serial-output", str(g.node(f"output.{name}")["serial"])))
        leg["records"].append(record("g5c-id-output", str(g.node(f"output.{name}")["id"])))
        leg["records"].append(record("g5d-serial-input", str(g.node(f"input.{name}")["serial"])))
        leg["records"].append(record("g5e-name-input-prop", f"input.{name}",
                                     capture_sink=True))
        leg["tone_reap"] = reap(tone_p, wait=3.0)
        leg["alive"] = lb.poll() is None
    finally:
        kill(lb)
    out["legs"].append(leg)

    # ---- numeric targets for pw-loopback itself
    g = graph_now()
    if g.node(ns_a) is None or g.node(ns_b) is None:
        out["legs"].append({"leg": "g5f..g5h", "error": "sinks missing from dump",
                            "nodes": sorted(n for n in g.nodes if PREFIX in n)})
        out["host_end"] = host_snapshot()
        return out
    serial_a = g.node(ns_a)["serial"]
    serial_b = g.node(ns_b)["serial"]
    id_a, id_b = g.node(ns_a)["id"], g.node(ns_b)["id"]
    out["legs"].append(run_leg(
        "g5f-loopback-serial-both",
        ["-C", str(serial_a), "-i", "stream.capture.sink=true",
         "-P", str(serial_b)],
        sinks=(ns_a, ns_b), tone=ns_a, tap=ns_b,
        note="both sides named by object.serial"))
    out["legs"].append(run_leg(
        "g5g-loopback-id-both",
        ["-C", str(id_a), "-i", "stream.capture.sink=true", "-P", str(id_b)],
        sinks=(ns_a, ns_b), tone=ns_a, tap=None,
        note="both sides named by global node id (not the serial)"))
    out["legs"].append(run_leg(
        "g5h-loopback-serial-mixed",
        ["-C", str(serial_a), "-i", "stream.capture.sink=true", "-P", ns_b],
        sinks=(ns_a, ns_b), tone=ns_a, tap=ns_b,
        note="capture by serial, playback by name"))
    out["host_end"] = host_snapshot()
    return out


# ---------------------------------------------------------------- group g6

def g6():
    out = host_line("g6-suspended-target")
    ns_a = f"{PREFIX}_ns_a"
    ns_b = f"{PREFIX}_ns_b"
    ns_hp = f"{PREFIX}_ns_hp"
    for n in (ns_a, ns_b, ns_hp):
        out.setdefault("sinks", []).append(null_sink(n))
    time.sleep(0.8)
    out["legs"] = []
    out["states"] = {"idle": {n: sink_state(n) for n in (ns_a, ns_b, ns_hp)}}

    # ---- g6a loopback against an idle (suspended) playback target
    name = f"{PREFIX}_g6a"
    lb = lb_start(name, ["-C", ns_a, "-i", "stream.capture.sink=true",
                         "-P", ns_b], secs=30)
    leg = {"leg": "g6a-idle-target", "name": name, "steps": []}
    try:
        g, wait_s = wait_two(name)
        leg["wait_s"] = wait_s
        leg["nodes_seen"] = [n for n in (f"input.{name}", f"output.{name}")
                             if n in g.nodes]
        tone_p = tone_start(ns_a, f"{PREFIX}_g6a_tone")
        time.sleep(1.2)
        g = Graph(pw_dump())
        leg["steps"].append({"phase": "idle-target-live",
                             "states": {n: sink_state(n) for n in (ns_a, ns_b)},
                             "sample": lb_sample(g, name, (ns_a, ns_b))})
        p = RAW / "g6a_idle_tap.wav"
        rr = rec_run(ns_b, p, int(RATE * 0.8), f"{PREFIX}_g6a_rec", capture_sink=True)
        leg["idle_tap"] = {"content": analyze(p), "rc": rr["rc"]}

        # ---- g6b suspend the PLAYBACK target mid-route
        s1 = sh(["pactl", "suspend-sink", ns_b, "1"], timeout=8.0)
        time.sleep(1.2)
        g = Graph(pw_dump())
        leg["steps"].append({"phase": "playback-target-suspended",
                             "suspend_rc": s1["rc"], "suspend_err": s1["err"][:120],
                             "states": {n: sink_state(n) for n in (ns_a, ns_b)},
                             "sample": lb_sample(g, name, (ns_a, ns_b))})
        p = RAW / "g6b_suspended_tap.wav"
        rr = rec_run(ns_b, p, int(RATE * 0.8), f"{PREFIX}_g6b_rec", capture_sink=True)
        leg["suspended_tap"] = {"content": analyze(p), "rc": rr["rc"],
                                "bytes": rr["bytes"], "err": rr["err"][:200]}
        s2 = sh(["pactl", "suspend-sink", ns_b, "0"], timeout=8.0)
        time.sleep(1.2)
        g = Graph(pw_dump())
        leg["steps"].append({"phase": "playback-target-resumed",
                             "resume_rc": s2["rc"],
                             "states": {n: sink_state(n) for n in (ns_a, ns_b)},
                             "sample": lb_sample(g, name, (ns_a, ns_b))})
        p = RAW / "g6c_resumed_tap.wav"
        rr = rec_run(ns_b, p, int(RATE * 0.8), f"{PREFIX}_g6c_rec", capture_sink=True)
        leg["resumed_tap"] = {"content": analyze(p), "rc": rr["rc"]}

        # ---- g6d suspend the CAPTURE target mid-route
        s3 = sh(["pactl", "suspend-sink", ns_a, "1"], timeout=8.0)
        time.sleep(1.2)
        g = Graph(pw_dump())
        leg["steps"].append({"phase": "capture-target-suspended",
                             "suspend_rc": s3["rc"],
                             "states": {n: sink_state(n) for n in (ns_a, ns_b)},
                             "sample": lb_sample(g, name, (ns_a, ns_b))})
        p = RAW / "g6d_cap_susp_tap.wav"
        rr = rec_run(ns_b, p, int(RATE * 0.8), f"{PREFIX}_g6d_rec", capture_sink=True)
        leg["capture_suspended_tap"] = {"content": analyze(p), "rc": rr["rc"]}
        s4 = sh(["pactl", "suspend-sink", ns_a, "0"], timeout=8.0)
        time.sleep(1.2)
        g = Graph(pw_dump())
        leg["steps"].append({"phase": "capture-target-resumed",
                             "resume_rc": s4["rc"],
                             "states": {n: sink_state(n) for n in (ns_a, ns_b)},
                             "sample": lb_sample(g, name, (ns_a, ns_b))})
        p = RAW / "g6e_cap_res_tap.wav"
        rr = rec_run(ns_b, p, int(RATE * 0.8), f"{PREFIX}_g6e_rec", capture_sink=True)
        leg["capture_resumed_tap"] = {"content": analyze(p), "rc": rr["rc"]}
        leg["alive"] = lb.poll() is None
        leg["tone_reap"] = reap(tone_p, wait=3.0)
    finally:
        kill(lb)
    out["legs"].append(leg)

    # ---- g6e loopback created while the target is EXPLICITLY suspended
    s5 = sh(["pactl", "suspend-sink", ns_hp, "1"], timeout=8.0)
    out["states"]["explicit_suspend"] = {ns_hp: sink_state(ns_hp),
                                         "rc": s5["rc"]}
    out["legs"].append(run_leg(
        "g6e-created-while-suspended",
        ["-C", ns_a, "-i", "stream.capture.sink=true", "-P", ns_hp],
        sinks=(ns_a, ns_hp), tone=ns_a, tap=ns_hp,
        note="target explicitly suspended before the loopback spawns"))
    out["host_end"] = host_snapshot()
    return out


# ---------------------------------------------------------------- group g7

def g7():
    out = host_line("g7-self-binding")
    ns_a = f"{PREFIX}_ns_a"
    ns_b = f"{PREFIX}_ns_b"
    for n in (ns_a, ns_b):
        out.setdefault("sinks", []).append(null_sink(n))
    time.sleep(0.8)
    out["legs"] = []
    nm = f"{PREFIX}_g7a"
    out["legs"].append(run_leg(
        "g7a-capture-own-output",
        ["-C", f"output.{nm}", "-i", "stream.capture.sink=true", "-P", ns_b],
        sinks=(ns_a, ns_b), tone=ns_a, tap=ns_b,
        note="capture target is this client's own playback node (name is "
             "published by the same client)"))
    nm = f"{PREFIX}_g7b"
    out["legs"].append(run_leg(
        "g7b-playback-own-input",
        ["-C", ns_a, "-i", "stream.capture.sink=true", "-P", f"input.{nm}"],
        sinks=(ns_a, ns_b), tone=None, tap=None,
        note="playback target is this client's own capture node; no tone "
             "(a failed self-resolution falls back to the shared default sink)"))
    nm = f"{PREFIX}_g7c"
    out["legs"].append(run_leg(
        "g7c-capture-own-monitor",
        ["-C", f"input.{nm}", "-i", "stream.capture.sink=true", "-P", ns_b],
        sinks=(ns_a, ns_b), tone=ns_a, tap=ns_b,
        note="capture target is this client's own capture node with the sink "
             "prop -> its own monitor ports"))
    nm = f"{PREFIX}_g7d"
    out["legs"].append(run_leg(
        "g7d-playback-prop-own-input",
        ["-C", ns_a, "-i", "stream.capture.sink=true", "-P", ns_b,
         "-o", f"target.object=input.{nm}"],
        sinks=(ns_a, ns_b), tone=None, tap=None,
        note="playback prop points at this client's own capture node; no tone"))
    nm = f"{PREFIX}_g7e"
    out["legs"].append(run_leg(
        "g7e-capture-prop-own-monitor",
        ["-C", ns_a, "-i", f"target.object=input.{nm}", "-P", ns_b],
        sinks=(ns_a, ns_b), tone=ns_a, tap=ns_b,
        note="capture prop points at this client's own capture node"))
    out["legs"].append(run_leg(
        "g7f-same-sink-both-sides",
        ["-C", ns_a, "-i", "stream.capture.sink=true", "-P", ns_a],
        sinks=(ns_a, ns_b), tone=ns_a, tap=ns_a,
        note="capture monitor and playback target are the same probe sink: a "
             "sink-level self-loop"))
    out["host_end"] = host_snapshot()
    return out


# ------------------------------------------------------------------ main

GROUPS = {"g1": g1, "g2": g2, "g3": g3, "g4": g4, "g5": g5, "g6": g6, "g7": g7}


def final_check(group):
    g = Graph(pw_dump())
    survivors = nodes_with_prefix(g)
    r = sh(["pactl", "list", "modules", "short"], timeout=8.0)
    my_sink_survivors = [l for l in r["out"].splitlines() if PREFIX in l]
    return {"group": group, "own_nodes_after": survivors,
            "own_sink_modules_after": my_sink_survivors,
            "own_procs_alive": [f"{lbl}:{p.pid}" for lbl, p in PROCS
                                if p.poll() is None]}


def cleanup():
    for lbl, p in PROCS:
        if p.poll() is None:
            kill(p)
    for n in list(SINKS):
        null_sink_unload(n)


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "g1"
    make_wavs()
    fn = GROUPS[which]
    payload = None
    err = None
    try:
        payload = fn()
    except BaseException:
        import traceback
        err = traceback.format_exc()
        print(err, file=sys.stderr, flush=True)
    finally:
        cleanup()
        time.sleep(0.5)
        chk = final_check(which)
        if payload is not None:
            payload["final_check"] = chk
            path = write_out(f"r79b-{which}", payload)
            print(json.dumps({"written": path, "final_check": chk}, indent=1))
        else:
            print(json.dumps({"failed": which, "error": err, "final_check": chk},
                             indent=1))
            sys.exit(1)


if __name__ == "__main__":
    main()
