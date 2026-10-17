#!/usr/bin/env python3
"""r92 verifier — entry-level mutation/negative-control runner.

Runs ONE r92 entry function from a mutated tree (no CLI, no receipt, no
family lock) and prints the entry's failures / coverage_blocked /
own_nodes_after as JSON.  Used for the mutation controls, where the point
is the ARM's detection, not the receipt writer.

Usage: run_entry.py <tree> <entry> [tag]
"""
import json
import os
import sys

tree, entry = sys.argv[1], sys.argv[2]
tag = sys.argv[3] if len(sys.argv) > 3 else entry
sys.path.insert(0, os.path.join(tree, "corpus/fixtures"))
import measure_audio as m  # noqa: E402

fn = getattr(m, entry)
r = fn()
out = {"tag": tag, "tree": tree, "entry": entry,
       "failures": r.get("failures"),
       "coverage_blocked": r.get("coverage_blocked"),
       "own_nodes_after": r.get("own_nodes_after"),
       "sinks_gone": r.get("sinks_gone"),
       "live_after": r.get("live_after"),
       "legs": sorted((r.get("legs") or {}).keys()),
       "blocked": r.get("blocked")}
print(json.dumps(out, indent=1))
