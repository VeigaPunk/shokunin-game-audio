#!/usr/bin/env python3
"""R79 scout pre-measurement harness — pw-loopback / filter-chain DSP frontier.

Own harness, own classifiers. `corpus/fixtures/measure_audio.py` is owned by a
concurrent r78 author seat this round and is NEVER imported or read here.

Bounds (every leg): consumer duration/sample-count flag, outer subprocess
timeout <= 15 s, reader byte cap. All artifacts stay under
`corpus/live/r79-scout/`.

Contention discipline: the shared default sink (SPDIF) is being recorded by a
concurrent r78-baseline seat, so *no leg may feed tone into it*. Tone only ever
enters probe-owned null sinks (`r79_ns_a_*`, `r79_ns_b_*`); legs whose target
falls back to the default sink run on a digital-silent source and are judged by
topology only.
"""
import json
import math
import os
import signal
import struct
import subprocess
import sys
import time
import wave

import numpy as np

SEAT = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.join(SEAT, "scratch")
RAW = os.path.join(SEAT, "raw")
CFG = os.path.join(SEAT, "cfg")
PID = os.getpid()
TAG = f"r79_{PID}"
TONE = os.path.join(SCRATCH, "tone_r79_long.wav")     # 40 s, L 1 kHz / R 1.5 kHz
TONE_AMP = 8192
TONE_L_HZ = 1000.0
TONE_R_HZ = 1500.0
DEFAULT_TIMEOUT = 15.0
DEFAULT_SINK = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink"
DEFAULT_SOURCE = ("alsa_input.usb-Sony_Interactive_Entertainment_DualSense_"
                  "Wireless_Controller-00.Direct__Direct__source")
LINE_SOURCE = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source"

for d in (SCRATCH, RAW, CFG):
    os.makedirs(d, exist_ok=True)


# ---------------------------------------------------------------- subprocess

def sh(argv, timeout=DEFAULT_TIMEOUT, env=None, stdin=None):
    """Bounded run -> dict(rc, out, err, wall, timeout)."""
    e = dict(os.environ)
    if env:
        e.update(env)
    t0 = time.monotonic()
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout, env=e,
                           input=stdin)
        return {"rc": p.returncode, "out": p.stdout, "err": p.stderr.decode(
            errors="replace"), "wall": round(time.monotonic() - t0, 3),
            "timeout": False, "argv": list(argv)}
    except subprocess.TimeoutExpired as exc:
        return {"rc": None, "out": exc.stdout or b"", "err": (
            exc.stderr or b"").decode(errors="replace"),
            "wall": round(time.monotonic() - t0, 3), "timeout": True,
            "argv": list(argv)}
    except OSError as exc:
        return {"rc": None, "out": b"", "err": f"spawn failed: {exc}",
                "wall": round(time.monotonic() - t0, 3), "timeout": False,
                "argv": list(argv)}


def spawn(argv, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    return subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE, env=e)


def kill(p, sig=signal.SIGKILL):
    if p is None:
        return
    if p.poll() is None:
        try:
            p.send_signal(sig)
        except ProcessLookupError:
            return
        try:
            p.wait(timeout=3)
        except subprocess.TimeoutExpired:
            p.send_signal(signal.SIGKILL)
            p.wait(timeout=3)


def popen_err(p):
    try:
        return (p.stderr.read() or b"").decode(errors="replace") if p.stderr else ""
    except Exception as exc:  # pragma: no cover
        return f"<stderr read failed: {exc}>"


def reap(p, wait=8.0):
    """Wait bounded, KILL, then read stderr (never read a live process's pipe)."""
    t0 = time.monotonic()
    try:
        p.wait(timeout=wait)
    except subprocess.TimeoutExpired:
        pass
    kill(p)
    return {"wall_s": round(time.monotonic() - t0, 2), "rc": p.returncode,
            "stderr": popen_err(p)}


# ------------------------------------------------------------------- graph

def pw_dump(env=None):
    r = sh(["pw-dump"], timeout=15.0, env=env)
    if r["rc"] != 0:
        return None
    try:
        return json.loads(r["out"])
    except json.JSONDecodeError:
        return None


