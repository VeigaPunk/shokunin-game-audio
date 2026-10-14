#!/usr/bin/env python3
"""r70 reviewer compare: fresh 119-row replay vs committed r69 ledger.

Checks per row: (a) exit code identical, (b) failure_summary column identical,
(c) fresh receipt bytes == committed receipt bytes (committed path taken from
ledger-r69.tsv column 3; fresh path from ledger-r70rev.tsv column 3).
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMMITTED = HERE.parent / "r69-author" / "ledger-r69.tsv"
FRESH = HERE / "ledger-r70rev.tsv"


def rows(tsv):
    out = []
    for line in tsv.read_text().splitlines():
        idx, code, receipt, failsum = line.split("\t", 3)
        out.append((int(idx), int(code), receipt, failsum))
    return out


def main():
    committed = rows(COMMITTED)
    fresh = rows(FRESH)
    print(f"committed rows: {len(committed)}  fresh rows: {len(fresh)}")
    if len(committed) != len(fresh):
        return 1
    exit_mm = sum_mm = byte_mm = 0
    for (i_c, c_c, p_c, f_c), (i_f, c_f, p_f, f_f) in zip(committed, fresh):
        assert i_c == i_f
        if c_c != c_f:
            exit_mm += 1
            print(f"row {i_c}: exit committed={c_c} fresh={c_f}")
        if f_c != f_f:
            sum_mm += 1
            print(f"row {i_c}: failsum committed={f_c!r} fresh={f_f!r}")
        if p_c == "-" or p_f == "-":
            print(f"row {i_c}: missing receipt (committed={p_c!r} fresh={p_f!r})")
            byte_mm += 1
            continue
        if Path(p_c).read_bytes() != Path(p_f).read_bytes():
            byte_mm += 1
            print(f"row {i_c}: receipt bytes differ\n  committed {p_c}\n  fresh     {p_f}")
    tally_c = sum(1 for r in committed if r[1] == 0), sum(1 for r in committed if r[1] == 1)
    tally_f = sum(1 for r in fresh if r[1] == 0), sum(1 for r in fresh if r[1] == 1)
    print(f"exit tally committed 0/1: {tally_c}  fresh 0/1: {tally_f}")
    print(f"mismatches: exit={exit_mm} failsum={sum_mm} receipt_bytes={byte_mm}")
    return bool(exit_mm or sum_mm or byte_mm)


if __name__ == "__main__":
    sys.exit(main())
