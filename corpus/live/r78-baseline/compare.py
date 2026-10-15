#!/usr/bin/env python3
"""r78-baseline committed-anchor comparison (adapted from r77; anchor-pinned to
frozen HEAD 731937c):
 (a) committed ledger anchor: corpus/live/r70-author/ledger-r71.tsv @ ANCHOR
     (121 rows) — mode-keyed exit/failsum compare vs the fresh 127-row ledger;
 (b) receipt byte-stability: every fresh env receipt's sha256 checked against
     the committed same-mode receipt set (ls-tree @ ANCHOR corpus/live/runs/*);
 (c) receipt-level diffs classified: EQUAL / EQUAL-MOD-PATHS (env-infix
     rewrite restores equality) / DIFFER.
ANCHOR = frozen pre-move HEAD 731937c (not live HEAD — immune to mid-window
commits).
"""
import re
import subprocess
from collections import defaultdict
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]                      # audio-shokunin
ANCHOR = "731937ccf731c711b54942d22ae4f32b7683c498"
ENV_INFIX = "corpus/live/r78-baseline/measure-env/corpus/"
LEDGER = HERE / "ledger-r78-baseline.tsv"


def git_show(path):
    return subprocess.run(["git", "show", f"{ANCHOR}:{path}"], cwd=REPO,
                          capture_output=True).stdout


def mode_of(receipt_path):
    d = Path(receipt_path).parent.name
    return re.sub(r"^\d{8}T\d+Z-?", "", d) or "?"


def sha(b):
    return sha256(b).hexdigest()


def main():
    # --- committed ledger (r71 battery order, 121 rows) @ ANCHOR ---
    committed = subprocess.run(
        ["git", "show", f"{ANCHOR}:corpus/live/r70-author/ledger-r71.tsv"],
        cwd=REPO, capture_output=True, text=True).stdout
    crows = []
    for line in committed.splitlines():
        parts = line.split("\t")
        if len(parts) >= 4:
            crows.append({"idx": int(parts[0]), "exit": parts[1],
                          "receipt": parts[2], "failsum": parts[3],
                          "mode": mode_of(parts[2])})
    # --- fresh ledger ---
    frows = []
    for line in LEDGER.read_text().splitlines():
        parts = line.split("\t")
        frows.append({"idx": int(parts[0]), "exit": parts[1],
                      "receipt": parts[2], "failsum": parts[3],
                      "mode": mode_of(parts[2])})
    by_mode = defaultdict(list)
    for r in frows:
        by_mode[r["mode"]].append(r)

    lines = [f"committed ledger @ {ANCHOR[:9]}: {len(crows)} rows; "
             f"fresh: {len(frows)} rows"]
    counts = defaultdict(int)
    out = []
    for c in crows:
        cands = by_mode.get(c["mode"], [])
        if not cands:
            out.append(f"NO-FRESH\tcommitted-{c['idx']:02d}\t{c['mode']}")
            counts["NO-FRESH"] += 1
            continue
        exact = [f for f in cands
                 if f["exit"] == c["exit"] and f["failsum"] == c["failsum"]]
        if exact:
            out.append(f"MATCH\tcommitted-{c['idx']:02d}\t{c['mode']}")
            counts["MATCH"] += 1
        else:
            out.append(f"EXIT-ONLY\tcommitted-{c['idx']:02d}\t{c['mode']}\t"
                       f"committed_exit={c['exit']} fresh_exit={cands[0]['exit']}"
                       f"\tcommitted_failsum='{c['failsum'][:150]}'"
                       f"\tfresh_failsum='{cands[0]['failsum'][:150]}'")
            counts["EXIT-ONLY"] += 1
    lines.append("--- (a) committed-ledger mode-keyed compare: "
                 + str(dict(counts)))
    lines += out
    (HERE / "ledger-compare-mode.tsv").write_text("\n".join(out) + "\n")
    mism = [o for o in out if not o.startswith("MATCH")]
    (HERE / "ledger-compare-mismatches.txt").write_text(
        "\n".join(mism) + ("\n" if mism else ""))

    # --- (b)/(c) committed receipt set @ ANCHOR ---
    ls = subprocess.run(["git", "ls-tree", "-r", "--name-only", ANCHOR,
                         "corpus/live/runs/"], cwd=REPO, capture_output=True,
                        text=True).stdout.split()
    committed_receipts = [p for p in ls if p.endswith("measurements.json")]
    committed_by_mode = defaultdict(list)
    for p in committed_receipts:
        committed_by_mode[mode_of(p)].append(p)
    lines.append(f"--- (b) committed receipt blobs @ {ANCHOR[:9]}: "
                 f"{len(committed_receipts)}")
    rlines = []
    rcounts = defaultdict(int)
    inset = 0
    for r in frows:
        fb = Path(r["receipt"]).read_bytes()
        s = sha(fb)
        mode = r["mode"]
        hit = False
        for cp in committed_by_mode.get(mode, []):
            if sha(git_show(cp)) == s:
                hit = True
                break
        if hit:
            inset += 1
            rlines.append(f"INSET\t{r['idx']:03d}\t{mode}\t{s[:16]}")
            rcounts["INSET"] += 1
            continue
        # classify against same-mode committed receipts
        cls = "NO-COMMITTED-MODE"
        for cp in committed_by_mode.get(mode, []):
            cb = git_show(cp)
            if fb == cb:
                cls = "EQUAL"
                break
            try:
                f = fb.decode()
                c = cb.decode()
            except Exception:
                continue
            f2 = f.replace(ENV_INFIX, "corpus/")
            if f2 == c:
                cls = "EQUAL-MOD-PATHS"
                break
            cls = "DIFFER"
        rlines.append(f"{cls}\t{r['idx']:03d}\t{mode}\t{s[:16]}")
        rcounts[cls] += 1
    lines.append(f"fresh-receipt membership: {inset}/{len(frows)} sha256 present "
                 f"in the committed same-mode receipt set")
    lines.append(f"receipt-level counts: {dict(rcounts)}")
    (HERE / "receipt-compare.tsv").write_text("\n".join(rlines) + "\n")
    (HERE / "receipt-membership.tsv").write_text("\n".join(rlines) + "\n")
    (HERE / "receipt-shas.txt").write_text(
        "\n".join(f"{r['idx']:03d}\t{sha(Path(r['receipt']).read_bytes())}\t"
                  f"{r['receipt']}" for r in frows) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
