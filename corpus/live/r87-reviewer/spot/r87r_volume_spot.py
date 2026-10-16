#!/usr/bin/env python3
"""r87 reviewer — S2c: spawn-time --volume 0.0 / 1.5 through one tap."""
import json
import math
import os
import signal
import struct
import subprocess
import time
import wave
from pathlib import Path

PID = os.getpid()
PFX = f"r87r_{PID}"
NS = f"r87r_ns_{PID}"
TAP = f"r87r_tap_{PID}"
TMP = Path(os.environ.get("TMPDIR", "/tmp")) / f"r87r-v-{PID}"
TMP.mkdir(parents=True, exist_ok=True)
OUT = Path(__file__).resolve().parent / "volume-spot.json"


def run(argv, timeout=20.0):
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout)
        return {"rc": p.returncode, "stdout": p.stdout.decode()[:200],
                "stderr": p.stderr.decode()[:200]}
    except subprocess.TimeoutExpired:
        return {"rc": None, "timeout": True, "stdout": "", "stderr": ""}


def spawn(argv):
    return subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            stdin=subprocess.DEVNULL,
                            start_new_session=True)


def kill(p):
    if p is None:
        return
    try:
        os.killpg(p.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        p.wait(timeout=4)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        p.wait(timeout=3)


def tone(path, seconds=12.0, amp=12000, rate=48000):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        buf = bytearray()
        for i in range(int(seconds * rate)):
            v = int(amp * math.sin(2 * math.pi * 1000.0 * i / rate))
            buf += struct.pack("<hh", v, v)
        w.writeframes(bytes(buf))


def series(path, win=0.1):
    import numpy as np
    with wave.open(str(path), "rb") as w:
        rate, ch = w.getframerate(), w.getnchannels()
        data = w.readframes(w.getnframes())
    a = np.frombuffer(data, dtype="<i2").astype("float64")
    if not len(a):
        return []
    a = a.reshape(-1, ch).mean(axis=1)
    step = int(rate * win)
    return [(i / rate, float(np.sqrt((a[i:i + step] ** 2).mean())))
            for i in range(0, len(a) - step, step)]


def med(s, lo, hi):
    v = sorted(x for t, x in s if lo <= t <= hi)
    return v[len(v) // 2] if v else None


def main():
    out = {}
    tf = TMP / "tone.wav"
    tone(tf)
    m = run(["pactl", "load-module", "module-null-sink",
             f"sink_name={NS}"])
    idx = m["stdout"].strip() if m["rc"] == 0 else None
    time.sleep(0.7)
    try:
        tapf = TMP / "tap.wav"
        tap = spawn(["pw-record", "-P", f"node.name={TAP}", "-P",
                     "stream.capture.sink=true", "--target", NS,
                     str(tapf)])
        time.sleep(1.0)
        marks = {}
        t0 = time.monotonic()
        for label, vol in (("v100", "1.0"), ("v150", "1.5"),
                           ("v000", "0.0")):
            at = time.monotonic() - t0
            p = spawn(["pw-play", "-P", f"node.name={PFX}_{label}",
                       "--volume", vol, "--target", NS, str(tf)])
            marks[label] = {"volume": vol, "spawn_s": round(at, 3)}
            time.sleep(2.6)
            kill(p)
            time.sleep(0.4)
        kill(tap)
        s = series(tapf)
        for label, mk in marks.items():
            mk["median_peak"] = med(s, mk["spawn_s"] + 1.0,
                                    mk["spawn_s"] + 2.0)
        base = (marks.get("v100") or {}).get("median_peak")
        for label, mk in marks.items():
            mk["ratio_vs_v100"] = (round(mk["median_peak"] / base, 4)
                                   if mk["median_peak"] is not None and base
                                   else None)
        out["volume_spot"] = marks
        out["verdict"] = {
            "v150_ratio_15": bool(marks["v150"]["ratio_vs_v100"] and
                                  abs(marks["v150"]["ratio_vs_v100"] - 1.5)
                                  <= 0.05),
            "v000_zero": bool(marks["v000"]["median_peak"] is not None and
                              marks["v000"]["median_peak"] <= 200)}
    finally:
        un = None
        for _ in range(5):
            short = run(["pactl", "list", "modules", "short"])
            for ln in short["stdout"].splitlines():
                parts = ln.split("\t")
                if len(parts) >= 3 and f"sink_name={NS}" in parts[2]:
                    un = {"verified_index": parts[0].strip(),
                          "unload": run(["pactl", "unload-module",
                                         parts[0].strip()])}
                    break
            if un:
                break
            time.sleep(1.0)
        out["_unload"] = un
        time.sleep(0.5)
        sinks = run(["pactl", "list", "sinks", "short"])["stdout"]
        out["_residue_sinks"] = [ln for ln in sinks.splitlines()
                                 if PFX in ln]
        OUT.write_text(json.dumps(out, indent=1) + "\n")
        print(json.dumps(out, indent=1))
        print("receipt:", OUT)


if __name__ == "__main__":
    main()
