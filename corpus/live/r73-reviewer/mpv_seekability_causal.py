#!/usr/bin/env python3
"""r73 reviewer: causal test of the mpv inverted-seekability fork.

Hypothesis (frontier (c), mechanism *inferred* there): the hcom member's mpv
file/fifo fork is caused by mpv's refresh-seek — a seekable stream triggers it
and the seek is refused (EPERM), a non-seekable stream skips it and decodes.

Direct test: flip seekability with mpv's own --force-seekable flag on both arms.
  file + --force-seekable=no  -> if hypothesis holds: no refresh seek -> rc=0
  fifo + --force-seekable=yes -> if hypothesis holds: refresh seek -> rc=2 EPERM
"""
import json
import os
import subprocess
import time
from pathlib import Path

REPO = Path.home() / "Projects/shokunin/audio-shokunin"
SCRATCH = REPO / "corpus/live/r73-reviewer"
MEMBER = REPO / "corpus/live/round-66/pair_dec_hcom.wav"
results = []

BASE = ["--no-config", "--vo=null", "--ao=null", "--audio-display=no", "--really-quiet"]


def run_mpv(label, target, extra, transport):
    log = SCRATCH / f"mpv-force-{label}.log"
    if transport == "fifo":
        fifo = SCRATCH / "fifo-mpv-force"
        if fifo.exists():
            fifo.unlink()
        os.mkfifo(fifo)
        target = str(fifo)
    cmd = ["timeout", "-s", "KILL", "15", "mpv", *BASE, *extra,
           f"--log-file={log}", str(target)]
    t0 = time.monotonic()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if transport == "fifo":
        time.sleep(0.3)
        w = subprocess.Popen(["sh", "-c", f"cat {MEMBER} > {target}"])
    try:
        out, err = p.communicate(timeout=20)
        rc, killed = p.returncode, False
    except subprocess.TimeoutExpired:
        p.kill()
        out, err = p.communicate()
        rc, killed = "TIMEOUT", True
    if transport == "fifo":
        w.wait(timeout=5)
        Path(target).unlink()
    logtext = log.read_text(errors="replace")
    marks = [ln.split("] ", 1)[-1] for ln in logtext.splitlines()
             if any(k in ln for k in ("refresh seek", "Seek failed", "Stream is not seekable",
                                      "finished playback", "Detected file format"))]
    return {"label": label, "transport": transport, "extra": extra, "rc": rc,
            "timeout": killed, "wall_s": round(time.monotonic() - t0, 2),
            "marks": marks, "log": str(log.relative_to(REPO))}


results.append(run_mpv("file-default", MEMBER, [], "file"))
results.append(run_mpv("file-force-seekable-no", MEMBER, ["--force-seekable=no"], "file"))
results.append(run_mpv("fifo-default", MEMBER, [], "fifo"))
results.append(run_mpv("fifo-force-seekable-yes", MEMBER, ["--force-seekable=yes"], "fifo"))
results.append(run_mpv("file-force-seekable-no-2x", MEMBER, ["--force-seekable=no"], "file"))

out = SCRATCH / "mpv-seekability-causal.json"
out.write_text(json.dumps(results, indent=1))
for r in results:
    print(f"{r['label']:26s} rc={str(r['rc']):6s} wall={r['wall_s']:5}")
    for m in r["marks"]:
        print(f"      {m}")
print("wrote", out)
