#!/usr/bin/env python3
"""r64 critic: falsify the valid-bits step-map attribution (ffmpeg bridge).

Source-pinned mechanisms under test (n9.0.1):
  riffdec.c parse_waveformatex :62-92  bps=rl16; if(bps) bits_coded=bps;
             mask->ch_layout; guid: base-guid tail -> tag -> ff_wav_codec_get_id
             else guid-table lookup.
  riffdec.c ff_get_wav_header   :179-195 tag==0xfffe -> codec unset until
             extensible parse which needs declared cbSize>=22 AND fmt_size>=40.
  riffdec.c compute_bitrate     :99-138 recomp ba = ceil8(bps_coded)*ch;
             only overrides declared byte_rate*8 when consistent.
  pcm.c ff_pcm_default_packet_size :29-55 bits=av_get_bits_per_sample(codec_id);
             bitrate=bits*rate*ch (self-recomputed); nb=clip64(br/8/10/ba,1,INT_MAX/ba);
             max=ba*2^floor(log2(nb)); ba<=0 -> EINVAL -> wav.max_size=4096.
  wavdec.c wav_read_packet      :792-799 size=max_size rounded DOWN to declared ba
             (up to one ba if smaller); min(size,left).
  wavdec.c                      :664-674 hidden flips: s32le+ba==4ch+bps32+
             extradata{01 00} -> f16le; s24le+ba==4ch+bps24 -> f24le.
  pcmdec.c pcm_decode_frame     :431-443 n=ch*sample_size; buf<n -> EINVAL
             (packet dropped); else buf -= buf%n (residue drop).
  au.c codec_au_tags            :46-62  au on-wire encodings.

Probe record (TSV): name, codec, bps_coded, pkts, detected, nat_cnt, act_cnt,
act_exit, note.
"""
import os, re, struct, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
VAR = os.path.join(ROOT, "var")
RUNS = os.path.join(ROOT, "runs")
os.makedirs(VAR, exist_ok=True)
os.makedirs(RUNS, exist_ok=True)

BASE = open(os.path.join(ROOT, "..", "round-61", "pair_valid_17.wav"), "rb").read()
PAYLOAD = BASE[68:]
assert BASE[256] == 0x84 and len(PAYLOAD) == 11520

PCM_TAIL = bytes.fromhex("00001000800000aa00389b71")   # bytes 4..15 of KSDATAFORMAT GUID


def wav(tag=0xfffe, ch=1, rate=48000, br=None, ba=None, bps=16, cbsize=22,
        valid=17, mask=4, guid_tag=1, guid_tail=PCM_TAIL,
        ext_extra=b"", fmt_size=None, payload=None, data_decl=None,
        tail=b"", pin256=True):
    """Structural builder. fmt_size=None -> 40 (canonical extensible)."""
    if ba is None:
        ba = max(1, ((bps + 7) // 8) * ch)
    if br is None:
        br = rate * ba
    ext = struct.pack("<H", cbsize)
    ext += struct.pack("<H", valid) + struct.pack("<I", mask)
    ext += struct.pack("<I", guid_tag) + guid_tail
    ext += ext_extra
    fmt = struct.pack("<HHIIHH", tag, ch, rate, br, ba, bps) + ext
    if fmt_size is not None:
        assert fmt_size >= len(fmt) or fmt_size < len(fmt), fmt_size
        if fmt_size > len(fmt):
            fmt += b"\x00" * (fmt_size - len(fmt))
        else:
            fmt = fmt[:fmt_size]
    if payload is None:
        payload = PAYLOAD
    if data_decl is None:
        data_decl = len(payload)
    body = (b"fmt " + struct.pack("<I", len(fmt)) + fmt
            + b"data" + struct.pack("<I", data_decl) + payload + tail)
    blob = bytearray(b"RIFF" + struct.pack("<I", len(body) + 8) + b"WAVE" + body)
    if pin256 and len(blob) > 256 and blob[256] != 0x84:
        blob[256] = 0x84
    return bytes(blob)


def patch(mods):
    b = bytearray(BASE)
    for off, v in mods.items():
        b[off] = v
    return bytes(b)


DET = re.compile(r"detected file format type `([^']+)'")


def ffprobe_codec(path):
    p = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a:0",
         "-show_entries", "stream=codec_name,bits_per_coded_sample,channels",
         "-of", "csv=p=0", path], capture_output=True, timeout=20)
    return p.stdout.decode().strip() or "ERR:" + p.stderr.decode().strip()[:60]


