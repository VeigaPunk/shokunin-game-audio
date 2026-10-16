#!/usr/bin/env python3
"""r88 critic — the fixed-path lock either-way proof.

Five cases, all run on SCRATCH trees under corpus/live/r88-critic/locktest
so the live lane lock file is never touched (a sibling r88-verifier seat
was mid-run during this gate):

  A  r88 lock, same tree,   same TMPDIR      -> SERIALIZED
  B  r88 lock, same tree,   DIFFERENT TMPDIR -> SERIALIZED  (not $TMPDIR)
  C  r85 lock, different TMPDIRs             -> RACED   (negative control,
                                              the in-tree pre-fix shape)
  D  r88 lock, DIFFERENT trees, same TMPDIR  -> RACED   (tree-relative)
  E  r85 lock, same TMPDIR                   -> SERIALIZED (control can
                                              detect both directions)

Each case: child 1 takes the lock and holds ~2 s; child 2 starts 0.5 s
later and its acquire wait is measured. Both children exec the VERBATIM
committed lock functions (lockfn-r88.py / lockfn-r85.py, sha'd).
"""
import json
import os
import shutil
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "locktest")
CHILD = os.path.join(HERE, "locktest_child.py")
FN88 = os.path.join(HERE, "lockfn-r88.py")
FN85 = os.path.join(HERE, "lockfn-r85.py")

TREES = {"A": os.path.join(BASE, "treeA"),
         "B": os.path.join(BASE, "treeB")}
TMPDIRS = {"t1": os.path.join(BASE, "tmp1"),
         "t2": os.path.join(BASE, "tmp2")}

for t in list(TREES.values()) + list(TMPDIRS.values()):
    os.makedirs(os.path.join(t, "corpus", "live"), exist_ok=True)
    os.makedirs(os.path.join(t, "corpus", "fixtures"), exist_ok=True)
for t in TREES.values():
    shutil.copy(CHILD, os.path.join(t, "corpus", "fixtures",
                                    "locktest_child.py"))

CASES = [
    ("A", "r88", "A", "t1", "A", "t1", "SERIALIZED"),
    ("B", "r88", "A", "t1", "A", "t2", "SERIALIZED"),
    ("C", "r85", "A", "t1", "A", "t2", "RACED"),
    ("D", "r88", "A", "t1", "B", "t1", "RACED"),
    ("E", "r85", "A", "t1", "A", "t1", "SERIALIZED"),
]

results = []


def spawn(tree, tmp, mode, hold):
    fn = FN88 if mode == "r88" else FN85
    env = dict(os.environ)
    env["TMPDIR"] = TMPDIRS[tmp]
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    child = os.path.join(TREES[tree], "corpus", "fixtures",
                         "locktest_child.py")
    return subprocess.Popen(
        ["python3", child, mode, str(hold), fn],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        env=env, start_new_session=True)


for cid, m1, tree1, tmp1, tree2, tmp2, expect in CASES:
    p1 = spawn(tree1, tmp1, m1, 2.0)
    time.sleep(0.5)
    p2 = spawn(tree2, tmp2, m1, 0.2)
    out2, err2 = p2.communicate(timeout=30)
    out1, err1 = p1.communicate(timeout=30)
    try:
        r2 = json.loads(out2.strip().splitlines()[-1])
    except Exception:
        r2 = {"raw": out2, "err": err2}
    try:
        r1 = json.loads(out1.strip().splitlines()[-1])
    except Exception:
        r1 = {"raw": out1, "err": err1}
    waited = r2.get("waited")
    got = ("SERIALIZED" if (waited or 0) >= 1.0 else
           "RACED" if (waited or 0) < 0.1 else "INCONCLUSIVE")
    results.append({"case": cid, "mode": m1,
                    "child1": {"tree": tree1, "TMPDIR": tmp1, **r1},
                    "child2": {"tree": tree2, "TMPDIR": tmp2, **r2},
                    "child2_waited": waited, "expect": expect,
                    "got": got, "as_designed": got == expect})
    print(f"{cid}: mode={m1} c1(tree {tree1},{tmp1}) waited="
          f"{r1.get('waited')} c2(tree {tree2},{tmp2}) waited={waited} "
          f"-> {got} (expect {expect}) "
          f"{'OK' if got == expect else 'NOT-AS-DESIGNED'}")

with open(os.path.join(HERE, "locktest.json"), "w") as f:
    json.dump({"cases": results}, f, indent=2, sort_keys=True)
print("as-designed:",
      sum(1 for r in results if r["as_designed"]), "/", len(results))
