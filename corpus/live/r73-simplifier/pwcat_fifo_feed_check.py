#!/usr/bin/env python3
"""Compatibility check: run pw-cat against the fixture's OWN writer protocol
(fifo_feed + fifo_writer_hold_s, measure_audio.py:285-315) instead of a raw
`cat`, and record rc/wall. Read-only; fifo lives in /tmp.
"""
import importlib.util, os, subprocess, tempfile, threading, time
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
spec = importlib.util.spec_from_file_location("measure_audio", REPO / "corpus/fixtures/measure_audio.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

member = mod.ROOT / "live" / "round-66" / "pair_dec_hcom.wav"
data = member.read_bytes()
hold = mod.fifo_writer_hold_s()

with tempfile.TemporaryDirectory(prefix="r73sim-fifofeed-") as tmp:
    fifo = Path(tmp) / member.name
    os.mkfifo(fifo)
    w = threading.Thread(target=mod.fifo_feed, args=(fifo, data, hold), daemon=True)
    w.start()
    t0 = time.monotonic()
    proc = subprocess.run(["timeout", "-s", "KILL", "15", "pw-cat", "-p", str(fifo)],
                          capture_output=True)
    wall = time.monotonic() - t0
    w.join(timeout=hold + 5)
    print(f"pw-cat via fixture fifo_feed: rc={proc.returncode} wall_s={wall:.2f} "
          f"hold_s={hold} writer_alive={w.is_alive()} "
          f"stderr={proc.stderr.decode(errors='replace')!r}")
