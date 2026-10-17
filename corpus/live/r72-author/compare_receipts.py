#!/usr/bin/env python3
"""r72 byte-identity check: every r72-ledger row whose mode has a prior
receipt in corpus/live/runs/ must produce a byte-identical receipt AND an
exit code identical to the r71 ledger's for that mode.

Baseline rule: for mode M (flag --probe-M or 'normal'), the prior receipt
is the newest corpus/live/runs/*-M/measurements.json NOT produced by this
r72 ledger run (ledger receipt paths are excluded). The dir suffix equals
the mode name verbatim ("-ffprobe-transport-r71" for mode
"ffprobe-transport-r71"), which also routes around the r71 row-2
pre-D1-fix receipt that landed in a -normal dir.

Exit-code baseline: the r71 ledger row for the same mode flag
(corpus/live/r70-author/ledger-r71.tsv + r71-author/run_ledger.py MODES).
"""
import ast, sys
from pathlib import Path

BASE = Path("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live")
RUNS = BASE / "runs"


def modes_from(path):
    tree = ast.parse(path.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and node.targets[0].id == "MODES":
            return [e.value for e in node.value.elts]
    raise RuntimeError("MODES not found")


def mode_of(flag):
    return flag[len("--probe-"):] if flag.startswith("--probe-") else "normal"


def main():
    r72_modes = modes_from(BASE / "r72-author/run_ledger.py")
    r71_modes = modes_from(BASE / "r71-author/run_ledger.py")
    r72 = [l.split("\t") for l in
           (BASE / "r72-author/ledger-r72.tsv").read_text().splitlines()]
    r71 = [l.split("\t") for l in
           (BASE / "r70-author/ledger-r71.tsv").read_text().splitlines()]
    assert len(r72) == len(r72_modes) == 122, (len(r72), len(r72_modes))
    assert len(r71) == len(r71_modes) == 121, (len(r71), len(r71_modes))

    mine = {row[2] for row in r72}
    r71_exit = {}
    for (idx, code, receipt, _), flag in zip(r71, r71_modes):
        r71_exit.setdefault(mode_of(flag), int(code))

    # newest prior receipt per mode-suffix, excluding this run's receipts
    priors = {}
    for d in sorted(RUNS.iterdir()):
        m = d.name
        if "-" not in m:
            continue
        suffix = m.split("Z-", 1)[-1]
        rec = d / "measurements.json"
        if rec.exists() and str(rec) not in mine:
            priors[suffix] = rec   # sorted() -> last wins = newest stamp

    matched, new_modes, mismatches = [], [], []
    for i, (row, flag) in enumerate(zip(r72, r72_modes), 1):
        idx, code, receipt, _ = row
        mode = mode_of(flag)
        prior = priors.get(mode)
        if prior is None:
            new_modes.append((i, mode))
            continue
        if mode in r71_exit and int(code) != r71_exit[mode]:
            mismatches.append(f"row {i} {mode}: exit {code} vs r71 {r71_exit[mode]}")
        elif Path(receipt).read_bytes() != prior.read_bytes():
            mismatches.append(f"row {i} {mode}: receipt bytes differ "
                              f"({receipt} vs {prior})")
        else:
            matched.append(mode)

    print(f"matched+identical: {len(matched)}")
    print(f"r72-only modes (no prior receipt): {len(new_modes)}")
    for i, m in new_modes:
        print(f"   row {i}: {m}")
    print(f"mismatches: {len(mismatches)}")
    for m in mismatches:
        print("  ", m)
    return bool(mismatches)


if __name__ == "__main__":
    sys.exit(main())
