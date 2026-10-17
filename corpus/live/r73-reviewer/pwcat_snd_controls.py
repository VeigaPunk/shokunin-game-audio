#!/usr/bin/env python3
"""r73 reviewer: controls for the pw-cat extsuffix_snd fork.

Matrix row: pw-cat extsuffix_snd  file rc=0 / fifo rc=1.
Two competing explanations:
  H1 NAME: libsndfile's named fallback (.snd/.au -> RAW|U-Law, r72 finding) is
           reached on the file arm because the path ends in .snd; the fifo is
           named "matrix-fifo" so the fallback misses.
  H2 TRANSPORT: seekable input is required (file) and a pipe cannot.
Controls:
  C1 fifo NAMED *.snd  (non-seekable, .snd name)  -> H1: rc=0 ; H2: rc=1
  C2 file copy with NO suffix (seekable, no name) -> H1: rc=1 ; H2: rc=0
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path.home() / "Projects/shokunin/audio-shokunin"
SCRATCH = REPO / "corpus/live/r73-reviewer"
SRC = REPO / "corpus/live/round-69/extsuffix_nomatch.snd"
HOLD = 1.0
res = {}


def pwcat(target, timeout=20):
    t0 = time.monotonic()
    try:
        p = subprocess.run(["timeout", "-s", "KILL", "15", "pw-cat", "-p", str(target)],
                           capture_output=True, text=True, timeout=timeout)
        rc, err = p.returncode, p.stderr
    except subprocess.TimeoutExpired:
        rc, err = "TIMEOUT", ""
    return {"rc": rc, "wall_s": round(time.monotonic() - t0, 2),
            "stderr": err.replace(str(target), "<input>")[-200:]}


def fifo_case(name):
    fifo = SCRATCH / name
    if fifo.exists():
        fifo.unlink()
    os.mkfifo(fifo)
    t0 = time.monotonic()
    reader = subprocess.Popen(["timeout", "-s", "KILL", "15", "pw-cat", "-p", str(fifo)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(0.3)
    w = subprocess.Popen(["sh", "-c", f"cat {SRC} > {fifo}"], stdout=subprocess.DEVNULL)
    out, err = reader.communicate(timeout=25)
    w.wait(timeout=5)
    fifo.unlink()
    return {"rc": reader.returncode, "wall_s": round(time.monotonic() - t0, 2),
            "stderr": err.replace(str(fifo), "<input>")[-200:]}


res["C1_fifo_named.snd"] = fifo_case("ctl-named.snd")
res["C1b_fifo_named.au"] = fifo_case("ctl-named.au")
res["C1c_fifo_named.noext"] = fifo_case("ctl-named")

nosuffix = SCRATCH / "ctl-noext-file"
shutil.copyfile(SRC, nosuffix)
res["C2_file_no_suffix"] = pwcat(nosuffix)
res["C2b_file_named.snd"] = pwcat(SRC)
shutil.copyfile(SRC, SCRATCH / "ctl-copy.au")
res["C2c_file_named.au"] = pwcat(SCRATCH / "ctl-copy.au")
# extra: does the name fallback apply to the *hcom* bytes too?
shutil.copyfile(REPO / "corpus/live/round-66/pair_dec_hcom.wav", SCRATCH / "ctl-hcom.snd")
res["C3_hcom_bytes_named.snd_file"] = pwcat(SCRATCH / "ctl-hcom.snd")

out = SCRATCH / "pwcat-snd-controls.json"
out.write_text(json.dumps(res, indent=1))
for k, v in res.items():
    print(f"{k:28s} rc={str(v['rc']):7s} wall={v['wall_s']:5} err={(v['stderr'] or '').strip()[:90]}")
print("wrote", out)
