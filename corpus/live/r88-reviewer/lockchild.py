#!/usr/bin/env python3
"""r88 reviewer — lock child: import a fixture copy, take the r88 family
lock, report the resolved path, optionally hold it.

argv: <fixture.py> [hold_seconds]
Prints lines:  lock_path=<realpath>  locked_at=<monotonic-since-spawn>
"""
import importlib.util
import os
import sys
import time

t0 = time.monotonic()
fx_path, *rest = sys.argv[1:]
hold = float(rest[0]) if rest else 0.0

spec = importlib.util.spec_from_file_location("fx", fx_path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
fd = m._btwit_r88_family_lock()
path = os.readlink(f"/proc/self/fd/{fd}") if fd is not None else "NONE"
print(f"lock_path={path} locked_at={time.monotonic() - t0:.3f} "
      f"tmpdir={os.environ.get('TMPDIR')}", flush=True)
if hold:
    time.sleep(hold)
    print(f"released_after={time.monotonic() - t0:.3f}", flush=True)
