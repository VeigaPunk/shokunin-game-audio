#!/usr/bin/env python3
"""r69 byte-identity check: every r69-ledger receipt for a prior-r68 mode must
be byte-identical to the matching r68-ledger receipt.

r69 ledger rows: 1 (normal) + 2..6 (new r69 extsuffix modes) + 7..119 (the
r68 order verbatim). r68 ledger rows: 1..114. Mapping:
  r69 row 1            <-> r68 row 1   (leading normal)
  r69 rows 7..119      <-> r68 rows 2..114
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
    r69 = rows(HERE / "ledger-r69.tsv")
    r68 = rows(HERE.parent / "r68-author" / "ledger-r68.tsv")
    assert len(r69) == 119 and len(r68) == 114
    pairs = [(r69[0], r68[0])] + [(r69[5 + k], r68[k]) for k in range(1, 114)]
    mismatches = []
    for (i69, c69, p69), (i68, c68, p68) in pairs:
        if c69 != c68:
            mismatches.append(f"exit r69[{i69}]={c69} vs r68[{i68}]={c68}")
            continue
        if p69 == "-" or p68 == "-":
            mismatches.append(f"missing receipt r69[{i69}] / r68[{i68}]")
            continue
        if Path(p69).read_bytes() != Path(p68).read_bytes():
            mismatches.append(f"bytes differ r69[{i69}] {p69} vs r68[{i68}] {p68}")
    print(f"{len(pairs)} prior-mode pairs checked, {len(mismatches)} mismatches")
    for m in mismatches:
        print(" ", m)
    return bool(mismatches)


if __name__ == "__main__":
    sys.exit(main())
