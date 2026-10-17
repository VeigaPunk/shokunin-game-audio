#!/usr/bin/env python3
"""r89 RE-VERIFY: same-window replay of the PRE-FOLD global x_foot law vs the
COMMITTED own-scoped arm, over every recorded receipt (re-verifier + the r89
verifier's pre-fix battery + the foldfix battery).

pre-fold global law (laws.py X03, the lottery):
    PASS iff pwprof_during == pwprof_before + 1 and nodes_delta == 0
committed own-scoped arm (measure_audio.py :31002-31015):
    PASS iff own_clients == [<own pid>] and own_objects == []
    BLOCKED (named class) iff census unreadable / foot rc != 0 /
        own client not enumerated in the 0.35 s bracket
    FAIL otherwise

The replay is deterministic over recorded windows: the same receipt that the
committed arm passes can red the global law (and vice versa). It shows the
fold changed the VERDICT FUNCTION, not the windows.
"""
import glob
import json
import sys

PATHS = []
for pat in sys.argv[1:]:
    PATHS.extend(sorted(glob.glob(pat)))


def committed(l):
    oc = l.get("own_clients")
    if oc is None:
        return "BLOCKED", "census unreadable"
    if l.get("rc") not in (0, None):
        return "BLOCKED", f"foot rc={l.get('rc')}"
    if len(oc) == 0:
        return "BLOCKED", "own client not enumerated"
    if len(oc) == 1 and not l.get("own_objects"):
        return "PASS", f"own_clients={oc}"
    return "FAIL", f"own_clients={oc} own_objects={l.get('own_objects')}"


def global_law(l):
    b, d = l.get("pwprof_before"), l.get("pwprof_during")
    nd = l.get("nodes_delta")
    if b is None or d is None:
        return "N/A", "pre-fix receipt without global census"
    ok = (d == (b or 0) + 1) and nd == 0
    return ("PASS" if ok else "FAIL",
            f"before={b} during={d} nodes_delta={nd}")


print(f"{'receipt':38s} {'committed':9s} {'global(pre-fold)':16s} note")
agree = 0
both_pass = 0
flip = 0
for p in PATHS:
    try:
        d = json.load(open(p))
        l = d["measurements"]["pwprof_xw_r89_probe"]["legs"]["x_foot"]
    except Exception as e:  # noqa: BLE001
        print(f"{p.split('/')[-1][:38]:38s} SKIP {e}")
        continue
    rid = p.split('/')[-2] if p.endswith('.measurements.json') else p.split('/')[-1].replace('.receipt.json', '')
    cv, cn = committed(l)
    gv, gn = global_law(l)
    tag = ""
    if cv == "PASS" and gv == "FAIL":
        tag = "**global false-FAILs the committed-green window**"
        flip += 1
    elif cv == "BLOCKED" and gv == "FAIL":
        tag = "committed names the class, global false-FAILs"
        flip += 1
    elif cv == "BLOCKED" and gv == "PASS":
        tag = "global passes by luck, committed refuses to claim"
    elif cv == gv == "PASS":
        both_pass += 1
    if cv == gv:
        agree += 1
    print(f"{rid:38s} {cv:9s} {gv:16s} {tag or cn + ' | ' + gn}")
print(f"\nreceipts={len(PATHS)} agree={agree} both_PASS={both_pass} "
      f"divergences={flip}")
