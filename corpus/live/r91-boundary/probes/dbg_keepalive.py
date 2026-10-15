#!/usr/bin/env python3
"""r91b: why does keepalive-time=20 NOT resend after target loss?

The scout's source read (§1.1 last row) says keepalive 0 -> bare
`pw_thread_loop_wait` ("no timeout, no error path").  The same source has an
explicit opt-in timeout branch (:1631-1643 -> :1601-1605 resend of
`last_buffer`) and an explicit `on-disconnect` = eos|error branch
(:613-689).  Prediction from that read: keepalive-time>0 resends after loss.
Measured in B1: the file still freezes.  This probe captures the element's own
GST_DEBUG lines (category is NOT "pipewire" -- see --cat) to see whether the
create loop is re-entered at all after the target dies.

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
RAW = os.path.join(SCRATCH, "tmp", "gstdebug_raw.log")

LEGS = {
    # keepalive-time=20, target dies at 1.2 s
    "DBG_keepalive20": {"ns": "r91b_ns_dbg1",
                        "props": ["keepalive-time=20"], "wall": 3.2},
    # default keepalive 0, target dies at 1.2 s (baseline for comparison)
    "DBG_keepalive0": {"ns": "r91b_ns_dbg0",
                       "props": [], "wall": 3.2},
}

KEEP = re.compile(r"pipewiresrc|pipewire_src|keepalive|popped|timeout|removed all|"
                  r"flush|EOS|eos|negotiat|set format|stream state|"
                  r"queue|dequeue|pool")


def one(name, spec):
    ns = load_null_sink(spec["ns"])
    leg_dir = os.path.join(RUNS, name)
    os.makedirs(leg_dir, exist_ok=True)
    out = os.path.join(TMP, name + ".wav")
    argv = ["gst-launch-1.0", "-q", "pipewiresrc",
            "client-name=gst_r91b_dbg", "target-object=" + spec["ns"],
            "stream-properties=props,stream.capture.sink=true"]
    argv += spec["props"]
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
                unload = unload_verified(ns["idx"], spec["ns"])
            if t >= spec["wall"]:
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
    with open(RAW, "rb") as f:
        blob = f.read()
    lines = blob.decode("utf-8", "replace").splitlines()
    keep = [l for l in lines if KEEP.search(l)]
    idx = next((i for i, l in enumerate(keep) if "set format" in l), 0)
    keep = keep[idx:]
    with open(os.path.join(leg_dir, "gstdebug_filtered.log"), "w") as f:
        f.write("\n".join(keep) + "\n")
    rec = {
        "leg": name, "argv": argv, "gst_debug": env["GST_DEBUG"],
        "raw_log_bytes": len(blob), "raw_log_sha256": sha(blob),
        "raw_lines": len(lines), "filtered_lines": len(keep),
        "keepalive_resend_lines": sum(1 for l in keep if "keepalive buffer" in l),
        "popped_buffer_lines": sum(1 for l in keep if "popped buffer" in l),
        "state_lines": [l.strip() for l in keep if "stream state" in l][:12],
        "tail_after_loss": [l.strip() for l in keep
                            if "removed all buffers" in l or "EOS" in l][:12],
        "timeline": timeline,
        "file_bytes": os.path.getsize(out) if os.path.exists(out) else None,
        "unload": unload, "rc": rc,
    }
    with open(os.path.join(leg_dir, "receipt.json"), "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    print(json.dumps({k: rec[k] for k in
                      ("leg", "raw_log_bytes", "raw_lines", "filtered_lines",
                       "keepalive_resend_lines", "popped_buffer_lines",
                       "file_bytes", "state_lines", "tail_after_loss")}, indent=1))
    unload_verified(ns["idx"], spec["ns"])
    os.unlink(RAW)
    if os.path.exists(out):
        os.unlink(out)
    return rec


if __name__ == "__main__":
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    which = sys.argv[1:] or list(LEGS)
    for k in which:
        one(k, LEGS[k])
