#!/usr/bin/env python3
"""r76-simplifier replay round 2: B3/A4/A5/B4 for the D9 increment.

Round 1 proved D1..D8 byte-neutral (baseline A2 == simplified B2, and
baseline A3 == simplified B1 — one byte-identity pair per observed
environment state).  Round 2 adds D9 (dead `env` parameter + internal env
merge on _capture_sever_cell) and interleaves four passes so a same-state
byte-identity pair can be observed for the extended set.
"""
import hashlib, json, shutil, subprocess, sys, time
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
SIM = REPO / "corpus" / "live" / "r76-simplifier"
MIRROR = SIM / "mirror" / "corpus"
FIXTURES = MIRROR / "fixtures"
PRISTINE = SIM / "mirror-artifacts-pristine"
RECEIPTS = SIM / "receipts"

PASSES = [
    ("B3-simplified-d1d9", FIXTURES / "measure_audio_simplified_d1d9.py"),
    ("A4-baseline", FIXTURES / "measure_audio_baseline_head.py"),
    ("A5-baseline", FIXTURES / "measure_audio_baseline_head.py"),
    ("B4-simplified-d1d9", FIXTURES / "measure_audio_simplified_d1d9.py"),
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

(SIM / "replay-log-round2.json").write_text(json.dumps(log, indent=2) + "\n")
print("DRIVER2-DONE")
