#!/usr/bin/env python3
"""Verifier: compare my 10 transport receipts (verifier ledger rows 2-11)
byte-for-byte against the author's own ledger receipts (rows 2-11)."""
import pathlib

LIVE = pathlib.Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live")
auth = [l.split("\t") for l in (LIVE / "r67-author/ledger-r67.tsv").read_text().splitlines()]
verf = [l.split("\t") for l in (LIVE / "r67-verifier/ledger-r67-verifier.tsv").read_text().splitlines()]
same = diff = 0
for a, v in zip(auth[1:11], verf[1:11]):
    ok = pathlib.Path(a[2]).read_bytes() == pathlib.Path(v[2]).read_bytes()
    same += ok
    diff += (not ok)
    print(f"row{a[0]} {'IDENTICAL' if ok else 'DIFFERS'}  {a[2].split('/')[-2]}")
print(f"{same} identical, {diff} differ (author receipt vs verifier independent replay)")
