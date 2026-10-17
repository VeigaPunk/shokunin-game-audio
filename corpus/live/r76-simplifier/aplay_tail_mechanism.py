#!/usr/bin/env python3
"""Why the r76 roundtrip's aplay tail differs between two receipts taken
from the SAME fixture: `_consumer_tail` truncates to the last 160 chars
AFTER replacing the relative label, and the roundtrip's scratch file
lives in a tmp dir under ROOT, so the surviving head depends on the
ABSOLUTE ROOT prefix length (which differs between the author's tree and
any mirrored/relocated tree).

Pure string arithmetic — no audio, no subprocess.
"""
import re


def consumer_tail(text, probe_arg):
    lines = text.strip().splitlines()
    if not lines:
        return None
    t = re.sub(r"^\s*(\[[^\]]*\])+\s*", "", lines[-1])
    t = re.sub(r"`[^']*'", "`<input>'", t)
    t = re.sub(r'"[^"]*"', '"<input>"', t)
    t = re.sub(r" @ 0x[0-9a-fA-F]+", "", t)
    return t.replace(str(probe_arg), "<input>")[-160:]


def consumer2_tail(text, probe_arg):
    tail = consumer_tail(text, probe_arg)
    if not tail:
        return tail
    tail = re.sub(r"'[^']*[/\\][^']*'", "'<input>'", tail)
    tail = re.sub(r"\S+<input>", "<input>", tail)
    return tail


LINE = ("Playing WAVE '{p}' : Signed 16 bit Little Endian, "
        "Rate 48000 Hz, Stereo")
REL = "live/r76-author/capture-r76-XXXXXXXX/roundtrip_capture.wav"
CASES = (
    ("author tree  ", "/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/"),
    ("mirror tree  ", "/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/"
                      "live/r76-simplifier/mirror/corpus/"),
)
for tag, root in CASES:
    raw = LINE.format(p=root + REL)
    mid = raw.replace(REL, "<input>")
    print(f"{tag} raw_line={len(raw)} after_rel_replace={len(mid)} "
          f"head_cut={max(0, len(mid) - 160)}")
    print(f"             tail={consumer2_tail(raw, REL)!r}")
