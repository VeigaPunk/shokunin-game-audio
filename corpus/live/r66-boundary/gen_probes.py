#!/usr/bin/env python3
"""r66-boundary probe generator — preemptor-map edge probes.

Families:
  a_*  wve CHECK predicate identification (magic bytes, len floor, pos/value sweeps)
  b_*  wve ordering on wve carriers (wve vs gsrt/hcom/act-sig; decodable wve+hcom)
  c_*  RIFF carriers revisited (wve magic embedded at non-0 offset = inert)
  d_*  RIFX/RF64 variants of the collision family
  e_*  co-satisfaction with post-act rows (avi@8, ftyp@4) — earliest wins?
  g_*  unmapped rows 82..89 (amr-wb,prc,sph,amr-nb,txw,sndt,vorbis,opus) vs gsrt/hcom
  n_*  length-gate pins (wve 14|15, reader 31|32, gsrt 24|25, hcom 131|132)
  z_*  controls (bare gsrt/hcom decodable, riff act base)

Layout notes (formats.c:78-97 + readers):
  wve detect : bytes 0..14 == "ALawSoundFile**", len>=15
  wve reader : ID1[18] = magic + 00 0f 10, num_samples BE32 @18, ID2 pad @22..31,
               A-law data @32.  So gsrt's ring.bin@16 destroys reader bytes 16-17.
  gsrt detect: "ring.bin\\0" @16..24, len>=25
  hcom detect: "FSSD"@65..68 AND "HCOM"@128..131, len>=132
  act detect : "RIFF"@0 AND 0x84@256, len>=257
  wav detect : RIFF|RIFX|RF64 @0 AND "WAVE"@8
"""
import os, struct

P = "probes"
SW = os.path.join(P, "sweep")
os.makedirs(SW, exist_ok=True)
W = {}

def put(name, data, sweep=False):
    W[(name, sweep)] = bytes(data)

# ---- signatures -------------------------------------------------------------
WVE   = b"ALawSoundFile**"                    # @0 len 15 (CHECK wve)
WVE1  = WVE + b"\x00\x0f\x10"                  # reader ID1, 18 bytes
GSRT  = b"ring.bin\x00"                        # @16 len 9 (CHECK gsrt)
FSSD  = b"FSSD"; HCOM = b"HCOM"                # @65 / @128
ACTB  = 0x84                                   # @256 with RIFF@0

def wve_file(nsamp, total=None):
    """32-byte wve header + payload; total pads file out."""
    h = bytearray(32)
    h[0:18] = WVE1
    h[18:22] = struct.pack(">I", nsamp)
    if total is None:
        total = 32 + nsamp
    h.extend(bytearray(total - 32))
    return h

def hcom_chain(buf):
    """Embed the r65-critic D1 decodable hcom chain verbatim at absolute
    offsets 65..166: FSSD@65, HCOM@128, huffcount=9@132, cksum@136,
    compresstype=0@140, divisor=1@144, dictsize=2@148, dict@150..157,
    pad@158, compressed data@159..166 (decodes 9 samples @22050)."""
    d1 = bytes.fromhex(
        "46535344"                                      # 65-68 FSSD
        "e6edf4fb020910171e252c333a41484f565d646b727980"  # 69-87 (datasize area)
        "878e959ca3aab1b8bfc6cdd4dbe2e9f0f7fe050c"      # 88-109
        "131a21282f363d444b525960676e757c"              # 110-127
        "48434f4d"                                      # 128-131 HCOM
        "00000009"                                      # 132-135 huffcount=9
        "a5a5a5a5"                                      # 136-139 checksum
        "00000000"                                      # 140-143 compresstype=0
        "00000001"                                      # 144-147 divisor=1
        "0002"                                          # 148-149 dictsize=2
        "00010001ffff0000"                              # 150-157 dict[2] (e0 l1 r1; e1 l-1 r0)
        "00"                                            # 158 pad
        "40a5a5a5a57f868d"                              # 159-166 compressed data
    )
    buf[65:65+len(d1)] = d1
    return buf

def riff_prelude(buf, magic=b"RIFF", waveid=b"WAVE", actbyte=True):
    buf[0:4] = magic
    buf[4:8] = struct.pack("<I", len(buf) - 8)
    buf[8:12] = waveid
    if actbyte:
        buf[256] = ACTB
    return buf

# =============================================================================
# A. wve predicate identification
# =============================================================================
put("a_wve_magic15.bin", WVE)                              # len 15 floor hit
put("a_wve_14.bin", WVE[:14])                              # len 14 -> no detect
put("a_wve_magic15_pad.bin", WVE + bytes(49))              # 64B: detect + reader EOF
put("a_wve_valid.bin", wve_file(16))                       # decodable: 16 alaw @8k
put("a_wve_valid0.bin", wve_file(0))                       # 32B, nsamp=0 -> open/0
b = wve_file(16, 64); b[15:18] = b"XYZ"
put("a_wve_badid.bin", b)                                  # detect wve, reader: Psion id fail
# position sweep: each magic byte 0..14 mutated once (len 64 so len isn't the gate)
for pos in range(15):
    m = bytearray(64); m[0:15] = WVE
    m[pos] = 0x41 if WVE[pos] != 0x41 else 0x42           # flip to 'A' or 'B'
    put(f"a_wve_pos{pos:02d}_mut.bin", m)
