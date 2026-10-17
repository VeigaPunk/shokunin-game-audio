#!/usr/bin/env python3
"""R79 probe B — pw-loopback capture-side (-C) target lattice + channel matrix.

Playback side is pinned to a probe-owned null sink on every leg. Legs whose
capture side falls back to the shared default source (mic) are content-labelled
`foreign_risk`; no leg feeds tone into the shared default sink.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r79_probe import (DEFAULT_SINK, DEFAULT_SOURCE, LINE_SOURCE, RAW, TAG,
                       Graph, analyze, kill, loopback_start, null_sink_load,
                       popen_err, pw_dump, run_leg, save, sh, tone_start,
                       wait_nodes)

out = {"probe": "b-capture-matrix", "tag": TAG, "legs": [],
       "defaults": {"sink": DEFAULT_SINK, "source": DEFAULT_SOURCE}}
ns_a, ns_b = f"r79_ns_a_{TAG}", f"r79_ns_b_{TAG}"
mods = [null_sink_load(ns_a), null_sink_load(ns_b)]
time.sleep(0.5)
SINK_PROP = "stream.capture.sink=true"

LEGS = [
    # id, argv tail, tone?, note
    ("B01-base", ["-C", ns_a, "-i", SINK_PROP, "-P", ns_b], True,
     "sink target + capture.sink prop"),
    ("B02-sink-noprop", ["-C", ns_a, "-P", ns_b], False,
     "sink target, prop absent"),
    ("B03-dotmonitor", ["-C", ns_a + ".monitor", "-P", ns_b], False,
     "pulse-style .monitor alias"),
    ("B04-real-source", ["-C", LINE_SOURCE, "-P", ns_b], False,
     "real Audio/Source node"),
    ("B05-garbage", ["-C", "no_such_node_xyz", "-P", ns_b], False,
     "unresolvable name"),
    ("B06-target0", ["-C", "0", "-P", ns_b], False,
     "pw-cat --target 0 idiom"),
    ("B07-prop-false", ["-C", ns_a, "-i", "stream.capture.sink=false", "-P", ns_b], False,
     "prop explicitly false"),
    ("B08-prop-beats-flag", ["-C", LINE_SOURCE, "-i",
                             f"target.object={ns_a} {SINK_PROP}", "-P", ns_b], True,
     "target.object prop + real flag"),
    ("B09-prop-garbage", ["-i", "target.object=no_such_node_xyz " + SINK_PROP,
                           "-P", ns_b], False, "unresolvable target.object prop, sink prop true"),
    ("B10-autoconnect-off", ["-C", ns_a, "-i", SINK_PROP + " node.autoconnect=false",
                             "-P", ns_b], True, "node.autoconnect=false + valid target"),
    ("B11-autoconnect-off-garbage", ["-i", "node.autoconnect=false", "-P", ns_b], False,
     "node.autoconnect=false, no target"),
    ("B12-source-prop", ["-C", DEFAULT_SOURCE, "-i", SINK_PROP, "-P", ns_b], False,
     "real default source + sink prop"),
]

try:
    for lid, args, tone, note in LEGS:
        leg = run_leg(lid, f"{TAG}_{lid.split('-')[0].lower()}", args,
                      rec_sink=ns_b, tone_into=ns_a if tone else None,
                      secs=12)
        leg["note"] = note
        leg["tone_playing"] = tone
        if not tone:
            leg["content_note"] = ("no tone: destination sink carries silence; "
                                   "topology is the witness")
        out["legs"].append(leg)
        c = leg.get("content") or {}
        print(f"{lid:24s} in_peers={leg.get('samples',{}).get('t1.0',{}).get('input_peers_in')} "
              f"class={c.get('class')}")

    # ---- channel-map / matrix group: full node props + content
    for lid, extra in (("CM1-mono-c1-m", ["-c", "1", "-m", "[ MONO ]"]),
                       ("CM2-c1-only", ["-c", "1"]),
                       ("CM3-m-only", ["-m", "[ MONO ]"]),
                       ("CM4-m-unbracketed", ["-m", "MONO"])):
        name = f"{TAG}_{lid.split('-')[0].lower()}"
        args = ["-C", ns_a, "-i", SINK_PROP, "-P", ns_b] + extra
        lb = loopback_start(name, args, 8)
        g, got, wait_s = wait_nodes(Graph(pw_dump()), name, 2)
        leg = {"leg": lid, "args": args, "nodes_seen": got, "wait_s": wait_s}
        tone = tone_start(ns_a, f"{TAG}_{lid}_tone")
        try:
            time.sleep(1.2)
            g = Graph(pw_dump())
            leg["edges"] = g.edges(name)
            leg["props"] = {}
            for n in got:
                p = g.nodes[n]["props"]
                leg["props"][n] = {k: p.get(k) for k in
                                   ("audio.channels", "audio.position",
                                    "media.class", "port.group", "node.name")}
                leg["props"][n]["ports_in"] = [x[0] for x in g.nodes[n]["in"]]
                leg["props"][n]["ports_out"] = [x[0] for x in g.nodes[n]["out"]]
            recp = os.path.join(RAW, f"{lid}_{TAG}.wav")
            rr = __import__("r79_probe").rec_monitor(
                ns_b, recp, 24000, f"{TAG}_{lid}_rec")
            leg["record"] = {k: rr[k] for k in ("rc", "err", "bytes")}
            leg["content"] = analyze(recp)
            leg["loopback_stderr"] = popen_err(lb)
        finally:
            kill(tone)
            kill(lb)
        out["legs"].append(leg)
        c = leg.get("content") or {}
        print(f"{lid:24s} props={leg.get('props')} class={c.get('class')}")
finally:
    for m in mods:
        if m["module_id"]:
            sh(["pactl", "unload-module", str(m["module_id"])], timeout=10.0)
    out["cleanup"] = {"unloaded": [m["module_id"] for m in mods]}
    out["null_sinks"] = mods

save("probe-b-capture-r79.json", out)
print("saved")
