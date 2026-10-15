#!/usr/bin/env python3
"""r78b p5 — aplay -D hw: vs PipeWire: REVERSE hold (aplay first) +
monitor-tap witness contention, on idle Speaker (hw:0,0)."""
import os, sys, time, subprocess, signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r78b_lib import *

out = {"probe": "p5-aplay-reverse", "ts": time.time(),
       "env": foreign_note()}
out["cleanup"] = unload_all_mine()
make_tone(TONE, dur=1.8)
TONE4 = os.path.join(RAW, "tone4.wav"); make_tone(TONE4, dur=4.0)

SPK_PCM = "hw:0,0"   # Speaker per r78p pcm-map
out["pre"] = {"spk_state": node_state(S_SPK),
              "foreign_inputs": foreign_sink_inputs()}

def aplay(dev, f=TONE, extra=None, timeout=8.0):
    return sh(["aplay", "-D", dev, "-q", *(extra or []), f],
              timeout=timeout)

# -- A. baseline: aplay to the idle PCM (expect rc=0 real-time) -----------
out["A_aplay_idle"] = dict(zip(("rc","stdout","stderr","wall","to"),
                               aplay(SPK_PCM)))
out["A_aplay_idle"]["stderr"] = out["A_aplay_idle"]["stderr"][:120]

# -- B. monitor tap holds the PCM: tap Speaker, then aplay ----------------
tap_p = os.path.join(RAW, "spktap.wav")
tap = subprocess.Popen(
    ["pw-record", "-P", "node.name=r78bH_tap",
     "-P", "stream.capture.sink=true", "--target", S_SPK,
     "--format", "s16", "--rate", "48000", "--channels", "2", tap_p],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.0)
out["B_state_with_tap"] = node_state(S_SPK)
out["B_aplay_vs_tap"] = dict(zip(("rc","stdout","stderr","wall","to"),
                               aplay(SPK_PCM)))
out["B_aplay_vs_tap"]["stderr"] = out["B_aplay_vs_tap"]["stderr"][:120]
tap.send_signal(signal.SIGTERM); tap.wait(timeout=5)
out["B_tap_cap"] = {"bytes": classify(tap_p)["meta"].get("bytes")}

# -- C. REVERSE: aplay holds PCM, then pw-play --target Speaker ------------
hold = subprocess.Popen(["aplay", "-D", SPK_PCM, "-q", TONE4],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.8)   # aplay holds the PCM now
out["C_hold_alive"] = hold.poll() is None
out["C_state_during_hold"] = node_state(S_SPK)
tag = "r78bH_pw"
leg = play_leg(["pw-play", "-P", f"node.name={tag}", "--target", S_SPK,
                TONE], tag, timeout=8.0,
               monitors=Monitors(sinks=[("spk", S_SPK), ("spdif", S_SPDIF),
                                        ("ns", NS)],
                                tag="r78bH_m"))
out["C_pwplay_vs_aplay_hold"] = {
    "rc": leg["rc"], "wall": leg["wall_s"], "stderr": leg["stderr"],
    "timed_out": leg["timed_out"], "links": leg["mid"].get("links"),
    "carried": leg["carried"], "state_after": node_state(S_SPK)}
# while still held, also a monitor tap on Speaker
if hold.poll() is None:
    tp2 = os.path.join(RAW, "spktap2.wav")
    tap2 = subprocess.Popen(
        ["pw-record", "-P", "node.name=r78bH_tap2",
         "-P", "stream.capture.sink=true", "--target", S_SPK,
         "--format", "s16", "--rate", "48000", "--channels", "2",
         "-n", "48000", tp2],
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        _, te = tap2.communicate(timeout=6)
        out["C_tap_during_hold"] = {"rc": tap2.returncode,
                                    "stderr": te.decode(
                                        errors="replace").strip()[:160],
                                    "cap": classify(tp2)["verdict"]}
    except subprocess.TimeoutExpired:
        tap2.kill(); tap2.wait()
        out["C_tap_during_hold"] = {"rc": "timeout_kill",
                                    "cap": classify(tp2)["verdict"]}
hold.wait(timeout=8)
out["C_hold_rc"] = hold.returncode

# -- D. retention re-check on my own tag ----------------------------------
out["D_retention"] = []
for dt in (0.3, 1.5, 4.0):
    r = aplay(SPK_PCM)
    out["D_retention"].append({"rc": r[0],
                               "err": r[2].strip()[:80], "wall": r[3]})
    if r[0] == 0:
        break
    time.sleep(dt)

# -- E. does a PipeWire PLAYBACK on Speaker block aplay? (scout row, mine)
pl = subprocess.Popen(["pw-play", "-P", "node.name=r78bH_fill",
                       "--target", S_SPK, TONE4],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.8)
out["E_aplay_vs_pw_stream"] = dict(zip(("rc","stdout","stderr","wall","to"),
                                     aplay(SPK_PCM)))
out["E_aplay_vs_pw_stream"]["stderr"] = \
    out["E_aplay_vs_pw_stream"]["stderr"][:120]
pl.wait(timeout=8)
out["E_pw_rc"] = pl.returncode

out["post_state"] = node_state(S_SPK)
out["post_cleanup"] = unload_all_mine()
save("probe-p5-aplay-reverse-r78b.json", out)
for k in ("A_aplay_idle", "B_aplay_vs_tap", "E_aplay_vs_pw_stream"):
    print(k, "rc", out[k]["rc"], "wall", out[k]["wall"],
          "err", out[k]["stderr"])
print("B_state_with_tap:", out["B_state_with_tap"])
print("C:", {k: out["C_pwplay_vs_aplay_hold"][k] for k in
             ("rc","wall","stderr","carried","state_after")})
print("C links:", out["C_pwplay_vs_aplay_hold"]["links"])
print("C_tap_during_hold:", out.get("C_tap_during_hold"))
print("D:", out["D_retention"])
