#!/usr/bin/env python3
"""r66 author sweep: wve predicate identification + decodable-preemptor pair
candidates + length-gate boundary constructions.

Families:
  W*  = wve CHECK row probes (identify the predicate empirically; try every
        RIFF-family placement that could let wve fire on a RIFF file)
  D*  = hcom-decodable pair candidates (D1-equivalent + sole-byte demotions)
  L*  = length-gate boundary members (gsrt 24|25, hcom 131|132)
  X*  = cross-checks (wve vs gsrt/hcom on non-RIFF; wve reader on RIFF)

Probes per variant: `sox -V6 <f> -n stat` (detected/samples/exit), `sox --i`,
raw f32 decode, forced -t legs {act,gsrt,hcom,wve,wav}, ffprobe codec/duration.
Writes variants/* + results.tsv (one row per variant).
"""
import math
import re
import struct
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
VAR = HERE / "variants"
RATE = 48000

WVE = b"ALawSoundFile**"          # candidate 15-byte magic @0-14
GSRT = b"ring.bin\x00"            # 9 bytes @16-24
FSSD = b"FSSD"                    # @65-68
HCOM = b"HCOM"                    # @128-131


def base_riff(n=600):
    """Minimal RIFF/WAVE skeleton: fmt16 PCM16 mono 8kHz + data chunk,
    deterministic ramp payload (r65-critic construction, greppable)."""
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


def hcom_fields(b):
    """hcom reader fields so startread accepts and decodes (r65-critic D1):
    huffcount@132 BE=9, checksum@136 BE, compresstype@140 BE<=1,
    divisor@144 BE in 1..4, dictsize@148 BE in 1..511, dict entries 4B each,
    pad@158, first raw sample@159, Huffman word@160-163 (== checksum)."""
    struct.pack_into(">I", b, 132, 9)
    word = 0xA5A5A5A5
    struct.pack_into(">I", b, 136, word)
    struct.pack_into(">I", b, 140, 0)
    struct.pack_into(">I", b, 144, 1)      # divisor 1 -> 22050 Hz
    struct.pack_into(">H", b, 148, 2)      # dictsize 2
    struct.pack_into(">hh", b, 150, 1, 1)  # dict[0] -> entry 1
    struct.pack_into(">hh", b, 154, -1, 0) # dict[1] leaf, datum 0
    b[158] = 0
    b[159] = 0x40
    struct.pack_into(">I", b, 160, word)
    return b


def build():
    VAR.mkdir(exist_ok=True)
    specs = []

    def add(name, buf, ext=".wav"):
        specs.append((name, bytes(buf), ext))

    # ---------- W: wve predicate identification + RIFF attempts ----------
    w = bytearray(300); w[0:15] = WVE
    add("W01_wve_bare", w, ".bin")                       # positive control
    w2 = bytearray(w); w2[16:25] = GSRT; w2[256] = 0x84
    add("W02_wve+gsrt+84", w2, ".bin")                   # coexistence: wve vs gsrt
    w3 = bytearray(w2); w3[65:69] = FSSD; w3[128:132] = HCOM
    add("W03_wve+gsrt+hcom+84", w3, ".bin")              # wve vs gsrt vs hcom
    w4 = bytearray(w); w4[65:69] = FSSD; w4[128:132] = HCOM; w4[256] = 0x84
    add("W04_wve+hcom+84", w4, ".bin")                   # wve vs hcom only
    add("W05_wve_len14", bytearray(w[:14]), ".bin")      # len gate: 14
    add("W06_wve_len15", bytearray(w[:15]), ".bin")      # len gate: 15
    add("W07_wve_len16", bytearray(w[:16]), ".bin")      # len gate: 16
    # byte-exactness: flip one byte at each position 0-14
    for pos in range(15):
        m = bytearray(w); m[pos] ^= 0x01
        add(f"W10{pos:02d}_wve_x{pos}", m, ".bin")
    m = bytearray(w); m[14] = ord('?')                   # last '*' -> '?'
    add("W25_wve_x14q", m, ".bin")
    m = bytearray(w); m[15] = 0xAA                       # byte15 free?
    add("W26_wve_b15aa", m, ".bin")
    # magic at nonzero offsets inside a RIFF+0x84 file
    for off in (4, 8, 12, 15, 16, 36, 44, 64, 128, 252):
        b = base_riff(300); b[256] = 0x84
        if off + 15 <= len(b):
            b[off:off+15] = WVE
            add(f"W3{off:02d}_riff+wve@{off}", b)
    # RIFX / RF64 heads + wve magic placed after the tag
    b = base_riff(300); b[0:4] = b"RIFX"; b[16:31] = WVE; b[256] = 0x84
    add("W40_rifx+wve@16", b)
    b = base_riff(300); b[0:4] = b"RF64"; b[16:31] = WVE; b[256] = 0x84
    add("W41_rf64+wve@16", b)
    # wve file carrying a fake RIFF deeper inside (control: content vs name)
    w8 = bytearray(w); w8[32:36] = b"RIFF"; w8[256] = 0x84
    add("W42_wve+riff@32", w8, ".bin")
    # wve magic that overlaps the RIFF tag differently: "RIFF" can never be
    # "ALaw" at byte0, but test whether a prefix inside RIFF size field helps
    b = base_riff(300); b[4:19] = WVE; b[256] = 0x84     # magic@4 over size field
    add("W43_riff+wve@4b", b)
    # ---------- D: hcom-decodable pair candidates (D1-equivalent) ----------
    d = hcom_fields(base_riff(600))
    d[65:69] = FSSD; d[128:132] = HCOM; d[256] = 0x84
    add("D01_hcomdecode+act", d)                          # the tracked-shape candidate
    d2 = bytearray(d); d2[68] = ord('E')                  # sole byte @68 'D'->'E'
    add("D02_dec68x+act", d2)
    d3 = bytearray(d); d3[131] = ord('X')                 # sole byte @131 'M'->'X'
    add("D03_dec131x+act", d3)
    d4 = bytearray(d); d4[256] = 0x00                     # same, no act byte
    add("D04_hcomdecode_00", d4)
    # ---------- L: length-gate boundary members ----------
    g = base_riff(25); g[16:25] = GSRT                    # len 25, sig complete
    add("L01_gsrt_len25", g)
    g = base_riff(24); g[16:24] = b"ring.bin"             # len 24, sig truncated by EOF
    add("L02_gsrt_len24", g)
    h = base_riff(132); h[65:69] = FSSD; h[128:132] = HCOM
    add("L03_hcom_len132", h)
    h = base_riff(131); h[65:69] = FSSD; h[128:131] = b"HCO"
    add("L04_hcom_len131", h)
    # non-RIFF len-gate cross-check (boundary's n_* shapes)
    g = bytearray(25); g[16:25] = GSRT
    add("L05_gsrt25_noriff", g, ".bin")
    g = bytearray(24); g[16:24] = b"ring.bin"
    add("L06_gsrt24_noriff", g, ".bin")
    h = bytearray(132); h[65:69] = FSSD; h[128:132] = HCOM
    add("L07_hcom132_noriff", h, ".bin")
    h = bytearray(131); h[65:69] = FSSD; h[128:131] = b"HCO"
    add("L08_hcom131_noriff", h, ".bin")
    # ---------- X: wve reader on a RIFF file; gsrt-enc decodables ----------
    add("X01_riff_forced_wve", base_riff(300))
    x = base_riff(300); x[16:25] = GSRT; struct.pack_into(">h", x, 32, 0); x[256] = 0x84
    add("X02_gsrtULAW+act", x)
    return specs


