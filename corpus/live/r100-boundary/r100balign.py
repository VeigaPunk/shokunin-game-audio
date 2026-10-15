#!/usr/bin/env python3
"""r100b alignment witness — is the sofa output the same *signal* across seats?

The r100 scout pinned its numbers at "analysis level" and disclosed that the WAV
bytes are not identical. This script asks the stronger question: after an integer
lag, is the captured waveform the same signal?

Two questions, two receipts:
  * global  — max |Δ| and exact fraction over the overlap
  * blocks  — every mismatching sample is localized into contiguous blocks, and the
              *residual* outside those blocks is reported (this is what a "bit
              identical modulo 1 LSB" claim must be receipted by).

Alignment is a direct search (the captures carry different amounts of leading
silence, so a global FFT correlation peak lands on the silence).

Usage: r100balign.py
"""
import json
import os
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.join(HERE, "scratch")
SCOUT_SCRATCH = os.path.join(os.path.dirname(HERE), "r100-scout", "scratch")

PAIRS = [
    ("quiet az0 r0", "cap_sofa_44k_az0_r0.wav", "cap_sofa_44k_az0_r0.wav"),
    ("quiet az0 r1", "cap_sofa_44k_az0_r1.wav", "cap_sofa_44k_az0_r1.wav"),
    ("quiet az90 r1", "cap_sofa_44k_az90_r1.wav", "cap_sofa_44k_az90_r1.wav"),
    ("quiet az270 r0", "cap_sofa_44k_az270_r0.wav", "cap_sofa_44k_az270_r0.wav"),
    ("quiet 48k az90 r0", "cap_sofa_48k_az90_r0.wav", "cap_sofa_48k_az90_r0.wav"),
]


def rd(p):
    w = wave.open(p)
    raw = w.readframes(w.getnframes())
    v = np.frombuffer(raw, dtype="<i2").reshape(-1, w.getnchannels())
    return v.astype(np.float64) / 32768.0, w.getframerate()


def align(a, b, thresh=1e-3):
    """Direct alignment + mismatch localization for one channel pair."""
    na = int(np.argmax(np.abs(a) > 1e-6))
    nb = int(np.argmax(np.abs(b) > 1e-6))
    win = min(8192, len(a) - na - 1, len(b) - nb - 1)
    if win < 1024:
        return {"error": "no signal", "first_nonzero": [na, nb]}
    seg = a[na:na + win]
    best = None
    for lag in range(nb, len(b) - win):
        d = np.abs(b[lag:lag + win] - seg).max()
        if best is None or d < best[1]:
            best = (lag, float(d))
    shift = best[0] - na                      # b[j] corresponds to a[j - shift]
    if shift >= 0:
        n = min(len(a), len(b) - shift)
        x, y = a[:n], b[shift:shift + n]
    else:
        n = min(len(a) + shift, len(b))
        x, y = a[-shift:-shift + n], b[:n]
    d = np.abs(x - y)
    # contiguous blocks of mismatching samples (any sample above 1 LSB)
    lsb = 1.0 / 32768.0
    bad = np.where(d > lsb + 1e-12)[0]
    blocks = []
    if len(bad):
        splits = np.split(bad, np.where(np.diff(bad) > 64)[0] + 1)
        for s in splits:
            blocks.append({"start": int(s[0]), "len": int(len(s)),
                           "max_abs_diff": float(d[s].max())})
    mask = np.ones(len(d), dtype=bool)
    if len(bad):
        for s in np.split(bad, np.where(np.diff(bad) > 64)[0] + 1):
            lo, hi = max(0, int(s[0]) - 1), min(len(d), int(s[-1]) + 2)
            mask[lo:hi] = False
    resid = d[mask]
    return {"lag": int(shift), "overlap": int(n), "first_nonzero": [na, nb],
            "max_abs_diff": float(d.max()),
            "rms_diff": float(np.sqrt(np.mean((x - y) ** 2))),
            "exact_frac": float(np.mean(x == y)),
            "lsb_frac": float(np.mean(d <= lsb + 1e-12)),
            "gt1lsb_samples": int(len(bad)),
            "gt1lsb_frac": float(len(bad) / len(d)),
            "mismatch_blocks": blocks,
            "residual_outside_blocks": {
                "samples": int(len(resid)),
                "max_abs_diff": float(resid.max()) if len(resid) else 0.0,
                "exact_frac": float(np.mean(resid == 0)) if len(resid) else 1.0},
            "tone_span_in_b": [nb, int(np.where(np.abs(b) > 1e-6)[0][-1])]}


def main():
    out = {}
    print("%-18s %-6s %-8s %-11s %-9s %-9s %s" % (
        "pair", "ch", "lag", "maxdiff", "exact", ">1LSB", "blocks(start:len:max)"))
    for label, mine, scout in PAIRS:
        p1 = os.path.join(SCRATCH, mine)
        p2 = os.path.join(SCOUT_SCRATCH, scout)
        if not (os.path.exists(p1) and os.path.exists(p2)):
            out[label] = {"skipped": "missing", "mine": p1, "scout": p2}
            print("%-18s SKIP (missing)" % label)
            continue
        a, ra = rd(p1)
        b, rb = rd(p2)
        res = {"mine": p1, "scout": p2, "mine_frames": int(len(a)),
               "scout_frames": int(len(b)), "mine_rate": ra, "scout_rate": rb}
        for ch in (0, 1):
            res["ch%d" % ch] = align(a[:, ch], b[:, ch])
            c = res["ch%d" % ch]
            blocks = ",".join("%d:%d:%.2e" % (bl["start"], bl["len"], bl["max_abs_diff"])
                              for bl in c.get("mismatch_blocks", []))
            print("%-18s %-6d %-8s %-11.3e %-9.4f %-9d %s" % (
                label, ch, c.get("lag"), c.get("max_abs_diff", 0), c.get("exact_frac", 0),
                c.get("gt1lsb_samples", 0), blocks or "-"))
        out[label] = res
    p = os.path.join(SCRATCH, "align.json")
    with open(p, "w") as f:
        json.dump(out, f, indent=1)
    print("wrote", p)


if __name__ == "__main__":
    main()
