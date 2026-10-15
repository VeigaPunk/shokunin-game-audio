#!/usr/bin/env python3
"""Probe E3 — ffmpeg pulse OUTPUT, forced past the mpegts misprobe.

E1/E2's ffmpeg legs failed before touching PipeWire: ffmpeg's format probe
scored `mpegts` 100 over `wav` 99 on this seat's periodic dual-tone wav, then
failed with `could not find codec parameters`.  With `-f wav` the same file
demuxes fine, so the pulse-output lattice can finally be measured.
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


def leg(label, dev, out, timeout=10.0):
    mon = H.Monitors(sinks=WITS, tag="r78pmonE3_" + label, win=0.25)
    mon.start()
    argv = ["ffmpeg", "-hide_banner", "-nostdin", "-re", "-f", "wav", "-i",
            TONE, "-f", "pulse", "-device", dev, "out"]
    t0 = time.monotonic()
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout)
        rc, se, to = p.returncode, p.stderr.decode(errors="replace"), False
    except subprocess.TimeoutExpired as exc:
        rc, se, to = None, (exc.stderr or b"").decode(errors="replace"), True
    wall = round(time.monotonic() - t0, 3)
    time.sleep(0.5)
    caps = mon.stop()
    rec = {"label": label, "device": dev, "argv": argv, "rc": rc,
           "wall_s": wall, "timed_out": to,
           "stderr_tail": se.strip().splitlines()[-3:],
           "carried": [k for k, v in caps.items()
                       if v["verdict"] in ("mine", "mine_r_tag")],
           "tone_windows": {k: v["mine"] for k, v in caps.items() if v["mine"]}}
    out["legs"].append(rec)
    print(f"{label:24s} rc={str(rc):>4s} wall={wall:5.2f} "
          f"carried={rec['carried']} tail={rec['stderr_tail'][-1:]}", flush=True)
    for f in os.listdir(H.RAW):
        if f.startswith("r78pmonE3_"):
            os.unlink(os.path.join(H.RAW, f))
    return rec


def main():
    out = {"probe": "ffmpeg-pulse-output-r78p", "legs": [],
           "toolchain": H.toolchain()}
    out["pre_cleanup"] = H.unload_all_mine()
    m1, _, _ = H.load_null(H.NS)
    m2, _, _ = H.load_null(H.NS2)
    time.sleep(0.6)
    H.make_tone(TONE, dur=1.2)
    for label, dev in (("ffmpeg_ns", H.NS), ("ffmpeg_ns2", H.NS2),
                       ("ffmpeg_spdif", H.S_SPDIF),
                       ("ffmpeg_garbage", "no_such_sink")):
        leg(label, dev, out)
    H.unload(m1)
    H.unload(m2)
    out["post_cleanup"] = H.unload_all_mine()
    H.save("probe-ffmpeg-pulse-output-r78p.json", out)


if __name__ == "__main__":
    main()
