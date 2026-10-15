#!/usr/bin/env python3
"""r78b p6 — media.class variant lattice on pw-play + cross-consumer crash."""
import os, sys, time, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r78b_lib import *

out = {"probe": "p6-mediaclass", "ts": time.time(),
       "env": foreign_note()}
out["cleanup"] = unload_all_mine()
make_tone(TONE, dur=1.8)
m1, _, _ = load_null(NS, "r78b probe A")
time.sleep(0.5)

VARIANTS = [
    ("control_out", "Stream/Output/Audio"),
    ("audio_source", "Audio/Source"),
    ("audio_sink", "Audio/Sink"),
    ("audio_sink_virtual", "Audio/Sink/Virtual"),
    ("audio_source_virtual", "Audio/Source/Virtual"),
    ("stream_in_audio", "Stream/Input/Audio"),
    ("stream_in_midi", "Stream/Input/Audio/Midi"),
    ("stream_out_midi", "Stream/Output/Audio/Midi"),
    ("audio_duplex", "Audio/Duplex"),
    ("midi_bridge", "Midi/Bridge"),
    ("video_source", "Video/Source"),
    ("lowercase", "stream/output/audio"),
    ("uppercase", "STREAM/OUTPUT/AUDIO"),
    ("trailing_space", "Stream/Output/Audio "),
    ("audio_source_sink", "Audio/Source/Sink"),
    ("internal", "Audio/Internal"),
]
legs = {}
for label, cls in VARIANTS:
    tag = f"r78bI_{label}"
    argv = ["pw-play", "-P", f"node.name={tag}", "-P",
            f"media.class={cls}", "--target", NS, TONE]
    legs[label] = play_leg(argv, tag, timeout=6.0, tail=0.4)

# cross-consumer: same wrong class via pw-cat -p, PIPEWIRE_PROPS, paplay env
tag = "r78bI_pwcat"
legs["pwcat_audio_sink"] = play_leg(
    ["pw-cat", "-P", f"node.name={tag}", "-P", "media.class=Audio/Sink",
     "-p", "--target", NS, TONE], tag, timeout=6.0)
tag = "r78bI_env"
legs["envprops_audio_sink"] = play_leg(
    ["pw-play", "-P", f"node.name={tag}", "--target", NS, TONE], tag,
    timeout=6.0, env={"PIPEWIRE_PROPS": "{ media.class=Audio/Sink }"})
tag = "r78bI_paplay"
legs["paplay_pulseprop"] = play_leg(
    ["paplay", "--device", NS, TONE], tag, timeout=6.0,
    env={"PULSE_PROP_media.class": "Audio/Sink"})
# capture-side symmetry: pw-record with an OUTPUT class
rcp = os.path.join(RAW, "mclass_cap.wav")
tag = "r78bI_rec"
legs["pwrecord_audio_sink"] = play_leg(
    ["pw-record", "-P", f"node.name={tag}", "-P", "media.class=Audio/Sink",
     "-P", "stream.capture.sink=true", "--target", NS, "-n", "48000",
     "--format", "s16", rcp], tag, timeout=6.0)
legs["pwrecord_audio_sink"]["cap_bytes"] = \
    classify(rcp)["meta"].get("bytes")

out["legs"] = legs
out["post_cleanup"] = unload_all_mine()
save("probe-p6-mediaclass-r78b.json", out)
for k, l in legs.items():
    st = l["mid"].get("node_state")
    cls = (l["mid"].get("props") or {}).get("media.class")
    print(f"{k:22s} rc={l['rc']} wall={l['wall_s']} out={l['timed_out']} "
          f"carried={l['carried']} node={st} cls={cls} "
          f"err={l['stderr'][:60]!r}")
