#!/usr/bin/env python3
"""r73 reviewer: pw-cat playback-pacing arms on the 4 s tone (frontier (b) rows)."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path.home() / "Projects/shokunin/audio-shokunin"
SCRATCH = REPO / "corpus/live/r73-reviewer"
TONE = SCRATCH / "tone4s.wav"
results = []


def reader_writer(reader_cmd, writer_cmd, timeout=30):
    """writer_cmd is a *shell* string whose stdout is redirected to the fifo by sh
    (the parent must never hold a write fd, or EOF never reaches the reader)."""
    fifo = SCRATCH / "fifo-pace"
    if fifo.exists():
        fifo.unlink()
    os.mkfifo(fifo)
    cmd = [c.replace("@FIFO@", str(fifo)) for c in reader_cmd]
    t0 = time.monotonic()
    reader = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(0.3)
    wcmd = ["sh", "-c", writer_cmd.replace("@FIFO@", str(fifo))]
    writer = subprocess.Popen(wcmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
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
            "writer_rc": writer.returncode, "writer_stderr": werr}


# file arm
t0 = time.monotonic()
p = subprocess.run(["timeout", "-s", "KILL", "20", "pw-cat", "-p", str(TONE)],
                   capture_output=True, text=True)
results.append({"arm": "tone-file", "rc": p.returncode, "wall_s": round(time.monotonic() - t0, 2),
                "stderr": p.stderr, "stdout": p.stdout})

# fifo, instant dump
r = reader_writer(["timeout", "-s", "KILL", "25", "pw-cat", "-p", "@FIFO@"],
                  "cat " + str(TONE) + " > @FIFO@")
r["arm"] = "tone-fifo-instant-dump"
results.append(r)

# fifo, half-rate trickle: 1600 B every 0.2 s (41 chunks ~ 8.2 s of delivery for 4 s audio)
code = ("import sys,time\n"
        "d=open(sys.argv[1],'rb').read()\n"
        "f=open(sys.argv[2],'wb',buffering=0)\n"
        "for i in range(0,len(d),1600):\n"
        "    f.write(d[i:i+1600]); time.sleep(0.2)\n"
        "f.close()\n")
r = reader_writer(["timeout", "-s", "KILL", "25", "pw-cat", "-p", "@FIFO@"],
                  sys.executable + " -c " + repr(code) + " " + str(TONE) + " @FIFO@", timeout=30)
r["arm"] = "tone-fifo-trickle-1600B-0.2s"
results.append(r)

# fifo, raw mode -a
r = reader_writer(["timeout", "-s", "KILL", "25", "pw-cat", "-p", "-a", "--rate", "8000",
                   "--channels", "1", "--format", "s16", "@FIFO@"],
                  "cat " + str(TONE) + " > @FIFO@")
r["arm"] = "tone-fifo-raw"
results.append(r)

out = SCRATCH / "replay-pacing.json"
out.write_text(json.dumps(results, indent=1))
for r in results:
    print(f"{r['arm']:28s} rc={str(r['rc']):8s} wall={r['wall_s']:6} "
          f"err={(r.get('stderr') or '').strip()[:80]}")
print("wrote", out)
