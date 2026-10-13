#!/usr/bin/env python3
"""r63-simplifier: sweep byte value at file offset 256 of pair_valid_17.wav.
For each value 0..255 record sox detected format type + exit/decode signal.
Probe: sox -V3 file -n  → 'detected file format type `X'' + exit code.
"""
import subprocess, re, sys

F = "mut.wav"
base = open("base.wav", "rb").read()
assert base[256] == 0x84
open(F, "wb").write(base)

DET = re.compile(rb"detected file format type `([a-zA-Z0-9_-]+)'")
rows = []
for v in range(256):
    with open(F, "r+b") as f:
        f.seek(256)
        f.write(bytes([v]))
    p = subprocess.run(["sox", "-V3", F, "-n"], capture_output=True)
    m = DET.search(p.stderr)
    det = m.group(1).decode() if m else "NONE"
    rows.append((v, det, p.returncode))

from collections import Counter
agg = Counter((d, rc) for _, d, rc in rows)
for (d, rc), n in sorted(agg.items()):
    vals = [v for v, dd, rr in rows if dd == d and rr == rc]
    print(f"detected={d!s:10s} exit={rc}  count={n}  values={','.join(f'{x:02x}' for x in vals[:20])}{'...' if len(vals)>20 else ''}")
print("--- per-value table written to value_sweep.tsv")
with open("value_sweep.tsv", "w") as f:
    f.write("byte256\tdetected\texit\n")
    for v, d, rc in rows:
        f.write(f"{v:02x}\t{d}\t{rc}\n")
