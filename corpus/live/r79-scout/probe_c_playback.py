#!/usr/bin/env python3
"""R79 probe C — pw-loopback playback-side (-P) target lattice + prop precedence.

Capture side is pinned to a probe-owned null sink (`stream.capture.sink=true`);
the tone only ever plays when the playback destination is a probe-owned sink.
Legs that can reach the shared default sink run on a digital-silent source and
are judged by topology only.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r79_probe import (DEFAULT_SINK, DEFAULT_SOURCE, LINE_SOURCE, RAW, TAG,
                       Graph, analyze, kill, loopback_start, null_sink_load,
                       popen_err, pw_dump, rec_monitor, run_leg, save, sh,
                       tone_start, wait_nodes)

out = {"probe": "c-playback-matrix", "tag": TAG, "legs": [],
       "defaults": {"sink": DEFAULT_SINK, "source": DEFAULT_SOURCE}}
ns_a, ns_b, ns_b2 = (f"r79_ns_a_{TAG}", f"r79_ns_b_{TAG}", f"r79_ns_b2_{TAG}")
mods = [null_sink_load(ns_a), null_sink_load(ns_b), null_sink_load(ns_b2)]
time.sleep(0.5)
SINK_PROP = "stream.capture.sink=true"
CAP = ["-C", ns_a, "-i", SINK_PROP]

# id, argv tail, tone?, rec_sink, note
LEGS = [
    ("C01-base", CAP + ["-P", ns_b], True, ns_b, "sink target honored"),
    ("C02-second-sink", CAP + ["-P", ns_b2], True, ns_b2, "second probe sink"),
    ("C03-garbage", CAP + ["-P", "no_such_sink_xyz"], False, None,
     "unresolvable name"),
    ("C04-source-name", CAP + ["-P", LINE_SOURCE], False, None,
     "Audio/Source name as playback target"),
    ("C05-target0", CAP + ["-P", "0"], False, None, "pw-cat --target 0 idiom"),
    ("C06-absent", CAP, False, None, "no -P at all"),
    ("C07-prop-beats-flag", CAP + ["-P", ns_b, "-o", f"target.object={ns_b2}"],
     True, ns_b2, "target.object prop + -P flag"),
    ("C08-autoconnect-off", CAP + ["-P", ns_b, "-o", "node.autoconnect=false"],
     False, None, "node.autoconnect=false on playback"),
    ("C09-capsink-on-playback", CAP + ["-P", ns_b, "-o", SINK_PROP], True, ns_b,
     "stream.capture.sink=true on the PLAYBACK stream"),
    ("C10-prop-garbage", CAP + ["-P", ns_b, "-o", "target.object=no_such_node_xyz"],
     False, None, "unresolvable target.object prop"),
]

try:
    for lid, args, tone, recsink, note in LEGS:
        leg = run_leg(lid, f"{TAG}_{lid.split('-')[0].lower()}", args,
                      rec_sink=recsink, tone_into=ns_a if tone else None,
                      secs=12)
        leg["note"] = note
        leg["tone_playing"] = tone
        if lid == "C07-prop-beats-flag":
            # control: the flag's sink must stay silent while the prop's sink sings
            ctrl = os.path.join(RAW, f"C07-control-flag-sink_{TAG}.wav")
            rr = rec_monitor(ns_b, ctrl, 24000, f"{TAG}_c07ctrl")
            leg["control"] = {"record": {k: rr[k] for k in ("rc", "err", "bytes")},
                              "content": analyze(ctrl),
                              "note": "flag sink (-P ns_b) while prop routed to ns_b2"}
        out["legs"].append(leg)
        c = leg.get("content") or {}
        print(f"{lid:26s} out_peers={leg.get('samples',{}).get('t1.0',{}).get('output_peers_out')} "
              f"class={c.get('class')}")
finally:
    for m in mods:
        if m["module_id"]:
            sh(["pactl", "unload-module", str(m["module_id"])], timeout=10.0)
    out["cleanup"] = {"unloaded": [m["module_id"] for m in mods]}
    out["null_sinks"] = mods

save("probe-c-playback-r79.json", out)
print("saved")
