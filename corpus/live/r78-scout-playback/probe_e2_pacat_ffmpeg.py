#!/usr/bin/env python3
"""Probe E2 — pacat (raw) and ffmpeg pulse-OUTPUT legs, done right.

E1's pacat legs fed a WAV file to a RAW consumer (pacat -p defaults to
s16le/44100/2ch, so the wav header + 48 k rate never matched the tag tone), and
the ffmpeg legs used the wrong output syntax.  Both are re-measured with a raw
tone and ffmpeg's own documented muxer options.
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r78p as H

RAW = os.path.join(H.RAW, "tone_r78p.raw")
TONE = os.path.join(H.RAW, "tone_r78p_12.wav")
WITS = [("ns", H.NS), ("ns2", H.NS2), ("spdif", H.S_SPDIF),
        ("spk", H.S_SPK)]


def leg(label, argv, out, timeout=9.0):
    mon = H.Monitors(sinks=WITS, tag="r78pmonE2_" + label, win=0.25)
    mon.start()
    t0 = time.monotonic()
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout)
        rc, se, to = p.returncode, p.stderr.decode(errors="replace"), False
    except subprocess.TimeoutExpired as exc:
        rc, se, to = None, (exc.stderr or b"").decode(errors="replace"), True
    wall = round(time.monotonic() - t0, 3)
    time.sleep(0.5)
    caps = mon.stop()
    rec = {"label": label, "argv": argv, "rc": rc, "wall_s": wall,
           "timed_out": to, "stderr_tail": se.strip().splitlines()[-3:],
           "carried": [k for k, v in caps.items()
                       if v["verdict"] in ("mine", "mine_r_tag")],
           "tone_windows": {k: v["mine"] for k, v in caps.items() if v["mine"]},
           "foreign": {k: v["foreign"] for k, v in caps.items()
                       if v["foreign"]}}
    out["legs"].append(rec)
    print(f"{label:26s} rc={str(rc):>4s} wall={wall:5.2f} "
          f"carried={rec['carried']} tail={rec['stderr_tail'][-1:]}", flush=True)
    for f in os.listdir(H.RAW):
        if f.startswith("r78pmonE2_"):
            os.unlink(os.path.join(H.RAW, f))
    return rec


def main():
    out = {"probe": "cross-consumer-playback-e2-r78p", "legs": [],
           "toolchain": H.toolchain()}
    out["pre_cleanup"] = H.unload_all_mine()
    m1, _, _ = H.load_null(H.NS)
    m2, _, _ = H.load_null(H.NS2)
    time.sleep(0.6)
    H.make_tone(TONE, dur=1.2)
    # raw twin of the tone (same samples, no RIFF header)
    with open(TONE, "rb") as f:
        b = f.read()
    i = b.find(b"data", 12)
    n = int.from_bytes(b[i + 4:i + 8], "little")
    with open(RAW, "wb") as f:
        f.write(b[i + 8:i + 8 + n])
    out["raw_bytes"] = os.path.getsize(RAW)

    rc, o, e, _, _ = H.sh(["ffmpeg", "-hide_banner", "-h", "muxer=pulse"],
                          timeout=8)
    out["ffmpeg_pulse_muxer_help"] = o.decode(errors="replace").splitlines()[:20]

    for label, dev in (("pacat_ns", H.NS), ("pacat_garbage", "no_such_sink"),
                       ("pacat_line", H.LINE),
                       ("pacat_at_default", "@DEFAULT_SINK@"),
                       ("pacat_spdif", H.S_SPDIF)):
        leg(label, ["pacat", "-p", "--device", dev, "--format=s16le",
                    "--rate=48000", "--channels=2", RAW], out)
    for label, dev in (("ffmpeg_pulse_ns", H.NS),
                       ("ffmpeg_pulse_garbage", "no_such_sink")):
        leg(label, ["ffmpeg", "-hide_banner", "-nostdin", "-re", "-i", TONE,
                    "-f", "pulse", "-device", dev, "-"], out, timeout=10.0)
    H.unload(m1)
    H.unload(m2)
    out["post_cleanup"] = H.unload_all_mine()
    H.save("probe-cross-consumer-playback-e2-r78p.json", out)


if __name__ == "__main__":
    main()
