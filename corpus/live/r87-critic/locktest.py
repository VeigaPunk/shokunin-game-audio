#!/usr/bin/env python3
"""r87-critic lock either-way proof.

Slices the three committed lock functions VERBATIM out of
`git show d1e687b9:corpus/fixtures/measure_audio.py` and execs them in a
controlled harness:

  * r87 `_pwbind_r87_family_lock`  -> fixed lane path (the claim under test)
  * r86 `_pwctl_r86_family_lock`   -> fixed lane path (already-fixed sibling)
  * r85 `_pactlmon_r85_family_lock`-> $TMPDIR-scoped (NEGATIVE CONTROL,
                                      the in-tree pre-fix shape)

Cases:
  A same-tree  / different TMPDIR / r87  -> expect SERIALIZED
  B same-tree  / different TMPDIR / r86  -> expect SERIALIZED
  C same-tree  / different TMPDIR / r85  -> expect RACED (control: proves
                                            the harness can detect racing)
  D same-TMPDIR/ same tree      / r87  -> expect SERIALIZED
  E cross-tree (copied fixture) / r87  -> expect RACED (the inherited
                                          tree-relative co-tenancy residual)

Read-only w.r.t. tracked content: it only creates/reuses the lock files
under corpus/live/ (untracked) and scratch trees under $TMPDIR.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = "/home/vgpnk/Projects/shokunin/audio-shokunin"
HERE = os.path.join(ROOT, "corpus/live/r87-critic")
COMMIT = "d1e687b9"
FIXTURE = "corpus/fixtures/measure_audio.py"
HOLD_S = 2.0


def slice_committed_fixture(dest):
    """Write the COMMITTED bytes of the fixture to dest (not the worktree)."""
    out = subprocess.run(
        ["git", "show", f"{COMMIT}:{FIXTURE}"],
        cwd=ROOT, capture_output=True, check=True,
    )
    open(dest, "wb").write(out.stdout)
    return out.stdout


def extract_fn(src, name):
    """Slice a top-level `def name(` ... up to the next top-level def."""
    lines = src.split("\n")
    start = None
    for i, ln in enumerate(lines):
        if ln.startswith(f"def {name}("):
            start = i
            break
    if start is None:
        raise SystemExit(f"function {name} not found")
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("def "):
            end = j
            break
    return "\n".join(lines[start:end]).rstrip() + "\n"


def main():
    # --- 1. slice the committed functions verbatim ----------------------
    tmp_fixture = os.path.join(HERE, "_committed_measure_audio.py")
    blob = slice_committed_fixture(tmp_fixture)
    src = blob.decode()
    fns = {
        "r87": extract_fn(src, "_pwbind_r87_family_lock"),
        "r86": extract_fn(src, "_pwctl_r86_family_lock"),
        "r85": extract_fn(src, "_pactlmon_r85_family_lock"),
    }
    for k, v in fns.items():
        open(os.path.join(HERE, f"lockfn-{k}.py"), "w").write(v)

    # --- 2. build the child harness -------------------------------------
    harness = os.path.join(HERE, "locktest_child.py")
    open(harness, "w").write('''#!/usr/bin/env python3
"""Child: acquire one sliced committed lock function, hold, release."""
import fcntl, json, os, sys, time
from pathlib import Path
import tempfile

LOCKFN, ROOTDIR, HOLD_S, OUT = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
FN = open(LOCKFN).read()

ROOT = Path(ROOTDIR)
# the committed functions reference these module globals by name
PWBIND_R87_PID = os.getpid()
PWBIND_R87_NS = f"r87a_ns_{os.getpid()}"
PWBIND_R87_ROLE = f"r87arole{os.getpid()}"
PWCTL_R86_PID = os.getpid()
PWCTL_R86_NS = f"r86a_ns_{os.getpid()}"
PWCTL_R86_ROLE = f"r86arole{os.getpid()}"
PACTLMON_R85_PID = os.getpid()
PACTLMON_R85_NS = f"r85a_ns_{os.getpid()}"
PACTLMON_R85_ROLE = f"r85arole{os.getpid()}"

ns = {"fcntl": fcntl, "os": os, "time": time, "Path": Path,
      "tempfile": tempfile, "ROOT": ROOT,
      "PWBIND_R87_PID": PWBIND_R87_PID, "PWBIND_R87_NS": PWBIND_R87_NS,
      "PWBIND_R87_ROLE": PWBIND_R87_ROLE,
      "PWCTL_R86_PID": PWCTL_R86_PID, "PWCTL_R86_NS": PWCTL_R86_NS,
      "PWCTL_R86_ROLE": PWCTL_R86_ROLE,
      "PACTLMON_R85_PID": PACTLMON_R85_PID, "PACTLMON_R85_NS": PACTLMON_R85_NS,
      "PACTLMON_R85_ROLE": PACTLMON_R85_ROLE}
exec(compile(FN, LOCKFN, "exec"), ns)
fn = [v for k, v in ns.items() if callable(v) and getattr(v, "__name__", "").startswith("_") and "family_lock" in getattr(v, "__name__", "")][0]

t0 = time.time()
fd = fn()
t1 = time.time()
time.sleep(HOLD_S)
t2 = time.time()
if fd is not None:
    fcntl.flock(fd, fcntl.LOCK_UN)
json.dump({"pid": os.getpid(), "t0": t0, "t1": t1, "t2": t2,
           "held_s": t2 - t1, "waited_s": t1 - t0, "fd": fd is not None},
          open(OUT, "w"))
''')

    # --- 3. scratch trees ------------------------------------------------
    scratch = tempfile.mkdtemp(prefix="r87crit-lock-", dir=os.environ["TMPDIR"])
    treeA = os.path.join(scratch, "treeA")
    os.makedirs(os.path.join(treeA, "live"))
    treeB = os.path.join(scratch, "treeB")
    os.makedirs(os.path.join(treeB, "live"))
    # treeA: point at the real lane (same tree as the committed lane)
    # treeB: a COPY of the fixture location (cross-tree case)
    tmpd1 = os.path.join(scratch, "tmp1")
    tmpd2 = os.path.join(scratch, "tmp2")
    os.makedirs(tmpd1)
    os.makedirs(tmpd2)

    def run_pair(label, lockfn, rootA, rootB, tmpA, tmpB, expect):
        outs = []
        procs = []
        for i, (rt, td) in enumerate(((rootA, tmpA), (rootB, tmpB))):
            out = os.path.join(scratch, f"{label}-{i}.json")
            env = dict(os.environ, TMPDIR=td, PYTHONDONTWRITEBYTECODE="1")
            p = subprocess.Popen(
                [sys.executable, harness,
                 os.path.join(HERE, f"lockfn-{lockfn}.py"), rt,
                 str(HOLD_S), out],
                env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            procs.append(p)
            outs.append(out)
        for p in procs:
            p.wait()
        res = [json.load(open(o)) for o in outs]
        a, b = res
        # serialized iff their held intervals do not overlap
        overlap = min(a["t2"], b["t2"]) - max(a["t1"], b["t1"])
        serialized = overlap <= 0.0
        # lock file each child actually took (by path)
        return {
            "label": label, "lockfn": lockfn, "expect": expect,
            "a": a, "b": b,
            "overlap_s": round(overlap, 4),
            "serialized": serialized,
            "waited_a": round(a["waited_s"], 3),
            "waited_b": round(b["waited_s"], 3),
            "verdict": "PASS" if serialized == (expect == "SERIALIZED") else "FAIL",
        }

    real_live = os.path.join(ROOT, "corpus")  # ROOT for the real lane tree
    cases = []
    cases.append(run_pair("A-r87-cross-tmpdir", "r87", real_live, real_live,
                          tmpd1, tmpd2, "SERIALIZED"))
    cases.append(run_pair("B-r86-cross-tmpdir", "r86", real_live, real_live,
                          tmpd1, tmpd2, "SERIALIZED"))
    cases.append(run_pair("C-r85-cross-tmpdir-CONTROL", "r85", real_live,
                          real_live, tmpd1, tmpd2, "RACED"))
    cases.append(run_pair("D-r87-same-tmpdir", "r87", real_live, real_live,
                          tmpd1, tmpd1, "SERIALIZED"))
    cases.append(run_pair("E-r87-cross-tree", "r87", real_live, treeA,
                          tmpd1, tmpd2, "RACED"))

    out = {"commit": COMMIT, "hold_s": HOLD_S, "cases": cases,
           "scratch": scratch,
           "lockfiles_after": {}}
    for lf in ("measure_audio-pwbind-r87.lock", "measure_audio-pwctl-r86.lock"):
        p = os.path.join(real_live, "live", lf)
        out["lockfiles_after"][lf] = open(p).read() if os.path.exists(p) else None
    json.dump(out, open(os.path.join(HERE, "locktest.json"), "w"), indent=1)

    lines = []
    for c in cases:
        lines.append(
            f"{c['label']:30s} expect={c['expect']:10s} "
            f"overlap={c['overlap_s']:>8.4f}s serialized={c['serialized']!s:5s} "
            f"waited=({c['waited_a']:.3f},{c['waited_b']:.3f}) {c['verdict']}")
    txt = "\n".join(lines) + "\n"
    open(os.path.join(HERE, "locktest.out"), "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
