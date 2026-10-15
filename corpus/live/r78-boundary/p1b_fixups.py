#!/usr/bin/env python3
"""r78b p1b — fixups: FL-only pin (correct tag), dup-name winner rule,
late-bind content witness."""
import os, sys, time, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r78b_lib import *

out = {"probe": "p1b-fixups", "ts": time.time()}
out["cleanup"] = unload_all_mine()
TONE4 = os.path.join(RAW, "tone4.wav")
make_tone(TONE4, dur=4.0)
make_tone(TONE, dur=1.8)

m1, _, _ = load_null(NS, "r78b probe A")
time.sleep(0.5)
legs = {}

# -- FL-only pin (correct tag this time) ---------------------------------
def _pin_fl():
    r = sh(["pw-link", "r78bB_pinfl:output_FL", f"{NS}:playback_FL"],
           timeout=6)
    return f"pinrc={r[0]} err={r[2].strip()[:80]}"
legs["pin_fl_only"] = play_leg(
    ["pw-play", "-P", "node.name=r78bB_pinfl", "--target", "0", TONE4],
    "r78bB_pinfl", timeout=9.0, actions=[(1.6, _pin_fl)],
    timeline_every=0.5)

# -- dup-name winner: is it lowest-serial / first-created? ----------------
dm1, _, _ = load_null("r78b_dup", "r78b dup A")
time.sleep(0.3)
dm2, _, _ = load_null("r78b_dup", "r78b dup B")
time.sleep(0.5)
dups = pw_objects_by_name("r78b_dup")
out["dup_nodes_2"] = dups
dups_sorted = sorted(dups, key=lambda n: n["object.serial"])
dup_wit = [("ns", NS), ("spdif", S_SPDIF)] + [
    (f"d{n['object.serial']}", str(n["object.serial"])) for n in dups_sorted]
mon = Monitors(sinks=dup_wit, tag="r78bdupm")
legs["dup_again"] = play_leg(
    ["pw-play", "-P", "node.name=r78bB_dup", "--target", "r78b_dup", TONE],
    "r78bB_dup", timeout=9.0, monitors=mon)

# -- late-bind WITH a witness that exists: start capture after load -------
mid_l, rc_l, e_l = load_null("r78b_late2", "r78b late2")
time.sleep(0.4)
cap_path = os.path.join(RAW, "late2cap.wav")
cap = subprocess.Popen(
    ["pw-record", "-P", "node.name=r78bB_latecap",
     "-P", "stream.capture.sink=true", "--target", "r78b_late2",
     "--format", "s16", "--rate", "48000", "--channels", "2", cap_path],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.4)
unload(mid_l)          # sink dies; metadata untouched; then re-create
time.sleep(0.6)
mid_l2, _, _ = load_null("r78b_late2", "r78b late2 reborn")
time.sleep(3.0)        # does the DEFECTED witness re-bind to the reborn sink?
cap.send_signal(signal.SIGTERM)
cap.wait(timeout=5)
legs["latecap_after_recreate"] = classify(cap_path)
legs["latecap_after_recreate"]["note"] = (
    "capture started while r78b_late2 absent -> defected to default; "
    "then r78b_late2 re-created at ~1s — does the capture re-bind?")

out["legs"] = legs
out["post_cleanup"] = unload_all_mine()
out["post_cleanup2"] = unload_all_mine(prefix="r78b_dup") or unload_all_mine()
save("probe-p1b-fixups-r78b.json", out)
for k, l in legs.items():
    if isinstance(l, dict) and "rc" in l:
        print(f"{k:20s} rc={l['rc']} wall={l['wall_s']} carried={l['carried']}")
        print("   actions:", l.get("actions"))
    else:
        print(k, "->", {kk: l[kk] for kk in ("verdict", "mine", "foreign")
                        if kk in l} if isinstance(l, dict) else l)
