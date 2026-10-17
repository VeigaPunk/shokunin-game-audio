#!/usr/bin/env python3
"""r77-baseline bounded intermittency probe for the capture-r76 roundtrip
content witness (the single non-canonical row in the frozen-byte replay).

Runs the frozen env fixture's --probe-capture-r76 arm REPEATS times, serially,
and after each run extracts from that run's fresh receipt:
  exit, failures, content_witness, capture_leg.exit_code,
  detect_legs.sox.{member,captured}.stderr_tail  (level proxy: sox "Volume
  adjustment"), detect_legs.aplay.captured.stderr_tail (tail-scrub window).

Also runs a direct level measurement (own harness, no fixture import): play the
member into the default sink with pw-cat while pw-record captures the sink
monitor, then compute the captured-vs-member peak delta in dB with numpy. This
quantifies the deviation the 3 dB witness bounds.

Write scope: corpus/live/r77-baseline/ only (receipts land in the env tree).
Writes roundtrip-repeat.txt.
"""
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ENVROOT = HERE / "measure-env" / "corpus"
MEASURE = str(ENVROOT / "fixtures" / "measure_audio.py")
RUNS = ENVROOT / "live" / "runs"
MEMBER = ENVROOT / "artifacts" / "stem_sections.wav"
REPEATS = 3
OUT = HERE / "roundtrip-repeat.txt"


def newest(mode):
    dirs = sorted(RUNS.glob(f"*-{mode}"))
    return dirs[-1] / "measurements.json" if dirs else None


def digest(receipt):
    p = json.loads(Path(receipt).read_text())
    rt = p["measurements"]["capture_roundtrip_r76_probe"]
    return {
        "receipt": str(receipt),
        "content_witness": rt["content_witness"],
        "capture_exit": rt["capture_leg"]["exit_code"],
        "player_exit": rt["capture_leg"]["player_exit_code"],
        "bytes": rt["capture_leg"]["file"]["bytes"],
        "sox_member_vol": rt["detect_legs"]["sox"]["member"]["stderr_tail"],
        "sox_captured_vol": rt["detect_legs"]["sox"]["captured"]["stderr_tail"],
        "aplay_captured_tail": rt["detect_legs"]["aplay"]["captured"].get("stderr_tail"),
        "failures": rt["failures"],
    }


def direct_level_rep(tag):
    """own harness: peak(captured monitor) vs peak(member) in dB."""
    sink = subprocess.run(["pactl", "get-default-sink"], capture_output=True,
                          text=True).stdout.strip()
    with tempfile.TemporaryDirectory(prefix="r77b-", dir=HERE) as tmp:
        cap = Path(tmp) / "cap.wav"
        argv = ["pw-record", "-P", "stream.capture.sink=true", "--target", sink,
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
        nz = float((np.abs(pcm) > 0).mean()) if len(pcm) else 0.0
        return {"tag": tag, "sink": sink, "cap_bytes": len(data),
                "cap_peak": cap_peak, "src_peak": src_peak,
                "delta_db": round(delta, 3), "nonzero_frac": round(nz, 4),
                "rec_exit": rec.returncode, "play_exit": play.returncode,
                "within_3db": bool(abs(delta) <= 3.0)}


def main():
    lines = [f"host {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}",
             f"member {MEMBER.relative_to(HERE)}",
             f"REPEATS={REPEATS}", ""]
    for i in range(1, REPEATS + 1):
        proc = subprocess.run(["python3", MEASURE, "--probe-capture-r76"],
                              capture_output=True, text=True)
        receipt = newest("capture-r76")
        rec = digest(receipt) if receipt else {"receipt": "MISSING"}
        lines.append(f"--- fixture rep {i}: exit={proc.returncode}")
        lines.append(json.dumps(rec, indent=1))
        lines.append("")
    for i in range(1, REPEATS + 1):
        lines.append(f"--- direct level rep {i}")
        lines.append(json.dumps(direct_level_rep(i), indent=1))
        lines.append("")
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
