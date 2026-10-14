#!/usr/bin/env python3
"""r66-scribe independent probes: wve CHECK predicate discovery + preemptor
decode-fate matrix + exact length gates. Own constructions — not the author's
r66 ramp carrier, not r65-scribe's JUNK family.

Families:
  P*  = wve predicate bisection (every byte of the 15-B literal load-bearing?
        len gate? is byte 15 free? '*' literal vs version digits?)
  Q*  = wve ordering probes (wve vs gsrt/hcom/act co-signatures; wve magic
        embedded inside a RIFF+0x84@256 file at nonzero offsets)
  R*  = wve reader fate (valid header -> decode; header-subset detection ->
        reject; num_samples vs data-length mismatch directions)
  S*  = hcom decodable-preemptor inside RIFF (own field values) + its fail
        ladder (compresstype / divisor / dictsize / dictionary / checksum /
        huffcount gates)
  T*  = gsrt decode fate (non-RIFF decodable carrier; RIFF collider file vs
        pipe transport fork = seekability conjunct)
  U*  = exact length gates on RIFF/WAVE shells + bare carriers (gsrt 24|25,
        hcom 131|132, wve 14|15, act 256|257)
"""
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
VAR = HERE / "variants"

WVE15 = b"ALawSoundFile**"                 # 15-B detector literal @0-14
WVE18 = WVE15 + b"\x00\x0f\x10"            # 18-B reader ID1
GSRT9 = b"ring.bin\x00"                    # 9-B detector literal @16-24
FSSD = b"FSSD"
HCOM = b"HCOM"


def fill(n, seed=0x35):
    """Deterministic nonzero-ish filler distinct from the author's ramp."""
    b = bytearray(n)
    x = seed
    for i in range(n):
        x = (x * 1103515245 + 12345) & 0x7FFFFFFF
        b[i] = (x >> 16) & 0xFF
    return b


