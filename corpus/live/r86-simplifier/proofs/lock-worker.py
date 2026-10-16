#!/usr/bin/env python3
"""Lock worker: import the SHIPPED fixtures module (committed tree,
load path), acquire the r86 family lock, report the locked fd path and
timestamps. Args: hold_seconds. Prints one JSON line."""
import importlib.util
import json
import os
import sys
import tempfile
import time

MOD = ("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/fixtures/"
       "measure_audio.py")
spec = importlib.util.spec_from_file_location("ma_fixtures_r86", MOD)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
enter = time.monotonic()
fd = m._pwctl_r86_family_lock()
locked = time.monotonic()
path = os.readlink(f"/proc/self/fd/{fd}")
time.sleep(float(sys.argv[1]))
exit_t = time.monotonic()
print(json.dumps({
    "enter": enter, "locked": locked, "exit": exit_t,
    "fd_path": path, "fd": fd,
    "TMPDIR": os.environ.get("TMPDIR"),
    "gettempdir": tempfile.gettempdir(),
    "pid": os.getpid(),
}))
