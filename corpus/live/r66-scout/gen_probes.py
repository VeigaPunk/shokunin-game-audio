#!/usr/bin/env python3
"""r66-scout: independent preemptor-map probes (wve predicate + RIFF geometry
+ len gates + decodable-preemptor cross-validation).

Families:
  P*  = wve CHECK predicate pinning (magic content, len edge, byte exactness)
  V*  = wve READER-valid files (ID1 = magic + {00 0F 10}@15-17, num_samples
        @18-21 BE, 10B pad, alaw data @32) — incl. a decodable preemptor that
        also carries hcom conjuncts + the act byte (non-RIFF surface)
  Q*  = quad/multi collisions: wve magic vs ring.bin@16 vs FSSD/HCOM vs 0x84
  S*  = RIFF head-swap minimal divergence (byte-0..3 conflict demonstration)
  L*  = length-gate shells, RIFF+WAVE layout, independent rebuild of the
        round-66 tracked members + bare .bin cross-checks
  D*  = independent rebuild of the decodable-preemptor pair (sha-check vs
        corpus/live/round-66/pair_dec_*.wav) + HCOM-side demotion variant
"""
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "probes"
OUT.mkdir(exist_ok=True)

WVE = b"ALawSoundFile**"          # candidate 15-byte magic @0-14
WVE_ID1_TAIL = b"\x00\x0f\x10"    # reader ID1 bytes 15-17 (wve.c: {'*','*','\0','\017','\020'})
GSRT = b"ring.bin\x00"            # 9 bytes @16-24 (memcmp incl. literal NUL)
FSSD = b"FSSD"                    # @65-68
HCOM = b"HCOM"                    # @128-131


def w(name, buf, ext=".bin"):
    p = OUT / f"{name}{ext}"
    p.write_bytes(bytes(buf))
    print(f"{name + ext:38s} {len(buf):5d} B")
    return p


def riff_shell(n):
    """Minimal RIFF/WAVE skeleton: fmt16 PCM16 mono 8kHz + data chunk,
    deterministic ramp payload (same recipe as prior seats, built fresh)."""
    buf = bytearray(b"\x00" * n)
    buf[0:4] = b"RIFF"
    struct.pack_into("<I", buf, 4, n - 8)
    if n >= 12:
        buf[8:12] = b"WAVE"
    if n >= 44:
        buf[12:16] = b"fmt "
        struct.pack_into("<I", buf, 16, 16)
        struct.pack_into("<H", buf, 20, 1)
        struct.pack_into("<H", buf, 22, 1)
        struct.pack_into("<I", buf, 24, 8000)
        struct.pack_into("<I", buf, 28, 16000)
        struct.pack_into("<H", buf, 32, 2)
        struct.pack_into("<H", buf, 34, 16)
        buf[36:40] = b"data"
        struct.pack_into("<I", buf, 40, n - 44)
    for i in range(44, n):
        buf[i] = (i * 7 + 3) & 0xFF
    return buf


def hcom_valid_fields(b):
    """r65-critic D1 chain, all BE: huffcount@132=9, checksum@136,
    compresstype@140=0 (<=1), divisor@144=1 (1..4 -> 22050 Hz),
    dictsize@148=2 (1..511), dict[0]{1,1} dict[1]{-1,0} leaf,
    pad@158=0, first sample@159=0x40, huffman word@160 == checksum."""
    struct.pack_into(">I", b, 132, 9)
    struct.pack_into(">I", b, 136, 0xA5A5A5A5)
    struct.pack_into(">I", b, 140, 0)
    struct.pack_into(">I", b, 144, 1)
    struct.pack_into(">H", b, 148, 2)
    struct.pack_into(">hh", b, 150, 1, 1)
    struct.pack_into(">hh", b, 154, -1, 0)
    b[158] = 0
    b[159] = 0x40
    struct.pack_into(">I", b, 160, 0xA5A5A5A5)
    return b


def wve_valid(n=300, nsamp=64):
    """Reader-valid wve: ID1 @0-17 (magic + 00 0F 10), num_samples BE @18-21,
    ID2 pad @22-31, alaw payload @32. Data bytes = deterministic ramp."""
    b = bytearray(b"\x00" * n)
    b[0:15] = WVE
    b[15:18] = WVE_ID1_TAIL
    struct.pack_into(">I", b, 18, nsamp)
    # bytes 22-31 = ID2 pad (ignored by reader)
    for i in range(32, n):
        b[i] = (i * 13 + 5) & 0xFF          # arbitrary alaw payload
    return b


# ---------- P: wve predicate pinning ----------
w("P01_wve_magic", (lambda b: b)(bytearray(b"\x00" * 300)))  # placeholder replaced below
b = bytearray(b"\x00" * 300); b[0:15] = WVE
w("P01_wve_magic", b)                      # magic@0-14, zeros elsewhere
w("P02_wve_len15", bytearray(WVE))                       # exactly 15 B
w("P03_wve_len14", bytearray(WVE[:14]))                  # 14 B: 'ALawSoundFile*'
b = bytearray(WVE[:14] + b"X"); w("P04_wve_len15_b14X", b)  # 15 B, last '*' -> 'X'
b = bytearray(b"\x00" * 300); b[0:15] = WVE; b[14] = ord('X')
w("P05_wve_b14X", b)                       # '*' @14 is literal, not wildcard
b = bytearray(b"\x00" * 300); b[0:15] = WVE; b[13] = ord('X')
w("P06_wve_b13X", b)                       # '*' @13 is literal too
b = bytearray(b"\x00" * 300); b[0:15] = WVE; b[0] = ord('a')
w("P07_wve_b0low", b)                      # case: 'alaw...' fails
b = bytearray(b"\x00" * 300); b[0:15] = WVE; b[7] = ord('X')
w("P08_wve_b07X", b)                       # mid-magic mutation
b = bytearray(b"\x00" * 300); b[0:15] = WVE; b[15] = 0xAA
w("P09_wve_b15free", b)                    # byte 15 outside detector predicate
w("P10_wve_len18_idok", bytearray(WVE + WVE_ID1_TAIL))   # 18 B: reader-id OK, EOF at num_samples

