#!/usr/bin/env python3
"""r77-baseline mechanism probe: is the intermittent roundtrip deviation a
GAIN change (whole capture louder) or a TRANSIENT excursion (a few samples)?

The A/B (residue-ab.txt) falsified prior-playback residue: the residue arm
matched the member 3/3 while the clean arm deviated once (+3.134 dB). Every
observed deviation is POSITIVE (captured louder than the member).

6 reps of the standalone capture idiom, recording per rep:
  cap_peak, src_peak, delta_db, within_3db,
  n_above_src   samples with |x| > src_peak (a gain change puts ~half the
                samples above; a transient puts a handful),
  argmax_frac   position of the peak in the capture (0..1),
  rms_db        RMS ratio in dB (gain would move this; a lone transient
                barely moves it),
  peak_first_half / peak_second_half
Own harness, no fixture import. Bounded (5 s capture, 30 s per-leg timeout).
Writes transient-shape.txt.
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
OUT = HERE / "transient-shape.txt"
REPS = 18


def sink():
    return subprocess.run(["pactl", "get-default-sink"], capture_output=True,
                          text=True).stdout.strip()


def rep(i):
    s = sink()
    with tempfile.TemporaryDirectory(prefix="r77ts-", dir=HERE) as tmp:
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
        half = len(pcm) // 2
        rms_src = float(np.sqrt(np.mean(src ** 2)))
        rms_cap = float(np.sqrt(np.mean(pcm ** 2))) if len(pcm) else 0.0
        return {
            "rep": i, "sink": s, "cap_bytes": len(data),
            "cap_peak": cap_peak, "src_peak": src_peak,
            "delta_db": round(20 * np.log10(max(cap_peak, 1) / max(src_peak, 1)), 3),
            "within_3db": bool(abs(20 * np.log10(max(cap_peak, 1) / max(src_peak, 1))) <= 3.0),
            "n_above_src": int(np.sum(np.abs(pcm) > src_peak)),
            "argmax_frac": round(float(np.argmax(np.abs(pcm))) / max(len(pcm) - 1, 1), 4),
            "rms_db": round(20 * np.log10(max(rms_cap, 1e-9) / max(rms_src, 1e-9)), 3),
            "peak_first_half": float(np.max(np.abs(pcm[:half]))) if half else 0.0,
            "peak_second_half": float(np.max(np.abs(pcm[half:]))) if half else 0.0,
            "rec_exit": rec.returncode, "play_exit": play.returncode,
        }


def main():
    lines = [f"host {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}",
             f"member {MEMBER.relative_to(HERE)} src_peak={int(np.max(np.abs(np.frombuffer(MEMBER.read_bytes()[44:], dtype='<i2'))))}"]
    for i in range(1, REPS + 1):
        lines.append(json.dumps(rep(i)))
        time.sleep(0.5)
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
