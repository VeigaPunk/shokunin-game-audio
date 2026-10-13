#!/usr/bin/env python3
"""r62-simplifier scratch: sweep data-size on the same malformed
WAVE_FORMAT_EXTENSIBLE header (validbits=17, 16-bit container, PCM GUID,
mask 0x4, fmt40/cbSize22) to discriminate the 3839-vs-3840 mechanism."""
import struct, sys, os

RATE = 48000
GUID = bytes.fromhex("0100000000001000800000aa00389b71")

def make(path, data_bytes, valid=17):
    # payload content irrelevant to count; use zeros
    fmt = struct.pack("<HHIIHHHHI", 0xfffe, 1, RATE, RATE*2, 2, 16, 22, valid, 0x4) + GUID
    riff = b"WAVEfmt " + struct.pack("<I", len(fmt)) + fmt + b"data" + struct.pack("<I", data_bytes) + b"\x00" * data_bytes
    with open(path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", len(riff)) + riff)

if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for d in (3, 30, 4095, 4096, 8192, 8196, 11520, 11521, 12288, 16386, 24576):
        make(os.path.join(out, f"sweep_{d}.wav"), d)
    # controls: valid=16 versions at the key sizes (should decode D/2 samples)
    for d in (11520, 12288):
        make(os.path.join(out, f"sweep_v16_{d}.wav"), d, valid=16)
    # also: genuine pcm_s24le file (tag=1? no -- extensible, 24-bit container, validbits=24)
    # to separate "extensible+validbits" from "24-bit decode" as the loss trigger
    for d in (11520, 12288):
        fmt = struct.pack("<HHIIHHHHI", 0xfffe, 1, RATE, RATE*3, 3, 24, 22, 24, 0x4) + GUID
        riff = b"WAVEfmt " + struct.pack("<I", len(fmt)) + fmt + b"data" + struct.pack("<I", d) + b"\x00" * d
        with open(os.path.join(out, f"native24_{d}.wav"), "wb") as f:
            f.write(b"RIFF" + struct.pack("<I", len(riff)) + riff)
    print("wrote", len(os.listdir(out)), "files to", out)
