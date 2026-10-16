#!/usr/bin/env python3
"""r88 simplifier — receipt-oracle proofs (R1..R8) over the btwit-r88
runs. The two green runs are the replay oracle (no fresh live replay:
live-host family, sibling wave-B seats, 79-leg wall time); the stale RED
dev run is recorded as a non-oracle. Reads only."""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS_DIR = os.path.abspath(os.path.join(HERE, "..", "..", "runs"))
FAIL = []

GREEN = ["20261016T072313132218Z-btwit-r88", "20261016T072341162452Z-btwit-r88"]
DEV = "20261016T071710822152Z-btwit-r88"
PROBES = ["btabs_bluez_r88_probe", "witdiff_dump_r88_probe", "pwtop_r88_probe"]
EXPECT_LEGS = {"btabs_bluez_r88_probe": 28, "witdiff_dump_r88_probe": 41,
               "pwtop_r88_probe": 10}
DYNAMIC = {"bz_loadmod_discover", "bz_loadmod_device",
           "bz_loadmod_device_path", "bz_loadmod_discover_arg",
           "bz_create_a2dpsink", "bz_create_sink", "bz_create_a2dpsource",
           "bz_create_midi", "wd_mode_raw", "wd_mode_indent0"}


def check(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")
    if not cond:
        FAIL.append(name)


def load(d):
    p = os.path.join(RUNS_DIR, d, "measurements.json")
    return p, json.load(open(p))


# ---------------- R1: run census ----------------------------------------
dirs = sorted(x for x in os.listdir(RUNS_DIR) if "btwit-r88" in x)
check("R1a exactly 3 btwit-r88 runs on disk", len(dirs) == 3, str(dirs))
for d in GREEN:
    p, doc = load(d)
    check(f"R1b[{d}] mode + sha256",
          doc.get("mode") == "probe-btwit-r88",
          hashlib.sha256(open(p, "rb").read()).hexdigest())

# ---------------- R2: green structure -----------------------------------
run_docs = {}
for d in GREEN:
    _, doc = load(d)
    run_docs[d] = doc
    m = doc["measurements"]
    ok = all(m.get(pr) is not None for pr in PROBES)
    check(f"R2a[{d}] 3 r88 entries present", ok)
    check(f"R2b[{d}] leg counts 28/41/10 (79)",
          all(len(m[pr]["legs"]) == EXPECT_LEGS[pr] for pr in PROBES),
          str({pr: len(m[pr]["legs"]) for pr in PROBES}))
    check(f"R2c[{d}] failures == [] in all 3 entries",
          all(m[pr]["failures"] == [] for pr in PROBES))
    check(f"R2d[{d}] no coverage_blocked / blocked realized",
          all(not m[pr].get("coverage_blocked") and
              not m[pr].get("blocked") for pr in PROBES))

# ---------------- R3: leg-key census ------------------------------------
keysets = {}
for d in GREEN:
    m = run_docs[d]["measurements"]
    for pr in PROBES:
        keysets.setdefault(pr, []).append(set(m[pr]["legs"]))
for pr in PROBES:
    a, b = keysets[pr]
    check(f"R3a[{pr}] leg-key set identical across the two green runs",
          a == b, f"({len(a)} keys)")
union = set().union(*[keysets[pr][0] for pr in PROBES])
check("R3b recorded leg keys == 79", len(union) == 79, str(len(union)))
static = set(re.findall(r'legs\["([^"]+)"\]',
                        open(os.path.join(HERE, "base-measure_audio.py"),
                             encoding="utf-8").read()[0:0] or ""))
# static literal keys are re-derived from the region only
text = open(os.path.join(HERE, "base-measure_audio.py"),
            encoding="utf-8").read()
region = "\n".join(text.splitlines()[27506:29252])
static = set(re.findall(r'legs\["([^"]+)"\]', region)) | \
    set(re.findall(r'legs\.get\("([^"]+)"\)', region))
check("R3c recorded keys == static literal keys + 10 loop-generated keys",
      union == static | DYNAMIC,
      f"missing={sorted(union - (static | DYNAMIC))} "
      f"extra={sorted((static | DYNAMIC) - union)}")

# ---------------- R4: unload records (T5 domain) ------------------------
records = []
for d in GREEN:
    for pr in PROBES:
        records += list((run_docs[d]["measurements"][pr]
                         .get("unloads") or {}).values())
check("R4a 8 unload records (4 per green run)", len(records) == 8)
check("R4b every record is name-verified fired or skipped:not_listed",
      all((r.get("verified_index") == r.get("captured") and
           r.get("recycled") is False and r.get("exit_code") == 0)
          or r.get("skipped") == "not_listed" for r in records),
      str([r.get("skipped") for r in records if r.get("skipped")]))
check("R4c every record carries field=sink_name and value=<own name> "
      "(the T5 .get() defaults never fire in the receipts)",
      all(r.get("field") == "sink_name" and
          str(r.get("value", "")).startswith("r88a_ns") for r in records))

# ---------------- R5: teardown verdict surfaces -------------------------
for d in GREEN:
    for pr in PROBES:
        e = run_docs[d]["measurements"][pr]
        check(f"R5[{d}/{pr}] sinks_gone all true, own_nodes_after [], "
              f"no residual_destroy, foreign []",
              all(e.get("sinks_gone", {}).values()) and
              e.get("own_nodes_after") == [] and
              "residual_destroy" not in e and
              e.get("foreign_r88a_nodes") == [],
              str({k: e.get(k) for k in
                   ("sinks_gone", "own_nodes_after",
                    "foreign_r88a_nodes")}))

# ---------------- R6: the folded surfaces in the receipts ---------------
for d in GREEN:
    p = os.path.join(RUNS_DIR, d, "measurements.json")
    txt = open(p).read()
    check(f"R6a[{d}] no _frames_cache in the receipt", "_frames_cache" not in txt)
    for pr in PROBES:
        e = run_docs[d]["measurements"][pr]
        if pr == "pwtop_r88_probe":
            check(f"R6b[{d}] pt_n3 attempt==1 and >=2 frames",
                  e["legs"]["pt_n3"].get("attempt") == 1 and
                  len(e["legs"]["pt_n3"].get("frames", [])) >= 2,
                  f"attempt={e['legs']['pt_n3'].get('attempt')} "
                  f"frames={e['legs']['pt_n3'].get('frames')}")
    check(f"R6c[{d}] both toprec legs recorded",
          "pt_state_idle_toprec" in
          run_docs[d]["measurements"]["pwtop_r88_probe"]["legs"] and
          "pt_state_active_toprec" in
          run_docs[d]["measurements"]["pwtop_r88_probe"]["legs"])

# ---------------- R7: every r88-local class row fires -------------------
classes = set()
for d in GREEN:
    for pr in PROBES:
        for l in run_docs[d]["measurements"][pr]["legs"].values():
            if isinstance(l, dict) and l.get("error_class"):
                classes.add(l["error_class"])
check("R7 all 5 r88-local class rows fire across the green runs",
      {"pa_sendmsg_noent", "pwtop_connect_down", "pwdump_invalid_opt",
       "cli_enum_notimpl", "cli_unsupported_type"} <= classes,
      str(sorted(classes)))

# ---------------- R8: the stale RED dev run (non-oracle) ----------------
p, dev = load(DEV)
m = dev["measurements"]
dev_classes = set()
for pr in PROBES:
    for l in m.get(pr, {}).get("legs", {}).values():
        if isinstance(l, dict) and l.get("error_class"):
            dev_classes.add(l["error_class"])
dev_fail = {pr: m[pr]["failures"] for pr in PROBES if m.get(pr)}
check("R8a dev run is RED (6 failures) — non-oracle",
      sum(len(v) for v in dev_fail.values()) > 0,
      str({k: len(v) for k, v in dev_fail.items()}))
check("R8b dev run carries the pre-final class cli_cant_create (absent "
      "from the committed table)", "cli_cant_create" in dev_classes)
check("R8c dev run carries the pre-final leg pt_n2 (absent from the "
      "committed code)", "pt_n2" in m["pwtop_r88_probe"]["legs"])
check("R8d dev run leg total 75 (28+39+8), not the committed 79",
      sum(len(m[pr]["legs"]) for pr in PROBES) == 75,
      str({pr: len(m[pr]["legs"]) for pr in PROBES}))

print()
print(f"RECEIPT PROOFS: {'ALL PASS' if not FAIL else 'FAILURES: ' + str(FAIL)}")
sys.exit(1 if FAIL else 0)
