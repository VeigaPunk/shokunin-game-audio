#!/usr/bin/env python3
"""R83 scout pre-measurement harness — pw-loopback props DSP / midi / stream
remix props / adaptive-resampler frontier.

Own harness, own classifiers; `corpus/fixtures/measure_audio.py` is a live
sibling-seat file and is NEVER imported or read here. Every leg is
triple-bounded (consumer flag, subprocess timeout, reader cap). All writes stay
under `corpus/live/r83-scout/`. Node names are tagged `r83dsp*`; the only
module loads are seat-owned `r83dsp_ns*` null sinks and they are unloaded by
index verified against the sink name — never by name.

Contention: a sibling r78 seat is live and recording the SPDIF monitor.
FAIL-CLOSED rule: no tone ever targets the shared default sink; legs whose
route can land there run silent and are judged by topology only.
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
RECEIPTS = os.path.join(SEAT, "receipts")
PID = os.getpid()
TAG = "r83dsp"
TONE48 = os.path.join(SCRATCH, "tone48.wav")      # 48k stereo L 1k / R 1.5k
TONE44 = os.path.join(SCRATCH, "tone44.wav")      # 44.1k stereo L 1k / R 1.5k
MONO48 = os.path.join(SCRATCH, "mono48.wav")      # 48k mono 1 kHz
TONE_AMP = 8192
L_HZ, R_HZ, M_HZ = 1000.0, 1500.0, 1000.0
DEF_TIMEOUT = 15.0
DEFAULT_SINK = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink"

for d in (SCRATCH, RAW, RECEIPTS):
    os.makedirs(d, exist_ok=True)


# ---------------------------------------------------------------- fixtures

def _wav(path, rate, chans, dur_s, freqs, amp=TONE_AMP):
    n = int(rate * dur_s)
    t = np.arange(n) / rate
    frames = []
    for f in freqs:
        frames.append(np.clip(np.rint(amp * np.sin(2 * np.pi * f * t)),
                              -32768, 32767).astype("<i2"))
    data = np.stack(frames, axis=1) if chans > 1 else frames[0].reshape(-1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(chans)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(data.tobytes())


def ensure_tones():
    if not os.path.exists(TONE48):
        _wav(TONE48, 48000, 2, 20.0, [L_HZ, R_HZ])
    if not os.path.exists(TONE44):
        _wav(TONE44, 44100, 2, 20.0, [L_HZ, R_HZ])
    if not os.path.exists(MONO48):
        _wav(MONO48, 48000, 1, 20.0, [M_HZ])


def mid_file(path):
    """Minimal SMF: 96 tpq, one note-on C4 vel 96 + note-off after 480 ticks."""
    if os.path.exists(path):
        return path
    trk = bytes([
        0x00, 0xFF, 0x51, 0x03, 0x07, 0xA1, 0x20,      # tempo 500000
        0x00, 0x90, 0x3C, 0x60,                       # note on  C4 v96
        0x83, 0x60, 0x80, 0x3C, 0x40,                 # dt 480, note off
        0x00, 0xFF, 0x2F, 0x00])                      # eot
    smf = (b"MThd" + struct.pack(">IHHH", 6, 0, 1, 96)
           + b"MTrk" + struct.pack(">I", len(trk)) + trk)
    with open(path, "wb") as fh:
        fh.write(smf)
    return path


# ---------------------------------------------------------------- subprocess

def sh(argv, timeout=DEF_TIMEOUT, env=None, stdin=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    t0 = time.monotonic()
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout, env=e,
                           input=stdin)
        return {"rc": p.returncode, "out": p.stdout, "err": p.stderr.decode(
            errors="replace"), "wall": round(time.monotonic() - t0, 3),
            "timeout": False, "argv": [str(a) for a in argv]}
    except subprocess.TimeoutExpired as exc:
        return {"rc": None, "out": exc.stdout or b"", "err": (
            exc.stderr or b"").decode(errors="replace"),
            "wall": round(time.monotonic() - t0, 3), "timeout": True,
            "argv": [str(a) for a in argv]}
    except OSError as exc:
        return {"rc": None, "out": b"", "err": f"spawn failed: {exc}",
                "wall": round(time.monotonic() - t0, 3), "timeout": False,
                "argv": [str(a) for a in argv]}


def spawn(argv, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    return subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE, env=e)


def spawn_out(argv, env=None):
    """Like spawn but captures stdout too (for bounded text witnesses)."""
    e = dict(os.environ)
    if env:
        e.update(env)
    return subprocess.Popen(argv, stdout=subprocess.PIPE,
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
            "stderr": popen_err(p)}


def reap_io(p, wait=8.0, cap=1 << 20):
    """Bounded reap returning capped stdout+stderr from a live process."""
    t0 = time.monotonic()
    try:
        out, err = p.communicate(timeout=wait)
    except subprocess.TimeoutExpired:
        kill(p)
        out, err = p.communicate(timeout=3)
    return {"wall_s": round(time.monotonic() - t0, 2), "rc": p.returncode,
            "stdout": (out or b"")[:cap].decode(errors="replace"),
            "stderr": (err or b"")[:cap].decode(errors="replace")}


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
    def __init__(self, objs):
        self.nodes = {}
        self.by_id = {}
        self.ports = {}
        self.links = []
        for o in objs or []:
            t = o.get("type", "").split(":")[-1]
            if t == "Node":
                props = (o.get("info", {}) or {}).get("props", {}) or {}
                rec = {"id": o["id"], "class": props.get("media.class", ""),
                       "props": props, "in": [], "out": [],
                       "params": o.get("info", {}).get("params")}
                self.nodes[props.get("node.name", f"#{o['id']}")] = rec
                self.by_id[o["id"]] = props.get("node.name", f"#{o['id']}")
            elif t == "Port":
                props = (o.get("info", {}) or {}).get("props", {}) or {}
                self.ports[o["id"]] = {
                    "node_id": props.get("node.id"),
                    "name": props.get("port.name", ""),
                    "dir": (o.get("info", {}) or {}).get("direction", ""),
                    "format": props.get("format.dsp", "")}
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
                     else self.nodes[nm]["out"]).append(
                         (p["name"], o["id"], p.get("format", "")))

    def find(self, substr):
        return sorted(n for n in self.nodes if substr in n)

    def node(self, name):
        return self.nodes.get(name)

    def edges(self, substr):
        return sorted(
            f"{l['out_node']}:{l['out_port']} -> {l['in_node']}:{l['in_port']}"
            for l in self.links
            if substr in (l["out_node"] or "") or substr in (l["in_node"] or ""))

    def peers(self, substr, side="both"):
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

def sink_module_index(name):
    r = sh(["pactl", "list", "short", "modules"], timeout=10.0)
    if r["rc"] != 0:
        return None
    out = r["out"].decode() if isinstance(r["out"], bytes) else r["out"]
    hits = [int(l.split()[0]) for l in out.splitlines()
            if f"sink_name={name}" in l]
    return hits[0] if len(hits) == 1 else None


def ns_load(name, extra_args=None):
    args = ["pactl", "load-module", "module-null-sink", f"sink_name={name}"]
    args += list(extra_args or [])
    r = sh(args, timeout=10.0)
    mid = None
    if r["rc"] == 0:
        try:
            mid = int(r["out"].decode().strip())
        except ValueError:
            mid = None
    ok = mid is not None and sink_module_index(name) == mid
    return {"rc": r["rc"], "module_id": mid, "err": r["err"].strip(),
            "name": name, "verified": ok}


def ns_unload(name):
    mid = sink_module_index(name)
    if mid is None:
        return {"skipped": "no unique module with that sink_name"}
    return {"module_id": mid,
            "unload": sh(["pactl", "unload-module", str(mid)], timeout=10.0)["rc"]}


# ---------------------------------------------------------------- tone/rec

def play(path, target, tag, props=None, extra_args=None):
    argv = ["pw-cat", "-p", "-P", f"node.name={tag}"]
    for x in props or []:
        argv += ["-P", x]
    argv += ["--target", target] + list(extra_args or []) + [path]
    return spawn(argv)


def rec_monitor(sink, path, frames, tag, extra=None, wall=15.0):
    argv = ["pw-record", "-P", "stream.capture.sink=true", "-P",
            f"node.name={tag}"]
    for x in extra or []:
        argv += ["-P", x]
    argv += ["--target", sink, "-n", str(frames), path]
    r = sh(argv, timeout=wall)
    r.update(path=path, exists=os.path.exists(path),
             bytes=os.path.getsize(path) if os.path.exists(path) else 0)
    return r


def rec_stream(target, path, frames, tag, extra=None, wall=15.0):
    argv = ["pw-record", "-P", f"node.name={tag}"]
    for x in extra or []:
        argv += ["-P", x]
    argv += ["--target", target, "-n", str(frames), path]
    r = sh(argv, timeout=wall)
    r.update(path=path, exists=os.path.exists(path),
             bytes=os.path.getsize(path) if os.path.exists(path) else 0)
    return r


# ---------------------------------------------------------------- analysis

def analyze(path, amp=TONE_AMP, quiet=64, foreign=400, freqs=(L_HZ, R_HZ)):
    res = {"path": path, "exists": os.path.exists(path)}
    if not res["exists"]:
        return res
    try:
        w = wave.open(path)
    except Exception as exc:
        res["error"] = f"wave: {exc}"
        return res
    n, ch, sw, rate = (w.getnframes(), w.getnchannels(), w.getsampwidth(),
                       w.getframerate())
    raw = w.readframes(n)
    res.update(frames=n, ch=ch, width=sw, rate=rate,
               bytes=os.path.getsize(path))
    if sw != 2 or n == 0:
        res["class"] = "non_s16" if sw != 2 else "empty"
        return res
    a = np.frombuffer(raw, dtype="<i2").astype(np.float64)
    a = a[: (len(a) // ch) * ch].reshape(-1, ch)
    res["peak"] = [int(np.abs(a[:, c]).max()) if len(a) else 0
                   for c in range(ch)]
    res["rms"] = [round(float(np.sqrt((a[:, c] ** 2).mean())), 2)
                  if len(a) else 0.0 for c in range(ch)]
    seg = a[len(a) // 4: len(a) // 4 + min(len(a) // 2, rate // 2)] if len(a) else a
    doms, at_freqs = [], []
    for c in range(ch):
        if len(seg) < 64:
            doms.append({"hz": None, "amp": 0.0})
            at_freqs.append([])
            continue
        x = seg[:, c] * np.hanning(len(seg))
        sp = np.abs(np.fft.rfft(x))
        k = int(np.argmax(sp))
        doms.append({"hz": round(k * rate / len(seg), 1),
                     "amp": round(float(sp[k]) * 2 / len(seg), 1)})
        at_freqs.append({f"{f:g}": round(goertzel_amp(seg[:, c], rate, f), 1)
                         for f in freqs})
    res["dom"] = doms
    res["amp_at"] = at_freqs
    cls = []
    for c in range(ch):
        pk = res["peak"][c]
        if pk <= quiet:
            cls.append("silence")
            continue
        hz = doms[c]["hz"]
        hit = next((f"tone{int(f)}" for f in freqs
                    if hz and abs(hz - f) <= 0.03 * f and pk >= 0.3 * amp), None)
        cls.append(hit or (f"foreign@{hz}Hz" if pk >= foreign
                           else f"noise@{hz}Hz"))
    res["class"] = cls
    res["carries_tone"] = any(c.startswith("tone") for c in cls)
    return res


def goertzel_amp(sig, rate, hz):
    n = len(sig)
    k = int(0.5 + n * hz / rate)
    w = 2 * math.pi * k / n
    coeff = 2 * math.cos(w)
    s0 = s1 = s2 = 0.0
    for x in sig:
        s0 = x + coeff * s1 - s2
        s2, s1 = s1, s0
    return math.sqrt(max(s1 * s1 + s2 * s2 - coeff * s1 * s2, 0.0)) * 2 / n


def fft_at(path, hz, ch=None, seconds=None, offset_s=0.5):
    """Goertzel amplitude at `hz` per channel over a window."""
    with wave.open(path) as w:
        n, chn, sw, rate = (w.getnframes(), w.getnchannels(), w.getsampwidth(),
                            w.getframerate())
        w.setpos(min(n - 1, int(offset_s * rate)))
        take = min(n - w.tell(), int((seconds or 1.0) * rate))
        raw = w.readframes(take)
    a = np.frombuffer(raw, dtype="<i2").astype(np.float64)
    a = a[: (len(a) // chn) * chn].reshape(-1, chn)
    out = []
    for c in range(chn):
        seg = a[:, c] if ch is None or c == ch else None
        out.append(None if seg is None else
                   round(goertzel_amp(seg, rate, hz), 1))
    return out


# ---------------------------------------------------------------- loopback

def lb_start(name, args, secs=8):
    return spawn(["timeout", "-s", "KILL", str(secs), "pw-loopback",
                  "-n", name] + list(args))


def wait_nodes(substr, want, timeout=4.0):
    t0 = time.monotonic()
    g = None
    while time.monotonic() - t0 < timeout:
        g = Graph(pw_dump())
        got = [n for n in g.nodes if substr in n]
        if len(got) >= want:
            return g, got, round(time.monotonic() - t0, 3)
        time.sleep(0.15)
    g = Graph(pw_dump())
    return g, [n for n in g.nodes if substr in n], round(
        time.monotonic() - t0, 3)


def lb_leg(leg_id, name, args, wait=1.2, secs=8, sample_props=None):
    """Spawn pw-loopback, snapshot node props + edges, reap."""
    rec = {"leg": leg_id, "name": name, "args": list(args)}
    lb = lb_start(name, args, secs)
    try:
        g, got, ws = wait_nodes(name, 2)
        rec["wait_s"] = ws
        rec["nodes"] = got
        if len(got) < 2:
            rec["spawn_note"] = "fewer than 2 nodes"
        time.sleep(wait)
        g = Graph(pw_dump())
        for n in got:
            node = g.node(n)
            if not node:
                continue
            p = node["props"]
            keys = sorted(sample_props) if sample_props else sorted(p.keys())
            rec.setdefault("props", {})[n] = {
                "id": node["id"], "class": node["class"],
                "in_ports": [x[0] for x in node["in"]],
                "out_ports": [x[0] for x in node["out"]],
                "picked": {k: p.get(k) for k in keys}}
        rec["edges"] = g.edges(name)
        rec["peers_in"] = {n: g.peers(n, "in") for n in got if "input" in n}
        rec["peers_out"] = {n: g.peers(n, "out") for n in got if "output" in n}
    finally:
        rr = reap(lb, wait=secs + 1)
        rec["rc"] = rr["rc"]
        rec["stderr"] = rr["stderr"].strip()
    return rec


def save_receipt(name, obj):
    path = os.path.join(RECEIPTS, name)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, sort_keys=True, default=str)
    return path
