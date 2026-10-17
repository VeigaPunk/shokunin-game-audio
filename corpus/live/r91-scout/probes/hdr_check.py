#!/usr/bin/env python3
"""r91 scout: one bounded leg to read the frozen wav header fields directly
(independent check of the r81-boundary corrected constant 0x7FFF0024/0x7FFF0000)."""
import json, os, signal, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from driver import (load_null_sink, unload_verified, run_bounded, sha, TMP)

NS = "r91s_ns1"
OUT = os.path.join(TMP, "hdr_check.wav")
ARGV = ["gst-launch-1.0", "-q", "pipewiresrc", "client-name=gst_r91_hdr",
        "target-object=" + NS, "stream-properties=props,stream.capture.sink=true",
        "num-buffers=1000000", "!", "audio/x-raw,format=S16LE,rate=48000,channels=2",
        "!", "wavenc", "!", "filesink", "location=" + OUT]


def main():
    ns = load_null_sink(NS)
    leg_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs", "header", "H1_r0")
    res = run_bounded(leg_dir, ARGV, wall=4.6, byte_cap_path=OUT,
                      unload_at=1.2,
                      unload_fn=lambda: unload_verified(ns["idx"], NS))
    with open(OUT, "rb") as f:
        head = f.read(64)
    size = os.path.getsize(OUT)
    riff = int.from_bytes(head[4:8], "little")
    data = int.from_bytes(head[40:44], "little")
    rec = {"file_bytes": size, "riff_size_le": hex(riff), "data_size_le": hex(data),
           "head_hex": head.hex(), "unload": res["unload_result"], "rc": res["rc"],
           "killed": res["killed"],
           "sizes": [s.get("file_bytes") for s in res["timeline"]]}
    with open(os.path.join(leg_dir, "receipt.json"), "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    print(json.dumps(rec, indent=1))
    unload_verified(ns["idx"], NS)
    os.unlink(OUT)


if __name__ == "__main__":
    main()
