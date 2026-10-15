#!/usr/bin/env python3
"""r78-baseline semantic compare (adapted from r77; anchor-pinned to 731937c):
for each NOT-INSET / DIFFER fresh receipt, walk both JSON trees leaf-by-leaf
and classify:
  EQUAL                  identical bytes
  EQUAL-ANCHORED-TAIL    same structure; every differing leaf is
                         'corpus/'-anchored in both with equal post-anchor
                         suffix (env infix is the only delta)
  JITTER-LEAVES          same structure; differing leaves confined to the
                         declared jitter key set (wall_s, wchan, waited_s,
                         pacing wall clocks, timestamps)
  STRUCTURE-DIFF         key sets differ
  CONTENT-DIFF           same structure, non-path non-jitter leaf differs
Also compares the committed-anchor-less rows (capture-r77 [new], capture-r76,
consumers2-r75, lavfsweep-r74, consumers-r73) against their untracked canonical
sibling receipts.
Writes semantic-compare.txt.
"""
import json
import re
import subprocess as sp
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ANCHOR = "731937ccf731c711b54942d22ae4f32b7683c498"
ENV_INFIX = "corpus/live/r78-baseline/measure-env/corpus/"
JITTER_KEYS = {"wall_s", "wchan", "waited_s", "delivery_window_s",
               "playback_paced", "starved_ok"}


def leaves(obj, prefix=""):
    if isinstance(obj, dict):
        for k in sorted(obj):
            yield from leaves(obj[k], f"{prefix}.{k}" if prefix else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from leaves(v, f"{prefix}[{i}]")
    else:
        yield prefix, obj


def keys_and_vals(obj):
    return dict(leaves(obj))


def anchored_tail(v):
    """post-'corpus/' suffix if the value carries a corpus/ anchor
    (LAST occurrence — env paths carry a second corpus/ inside the
    measure-env infix, and _tail() truncation may clip the prefix)."""
    if isinstance(v, str) and "corpus/" in v:
        return v.rsplit("corpus/", 1)[1]
    return None


def classify(fresh_path, committed_bytes, label):
    fb = Path(fresh_path).read_bytes()
    if fb == committed_bytes:
        return f"EQUAL\t{label}"
    try:
        f = json.loads(fb)
        c = json.loads(committed_bytes)
    except Exception:
        return f"UNPARSEABLE\t{label}"
    fk, ck = keys_and_vals(f), keys_and_vals(c)
    if set(fk) != set(ck):
        only_f = sorted(set(fk) - set(ck))[:5]
        only_c = sorted(set(ck) - set(fk))[:5]
        return (f"STRUCTURE-DIFF\t{label}\tonly-fresh={only_f}\t"
                f"only-committed={only_c}")
    pathdiff, jitter, content = [], [], []
    for k in fk:
        if fk[k] == ck[k]:
            continue
        # path-embedding class: replacing the env infix inside the fresh
        # leaf with 'corpus/' restores byte-equality with the committed leaf
        if isinstance(fk[k], str) and ENV_INFIX in fk[k] \
                and fk[k].replace(ENV_INFIX, "corpus/") == ck[k]:
            pathdiff.append(k)
            continue
        fa, ca = anchored_tail(fk[k]), anchored_tail(ck[k])
        if fa is not None and ca is not None and fa == ca \
                and ENV_INFIX in str(fk[k]):
            pathdiff.append(k)
        elif k.split(".")[-1].split("[")[0] in JITTER_KEYS:
            jitter.append(k)
        else:
            content.append(k)
    if content:
        return (f"CONTENT-DIFF\t{label}\tkeys={content[:6]}\t"
                f"path_embedded={len(pathdiff)}\tjitter={len(jitter)}")
    if jitter:
        return (f"JITTER-LEAVES\t{label}\tjitter={jitter[:8]}\t"
                f"path_embedded={len(pathdiff)}")
    return (f"EQUAL-ANCHORED-TAIL\t{label}\tpath_embedded={len(pathdiff)}\t"
            f"keys={pathdiff[:6]}")


def main():
    lines = []
    # (a) committed-ledger-anchored DIFFER rows (from receipt-compare.tsv)
    #     receipt-compare.tsv rows: <CLASS>\t<idx:03d>\t<mode>\t<sha16>
    committed = sp.run(
        ["git", "show", f"{ANCHOR}:corpus/live/r70-author/ledger-r71.tsv"],
        cwd=REPO, capture_output=True, text=True).stdout
    cby_mode = {}
    for line in committed.splitlines():
        p = line.split("\t")
        if len(p) >= 4:
            cby_mode.setdefault(
                re.sub(r"^\d{8}T\d+Z-?", "", Path(p[2]).parent.name), []).append(
                    (int(p[0]), p[2]))
    fresh = []
    for line in (HERE / "ledger-r78-baseline.tsv").read_text().splitlines():
        p = line.split("\t")
        fresh.append({"idx": int(p[0]), "receipt": p[2]})
    for l in (HERE / "receipt-compare.tsv").read_text().splitlines():
        if not l.startswith("DIFFER"):
            continue
        parts = l.split("\t")
        fidx, mode = int(parts[1]), parts[2]
        if mode not in cby_mode:
            lines.append(f"NO-COMMITTED-ANCHOR\tfresh-{fidx:03d}\t{mode}")
            continue
        ci, creceipt = cby_mode[mode][0]
        crel = creceipt.split("audio-shokunin/")[-1]
        cb = sp.run(["git", "show", f"{ANCHOR}:{crel}"], cwd=REPO,
                    capture_output=True).stdout
        frc = [f for f in fresh if f["idx"] == fidx]
        if not frc:
            lines.append(f"NO-FRESH\tcommitted-{ci:02d}\t{mode}")
            continue
        lines.append(classify(frc[0]["receipt"], cb,
                              f"committed-{ci:02d}\t{mode}"))
    # (b) rows with no committed anchor vs canonical sibling receipts
    # (untracked corpus/live/runs/*-<mode>/measurements.json)
    for mode in ("capture-r77", "capture-r76", "consumers2-r75",
                 "lavfsweep-r74", "consumers-r73"):
        frow = [f for f in fresh if f["receipt"].endswith(f"-{mode}/measurements.json")]
        canon = sorted(REPO.glob(f"corpus/live/runs/*-{mode}/measurements.json"))
        if frow and canon:
            for cp in canon:
                lines.append(classify(frow[0]["receipt"], cp.read_bytes(),
                                      f"fresh-{mode} vs {cp.parent.name}"))
    (HERE / "semantic-compare.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
