#!/usr/bin/env python3
"""Interleaved onset/transport-delay probe: control vs -d 1.0 on the loopback.

Loopback is up and linked before the recorder starts; the tone starts a fixed
~150 ms after the recorder, with both spawn times timestamped, so the measured
transport delay = first-tone-sample offset - (t_tone - t_mon).
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r83b_probe as P  # noqa: E402

LB = P.LB_BASE
TONE = P.SCRATCH + "/tone48.wav"


def one_rep(leg, extra, delay=0.15):
    name = f"r83b_s5_{leg}"
    out = os.path.join(P.RAW, f"onset_{leg}.wav")
    d = P.leg_dir("s5_latency", f"onset_{leg}")
    rec = {"leg": f"onset_{leg}", "extra": extra, "load_before": os.getloadavg()}
    lb = P.spawn(["timeout", "-s", "KILL", "8", "pw-loopback", "-n", name]
                 + LB + list(extra))
    try:
        time.sleep(1.5)  # links up
        mon = P.spawn(["timeout", "-s", "INT", "10", "pw-record",
                       "-P", "stream.capture.sink=true",
                       "-P", f"node.name={name}_rec", "--target", P.NS_B,
                       "-n", "96000", "--rate", "48000", "--channels", "2",
                       "--format", "s16", out])
        t_mon = time.monotonic()
        time.sleep(delay)
        tone = P.spawn(["timeout", "-s", "KILL", "6", "pw-cat", "-p",
                        "-P", f"node.name={name}_tone", "--target", P.NS_A,
                        TONE])
        t_tone = time.monotonic()
        P.reap(tone, 4)
        rr = P.reap(mon, 8)
        rec["rec_rc"], rec["rec_err"] = rr["rc"], rr["err"][:200]
        o = P.onset(out, thresh=500)
        rec["onset"] = o
        if o:
            rec["transport_s"] = round(o["first_s"] - (t_tone - t_mon), 4)
        rec["load_after"] = os.getloadavg()
    finally:
        rr = P.reap(lb, 10)
        rec["lb_rc"], rec["lb_err"] = rr["rc"], rr["err"][:200]
    P.save_leg("s5_latency", f"onset_{leg}", rec)
    return rec


def main():
    res = {"legs": []}
    for i in range(3):
        res["legs"].append(one_rep(f"O_ctrl_r{i}", []))
        res["legs"].append(one_rep(f"O_d1_r{i}", ["-d", "1.0"]))
    P.save_receipt("s5-onsets.json", res)
    for l in res["legs"]:
        print(f"{l['leg']:14s} onset={l.get('onset')} transport={l.get('transport_s')} load={l.get('load_before')}")
    # under load
    n = P.hogs_start(16)
    res2 = {"legs": [], "hogs": n}
    for i in range(2):
        res2["legs"].append(one_rep(f"O_ctrl_ld_r{i}", []))
        res2["legs"].append(one_rep(f"O_d1_ld_r{i}", ["-d", "1.0"]))
    P.hogs_stop()
    res2["load_after_hogs"] = os.getloadavg()
    P.save_receipt("s5-onsets-load.json", res2)
    for l in res2["legs"]:
        print(f"{l['leg']:16s} onset={l.get('onset')} transport={l.get('transport_s')} load={l.get('load_before')}")


if __name__ == "__main__":
    main()
