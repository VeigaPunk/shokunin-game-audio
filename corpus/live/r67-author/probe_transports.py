#!/usr/bin/env python3
"""r67 scratch: transport matrix over the 10 tracked autodetect members + ui.wav.

Transports (the 2x2 of {named x seekable}):
  file          sox -V6 <path> -n stat
  stdin_pipe    sox -V6 - -n stat  with member bytes on a real pipe (unnamed, non-seekable)
  redirected_fd sox -V6 - -n stat  with stdin = the member's own fd (unnamed, seekable)
  fifo_path     sox -V6 <fifo> -n stat  one-shot writer feeds a named fifo (named, non-seekable)

Per arm: detected format, route (native|ffmpeg|none), exit, samples read,
last stderr line (ASLR-stripped, 160 chars per lane convention). Arms are
bounded: a sox still running after ARM_TIMEOUT s is killed and recorded as
verdict "timeout" (a blocked transport, not a silent hang of the runner).
"""
import json
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
FIFODIR = ROOT / "corpus" / "live" / "r67-author" / "fifo"
ARM_TIMEOUT = 10
MEMBERS = [
    "corpus/live/round-65/pair_preempt_act.wav",
    "corpus/live/round-65/pair_preempt_gsrt.wav",
    "corpus/live/round-65/pair_preempt_hcom.wav",
    "corpus/live/round-65/pair_preempt_both.wav",
    "corpus/live/round-66/pair_dec_hcom.wav",
    "corpus/live/round-66/pair_dec_act.wav",
    "corpus/live/round-66/pair_lengate_gsrt_24.wav",
    "corpus/live/round-66/pair_lengate_gsrt_25.wav",
    "corpus/live/round-66/pair_lengate_hcom_131.wav",
    "corpus/live/round-66/pair_lengate_hcom_132.wav",
    "corpus/artifacts/ui.wav",
]

DETECTED = re.compile(r"detected file format type `(\S+?)'")
SAMPLES = re.compile(r"Samples read:\s*(\d+)")
ADDR = re.compile(r" @ 0x[0-9a-f]+\]")


def error_class(err):
    """Normalized verdict error: text after the input-name close-quote on the
    last `sox FAIL` line; None when no FAIL line (decode succeeded)."""
    fails = [ln for ln in err.strip().splitlines() if "sox FAIL" in ln]
    if not fails:
        return None
    m = re.search(r"':\s*(.*)$", fails[-1])
    return m.group(1) if m else fails[-1]


def summarize(proc, input_arg=None):
    err = proc.stderr.decode(errors="replace")
    det = DETECTED.search(err)
    read = SAMPLES.search(err)
    route = ("ffmpeg" if (det and det.group(1) == "act") or "(ffmpeg)" in err
             else "native" if det else "none")
    tail = err.strip().splitlines()
    return {"detected": det.group(1) if det else None,
            "route": route,
            "exit": proc.returncode,
            "samples": int(read.group(1)) if read else None,
            "error": error_class(err),
            "stderr_tail": ADDR.sub("]", tail[-1])[-160:] if tail else ""}


def run_sox(args, **kw):
    try:
        return summarize(subprocess.run(args, capture_output=True,
                                        timeout=ARM_TIMEOUT, **kw))
    except subprocess.TimeoutExpired as exc:
        err = (exc.stderr or b"").decode(errors="replace")
        det = DETECTED.search(err)
        return {"detected": det.group(1) if det else None,
                "route": "ffmpeg" if (det and det.group(1) == "act") or "(ffmpeg)" in err else "native" if det else "none",
                "exit": None, "samples": None, "error": "blocked (no verdict)",
                "stderr_tail": f"BLOCKED: no verdict within {ARM_TIMEOUT}s (arm killed)"}


def arm_file(path):
    return run_sox(["sox", "-V6", str(path), "-n", "stat"])


def arm_stdin_pipe(path):
    return run_sox(["sox", "-V6", "-", "-n", "stat"], input=path.read_bytes())


def arm_redirected_fd(path):
    with path.open("rb") as fh:
        return run_sox(["sox", "-V6", "-", "-n", "stat"], stdin=fh)


def arm_fifo_path(path):
    FIFODIR.mkdir(parents=True, exist_ok=True)
    fifo = FIFODIR / path.name
    if fifo.exists():
        fifo.unlink()
    os.mkfifo(fifo)
    data = path.read_bytes()

    def feed():
        try:
            with fifo.open("wb") as fh:
                fh.write(data)
                fh.flush()
                # linger: the ffmpeg bridge re-opens the fifo by name (open#2);
                # holding the writer attached makes that open succeed instead
                # of blocking. Native readers simply see EOF when we close.
                time.sleep(1.0)
        except OSError:
            pass

    t = threading.Thread(target=feed, daemon=True)
    t.start()
    try:
        return run_sox(["sox", "-V6", str(fifo), "-n", "stat"])
    finally:
        t.join(timeout=5)
        fifo.unlink()


def verdict_sig(a):
    return (a["detected"], a["route"], a["exit"], a["samples"], a["error"])


def main():
    out = {}
    for rel in MEMBERS:
        path = ROOT / rel
        arms = {
            "file": arm_file(path),
            "stdin_pipe": arm_stdin_pipe(path),
            "redirected_fd": arm_redirected_fd(path),
            "fifo_path": arm_fifo_path(path),
        }
        sigs = {t: verdict_sig(a) for t, a in arms.items()}
        fork = len(set(sigs.values())) > 1
        out[rel] = {"arms": arms, "fork": fork}
        print(f"== {rel}  fork={fork}", flush=True)
        for t, a in arms.items():
            print(f"   {t:14s} det={str(a['detected']):9} route={a['route']:6} "
                  f"exit={a['exit']} samples={a['samples']}  err={a['error']}",
                  flush=True)
    dest = (sys.argv[1] if len(sys.argv) > 1 else
            str(ROOT / "corpus" / "live" / "r67-author" / "transport-matrix.json"))
    Path(dest).write_text(json.dumps(out, indent=2) + "\n")


if __name__ == "__main__":
    main()
