#!/usr/bin/env python3
"""r77-baseline prior-row stability vs the r76 canonical receipts.

Prior canonical set = the r76-baseline ledger (corpus/live/r76-baseline/
ledger-r76-baseline.tsv, 125 rows) — the freshest full-battery receipt set in
existence (no committed ledger past ledger-r71.tsv; r76-author carries none).
Every one of those 125 modes must appear in the fresh 126-row ledger with the
same exit and the same failure summary, and its receipt must be byte-stable
after the displaced-tree infix rewrite (r76 env infix -> r77 env infix).

Leaf-walk classification of every non-byte-equal pair:
  EQUAL-MOD-PATHS   every differing leaf is corpus/-anchored with equal
                    post-anchor suffix (env infix is the only delta)
  DECLARED-DRIFT    differing leaves confined to the declared host-drift
                    leaves: pw_capture_ports inventory, aplay stderr_tail
                    scrub window, hw-contention rows (device_axis sysdefault
                    leg, bounded ffmpeg_alsa_t leg, arecord_{term,kill}
                    sever device cells)
  JITTER-LEAVES     differing leaves confined to the declared wall-clock
                    jitter key set
  STRUCTURE-DIFF    key sets differ
  UNDECLARED-DIFF   same structure, non-path non-jitter non-declared leaf
Writes prior-rows-stable.txt + prior-receipt-compare.tsv.
"""
import json
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PRIOR_LEDGER = REPO / "corpus" / "live" / "r76-baseline" / "ledger-r76-baseline.tsv"
FRESH_LEDGER = HERE / "ledger-r77-baseline.tsv"
PRIOR_INFIX = "corpus/live/r76-baseline/measure-env/corpus/"
FRESH_INFIX = "corpus/live/r77-baseline/measure-env/corpus/"
JITTER_KEYS = {"wall_s", "wchan", "waited_s", "delivery_window_s",
               "playback_paced", "starved_ok"}
# declared host-drift leaves (r76 verifier/reviewer/simplifier fold set)
DECLARED = [
    re.compile(r"pw_capture_ports"),
    re.compile(r"stderr_tail"),
    re.compile(r"device_axis\.legs\.sysdefault"),
    re.compile(r"bounded\.legs\.ffmpeg_alsa_t"),
    re.compile(r"sever\.cells\.arecord_(term|kill)\.device"),
]


def mode_of(receipt_path):
    d = Path(receipt_path).parent.name
    return re.sub(r"^\d{8}T\d+Z-?", "", d) or "?"


def read_ledger(path):
    rows = []
    for line in path.read_text().splitlines():
        p = line.split("\t")
        if len(p) >= 4:
            rows.append({"idx": int(p[0]), "exit": p[1], "receipt": p[2],
                         "failsum": p[3], "mode": mode_of(p[2])})
    return rows


