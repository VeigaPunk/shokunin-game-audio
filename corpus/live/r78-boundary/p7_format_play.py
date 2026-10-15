#!/usr/bin/env python3
"""r78b p7 — format axis on playback: aplay convert-vs-refuse, pw-play
channel/format adaptation, truncated-header playout."""
import os, sys, time, struct, wave, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r78b_lib import *

out = {"probe": "p7-format-play", "ts": time.time(),
       "env": foreign_note()}
out["cleanup"] = unload_all_mine()
make_tone(TONE, dur=1.8)
m1, _, _ = load_null(NS, "r78b probe A")
time.sleep(0.5)

F = {}
def mk(name, dur=1.5, rate=48000, ch=2, width=2):
    p = os.path.join(RAW, name)
    n = int(dur * rate)
    with wave.open(p, "wb") as w:
        w.setnchannels(ch); w.setsampwidth(width); w.setframerate(rate)
        import math as m
        buf = bytearray()
        for i in range(n):
            v = m.sin(2 * m.pi * 1100 * i / rate)
            for c in range(ch):
                vv = v if c < 2 else 0.0
                if width == 2:
                    buf += struct.pack("<h", int(12000 * vv))
                elif width == 1:
                    buf += struct.pack("<B", int(128 + 64 * vv))
                elif width == 3:
                    x = int(12000 * 256 * vv)
                    buf += bytes((x & 0xff, (x >> 8) & 0xff,
                                  (x >> 16) & 0xff))
        w.writeframes(bytes(buf))
    F[name] = p
    return p

mk("f_s16.wav")
mk("f_u8.wav", width=1)
mk("f_s24.wav", width=3)
mk("f_ch6.wav", ch=6)
mk("f_8k.wav", rate=8000, ch=1)
mk("f_96k.wav", rate=96000)
# ffmpeg-generated formats
for name, codec in (("f_f32.wav", "pcm_f32le"), ("f_mulaw.wav", "pcm_mulaw")):
    p = os.path.join(RAW, name)
    r = sh(["ffmpeg", "-y", "-f", "lavfi", "-i",
            "sine=frequency=1100:duration=1.5", "-ac", "2", "-ar", "48000",
            "-c:a", codec, p], timeout=15)
    F[name] = p if r[0] == 0 else f"GENFAIL rc={r[0]}"
# truncated wav: real header claims MORE than present
src = open(F["f_s16.wav"], "rb").read()
tp = os.path.join(RAW, "f_trunc.wav")
i = src.find(b"data")
patched = bytearray(src)
struct.pack_into("<I", patched, i + 4, 0x00FFFFFF)  # claim ~16M data bytes
struct.pack_into("<I", patched, 4, len(src) + 0x00FFF000)
open(tp, "wb").write(bytes(patched[:80000]))         # ~0.4 s of real payload
F["f_trunc.wav"] = tp
# garbage file
gp = os.path.join(RAW, "f_garbage.bin")
open(gp, "wb").write(os.urandom(600))
F["f_garbage.bin"] = gp

legs = {}
def rec(name, argv, timeout=8.0):
    rc, so, se, w, to = sh(argv, timeout=timeout)
    legs[name] = {"argv": argv[0:2] + argv[-2:], "rc": rc,
                  "stderr": se.strip()[:160], "wall": w, "timed_out": to}

# ---- aplay on hw: (conversion vs refusal) -------------------------------
for dev, fn in (("hw:0,0", "f_f32.wav"), ("hw:0,0", "f_s24.wav"),
                ("hw:0,0", "f_u8.wav"), ("hw:0,0", "f_ch6.wav"),
                ("hw:0,0", "f_8k.wav"), ("hw:0,0", "f_96k.wav"),
                ("hw:0,0", "f_mulaw.wav"), ("hw:0,0", "f_trunc.wav"),
                ("hw:0,0", "f_garbage.bin")):
    rec(f"aplay_{dev.replace(':','').replace(',','_')}_{fn}", 
        ["aplay", "-D", dev, "-q", F[fn]])
# plughw contrast on the two most interesting refusals
for fn in ("f_8k.wav", "f_mulaw.wav", "f_ch6.wav"):
    rec(f"aplay_plughw00_{fn}", ["aplay", "-D", "plughw:0,0", "-q", F[fn]])
# plugin-device contrast
rec("aplay_default_f32", ["aplay", "-D", "default", "-q", F["f_f32.wav"]])
rec("aplay_default_8k", ["aplay", "-D", "default", "-q", F["f_8k.wav"]])

# ---- pw-play on the same files ------------------------------------------
for fn in ("f_f32.wav", "f_s24.wav", "f_u8.wav", "f_ch6.wav",
           "f_8k.wav", "f_96k.wav", "f_mulaw.wav", "f_trunc.wav",
           "f_garbage.bin"):
    tag = f"r78bJ_{fn.split('.')[0].split('_')[1]}"
    mon = Monitors(sinks=[("ns", NS)], tag=f"{tag}m")
    legs[f"pwplay_{fn}"] = play_leg(
        ["pw-play", "-P", f"node.name={tag}", "--target", NS, F[fn]],
        tag, timeout=8.0, monitors=mon, tail=0.3)

out["files"] = F
out["legs"] = legs
out["post_cleanup"] = unload_all_mine()
save("probe-p7-format-play-r78b.json", out)
for k, l in legs.items():
    extra = ""
    if "pwplay" in k:
        extra = f"carried={l['carried']} links={json.dumps(l['mid'].get('links'))[:90]}"
    print(f"{k:34s} rc={l['rc']} wall={l['wall']} to={l['timed_out']} "
          f"{extra} err={l['stderr'][:70]!r}")
