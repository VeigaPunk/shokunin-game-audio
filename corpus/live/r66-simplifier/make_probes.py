#!/usr/bin/env python3
"""r66-simplifier independent probes for the preemptor-map-completion audit.

CHECK rows (sox_ng-14.8.0.1 formats.c, order): wve(80) gsrt(81) hcom(90) act(93) wav(95+).
  wve  : len>=15  AND file[0:15]=="ALawSoundFile**"          (offset-0 magic)
  gsrt : len>=25  AND file[16:25]=="ring.bin\\0"
  hcom : len>=132 AND file[65:69]=="FSSD" AND file[128:132]=="HCOM"
  act  : len>=257 AND file[0:4]=="RIFF" AND file[256]==0x84

Axes under audit:
  A. wve on RIFF — reachable?  (offset-0 magic excludes RIFF@0 by construction)
  B. len gates — gsrt 24|25, hcom 131|132 exact
  C. decodable-preemptor pair — hcom-detected AND hcom-reader-decodes (D1 shape),
     plus fmt-16 pcm pair (scout shape) where the wav reader decodes
  D. bare (no-RIFF) preemptor decode — RIFF not required for preemptors
"""
import hashlib
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "probes"
OUT.mkdir(exist_ok=True)

GSRT = b"ring.bin\x00"      # @16-24
FSSD = b"FSSD"              # @65-68
HCOM = b"HCOM"              # @128-131
WVE  = b"ALawSoundFile**"   # @0-14 (15 B)
BASE = ROOT.parent / "round-63" / "pair_route_84.wav"  # 11,588 B RIFF+0x84@256


def w(name, buf):
    p = OUT / name
    p.write_bytes(bytes(buf))
    print(f"{name:36s} {len(buf):6d} B  {hashlib.sha256(bytes(buf)).hexdigest()[:16]}")
    return p


def patch(base, edits=(), spans=()):
    b = bytearray(base)
    for off, blob in spans:
        b[off:off + len(blob)] = blob
    for off, val in edits:
        b[off] = val
    return b


def riff_shell(n, spans=(), wave=True):
    """Bare RIFF shell: RIFF@0 (+WAVE@8), zero filler, caller magics."""
    b = bytearray(n)
    b[0:4] = b"RIFF"
    b[4:8] = (n - 8).to_bytes(4, "little")
    if wave and n >= 12:
        b[8:12] = b"WAVE"
    for off, blob in spans:
        b[off:off + len(blob)] = blob
    return b


def pcm16_wav(n=1068, rate=8000):
    """fmt-16 PCM WAV, 512-sample deterministic sine-ish payload (scout shape)."""
    import math
    nsamp = (n - 44) // 2
    data = struct.pack("<" + "h" * nsamp,
                       *[int(8000 * math.sin(2 * math.pi * 440 * i / rate)) for i in range(nsamp)])
    fmt = struct.pack("<HHIIHH", 1, 1, rate, rate * 2, 2, 16)
    riff = b"WAVEfmt " + struct.pack("<I", 16) + fmt + b"data" + struct.pack("<I", len(data)) + data
    return bytearray(b"RIFF" + struct.pack("<I", len(riff)) + riff)


def hcom_decode_fields(b):
    """Fill the hcom reader's accept chain (critic's D1 recipe, BE fields)."""
    struct.pack_into(">I", b, 132, 9)          # huffcount = 9 samples
    word = 0xA5A5A5A5
    struct.pack_into(">I", b, 136, word)       # checksum = data word sum
    struct.pack_into(">I", b, 140, 0)          # compresstype 0
    struct.pack_into(">I", b, 144, 1)          # divisor 1 -> 22050 Hz
    struct.pack_into(">H", b, 148, 2)          # dictsize 2
    struct.pack_into(">hh", b, 150, 1, 1)      # dict[0] -> entry 1
    struct.pack_into(">hh", b, 154, -1, 0)     # dict[1] leaf, datum 0
    b[158] = 0
    b[159] = 0x40                              # first raw sample byte
    struct.pack_into(">I", b, 160, word)       # Huffman word
    return b


base = BASE.read_bytes()
assert base[0:4] == b"RIFF" and base[256] == 0x84 and len(base) == 11588

