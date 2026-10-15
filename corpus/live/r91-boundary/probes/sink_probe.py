#!/usr/bin/env python3
"""r91b: does a non-capture gst path reconnect after target loss?

Scout headline 3: gstpipewiresink does not set DONT_RECONNECT, so r81's
playback re-link law stands.  That is a prop/source claim; the *behaviour* on
target loss was never measured.  This probe measures it with a data source that
never blocks: `fakesrc` -> pipewiresink targeting a seat null sink, then the
sink module is unloaded and we watch (a) whether the element gets a new link
(back to the default sink), (b) whether its stream state changes, and (c)
whether the element's process callback keeps being called (counter via
GST_DEBUG is avoided; instead the element's own node state + link set are
sampled, and the bus is watched for CLOCK_LOST/ERROR/EOS).

Bounded: wall cap, killpg, seat-owned names r91b_*/gst_r91b_* only.
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
                        pw_dump, nodes_by_prefix, relevant_links, sh)

SCRATCH = "/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r91-boundary"
STATE_RE = re.compile(r"^\s*\*?\s*state:\s*\"?([a-z]+)\"?", re.M)


def one(name, ns, wall=4.6):
    leg_dir = os.path.join(RUNS, name)
    os.makedirs(leg_dir, exist_ok=True)
    n = load_null_sink(ns)
    prefix = "gst_r91b_snk"
    argv = ["gst-launch-1.0", "-q", "fakesrc", "is-live=true",
            "filltype=3", "num-buffers=1000000", "!",
            "audio/x-raw,format=S16LE,rate=48000,channels=2", "!",
            "pipewiresink", "client-name=" + prefix, "target-object=" + ns,
            "sync=false"]
    log = open(os.path.join(leg_dir, "combined.log"), "wb")
    p = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT,
                         start_new_session=True)
    t0 = time.monotonic()
    unload = None
    timeline = []
    st = {"node": None}
    try:
        while True:
            t = time.monotonic() - t0
            if t >= 1.2 and unload is None:
                unload = unload_verified(n["idx"], ns)
            if t >= wall:
                break
            if st["node"] is None:
                d, _ = pw_dump()
                nn = nodes_by_prefix(d, prefix)
                if nn:
                    st["node"] = nn[0]
            s = {"t": round(t, 2)}
            if st["node"] is not None:
                info = sh(["pw-cli", "info", str(st["node"]["id"])], timeout=8)
                m = STATE_RE.search(info["stdout"])
                s["stream_state"] = m.group(1) if m else None
                s["node_state"] = st["node"]["state"]
                s["dont_reconnect"] = st["node"]["props"].get("node.dont-reconnect")
            s["links"] = relevant_links(sh(["pw-link", "-l"], timeout=8)["stdout"])
            timeline.append(s)
            time.sleep(0.2)
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
    post = [s for s in timeline if unload and s["t"] >= 1.5]
    rec = {
        "leg": name, "argv": argv, "ns_load": n, "unload": unload,
        "rc": rc, "timeline": timeline,
        "props_at_connect": (st["node"] or {}).get("props") and {
            k: (st["node"]["props"] or {}).get(k) for k in
            ("node.dont-reconnect", "node.name", "target.object", "node.target")},
        "node_state_after_loss": [s.get("node_state") for s in post],
        "links_after_loss": [l for s in post for l in (s.get("links") or [])][:12],
        "log_head": open(os.path.join(leg_dir, "combined.log")).read()[:600],
    }
    with open(os.path.join(leg_dir, "receipt.json"), "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    print(json.dumps({k: rec[k] for k in
                      ("leg", "props_at_connect", "node_state_after_loss",
                       "links_after_loss", "rc", "unload")}, indent=1))
    unload_verified(n["idx"], ns)


if __name__ == "__main__":
    one("S1_gst_sink_targetloss", "r91b_ns_sink")
