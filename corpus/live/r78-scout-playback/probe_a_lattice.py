#!/usr/bin/env python3
"""Probe A (strict) — the PLAYBACK-side sink-selection lattice.

Playback has no output artifact, so each leg is judged by two independent
witnesses:
  * link topology: consumers of <tag>:output_* ports (names the port pair)
  * content: which candidate sink's monitor carries THIS seat's tagged tone
    (L 1 kHz / R 1.5 kHz, amp 8192) — frequency-strict, because a concurrent
    lane's tone aliases the default-sink monitor.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r78p as H

KEEP = {"ns_baseline", "garbage", "zero_target", "no_target", "control",
        "fallback_default_spk"}

STATIC = [
    ("control", []),                       # no playback: ambient floor
    ("ns_baseline", ["--target", H.NS]),
    ("ns2", ["--target", H.NS2]),
    ("spk_real", ["--target", H.S_SPK]),
    ("spdif_real", ["--target", H.S_SPDIF]),
    ("hdmi_real", ["--target", H.S_HDMI]),
    ("garbage", ["--target", "no_such_sink_xyz"]),
    ("garbage2", ["--target", "r78p_ns_absent"]),
    ("default_word", ["--target", "default"]),
    ("pulse_word", ["--target", "pulse"]),
    ("at_default_sink", ["--target", "@DEFAULT_SINK@"]),
    ("at_default_monitor", ["--target", "@DEFAULT_MONITOR@"]),
    ("at_default_source", ["--target", "@DEFAULT_SOURCE@"]),
    ("line_source_name", ["--target", H.LINE]),
    ("mic_source_name", ["--target", H.MIC]),
    ("ns_monitor_suffix", ["--target", H.NS + ".monitor"]),
    ("spdif_monitor_suffix", ["--target", H.S_SPDIF + ".monitor"]),
    ("zero_target", ["--target", "0"]),
    ("zero_target_n", ["--target", "0", "-n", "48000"]),
    ("no_target", []),
    ("empty_target", ["--target", ""]),
]


def run_leg(label, args, out, timeout=9.0, sample_every=0.4):
    tag = "r78pA_" + label
    mon = H.Monitors(tag="r78pmonA_" + label)
    if label == "control":                 # no consumer at all
        mon.start()
        time.sleep(2.6)
        caps = mon.stop()
        leg = {"argv": [], "rc": None, "stderr": "", "wall_s": 2.6,
               "timed_out": False, "mid": {}, "timeline": [], "caps": caps,
               "carried": [], "foreign": [k for k, v in caps.items()
                                          if "foreign" in v["verdict"]]}
    else:
        argv = ["pw-play", "-P", f"node.name={tag}", *args, H.TONE]
        leg = H.one_leg(mon, argv, tag, probe_at=0.85, timeout=timeout,
                        sample_every=sample_every)
    leg["label"], leg["requested"] = label, args
    out["legs"].append(leg)
    print(f"{label:22s} rc={leg['rc']} wall={leg['wall_s']:5.2f} "
          f"mine={leg['carried']} foreign={leg['foreign']} "
          f"links={sorted({p for v in leg['mid'].get('links', {}).values() for p in v})} "
          f"tgt={leg['mid'].get('props', {}).get('target.object')} "
          f"err={leg['stderr'][:50]!r}", flush=True)
    return leg


def main():
    out = {"probe": "playback-target-lattice-strict-r78p",
           "host": os.uname().nodename, "toolchain": H.toolchain(),
           "legs": []}
    m1, _, _ = H.load_null(H.NS)
    m2, _, _ = H.load_null(H.NS2)
    out["null_sinks"] = {"ns": m1, "ns2": m2}
    time.sleep(0.5)
    H.make_tone(dur=1.6)

    for label, args in STATIC:
        run_leg(label, args, out)

    # does the fallback follow the CURRENT default sink (dynamic) or SPDIF?
    rc, outb, err, _, _ = H.pactl("set-default-sink", H.S_SPK)
    time.sleep(0.4)
    out["default_sink_now"] = H.pactl("get-default-sink")[1].decode().strip()
    run_leg("fallback_default_spk", ["--target", "no_such_sink_xyz"], out)
    run_leg("default_word_spk", ["--target", "default"], out)
    run_leg("at_default_sink_spk", ["--target", "@DEFAULT_SINK@"], out)
    H.pactl("set-default-sink", H.S_SPDIF)
    time.sleep(0.4)
    out["default_sink_restored"] = H.pactl(
        "get-default-sink")[1].decode().strip()
    run_leg("fallback_default_spdif_again",
            ["--target", "no_such_sink_xyz"], out)

    H.unload(m1)
    H.unload(m2)
    for label in list(KEEP):
        pass
    # bound the footprint: keep only KEEP legs' witnesses
    for f in os.listdir(H.RAW):
        if f.startswith("r78pmonA_"):
            lab = f[len("r78pmonA_"):].rsplit("_", 1)[0]
            if lab not in KEEP:
                os.unlink(os.path.join(H.RAW, f))
    H.save("probe-play-lattice-strict-r78p.json", out)


if __name__ == "__main__":
    main()
