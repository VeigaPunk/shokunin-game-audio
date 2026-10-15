#!/usr/bin/env python3
"""r91b: what sets the pipeline back to PAUSED right after CLOCK_LOST?

The element log at target loss shows, in order:
    :900  got stream state paused            (element's own on_state_changed)
    :1788 in-activating stream               (GstBaseSrc state change)
    :1449 setting flushing
    :1774 activating stream
    :1074 waiting for NEGOTIATED, now paused
    :1094 error during negotiation
    -> gst_base_src_get_range returns FLUSHING  => pipeline stalls forever

Something drives a PAUSED transition.  Candidate: gst-launch-1.0's own
CLOCK_LOST branch (the binary carries "Clock lost, selecting a new one").
This probe prints the full log window around the loss, unfiltered by category
but bounded to a 0.25 s span, and checks the gst-launch bus handler by running
`-m` (which prints bus messages to stdout).

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
RAW = os.path.join(SCRATCH, "tmp", "window_raw.log")
TS = re.compile(r"^0:00:0(\d)\.(\d+)")


def secs(line):
    m = TS.match(line)
    if not m:
        return None
    return int(m.group(1)) + float("0." + m.group(2))


def one(name, ns, extra, wall=4.6, use_m=True):
    leg_dir = os.path.join(RUNS, name)
    os.makedirs(leg_dir, exist_ok=True)
    out = os.path.join(TMP, name + ".wav")
    n = load_null_sink(ns)
    argv = ["gst-launch-1.0"]
    if use_m:
        argv.append("-m")
    argv += ["-q", "pipewiresrc", "client-name=gst_r91b_win",
             "target-object=" + ns,
             "stream-properties=props,stream.capture.sink=true"] + extra
    argv += ["num-buffers=1000000", "!",
             "audio/x-raw,format=S16LE,rate=48000,channels=2", "!",
             "wavenc", "!", "filesink", "location=" + out]
    env = dict(os.environ)
    env["GST_DEBUG"] = "*:4"
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
    # window 1.15 -> 1.60 s
    win = [l for l in lines if (s := secs(l)) is not None and 1.15 <= s <= 1.60]
    with open(os.path.join(leg_dir, "window_1.15-1.60.log"), "w") as f:
        f.write("\n".join(win) + "\n")
    # lines mentioning clock/lost/pause anywhere
    key = [l for l in lines if re.search(r"got lost|clock-lost|Lost clock|"
                                        r"Clock lost|set_state|"
                                        r"change_state.*pipeline0|"
                                        r"in-activating|activating stream|"
                                        r"error during negotiation", l)]
    with open(os.path.join(leg_dir, "key_lines.log"), "w") as f:
        f.write("\n".join(key) + "\n")
    # gst-launch's own messages (it prints them on stdout when -m)
    launcher = [l for l in lines if re.search(r"^(Got message|Setting state|"
                                              r"Clock lost|ERROR|WARNING)", l)]
    sizes = [x["bytes"] for x in timeline if x["bytes"] is not None]
    rec = {"leg": name, "argv": argv, "use_m": use_m, "gst_debug": env["GST_DEBUG"],
           "raw_log_bytes": len(blob), "raw_log_sha256": sha(blob),
           "window_lines": len(win), "key_lines": len(key),
           "launcher_lines": launcher[:20],
           "first_bytes": sizes[0] if sizes else None,
           "last_bytes": sizes[-1] if sizes else None,
           "timeline": timeline, "unload": unload, "rc": rc}
    with open(os.path.join(leg_dir, "receipt.json"), "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    print(json.dumps({k: rec[k] for k in ("leg", "use_m", "raw_log_bytes",
                                          "window_lines", "key_lines",
                                          "launcher_lines", "first_bytes",
                                          "last_bytes", "unload")}, indent=1))
    unload_verified(n["idx"], ns)
    os.unlink(RAW)
    if os.path.exists(out):
        os.unlink(out)


if __name__ == "__main__":
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    one("WIN_m", "r91b_ns_win", [], use_m=True)
    one("WIN_nom", "r91b_ns_win2", [], use_m=False)
