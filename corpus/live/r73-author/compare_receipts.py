#!/usr/bin/env python3
"""r73 byte-identity check: every r73-ledger row whose mode has a prior
receipt in corpus/live/runs/ must produce a byte-identical receipt AND an
exit code identical to the r72 ledger's for that mode.

Baseline rule: for mode M (flag --probe-M or 'normal'), the prior receipt
is the newest corpus/live/runs/*-M/measurements.json NOT produced by this
r73 ledger run (ledger receipt paths are excluded). The dir suffix equals
the mode name verbatim ("-consumers-r73" for mode "consumers-r73").

Exit-code baseline: the r72 ledger row for the same mode flag
(corpus/live/r72-author/ledger-r72.tsv + r72-author/run_ledger.py MODES).
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
    r73_modes = modes_from(BASE / "r73-author/run_ledger.py")
    r72_modes = modes_from(BASE / "r72-author/run_ledger.py")
    r73 = [l.split("\t") for l in
           (BASE / "r73-author/ledger-r73.tsv").read_text().splitlines()]
    r72 = [l.split("\t") for l in
           (BASE / "r72-author/ledger-r72.tsv").read_text().splitlines()]
    assert len(r73) == len(r73_modes) == 123, (len(r73), len(r73_modes))
    assert len(r72) == len(r72_modes) == 122, (len(r72), len(r72_modes))

    mine = {row[2] for row in r73}
    # This seat's pre-ledger smoke receipt for the new mode — a this-round
    # product, not a prior baseline (and wall_s fields in the pw-cat ops
    # legs are realtime measurements, so it could never be a byte-baseline
    # anyway; stability of the new row is checked field-wise in the report).
    mine.add(str(RUNS / "20261014T145109998458Z-consumers-r73/measurements.json"))
    r72_exit = {}
    for (idx, code, receipt, _), flag in zip(r72, r72_modes):
        r72_exit.setdefault(mode_of(flag), int(code))

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
    for i, (row, flag) in enumerate(zip(r73, r73_modes), 1):
        idx, code, receipt, _ = row
        mode = mode_of(flag)
        prior = priors.get(mode)
        if prior is None or mode not in r72_exit:
            # consumers-r73 has no committed prior; sibling seats re-running
            # the fixture this round leave stray *-consumers-r73 receipts in
            # runs/ — mode-membership in the r72 ledger is the new/old test,
            # not receipt presence.
            new_modes.append((i, mode))
            continue
        if mode in r72_exit and int(code) != r72_exit[mode]:
            mismatches.append(f"row {i} {mode}: exit {code} vs r72 {r72_exit[mode]}")
        elif Path(receipt).read_bytes() != prior.read_bytes():
            mismatches.append(f"row {i} {mode}: receipt bytes differ "
                              f"({receipt} vs {prior})")
        else:
            matched.append(mode)

    print(f"matched+identical: {len(matched)}")
    print(f"r73-only modes (no prior receipt): {len(new_modes)}")
    for i, m in new_modes:
        print(f"   row {i}: {m}")
    print(f"mismatches: {len(mismatches)}")
    for m in mismatches:
        print("  ", m)
    return bool(mismatches)


if __name__ == "__main__":
    sys.exit(main())
