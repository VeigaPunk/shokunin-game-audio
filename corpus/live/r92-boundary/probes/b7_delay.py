#!/usr/bin/env python3
"""B7 — the `delay` node's delay-vs-request map and its clamp point.

The scout never armed this control (its `Delay` typo); B3 showed 0.01 s -> exactly
480 samples and 0.1 s (with max-delay=0.05) -> 2431 samples, not 2400. Map the
law: shift in samples vs requested seconds, with max-delay=0.05.

argv[1] = reps (default 2).
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig as R

S = R.SCRATCH
DELTA = "r92b_delta.wav"
REQS = [0.0, 0.001, 0.01, 0.02, 0.049, 0.05, 0.051, 0.06, 0.1]


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    t0 = time.time()
    if not os.path.exists(os.path.join(S, DELTA)):
        R.wav_write(os.path.join(S, DELTA),
                    np.concatenate([np.zeros(100), [1.0], np.zeros(4095)]), fmt="s16")
    pf = R.preflight()
    out = {"stage": "b7_delay", "reps": reps, "preflight": pf, "max_delay": 0.05,
           "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "legs": {}}

    for req in REQS:
        name = "d-%s" % ("%g" % req).replace(".", "p")
        args = R.fc_args(['{type=builtin,name=d,label=delay,config={max-delay=0.05},'
                          'control={"Delay (s)"=%g}}' % req])
        rows = []
        for rep in range(reps):
            row = R.run_leg(name, args, "ir", rep, DELTA)
            rp = os.path.join(S, "%s_ref_%s_%d_%d.wav" % (name, name, rep, row["attempt"]))
            op = os.path.join(S, "%s_out_%s_%d_%d.wav" % (name, name, rep, row["attempt"]))
            shift = None
            if os.path.exists(rp) and os.path.exists(op):
                xr = R.wav_read(rp)["x"]
                xo = R.wav_read(op)["x"]
                rf = np.nonzero(np.abs(xr) > 1e-4)[0]
                of = np.nonzero(np.abs(xo) > 1e-4)[0]
                if len(rf) and len(of):
                    shift = int(of[0]) - int(rf[0])
            rows.append({"rep": rep, "shift": shift, "valid": row["valid"],
                         "out_bytes": row["analysis"].get("out_bytes")})
            print("b7 req=%-6g r%d shift=%-6s valid=%s" % (req, rep, shift, row["valid"]))
        out["legs"][name] = {"req_s": req, "req_samples": req * R.RATE, "args": args, "rows": rows}

    out["elapsed_s"] = round(time.time() - t0, 1)
    out["sweep"] = R.sweep()
    out["final"] = R.live_r92b()
    R.jdump(os.path.join(R.REC, "b7_delay.json"), out)
    print("WROTE b7_delay.json (%.1fs)" % (time.time() - t0))
    print("SWEEP clean:", out["sweep"]["clean"], "final:", out["final"])


if __name__ == "__main__":
    main()
