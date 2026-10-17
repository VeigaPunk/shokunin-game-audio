#!/usr/bin/env python3
"""r74 reviewer — independent mpv transport runner (own implementation).

Usage: mpv_matrix.py <member> [<member> ...]
Runs mpv 4 ways {file, stdin_pipe, redirected_fd, fifo_path} per member,
bounded 15 s (SIGKILL), parses the --log-file surface, prints JSON lines.
Deliberately NOT importing corpus/fixtures/measure_audio.py: an independent
re-implementation so agreement is evidence, not shared code.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

TIMEOUT = 15


def feed(fifo, data, hold):
    try:
        with open(fifo, "wb") as fh:
            fh.write(data)
            fh.flush()
            time.sleep(hold)
    except OSError:
        pass


def parse_log(text):
    def g(pat):
        m = re.search(pat, text)
        return m.group(1) if m else None
    det = g(r"Detected file format: (\S+) \(libavformat\)")
    probe = re.search(r"Found '([^']+)' at score=(\d+)", text)
    seekfail = re.search(r"Seek failed \(([^)]*)\)", text)
    track = re.search(r"Audio\s+--aid=1\s+\(([^)]*)\)", text)
    verdict = re.search(r"finished playback, (.*)$", text, re.M)
    return {
        "lavf_detected": det,
        "lavf_probe": probe.group(1) if probe else None,
        "lavf_score": int(probe.group(2)) if probe else None,
        "stream_not_seekable": "Stream is not seekable" in text,
        "refresh_seek": "refresh seek to" in text,
        "seek_failed": seekfail.group(1) if seekfail else None,
        "audio_track": track.group(1) if track else None,
        "mpv_verdict": verdict.group(1).strip() if verdict else None,
        "demux_errors": len(re.findall(r"Error during demuxing", text)),
        "decode_errors": len(re.findall(r"Decoding error", text)),
        "eof_code": g(r"EOF code: (\d+)"),
    }


def run_leg(path, transport, data, hold):
    with tempfile.TemporaryDirectory(prefix="rv-mpv-") as tmp:
        log = Path(tmp) / "mpv.log"
        argv = ["mpv", "--no-config", "--vo=null", "--ao=null",
                "--audio-display=no", "--really-quiet", f"--log-file={log}"]
        blocked = None
        if transport == "file":
            argv.append(str(path))
            kw = {}
        elif transport == "stdin_pipe":
            argv.append("-")
            kw = {"input": data}
        elif transport == "redirected_fd":
            argv.append("-")
            kw = {"stdin": open(path, "rb")}
        else:
            fifo = Path(tmp) / path.name
            os.mkfifo(fifo)
            w = threading.Thread(target=feed, args=(fifo, data, hold), daemon=True)
            w.start()
            argv.append(str(fifo))
            kw = {}
        try:
            p = subprocess.run(argv, capture_output=True, timeout=TIMEOUT, **kw)
            code = p.returncode
        except subprocess.TimeoutExpired:
            code, blocked = None, f"blocked >{TIMEOUT}s"
        finally:
            if transport == "redirected_fd":
                kw["stdin"].close()
            if transport == "fifo_path":
                w.join(timeout=hold + 5)
        text = log.read_text(errors="replace") if log.exists() else ""
        leg = {"transport": transport, "exit_code": code,
               "blocked": blocked}
        leg.update(parse_log(text))
        return leg


def main():
    hold = 1.0
    out = []
    for name in sys.argv[1:]:
        path = Path(name).resolve()
        data = path.read_bytes()
        legs = {}
        for t in ("file", "stdin_pipe", "redirected_fd", "fifo_path"):
            legs[t] = run_leg(path, t, data, hold)
        groups = {}
        for t in ("file", "stdin_pipe", "redirected_fd", "fifo_path"):
            a = legs[t]
            sig = (a["exit_code"], a["lavf_detected"], a["seek_failed"])
            groups.setdefault(sig, []).append(t)
        print(json.dumps({"member": name, "legs": legs,
                          "fork": len(groups) > 1,
                          "groups": [{"transports": v, "verdict": list(k)}
                                     for k, v in groups.items()]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
