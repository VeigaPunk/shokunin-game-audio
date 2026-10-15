#!/usr/bin/env python3
"""r83 boundary harness — own tones, own FFT/analysis, own null sinks r83b_*.

Seat: audio r83 boundary (executor-class, leaf). Attacking the r83 scout pins
under varied host state. Every PipeWire/Pulse object this seat creates is
r83b_*; every module is unloaded strictly by index verified against
(sink_name, module-null-sink). Never targets SPDIF/Line or any foreign object.

No tracked writes: everything lands under corpus/live/r83-boundary/.
"""
import json
import math
import os
import re
import signal
import subprocess
import sys
import time
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")
RECEIPTS = os.path.join(HERE, "receipts")
SCRATCH = os.path.join(HERE, "scratch")
RAW = os.path.join(HERE, "raw")

NS_A = "r83b_nsa"      # stereo 48k source-side null sink
NS_B = "r83b_nsb"      # stereo 48k sink-side null sink
NS_M = "r83b_nsm"      # mono 48k null sink
NS_48 = "r83b_ns48"    # stereo 48k null sink (resample legs)
NS_44 = "r83b_ns44"    # stereo 44.1k null sink

DEFAULT_SINK = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink"
DEFAULT_SOURCE = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source"

L_HZ, R_HZ, TONE_AMP = 1000.0, 1500.0, 8192
TONE_S = 2.0

_state = {"procs": [], "hogs": [], "modules": {}}
_foreign = []


def now():
    return time.strftime("%H:%M:%S")


def sh(cmd, timeout=20.0, env=None):
    t0 = time.monotonic()
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout, env=env)
        return {"cmd": [str(c) for c in cmd], "rc": p.returncode,
                "out": p.stdout.decode("utf-8", "replace"),
                "err": p.stderr.decode("utf-8", "replace"),
                "wall": round(time.monotonic() - t0, 3), "timeout": False}
    except subprocess.TimeoutExpired as e:
        def dec(x):
            if x is None:
                return ""
            return x.decode("utf-8", "replace") if isinstance(x, bytes) else x
        return {"cmd": [str(c) for c in cmd], "rc": None, "out": dec(e.stdout),
                "err": dec(e.stderr), "wall": round(time.monotonic() - t0, 3),
                "timeout": True}


def spawn(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE):
    p = subprocess.Popen(cmd, stdout=stdout, stderr=stderr,
                         start_new_session=True)
    _state["procs"].append(p)
    return p


def reap(p, wait=6.0):
    """Wait for a spawned proc; return rc/stderr, kill its group if needed."""
    try:
        _, err = p.communicate(timeout=wait)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            p.kill()
        try:
            _, err = p.communicate(timeout=3)
        except Exception:
            err = b""
    if p in _state["procs"]:
        _state["procs"].remove(p)
    return {"rc": p.returncode,
            "err": (err or b"").decode("utf-8", "replace").strip()}


def kill_all():
    for p in list(_state["procs"]):
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            try:
                p.kill()
            except Exception:
                pass
    _state["procs"].clear()


# ---------------------------------------------------------------- load hogs

def hogs_start(n):
    started = []
    for _ in range(n):
        p = subprocess.Popen(["yes"], stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=True)
        started.append(p)
        _state["hogs"].append(p)
    time.sleep(2.0)
    return len(started)


def hogs_stop():
    for p in list(_state["hogs"]):
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            try:
                p.kill()
            except Exception:
                pass
    _state["hogs"].clear()
    time.sleep(1.0)


# ---------------------------------------------------------------- graph view

def pw_dump():
    r = sh(["pw-dump"], timeout=25.0)
    try:
        return json.loads(r["out"] or "[]")
    except json.JSONDecodeError:
        return []


class Graph:
    def __init__(self, objs):
        self.objs = objs
        self.node_by_name = {}
        self.props_by_id = {}
        self.port_name = {}
        for o in objs:
            if o.get("type") == "PipeWire:Interface:Node":
                p = (o.get("info") or {}).get("props") or {}
                nm = p.get("node.name")
                if nm:
                    self.node_by_name[nm] = o
            if o.get("type") in ("PipeWire:Interface:Node",
                                 "PipeWire:Interface:Port"):
                self.props_by_id[o["id"]] = ((o.get("info") or {})
                                             .get("props") or {})
            if o.get("type") == "PipeWire:Interface:Port":
                p = self.props_by_id[o["id"]]
                if p.get("port.name"):
                    self.port_name[o["id"]] = p["port.name"]

    def nodes_matching(self, substr):
        return sorted(n for n in self.node_by_name if substr in n)

    def node(self, name):
        o = self.node_by_name.get(name)
        return ((o.get("info") or {}).get("props") or {}) if o else None

    def edges(self, substr=None):
        out = []
        for o in self.objs:
            if o.get("type") != "PipeWire:Interface:Link":
                continue
            p = (o.get("info") or {}).get("props") or {}
            on, inn = p.get("link.output.node"), p.get("link.input.node")
            if on is None or inn is None:
                continue
            onm = (self.props_by_id.get(on) or {}).get("node.name", str(on))
            inm = (self.props_by_id.get(inn) or {}).get("node.name", str(inn))
            if substr and substr not in onm and substr not in inm:
                continue
            out.append(f"{onm}:{p.get('link.output.port')} -> "
                       f"{inm}:{p.get('link.input.port')}")
        return sorted(out)


