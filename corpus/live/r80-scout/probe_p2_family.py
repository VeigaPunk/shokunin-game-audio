#!/usr/bin/env python3
"""P2 — the `pactl load-module` family: acceptance table + what lands in pw-dump.

Every leg is run REPS times; each rep loads fresh, observes the graph keyed by
`pulse.module.id == index` (not by name, so auto-named modules are caught),
then unloads.  Receipts under runs/p2-family/.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r80_probe import Receipt, load, unload, snap, pactl_sinks, pactl_sources, run

REPS = 3
T = "r80_p2"           # name prefix

# (label, module name, args, host-risk?)
ROWS = [
    ("null-bare",     "module-null-sink",       [], False),
    ("null-named",    "module-null-sink",       [f"sink_name={T}_n1"], False),
    ("null-props",    "module-null-sink",       [f"sink_name={T}_n2",
                                                 "sink_properties=device.description=r80desc media.class=Audio/Sink"], False),
    ("null-fmt-rate", "module-null-sink",       [f"sink_name={T}_n3", "format=s16le", "rate=44100",
                                                 "channels=2", "channel_map=front-left,front-right"], False),
    ("null-linger",   "module-null-sink",       [f"sink_name={T}_n4", "sink_properties=object.linger=true"], False),
    ("null-nofail",   "module-null-sink",       [f"sink_name={T}_n5", "nofail=1"], False),
    ("null-namereg",  "module-null-sink",       [f"sink_name={T}_n6", "namereg_fail=false"], False),
    ("remap-bare",    "module-remap-sink",      [f"sink_name={T}_r1"], False),
    ("remap-master",  "module-remap-sink",      [f"sink_name={T}_r2", "master=@DEFAULT_SINK@"], False),
    ("remap-full",    "module-remap-sink",      [f"sink_name={T}_r3", "master=@DEFAULT_SINK@",
                                                 "master_channel_map=front-right,front-left",
                                                 "channels=2", "channel_map=front-left,front-right",
                                                 "remix=yes", "resample_method=trivial"], False),
    ("remapsrc",      "module-remap-source",    [f"source_name={T}_rs1", "master=@DEFAULT_SOURCE@"], False),
    ("combine-bare",  "module-combine-sink",    [f"sink_name={T}_c1"], False),
    ("combine-slaves","module-combine-sink",    [f"sink_name={T}_c2", "slaves=@DEFAULT_SINK@"], False),
    ("combine-sinks", "module-combine-sink",    [f"sink_name={T}_c3", "sinks=@DEFAULT_SINK@"], False),
    ("combine-adj",   "module-combine-sink",    [f"sink_name={T}_c4", "slaves=@DEFAULT_SINK@", "adjust_time=1"], False),
    ("echocancel",    "module-echo-cancel",     [f"sink_name={T}_e1", f"source_name={T}_e1s",
                                                 "aec_method=webrtc", "aec_args=analog_gain_control=0"], False),
    ("echo-null",     "module-echo-cancel",     [f"sink_name={T}_e2", f"source_name={T}_e2s",
                                                 "aec_method=null"], False),
    ("loopback",      "module-loopback",        [f"sink_name={T}_l1", "source=@DEFAULT_MONITOR@",
                                                 "sink=@DEFAULT_SINK@"], False),
    ("vsink",         "module-virtual-sink",    [f"sink_name={T}_v1"], False),
    ("vsource",       "module-virtual-source",  [f"source_name={T}_v2"], False),
    ("pipesink",      "module-pipe-sink",       [f"sink_name={T}_p1",
                                                 f"file={os.path.dirname(os.path.abspath(__file__))}/tmp/r80_p1.fifo"], False),
    ("always-sink",   "module-always-sink",     [], True),
    ("unknown-name",  "module-does-not-exist",  [], False),
    ("native-name",   "libpipewire-module-null-audio-sink", [], False),
    ("pw-combine",    "libpipewire-module-combine-stream", ["node.name=r80_p2_nat1",
                                                            "stream.props={ media.class=Audio/Sink }"], False),
]


def by_mod_id(s, idx):
    return {k: v for k, v in s["nodes"].items() if v.get("pulse.module.id") == idx}


def main():
    rc = Receipt("p2-family")
    for label, mod, args, risky in ROWS:
        reps = []
        for rep in range(REPS):
            pre = snap()
            idx, r = load(mod, *args)
            time.sleep(0.35)
            s = snap()
            nodes = by_mod_id(s, idx) if idx else {}
            # links touching our new nodes
            ids = set(int(k) for k in nodes)
            links = [l for l in s["links"] if l["out.node"] in ids or l["in.node"] in ids]
            ps, pss = pactl_sinks(), pactl_sources()
            new_sinks = {k: v for k, v in ps.items() if k not in pactl_sinks_of(pre)}
            u = unload(idx) if idx else None
            time.sleep(0.4)
            after = snap()
            gone = {k: (k not in after["nodes"]) for k in nodes}
            reps.append({"rep": rep, "index": idx, "load": r, "nodes": nodes,
                         "links": links, "new_sinks": new_sinks,
                         "unload": u, "nodes_gone_after_unload": gone})
            time.sleep(0.25)
        sig = set()
        for x in reps:
            sig.add(json.dumps({"rc": x["load"]["rc"], "err": x["load"]["stderr"].strip(),
                                "names": sorted(v["name"] for v in x["nodes"].values()),
                                "classes": sorted(v["class"] for v in x["nodes"].values()),
                                "links": len(x["links"])}, sort_keys=True))
        rc.leg(label, {"module": mod, "args": args, "risky": risky, "reps": reps,
                       "stable": len(sig) == 1, "n_sigs": len(sig)})
        r0 = reps[0]
        rc.note(f"{label:14s} {mod:24s} rc={r0['load']['rc']} idx={r0['index']} "
                f"err={r0['load']['stderr'].strip()[:80]!r} "
                f"nodes={[(v['name'], v['class'], v['n_in'], v['n_out']) for v in r0['nodes'].values()]} "
                f"links={[(l['out'], l['in']) for l in r0['links']]} stable={len(sig)==1}")
        time.sleep(0.3)
    rc.close()


def pactl_sinks_of(snapd):
    return {k: v["name"] for k, v in snapd["nodes"].items()
            if v.get("class") in ("Audio/Sink", "Audio/Source")}


if __name__ == "__main__":
    main()
