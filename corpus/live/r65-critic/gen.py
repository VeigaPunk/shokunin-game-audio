#!/usr/bin/env python3
"""r65-critic: discriminating RIFF/preemptor collision variants.

All files are RIFF@0 + WAVE@8 skeletons (300 B unless noted) with the
declared preemptor signatures and/or the r63 act trigger byte overlaid.
Offsets are file offsets.

Detection table order (corroborative, sox_ng-14.8.0.1 formats.c):
  gsrt  CHECK(0,0,"", 16,9,"ring.bin")     9B incl NUL @16-24
  hcom  CHECK(65,4,"FSSD",128,4,"HCOM")    both conjuncts
  act   CHECK(0,4,"RIFF",256,1,"\\x84")    #if USING_FFMPEG
  wav   CHECK(0,4,"RIFF",8,4,"WAVE")
"""
import os, struct, sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "var")
os.makedirs(OUT, exist_ok=True)

GSRT = b"ring.bin\x00"          # 9 bytes @16-24 (sig + C-literal NUL)
FSSD = b"FSSD"                   # @65-68
HCOM = b"HCOM"                   # @128-131

def base(n=600):
    """Minimal RIFF/WAVE skeleton: fmt16 PCM16 mono 8kHz + data chunk."""
    buf = bytearray(b"\x00" * n)
    buf[0:4] = b"RIFF"
    struct.pack_into("<I", buf, 4, n - 8)
    if n >= 12:
        buf[8:12] = b"WAVE"
    if n >= 44:
        buf[12:16] = b"fmt "
        struct.pack_into("<I", buf, 16, 16)          # fmt size
        struct.pack_into("<H", buf, 20, 1)           # PCM
        struct.pack_into("<H", buf, 22, 1)           # mono
        struct.pack_into("<I", buf, 24, 8000)        # rate
        struct.pack_into("<I", buf, 28, 16000)       # byte rate
        struct.pack_into("<H", buf, 32, 2)           # block align
        struct.pack_into("<H", buf, 34, 16)          # bits
        buf[36:40] = b"data"
        struct.pack_into("<I", buf, 40, n - 44)      # data size
    # payload: deterministic ramp so offsets are greppable
    for i in range(44, n):
        buf[i] = (i * 7 + 3) & 0xFF
    return buf

def w(name, buf, ext=".wav"):
    p = os.path.join(OUT, name + ext)
    with open(p, "wb") as f:
        f.write(buf)
    print(f"{name+ext:44s} {len(buf):6d} B")
    return p

def gsrtify(b, nul=True, off=16, enc=None):
    b[off:off+8] = b"ring.bin"
    b[off+8] = 0x00 if nul else 0x58           # byte24: NUL or 'X'
    if enc is not None:
        struct.pack_into(">h", b, 32, enc)     # gsrt encoding int16 @32-33 BE
    return b

def hcomify(b, fssd=True, hcom=True, fssd_off=65, hcom_off=128, decode=False):
    if fssd:
        b[fssd_off:fssd_off+4] = FSSD
    if hcom:
        b[hcom_off:hcom_off+4] = HCOM
    if decode:
        # hcom reader fields (all BE): huffcount@132, checksum@136,
        # compresstype@140 (<=1), divisor@144 (1..4), dictsize@148 (1..511),
        # dict entries 4B each {leftson,rightson} BE shorts, pad byte @158,
        # data @159: raw first sample byte + Huffman words.
        struct.pack_into(">I", b, 132, 9)      # huffcount = 9 samples total
        word = 0xA5A5A5A5
        struct.pack_into(">I", b, 136, word)   # checksum = the data word sum
        struct.pack_into(">I", b, 140, 0)      # compresstype 0 (value comp.)
        struct.pack_into(">I", b, 144, 1)      # divisor 1 -> 22050 Hz
        struct.pack_into(">H", b, 148, 2)      # dictsize 2
        struct.pack_into(">hh", b, 150, 1, 1)  # dict[0] -> entry 1 either bit
        struct.pack_into(">hh", b, 154, -1, 0) # dict[1] leaf, datum 0
        b[158] = 0                             # pad
        b[159] = 0x40                          # first raw sample
        struct.pack_into(">I", b, 160, word)   # the Huffman word (cksum match)
    return b

def actify(b, val=0x84):
    b[256] = val
    return b

