#!/usr/bin/env python3
"""Probe E — cross-consumer playback lattice (paplay / pacat / ffmpeg) plus the
ALSA lock-retention window that confounded D3's matrix.

Questions: does the pulse-protocol playback side (paplay/pacat) share the
native lattice (unresolvable device -> default sink)?  And how long does a
PipeWire stream keep the ALSA PCM of its sink locked against direct `aplay -D
hw:` access?
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r78p as H

TONE = os.path.join(H.RAW, "tone_r78p_12.wav")
WITS = [("ns", H.NS), ("ns2", H.NS2), ("spdif", H.S_SPDIF),
        ("spk", H.S_SPK)]


def leg(label, argv, out, timeout=8.0, env=None):
    tag = "r78pE_" + label
    mon = H.Monitors(sinks=WITS, tag="r78pmonE_" + label, win=0.25)
    mon.start()
    t0 = time.monotonic()
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout,
                           env={**os.environ, **(env or {})})
        rc, se, to = p.returncode, p.stderr.decode(errors="replace"), False
    except subprocess.TimeoutExpired as exc:
        rc, se, to = None, (exc.stderr or b"").decode(errors="replace"), True
    wall = round(time.monotonic() - t0, 3)
    time.sleep(0.5)
    caps = mon.stop()
    rec = {"label": label, "argv": argv, "rc": rc, "wall_s": wall,
           "timed_out": to, "stderr": se.strip().splitlines()[:3],
           "carried": [k for k, v in caps.items()
                       if v["verdict"] in ("mine", "mine_r_tag")],
           "tone_windows": {k: v["mine"] for k, v in caps.items() if v["mine"]},
           "foreign": {k: v["foreign"] for k, v in caps.items()
                       if v["foreign"]}}
    out["legs"].append(rec)
    print(f"{label:26s} rc={str(rc):>4s} wall={wall:5.2f} "
          f"carried={rec['carried']} err={se.strip().splitlines()[:1]}",
          flush=True)
    for f in os.listdir(H.RAW):
        if f.startswith("r78pmonE_"):
            os.unlink(os.path.join(H.RAW, f))
    return rec


def main():
    out = {"probe": "cross-consumer-playback-r78p", "legs": [],
           "lock_retention": [], "toolchain": H.toolchain()}
    out["pre_cleanup"] = H.unload_all_mine()
    m1, _, _ = H.load_null(H.NS)
    m2, _, _ = H.load_null(H.NS2)
    time.sleep(0.6)
    H.make_tone(TONE, dur=1.2)

    # ---- paplay ---------------------------------------------------------
    leg("paplay_nodev", ["paplay", TONE], out)
    leg("paplay_ns", ["paplay", "--device", H.NS, TONE], out)
    leg("paplay_ns2", ["paplay", "--device", H.NS2, TONE], out)
    leg("paplay_garbage", ["paplay", "--device", "no_such_sink", TONE], out)
    leg("paplay_line_source", ["paplay", "--device", H.LINE, TONE], out)
    leg("paplay_monitor_name", ["paplay", "--device", H.NS + ".monitor", TONE],
        out)
    leg("paplay_at_default", ["paplay", "--device", "@DEFAULT_SINK@", TONE],
        out)
    leg("paplay_default_word", ["paplay", "--device", "default", TONE], out)
    leg("paplay_spdif", ["paplay", "--device", H.S_SPDIF, TONE], out)
    leg("paplay_spk", ["paplay", "--device", H.S_SPK, TONE], out)

    # ---- pacat ----------------------------------------------------------
    leg("pacat_ns", ["pacat", "-p", "--device", H.NS, TONE], out)
    leg("pacat_garbage", ["pacat", "-p", "--device", "no_such_sink", TONE],
        out)
    leg("pacat_at_default", ["pacat", "-p", "--device", "@DEFAULT_SINK@",
                             TONE], out)

    # ---- ffmpeg pulse output -------------------------------------------
    leg("ffmpeg_pulse_ns",
        ["ffmpeg", "-nostdin", "-re", "-i", TONE, "-f", "pulse",
         "-device", H.NS, "out"], out, timeout=10.0)
    leg("ffmpeg_pulse_garbage",
        ["ffmpeg", "-nostdin", "-re", "-i", TONE, "-f", "pulse",
         "-device", "no_such_sink", "out"], out, timeout=10.0)

    # ---- ALSA lock retention after a PipeWire stream ends ----------------
    for label, wait, dev in (("retention_1s", 1.0, "hw:0,0"),
                             ("retention_7s", 7.0, "hw:0,0"),
                             ("retention_1s_hp", 1.0, "hw:0,1"),
                             ("retention_7s_hp", 7.0, "hw:0,1")):
        target = H.S_SPK if dev == "hw:0,0" else H.S_HP
        p = subprocess.run(["pw-play", "-P", f"node.name=r78pE_{label}",
                            "--target", target, TONE], capture_output=True,
                           timeout=8)
        time.sleep(wait)
        try:
            q = subprocess.run(["aplay", "-D", dev, TONE], capture_output=True,
                               timeout=6)
            rc, err = q.returncode, q.stderr.decode(errors="replace")
        except subprocess.TimeoutExpired as exc:
            rc, err = None, (exc.stderr or b"").decode(errors="replace")
        row = {"label": label, "wait_s": wait, "dev": dev, "sink": target,
               "pw_play_rc": p.returncode,
               "aplay_rc": rc, "aplay_err": err.strip().splitlines()[:2]}
        out["lock_retention"].append(row)
        print(f"{label:26s} wait={wait:4.1f}s dev={dev} aplay_rc={rc} "
              f"{err.strip().splitlines()[:1]}", flush=True)
        time.sleep(2.0)

    H.unload(m1)
    H.unload(m2)
    out["post_cleanup"] = H.unload_all_mine()
    H.save("probe-cross-consumer-playback-r78p.json", out)


if __name__ == "__main__":
    main()
