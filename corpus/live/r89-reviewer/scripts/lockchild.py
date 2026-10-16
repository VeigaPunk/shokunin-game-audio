#!/usr/bin/env python3
"""Lock witness child: resolve the r89 family-lock path (via /proc/self/fd),
take the flock, hold it for `hold_s`, and print the timeline. Imported from a
COPY of the pinned r89 blob so ROOT is the copy's root (never the worktree).

usage: lockchild.py <tree> <tmpdir> <hold_s> <label>
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

tree, tmpdir, hold_s, label = sys.argv[1], sys.argv[2], float(sys.argv[3]), \
    sys.argv[4]
os.environ["TMPDIR"] = tmpdir
sys.path.insert(0, str(Path(tree) / "corpus" / "fixtures"))
import measure_audio as M  # noqa: E402

t0 = time.time()
fd = M._pwprof_r89_family_lock()
t_locked = time.time()
if fd is None:
    resolved = None
else:
    resolved = os.readlink(f"/proc/self/fd/{fd}")
t_write = time.time()
if fd is not None:
    with open(resolved) as fh:
        content = fh.read()
else:
    content = None
time.sleep(hold_s)
if fd is not None:
    os.close(fd)
t_end = time.time()
print(json.dumps({
    "label": label, "tmpdir": tmpdir, "pid": os.getpid(),
    "lock_path": str(M.ROOT / "live" / "measure_audio-pwprof-r89.lock"),
    "resolved_fd_path": resolved, "content": content,
    "t_lock_rel": round(t_locked - t0, 3),
    "t_write_rel": round(t_write - t0, 3),
    "t_end_rel": round(t_end - t0, 3),
}))
