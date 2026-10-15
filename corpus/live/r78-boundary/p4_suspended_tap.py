#!/usr/bin/env python3
"""r78b p4 — monitor-tap of a SUSPENDED sink (null + hardware Speaker)."""
import os, sys, time, subprocess, signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r78b_lib import *

out = {"probe": "p4-suspended-tap", "ts": time.time(),
       "env": foreign_note()}
out["cleanup"] = unload_all_mine()
make_tone(TONE, dur=1.8)
TONE4 = os.path.join(RAW, "tone4.wav"); make_tone(TONE4, dur=4.0)

SUS = "r78b_sus"
m1, _, _ = load_null(SUS, "r78b suspended")
time.sleep(0.8)
out["fresh_state"] = node_state(SUS)
rc, o, e, _, _ = pactl("suspend-sink", SUS, "1")
time.sleep(0.5)
out["after_pactl_suspend"] = {"rc": rc, "err": e.strip()[:80],
                              "state": node_state(SUS)}

# -- tap the suspended null sink (bounded capture) ------------------------
def capture(path, target, frames=96000, timeout=8.0, props=None):
    argv = ["pw-record", "-P", "node.name=r78bG_tap",
            "-P", "stream.capture.sink=true",
            "--target", target, "--format", "s16", "--rate", "48000",
            "--channels", "2", "-n", str(frames), path]
    for pr in (props or []):
        argv[1:1] = ["-P", pr]
    rc, so, se, w, to = sh(argv, timeout=timeout)
    c = classify(path)
    return {"rc": rc, "wall": w, "timed_out": to,
            "stderr": se.strip()[:160], "bytes": c["meta"].get("bytes"),
            "verdict": c["verdict"],
            "peaks": [x["peak_L"] for x in c["windows"]][:8],
            "state_after": node_state(target)}

p1 = os.path.join(RAW, "tap_suspended.wav")
out["tap_suspended_null"] = capture(p1, SUS)

# -- tap WHILE suspended, then unsuspend mid-capture -----------------------
p2 = os.path.join(RAW, "tap_then_unsuspend.wav")
cap = subprocess.Popen(
    ["pw-record", "-P", "node.name=r78bG_tap2",
     "-P", "stream.capture.sink=true", "--target", SUS,
     "--format", "s16", "--rate", "48000", "--channels", "2", p2],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.2)
st_during = node_state(SUS)
pactl("suspend-sink", SUS, "0")
time.sleep(0.6)
st_after_unsusp = node_state(SUS)
# now play the tag tone into it for 1.8s so a re-alive tap shows content
pl = subprocess.Popen(["pw-play", "-P", "node.name=r78bG_fill",
                       "--target", SUS, TONE],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
pl.wait(timeout=6)
time.sleep(0.4)
cap.send_signal(signal.SIGTERM); cap.wait(timeout=5)
c2 = classify(p2)
out["tap_while_suspended_then_live"] = {
    "state_during_suspend": st_during,
    "state_after_unsuspend": st_after_unsusp,
    "bytes": c2["meta"].get("bytes"), "verdict": c2["verdict"],
    "mine_windows": c2["mine"], "windows": c2["windows"]}

# -- play into a suspended sink: does playback wake it? --------------------
pactl("suspend-sink", SUS, "1"); time.sleep(0.5)
out["state_pre_play"] = node_state(SUS)
leg = play_leg(["pw-play", "-P", "node.name=r78bG_play",
                "--target", SUS, TONE4], "r78bG_play", timeout=10.0,
               monitors=Monitors(sinks=[("sus", SUS), ("spdif", S_SPDIF)],
                                 tag="r78bG_susm"))
out["play_into_suspended"] = {"rc": leg["rc"], "carried": leg["carried"],
                              "state_after": node_state(SUS),
                              "links": leg["mid"].get("links")}

# -- hardware: Speaker is already SUSPENDED; tap it (isolated, unused) ----
out["spk_state_pre"] = node_state(S_SPK)
p3 = os.path.join(RAW, "tap_spk.wav")
out["tap_suspended_hw"] = capture(p3, S_SPK)
# and unsuspend+tap comparison on the same sink:
pactl("suspend-sink", S_SPK, "0"); time.sleep(0.3)
p4 = os.path.join(RAW, "tap_spk_live.wav")
out["tap_live_hw"] = capture(p4, S_SPK)
pactl("suspend-sink", S_SPK, "1")   # leave it suspended again
time.sleep(0.3)
out["spk_state_post"] = node_state(S_SPK)

out["post_cleanup"] = unload_all_mine()
save("probe-p4-suspended-tap-r78b.json", out)
for k, v in out.items():
    if isinstance(v, dict) and "verdict" in v:
        print(k, {kk: v[kk] for kk in ("rc","wall","bytes","verdict",
                                       "state_after") if kk in v})
print("play_into_suspended:", {k: out["play_into_suspended"][k]
      for k in ("rc","carried","state_after")})
print("tap_while_suspended_then_live:", {
      k: out["tap_while_suspended_then_live"][k] for k in
      ("state_during_suspend","state_after_unsuspend","bytes","verdict",
       "mine_windows")})
print("fresh_state:", out["fresh_state"], "| after_pactl_suspend:",
      out["after_pactl_suspend"])
