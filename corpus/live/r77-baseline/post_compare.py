#!/usr/bin/env python3
"""r77-baseline POST-COMMIT comparison.

 (a) post ledger (post env, pinned to author commit 65790f13) vs the Phase-1
     ledger (frozen env, pinned to b0b5d4d): row N of both is the same flag
     (rerun_post.py imports MODES from rerun.py), so the compare is index-exact
     — same exit, same failure summary, and receipt-stable modulo the env
     infix and the declared host-drift leaves;
 (b) post ledger vs the r76 canonical receipts (r76-baseline ledger, 125 rows)
     — the round's prior-row stability obligation, re-checked on the committed
     post-move bytes.

Leaf classification as in prior_compare.py: EQUAL / EQUAL-MOD-PATHS /
DECLARED-DRIFT (pw_capture_ports inventory, aplay stderr_tail scrub window,
hw-contention device rows) / JITTER-LEAVES / STRUCTURE-DIFF / UNDECLARED-DIFF.
Writes post-rows-stable.txt + post-receipt-compare.tsv.
"""
import json
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
POST_LEDGER = HERE / "ledger-r77-baseline-post.tsv"
PRE_LEDGER = HERE / "ledger-r77-baseline.tsv"
PRIOR_LEDGER = REPO / "corpus" / "live" / "r76-baseline" / "ledger-r76-baseline.tsv"
POST_INFIX = "corpus/live/r77-baseline/measure-env-post/corpus/"
PRE_INFIX = "corpus/live/r77-baseline/measure-env/corpus/"
PRIOR_INFIX = "corpus/live/r76-baseline/measure-env/corpus/"
JITTER_KEYS = {"wall_s", "wchan", "waited_s", "delivery_window_s",
               "playback_paced", "starved_ok"}
DECLARED = [
    re.compile(r"pw_capture_ports"),
    re.compile(r"stderr_tail"),
    re.compile(r"device_axis\.legs\.sysdefault"),
    re.compile(r"bounded\.legs\.ffmpeg_alsa_t"),
    re.compile(r"sever\.cells\.arecord_(term|kill)\.device"),
]


def mode_of(p):
    return re.sub(r"^\d{8}T\d+Z-?", "", Path(p).parent.name) or "?"


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


def classify(a_bytes, b_bytes, label, a_infix, b_infix):
    if a_bytes == b_bytes:
        return f"EQUAL\t{label}", []
    try:
        a = json.loads(a_bytes)
        b = json.loads(b_bytes)
    except Exception:
        return f"UNPARSEABLE\t{label}", []
    ak, bk = dict(leaves(a)), dict(leaves(b))
    if set(ak) != set(bk):
        return (f"STRUCTURE-DIFF\t{label}\tonly-a={sorted(set(ak)-set(bk))[:5]}\t"
                f"only-b={sorted(set(bk)-set(ak))[:5]}"), []
    pathdiff, jitter, drift, content = [], [], [], []
    for k in ak:
        if ak[k] == bk[k]:
            continue
        if isinstance(ak[k], str) and a_infix in ak[k] \
                and ak[k].replace(a_infix, b_infix) == bk[k]:
            pathdiff.append(k)
            continue
        ta, tb = anchored_tail(ak[k]), anchored_tail(bk[k])
        if ta is not None and tb is not None and ta == tb \
                and (a_infix in str(ak[k]) or b_infix in str(bk[k])):
            pathdiff.append(k)
        elif any(rx.search(k) for rx in DECLARED):
            drift.append(k)
        elif k.split(".")[-1].split("[")[0] in JITTER_KEYS:
            jitter.append(k)
        else:
            content.append(k)
    if content:
        return (f"UNDECLARED-DIFF\t{label}\tkeys={content[:8]}\t"
                f"declared={len(drift)}\tjitter={len(jitter)}\t"
                f"path={len(pathdiff)}"), content
    if drift:
        return (f"DECLARED-DRIFT\t{label}\tleaves={drift[:8]}\t"
                f"jitter={len(jitter)}\tpath={len(pathdiff)}"), []
    if jitter:
        return (f"JITTER-LEAVES\t{label}\tjitter={jitter[:8]}\t"
                f"path={len(pathdiff)}"), []
    return f"EQUAL-MOD-PATHS\t{label}\tpath={len(pathdiff)}", []


