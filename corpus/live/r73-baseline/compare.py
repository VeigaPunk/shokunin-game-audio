#!/usr/bin/env python3
"""r73-baseline comparison:
 (a) committed ledger anchor: corpus/live/r70-author/ledger-r71.tsv @ HEAD
     (121 rows) — mode-keyed exit/failsum compare vs the fresh 122-row ledger;
 (b) receipt byte-stability: every fresh env receipt's sha256 checked against
     the committed same-mode receipt set (git show HEAD:corpus/live/runs/*);
 (c) receipt-level diffs classified: EQUAL / EQUAL-MOD-PATHS (env-infix
     rewrite restores equality) / TAIL-EQUAL (truncated-path class, suffix
     after last 'corpus/' identical) / CONTENT-DIFF.
"""
import json
import re
import subprocess
import sys
from collections import defaultdict
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]                      # audio-shokunin
ENV_INFIX = "corpus/live/r73-baseline/measure-env/corpus/"
LEDGER = HERE / "ledger-r73-baseline.tsv"


def git_show(path):
    return subprocess.run(["git", "show", f"HEAD:{path}"], cwd=REPO,
                          capture_output=True).stdout


def mode_of(receipt_path):
    d = Path(receipt_path).parent.name
    return re.sub(r"^\d{8}T\d+Z-?", "", d) or "?"


def sha(b):
    return sha256(b).hexdigest()


def main():
    # --- committed ledger (r71 battery order, 121 rows) ---
    committed = subprocess.run(
        ["git", "show", "HEAD:corpus/live/r70-author/ledger-r71.tsv"],
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
    fresh_by_mode = defaultdict(list)
    for r in frows:
        fresh_by_mode[r["mode"]].append(r)

    # --- committed runs/ sha-sets per mode (all tracked receipts) ---
    names = subprocess.run(["git", "ls-files", "corpus/live/runs"],
                           cwd=REPO, capture_output=True, text=True
                           ).stdout.split()
    sha_sets = defaultdict(set)
    committed_receipt_sha = {}
    for p in names:
        b = git_show(p)
        sha_sets[mode_of(p)].add(sha(b))
        committed_receipt_sha[p] = sha(b)

    # --- ledger compare: every committed row matched by mode ---
    out = []
    mism = []
    for c in crows:
        cands = fresh_by_mode.get(c["mode"], [])
        if not cands:
            mism.append(f"committed row {c['idx']:02d} mode {c['mode']}: NO FRESH ROW")
            continue
        exitc = [f for f in cands if f["exit"] == c["exit"]]
        exact = [f for f in cands
                 if f["exit"] == c["exit"] and f["failsum"] == c["failsum"]]
        st = "MATCH" if exact else ("EXIT-ONLY" if exitc else "NO-MATCH")
        out.append(f"{st}\tcommitted-{c['idx']:02d}\t{c['mode']}\t"
                   f"exit {c['exit']} failsum_equal={bool(exact)}")
        if not exact:
            mism.append(f"committed-{c['idx']:02d} {c['mode']} {st}: "
                        f"committed='{c['failsum'][:110]}' "
                        f"fresh='{(cands[0]['failsum'] if cands else '-')[:110]}'")
    Path(HERE / "ledger-compare-mode.tsv").write_text("\n".join(out) + "\n")

    # --- receipt compare for committed-ledger-named receipts ---
    lines, diffs = [], []
    for c in crows:
        rel = c["receipt"].split("audio-shokunin/")[-1] if "audio-shokunin" in c["receipt"] else c["receipt"]
        cb = git_show(rel)
        cands = fresh_by_mode.get(c["mode"], [])
        fbytes = []
        for f in cands:
            try:
                fbytes.append((f, Path(f["receipt"]).read_bytes()))
            except OSError:
                pass
        hit = [f for (f, b) in fbytes if b == cb]
        if hit:
            cls = "EQUAL"
        else:
            norm = cb.replace(ENV_INFIX.encode(), b"corpus/")
            hitn = [f for (f, b) in fbytes if b == norm]
            cls = "EQUAL-MOD-PATHS" if hitn else "DIFFER"
        lines.append(f"{cls}\tcommitted-{c['idx']:02d}\t{c['mode']}\t{sha(cb)[:16]}\t"
                     f"fresh_candidates={len(fbytes)}")
        if cls == "DIFFER" and fbytes:
            diffs.append((c, fbytes[0][1], cb))
    Path(HERE / "receipt-compare.tsv").write_text("\n".join(lines) + "\n")

    # --- full-set membership: fresh receipt sha in committed same-mode set? ---
    mem = []
    for f in frows:
        try:
            b = Path(f["receipt"]).read_bytes()
        except OSError:
            mem.append(f"MISSING\trow-{f['idx']:02d}\t{f['mode']}")
            continue
        inset = sha(b) in sha_sets.get(f["mode"], set())
        mem.append(f"{'INSET' if inset else 'NOT-INSET'}\trow-{f['idx']:02d}\t"
                   f"{f['mode']}\t{sha(b)[:16]}\tset_size={len(sha_sets.get(f['mode'], set()))}")
    Path(HERE / "receipt-membership.tsv").write_text("\n".join(mem) + "\n")

    # --- summary ---
    n_eq = sum(1 for l in lines if l.startswith("EQUAL\t"))
    n_mp = sum(1 for l in lines if l.startswith("EQUAL-MOD-PATHS"))
    n_df = sum(1 for l in lines if l.startswith("DIFFER"))
    n_in = sum(1 for l in mem if l.startswith("INSET"))
    print(f"committed-ledger rows: {len(crows)}; fresh rows: {len(frows)}")
    print(f"ledger mode-keyed: {sum(1 for l in out if l.startswith('MATCH'))} MATCH, "
          f"{len(mism)} anomalies -> ledger-compare-mismatches.txt")
    Path(HERE / "ledger-compare-mismatches.txt").write_text("\n".join(mism) + "\n")
    print(f"committed-receipt anchors: {n_eq} EQUAL, {n_mp} EQUAL-MOD-PATHS, {n_df} DIFFER")
    print(f"membership: {n_in}/{len(frows)} fresh receipts byte-in-committed-set")
    for c, fb, cb in diffs[:5]:
        print("DIFFER sample:", c["mode"])


if __name__ == "__main__":
    main()
