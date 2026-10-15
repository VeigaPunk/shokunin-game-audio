#!/usr/bin/env python3
"""r78b p2b — pin the routed sink under forged default metadata; dwell/heal."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r78b_lib import *

S_DS = ("alsa_output.usb-Sony_Interactive_Entertainment_DualSense_"
        "Wireless_Controller-00.Direct__Direct__sink")
WIT6 = [("ns", NS), ("spdif", S_SPDIF), ("spk", S_SPK),
        ("ds", S_DS), ("hdmi", S_HDMI)]

out = {"probe": "p2b-divergence", "ts": time.time()}
out["cleanup"] = unload_all_mine()
make_tone(TONE, dur=1.8)
m1, _, _ = load_null(NS, "r78b probe A")
time.sleep(0.5)

def meta(): return metadata_default()[0].get("default.audio.sink")
def restore(tag):
    set_default_sink_meta(SPDIF_META_JSON); time.sleep(0.4)
    out.setdefault("restores", []).append(
        {"tag": tag, "get": get_default_sink()[:2], "meta": meta()})

def pactl_info_default():
    rc, o, e, _, _ = sh(["pactl", "info"], timeout=8)
    for ln in o.decode(errors="replace").splitlines():
        if "Default Sink" in ln:
            return ln.strip()
    return "?"

try:
    # --- dwell: does WirePlumber heal a bogus metadata value? --------------
    set_default_sink_meta('{"name":"no_such_sink_r78b"}')
    out["dwell"] = []
    for i in range(6):
        time.sleep(0.7)
        out["dwell"].append({"t": round(0.7*(i+1), 1),
                             "get": get_default_sink()[0],
                             "pactl_info": pactl_info_default(),
                             "meta": meta()})
    # --- the routed-sink pin: 5 witnesses incl. DualSense -------------------
    tag = "r78bD_pin"
    mon = Monitors(sinks=WIT6, tag=f"{tag}m")
    out["leg_pin"] = play_leg(
        ["pw-play", "-P", f"node.name={tag}", "--target",
         "no_such_sink_r78b", TONE], tag, timeout=9.0, monitors=mon)
    tag = "r78bD_pin2"
    mon = Monitors(sinks=WIT6, tag=f"{tag}m")
    out["leg_pin_notarget"] = play_leg(
        ["pw-play", "-P", f"node.name={tag}", TONE], tag, timeout=9.0,
        monitors=mon)
    # --- does a live stream FOLLOW into the bogus-default route? -----------
    # active stream to r78b_ns; then default->bogus: does it get moved?
    tag = "r78bD_follow"
    mon = Monitors(sinks=WIT6, tag=f"{tag}m")
    def _setbogus():
        r = set_default_sink_meta('{"name":"no_such_sink_r78b"}')
        return f"setrc={r[0]}"
    out["leg_follow"] = play_leg(
        ["pw-play", "-P", f"node.name={tag}", "--target", NS,
         os.path.join(RAW, "tone4.wav")], tag, timeout=10.0,
        monitors=mon, actions=[(2.2, _setbogus)], timeline_every=0.4)
finally:
    restore("FINAL")
    out["post_cleanup"] = unload_all_mine()
    out["post_default"] = get_default_sink()
    out["post_meta"] = meta()

save("probe-p2b-divergence-r78b.json", out)
for d_ in out["dwell"]:
    print(d_["t"], "| get:", d_["get"][-40:], "| info:",
          d_["pactl_info"][-45:], "| meta:", str(d_["meta"])[:50])
for k in ("leg_pin", "leg_pin_notarget", "leg_follow"):
    l = out[k]
    print(k, "rc", l["rc"], "carried", l["carried"],
          "links", json.dumps(l["mid"].get("links"))[:160])
EOF = None
