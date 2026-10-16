#!/usr/bin/env python3
"""Build the per-law x per-receipt arm matrix from laws.py output.

Usage: matrix.py laws-all.txt > matrix.txt
"""
import re
import sys
from collections import OrderedDict

rows = OrderedDict()
receipts = []
for ln in open(sys.argv[1]):
    m = re.match(r"^LAW (\S+) (.+) (PASS|FAIL|BLOCKED) ?(.*)$", ln.rstrip())
    if not m:
        continue
    rid, law, verdict, detail = m.groups()
    if rid not in receipts:
        receipts.append(rid)
    rows.setdefault(law, {})[rid] = (verdict, detail)

print(f"receipts ({len(receipts)}): {' '.join(receipts)}")
print()
hdr = f"{'law':58} " + " ".join(f"{r[:10]:>10}" for r in receipts)
print(hdr)
bad = []
for law, per in rows.items():
    cells = []
    for r in receipts:
        v = per.get(r, ("-", ""))[0]
        cells.append(f"{v[:10]:>10}")
        if v == "FAIL":
            bad.append((law, r, per[r][1]))
    print(f"{law:58} " + " ".join(cells))
print()
print("LAWS WITH FAIL:")
for law, r, detail in bad:
    print(f"  {law:56} {r:18} {detail[:110]}")
print()
tot = {v: sum(1 for per in rows.values()
              for x in per.values() if x[0] == v)
       for v in ("PASS", "FAIL", "BLOCKED")}
print(f"law-cells: PASS={tot['PASS']} FAIL={tot['FAIL']} "
      f"BLOCKED={tot['BLOCKED']} total={sum(tot.values())} "
      f"laws={len(rows)} receipts={len(receipts)}")