# value sweeps at pos 0, 7, 14 (256 each; len 64) — detect-only probes
for pos in (0, 7, 14):
    for v in range(256):
        m = bytearray(64); m[0:15] = WVE; m[pos] = v
        put(f"sw_wve_p{pos:02d}_v{v:02x}.bin", m, sweep=True)

# =============================================================================
# B. wve ordering on wve carriers
# =============================================================================
put("b_wve_dec.bin", wve_file(100))                        # decodable 100 alaw

b = bytearray(300); b[0:15] = WVE; b[16:25] = GSRT; b[256] = ACTB
put("b_wve_gsrt.bin", b)                                   # wve+gsrt sig: detect wve, reader dies (b16-17='ri')

b = wve_file(268, 300)                                     # decodable wve, 268 alaw
hcom_chain(b)                                              # FSSD@65+HCOM@128+chain @132-166
b[256] = ACTB                                              # inert (no RIFF@0)
put("b_wve_hcomsig_dec.bin", b)                            # wve detect + DECODES; hcom sig live

b2 = bytearray(b); b2[0] = 0x42                            # 'B'awSoundFile** — break wve magic
put("b_xve_hcomsig_dec.bin", b2)                           # mate: wve magic dead -> hcom detect+decode

b = bytearray(300); b[0:15] = WVE; b[16:25] = GSRT
hcom_chain(b); b[256] = ACTB
put("b_wve_gsrt_hcom.bin", b)                              # wve wins quad-match; reader dies

b = wve_file(50, 300); b[256] = ACTB
put("b_wve_dec_actbyte.bin", b)                            # decodable wve + lone 0x84@256

# =============================================================================
# C. RIFF carriers — wve magic embedded away from @0 is inert
# =============================================================================
b = riff_prelude(bytearray(300)); b[16:31] = WVE
put("c_riff_wve16_act.wav", b)                             # RIFF+wve@16+0x84 -> act (wve needs @0)

b = riff_prelude(bytearray(300)); b[16:25] = GSRT; b[40:55] = WVE
put("c_riff_gsrt_wve40.wav", b)                            # gsrt wins; wve@40 inert

b = riff_prelude(bytearray(300)); b[16:31] = WVE; b[65:69] = FSSD; b[128:132] = HCOM
put("c_riff_wve16_hcom.wav", b)                            # hcom(90) < act(93); wve@16 inert

# =============================================================================
# D. RIFX / RF64 variants
# =============================================================================
b = riff_prelude(bytearray(300), magic=b"RIFX")
put("d_rifx_act.wav", b)                                   # wav row96 (act needs RIFF literal)

b = riff_prelude(bytearray(300), magic=b"RIFX"); hcom_chain(b)
put("d_rifx_hcom.wav", b)                                  # hcom(90) < wav(96)? (+ decode 9?)

b = riff_prelude(bytearray(300), magic=b"RF64"); hcom_chain(b)
put("d_rf64_hcom.wav", b)                                  # hcom(90) < wav(97)?

b = riff_prelude(bytearray(300), magic=b"RIFX"); b[16:25] = GSRT
put("d_rifx_gsrt.wav", b)                                  # gsrt control

b = riff_prelude(bytearray(300), magic=b"RF64")
put("d_rf64_act.wav", b)                                   # wav row97

# =============================================================================
# E. post-act row co-satisfaction — earliest still wins?
# =============================================================================
b = riff_prelude(bytearray(300)); b[8:12] = b"AVI "
put("e_riff_avi_act.wav", b)                               # act(93) < avi(176)

b = riff_prelude(bytearray(300)); b[8:12] = b"AVI "; b[16:25] = GSRT
put("e_riff_avi_gsrt.wav", b)                              # gsrt(81) < act < avi

b = riff_prelude(bytearray(300)); b[8:12] = b"AVI "; hcom_chain(b)
put("e_riff_avi_hcom.wav", b)                              # hcom(90) < act < avi

b = bytearray(300); b[4:12] = b"ftypisom"; b[16:25] = GSRT; b[256] = ACTB
put("e_ftyp_gsrt.bin", b)                                  # gsrt(81) < mp4(216)

b = bytearray(300); b[4:12] = b"ftypisom"; hcom_chain(b)
put("e_ftyp_hcom.bin", b)                                  # hcom(90) < mp4(216)

