#!/usr/bin/env python3
"""r91b: the no-prop connect law, verified target existence.

Scout F1 (pw-record, no props, --target <sink>) never links: 44 B, suspended.
Scout §0.5 mechanism: `getTargetDirection` returns "output" for a no-prop
capture, and `find-defined-target` requires the target's direction to match,
so a sink-name target is filtered out.

But the same source read says the capture element sets
PW_STREAM_FLAG_DONT_RECONNECT **unconditionally on the capture element**
(gstpipewiresrc.c:1207) and uses `target-object=` + `node.target`.  This probe
re-runs the no-prop case for BOTH client families (pw-record and pipewiresrc),
and additionally for a pipewiresrc with an explicit capture.sink prop, with the
target's existence verified in pw-dump immediately before each leg.

Bounded: element bound in argv, wall cap, byte cap in the owning loop, killpg.
Seat-owned names r91b_*/gst_r91b_* only.
"""
import json
import os
import re
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r91b_probe import (TMP, RUNS, load_null_sink, unload_verified, sha,
                        pw_dump, nodes_by_prefix, relevant_links, sh, wav_head)

SCRATCH = "/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r91-boundary"
NS = "r91b_ns_connect"
SRC = "r91b_src_connect"
BYTE_CAP = 4 * 1024 * 1024
STATE_RE = re.compile(r"^\s*\*?\s*state:\s*\"?([a-z]+)\"?", re.M)

LEGS = {
    "C1_pwrecord_noprop_sink": {
        "argv": lambda out: ["pw-record", "-P", "node.name=r91b_c1",
                             "--target", NS, "-n", "1000000", out],
        "prefix": "r91b_c1", "target": "sink", "props": False},
    "C2_gst_noprop_sink": {
        "argv": lambda out: ["gst-launch-1.0", "-q", "pipewiresrc",
                             "client-name=gst_r91b_c2", "target-object=" + NS,
                             "num-buffers=1000000", "!",
                             "audio/x-raw,format=S16LE,rate=48000,channels=2",
                             "!", "wavenc", "!", "filesink", "location=" + out],
        "prefix": "gst_r91b_c2", "target": "sink", "props": False},
    "C3_gst_capsink_sink": {
        "argv": lambda out: ["gst-launch-1.0", "-q", "pipewiresrc",
                             "client-name=gst_r91b_c3", "target-object=" + NS,
                             "stream-properties=props,stream.capture.sink=true",
                             "num-buffers=1000000", "!",
                             "audio/x-raw,format=S16LE,rate=48000,channels=2",
                             "!", "wavenc", "!", "filesink", "location=" + out],
        "prefix": "gst_r91b_c3", "target": "sink", "props": True},
    "C4_pwrecord_noprop_source": {
        "argv": lambda out: ["pw-record", "-P", "node.name=r91b_c4",
                             "--target", SRC, "-n", "1000000", out],
        "prefix": "r91b_c4", "target": "source", "props": False},
}


def one(name, spec, wall=3.0):
    leg_dir = os.path.join(RUNS, name)
    os.makedirs(leg_dir, exist_ok=True)
    out = os.path.join(TMP, name + ".wav")
    if os.path.exists(out):
        os.unlink(out)
    sink = load_null_sink(NS) if spec["target"] == "sink" else None
    src = None
    if spec["target"] == "source":
        src = load_null_sink(NS)
        # remap-source so the target is a real SOURCE node
        r = sh(["pactl", "load-module", "module-remap-source",
                "source_name=" + SRC, "master=" + NS + ".monitor"])
        src = {"idx": int(r["stdout"].strip()) if r["stdout"].strip().isdigit() else None,
               "load": r}
    time.sleep(0.9)
    dump, _ = pw_dump()
    tname = NS if spec["target"] == "sink" else SRC
    present = [n for n in nodes_by_prefix(dump, tname)]
    argv = spec["argv"](out)
    log = open(os.path.join(leg_dir, "combined.log"), "wb")
    p = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT,
                         start_new_session=True)
    t0 = time.monotonic()
    timeline = []
    st = {"node": None}
    try:
        while True:
            t = time.monotonic() - t0
            if t >= wall:
                break
            if os.path.exists(out) and os.path.getsize(out) > BYTE_CAP:
                break
            if st["node"] is None:
                d, _ = pw_dump()
                nn = nodes_by_prefix(d, spec["prefix"])
                if nn:
                    st["node"] = nn[0]
            s = {"t": round(t, 2),
                 "bytes": os.path.getsize(out) if os.path.exists(out) else None}
            if st["node"] is not None:
                info = sh(["pw-cli", "info", str(st["node"]["id"])], timeout=8)
                m = STATE_RE.search(info["stdout"])
                s["stream_state"] = m.group(1) if m else None
                s["node_state"] = st["node"]["state"]
                s["props"] = {k: st["node"]["props"].get(k) for k in
                              ("node.dont-reconnect", "stream.capture.sink",
                               "target.object", "node.target")}
            s["links"] = relevant_links(sh(["pw-link", "-l"], timeout=8)["stdout"])
            timeline.append(s)
            time.sleep(0.25)
    finally:
        rc = p.poll()
        if rc is None:
            try:
                os.killpg(os.getpgid(p.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
            try:
                rc = p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                rc = None
        log.close()
    sizes = [s["bytes"] for s in timeline if s["bytes"] is not None]
    links_any = any(s.get("links") for s in timeline)
    rec = {"leg": name, "argv": argv, "target_present_in_dump": bool(present),
           "target_nodes": [{"name": n["props"].get("node.name"),
                             "state": n["state"]} for n in present],
           "sink_load": sink, "src_load": src,
           "rc": rc, "final_bytes": sizes[-1] if sizes else None,
           "max_bytes": max(sizes) if sizes else None,
           "links_ever": links_any,
           "post_links": [l for s in timeline for l in (s.get("links") or [])][:8],
           "node_props": (st["node"] or {}).get("props"),
           "node_state_last": (st["node"] or {}).get("state"),
           "timeline": timeline,
           "log_head": open(os.path.join(leg_dir, "combined.log")).read()[:800]}
    with open(os.path.join(leg_dir, "receipt.json"), "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    print(json.dumps({k: rec[k] for k in
                      ("leg", "target_present_in_dump", "rc", "final_bytes",
                       "max_bytes", "links_ever", "node_props",
                       "node_state_last")}, sort_keys=True))
    if src and src.get("idx"):
        unload_verified(src["idx"], SRC)
    if sink and sink.get("idx"):
        unload_verified(sink["idx"], NS)
    if os.path.exists(out):
        os.unlink(out)


if __name__ == "__main__":
    which = sys.argv[1:] or list(LEGS)
    for k in which:
        one(k, LEGS[k])
