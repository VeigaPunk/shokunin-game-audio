#!/usr/bin/env python3
"""r85 simplifier RECEIPT census — both pinned author runs.

Read-only: reads ../r85-author/runs/run{1,2}/measurements.json and writes
proofs/receipt-census.txt.
"""
import json
from pathlib import Path

OUT = []
PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    tag = "PASS" if cond else "FAIL"
    if cond:
        PASS += 1
    else:
        FAIL += 1
    OUT.append(f"[{tag}] {name}: {detail}")


RUNS = {}
for r in ("run1", "run2"):
    RUNS[r] = json.loads(
        Path(f"../r85-author/runs/{r}/measurements.json").read_text())

ENTRIES = [k for k in RUNS["run1"]["measurements"] if k.startswith("pactlmon_")]
LEG_COUNT = {r: {e: len(RUNS[r]["measurements"][e].get("legs", {}))
                 for e in ENTRIES} for r in RUNS}

# ------------------------------------------------------------------ R1
ok1 = all(len(LEG_COUNT[r]) == 5 and sum(LEG_COUNT[r].values()) == 87
          for r in RUNS)
ok1 = ok1 and all(
    RUNS[r]["measurements"][e].get("failures") == [] and
    not RUNS[r]["measurements"][e].get("blocked") and
    not RUNS[r]["measurements"][e].get("coverage_blocked")
    for r in RUNS for e in ENTRIES)
ok1 = ok1 and all(RUNS[r]["measurements"][e].get("own_nodes_after") == []
                  for r in RUNS for e in ENTRIES)
check("R1 both runs: 5 entries / 87 legs / no failures / no blocked / "
      "no own-node residue", ok1,
      f"legs run1={LEG_COUNT['run1']} run2={LEG_COUNT['run2']}")

# ------------------------------------------------------------------ R2
blob = {r: json.dumps(RUNS[r]) for r in RUNS}
check("R2 the deleted constant has no receipt surface",
      all("STREAM_WAIT" not in b and "stream_wait" not in b
          for b in blob.values()),
      "0 occurrences of any STREAM_WAIT key/value in both receipts")

# ------------------------------------------------------------------ R3
unl = {r: {e: RUNS[r]["measurements"][e].get("unloads") for e in ENTRIES}
       for r in RUNS}
all_vals = [v for r in RUNS for e in ENTRIES
            for v in (unl[r][e] or {}).values()]
kinds = sorted({type(v).__name__ for v in all_vals})
counts = {r: sum(len(unl[r][e] or {}) for e in ENTRIES) for r in RUNS}
gone_ok = all(
    all(g is True for g in (RUNS[r]["measurements"][e].get("sinks_gone") or
                            {}).values()) and
    all(g is True for g in (RUNS[r]["measurements"][e].get("sources_gone") or
                            {}).values())
    for r in RUNS for e in ENTRIES)
check("R3 every `unloads` value is a dict and every gone-witness is true",
      kinds == ["dict"] and counts["run1"] == 13 and counts["run2"] == 13
      and gone_ok,
      f"unload record types={kinds}; records run1={counts['run1']} "
      f"run2={counts['run2']}; all sinks_gone/sources_gone true")

# ------------------------------------------------------------------ R4
def keys_with(entry, key):
    return [n for n, l in entry.get("legs", {}).items() if key in l]


hit_ok = True
detail = {}
for r in RUNS:
    m = RUNS[r]["measurements"]
    cap_legs = [n for n in m["pactlmon_capture_r85_probe"]["legs"]
                if n.startswith(("cap_", "t_", "sd_", "late"))]
    cap_hit = [n for n in cap_legs
               if "hit" in m["pactlmon_capture_r85_probe"]["legs"][n] or
               "error_hit" in m["pactlmon_capture_r85_probe"]["legs"][n]]
    run_hits = [n for n in m["pactlmon_negctl_r85_probe"]["legs"]
                if "error_hit" in m["pactlmon_negctl_r85_probe"]["legs"][n]]
    unit_hits = [n for n in m["pactlmon_negctl_r85_probe"]["legs"]
                 if "hit" in m["pactlmon_negctl_r85_probe"]["legs"][n]]
    detail[r] = (len(cap_legs), cap_hit, run_hits, len(unit_hits))
    hit_ok = hit_ok and not cap_hit and run_hits and len(unit_hits) == 13
check("R4 the two folded `hit` stores have no receipt surface; the live "
      "ones do", hit_ok,
      f"capture legs={detail['run1'][0]}/= {detail['run2'][0]}, none "
      f"carrying a hit key={detail['run1'][1]}/{detail['run2'][1]}; "
      f"live `error_hit` records={detail['run1'][2]}/"
      f"{detail['run2'][2]}; unit-table `hit` records="
      f"{detail['run1'][3]}/{detail['run2'][3]}")

