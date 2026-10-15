#!/usr/bin/env python3
"""Probe D — the aplay device axis vs arecord's (same session, same host).

r77 pinned arecord's axis: `hw:0,0` stereo-only (`-f cd`/`-f dat` only),
`null` is the exact-arithmetic oracle, no `pulse` PCM, `sysdefault` TERM lands
`alsa_read_eintr`.  r78 found ffmpeg and arecord both REFUSE the `pipewire` /
`default` PCMs.  What does the PLAYBACK side do — and where does the audio
actually land (PipeWire monitor witness) versus the direct-ALSA path?
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r78p as H

TONE = os.path.join(H.RAW, "tone_r78p_12.wav")
TINY = os.path.join(H.RAW, "tiny_r78p.wav")
AW = [("spdif", H.S_SPDIF), ("spk", H.S_SPK), ("hp", H.S_HP),
      ("hdmi", H.S_HDMI)]

DEVICES = [
    ("hw00", ["-D", "hw:0,0"]),
    ("hw01", ["-D", "hw:0,1"]),
    ("hw02", ["-D", "hw:0,2"]),
    ("hw03", ["-D", "hw:0,3"]),
    ("plughw00", ["-D", "plughw:0,0"]),
    ("plughw01", ["-D", "plughw:0,1"]),
    ("sysdefault", ["-D", "sysdefault"]),
    ("sysdefault_Audio", ["-D", "sysdefault:CARD=Audio"]),
    ("front_Audio", ["-D", "front:CARD=Audio,DEV=0"]),
    ("iec958_dev0", ["-D", "iec958:CARD=Audio,DEV=0"]),
    ("iec958_dev1", ["-D", "iec958:CARD=Audio,DEV=1"]),
    ("surround51", ["-D", "surround51:CARD=Audio,DEV=0"]),
    ("default", ["-D", "default"]),
    ("pipewire", ["-D", "pipewire"]),
    ("null", ["-D", "null"]),
    ("pulse", ["-D", "pulse"]),
    ("nosuch", ["-D", "no_such_pcm"]),
    ("hw99", ["-D", "hw:9,9"]),
]

FORMATS = [
    ("cd", ["-f", "cd"]),
    ("dat", ["-f", "dat"]),
    ("s16", ["-f", "S16_LE"]),
    ("s16_mono", ["-f", "S16_LE", "-c", "1"]),
    ("s16_6ch", ["-f", "S16_LE", "-c", "6"]),
    ("s16_r44100", ["-f", "S16_LE", "-r", "44100"]),
    ("s16_r96000", ["-f", "S16_LE", "-r", "96000"]),
    ("f32", ["-f", "FLOAT_LE"]),
    ("s24_3le", ["-f", "S24_3LE"]),
    ("u8", ["-f", "U8"]),
    ("bogus", ["-f", "BOGUS"]),
]
FMT_DEVS = ["hw:0,0", "hw:0,1", "sysdefault", "default", "pipewire", "null"]


def nodes_now():
    return H.pw_nodes()


def run_aplay(label, args, out, dev=None, file=TONE, witness=True,
              timeout=8.0):
    tag = "r78pD_" + label
    before = set(nodes_now())
    mon = H.Monitors(sinks=AW, tag="r78pmonD_" + label, win=0.25) if witness \
        else None
    if mon:
        mon.start()
    argv = ["aplay", *args, file]
    t0 = time.monotonic()
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout)
        rc, se, to = p.returncode, p.stderr.decode(errors="replace"), False
    except subprocess.TimeoutExpired as exc:
        rc, se, to = None, (exc.stderr or b"").decode(errors="replace"), True
    wall = round(time.monotonic() - t0, 3)
    during = nodes_now()
    new = {k: H.prop_slice(v) for k, v in during.items() if k not in before}
    time.sleep(0.4)
    caps = mon.stop() if mon else {}
    leg = {"label": label, "argv": argv, "device": dev, "rc": rc,
           "stderr": se.strip().splitlines()[:3], "wall_s": wall,
           "timed_out": to, "new_nodes": new,
           "carried": [k for k, v in caps.items()
                       if v["verdict"] in ("mine", "mine_r_tag")],
           "tone_windows": {k: v["mine"] for k, v in caps.items()
                            if v["mine"]},
           "foreign": {k: v["foreign"] for k, v in caps.items()
                       if v["foreign"]}}
    out["legs"].append(leg)
    print(f"{label:22s} rc={str(rc):>4s} wall={wall:5.2f} "
          f"carried={leg['carried']} newnodes={list(new)[:2]} "
          f"err={se.strip().splitlines()[:1]}", flush=True)
    if mon:
        for f in os.listdir(H.RAW):
            if f.startswith("r78pmonD_"):
                os.unlink(os.path.join(H.RAW, f))
    return leg


def dump_params(label, tool, dev, out, file=None):
    argv = [tool, "-D", dev, "--dump-hw-params", file or TINY]
    try:
        p = subprocess.run(argv, capture_output=True, timeout=8)
        rc, se = p.returncode, p.stderr.decode(errors="replace")
    except subprocess.TimeoutExpired as exc:
        rc, se = None, (exc.stderr or b"").decode(errors="replace")
    txt = [l.strip() for l in se.splitlines() if l.strip()]
    out["hw_params"].append({"label": label, "tool": tool, "dev": dev,
                             "rc": rc, "lines": txt[:12]})
    print(f"  hwparams {tool:8s} {label:22s} rc={rc} "
          f"{txt[:3]}", flush=True)


def main():
    out = {"probe": "aplay-device-axis-r78p", "legs": [], "hw_params": [],
           "toolchain": H.toolchain()}
    out["pre_cleanup"] = H.unload_all_mine()
    H.make_tone(TONE, dur=1.2)
    H.make_tone(TINY, dur=0.15, amp=2048)
    out["aplay_L"] = H.sh(["aplay", "-L"], timeout=8)[1].decode()
    out["arecord_L"] = H.sh(["arecord", "-L"], timeout=8)[1].decode()

    for label, args in DEVICES:
        run_aplay(label, args, out, dev=args[-1])

    # format axis, per device (no witnesses except on the accepted PipeWire path)
    for dev in FMT_DEVS:
        for flabel, fargs in FORMATS:
            run_aplay(f"fmt_{dev.replace(':', '_').replace(',', '_')}_{flabel}",
                      ["-D", dev, *fargs], out, dev=dev, witness=False,
                      timeout=6.0)

    for dev in ("hw:0,0", "hw:0,1", "hw:0,2", "hw:0,3", "plughw:0,0",
                "sysdefault", "null", "default", "pipewire"):
        dump_params(dev, "aplay", dev, out)
    for dev in ("hw:0,0", "hw:0,1", "hw:0,2", "hw:0,3", "plughw:0,0",
                "sysdefault", "null", "default", "pipewire"):
        dump_params(dev, "arecord", dev, out)

    # arecord side of the same PCM lattice (same session comparison)
    for label, args in (("arec_hw00_cd", ["-D", "hw:0,0", "-f", "cd"]),
                        ("arec_hw00_dat", ["-D", "hw:0,0", "-f", "dat"]),
                        ("arec_hw00_s16", ["-D", "hw:0,0", "-f", "S16_LE"]),
                        ("arec_hw00_s16_c1", ["-D", "hw:0,0", "-f", "S16_LE",
                                              "-c", "1"]),
                        ("arec_default", ["-D", "default"]),
                        ("arec_pipewire", ["-D", "pipewire"]),
                        ("arec_pulse", ["-D", "pulse"]),
                        ("arec_null", ["-D", "null"])):
        rc, o, e, wall, to = H.sh(["arecord", *args, "-d", "1", "/dev/null"],
                                  timeout=8)
        out["arecord_legs"] = out.get("arecord_legs", [])
        out["arecord_legs"].append({"label": label, "argv": args, "rc": rc,
                                    "wall_s": wall, "timed_out": to,
                                    "stderr": e.strip().splitlines()[:3]})
        print(f"{label:22s} rc={str(rc):>4s} wall={wall:5.2f} "
              f"err={e.strip().splitlines()[:1]}", flush=True)

    # does `-D default` follow the CURRENT default sink?
    def md(name):
        return H.sh(["pw-metadata", "-n", "default", "0", "default.audio.sink",
                     json.dumps({"name": name})], timeout=6)[0]
    try:
        md(H.S_SPDIF)
        time.sleep(0.5)
        run_aplay("default_follow_spdif", ["-D", "default"], out)
        md(H.S_SPK)
        time.sleep(0.8)
        run_aplay("default_follow_spk", ["-D", "default"], out)
        run_aplay("pipewire_follow_spk", ["-D", "pipewire"], out)
    finally:
        md(H.S_SPDIF)
        time.sleep(0.4)
    H.save("probe-aplay-axis-r78p.json", out)


if __name__ == "__main__":
    main()
