#!/usr/bin/env python3
"""R79 boundary follow-up — does the *order of stream creation* decide whether a
SIGSTOP'd pw-loopback stalls its graph or keeps carrying live content?

Two orders x 2 reps. Marker: at the freeze instant the 1 kHz source is killed
and a 1.5 kHz source started. If the tap shows 1.5 kHz while the client is in
state T, the path is live; if it goes silent, the graph stalled.

Writes r79b-freeze-order.json next to this file. Probe-owned names only, no
tone outside r79bo_* null sinks, everything torn down in a finally.
"""
import json
import os
import signal
import subprocess
import time
import wave
from pathlib import Path

import numpy as np

SEAT = Path(__file__).resolve().parent
PID = os.getpid()
PREFIX = f"r79bo_{PID}"
RATE = 48000
PROCS = []
SINKS = {}


def sh(argv, timeout=20.0):
    p = subprocess.run(argv, capture_output=True, timeout=timeout)
    return {"rc": p.returncode, "out": p.stdout.decode(errors="replace"),
            "err": p.stderr.decode(errors="replace")}


def spawn(argv):
    p = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                         stderr=subprocess.PIPE, start_new_session=True)
    PROCS.append(p)
    return p


def kill(p, sig=signal.SIGKILL):
    if p is None:
        return
    try:
        os.killpg(os.getpgid(p.pid), sig)
    except ProcessLookupError:
        pass
    try:
        p.wait(timeout=3)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
        p.wait(timeout=3)


def wav(path, hz, seconds=20):
    n = int(RATE * seconds)
    t = np.arange(n) / RATE
    x = (8192 * np.sin(2 * np.pi * hz * t)).astype("<i2")
    a = np.stack([x, x], 1)
    w = wave.open(str(path), "wb")
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(RATE)
    w.writeframes(a.astype("<i2").tobytes())
    w.close()


def amp(seg, hz):
    if len(seg) == 0:
        return 0.0
    tt = np.arange(len(seg)) / RATE
    re = 2 * np.dot(seg, np.cos(2 * np.pi * hz * tt)) / len(seg)
    im = 2 * np.dot(seg, np.sin(2 * np.pi * hz * tt)) / len(seg)
    return float(np.hypot(re, im))


def timeline(path, lo=0.0, hi=12.0, step=0.25):
    w = wave.open(str(path))
    a = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(float)
    a = a.reshape(-1, 2)[:, 0]
    w.close()
    out = []
    for s in np.arange(lo, hi, step):
        seg = a[int(s * RATE):int((s + 0.15) * RATE)]
        out.append([round(float(s), 2), round(amp(seg, 1000.0), 1),
                    round(amp(seg, 1500.0), 1)])
    return out


def null_sink(name):
    r = sh(["pactl", "load-module", "module-null-sink", f"sink_name={name}"])
    SINKS[name] = int(r["out"].strip()) if r["out"].strip().isdigit() else None


