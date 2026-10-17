#!/usr/bin/env python3
"""P5 — adaptive resampler + rate-mismatch content witness.

TONE44 = 44.1 kHz stereo dual-tone (L 1 kHz / R 1.5 kHz, amp 8192). The
question the brief asks: played into a 48 kHz sink, does the tag tone's
frequency still verify? And on the pw-loopback copy path (whose default is
resample.disable=true), does a 44.1k sink -> 48k sink copy keep the pitch?
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r83_probe as P

NS48 = "r83dsp_p5_ns48"
NS44 = "r83dsp_p5_ns44"

PICK = ["node.name", "media.class", "audio.channels", "audio.position",
        "resample.disable", "resample.quality", "resample.peaks",
        "resample.prefill", "node.rate", "stream.is-live", "target.object",
        "node.latency"]


def play_leg(leg_id, path, props, sink, extra_args=None, rec_frames=24000,
             settle=1.1):
    tag = f"r83dsp_p5_{leg_id}"
    rec = {"leg": leg_id, "file": os.path.basename(path), "props": props,
           "extra": extra_args, "sink": sink}
    p = P.play(path, sink, tag, props=props, extra_args=extra_args)
    try:
        time.sleep(settle)
        g = P.Graph(P.pw_dump())
        node = g.node(tag)
        rec["node"] = ({"id": node["id"], "class": node["class"],
                        "picked": {k: node["props"].get(k) for k in PICK}}
                       if node else None)
        rec["edges"] = g.edges(tag)
        out = os.path.join(P.RAW, f"{leg_id}_mon.wav")
        rr = P.rec_monitor(sink, out, rec_frames, f"{tag}_rec")
        rec["record"] = {k: rr[k] for k in ("rc", "err", "bytes")}
        rec["content"] = P.analyze(out)
        if rec["content"].get("exists"):
            # spectral detail: amp at tag freqs + top-5 bins to expose images
            rec["amp_detail"] = {"ch0": P.fft_at(out, 1000.0, ch=0),
                                 "ch1": P.fft_at(out, 1500.0, ch=1)}
    finally:
        rr = P.reap(p, wait=8)
        rec["rc"], rec["stderr"] = rr["rc"], rr["stderr"].strip()
    return rec


def lb_rate_leg(leg_id, lb_extra, secs=10):
    """TONE44 -> NS44 (sink rate 44100) ; pw-loopback NS44 -> NS48 ; record
    NS48 monitor. Witness = freq of the tone that survives the loopback."""
    name = f"r83dsp_p5_{leg_id}"
    rec = {"leg": leg_id, "lb_extra": lb_extra}
    lb = P.lb_start(name, ["-C", NS44, "-i", "stream.capture.sink=true",
                           "-P", NS48] + list(lb_extra), secs)
    try:
        g, got, ws = P.wait_nodes(name, 2)
        rec["nodes"] = got
        tone = P.play(P.TONE44, NS44, f"{name}_tone")
        try:
            time.sleep(1.4)
            g = P.Graph(P.pw_dump())
            for n in got:
                node = g.node(n)
                if node:
                    rec.setdefault("props", {})[n] = {
                        k: node["props"].get(k) for k in PICK}
            rec["edges"] = g.edges(name)
            rec["lb_peers"] = {n: g.peers(n) for n in got}
            out = os.path.join(P.RAW, f"{leg_id}_mon.wav")
            rr = P.rec_monitor(NS48, out, 24000, f"{name}_rec")
            rec["record"] = {k: rr[k] for k in ("rc", "err", "bytes")}
            rec["content"] = P.analyze(out)
            if rec["content"].get("exists"):
                rec["amp_detail"] = {"ch0": P.fft_at(out, 1000.0, ch=0),
                                     "ch1": P.fft_at(out, 1500.0, ch=1)}
        finally:
            P.kill(tone)
    finally:
        rr = P.reap(lb, wait=secs + 1)
        rec["rc"], rec["stderr"] = rr["rc"], rr["stderr"].strip()
    return rec


def main():
    P.ensure_tones()
    sinks = [P.ns_load(NS48), P.ns_load(NS44, ["rate=44100"])]
    res = {"sinks": sinks, "legs": [], "lb_legs": []}
    if not all(s["verified"] for s in sinks):
        res["fatal"] = "null sinks failed"
        return P.save_receipt("p5-resample.json", res)

    L = res["legs"].append
    # -- 44.1k file -> 48k sink, resample knobs -------------------------------
    L(play_leg("S0_44_into_48", P.TONE44, [], NS48))
    L(play_leg("S1_resample_off", P.TONE44, ["resample.disable=true"], NS48))
    L(play_leg("S2_q0", P.TONE44, ["resample.quality=0"], NS48))
    L(play_leg("S3_q14", P.TONE44, ["resample.quality=14"], NS48))
    L(play_leg("S4_peaks", P.TONE44, ["resample.peaks=true"], NS48))
    L(play_leg("S5_rate_flag", P.TONE44, [], NS48,
               extra_args=["--rate", "48000"]))
    # -- 48k file -> 44.1k sink (the reverse direction) -----------------------
    L(play_leg("S6_48_into_44", P.TONE48, [], NS44))
    # -- loopback across the rate boundary ------------------------------------
    res["lb_legs"].append(lb_rate_leg("LB0_def", []))
    res["lb_legs"].append(lb_rate_leg(
        "LB1_resample_on", ["-i", "resample.disable=false",
                            "-o", "resample.disable=false"]))
    res["lb_legs"].append(lb_rate_leg(
        "LB2_q14", ["-i", "resample.disable=false resample.quality=14",
                    "-o", "resample.disable=false resample.quality=14"]))

    for s in (NS48, NS44):
        res.setdefault("unloads", []).append(P.ns_unload(s))
    return P.save_receipt("p5-resample.json", res)


if __name__ == "__main__":
    print(main())
