#!/usr/bin/env python3
"""P1 — module-null-sink argument lattice: what lands in pw-dump.

Each leg runs 3 times (reps), each rep loads a fresh module, snapshots the
graph, then unloads it. Receipts under runs/p1-null-args/.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r80_probe import (Receipt, load, unload, snap, named, pactl_sinks,
                       pactl_sources, run, SEAT)

LEGS = [
    ("bare",        []),
    ("sink_name",   ["sink_name=r80_p1_name"]),
    ("desc",        ["sink_name=r80_p1_desc", "description=r80 desc here"]),
    ("rate44",      ["sink_name=r80_p1_r44", "rate=44100"]),
    ("rate_odd",    ["sink_name=r80_p1_r99", "rate=99999"]),
    ("ch1",         ["sink_name=r80_p1_c1", "channels=1"]),
    ("ch6",         ["sink_name=r80_p1_c6", "channels=6"]),
    ("cm_mono",     ["sink_name=r80_p1_cmm", "channel_map=mono"]),
    ("cm_flfr",     ["sink_name=r80_p1_cmf", "channel_map=front-left,front-right"]),
    ("cm_51",       ["sink_name=r80_p1_cm5", "channel_map=surround-51"]),
    ("cm_bogus",    ["sink_name=r80_p1_cmx", "channel_map=notachannel"]),
    ("fmt_s16",     ["sink_name=r80_p1_f16", "format=s16le"]),
    ("fmt_f32",     ["sink_name=r80_p1_f32", "format=float32le"]),
    ("fmt_bogus",   ["sink_name=r80_p1_fbx", "format=not_a_format"]),
    ("class_ovr",   ["sink_name=r80_p1_cls", "media.class=Audio/Source"]),
    ("obj_linger",  ["sink_name=r80_p1_lng", "object.linger=true"]),
    ("unknown_k",   ["sink_name=r80_p1_unk", "totally.unknown.key=42"]),
    ("dup_name",    ["sink_name=r80_p1_dup"]),          # 2nd load in a leg
    ("sink_props",  ["sink_props=media.class=Audio/Source"]),
    ("no_sink_name_2", []),
]

REPS = 3


def observe(name):
    s = snap()
    hits = named(s, name) if name else {}
    out = {}
    for nid, n in hits.items():
        out[nid] = n
    return out


def main():
    rc = Receipt("p1-null-args")
    gen = {}
    for label, args in LEGS:
        legs = []
        for rep in range(REPS):
            # --- collision leg: load the same sink_name twice before observing
            first = None
            if label == "dup_name":
                first, r1 = load("module-null-sink", *args)
            idx, r = load("module-null-sink", *args)
            t_load = time.time()
            sink = r["stdout"].strip()
            # latency to appear in pw-dump
            seen, tries = None, 0
            while tries < 20:
                s = snap()
                nm = args[0].split("=", 1)[1] if args and "=" in args[0] else None
                hits = named(s, nm) if nm else {}
                if hits:
                    seen = {"tries": tries, "dt": round(time.time() - t_load, 3)}
                    break
                tries += 1
                time.sleep(0.05)
            s = snap()
            nm = args[0].split("=", 1)[1] if args and "=" in args[0] else None
            hits = named(s, nm) if nm else {}
            ps = pactl_sinks()
            pss = pactl_sources()
            # pactl list sinks entry for our sink(s)
            entry = {}
            for k, v in ps.items():
                if k.startswith("r80_p1") or (nm and k == nm):
                    entry[k] = v
            src_entry = {k: v for k, v in pss.items()
                         if k.startswith("r80_p1") or (nm and k == nm + ".monitor")}
            u = unload(idx) if idx else None
            u1 = unload(first) if first else None
            legs.append({
                "rep": rep, "load": r, "index": idx, "stdout": sink,
                "first_of_dup": first, "first_unload": u1,
                "appear": seen, "nodes": hits, "pactl_sinks": entry,
                "pactl_sources": src_entry, "unload": u,
            })
            time.sleep(0.25)
        # summarise: is it stable across reps?
        sigs = set()
        for l in legs:
            sigs.add(json.dumps({
                "rc": l["load"]["rc"], "err": l["load"]["stderr"].strip(),
                "props": {k: v for k, v in sorted(
                    list(l["nodes"].values())[0].items())} if l["nodes"] else None,
            }, sort_keys=True))
        rc.leg(label, {"args": args, "reps": legs, "stable": len(sigs) == 1,
                       "n_sigs": len(sigs)})
        first_node = list(legs[0]["nodes"].values())[0] if legs[0]["nodes"] else None
        rc.note(f"{label:14s} args={args} rc={legs[0]['load']['rc']} "
                f"idx={legs[0]['index']} err={legs[0]['load']['stderr'].strip()[:70]!r} "
                f"node={json.dumps(first_node) if first_node else None} "
                f"stable={len(sigs)==1}")
        gen[label] = legs[0]
        time.sleep(0.3)
    rc.close()
    print("done")


if __name__ == "__main__":
    main()
