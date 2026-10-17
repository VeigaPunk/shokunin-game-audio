#!/usr/bin/env python3
"""r79 CRITIC forge 1 — build a scratch copy of the frozen artifact in
which ONE arm of the `-C` lattice does not link, then run the REAL entry.

The forge is the smallest possible: the leg is spawned, measured and torn
down exactly as the frozen artifact does; only the *observation* of the
`b01_sink_prop` leg's capture node is rewritten to the shape a broken
sink-prop arm produces (published, zero ports, zero links — the shape the
author himself measured for an unnegotiated stream).

If the entry still reports `failures == []`, the round's headline arm
("stream.capture.sink=true + resolvable sink -> that sink's monitor") can
go unmeasured inside a green formal run.
"""
import pathlib
import re
import sys

SRC = pathlib.Path(__file__).resolve().parents[3] / "corpus/fixtures/measure_audio.py"
DST = pathlib.Path(__file__).resolve().parent / "forge1-measure_audio.py"

text = SRC.read_text()
anchor = '''    cell["carries_tone"] = (cell.get("tap") or {}).get("carries_tone")
    return cell'''
n_anchor = text.count(anchor)
assert n_anchor == 2, f"expected the anchor twice (r78+r79), got {n_anchor}"
# the r79 leg builder is the LAST occurrence (line 9262 vs the r78 line 6614)
head = text[:text.rindex(anchor)]
tail = text[text.rindex(anchor) + len(anchor):]
patch = '''    cell["carries_tone"] = (cell.get("tap") or {}).get("carries_tone")
    # ---- FORGE 1 (r79 critic): the sink-prop arm publishes unnegotiated.
    if name == "b01_sink_prop":
        for _s in run["samples"]:
            _w = (_s.get("watch") or {}).get(f"input.{ltag}")
            if _w is not None:
                for _k in ("input_ports", "output_ports", "producers",
                           "producer_ports", "consumers", "consumer_ports"):
                    _w[_k] = []
            (_s.get("nodes") or {}).get(f"input.{ltag}", {})["state"] = \\
                "suspended"
    return cell'''
DST.write_text(head + patch + tail)
print("patched occurrence: r79 _loopback_r79_leg (last of", n_anchor, ")")
print(f"forge1 written: {DST}")
print("diff size:", len(patch.splitlines()), "lines inserted")
