
import fcntl, json, os, sys, tempfile, time
from pathlib import Path
which, root, hold_s, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
ROOT = Path(root)
PWPROF_R89_PID = os.getpid()
PWPROF_R89_NS = f"r89a_ns_{os.getpid()}"
PWPROF_R89_ROLE = f"r89arole{os.getpid()}"
PACTLMON_R85_PID = os.getpid()
PACTLMON_R85_NS = f"r85a_ns_{os.getpid()}"
PACTLMON_R85_ROLE = f"r85arole{os.getpid()}"
src = open(sys.argv[5]).read()
env = dict(globals())
exec(compile(src, "lockfn", "exec"), env)
t0 = time.monotonic()
fd = env[{"r89": "_pwprof_r89_family_lock",
          "r85": "_pactlmon_r85_family_lock"}[which]]()
t1 = time.monotonic()
json.dump({"acquired_after_s": round(t1 - t0, 3), "pid": os.getpid()},
          open(out, "w"))
time.sleep(hold_s)
if fd is not None:
    os.close(fd)
