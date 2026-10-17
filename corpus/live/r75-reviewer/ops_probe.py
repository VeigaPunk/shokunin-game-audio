#!/usr/bin/env python3
"""r75 reviewer independent ops probe: writerless-fifo hang + kill semantics
for paplay / aplay / ffplay. Independent of the author harness; records raw
observations only. Protocol: SIGTERM first (1.0 s grace), then SIGKILL pgid."""
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SDL = {**os.environ, "SDL_AUDIODRIVER": "dummy"}


def probe(cmd, env=None, wait_s=3.0):
    """Spawn cmd on a writerless fifo; measure block, wchan, TERM, KILL."""
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            start_new_session=True, env=env)
    rec = {"cmd": " ".join(cmd)}
    t0 = time.monotonic()
    try:
        proc.wait(timeout=wait_s)
        rec.update(blocked=False, exit_code=proc.returncode,
                   waited_s=wait_s, wall_s=round(time.monotonic() - t0, 3))
        return rec
    except subprocess.TimeoutExpired:
        pass
    rec["blocked"] = True
    try:
        rec["wchan"] = Path(f"/proc/{proc.pid}/wchan").read_text().strip()
    except OSError:
        rec["wchan"] = None
    rec["state"] = None
    try:
        for ln in Path(f"/proc/{proc.pid}/status").read_text().splitlines():
            if ln.startswith("State:"):
                rec["state"] = ln.split(":", 1)[1].strip()
    except OSError:
        pass
    # SIGTERM grace
    t0 = time.monotonic()
    os.kill(proc.pid, signal.SIGTERM)
    try:
        proc.wait(timeout=1.0)
        rec.update(sigterm_immune=False, exit_code=proc.returncode,
                   sigterm_wall_s=round(time.monotonic() - t0, 3))
        return rec
    except subprocess.TimeoutExpired:
        rec["sigterm_immune"] = True
    # SIGKILL pgid
    os.killpg(proc.pid, signal.SIGKILL)
    proc.wait()
    rec.update(exit_code=proc.returncode,
               sigterm_wall_s=round(time.monotonic() - t0, 3))
    return rec


def main():
    out = {}
    with tempfile.TemporaryDirectory(prefix="r75rev-ops-") as tmp:
        for name, argv, env in (
            ("paplay", ["paplay", f"{tmp}/nowriter.wav"], None),
            ("aplay", ["aplay", f"{tmp}/nowriter.wav"], None),
            ("ffplay", ["ffplay", "-nodisp", "-autoexit", "-hide_banner",
                        "-loglevel", "warning", f"{tmp}/nowriter.wav"], SDL),
        ):
            fifo = Path(tmp) / "nowriter.wav"
            if fifo.exists():
                fifo.unlink()
            os.mkfifo(fifo)
            out[name] = probe(argv, env=env)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    sys.exit(main())
