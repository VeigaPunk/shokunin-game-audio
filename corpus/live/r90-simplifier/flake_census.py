#!/usr/bin/env python3
"""m_phantom / timing-law census over every DISTINCT r90 battery in the
window (the verifier's tree-mut* dirs carry copies of the base tree's runs —
deduplicated by run-dir basename)."""
import glob
import json
import os

TREES = [
    ("/home/vgpnk/Projects/shokunin/r90s/base", "S-base", "pristine"),
    ("/home/vgpnk/Projects/shokunin/r90s/f1", "S-f1", "fold-1"),
    ("/home/vgpnk/Projects/shokunin/r90s/f2", "S-f2", "fold-2"),
    ("/home/vgpnk/Projects/shokunin/r90c-tree", "r90c", "pristine"),
    ("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/"
     "r90-verifier/tree", "verifier", "pristine"),
    ("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/"
     "r90-verifier/tree-mutecho", "v-mutecho", "mutant"),
    ("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/"
     "r90-verifier/tree-mutband", "v-mutband", "mutant"),
    ("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/"
     "r90-verifier/tree-mutsha", "v-mutsha", "mutant"),
]

seen = {}
for tree, label, kind in TREES:
    for d in glob.glob(f"{tree}/corpus/live/runs/*wpstate-r90"):
        seen.setdefault(os.path.basename(d), (d, label, kind))

rows = []
for base, (d, label, kind) in seen.items():
    j = json.load(open(f"{d}/measurements.json"))["measurements"]
    ph = j.get("wpstate_pmod_r90_probe", {}).get("legs", {}).get("m_phantom", {})
    st = j.get("wpstate_store_r90_probe", {})
    rows.append((base[:15], label, kind,
                 ph.get("load", {}).get("exit_code"),
                 len(j.get("wpstate_pmod_r90_probe", {}).get("failures") or []),
                 len(st.get("failures") or []),
                 (st.get("legs", {}).get("w_vanished_target", {})
                  or {}).get("outcome")))
rows.sort()
print(f"{'start(UTC)':17s} {'tree':10s} {'kind':9s} {'m_ph rc':7s} "
      f"{'pmod F':6s} {'store F':7s} w_vanished.outcome")
red = 0
for r in rows:
    print(f"{r[0]:17s} {r[1]:10s} {r[2]:9s} {str(r[3]):7s} {r[4]:<6d} "
          f"{r[5]:<7d} {r[6]}")
    red += 1 if (r[3] != 0) else 0
print(f"\n{len(rows)} distinct batteries; {red} with a non-zero m_phantom "
      f"load rc; {sum(1 for r in rows if r[5])} with store-entry failures")
print("pristine-tree batteries:",
      sum(1 for r in rows if r[2] == "pristine"),
      "of which m_phantom red:",
      sum(1 for r in rows if r[2] == "pristine" and r[3] != 0))
