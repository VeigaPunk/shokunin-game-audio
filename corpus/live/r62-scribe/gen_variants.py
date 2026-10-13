#!/usr/bin/env python3
"""r62-scribe scratch: emit WAVE_FORMAT_EXTENSIBLE variants cloned from the
r61 pair_valid_17.wav header (PCM subtype, mono 48k, fmt40/cbSize22/mask0x4,
16-bit container) varying ONLY data-chunk byte count or wValidBitsPerSample.
Payload is deterministic ASCII-derived bytes (pattern 0..255 cycle); nothing
here touches tracked fixtures."""
import struct, sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "round-61" / "pair_valid_17.wav"
OUT = Path(__file__).resolve().parent / "variants"
OUT.mkdir(exist_ok=True)

hdr = bytearray(SRC.read_bytes()[:68])  # RIFF+WAVE+fmt40+data tag+size
assert hdr[0:4] == b"RIFF" and hdr[12:16] == b"fmt " and hdr[60:64] == b"data"
assert int.from_bytes(hdr[20:22], "little") == 0xFFFE
assert int.from_bytes(hdr[38:40], "little") == 17

def emit(name, data_len, valid_bits):
    h = bytearray(hdr)
    h[4:8] = struct.pack("<I", 60 + data_len)      # RIFF size = 4+ (8+40) + (8+N)
    h[38:40] = struct.pack("<H", valid_bits)       # wValidBitsPerSample
    h[64:68] = struct.pack("<I", data_len)         # data chunk size
    payload = bytes((i * 37 + 11) & 0xFF for i in range(data_len))
    p = OUT / name
    p.write_bytes(bytes(h) + payload)
    return p

# --- size-discriminator set, valid_bits=17 constant ---
# model: demuxer packets = 8192B chunks; decoder emits floor(pkt/3) samples,
# remainder bytes per packet are rejected (observed ffmpeg stderr size2/size1).
sizes = {
    "v17_d24":    24,     # single pkt, 24%3==0  -> 8 samples, 0 err
    "v17_d3840":  3840,   # single pkt, %3==0    -> 1280 exact (kills "always -1")
    "v17_d8190":  8190,   # single pkt, %3==0    -> 2730 exact, 0 err
    "v17_d8194":  8194,   # [8192,2] -> 2730+0 vs global floor 2731 (drop 1, 2 pkts)
    "v17_d11520": 11520,  # r61 shape [8192,3328] -> predict 3839
    "v17_d16386": 16386,  # [8192,8192,2] -> 5460 vs global 5462 (drop 2)
    "v17_d24576": 24576,  # [8192 x3] -> 8190 vs global 8192 (drop 2)
}
for name, n in sizes.items():
    emit(f"{name}.wav", n, 17)

# --- valid-bits sweep, data=11520 constant ---
# if codec is reclassified by valid-bits: <=16->s16le(5760), 17..24->s24le(3839),
# 25..32->s32le(2880 exact, 8192%4==0 -> no drop)
for vb in [0, 8, 15, 16, 17, 18, 20, 23, 24, 25, 31, 32, 33, 40, 255]:
    emit(f"vb{vb}_d11520.wav", 11520, vb)

for p in sorted(OUT.glob("*.wav")):
    print(p.name, p.stat().st_size)
