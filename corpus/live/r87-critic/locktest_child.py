#!/usr/bin/env python3
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
