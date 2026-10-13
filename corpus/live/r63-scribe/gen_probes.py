#!/usr/bin/env python3
"""r63-scribe: single-byte-mutated variants of r61 pair_valid_{17,16}.wav.

Pins the SoX_ng `act` autodetect predicate. Base fixtures (r61, SHAs verified
2026-10-13): pair_valid_17.wav byte256==0x84 -> 'act' -> (ffmpeg) bridge;
pair_valid_16.wav identical except byte38 (valid-bits 16 vs 17).
"""
import os, sys

BASE = "/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-61"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "variants")
os.makedirs(OUT, exist_ok=True)

v17 = open(os.path.join(BASE, "pair_valid_17.wav"), "rb").read()
v16 = open(os.path.join(BASE, "pair_valid_16.wav"), "rb").read()
assert len(v17) == len(v16) == 11588, (len(v17), len(v16))
assert v17[256] == 0x84 and v16[256] == 0x84
assert v17[38] == 0x11 and v16[38] == 0x10

made = []
def w(name, buf):
    p = os.path.join(OUT, name)
    open(p, "wb").write(buf)
    made.append(name)

# --- 1. value sweep at file offset 256 on the real v17 payload (256 files) ---
for val in range(256):
    b = bytearray(v17); b[256] = val
    w(f"v17_b256_{val:02x}.wav", b)

# --- 2. position sweep: move the 0x84 to other offsets (byte256 cleared) ---
for off in (12, 64, 100, 128, 188, 255, 257, 258, 300, 511, 512, 1024,
            2048, 4096, 8192, 11587):
    b = bytearray(v17); b[256] = 0x00; b[off] = 0x84
    w(f"v17_off{off:05d}_84.wav", b)
# flanking / double-hit controls
b = bytearray(v17); b[255] = 0x84                      # 0x84 at 255 AND 256
w("v17_off255+256.wav", b)
b = bytearray(v17); b[256] = 0x00; b[255] = 0x84; b[257] = 0x84  # flanked, 256 clear
w("v17_off255+257_no256.wav", b)

# --- 3. length guard (AUTO_DETECT_SIZE=257) ---
for n in (256, 257, 258):
    w(f"v17_trunc{n}.wav", v17[:n])
b = bytearray(v17[:257]); b[256] = 0x00                # 257 B, trigger byte cleared
w("v17_trunc257_b256_00.wav", b)

# --- 4. conjunction: RIFF@0 is required; WAVE@8 is NOT (for act) ---
b = bytearray(v17); b[0] = ord('X')                    # XIFF..., 0x84@256 kept
w("v17_xiff.wav", b)
b = bytearray(v17); b[0:4] = b"RIFX"                   # RIFX big-endian magic
w("v17_rifx.wav", b)
b = bytearray(v17); b[8:12] = b"\x00\x00\x00\x00"      # RIFF + no WAVE + 0x84@256
w("v17_nowave.wav", b)
b = bytearray(v17); b[8:12] = b"\x00\x00\x00\x00"; b[256] = 0x00
w("v17_nowave_b256_00.wav", b)

# --- 5. no-fallback probe: act detected, ffmpeg child decodes nothing ---
b = bytearray(v17); b[38] = 0x21                       # wValidBitsPerSample=33 -> codec unknown
w("v17_vb33.wav", b)

# --- 6. earlier-row preemption: hcom CHECK (FSSD@65,HCOM@128) precedes act ---
b = bytearray(v17); b[65:69] = b"FSSD"; b[128:132] = b"HCOM"
w("v17_hcom.wav", b)

# --- 7. v16 controls + extension (non-.wav name) ---
w("v16_b256_84.wav", v16)                              # v16 keeps 0x84@256
b = bytearray(v16); b[256] = 0x00
w("v16_b256_00.wav", b)
w("v17_act.bin", v17)                                  # unknown extension, 0x84@256
b = bytearray(v17); b[256] = 0x00
w("v17_wav.bin", b)                                    # unknown ext, RIFF+WAVE, no trigger
b = bytearray(v17); b[0] = ord('X'); b[256] = 0x00
w("v17_xiff_nowav.bin", b)                             # no magic match, unknown ext
print(f"{len(made)} variants written to {OUT}")
