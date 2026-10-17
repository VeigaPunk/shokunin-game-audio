#!/usr/bin/env python3
"""Line-reference corrections for reports/round-76/r76-simplifier.md.

Applies and PERSISTS each fix as it goes (so a later anchor miss cannot
discard earlier work), and reports every count before asserting.
"""
import re
from pathlib import Path

p = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/reports/round-76/r76-simplifier.md")
t = p.read_text()

print("context repr for 3727:")
for m in re.finditer(r"3727", t):
    print("   ", repr(t[m.start() - 20:m.start() + 25]))

FIX = [
    ("`_capture_file_leg` 3320–3332, `_capture_sever_cell` 3331–3333",
     "`_capture_file_leg` 3249–3269, `_capture_sever_cell` 3323–3334", 1),
    ("(3664–3685)", "(3671–3690)", 1),
    ('(`_capture_tail(err, "-")`, 3547–3549)', '(`_capture_tail(err, "-")`, 3553)', 1),
    ("(3085–3088)", "(3084–3089)", 1),
    ("(`_capture_run`, 3009–3013)", "(`_capture_run`, 3014–3016)", 1),
    ("(3959)", "(3935)", 1),
    ("(3991)", "(3990–3991)", 1),
    ("2099–2101", "2099–2100", 1),
    ("2967–2969", "2967–2968", 1),
    ("3382/3393/3414", "3382/3391/3412", 1),
    ("3194–3199", "3194–3201", 1),
    ("(3021 —", "(3058 —", 1),
    ("3727–3741", "3730–3741", None),
    ("1013–1025", "1013–1024", 1),
    ("(3076–3079, asserted at 3606)",
     "(3076–3078, recorded at 3331–3332 and asserted at 3606)", 1),
    ("including the two the gate does not currently exercise.",
     "including the four the *gate* legs never exercise (`alsa_channels`, "
     "`alsa_busy`, `ffmpeg_muxer`, `aborted_by_signal`), which the "
     "device-axis, contention, name-axis and sever legs exercise "
     "respectively.", 1),
]

for old, new, exp in FIX:
    n = t.count(old)
    print(f"count={n} exp={exp} :: {old[:58]!r}")
    if exp is not None:
        assert n == exp, f"anchor count {n} != {exp}: {old[:60]!r}"
    if n:
        t = t.replace(old, new)
        p.write_text(t)

print("final bytes:", len(t))
