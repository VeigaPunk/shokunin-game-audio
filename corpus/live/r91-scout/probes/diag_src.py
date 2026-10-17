#!/usr/bin/env python3
"""r91 scout diagnostic: why did the F1s remap-source chain stay suspended?

Bounded (wall 25 s total, explicit teardown, verified-index unloads).
Seat names: r91s_diag_*.
"""
import json, os, signal, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from driver import (sh, pw_dump, nodes_by_prefix, links_raw, relevant_links,
                    load_null_sink, load_remap_source, unload_verified)

NS = "r91s_diag_ns"
SRC = "r91s_diag_src"
REC = "r91s_diag_rec"

def state_of(prefix):
    dump, _ = pw_dump()
    nodes = nodes_by_prefix(dump, prefix)
    if not nodes:
        return None
    props = nodes[0]["props"]
    return {"id": nodes[0]["id"], "state": nodes[0]["state"],
            "driver": props.get("node.driver"), "name": props.get("node.name"),
            "dont_reconnect": props.get("node.dont-reconnect")}

def main():
    ns = load_null_sink(NS)
    print("ns load:", ns["ok"], ns["idx"])
    tone = subprocess.Popen(["gst-launch-1.0", "-q", "audiotestsrc", "wave=sine",
                             "freq=997", "is-live=true", "num-buffers=1000000", "!",
                             "audio/x-raw,format=S16LE,rate=48000,channels=2", "!",
                             "pipewiresink", "client-name=r91s_diag_tone", "target-object=" + NS],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            start_new_session=True)
    time.sleep(1.5)
    print("tone:", json.dumps(state_of("r91s_diag_tone")))
    print("ns:", json.dumps(state_of(NS)))
    src = load_remap_source(SRC, NS)
    print("src load:", src["ok"], src["idx"])
    time.sleep(1.5)
    print("src:", json.dumps(state_of(SRC)))
    out = "/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r91-scout/tmp/diag_rec.wav"
    rec = subprocess.Popen(["pw-record", "-P", "node.name=" + REC, "--target", SRC,
                            "-n", "1000000", out],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           start_new_session=True)
    for t in (0.5, 1.5, 3.0):
        time.sleep(t if t == 0.5 else t - 0.5)
        sz = os.path.getsize(out) if os.path.exists(out) else None
        print(f"t~{t}: rec={json.dumps(state_of(REC))} bytes={sz}")
    print("links:", json.dumps(relevant_links(links_raw()["stdout"]), indent=0)[:1200])
    # teardown
    try:
        os.killpg(os.getpgid(rec.pid), signal.SIGKILL)
    except ProcessLookupError:
        pass
    rec.wait(timeout=5)
    try:
        os.killpg(os.getpgid(tone.pid), signal.SIGKILL)
    except ProcessLookupError:
        pass
    tone.wait(timeout=5)
    print("unload src:", unload_verified(src["idx"], SRC))
    print("unload ns:", unload_verified(ns["idx"], NS))
    if os.path.exists(out):
        os.unlink(out)

if __name__ == "__main__":
    main()
