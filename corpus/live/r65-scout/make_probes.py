#!/usr/bin/env python3
"""r65-scout probe builder: RIFF+0x84@256 x preemptor collisions.

act predicate (formats.c:93): len>=257 AND file[0:4]=="RIFF" AND file[256]==0x84
gsrt row (:81): len>=25  AND file[16:25]=="ring.bin\\0"
hcom row (:90): len>=132 AND file[65:69]=="FSSD" AND file[128:132]=="HCOM"

All files written into corpus/live/r65-scout/probes/.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "probes"
BASE = ROOT.parent / "round-63" / "pair_route_84.wav"   # 11,588 B, RIFF@0, 0x84@256

def w(name: str, data: bytearray) -> Path:
    p = OUT / name
    p.write_bytes(bytes(data))
    return p

def patch(base: bytes, edits: dict[int, int], spans: dict[int, bytes] | None = None) -> bytearray:
    b = bytearray(base)
    for off, val in edits.items():
        b[off] = val
    for off, blob in (spans or {}).items():
        b[off:off + len(blob)] = blob
    return b

def minimal(length: int, spans: dict[int, bytes]) -> bytearray:
    """Bare shell: RIFF@0, filler 0x00, caller supplies magics; len>=257."""
    b = bytearray(length)
    b[0:4] = b"RIFF"
    b[4:8] = (length - 8).to_bytes(4, "little")
    for off, blob in spans.items():
        b[off:off + len(blob)] = blob
    return b

base = BASE.read_bytes()
assert base[0:4] == b"RIFF" and base[256] == 0x84 and len(base) == 11588, "unexpected base"

probes = {}

# --- pair-family collisions (11,588 B) -----------------------------------
probes["probe_act_base.wav"]     = patch(base, {})                                  # control: act only
probes["probe_gsrt_act.wav"]     = patch(base, {}, {16: b"ring.bin\x00"})           # gsrt + act
probes["probe_hcom_act.wav"]     = patch(base, {}, {65: b"FSSD", 128: b"HCOM"})     # hcom + act
probes["probe_gsrt_hcom_act.wav"]= patch(base, {}, {16: b"ring.bin\x00",
                                                    65: b"FSSD", 128: b"HCOM"})    # gsrt before hcom
probes["probe_gsrt_only.wav"]    = patch(base, {256: 0x00}, {16: b"ring.bin\x00"})  # gsrt, no act
probes["probe_hcom_only.wav"]    = patch(base, {256: 0x00}, {65: b"FSSD",
                                                           128: b"HCOM"})          # hcom, no act
# --- conjunct/boundary controls ------------------------------------------
probes["probe_gsrt_badnul.wav"]  = patch(base, {}, {16: b"ring.bin\x80"})           # 9th byte != NUL -> not gsrt
probes["probe_hcom_halffssd.wav"]= patch(base, {}, {65: b"FSSD"})                   # missing HCOM@128
probes["probe_hcom_halfhcom.wav"]= patch(base, {}, {128: b"HCOM"})                  # missing FSSD@65
# --- later-row shielding (post-act rows can match but lose) --------------
probes["probe_avi_act.wav"]      = patch(base, {}, {8: b"AVI "})                    # RIFF+AVI@8 + 0x84 -> act beats avi
probes["probe_ftyp_act.wav"]     = patch(base, {}, {4: b"ftypisom"})                # ftyp@4 -> act beats mp4 row
# --- minimal shells (257 B) ----------------------------------------------
probes["min_act.wav"]            = minimal(257, {8: b"WAVE", 256: b"\x84"})         # act on a shell
probes["min_gsrt_act.bin"]       = minimal(257, {16: b"ring.bin\x00", 256: b"\x84"})
probes["min_hcom_act.bin"]       = minimal(257, {65: b"FSSD", 128: b"HCOM", 256: b"\x84"})
probes["min_hcom_200.bin"]       = minimal(200, {65: b"FSSD", 128: b"HCOM"})        # hcom, len<257 so act impossible
probes["min_gsrt_hcom_act.bin"]  = minimal(257, {16: b"ring.bin\x00", 65: b"FSSD",
                                               128: b"HCOM", 256: b"\x84"})

for name, data in probes.items():
    p = w(name, data)
    print(f"{name:28s} {len(data):6d} B  sha256-short", end=" ")
    import hashlib
    print(hashlib.sha256(bytes(data)).hexdigest()[:16])
