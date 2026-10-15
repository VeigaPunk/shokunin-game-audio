#!/usr/bin/env python3
"""Probe D2 — aplay device axis, unperturbed, and the witness observer-effect.

D1's device lattice returned `Device or resource busy` for every `hw:*` leg —
but the format legs (run WITHOUT monitor witnesses) opened the same PCMs fine.
Hypothesis: a PipeWire monitor capture holds the ALSA device, so the witness
needed to observe the direct-ALSA path is itself what breaks it.  Also: r78
reported arecord refusing the `pipewire`/`default` PCMs; D1 measured rc=0 with
the default u8/8k/mono request, so the refusal is request-dependent.
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r78p as H

TONE = os.path.join(H.RAW, "tone_r78p_12.wav")
AW = [("spdif", H.S_SPDIF), ("spk", H.S_SPK), ("hp", H.S_HP),
      ("hdmi", H.S_HDMI)]


def aplay(dev, out, label, witness=None, file=TONE, timeout=8.0, extra=()):
    tag = "r78pD2_" + label
    mon = None
    if witness:
        mon = H.Monitors(sinks=witness, tag="r78pmonD2_" + label, win=0.25)
        mon.start()
    argv = ["aplay", "-D", dev, *extra, file]
    t0 = time.monotonic()
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout)
        rc, se, to = p.returncode, p.stderr.decode(errors="replace"), False
    except subprocess.TimeoutExpired as exc:
        rc, se, to = None, (exc.stderr or b"").decode(errors="replace"), True
    wall = round(time.monotonic() - t0, 3)
    time.sleep(0.3)
    caps = mon.stop() if mon else {}
    leg = {"label": label, "dev": dev, "witness": [w[0] for w in (witness or [])],
           "rc": rc, "wall_s": wall, "timed_out": to,
           "stderr": se.strip().splitlines()[:3],
           "carried": [k for k, v in caps.items()
                       if v["verdict"] in ("mine", "mine_r_tag")],
           "tone_windows": {k: v["mine"] for k, v in caps.items() if v["mine"]}}
    out["legs"].append(leg)
    print(f"{label:34s} rc={str(rc):>4s} wall={wall:5.2f} "
          f"witness={leg['witness']} carried={leg['carried']} "
          f"err={se.strip().splitlines()[:1]}", flush=True)
    if mon:
        for f in os.listdir(H.RAW):
            if f.startswith("r78pmonD2_"):
                os.unlink(os.path.join(H.RAW, f))
    return leg


def arecord(dev, out, label, extra=(), timeout=8.0):
    argv = ["arecord", "-D", dev, *extra, "-d", "2", "/dev/null"]
    rc, o, e, wall, to = H.sh(argv, timeout=timeout)
    leg = {"label": label, "dev": dev, "argv": argv, "rc": rc, "wall_s": wall,
           "timed_out": to, "stderr": e.strip().splitlines()[:3]}
    out["arecord_legs"].append(leg)
    print(f"{label:34s} rc={str(rc):>4s} wall={wall:5.2f} "
          f"err={e.strip().splitlines()[:1]}", flush=True)
    return leg


def main():
    out = {"probe": "aplay-device-axis-d2-r78p", "legs": [],
           "arecord_legs": [], "toolchain": H.toolchain()}
    out["pre_cleanup"] = H.unload_all_mine()
    H.make_tone(TONE, dur=1.2)
    time.sleep(0.5)

    # (1) unperturbed direct-ALSA lattice
    for dev in ("hw:0,0", "hw:0,1", "hw:0,2", "hw:0,3", "plughw:0,0",
                "plughw:0,1", "sysdefault", "front:CARD=Audio,DEV=0",
                "iec958:CARD=Audio,DEV=0", "surround51:CARD=Audio,DEV=0"):
        aplay(dev, out, "free_" + dev.replace(":", "_").replace(",", "_")
              .replace("=", "-"))

    # (2) same PCMs WITH a monitor witness on the same card
    aplay("hw:0,1", out, "wit_spdifmon_hw01", witness=[("spdif", H.S_SPDIF)])
    aplay("hw:0,0", out, "wit_spkmon_hw00", witness=[("spk", H.S_SPK)])
    aplay("hw:0,1", out, "wit_hdmimon_hw01", witness=[("hdmi", H.S_HDMI)])

    # (3) same PCM while a PipeWire playback stream is active on that sink
    tag = "r78pD2_pwplay"
    proc = subprocess.Popen(["pw-play", "-P", f"node.name={tag}",
                             "--target", H.S_SPDIF,
                             os.path.join(H.RAW, "tone_r78p_6s.wav")],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)
    aplay("hw:0,1", out, "pwactive_hw01")
    arecord("hw:0,0", out, "pwactive_hw00_rec")
    proc.kill()
    time.sleep(0.5)

    # (4) arecord pipewire/default request-dependence (r78's TICK_TIME row)
    arecord("default", out, "rec_default_u8_8k_mono")
    arecord("default", out, "rec_default_s16_48k_stereo",
            extra=["-f", "S16_LE", "-r", "48000", "-c", "2"])
    arecord("pipewire", out, "rec_pipewire_s16_48k_stereo",
            extra=["-f", "S16_LE", "-r", "48000", "-c", "2"])
    arecord("pipewire", out, "rec_pipewire_u8_8k_mono")
    arecord("default", out, "rec_default_s16_44k_stereo_nod",
            extra=["-f", "S16_LE", "-r", "44100", "-c", "2"])

    # (5) fair arecord --dump-hw-params (bounded with -d 1)
    for dev in ("hw:0,0", "hw:0,1", "hw:0,2", "hw:0,3", "plughw:0,0",
                "sysdefault", "null", "default", "pipewire"):
        rc, o, e, wall, to = H.sh(
            ["arecord", "-D", dev, "--dump-hw-params", "-d", "1",
             "/dev/null"], timeout=8)
        txt = [l.strip() for l in e.splitlines() if l.strip()]
        out.setdefault("arecord_hw_params", []).append(
            {"dev": dev, "rc": rc, "lines": txt[:10]})
        print(f"  rec-hwparams {dev:12s} rc={rc} "
              f"{[x for x in txt if x.startswith(('CHANNELS', 'RATE', 'FORMAT'))][:3]}",
              flush=True)

    H.save("probe-aplay-axis-d2-r78p.json", out)


if __name__ == "__main__":
    main()
