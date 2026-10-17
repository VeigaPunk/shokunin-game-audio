#!/usr/bin/env python3
"""r73-scout: independent mpv consumer matrix (4 arms x 11 members).

Arms: file (named+seekable), fifo_path (named+unseekable),
stdin_pipe (anonymous+unseekable), stdin_file (anonymous+seekable).
Claim surface: mpv forks on seekability (file->rc2 / fifo->rc0) for the
hcom member; detection is content-only (libavformat probe).
"""
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
OUT = ROOT / "corpus" / "live" / "r73-scout"
LOGS = OUT / "logs" / "mpv"
RUNS = OUT / "runs"
FIFOS = OUT / "fifos"
for d in (LOGS, RUNS, FIFOS):
    d.mkdir(parents=True, exist_ok=True)

ARM_TIMEOUT_S = 15
MPV_OPTS = ["--no-config", "--vo=null", "--ao=null", "--audio-display=no",
            "--really-quiet"]

MEMBERS = {
    "posttable_nomatch": ROOT / "corpus/live/round-68/posttable_nomatch.wav",
    "txw_piperefuse": ROOT / "corpus/live/round-68/txw_piperefuse.wav",
    "dec_act": ROOT / "corpus/live/round-66/pair_dec_act.wav",
    "dec_hcom": ROOT / "corpus/live/round-66/pair_dec_hcom.wav",
    "extsuffix_wav": ROOT / "corpus/live/round-69/extsuffix_nomatch.wav",
    "extsuffix_bin": ROOT / "corpus/live/round-69/extsuffix_nomatch.bin",
    "extsuffix_txw": ROOT / "corpus/live/round-69/extsuffix_nomatch.txw",
    "extsuffix_f32": ROOT / "corpus/live/round-69/extsuffix_nomatch.f32",
    "extsuffix_snd": ROOT / "corpus/live/round-69/extsuffix_nomatch.snd",
    "lengate_gsrt_25": ROOT / "corpus/live/round-66/pair_lengate_gsrt_25.wav",
    "tone4s": OUT / "tone4s.wav",
}

KEY_PATTERNS = (
    "Found '", "avformat_find_stream_info() finished", "Stream is not seekable",
    "refresh seek to", "execute seek", "Seek failed", "using bullshit",
    "finished playback", "Exiting...", "Audio  --aid",
)


def key_lines(log_text):
    out = []
    for line in log_text.splitlines():
        if any(p in line for p in KEY_PATTERNS):
            # strip the [ time][lvl][mod] prefix, keep message
            msg = line.split("] ", 2)[-1] if line.startswith("[") else line
            out.append(msg)
    return out


def unblock_writer(fifo, data_len):
    """If the writer thread is still blocked in open(), a reader-open with
    O_NONBLOCK lets it proceed (then its write fails EPIPE harmlessly)."""
    try:
        fd = os.open(fifo, os.O_RDONLY | os.O_NONBLOCK)
        os.close(fd)
    except OSError:
        pass


def writer_thread(fifo, data):
    try:
        with open(fifo, "wb", buffering=0) as fh:
            fh.write(data)
    except OSError:
        pass


def run_leg(member, arm):
    path = MEMBERS[member]
    data = path.read_bytes()
    log = LOGS / f"{member}__{arm}.log"
    argv = ["timeout", "-s", "KILL", str(ARM_TIMEOUT_S), "mpv"] + MPV_OPTS + \
           [f"--log-file={log}"]
    fifo = None
    wthr = None
    stdin = None
    kwargs = {}
    if arm == "file":
        argv.append(str(path))
    elif arm == "fifo_path":
        fifo = FIFOS / f"{member}__{arm}.fifo"
        if fifo.exists():
            fifo.unlink()
        os.mkfifo(fifo)
        wthr = threading.Thread(target=writer_thread, args=(fifo, data), daemon=True)
        wthr.start()
        argv.append(str(fifo))
    elif arm == "stdin_pipe":
        argv.append("-")
        kwargs["input"] = data
    elif arm == "stdin_file":
        argv.append("-")
        stdin = open(path, "rb")
        kwargs["stdin"] = stdin
    else:
        raise ValueError(arm)
    t0 = time.monotonic()
    try:
        proc = subprocess.run(argv, capture_output=True, timeout=ARM_TIMEOUT_S + 5,
                              **kwargs)
        rc = proc.returncode
        err = proc.stderr.decode(errors="replace")
        blocked = None
    except subprocess.TimeoutExpired:
        rc, err, blocked = None, "", "blocked: no verdict within timeout"
    wall = time.monotonic() - t0
    if wthr is not None:
        wthr.join(timeout=1.0)
        if wthr.is_alive():
            unblock_writer(fifo, len(data))
            wthr.join(timeout=1.0)
        try:
            fifo.unlink()
        except OSError:
            pass
    if stdin is not None:
        stdin.close()
    text = log.read_text(errors="replace") if log.exists() else ""
    lines = key_lines(text)
    verdict = {
        "member": member, "arm": arm, "rc": rc, "wall_s": round(wall, 3),
        "blocked": blocked,
        "found": next((l for l in lines if "Found '" in l), None),
        "not_seekable": any("Stream is not seekable" in l for l in lines),
        "refresh_seek": next((l for l in lines if "refresh seek to" in l), None),
        "seek_failed": next((l for l in lines if "Seek failed" in l), None),
        "pcm_seek_hack": any("using bullshit" in l for l in lines),
        "playback": next((l for l in lines if "finished playback" in l), None),
        "track": next((l for l in lines if "Audio  --aid" in l), None),
        "log": str(log.relative_to(ROOT)),
        "stderr_tail": err.strip().splitlines()[-1] if err.strip() else "",
    }
    return verdict


def main():
    run_tag = sys.argv[1] if len(sys.argv) > 1 else "run1"
    arms = ("file", "fifo_path", "stdin_pipe", "stdin_file")
    cells = []
    for member in MEMBERS:
        for arm in arms:
            v = run_leg(member, arm)
            cells.append(v)
            print(f"{member:20s} {arm:11s} rc={v['rc']} wall={v['wall_s']:>6.3f} "
                  f"playback={v['playback']}")
    doc = {
        "probe": "mpv consumer matrix (r73-scout independent)",
        "tool": "mpv v0.41.0 / libavformat 63.1.101 (FFmpeg n9.0.1)",
        "arms": {"file": "named seekable", "fifo_path": "named unseekable",
                 "stdin_pipe": "anonymous unseekable", "stdin_file": "anonymous seekable"},
        "arm_timeout_s": ARM_TIMEOUT_S,
        "cells": cells,
    }
    out = RUNS / f"mpv-matrix-{run_tag}.json"
    out.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
