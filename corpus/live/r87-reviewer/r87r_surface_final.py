#!/usr/bin/env python3
"""r87 reviewer — pid-normalized verdict-surface comparison.

Wraps r87r_surface2.surfaces(), normalizes the probe pid out of the
sink names, and diffs the four receipts pairwise into one summary.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from r87r_surface2 import flat, surfaces  # noqa: E402

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
RECEIPTS = {
    "A": REPO / "corpus/live/runs/20261016T070036115509Z-pwbind-r87/measurements.json",
    "B": REPO / "corpus/live/runs/20261016T070305393338Z-pwbind-r87/measurements.json",
    "r87r1": REPO / "corpus/live/r87-reviewer/runs/r87r1-live.json",
    "r87r2": REPO / "corpus/live/r87-reviewer/runs/r87r2-live.json",
}


def norm(v):
    if isinstance(v, str):
        return re.sub(r"r87a_(ns2?)_\d+", r"r87a_\1_<pid>", v)
    return v


def main():
    flatmaps = {}
    for tag, p in RECEIPTS.items():
        f = flat(surfaces(str(p)))
        flatmaps[tag] = {k: norm(v) for k, v in f.items()}
    pairs = [("A", "B"), ("A", "r87r2"), ("B", "r87r2"), ("A", "r87r1"),
             ("B", "r87r1")]
    out = {"fields": len(flatmaps["A"]), "pairs": {}}
    for a, b in pairs:
        fa, fb = flatmaps[a], flatmaps[b]
        keys = sorted(set(fa) | set(fb))
        diffs = [{"key": k, "a": fa.get(k), "b": fb.get(k)}
                 for k in keys if fa.get(k) != fb.get(k)]
        out["pairs"][f"{a}-vs-{b}"] = {"diffs": len(diffs),
                                       "diff_keys": diffs}
    dest = REPO / "corpus/live/r87-reviewer/runs/vsurface-summary.json"
    dest.write_text(json.dumps(out, indent=1) + "\n")
    for k, v in out["pairs"].items():
        print(k, "diffs:", v["diffs"])
        for d in v["diff_keys"]:
            print("   ", d["key"], "|", str(d["a"])[:60], "->",
                  str(d["b"])[:60])
    print("receipt:", dest)


if __name__ == "__main__":
    main()
