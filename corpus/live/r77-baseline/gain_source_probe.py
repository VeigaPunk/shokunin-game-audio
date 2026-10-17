#!/usr/bin/env python3
"""r77-baseline gain-source probe for the roundtrip content witness.

transient-shape.txt (18 reps, 5 over the 3 dB bound) falsified the lone-
transient hypothesis: a failing capture has 9,396-39,464 samples above the
member's peak and RMS up 0.05-2.56 dB — the whole monitored tone is hotter,
up to +4.46 dB. That is a GAIN change on the monitor path.

This probe tests the one candidate gain source reachable from this seat: the
default sink's volume/mute state (PipeWire monitors a sink post-volume).
Each rep records the sink volume + mute before and after, plus the capture
delta. Bounded (5 s capture, 30 s per-leg timeout, REPS reps).
Writes gain-source.txt.
"""
import json
import subprocess
import tempfile
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ENVROOT = HERE / "measure-env" / "corpus"
MEMBER = ENVROOT / "artifacts" / "stem_sections.wav"
OUT = HERE / "gain-source.txt"
REPS = 12


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True,
                          text=True).stdout.strip()


def sink():
    return sh("pactl get-default-sink")


def vol(s):
    v = sh(f"pactl get-sink-volume '{s}' 2>/dev/null")
    m = sh(f"pactl get-sink-mute '{s}' 2>/dev/null")
    return {"volume": " ".join(v.split()), "mute": m}


def rep(i):
    s = sink()
    v0 = vol(s)
    with tempfile.TemporaryDirectory(prefix="r77gs-", dir=HERE) as tmp:
        cap = Path(tmp) / "cap.wav"
        argv = ["pw-record", "-P", "stream.capture.sink=true", "--target", s,
                "-n", "240000", "--rate", "48000", "--channels", "2",
                "--format", "s16", str(cap)]
        rec = subprocess.Popen(argv, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, start_new_session=True)
        time.sleep(0.7)
        play = subprocess.run(["pw-cat", "-p", str(MEMBER)],
                              capture_output=True, timeout=30)
        try:
            rec.wait(timeout=30)
        except subprocess.TimeoutExpired:
            rec.kill()
            rec.wait()
        data = cap.read_bytes() if cap.exists() else b""
        pcm = np.frombuffer(data[44:], dtype="<i2").astype(np.float64)
        src = np.frombuffer(MEMBER.read_bytes()[44:], dtype="<i2").astype(np.float64)
        cap_peak = float(np.max(np.abs(pcm))) if len(pcm) else 0.0
        src_peak = float(np.max(np.abs(src)))
        delta = 20 * np.log10(max(cap_peak, 1) / max(src_peak, 1))
        v1 = vol(s)
        return {"rep": i, "sink": s, "volume_before": v0["volume"],
                "volume_after": v1["volume"], "mute_before": v0["mute"],
                "mute_after": v1["mute"], "cap_peak": cap_peak,
                "delta_db": round(delta, 3),
                "within_3db": bool(abs(delta) <= 3.0), "rec_exit": rec.returncode}


def main():
    lines = [f"host {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}"]
    for i in range(1, REPS + 1):
        lines.append(json.dumps(rep(i)))
        time.sleep(0.4)
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
