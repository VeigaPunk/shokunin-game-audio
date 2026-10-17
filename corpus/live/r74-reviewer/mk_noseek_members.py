#!/usr/bin/env python3
"""r74 reviewer — independent minimal no-seek member builder.

Built from the demuxer source (fetched FFmpeg master iss.c/apc.c/acm.c +
libavcodec/interplayacm.c) — NOT from the author's generator, so a replay
on these members is an independent check of the fork mechanism.

Members (all mono, 44100 Hz unless noted):
  my_iss_multi.iss  : ASCII token header, 6 x 512-byte packets (multi-packet)
  my_iss_one.iss    : 1 x 512-byte packet (single-packet control)
  my_apc_multi.apc  : 32-byte header, 5120-byte payload (>4096 => multi-packet)
  my_acm_multi.acm  : 18-byte header, 400-byte payload (4-byte ACM frames)
"""
import struct
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent


def iss(packet_size, n_packets, name):
    """Funcom ISS: space-separated ASCII tokens, then packets of exactly
    packet_size bytes (iss_read_packet errors on a short packet)."""
    hdr = " ".join(["IMA_ADPCM_Sound", str(packet_size), "1", str(packet_size * n_packets),
                    "0", "0", "1", "0", "1", str(n_packets)]) + " "
    # packet payload: predictor=0, step_index=0, then zero nibbles
    payload = b"\x00" * (packet_size * n_packets)
    p = OUT / name
    p.write_bytes(hdr.encode() + payload)
    return p


def apc(n_samples, name):
    """CRYO APC: 'CRYO'+'_APC'+'1.20', u32 samples, u32 rate, 8B extradata,
    u32 channels flag (0=mono), payload (demuxer reads <=4096 B/packet)."""
    hdr = b"CRYO" + b"_APC" + b"1.20"
    hdr += struct.pack("<II", n_samples, 44100)
    hdr += b"\x00" * 8
    hdr += struct.pack("<I", 0)          # mono
    p = OUT / name
    p.write_bytes(hdr + b"\x00" * 5120)
    return p


def acm(n_samples, name):
    """Interplay ACM: the demuxer's 14-byte extradata INCLUDES the magic
    (acm_read_header does not skip it) — measured by reviewer bisection:
    file = magic(4) | samples u32 | channels u16 | rate u16 | subformat u16.
    subformat 0x7700 -> level=0 rows=0x77 -> 119-byte all-zero frames."""
    hdr = bytes((0x97, 0x28, 0x03, 0x01))
    hdr += struct.pack("<I", n_samples)
    hdr += struct.pack("<H", 1)          # channels
    hdr += struct.pack("<H", 44100)      # rate
    hdr += struct.pack("<H", 0x7700)     # subformat: level 0, rows 0x77
    assert len(hdr) == 14
    p = OUT / name
    p.write_bytes(hdr + b"\x00" * 2380)  # 20 frames x 119 B
    return p


if __name__ == "__main__":
    made = [
        iss(512, 6, "my_iss_multi.iss"),
        iss(512, 1, "my_iss_one.iss"),
        apc(5120, "my_apc_multi.apc"),
        acm(400, "my_acm_multi.acm"),
    ]
    for p in made:
        print(p, p.stat().st_size)
    sys.exit(0)
