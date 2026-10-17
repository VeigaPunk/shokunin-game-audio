#!/usr/bin/env python3
"""r73 reviewer: independent 9-member x {file,fifo} consumer matrix (pw-cat + mpv).

Protocol matches the fixture's landed transport protocol where it exists:
one-shot writer feed, writer holds the fifo open 1.0 s after the bytes (the
canonical `fifo_writer_hold_s()` value), 15 s SIGKILL arm bound.
Writes only inside corpus/live/r73-reviewer/.
"""
import json
import os
import re
import tempfile
import subprocess
import sys
import time
from pathlib import Path

REPO = Path.home() / "Projects/shokunin/audio-shokunin"
SCRATCH = REPO / "corpus/live/r73-reviewer"
HOLD = 1.0
ARM_TIMEOUT = 15

MEMBERS = {
    "posttable_nomatch": "corpus/live/round-68/posttable_nomatch.wav",
    "txw_piperefuse": "corpus/live/round-68/txw_piperefuse.wav",
    "dec_act": "corpus/live/round-66/pair_dec_act.wav",
    "dec_hcom": "corpus/live/round-66/pair_dec_hcom.wav",
    "extsuffix_wav": "corpus/live/round-69/extsuffix_nomatch.wav",
    "extsuffix_bin": "corpus/live/round-69/extsuffix_nomatch.bin",
    "extsuffix_txw": "corpus/live/round-69/extsuffix_nomatch.txw",
    "extsuffix_f32": "corpus/live/round-69/extsuffix_nomatch.f32",
    "extsuffix_snd": "corpus/live/round-69/extsuffix_nomatch.snd",
}

WRITER = SCRATCH / "matrix_writer.py"
WRITER.write_text(
    "import sys, time\n"
    "path, fifo, hold = sys.argv[1], sys.argv[2], float(sys.argv[3])\n"
    "f = open(fifo, 'wb', buffering=0)\n"
    "f.write(open(path, 'rb').read())\n"
    "time.sleep(hold)\n"
    "f.close()\n")

results = {}


def norm_paths(text, member_path):
    t = text.replace(str(member_path), "<input>")
    t = re.sub(r"/[^\s\"']*(fifo|member)[^\s\"']*", "<input>", t)
    return t.strip()


