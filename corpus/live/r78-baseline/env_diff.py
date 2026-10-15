#!/usr/bin/env python3
"""r78-baseline environmental-set characterization: full leaf-by-leaf diff of
the two capture-family rows against their prior canonical references.

 (1) fresh capture-r76 (row 03) vs the r77-baseline Phase-1 capture-r76 receipt
     (corpus/live/r77-baseline/measure-env/.../20261014T194043238882Z-capture-r76)
 (2) fresh capture-r77 (row 02) vs the r77 folded-run reference receipt
     (corpus/live/runs/20261014T210316456683Z-capture-r77)
 (3) fresh capture-r77 vs all 12 canonical capture-r77 sibling receipts

Every differing leaf is printed with both values (truncated), so the report can
name the environmental set exactly instead of asserting it.
Writes env-diff.txt.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
FRESH_R76 = (HERE / "measure-env" / "corpus" / "live" / "runs"
             / "20261014T213136105621Z-capture-r76" / "measurements.json")
REF_R76 = (REPO / "corpus" / "live" / "r77-baseline" / "measure-env" / "corpus"
           / "live" / "runs" / "20261014T194043238882Z-capture-r76"
           / "measurements.json")
FRESH_R77 = (HERE / "measure-env" / "corpus" / "live" / "runs"
             / "20261014T213014753652Z-capture-r77" / "measurements.json")
REF_R77 = (REPO / "corpus" / "live" / "runs"
           / "20261014T210316456683Z-capture-r77" / "measurements.json")


def leaves(obj, prefix=""):
    if isinstance(obj, dict):
        for k in sorted(obj):
            yield from leaves(obj[k], f"{prefix}.{k}" if prefix else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from leaves(v, f"{prefix}[{i}]")
    else:
        yield prefix, obj


def trunc(v, n=160):
    s = json.dumps(v)
    return s if len(s) <= n else s[:n] + "…"


def diff(a, b, label, out):
    fa, fb = dict(leaves(a)), dict(leaves(b))
    only_a = sorted(set(fa) - set(fb))
    only_b = sorted(set(fb) - set(fa))
    out.append(f"=== {label}")
    out.append(f"    leaves: fresh={len(fa)} ref={len(fb)} "
               f"only-fresh={len(only_a)} only-ref={len(only_b)}")
    for k in only_a:
        out.append(f"    ONLY-FRESH {k} = {trunc(fa[k])}")
    for k in only_b:
        out.append(f"    ONLY-REF   {k} = {trunc(fb[k])}")
    nd = 0
    for k in sorted(set(fa) & set(fb)):
        if fa[k] == fb[k]:
            continue
        nd += 1
        out.append(f"    DIFF {k}\n        fresh={trunc(fa[k])}\n"
                   f"        ref  ={trunc(fb[k])}")
    out.append(f"    differing shared leaves: {nd}")
    return out


def main():
    out = []
    if FRESH_R76.is_file() and REF_R76.is_file():
        diff(json.loads(FRESH_R76.read_bytes()), json.loads(REF_R76.read_bytes()),
             "fresh capture-r76 (r78 row 03) vs r77-baseline Phase-1 capture-r76",
             out)
    else:
        out.append(f"MISSING: {FRESH_R76} / {REF_R76}")
    if FRESH_R77.is_file() and REF_R77.is_file():
        diff(json.loads(FRESH_R77.read_bytes()), json.loads(REF_R77.read_bytes()),
             "fresh capture-r77 (r78 row 02) vs r77 folded reference "
             "(20261014T210316456683Z)", out)
    else:
        out.append(f"MISSING: {FRESH_R77} / {REF_R77}")
    # (3) sibling partition for capture-r77
    canon = sorted(REPO.glob("corpus/live/runs/*-capture-r77/measurements.json"))
    out.append(f"=== fresh capture-r77 vs {len(canon)} canonical siblings")
    if FRESH_R77.is_file():
        fb = FRESH_R77.read_bytes()
        f = json.loads(fb)
        for cp in canon:
            cb = cp.read_bytes()
            if cb == fb:
                out.append(f"    EQUAL {cp.parent.name}")
                continue
            c = json.loads(cb)
            fk, ck = dict(leaves(f)), dict(leaves(c))
            if set(fk) != set(ck):
                only_f = sorted(set(fk) - set(ck))[:6]
                only_c = sorted(set(ck) - set(fk))[:6]
                out.append(f"    STRUCTURE-DIFF {cp.parent.name} "
                           f"only-fresh={only_f} only-ref={only_c}")
                continue
            content = [k for k in fk if fk[k] != ck[k]]
            out.append(f"    CONTENT-DIFF({len(content)}) {cp.parent.name} "
                       f"keys={content[:6]}")
    (HERE / "env-diff.txt").write_text("\n".join(out) + "\n")
    print("\n".join(out[:200]))
    print(f"\n[written to {HERE / 'env-diff.txt'}; {len(out)} lines]")


if __name__ == "__main__":
    main()
