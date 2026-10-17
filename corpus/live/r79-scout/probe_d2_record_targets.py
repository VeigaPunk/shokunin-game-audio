#!/usr/bin/env python3
"""R79 probe D2 — pw-record --target against pw-loopback-created nodes,
with the link graph sampled WHILE the record stream is alive.

(The first pass sampled after pw-record exited, so `peers` was vacuous.)
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r79_probe import (RAW, TAG, Graph, analyze, kill, loopback_start,
                       null_sink_load, pw_dump, reap, save, sh, spawn,
                       tone_start, wait_nodes)

out = {"probe": "d2-record-targets", "tag": TAG, "legs": []}
ns_a, ns_b = f"r79_ns_a_{TAG}", f"r79_ns_b_{TAG}"
mods = [null_sink_load(ns_a), null_sink_load(ns_b)]
time.sleep(0.5)


def log(m):
    print(m, flush=True)


try:
    lb_name = f"{TAG}_d2loop"
    lb = loopback_start(lb_name, ["-C", ns_a, "-i", "stream.capture.sink=true",
                                  "-P", ns_b], 60)
    g, got, wait_s = wait_nodes(Graph(pw_dump()), lb_name, 2)
    tone = tone_start(ns_a, f"{TAG}_d2loop_tone")
    try:
        time.sleep(1.0)
        legs = [
            ("D2a-input-node", f"input.{lb_name}", []),
            ("D2b-output-node", f"output.{lb_name}", []),
            ("D2c-input-capsink", f"input.{lb_name}", ["stream.capture.sink=true"]),
            ("D2d-input-capsink-on-output", f"output.{lb_name}",
             ["stream.capture.sink=true"]),
        ]
        for lid, target, extra in legs:
            tag = f"{TAG}_{lid.split('-')[0].lower()}"
            path = os.path.join(RAW, f"{lid}_{TAG}.wav")
            argv = ["pw-record", "-P", f"node.name={tag}"]
            for x in extra:
                argv += ["-P", x]
            argv += ["--target", target, "-n", "240000", path]
            p = spawn(argv)
            rec = {"leg": lid, "argv": argv, "target": target, "extra": extra}
            try:
                time.sleep(1.0)
                g = Graph(pw_dump())
                rec["rec_peers_in"] = g.peers(tag, "in")
                rec["rec_node_props"] = {
                    k: (g.nodes.get(tag, {}).get("props", {}) or {}).get(k)
                    for k in ("target.object", "stream.capture.sink",
                              "node.autoconnect", "media.class")}
                rec["lb_edges"] = g.edges(lb_name)
            finally:
                rec.update(reap(p, wait=6.0))
            rec["content"] = analyze(path)
            rec["bytes"] = os.path.getsize(path) if os.path.exists(path) else 0
            out["legs"].append(rec)
            save("probe-d2-record-targets-r79.json", out)
            log(f"{lid:26s} peers_in={rec['rec_peers_in']} "
                f"class={rec['content'].get('class')} bytes={rec['bytes']} rc={rec['rc']}")
    finally:
        kill(tone)
        kill(lb)
finally:
    for m in mods:
        if m["module_id"]:
            sh(["pactl", "unload-module", str(m["module_id"])], timeout=10.0)
    out["cleanup"] = {"unloaded": [m["module_id"] for m in mods]}
    out["null_sinks"] = mods

save("probe-d2-record-targets-r79.json", out)
log("saved")
