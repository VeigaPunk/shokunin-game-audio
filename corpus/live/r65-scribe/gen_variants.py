#!/usr/bin/env python3
"""r65-scribe: minimal RIFF preemptor-collision fixture family.

Two independent constructions (NOT the r61/r63 68-byte extensible family):

  Family V — a VALID minimal WAV: JUNK pad chunk carries the hcom windows
  (65-68, 128-131) inside its payload, so the file stays a well-formed
  RIFF/WAVE that would decode natively. gsrt's window 16-24 cannot live in
  any valid RIFF (offsets 16-19 are always the first subchunk's size), so
  family B carries it.

  Family B — bare RIFF shell: "RIFF"+size+"WAVE" then zero fill; minimal
  detection bait, not chunk-parseable.

  Family N — non-RIFF controls (zeros + signatures): isolate each
  preemptor's need for RIFF@0 (it has none).

  Family L — length-gate files at exact len >= p1+l1 boundaries.

Byte 256 is asserted where required by the act predicate.
"""
import struct, hashlib, os

V = os.path.join(os.path.dirname(os.path.abspath(__file__)), "variants")
os.makedirs(V, exist_ok=True)
made = {}

def put(name, buf):
    p = os.path.join(V, name)
    with open(p, "wb") as f:
        f.write(buf)
    made[name] = (len(buf), hashlib.sha256(buf).hexdigest())

def wav_shell(b256, fssd=False, hcom=False, fill=0):
    """Valid minimal WAV, 312 B. JUNK(196B payload @20..215) + fmt @216 + data @240.
    data payload @248..311; file offset 256 = data payload byte 8."""
    junk_size = 196
    body = bytearray([fill] * junk_size)
    if fssd:
        body[65 - 20:69 - 20] = b"FSSD"          # JUNK payload covers file 65-68
    if hcom:
        body[128 - 20:132 - 20] = b"HCOM"        # JUNK payload covers file 128-131
    data = bytearray(64)
    data[8] = b256                                # file offset 256
    riff_size = 4 + (8 + junk_size) + (8 + 16) + (8 + len(data))
    out = bytearray()
    out += b"RIFF" + struct.pack("<I", riff_size) + b"WAVE"
    out += b"JUNK" + struct.pack("<I", junk_size) + body
    out += b"fmt " + struct.pack("<I", 16) + struct.pack("<HHIIHH", 1, 1, 8000, 16000, 2, 16)
    out += b"data" + struct.pack("<I", len(data)) + data
    assert len(out) == 312, len(out)
    assert out[256] == b256
    return out

def bare_shell(total=312, form=b"WAVE", b256=0x84, gsrt=False, fssd=False,
               hcom=False, nul=0x00):
    """Bare RIFF shell: RIFF+size+form+zeros. Not chunk-valid."""
    out = bytearray(total)
    out[0:4] = b"RIFF"
    out[4:8] = struct.pack("<I", total - 8)
    out[8:12] = form
    if total > 256:
        out[256] = b256
    if gsrt:
        out[16:24] = b"ring.bin"
        out[24] = nul
    if fssd:
        out[65:69] = b"FSSD"
    if hcom:
        out[128:132] = b"HCOM"
    return out

# ---------------- Family V: valid WAV ----------------
put("v_base84.wav",   wav_shell(0x84))                          # act expected
put("v_base00.wav",   wav_shell(0x00))                          # wav expected, decodes
put("v_hcom84.wav",   wav_shell(0x84, fssd=True, hcom=True))    # hcom beats valid WAV+act
put("v_hcom00.wav",   wav_shell(0x00, fssd=True, hcom=True))    # hcom beats valid WAV
put("v_fssd_only.wav",wav_shell(0x84, fssd=True))               # half hcom -> act
put("v_hcom_only.wav",wav_shell(0x84, hcom=True))               # half hcom -> act
vgsrt = wav_shell(0x84)
vgsrt[16:24] = b"ring.bin"; vgsrt[24] = 0x00                    # gsrt over JUNK size field
put("v_gsrt84.wav",   vgsrt)                                    # gsrt; -t wav now broken

# ---------------- Family B: bare RIFF shell ----------------
put("b_riff84.wav",      bare_shell())                                   # act
put("b_riff00.wav",      bare_shell(b256=0x00))                          # WAVE@8 -> wav detect
put("b_gsrt84.wav",      bare_shell(gsrt=True))                          # gsrt
put("b_hcom84.wav",      bare_shell(fssd=True, hcom=True))               # hcom
put("b_both84.wav",      bare_shell(gsrt=True, fssd=True, hcom=True))    # gsrt vs hcom order
put("b_gsrt_00.wav",     bare_shell(b256=0x00, gsrt=True))               # gsrt w/o act byte
put("b_hcom_00.wav",     bare_shell(b256=0x00, fssd=True, hcom=True))    # hcom w/o act byte
put("b_gsrt_badnul.wav", bare_shell(gsrt=True, nul=0x2E))                # 9th byte compared
put("b_avi84.wav",       bare_shell(form=b"AVI "))                       # act precedes avi rows
put("b_noform84.wav",    bare_shell(form=b"XXXX"))                       # act w/o WAVE

# ---------------- Family N: non-RIFF controls ----------------
n = bytearray(312); n[16:24] = b"ring.bin"; n[24] = 0
put("n_gsrt.bin", n)
n = bytearray(312); n[65:69] = b"FSSD"; n[128:132] = b"HCOM"
put("n_hcom.bin", n)
n = bytearray(312); n[16:24] = b"ring.bin"; n[24] = 0
n[65:69] = b"FSSD"; n[128:132] = b"HCOM"
put("n_gsrt_hcom.bin", n)                                  # both sigs, no RIFF -> order
put("n_zero.bin", bytearray(312))

# ---------------- Family L: length gates ----------------
l = bytearray(25); l[16:24] = b"ring.bin"; l[24] = 0
put("l_gsrt_25.bin", l)                                    # len == 16+9 exactly
l = bytearray(24); l[16:24] = b"ring.bin"
put("l_gsrt_24.bin", l)                                    # byte 24 absent -> no gsrt
l = bytearray(132); l[65:69] = b"FSSD"; l[128:132] = b"HCOM"
put("l_hcom_132.bin", l)                                   # len == 128+4 exactly
l = bytearray(131); l[65:69] = b"FSSD"; l[128:131] = b"HCO"
put("l_hcom_131.bin", l)                                   # 'M' absent -> no hcom
l = bare_shell(total=257)
put("l_act_257.wav", l)                                    # len == 257 exactly -> act
l = bare_shell(total=256)                                  # byte 256 absent
put("l_act_256.wav", l)                                    # -> wav detect

with open(os.path.join(V, "manifest.tsv"), "w") as f:
    f.write("file\tsize\tsha256\n")
    for k in sorted(made):
        f.write(f"{k}\t{made[k][0]}\t{made[k][1]}\n")
with open(os.path.join(V, "manifest.tsv")) as f:
    print(f.read(), end="")
