#!/usr/bin/env python3
"""R79 probe A — pw-loopback node shape, internal topology, prop syntax.

Q: what does pw-loopback actually create, how are its two streams wired to each
other, and which prop syntax does `-i`/`-o` accept?
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r79_probe import (CFG, DEFAULT_SINK, DEFAULT_SOURCE, Graph, LINE_SOURCE,
                       RAW, SCRATCH, TAG, analyze, kill, loopback_start,
                       null_sink_load, popen_err, pw_dump, run_leg, save,
                       sh, tone_start, wait_nodes)

out = {"probe": "a-shape", "tag": TAG, "legs": [], "env": {}}
r = sh(["pw-metadata"], timeout=10.0)
out["env"]["default_sink"] = DEFAULT_SINK
out["env"]["default_source"] = DEFAULT_SOURCE
out["env"]["metadata"] = [l for l in r["out"].decode().splitlines()
                          if "default.audio" in l]

ns_a, ns_b = f"r79_ns_a_{TAG}", f"r79_ns_b_{TAG}"
ns_b2 = f"r79_ns_b2_{TAG}"
mods = []
for nm in (ns_a, ns_b, ns_b2):
    m = null_sink_load(nm)
    mods.append(m)
out["env"]["null_sinks"] = mods
time.sleep(0.5)

try:
    # ---------------------------------------------------------------- A1
    name = f"{TAG}_a1"
    lb = loopback_start(name, ["-C", ns_a, "-i", "stream.capture.sink=true",
                               "-P", ns_b], 8)
    g, got, wait_s = wait_nodes(Graph(pw_dump()), name, 2)
    tone = tone_start(ns_a, f"{TAG}_a1_tone")
    time.sleep(1.2)
    g = Graph(pw_dump())
    a1 = {"leg": "A1", "name": name,
          "argv": ["pw-loopback", "-n", name, "-C", ns_a, "-i",
                   "stream.capture.sink=true", "-P", ns_b],
          "nodes_seen": got, "wait_s": wait_s,
          "edges": g.edges(name),
          "nodes": {}, "internal_link_client": None, "ports": {}}
    for n in got:
        nd = g.nodes[n]
        a1["nodes"][n] = {k: nd["props"].get(k) for k in sorted(nd["props"])}
        a1["ports"][n] = {"in": [p[0] for p in nd["in"]],
                          "out": [p[0] for p in nd["out"]]}
    for l in g.links:
        if "input." + name in (l["out_node"] or "") and \
           "output." + name in (l["in_node"] or ""):
            a1["internal_link_client"] = l.get("state")
    # raw link objects touching both loopback nodes (client ids of the links)
    raw = pw_dump()
    a1["link_props"] = []
    for o in raw or []:
        if o.get("type", "").endswith("Link"):
            i = o.get("info", {}) or {}
            pr = i.get("props", {}) or {}
            on = g.by_id.get(i.get("output-node-id"), "")
            inn = g.by_id.get(i.get("input-node-id"), "")
            if name in (on or "") + (inn or ""):
                a1["link_props"].append({"out": on, "in": inn,
                                         "client.id": pr.get("client.id"),
                                         "state": i.get("state"),
                                         "format": (i.get("format") or {}).get("format")})
    kill(tone)
    kill(lb)
    a1["loopback_stderr"] = popen_err(lb)
    out["legs"].append(a1)

    # ---------------------------------------------------------------- A2
    # multi-prop syntax: space vs comma separated
    for sid, propstr in (("A2-space", "stream.capture.sink=true media.role=DSP"),
                         ("A2-comma", "stream.capture.sink=true,media.role=DSP")):
        name = f"{TAG}_a2{sid[-5:]}"
        lb = loopback_start(name, ["-C", ns_a, "-i", propstr, "-P", ns_b], 5)
        g, got, wait_s = wait_nodes(Graph(pw_dump()), name, 2)
        leg = {"leg": sid, "propstr": propstr, "nodes_seen": got, "wait_s": wait_s}
        for n in got:
            nd = g.nodes[n]
            leg[n] = {k: nd["props"].get(k) for k in
                      ("stream.capture.sink", "media.role", "target.object")}
        leg["input_peers_in"] = g.peers("input." + name, "in")
        kill(lb)
        out["legs"].append(leg)

    # ---------------------------------------------------------------- A3
    out["legs"].append(run_leg(
        "A3-mono", f"{TAG}_a3", ["-C", ns_a, "-i", "stream.capture.sink=true",
                                 "-P", ns_b, "-c", "1", "-m", "[ MONO ]"],
        rec_sink=ns_b, tone_into=ns_a))

    # ---------------------------------------------------------------- A4
    out["legs"].append(run_leg(
        "A4-ch1-only", f"{TAG}_a4", ["-C", ns_a, "-i", "stream.capture.sink=true",
                                     "-P", ns_b, "-c", "1"],
        rec_sink=ns_b, tone_into=ns_a))

    # ---------------------------------------------------------------- A5
    # absent capture target (-P only): capture side -> ? (contained: sink is ours)
    out["legs"].append(run_leg(
        "A5-noC", f"{TAG}_a5", ["-P", ns_b], rec_sink=ns_b))

    # ---------------------------------------------------------------- A6
    # absent playback target (-C only, silent source): playback side -> default
    out["legs"].append(run_leg(
        "A6-noP", f"{TAG}_a6", ["-C", ns_a, "-i", "stream.capture.sink=true"]))

    # ---------------------------------------------------------------- A7
    # no targets at all is NOT run: it would route the live mic into the shared
    # default sink (SPDIF) while a concurrent r78-baseline seat records its
    # monitor. A5+A6 establish both autoconnect defaults with zero tone leakage.
    out["legs"].append({"leg": "A7-noargs", "verdict": "declined",
                        "reason": "mic->shared default sink contamination window; "
                                  "A5+A6 cover both autoconnect defaults"})
finally:
    kill(None)
    for m in mods:
        if m["module_id"]:
            sh(["pactl", "unload-module", str(m["module_id"])], timeout=10.0)
    out["cleanup"] = {"unloaded": [m["module_id"] for m in mods]}

save("probe-a-shape-r79.json", out)
print(json.dumps(out, indent=1)[:6000])
