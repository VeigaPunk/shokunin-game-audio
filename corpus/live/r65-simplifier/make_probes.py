#!/usr/bin/env python3
"""r65-simplifier independent probes: RIFF+0x84@256 x preemptor ordering.

Base: tracked corpus/live/round-63/pair_route_84.wav (11,588 B,
RIFF@0, file[256]==0x84, valid17 extensible header -> decodes only via
the act/ffmpeg bridge). Also minimal 257-B shells for geometry checks.

act : len>=257 AND file[0:4]=="RIFF" AND file[256]==0x84   (formats.c:93)
gsrt: len>=25  AND file[16:25]=="ring.bin\\0"              (r63: CHECK :81)
hcom: len>=132 AND file[65:69]=="FSSD" AND file[128:132]=="HCOM"  (:90)
"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "probes"
BASE = ROOT.parent / "round-63" / "pair_route_84.wav"

def patch(base: bytes, edits=None, spans=None) -> bytearray:
    b = bytearray(base)
    for off, val in (edits or {}).items():
        b[off] = val
    for off, blob in (spans or {}).items():
        b[off:off + len(blob)] = blob
    return b

def minimal(length: int, spans) -> bytearray:
    b = bytearray(length)
    b[0:4] = b"RIFF"
    b[4:8] = (length - 8).to_bytes(4, "little")
    for off, blob in spans.items():
        b[off:off + len(blob)] = blob
    return b

base = BASE.read_bytes()
assert base[0:4] == b"RIFF" and base[256] == 0x84 and len(base) == 11588

probes = {
    # --- pair-family collisions -------------------------------------
    "s_act_base.wav":        patch(base),                                            # control
    "s_gsrt_act.wav":        patch(base, spans={16: b"ring.bin\x00"}),
    "s_hcom_act.wav":        patch(base, spans={65: b"FSSD", 128: b"HCOM"}),
    "s_gsrt_hcom_act.wav":   patch(base, spans={16: b"ring.bin\x00", 65: b"FSSD", 128: b"HCOM"}),
    # --- conjunct integrity ------------------------------------------
    "s_gsrt_nonul.wav":      patch(base, spans={16: b"ring.bin\x01"}),               # last sig byte 0x01
    "s_gsrt_short8.wav":     patch(base, spans={16: b"ring.bin"}),                   # 8B only, no NUL term
    "s_hcom_fssd_only.wav":  patch(base, spans={65: b"FSSD"}),
    "s_hcom_hcom_only.wav":  patch(base, spans={128: b"HCOM"}),
    # --- adjacent-boundary bytes --------------------------------------
    "s_gsrt_off15.wav":      patch(base, spans={15: b"ring.bin\x00"}),               # sig at 15 -> not gsrt
    "s_gsrt_off17.wav":      patch(base, spans={17: b"ring.bin\x00"}),               # sig at 17 -> not gsrt
    "s_hcom_fssd64.wav":     patch(base, spans={64: b"FSSD", 128: b"HCOM"}),         # FSSD off by -1
    "s_hcom_fssd66.wav":     patch(base, spans={66: b"FSSD", 128: b"HCOM"}),         # FSSD off by +1
    "s_hcom_hcom127.wav":    patch(base, spans={65: b"FSSD", 127: b"HCOM"}),         # HCOM off by -1
    "s_hcom_hcom129.wav":    patch(base, spans={65: b"FSSD", 129: b"HCOM"}),         # HCOM off by +1
    # --- act-byte adjacency on a preemptor-shaped file -----------------
    "s_gsrt_act83.wav":      patch(base, {256: 0x83}, {16: b"ring.bin\x00"}),        # gsrt + act-miss below
    "s_gsrt_act85.wav":      patch(base, {256: 0x85}, {16: b"ring.bin\x00"}),        # gsrt + act-miss above
    "s_hcom_act00.wav":      patch(base, {256: 0x00}, {65: b"FSSD", 128: b"HCOM"}),  # hcom, no act byte
    # --- minimal 257-B shells -----------------------------------------
    "m_act.wav":             minimal(257, {8: b"WAVE", 256: b"\x84"}),
    "m_gsrt_act.bin":        minimal(257, {16: b"ring.bin\x00", 256: b"\x84"}),
    "m_hcom_act.bin":        minimal(257, {65: b"FSSD", 128: b"HCOM", 256: b"\x84"}),
    "m_256_gsrt.bin":        minimal(256, {16: b"ring.bin\x00"}),                    # len<257: act impossible
}

for name, data in probes.items():
    p = OUT / name
    p.write_bytes(bytes(data))
    print(f"{name:22s} {len(data):6d} B  sha256:{hashlib.sha256(bytes(data)).hexdigest()[:16]}")
