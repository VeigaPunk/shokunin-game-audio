#!/usr/bin/env python3
"""r88-verifier lock probe control: the r85 helper is TMPDIR-scoped.

Usage: python3 lockprobe_r85ctl.py <tree> <outdir>
Proves the contrast: the r85 lock lands under $TMPDIR and NOT under the
tree (so the r88 fold to a tree-relative path is a real change).
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

TREE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
ROOT = TREE / "corpus"
src = (ROOT / "fixtures" / "measure_audio.py").read_text()
m = re.search(r"^def _pactlmon_r85_family_lock\(.*?(?=^def |\Z)", src,
              re.S | re.M)
assert m
fn = m.group(0)
foreign_tmp = tempfile.mkdtemp(prefix="r88v-ctl-tmp-")
script = "\n".join([
    "import tempfile, os, fcntl",
    "from pathlib import Path",
    f"ROOT = Path({str(ROOT)!r})",
    "PACTLMON_R85_PID = 424245",
    'PACTLMON_R85_NS = "r88v_ns_424245"',
    'PACTLMON_R85_ROLE = "r88vrole424245"',
    fn,
    "fd = _pactlmon_r85_family_lock()",
    'lock = Path(tempfile.gettempdir()) / "measure_audio-pactlmon-r85.lock"',
    'print("fd_none=" + str(fd is None))',
    'print("under_tmpdir=" + str(lock.exists()))',
    'print("lock_path=" + str(lock))',
    'print("under_tree=" + str((ROOT / "live" / "measure_audio-pactlmon-r85.lock").exists()))',
    'print("tmpdir=" + tempfile.gettempdir())',
])
p = subprocess.run([sys.executable, "-c", script],
                   env=dict(os.environ, TMPDIR=foreign_tmp),
                   capture_output=True, timeout=30)
res = {"rc": p.returncode, "stdout": p.stdout.decode(),
       "stderr": p.stderr.decode()[-400:], "foreign_tmpdir": foreign_tmp}
(OUT / "lockprobe-r85ctl.json").write_text(json.dumps(res, indent=1) + "\n")
print(json.dumps(res, indent=1))
