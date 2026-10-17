#!/usr/bin/env python3
"""R79 probe E — the hot-plug pseudo-surface: null-sink module load/unload while
a pw-loopback routes through it.

Contamination discipline: the tone is stopped before any unload, so any silent
re-link to the shared default sink carries digital silence. Content witnesses
are only taken while the destination is a live probe-owned sink.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r79_probe import (RAW, TAG, Graph, analyze, kill, loopback_start,
                       null_sink_load, null_sink_unload, pw_dump, reap,
                       rec_monitor, save, sh, spawn, tone_start, wait_nodes)

out = {"probe": "e-hotplug", "tag": TAG, "legs": []}
ns_a, ns_b = f"r79_ns_a_{TAG}", f"r79_ns_b_{TAG}"
hp, hp2 = f"r79_hp_{TAG}", f"r79_hp2_{TAG}"


def log(m):
    print(m, flush=True)


def sample(lb_name, sinks, when):
    g = Graph(pw_dump())
    return {"t": when, "edges": g.edges(lb_name),
            "input_peers_in": g.peers("input." + lb_name, "in"),
            "output_peers_out": g.peers("output." + lb_name, "out"),
            "lb_nodes_present": [n for n in g.nodes if lb_name in n],
            "sinks_present": [s for s in sinks if s in g.nodes]}


mods = [null_sink_load(ns_a), null_sink_load(ns_b), null_sink_load(hp)]
time.sleep(0.5)

try:
    # ---------------------------------------------------------------- E1
    # unload the PLAYBACK target mid-route
    lb_name = f"{TAG}_e1"
    lb = loopback_start(lb_name, ["-C", ns_a, "-i", "stream.capture.sink=true",
                                  "-P", hp], 30)
    g, got, wait_s = wait_nodes(Graph(pw_dump()), lb_name, 2)
    leg = {"leg": "E1-unload-playback-target", "nodes_seen": got, "phases": []}
    tone = tone_start(ns_a, f"{TAG}_e1_tone")
    try:
        time.sleep(1.0)
        p = os.path.join(RAW, f"E1-pre-unload_{TAG}.wav")
        rr = rec_monitor(hp, p, 24000, f"{TAG}_e1rec")
        leg["phases"].append({"phase": "pre-unload",
                              "content": analyze(p),
                              "record_bytes": rr["bytes"],
                              "sample": sample(lb_name, [ns_a, ns_b, hp], "pre")})
        kill(tone)                      # silence before the unload
        time.sleep(0.8)
        u = null_sink_unload(mods[2]["module_id"])
        leg["unload"] = {"module_id": mods[2]["module_id"], "rc": u["rc"],
                         "err": u["err"].strip(), "at": round(time.monotonic(), 2)}
        for dt in (0.5, 1.5, 3.0):
            time.sleep(dt if dt == 0.5 else dt - leg["phases"][-1].get("dt", 0.5))
            leg["phases"].append({"phase": f"post-unload+{dt}",
                                  "dt": dt,
                                  "sample": sample(lb_name, [ns_a, ns_b, hp], f"+{dt}")})
        leg["loopback_alive"] = lb.poll() is None
        leg.update(reap(lb, wait=2.0))
    finally:
        kill(tone)
        kill(lb)
    out["legs"].append(leg)
    save("probe-e-hotplug-r79.json", out)
    log(f"E1 post edges: {leg['phases'][-1]['sample']['edges']} "
        f"alive={leg['loopback_alive']} rc={leg.get('rc')}")

    # ---------------------------------------------------------------- E2
    # load the PLAYBACK target after the route is already up (hot-plug return)
    lb_name = f"{TAG}_e2"
    lb = loopback_start(lb_name, ["-C", ns_a, "-i", "stream.capture.sink=true",
                                  "-P", hp2], 30)
    g, got, wait_s = wait_nodes(Graph(pw_dump()), lb_name, 2)
    leg = {"leg": "E2-load-playback-target", "nodes_seen": got, "phases": []}
    try:
        time.sleep(1.0)
        leg["phases"].append({"phase": "pre-load", "dt": 0,
                              "sample": sample(lb_name, [ns_a, ns_b, hp2], "pre")})
        m2 = null_sink_load(hp2)
        leg["load"] = m2
        for dt in (0.5, 1.5, 3.0):
            time.sleep(dt if dt == 0.5 else dt - leg["phases"][-1]["dt"])
            leg["phases"].append({"phase": f"post-load+{dt}", "dt": dt,
                                  "sample": sample(lb_name, [ns_a, ns_b, hp2],
                                                   f"+{dt}")})
        linked_to_probe = any(hp2 in e for e in leg["phases"][-1]["sample"]["edges"])
        leg["relinked_to_new_sink"] = linked_to_probe
        if linked_to_probe:                     # safe: destination is probe-owned
            tone = tone_start(ns_a, f"{TAG}_e2_tone")
            try:
                time.sleep(1.0)
                p = os.path.join(RAW, f"E2-post-load_{TAG}.wav")
                rr = rec_monitor(hp2, p, 24000, f"{TAG}_e2rec")
                leg["content"] = analyze(p)
                leg["record_bytes"] = rr["bytes"]
            finally:
                kill(tone)
        else:
            leg["content"] = None
            leg["content_note"] = ("no tone: post-load destination is the shared "
                                   "default sink; topology is the witness")
        leg.update(reap(lb, wait=2.0))
    finally:
        kill(lb)
    out["legs"].append(leg)
    save("probe-e-hotplug-r79.json", out)
    log(f"E2 relinked={leg['relinked_to_new_sink']} "
        f"edges={leg['phases'][-1]['sample']['edges']} class={(leg.get('content') or {}).get('class')}")
    if m2["module_id"]:
        null_sink_unload(m2["module_id"])

    # ---------------------------------------------------------------- E3
    # unload the CAPTURE target mid-route
    lb_name = f"{TAG}_e3"
    lb = loopback_start(lb_name, ["-C", ns_a, "-i", "stream.capture.sink=true",
                                  "-P", ns_b], 30)
    g, got, wait_s = wait_nodes(Graph(pw_dump()), lb_name, 2)
    leg = {"leg": "E3-unload-capture-target", "nodes_seen": got, "phases": []}
    tone = tone_start(ns_a, f"{TAG}_e3_tone")
    try:
        time.sleep(1.0)
        p = os.path.join(RAW, f"E3-pre-unload_{TAG}.wav")
        rr = rec_monitor(ns_b, p, 24000, f"{TAG}_e3rec")
        leg["phases"].append({"phase": "pre-unload", "dt": 0,
                              "content": analyze(p), "record_bytes": rr["bytes"],
                              "sample": sample(lb_name, [ns_a, ns_b], "pre")})
        kill(tone)
        time.sleep(0.8)
        u = null_sink_unload(mods[0]["module_id"])
        leg["unload"] = {"module_id": mods[0]["module_id"], "rc": u["rc"],
                         "err": u["err"].strip()}
        for dt in (0.5, 1.5, 3.0):
            time.sleep(dt if dt == 0.5 else dt - leg["phases"][-1]["dt"])
            leg["phases"].append({"phase": f"post-unload+{dt}", "dt": dt,
                                  "sample": sample(lb_name, [ns_a, ns_b], f"+{dt}")})
        leg["loopback_alive"] = lb.poll() is None
        leg.update(reap(lb, wait=2.0))
    finally:
        kill(tone)
        kill(lb)
    out["legs"].append(leg)
    save("probe-e-hotplug-r79.json", out)
    log(f"E3 post edges: {leg['phases'][-1]['sample']['edges']} "
        f"alive={leg['loopback_alive']} rc={leg.get('rc')}")
finally:
    for m in mods:
        if m["module_id"]:
            sh(["pactl", "unload-module", str(m["module_id"])], timeout=10.0)
    out["cleanup"] = {"unloaded": [m["module_id"] for m in mods]}
    out["null_sinks"] = mods

save("probe-e-hotplug-r79.json", out)
log("saved")
