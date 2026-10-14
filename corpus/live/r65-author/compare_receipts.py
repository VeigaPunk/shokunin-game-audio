#!/usr/bin/env python3
"""Compare r65-ledger prior rows against the r64-ledger receipt paths.

r65 ledger row layout: row 1 normal; rows 2-5 the new r65 modes; rows 6-96
replay r64's rows 2-92 verbatim. For each prior row, read the receipt path
recorded in ledger-r64.tsv at the corresponding position and compare the
fresh receipt's bytes against the original file's bytes.
"""
import sys
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
R64 = ROOT / "corpus/live/r64-author/ledger-r64.tsv"
R65 = ROOT / "corpus/live/r65-author/ledger-r65.tsv"


def rows(path):
    out = []
    for line in path.read_text().splitlines():
        idx, code, receipt, failsum = line.split("\t", 3)
        out.append((int(idx), int(code), receipt, failsum))
    return out


def main():
    old, new = rows(R64), rows(R65)
    assert len(old) == 92 and len(new) == 96
    # r65 row i (i==1 or i>=6) replays r64 row (i if i==1 else i-4).
    pairs = [(new[0], old[0])] + [(new[i+4], old[i]) for i in range(1, 92)]
    mism = []
    for nrow, orow in pairs:
        n_idx, n_code, n_path, n_fail = nrow
        o_idx, o_code, o_path, o_fail = orow
        if n_code != o_code or n_fail != o_fail:
            mism.append((n_idx, o_idx, "exit/failsum", n_code, o_code, n_fail[:80], o_fail[:80]))
            continue
        nb = Path(n_path).read_bytes() if n_path != "-" else b"-"
        ob = Path(o_path).read_bytes() if o_path != "-" else b"-"
        if nb != ob:
            mism.append((n_idx, o_idx, "receipt-bytes", n_path, o_path))
    print(f"compared {len(pairs)} prior rows; mismatches: {len(mism)}")
    for m in mism:
        print("  MISMATCH", m)
    return 1 if mism else 0


if __name__ == "__main__":
    sys.exit(main())