# ---------- V: reader-valid wve ----------
w("V01_wve_valid", wve_valid())                          # expect decode 64 @8k
b = wve_valid(); b[65:69] = FSSD; b[128:132] = HCOM; b[256] = 0x84
w("V02_wve_valid+hcom+84", b)              # decodable preemptor carrying hcom+act-byte
b = wve_valid(); b[256] = 0x84
w("V03_wve_valid+84", b)                   # wve decodable + act byte (no RIFF: act unreachable)

# ---------- Q: multi-signature non-RIFF collisions ----------
b = bytearray(b"\x00" * 300); b[0:15] = WVE; b[16:25] = GSRT; b[256] = 0x84
w("Q01_wve+gsrt+84", b)                    # wve vs gsrt on one file
b = bytearray(b); b[65:69] = FSSD; b[128:132] = HCOM
w("Q02_wve+gsrt+hcom+84", b)               # quad: wve,gsrt,hcom,act-byte
b = bytearray(b"\x00" * 300); b[0:15] = WVE; b[65:69] = FSSD; b[128:132] = HCOM; b[256] = 0x84
w("Q03_wve+hcom+84", b)                    # wve vs hcom only

# ---------- S: RIFF head-swap (byte-0..3 conflict) ----------
# Common tail: bytes 15+ = zeros except 0x84@256. Heads differ only @0-3.
tail = bytearray(b"\x00" * 300); tail[256] = 0x84
a = bytearray(tail); a[0:15] = WVE                    # ALawSoundFile** + tail
w("S01_head_wve", a)                                  # -> wve
b_ = bytearray(tail); b_[0:4] = b"RIFF"; b_[4:15] = WVE[4:15]  # 'RIFFSoundFile**'
w("S02_head_riff84", b_)                              # 4-byte-span diff vs S01 -> act
b3 = bytearray(tail); b3[0] = ord('R')                # 'RLawSoundFile**': one-byte flip
w("S03_head_b0R", b3)                                 # -> neither wve nor RIFF -> NONE
# wve tail at nonzero offset inside a real RIFF+0x84 file
b4 = riff_shell(300); b4[256] = 0x84; b4[44:59] = WVE # magic @44 inside data
w("S04_riff+wve@44", b4, ".wav")                      # -> act (wve not anchored @0)
b5 = riff_shell(300); b5[256] = 0x84
w("S05_riff+84_ctl", b5, ".wav")                      # -> act control
b6 = riff_shell(300); b6[256] = 0x84; b6[16:25] = GSRT
w("S06_riff+gsrt+84", b6, ".wav")                     # -> gsrt control
b7 = riff_shell(300); b7[256] = 0x84; b7[65:69] = FSSD; b7[128:132] = HCOM
w("S07_riff+hcom+84", b7, ".wav")                     # -> hcom control

# ---------- L: length gates (RIFF+WAVE shells; independent rebuild) ----------
g = riff_shell(25); g[16:25] = GSRT
w("L01_gsrt_25", g, ".wav")                           # len>=25: full 'ring.bin\0' fits
g = riff_shell(24); g[16:24] = b"ring.bin"
w("L02_gsrt_24", g, ".wav")                           # len 24: NUL@24 cut by EOF
h = riff_shell(132); h[65:69] = FSSD; h[128:132] = HCOM
w("L03_hcom_132", h, ".wav")                          # len>=132: 'M'@131 present
h = riff_shell(131); h[65:69] = FSSD; h[128:131] = b"HCO"
w("L04_hcom_131", h, ".wav")                          # len 131: 'M' cut by EOF
# bare .bin cross-checks (extension-fallback shape, r65-boundary convention)
g = bytearray(25); g[16:25] = GSRT
w("L05_gsrt_25_noriff", g)
g = bytearray(24); g[16:24] = b"ring.bin"
w("L06_gsrt_24_noriff", g)
h = bytearray(132); h[65:69] = FSSD; h[128:132] = HCOM
w("L07_hcom_132_noriff", h)
h = bytearray(131); h[65:69] = FSSD; h[128:131] = b"HCO"
w("L08_hcom_131_noriff", h)
# sub-detection-size oddity: len 12..14 file carrying full WVE tail positions
w("L09_wve_15minus1_noext", bytearray(WVE[:14]))      # dup of P03 w/ .bin ext semantics

# ---------- D: independent rebuild of the tracked dec pair ----------
d = hcom_valid_fields(riff_shell(600))
d[65:69] = FSSD; d[128:132] = HCOM; d[256] = 0x84
w("D01_dec_hcom_rebuild", d, ".wav")                  # sha should == pair_dec_hcom.wav
d2 = bytearray(d); d2[68] = ord('E')
w("D02_dec_act_rebuild", d2, ".wav")                  # sha should == pair_dec_act.wav
d3 = bytearray(d); d3[131] = ord('X')                 # alternate demotion: 'M'->'X' @131
w("D03_dec_hcom131x", d3, ".wav")                     # -> act (HCOM conjunct broken)
d4 = bytearray(d); d4[256] = 0x00                     # hcom-valid, no act byte
w("D04_dec_hcom_00", d4, ".wav")                      # -> hcom (preemptor self-sufficient)
