#!/usr/bin/env python3
"""r65-boundary probe builder: preemptor-ordering edges + stdin survival.

Predicates (sox_ng-14.8.0.1 src/formats.c, corroborative only):
  gsrt row :81  len>=25  AND file[16:25]=="ring.bin\\0"   (no @0 conjunct)
  hcom row :90  len>=132 AND file[65:69]=="FSSD" AND file[128:132]=="HCOM"
  act  row :93  len>=257 AND file[0:4]=="RIFF"  AND file[256]==0x84
  wav  rows :95-97 RIFF/RIFX/RF64@0 + WAVE@8
First match wins; order voc(78) smp(79) wve(80) gsrt(81) ... hcom(90) act(93) wav(95+).

gsrt reader (gsrt.c:69-119): dw file_size@0; IF file_size>=2 AND ft->seekable ->
whole-file checksum pass then lsx_seeki(4). On non-seekable input the pass is
skipped. id[16]@16 vs "ring.bin" (8-byte cmp), enc int16BE@32, pad to 512.
hcom reader (hcom.c:75-195): purely sequential, zero seeks.
"""
import hashlib, struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "probes"
OUT.mkdir(exist_ok=True)
BASE = ROOT.parent / "round-63" / "pair_route_84.wav"   # 11,588 B, RIFF@0, 0x84@256

def w(name, data):
    p = OUT / name
    p.write_bytes(bytes(data))
    return p, len(data), hashlib.sha256(bytes(data)).hexdigest()

def patch(base, edits=None, spans=None):
    b = bytearray(base)
    for off, val in (edits or {}).items():
        b[off] = val
    for off, blob in (spans or {}).items():
        b[off:off + len(blob)] = blob
    return b

def shell(length, spans):
    """Bare buffer (no RIFF unless caller puts it), zero fill."""
    b = bytearray(length)
    for off, blob in spans.items():
        b[off:off + len(blob)] = blob
    return b

base = BASE.read_bytes()
assert base[0:4] == b"RIFF" and base[256] == 0x84 and len(base) == 11588

made = {}

# ---------------------------------------------------------------- group S
# stdin survival probes. RIFF collision fixtures keep the r61-family payload.
# bytes 32-33 = fmt block_align field in the base (0x0002); gsrt reads them as
# the BIG-ENDIAN ft_encoding int16 -> table lookup.
made["coll_gsrt_alaw.wav"]  = patch(base, spans={16: b"ring.bin\x00", 32: b"\x00\x08"})  # enc 8 -> ALAW
made["coll_gsrt_ulaw.wav"]  = patch(base, spans={16: b"ring.bin\x00", 32: b"\x00\x00"})  # enc 0 -> ULAW
made["coll_gsrt_g726.wav"]  = patch(base, spans={16: b"ring.bin\x00"})                    # enc 2 -> UNKNOWN (block_align)
made["coll_act_base.wav"]   = patch(base)                                                # act-only control

def gsrt_file(nsamp, enc, corrupt_ck=False, fs_override=None, body_len=None):
    """Minimal well-formed GSRT: u32BE file_size, i16BE checksum, u32 version,
    6B timestamp, 'ring.bin'+pad @16, i16BE enc @32, pad to 512, payload.
    fs_override/body_len decouple DECLARED size from ACTUAL length."""
    fs = (512 + nsamp) // 2 if fs_override is None else fs_override
    n = fs * 2 - 512                     # declared samples
    total = fs * 2 if body_len is None else body_len
    body = bytearray(total)              # seekable checksum pass needs len >= 2*fs
    struct.pack_into(">I", body, 0, fs)
    struct.pack_into(">I", body, 6, 0x01000000)          # version
    # timestamp @10-15 left zero
    body[16:32] = b"ring.bin\x00" + bytes(7)
    struct.pack_into(">h", body, 32, enc)
    # payload @512.. : constant 0xFF for ulaw / 0x55 for alaw (audible-neutral)
    fill = 0xFF if enc == 0 else 0x55
    body[512:] = bytes([fill]) * max(0, total - 512)
    # checksum: (fs>>16)+fs + sum(int16BE over bytes 4..2*fs) must be &0xffff==0
    region = bytes(body[4:min(total, fs * 2)])
    if len(region) % 2:
        region += b"\x00"
    s = (fs >> 16) + fs + sum(struct.unpack(f">{len(region)//2}h", region))
    ck = (-s) & 0xFFFF
    if corrupt_ck:
        ck ^= 0x5A5A
    struct.pack_into(">h", body, 4, ck if ck < 0x8000 else ck - 0x10000)
    return body

made["bare_gsrt_ulaw.bin"]   = gsrt_file(1000, 0)            # fs=756, len 1512, clean checksum
made["bare_gsrt_alaw.bin"]   = gsrt_file(1000, 8)
made["bare_gsrt_badck.bin"]  = gsrt_file(1000, 0, corrupt_ck=True)   # checksum warn on seekable only
made["bare_gsrt_fs0.bin"]    = gsrt_file(0, 0, body_len=640)         # fs=0 -> UNSPEC, checksum skipped everywhere
made["bare_gsrt_fsbig.bin"]  = gsrt_file(0, 8, fs_override=800, body_len=768)  # declared 1600B > actual 768B: seekable dies mid-checksum, pipe skips

