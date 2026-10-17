#!/usr/bin/env python3
"""r76-simplifier receipt comparison: pairwise leaf diff + byte identity.

Symmetric key walk (a key present in only one receipt is reported), so a
list that grew/shrank is never silently equal.
"""
import hashlib
import itertools
import json
from pathlib import Path

SIM = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r76-simplifier")
CANON = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/runs/"
             "20261014T182539237046Z-capture-r76/measurements.json")

LABELS = ["A2-baseline", "B1-simplified", "B2-simplified", "A3-baseline",
          "B3-simplified-d1d9", "A4-baseline", "A5-baseline", "B4-simplified-d1d9"]


def leaves(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, f"{p}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, f"{p}/{i}")
    else:
        yield p, o


def load(p):
    return dict(leaves(json.loads(Path(p).read_text())))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


receipts = {lab: SIM / "receipts" / f"{lab}.json" for lab in LABELS}
receipts = {k: v for k, v in receipts.items() if v.exists()}
data = {k: load(v) for k, v in receipts.items()}

print("== receipt shas ==")
for k, v in receipts.items():
    print(f"{k:22s} {sha(v)}  {v.name}")

print("\n== pairwise ==")
for a, b in itertools.combinations(data, 2):
    ka, kb = set(data[a]), set(data[b])
    keys = ka | kb
    diffs = [(k, data[a].get(k, "<absent>"), data[b].get(k, "<absent>"))
             for k in sorted(keys) if data[a].get(k, "<absent>") != data[b].get(k, "<absent>")]
    same = sha(receipts[a]) == sha(receipts[b])
    print(f"{a:22s} vs {b:22s} byte-identical={same!s:5s} differing_leaves={len(diffs)}")
    for k, x, y in diffs:
        print(f"      {k} | {x!r} -> {y!r}")

print("\n== canonical vs each (baseline runs only) ==")
canon = load(CANON)
for lab in data:
    keys = set(canon) | set(data[lab])
    diffs = [(k, canon.get(k, "<absent>"), data[lab].get(k, "<absent>"))
             for k in sorted(keys) if canon.get(k, "<absent>") != data[lab].get(k, "<absent>")]
    print(f"canonical(ba36cd70) vs {lab:22s} differing_leaves={len(diffs)}")
    for k, x, y in diffs:
        print(f"      {k} | {x!r} -> {y!r}")
