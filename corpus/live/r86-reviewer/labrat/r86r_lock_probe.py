#!/usr/bin/env python3
"""r86 reviewer — r84-F1 fold probe: is the r86 family lock
TMPDIR-independent, and does it actually serialize two same-family runs
with different TMPDIRs?

Two independent measurements, no fixture edits, no audio objects:

  resolve  — load the pinned module under a given TMPDIR with os.open
             monkeypatched, so the lock function's RESOLVED PATH is
             captured without creating/locking anything. Run under two
             different TMPDIRs: the r86 path must be identical, the r85
             (r84) path must differ (the TMPDIR-scoped contrast).

  hold/wait — real flock serialization: `hold` takes the named lock and
             sleeps HOLD_S; `wait` starts later and measures how long it
             waits to acquire. r86 lock with TMPDIR-B must wait on
             TMPDIR-A's holder; the r85 lock must not.

Subcommands: resolve MODULE TMPDIR LOCKFN | hold MODULE LOCKFN SECONDS |
             wait MODULE LOCKFN
LOCKFN ∈ {r86, r85}
"""
import json
import os
import subprocess
import sys
import tempfile
import time

HOLD_DEFAULT = 4.0
REAL_OPEN = os.open


def load_module(module_path, lockfn, capture_path=None):
    """Import the pinned module; optionally monkeypatch os.open so the
    lock path is captured and no real lock file is touched."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("r86r_pinned", module_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["r86r_pinned"] = mod
    spec.loader.exec_module(mod)
    if capture_path is not None:
        real_open = REAL_OPEN

        def spy(path, flags, *a, **k):
            capture_path.append(str(path))
            return real_open("/dev/null", os.O_RDWR)
        os.open = spy
    return mod


def lockfn(mod, name):
    return (mod._pwctl_r86_family_lock if name == "r86"
            else mod._pactlmon_r85_family_lock)


def cmd_resolve(module_path, tmpdir, name):
    os.environ["TMPDIR"] = tmpdir
    tempfile.tempdir = None
    gettempdir_before = tempfile.gettempdir()
    paths = []
    mod = load_module(module_path, name, capture_path=paths)
    fd = lockfn(mod, name)()
    os.open = REAL_OPEN                     # restore the real os.open
    out = {"lockfn": name, "tmpdir": tmpdir, "module": module_path,
           "tempfile.gettempdir": gettempdir_before,
           "captured_paths": paths, "fd_returned": fd is not None,
           "roothint": str(mod.ROOT)}
    print(json.dumps(out))
    return 0


def cmd_hold(module_path, name, seconds):
    mod = load_module(module_path, name)
    t0 = time.time()
    fd = lockfn(mod, name)()
    t1 = time.time()
    with open(os.environ["WITNESS"], "w") as fh:
        json.dump({"holder_pid": os.getpid(), "acquired_at": t1,
                   "acquire_s": t1 - t0, "fd": fd}, fh)
    time.sleep(float(seconds))
    return 0


def cmd_wait(module_path, name):
    mod = load_module(module_path, name)
    t0 = time.time()
    fd = lockfn(mod, name)()
    t1 = time.time()
    print(json.dumps({"waiter_pid": os.getpid(), "waited_s": t1 - t0,
                      "fd": fd}))
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    cmd = sys.argv[1]
    if cmd == "resolve":
        return cmd_resolve(sys.argv[2], sys.argv[3], sys.argv[4])
    if cmd == "hold":
        return cmd_hold(sys.argv[2], sys.argv[3],
                        sys.argv[4] if len(sys.argv) > 4 else HOLD_DEFAULT)
    if cmd == "wait":
        return cmd_wait(sys.argv[2], sys.argv[3])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
