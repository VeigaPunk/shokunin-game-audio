#!/usr/bin/env python3
"""r75 simplifier: generate treatment copies of the landed fixture.

Each treatment is an exact single-occurrence replacement (asserted), written
as a full file into this scratch dir. Nothing here writes to the shared tree.

Usage: python3 make_treatments.py
"""
from pathlib import Path

R = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
S = R / "corpus/live/r75-simplifier"
SRC = R / "corpus/fixtures/measure_audio.py"

TREATMENTS = [
    # T1: drop the pa_context_connect fallback pattern (shadowed by
    # "Connection failure:" on every captured pacat surface).
    ("t1-paplay-shadowed-pattern.py",
     '''    for pat in (r"open\\(\\): [^\\n]+", r"Connection failure: [^\\n]+",
                r"pa_context_connect\\(\\) failed: [^\\n]+",
                r"Failed to open audio file\\.?"):''',
     '''    for pat in (r"open\\(\\): [^\\n]+", r"Connection failure: [^\\n]+",
                r"Failed to open audio file\\.?"):'''),
    # T2: ffplay ops driver leg reuses _ffplay_fields for the detect field
    # instead of a second inline copy of the regex.
    ("t2-ops-detect-fold.py",
     '''            detected = re.search(r"Input #0, ([^,\\s]+), from", text)
            sdl_err = re.search(r"(SDL[^:\\n]*:[^\\n]*|could not (?:open|"
                                r"initialize)[^\\n]*)", text)
            driver_legs[drv] = {
                "exit_code": proc.returncode,
                "ffplay_detected": detected.group(1) if detected else None,''',
     '''            detected = _ffplay_fields(text)["ffplay_detected"]
            sdl_err = re.search(r"(SDL[^:\\n]*:[^\\n]*|could not (?:open|"
                                r"initialize)[^\\n]*)", text)
            driver_legs[drv] = {
                "exit_code": proc.returncode,
                "ffplay_detected": detected,'''),
    # T3: ffplay ops empty-writer cell reuses _ffplay_fields for ffplay_invalid
    # instead of re-spelling the literal.
    ("t3-ops-invalid-fold.py",
     '''                "ffplay_invalid": ("Invalid data found when processing "
                                   "input" in text),''',
     '''                "ffplay_invalid": _ffplay_fields(text)["ffplay_invalid"],'''),
    # T4: drop the inert `Time:.*Latency:` alternation (cannot match the real
    # pacat line; anchored to require the line to end at "Latency:").
    ("t4-inert-time-branch.py",
     '''    r"^(Time:.*Latency:|Playback stream drained\\.|"''',
     '''    r"^(Playback stream drained\\.|"'''),
]


def main():
    src = SRC.read_text()
    for name, old, new in TREATMENTS:
        assert src.count(old) == 1, f"{name}: anchor count {src.count(old)}"
        (S / name).write_text(src.replace(old, new))
        print(f"wrote {name} ({len(src.replace(old, new))} B)")


if __name__ == "__main__":
    main()
