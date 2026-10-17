#!/usr/bin/env python3
"""Print one battery's verdict surface: per entry failures / coverage_blocked
/ blocked, the leg-key census, and the fired-event shape census (every fired
event must be a GATED one — the `hooks` path never fires)."""
import json
import sys
from pathlib import Path

tree, tag, run, rc = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
d = json.loads((Path(run) / "measurements.json").read_text())
ms = d["measurements"]
entries = {k: v for k, v in ms.items() if k.endswith("r91_probe")}
fired_gated = fired_plain = 0
legs = 0
for k in sorted(entries):
    e = entries[k]
    legs += len(e.get("legs") or {})
    for leg in (e.get("legs") or {}).values():
        for f in (leg.get("fired") or []):
            if f.get("gated"):
                fired_gated += 1
            else:
                fired_plain += 1
    print(f"  {k}: failures={e.get('failures')} "
          f"coverage_blocked={e.get('coverage_blocked')} "
          f"blocked={e.get('blocked')} legs={len(e.get('legs') or {})}")
print(f"  [{tag}] rc={rc} entries={len(entries)} legs={legs} "
      f"fired_gated={fired_gated} fired_ungated={fired_plain}")
