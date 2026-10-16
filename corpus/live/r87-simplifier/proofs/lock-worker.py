#!/usr/bin/env python3
"""One lock holder: load the REAL shipped module, acquire the r87 family
lock, print {pid, path, tmpdir, fd} as JSON on stdout, hold, exit.

The lock path is resolved through /proc/self/fd/<fd> — the actual file
the kernel locked — not through the module's own constant.
"""
import importlib.util
import json
import os
import pathlib
import sys
import tempfile
import time

repo = pathlib.Path(sys.argv[1])
hold_s = float(sys.argv[2])

spec = importlib.util.spec_from_file_location(
    "shipped_measure_audio", repo / "corpus" / "fixtures" / "measure_audio.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

fd = mod._pwbind_r87_family_lock()
rec = {
    "pid": os.getpid(),
    "fd": fd,
    "tmpdir": tempfile.gettempdir(),
    "path": os.readlink(f"/proc/self/fd/{fd}") if fd is not None else None,
    "acquired_at": time.time(),
}
print(json.dumps(rec), flush=True)
time.sleep(hold_s)
# release + leave the witness bytes in place (the lane file is scratch)
if fd is not None:
    os.close(fd)
