#!/usr/bin/env python3
"""r88 critic — lock-test child. Holds ONE family lock via the VERBATIM
committed lock function (sliced into lockfn-*.py), then reports the
acquire wait. The path formula is the committed one: the r88 lock is
ROOT/live/... with ROOT = Path(__file__).resolve().parents[1]; the r85
control is Path(tempfile.gettempdir())/... (the pre-fix shape).

argv: <mode r88|r85> <hold_s> <lockfn file>
Prints one JSON line {pid, waited, fd} to stdout, then holds.
"""
import fcntl
import json
import os
import sys
import tempfile
import time
from pathlib import Path

mode, hold, fnfile = sys.argv[1], float(sys.argv[2]), sys.argv[3]
ROOT = Path(__file__).resolve().parents[1]      # the committed formula
src = open(fnfile).read()
g = {"os": os, "fcntl": fcntl, "Path": Path, "tempfile": tempfile,
     "ROOT": ROOT, "time": time,
     "BTWIT_R88_PID": os.getpid(),
     "BTWIT_R88_NS": f"r88a_ns_{os.getpid()}",
     "BTWIT_R88_ROLE": f"r88arole{os.getpid()}",
     "PACTLMON_R85_PID": os.getpid(), "PACTLMON_R85_NS": "ns",
     "PACTLMON_R85_ROLE": "role"}
exec(compile(src, fnfile, "exec"), g)
fn = (g["_btwit_r88_family_lock"] if mode == "r88"
      else g["_pactlmon_r85_family_lock"])
t0 = time.monotonic()
fd = fn()
t1 = time.monotonic()
print(json.dumps({"pid": os.getpid(), "mode": mode,
                  "waited": round(t1 - t0, 3),
                  "lock_path": str((ROOT / "live"
                                    / "measure_audio-btwit-r88.lock")
                                   if mode == "r88" else
                                   (Path(tempfile.gettempdir())
                                    / "measure_audio-pactlmon-r85.lock")),
                  "held": fd is not None}), flush=True)
time.sleep(hold)
if fd is not None:
    os.close(fd)
