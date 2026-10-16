#!/usr/bin/env python3
"""r88 simplifier — family-lock worker. Loads a fixture copy, calls
`_btwit_r88_family_lock()`, prints the resolved lock path + wait time,
holds the lock, exits. Used by lock-proof.py (scratch trees only)."""
import importlib.util
import json
import os
import sys
import time

sys.dont_write_bytecode = True
fixture, hold_s, mode = sys.argv[1], float(sys.argv[2]), sys.argv[3]
spec = importlib.util.spec_from_file_location("fixture_" + mode, fixture)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

t0 = time.monotonic()
fd = mod._btwit_r88_family_lock()
t1 = time.monotonic()
resolved = None
if fd is not None:
    try:
        resolved = os.readlink(f"/proc/self/fd/{fd}")
    except OSError:
        resolved = None
print(json.dumps({"mode": mode, "wait_s": round(t1 - t0, 3), "fd": fd,
                  "resolved": resolved, "tmpdir": os.environ.get("TMPDIR"),
                  "root": str(mod.ROOT)}), flush=True)
time.sleep(hold_s)
print(json.dumps({"mode": mode, "released": True}), flush=True)
