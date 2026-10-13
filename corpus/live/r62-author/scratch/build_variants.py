#!/usr/bin/env python3
"""R62 scratch: discriminating WAV variants for the SoX/ffmpeg decode-length
UNKNOWN from R61. Each variant changes exactly ONE declared field or the data
extent relative to the round-61 pair_valid_17.wav control. Scratch only."""
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
R61 = HERE.parents[1] / "round-61"
BASE = (R61 / "pair_valid_17.wav").read_bytes()
DATA = BASE[68:]           # 11,520 bytes of signed-16 payload
GUID = bytes.fromhex("0100000000001000800000aa00389b71")
RATE = 48000


def extensible(path, valid, bits, block_align, byte_rate, data, declared=None,
               tag=0xfffe, extra_chunks=b""):
    """WAVE_FORMAT_EXTENSIBLE mono file; declared = data-chunk size field lie."""
    fmt = struct.pack("<HHIIHHHHI", tag, 1, RATE, byte_rate, block_align,
                      bits, 22, valid, 0x4) + GUID
    body = (b"WAVEfmt " + struct.pack("<I", len(fmt)) + fmt + extra_chunks
            + b"data" + struct.pack("<I", len(data) if declared is None else declared)
            + data)
    path.write_bytes(b"RIFF" + struct.pack("<I", len(body)) + body)


def std_pcm(path, bits, block_align, byte_rate, data):
    """Plain PCM tag=1 mono file."""
    fmt = struct.pack("<HHIIHH", 1, 1, RATE, byte_rate, block_align, bits)
    body = (b"WAVEfmt " + struct.pack("<I", len(fmt)) + fmt
            + b"data" + struct.pack("<I", len(data)) + data)
    path.write_bytes(b"RIFF" + struct.pack("<I", len(body)) + body)


out = HERE / "wav"
out.mkdir(exist_ok=True)

# byte-exact control
(out / "ctrl_valid17.wav").write_bytes(BASE)
assert (out / "ctrl_valid17.wav").read_bytes() == BASE

# -- hypothesis 3/4: declared nBlockAlign drives packet cuts (data identical) --
for ba in (1, 3, 4, 5, 6, 8):
    extensible(out / f"ba{ba}_valid17.wav", 17, 16, ba, RATE * ba, DATA)

# -- hypothesis 2/3: valid-bits value -> reclassified sample width ----------
for v in (20, 24, 25, 32, 33, 64):
    extensible(out / f"v{v}.wav", v, 16, 2, RATE * 2, DATA)

# -- packet-tail boundaries: tail remainder behaviour ----------------------
extensible(out / "d8194_valid17.wav", 17, 16, 2, RATE * 2, DATA[:8194])
extensible(out / "d8190_valid17.wav", 17, 16, 2, RATE * 2, DATA[:8190])
extensible(out / "d8196_valid17.wav", 17, 16, 2, RATE * 2, DATA[:8196])
extensible(out / "d11522_valid17.wav", 17, 16, 2, RATE * 2, DATA + b"\x00\x00")
extensible(out / "d11521_valid17.wav", 17, 16, 2, RATE * 2, DATA + b"\x00")

# -- hypothesis 1: declared data size / 'fact' governs extent --------------
extensible(out / "declared_long.wav", 17, 16, 2, RATE * 2, DATA, declared=17280)
extensible(out / "declared_short.wav", 17, 16, 2, RATE * 2, DATA, declared=5766)
fact = b"fact" + struct.pack("<II", 4, 5760)
extensible(out / "fact5760.wav", 17, 16, 2, RATE * 2, DATA, extra_chunks=fact)

# -- true pcm_s24le control: same byte count, codec-native blockAlign=3 ------
pcm24 = bytearray()
for i in range(3840):                       # real 24-bit samples
    v = int(4000000 * __import__("math").sin(2 * 3.141592653589793 * 1050 * i / RATE))
    pcm24 += struct.pack("<i", v)[:3]
std_pcm(out / "pcm24_true.wav", 24, 3, RATE * 3, bytes(pcm24))

# -- legal valid<container in a 32-bit container ----------------------------
data32 = b"".join(struct.pack("<i", v * 65536)
                  for v in struct.unpack("<5760h", DATA))
extensible(out / "v17_c32.wav", 17, 32, 4, RATE * 4, data32)

for p in sorted(out.glob("*.wav")):
    print(f"{p.name}: {p.stat().st_size} bytes")
sys.exit(0)