def leaves(obj, prefix=""):
    if isinstance(obj, dict):
        for k in sorted(obj):
            yield from leaves(obj[k], f"{prefix}.{k}" if prefix else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from leaves(v, f"{prefix}[{i}]")
    else:
        yield prefix, obj


def anchored_tail(v):
    if isinstance(v, str) and "corpus/" in v:
        return v.rsplit("corpus/", 1)[1]
    return None


def declared(key):
    return any(rx.search(key) for rx in DECLARED)


def classify(fresh_bytes, prior_bytes, label):
    if fresh_bytes == prior_bytes:
        return f"EQUAL\t{label}", []
    try:
        f = json.loads(fresh_bytes)
        p = json.loads(prior_bytes)
    except Exception:
        return f"UNPARSEABLE\t{label}", []
    fk = dict(leaves(f))
    pk = dict(leaves(p))
    if set(fk) != set(pk):
        only_f = sorted(set(fk) - set(pk))[:5]
        only_p = sorted(set(pk) - set(fk))[:5]
        return (f"STRUCTURE-DIFF\t{label}\tonly-fresh={only_f}\t"
                f"only-prior={only_p}"), []
    pathdiff, jitter, drift, content = [], [], [], []
    for k in fk:
        if fk[k] == pk[k]:
            continue
        if isinstance(fk[k], str) and PRIOR_INFIX in pk[k] \
                and fk[k].replace(FRESH_INFIX, PRIOR_INFIX) == pk[k]:
            pathdiff.append(k)
            continue
        fa, ca = anchored_tail(fk[k]), anchored_tail(pk[k])
        if fa is not None and ca is not None and fa == ca \
                and (FRESH_INFIX in str(fk[k]) or PRIOR_INFIX in str(pk[k])):
            pathdiff.append(k)
        elif declared(k):
            drift.append(k)
        elif k.split(".")[-1].split("[")[0] in JITTER_KEYS:
            jitter.append(k)
        else:
            content.append(k)
    if content:
        return (f"UNDECLARED-DIFF\t{label}\tkeys={content[:8]}\t"
                f"declared_drift={len(drift)}\tjitter={len(jitter)}\t"
                f"path_embedded={len(pathdiff)}"), content
    if drift:
        return (f"DECLARED-DRIFT\t{label}\tleaves={drift[:8]}\t"
                f"jitter={len(jitter)}\tpath_embedded={len(pathdiff)}"), []
    if jitter:
        return (f"JITTER-LEAVES\t{label}\tjitter={jitter[:8]}\t"
                f"path_embedded={len(pathdiff)}"), []
    return (f"EQUAL-MOD-PATHS\t{label}\tpath_embedded={len(pathdiff)}\t"
            f"keys={pathdiff[:6]}"), []


def main():
    prior = read_ledger(PRIOR_LEDGER)
    fresh = read_ledger(FRESH_LEDGER)
    fresh_by_mode = defaultdict(list)
    for r in fresh:
        fresh_by_mode[r["mode"]].append(r)

    lines = [f"prior ledger: {PRIOR_LEDGER.relative_to(REPO)} rows={len(prior)}",
             f"fresh ledger: {FRESH_LEDGER.relative_to(REPO)} rows={len(fresh)}"]
    # --- row-level (exit, failsum) stability, mode-keyed ---
    row_cls = defaultdict(int)
    for p in prior:
        cands = fresh_by_mode.get(p["mode"], [])
        if not cands:
            row_cls["NO-FRESH-ROW"] += 1
            lines.append(f"NO-FRESH-ROW\tprior-{p['idx']:02d}\t{p['mode']}")
            continue
        exact = [f for f in cands
                 if f["exit"] == p["exit"] and f["failsum"] == p["failsum"]]
        if exact:
            row_cls["ROW-STABLE"] += 1
            continue
        exit_only = [f for f in cands if f["exit"] == p["exit"]]
        cls = "ROW-EXIT-ONLY" if exit_only else "ROW-NO-MATCH"
        row_cls[cls] += 1
        lines.append(f"{cls}\tprior-{p['idx']:02d}\t{p['mode']}\t"
                     f"prior_exit={p['exit']} fresh_exit={cands[0]['exit']}\n"
                     f"    prior_failsum='{p['failsum'][:150]}'\n"
                     f"    fresh_failsum='{cands[0]['failsum'][:150]}'")
    lines.append(f"row-level: {dict(row_cls)}")

    # --- receipt-level stability ---
    rlines = []
    cls_count = defaultdict(int)
    undeclared = []
    for p in prior:
        cands = fresh_by_mode.get(p["mode"], [])
        pp = Path(p["receipt"])
        if not pp.is_file():
            rlines.append(f"PRIOR-MISSING\tprior-{p['idx']:02d}\t{p['mode']}")
            cls_count["PRIOR-MISSING"] += 1
            continue
        pb = pp.read_bytes()
        if not cands:
            rlines.append(f"NO-FRESH\tprior-{p['idx']:02d}\t{p['mode']}")
            cls_count["NO-FRESH"] += 1
            continue
        fb = Path(cands[0]["receipt"]).read_bytes()
        cls, content = classify(fb, pb, f"prior-{p['idx']:02d}\t{p['mode']}")
        cls_count[cls.split("\t")[0]] += 1
        rlines.append(cls)
        if content:
            undeclared.append(f"prior-{p['idx']:02d} {p['mode']}: {content[:8]}")
    lines.append("--- receipt-level (fresh r77 vs prior r76 receipt, infix-rewritten):")
    lines += rlines
    lines.append(f"receipt-level counts: {dict(cls_count)}")
    (HERE / "prior-rows-stable.txt").write_text("\n".join(lines) + "\n")
    (HERE / "prior-receipt-compare.tsv").write_text("\n".join(rlines) + "\n")
    if undeclared:
        (HERE / "prior-undeclared-diffs.txt").write_text("\n".join(undeclared) + "\n")
    print("\n".join(lines))
    print(f"\nreceipt-level counts: {dict(cls_count)}")


if __name__ == "__main__":
    main()
