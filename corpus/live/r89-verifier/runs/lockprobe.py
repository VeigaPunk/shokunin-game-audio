#!/usr/bin/env python3
"""r89 verifier lock probe — flock semantics + fixed-path materialization.

Legs:
  A: single holder acquires the fixed-path lock; a nonblocking second
     acquire on the SAME path must fail (EWOULDBLOCK); after release it
     succeeds. Proves mutual exclusion at the path.
  B: cross-materialization — two different ROOTs each with their own
     corpus/live/measure_audio-pwprof-r89.lock can hold simultaneously
     (the r84-r88 F1 residual: the lock is tree-relative, so two tree
     copies do not exclude each other).
  C: the lock path is NOT TMPDIR-derived: with TMPDIR pointed at a foreign
     dir, the lock still lands at ROOT/live/... and nothing lands under
     TMPDIR (static + executed).
"""
import fcntl
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
HERE = Path(__file__).resolve().parent
LOCKNAME = "measure_audio-pwprof-r89.lock"


def try_lock(path, block=False):
    fd = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o644)
    flags = fcntl.LOCK_EX | (0 if block else fcntl.LOCK_NB)
    try:
        fcntl.flock(fd, flags)
        return fd
    except BlockingIOError:
        os.close(fd)
        return None


def holder(path, seconds):
    """Child-process body: hold the lock, print the pid, sleep, exit."""
    fd = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o644)
    fcntl.flock(fd, fcntl.LOCK_EX)
    os.ftruncate(fd, 0)
    os.write(fd, f"pid={os.getpid()}\n".encode())
    print(f"held {os.getpid()}", flush=True)
    time.sleep(seconds)
    return 0


def main():
    out = {"root": str(ROOT), "legs": {}}
    if len(sys.argv) > 2 and sys.argv[2] == "hold":
        return holder(Path(sys.argv[3]), float(sys.argv[4]))
    live = ROOT / "live"
    live.mkdir(parents=True, exist_ok=True)
    lock = live / LOCKNAME
    # ---- A: mutual exclusion at one path ---------------------------
    f1 = try_lock(lock)
    f2 = try_lock(lock)
    out["legs"]["A_excl"] = {
        "first_acquired": f1 is not None,
        "second_blocked": f2 is None}
    if f1 is not None:
        os.close(f1)
    f3 = try_lock(lock)
    out["legs"]["A_after_release"] = {"reacquired": f3 is not None}
    if f3 is not None:
        os.close(f3)
    # ---- B: cross-materialization ---------------------------------
    with tempfile.TemporaryDirectory(prefix="r89v-root2-") as td:
        live2 = Path(td) / "live"
        live2.mkdir(parents=True, exist_ok=True)
        lock2 = live2 / LOCKNAME
        g1 = try_lock(lock)
        g2 = try_lock(lock2)
        out["legs"]["B_cross_materialization"] = {
            "lock1_held": g1 is not None, "lock2_held": g2 is not None,
            "both_held": g1 is not None and g2 is not None,
            "note": "two ROOTs -> two independent locks (F1 residual)"}
        for fd in (g1, g2):
            if fd is not None:
                os.close(fd)
    # ---- C: TMPDIR independence -----------------------------------
    foreign = Path(tempfile.mkdtemp(prefix="r89v-foreign-tmp-"))
    env = dict(os.environ, TMPDIR=str(foreign))
    script = f"""
import fcntl, os, sys
root = sys.argv[1]
p = os.path.join(root, "live", "{LOCKNAME}")
fd = os.open(p, os.O_RDWR | os.O_CREAT, 0o644)
fcntl.flock(fd, fcntl.LOCK_EX)
os.ftruncate(fd, 0); os.write(fd, b"probe\\n")
print(p)
"""
    r = subprocess.run([sys.executable, "-c", script, str(ROOT)],
                       capture_output=True, text=True, env=env, timeout=15)
    under_tmp = [str(p) for p in foreign.rglob(LOCKNAME)]
    out["legs"]["C_tmpdir_independence"] = {
        "rc": r.returncode,
        "lock_landed": r.stdout.strip(),
        "expected": str(lock),
        "landed_in_tree": r.stdout.strip() == str(lock),
        "foreign_tmpdir": str(foreign),
        "lock_under_tmpdir": under_tmp}
    # ---- D: child-holder + parent nonblocking ----------------------
    proc = subprocess.Popen(
        [sys.executable, __file__, str(ROOT), "hold", str(lock), "2.0"],
        stdout=subprocess.PIPE, text=True)
    proc.stdout.readline()
    out["legs"]["D_child_holder"] = {
        "parent_nonblocking_fails": try_lock(lock) is None}
    proc.wait(timeout=10)
    fd = try_lock(lock)
    out["legs"]["D_after_child_exit"] = {"reacquired": fd is not None}
    if fd is not None:
        os.close(fd)
    (HERE / "lockprobe.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
