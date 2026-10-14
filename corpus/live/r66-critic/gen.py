#!/usr/bin/env python3
"""r66-critic variants: attack the completed preemptor map.

Families:
  Q* = wve ordering (max collision; attempts to make wve lose)
  H* = hcom reader field-walk: same detection signature, different fate
  S* = seekability forks on the tracked pair members (file vs pipe vs fifo)
  N* = NUL@24 detector-vs-reader conjunct divergence
  G* = gsrt reader floor vs detector floor (34B header walk vs 25B gate)
"""
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
VAR = HERE / "var"
VAR.mkdir(exist_ok=True)

WVE = b"ALawSoundFile**"
GSRT = b"ring.bin\x00"
FSSD = b"FSSD"
HCOM = b"HCOM"


def base_riff(n=600):
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


def hcom_fields(b, huffcount=9, checksum=0xA5A5A5A5, compresstype=0,
                divisor=1, dictsize=2, dict_entries=((1, 1), (-1, 0)),
                pad=0, first=0x40, word=0xA5A5A5A5):
    struct.pack_into(">I", b, 132, huffcount)
    struct.pack_into(">I", b, 136, checksum)
    struct.pack_into(">I", b, 140, compresstype)
    struct.pack_into(">I", b, 144, divisor)
    struct.pack_into(">H", b, 148, dictsize)
    off = 150
    for l, r in dict_entries:
        struct.pack_into(">hh", b, off, l, r)
        off += 4
    b[158] = pad
    b[159] = first
    struct.pack_into(">I", b, 160, word)
    return b


def hcomsig(b):
    """Just the detection signature: FSSD@65, HCOM@128, RIFF@0, 0x84@256."""
    b[65:69] = FSSD
    b[128:132] = HCOM
    b[256] = 0x84
    return b


def w(name, blob, ext=".wav"):
    p = VAR / f"{name}{ext}"
    p.write_bytes(bytes(blob))
    return p


made = {}

# ---------- Q: wve ordering ----------
# maximal constructable collision (RIFF@0 impossible with wve@0)
q = bytearray(600); q[0:15] = WVE; q[16:25] = GSRT
q[65:69] = FSSD; q[128:132] = HCOM; q[256] = 0x84
made["Q1_wve+gsrt+hcom+84"] = (q, ".bin")
made["Q2_wve+gsrt+hcom+84_wavname"] = (q, ".wav")   # same bytes, .wav name

# wve that also fully decodes + carries later sigs (valid Psion .wve).
# wve reader checks 18-byte ID @0 (magic15 + \x00\x0f\x10 @15-17): gsrt@16
# collides with the Psion id, so a wve-decodable file can never carry gsrt.
# Max decodable collision = wve + hcom sigs + 0x84 (payload-region bytes).
src = HERE.parent / "r66-boundary" / "probes" / "b_wve_hcomsig_dec.bin"
if src.exists():
    bd = bytearray(src.read_bytes())
    if len(bd) >= 257:
        bd[256] = 0x84
    made["Q3_wveDEC+hcom+84"] = (bd, ".bin")

# wve + gsrt sig at 16 (detector-level collision; reader dies on Psion id —
# byte16 'r' breaks \x0f). Proves detect!=decode on the wve row too.
w2 = bytearray(600); w2[0:15] = WVE; w2[15:18] = b"\x00\x0f\x10"
struct.pack_into(">I", w2, 18, 500)
w2[16:25] = GSRT   # overwrites bytes16-17: kills Psion id, installs gsrt sig
w2[65:69] = FSSD; w2[128:132] = HCOM; w2[256] = 0x84
made["Q5_wveVALID15+gsrt+hcom+84"] = (w2, ".bin")

# RIFF file named .wve: does extension ever win over content?
made["Q4_riff_named_wve"] = (base_riff(300), ".wve")

