#!/usr/bin/env python3
"""r74 author scratch member builder — lavf no-seek demuxer family."""
import struct, subprocess, sys
from pathlib import Path
OUT = Path(__file__).resolve().parent / "members"

def iss(packet_size, n_packets, name):
    # Funcom ISS: space-separated ASCII tokens then n_packets*packet_size
    # bytes. iss_read_packet requires each read == packet_size.
    hdr = " ".join(["IMA_ADPCM_Sound", str(packet_size), "0",
                    str(packet_size * n_packets), "0", "0", "1", "0", "1",
                    str(packet_size * n_packets)]) + " "
    p = OUT / name
    p.write_bytes(hdr.encode() + b"\x00" * (packet_size * n_packets))
    return p

def apc(n_samples, rate, payload_len, name):
    # CRYO APC: 'CRYO_APC' + '1.20' + u32 samples + u32 rate + 8B extradata
    # + u32 stereo-flag, then adpcm payload (demuxer: <=4096 B per packet).
    hdr = b"CRYO_APC" + b"1.20"
    hdr += struct.pack("<II", n_samples, rate)
    hdr += b"\x00" * 8
    hdr += struct.pack("<I", 0)
    p = OUT / name
    p.write_bytes(hdr + b"\x00" * payload_len)
    return p

def acm(n_samples, name):
    # Interplay ACM: 14-B extradata INCLUDES the BE magic 0x97280301.
    # u32LE samples | u16LE channels | u16LE rate | u16LE subformat.
    # subformat 0x7700 -> level 0 / rows 0x77 -> 119-byte all-zero frames
    # decode as silence through interplayacm (reviewer-bisected recipe).
    hdr = bytes((0x97, 0x28, 0x03, 0x01))
    hdr += struct.pack("<I", n_samples)
    hdr += struct.pack("<H", 1)
    hdr += struct.pack("<H", 44100)
    hdr += struct.pack("<H", 0x7700)
    assert len(hdr) == 14
    p = OUT / name
    p.write_bytes(hdr + b"\x00" * 2380)   # 20 frames x 119 B
    return p

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    made = [iss(256, 2, "lavf_iss.iss"),
            iss(512, 256, "lavf_iss_multi.iss"),
            apc(5120, 44100, 5120, "lavf_apc.apc"),
            acm(400, "lavf_acm.acm")]
    subprocess.run(["ffmpeg", "-hide_banner", "-y", "-f", "lavfi", "-i",
                    "sine=frequency=440:sample_rate=44100:duration=0.5",
                    "-ac", "1", "-c:a", "adpcm_adx", str(OUT / "lavf_adx.adx")],
                   check=True, capture_output=True)
    made.append(OUT / "lavf_adx.adx")
    subprocess.run(["ffmpeg", "-hide_banner", "-y", "-f", "lavfi", "-i",
                    "sine=frequency=440:sample_rate=44100:duration=0.5",
                    "-ac", "1", "-c:a", "pcm_s16be", str(OUT / "lavf_aifc.aifc")],
                   check=True, capture_output=True)
    made.append(OUT / "lavf_aifc.aifc")
    for p in made:
        print(p.name, p.stat().st_size)
