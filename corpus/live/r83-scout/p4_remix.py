#!/usr/bin/env python3
"""P4 — node.passive / node.dont-remix / channelmix.* on playback streams
(pw-cat -p into a probe-owned null sink; the sink monitor is the content
witness, pw-dump props/links the topology witness).

Audio: MONO48 (1 kHz mono) and TONE48 (L 1 kHz / R 1.5 kHz).
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r83_probe as P

NS = "r83dsp_p4_ns"
NSM = "r83dsp_p4_nsm"   # mono sink (channel_map=mono)

PICK = ["node.name", "media.class", "audio.channels", "audio.position",
        "node.passive", "node.dont-remix", "stream.dont-remix",
        "node.dont-move", "channelmix.disabled", "channelmix.upmix",
        "channelmix.downmix", "channelmix.stereo-widen", "channelmix.mix-lfe",
        "channelmix.upmix-method", "stream.is-live", "target.object",
        "resample.disable", "channelmix.normalize"]


def play_leg(leg_id, path, props, sink=NS, mono_rec_frames=24000,
             settle=1.0, move_to=None, extra_props=None):
    """Play `path` into `sink` with -P props; snapshot stream node; record
    sink monitor; return prop+link+content witnesses."""
    tag = f"r83dsp_p4_{leg_id}"
    rec = {"leg": leg_id, "file": os.path.basename(path), "props": props,
           "sink": sink}
    p = P.play(path, sink, tag, props=props)
    try:
        time.sleep(settle)
        g = P.Graph(P.pw_dump())
        node = g.node(tag)
        rec["node"] = ({"id": node["id"], "class": node["class"],
                        "picked": {k: node["props"].get(k) for k in PICK},
                        "in_ports": node["in"], "out_ports": node["out"]}
                       if node else None)
        rec["edges"] = g.edges(tag)
        if move_to:  # pactl move-sink-input while live
            idx = None
            si = P.sh(["pactl", "-f", "json", "list", "sink-inputs"],
                      timeout=8)
            try:
                arr = json.loads(si["out"])
                for it in arr:
                    if it.get("properties", {}).get("node.name") == tag:
                        idx = it.get("index")
            except Exception as exc:
                rec["move_err"] = f"json: {exc}"
            rec["sink_input_idx"] = idx
            if idx is not None:
                mv = P.sh(["pactl", "move-sink-input", str(idx), move_to],
                          timeout=8)
                rec["move"] = {"rc": mv["rc"], "err": mv["err"].strip(),
                               "to": move_to}
                time.sleep(0.7)
                g = P.Graph(P.pw_dump())
                rec["edges_after_move"] = g.edges(tag)
        out = os.path.join(P.RAW, f"{leg_id}_mon.wav")
        rr = P.rec_monitor(sink, out, mono_rec_frames, f"{tag}_rec")
        rec["record"] = {k: rr[k] for k in ("rc", "err", "bytes")}
        rec["content"] = P.analyze(out)
    finally:
        rr = P.reap(p, wait=8)
        rec["rc"], rec["stderr"] = rr["rc"], rr["stderr"].strip()
    return rec


def main():
    P.ensure_tones()
    sinks = [P.ns_load(NS), P.ns_load(NSM, ["channel_map=mono"])]
    res = {"sinks": sinks, "legs": []}
    if not all(s["verified"] for s in sinks):
        res["fatal"] = "null sinks failed"
        return P.save_receipt("p4-remix.json", res)

    L = res["legs"].append
    # -- mono file into stereo sink: remix surface ---------------------------
    L(play_leg("M0_mono_base", P.MONO48, []))
    L(play_leg("M1_mono_noderemix", P.MONO48, ["node.dont-remix=true"]))
    L(play_leg("M2_mono_streamremix", P.MONO48, ["stream.dont-remix=true"]))
    L(play_leg("M3_mono_upmixfalse", P.MONO48, ["channelmix.upmix=false"]))
    L(play_leg("M4_mono_chmixoff", P.MONO48, ["channelmix.disabled=true"]))
    L(play_leg("M5_mono_normvol", P.MONO48, ["channelmix.normalize=true"]))

    # -- stereo file + widen --------------------------------------------------
    L(play_leg("W0_stereo_base", P.TONE48, []))
    L(play_leg("W1_widen1", P.TONE48, ["channelmix.stereo-widen=1.0"]))
    L(play_leg("W2_widen05", P.TONE48, ["channelmix.stereo-widen=0.5"]))
    L(play_leg("W3_stereo_node_remix", P.TONE48, ["node.dont-remix=true"]))
    L(play_leg("W4_upmix_method", P.TONE48, ["channelmix.upmix-method=simple"]))

    # -- passive / dont-move --------------------------------------------------
    L(play_leg("P0_passive", P.TONE48, ["node.passive=true"], settle=1.5))
    L(play_leg("P1_passive_false", P.TONE48, ["node.passive=false"]))
    L(play_leg("P2_dontmove", P.TONE48, ["node.dont-move=true"],
               move_to=P.DEFAULT_SINK))     # move is refused -> stays on NS
    L(play_leg("P3_move_ctrl", P.TONE48, [], move_to=NSM))

    # -- stereo into MONO sink ------------------------------------------------
    L(play_leg("D0_stereo_to_mono", P.TONE48, [], sink=NSM))
    L(play_leg("D1_mono_downmixoff", P.TONE48, ["channelmix.downmix=false"],
               sink=NSM))
    L(play_leg("D2_mono_dontremix", P.TONE48, ["node.dont-remix=true"],
               sink=NSM))
    L(play_leg("D3_mono_streamremix", P.TONE48, ["stream.dont-remix=true"],
               sink=NSM))

    for s in (NS, NSM):
        res.setdefault("unloads", []).append(P.ns_unload(s))
    return P.save_receipt("p4-remix.json", res)


if __name__ == "__main__":
    print(main())
