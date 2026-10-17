#!/usr/bin/env python3
"""r92 verifier — receipt-forgery controls (M4).

Writes forged copies of a receipt and runs the independent law set on each.
Expected: every fabrication is caught by FAIL/BLOCKED; the blank-verdicts
control is a no-op (the entry's own lists are not the detector).
"""
import copy
import json
import os
import subprocess
import sys

BASE = "/home/vgpnk/r92-verifier"
SRC = sys.argv[1]
OUT = f"{BASE}/runs/forged"
os.makedirs(OUT, exist_ok=True)
base = json.load(open(SRC))
AR = "filterchain_arm_r92_probe"
IR = "filterchain_ir_r92_probe"
WP = "filterchain_wpx_r92_probe"
DP = "filterchain_dsp_r92_probe"

forges = {}
f = copy.deepcopy(base)
f["measurements"][AR]["failures"] = []
f["measurements"][DP]["failures"] = []
f["measurements"][IR]["failures"] = []
f["measurements"][WP]["failures"] = []
for e in (AR, DP, IR, WP):
    f["measurements"][e].pop("coverage_blocked", None)
forges["blank-verdicts"] = f

f = copy.deepcopy(base)
f["measurements"][AR]["own_nodes_after"] = ["r92a_999999_fake"]
forges["forge-own-nodes-after"] = f

f = copy.deepcopy(base)
f["measurements"][DP]["legs"]["d_copy"]["analysis"]["gain_db"]["200"] = 0.5
forges["forge-d-copy-gain"] = f

f = copy.deepcopy(base)
f["measurements"][DP]["legs"]["d_gneg140"]["analysis"]["gain_db"]["200"] = -66.0
forges["forge-d-gneg140-unclamped"] = f

f = copy.deepcopy(base)
del f["measurements"][IR]["legs"]["i_2tap"]
forges["pop-leg-i-2tap"] = f

f = copy.deepcopy(base)
f["measurements"][WP]["legs"]["v_spa"]["filter_graph_count"] = 5
forges["forge-v-spa-count"] = f

f = copy.deepcopy(base)
f["measurements"][IR]["legs"]["i_residual"]["i_2tap"]["max_residual_lsb"] = 4.0
forges["forge-residual-lsb"] = f

f = copy.deepcopy(base)
f["measurements"][IR]["legs"]["i_2tap"]["analysis"]["peak_gap"] = 70
forges["forge-i-2tap-gap"] = f

rows = []
for name, rec in forges.items():
    p = f"{OUT}/{name}.json"
    json.dump(rec, open(p, "w"), indent=1)
    r = subprocess.run([sys.executable, f"{BASE}/runs/r92v_laws.py", p,
                        "--tag", name, "--json", f"{OUT}/{name}.laws.json"],
                       capture_output=True, text=True)
    head = r.stdout.strip().split("\n")
    summary = next((l for l in head if l.startswith("laws:")), "?")
    fails = [l.strip() for l in head if l.startswith("  ") and
             ("FAIL" in l or "BLOCKED" in l)]
    rows.append((name, summary, fails[:4]))
    print("==", name)
    print("  ", summary)
    for l in fails[:6]:
        print("   ", l[:150])
print()
print("# forgery controls: caught =", sum(1 for _, s, _ in rows if "FAIL: 0" not in s or "BLOCKED: 0" not in s),
      "of", len(rows))