def pwcat_leg(member, rel, transport):
    path = REPO / rel
    if transport == "file":
        cmd = ["timeout", "-s", "KILL", str(ARM_TIMEOUT), "pw-cat", "-p", str(path)]
        t0 = time.monotonic()
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=ARM_TIMEOUT + 10)
            rc, err, killed = p.returncode, p.stderr, False
        except subprocess.TimeoutExpired:
            rc, err, killed = "TIMEOUT", "", True
        wall = round(time.monotonic() - t0, 2)
        return {"rc": rc, "killed": killed, "wall_s": wall,
                "reason": norm_paths(err.splitlines()[-2] if len(err.splitlines()) > 1
                                     else err, path),
                "stderr_tail": norm_paths(err[-200:], path)}
    naming = os.environ.get("R73_FIFO_NAMING", "plain")
    tmpdir = tempfile.mkdtemp(prefix="r73rev-fifo-")
    fifo = Path(tmpdir) / (Path(rel).name if naming == "fixture" else "matrix-fifo")
    os.mkfifo(fifo)
    t0 = time.monotonic()
    reader = subprocess.Popen(["timeout", "-s", "KILL", str(ARM_TIMEOUT), "pw-cat", "-p", str(fifo)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(0.3)
    w = subprocess.Popen([sys.executable, str(WRITER), str(path), str(fifo), str(HOLD)],
                         stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    try:
        out, err = reader.communicate(timeout=ARM_TIMEOUT + 10)
        rc, killed = reader.returncode, False
    except subprocess.TimeoutExpired:
        reader.kill()
        out, err = reader.communicate()
        rc, killed = "TIMEOUT", True
    wall = round(time.monotonic() - t0, 2)
    try:
        w.wait(timeout=5)
    except subprocess.TimeoutExpired:
        w.kill()
    fifo.unlink()
    os.rmdir(tmpdir)
    return {"rc": rc, "killed": killed, "wall_s": wall, "fifo_name": fifo.name,
            "reason": norm_paths(err.splitlines()[-2] if len(err.splitlines()) > 1 else err, path),
            "stderr_tail": norm_paths(err[-200:], path)}


def mpv_leg(member, rel, transport):
    path = REPO / rel
    log = SCRATCH / f"matrix-mpv-{transport}-{member}.log"
    base = ["--no-config", "--vo=null", "--ao=null", "--audio-display=no", "--really-quiet"]
    if transport == "file":
        cmd = ["timeout", "-s", "KILL", str(ARM_TIMEOUT), "mpv", *base,
               f"--log-file={log}", str(path)]
        t0 = time.monotonic()
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=ARM_TIMEOUT + 10)
            rc, killed = p.returncode, False
        except subprocess.TimeoutExpired:
            rc, killed = "TIMEOUT", True
        wall = round(time.monotonic() - t0, 2)
    else:
        naming = os.environ.get("R73_FIFO_NAMING", "plain")
        tmpdir = tempfile.mkdtemp(prefix="r73rev-fifompv-")
        fifo = Path(tmpdir) / (Path(rel).name if naming == "fixture" else "matrix-fifo-mpv")
        os.mkfifo(fifo)
        t0 = time.monotonic()
        reader = subprocess.Popen(["timeout", "-s", "KILL", str(ARM_TIMEOUT), "mpv", *base,
                                   f"--log-file={log}", str(fifo)],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(0.3)
        w = subprocess.Popen([sys.executable, str(WRITER), str(path), str(fifo), str(HOLD)],
                             stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        try:
            out, err = reader.communicate(timeout=ARM_TIMEOUT + 10)
            rc, killed = reader.returncode, False
        except subprocess.TimeoutExpired:
            reader.kill()
            out, err = reader.communicate()
            rc, killed = "TIMEOUT", True
        wall = round(time.monotonic() - t0, 2)
        try:
            w.wait(timeout=5)
        except subprocess.TimeoutExpired:
            w.kill()
        fifo.unlink()
        os.rmdir(tmpdir)
    text = log.read_text(errors="replace") if log.exists() else ""
    def pick(pat):
        m = re.search(pat, text)
        return m.group(1) if m else None
    return {"rc": rc, "killed": killed, "wall_s": wall,
            "detected_format": pick(r"Detected file format: (\S+)"),
            "not_seekable": "Stream is not seekable." in text,
            "seek_failed": "Seek failed (Operation not permitted)" in text,
            "finished": pick(r"finished playback, (.+?) \(reason (\d+)\)"),
            "log": str(log.relative_to(REPO))}


only = sys.argv[1] if len(sys.argv) > 1 else None
out_path = SCRATCH / os.environ.get("R73_MATRIX_OUT", "my-matrix.json")
if out_path.exists():
    results = json.loads(out_path.read_text())
for member, rel in MEMBERS.items():
    if only and member != only:
        continue
    results.setdefault(member, {})
    for consumer in ("pwcat", "mpv"):
        for transport in ("file", "fifo"):
            key = f"{consumer}-{transport}"
            if key in results[member]:
                continue
            r = pwcat_leg(member, rel, transport) if consumer == "pwcat" else mpv_leg(member, rel, transport)
            results[member][key] = r
            out_path.write_text(json.dumps(results, indent=1))
            extra = ""
            if consumer == "mpv":
                extra = f"fmt={r.get('detected_format')} notseek={r.get('not_seekable')} seekfail={r.get('seek_failed')} fin={r.get('finished')}"
            print(f"{member:20s} {key:11s} rc={str(r['rc']):7s} wall={r['wall_s']:5} "
                  f"reason={(r.get('reason') or '')[:60]} {extra}", flush=True)
print("wrote", out_path)
