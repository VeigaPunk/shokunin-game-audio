#!/usr/bin/env python3
"""r62 scout scratch: synthetic WAVE_FORMAT_EXTENSIBLE valid17 files with varying
data-chunk sizes, to discriminate packet-boundary remainder-drop (H1) vs
one-frame-dropped-at-EOF (H3). Same header shape as round-61 builder
(build_artifacts.py:192-201); payload = i%256 ramp bytes (content irrelevant,
only decode length is measured)."""
import struct
from pathlib import Path

OUT = Path(__file__).resolve().parent
GUID = bytes.fromhex("0100000000001000800000aa00389b71")
RATE = 48000

def write_valid17(path, nbytes):
    fmt = struct.pack("<HHIIHHHHI", 0xfffe, 1, RATE, RATE * 2, 2, 16, 22, 17, 0x4) + GUID
    data = bytes(i % 256 for i in range(nbytes))
    riff = b"WAVEfmt " + struct.pack("<I", len(fmt)) + fmt + b"data" + struct.pack("<I", len(data)) + data
    path.write_bytes(b"RIFF" + struct.pack("<I", len(riff)) + riff)

# N -> (H1 packet-floor prediction, H3 eof-drop prediction)
CASES = {
    11520: (8192 // 3 + 3328 // 3, 11520 // 3 - 1),          # repro: 3839 vs 3839
    8190:  (8190 // 3, 8190 // 3 - 1),                        # H1 2730 vs H3 2729
    8193:  (8192 // 3 + 1 // 3, 8193 // 3 - 1),               # H1 2730 vs H3 2730 (non-disc.)
    12289: (8192 // 3 + 4097 // 3, 12289 // 3 - 1),           # H1 4095 vs H3 4095 (non-disc.)
    24576: (3 * (8192 // 3), 24576 // 3 - 1),                 # H1 8190 vs H3 8191  <-- key
    16383: (8192 // 3 + 8191 // 3, 16383 // 3 - 1),           # H1 5460 vs H3 5460 (non-disc.)
}
for n, (h1, h3) in CASES.items():
    p = OUT / f"ctrl_v17_data{n}.wav"
    write_valid17(p, n)
    print(f"{p.name}: bytes={p.stat().st_size} H1_pred={h1} H3_pred={h3}")
