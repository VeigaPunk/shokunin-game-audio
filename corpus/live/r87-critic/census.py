#!/usr/bin/env python3
"""r87-critic census: read the two green committed receipts + the 3 dev runs.

Read-only. Emits census.json + census.out.
"""
import json
import os
import sys
import hashlib

ROOT = "/home/vgpnk/Projects/shokunin/audio-shokunin"
RUNS = os.path.join(ROOT, "corpus/live/runs")
ENTRIES = [
    "pwbind_modes_r87_probe",
    "pwbind_target_r87_probe",
    "pwbind_cli_r87_probe",
    "pwbind_midi_r87_probe",
]

GREEN = [
    "20261016T070036115509Z-pwbind-r87",
    "20261016T070305393338Z-pwbind-r87",
]
DEV = [
    "20261016T064958137082Z-pwbind-r87",
    "20261016T065456126915Z-pwbind-r87",
    "20261016T065750423328Z-pwbind-r87",
]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(run):
    p = os.path.join(RUNS, run, "measurements.json")
    return json.load(open(p)), sha(p)


def census_one(d):
    out = {}
    m = d["measurements"]
    for e in ENTRIES:
        ent = m.get(e)
        if ent is None:
            out[e] = {"present": False}
            continue
        legs = ent.get("legs", {})
        fails = ent.get("failures", {})
        out[e] = {
            "present": True,
            "n_legs": len(legs),
            "leg_names": sorted(legs.keys()),
            "failures": fails,
            "n_failures": len(fails) if isinstance(fails, dict) else None,
            "coverage_blocked": ent.get("coverage_blocked"),
            "sinks_gone": ent.get("sinks_gone"),
            "own_nodes_after": ent.get("own_nodes_after"),
            "foreign_r87a_nodes": ent.get("foreign_r87a_nodes"),
            "loadavg": ent.get("loadavg"),
            "contention": ent.get("contention"),
            "oracle_at_start": ent.get("oracle_at_start"),
            "inventory": ent.get("inventory"),
            "unloads": ent.get("unloads"),
            "default_sink_at_start": ent.get("default_sink_at_start"),
            "default_sink_at_end": ent.get("default_sink_at_end"),
            "ns_leaf": ent.get("ns_leaf"),
            "bridge": ent.get("bridge"),
            "seq_port": ent.get("seq_port"),
            "tools": ent.get("tools"),
        }
    return out


def main():
    report = {"runs": {}, "legname_diff": {}}
    for run in GREEN + DEV:
        try:
            d, s = load(run)
        except Exception as ex:
            report["runs"][run] = {"error": str(ex)}
            continue
        c = census_one(d)
        report["runs"][run] = {
            "sha256": s,
            "mode": d.get("mode"),
            "census": c,
            "totals": {
                "n_entries": sum(1 for e in ENTRIES if c[e].get("present")),
                "n_legs": sum(c[e].get("n_legs", 0) for e in ENTRIES),
                "n_failures": sum(
                    (c[e].get("n_failures") or 0) for e in ENTRIES
                ),
            },
        }
    # leg-name identity across the two green runs
    a = report["runs"][GREEN[0]]["census"]
    b = report["runs"][GREEN[1]]["census"]
    for e in ENTRIES:
        la, lb = a[e].get("leg_names", []), b[e].get("leg_names", [])
        report["legname_diff"][e] = {
            "identical": la == lb,
            "only_run1": sorted(set(la) - set(lb)),
            "only_run2": sorted(set(lb) - set(la)),
        }
    json.dump(report, open(os.path.join(os.path.dirname(__file__), "census.json"), "w"),
              indent=1, sort_keys=True)

    # human-readable
    lines = []
    for run in GREEN + DEV:
        r = report["runs"].get(run, {})
        if "error" in r:
            lines.append(f"RUN {run}: ERROR {r['error']}")
            continue
        t = r["totals"]
        lines.append(f"RUN {run} sha={r['sha256'][:16]} mode={r['mode']} "
                     f"entries={t['n_entries']} legs={t['n_legs']} failures={t['n_failures']}")
        for e in ENTRIES:
            c = r["census"][e]
            lines.append(f"   {e:26s} legs={c.get('n_legs')!s:>4} "
                         f"fails={c.get('n_failures')} blocked={c.get('coverage_blocked')!r} "
                         f"sinks_gone={c.get('sinks_gone')!r} own_after={c.get('own_nodes_after')!r} "
                         f"foreign={c.get('foreign_r87a_nodes')!r}")
    lines.append("")
    lines.append("LEGNAME IDENTITY run1 vs run2:")
    for e, v in report["legname_diff"].items():
        lines.append(f"   {e:26s} identical={v['identical']} "
                     f"only1={v['only_run1']} only2={v['only_run2']}")
    txt = "\n".join(lines) + "\n"
    open(os.path.join(os.path.dirname(__file__), "census.out"), "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
