#!/usr/bin/env python3
"""r64-boundary: wValidBitsPerSample sweep on the deterministic r63 family.

Base: corpus/live/round-63/pair_route_84.wav — WAVE_FORMAT_EXTENSIBLE,
fmt=40, 16-bit container, cbSize=22, valid=17, mask=4, PCM GUID,
11,520-byte deterministic payload, byte[256]==0x84 (act trigger).

Single-field change: uint16 LE at offset 38 (wValidBitsPerSample).
Every other byte identical -> byte 256 stays 0x84 -> all variants take the
SAME act-forced route (RIFF@0 + 0x84@256, sox_ng formats.c CHECK table).

ff_get_pcm_codec_id(vb, flt=0, be=0, sflags=~1) on n9.0.1 (lavf_utils.c):
  vb<=0 or vb>64 -> NONE ; else w=(vb+7)>>3 ; sflags& (1<<(w-1)) :
    w=1 -> bit0 of ~1 is CLEAR -> unsigned -> PCM_U8
    w=2,3,4,8 -> S16LE,S24LE,S32LE,S64LE ; w=5,6,7 -> NONE
Predicted steps: 0|1, 8|9, 16|17, 24|25, 32|33, 56|57, 64|65.
"""
import os, struct, hashlib

BASE = "/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/round-63/pair_route_84.wav"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "variants")

VALUES = [0, 1, 2, 7, 8, 9, 15, 16, 17, 23, 24, 25, 31, 32, 33, 39, 40, 41,
          47, 48, 49, 55, 56, 57, 58, 63, 64, 65, 66, 80, 96, 127, 128,
          255, 256, 1024, 8192, 32767, 65535]

def main():
    os.makedirs(OUT, exist_ok=True)
    base = open(BASE, "rb").read()
    assert base[256] == 0x84, "act trigger byte moved?"
    assert struct.unpack_from("<H", base, 38)[0] == 17
    rows = []
    for vb in VALUES:
        b = bytearray(base)
        struct.pack_into("<H", b, 38, vb)
        name = f"s_valid_{vb:05d}.wav"
        p = os.path.join(OUT, name)
        open(p, "wb").write(b)
        assert b[256] == 0x84
        rows.append((name, vb, hashlib.sha256(b).hexdigest()))
    with open(os.path.join(OUT, "sweep-shas.txt"), "w") as f:
        for n, v, h in rows:
            f.write(f"{h}  {n}  valid={v}\n")
    print(f"{len(rows)} variants -> {OUT}")

if __name__ == "__main__":
    main()
