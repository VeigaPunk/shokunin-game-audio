#!/usr/bin/env python3
"""r73 reviewer: raw-output replay stability for the two consumer legs.

Runs each leg twice and diffs the raw text, so the landed arm's normalizer
requirement is measured rather than assumed (r71 `_tail` strips ffmpeg @0x tags
and sox backtick paths only).
"""
import difflib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path.home() / "Projects/shokunin/audio-shokunin"
SCRATCH = REPO / "corpus/live/r73-reviewer"
HCOM = REPO / "corpus/live/round-66/pair_dec_hcom.wav"
res = {}


def pwcat_file():
    p = subprocess.run(["timeout", "-s", "KILL", "15", "pw-cat", "-p", str(HCOM)],
                       capture_output=True, text=True)
    return p.returncode, p.stderr


def pwcat_fifo():
    fifo = SCRATCH / "stab-fifo"
    if fifo.exists():
        fifo.unlink()
    os.mkfifo(fifo)
    r = subprocess.Popen(["timeout", "-s", "KILL", "15", "pw-cat", "-p", str(fifo)],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(0.2)
    w = subprocess.Popen(["sh", "-c", f"cat {HCOM} > {fifo}"])
    out, err = r.communicate(timeout=20)
    w.wait(timeout=5)
    fifo.unlink()
    return r.returncode, err


def mpv_file(tag):
    log = SCRATCH / f"stab-mpv-file-{tag}.log"
    p = subprocess.run(["timeout", "-s", "KILL", "15", "mpv", "--no-config", "--vo=null",
                        "--ao=null", "--audio-display=no", "--really-quiet",
                        f"--log-file={log}", str(HCOM)], capture_output=True, text=True)
    return p.returncode, log.read_text(errors="replace")


def mpv_fifo(tag):
    fifo = SCRATCH / "stab-fifo-mpv"
    if fifo.exists():
        fifo.unlink()
    os.mkfifo(fifo)
    log = SCRATCH / f"stab-mpv-fifo-{tag}.log"
    r = subprocess.Popen(["timeout", "-s", "KILL", "15", "mpv", "--no-config", "--vo=null",
                          "--ao=null", "--audio-display=no", "--really-quiet",
                          f"--log-file={log}", str(fifo)],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(0.2)
    w = subprocess.Popen(["sh", "-c", f"cat {HCOM} > {fifo}"])
    r.communicate(timeout=20)
    w.wait(timeout=5)
    fifo.unlink()
    return r.returncode, log.read_text(errors="replace")


def compare(a, b, label):
    if a == b:
        res[label] = {"identical_raw": True}
        return
    la, lb = a.splitlines(), b.splitlines()
    diff = [l for l in difflib.unified_diff(la, lb, lineterm="") if l[:1] in "+-" and l[:3] not in ("+++", "---")]
    # classify: timestamp-only, path-only, address-only, other
    def cls(line):
        s = line[1:]
        s2 = re.sub(r"\[\s*[0-9]+\.[0-9]+\]", "[T]", s)
        s2 = re.sub(r"0x[0-9a-f]+", "0xADDR", s2)
        s2 = re.sub(r"/[^\s\"']+", "<path>", s2)
        return s2
    ts = sum(1 for l in diff if cls(l) == cls(l) and re.search(r"\[\s*[0-9]+\.[0-9]+\]", l))
    res[label] = {"identical_raw": False, "diff_lines": len(diff),
                  "timestamp_lines": ts, "sample": diff[:4]}


rc1, e1 = pwcat_file()
rc2, e2 = pwcat_file()
compare(e1, e2, "pwcat-file-stderr")
res["pwcat-file-stderr"]["rc"] = [rc1, rc2]

rc1, e1 = pwcat_fifo()
rc2, e2 = pwcat_fifo()
compare(e1, e2, "pwcat-fifo-stderr")
res["pwcat-fifo-stderr"]["rc"] = [rc1, rc2]

rc1, l1 = mpv_file("a")
rc2, l2 = mpv_file("b")
compare(l1, l2, "mpv-file-log")
res["mpv-file-log"]["rc"] = [rc1, rc2]

rc1, l1 = mpv_fifo("a")
rc2, l2 = mpv_fifo("b")
compare(l1, l2, "mpv-fifo-log")
res["mpv-fifo-log"]["rc"] = [rc1, rc2]

out = SCRATCH / "text-stability.json"
out.write_text(json.dumps(res, indent=1))
print(json.dumps(res, indent=1)[:2400])
print("wrote", out)