def rows_stable(post, ref, lines, tag):
    by_mode = defaultdict(list)
    for r in post:
        by_mode[r["mode"]].append(r)
    counts = defaultdict(int)
    for r in ref:
        cands = by_mode.get(r["mode"], [])
        if not cands:
            counts["NO-FRESH-ROW"] += 1
            lines.append(f"{tag} NO-FRESH-ROW\tref-{r['idx']:02d}\t{r['mode']}")
            continue
        exact = [c for c in cands if c["exit"] == r["exit"] and c["failsum"] == r["failsum"]]
        if exact:
            counts["ROW-STABLE"] += 1
            continue
        cls = "ROW-EXIT-ONLY" if any(c["exit"] == r["exit"] for c in cands) else "ROW-NO-MATCH"
        counts[cls] += 1
        lines.append(f"{tag} {cls}\tref-{r['idx']:02d}\t{r['mode']}\n"
                     f"    ref_failsum='{r['failsum'][:150]}'\n"
                     f"    post_failsum='{cands[0]['failsum'][:150]}'")
    return counts


def main():
    post = read_ledger(POST_LEDGER)
    pre = read_ledger(PRE_LEDGER)
    prior = read_ledger(PRIOR_LEDGER)
    lines = [f"post ledger rows={len(post)} (env pinned 65790f13)",
             f"phase-1 ledger rows={len(pre)} (env pinned b0b5d4d)",
             f"r76 canonical ledger rows={len(prior)}"]

    # (a) index-exact post vs phase-1
    lines.append("--- (a) post vs phase-1, index-exact (same MODES ordering):")
    a_counts = defaultdict(int)
    rlines = []
    undeclared = []
    for p, q in zip(pre, post):
        assert p["mode"] == q["mode"], (p["idx"], q["mode"])
        if p["exit"] == q["exit"] and p["failsum"] == q["failsum"]:
            a_counts["ROW-STABLE"] += 1
        else:
            a_counts["ROW-DIFF"] += 1
            lines.append(f"ROW-DIFF row-{p['idx']:02d} {p['mode']}\n"
                         f"    phase1 exit={p['exit']} post exit={q['exit']}\n"
                         f"    phase1='{p['failsum'][:150]}'\n"
                         f"    post   ='{q['failsum'][:150]}'")
        try:
            pb = Path(p["receipt"]).read_bytes()
            qb = Path(q["receipt"]).read_bytes()
        except OSError:
            rlines.append(f"MISSING\trow-{p['idx']:02d}\t{p['mode']}")
            a_counts["MISSING"] += 1
            continue
        cls, content = classify(qb, pb, f"row-{p['idx']:02d}\t{p['mode']}",
                                POST_INFIX, PRE_INFIX)
        rlines.append(cls)
        a_counts[cls.split("\t")[0]] += 1
        if content:
            undeclared.append(f"row-{p['idx']:02d} {p['mode']}: {content[:8]}")
    lines.append(f"(a) row-level: {dict(a_counts)}")

    # (b) post vs r76 canonical
    lines.append("--- (b) post vs r76 canonical receipts:")
    b_counts = rows_stable(post, prior, lines, "r76")
    lines.append(f"(b) row-level: {dict(b_counts)}")
    rlines.append("=== post-vs-r76 receipt-level ===")
    by_mode = defaultdict(list)
    for r in post:
        by_mode[r["mode"]].append(r)
    c_counts = defaultdict(int)
    for r in prior:
        cands = by_mode.get(r["mode"], [])
        pp = Path(r["receipt"])
        if not pp.is_file() or not cands:
            c_counts["SKIP"] += 1
            continue
        cls, content = classify(Path(cands[0]["receipt"]).read_bytes(),
                                pp.read_bytes(), f"r76-{r['idx']:02d}\t{r['mode']}",
                                POST_INFIX, PRIOR_INFIX)
        rlines.append(cls)
        c_counts[cls.split("\t")[0]] += 1
        if content:
            undeclared.append(f"r76-{r['idx']:02d} {r['mode']}: {content[:8]}")
    lines.append(f"(b) receipt-level vs r76 canonical: {dict(c_counts)}")
    lines.append("--- receipt-level (post vs phase-1):")
    lines += rlines
    (HERE / "post-rows-stable.txt").write_text("\n".join(lines) + "\n")
    (HERE / "post-receipt-compare.tsv").write_text("\n".join(rlines) + "\n")
    if undeclared:
        (HERE / "post-undeclared-diffs.txt").write_text("\n".join(undeclared) + "\n")
    print("\n".join(lines[:6]))
    print(f"(a) row-level: {dict(a_counts)}")
    print(f"(b) row-level: {dict(b_counts)}")
    print(f"(b) receipt-level vs r76: {dict(c_counts)}")
    print(f"undeclared diffs: {len(undeclared)}")


if __name__ == "__main__":
    main()
