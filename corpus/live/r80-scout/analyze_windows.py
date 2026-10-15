#!/usr/bin/env python3
"""Window-resolved content witness for the P6 lifecycle legs.

For every recorder wav: split at the action boundary (1.5 s) into a PRE window
[0.0,1.5) and a POST window [1.65, end), then report peak + the exact
Goertzel/FFT amplitude at the two tone bins (L 1000 Hz, R 1500 Hz) plus the
cross terms.  A tone arriving on the default sink after the action must show a
large same-channel bin and a near-zero cross term.
"""
import glob
import json
import os
import sys
import wave
from array import array

try:
    import numpy as np
except Exception:
    np = None

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "tmp")


def windows(path, t_act=1.5, gap=0.15):
    with wave.open(path, "rb") as w:
        n, ch = w.getnframes(), w.getnchannels()
        raw = w.readframes(n)
    a = array("h")
    a.frombytes(raw[: len(raw) - (len(raw) % 2)])
    if np is not None:
        x = np.frombuffer(a, dtype="<i2").astype(np.float64)
    split = int(t_act * SR) * ch
    skip = int(gap * SR) * ch
    return (x[:split], x[split + skip:], ch)


def amps(x, ch):
    if np is None or len(x) < ch * 1000:
        return {}
    L = x[0::ch]
    R = x[1::ch] if ch > 1 else L
    N = len(L)
    win = np.hanning(N)
    out = {}
    for name, sig in (("L", L), ("R", R)):
        sp = np.abs(np.fft.rfft(sig * win)) * 2 / (win.sum())
        for f in (1000, 1500):
            k = int(round(f * N / SR))
            out[f"{name}@{f}"] = round(float(sp[k]), 1)
    out["n"] = N
    return out


def main():
    rows = []
    for path in sorted(glob.glob(os.path.join(OUT, "*-mon.wav"))):
        base = os.path.basename(path)
        try:
            pre, post, ch = windows(path)
        except Exception as e:
            rows.append({"file": base, "error": str(e)})
            continue
        pk = lambda v: int(np.max(np.abs(v))) if np is not None and len(v) else 0
        rows.append({"file": base, "ch": ch,
                     "pre_peak": pk(pre), "post_peak": pk(post),
                     "pre_frames": len(pre) // ch, "post_frames": len(post) // ch,
                     "post_amps": amps(post, ch)})
    print(json.dumps(rows, indent=1))
    with open(os.path.join(HERE, "p6-window-analysis.json"), "w") as f:
        json.dump(rows, f, indent=1)


if __name__ == "__main__":
    main()
