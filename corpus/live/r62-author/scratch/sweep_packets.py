#!/usr/bin/env python3
"""Map ffmpeg wavdec packetization: f(block_align) and f(data_size)."""
import struct
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = (HERE.parents[1] / "round-61" / "pair_valid_17.wav").read_bytes()
DATA = BASE[68:]
GUID = bytes.fromhex("0100000000001000800000aa00389b71")
RATE = 48000
out = HERE / "sweep"
out.mkdir(exist_ok=True)


def build(path, ba, nbytes):
    fmt = struct.pack("<HHIIHHHHI", 0xfffe, 1, RATE, RATE * ba, ba, 16,
                      22, 17, 0x4) + GUID
    data = DATA[:nbytes] if nbytes <= len(DATA) else DATA + bytes(nbytes - len(DATA))
    body = (b"WAVEfmt " + struct.pack("<I", len(fmt)) + fmt
            + b"data" + struct.pack("<I", len(data)) + data)
    path.write_bytes(b"RIFF" + struct.pack("<I", len(body)) + body)


def packets(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "packet=size", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    return [int(x.split(",")[-1]) for x in r.stdout.split() if x.strip()]


for ba in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 16, 4096, 8192, 16384):
    p = out / f"ba{ba}.wav"
    build(p, ba, 11520)
    print(f"ba={ba:>5}  packets={packets(p)}")

for d in (4096, 8192, 8194, 11520, 16384, 23040, 40960):
    for ba in (2, 3, 5):
        p = out / f"d{d}_ba{ba}.wav"
        build(p, ba, d)
        print(f"d={d:>5} ba={ba}  packets={packets(p)}")
