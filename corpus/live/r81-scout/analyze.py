#!/usr/bin/env python3
"""Summarize r81 leg receipts: per-leg modal rc/class/links/node-identity."""
import json
import sys
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent
RUNS = OUT / "runs"


def load(stage, leg):
    d = RUNS / stage / leg
    return json.load(open(d / "receipt.json")) if (d / "receipt.json").exists() else None


def summarize(stage, legs=None, show_props=True):
    base = RUNS / stage
    names = sorted({p.name.rsplit("_r", 1)[0] for p in base.iterdir()}) if base.exists() else []
    if legs:
        names = [n for n in names if n in legs]
    for name in names:
        reps = [load(stage, "%s_r%d" % (name, i)) for i in range(3)]
        reps = [r for r in reps if r]
        if not reps:
            continue
        rcs = Counter((r["rc"], r["err_class"]) for r in reps)
        print("== %s   reps=%d" % (name, len(reps)))
        for (rc, cls), n in rcs.items():
            print("   rc=%-5s class=%-22s x%d" % (rc, cls, n))
        for r in reps:
            if r["err_class"] or r["rc"] not in (0, -15, -9):
                print("      stderr:", (r["stderr_head"] or [""])[0][:140])
        # links across all samples of all reps
        lk = Counter()
        for r in reps:
            for s in r["samples"]:
                for l in s["g"].get("links", []):
                    if "gst" in l or "r81" in l:
                        lk[l] += 1
        for l, n in lk.most_common(6):
            print("   link x%-2d %s" % (n, l))
        # node identity (union of my_nodes keys + props)
        seen = {}
        for r in reps:
            for s in r["samples"]:
                for nm, v in s["g"]["my_nodes"].items():
                    if "gst" in nm or "r81" in nm:
                        seen.setdefault(nm, Counter())[json.dumps(
                            {k: v[k] for k in ("class", "client")}, sort_keys=True)] += 1
                        if show_props and v.get("props"):
                            seen.setdefault(nm + "|props", Counter())[json.dumps(
                                v["props"], sort_keys=True)] += 1
        for nm, c in seen.items():
            for v, n in c.most_common(2):
                print("   node %-26s x%-2d %s" % (nm, n, v[:340]))
        # out shape
        outs = Counter(json.dumps(r["out"], sort_keys=True) for r in reps if r["out"])
        for v, n in outs.items():
            print("   out x%d %s" % (n, v[:200]))
        # samples sizes
        for r in reps[:1]:
            print("   sizes:", [(s["t"], s["size"]) for s in r["samples"]])
            if r["actions"]:
                print("   actions:", r["actions"])
        print()


if __name__ == "__main__":
    stage = sys.argv[1]
    legs = sys.argv[2].split(",") if len(sys.argv) > 2 else None
    summarize(stage, legs)