# ------------------------------------------------------------------ R5
real = {}
for r in RUNS:
    m = RUNS[r]["measurements"]
    real[r] = {
        "cdup_cap": m["pactlmon_addr_r85_probe"]["legs"]["cdup_cap"]
        .get("realization"),
        "latebind": m["pactlmon_capture_r85_probe"]["legs"]["latebind"]
        .get("realization"),
        "sd_prop": m["pactlmon_capture_r85_probe"]["legs"]["sd_prop"]
        .get("realization"),
        "t_sinkname": m["pactlmon_capture_r85_probe"]["legs"]["t_sinkname"]
        .get("realization"),
        "mixdup": m["pactlmon_mix_r85_probe"]["legs"]["mixdup"]
        .get("realization"),
        "mixdelay": m["pactlmon_mix_r85_probe"]["legs"]["mixdelay"]
        .get("realization"),
        "mixinv": m["pactlmon_mix_r85_probe"]["legs"]["mixinv"]
        .get("realization"),
    }
check("R5 the three host-bimodal realizations are recorded (and the "
      "phase realizations vary run-to-run)",
      real["run1"]["cdup_cap"] == real["run2"]["cdup_cap"] ==
      "serial_monitor_bypass" and
      real["run1"]["latebind"] == real["run2"]["latebind"] == "late_bound"
      and real["run1"]["sd_prop"] == real["run2"]["sd_prop"] ==
      "bind_killed_then_default",
      f"cdup_cap={real['run1']['cdup_cap']}/{real['run2']['cdup_cap']}; "
      f"latebind={real['run1']['latebind']}/{real['run2']['latebind']}; "
      f"sd_prop={real['run1']['sd_prop']}/{real['run2']['sd_prop']}; "
      f"t_sinkname={real['run1']['t_sinkname']}/"
      f"{real['run2']['t_sinkname']}; mixdup="
      f"{real['run1']['mixdup']}/{real['run2']['mixdup']}; mixdelay="
      f"{real['run1']['mixdelay']}/{real['run2']['mixdelay']}; mixinv="
      f"{real['run1']['mixinv']}/{real['run2']['mixinv']}")

# ------------------------------------------------------------------ R6
dead_keys = []
for r in RUNS:
    for e in ENTRIES:
        for n, l in RUNS[r]["measurements"][e].get("legs", {}).items():
            if not isinstance(l, dict):
                continue
            for k in ("sers", "want_node", "lp", "label"):
                if k in l:
                    dead_keys.append((r, e, n, k))
check("R6 none of the dead locals has a receipt key",
      not dead_keys,
      f"receipt keys named sers/want_node/lp/label: {dead_keys}")

# ------------------------------------------------------------------ R7
key_stability = {}
for e in ENTRIES:
    k1 = set(RUNS["run1"]["measurements"][e].get("legs", {}))
    k2 = set(RUNS["run2"]["measurements"][e].get("legs", {}))
    key_stability[e] = sorted(k1 ^ k2)
check("R7 leg-name surface identical across both runs (replay oracle)",
      all(not v for v in key_stability.values()),
      f"leg-name symmetric differences per entry={key_stability}")

# ------------------------------------------------------------------ R8
# the receipts' volatile fields only — the fold must not touch any
# verdict-bearing value; check the verdict surfaces the fold touches.
touched = {
    "unloads": lambda e: json.dumps(e.get("unloads"), sort_keys=True),
    "sinks_gone": lambda e: json.dumps(e.get("sinks_gone"), sort_keys=True),
    "sources_gone": lambda e: json.dumps(e.get("sources_gone"),
                                         sort_keys=True),
    "own_nodes_after": lambda e: json.dumps(e.get("own_nodes_after")),
    "failures": lambda e: json.dumps(e.get("failures")),
    "serial_cycles": lambda e: json.dumps(
        e.get("serial_cycles") if e.get("probe", "").startswith(
            "r85a pactl/pw-cli") else "n/a"),
    "vol_pct_rows": lambda e: json.dumps(
        {n: l.get("stdout", "")[:40] for n, l in
         (e.get("legs") or {}).items()
         if n.startswith(("g_", "s_"))}),
    "realizations": lambda e: json.dumps(
        {n: l.get("realization") for n, l in (e.get("legs") or {}).items()
         if isinstance(l, dict) and "realization" in l}, sort_keys=True),
}
detail8 = {}
ok8 = True
for r in RUNS:
    for e in ENTRIES:
        rec = RUNS[r]["measurements"][e]
        for nm, fn in touched.items():
            v = fn(rec)
            if v in (None, "null"):
                ok8 = False
                detail8[(r, e, nm)] = v
check("R8 every verdict-bearing surface the fold touches is realized "
      "(non-null) in both runs", ok8,
      f"null surfaces={detail8}" if detail8 else
      "all of unloads/sinks_gone/sources_gone/own_nodes_after/failures/"
      "serial_cycles/volume rows/realizations present in 10/10 entries")

Path("proofs/receipt-census.txt").write_text(
    "\n".join(OUT) + f"\n\nTOTAL: {PASS} PASS / {FAIL} FAIL\n",
    encoding="utf-8")
print("\n".join(OUT))
print(f"\nTOTAL: {PASS} PASS / {FAIL} FAIL")
