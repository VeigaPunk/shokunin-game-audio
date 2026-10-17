#!/usr/bin/env python3
"""r74 simplifier: measure the acm member's PCM extent on file vs fifo using
the LANDED fixture's own mpv_extent_leg instrument (tree copy).

If the extents are identical while the landed matrix reports
transport_fork=True, the fork verdict is produced solely by the seek_failed
leaf -> the acm 'fork' cell is a false positive relative to rc/extent.
"""
import importlib.util
import json
import sys
from pathlib import Path

TREE = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r74-simplifier/tree")
spec = importlib.util.spec_from_file_location(
    "measure_audio_r74", TREE / "corpus" / "fixtures" / "measure_audio.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

member = TREE / "corpus" / "live" / "round-74" / "lavf_acm.acm"
data = member.read_bytes()
hold_s = m.fifo_writer_hold_s()
out = {}
for t in ("file", "redirected_fd", "stdin_pipe", "fifo_path"):
    leg = m.mpv_extent_leg(t, member, data, hold_s)
    out[t] = {k: leg[k] for k in ("exit_code", "lavf_detected", "seek_failed",
                                  "pcm_out_bytes", "pcm_out_duration_s",
                                  "mpv_verdict")}
print(json.dumps(out, indent=2, sort_keys=True))
b = {t: out[t]["pcm_out_bytes"] for t in out}
print("extent identical across transports:", len(set(b.values())) == 1)
