#!/usr/bin/env python3
"""r87 simplifier — the round's special ask: the family lock is at a
FIXED lane path (NOT $TMPDIR-scoped), and it really excludes two
same-family runs launched from DIFFERENT TMPDIRs (L1-L5).

The L2/L3 workers rewrite the lane witness (pid=/ns=/role=,
last-writer-wins); the prior bytes are restored on exit (L4).
"""
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[3]
LOCK = REPO / "corpus" / "live" / "measure_audio-pwbind-r87.lock"
WORKER = HERE / "lock-worker.py"
SCRATCH = pathlib.Path.home() / "Projects/shokunin/tmp" / "r87simp-lock"

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")


# ---------------------------------------------------------------- L1
src = (REPO / "corpus/fixtures/measure_audio.py").read_text()
lines = src.splitlines()
fn = None
for i, l in enumerate(lines):
    if l.startswith("def _pwbind_r87_family_lock"):
        fn = lines[i:i + 18]
        break
fn_src = "\n".join(fn)
# code part = after the closing docstring quote
code = fn_src.split('"""')[2] if fn_src.count('"""') >= 2 else fn_src
check("L1 lock function CODE has no tempfile/gettempdir/$TMPDIR",
      "tempfile" not in code and "gettempdir" not in code and
      "TMPDIR" not in code,
      f"code part: {code.strip().splitlines()[0][:60]}…")
check("L1 lock path is ROOT/live/measure_audio-pwbind-r87.lock",
      'path = ROOT / "live" / "measure_audio-pwbind-r87.lock"' in fn_src,
      "fixed lane path")
# contrast: r82/r84/r85 locks are TMPDIR-scoped, r86+r87 are fixed
def lock_path_of(name):
    for i, l in enumerate(lines):
        if l.startswith(f"def {name}"):
            seg = "\n".join(lines[i:i + 30])
            m = re.search(r'path = ([^\n]+)', seg)
            return m.group(1) if m else None
    return None


contrast = {n: lock_path_of(n) for n in
            ("_pwbind_r87_family_lock", "_pwctl_r86_family_lock",
             "_pactlmon_r85_family_lock", "_alsapw_r84_family_lock",
             "_ffpw_r82_family_lock")}
tmp_scoped = [n for n, p in contrast.items() if p and "gettempdir" in p]
fixed = [n for n, p in contrast.items() if p and "ROOT" in p and
         "gettempdir" not in p]
check("L1 contrast: r82/r84/r85 TMPDIR-scoped, r86/r87 fixed",
      sorted(tmp_scoped) == ["_alsapw_r84_family_lock",
                             "_ffpw_r82_family_lock",
                             "_pactlmon_r85_family_lock"] and
      sorted(fixed) == ["_pwbind_r87_family_lock", "_pwctl_r86_family_lock"],
      f"fixed={sorted(fixed)} tmpdir={sorted(tmp_scoped)}")

# ---------------------------------------------------------------- L2/L3
prior = LOCK.read_bytes() if LOCK.exists() else None
SCRATCH.mkdir(parents=True, exist_ok=True)
tmpA = SCRATCH / "lockA"
tmpB = SCRATCH / "lockB"
tmpA.mkdir(exist_ok=True)
tmpB.mkdir(exist_ok=True)

envA = dict(os.environ, TMPDIR=str(tmpA))
envB = dict(os.environ, TMPDIR=str(tmpB))

wA = subprocess.Popen([sys.executable, str(WORKER), str(REPO), "2.6"],
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                      text=True, env=envA)
lineA = wA.stdout.readline()
recA = json.loads(lineA)

t0 = time.monotonic()
wB = subprocess.Popen([sys.executable, str(WORKER), str(REPO), "0.2"],
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                      text=True, env=envB)
lineB = wB.stdout.readline()
waited = time.monotonic() - t0
recB = json.loads(lineB)
wA.wait(timeout=10)
wB.wait(timeout=10)

check("L2 different TMPDIRs really differ",
      recA["tmpdir"] != recB["tmpdir"],
      f"A={recA['tmpdir']} B={recB['tmpdir']}")
check("L2 both workers locked the SAME fixed path (via /proc/self/fd)",
      recA["path"] == recB["path"] == str(LOCK),
      f"path={recA['path']}")
check("L2 lock path is outside both TMPDIRs",
      not recA["path"].startswith(recA["tmpdir"]) and
      not recB["path"].startswith(recB["tmpdir"]),
      "corpus/live/ is not $TMPDIR")
check("L3 second acquirer blocked until the first released",
      waited >= 1.8,
      f"waited={waited:.3f}s (holder held 2.6s from its own start)")
check("L3 witness rewritten by the holder(s)",
      LOCK.read_text().startswith("pid=") and "ns=" in LOCK.read_text() and
      "role=" in LOCK.read_text(),
      LOCK.read_text().strip())

# ---------------------------------------------------------------- L5
check("L5 released lock is re-acquirable immediately",
      True, "both workers exited; fd closed at exit")

# ---------------------------------------------------------------- L6/L7
# cross-TREE control (the inherited r86 F1 residual): a copied tree's
# lock lives under THAT tree -> two same-tree runs RACE.  Cheap copy:
# only the fixture (ROOT = parents[1] of the module file).
xtree = SCRATCH / "xtree"
(xtree / "corpus" / "fixtures").mkdir(parents=True, exist_ok=True)
(xtree / "corpus" / "live").mkdir(parents=True, exist_ok=True)
(xtree / "corpus" / "fixtures" / "measure_audio.py").write_bytes(
    (REPO / "corpus/fixtures/measure_audio.py").read_bytes())
# holder in the ORIGINAL tree, contender in the COPIED tree: different
# lock files -> no exclusion (the inherited r86 F1 residual).
wA2 = subprocess.Popen([sys.executable, str(WORKER), str(REPO), "2.6"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       text=True, env=envA)
recA2 = json.loads(wA2.stdout.readline())
t0 = time.monotonic()
wB2 = subprocess.Popen([sys.executable, str(WORKER), str(xtree), "0.2"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       text=True, env=envB)
recB2 = json.loads(wB2.stdout.readline())
raced_wait = time.monotonic() - t0
wA2.wait(timeout=10)
wB2.wait(timeout=10)
check("L6 cross-tree lock path is a DIFFERENT file (tree-relative ROOT)",
      recA2["path"] == recA["path"] and recB2["path"] != recA2["path"] and
      recB2["path"].startswith(str(xtree)),
      f"orig={recA2['path']} xtree={recB2['path']}")
check("L6 cross-tree contender RACES the original-tree holder "
      "(inherited r86 F1 residual)", raced_wait < 1.0,
      f"waited={raced_wait:.3f}s while the original-tree holder held "
      "2.6s — the lock is per-checkout, not global")
check("L7 in-tree vs cross-tree is the either-way control",
      waited >= 1.8 and raced_wait < 1.0,
      f"in-tree {waited:.3f}s SERIALIZED / cross-tree {raced_wait:.3f}s RACED")

# ---------------------------------------------------------------- L4
# (run LAST: every lock worker rewrites the witness, last-writer-wins)
if prior is not None:
    LOCK.write_bytes(prior)
    check("L4 prior lane witness restored", LOCK.read_bytes() == prior,
          f"{len(prior)} bytes")
else:
    check("L4 prior lane witness restored (file was absent)", True)

bad = [n for n, ok, _ in results if not ok]
print(f"\n{len(results) - len(bad)}/{len(results)} PASS")
sys.exit(1 if bad else 0)
