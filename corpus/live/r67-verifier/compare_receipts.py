#!/usr/bin/env python3
"""r67 byte-identity check: every r67-ledger receipt for a prior-r66 mode must
be byte-identical to the matching r66-ledger receipt.

r67 ledger rows: 1 (normal) + 2..11 (new r67 transport modes) + 12..112 (the
r66 order verbatim). r66 ledger rows: 1 (normal) + 2..102. Mapping:
  r67 row 1            <-> r66 row 1   (leading normal)
  r67 rows 12..112     <-> r66 rows 2..102
Receipt paths are taken from each ledger TSV (3rd column) and compared with
cmp semantics (byte equality). Exit codes from column 2 must also match.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(tsv):
    out = []
    for line in tsv.read_text().splitlines():
        idx, code, receipt, _ = line.split("\t", 3)
        out.append((int(idx), int(code), receipt))
    return out


def main():
    r67 = rows(HERE / "ledger-r67-verifier.tsv")
    r66 = rows(HERE.parent / "r66-author" / "ledger-r66.tsv")
    assert len(r67) == 112 and len(r66) == 102
    pairs = [(r67[0], r66[0])] + [(r67[10 + k], r66[k]) for k in range(1, 102)]
    mismatches = []
    for (i67, c67, p67), (i66, c66, p66) in pairs:
        if c67 != c66:
            mismatches.append(f"exit r67[{i67}]={c67} vs r66[{i66}]={c66}")
            continue
        if p67 == "-" or p66 == "-":
            mismatches.append(f"missing receipt r67[{i67}] / r66[{i66}]")
            continue
        if Path(p67).read_bytes() != Path(p66).read_bytes():
            mismatches.append(f"bytes differ r67[{i67}] {p67} vs r66[{i66}] {p66}")
    print(f"{len(pairs)} prior-mode pairs checked, {len(mismatches)} mismatches")
    for m in mismatches:
        print(" ", m)
    return bool(mismatches)


if __name__ == "__main__":
    sys.exit(main())
