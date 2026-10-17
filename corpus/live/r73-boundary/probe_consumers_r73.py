#!/usr/bin/env python3
"""r73 BOUNDARY scratch arm — consumer matrix (pw-cat + mpv) over the member corpus.

Scratch only (corpus/live/r73-boundary/), NOT tracked evidence. Mirrors the r73
MOVE `--probe-consumers-r73` shape: {pw-cat, mpv} x {file, fifo} x members.
Receipts: runs/<UTCstamp>-consumers-r73/{measurements.json,verdicts.json}.
verdicts.json is the replay-stable core (no walls/timestamps); measurements.json
adds wall_s, tool/daemon snapshot, member hashes.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

SCRATCH = Path(__file__).resolve().parent
ROOT = SCRATCH.parents[2]  # corpus/live/r73-boundary -> repo root
RUNS = SCRATCH / "runs"
LOGS = SCRATCH / "logs"
FIFODIR = LOGS / "fifos"

ARM_TIMEOUT = 20  # seconds, wrapped by timeout -s KILL

MEMBERS = [
    ("dec_act", "corpus/live/round-66/pair_dec_act.wav"),
    ("dec_hcom", "corpus/live/round-66/pair_dec_hcom.wav"),
    ("lengate_gsrt_25", "corpus/live/round-66/pair_lengate_gsrt_25.wav"),
    ("posttable_nomatch", "corpus/live/round-68/posttable_nomatch.wav"),
    ("txw_piperefuse", "corpus/live/round-68/txw_piperefuse.wav"),
    ("extsuffix_wav", "corpus/live/round-69/extsuffix_nomatch.wav"),
    ("extsuffix_bin", "corpus/live/round-69/extsuffix_nomatch.bin"),
    ("extsuffix_txw", "corpus/live/round-69/extsuffix_nomatch.txw"),
    ("extsuffix_f32", "corpus/live/round-69/extsuffix_nomatch.f32"),
    ("extsuffix_snd", "corpus/live/round-69/extsuffix_nomatch.snd"),
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def run_cmd(cmd, timeout_s):
    t0 = time.monotonic()
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           timeout=timeout_s + 5)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        rc, out, err = 999, e.stdout or b"", e.stderr or b""
    return {"rc": rc, "wall_s": round(time.monotonic() - t0, 3),
            "stdout": out.decode("utf-8", "replace"),
            "stderr": err.decode("utf-8", "replace")}


def norm_pwcat(text, member_abs, fifo_abs=None):
    text = text.replace(str(member_abs), "<input>")
    if fifo_abs:
        text = text.replace(str(fifo_abs), "<fifo>")
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    return lines[:4]


def pwcat_file(member):
    r = run_cmd(["timeout", "-s", "KILL", str(ARM_TIMEOUT), "pw-cat", "-p",
                 str(member)], ARM_TIMEOUT)
    return {"rc": r["rc"], "wall_s": r["wall_s"],
            "stderr_norm": norm_pwcat(r["stderr"], member)}


def make_fifo(name):
    FIFODIR.mkdir(parents=True, exist_ok=True)
    f = FIFODIR / name
    if f.exists():
        f.unlink()
    os.mkfifo(f, 0o600)
    return f


def writer_cmd(script):
    return ["timeout", "-s", "KILL", str(ARM_TIMEOUT), "sh", "-c", script]


def pwcat_fifo(member, writer_script=None):
    fifo = make_fifo(member.name)
    reader = subprocess.Popen(["timeout", "-s", "KILL", str(ARM_TIMEOUT),
                               "pw-cat", "-p", str(fifo)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(0.35)
    script = writer_script or f"cat {member} > {fifo}"
    wr = run_cmd(writer_cmd(script), ARM_TIMEOUT)
    t0 = time.monotonic()
    try:
        out, err = reader.communicate(timeout=ARM_TIMEOUT + 5)
        rc = reader.returncode
    except subprocess.TimeoutExpired:
        reader.kill()
        out, err = reader.communicate()
        rc = 999
    wall = round(time.monotonic() - t0 + 0.35, 3)
    if fifo.exists():
        fifo.unlink()
    return {"rc": rc, "wall_s": wall, "writer_rc": wr["rc"],
            "stderr_norm": norm_pwcat(err.decode("utf-8", "replace"), member, fifo)}


def parse_mpv_log(logpath):
    txt = logpath.read_text(encoding="utf-8", errors="replace")
    v = {"detected": None, "not_seekable": "Stream is not seekable." in txt,
         "refresh_seek": "refresh seek to 0.000000" in txt,
         "seek_failed_eperm": "Seek failed (Operation not permitted)" in txt,
         "audio_track": None, "finished": None, "reason": None,
         "eof_reached": "EOF reached." in txt}
    m = re.search(r"\[lavf\] Found '([^']+)' at score=(\d+) size=(\d+)", txt)
    if m:
        v["detected"] = {"fmt": m.group(1), "score": int(m.group(2)),
                         "size": int(m.group(3))}
    m = re.search(r"● Audio\s+--aid=1\s+\(([^)]+)\)", txt)
    if m:
        v["audio_track"] = m.group(1)
    m = re.search(r"finished playback, ([a-z ]+) \(reason (\d+)\)", txt)
    if m:
        v["finished"] = m.group(1).strip()
        v["reason"] = int(m.group(2))
    return v


def mpv_file(member, tag):
    log = LOGS / f"r73-mpv-file-{tag}.log"
    r = run_cmd(["timeout", "-s", "KILL", str(ARM_TIMEOUT), "mpv", "--no-config",
                 "--vo=null", "--ao=null", "--audio-display=no", "--really-quiet",
                 f"--log-file={log}", str(member)], ARM_TIMEOUT)
    return {"rc": r["rc"], "wall_s": r["wall_s"], **parse_mpv_log(log)}


def mpv_fifo(member, tag, writer_script=None):
    fifo = make_fifo(member.name)
    log = LOGS / f"r73-mpv-fifo-{tag}.log"
    mpv = subprocess.Popen(["timeout", "-s", "KILL", str(ARM_TIMEOUT), "mpv",
                            "--no-config", "--vo=null", "--ao=null",
                            "--audio-display=no", "--really-quiet",
                            f"--log-file={log}", str(fifo)],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(0.35)
    script = writer_script or f"cat {member} > {fifo}"
    wr = run_cmd(writer_cmd(script), ARM_TIMEOUT)
    t0 = time.monotonic()
    try:
        mpv.communicate(timeout=ARM_TIMEOUT + 5)
        rc = mpv.returncode
    except subprocess.TimeoutExpired:
        mpv.kill()
        mpv.communicate()
        rc = 999
    wall = round(time.monotonic() - t0 + 0.35, 3)
    if fifo.exists():
        fifo.unlink()
    return {"rc": rc, "wall_s": wall, "writer_rc": wr["rc"],
            **parse_mpv_log(log)}


def tools_snapshot():
    def v(cmd):
        r = run_cmd(cmd, 10)
        return (r["stdout"] + r["stderr"]).strip().splitlines()
    pids = {}
    for name in ("pipewire", "pipewire-pulse", "wireplumber"):
        r = run_cmd(["pgrep", "-a", name], 10)
        pids[name] = r["stdout"].strip().splitlines()
    return {"pw-cat": v(["pw-cat", "--version"]),
            "mpv": v(["mpv", "--version"])[:2],
            "daemon": pids}


def main():
    stamp = time.strftime("%Y%m%dT%H%M%S", time.gmtime()) + f"{time.time()%1:.9f}"[1:10]
    rundir = RUNS / f"{stamp}Z-consumers-r73"
    rundir.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)

    cells = {}
    for tag, rel in MEMBERS:
        member = (ROOT / rel).resolve()
        cells[f"pwcat_file:{tag}"] = pwcat_file(member)
        cells[f"pwcat_fifo:{tag}"] = pwcat_fifo(member)
        cells[f"mpv_file:{tag}"] = mpv_file(member, tag)
        cells[f"mpv_fifo:{tag}"] = mpv_fifo(member, tag)
        print(f"[{tag}] done", flush=True)

    verdicts = {"mode": "probe-consumers-r73", "seat": "boundary",
                "corpus_root": "<repo>/corpus/live",
                "members": {tag: {"path": "<repo>/" + rel,
                                  "sha256": sha256(ROOT / rel),
                                  "bytes": (ROOT / rel).stat().st_size}
                            for tag, rel in MEMBERS},
                "cells": {k: {kk: vv for kk, vv in v.items() if kk != "wall_s"}
                          for k, v in sorted(cells.items())}}
    measurements = dict(verdicts)
    measurements["host"] = os.uname().nodename
    measurements["timestamp_utc"] = stamp
    measurements["tools"] = tools_snapshot()
    measurements["cells"] = dict(sorted(cells.items()))

    (rundir / "measurements.json").write_text(
        json.dumps(measurements, indent=1, sort_keys=True) + "\n")
    (rundir / "verdicts.json").write_text(
        json.dumps(verdicts, indent=1, sort_keys=True) + "\n")
    print(f"rundir: {rundir}")
    print(f"verdicts sha256: {sha256(rundir / 'verdicts.json')}")


if __name__ == "__main__":
    sys.exit(main())