def run(order, rep):
    tag = f"{order}-{rep}"
    ns_a, ns_b = f"{PREFIX}_ns_a_{order}_{rep}", f"{PREFIX}_ns_b_{order}_{rep}"
    null_sink(ns_a)
    null_sink(ns_b)
    time.sleep(0.7)
    tone1 = f"/tmp/{PREFIX}_1k.wav"
    tone2 = f"/tmp/{PREFIX}_15k.wav"
    wav(tone1, 1000.0)
    wav(tone2, 1500.0)
    lb = None
    leg = {"order": order, "rep": rep, "ns_a": ns_a, "ns_b": ns_b}

    def start_tone(path, name):
        return spawn(["pw-cat", "-p", "-P", f"node.name={PREFIX}_{name}",
                      "--target", ns_a, path])

    def wait_nodes(name, timeout=6.0):
        t0 = time.monotonic()
        while time.monotonic() - t0 < timeout:
            g = json.loads(sh(["pw-dump"])["out"])
            names = [((o.get("info") or {}).get("props") or {}).get("node.name")
                     for o in g if o.get("type", "").endswith("Node")]
            if f"input.{name}" in names and f"output.{name}" in names:
                return True
            time.sleep(0.15)
        return False

    try:
        if order in ("harness-like", "harness-like-1swap", "loopback-first-2swap"):
            lb = spawn(["timeout", "-s", "KILL", "25", "pw-loopback", "-n",
                        f"{PREFIX}_lb_{tag}", "-C", ns_a,
                        "-i", "stream.capture.sink=true", "-P", ns_b])
            leg["nodes_seen"] = wait_nodes(f"{PREFIX}_lb_{tag}")
            if order == "loopback-first-2swap":
                time.sleep(0.8)
            t1 = start_tone(tone1, f"t1_{tag}")
            if order == "loopback-first-2swap":
                time.sleep(1.5)
            p = SEAT / f"raw/{PREFIX}_freeze_{tag}.wav"
            tap = spawn(["pw-record", "-P", f"node.name={PREFIX}_rec_{tag}",
                         "-P", "stream.capture.sink=true", "--target", ns_b,
                         "-n", str(RATE * 10), str(p)])
            time.sleep(2.0 if order != "loopback-first-2swap" else 1.5)
            os.killpg(os.getpgid(lb.pid), signal.SIGSTOP)
            kill(t1)
            t2 = start_tone(tone2, f"t2_{tag}")
            time.sleep(2.5)
            if order != "harness-like-1swap":
                kill(t2)
                t3 = start_tone(tone1, f"t3_{tag}")
                time.sleep(2.0)
            leg["ps"] = sh(["ps", "-o", "pid,stat,nlwp,cmd", "-g",
                            str(os.getpgid(lb.pid))])["out"].strip()
            os.killpg(os.getpgid(lb.pid), signal.SIGCONT)
            time.sleep(1.5)
            kill(t2)
            if order != "harness-like-1swap":
                kill(t3)
            try:
                tap.wait(timeout=12)
            except subprocess.TimeoutExpired:
                kill(tap)
            leg["tap_rc"] = tap.returncode
            leg["timeline"] = timeline(p)
            live = [row for row in leg["timeline"] if row[2] > 4096]
            leg["pattern"] = ("live-swap-continued" if live
                              else "stalled-or-silent")
            leg["swap_windows"] = live[:4]
            return leg
        if order == "source-first":
            t1 = start_tone(tone1, f"t1_{tag}")
            time.sleep(0.8)
            lb = spawn(["timeout", "-s", "KILL", "25", "pw-loopback", "-n",
                        f"{PREFIX}_lb_{tag}", "-C", ns_a,
                        "-i", "stream.capture.sink=true", "-P", ns_b])
            time.sleep(1.5)
        else:
            lb = spawn(["timeout", "-s", "KILL", "25", "pw-loopback", "-n",
                        f"{PREFIX}_lb_{tag}", "-C", ns_a,
                        "-i", "stream.capture.sink=true", "-P", ns_b])
            time.sleep(0.8)
            t1 = start_tone(tone1, f"t1_{tag}")
            time.sleep(1.5)
        p = SEAT / f"raw/{PREFIX}_freeze_{tag}.wav"
        tap = spawn(["pw-record", "-P", f"node.name={PREFIX}_rec_{tag}",
                     "-P", "stream.capture.sink=true", "--target", ns_b,
                     "-n", str(RATE * 10), str(p)])
        time.sleep(1.5)
        os.killpg(os.getpgid(lb.pid), signal.SIGSTOP)
        kill(t1)
        t2 = start_tone(tone2, f"t2_{tag}")
        time.sleep(2.5)
        leg["ps"] = sh(["ps", "-o", "pid,stat,nlwp,cmd", "-g",
                        str(os.getpgid(lb.pid))])["out"].strip()
        leg["links"] = sh(["pw-link", "-l"])["out"]
        os.killpg(os.getpgid(lb.pid), signal.SIGCONT)
        time.sleep(1.0)
        kill(t2)
        try:
            tap.wait(timeout=12)
        except subprocess.TimeoutExpired:
            kill(tap)
        leg["tap_rc"] = tap.returncode
        leg["timeline"] = timeline(p)
        live = [row for row in leg["timeline"] if row[2] > 4096]
        leg["pattern"] = ("live-swap-continued" if live else "stalled-or-silent")
        leg["swap_windows"] = live[:4]
    finally:
        kill(lb)
    return leg


def main():
    (SEAT / "raw").mkdir(parents=True, exist_ok=True)
    out = {"pid": PID, "legs": []}
    try:
        for order in ("source-first", "loopback-first", "harness-like",
                      "harness-like-1swap", "loopback-first-2swap"):
            for rep in (1, 2):
                out["legs"].append(run(order, rep))
    finally:
        for p in PROCS:
            if p.poll() is None:
                kill(p)
        for n, mid in SINKS.items():
            if mid:
                sh(["pactl", "unload-module", str(mid)])
    (SEAT / "r79b-freeze-order.json").write_text(
        json.dumps(out, indent=1) + "\n")
    for leg in out["legs"]:
        print(leg["order"], leg["rep"], "->", leg["pattern"],
              "| swap windows:", leg["swap_windows"])


if __name__ == "__main__":
    main()
