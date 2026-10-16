#!/usr/bin/env python3
"""r86-critic lock driver: cross-TMPDIR and same-TMPDIR exclusion tests.

A (r86, cross-TMPDIR): holder in TMPDIR-A holds 3.0 s; contender in
   TMPDIR-B must wait (fixed-path lock) -> ~3 s wait, path identical.
B (r86, same-TMPDIR): control, same behaviour expected.
C (r85, cross-TMPDIR): NEGATIVE CONTROL for the harness itself — the
   inherited $TMPDIR-scoped lock must NOT serialize; contender acquires
   in ~0 s at a different path. Proves the test can detect non-exclusion.
"""
import json
import os
import subprocess
import time
from pathlib import Path

REPO = "/home/vgpnk/Projects/shokunin/audio-shokunin"
CHILD = f"{REPO}/corpus/live/r86-critic/locktest_child.py"
BASE = Path("/home/vgpnk/Projects/shokunin/tmp")
TMPA = BASE / "r86crit-lock-a"
TMPB = BASE / "r86crit-lock-b"
for d in (TMPA, TMPB):
    d.mkdir(parents=True, exist_ok=True)

results = {}


def run_case(name, lock, cross, hold_s=3.0):
    env_a = dict(os.environ, TMPDIR=str(TMPA), PYTHONDONTWRITEBYTECODE="1")
    env_b = dict(os.environ, TMPDIR=str(TMPB), PYTHONDONTWRITEBYTECODE="1")
    holder = subprocess.Popen(
        ["python3", CHILD, lock, "hold", str(hold_s)], env=env_a,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(0.8)  # let the holder acquire
    t0 = time.monotonic()
    cont_env = env_b if cross else env_a
    cont = subprocess.run(["python3", CHILD, lock, "try", "0"],
                          env=cont_env, capture_output=True, text=True)
    t1 = time.monotonic()
    h_out, h_err = holder.communicate(timeout=30)
    case = {"name": name, "lock": lock, "cross_tmpdir": cross,
            "holder": json.loads(h_out.strip().splitlines()[-1]),
            "contender": json.loads(cont.stdout.strip().splitlines()[-1]),
            "wall_s_contender": round(t1 - t0, 3)}
    case["holder_stderr"] = h_err[-300:]
    case["contender_stderr"] = cont.stderr[-300:]
    results[name] = case


run_case("A_r86_cross_tmpdir", "r86", cross=True)
run_case("B_r86_same_tmpdir", "r86", cross=False)
run_case("C_r85_cross_tmpdir", "r85", cross=True)

out = Path(f"{REPO}/corpus/live/r86-critic/locktest.json")
out.write_text(json.dumps(results, indent=2) + "\n")
for name, c in results.items():
    print(f"{name}: holder={c['holder']['path']} "
          f"contender={c['contender']['path']} "
          f"waited={c['contender']['waited_s']}s "
          f"wall={c['wall_s_contender']}s")
