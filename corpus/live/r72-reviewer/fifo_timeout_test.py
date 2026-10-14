#!/usr/bin/env python3
"""r72-reviewer: error-path test of the landed arm's SIGALRM bound.

The landed `_sndfile_leg` arms a 15 s SIGALRM around every transport leg.
This test drives the leg's *named* branch at a fifo with NO writer attached
(the failure mode my boundary probe C measured as an unbounded block for a
bare sf_open). It measures whether the alarm actually bounds the leg.

Run: timeout 60 python3 fifo_timeout_test.py
"""
import os, sys, tempfile, time

sys.path.insert(0, os.path.abspath("corpus/fixtures"))
import measure_audio as M  # noqa: E402

tmp = tempfile.mkdtemp(prefix="r72-reviewer-timeout-")
fifo = os.path.join(tmp, "pair_dec_act.wav")
os.mkfifo(fifo)
t0 = time.monotonic()
verdict = M._sndfile_leg("file", fifo, b"", 0.0)
elapsed = time.monotonic() - t0
print(f"elapsed_s={elapsed:.2f}")
print("verdict:", {k: verdict[k] for k in ("format_name", "read_frames", "error")})
os.unlink(fifo)
os.rmdir(tmp)