print("== A. wve reachability on/off RIFF ==")
# A1: full wve magic @0 + all other sigs + 0x84@256, NO RIFF — wve should win everything
b = bytearray(600)
b[0:15] = WVE
b[16:25] = GSRT
b[65:69] = FSSD; b[128:132] = HCOM
b[256] = 0x84
w("s_wve_all_noriff.bin", b)
# A2: same but ALSO RIFF — impossible (RIFF@0 destroys wve magic); show the two
# predicates share offset 0: RIFF@0 + wve magic placed at a nonzero offset.
b = riff_shell(600, [(300, WVE), (16, GSRT), (65, FSSD), (128, HCOM)])
b[256] = 0x84
w("s_riff_wve300_all.wav", b)          # RIFF@0 + wve magic displaced -> gsrt expected
# A3: RIFF + wve magic displaced, NO other sigs -> act expected (wve blind off-0)
b = riff_shell(600, [(300, WVE)])
b[256] = 0x84
w("s_riff_wve300_act.wav", b)
# A4: wve magic @0 with a RIFF later — can a file be "wve-shaped RIFF"? offset-0
# exclusivity means no; closest is wve@0 + RIFF@some offset.
b = bytearray(600)
b[0:15] = WVE
b[300:304] = b"RIFF"
b[256] = 0x84
w("s_wve0_riff300.bin", b)             # -> wve (RIFF off-0 is not the act row anyway)

print("== B. length gates ==")
for n, tag in ((24, "24"), (25, "25")):
    b = riff_shell(n, [(16, GSRT[:max(0, n - 16)] or GSRT)])  # only what fits
    w(f"s_gsrt_len{tag}.bin", b)
for n, tag in ((131, "131"), (132, "132")):
    b = riff_shell(n, [(65, FSSD), (128, HCOM[:max(0, n - 128)] or HCOM)])
    w(f"s_hcom_len{tag}.bin", b)
# on-RIFF variants (act byte present): 131/132 with 0x84 — but 131|132 < 257 so
# act unreachable; still worth seeing wav-vs-none on RIFF bodies.
b = riff_shell(257, [(65, FSSD), (128, HCOM)])
w("s_riff_hcom_257.bin", b)            # control: hcom on RIFF shell

print("== C. decodable-preemptor pairs ==")
# C1: critic D1 shape — 600-B fmt-16 RIFF/WAVE + FSSD@65 + HCOM@128 +
#     hcom accept fields + 0x84@256. Detects hcom AND hcom reader decodes.
b = pcm16_wav(600)                      # fmt16 PCM skeleton w/ payload @44+
b[65:69] = FSSD; b[128:132] = HCOM
hcom_decode_fields(b)
b[256] = 0x84
w("s_d1_hcomdecode_act.wav", b)
# C1b: sole-diff partner — break HCOM @131 only -> act, bridge decodes PCM
b2 = bytearray(b); b2[131] = ord('N')
w("s_d1_hcom131x_act.wav", b2)
# C2: scout fmt-16 pair — 1,068-B PCM WAV, sigs inside data payload
b = pcm16_wav(1068)
b[65:69] = FSSD; b[128:132] = HCOM
b[256] = 0x84
w("s_pcm_hcom_act.wav", b)
b2 = bytearray(b); b2[68] = ord('E')    # FSSD -> FSSE: sole byte-68 diff
w("s_pcm_hcom68x_act.wav", b2)

print("== D. bare (no-RIFF) preemptor members ==")
# D1: bare gsrt decodable (boundary recipe: honest small file_size@0, enc 0)
b = bytearray(1512)
struct.pack_into(">I", b, 0, 1000)      # gsrt file_size=1000 int16s
b[4:16] = b"\x00" * 12
b[16:24] = b"ring.bin"
b[24] = 0
struct.pack_into(">h", b, 32, 0)        # enc 0 = ulaw
b[256] = 0x84                           # act byte present but no RIFF -> act row dead
w("s_bare_gsrt_act84.bin", b)
# D2: bare hcom decodable (FSSD/HCOM + valid accept fields, no RIFF, 0x84@256)
b = bytearray(300)
b[65:69] = FSSD; b[128:132] = HCOM
hcom_decode_fields(b)
b[256] = 0x84
w("s_bare_hcom_act84.bin", b)
# D3: 0x84@256 alone, no RIFF, .wav ext -> wav row still needs RIFF@0? (RIFF absent)
b = bytearray(300)
b[256] = 0x84
w("s_actbyte_only.wav", b)
print("done")
