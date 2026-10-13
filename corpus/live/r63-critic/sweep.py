#!/usr/bin/env python3
"""r63 critic: falsify/map the SoX_ng `act` autodetect predicate.

Claim under test (r62): `CHECK(act, 0,4,"RIFF", 256,1,"\\x84")` in
sox_ng-14.8.0.1 formats.c:93 — i.e. file[0:4]=="RIFF" AND file[256]==0x84 AND
len>=257 — checked before wav (formats.c:95-97), and `act` resolves to the
(ffmpeg) pseudo-handler (ffmpeg.c names[]).

Probe: `sox -V6 <f> -n` → parse `detected file format type `X'` and the
`(ffmpeg)` handler marker. One exec per variant; mass sweeps reuse one temp
path; named exhibits are kept under var/.
"""
import csv, os, re, struct, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
VAR = os.path.join(ROOT, "var")
os.makedirs(VAR, exist_ok=True)
BASE17 = open(os.path.join(ROOT, "pair_valid_17.wav"), "rb").read()
BASE16 = open(os.path.join(ROOT, "pair_valid_16.wav"), "rb").read()
TMP = os.path.join(VAR, "_tmp.wav")

DET = re.compile(r"detected file format type `([^']+)'")
INP = re.compile(r"Input File\s+: '([^']+)'(\s*\(ffmpeg\))?")
FAIL = re.compile(r"sox FAIL .*")


def probe(path, forced=None):
    cmd = ["sox", "-V6"] + (["-t", forced] if forced else []) + [path, "-n"]
    p = subprocess.run(cmd, capture_output=True, timeout=15)
    out = (p.stdout + p.stderr).decode("utf-8", errors="replace")
    m = DET.search(out)
    detected = m.group(1) if m else ""
    h = INP.search(out)
    handler = "ffmpeg" if (h and h.group(2)) else ("native" if h else "")
    f = FAIL.search(out)
    fail = f.group(0).strip() if f else ""
    return detected, handler, p.returncode, fail, out