def ffprobe_pkts(path):
    p = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a:0",
         "-show_entries", "packet=size", "-of", "csv=p=0", path],
        capture_output=True, timeout=20)
    sizes = [int(x) for x in p.stdout.decode().split() if x.strip().isdigit()]
    return sizes[:8] if len(sizes) > 8 else sizes


def sox_detect(path):
    p = subprocess.run(["sox", "-V4", path, "-n", "stat"],
                       capture_output=True, timeout=20)
    m = DET.search(p.stderr.decode(errors="replace"))
    return m.group(1) if m else "?"


def sox_count(path, forced=None):
    cmd = ["sox"] + (["-t", forced] if forced else []) + \
          [path, "-t", "f32", "-e", "floating-point", "-"]
    p = subprocess.run(cmd, capture_output=True, timeout=20)
    if p.returncode != 0:
        tail = p.stderr.decode(errors="replace").strip().splitlines()
        return "X%d:%s" % (p.returncode, (tail[-1][:60] if tail else ""))
    return str(len(p.stdout) // 4)


def au_enc(path):
    p = subprocess.run(["ffmpeg", "-loglevel", "quiet", "-nostdin", "-strict",
                        "-2", "-i", path, "-f", "au", "-"],
                       capture_output=True, timeout=20)
    d = p.stdout
    if len(d) < 24 or d[:4] != b".snd":
        return "-"
    return str(struct.unpack(">I", d[16:20])[0]) + "/" + str(len(d) - 24)


ROWS = []


def run(name, blob, note="", keep=False):
    path = os.path.join(VAR, name + ".wav")
    with open(path, "wb") as fh:
        fh.write(blob)
    codec = ffprobe_codec(path)
    pkts = ffprobe_pkts(path)
    det = sox_detect(path)
    nat = sox_count(path)
    act = sox_count(path, "act")
    rec = [name, codec, str(pkts), det, nat, act, note]
    ROWS.append(rec)
    print("\t".join(rec), flush=True)
    if not keep:
        pass
    return rec


def H(msg):
    print("## " + msg, flush=True)
    ROWS.append(["## " + msg, "", "", "", "", "", ""])


# ============ A: codec attribution — declared vs valid, structural gates =========
H("A1 declBPS x valid disagreement (patch 34/38 only; ba2 br96000)")
for decl, val in [(24, 16), (32, 8), (8, 24), (32, 16), (8, 57), (24, 32),
                  (64, 8), (0, 17), (24, 0), (32, 0), (0, 0), (57, 0), (16, 0)]:
    b = bytearray(BASE)
    struct.pack_into("<H", b, 34, decl)
    struct.pack_into("<H", b, 38, val)
    run(f"A1_d{decl}_v{val}", bytes(b), f"decl={decl} valid={val}")

H("A2 tag gate: same valid17 bytes, wFormatTag non-extensible")
run("A2_tag0001_pcm", patch({20: 0x01, 21: 0x00}), "tag=1: valid17 -> extradata?")
run("A2_tag0003_flt", patch({20: 0x03, 21: 0x00}), "tag=3 float,bps16->none?")
run("A2_tag0006_alaw", patch({20: 0x06, 21: 0x00}), "tag=6 alaw declared path")

H("A3 cbSize gate at fixed valid17 (patch @36 only)")
for cb in (0, 1, 20, 21, 22, 23, 24, 0xFFFF):
    b = bytearray(BASE)
    struct.pack_into("<H", b, 36, cb)
    run(f"A3_cb{cb}", bytes(b), f"cbSize={cb}")

H("A4 fmt_size gate (structural rebuild; valid17 GUID present)")
for fs, extra in ((16, b""), (18, b""), (38, b""), (39, b""), (40, b""),
                  (42, b"\xAA\xBB"), (64, b"\x00" * 24)):
    run(f"A4_fmt{fs}", wav(fmt_size=fs, ext_extra=extra), f"fmt_size={fs}")

H("A5 subformat GUID tag @44 (valid17; PCM tail kept)")
for t, lbl in ((1, "pcm"), (3, "float"), (6, "alaw"), (7, "mulaw"),
               (2, "adpcm_ms"), (0x11, "ima_adpcm"), (0x55, "mp3"),
               (0x2000, "ac3"), (0, "zero"), (0xFFFF, "ffff")):
    b = bytearray(BASE)
    struct.pack_into("<I", b, 44, t)
    run(f"A5_g{t:04x}_{lbl}", bytes(b), f"guidtag={t:#x}")

H("A6 GUID tail corruption @59 (0x71->0x72) + tail=0")
run("A6_tail72", patch({59: 0x72}), "guid tail not base -> guid-table lookup")
b = bytearray(BASE)
for i in range(48, 60):
    b[i] = 0
run("A6_tail00", bytes(b), "guid tail zeroed")

H("A7 valid high byte (offset39): 256/512/1024/4096/65535")
for v in (256, 512, 1024, 4096, 65535):
    b = bytearray(BASE)
    struct.pack_into("<H", b, 38, v)
    run(f"A7_v{v}", bytes(b), f"valid={v}")

H("A8 mask/channels/rate edge inputs (valid17)")
for name, kw in [("ch0_mask4", dict(ch=0, mask=4, ba=2, br=96000)),
                 ("ch0_mask0", dict(ch=0, mask=0, ba=2, br=96000)),
                 ("rate0", dict(rate=0, br=0)),
                 ("mask0", dict(mask=0)),
                 ("mask3", dict(mask=3))]:
    run("A8_" + name, wav(**kw), str(kw))

# ============ B: count law — packetization inputs beyond valid-bits ============
H("B1 block_align sweep at fixed valid17 (patch @32)")
for ba in (0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 16, 8192, 16384, 40000, 65535):
    b = bytearray(BASE)
    struct.pack_into("<H", b, 32, ba)
    run(f"B1_ba{ba}", bytes(b), f"ba={ba}")

H("B2 byte_rate sweep at fixed valid17 (patch @28)")
for br in (0, 1, 48000, 96000, 192000, 4000000, 0xFFFFFFFF):
    b = bytearray(BASE)
    struct.pack_into("<I", b, 28, br)
    run(f"B2_br{br}", bytes(b), f"byte_rate={br}")

H("B3 channels/stereo geometry")
run("B3_ch2_v17", wav(ch=2, bps=16, ba=4, br=192000), "stereo v17, ba4")
run("B3_ch2_v24", wav(ch=2, bps=16, ba=4, br=192000, valid=24), "stereo v24 ba4")
run("B3_ch2_v24_ba8", wav(ch=2, bps=16, ba=8, br=384000, valid=24), "stereo v24 ba8")
run("B3_ch3_v17", wav(ch=3, bps=16, ba=6, br=288000), "3ch v17 ba6")
run("B3_ch1_ba4_v17", wav(ch=1, bps=16, ba=4, br=192000), "mono v17 ba4 (ba==ch*4 but bps17)")

H("B4 data_size edges (valid17; natural route needs len>256)")
for n in (1, 2, 3, 4, 6, 7, 8, 189, 8190, 8191, 8192, 8193, 8194, 8195, 8196,
          11517, 11518, 11519, 11520, 11521, 16383, 16384, 16385, 16387,
          32768, 32769, 32771, 40000):
    pl = PAYLOAD[:n] + (bytes(((i * 7 + 13) & 0xFF) for i in range(max(0, n - 11520)))
                        if n > 11520 else b"")
    run(f"B4_n{n}", wav(payload=pl[:n]), f"data={n}")

H("B5 declared data_size vs physical payload")
run("B5_decl8192", wav(data_decl=8192), "decl 8192 < phys 11520")
run("B5_decl11520_phys8192", wav(payload=PAYLOAD[:8192], data_decl=11520),
    "decl 11520 > phys 8192")
run("B5_decl6", wav(data_decl=6), "decl 6 < phys")
run("B5_decl20000", wav(data_decl=20000), "decl 20000 > phys 11520")

H("B6 data-chunk continuation (find_tag after data_end)")
run("B6_8194+data3000", wav(payload=PAYLOAD[:8194],
    tail=b"data" + struct.pack("<I", 3000) + PAYLOAD[8194:8194 + 3000]),
    "chunk1 8194(subframe tail)+data2 3000")
run("B6_8192+data3000", wav(payload=PAYLOAD[:8192],
    tail=b"data" + struct.pack("<I", 3000) + PAYLOAD[8192:8192 + 3000]),
    "chunk1 8192 + data2 3000")
run("B6_8192+junk+data3000", wav(payload=PAYLOAD[:8192],
    tail=b"JUNK" + struct.pack("<I", 16) + b"\x00" * 16
         + b"data" + struct.pack("<I", 3000) + PAYLOAD[8192:8192 + 3000]),
    "chunk1 8192 + JUNK + data2")
run("B6_full+data3000", wav(tail=b"data" + struct.pack("<I", 3000) + PAYLOAD[:3000]),
    "full 11520 + data2 3000")
run("B6_tail_text", wav(tail=b"data" + struct.pack("<I", 0xFFFFFFFF)),
    "tail 'data'+size=0xFFFFFFFF (overread probe)")
run("B6_tail_fakedata_in_payload", wav(payload=PAYLOAD[:8192] + b"data" +
    struct.pack("<I", 4000) + PAYLOAD[8196:8196 + 4000]),
    "payload region containing 'data' tag+size inside data chunk")

H("B7 hidden codec flips via block_align/extradata")
run("B7_v24_ba4", wav(ba=4, br=192000, valid=24), "v24+ba4 mono -> f24le?")
run("B7_v24_ba2", wav(ba=2, br=96000, valid=24), "v24+ba2 control")
run("B7_v17_ba4", wav(ba=4, br=192000, valid=17), "v17+ba4 (bps!=24 no flip)")
run("B7_v32_ba4_ext1", wav(ba=4, br=192000, valid=32, cbsize=24,
    ext_extra=b"\x01\x00"), "v32+ba4+cb24+ext{01 00} -> f16le?")
run("B7_v32_ba4_ext0", wav(ba=4, br=192000, valid=32, cbsize=24,
    ext_extra=b"\x00\x00"), "v32+ba4+cb24+ext{00 00} control")
run("B7_v32_ba2_ext1", wav(ba=2, br=96000, valid=32, cbsize=24,
    ext_extra=b"\x01\x00"), "v32+ba2+ext{01} ba!=4 control")

# ============ C: ffprobe-vs-SoX contradictions + fallback probing ============
H("C1 channels=0 -> decoder EINVAL while ffprobe names codec")
run("C1_ch0", wav(ch=0, mask=4, ba=2, br=96000), "ch=0 mask=4")
run("C1_ch0_m0", wav(ch=0, mask=0, ba=2, br=96000), "ch=0 mask=0")

H("C2 non-PCM subformat codecs vs count law (valid17)")
b = bytearray(BASE); struct.pack_into("<I", b, 44, 3)
run("C2_float_v17", bytes(b), "float GUID + v17 -> flt17 none?")
b = bytearray(BASE); struct.pack_into("<I", b, 44, 3); struct.pack_into("<H", b, 38, 32)
run("C2_float_v32", bytes(b), "float GUID + v32 -> f32le")
b = bytearray(BASE); struct.pack_into("<I", b, 44, 3); struct.pack_into("<H", b, 38, 24)
run("C2_float_v24", bytes(b), "float GUID + v24 -> none hole")

H("C3 au wire encoding per negotiated codec")
for v in (1, 9, 17, 25, 32, 57, 64):
    b = bytearray(BASE); struct.pack_into("<H", b, 38, v)
    p = os.path.join(VAR, f"C3_v{v}.wav")
    with open(p, "wb") as fh:
        fh.write(b)
    print(f"C3_v{v}\tau_enc={au_enc(p)}\tcodec={ffprobe_codec(p)}", flush=True)

H("C4 valid=0 fallback reads DECLARED bps")
# (folded into A1 rows d{24,32,57,0}_v0)

H("C5 native-route contrast on codec-NONE variant")
b = bytearray(BASE); struct.pack_into("<H", b, 38, 33)
p = os.path.join(VAR, "C5_v33.wav")
open(p, "wb").write(bytes(b))
for t in (None, "wav", "act"):
    r = sox_count(p, t)
    print(f"C5_v33 forced={t}: {r}", flush=True)

with open(os.path.join(RUNS, "probe-results.tsv"), "w") as fh:
    fh.write("name\tcodec\tpkts\tdetected\tnat_cnt\tact_cnt\tnote\n")
    for r in ROWS:
        fh.write("\t".join(r) + "\n")
print("WROTE", os.path.join(RUNS, "probe-results.tsv"))