def props_of(name, keys):
    g = Graph(pw_dump())
    p = g.node(name) or {}
    return {k: p.get(k) for k in keys}


# ---------------------------------------------------------------- null sinks

def sink_rows():
    r = sh(["pactl", "list", "short", "sinks"], timeout=10.0)
    return [ln.split("\t") for ln in r["out"].splitlines() if ln.strip()]


def module_rows():
    r = sh(["pactl", "list", "short", "modules"], timeout=10.0)
    return [ln.split("\t") for ln in r["out"].splitlines() if ln.strip()]


def ns_load(name, extra=None):
    """Load module-null-sink; verify by row; refuse duplicates."""
    if any(len(r) > 1 and r[1] == name for r in sink_rows()):
        return {"name": name, "rc": "dup-refused", "verified": False}
    argv = ["pactl", "load-module", "module-null-sink", f"sink_name={name}"]
    argv += list(extra or [])
    r = sh(argv, timeout=10.0)
    mid = (r["out"] or "").strip()
    ok = r["rc"] == 0 and mid.isdigit()
    verified = False
    if ok:
        for row in module_rows():
            if len(row) >= 3 and row[0] == mid and \
                    "module-null-sink" in row[1] and f"sink_name={name}" in row[2]:
                verified = True
    if verified:
        _state["modules"][name] = mid
    return {"name": name, "rc": r["rc"], "module_id": mid, "err": r["err"],
            "verified": verified}


def ns_unload(name):
    mid = _state["modules"].get(name)
    if not mid:
        return {"name": name, "rc": "not-loaded"}
    ok = False
    for row in module_rows():
        if len(row) >= 3 and row[0] == mid and "module-null-sink" in row[1] \
                and f"sink_name={name}" in row[2]:
            ok = True
    if not ok:
        return {"name": name, "rc": "verify-failed", "verified": False}
    r = sh(["pactl", "unload-module", mid], timeout=10.0)
    del _state["modules"][name]
    return {"name": name, "rc": r["rc"], "verified": True}


# ---------------------------------------------------------------- tones

def _write_wav(path, rate, chans):
    n = int(rate * TONE_S)
    t = np.arange(n) / rate
    if chans == 1:
        data = (TONE_AMP * np.sin(2 * math.pi * L_HZ * t)).astype("<i2")
    else:
        l = TONE_AMP * np.sin(2 * math.pi * L_HZ * t)
        r = TONE_AMP * np.sin(2 * math.pi * R_HZ * t)
        data = np.stack([l, r], axis=1).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(chans)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(data.tobytes())
    return path


def ensure_tones():
    os.makedirs(SCRATCH, exist_ok=True)
    out = {}
    for key, rate, ch in (("tone48", 48000, 2), ("tone44", 44100, 2),
                          ("mono48", 48000, 1), ("stereo48", 48000, 2)):
        p = os.path.join(SCRATCH, f"{key}.wav")
        if not os.path.exists(p):
            _write_wav(p, rate, ch)
        out[key] = p
    return out


def midi_file():
    """42-byte SMF: tempo, note C4 on/off, end of track (own generation)."""
    p = os.path.join(SCRATCH, "r83b_note.mid")
    if os.path.exists(p):
        return p
    hdr = b"MThd" + (6).to_bytes(4, "big") + (0).to_bytes(2, "big") + \
        (1).to_bytes(2, "big") + (96).to_bytes(2, "big")
    tr = bytearray()
    tr += b"\x00\xff\x51\x03\x07\xa1\x20"
    tr += b"\x00\x90\x3c\x60"
    tr += b"\x81\x70\x80\x3c\x40"
    tr += b"\x00\xff\x2f\x00"
    trk = b"MTrk" + len(tr).to_bytes(4, "big") + bytes(tr)
    with open(p, "wb") as fh:
        fh.write(hdr + trk)
    return p


