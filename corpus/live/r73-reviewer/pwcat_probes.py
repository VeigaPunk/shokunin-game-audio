#!/usr/bin/env python3
"""r73 reviewer: pw-cat suffix/name-axis, --target 0 hang, and single-open probes."""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path.home() / "Projects/shokunin/audio-shokunin"
SCRATCH = REPO / "corpus/live/r73-reviewer"
HCOM = REPO / "corpus/live/round-66/pair_dec_hcom.wav"
results = []


def run(cmd, timeout=25, env=None):
    t0 = time.monotonic()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
        rc, err, out = p.returncode, p.stderr, p.stdout
    except subprocess.TimeoutExpired as e:
        rc = "TIMEOUT"
        err = (e.stderr or "") if isinstance(e.stderr, str) else ""
        out = ""
    return {"cmd": " ".join(cmd), "rc": rc, "wall_s": round(time.monotonic() - t0, 2),
            "stderr": err[-300:], "stdout": out[-300:]}


def with_writer(reader_cmd, writer_cmd, timeout=25):
    fifo = SCRATCH / "fifo-probe"
    if fifo.exists():
        fifo.unlink()
    os.mkfifo(fifo)
    t0 = time.monotonic()
    reader = subprocess.Popen([c.replace("@FIFO@", str(fifo)) for c in reader_cmd],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(0.3)
    w = subprocess.Popen(["sh", "-c", writer_cmd.replace("@FIFO@", str(fifo))],
                         stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    try:
        out, err = reader.communicate(timeout=timeout)
        rc = reader.returncode
    except subprocess.TimeoutExpired:
        reader.kill()
        out, err = reader.communicate()
        rc = "TIMEOUT"
    wall = round(time.monotonic() - t0, 2)
    w.wait(timeout=5)
    fifo.unlink()
    return {"rc": rc, "wall_s": wall, "stderr": err[-300:], "stdout": out[-200:]}


# 1. suffix/name axis: WAV bytes in a fifo NAMED *.txw (name-based decoders reject .txw)
r = with_writer(["timeout", "-s", "KILL", "20", "pw-cat", "-p", "@FIFO@"],
                f"cat {HCOM} > @FIFO@")
r["arm"] = "pwcat-fifo-named-unknown-suffix (fifo-probe: no suffix)"
results.append(r)
# named variant
fifo = SCRATCH / "probe-name.txw"
if fifo.exists():
    fifo.unlink()
os.mkfifo(fifo)
reader = subprocess.Popen(["timeout", "-s", "KILL", "20", "pw-cat", "-p", str(fifo)],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
time.sleep(0.3)
w = subprocess.Popen(["sh", "-c", f"cat {HCOM} > {fifo}"], stdout=subprocess.DEVNULL)
t0 = time.monotonic()
out, err = reader.communicate(timeout=25)
results.append({"arm": "pwcat-fifo-named-.txw", "rc": reader.returncode,
                "wall_s": round(time.monotonic() - t0, 2), "stderr": err[-300:], "stdout": out[-200:]})
w.wait(timeout=5)
fifo.unlink()

# 2. file named .txw with WAV bytes (name axis on the file arm)
named = SCRATCH / "hcom-copy.txw"
shutil.copyfile(HCOM, named)
r = run(["timeout", "-s", "KILL", "20", "pw-cat", "-p", str(named)])
r["arm"] = "pwcat-file-hcom-bytes-named-.txw"
results.append(r)

# 3. --target 0 (unlinked stream) hang, bounded by SIGKILL
r = run(["timeout", "-s", "KILL", "8", "pw-cat", "-p", "--target", "0", str(HCOM)], timeout=20)
r["arm"] = "pwcat-target0-file"
results.append(r)

# 4. writer holds the fifo open without closing (linger) after the bytes: does pw-cat exit?
fifo = SCRATCH / "fifo-linger"
if fifo.exists():
    fifo.unlink()
os.mkfifo(fifo)
reader = subprocess.Popen(["timeout", "-s", "KILL", "20", "pw-cat", "-p", str(fifo)],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
time.sleep(0.3)
w = subprocess.Popen(["sh", "-c", f"cat {HCOM} > {fifo}; sleep 5"],
                     stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
t0 = time.monotonic()
out, err = reader.communicate(timeout=25)
results.append({"arm": "pwcat-fifo-writer-linger-5s", "rc": reader.returncode,
                "wall_s": round(time.monotonic() - t0, 2), "stderr": err[-200:], "stdout": out[-100:]})
w.wait(timeout=10)
fifo.unlink()

out = SCRATCH / "pwcat-probes.json"
out.write_text(json.dumps(results, indent=1))
for r in results:
    print(f"{r['arm']:38s} rc={str(r['rc']):7s} wall={r['wall_s']:5} "
          f"err={(r.get('stderr') or '').strip()[:90]}")
print("wrote", out)