def riff_pcm(n, rate=8000, ch=1, bits=16):
    """fmt-16 PCM RIFF/WAVE shell with deterministic payload @44..n."""
    b = fill(n)
    b[0:4] = b"RIFF"
    struct.pack_into("<I", b, 4, n - 8)
    b[8:12] = b"WAVE"
    if n >= 44:
        b[12:16] = b"fmt "
        struct.pack_into("<I", b, 16, 16)
        struct.pack_into("<H", b, 20, 1)
        struct.pack_into("<H", b, 22, ch)
        struct.pack_into("<I", b, 24, rate)
        struct.pack_into("<I", b, 28, rate * ch * bits // 8)
        struct.pack_into("<H", b, 32, ch * bits // 8)
        struct.pack_into("<H", b, 34, bits)
        b[36:40] = b"data"
        struct.pack_into("<I", b, 40, n - 44)
    return b


def wve_file(nsamp, data_byte=0xD5, total=None):
    """Fully reader-valid wve: ID1(18) + BE32 num_samples + 10-B pad + data."""
    n = total if total is not None else 32 + nsamp
    b = fill(n, seed=0x51)
    b[0:18] = WVE18
    struct.pack_into(">I", b, 18, nsamp)
    b[22:32] = bytes(10)                     # ID2 pad/repeat (ignored)
    for i in range(32, n):
        b[i] = data_byte
    return b


def hcom_chain(b, huffcount=5, checksum=0xC0FFEE00, compresstype=0, divisor=2,
               dictsize=2, dict0=(1, 1), dict1=(-1, 0x2A), first=0x77,
               word=0xC0FFEE00):
    """Install a reader-acceptable hcom field chain at the fixed offsets.
    divisor 2 -> 11025 Hz; dict: entry0 always steps to entry1 (leaf) so each
    Huffman bit emits datum; huffcount counts the first raw byte + leaves."""
    struct.pack_into(">I", b, 132, huffcount)
    struct.pack_into(">I", b, 136, checksum)
    struct.pack_into(">I", b, 140, compresstype)
    struct.pack_into(">I", b, 144, divisor)
    struct.pack_into(">H", b, 148, dictsize)
    struct.pack_into(">hh", b, 150, *dict0)
    struct.pack_into(">hh", b, 154, *dict1)
    b[158] = 0
    b[159] = first
    struct.pack_into(">I", b, 160, word)
    return b


def build():
    VAR.mkdir(exist_ok=True)
    specs = []

    def add(name, buf, ext=".bin"):
        specs.append((name, bytes(buf), ext))

    # ---------- P: wve predicate bisection ----------
    add("P01_wve_magic15", fill(280, 7)[:0] + WVE15 + fill(265, 11))
    # byte bisection: XOR 0xFF at each position 0-14 (author used ^0x01)
    for pos in range(15):
        m = bytearray(fill(280, 13))
        m[0:15] = WVE15
        m[pos] ^= 0xFF
        add(f"P02_x{pos:02d}", m)
    m = bytearray(fill(280, 17)); m[0:15] = WVE15; m[15] = 0x99
    add("P03_b15free", m)                    # byte 15 outside predicate?
    m = bytearray(fill(280, 19)); m[0:15] = WVE15[:13] + b"00"
    add("P04_stars00", m)                    # '**' -> '00': literal or wildcard?
    m = bytearray(fill(280, 23)); m[0:15] = WVE15[:13] + b"1A"
    add("P05_stars1A", m)                    # plausible real-version digits
    m = bytearray(fill(280, 29)); m[0:15] = WVE15[:12] + b"X**"
    add("P06_e12X", m)
    add("P07_len14", WVE15[:14])
    add("P08_len15", WVE15)
    add("P09_len18_badver", WVE15 + b"\x00\x00\x00" + fill(100, 31))  # ID1 tail wrong
    m = bytearray(fill(280, 37)); m[0:15] = WVE15.lower()
    add("P10_lowercase", m)                  # case sensitivity

    # ---------- Q: ordering — wve co-signatures ----------
    q = wve_file(64, 0xD5, total=300); q[16:25] = GSRT9
    add("Q01_wve+gsrt", q)                   # wve<gsrt (reader id bytes clobbered)
    q = wve_file(64, 0xD5, total=300); q[65:69] = FSSD; q[128:132] = HCOM
    q[256] = 0x84
    add("Q02_wve+hcom+84", q)                # wve<hcom; wve reader still decodes
    q = wve_file(64, 0xD5, total=300); q[16:25] = GSRT9; q[65:69] = FSSD
    q[128:132] = HCOM; q[256] = 0x84
    add("Q03_wve+gsrt+hcom+84", q)           # wve over everything (reader fails)
    q = wve_file(64, 0xD5, total=300); q[40:44] = b"RIFF"; q[256] = 0x84
    add("Q04_wve+riff@40", q)                # RIFF not at 0: act can't fire; wve wins
    # wve magic embedded inside a RIFF+0x84@256 file: unreachable rows
    for off in (16, 44, 64, 100, 200):
        b = riff_pcm(400)
        b[off:off + 15] = WVE15
        b[256] = 0x84
        add(f"Q1{off:03d}_riff_wveat{off}", b, ".wav")
    b = riff_pcm(400); b[4:19] = WVE15; b[256] = 0x84
    add("Q120_riff_wveat4", b, ".wav")       # magic inside the size field
    b = riff_pcm(400); b[0:4] = b"RIFX"; b[16:31] = WVE15; b[256] = 0x84
    add("Q121_rifx_wveat16", b, ".wav")
    # a file that is wve AND act would need ALaw@0 AND RIFF@0 — impossible;
    # closest legal shape: wve file whose byte256 is 0x84
    q = wve_file(64, 0xD5, total=300); q[256] = 0x84
    add("Q05_wve+84_noriff", q)

    # ---------- R: wve reader fate ----------
    add("R01_wve_dec64", wve_file(64, 0xD5))             # 64 A-law samples
    add("R02_wve_dec0", wve_file(0, 0xD5))               # num_samples=0, no data
    r = wve_file(32, 0xD5, total=96)                     # 64 B data > num 32
    add("R03_wve_num_lt_data", r)
    # num_samples > available bytes: header declares 500, file has 268 data B
    r = wve_file(0, 0xD5, total=300)
    struct.pack_into(">I", r, 18, 500)
    add("R04_wve_num_gt_data", r)
    r = fill(280, 41); r[0:15] = WVE15                   # 15-B magic only, zeroish tail
    add("R05_wve_det_only", r)                           # detect wve, reader rejects
    r = bytearray(wve_file(64, 0xD5)); r[15:18] = b"\x01\x02\x03"
    add("R06_wve_badver_dec", r)                         # detect wve; reader rejects

    # ---------- S: hcom decodable preemptor inside RIFF (own values) ----------
    s = riff_pcm(512)
    s[65:69] = FSSD
    s[128:132] = HCOM
    s = hcom_chain(s)                                    # 5 samples @11025 Hz
    s[256] = 0x84
    add("S01_hcom_dec_riff", s, ".wav")                  # detect hcom AND decode 5
    s2 = bytearray(s); s2[68] = ord("E")                 # FSSD broken: demote to act
    add("S02_hcom_demoted_act", s2, ".wav")
    s2 = bytearray(s); s2[131] = ord("N")                # HCOM broken: act
    add("S03_hcom_demoted_act131", s2, ".wav")
    s2 = bytearray(s); s2[256] = 0x00                    # no act byte: still hcom
    add("S04_hcom_dec_no84", s2, ".wav")
    # fail ladder (each detects hcom, reader stops at a named field)
    s2 = hcom_chain(riff_pcm(512), compresstype=7)
    s2[65:69] = FSSD; s2[128:132] = HCOM; s2[256] = 0x84
    add("S05_hcom_badcomp", s2, ".wav")
    s2 = hcom_chain(riff_pcm(512), divisor=9)
    s2[65:69] = FSSD; s2[128:132] = HCOM; s2[256] = 0x84
    add("S06_hcom_baddiv", s2, ".wav")
    s2 = hcom_chain(riff_pcm(512), dictsize=0)
    s2[65:69] = FSSD; s2[128:132] = HCOM; s2[256] = 0x84
    add("S07_hcom_dictsize0", s2, ".wav")
    s2 = hcom_chain(riff_pcm(512), dict0=(9, 9))         # entry0 out of range
    s2[65:69] = FSSD; s2[128:132] = HCOM; s2[256] = 0x84
    add("S08_hcom_baddict", s2, ".wav")
    s2 = hcom_chain(riff_pcm(512), checksum=0xDEADBEEF)  # cksum mismatch at close
    s2[65:69] = FSSD; s2[128:132] = HCOM; s2[256] = 0x84
    add("S09_hcom_badcksum", s2, ".wav")
    s2 = hcom_chain(riff_pcm(512), huffcount=9000)       # wants more bits than file
    s2[65:69] = FSSD; s2[128:132] = HCOM; s2[256] = 0x84
    add("S10_hcom_huff_big", s2, ".wav")
    s2 = hcom_chain(riff_pcm(512), huffcount=0)
    s2[65:69] = FSSD; s2[128:132] = HCOM; s2[256] = 0x84
    add("S11_hcom_huff0", s2, ".wav")
    s2 = hcom_chain(riff_pcm(512), compresstype=1)       # delta mode
    s2[65:69] = FSSD; s2[128:132] = HCOM; s2[256] = 0x84
    add("S12_hcom_delta", s2, ".wav")

    # ---------- T: gsrt decode fate ----------
    t = fill(700, 43)
    struct.pack_into(">I", t, 0, 0)          # file_size=0 -> checksum pass skipped
    t[16:25] = GSRT9
    struct.pack_into(">h", t, 32, 0)         # enc 0 -> u-law 8-bit
    add("T01_gsrt_dec_ulaw", t)              # non-RIFF carrier: open + decode 188
    t = fill(700, 47)
    struct.pack_into(">I", t, 0, 0)
    t[16:25] = GSRT9
    struct.pack_into(">h", t, 32, 8)         # enc 8 -> A-law
    add("T02_gsrt_dec_alaw", t)
    t = fill(700, 53)
    struct.pack_into(">I", t, 0, 0)
    t[16:25] = GSRT9
    struct.pack_into(">h", t, 32, 2)         # enc 2 -> G726 unsupported
    add("T03_gsrt_enc2", t)
    t = riff_pcm(600)                        # RIFF collider: checksum loop death on file
    t[16:25] = GSRT9
    struct.pack_into(">h", t, 32, 0)         # enc ulaw for the pipe leg
    t[256] = 0x84
    add("T04_gsrt_riff_collide", t, ".wav")  # file: premature EOF / pipe: decode
    t = riff_pcm(600)
    t[16:24] = b"ring.bin"; t[24] = 0x2E     # detector-stricter-than-reader:
    struct.pack_into(">h", t, 32, 0)         # NUL@24 broken -> detects act, but
    t[256] = 0x84                            # -t gsrt accepts on pipe
    add("T05_gsrt_badnul", t, ".wav")

    # ---------- U: exact length gates ----------
    g = riff_pcm(25); g[16:25] = GSRT9
    add("U01_gsrt25", g, ".wav")
    g = riff_pcm(24); g[16:24] = b"ring.bin"
    add("U02_gsrt24", g, ".wav")
    h = riff_pcm(132); h[65:69] = FSSD; h[128:132] = HCOM
    add("U03_hcom132", h, ".wav")
    h = riff_pcm(131); h[65:69] = FSSD; h[128:131] = b"HCO"
    add("U04_hcom131", h, ".wav")
    g = fill(25, 59); g[16:25] = GSRT9
    add("U05_gsrt25_bare", g)
    g = fill(24, 61); g[16:24] = b"ring.bin"
    add("U06_gsrt24_bare", g)
    h = fill(132, 67); h[65:69] = FSSD; h[128:132] = HCOM
    add("U07_hcom132_bare", h)
    h = fill(131, 71); h[65:69] = FSSD; h[128:131] = b"HCO"
    add("U08_hcom131_bare", h)
    add("U09_wve15_bare", WVE15)
    add("U10_wve14_bare", WVE15[:14])
    a = riff_pcm(257); a[256] = 0x84
    add("U11_act257", a, ".wav")
    a = riff_pcm(256)
    add("U12_act256", a, ".wav")

    return specs


def main():
    specs = build()
    man = VAR / "manifest.tsv"
    import hashlib
    with man.open("w") as fh:
        fh.write("name\tsha256\tbytes\n")
        for name, blob, ext in specs:
            p = VAR / f"{name}{ext}"
            p.write_bytes(blob)
            fh.write(f"{name}{ext}\t{hashlib.sha256(blob).hexdigest()}\t{len(blob)}\n")
    print(f"wrote {len(specs)} variants")


if __name__ == "__main__":
    main()
