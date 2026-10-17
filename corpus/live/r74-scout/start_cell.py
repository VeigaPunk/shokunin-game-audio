#!/usr/bin/env python3
"""r74-scout secondary cell (ii): mpv --start=N position fork.

Prediction: on a SEEKING member the file arm honours --start=N (plays the
tail); on a fifo (unseekable) mpv plays from 0 (or refuses) -> position
fork. Witness = decoded PCM byte count via --ao=pcm.
"""
import hashlib
import json
import os
import subprocess
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TONE = ROOT / "members" / "sweep_tone2s.wav"
FIFOS = ROOT / "fifos"
RAW = ROOT / "raw"
LOGS = ROOT / "logs"


def feed(fifo, data):
    with open(fifo, "wb") as fh:
        fh.write(data)


def leg(arm, start, decode=True):
    data = TONE.read_bytes()
    log = LOGS / ("start__%s__%s.log" % (arm, start))
    pcm = RAW / ("start__%s__%s.raw" % (arm, start))
    for p in (log, pcm):
        if p.exists():
            p.unlink()
    argv = ["mpv", "--no-config", "--vo=null", "--audio-display=no",
            "--really-quiet", "--ao=pcm", "--ao-pcm-file=%s" % pcm,
            "--ao-pcm-waveheader=no", "--start=%s" % start]
    if arm == "file":
        argv.append(str(TONE))
    else:
        fifo = FIFOS / "r74start.fifo"
        if fifo.exists():
            fifo.unlink()
        os.mkfifo(fifo)
        t = threading.Thread(target=feed, args=(fifo, data), daemon=True)
        t.start()
        argv.append(str(fifo))
    argv.append("--log-file=%s" % log)
    t0 = time.monotonic()
    try:
        p = subprocess.run(argv, capture_output=True, timeout=20)
        rc, to = p.returncode, False
    except subprocess.TimeoutExpired:
        rc, to = -9, True
    wall = time.monotonic() - t0
    text = log.read_text(errors="replace") if log.exists() else ""
    rec = {"arm": arm, "start": start, "rc": rc, "timed_out": to,
           "wall_s": round(wall, 3),
           "pcm_bytes": pcm.stat().st_size if pcm.exists() else 0,
           "seek_ok": "seek done" in text,
           "seek_failed": "Seek failed" in text,
           "not_seekable": "Stream is not seekable." in text,
           "seek_ignored": "Cannot seek" in text or "not seekable" in text,
           "input_bytes": len(data),
           "input_sha256": hashlib.sha256(data).hexdigest()}
    if arm == "fifo":
        t.join(timeout=2)
        try:
            fifo.unlink()
        except OSError:
            pass
    print(rec, flush=True)
    return rec


def main():
    if not TONE.exists():
        subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-f", "lavfi",
                        "-i", "sine=frequency=440:sample_rate=8000:"
                        "duration=2", str(TONE)], check=True)
    out = []
    for arm in ("file", "fifo"):
        for start in ("1", "0"):
            out.append(leg(arm, start))
    (ROOT / "runs" / "start-cell.json").write_text(
        json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
