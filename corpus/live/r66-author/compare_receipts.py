#!/usr/bin/env python3
"""r66 byte-identity check: every r66-ledger receipt for a prior-r65 mode must
be byte-identical to the matching r65-ledger receipt.

r66 ledger rows: 1 (normal) + 2..7 (new r66 modes) + 8..102 (the r65 order
verbatim). r65 ledger rows: 1 (normal) + 2..96. Mapping:
  r66 row 1            <-> r65 row 1   (leading normal)
  r66 rows 8..102      <-> r65 rows 2..96
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
    r66 = rows(HERE / "ledger-r66.tsv")
    r65 = rows(HERE.parent / "r65-author" / "ledger-r65.tsv")
    assert len(r66) == 102 and len(r65) == 96
    pairs = [(r66[0], r65[0])] + [(r66[6 + k], r65[k]) for k in range(1, 96)]
    mismatches = []
    for (i66, c66, p66), (i65, c65, p65) in pairs:
        if c66 != c65:
            mismatches.append(f"exit r66[{i66}]={c66} vs r65[{i65}]={c65}")
            continue
        if p66 == "-" or p65 == "-":
            mismatches.append(f"missing receipt r66[{i66}] / r65[{i65}]")
            continue
        if Path(p66).read_bytes() != Path(p65).read_bytes():
            mismatches.append(f"bytes differ r66[{i66}] {p66} vs r65[{i65}] {p65}")
    print(f"{len(pairs)} prior-mode pairs checked, {len(mismatches)} mismatches")
    for m in mismatches:
        print(" ", m)
    return bool(mismatches)


if __name__ == "__main__":
    sys.exit(main())