# ---------- H: same hcom signature, different fate ----------
d0 = hcom_fields(hcomsig(base_riff(600)))
made["H00_base_decode9"] = (d0, ".wav")
v = hcom_fields(hcomsig(base_riff(600)), compresstype=1)
made["H01_compresstype1"] = (v, ".wav")
v = hcom_fields(hcomsig(base_riff(600)), divisor=2)
made["H02_divisor2"] = (v, ".wav")
v = hcom_fields(hcomsig(base_riff(600)), divisor=4)
made["H03_divisor4"] = (v, ".wav")
v = hcom_fields(hcomsig(base_riff(600)), divisor=5)
made["H04_divisor5"] = (v, ".wav")
v = hcom_fields(hcomsig(base_riff(600)), divisor=0)
made["H05_divisor0"] = (v, ".wav")
v = hcom_fields(hcomsig(base_riff(600)), compresstype=2)
made["H06_compresstype2"] = (v, ".wav")
v = hcom_fields(hcomsig(base_riff(600)), dictsize=0)
made["H07_dictsize0"] = (v, ".wav")
v = hcom_fields(hcomsig(base_riff(600)), dictsize=512)
made["H08_dictsize512"] = (v, ".wav")
v = hcom_fields(hcomsig(base_riff(600)), dict_entries=((5, 5), (-1, 0)))
made["H09_invaliddict"] = (v, ".wav")
v = hcom_fields(hcomsig(base_riff(600)), checksum=0xDEADBEEF)
made["H10_badchecksum"] = (v, ".wav")
v = hcom_fields(hcomsig(base_riff(600)), huffcount=10)
made["H11_huffcount10"] = (v, ".wav")
v = hcom_fields(hcomsig(base_riff(600)), huffcount=1)
made["H12_huffcount1"] = (v, ".wav")
v = hcom_fields(hcomsig(base_riff(600)), huffcount=0)
made["H13_huffcount0"] = (v, ".wav")
v = hcom_fields(hcomsig(base_riff(600)), first=0x41)
made["H14_firstsample41"] = (v, ".wav")
v = hcom_fields(hcomsig(base_riff(600)), dict_entries=((1, 1), (-1, 5)))
made["H15_datum5"] = (v, ".wav")
v = bytearray(d0); v[83:91] = b"\xDE\xAD\xBE\xEF\xCA\xFE\xBA\xBE"  # datasize/rsrcsize
made["H16_datasize_mut"] = (v, ".wav")
v = bytearray(d0); v[158] = 0x99                                   # pad byte
made["H17_padmut"] = (v, ".wav")
v = hcom_fields(hcomsig(base_riff(600)), dictsize=1,
                dict_entries=((-1, 0),))
made["H18_dictsize1"] = (v, ".wav")

# ---------- S: seekability on tracked members ----------
R66 = HERE.parent / "round-66"
for m in ("pair_dec_hcom", "pair_dec_act", "pair_lengate_gsrt_24",
          "pair_lengate_gsrt_25", "pair_lengate_hcom_131",
          "pair_lengate_hcom_132"):
    p = R66 / f"{m}.wav"
    if p.exists():
        made[f"S_{m}"] = (bytearray(p.read_bytes()), ".wav")

# ---------- N: NUL@24 detector-vs-reader divergence ----------
n = base_riff(600); n[16:25] = b"ring.binX"  # byte24 = 'X' not NUL
n[256] = 0x84
made["N1_badnul_riff84"] = (n, ".wav")       # detected act; -t gsrt on pipe?
n0 = bytearray(600)                          # file_size=0 -> checksum skipped
n0[16:25] = b"ring.binX"
n0[256] = 0x84
made["N2_badnul_sz0"] = (n0, ".bin")         # -t gsrt even on a file
n0z = bytearray(600); n0z[16:25] = GSRT; n0z[256] = 0x84
made["N3_goodnul_sz0"] = (n0z, ".bin")       # detected gsrt AND -t gsrt decodes

# ---------- G: gsrt reader floor vs detector floor ----------
for L in (25, 30, 31, 32, 33, 34, 35, 100, 511, 512):
    g = bytearray(L)
    g[16:25] = GSRT[:min(9, max(0, L - 16))]
    made[f"G_sz0_len{L}"] = (g, ".bin")      # file_size=0 -> no checksum wall

import hashlib
for name, (blob, ext) in sorted(made.items()):
    p = w(name, blob, ext)
    print(f"{name:34s} {len(blob):4d} B {ext} sha={hashlib.sha256(bytes(blob)).hexdigest()[:12]}")
