#!/usr/bin/env python3
"""r74 BOUNDARY scratch — hand-built iss/apc/acm members + malformed/partial edge variants.

Scratch only (corpus/live/r74-boundary/), NOT tracked evidence.

Layouts derived from FFmpeg source (read this seat, master @ fetch time):
- libavformat/iss.c  : probe strncmp(buf,"IMA_ADPCM_Sound",15)==0 -> score 100;
  header = 10 space/NUL-separated tokens (packet_size,file_id,out_size,stereo,
  unk1,rate_divisor,unk2,version,size); packet_size<=0 -> INVALIDDATA;
  read_packet: av_get_packet(packet_size) must return exactly packet_size.
- libavformat/apc.c  : probe strncmp(buf,"CRYO_APC",8)==0 -> score 100;
  header = "CRYO"+"_APC"+"1.20" + u32le nsamples + u32le rate + 8B predictor
  extradata + u32le chflag(+1 channels); NO validation of rate/channels.
- libavformat/acm.c  : probe AV_RB32(buf)==0x97280301 -> score 66;
  +14B extradata: [4..7]=max_samples u32le, [8..9]=channels u16le,
  [10..11]=rate u16le, [12..13]=u16le(level=low nibble, rows=high nibble);
  channels<=0 or rate<=0 -> INVALIDDATA; flags NOBYTE/NOGEN/NO_BYTE_SEEK.
- libavcodec/interplayacm.c: frame = rows*cols bytes (cols=1<<level); all-zero
  frame decodes as silence (pwr=0,val=0,filler_list[0]=zero, level=0 skips juggle).
"""
import hashlib
import json
import struct
from pathlib import Path

SCRATCH = Path(__file__).resolve().parent
MEM = SCRATCH / "members"
MEM.mkdir(exist_ok=True)

ISS_HDR = (b"IMA_ADPCM_Sound 512 0 0 0 0 1 0 0 0 ")   # 10 tokens, trailing space
APC_HDR_PREFIX = b"CRYO_APC1.20"


def iss(packet_size=512, stereo=0, rate_divisor=1, data=b"\x00" * (40 * 512),
        hdr=None, trailing=True):
    if hdr is None:
        hdr = (b"IMA_ADPCM_Sound %d 0 0 %d 0 %d 0 0 0 " % (packet_size, stereo,
                                                             rate_divisor))
    return hdr + data


def apc(nsamples=0, rate=22050, pred=b"\x00" * 8, chflag=0, data=b"\x00" * 4096,
        prefix=APC_HDR_PREFIX, tail=True):
    b = prefix + struct.pack("<I", nsamples) + struct.pack("<I", rate) + pred + \
        struct.pack("<I", chflag)
    return b + data if tail else b


def acm(max_samples=0, channels=1, rate=22050, level=0, rows=32,
        frames=350, data=None, magic=bytes([0x97, 0x28, 0x03, 0x01])):
    # NOTE: ff_get_extradata(...,14) reads from file offset 0 (magic included),
    # so file layout = magic(4) + max_samples u32le + ch u16le + rate u16le +
    # (rows<<4|level) u16le, data at offset 14.  (first build had an extra u32
    # at offset 4 -> ffmpeg INVALIDDATA; corrected this seat.)
    u16 = (rows << 4) | level
    hdr = magic + struct.pack("<I", max_samples) + \
        struct.pack("<H", channels) + struct.pack("<H", rate) + \
        struct.pack("<H", u16)
    if data is None:
        data = b"\x00" * (rows * (1 << level) * frames)
    return hdr + data


def build():
    out = {}

    # ---- valid controls (multi-packet) ----
    out["iss_valid"] = iss()
    out["apc_valid"] = apc()
    out["acm_valid"] = acm()

    # ---- ISS malformed ----
    out["iss_magic_bad"] = b"IMA_ADPCM_SounX 512 0 0 0 0 1 0 0 0 " + b"\x00" * 2048
    out["iss_magic_trunc"] = b"IMA_ADPC"                     # 8B only
    out["iss_hdr_2tok"] = b"IMA_ADPCM_Sound 512 "            # 2 tokens, then EOF
    out["iss_pkt_zero"] = iss(packet_size=0)
    out["iss_pkt_neg"] = iss(packet_size=-512)
    out["iss_pkt_nan"] = iss(hdr=b"IMA_ADPCM_Sound abc 0 0 0 0 1 0 0 0 ")
    out["iss_pkt_huge"] = iss(packet_size=100000000,
                              data=b"\x00" * 512)            # < one packet of data
    out["iss_stereo1"] = iss(stereo=1)                       # 2ch control

    # ---- ISS partial (truncate valid member) ----
    valid = out["iss_valid"]
    out["iss_partial_0pkt"] = valid[:len(ISS_HDR)]            # header only
    out["iss_partial_halfpkt"] = valid[:len(ISS_HDR) + 256]   # 0.5 packet
    out["iss_partial_1pkt"] = valid[:len(ISS_HDR) + 512]      # 1 packet
    out["iss_partial_1p5pkt"] = valid[:len(ISS_HDR) + 768]    # 1.5 packets

    # ---- APC malformed ----
    out["apc_magic_bad"] = apc(prefix=b"CRYO_APX1.20")
    out["apc_hdr_trunc8"] = b"CRYO_APC"                       # 8B only
    out["apc_hdr_trunc20"] = APC_HDR_PREFIX + b"\x00" * 8      # 20B only
    out["apc_rate_zero"] = apc(rate=0)
    out["apc_rate_huge"] = apc(rate=0xFFFFFFFF)
    out["apc_nodata"] = apc(data=b"")
    out["apc_stereo"] = apc(chflag=1)                         # 2ch control

    # ---- APC partial ----
    av = out["apc_valid"]
    out["apc_partial_0data"] = av[:len(av) - 4096]
    out["apc_partial_100"] = av[:len(av) - 4096 + 100]

    # ---- ACM malformed ----
    out["acm_magic_bad"] = acm(magic=bytes([0x96, 0x28, 0x03, 0x01]))
    out["acm_hdr_trunc10"] = bytes([0x97, 0x28, 0x03, 0x01]) + b"\x00" * 6
    out["acm_ch_zero"] = acm(channels=0)
    out["acm_rate_zero"] = acm(rate=0)
    out["acm_rows0"] = acm(rows=0, data=b"\x00" * 1024)       # block_len=0
    out["acm_level4"] = acm(level=4, rows=2, frames=200)      # cols=16, blk=32
    out["acm_nodata"] = acm(data=b"")

    # ---- ACM partial ----
    cv = out["acm_valid"]
    out["acm_partial_0data"] = cv[:14]
    out["acm_partial_20"] = cv[:14 + 20]                      # < one 32B frame
    out["acm_partial_1frame"] = cv[:14 + 32]
    out["acm_partial_1frame5"] = cv[:14 + 48]

    hashes = {}
    for name, blob in out.items():
        p = MEM / name
        p.write_bytes(blob)
        hashes[name] = {"file": p.name, "bytes": len(blob),
                        "sha256": hashlib.sha256(blob).hexdigest()}
    (MEM / "manifest.json").write_text(json.dumps(hashes, indent=1, sort_keys=True))
    print(json.dumps(hashes, indent=1, sort_keys=True))


if __name__ == "__main__":
    build()
