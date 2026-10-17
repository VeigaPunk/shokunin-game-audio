#!/usr/bin/env python3
"""Census every --probe-gstfrz-r91 receipt under the given run dirs: the
fired-event shape (gated vs ungated) and the leg census.

The fold-1 claim is that the `hooks` (ungated timed-event) path never fires:
every recorded fired event must carry `"gated": true`.
"""
import json
import sys
from pathlib import Path

gated = ungated = 0
runs = 0
for root in sys.argv[1:]:
    for p in sorted(Path(root).glob("*/measurements.json")):
        try:
            j = json.loads(p.read_text())
        except ValueError:
            continue
        ms = {k: v for k, v in j.get("measurements", {}).items()
              if k.endswith("r91_probe")}
        if not ms:
            continue
        runs += 1
        g = u = 0
        for e in ms.values():
            for leg in (e.get("legs") or {}).values():
                for f in (leg.get("fired") or []):
                    if f.get("gated"):
                        g += 1
                    else:
                        u += 1
        gated += g
        ungated += u
        print(f"{p.parent.name}: gated={g} ungated={u}")
print(f"\nruns={runs} fired_gated={gated} fired_ungated={ungated}")
