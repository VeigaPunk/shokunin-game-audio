#!/usr/bin/env python3
"""Re-run named legs of a stage (argv taken from the old receipt) with a fresh
tone anchor, then patch the stage receipt. For legs whose content witness
(peak) was lost when the 60 s tone ran out mid-battery."""
import json
import os
import signal
import subprocess
import sys
import time

import r81_probe as P

stage = sys.argv[1]
legs = sys.argv[2].split(",")
receipt = P.REC / ("%s.json" % stage)
doc = json.load(open(receipt))

tone = P.make_tone(seconds=60)
tp = subprocess.Popen(["pw-play", "-P", "node.name=gst_r81_tone", "--target", P.NS,
                       str(tone)], stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL, preexec_fn=os.setsid)
time.sleep(0.5)
try:
    for name in legs:
        old = json.load(open(P.RUNS / stage / ("%s_r0" % name) / "receipt.json"))
        argv = old["argv"]
        out_path = None
        for a in argv:
            if a.startswith("location="):
                out_path = a.split("=", 1)[1]
        if out_path is None and argv[-1].endswith(".wav"):
            out_path = argv[-1]
        reps = []
        for rep in range(3):
            reps.append(P.leg("%s_r%d" % (name, rep), argv, out_path=out_path,
                              env_extra=old.get("env_extra"),
                              samples=(0.4, 0.9), stage=stage, wall_cap=6.0))
        doc["body"]["legs"][name] = reps
        print("  ", name, [(r["rc"], r["out_peak"]) for r in reps])
finally:
    try:
        os.killpg(os.getpgid(tp.pid), signal.SIGKILL)
    except Exception:
        pass
json.dump(doc, open(receipt, "w"), indent=1)
print("patched", receipt)
