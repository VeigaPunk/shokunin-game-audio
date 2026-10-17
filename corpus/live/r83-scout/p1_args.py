#!/usr/bin/env python3
"""P1 — pw-loopback -i/-o prop lattice: syntax forms, channel map via props,
resample.* / latency / passive / remix props — landing vs silent drop, plus
content legs proving which props actually steer the DSP copy.

Fixed route: -C <nsa> (sink prop) -> loopback -> -P <nsb>; all probe-owned.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r83_probe as P

NSA, NSB = "r83dsp_p1_nsa", "r83dsp_p1_nsb"
BASE = ["-C", NSA, "-i", "stream.capture.sink=true", "-P", NSB]

# props picked for landing checks (beyond the full baseline dump)
PICK = ["media.name", "bogus.prop", "audio.channels", "audio.position",
        "channelmap.map", "resample.quality", "resample.disable",
        "resample.peaks", "resample.prefill", "node.latency",
        "node.force-latency", "node.passive", "node.dont-move",
        "node.dont-remix", "stream.dont-remix", "channelmix.disabled",
        "channelmix.stereo-widen", "channelmix.upmix", "node.name",
        "node.group", "target.object", "stream.is-live",
        "node.autoconnect", "media.class"]


def leg(leg_id, extra, **kw):
    name = f"r83dsp_p1_{leg_id}"
    return P.lb_leg(leg_id, name, BASE + list(extra), sample_props=PICK, **kw)


def content_leg(leg_id, extra, secs=9):
    """Loopback + tone into NSA + record NSB monitor -> per-channel content."""
    name = f"r83dsp_p1_{leg_id}"
    rec = {"leg": leg_id, "args": BASE + list(extra)}
    lb = P.lb_start(name, BASE + list(extra), secs)
    try:
        g, got, ws = P.wait_nodes(name, 2)
        rec["nodes"] = got
        rec["wait_s"] = ws
        tone = P.play(P.TONE48, NSA, f"{name}_tone",
                      props=["stream.capture.sink=false"])
        try:
            time.sleep(1.2)
            g = P.Graph(P.pw_dump())
            for n in got:
                node = g.node(n)
                if node:
                    rec.setdefault("props", {})[n] = {
                        k: node["props"].get(k) for k in PICK}
            rec["edges"] = g.edges(name)
            out = os.path.join(P.RAW, f"{leg_id}_mon.wav")
            rr = P.rec_monitor(NSB, out, 24000, f"{name}_rec")
            rec["record"] = {k: rr[k] for k in ("rc", "err", "bytes")}
            rec["content"] = P.analyze(out)
        finally:
            P.kill(tone)
    finally:
        rr = P.reap(lb, wait=secs + 1)
        rec["rc"], rec["stderr"] = rr["rc"], rr["stderr"].strip()
    return rec


def flag_leg(leg_id, argv_tail, secs=6):
    """Raw argv tail (for -l/-d/-g parse legs that may fail at spawn)."""
    name = f"r83dsp_p1_{leg_id}"
    return P.lb_leg(leg_id, name, argv_tail, sample_props=PICK, secs=secs)


def main():
    P.ensure_tones()
    sinks = [P.ns_load(NSA), P.ns_load(NSB)]
    res = {"sinks": sinks, "legs": [], "content_legs": []}
    if not all(s["verified"] for s in sinks):
        res["fatal"] = "null sinks failed"
        return P.save_receipt("p1-args.json", res)

    # -- syntax forms -------------------------------------------------------
    res["legs"].append(leg("S0_base", []))
    res["legs"].append(leg("S1_space", ["-i", "media.name=SPACEV bogus.prop=42"]))
    res["legs"].append(leg("S2_brace", ["-i", "{ media.name = BRACEV bogus.prop = 42 }"]))
    res["legs"].append(leg("S3_braceq", ["-i", '{ "media.name" = "BRACEQ" "bogus.prop" = "42" }']))
    res["legs"].append(leg("S4_colon", ["-i", '{ "media.name": "COLONV" }']))
    res["legs"].append(leg("S5_comma", ["-i", "media.name=COMMAV,bogus.prop=42"]))
    res["legs"].append(leg("S6_malformed", ["-i", "}{ garbage"], wait=1.5))
    res["legs"].append(leg("S7_empty", ["-i", ""]))

    # -- channel map via -i/-o props ---------------------------------------
    res["legs"].append(leg("C1_pos_mono_i", ["-i", "audio.position=[ MONO ]"]))
    res["legs"].append(leg("C2_pos_mono_brace", ["-i", "{ audio.position = [ MONO ] }"]))
    res["legs"].append(leg("C3_ch1_pos", ["-i", "audio.channels=1 audio.position=[ MONO ]"]))
    res["legs"].append(leg("C4_channelmap", ["-i", "channelmap.map=[ MONO ]"]))
    res["legs"].append(leg("C5_pos_mono_o", ["-o", "audio.position=[ MONO ]"]))
    res["legs"].append(leg("C6_flag_m", ["-c", "6", "-m", "[ FL, FR, RL, RR, FC, LFE ]"]))

    # -- resample.* props ----------------------------------------------------
    res["legs"].append(leg("R1_q0", ["-i", "resample.quality=0"]))
    res["legs"].append(leg("R2_q999", ["-i", "resample.quality=999"]))
    res["legs"].append(leg("R3_resample_on", ["-o", "resample.disable=false",
                                              "-o", "resample.quality=14"]))
    res["legs"].append(leg("R4_peaks", ["-i", "resample.peaks=true"]))
    res["legs"].append(leg("R5_prefill", ["-i", "resample.prefill=false"]))

    # -- latency / delay -----------------------------------------------------
    res["legs"].append(flag_leg("L1_lat5", BASE + ["-l", "5"]))
    res["legs"].append(flag_leg("L2_delay", BASE + ["-d", "0.25"]))
    res["legs"].append(flag_leg("L3_lat0", BASE + ["-l", "0"]))
    res["legs"].append(flag_leg("L4_latabc", BASE + ["-l", "abc"]))
    res["legs"].append(flag_leg("L5_delayneg", BASE + ["-d", "-1"]))
    res["legs"].append(flag_leg("L6_lat10k", BASE + ["-l", "10000"]))
    res["legs"].append(flag_leg("L7_group", BASE + ["-g", "r83dsp_grp"]))
    res["legs"].append(flag_leg("L8_lat256", BASE + ["-l", "256"]))

    # -- routing-ish props ---------------------------------------------------
    res["legs"].append(leg("P1_passive_i", ["-i", "node.passive=true"]))
    res["legs"].append(leg("P2_passive_o", ["-o", "node.passive=true"]))
    res["legs"].append(leg("P3_dontmove", ["-o", "node.dont-move=true"]))
    res["legs"].append(leg("P4_dontremix_node", ["-o", "node.dont-remix=true"]))
    res["legs"].append(leg("P5_dontremix_stream", ["-o", "stream.dont-remix=true"]))
    res["legs"].append(leg("P6_chanmix", ["-o", "channelmix.disabled=true",
                                          "-o", "channelmix.stereo-widen=0.8",
                                          "-o", "channelmix.upmix=false"]))
    res["legs"].append(leg("P7_nodename_i", ["-i", "node.name=r83dsp_capX"]))
    res["legs"].append(leg("P8_nodename_o", ["-o", "node.name=r83dsp_pbX"]))
    res["legs"].append(leg("P9_mediaclass", ["-i", "media.class=Audio/Source"]))

    # -- content legs (does a prop-set position actually mix?) ---------------
    res["content_legs"].append(content_leg("CC0_ctrl", []))
    res["content_legs"].append(content_leg("CC1_i_mono", ["-i", "audio.position=[ MONO ]"]))
    res["content_legs"].append(content_leg("CC2_o_mono", ["-o", "audio.position=[ MONO ]"]))
    res["content_legs"].append(content_leg("CC3_both_mono", ["-i", "audio.position=[ MONO ]",
                                                           "-o", "audio.position=[ MONO ]"]))
    res["content_legs"].append(content_leg("CC4_chmap_key", ["-i", "channelmap.map=[ MONO ]"]))

    for s in (NSA, NSB):
        res.setdefault("unloads", []).append(P.ns_unload(s))
    return P.save_receipt("p1-args.json", res)


if __name__ == "__main__":
    print(main())
