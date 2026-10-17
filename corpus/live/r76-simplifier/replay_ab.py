#!/usr/bin/env python3
"""r76-simplifier replay harness: A2 / B1 / B2 / A3 receipt compare.

A = baseline (HEAD bytes) fixture, B = deletion-set variant.  Interleaved
A,B,B,A so an environment flip is visible as A2 != A3 (or B1 != B2) in
the SAME leaf rather than being misread as a deletion effect.

Each pass: restore the pristine artifact copy (identical start state),
run `--probe-capture-r76` with cwd = repo root (the author's invocation),
copy measurements.json into corpus/live/r76-simplifier/receipts/<label>.json.
"""
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
SIM = REPO / "corpus" / "live" / "r76-simplifier"
MIRROR = SIM / "mirror" / "corpus"
FIXTURES = MIRROR / "fixtures"
PRISTINE = SIM / "mirror-artifacts-pristine"
RECEIPTS = SIM / "receipts"
RECEIPTS.mkdir(parents=True, exist_ok=True)

PASSES = [
    ("A2-baseline", FIXTURES / "measure_audio_baseline_head.py"),
    ("B1-simplified", FIXTURES / "measure_audio_simplified.py"),
    ("B2-simplified", FIXTURES / "measure_audio_simplified.py"),
    ("A3-baseline", FIXTURES / "measure_audio_baseline_head.py"),
]

log = []


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


for label, script in PASSES:
    if (MIRROR / "artifacts").exists():
        shutil.rmtree(MIRROR / "artifacts")
    shutil.copytree(PRISTINE, MIRROR / "artifacts")
    t0 = time.time()
    proc = subprocess.run(
        ["timeout", "-s", "KILL", "600", sys.executable, str(script),
         "--probe-capture-r76"],
        cwd=str(REPO), capture_output=True, text=True)
    wall = time.time() - t0
    (SIM / f"stdout-{label}.txt").write_text(proc.stdout)
    (SIM / f"stderr-{label}.txt").write_text(proc.stderr)
    out = json.loads(proc.stdout.strip().splitlines()[-1])
    src = Path(out["receipt"])
    dst = RECEIPTS / f"{label}.json"
    shutil.copy2(src, dst)
    row = {"pass": label, "script": script.name, "fixture_sha256": sha(script),
           "exit": proc.returncode, "wall_s": round(wall, 1),
           "receipt_dir": str(src.parent.relative_to(REPO)),
           "receipt_sha256": sha(dst), "failures": out["failures"]}
    log.append(row)
    print(json.dumps(row), flush=True)

(SIM / "replay-log.json").write_text(json.dumps(log, indent=2) + "\n")
print("DRIVER-DONE")
