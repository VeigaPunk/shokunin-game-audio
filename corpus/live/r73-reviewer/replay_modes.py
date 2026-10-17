#!/usr/bin/env python3
"""r73 reviewer: prior-row byte-stability replay.

Runs the pre-existing probe modes and records the sha256 of each receipt, plus the
fixture sha256 before/after the batch (so a mid-batch landing is attributable).
Usage: replay_modes.py <label>   -> writes corpus/live/r73-reviewer/replay-<label>.json
"""
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path.home() / "Projects/shokunin/audio-shokunin"
SCRATCH = REPO / "corpus/live/r73-reviewer"
FIXTURE = REPO / "corpus/fixtures/measure_audio.py"

MODES = [
    ("normal", []),
    ("ffprobe-transport-r71", ["--probe-ffprobe-transport-r71"]),
    ("sndfile-transport-r72", ["--probe-sndfile-transport-r72"]),
    ("transport-txw-piperefuse-r68", ["--probe-transport-txw-piperefuse-r68"]),
    ("transport-extsuffix-snd-r69", ["--probe-transport-extsuffix-snd-r69"]),
    ("transport-dec-act-r67", ["--probe-transport-dec-act-r67"]),
    ("ui-preempt-gsrt-r65", ["--probe-ui-preempt-gsrt-r65"]),
    ("fifo-hold-ladder-r70", ["--probe-fifo-hold-ladder-r70"]),
]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


label = sys.argv[1]
res = {"label": label, "fixture_sha_before": sha(FIXTURE), "modes": {}}
for name, args in MODES:
    t0 = time.monotonic()
    p = subprocess.run([sys.executable, str(FIXTURE), *args], capture_output=True,
                       text=True, cwd=REPO, timeout=600)
    wall = round(time.monotonic() - t0, 2)
    receipt = None
    try:
        receipt = json.loads(p.stdout.strip().splitlines()[-1]).get("receipt")
    except Exception:
        pass
    res["modes"][name] = {"rc": p.returncode, "wall_s": wall, "receipt": receipt,
                          "receipt_sha": sha(receipt) if receipt else None}
    print(f"{name:32s} rc={p.returncode} wall={wall:7} {res['modes'][name]['receipt_sha']}")
res["fixture_sha_after"] = sha(FIXTURE)
(SCRATCH / f"replay-{label}.json").write_text(json.dumps(res, indent=1))
print("fixture:", res["fixture_sha_before"], "->", res["fixture_sha_after"])
print("wrote", SCRATCH / f"replay-{label}.json")
