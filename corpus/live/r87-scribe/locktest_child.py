"""r87-scribe lock-test child: exec the COMMITTED lock function verbatim
with __file__ pointed at the pinned fixture, acquire, hold, release.

usage: locktest_child.py <r87|r84> <hold_s> <label>
Env: TMPDIR must be set by the caller (differs per child for the race).
Read-only w.r.t. the lane: the r87 lock path resolves INSIDE the pin copy
under scratch (ROOT = <pin>/corpus).
"""
import fcntl
import json
import os
import sys
import time
from pathlib import Path

PIN = Path(os.environ.get("PIN_ROOT",
                          "/home/vgpnk/Projects/shokunin/tmp/r87-scribe-work"))
FIXTURE = PIN / "corpus" / "fixtures" / "measure_audio.py"
# the lockfn SOURCE always comes from the main pin scratch; only __file__
# (and therefore ROOT) follows PIN_ROOT for the cross-tree case
SRCPIN = Path("/home/vgpnk/Projects/shokunin/tmp/r87-scribe-work")
WHICH = sys.argv[1]
HOLD = float(sys.argv[2])
LABEL = sys.argv[3]

ns = {
    "os": os,
    "fcntl": fcntl,
    "time": time,
    "Path": Path,
    "__file__": str(FIXTURE),
}
# ROOT exactly as committed (L26 of the fixture)
ns["ROOT"] = Path(ns["__file__"]).resolve().parents[1]

consts = (SRCPIN / "locktest" / "consts-r87.txt").read_text()
# the r84 control fn references its own family constants; stub them (the
# control only needs the TMPDIR-scoped PATH and flock behaviour)
ns["ALSAPW_R84_PID"] = os.getpid()
ns["ALSAPW_R84_NS"] = f"r84a_ns_{os.getpid()}"
ns["ALSAPW_R84_ROLE"] = f"r84arole{os.getpid()}"
fnfile = (SRCPIN / "locktest" / "lockfn-r87.txt").read_text() if WHICH == "r87" \
    else (SRCPIN / "locktest" / "lockfn-r84-control.txt").read_text()
import tempfile  # noqa: E402  (after env is set by the caller)
ns["tempfile"] = tempfile
exec(compile(consts + "\n" + fnfile, str(FIXTURE), "exec"), ns)
fn = ns["_pwbind_r87_family_lock"] if WHICH == "r87" \
    else ns["_alsapw_r84_family_lock"]

path = None
if WHICH == "r87":
    path = str(ns["ROOT"] / "live" / "measure_audio-pwbind-r87.lock")
else:
    path = str(Path(tempfile.gettempdir()) / "measure_audio-alsapw-r84.lock")

t0 = time.monotonic()
fd = fn()
t1 = time.monotonic()
time.sleep(HOLD)
t2 = time.monotonic()
if fd is not None:
    os.close(fd)
print(json.dumps({"label": LABEL, "pid": os.getpid(), "which": WHICH,
                  "tmpdir": os.environ.get("TMPDIR"), "path": path,
                  "t0": t0, "t1": t1, "t2": t2,
                  "held_s": t2 - t1, "waited_s": t1 - t0,
                  "fd": fd is not None}))
