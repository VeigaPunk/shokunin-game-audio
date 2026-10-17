#!/usr/bin/env python3
"""r74-scout: hand-build minimal iss / apc / acm members (no ffmpeg muxer
exists for these three on this host: ffmpeg n9.0.1 has demuxers only).

Byte layouts derived from upstream libavformat/{iss,apc,acm}.c +
libavcodec/interplayacm.c (fetched master, labelled inference; validated
empirically against the LOCAL ffmpeg n9.0.1 / ffprobe in validate_members.sh).

Payloads are deterministic (fixed LCG), never zeros, so a decoded output
cannot be confused with an empty/silent decode.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent / "members"
OUT.mkdir(exist_ok=True)


def prng(n, seed=0x1234):
    out = bytearray()
    x = seed
    for _ in range(n):
        x = (1103515245 * x + 12345) & 0x7FFFFFFF
        out.append((x >> 16) & 0xFF)
    return bytes(out)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


manifest = {}


def build_iss(name, packet_size, packets):
    # iss.c: tokens space-separated, get_token stops at NUL and then consumes
    # ONE more byte; then data starts (sample_start_pos).
    # tokens: magic, packet_size, file_id, out_size, stereo, unknown1,
    #         rate_divisor, unknown2, version, size
    # adpcm.c AV_CODEC_ID_ADPCM_IMA_ISS: each packet (block_align =
    # packet_size) starts with 4*ch bytes: predictor LE16 + step_index LE16
    # (must be <= 88, else the decoder errors). Nibble body after that.
    hdr = ("IMA_ADPCM_Sound %d 0 %d 0 0 1 0 0 0"
           % (packet_size, packet_size * packets)).encode()
    body = b""
    for pk in range(packets):
        body += b"\x00\x00" + b"\x00\x00"          # predictor 0, step_index 0
        body += prng(packet_size - 4, seed=0x155 + pk)
    data = hdr + b"\x00" + b"\x00" + body   # NUL terminator + 1 consumed pad
    p = OUT / name
    p.write_bytes(data)
    manifest[name] = {
        "bytes": len(data), "sha256": sha(p),
        "layout": ("iss text header (10 tokens) + NUL + 1 pad byte; "
                   "%d packet(s) x (4B IMA header [pred=0, step=0] + "
                   "%d B LCG nibbles)"
                   % (packets, packet_size - 4)),
        "header_len": len(hdr) + 2,
    }


def build_apc(name, payload_len):
    # apc.c: rl32 'CRYO' rl32 '_APC' rl32 '1.20' rl32 nsamples rl32 rate
    # 8B extradata (initial predictors) rl32 channels_flag -> 32 B header
    hdr = b"CRYO_APC" + b"1.20"
    hdr += struct.pack("<I", payload_len // 2)      # number of samples
    hdr += struct.pack("<I", 8000)                  # sample_rate
    hdr += bytes([0, 0, 0, 0, 0, 0, 0, 0])          # 8 B extradata
    hdr += struct.pack("<I", 0)                     # channels flag: 0 -> 1ch
    body = prng(payload_len, seed=0x2a9)
    data = hdr + body
    p = OUT / name
    p.write_bytes(data)
    manifest[name] = {
        "bytes": len(data), "sha256": sha(p),
        "layout": ("apc 32 B header (CRYO_APC 1.20 + nsamples + rate 8000 + "
                   "8B extradata + channels=0) + %d B LCG payload"
                   % payload_len),
        "header_len": 32,
    }


class BitWriter:
    """LSB-first bit packer (codec uses BITSTREAM_READER_LE)."""

    def __init__(self):
        self.bits = []

    def put(self, value, n):
        for i in range(n):
            self.bits.append((value >> i) & 1)

    def bytes(self):
        out = bytearray((len(self.bits) + 7) // 8)
        for i, b in enumerate(self.bits):
            out[i // 8] |= b << (i % 8)
        return bytes(out)


def build_acm(name, blocks, level=0, rows=8, sr=8000):
    # acm.c: ff_get_extradata(pb, 14) runs from the CURRENT position with NO
    # magic skip -> the 14 B extradata INCLUDES the magic (measured: an
    # 18-byte variant with a separate magic fails read_header with
    # INVALIDDATA on local n9.0.1). So: [0..4) magic RB32 0x97280301,
    # [4..8) nsamples LE32, [8..10) channels LE16, [10..12) sample_rate
    # LE16, [12..14) (rows<<4)|level LE16; data at 14.
    # interplayacm.c: cols=1<<level, block_len=rows*cols bytes buffered before
    # each frame; block bitstream: 4b pwr + 16b val, then per column a 5b
    # filler index; filler linear(ind) reads `ind` bits per row.
    cols = 1 << level
    bw = BitWriter()
    for _ in range(blocks):
        bw.put(0, 4)      # pwr = 0
        bw.put(0, 16)     # val = 0
        for _c in range(cols):
            bw.put(3, 5)  # filler index 3 = linear
            for _r in range(rows):
                bw.put(3, 3)  # b=3 -> sample b-4 = -1
    stream = bw.bytes()
    hdr = struct.pack(">I", 0x97280301)             # magic [0..4)
    hdr += struct.pack("<I", rows * blocks)         # nsamples [4..8)
    hdr += struct.pack("<H", 1)                     # channels [8..10)
    hdr += struct.pack("<H", sr)                    # sample_rate [10..12)
    hdr += struct.pack("<H", (rows << 4) | level)   # rows<<4 | level [12..14)
    data = hdr + stream
    p = OUT / name
    p.write_bytes(data)
    manifest[name] = {
        "bytes": len(data), "sha256": sha(p),
        "layout": ("acm 14 B header (magic + nsamples + channels + rate + "
                   "rows<<4|level) + %d blocks x (4b pwr +16b val + cols*(5b "
                   "filler + rows*3b)) level=%d rows=%d cols=%d sr=%d; "
                   "block_len=%d B; bitstream=%d B"
                   % (blocks, level, rows, cols, sr, rows * cols, len(stream))),
        "header_len": 14,
        "block_bits": 20 + cols * (5 + rows * 3),
    }


def main():
    build_iss("sweep_iss_1pkt.iss", 256, 1)
    build_iss("sweep_iss_4pkt.iss", 256, 4)
    build_iss("sweep_iss_40pkt.iss", 256, 40)
    build_apc("sweep_apc_1pkt.apc", 512)
    build_apc("sweep_apc_multi.apc", 8192)
    build_apc("sweep_apc_3pkt.apc", 12288)
    build_acm("sweep_acm_64blk.acm", 64)
    build_acm("sweep_acm_2000blk.acm", 2000)
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    for k, v in manifest.items():
        print("%-24s %6d B  %s  %s" % (k, v["bytes"], v["sha256"][:16],
                                       v["layout"][:60]))


if __name__ == "__main__":
    sys.exit(main())
