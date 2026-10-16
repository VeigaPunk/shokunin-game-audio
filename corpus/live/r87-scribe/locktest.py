"""r87-scribe lock test driver: race two children with DIFFERENT TMPDIRs.

Cases:
  A r87 cross-TMPDIR  expect SERIALIZED
  B r84 cross-TMPDIR  expect RACED  (negative control: harness can see racing)
  C r87 same-TMPDIR   expect SERIALIZED
  D r87 dead-holder   expect immediate re-acquire (0 s)
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHILD = str(HERE / "locktest_child.py")
HOLD = 2.0
OUT = []
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")


def run_child(which, label, tmpdir, hold=HOLD):
    tmpdir = Path(tmpdir)
    tmpdir.mkdir(parents=True, exist_ok=True)
    env = dict(ENV, TMPDIR=str(tmpdir))
    p = subprocess.run([sys.executable, CHILD, which, str(hold), label],
                       capture_output=True, text=True, env=env, timeout=60)
    lines = p.stdout.strip().splitlines()
    if not lines:
        raise RuntimeError(f"child {label} produced no output; "
                           f"rc={p.returncode} stderr={p.stderr[-400:]}")
    rec = json.loads(lines[-1])
    rec["stderr_tail"] = p.stderr[-200:]
    return rec


def spawn_child(which, label, tmpdir, pin_root=None):
    tmpdir = Path(tmpdir)
    tmpdir.mkdir(parents=True, exist_ok=True)
    env = dict(ENV, TMPDIR=str(tmpdir))
    if pin_root:
        env["PIN_ROOT"] = str(pin_root)
    return subprocess.Popen([sys.executable, CHILD, which, str(HOLD), label],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, env=env)


def collect(p, label):
    out, err = p.communicate(timeout=60)
    lines = out.strip().splitlines()
    if not lines:
        raise RuntimeError(f"child {label} produced no output; "
                           f"rc={p.returncode} stderr={err[-400:]}")
    rec = json.loads(lines[-1])
    rec["stderr_tail"] = err[-200:]
    return rec


def pair(which, label, tA, tB, pin_a=None, pin_b=None):
    """Spawn BOTH children back-to-back so their hold windows overlap."""
    pa = spawn_child(which, label + "-A", tA, pin_root=pin_a)
    pb = spawn_child(which, label + "-B", tB, pin_root=pin_b)
    a = collect(pa, label + "-A")
    b = collect(pb, label + "-B")
    return a, b


def verdict(a, b, expect):
    overlap = min(a["t2"], b["t2"]) - max(a["t1"], b["t1"])
    serialized = overlap <= 0
    got = "SERIALIZED" if serialized else "RACED"
    return {"expect": expect, "got": got, "serialized": serialized,
            "overlap_s": round(overlap, 4),
            "waited_a": round(a["waited_s"], 4),
            "waited_b": round(b["waited_s"], 4),
            "pass": got == expect}


cases = []
# A: r87 cross-TMPDIR — the assigned focus
a, b = pair("r87", "A-r87-cross-tmpdir", HERE / "tmpA1", HERE / "tmpB1")
cases.append({"case": "A-r87-cross-tmpdir", "a": a, "b": b,
              **verdict(a, b, "SERIALIZED")})
# B: r84 control (TMPDIR-scoped) — must race
a, b = pair("r84", "B-r84-control-cross-tmpdir", HERE / "tmpA2", HERE / "tmpB2")
cases.append({"case": "B-r84-control-cross-tmpdir", "a": a, "b": b,
              **verdict(a, b, "RACED")})
# C: r87 same TMPDIR
a, b = pair("r87", "C-r87-same-tmpdir", HERE / "tmpC", HERE / "tmpC")
cases.append({"case": "C-r87-same-tmpdir", "a": a, "b": b,
              **verdict(a, b, "SERIALIZED")})
# D: dead holder — acquire, exit, re-acquire should not wait
d1 = run_child("r87", "D-r87-dead-holder-1", HERE / "tmpD", hold=0.05)
time.sleep(0.3)
d2 = run_child("r87", "D-r87-dead-holder-2", HERE / "tmpD", hold=0.05)
cases.append({"case": "D-r87-dead-holder",
              "a": d1, "b": d2,
              "expect": "IMMEDIATE", "got": "IMMEDIATE"
              if d2["waited_s"] < 0.05 else f"WAITED {d2['waited_s']:.3f}s",
              "pass": d2["waited_s"] < 0.05,
              "first_waited_s": round(d1["waited_s"], 4),
              "second_waited_s": round(d2["waited_s"], 4)})
# E: cross-TREE copy of the same commit — the lock is tree-relative, so
# two DIFFERENT checkout copies must NOT exclude (known r86 residual)
tree2 = HERE.parent / "tree2"
(tree2 / "corpus" / "fixtures").mkdir(parents=True, exist_ok=True)
(tree2 / "corpus" / "live").mkdir(parents=True, exist_ok=True)
import shutil
shutil.copyfile(HERE.parent / "corpus" / "fixtures" / "measure_audio.py",
                tree2 / "corpus" / "fixtures" / "measure_audio.py")
a, b = pair("r87", "E-r87-cross-tree", HERE / "tmpE1", HERE / "tmpE2",
            pin_a=HERE.parent, pin_b=tree2)
cases.append({"case": "E-r87-cross-tree", "a": a, "b": b,
              **verdict(a, b, "RACED")})

print(json.dumps({"hold_s": HOLD, "cases": cases}, indent=1))
print("SUMMARY:", " ".join(
    f"{c['case']}={'PASS' if c['pass'] else 'FAIL'}" for c in cases))
