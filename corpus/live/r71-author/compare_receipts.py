#!/usr/bin/env python3
"""r71 byte-identity check: every r71-ledger row whose mode also ran in the
r70 ledger must produce a byte-identical receipt AND identical exit code.

Mode identity:
  r71 row i -> MODES[i-1] flag parsed from run_ledger.py (authoritative:
  the flag actually passed to measure_audio.py on that row).
  r70 row   -> receipt-dir suffix (runs/<ts>Z-<suffix>/measurements.json);
  the r70 ledger ran one row per mode, no duplicates.

r71-only modes (the new ffprobe arm + modes absent from the r70 ledger)
are reported but not compared. Trailing r71 normal replays all compare
against r70's single normal receipt.
"""
import ast, re, sys
from pathlib import Path

BASE = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live")


def modes_from_ledger():
    tree = ast.parse((BASE / "r71-author/run_ledger.py").read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and node.targets[0].id == "MODES":
            return [e.value for e in node.value.elts]
    raise RuntimeError("MODES not found")


def suffix_of(receipt):
    m = re.search(r"Z-(.*)/measurements\.json$", receipt)
    return m.group(1)


def main():
    modes = modes_from_ledger()
    r71 = [l.split("\t") for l in
           (BASE / "r70-author/ledger-r71.tsv").read_text().splitlines()]
    r70 = [l.split("\t") for l in
           (BASE / "r70-author/ledger-r70.tsv").read_text().splitlines()]
    assert len(r71) == len(modes) == 121, (len(r71), len(modes))

    r70map = {}
    for idx, code, receipt, _ in r70:
        r70map[suffix_of(receipt)] = (int(code), receipt)

    matched, new_modes, mismatches = [], [], []
    for i, (row, flag) in enumerate(zip(r71, modes), 1):
        idx, code, receipt, _ = row
        mode = flag[len("--probe-"):] if flag.startswith("--probe-") else "normal"
        if i == 2:
            mode = "ffprobe-transport-r71"   # pre-D1-fix run: -normal dir
        if mode not in r70map:
            new_modes.append((i, mode))
            continue
        c70, p70 = r70map[mode]
        if int(code) != c70:
            mismatches.append(f"row {i} {mode}: exit {code} vs r70 {c70}")
        elif Path(receipt).read_bytes() != Path(p70).read_bytes():
            mismatches.append(f"row {i} {mode}: receipt bytes differ")
        else:
            matched.append(mode)

    print(f"matched+identical: {len(matched)}")
    print(f"r71-only modes (no r70 counterpart): {len(new_modes)}")
    for i, m in new_modes:
        print(f"   row {i}: {m}")
    print(f"mismatches: {len(mismatches)}")
    for m in mismatches:
        print("  ", m)
    return bool(mismatches)


if __name__ == "__main__":
    sys.exit(main())
