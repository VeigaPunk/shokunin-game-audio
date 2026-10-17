#!/usr/bin/env python3
"""r73 reviewer: pw-cat playback-pacing arms on the 4 s tone (frontier (b) rows).

v2: the fifo writer is a *separate script file* so the parent never holds a write
fd and shell quoting cannot corrupt the child (both were real harness bugs in v1).
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path.home() / "Projects/shokunin/audio-shokunin"
SCRATCH = REPO / "corpus/live/r73-reviewer"
TONE = SCRATCH / "tone4s.wav"
WRITER = SCRATCH / "trickle_writer.py"
results = []

WRITER.write_text(
    "import sys, time\n"
    "path, fifo, chunk, gap = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4])\n"
    "d = open(path, 'rb').read()\n"
    "f = open(fifo, 'wb', buffering=0)\n"
    "for i in range(0, len(d), chunk):\n"
    "    f.write(d[i:i+chunk])\n"
    "    time.sleep(gap)\n"
    "f.close()\n")


def reader_writer(reader_cmd, writer_cmd, timeout=30):
    fifo = SCRATCH / "fifo-pace"
    if fifo.exists():
        fifo.unlink()
    os.mkfifo(fifo)
    cmd = [c.replace("@FIFO@", str(fifo)) for c in reader_cmd]
    t0 = time.monotonic()
    reader = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(0.3)
    writer = subprocess.Popen(["sh", "-c", writer_cmd.replace("@FIFO@", str(fifo))],
                              stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    try:
        out, err = reader.communicate(timeout=timeout)
        rc, killed = reader.returncode, False
    except subprocess.TimeoutExpired:
        reader.kill()
        out, err = reader.communicate()
        rc, killed = "TIMEOUT", True
    wall = round(time.monotonic() - t0, 2)
    try:
        _, werr = writer.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        writer.kill()
        werr = "writer-killed"
    fifo.unlink()
    return {"rc": rc, "timeout": killed, "wall_s": wall, "stdout": out, "stderr": err,
            "writer_rc": writer.returncode, "writer_stderr": (werr or "")[:200]}


t0 = time.monotonic()
p = subprocess.run(["timeout", "-s", "KILL", "20", "pw-cat", "-p", str(TONE)],
                   capture_output=True, text=True)
results.append({"arm": "tone-file", "rc": p.returncode, "wall_s": round(time.monotonic() - t0, 2),
                "stderr": p.stderr, "stdout": p.stdout})

r = reader_writer(["timeout", "-s", "KILL", "25", "pw-cat", "-p", "@FIFO@"],
                  f"cat {TONE} > @FIFO@")
r["arm"] = "tone-fifo-instant-dump"
results.append(r)

r = reader_writer(["timeout", "-s", "KILL", "25", "pw-cat", "-p", "@FIFO@"],
                  f"{sys.executable} {WRITER} {TONE} @FIFO@ 1600 0.2", timeout=30)
r["arm"] = "tone-fifo-trickle-1600B-0.2s"
results.append(r)

r = reader_writer(["timeout", "-s", "KILL", "25", "pw-cat", "-p", "-a", "--rate", "8000",
                   "--channels", "1", "--format", "s16", "@FIFO@"],
                  f"cat {TONE} > @FIFO@")
r["arm"] = "tone-fifo-raw"
results.append(r)

# writer attaches, writes nothing, closes -> frontier claims rc=1 "Format not recognised"
r = reader_writer(["timeout", "-s", "KILL", "25", "pw-cat", "-p", "@FIFO@"],
                  "true > @FIFO@")
r["arm"] = "tone-fifo-empty-writer"
results.append(r)

out = SCRATCH / "replay-pacing2.json"
out.write_text(json.dumps(results, indent=1))
for r in results:
    print(f"{r['arm']:28s} rc={str(r['rc']):8s} wall={r['wall_s']:6} "
          f"wrc={r.get('writer_rc')} werr={(r.get('writer_stderr') or '').strip()[:60]} "
          f"err={(r.get('stderr') or '').strip()[:70]}")
print("wrote", out)
