#!/usr/bin/env python3
"""r82-verify2 spot s1 — independent re-derivation of the pid-class tone
pair. Re-implements _ffpw_r82_tone_pair + _ffpw_r82_write_tone from the
frozen source (verbatim arithmetic), writes wavs for the two observed
run pids, FFT-verifies both channel peaks land on the formula pair, and
re-checks the ±6% disjointness table vs every r78 class and sibling r82
class. Writes only into /tmp/r82w-spot/."""
import sys, wave
from pathlib import Path
import numpy as np

OUT = Path("/tmp/r82w-spot")
OUT.mkdir(exist_ok=True)
TOL = 0.06          # PLAYBACK_R78_TONE_TOL
AMP_MIN = 400       # r78 amp floor (PLAYBACK_R78_TONE_AMP_MIN)

def tone_pair(pid):
    l = 2900.0 + (pid % 4) * 400.0
    return l, l + 560.0

def write_tone(path, seconds, pid):
    l_hz, r_hz = tone_pair(pid)
    n = int(48000 * seconds)
    t = np.arange(n) / 48000
    rng = np.random.default_rng(0x82FF ^ (pid & 0xFFFF))
    dith = rng.integers(-30, 31, n)
    left = np.clip(8192 * np.sin(2 * np.pi * l_hz * t) + dith,
                   -32768, 32767).astype("<i2")
    right = np.clip(8192 * np.sin(2 * np.pi * r_hz * t) + dith,
                    -32768, 32767).astype("<i2")
    pcm = np.empty(n * 2, dtype="<i2")
    pcm[0::2], pcm[1::2] = left, right
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(48000)
        w.writeframes(pcm.tobytes())

def domfreq(seg, rate=48000):
    win = len(seg)
    sp = np.abs(np.fft.rfft(seg.astype(np.float64) *
                            np.hanning(win)))
    ax = np.fft.rfftfreq(win, 1.0 / rate)
    i = int(np.argmax(sp))
    return ax[i], sp[i]

res = {}
for pid in (417268, 454408, 511699):
    p = OUT / f"tone_{pid}.wav"
    write_tone(p, 3.6, pid)
    with wave.open(str(p)) as w:
        pcm = np.frombuffer(w.readframes(w.getnframes()),
                            dtype="<i2").reshape(-1, 2)
    fl, al = domfreq(pcm[:, 0]); fr, ar = domfreq(pcm[:, 1])
    L, R = tone_pair(pid)
    res[str(pid)] = {"class": pid % 4, "expect": [L, R],
                     "meas": [round(float(fl), 1), round(float(fr), 1)],
                     "amps": [round(float(al)), round(float(ar))],
                     "within_tol": bool(abs(fl - L) <= L * TOL and
                                        abs(fr - R) <= R * TOL and
                                        al >= AMP_MIN and ar >= AMP_MIN)}

# full disjointness table: every r82 class vs every r78 class (both
# directions) and every sibling r82 class
table = {}
for j in range(4):
    L, R = tone_pair(j)
    worst = None
    for k in range(4):
        l78, r78 = 997.0 + k * 211.0, 997.0 + k * 211.0 + 503.0
        # forward: r78 pair inside OUR +-6% windows?
        fwd = abs(l78 - L) <= L * TOL and abs(r78 - R) <= R * TOL
        rev = abs(L - l78) <= l78 * TOL and abs(R - r78) <= r78 * TOL
        dl = min(abs(l78 - L), abs(r78 - R))
        if worst is None or dl < worst[0]:
            worst = (dl, f"r78class{k}", fwd or rev)
    for k in range(4):
        if k == j:
            continue
        lo, ro = tone_pair(k)
        sib = abs(lo - L) <= L * TOL and abs(ro - R) <= R * TOL
        dl = min(abs(lo - L), abs(ro - R))
        if worst is None or dl < worst[0]:
            worst = (dl, f"r82class{k}", sib)
    table[f"class{j}"] = {"pair": [L, R], "min_hz_gap": worst[0],
                          "nearest": worst[1],
                          "any_collision": bool(worst[2])}
res["disjoint_table"] = table
res["all_within_tol"] = all(v["within_tol"] for k, v in res.items()
                            if k != "disjoint_table")
res["any_collision"] = any(v["any_collision"]
                           for v in table.values())
print(__import__("json").dumps(res, indent=2))
