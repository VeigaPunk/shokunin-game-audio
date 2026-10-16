#!/usr/bin/env python3
"""r87 reviewer — the family-lock probe (r84 F1 fold verification).

Imports the PINNED committed blob (never the worktree) from a replica
tree and exercises `_pwbind_r87_family_lock` for real:

  resolve   — capture the path the function would open (os.open patched),
              for the r87 lock and the r85 control lock, under two TMPDIRs
  hold      — take the real lock, write a witness, hold for N seconds
  wait      — take the real lock, record how long it blocked

Every lock this probe takes lives under this seat's receipts dir
(corpus/live/r87-reviewer/tree*/corpus/live/) — the lane's own lock file
is never touched.
"""
import importlib.util
import json
import os
import pathlib
import signal
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent


def load_module(tree):
    path = HERE / tree / "corpus/fixtures/measure_audio.py"
    spec = importlib.util.spec_from_file_location(f"r87r_mod_{tree}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cmd_resolve(tree, out):
    mod = load_module(tree)
    seen = []
    real_open = os.open

    def spy(path, flags, *a, **kw):
        seen.append(str(path))
        return real_open(path, flags, *a, **kw)

    os.open = spy
    try:
        mod._pwbind_r87_family_lock()
        # the r85 control lock (TMPDIR-scoped) — resolve only, real path
        r85 = pathlib.Path(
            mod.tempfile.gettempdir()) / "measure_audio-pactlmon-r85.lock"
    finally:
        os.open = real_open
    json.dump({"tree": tree, "module_file": str(mod.__file__),
               "root": str(mod.ROOT), "tmpdir": os.environ.get("TMPDIR"),
               "r87_open_paths": seen,
               "r87_lock_path": seen[0] if seen else None,
               "r85_lock_path": str(r85)}, open(out, "w"), indent=1)


def cmd_hold(tree, seconds, out):
    mod = load_module(tree)
    t0 = time.monotonic()
    fd = mod._pwbind_r87_family_lock()
    held = time.monotonic() - t0
    json.dump({"tree": tree, "fd": fd, "acquire_s": round(held, 4),
               "pid": os.getpid(), "tmpdir": os.environ.get("TMPDIR"),
               "lock": str(mod.ROOT / "live" /
                           "measure_audio-pwbind-r87.lock")},
              open(out, "w"), indent=1)
    time.sleep(float(seconds))
    json.dump({"tree": tree, "fd": fd, "released_after_s": float(seconds)},
              open(out + ".done", "w"), indent=1)


def _alarm(signum, frame):
    raise TimeoutError("waiter bound hit")


def cmd_wait(tree, out):
    mod = load_module(tree)
    signal.signal(signal.SIGALRM, _alarm)
    signal.setitimer(signal.ITIMER_REAL, 30.0)
    t0 = time.monotonic()
    try:
        fd = mod._pwbind_r87_family_lock()
        waited = time.monotonic() - t0
        state = "acquired"
    except TimeoutError:
        fd, waited, state = None, time.monotonic() - t0, "timeout"
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    json.dump({"tree": tree, "fd": fd, "state": state,
               "waited_s": round(waited, 4), "pid": os.getpid(),
               "tmpdir": os.environ.get("TMPDIR"),
               "lock": str(mod.ROOT / "live" /
                           "measure_audio-pwbind-r87.lock")},
              open(out, "w"), indent=1)


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "resolve":
        cmd_resolve(sys.argv[2], sys.argv[3])
    elif what == "hold":
        cmd_hold(sys.argv[2], sys.argv[3], sys.argv[4])
    elif what == "wait":
        cmd_wait(sys.argv[2], sys.argv[3])
    else:
        raise SystemExit(f"unknown subcommand {what}")