def hcom_file(n_samp, divisor=2, datum=5, compresstype=1, first=0x80):
    """Minimal decodable HCOM (MacBinary shell): FSSD@65, HCOM@128,
    huffcount@132, checksum@136, compresstype@140, divisor@144, dictsize@148,
    dict entries (2x i16BE each), pad byte, then data."""
    b = bytearray(512)
    b[65:69] = b"FSSD"
    struct.pack_into(">I", b, 83, 200)       # datasize (informational)
    struct.pack_into(">I", b, 87, 0)         # rsrcsize
    b[128:132] = b"HCOM"
    struct.pack_into(">I", b, 132, n_samp)   # huffcount = emitted samples
    struct.pack_into(">I", b, 136, 0)        # checksum field
    struct.pack_into(">I", b, 140, compresstype)
    struct.pack_into(">I", b, 144, divisor)
    struct.pack_into(">H", b, 148, 2)        # dictsize = 2
    struct.pack_into(">h", b, 150, 1)        # dict0.left  -> node1 on bit 0
    struct.pack_into(">h", b, 152, 1)        # dict0.right -> node1 on bit 1
    struct.pack_into(">h", b, 154, -1)       # dict1.left < 0 -> leaf
    struct.pack_into(">h", b, 156, datum)    # dict1.right = datum
    # byte 158 = pad (skipped); data starts @159
    b[159] = first
    # huffman stream: all-zero bits -> left-branch -> leaf -> datum each bit
    b[160:168] = bytes(8)
    return b[:168]

made["bare_hcom_valid.bin"]   = hcom_file(16)
made["bare_hcom_div0.bin"]    = hcom_file(16, divisor=0)     # 'bad sampling rate divisor'
made["bare_hcom_baddict.bin"] = hcom_file(16, datum=5)       # will patch dict below
b = bytearray(made["bare_hcom_baddict.bin"]); struct.pack_into(">h", b, 154, 3)
made["bare_hcom_baddict.bin"] = b                            # dict1.left=3 out of range -> 'invalid dictionary'

# ------------------------------------------------------------- group N
# non-RIFF sufficiency + length boundaries (CHECK len >= p1+l1).
made["n_gsrt_24.bin"]  = shell(24,  {16: b"ring.bin"})                    # len<25 -> no match
made["n_gsrt_25.bin"]  = shell(25,  {16: b"ring.bin\x00"})                # boundary len
made["n_gsrt_riffsize.bin"] = shell(25, {16: b"ring.bin\x00"})            # same as 25 (dup name kept simple)
made["n_hcom_131.bin"] = shell(131, {65: b"FSSD", 128: b"HCO"})           # len<132 -> no match
made["n_hcom_132.bin"] = shell(132, {65: b"FSSD", 128: b"HCOM"})          # boundary len -> hcom
made["n_act_noRIFF.bin"] = shell(300, {256: b"\x84"})                     # 0x84@256 w/o RIFF -> none
made["n_gsrt_act.bin"] = shell(300, {16: b"ring.bin\x00", 256: b"\x84"})  # gsrt w/o RIFF; act conjunct unsatisfiable

# ------------------------------------------------------------- group M
# multi-preemptor ordering (non-RIFF shells; first match wins).
made["m_voc_gsrt.bin"]  = shell(64,  {0: b"Creative Voice File\x1a", 16: b"ring.bin\x00"})  # voc(78)<gsrt(81)
made["m_smp_gsrt.bin"]  = shell(64,  {0: b"SOUND SAMPLE DATA", 16: b"ring.bin\x00"})        # smp(79)<gsrt(81)
made["m_wve_gsrt.bin"]  = shell(64,  {0: b"ALawSoundFile**", 16: b"ring.bin\x00"})          # wve(80)<gsrt(81)
made["m_sph_gsrt.bin"]  = shell(64,  {0: b"NIST_1A", 16: b"ring.bin\x00"})                  # gsrt(81)<sph(84)
made["m_aiff_gsrt.bin"] = shell(64,  {0: b"FORM", 8: b"AIFF", 16: b"ring.bin\x00"})         # gsrt(81)<aiff(98)
made["m_au_gsrt.bin"]   = shell(64,  {0: b".snd", 16: b"ring.bin\x00"})                     # gsrt(81)<au(106)
made["m_gsrt_hcom.bin"] = shell(200, {16: b"ring.bin\x00", 65: b"FSSD", 128: b"HCOM"})      # gsrt(81)<hcom(90)
made["m_rifx_act.wav"]  = patch(base, {3: ord('X')})                                        # RIFX+0x84 -> wav row96, act needs RIFF
made["m_rf64_act.wav"]  = patch(base, spans={0: b"RF64"})                                     # RF64+0x84 -> wav row97
made["m_rifx_gsrt.wav"] = patch(base, {3: ord('X')}, {16: b"ring.bin\x00"})                 # RIFX + ring.bin -> gsrt
made["t_hcom_act.wav"]  = patch(base, spans={65: b"FSSD", 128: b"HCOM"})                    # hcom + act
made["t_gsrt_hcom_act.wav"] = patch(base, spans={16: b"ring.bin\x00", 65: b"FSSD",
                                                 128: b"HCOM"})                             # all three -> gsrt

# ------------------------------------------------------------- group F
# detect-then-fail: terminal error provenance shows which reader ran.
made["f_badnul.wav"]    = patch(base, spans={16: b"ring.bin\x80"})      # 9th byte != NUL -> NOT gsrt -> act
made["f_hcom_badcomp.wav"] = patch(base, {140: 0, 141: 0, 142: 0, 143: 5},
                                   spans={65: b"FSSD", 128: b"HCOM"})   # compresstype=5 -> 'bad compression type'
made["f_hcom_div9.wav"] = patch(base, {140:0,141:0,142:0,143:0, 144:0,145:0,146:0,147:9},
                                  spans={65: b"FSSD", 128: b"HCOM"})    # divisor 9 -> 'bad sampling rate divisor'

for name, data in made.items():
    p, n, sha = w(name, data)
    print(f"{name:26s} {n:6d} B  {sha[:16]}")
