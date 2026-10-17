#!/usr/bin/env python3
"""r91 VERIFIER — flakiness rate of the committed clock entry.

Calls the committed `gstfrz_clock_r91_entry()` N times on the frozen tree
(same bytes the battery runs; no extra probes) and records the c_alive
cell + every leg's fired unload per iteration.

Usage: repeat_clock.py <out.json> [N]
"""
import importlib.util
import json
import sys
from pathlib import Path

TREE = Path("/home/vgpnk/r91-verify-tree")
spec = importlib.util.spec_from_file_location(
    "ma_r91v", TREE / "corpus/fixtures/measure_audio.py")
ma = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ma)

n = int(sys.argv[2]) if len(sys.argv) > 2 else 6
out = []
for i in range(n):
    e = ma.gstfrz_clock_r91_entry()
    legs = e.get("legs") or {}
    al = legs.get("c_alive") or {}
    rec = {
        "i": i, "failures": e.get("failures"),
        "c_alive": {
            "killed": al.get("killed"),
            "out": (al.get("out") or {}).get("bytes"),
            "first_states": [nd.get("state") for s in
                             (al.get("samples") or [])
                             for nd in (s.get("nodes") or [])][:3],
            "sizes": [s.get("size") for s in (al.get("samples") or [])][:4],
            "wall_s": al.get("wall_s")},
        "fired": {tag: [(f.get("kind"), f.get("at"),
                         (f.get("result") or {}).get("verified_index"))
                        for f in (l.get("fired") or [])]
                  for tag, l in legs.items()},
        "unloads": {k: (v or {}).get("verified_index")
                    for k, v in (e.get("unloads") or {}).items()},
        "loadavg": e.get("loadavg"),
    }
    out.append(rec)
    print(json.dumps(rec)[:400], flush=True)
Path(sys.argv[1]).write_text(json.dumps(out, indent=1, default=str) + "\n")
