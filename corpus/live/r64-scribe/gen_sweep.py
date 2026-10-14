#!/usr/bin/env python3
"""r64-scribe scratch: WAVE_FORMAT_EXTENSIBLE wValidBitsPerSample sweep.

Clones the r61 pair_valid_17.wav fixture byte-for-byte (PCM subtype, mono
48 kHz, fmt40/cbSize22/mask0x4, 16-bit container, data=11,520 B) so the
payload — and therefore file offset 256 = 0x84 (act autodetect trigger,
r63-pinned predicate RIFF && file[256]==0x84) — is identical across the
sweep. Only byte 38:40 (wValidBitsPerSample) varies on the c16 set.

Attribution controls (`c24`/`c32` sets) additionally rewrite the container
width fields — bits/sample (34:36), block align (36:38), byte rate
(28:32) — while keeping the same payload bytes, to separate
valid-bits-keyed reclassification from container-keyed classification.

Nothing here touches tracked fixtures; all output lands under
corpus/live/r64-scribe/variants/.
"""
import struct
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "round-61" / "pair_valid_17.wav"
OUT = Path(__file__).resolve().parent / "variants"
OUT.mkdir(exist_ok=True)

raw = SRC.read_bytes()
hdr = bytearray(raw[:68])
payload = raw[68:]

# --- fixture shape assertions (fail loud, not silent, on a moved fixture) ---
assert hdr[0:4] == b"RIFF" and hdr[12:16] == b"fmt " and hdr[60:64] == b"data"
assert int.from_bytes(hdr[20:22], "little") == 0xFFFE          # extensible
assert int.from_bytes(hdr[22:24], "little") == 1               # mono
assert int.from_bytes(hdr[24:28], "little") == 48000
assert int.from_bytes(hdr[34:36], "little") == 16              # container bits
assert int.from_bytes(hdr[38:40], "little") == 17              # vb (r61 pair)
assert int.from_bytes(hdr[64:68], "little") == 11520
assert len(payload) == 11520 and payload[188] == 0x84          # file[256]


def emit(name, valid_bits, container_bits=16):
    h = bytearray(hdr)
    h[38:40] = struct.pack("<H", valid_bits)                   # byte 38: vb
    if container_bits != 16:
        h[34:36] = struct.pack("<H", container_bits)           # bits/sample
        h[32:34] = struct.pack("<H", container_bits // 8)      # nBlockAlign
        h[28:32] = struct.pack("<I", 48000 * container_bits // 8)  # byte rate
        # cbSize (36:38) stays 22 — extension must still parse to vb
    p = OUT / name
    p.write_bytes(bytes(h) + payload)
    return p


made = []

# --- primary sweep: 16-bit container, vb exhaustive 0..64 + upper probes ---
for vb in list(range(0, 65)) + [65, 100, 128, 200, 255]:
    made.append(emit(f"vb{vb:03d}_c16.wav", vb, 16))

# --- attribution controls: same payload, other container widths ---
for vb in [0, 8, 17, 24, 32, 57, 64, 255]:
    made.append(emit(f"vb{vb:03d}_c32.wav", vb, 32))
for vb in [0, 17, 64]:
    made.append(emit(f"vb{vb:03d}_c24.wav", vb, 24))

for p in made:
    b = p.read_bytes()
    assert b[256] == 0x84, p  # act trigger intact on every variant
    print(p.name, p.stat().st_size)