DET = re.compile(r"detected file format type `(\S+?)'")
SAMPLES = re.compile(r"Samples read:\s*(\d+)")


def run(*args, stdin=None):
    p = subprocess.run(args, capture_output=True, input=stdin)
    return p.returncode, p.stdout, p.stderr


def tail(b, n=140):
    lines = b.decode(errors="replace").strip().splitlines()
    return lines[-1][-n:] if lines else ""


def probe(name, ext):
    f = str(VAR / f"{name}{ext}")
    row = {"name": name + ext}
    rc, out, err = run("sox", "-V6", f, "-n", "stat")
    det = DET.search(err.decode(errors="replace"))
    smp = SAMPLES.search(err.decode(errors="replace"))
    row["detected"] = det.group(1) if det else "NONE"
    row["rc"] = rc
    row["samples"] = smp.group(1) if smp else "-"
    row["tail"] = tail(err)
    for t in ("wve", "act", "wav"):
        rc, out, err = run("sox", "-t", t, f, "-n", "stat")
        smp = SAMPLES.search(err.decode(errors="replace"))
        row[f"t_{t}"] = f"rc={rc} smp={smp.group(1) if smp else '-'} {tail(err, 80)}"
    rc, out, err = run("sox", f, "-t", "f32", "-e", "floating-point", "-")
    row["dec"] = f"rc={rc} bytes={len(out)}"
    rc, out, err = run("ffprobe", "-v", "error", "-show_entries",
                       "stream=codec_name:format=duration", "-of", "json", f)
    row["ffprobe"] = (out.decode(errors="replace").strip().replace("\n", " ")[:120]
                      if rc == 0 else f"rc={rc} {tail(err, 80)}")
    return row


def main():
    specs = build()
    rows = []
    for name, blob, ext in specs:
        (VAR / f"{name}{ext}").write_bytes(blob)
        rows.append(probe(name, ext))
    fields = ["name", "detected", "rc", "samples", "tail", "t_wve", "t_act",
              "t_wav", "dec", "ffprobe"]
    with (HERE / "results.tsv").open("w") as fh:
        fh.write("\t".join(fields) + "\n")
        for r in rows:
            fh.write("\t".join(str(r.get(k, "")) for k in fields) + "\n")
    for r in rows:
        print(f"{r['name']:28s} det={r['detected']:6s} rc={r['rc']} smp={r['samples']:>6s} | {r['tail'][:70]}")


if __name__ == "__main__":
    main()
