#!/usr/bin/env python3
"""r75 simplifier: (a) shadowing proof for _paplay_fields pattern 3,
(b) inert-branch proof + re-anchor preview for _PACAT_RACY_TAIL.

Loads the landed fixture with -B (no bytecode writes; never mutates the
shared tree) and evaluates the two functions against every captured pacat
surface on disk (scribe raw/ captures) plus the receipt tails.

Usage: python3 -B shadow_proof.py
"""
import importlib.util
import json
import re
from pathlib import Path

R = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
S = R / "corpus/live/r75-simplifier"
RAW = R / "corpus/live/r75-scribe/raw"

spec = importlib.util.spec_from_file_location("ma", R / "corpus/fixtures/measure_audio.py")
ma = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ma)

CAPTURES = [
    "rv-pp-xdg.stderr",
    "rv-pp-pulseserver.stderr",
    "pp2.err",
    "pp3.err",
    "np-paplay_v_invalid.stderr",
    "rv-paplay-noise.stderr",
    "np-paplay_v_valid.stderr",
]

out = []
out.append("# (a) _paplay_fields with/without the pa_context_connect fallback")
PAT_FULL = (r"open\(\): [^\n]+", r"Connection failure: [^\n]+",
            r"pa_context_connect\(\) failed: [^\n]+", r"Failed to open audio file\.?")
PAT_T1 = (r"open\(\): [^\n]+", r"Connection failure: [^\n]+",
          r"Failed to open audio file\.?")


def fields_with(text, pats):
    spec_ = re.search(r"Using sample spec '([^']+)'", text)
    err = None
    for pat in pats:
        m = re.search(pat, text)
        if m:
            err = m.group(0).strip()
            break
    return (spec_.group(1) if spec_ else None), err


same_all = True
for name in CAPTURES:
    text = (RAW / name).read_text(errors="replace")
    full = fields_with(text, PAT_FULL)
    t1 = fields_with(text, PAT_T1)
    # which pattern index wins under the full list
    idx = None
    for i, pat in enumerate(PAT_FULL):
        if re.search(pat, text):
            idx = i
            break
    out.append(f"{name}: bytes={len(text)} winner_idx={idx} full={full!r} "
               f"t1={t1!r} identical={full == t1}")
    same_all &= (full == t1)
out.append(f"ALL IDENTICAL: {same_all}")

out.append("")
out.append("# (b) _PACAT_RACY_TAIL alternatives vs captured lines")
ALT = {
    "Time:.*Latency:": re.compile(r"^Time:.*Latency:$"),
    "Time:.*Latency:.*": re.compile(r"^Time:.*Latency:.*$"),
    "Playback stream drained.": re.compile(r"^Playback stream drained\.$"),
    "Draining connection to server.": re.compile(r"^Draining connection to server\.$"),
    "Connected to device.*": re.compile(r"^Connected to device.*$"),
    "Stream started..*": re.compile(r"^Stream started\..*$"),
}
valid = (RAW / "np-paplay_v_valid.stderr").read_text(errors="replace")
for i, ln in enumerate(valid.splitlines()):
    hits = [k for k, p in ALT.items() if p.match(ln)]
    out.append(f"  line{i:2}: {ln!r} -> matches {hits}")

out.append("")
out.append("# (c) tail preview on the captured valid surface")
landed_pat = re.compile(
    r"^(Time:.*Latency:|Playback stream drained\.|"
    r"Draining connection to server\.|Connected to device.*|"
    r"Stream started\..*)$")
fixed_pat = re.compile(
    r"^(Time:.*Latency:.*|Playback stream drained\.|"
    r"Draining connection to server\.|Connected to device.*|"
    r"Stream started\..*)$")
for label, pat in (("landed", landed_pat), ("re-anchored", fixed_pat)):
    ftext = "\n".join(ln for ln in valid.splitlines() if not pat.match(ln))
    tail = ma._consumer2_tail(ftext, "np-paplay_v_valid.stderr")
    out.append(f"  {label:10} tail={tail!r}")

out.append("")
out.append("# (d) receipt paplay tails (committed landed receipt)")
rec = json.load(open(R / "corpus/live/runs/20261014T165017429491Z-consumers2-r75/measurements.json"))
tails = set()
for k, v in rec["measurements"].items():
    if k.startswith("consumer2_") and "consumers" in v:
        for t, arm in v["consumers"]["paplay"]["transport_axis"].items():
            tails.add((k, t, arm.get("stderr_tail")))
for row in sorted(tails):
    out.append(f"  {row}")

(S / "shadow-proof.txt").write_text("\n".join(out) + "\n")
print("\n".join(out))