def f32count(path):
    q = subprocess.run(["sox", path, "-t", "f32", "-e", "floating-point", "-"],
                       capture_output=True, timeout=15)
    if q.returncode != 0:
        return f"exit{q.returncode}"
    return str(len(q.stdout) // 4)


def patch(base, mods):
    b = bytearray(base)
    for off, val in mods.items():
        b[off] = val
    return bytes(b)


def insert_chunk(base, tag, data):
    """Insert a RIFF chunk (tag+size+data+pad) before the `data` chunk header."""
    b = bytearray(base)
    didx = base.find(b"data")
    chunk = tag + struct.pack("<I", len(data)) + data
    if len(data) % 2:
        chunk += b"\x00"
    b[didx:didx] = chunk
    struct.pack_into("<I", b, 4, len(b) - 8)  # RIFF size
    return bytes(b)


rows = []          # name,base,mods,detected,handler,exit,fail
exhibits = {}      # name -> bytes (kept + f32 count)


def run(name, base_tag, mods_desc, blob, keep=False, f32=False):
    path = os.path.join(VAR, name + ".wav") if keep else TMP
    if keep:
        with open(path, "wb") as fh:
            fh.write(blob)
    else:
        with open(TMP, "wb") as fh:
            fh.write(blob)
        path = TMP
    detected, handler, code, fail, _ = probe(path)
    samples = f32count(path) if (f32 or keep) else ""
    rows.append([name, base_tag, mods_desc, detected, handler, code,
                 fail[:100], samples])
    return detected


def note(msg):
    print(msg, flush=True)


# ---------- Sweep A: byte 256 value sweep, on v17 AND v16 ----------
note("sweep A: value sweep @256")
for v in range(256):
    run(f"A17_{v:02x}", "v17", f"256=0x{v:02x}", patch(BASE17, {256: v}))
for v in range(256):
    run(f"A16_{v:02x}", "v16", f"256=0x{v:02x}", patch(BASE16, {256: v}))

# ---------- Sweep B: position sweep — 0x84 elsewhere, byte256=0x00 ----------
note("sweep B: position sweep")
positions = sorted(set(
    list(range(240, 273)) +                              # dense around 256
    [12, 13, 16, 20, 24, 32, 36, 38, 42, 50, 58, 60, 64,
     68, 69, 80, 94, 100, 120, 128, 150, 160, 188, 200, 220,
     236, 239, 273, 280, 300, 320, 384, 448, 512, 640, 768,
     896, 1024, 1280, 1536, 2048, 3072, 4096, 5120, 6144,
     7000, 8192, 9216, 10000, 11000, 11500, 11580, 11587]))
for p in positions:
    mods = {256: 0x00}
    if p != 256:
        mods[p] = 0x84
    run(f"B_{p:05d}", "v17", f"256=0x00;{p}=0x84", patch(BASE17, mods),
        keep=(p in (255, 257, 8192)))

# B-extreme: payload all 0x84 except file[256]=0x00
b = bytearray(BASE17)
for i in range(68, len(b)):
    b[i] = 0x84
b[256] = 0x00
run("B_all84_not256", "v17", "68..end=0x84 except 256=0x00", bytes(b), keep=True)
# B-extreme: payload all 0x00 except file[256]=0x84
b = bytearray(BASE17)
for i in range(68, len(b)):
    b[i] = 0x00
b[256] = 0x84
run("B_only256is84", "v17", "68..end=0x00 except 256=0x84", bytes(b), keep=True)

# ---------- Sweep C: neighbour sweeps with 0x84@256 fixed ----------
note("sweep C: neighbour sweeps")
for off in (255, 257, 258):
    for v in range(256):
        run(f"C_{off}_{v:02x}", "v17", f"256=0x84;{off}=0x{v:02x}",
            patch(BASE17, {off: v}))
for off in (259, 260, 261):
    for v in (0x00, 0x41, 0x84, 0xFF):
        run(f"C_{off}_{v:02x}", "v17", f"256=0x84;{off}=0x{v:02x}",
            patch(BASE17, {off: v}))

# ---------- Sweep D: conjunct-1 (RIFF) variants, 0x84@256 held ----------
note("sweep D: magic variants")
def setstr(blob, off, s):
    b = bytearray(blob); b[off:off+len(s)] = s; return bytes(b)
run("D_rifx_84", "v17", "0:4=RIFX,256=0x84",
    setstr(BASE17, 0, b"RIFX"), keep=True)
run("D_rf64_84", "v17", "0:4=RF64,256=0x84",
    setstr(BASE17, 0, b"RF64"), keep=True)
run("D_xxxx_84", "v17", "0:4=XXXX,256=0x84",
    setstr(BASE17, 0, b"XXXX"), keep=True)
run("D_riff_nowave_84", "v17", "8:12=XXXX,256=0x84",
    setstr(BASE17, 8, b"XXXX"), keep=True)
run("D_rifflower_84", "v17", "0:4=riff,256=0x84",
    setstr(BASE17, 0, b"riff"), keep=True)
# RIFX without 0x84 too (control: RIFX must not need the byte for wav)
run("D_rifx_00", "v17", "0:4=RIFX,256=0x00",
    setstr(patch(BASE17, {256: 0x00}), 0, b"RIFX"), keep=True)

# ---------- Sweep E: earlier-table preemptors ----------
note("sweep E: preemptors")
run("E_gsrt_84", "v17", "16:25=ring.bin,256=0x84",
    setstr(BASE17, 16, b"ring.bin"), keep=True)          # gsrt CHECK line 81
run("E_gsrt_00", "v17", "16:25=ring.bin,256=0x00",
    setstr(patch(BASE17, {256: 0x00}), 16, b"ring.bin"), keep=True)
b = patch(BASE17, {})
b = setstr(b, 65, b"FSSD"); b = setstr(b, 128, b"HCOM")  # hcom CHECK line 90
run("E_hcom_84", "v17", "65:69=FSSD,128:132=HCOM,256=0x84", b, keep=True)
b = setstr(patch(BASE17, {256: 0x00}), 65, b"FSSD"); b = setstr(b, 128, b"HCOM")
run("E_hcom_00", "v17", "65:69=FSSD,128:132=HCOM,256=0x00", b, keep=True)

# ---------- Sweep F: position-vs-content (chunk insertion) ----------
note("sweep F: JUNK insert")
INS = insert_chunk(BASE17, b"JUNK", b"\x00" * 8)   # 16-byte insert before data
# payload shifts +16: original 0x84 now at file 272; file[256] = old payload
# byte 172 (sample 86 low byte)
run("F_junk_off84", "v17", "JUNK16@60; orig0x84->272; f256=%02x" % INS[256],
    INS, keep=True)
INS84 = patch(INS, {256: 0x84})
run("F_junk_keep84", "v17", "JUNK16@60; 0x84 at 256 AND 272", INS84, keep=True)

# ---------- Sweep G: length boundary (AUTO_DETECT_SIZE 257) ----------
note("sweep G: truncation")
for n in (255, 256, 257, 258, 300):
    run(f"G_trunc{n}", "v17", f"first {n} bytes only", BASE17[:n],
        keep=(n in (256, 257)))

# ---------- Sweep H: named-base controls + extension routes ----------
note("sweep H: controls/extension")
run("H_v17_b256_00", "v17", "256=0x00", patch(BASE17, {256: 0x00}), keep=True)
run("H_v16_b256_00", "v16", "256=0x00", patch(BASE16, {256: 0x00}), keep=True)
run("H_v16_orig84", "v16", "(none)", BASE16, keep=True)
run("H_v17_orig84", "v17", "(none)", BASE17, keep=True)
# random content, no magic — extension fallback route
rand_bytes = bytes(((i * 37 + 11) & 0xFF) for i in range(300))
# ensure it cannot accidentally match a magic: force byte0..3 non-RIFF-ish
rand_bytes = b"\x99\x88\x77\x66" + rand_bytes[4:]
p_act = os.path.join(VAR, "H_rand.act")
open(p_act, "wb").write(rand_bytes)
d, h, c, f, out = probe(p_act)
rows.append(["H_rand.act", "rand300", "name=.act", d, h, c, f[:100],
             f32count(p_act) if c == 0 else ""])
p_wav = os.path.join(VAR, "H_rand.wav")
open(p_wav, "wb").write(rand_bytes)
d, h, c, f, out = probe(p_wav)
rows.append(["H_rand.wav", "rand300", "name=.wav", d, h, c, f[:100],
             f32count(p_wav) if c == 0 else ""])
# wav-content file named .act with byte256=0: autodetect should win (wav)
p_va = os.path.join(VAR, "H_v16_b256_00.act")
open(p_va, "wb").write(patch(BASE16, {256: 0x00}))
d, h, c, f, out = probe(p_va)
rows.append(["H_v16_b256_00.act", "v16", "256=0x00;name=.act", d, h, c,
             f[:100], f32count(p_va) if c == 0 else ""])
# wav-content named .act WITH 0x84@256: detects act either way
p_va = os.path.join(VAR, "H_v16_orig84.act")
open(p_va, "wb").write(BASE16)
d, h, c, f, out = probe(p_va)
rows.append(["H_v16_orig84.act", "v16", "256=0x84;name=.act", d, h, c,
             f[:100], f32count(p_va) if c == 0 else ""])

# ---------- forced-type references on the real file ----------
for t in ("wav", "act", "ffmpeg"):
    d, h, c, f, _ = probe(os.path.join(ROOT, "pair_valid_17.wav"), forced=t)
    rows.append([f"H_forced_t_{t}", "v17", f"-t {t}", d or "(forced)", h, c,
                 f[:100], ""])

with open(os.path.join(ROOT, "sweep_results.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["name", "base", "mods", "detected", "handler", "exit",
                "fail", "f32_samples"])
    w.writerows(rows)

# ---- summary ----
from collections import Counter
sa = Counter(r[3] or "(none)" for r in rows if r[0].startswith("A17_"))
note(f"A17 detected histogram: {dict(sa)}")
sa = Counter(r[3] or "(none)" for r in rows if r[0].startswith("A16_"))
note(f"A16 detected histogram: {dict(sa)}")
sb = Counter(r[3] or "(none)" for r in rows if r[0].startswith("B_"))
note(f"B detected histogram: {dict(sb)}")
sc = Counter(r[3] or "(none)" for r in rows if r[0].startswith("C_"))
note(f"C detected histogram: {dict(sc)}")
for r in rows:
    if r[0][0] in "DEFGH":
        note(f"{r[0]:22s} det={r[3] or '-':8s} hdl={r[4] or '-':7s} "
             f"exit={r[5]} samples={r[7] or '-':>6s} {r[6][:60]}")
note(f"total rows: {len(rows)}")
