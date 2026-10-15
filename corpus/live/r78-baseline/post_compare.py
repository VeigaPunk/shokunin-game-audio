#!/usr/bin/env python3
"""r78-baseline PHASE 2 compare: post-arm ledger vs the frozen Phase-1 ledger,
index-exact (row N <-> row N — same MODES list by construction), using the same
leaf-walk classifier as prior_compare.py (ENV / CONTENTION / DECLARED / JITTER /
PATH), plus the same-mode receipt membership check.

Expected Phase-2 outcome per the assignment: every prior cell byte-stable
modulo the SAME named environmental set (the DualSense default-source topology
change) + declared contention classes; the NEW r78 rows may differ freely (they
are the arm under test).

Writes post-rows-stable.txt + post-receipt-compare.tsv + post-undeclared-diffs.txt.
"""
import json
from collections import defaultdict
from pathlib import Path

import prior_compare as pc

HERE = Path(__file__).resolve().parent
PHASE1 = HERE / "ledger-r78-baseline.tsv"
POST = HERE / "ledger-r78-baseline-post.tsv"
INFIX_1 = "corpus/live/r78-baseline/measure-env/corpus/"
INFIX_2 = "corpus/live/r78-baseline/measure-env-post/corpus/"

# r78-only rows (the arm's own new families): differences here are the arm under
# test, not prior-cell drift — reported separately, never as drift.
NEW_MODES = {"capture-r78", "capture-r78-playback"}


def main():
    p1 = pc.read_ledger(PHASE1)
    post = pc.read_ledger(POST)
    lines = [f"phase-1 ledger: {len(p1)} rows", f"post ledger: {len(post)} rows"]
    by_idx = {r["idx"]: r for r in post}
    row_cls = defaultdict(int)
    cls_count = defaultdict(int)
    new_rows = []
    rlines, undeclared = [], []
    for a in p1:
        b = by_idx.get(a["idx"])
        if b is None:
            row_cls["NO-POST-ROW"] += 1
            lines.append(f"NO-POST-ROW\t{a['idx']:03d}\t{a['mode']}")
            continue
        if a["mode"] in NEW_MODES or b["mode"] in NEW_MODES:
            new_rows.append(f"{b['idx']:03d}\t{a['mode']}->{b['mode']}\t"
                            f"exit {a['exit']}->{b['exit']}")
            continue
        if a["exit"] == b["exit"] and a["failsum"] == b["failsum"]:
            row_cls["ROW-STABLE"] += 1
        else:
            cls = "ROW-EXIT-ONLY" if a["exit"] == b["exit"] else "ROW-NO-MATCH"
            row_cls[cls] += 1
            lines.append(f"{cls}\t{a['idx']:03d}\t{a['mode']}\t"
                         f"phase1_exit={a['exit']} post_exit={b['exit']}\n"
                         f"    phase1_failsum='{a['failsum'][:200]}'\n"
                         f"    post_failsum='{b['failsum'][:200]}'")
        pa, pb = Path(a["receipt"]), Path(b["receipt"])
        if not pa.is_file():
            rlines.append(f"PHASE1-MISSING\t{a['idx']:03d}\t{a['mode']}")
            cls_count["PHASE1-MISSING"] += 1
            continue
        cls, content = pc.classify(pb.read_bytes(), pa.read_bytes(),
                                   f"{a['idx']:03d}\t{a['mode']}", INFIX_1)
        cls_count[cls.split("\t")[0]] += 1
        rlines.append(cls)
        if content:
            undeclared.append(f"{a['idx']:03d} {a['mode']}: {content[:8]}")
    lines.append(f"row-level (index-exact, prior cells): {dict(row_cls)}")
    lines.append(f"receipt-level counts: {dict(cls_count)}")
    if new_rows:
        lines.append("--- arm-owned new rows (not drift):")
        lines += ["  " + r for r in new_rows]
    (HERE / "post-rows-stable.txt").write_text("\n".join(lines) + "\n")
    (HERE / "post-receipt-compare.tsv").write_text("\n".join(rlines) + "\n")
    if undeclared:
        (HERE / "post-undeclared-diffs.txt").write_text(
            "\n".join(undeclared) + "\n")
    print("\n".join(lines))
    print(f"\nreceipt-level: {dict(cls_count)}")


if __name__ == "__main__":
    main()
