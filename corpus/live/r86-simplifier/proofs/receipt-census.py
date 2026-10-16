#!/usr/bin/env python3
"""r86-simplifier receipt census R1-R9 over the two pinned green runs
(corpus/live/runs/*-pwctl-r86/measurements.json). Read-only."""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
RUNS = [REPO / "corpus/live/runs/20261016T063006268243Z-pwctl-r86/"
        "measurements.json",
        REPO / "corpus/live/runs/20261016T063043717745Z-pwctl-r86/"
        "measurements.json"]
ENTRIES = ("pwctl_addr_r86_probe", "pwctl_params_r86_probe",
           "pwctl_dsp_r86_probe", "pwctl_meta_r86_probe",
           "pwctl_tools_r86_probe")
results = []


def ck(name, cond, detail=""):
    results.append(bool(cond))
    print(f"{'PASS' if cond else 'FAIL'} {name} {detail}")


runs = [json.loads(p.read_text())["measurements"] for p in RUNS]
ck("R1 both runs parse", all(isinstance(r, dict) for r in runs))
ck("R1 five r86 entries in both runs",
   all(all(e in r for e in ENTRIES) for r in runs))
ck("R1 all r86 failures empty",
   all(r[e]["failures"] == [] for r in runs for e in ENTRIES))
ck("R1 all r86 coverage_blocked empty",
   all(r[e].get("coverage_blocked", []) == []
       for r in runs for e in ENTRIES))

# R2 — unload witness per entry x run
n_unloads = 0
ok = True
for r in runs:
    for e in ENTRIES:
        u = r[e].get("unloads", {})
        if len(u) != 1:
            ok = False
        for tag, rec in u.items():
            n_unloads += 1
            ok = ok and isinstance(rec, dict) \
                and rec.get("verified_index") == rec.get("captured") \
                and rec.get("recycled") is False \
                and tag.startswith("r86a_ns_")
ck("R2 10/10 unload records dicts with verified_index==captured, "
   "recycled False", ok and n_unloads == 10, f"n={n_unloads}")
ck("R2 all sinks_gone true",
   all(all(v is True for v in r[e]["sinks_gone"].values())
       for r in runs for e in ENTRIES))
ck("R2 own_nodes_after [] everywhere",
   all(r[e]["own_nodes_after"] == [] for r in runs for e in ENTRIES))
ck("R2 meta_keys_gone true (meta entry)",
   all(r["pwctl_meta_r86_probe"]["meta_keys_gone"] is True
       for r in runs))

# R3 — the recorded self_serials (what T3 must not change)
for i, r in enumerate(runs, 1):
    a = r["pwctl_addr_r86_probe"]["legs"]
    ck(f"R3 run{i} dump_full1/2 self_serials recorded",
       all(isinstance(a[f"dump_full{k}"]["self_serials"], list)
           and a[f"dump_full{k}"]["self_serials"]
           for k in (1, 2)),
       str([a["dump_full1"]["self_serials"],
            a["dump_full2"]["self_serials"]]))
    ck(f"R3 run{i} self_clients >= 1 both reps",
       all(a[f"dump_full{k}"]["self_clients"] >= 1 for k in (1, 2)))

# R4 — no receipt key/value names the deleted constants
blob = json.dumps(runs)
for nm in ("PWCTL_R86_LINK_WAIT_S", "PWCTL_R86_TAP_WAIT_S",
           "LINK_WAIT", "TAP_WAIT"):
    ck(f"R4 receipts contain no '{nm}'", nm not in blob)

# R5 — dsp regions (the solo window T8 must not move)
for i, r in enumerate(runs, 1):
    regs = r["pwctl_dsp_r86_probe"]["legs"]["regions"]
    ck(f"R5 run{i} regions solo/cv25/cv50/mute/reset/dead/pa25/pa100",
       all(k in regs for k in ("solo", "cv25", "cv50", "mute", "reset",
                               "dead", "pa25", "pa100")))
    solo = regs["solo"]["median_peak"]
    ck(f"R5 run{i} solo inside the x8192 envelope",
       solo is not None and 0.85 * 8192 <= solo <= 1.18 * 8192,
       f"solo={solo} t={regs['solo']['t']}")

# R6 — link censuses present (T6 domain)
for i, r in enumerate(runs, 1):
    a = r["pwctl_addr_r86_probe"]["legs"]
    t = r["pwctl_tools_r86_probe"]["legs"]
    ck(f"R6 run{i} self_loop_census + lk_census + junkprops_census",
       a["self_loop_census"]["links"]
       and t["lk_census"]["links"]
       and t["lk_junkprops_census"]["links"])

# R7 — the declared record-only / rc-only caveats are in the receipts
for i, r in enumerate(runs, 1):
    a = r["pwctl_addr_r86_probe"]["legs"]
    p = r["pwctl_params_r86_probe"]["legs"]
    ck(f"R7 run{i} dump_color_eq armed False",
       a["dump_color_eq"].get("armed") is False)
    ck(f"R7 run{i} d_route armed False",
       p["d_route"].get("armed") is False)
    ck(f"R7 run{i} n_format armed rc_only",
       p["n_format"].get("armed") == "rc_only")

# R8 — addr ns_leaf serials (T9 domain: ser != "None" on both runs)
for i, r in enumerate(runs, 1):
    leaf = r["pwctl_addr_r86_probe"]["ns_leaf"]
    ck(f"R8 run{i} ns_leaf serial is a real number",
       re.fullmatch(r"\d+", str(leaf["object_serial"]) or "") is not None,
       str(leaf))

# R9 — tools gates recorded
for i, r in enumerate(runs, 1):
    ck(f"R9 run{i} all five entries record tools",
       all(isinstance(r[e].get("tools"), dict) and r[e]["tools"]
           for e in ENTRIES))

n_fail = results.count(False)
print(f"\n{len(results) - n_fail}/{len(results)} PASS")
sys.exit(1 if n_fail else 0)
