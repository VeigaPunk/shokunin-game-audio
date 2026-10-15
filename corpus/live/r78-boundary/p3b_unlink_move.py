#!/usr/bin/env python3
"""r78b p3b — move-sink-input on a manually-unlinked stream (fixed unlink)."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r78b_lib import *

out = {"probe": "p3b-unlink-move", "ts": time.time()}
out["cleanup"] = unload_all_mine()
TONE6 = os.path.join(RAW, "tone6.wav")
make_tone(TONE6, dur=6.0)
m1, _, _ = load_null(NS, "r78b probe A")
m2, _, _ = load_null(NS2, "r78b probe B")
time.sleep(0.6)
legs = {}

tag = "r78bF_revive"
def _unlink():
    a = sh(["pw-link", "-d", f"{tag}:output_FL", f"{NS}:playback_FL"],
           timeout=6)
    b = sh(["pw-link", "-d", f"{tag}:output_FR", f"{NS}:playback_FR"],
           timeout=6)
    return f"dFL={a[0]}:{a[2].strip()[:40]} dFR={b[0]}:{b[2].strip()[:40]}"
def _mv():
    i = sink_input_index(tag)
    rc, o, e, w, t = pactl("move-sink-input", str(i), NS2)
    return f"idx={i} rc={rc} err={e.strip()[:60]}"
legs["unlink_then_move"] = play_leg(
    ["pw-play", "-P", f"node.name={tag}", "--target", NS, TONE6],
    tag, timeout=13.0, actions=[(1.8, _unlink), (2.6, _mv)],
    timeline_every=0.35)

# and: unlink then RE-LINK manually, then move (moved after relink)
tag2 = "r78bF_relink"
def _unlink2():
    a = sh(["pw-link", "-d", f"{tag2}:output_FL", f"{NS}:playback_FL"],
           timeout=6)
    b = sh(["pw-link", "-d", f"{tag2}:output_FR", f"{NS}:playback_FR"],
           timeout=6)
    return f"d={a[0]},{b[0]}"
def _relink2():
    a = sh(["pw-link", f"{tag2}:output_FL", f"{NS2}:playback_FL"], timeout=6)
    b = sh(["pw-link", f"{tag2}:output_FR", f"{NS2}:playback_FR"], timeout=6)
    return f"l={a[0]},{b[0]} err={a[2].strip()[:50]}"
legs["unlink_then_manual_pin_ns2"] = play_leg(
    ["pw-play", "-P", f"node.name={tag2}", "--target", NS, TONE6],
    tag2, timeout=13.0, actions=[(1.8, _unlink2), (2.6, _relink2)],
    timeline_every=0.35)

out["legs"] = legs
out["post_cleanup"] = unload_all_mine()
save("probe-p3b-unlink-move-r78b.json", out)
for k, l in legs.items():
    print(f"== {k}: rc={l['rc']} wall={l['wall_s']} carried={l['carried']}")
    print("   actions:", l["actions"])
    for t, c in l["timeline"]:
        print("   t", t, {p.split(':')[0][-16:]: [x.split(':')[0][:30]
                                                 for x in v]
                          for p, v in c.items()})
    for lab in ("ns", "ns2", "spdif"):
        print("   ", lab, l["caps"][lab]["mine"])
