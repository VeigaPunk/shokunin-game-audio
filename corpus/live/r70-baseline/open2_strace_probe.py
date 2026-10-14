#!/usr/bin/env python3
"""Mechanism probe: timestamp the ffmpeg bridge's open #2 on the fifo vs the
writer's detach, at hold={0, 0.05}. `strace -f -ttt -e trace=%file` follows the
sox->ffmpeg child; every openat() touching the fifo path is a *bridge-by-name*
open. Prints the ordered event list so the writer-attached-at-open-#2 predicate
is directly observable. Scratch only; does not feed the ledger.
"""
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import time

FIXTURE = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/round-66/pair_dec_act.wav")
DATA = FIXTURE.read_bytes()
HERE = Path(__file__).resolve().parent
OUT = HERE / "open2-strace.txt"


def probe(hold, label, fh):
    with tempfile.TemporaryDirectory(prefix=f"open2-{label}-") as tmp:
        fifo = Path(tmp) / FIXTURE.name
        os.mkfifo(fifo)
        marks = {}
        t0 = time.time()

        def writer():
            f = fifo.open("wb")
            marks["w_opened"] = time.time() - t0
            f.write(DATA)
            f.flush()
            if hold:
                time.sleep(hold)
            f.close()
            marks["w_closed"] = time.time() - t0

        w = threading.Thread(target=writer, daemon=True)
        w.start()
        timed_out = False
        try:
            proc = subprocess.run(
                ["strace", "-f", "-ttt", "-e", "trace=%file", "-o", "/dev/stderr",
                 "sox", "-V6", str(fifo), "-n", "stat"],
                capture_output=True, text=True, timeout=12)
            trace, rc = proc.stderr, proc.returncode
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            trace = (exc.stderr or b"").decode(errors="replace")
            rc = "TIMEOUT(12s)"
        w.join(timeout=12)
        opens = []
        for line in trace.splitlines():
            if str(fifo) in line and ("openat" in line or "open(" in line):
                fields = line.split()
                # strace -f -ttt: "<pid> <epoch.ts> <call> ..."
                ts = None
                for f in fields[:2]:
                    try:
                        v = float(f)
                    except ValueError:
                        continue
                    if v > 1e9:
                        ts = v
                        break
                opens.append((round(ts - t0, 4) if ts else -1.0,
                              line.strip()[:160]))
        fh.write(f"=== hold={hold} ({label}) — sox exit={rc} ===\n")
        for k, v in marks.items():
            fh.write(f"  writer.{k} @ {v:.4f}s\n")
        for ts, line in opens:
            fh.write(f"  open @ {ts:.4f}s  {line}\n")
        fh.write(f"  [open2-blocked>12s={timed_out}]\n\n")
        fh.flush()


if __name__ == "__main__":
    with OUT.open("w") as fh:
        probe(0.05, "hold-50ms", fh)
        probe(0.0, "hold-0", fh)
    print(OUT.read_text())
