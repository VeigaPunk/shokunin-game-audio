#!/usr/bin/env python3
"""r88 critic census — receipt-level facts on the committed c19bec96 runs.

Reads only corpus/live/runs/*btwit-r88*/measurements.json. Emits census.json
(and a human summary to stdout). No host mutation, no tracked writes.
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUNS = os.path.join(ROOT, "live", "runs")

RUN_IDS = {
    "dev": "20261016T071710822152Z-btwit-r88",
    "A": "20261016T072313132218Z-btwit-r88",
    "B": "20261016T072341162452Z-btwit-r88",
}

ENTRIES = ["btabs_bluez_r88_probe", "witdiff_dump_r88_probe", "pwtop_r88_probe"]


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


out = {"runs": {}}
for tag, rid in RUN_IDS.items():
    p = os.path.join(RUNS, rid, "measurements.json")
    d = json.load(open(p))
    m = d["measurements"]
    rec = {
        "receipt": p,
        "sha256": sha256(p),
        "mode": d.get("mode"),
        "measurement_keys": sorted(m.keys()),
        "entries": {},
    }
    for e in ENTRIES:
        if e not in m:
            rec["entries"][e] = {"absent": True}
            continue
        ent = m[e]
        legs = ent.get("legs") or {}
        fails = ent.get("failures")
        cb = ent.get("coverage_blocked")
        rec["entries"][e] = {
            "leg_count": len(legs),
            "leg_names": sorted(legs.keys()),
            "failures": fails,
            "coverage_blocked": cb,
            "extra_keys": sorted(k for k in ent.keys() if k not in ("legs", "failures", "coverage_blocked")),
        }
    out["runs"][tag] = rec

# cross-run leg-name identity per entry
diff = {}
for e in ENTRIES:
    names = {}
    for tag in RUN_IDS:
        ent = out["runs"][tag]["entries"].get(e, {})
        names[tag] = ent.get("leg_names")
    same_AB = names["A"] == names["B"]
    diff[e] = {
        "A==B": same_AB,
        "dev==A": names["dev"] == names["A"],
        "A_only": sorted(set(names["A"] or []) - set(names["B"] or [])),
        "B_only": sorted(set(names["B"] or []) - set(names["A"] or [])),
    }
out["legname_identity"] = diff
out["totals"] = {
    tag: sum(
        v.get("leg_count", 0) for v in out["runs"][tag]["entries"].values()
    )
    for tag in RUN_IDS
}

here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "census.json"), "w") as f:
    json.dump(out, f, indent=2, sort_keys=True)

for tag in RUN_IDS:
    r = out["runs"][tag]
    print(f"== {tag} {r['receipt']}")
    print(f"   sha256 {r['sha256']}")
    print(f"   mode {r['mode']}")
    for e in ENTRIES:
        ent = r["entries"][e]
        if ent.get("absent"):
            print(f"   {e}: ABSENT")
            continue
        print(
            f"   {e}: {ent['leg_count']} legs  failures={ent['failures']!r} "
            f"coverage_blocked={ent['coverage_blocked']!r} extra={ent['extra_keys']}"
        )
print("legname identity:", json.dumps(diff, indent=2))
print("totals:", out["totals"])
