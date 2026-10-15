#!/usr/bin/env python3
"""r100b window-landing witness — why the scout's rms pin scatters at ~1e-4.

The scout's `best_window()` searches the max-energy 0.4 s window with a stride of
`win // 10` (1920 samples at 48000). The stimulus has a short fade-in, so where
the coarse search lands changes the reported rms at the 1e-4 level — while the
*underlying waveform* is identical. This script recomputes both:
  coarse = the scout's exact recipe;  fine = stride 1.
"""
import json
import os
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(HERE, "scratch")
Q = os.path.join(os.path.dirname(HERE), "r100-scout", "scratch")

CAPS = [
    ("scout", "az0_44k_r0", os.path.join(Q, "cap_sofa_44k_az0_r0.wav"), 44100),
    ("scout", "az0_44k_r1", os.path.join(Q, "cap_sofa_44k_az0_r1.wav"), 44100),
    ("scout", "az90_44k_r0", os.path.join(Q, "cap_sofa_44k_az90_r0.wav"), 44100),
    ("scout", "az180_44k_r0", os.path.join(Q, "cap_sofa_44k_az180_r0.wav"), 44100),
    ("scout", "48k_r0", os.path.join(Q, "cap_sofa_48k_r0.wav"), 48000),
    ("r100b", "az0_44k_r0", os.path.join(S, "cap_sofa_44k_az0_r0.wav"), 44100),
    ("r100b", "az0_44k_r1", os.path.join(S, "cap_sofa_44k_az0_r1.wav"), 44100),
    ("r100b", "az90_44k_r0", os.path.join(S, "cap_sofa_44k_az90_r0.wav"), 44100),
    ("r100b", "az180_44k_r0", os.path.join(S, "cap_sofa_44k_az180_r0.wav"), 44100),
    ("r100b", "48k_rep0", os.path.join(S, "cap_sofa_48k_rep0_r0.wav"), 48000),
    ("r100b", "48k_rep4", os.path.join(S, "cap_sofa_48k_rep4_r4.wav"), 48000),
    ("r100b", "48k_az90_r0", os.path.join(S, "cap_sofa_48k_az90_r0.wav"), 48000),
]


def rd(p):
    w = wave.open(p)
    raw = w.readframes(w.getnframes())
    v = np.frombuffer(raw, dtype="<i2").reshape(-1, w.getnchannels())
    return v.astype(np.float64) / 32768.0


def best(x, win, stride):
    best_e, bi = -1.0, 0
    for i in range(0, max(1, len(x) - win + 1), stride):
        e = float(np.mean(x[i:i + win] ** 2))
        if e > best_e:
            best_e, bi = e, i
    return bi, best_e ** 0.5


def main():
    rows = []
    print("%-6s %-12s %-8s %-12s %-12s %-10s" % ("seat", "cap", "win", "coarse_rms", "fine_rms", "coarse_off"))
    for seat, name, path, fc_rate in CAPS:
        if not os.path.exists(path):
            print("%-6s %-12s MISSING" % (seat, name))
            continue
        x = rd(path)[:, 0]
        win = min(int(0.4 * fc_rate), len(x))
        c_off, c_rms = best(x, win, max(1, win // 10))
        f_off, f_rms = best(x, win, 1)
        rows.append({"seat": seat, "cap": name, "file": path, "win": win,
                     "coarse_rms": round(c_rms, 8), "coarse_off": c_off,
                     "fine_rms": round(f_rms, 8), "fine_off": f_off})
        print("%-6s %-12s %-8d %-12.8f %-12.8f %-10d" % (seat, name, win, c_rms, f_rms, c_off))
    # group spread per cell
    print()
    for cell in ("az0_44k_r0", "az90_44k_r0", "az180_44k_r0"):
        vals = [r for r in rows if r["cap"].startswith(cell.split("_")[0])]
        if len(vals) < 2:
            continue
        cr = [r["coarse_rms"] for r in vals]
        fr = [r["fine_rms"] for r in vals]
        print("%-14s coarse spread %.2e   fine spread %.2e"
              % (cell, (max(cr) - min(cr)) / max(cr), (max(fr) - min(fr)) / max(fr)))
    p = os.path.join(S, "window-landing.json")
    with open(p, "w") as f:
        json.dump(rows, f, indent=1)
    print("wrote", p)


if __name__ == "__main__":
    main()
