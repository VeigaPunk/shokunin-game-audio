#!/usr/bin/env python3
"""R79 probe D — pw-cat playback `-P` prop vector: node latencies, the
stream.capture.sink prop on a PLAYBACK tool, and pw-record --target against a
pw-loopback-created capture node.

Tone/playback targets are probe-owned null sinks only. Legs that can reach the
shared default sink play the 2 s SILENT file, so the topology witness is clean
and the shared sink stays uncontaminated.
"""
import json
import math
import os
import struct
import sys
import time
import wave

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r79_probe import (DEFAULT_SINK, RAW, SCRATCH, TAG, Graph, analyze, kill,
                       loopback_start, null_sink_load, popen_err, pw_dump,
                       reap, rec_target, save, sh, spawn, tone_start, wait_nodes)

SIL = os.path.join(SCRATCH, "silence_r79.wav")
if not os.path.exists(SIL):
    with wave.open(SIL, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(b"\x00" * (48000 * 4))

out = {"probe": "d-pwcat-props", "tag": TAG, "legs": [], "defaults": {"sink": DEFAULT_SINK}}


def log(msg):
    print(msg, flush=True)


def checkpoint():
    save("probe-d-pwcat-r79.json", out)
ns_a, ns_b = f"r79_ns_a_{TAG}", f"r79_ns_b_{TAG}"
mods = [null_sink_load(ns_a), null_sink_load(ns_b)]
time.sleep(0.5)


def node_probe(name, timeout=6.0):
    """Wait for a node named `name`, return (props, params) once."""
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        objs = pw_dump()
        for o in objs or []:
            if o.get("type", "").endswith("Node"):
                p = (o.get("info", {}) or {}).get("props", {}) or {}
                if p.get("node.name") == name:
                    return (o["id"], p, (o.get("info", {}) or {}).get("params", {}))
        time.sleep(0.15)
    return (None, {}, {})


def pwcat_leg(leg_id, extra, target, path, frames=48000, sample_at=0.7):
    name = f"{TAG}_{leg_id.split('-')[0].lower()}"
    argv = ["pw-cat", "-p", "-P", f"node.name={name}"] + extra + \
           ["--target", target, "-n", str(frames), path]
    p = spawn(argv)
    rec = {"leg": leg_id, "argv": argv, "target": target}
    try:
        time.sleep(sample_at)
        nid, props, params = node_probe(name, timeout=3.0)
        rec["node_id"] = nid
        rec["props"] = {k: props.get(k) for k in
                        ("node.latency", "node.rate", "node.force-latency",
                         "media.class", "target.object", "node.autoconnect",
                         "stream.capture.sink", "node.name")}
        rec["Latency_param"] = (params or {}).get("Latency")
        g = Graph(pw_dump())
        rec["edges"] = g.edges(name)
        rec["output_peers_out"] = g.peers(name, "out")
    finally:
        rec.update(reap(p))
    return rec


try:
    # ------------------------------------------------ latency vector (tone -> ns_b)
    TONE = os.path.join(SCRATCH, "tone_r79_long.wav")
    for lid, extra in (
            ("D01-default-latency", []),
            ("D02-flag-10ms", ["--latency", "10ms"]),
            ("D03-flag-256samples", ["--latency", "256"]),
            ("D04-prop-480", ["-P", "node.latency=480"]),
            ("D05-prop-fraction", ["-P", "node.latency=1024/48000"]),
            ("D06-flag-and-prop", ["--latency", "5ms", "-P", "node.latency=2048/48000"]),
            ("D07-flag-zero", ["--latency", "0"]),
            ("D08-prop-zero", ["-P", "node.latency=0"]),
            ("D09-flag-500ms", ["--latency", "500ms"]),
            ("D10-force-latency", ["--latency", "10ms", "-P", "node.force-latency=true"]),
    ):
        leg = pwcat_leg(lid, extra, ns_b, TONE)
        out["legs"].append(leg); checkpoint()
        log(f"{lid:22s} node.latency={leg['props'].get('node.latency')!r} "
              f"Latency={leg['Latency_param']} wall={leg['wall_s']} rc={leg['rc']} "
              f"err={leg['stderr'][:60]!r}")

    # --------------------------------------- stream.capture.sink on a playback tool
    for lid, extra, target, path, tone in (
            ("D11-capsink-valid", ["-P", "stream.capture.sink=true"], ns_b, TONE, True),
            ("D12-capsink-garbage", ["-P", "stream.capture.sink=true"],
             "no_such_sink_xyz", SIL, False),
            ("D13-autoconnect-off", ["-P", "node.autoconnect=false"], ns_b, TONE, True),
    ):
        leg = pwcat_leg(lid, extra, target, path)
        leg["tone_playing"] = tone
        out["legs"].append(leg); checkpoint()
        log(f"{lid:22s} out_peers={leg['output_peers_out']} "
              f"capsink={leg['props'].get('stream.capture.sink')}")

    # --------------------- pw-record --target against pw-loopback-created nodes
    lb_name = f"{TAG}_dloop"
    lb = loopback_start(lb_name, ["-C", ns_a, "-i", "stream.capture.sink=true",
                                  "-P", ns_b], 30)
    g, got, wait_s = wait_nodes(Graph(pw_dump()), lb_name, 2)
    tone = tone_start(ns_a, f"{TAG}_dloop_tone")
    try:
        time.sleep(1.0)
        rec_legs = [
            ("D14-record-input-node", f"input.{lb_name}", []),
            ("D15-record-output-node", f"output.{lb_name}", []),
            ("D16-record-input-capsink", f"input.{lb_name}",
             ["stream.capture.sink=true"]),
        ]
        for lid, target, extra in rec_legs:
            path = os.path.join(RAW, f"{lid}_{TAG}.wav")
            rr = rec_target(target, path, 24000, f"{TAG}_{lid.split('-')[0].lower()}",
                            extra=extra)
            g = Graph(pw_dump())
            leg = {"leg": lid, "target": target, "extra": extra,
                   "record": {k: rr[k] for k in ("rc", "err", "bytes", "exists")},
                   "content": analyze(path),
                   "rec_peers_in": g.peers(f"{TAG}_{lid.split('-')[0].lower()}", "in"),
                   "lb_edges": g.edges(lb_name)}
            out["legs"].append(leg); checkpoint()
            log(f"{lid:24s} target={target} peers_in={leg['rec_peers_in']} "
                  f"class={leg['content'].get('class')} bytes={rr['bytes']}")
        # D17 manual pin onto the loopback capture node's monitor ports
        tag = f"{TAG}_d17"
        path = os.path.join(RAW, f"D17-manual-pin_{TAG}.wav")
        argv = ["pw-record", "-P", f"node.name={tag}", "--target", "0",
                "-n", "24000", path]
        p = spawn(argv)
        try:
            time.sleep(0.8)
            pins = []
            for ch in ("FL", "FR"):
                r = sh(["pw-link", f"input.{lb_name}:monitor_{ch}",
                        f"{tag}:input_{ch}"], timeout=10.0)
                pins.append({"port": ch, "rc": r["rc"], "err": r["err"].strip()})
            p.wait(timeout=10)
            leg = {"leg": "D17-manual-pin", "argv": argv, "pins": pins,
                   "record": {"rc": p.returncode},
                   "content": analyze(path)}
            g = Graph(pw_dump())
            leg["lb_edges_after"] = g.edges(lb_name)
            out["legs"].append(leg); checkpoint()
            log(f"D17-manual-pin pins={pins} class={leg['content'].get('class')}")
        finally:
            kill(p)
    finally:
        kill(tone)
        kill(lb)
finally:
    for m in mods:
        if m["module_id"]:
            sh(["pactl", "unload-module", str(m["module_id"])], timeout=10.0)
    out["cleanup"] = {"unloaded": [m["module_id"] for m in mods]}
    log(f"cleanup unloaded {out['cleanup']['unloaded']}")
    out["null_sinks"] = mods

save("probe-d-pwcat-r79.json", out)
log("saved")
