#!/usr/bin/env python3
"""r68 byte-identity check: every r68-ledger receipt for a prior-r67 mode must
be byte-identical to the matching r67-ledger receipt.

r68 ledger rows: 1 (normal) + 2..3 (new r68 transport modes) + 4..114 (the
r67 order verbatim). r67 ledger rows: 1..112. Mapping:
  r68 row 1            <-> r67 row 1   (leading normal)
  r68 rows 4..114      <-> r67 rows 2..112
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
    r68 = rows(HERE / "ledger-r68.tsv")
    r67 = rows(HERE.parent / "r67-author" / "ledger-r67.tsv")
    assert len(r68) == 114 and len(r67) == 112
    pairs = [(r68[0], r67[0])] + [(r68[2 + k], r67[k]) for k in range(1, 112)]
    mismatches = []
    for (i68, c68, p68), (i67, c67, p67) in pairs:
        if c68 != c67:
            mismatches.append(f"exit r68[{i68}]={c68} vs r67[{i67}]={c67}")
            continue
        if p68 == "-" or p67 == "-":
            mismatches.append(f"missing receipt r68[{i68}] / r67[{i67}]")
            continue
        if Path(p68).read_bytes() != Path(p67).read_bytes():
            mismatches.append(f"bytes differ r68[{i68}] {p68} vs r67[{i67}] {p67}")
    print(f"{len(pairs)} prior-mode pairs checked, {len(mismatches)} mismatches")
    for m in mismatches:
        print(" ", m)
    return bool(mismatches)


if __name__ == "__main__":
    sys.exit(main())
