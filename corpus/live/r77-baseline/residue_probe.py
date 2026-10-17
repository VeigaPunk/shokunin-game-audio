#!/usr/bin/env python3
"""r77-baseline A/B for the roundtrip content-witness deviation mechanism.

The frozen-byte replay produced ONE non-canonical row: capture-r76's roundtrip
content witness measured the captured sink-monitor peak 3.802 dB above the
member's own peak (bound = 3.0 dB), and 2/3 bounded fixture reps deviated
(1.366 / 4.312 / 0.0 dB) while 3/3 reps of an equivalent standalone capture
idiom matched the member exactly (0.000 dB). The fixture runs the roundtrip
AFTER five other capture arms in the same process; those arms play material
into the default sink.

This A/B isolates that candidate mechanism: prior playback still resident in
the monitored sink mix.
  A (clean)   : capture idiom alone -> delta dB
  B (residue) : two full member plays into the default sink, then the capture
                idiom immediately -> delta dB
Alternating reps; own harness, no fixture import. Bounded (5 s capture, 30 s
per-leg timeout). Writes residue-ab.txt.
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
OUT = HERE / "residue-ab.txt"
REPS = 3


def sink():
    return subprocess.run(["pactl", "get-default-sink"], capture_output=True,
                          text=True).stdout.strip()


def capture_idiom(tag):
    s = sink()
    with tempfile.TemporaryDirectory(prefix="r77ab-", dir=HERE) as tmp:
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
        return {"arm": tag, "sink": s, "cap_peak": cap_peak, "src_peak": src_peak,
                "delta_db": round(delta, 3), "within_3db": bool(abs(delta) <= 3.0),
                "cap_bytes": len(data), "rec_exit": rec.returncode,
                "play_exit": play.returncode}


def residue_plays():
    out = []
    for _ in range(2):
        p = subprocess.run(["pw-cat", "-p", str(MEMBER)],
                           capture_output=True, timeout=30)
        out.append(p.returncode)
    return out


def main():
    lines = [f"host {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}",
             f"member {MEMBER.relative_to(HERE)}"]
    for i in range(1, REPS + 1):
        time.sleep(1.0)
        lines.append(json.dumps(capture_idiom(f"A-clean-{i}"), indent=1))
        r = residue_plays()
        lines.append(f"residue plays rc={r}")
        lines.append(json.dumps(capture_idiom(f"B-residue-{i}"), indent=1))
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
