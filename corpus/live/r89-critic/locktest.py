#!/usr/bin/env python3
"""r89 critic: the fixed-path lock either-way proof.

The committed r89 lock function is sliced VERBATIM out of the commit
object and executed on scratch trees only (the live lane lock file is
never written). The committed r85 lock — `Path(tempfile.gettempdir())`
scoped — is sliced the same way as the NEGATIVE CONTROL that proves the
harness can detect racing.

Cases (a child holds the lock 1.5 s; the parent measures the wait):
  A r89 lock, same tree,  same TMPDIR     -> SERIALIZED
  B r89 lock, same tree,  DIFFERENT TMPDIR-> SERIALIZED   (task claim)
  C r85 lock, same tree,  different TMPDIR-> RACED        (control)
  D r89 lock, DIFFERENT tree, same TMPDIR -> RACED        (inherited F8)
  E r85 lock, same tree,  same TMPDIR     -> SERIALIZED
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SCRATCH = OUT / "locktest"
COMMIT = "0d732989"
FIXTURE = "corpus/fixtures/measure_audio.py"

src = subprocess.run(["git", "show", f"{COMMIT}:{FIXTURE}"], cwd=ROOT,
                     capture_output=True, text=True).stdout
lines = src.splitlines(keepends=True)


def slice_fn(name):
    start = next(i for i, l in enumerate(lines) if l.startswith(f"def {name}("))
    end = next(j for j in range(start + 1, len(lines))
               if lines[j].startswith("def "))
    return "".join(lines[start:end])


lock_r89 = slice_fn("_pwprof_r89_family_lock")
lock_r85 = slice_fn("_pactlmon_r85_family_lock")
(OUT / "lockfn-r89.py").write_text(lock_r89)
(OUT / "lockfn-r85.py").write_text(lock_r85)

CHILD = r'''
import fcntl, json, os, sys, tempfile, time
from pathlib import Path
which, root, hold_s, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
ROOT = Path(root)
PWPROF_R89_PID = os.getpid()
PWPROF_R89_NS = f"r89a_ns_{os.getpid()}"
PWPROF_R89_ROLE = f"r89arole{os.getpid()}"
PACTLMON_R85_PID = os.getpid()
PACTLMON_R85_NS = f"r85a_ns_{os.getpid()}"
PACTLMON_R85_ROLE = f"r85arole{os.getpid()}"
src = open(sys.argv[5]).read()
env = dict(globals())
exec(compile(src, "lockfn", "exec"), env)
t0 = time.monotonic()
fd = env[{"r89": "_pwprof_r89_family_lock",
          "r85": "_pactlmon_r85_family_lock"}[which]]()
t1 = time.monotonic()
json.dump({"acquired_after_s": round(t1 - t0, 3), "pid": os.getpid()},
          open(out, "w"))
time.sleep(hold_s)
if fd is not None:
    os.close(fd)
'''


def make_tree(name):
    """ROOT in the fixture is `parents[1]` of the script = the corpus dir,
    so the lock lives at <tree>/corpus/live/<name>.lock."""
    tree = SCRATCH / name / "tree" / "corpus"
    (tree / "live").mkdir(parents=True, exist_ok=True)
    return tree


shutil.rmtree(SCRATCH, ignore_errors=True)
SCRATCH.mkdir(parents=True)
treeA = make_tree("A")
treeB = make_tree("B")
tmpA = SCRATCH / "tmpA"
tmpB = SCRATCH / "tmpB"
tmpA.mkdir()
tmpB.mkdir()
child_py = OUT / "locktest_child.py"
child_py.write_text(CHILD)

CASES = [
    ("A", "r89", treeA, tmpA, treeA, tmpA, "SERIALIZED"),
    ("B", "r89", treeA, tmpA, treeA, tmpB, "SERIALIZED"),
    ("C", "r85", treeA, tmpA, treeA, tmpB, "RACED"),
    ("D", "r89", treeA, tmpA, treeB, tmpA, "RACED"),
    ("E", "r85", treeA, tmpA, treeA, tmpA, "SERIALIZED"),
]

results = []
for case, which, tree1, tmp1, tree2, tmp2, expected in CASES:
    fn = OUT / ("lockfn-r89.py" if which == "r89" else "lockfn-r85.py")
    out1 = SCRATCH / f"{case}-1.json"
    out2 = SCRATCH / f"{case}-2.json"
    env1 = dict(os.environ, TMPDIR=str(tmp1))
    env2 = dict(os.environ, TMPDIR=str(tmp2))
    p1 = subprocess.Popen([sys.executable, str(child_py), which, str(tree1),
                           "1.5", str(out1), str(fn)], env=env1)
    time.sleep(0.4)                      # child 1 must own the lock first
    p2 = subprocess.Popen([sys.executable, str(child_py), which, str(tree2),
                           "0.0", str(out2), str(fn)], env=env2)
    p2.wait()
    p1.wait()
    j2 = json.loads(out2.read_text())
    got = "SERIALIZED" if j2["acquired_after_s"] >= 1.0 else "RACED"
    results.append({"case": case, "lock": which,
                    "tree1": str(tree1.relative_to(SCRATCH)),
                    "tree2": str(tree2.relative_to(SCRATCH)),
                    "tmp1": str(tmp1.relative_to(SCRATCH)),
                    "tmp2": str(tmp2.relative_to(SCRATCH)),
                    "expected": expected, "got": got,
                    "waited_s": j2["acquired_after_s"],
                    "as_designed": got == expected})
    print(f"case {case}: {which} {expected} -> {got} "
          f"(waited {j2['acquired_after_s']}s)")

lockfiles = sorted(str(p.relative_to(SCRATCH))
                   for p in SCRATCH.rglob("*.lock"))
summary = {"commit": COMMIT,
           "lock_r89_sha256": hashlib.sha256(lock_r89.encode()).hexdigest(),
           "lock_r85_sha256": hashlib.sha256(lock_r85.encode()).hexdigest(),
           "cases": results, "lockfiles": lockfiles,
           "live_lane_lock_untouched": True}
(OUT / "locktest.json").write_text(json.dumps(summary, indent=2) + "\n")
print("lockfiles created in scratch:", lockfiles)
print("all as designed:", all(r["as_designed"] for r in results))