# ---------- A: ordering (double/triple collision, act byte present) ----------
b = actify(gsrtify(hcomify(base())));            w("A1_gsrt+hcom+act", b)
b = actify(gsrtify(hcomify(base()), nul=False)); w("A2_gsrtNoNUL+hcom+act", b)
b = actify(gsrtify(hcomify(base(), hcom=False)));w("A3_gsrt+FSSDonly+act", b)
b = actify(hcomify(base()));                     w("A4_hcom+act", b)
b = actify(gsrtify(base()));                     w("A5_gsrt+act", b)
b = actify(hcomify(base(), hcom=False));         w("A6_FSSDonly+act", b)
b = actify(hcomify(base(), fssd=False));         w("A7_HCOMonly+act", b)
b = actify(base());                              w("A8_act_only", b)

# ---------- B: preemptor WITHOUT the act byte ----------
for val, tag in [(0x00, "00"), (0x41, "41")]:
    b = gsrtify(base()); b[256] = val;           w(f"B_gsrt_{tag}", b)
    b = hcomify(base()); b[256] = val;           w(f"B_hcom_{tag}", b)
b = gsrtify(hcomify(base())); b[256] = 0x00;     w("B_gsrt+hcom_00", b)
b = hcomify(base()); b[256] = 0x83;              w("B_hcom_83", b)
b = hcomify(base()); b[256] = 0x85;              w("B_hcom_85", b)

# ---------- D: reader-identity-by-success ----------
# hcom-decodable RIFF+WAVE+0x84 file (also a native-decodable PCM16 wav
# if forced -t wav: data chunk intact, fields live in payload bytes).
b = actify(hcomify(base(), decode=True));        w("D1_hcomdecode+act", b)
b = hcomify(base(), decode=True); b[256] = 0x00; w("D1b_hcomdecode_00", b)
# gsrt-decodable ONLY via non-seekable fd (RIFF@0 makes file_size huge ->
# checksum loop dies on seekable open; stdin skips it).
b = actify(gsrtify(base(), enc=0));              w("D2_gsrtULAW+act", b)   # enc 0 = ulaw 8b
b = actify(gsrtify(base(), enc=8));              w("D2b_gsrtALAW+act", b)  # enc 8 = alaw 8b
b = actify(gsrtify(base(), enc=3));              w("D2c_gsrtGSM+act", b)   # enc 3 -> read=NULL
# pure gsrt controls (not RIFF): size field small -> reader succeeds on file arg
b = bytearray(b"\x00" * 600)
struct.pack_into(">I", b, 0, 0)                  # file_size=0 -> no checksum
gsrtify(b, enc=0); b[256] = 0x84
w("D3_puregsrt_sz0", b)
b = bytearray(b"\x00" * 1200)
struct.pack_into(">I", b, 0, 300)                # file_size=300 -> 298-word sum
gsrtify(b, enc=0); b[256] = 0x84                 # checksum may warn, still reads
w("D3b_puregsrt_sz300", b)

# ---------- E: boundaries / position exactness ----------
b = base(132); hcomify(b);                       w("E1_hcom_len132", b)   # len>=132 edge
b = base(131); hcomify(b);                       w("E1b_hcom_len131", b)
b = base(200); gsrtify(b); b[100] = 0x84;        w("E2_gsrt_len200", b)  # <257: act impossible
b = base(25);  gsrtify(b);                       w("E2b_gsrt_len25", b)   # len>=25 edge
b = actify(base()); b[15:23] = b"ring.bin"; b[23] = 0  # sig @15-23
w("E3_gsrt@15+act", b)
b = actify(base()); b[17:25] = b"ring.bin"; b[25] = 0  # sig @17-25
w("E3b_gsrt@17+act", b)
b = actify(hcomify(base(), fssd_off=64));        w("E4_FSSD@64+act", b)
b = actify(hcomify(base(), hcom_off=127));       w("E4b_HCOM@127+act", b)
# RIFX container + preemptors (preemptor rows do not need RIFF)
b = actify(gsrtify(base())); b[0:4] = b"RIFX";   w("E5_RIFX+gsrt+act", b)
b = actify(hcomify(base())); b[0:4] = b"RIFX";   w("E5b_RIFX+hcom+act", b)
# triple collision with non-.wav extension (content autodetect vs ext)
b = actify(gsrtify(hcomify(base())));            w("E6_triple", b, ".bin")
# hcom-decodable triple (gsrt still wins detect; proves detect!=read success)
b = actify(gsrtify(hcomify(base(), decode=True), enc=0))
w("E7_triple_bothdecodable", b)
