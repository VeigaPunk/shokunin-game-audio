#!/usr/bin/env python3
"""r73 reviewer: is pw-cat's fifo exit driven by *writer close* (frontier (b) row)
or by *format-level EOF* (sndfile knows the WAV data length)?

Writer holds the write end open for 6 s after writing the member; if pw-cat exits
before the writer does, the exit cannot be writer-EOF driven. Writer liveness at
pw-cat exit is asserted from the writer's own timeline (it prints before/after).
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path.home() / "Projects/shokunin/audio-shokunin"
SCRATCH = REPO / "corpus/live/r73-reviewer"
HCOM = REPO / "corpus/live/round-66/pair_dec_hcom.wav"
WRITER = SCRATCH / "linger_writer.py"
WRITER.write_text(
    "import os, sys, time\n"
    "fifo, path, hold = sys.argv[1], sys.argv[2], float(sys.argv[3])\n"
    "f = open(fifo, 'wb', buffering=0)\n"
    "f.write(open(path, 'rb').read())\n"
    "print('WROTE', flush=True)\n"
    "time.sleep(hold)\n"
    "print('CLOSING', flush=True)\n"
    "f.close()\n")

fifo = SCRATCH / "fifo-linger2"
if fifo.exists():
    fifo.unlink()
os.mkfifo(fifo)

t0 = time.monotonic()
reader = subprocess.Popen(["timeout", "-s", "KILL", "20", "pw-cat", "-p", str(fifo)],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
time.sleep(0.3)
writer = subprocess.Popen([sys.executable, str(WRITER), str(fifo), str(HCOM), "6"],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
out, err = reader.communicate(timeout=25)
reader_done = time.monotonic() - t0
reader_rc = reader.returncode
writer_alive_at_reader_exit = writer.poll() is None
wout, werr = writer.communicate(timeout=15)
writer_done = time.monotonic() - t0
fifo.unlink()

res = {"arm": "pwcat-fifo-writer-holds-6s",
       "reader_rc": reader_rc, "reader_wall_s": round(reader_done, 2),
       "writer_still_alive_when_reader_exited": writer_alive_at_reader_exit,
       "writer_wall_s": round(writer_done, 2), "writer_stdout": wout.split(),
       "reader_stderr": err[-200:]}
print(json.dumps(res, indent=1))
(SCRATCH / "pwcat-linger-proof.json").write_text(json.dumps(res, indent=1))