class Graph:
    """pw-dump -> nodes / ports / links, addressed by node.name."""

    def __init__(self, objs):
        self.nodes = {}     # name -> {id, class, props, in:[(port,pid)], out:[...]}
        self.by_id = {}
        self.ports = {}     # port id -> {node, name, dir}
        self.links = []     # {out_node,out_port,in_node,in_port,state}
        for o in objs or []:
            t = o.get("type", "").split(":")[-1]
            if t == "Node":
                info = o.get("info", {}) or {}
                props = info.get("props", {}) or {}
                nm = props.get("node.name", "")
                rec = {"id": o["id"], "class": props.get("media.class", ""),
                       "props": props, "in": [], "out": []}
                self.nodes[nm] = rec
                self.by_id[o["id"]] = nm
            elif t == "Port":
                props = (o.get("info", {}) or {}).get("props", {}) or {}
                self.ports[o["id"]] = {
                    "node_id": props.get("node.id"), "name": props.get("port.name", ""),
                    "dir": (o.get("info", {}) or {}).get("direction", "")}
        for o in objs or []:
            if o.get("type", "").endswith("Link"):
                i = o.get("info", {}) or {}
                on, op = self.by_id.get(i.get("output-node-id")), self.ports.get(
                    i.get("output-port-id"), {})
                inn, ip = self.by_id.get(i.get("input-node-id")), self.ports.get(
                    i.get("input-port-id"), {})
                self.links.append({
                    "out_node": on, "out_port": op.get("name"), "in_node": inn,
                    "in_port": ip.get("name"), "state": i.get("state")})
        for o in objs or []:
            if o.get("type", "").endswith("Port"):
                p = self.ports[o["id"]]
                nm = self.by_id.get(p["node_id"])
                if nm in self.nodes:
                    (self.nodes[nm]["in"] if p["dir"] == "input"
                     else self.nodes[nm]["out"]).append((p["name"], o["id"]))

    def find(self, substr):
        return sorted(n for n in self.nodes if substr in n)

    def node(self, name):
        return self.nodes.get(name)

    def edges(self, substr, include_foreign=True):
        """All link endpoints touching nodes whose name contains `substr`."""
        out = []
        for l in self.links:
            if substr in (l["out_node"] or "") or substr in (l["in_node"] or ""):
                out.append(f"{l['out_node']}:{l['out_port']} -> "
                           f"{l['in_node']}:{l['in_port']}")
        return sorted(out)

    def peers(self, substr, side="both"):
        """(node, port) peers of a node-set, split by direction."""
        src, dst = set(), set()
        for l in self.links:
            if substr in (l["out_node"] or ""):
                dst.add(f"{l['in_node']}:{l['in_port']}")
            if substr in (l["in_node"] or ""):
                src.add(f"{l['out_node']}:{l['out_port']}")
        if side == "in":
            return sorted(src)
        if side == "out":
            return sorted(dst)
        return sorted(src | dst)


# --------------------------------------------------------------- null sinks

def null_sink_load(name):
    r = sh(["pactl", "load-module", "module-null-sink", f"sink_name={name}"],
           timeout=10.0)
    mid = None
    if r["rc"] == 0:
        try:
            mid = int(r["out"].decode().strip())
        except ValueError:
            mid = None
    return {"rc": r["rc"], "module_id": mid, "err": r["err"].strip(),
            "name": name}


def null_sink_unload(mid):
    return sh(["pactl", "unload-module", str(mid)], timeout=10.0)


# ---------------------------------------------------------------- tone/rec

def tone_start(target, tag, sink_prop=None, target0=False):
    """Start a bounded tone player into `target` (or an unlinked node if
    target0). Returns Popen."""
    argv = ["pw-cat", "-p", "-P", f"node.name={tag}"]
    if sink_prop:
        argv += ["-P", sink_prop]
    argv += ["--target", "0" if target0 else target, TONE]
    return spawn(argv)


