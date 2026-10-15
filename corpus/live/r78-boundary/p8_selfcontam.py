#!/usr/bin/env python3
"""r78b p8 — self-contamination: double-fallback false positive, two-producer
mix on one sink, twin node.name confusion, capture-side late bind."""
import os, sys, time, subprocess, signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r78b_lib import *
import numpy as np

out = {"probe": "p8-selfcontam", "ts": time.time(),
       "env": foreign_note()}
out["cleanup"] = unload_all_mine()
make_tone(TONE, dur=4.0)
make_tone(TONE2, dur=4.0, fl=TONE2_F_L, fr=TONE2_F_R, amp=14000)
m1, _, _ = load_null(NS, "r78b probe A")
m2, _, _ = load_null(NS2, "r78b probe B")
time.sleep(0.6)
legs = {}

# -- A. the double-fallback false positive --------------------------------
# playback targets a missing sink; "witness" targets ANOTHER missing sink;
# both defect to the default -> witness sees the tone -> naive arm reads
# "target honored" for a target that never existed.
cap_missing = os.path.join(RAW, "selfcontam_missingwit.wav")
cap = subprocess.Popen(
    ["pw-record", "-P", "node.name=r78bK_wit", "-P",
     "stream.capture.sink=true", "--target", "r78b_missing_witness",
     "--format", "s16", "--rate", "48000", "--channels", "2",
     cap_missing], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.4)
tag = "r78bK_dfb"
legA = play_leg(
    ["pw-play", "-P", f"node.name={tag}", "--target", "r78b_missing_play",
     TONE], tag, timeout=9.0,
    monitors=Monitors(sinks=[("ns", NS), ("spdif", S_SPDIF)],
                      tag="r78bK_am"))
time.sleep(0.2); cap.send_signal(signal.SIGTERM); cap.wait(timeout=5)
legA["missing_witness_cap"] = classify(cap_missing)
legA["missing_witness_cap"]["note"] = (
    "witness targeted a NONEXISTENT sink yet saw the tone -> both legs "
    "defected to the default; a name-only arm reads honored")
legs["double_fallback_falsepos"] = legA

# -- B. two producers into ONE sink: does the monitor carry the mix? ------
tag1, tag2 = "r78bK_p1", "r78bK_p2"
mon = Monitors(sinks=[("ns", NS)], tag="r78bK_bm")
mon.start()
p1 = subprocess.Popen(["pw-play", "-P", f"node.name={tag1}",
                       "--target", NS, TONE],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
p2 = subprocess.Popen(["pw-play", "-P", f"node.name={tag2}",
                       "--target", NS, TONE2],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
p1.wait(timeout=9); p2.wait(timeout=9)
caps = mon.stop()
w = caps["ns"]["windows"]
legs["two_producers_mix"] = {
    "rcs": [p1.returncode, p2.returncode],
    "mine_windows": caps["ns"]["mine"],
    "mine2_windows": caps["ns"]["mine2"],
    "window_sample": w[2] if len(w) > 2 else None,
    "note": "dominant freq per channel per window; sum/mix inferred"}

# -- C. twin node.name: two streams with ONE tag ---------------------------
tagx = "r78bK_twin"
mon = Monitors(sinks=[("ns", NS), ("ns2", NS2)], tag="r78bK_cm")
mon.start()
p1 = subprocess.Popen(["pw-play", "-P", f"node.name={tagx}",
                       "--target", NS, TONE],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
p2 = subprocess.Popen(["pw-play", "-P", f"node.name={tagx}",
                       "--target", NS2, TONE2],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.2)
links = consumers_of(pwlink(), tagx)
p1.wait(timeout=9); p2.wait(timeout=9)
caps = mon.stop()
legs["twin_name_topology"] = {
    "links_seen": links,
    "ns_mine": caps["ns"]["mine"], "ns2_mine": caps["ns2"]["mine"],
    "ns2_mine2": caps["ns2"]["mine2"],
    "note": "consumers_of(tag) merges both twins -> topology ambiguity"}

# -- D. capture-side late bind (mirror of p1's playback late-bind) --------
cap3 = os.path.join(RAW, "latebind_cap.wav")
cap = subprocess.Popen(
    ["pw-record", "-P", "node.name=r78bK_cap3",
     "-P", "stream.capture.sink=true", "--target", "r78b_late3",
     "--format", "s16", "--rate", "48000", "--channels", "2", cap3],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.6)
mm, _, _ = load_null("r78b_late3", "r78b late3")     # sink appears NOW
time.sleep(0.5)
pl = subprocess.Popen(["pw-play", "-P", "node.name=r78bK_feed3",
                       "--target", "r78b_late3", TONE],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
pl.wait(timeout=8)
time.sleep(0.3); cap.send_signal(signal.SIGTERM); cap.wait(timeout=5)
legs["capture_late_bind"] = classify(cap3)
legs["capture_late_bind"]["note"] = (
    "capture started while target absent (defected to default); "
    "target appeared at ~0.6s, tone fed ~1.1-2.9s -> mine windows "
    "mean the capture re-bound")

# -- E. 6ch file port fan-out (does pw-play publish >2 outputs?) ----------
p6 = subprocess.Popen(["pw-play", "-P", "node.name=r78bK_ch6",
                       "--target", NS, os.path.join(RAW, "f_ch6.wav")],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.8)
rc_, o_, e_, _, _ = sh(["pw-link", "-o"], timeout=6)
ports = [l.strip() for l in o_.decode(errors="replace").splitlines()
         if l.strip().startswith("r78bK_ch6:")]
p6.wait(timeout=8)
legs["ch6_output_ports"] = {"ports": ports, "rc": p6.returncode}

out["legs"] = legs
out["post_cleanup"] = unload_all_mine()
save("probe-p8-selfcontam-r78b.json", out)
for k, l in legs.items():
    print("==", k)
    for kk, vv in l.items():
        if kk != "windows":
            print("   ", kk, str(vv)[:150])