b = riff_prelude(bytearray(300)); b[4:12] = b"ftypisom"    # clobbers RIFF size field
put("e_riff_ftyp_act.wav", b)                              # act(93) < mp4(216)

b = wve_file(168, 300); b[32:40] = b"ftypisom"             # ftyp buried in payload
put("e_wve_ftyp32.bin", b)                                 # wve; interior ftyp inert

# =============================================================================
# G. rows 82..89 vs gsrt / hcom  (unmapped CHECK rows between wve and wav)
# =============================================================================
ROWS = {
    "amrwb":  b"#!AMR-WB\n",                               # 82
    "prc":    b"\x37\x00\x00\x10\x6d\x00\x00\x10",          # 83
    "sph":    b"NIST_1A",                                   # 84
    "amrnb":  b"#!AMR\n",                                   # 85
    "txw":    b"LM8953",                                    # 86
    "sndt":   b"SOUND\x1a",                                 # 87
}
for name, magic in ROWS.items():
    b = bytearray(300); b[0:len(magic)] = magic; b[16:25] = GSRT; b[256] = ACTB
    put(f"g_{name}_gsrt.bin", b)                            # predict gsrt (81 < row)
    b = bytearray(300); b[0:len(magic)] = magic; hcom_chain(b)
    put(f"g_{name}_hcom.bin", b)                            # predict row (<90) wins over hcom
    b = bytearray(300); b[0:len(magic)] = magic; b[256] = ACTB
    put(f"g_{name}_actbyte.bin", b)                         # row alone + 0x84 (no RIFF)

# vorbis(88): OggS@0 + vorbis@29 ; opus(89): OggS@0 + OpusHead@28
b = bytearray(300); b[0:4] = b"OggS"; b[29:35] = b"vorbis"; b[16:25] = GSRT
put("g_vorbis_gsrt.bin", b)
b = bytearray(300); b[0:4] = b"OggS"; b[28:36] = b"OpusHead"; b[16:25] = GSRT
put("g_opus_gsrt.bin", b)
b = bytearray(300); b[0:4] = b"OggS"; b[29:35] = b"vorbis"; hcom_chain(b)
put("g_vorbis_hcom.bin", b)                                 # vorbis(88) < hcom(90)
b = bytearray(300); b[0:4] = b"OggS"; b[28:36] = b"OpusHead"; hcom_chain(b)
put("g_opus_hcom.bin", b)                                   # opus(89) < hcom(90)
b = bytearray(300); b[0:4] = b"OggS"; b[29:35] = b"vorbis"; b[256] = ACTB
put("g_vorbis_actbyte.bin", b)
# vorbis/opus secondary bytes embedded in a RIFF+0x84 file: @0 conjunct fails
b = riff_prelude(bytearray(300)); b[29:35] = b"vorbis"
put("g_riff_vorbis29_act.wav", b)
b = riff_prelude(bytearray(300)); b[28:36] = b"OpusHead"
put("g_riff_opus28_act.wav", b)

# =============================================================================
# N. length-gate pins
# =============================================================================
put("n_wve_14.bin", WVE[:14])
put("n_wve_15.bin", WVE)
put("n_wve_31.bin", bytes(wve_file(0))[:31])                # detect wve; reader EOF mid-ID2
put("n_wve_32.bin", bytes(wve_file(0))[:32])                # detect + open, 0 samples
for L in (24, 25):
    m = bytearray(L); m[16:L] = GSRT[:L-16]
    put(f"n_gsrt_{L}.bin", m)
for L in (131, 132):
    m = bytearray(L); m[65:69] = FSSD; m[128:L] = HCOM[:L-128]
    put(f"n_hcom_{L}.bin", m)

# =============================================================================
# Z. controls — bare decodable gsrt / hcom, plain act base
# =============================================================================
b = bytearray(1512)
struct.pack_into(">I", b, 0, 756)                          # file_size=756 -> 1000 samples
b[16:25] = GSRT                                            # id@16 + pad
b[32:34] = struct.pack(">h", 0)                            # enc 0 -> ulaw
put("z_gsrt_ulaw.bin", b)                                  # gsrt decode (file: checksum warn ok)

b = bytearray(200); hcom_chain(b)
put("z_hcom_dec.bin", b)                                   # hcom detect + 9-sample decode

b = riff_prelude(bytearray(300))
put("z_riff_act.wav", b)                                   # plain act

b = riff_prelude(bytearray(300), actbyte=False)
put("z_riff_00.wav", b)                                    # wav control

n_main = n_sw = 0
for (name, sweep), d in sorted(W.items()):
    d_dir = SW if sweep else P
    with open(os.path.join(d_dir, name), "wb") as f:
        f.write(d)
    if sweep: n_sw += 1
    else: n_main += 1
print(f"{n_main} matrix fixtures -> {P}/ ; {n_sw} sweep fixtures -> {SW}/")
