#!/usr/bin/env python3
"""r70 byte-identity check: every r70-ledger receipt for a prior-r69 mode must
be byte-identical to the matching r69-ledger receipt.

r70 ledger rows: 1 (normal) + 2 (new fifo-hold-ladder mode) + 3..120 (the
r69 order verbatim). r69 ledger rows: 1..119. Mapping:
  r70 row 1            <-> r69 row 1   (leading normal)
  r70 rows 3..120      <-> r69 rows 2..119
Receipt paths are taken from each ledger TSV (3rd column) and compared
byte-for-byte. Exit codes from column 2 must also match.
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
    r70 = rows(HERE / "ledger-r70.tsv")
    r69 = rows(HERE.parent / "r69-author" / "ledger-r69.tsv")
    assert len(r70) == 120 and len(r69) == 119
    pairs = [(r70[0], r69[0])] + [(r70[1 + k], r69[k]) for k in range(1, 119)]
    mismatches = []
    for (i70, c70, p70), (i69, c69, p69) in pairs:
        if c70 != c69:
            mismatches.append(f"exit r70[{i70}]={c70} vs r69[{i69}]={c69}")
            continue
        if p70 == "-" or p69 == "-":
            mismatches.append(f"missing receipt r70[{i70}] / r69[{i69}]")
            continue
        if Path(p70).read_bytes() != Path(p69).read_bytes():
            mismatches.append(f"bytes differ r70[{i70}] {p70} vs r69[{i69}] {p69}")
    print(f"{len(pairs)} prior-mode pairs checked, {len(mismatches)} mismatches")
    for m in mismatches:
        print(" ", m)
    return bool(mismatches)


if __name__ == "__main__":
    sys.exit(main())
