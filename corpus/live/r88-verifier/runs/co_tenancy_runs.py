#!/usr/bin/env python3
"""r88-verifier co-tenancy probe: N rounds of 3 CONCURRENT fixture
probe runs from 3 distinct tree materializations (the r86-F1/r87-F2
cross-materialization shape, executed).

Each run writes its own receipt inside its own tree; the script reports
per-round rc + failures so the landing's false-FAIL rate under 3-seat
co-tenancy is measured, not asserted.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SEAT = Path(sys.argv[1]).resolve()
ROUNDS = int(sys.argv[2]) if len(sys.argv) > 2 else 3
FROZEN = SEAT / "tree"
SCRATCH = SEAT / "runs" / "cotree"
SRC = FROZEN / "corpus" / "fixtures"

trees = []
for i in (1, 2):
    t = SCRATCH / f"tree{i}"
    (t / "corpus" / "fixtures").mkdir(parents=True, exist_ok=True)
    (t / "corpus" / "live").mkdir(parents=True, exist_ok=True)
    (t / "corpus" / "artifacts").mkdir(parents=True, exist_ok=True)
    for f in SRC.iterdir():
        if f.is_file():
            shutil.copy2(f, t / "corpus" / "fixtures" / f.name)
    trees.append(t)
trees.append(FROZEN)

env = dict(os.environ, TMPDIR="/home/vgpnk/Projects/shokunin/tmp")
rounds = []
for r in range(1, ROUNDS + 1):
    procs = []
    for i, t in enumerate(trees, 1):
        procs.append((i, t, subprocess.Popen(
            ["python3", "corpus/fixtures/measure_audio.py",
             "--probe-btwit-r88"],
            cwd=str(t), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=env, start_new_session=True)))
    row = []
    for i, t, p in procs:
        try:
            out, err = p.communicate(timeout=600)
            rc = p.returncode
        except subprocess.TimeoutExpired:
            rc, out, err = None, b"", b"timeout"
        try:
            payload = json.loads(out.decode())
            fails = payload.get("failures") or {}
            receipt = payload.get("receipt")
        except Exception:
            fails, receipt = {"<unparsed>": out.decode()[:200]}, None
        row.append({"slot": i, "tree": str(t), "rc": rc,
                    "failures": {k: v for k, v in fails.items() if v},
                    "receipt": receipt})
    rounds.append({"round": r, "runs": row})
    print(f"round {r}: " + "; ".join(
        f"slot{r_['slot']} rc={r_['rc']} fails={len(r_['failures'])}"
        for r_ in row), flush=True)
reds = sum(1 for rd in rounds for x in rd["runs"] if x["rc"] != 0)
tot = sum(len(rd["runs"]) for rd in rounds)
summary = {"rounds": ROUNDS, "runs": tot, "reds": reds,
           "detail": rounds}
(SEAT / "raw" / "co-tenancy-runs.json").write_text(
    json.dumps(summary, indent=1) + "\n")
print(json.dumps({"runs": tot, "reds": reds}, indent=1))
