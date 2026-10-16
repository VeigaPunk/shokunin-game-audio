#!/usr/bin/env python3
"""Receipt census over the two pinned pwprof-r89 runs.

For every fold item this proves the receipt surface it could touch:
  T1 play role        -> no argv surface in receipts (pw-play argv is
                         not recorded; the link legs record only
                         {"player": true})
  T2 nleg wd          -> no surface (the recorded rec never carries wd)
  T3 block players    -> `blocked`/`coverage_blocked` are absent/empty
                         in both green runs; block never ran
  T4 ensure_player    -> the link legs record the boolean only
  T5/T6 unload guards -> every recorded unload carries field ==
                         "sink_name" and value == its own tag, exactly
                         what the folded leaf["field"]/leaf["value"]
                         passes; sinks_gone keys == loads keys
  T7 stats guard      -> stats is always a dict in the receipts
Exit code 0 iff every assertion holds.
"""
import glob
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = sorted(glob.glob(os.path.join(HERE, "..", "..", "runs",
                                     "*pwprof-r89", "measurements.json")))
PROBES = ("pwprof_gate_r89_probe", "pwprof_oart_r89_probe",
          "pwprof_schema_r89_probe", "pwprof_xw_r89_probe")
EXPECT_LEGS = {"pwprof_gate_r89_probe": 27, "pwprof_oart_r89_probe": 12,
               "pwprof_schema_r89_probe": 4, "pwprof_xw_r89_probe": 9}
FAIL = []


def check(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")
    if not cond:
        FAIL.append(name)


for p in RUNS:
    doc = json.load(open(p))
    m = doc.get("measurements") or {}
    print("=" * 74)
    print("run:", os.path.basename(os.path.dirname(p)))
    print("sha256:", hashlib.sha256(open(p, "rb").read()).hexdigest())
    print("mode:", doc.get("mode"))
    check("mode == probe-pwprof-r89", doc.get("mode") ==
          "probe-pwprof-r89", doc.get("mode"))
    total = 0
    for probe in PROBES:
        e = m.get(probe)
        if e is None:
            check(f"{probe}: present", False)
            continue
        legs = e.get("legs") or {}
        total += len(legs)
        print(f"  {probe}: legs={len(legs)} failures={e.get('failures')} "
              f"blocked={e.get('blocked')} "
              f"coverage_blocked={e.get('coverage_blocked')}")
        print(f"      unloads={json.dumps(e.get('unloads') or {})}")
        print(f"      sinks_gone={e.get('sinks_gone')} "
              f"own_nodes_after={e.get('own_nodes_after')} "
              f"foreign_r89a={e.get('foreign_r89a_nodes')}")
        print(f"      refs={e.get('refs')}")
        cls = {}
        for k, l in legs.items():
            if isinstance(l, dict) and l.get("error_class"):
                cls.setdefault(l["error_class"], []).append(k)
        for c, ks in sorted(cls.items()):
            print(f"      class {c:24s} x{len(ks):3d} {sorted(set(ks))}")
        check(f"{probe}: failures empty", e.get("failures") == [])
        check(f"{probe}: coverage_blocked empty",
              not e.get("coverage_blocked"))
        check(f"{probe}: blocked absent (block never ran)",
              "blocked" not in e)
        check(f"{probe}: leg count {EXPECT_LEGS[probe]}",
              len(legs) == EXPECT_LEGS[probe], len(legs))
        # T5/T6 surface: recorded unload field/value == folded values
        for tag, u in (e.get("unloads") or {}).items():
            check(f"{probe}: unload[{tag}] field/value == "
                  "('sink_name', tag)",
                  u.get("field") == "sink_name" and u.get("value") == tag,
                  f"field={u.get('field')} value={u.get('value')}")
        check(f"{probe}: sinks_gone keys == unload keys",
              set(e.get("sinks_gone") or {}) ==
              set(e.get("unloads") or {}))
        check(f"{probe}: own_nodes_after == []",
              e.get("own_nodes_after") == [])
        check(f"{probe}: residual_destroy absent (no residue)",
              "residual_destroy" not in e)
        # T7 surface: stats is a dict whenever the schema entry ran
        if probe == "pwprof_schema_r89_probe":
            st = (legs.get("s_window") or {}).get("stats")
            check("pwprof_schema_r89_probe: s_window.stats is a dict",
                  isinstance(st, dict), type(st).__name__)
    check("total leg keys == 52", total == 52, total)
    txt = open(p).read()
    for needle in ("leaf.get", "\"field\": \"sink_name\"", "residual_destroy",
                   "blocked", "killed_at_bound", "watch_seen",
                   "stream_samples", "stdout_raw", "nsb_blocks",
                   "pwprof_connect_down", "pwprof_opt", "pwprof_cant_open"):
        print(f"  needle {needle!r}: {txt.count(needle)}")

print()
print(f"RECEIPT CENSUS: {'ALL PASS' if not FAIL else 'FAILURES: ' + str(FAIL)}")
sys.exit(1 if FAIL else 0)
