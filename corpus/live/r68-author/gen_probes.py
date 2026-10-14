#!/usr/bin/env python3
"""r68 scratch probes: post-table fallback + pipe-refusal member candidates."""
import struct
from pathlib import Path

OUT = Path(__file__).resolve().parent / "probes"
OUT.mkdir(parents=True, exist_ok=True)

# --- no-match member: 512 B, no CHECK row may fire.
# Text prefix keeps every @0 magic dead; explicit pins keep the deeper
# two-conjunct rows dead (byte 256 != 0x84 kills act even though RIFF@0 is
# already absent; no "ring.bin"@16, no FSSD@65+HCOM@128).
b = bytearray(b"ufo-r68 post-table-fallback no-match member: no CHECK row\n")
b.extend((i * 7 + 3) & 0xFF for i in range(len(b), 512))
b[256] = 0x00
(OUT / "nomatch.wav").write_bytes(b)
(OUT / "nomatch_noext").write_bytes(b)          # same bytes, no extension
(OUT / "nomatch.bin").write_bytes(b)            # unregistered extension

# --- txw member: 32-B header + 96 B payload = 128 B.
# WaveHeader_: filetype[6] LM8953 | nulls[10] | dummy_aeg[6] | format@22
# (0xC9 non-looped) | sample_rate@23 (3 -> 16 kHz) | atc_length[3] |
# rpt_length[3] | unused[2]. Reader computes rest = size - 32 = 96 ->
# 32 3-byte groups -> 64 12-bit samples on seekable transports.
t = bytearray(128)
t[0:6] = b"LM8953"
t[22] = 0xC9
t[23] = 3
for i in range(32, 128):
    t[i] = (i * 5 + 1) & 0xFF
(OUT / "txw128.wav").write_bytes(t)

# --- txw 6-B pure-magic variant (file arm -> 'file is truncated')
(OUT / "txw6.wav").write_bytes(b"LM8953")

# --- smp 17-B pure-magic variant (file arm -> 'unexpected EOF in header')
(OUT / "smp17.wav").write_bytes(b"SOUND SAMPLE DATA")
print("wrote", sorted(p.name for p in OUT.iterdir()))
