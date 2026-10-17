#!/usr/bin/env python3
"""P3 — pw-mididump / pw-midiplay surfaces.

Midi-Bridge (api.alsa.seq.bridge) exposes 'Midi Through: Port-0 (playback)'
(input) and '... (capture)' (output) ports carrying '8 bit raw midi'.
ALSA side witness: aseqdump -p 14:0 / aplaymidi -p 14:0.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r83_probe as P

MID = os.path.join(P.SCRATCH, "r83_note.mid")
BRIDGE = "Midi-Bridge"


def midi_node_info(substr, g=None):
    g = g or P.Graph(P.pw_dump())
    hits = []
    for n in g.find(substr):
        node = g.nodes[n]
        hits.append({"name": n, "id": node["id"], "class": node["class"],
                     "props": {k: v for k, v in node["props"].items()
                               if k.startswith(("media.", "node.", "stream.",
                                                "target", "object.", "port"))},
                     "in": node["in"], "out": node["out"]})
    return hits


def midi_leg(leg_id, argv, secs=5, wait=1.0, find=("r83dsp", "pw-midi"),
             aplay=None, aseq=False, link=None):
    """Bounded midi leg with optional aplaymidi injector + aseqdump witness."""
    rec = {"leg": leg_id, "argv": argv}
    ap = None
    try:
        aq = None
        if aseq:
            aq = P.spawn_out(["aseqdump", "-p", "14:0"])
            time.sleep(0.4)
        p = P.spawn_out(argv)
        try:
            time.sleep(wait)
            g = P.Graph(P.pw_dump())
            rec["nodes"] = [n for s in find for n in midi_node_info(s, g)]
            rec["edges"] = [e for s in find for e in g.edges(s)]
            if link:  # manual pins [(out_name,out_port),(in_name,in_port)]
                rec["pins"] = []
                for o, i in link:
                    r = P.sh(["pw-link", o, i], timeout=5.0)
                    rec["pins"].append({"o": o, "i": i, "rc": r["rc"],
                                        "err": r["err"].strip()})
            if aplay:
                ap = P.sh(aplay, timeout=6.0)
            time.sleep(0.8)
        finally:
            rr = P.reap_io(p, wait=secs)
            rec.update(rc=rr["rc"], stdout=rr["stdout"][:4000],
                       stderr=rr["stderr"][:4000], wall_s=rr["wall_s"])
        if aplay:
            rec["aplaymidi"] = {"rc": ap["rc"] if ap else None,
                                "err": (ap["err"] if ap else "")[:200]}
        if aseq and aq:
            rr2 = P.reap_io(aq, wait=4)
            rec["aseqdump"] = {"rc": rr2["rc"],
                               "stdout": rr2["stdout"][-2000:]}
    finally:
        pass  # ap is a P.sh result dict (already reaped), not a Popen
    return rec


def main():
    P.mid_file(MID)
    res = {"smf": MID, "smf_bytes": os.path.getsize(MID), "legs": []}

    g0 = P.Graph(P.pw_dump())
    res["bridge_pre"] = midi_node_info("Midi", g0) + midi_node_info("bluez", g0)

    # Q1 pw-mididump bare — what node/ports does it publish?
    res["legs"].append(midi_leg("M1_dump_bare", ["pw-mididump"], wait=1.5))

    # Q2 pw-mididump <file> while aplaymidi injects through ALSA seq.
    out_mid = os.path.join(P.RAW, "m2_dump.mid")
    res["legs"].append(midi_leg(
        "M2_dump_file", ["pw-mididump", out_mid], wait=1.2,
        aplay=["aplaymidi", "-p", "14:0", MID]))
    res["m2_file"] = {"exists": os.path.exists(out_mid),
                      "bytes": os.path.getsize(out_mid) if os.path.exists(out_mid) else 0}

    # Q3 pw-mididump with manual pin from Midi-Bridge capture port
    out_mid3 = os.path.join(P.RAW, "m3_dump.mid")
    g = P.Graph(P.pw_dump())
    cap_ports = [p for n in g.find(BRIDGE) for p in g.nodes[n]["out"]]
    res["legs"].append(midi_leg(
        "M3_dump_pin", ["pw-mididump", out_mid3], wait=1.0,
        find=("pw-mididump", "r83dsp", "Midi"),
        aplay=["aplaymidi", "-p", "14:0", MID],
        link=[(f"{BRIDGE}:{cap_ports[0][0]}" if cap_ports else "x:y",
               "pw-mididump:input")]))
    res["m3_file"] = {"exists": os.path.exists(out_mid3),
                      "bytes": os.path.getsize(out_mid3) if os.path.exists(out_mid3) else 0}

    # Q4 pw-midiplay -> Midi-Bridge, aseqdump ALSA witness
    res["legs"].append(midi_leg(
        "M4_play_bridge",
        ["pw-midiplay", "--target", BRIDGE, "-P", "node.name=r83dsp_midiplay",
         MID], wait=1.2, find=("r83dsp", "pw-midiplay"), aseq=True))

    # Q5 pw-midiplay --target 0 (publish unlinked)
    res["legs"].append(midi_leg(
        "M5_play_t0",
        ["pw-midiplay", "--target", "0", "-P", "node.name=r83dsp_midi0", MID],
        wait=1.2, find=("r83dsp", "pw-midiplay")))

    # Q6 pw-midiplay bogus file
    res["legs"].append(midi_leg(
        "M6_play_nofile",
        ["pw-midiplay", "-P", "node.name=r83dsp_midi_nf",
         os.path.join(P.SCRATCH, "no_such.mid")], wait=1.0))

    # Q7 pw-mididump -M ump
    res["legs"].append(midi_leg("M7_dump_ump", ["pw-mididump", "-M", "ump"],
                                wait=1.2))

    # Q8 pw-midiplay -> garbage target (fallback where?)
    res["legs"].append(midi_leg(
        "M8_play_garbage",
        ["pw-midiplay", "--target", "no_such_midi_r83",
         "-P", "node.name=r83dsp_midi_gb", MID], wait=1.2,
        find=("r83dsp", "pw-midiplay"), aseq=True))

    g1 = P.Graph(P.pw_dump())
    res["bridge_post_edges"] = g1.edges("Midi") + g1.edges("bluez")
    return P.save_receipt("p3-midi.json", res)


if __name__ == "__main__":
    print(main())
