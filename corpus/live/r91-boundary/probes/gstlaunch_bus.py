#!/usr/bin/env python3
"""r91b: does gst-launch-1.0 itself stop the pipeline after CLOCK_LOST?

gst-launch-1.0's binary carries the string "Clock lost, selecting a new one",
so it has an explicit CLOCK_LOST branch.  This probe runs the canonical freeze
leg under `gst-launch-1.0 -m` (print bus messages) and captures the exact bus
sequence plus the element's own GST_DEBUG state lines, so we can attribute the
freeze: app pause vs element stall.

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
from r91b_probe import TMP, RUNS, load_null_sink, unload_verified, sha

SCRATCH = "/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r91-boundary"
RAW = os.path.join(SCRATCH, "tmp", "gstlaunch_m.log")

BUS_RE = re.compile(r"^(Got message|.*Clock lost|.*clock|ERROR|WARNING|EOS)",
                    re.I)
ELEM_RE = re.compile(r"pipewiresrc gstpipewiresrc\.c:\d+:")


def one(name, ns, extra_props, use_m, wall=4.6):
    leg_dir = os.path.join(RUNS, name)
    os.makedirs(leg_dir, exist_ok=True)
    out = os.path.join(TMP, name + ".wav")
    n = load_null_sink(ns)
    argv = ["gst-launch-1.0"]
    if use_m:
        argv.append("-m")
    argv += ["-q", "pipewiresrc", "client-name=gst_r91b_gl",
             "target-object=" + ns,
             "stream-properties=props,stream.capture.sink=true"]
    argv += extra_props
    argv += ["num-buffers=1000000", "!",
             "audio/x-raw,format=S16LE,rate=48000,channels=2", "!",
             "wavenc", "!", "filesink", "location=" + out]
    env = dict(os.environ)
    env["GST_DEBUG"] = "*:5"
    env["GST_DEBUG_NO_COLOR"] = "1"
    raw = open(RAW, "wb")
    t0 = time.monotonic()
    p = subprocess.Popen(argv, stdout=raw, stderr=subprocess.STDOUT,
                         start_new_session=True, env=env)
    unload = None
    timeline = []
    try:
        while True:
            t = time.monotonic() - t0
            if t >= 1.2 and unload is None:
                unload = unload_verified(n["idx"], ns)
            if t >= wall:
                break
            if os.path.exists(out) and os.path.getsize(out) > 4 * 1024 * 1024:
                break
            timeline.append({"t": round(t, 2),
                             "bytes": os.path.getsize(out) if os.path.exists(out) else None})
            time.sleep(0.1)
    finally:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            rc = p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            rc = None
        raw.close()
    blob = open(RAW, "rb").read()
    lines = blob.decode("utf-8", "replace").splitlines()
    bus_lines = [l for l in lines if BUS_RE.search(l) and "GST_" not in l]
    elem_lines = [l for l in lines if ELEM_RE.search(l)]
    state_lines = [l for l in elem_lines if "stream state" in l]
    keepalive_lines = [l for l in elem_lines if "keepalive" in l]
    popped = [l for l in elem_lines if "popped buffer" in l]
    filtered = elem_lines + bus_lines
    idx = next((i for i, l in enumerate(filtered) if "set format" in l), 0)
    with open(os.path.join(leg_dir, "filtered.log"), "w") as f:
        f.write("\n".join(filtered[idx:]) + "\n")
    sizes = [x["bytes"] for x in timeline if x["bytes"] is not None]
    rec = {
        "leg": name, "argv": argv, "use_m": use_m, "gst_debug": env["GST_DEBUG"],
        "raw_log_bytes": len(blob), "raw_log_sha256": sha(blob),
        "elem_lines": len(elem_lines), "state_lines": [l.strip() for l in state_lines],
        "keepalive_lines": [l.strip() for l in keepalive_lines][:5],
        "popped_buffer_lines": len(popped),
        "bus_lines": [l.strip() for l in bus_lines][:25],
        "timeline": timeline,
        "first_bytes": sizes[0] if sizes else None,
        "last_bytes": sizes[-1] if sizes else None,
        "file_bytes": os.path.getsize(out) if os.path.exists(out) else None,
        "unload": unload, "rc": rc,
    }
    with open(os.path.join(leg_dir, "receipt.json"), "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    print(json.dumps({k: rec[k] for k in
                      ("leg", "use_m", "raw_log_bytes", "elem_lines",
                       "popped_buffer_lines", "state_lines", "keepalive_lines",
                       "bus_lines", "first_bytes", "last_bytes", "unload")},
                     indent=1))
    unload_verified(n["idx"], ns)
    os.unlink(RAW)
    if os.path.exists(out):
        os.unlink(out)


if __name__ == "__main__":
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    one("GL_m_keepalive0", "r91b_ns_gl0", [], use_m=True)
    one("GL_m_keepalive20", "r91b_ns_gl20", ["keepalive-time=20"], use_m=True)
