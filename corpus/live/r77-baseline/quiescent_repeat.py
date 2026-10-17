#!/usr/bin/env python3
"""r77-baseline quiescence-gated repeat of the capture-r76 roundtrip row.

The first repeat window was itself contended (a sibling seat moved the default
sink to the Speaker sink at 19:51:08Z and ran up to 11 audio processes), so the
content-witness deviation could not be attributed. This harness waits for a
quiet host — 3 consecutive samples with zero competing audio processes — then
runs the frozen env fixture's --probe-capture-r76 arm 3 times, recording the
contention state (competing procs, default sink) immediately before and after
each rep, plus the same receipt leaves as roundtrip_repeat.py.

Bounded: QUIET_BUDGET_S wait cap, REPS fixture runs. Writes
quiescent-repeat.txt.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENVROOT = HERE / "measure-env" / "corpus"
MEASURE = str(ENVROOT / "fixtures" / "measure_audio.py")
RUNS = ENVROOT / "live" / "runs"
OUT = HERE / "quiescent-repeat.txt"
PAT = "measure_audio|pw-cat|pw-record|parec|parecord|arecord|aplay|ffmpeg|sox|mpv"
REPS = 3
QUIET_BUDGET_S = 480
NEED_QUIET_SAMPLES = 3


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True,
                          text=True).stdout.strip()


def state():
    procs = [l for l in sh(f"ps -eo pid=,args= | grep -E '{PAT}' | grep -v grep").splitlines()]
    sink = sh("pactl get-default-sink 2>/dev/null") or "-"
    return len(procs), sink


def newest():
    dirs = sorted(RUNS.glob("*-capture-r76"))
    return dirs[-1] / "measurements.json" if dirs else None


def digest(receipt):
    p = json.loads(Path(receipt).read_text())
    rt = p["measurements"]["capture_roundtrip_r76_probe"]
    return {"content_witness": rt["content_witness"],
            "sox_member_vol": rt["detect_legs"]["sox"]["member"]["stderr_tail"],
            "sox_captured_vol": rt["detect_legs"]["sox"]["captured"]["stderr_tail"],
            "aplay_captured_tail": rt["detect_legs"]["aplay"]["captured"].get("stderr_tail"),
            "capture_exit": rt["capture_leg"]["exit_code"],
            "failures": rt["failures"]}


def main():
    t0 = time.time()
    lines = [f"quiescence-gated repeat start {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}",
             f"budget={QUIET_BUDGET_S}s need={NEED_QUIET_SAMPLES} consecutive quiet samples"]
    quiet = 0
    while time.time() - t0 < QUIET_BUDGET_S and quiet < NEED_QUIET_SAMPLES:
        n, sink = state()
        lines.append(f"wait {time.strftime('%H:%M:%SZ', time.gmtime())} n_audio={n} sink={sink}")
        quiet = quiet + 1 if n == 0 else 0
        if quiet < NEED_QUIET_SAMPLES:
            time.sleep(15)
    lines.append(f"quiet_satisfied={quiet >= NEED_QUIET_SAMPLES}")
    for i in range(1, REPS + 1):
        n0, sink0 = state()
        proc = subprocess.run(["python3", MEASURE, "--probe-capture-r76"],
                              capture_output=True, text=True)
        n1, sink1 = state()
        rec = newest()
        lines.append(f"--- rep {i}: exit={proc.returncode} "
                     f"pre(n={n0},sink={sink0}) post(n={n1},sink={sink1}) "
                     f"utc={time.strftime('%H:%M:%SZ', time.gmtime())}")
        lines.append(json.dumps(digest(rec) if rec else {"receipt": "MISSING"},
                                indent=1))
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
