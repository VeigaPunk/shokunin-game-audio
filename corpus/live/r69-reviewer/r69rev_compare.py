#!/usr/bin/env python3
"""r69 reviewer compare: my fresh 114-row replay vs committed r68 ledger +
committed r67 receipts (prior-112 chain).

Checks:
 [a] exit sequence position-identical to committed ledger-r68.tsv; tally 49/65
 [b] each fresh receipt BYTE-IDENTICAL to the committed r68 receipt at the
     same row (path taken from the committed TSV column 3)
 [c] suffix check: fresh receipt dir suffix == committed receipt dir suffix
     (mode-order fidelity — the committed path's suffix names the mode run)
 [d] failure-summary column identical to committed TSV column 4
 [e] prior-112 chain: my rows {1}∪{4-114} receipts byte-identical to the
     committed r67 ledger receipts at rows {1-112} (r67 TSV column 3)
"""
import sys
from pathlib import Path

LIVE = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live")
MINE = LIVE / "r69-reviewer" / "ledger-r69rev.tsv"
R68 = LIVE / "r68-author" / "ledger-r68.tsv"
R67 = LIVE / "r67-author" / "ledger-r67.tsv"


def rows(tsv):
    out = []
    for line in tsv.read_text().splitlines():
        idx, code, receipt, failsum = line.split("\t", 3)
        out.append((int(idx), int(code), receipt, failsum))
    return out


def suffix_of(receipt_path):
    # .../runs/<stamp>-<suffix>/measurements.json -> <suffix>
    return Path(receipt_path).parent.name.split("Z-", 1)[-1]


def main():
    mine, r68, r67 = rows(MINE), rows(R68), rows(R67)
    assert len(mine) == 114 and len(r68) == 114 and len(r67) == 112

    exits = [c for _, c, _, _ in mine]
    n0 = exits.count(0)
    n1 = exits.count(1)
    nother = len(exits) - n0 - n1
    print(f"[a] my exits: {n0} exit-0 / {n1} exit-1 / {nother} other (committed r68: 49/65)")
    exit_mm = [(i, c, rc) for (i, c, _, _), (_, rc, _, _) in zip(mine, r68) if c != rc]
    print(f"    exit mismatches vs committed r68: {len(exit_mm)}")
    for m in exit_mm:
        print("     ", m)

    byte_mm = []
    for (i, c, p, _), (_, _, rp, _) in zip(mine, r68):
        if p == "-" or rp == "-":
            byte_mm.append(f"row {i}: missing receipt mine={p} committed={rp}")
            continue
        if Path(p).read_bytes() != Path(rp).read_bytes():
            byte_mm.append(f"row {i}: {p} != {rp}")
    print(f"[b] fresh receipts vs committed r68 receipts: {len(byte_mm)} mismatches")
    for m in byte_mm[:10]:
        print("     ", m)

    sfx_mm = [(i, suffix_of(p), suffix_of(rp))
              for (i, _, p, _), (_, _, rp, _) in zip(mine, r68)
              if p != "-" and rp != "-" and suffix_of(p) != suffix_of(rp)]
    print(f"[c] receipt-suffix (mode-order) mismatches: {len(sfx_mm)}")
    for m in sfx_mm[:10]:
        print("     ", m)

    fs_mm = [(i, f, rf) for (i, _, _, f), (_, _, _, rf) in zip(mine, r68) if f != rf]
    print(f"[d] failure-summary mismatches vs committed r68: {len(fs_mm)}")
    for m in fs_mm[:10]:
        print("     ", m)

    pairs = [(mine[0], r67[0])] + [(mine[2 + k], r67[k]) for k in range(1, 112)]
    chain_mm = []
    for (i69, c69, p69, _), (i67, c67, p67, _) in pairs:
        if c69 != c67:
            chain_mm.append(f"exit r69[{i69}]={c69} vs r67[{i67}]={c67}")
            continue
        if p69 == "-" or p67 == "-":
            chain_mm.append(f"missing receipt r69[{i69}] / r67[{i67}]")
            continue
        if Path(p69).read_bytes() != Path(p67).read_bytes():
            chain_mm.append(f"bytes differ r69[{i69}] {p69} vs r67[{i67}] {p67}")
    print(f"[e] prior-112 pairs vs committed r67 receipts: {len(pairs)} checked, {len(chain_mm)} mismatches")
    for m in chain_mm[:10]:
        print("     ", m)

    bad = bool(exit_mm or byte_mm or sfx_mm or fs_mm or chain_mm or nother)
    print("RESULT:", "MISMATCH" if bad else "ALL-CLEAN")
    return bad


if __name__ == "__main__":
    sys.exit(main())
