#!/usr/bin/env python3
"""r90-simplifier: run every comparison pair, one receipt per pair + a
one-line summary."""
import glob
import os
import subprocess
import sys

EVID = "/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r90-simplifier"
R = "/home/vgpnk/Projects/shokunin/r90s"


def run_dir(tree, stamp):
    hits = glob.glob(f"{R}/{tree}/corpus/live/runs/{stamp}*wpstate-r90")
    assert len(hits) == 1, (tree, stamp, hits)
    return hits[0]


RUN = {
    "base.before1": run_dir("base", "20261016T100056"),
    "f1.after1": run_dir("f1", "20261016T100215"),
    "base.before2": run_dir("base", "20261016T100335"),
    "f2.after2": run_dir("f2", "20261016T100500"),
    "f1.after1b": run_dir("f1", "20261016T100622"),
    "base.before3": run_dir("base", "20261016T100744"),
    "f1.after1c": run_dir("f1", "20261016T100947"),
    "f1.after1d": run_dir("f1", "20261016T101111"),
    "base.before4": run_dir("base", "20261016T101234"),
}

PAIRS = [
    ("base.before2", "f2.after2",
     "FOLD-2 primary pair (pristine -> folded, both green)"),
    ("base.before2", "f1.after1c",
     "FOLD-1 primary pair (pristine -> folded, both green)"),
    ("base.before1", "f1.after1d",
     "FOLD-1 second pair (pristine -> folded, both green)"),
    ("base.before2", "f1.after1",
     "FOLD-1 pair with the host race firing (folded run red)"),
    ("base.before1", "base.before2",
     "CONTROL identical bytes (pristine vs pristine)"),
    ("base.before2", "base.before3",
     "CONTROL identical bytes (pristine vs pristine; 2nd red)"),
    ("base.before3", "base.before4",
     "CONTROL identical bytes (pristine vs pristine; 3rd)"),
    ("f1.after1c", "f1.after1d",
     "CONTROL folded vs folded (same folded bytes)"),
]

out_lines = []
for a, b, note in PAIRS:
    path = f"{EVID}/cmp-{a}-vs-{b}.txt"
    with open(path, "w") as fh:
        rc = subprocess.call([sys.executable, f"{EVID}/compare_runs.py",
                              RUN[a], RUN[b]], stdout=fh,
                             stderr=subprocess.STDOUT)
    verdict = "?"
    with open(path) as fh:
        for ln in fh:
            if ln.startswith("VERDICT"):
                verdict = ln.strip()[len("VERDICT:"):].strip()
    out_lines.append(f"{a:14s} -> {b:14s} rc={rc}  {verdict}\n"
                     f"{'':34s} # {note}")
with open(f"{EVID}/summary.txt", "w") as fh:
    fh.write("\n".join(out_lines) + "\n")
print("\n".join(out_lines))