# ---------------------------------------------------------------- analysis

def _goertzel(sig, rate, hz):
    n = len(sig)
    if n == 0:
        return 0.0
    k = int(0.5 + n * hz / rate)
    w = 2 * math.pi * k / n
    coeff = 2 * math.cos(w)
    s0 = s1 = s2 = 0.0
    for x in sig:
        s0 = x + coeff * s1 - s2
        s2, s1 = s1, s0
    return math.sqrt(max(s1 * s1 + s2 * s2 - coeff * s1 * s2, 0.0)) * 2 / n


def analyze(path, freqs=(L_HZ, R_HZ), quiet=64, foreign=400, offset=0.5,
            window=1.0):
    res = {"path": path, "exists": os.path.exists(path)}
    if not res["exists"]:
        return res
    try:
        w = wave.open(path)
    except Exception as exc:
        res["error"] = f"wave: {exc}"
        return res
    n, ch, sw, rate = w.getnframes(), w.getnchannels(), w.getsampwidth(), \
        w.getframerate()
    raw = w.readframes(n)
    res.update(frames=n, ch=ch, width=sw, rate=rate,
               bytes=os.path.getsize(path))
    if sw != 2 or n == 0:
        res["class"] = "non_s16" if sw != 2 else "empty"
        return res
    a = np.frombuffer(raw, dtype="<i2").astype(np.float64)
    a = a[:(len(a) // ch) * ch].reshape(-1, ch)
    res["peak"] = [int(np.abs(a[:, c]).max()) for c in range(ch)]
    res["mean"] = [round(float(a[:, c].mean()), 2) for c in range(ch)]
    res["rms"] = [round(float(np.sqrt((a[:, c] ** 2).mean())), 2)
                  for c in range(ch)]
    res["min"] = [int(a[:, c].min()) for c in range(ch)]
    res["max"] = [int(a[:, c].max()) for c in range(ch)]
    neg = int((a < 0).sum())
    res["neg_frac"] = round(neg / max(1, a.size), 4)
    # longest-run zero histogram (sample == 0 exactly)
    z = (a[:, 0] == 0)
    runs = []
    run = 0
    for v in z:
        if v:
            run += 1
        elif run:
            runs.append(run)
            run = 0
    if run:
        runs.append(run)
    res["zero_runs_n"] = len(runs)
    if runs:
        res["zero_run_hist"] = {str(k): runs.count(k)
                                for k in sorted(set(runs))}
    res["all_zero"] = bool(len(a) and np.abs(a).max() == 0)
    off = int(offset * rate)
    take = int(window * rate)
    seg = a[off:off + take] if len(a) > off + 64 else a
    doms, at = [], []
    for c in range(ch):
        if len(seg) < 64:
            doms.append({"hz": None, "amp": 0.0})
            at.append({})
            continue
        x = seg[:, c] * np.hanning(len(seg))
        sp = np.abs(np.fft.rfft(x))
        k = int(np.argmax(sp))
        doms.append({"hz": round(k * rate / len(seg), 1),
                     "amp": round(float(sp[k]) * 2 / len(seg), 1)})
        at.append({f"{f:g}": round(_goertzel(seg[:, c], rate, f), 1)
                   for f in freqs})
    res["dom"] = doms
    res["amp_at"] = at
    cls = []
    for c in range(ch):
        pk = res["peak"][c]
        if pk <= quiet:
            cls.append("silence")
            continue
        hz = doms[c]["hz"]
        hit = next((f"tone{int(f)}" for f in freqs
                    if hz and abs(hz - f) <= 0.03 * f and pk >= 0.3 * TONE_AMP),
                   None)
        cls.append(hit or (f"foreign@{hz}Hz" if pk >= foreign
                           else f"noise@{hz}Hz"))
    res["class"] = cls
    res["carries_tone"] = any(c.startswith("tone") for c in cls)
    return res


def onset(path, thresh=500):
    """First sample index with |x| > thresh, in seconds (None if none)."""
    if not os.path.exists(path):
        return None
    try:
        w = wave.open(path)
        n, ch, sw, rate = (w.getnframes(), w.getnchannels(), w.getsampwidth(),
                           w.getframerate())
        raw = w.readframes(n)
    except Exception:
        return None
    a = np.frombuffer(raw, dtype="<i2").astype(np.float64)
    a = a[:(len(a) // ch) * ch].reshape(-1, ch)
    if not len(a):
        return None
    mag = np.abs(a).max(axis=1)
    idx = np.nonzero(mag > thresh)[0]
    if not len(idx):
        return None
    return {"first_s": round(float(idx[0]) / rate, 4),
            "first_idx": int(idx[0]), "rate": rate, "frames": n}


# ---------------------------------------------------------------- leg runner

def leg_dir(stage, leg):
    d = os.path.join(RUNS, stage, leg)
    os.makedirs(d, exist_ok=True)
    return d


def save_leg(stage, leg, rec):
    d = leg_dir(stage, leg)
    with open(os.path.join(d, "meta.json"), "w") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True, default=str)
    return d


def save_receipt(name, obj):
    os.makedirs(RECEIPTS, exist_ok=True)
    path = os.path.join(RECEIPTS, name)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, sort_keys=True, default=str)
    return path


# ---------------------------------------------------------------- loopback

LB_BASE = ["-C", NS_A, "-i", "stream.capture.sink=true", "-P", NS_B]


def lb_leg(stage, leg, name, args, wait=1.3, secs=5, sample_props=None,
           timeout_s=8):
    """Spawn pw-loopback, snapshot props/edges (no content witness)."""
    d = leg_dir(stage, leg)
    rec = {"leg": leg, "name": name, "args": list(args),
           "load_before": os.getloadavg()}
    with open(os.path.join(d, "cmd.txt"), "w") as fh:
        fh.write(" ".join(["pw-loopback", "-n", name] + [str(a) for a in args]))
    lb = spawn(["timeout", "-s", "KILL", str(timeout_s), "pw-loopback",
                "-n", name] + list(args))
    rec_audio = None
    try:
        g, got, ws = None, [], 0.0
        t0 = time.monotonic()
        while time.monotonic() - t0 < 4.0:
            g = Graph(pw_dump())
            got = g.nodes_matching(name)
            if len(got) >= 2:
                break
            time.sleep(0.15)
        ws = round(time.monotonic() - t0, 3)
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
            keys = sorted(sample_props) if sample_props else sorted(node)
            rec.setdefault("props", {})[n] = {
                "id": g.node_by_name[n]["id"],
                "picked": {k: node.get(k) for k in keys}}
        rec["edges"] = g.edges(name)
    finally:
        rr = reap(lb, wait=timeout_s + 2)
        rec["rc"] = rr["rc"]
        rec["stderr"] = rr["err"]
        with open(os.path.join(d, "stderr.txt"), "w") as fh:
            fh.write(rr["err"])
    rec["load_after"] = os.getloadavg()
    save_leg(stage, leg, rec)
    return rec


def lb_content_leg(stage, leg, name, args, tone_wav, tone_src, mon_sink,
                   secs=6, sample_props=None, timeout_s=8):
    """Play tone into tone_src; record mon_sink monitor while loopback runs."""
    d = leg_dir(stage, leg)
    rec = {"leg": leg, "name": name, "args": list(args),
           "tone_wav": tone_wav, "tone_src": tone_src, "mon_sink": mon_sink,
           "load_before": os.getloadavg()}
    with open(os.path.join(d, "cmd.txt"), "w") as fh:
        fh.write(" ".join(["pw-loopback", "-n", name] + [str(a) for a in args]))
    out = os.path.join(RAW, f"{leg}_mon.wav")
    mon = spawn(["timeout", "-s", "INT", "10", "pw-record",
                 "-P", "stream.capture.sink=true",
                 "-P", f"node.name={name}_rec", "--target", mon_sink,
                 "-n", str(int(48000 * TONE_S * 1.5)), "--rate", "48000",
                 "--channels", "2", "--format", "s16", out])
    lb = spawn(["timeout", "-s", "KILL", str(timeout_s), "pw-loopback",
                "-n", name] + list(args))
    try:
        g, got, ws = None, [], 0.0
        t0 = time.monotonic()
        while time.monotonic() - t0 < 4.0:
            g = Graph(pw_dump())
            got = g.nodes_matching(name)
            if len(got) >= 2:
                break
            time.sleep(0.15)
        ws = round(time.monotonic() - t0, 3)
        rec["wait_s"], rec["nodes"] = ws, got
        tone = spawn(["timeout", "-s", "KILL", "6", "pw-cat", "-p",
                      "-P", f"node.name={name}_tone", "--target", tone_src,
                      tone_wav])
        try:
            time.sleep(2.0)
            g = Graph(pw_dump())
            for n in got:
                node = g.node(n)
                if not node:
                    continue
                keys = sorted(sample_props) if sample_props else sorted(node)
                rec.setdefault("props", {})[n] = {
                    "id": g.node_by_name[n]["id"],
                    "picked": {k: node.get(k) for k in keys}}
            rec["edges"] = g.edges(name)
        finally:
            reap(tone, 3)
        rr = reap(mon, wait=6)
        rec["rec_rc"], rec["rec_err"] = rr["rc"], rr["err"]
        rec["content"] = analyze(out) if os.path.exists(out) else {"exists": False}
    finally:
        rr = reap(lb, wait=timeout_s + 2)
        rec["rc"] = rr["rc"]
        rec["stderr"] = rr["err"]
        with open(os.path.join(d, "stderr.txt"), "w") as fh:
            fh.write(rr["err"])
    rec["load_after"] = os.getloadavg()
    save_leg(stage, leg, rec)
    return rec


def pc_leg(stage, leg, name, wav, target, props=None, mon_sink=None,
           timeout_s=6, extra=None, mon_ch=2):
    """pw-cat playback leg with monitor witness."""
    d = leg_dir(stage, leg)
    rec = {"leg": leg, "name": name, "wav": wav, "target": target,
           "stream_props": list(props or []), "load_before": os.getloadavg()}
    cmd = ["pw-cat", "-p", "-P", f"node.name={name}"]
    for x in props or []:
        cmd += ["-P", x]
    cmd += ["--target", target] + list(extra or []) + [wav]
    with open(os.path.join(d, "cmd.txt"), "w") as fh:
        fh.write(" ".join(cmd))
    out = os.path.join(RAW, f"{leg}_mon.wav")
    mon = None
    if mon_sink:
        mon = spawn(["timeout", "-s", "INT", "10", "pw-record",
                     "-P", "stream.capture.sink=true",
                     "-P", f"node.name={name}_rec", "--target", mon_sink,
                     "-n", str(int(48000 * TONE_S * 1.5)), "--rate", "48000",
                     "--channels", str(mon_ch), "--format", "s16", out])
    play = spawn(["timeout", "-s", "KILL", str(timeout_s)] + cmd)
    try:
        t0 = time.monotonic()
        g, got = None, []
        while time.monotonic() - t0 < 4.0:
            g = Graph(pw_dump())
            got = g.nodes_matching(name)
            if got:
                break
            time.sleep(0.1)
        rec["wait_s"] = round(time.monotonic() - t0, 3)
        rec["nodes"] = got
        time.sleep(1.2)
        g = Graph(pw_dump())
        for n in got:
            node = g.node(n)
            if node:
                rec.setdefault("props", {})[n] = {
                    "id": g.node_by_name[n]["id"],
                    "picked": {k: node.get(k) for k in
                               ("node.name", "media.class", "target.object",
                                "stream.dont-remix", "node.dont-remix",
                                "node.passive", "node.dont-move",
                                "channelmix.stereo-widen", "node.rate",
                                "resample.disable", "resample.peaks",
                                "node.latency")}}
        rec["edges"] = g.edges(name)
        if mon:
            rr = reap(mon, wait=7)
            rec["rec_rc"], rec["rec_err"] = rr["rc"], rr["err"]
            rec["content"] = analyze(out) if os.path.exists(out) else \
                {"exists": False}
    finally:
        rr = reap(play, wait=timeout_s + 2)
        rec["rc"] = rr["rc"]
        rec["stderr"] = rr["err"]
        with open(os.path.join(d, "stderr.txt"), "w") as fh:
            fh.write(rr["err"])
    rec["load_after"] = os.getloadavg()
    save_leg(stage, leg, rec)
    return rec


# ---------------------------------------------------------------- host state

def host_snapshot():
    r = sh(["pactl", "list", "short", "sinks"], timeout=10.0)
    sinks = r["out"].strip().splitlines()
    r2 = sh(["pactl", "list", "short", "sources"], timeout=10.0)
    srcs = r2["out"].strip().splitlines()
    r3 = sh(["pactl", "get-default-sink"], timeout=10.0)
    r4 = sh(["pactl", "get-default-source"], timeout=10.0)
    return {
        "time": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "loadavg": os.getloadavg(),
        "nproc": os.cpu_count(),
        "default_sink": r3["out"].strip(),
        "default_source": r4["out"].strip(),
        "sinks": sinks,
        "sources": srcs,
        "foreign_r93s": [s for s in sinks + srcs if "r93s" in s],
        "foreign_r82ff": [s for s in sinks + srcs if "r82ff" in s],
        "r83b_rows": [s for s in sinks + srcs if "r83b" in s],
    }


def check_defaults():
    a = sh(["pactl", "get-default-sink"], timeout=10.0)["out"].strip()
    b = sh(["pactl", "get-default-source"], timeout=10.0)["out"].strip()
    return {"sink": a, "source": b,
            "sink_ok": a == DEFAULT_SINK, "source_ok": b == DEFAULT_SOURCE}
