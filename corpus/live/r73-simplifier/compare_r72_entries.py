#!/usr/bin/env python3
"""Retained-behavior driver: rerun the LANDED r72 libsndfile transport arm
(imported from the tracked fixture) on the canonical 9 members and deep-compare
each entry against the committed r72 receipt (runs/20261014T143409279922Z-sndfile-transport-r72).

Read-only against the shared tree: members are read, temp fifos live in /tmp.
Writes nothing outside stdout (caller redirects).
"""
import importlib.util, json, sys
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
spec = importlib.util.spec_from_file_location("measure_audio", REPO / "corpus/fixtures/measure_audio.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

committed = json.loads((REPO / "corpus/live/runs/20261014T143409279922Z-sndfile-transport-r72/measurements.json").read_text())

out = {}
for member, (directory, filename) in mod.TRANSPORT_R72_MEMBERS.items():
    path = mod.ROOT / "live" / directory / filename
    entry = mod.sndfile_transport_entry(member, path)
    key = f"sndfile_{member}_r72_probe"
    ref = committed["measurements"][key]
    same = entry == ref
    # field-level diff detail if not equal
    diff = {}
    if not same:
        for k in sorted(set(entry) | set(ref)):
            if entry.get(k) != ref.get(k):
                diff[k] = {"rerun": entry.get(k), "committed": ref.get(k)}
    out[key] = {"match": same, "diff": diff}
    print(f"{key}: {'MATCH' if same else 'MISMATCH'} path={entry['path']}")
    if diff:
        print(json.dumps(diff, indent=1)[:3000])

mismatch = sum(1 for v in out.values() if not v["match"])
print(f"TOTAL {len(out)} members, {mismatch} mismatches")
print(json.dumps(out, sort_keys=True))
sys.exit(1 if mismatch else 0)
