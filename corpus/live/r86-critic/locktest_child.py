#!/usr/bin/env python3
"""r86-critic lock harness (child). Executes the VERBATIM committed lock
functions (sliced from git show fa5994a0) under the caller's TMPDIR.

usage: locktest_child.py <r86|r85> <hold|try> <seconds>
Prints one JSON line: {lock, tmpdir, path, t0, t_acquired, waited_s,
holder_line}.
"""
import fcntl
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = "/home/vgpnk/Projects/shokunin/audio-shokunin"
src = subprocess.run(
    ["git", "-C", REPO, "show", "fa5994a0:corpus/fixtures/measure_audio.py"],
    capture_output=True, check=True).stdout.decode()

which, mode, secs = sys.argv[1], sys.argv[2], float(sys.argv[3])

if which == "r86":
    m = re.search(
        r"def _pwctl_r86_family_lock\(\):.*?\n    return fd\n", src, re.S)
    body = m.group(0)
    ns = {"os": os, "fcntl": fcntl,
          "ROOT": Path(REPO) / "corpus",
          "PWCTL_R86_PID": os.getpid(),
          "PWCTL_R86_NS": f"r86a_ns_{os.getpid()}",
          "PWCTL_R86_ROLE": f"r86arole{os.getpid()}"}
    path_expr = "ROOT / 'live' / 'measure_audio-pwctl-r86.lock'"
else:
    m = re.search(
        r"def _pactlmon_r85_family_lock\(\):.*?\n    return fd\n", src, re.S)
    body = m.group(0)
    ns = {"os": os, "fcntl": fcntl, "tempfile": tempfile, "Path": Path,
          "PACTLMON_R85_PID": os.getpid(),
          "PACTLMON_R85_NS": f"r85a_ns_{os.getpid()}",
          "PACTLMON_R85_ROLE": f"r85arole{os.getpid()}"}
    path_expr = ("Path(tempfile.gettempdir()) / "
                 "'measure_audio-pactlmon-r85.lock'")

exec(body, ns)
fn = ns["_pwctl_r86_family_lock" if which == "r86"
        else "_pactlmon_r85_family_lock"]
path = eval(path_expr, {"ROOT": Path(REPO) / "corpus", "Path": Path,
                        "tempfile": tempfile})

t0 = time.monotonic()
fd = fn()
t1 = time.monotonic()
holder = ""
if fd is not None:
    try:
        os.lseek(fd, 0, os.SEEK_SET)
        holder = os.read(fd, 200).decode(errors="replace").strip()
    except OSError:
        holder = "<read-failed>"
if mode == "hold":
    time.sleep(secs)
print(json.dumps({"lock": which, "mode": mode,
                  "tmpdir": os.environ.get("TMPDIR"),
                  "tempfile_dir": tempfile.gettempdir(),
                  "path": str(path), "pid": os.getpid(),
                  "t_acquired": round(t1 - t0, 4),
                  "waited_s": round(t1 - t0, 4),
                  "holder_line": holder}))
