#!/usr/bin/env python3
"""r82 reviewer probe: does the r78/r79 pid-offset tag pair collide with the
r82 tag classifier bands? Runs the FIXTURE'S OWN classifiers (imported, not
re-implemented) on synthetic tones. Read-only: writes only under
corpus/live/r82-reviewer/."""
import importlib.util
import json
import os
import sys
import wave
from pathlib import Path

import numpy as np

FIX = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/fixtures/measure_audio.py")
spec = importlib.util.spec_from_file_location("measure_audio", FIX)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

OUT = Path(__file__).with_name("probe_tone_bands.out")
OUT.mkdir(exist_ok=True)


def write_pair(path, l_hz, r_hz, seconds=2.0, amp=8192):
    n = int(48000 * seconds)
    t = np.arange(n) / 48000
    rng = np.random.default_rng(0x82FF ^ (os.getpid() & 0xFFFF))
    dith = rng.integers(-30, 31, n)
    left = np.clip(amp * np.sin(2 * np.pi * l_hz * t) + dith,
                   -32768, 32767).astype("<i2")
    right = np.clip(amp * np.sin(2 * np.pi * r_hz * t) + dith,
                    -32768, 32767).astype("<i2")
    pcm = np.empty(n * 2, dtype="<i2")
    pcm[0::2], pcm[1::2] = left, right
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(pcm.tobytes())


res = {
    "fixture": str(FIX),
    "r82_pair": [m.FFPW_R82_TONE_L_HZ, m.FFPW_R82_TONE_R_HZ],
    "r82_tol": m.PLAYBACK_R78_TONE_TOL,
    "r82_amp_floor": m.PLAYBACK_R78_TONE_AMP_MIN,
    "r78_pid_mod4": os.getpid() % 4,
    "r78_pair_this_proc": [m.PLAYBACK_R78_TONE_L_HZ, m.PLAYBACK_R78_TONE_R_HZ],
    "cases": {},
}

# case 1: r78 pid%4==1 pair (1208/1711) through the r82 classifier
p1 = OUT / "r78pid1_pair.wav"
write_pair(p1, 1208.0, 1711.0)
res["cases"]["r78pid1_tone_through_r82_classifier"] = {
    k: m._ffpw_r82_tone_windows(p1).get(k)
    for k in ("mine_windows", "carries_tone", "peak_l", "peak_r")}

# case 2: r78 pid%4==0 pair (997/1500) through the r82 classifier (control)
p2 = OUT / "r78pid0_pair.wav"
write_pair(p2, 997.0, 1500.0)
res["cases"]["r78pid0_tone_through_r82_classifier"] = {
    k: m._ffpw_r82_tone_windows(p2).get(k)
    for k in ("mine_windows", "carries_tone", "peak_l", "peak_r")}

# case 3: r82 pair (1210/1780) through the r82 classifier (self control)
p3 = OUT / "r82_pair.wav"
write_pair(p3, 1210.0, 1780.0)
res["cases"]["r82_tone_through_r82_classifier"] = {
    k: m._ffpw_r82_tone_windows(p3).get(k)
    for k in ("mine_windows", "carries_tone", "peak_l", "peak_r")}

# case 4: reverse — r82 pair through the r78 classifier pinned at pid%4==1
m.PLAYBACK_R78_TONE_L_HZ = 1208.0
m.PLAYBACK_R78_TONE_R_HZ = 1711.0
res["cases"]["r82_tone_through_r78_classifier_pid1"] = {
    k: m._playback_r78_tone_windows(p3).get(k)
    for k in ("mine_windows", "carries_tone", "peak_l", "peak_r")}

# case 5: r78 pid%4==0 pair through the r78 classifier pinned at pid%4==1
#         (must NOT match: the pid-offset design works within the family)
res["cases"]["r78pid0_tone_through_r78_classifier_pid1"] = {
    k: m._playback_r78_tone_windows(p2).get(k)
    for k in ("mine_windows", "carries_tone", "peak_l", "peak_r")}

res["verdict"] = {
    "r82_classifier_reads_r78pid1_as_mine":
        res["cases"]["r78pid1_tone_through_r82_classifier"]["carries_tone"],
    "r78_classifier_pid1_reads_r82_as_mine":
        res["cases"]["r82_tone_through_r78_classifier_pid1"]["carries_tone"],
}
(OUT / "probe_tone_bands.json").write_text(json.dumps(res, indent=2) + "\n")
print(json.dumps(res, indent=2))