def rec_monitor(sink, path, frames, tag, extra=None):
    """pw-record the monitor of `sink` (probe-owned null sinks only)."""
    argv = ["pw-record", "-P", f"stream.capture.sink=true", "-P",
            f"node.name={tag}"]
    if extra:
        for x in extra:
            argv += ["-P", x]
    argv += ["--target", sink, "-n", str(frames), path]
    r = sh(argv, timeout=15.0)
    r["path"] = path
    r["exists"] = os.path.exists(path)
    r["bytes"] = os.path.getsize(path) if r["exists"] else 0
    return r


def rec_target(target, path, frames, tag, extra=None):
    """pw-record with an explicit target (no capture.sink prop unless given)."""
    argv = ["pw-record", "-P", f"node.name={tag}"]
    if extra:
        for x in extra:
            argv += ["-P", x]
    argv += ["--target", target, "-n", str(frames), path]
    r = sh(argv, timeout=15.0)
    r["path"] = path
    r["exists"] = os.path.exists(path)
    r["bytes"] = os.path.getsize(path) if r["exists"] else 0
    return r


# ---------------------------------------------------------------- analysis

def analyze(path, tone_amp=TONE_AMP, quiet=64, foreign=200):
    """Per-channel peak/rms + dominant frequency + content class."""
    res = {"path": path, "exists": os.path.exists(path)}
    if not res["exists"]:
        return res
    try:
        w = wave.open(path)
    except Exception as exc:
        res["error"] = f"wave: {exc}"
        return res
    n, ch, sw, rate = w.getnframes(), w.getnchannels(), w.getsampwidth(), w.getframerate()
    raw = w.readframes(n)
    res.update(frames=n, ch=ch, width=sw, rate=rate, bytes=os.path.getsize(path))
    if sw != 2 or n == 0:
        res["class"] = "non_s16" if sw != 2 else "empty"
        return res
    a = np.frombuffer(raw, dtype="<i2").astype(np.float64)
    if ch > 0:
        a = a[: (len(a) // ch) * ch].reshape(-1, ch)
    res["peak"] = [int(np.abs(a[:, c]).max()) if len(a) else 0 for c in range(ch)]
    res["rms"] = [round(float(np.sqrt((a[:, c] ** 2).mean())), 2)
                  if len(a) else 0.0 for c in range(ch)]
    win = a[len(a) // 4: len(a) // 4 + min(len(a) // 2, rate // 2)] if len(a) else a
    freqs = []
    for c in range(ch):
        if len(win) < 64:
            freqs.append({"hz": None, "amp": 0.0})
            continue
        sp = np.abs(np.fft.rfft(win[:, c] * np.hanning(len(win))))
        k = int(np.argmax(sp))
        hz = k * rate / len(win)
        freqs.append({"hz": round(hz, 1), "amp": round(float(sp[k]) * 2 / len(win), 1)})
    res["dom"] = freqs
    cls = []
    for c in range(ch):
        pk = res["peak"][c]
        if pk <= quiet:
            cls.append("silence")
            continue
        hz = freqs[c]["hz"]
        if hz is not None and abs(hz - TONE_L_HZ) <= 0.03 * TONE_L_HZ and pk >= 0.3 * tone_amp:
            cls.append("tone1k")
        elif hz is not None and abs(hz - TONE_R_HZ) <= 0.03 * TONE_R_HZ and pk >= 0.3 * tone_amp:
            cls.append("tone1.5k")
        elif pk >= foreign:
            cls.append(f"foreign@{hz}Hz")
        else:
            cls.append(f"noise@{hz}Hz")
    res["class"] = cls
    res["carries_tone"] = any(c.startswith("tone") for c in cls)
    return res


def goertzel_amp(sig, rate, hz):
    n = len(sig)
    k = int(0.5 + n * hz / rate)
    w = 2 * math.pi * k / n
    cw, sw_ = math.cos(w), math.sin(w)
    coeff = 2 * cw
    s0 = s1 = s2 = 0.0
    for x in sig:
        s0 = x + coeff * s1 - s2
        s2, s1 = s1, s0
    return math.sqrt(max(s1 * s1 + s2 * s2 - coeff * s1 * s2, 0.0)) * 2 / n


# ---------------------------------------------------------------- loopback

def loopback_start(name, args, secs):
    """Bounded pw-loopback; the outer `timeout -s KILL` is the hard bound."""
    argv = ["timeout", "-s", "KILL", str(secs), "pw-loopback", "-n", name] + args
    return spawn(argv)


def wait_nodes(g, substr, want, timeout=4.0):
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        g = Graph(pw_dump())
        got = [n for n in g.nodes if substr in n]
        if len(got) >= want:
            return g, got, round(time.monotonic() - t0, 3)
        time.sleep(0.2)
    g = Graph(pw_dump())
    return g, [n for n in g.nodes if substr in n], round(time.monotonic() - t0, 3)


def run_leg(leg_id, name, args, *, rec_sink=None, tone_into=None,
            rec_frames=24000, secs=7, rec_tag=None, rec_extra=None,
            samples=(1.0, 2.2)):
    """One bounded pw-loopback leg.

    args        -- pw-loopback argv tail (after `-n <name>`)
    rec_sink    -- probe-owned null sink whose monitor is recorded
    tone_into   -- probe-owned null sink the tone plays into (None = no tone;
                   mandatory for legs that can reach the shared default sink)
    """
    rec = {"leg": leg_id, "name": name, "args": list(args),
           "tone_into": tone_into, "rec_sink": rec_sink, "samples": {}}
    # FAIL-CLOSED: a tone leg may never reach the shared default sink.
    if tone_into:
        if "-P" not in args:
            raise ValueError(f"{leg_id}: tone leg without an explicit -P pin")
        pt = args[args.index("-P") + 1]
        if not pt.startswith("r79_ns"):
            raise ValueError(f"{leg_id}: tone leg -P {pt!r} is not probe-owned")
        if "-o" in args:
            ot = args[args.index("-o") + 1]
            if "target.object" in ot and not any(
                    t in ot for t in ("r79_ns", "r79_hp")):
                raise ValueError(f"{leg_id}: tone leg -o {ot!r} can escape")
    lb = loopback_start(name, args, secs)
    try:
        g, got, wait_s = wait_nodes(Graph(pw_dump()), name, 2)
        rec["nodes_seen"] = got
        rec["wait_s"] = wait_s
        if len(got) < 2:
            rec["error"] = "loopback nodes did not both appear"
            return rec
        rec["node_props"] = {n: {"class": g.nodes[n]["class"],
                                 "target.object": g.nodes[n]["props"].get("target.object"),
                                 "node.autoconnect": g.nodes[n]["props"].get("node.autoconnect"),
                                 "ports": [p[0] for p in g.nodes[n]["in"] + g.nodes[n]["out"]]}
                             for n in got}
        tone_p = tone_start(tone_into, f"{TAG}_{leg_id}_tone") if tone_into else None
        try:
            t0 = time.monotonic()
            for at in samples:
                dt = at - (time.monotonic() - t0)
                if dt > 0:
                    time.sleep(dt)
                g = Graph(pw_dump())
                rec["samples"][f"t{at}"] = {
                    "edges": g.edges(name),
                    "input_peers_in": g.peers("input." + name, "in"),
                    "output_peers_out": g.peers("output." + name, "out"),
                    "output_peers_in": g.peers("output." + name, "in"),
                    "input_peers_out": g.peers("input." + name, "out")}
                if rec_sink and at == samples[0]:
                    out = os.path.join(RAW, f"{leg_id}_{TAG}.wav")
                    rr = rec_monitor(rec_sink, out, rec_frames,
                                     rec_tag or f"{TAG}_{leg_id}_rec",
                                     extra=rec_extra)
                    rec["record"] = {k: rr[k] for k in
                                     ("rc", "err", "wall", "bytes", "exists",
                                      "path")}
                    rec["record_offset_s"] = round(time.monotonic() - t0, 2)
                    rec["content"] = analyze(out)
        finally:
            kill(tone_p)
            kill(lb)
            time.sleep(0.2)
        rec["loopback_rc"] = lb.returncode
        rec["loopback_stderr"] = popen_err(lb)
    finally:
        kill(lb)
    return rec


def save(name, obj):
    path = os.path.join(SEAT, name)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, sort_keys=True)
    return path


def tail(obj, key="legs"):
    print(json.dumps({key: obj.get(key, [])}, indent=1)[:2000])
