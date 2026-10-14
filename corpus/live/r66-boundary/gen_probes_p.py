#!/usr/bin/env python3
"""r66-boundary supplementary probes — p_* family.

Closes the two rows the a..z matrix left unpinned:
  voc(78) 'Creative Voice File\\x1a' @0 len20 — bytes 0-19
  smp(79) 'SOUND SAMPLE DATA'        @0 len17 — bytes 0-16
vs hcom(90) sigs @65-68/@128-131: ranges do NOT overlap -> co-satisfiable,
so voc/smp vs hcom is the ONLY reachable pairing for the two pre-wve rows
(byte-0 disjoint from wve 'A' / act 'R'; byte-range clash with gsrt @16-24).

Mutual-exclusivity demonstrators (same carrier, flip which sig is intact):
  *_intact        : voc/smp magic complete -> row 78/79 wins, gsrt sig absent
  *_broken_gsrt   : ring.bin@16-24 overwrote voc bytes 16-19 / smp byte 16
                    -> voc/smp sig dead, gsrt live -> gsrt(81)
Also copies the six tracked round-66 members into probes/ namespace under
t_* so they run through the same 13-mode matrix (transports + forced -t
legs the author left unexercised).
"""
import os, struct, shutil

P = "probes"
os.makedirs(P, exist_ok=True)

VOC = b"Creative Voice File\x1a"   # 20B @0..19
SMP = b"SOUND SAMPLE DATA"         # 17B @0..16
GSRT = b"ring.bin\x00"             # @16..24
ACTB = 0x84

def hcom_chain(buf):
    """r65-critic D1 decodable hcom chain at absolute 65..166 (identical to
    gen_probes.py)."""
    d1 = bytes.fromhex(
        "46535344"
        "e6edf4fb020910171e252c333a41484f565d646b727980"
        "878e959ca3aab1b8bfc6cdd4dbe2e9f0f7fe050c"
        "131a21282f363d444b525960676e757c"
        "48434f4d"
        "00000009"
        "a5a5a5a5"
        "00000000"
        "00000001"
        "0002"
        "00010001ffff0000"
        "00"
        "40a5a5a5a57f868d"
    )
    buf[65:65+len(d1)] = d1
    return buf

W = {}
def put(name, data): W[name] = bytes(data)

# --- ordering pins: voc/smp vs hcom -----------------------------------------
b = bytearray(300); b[0:20] = VOC; hcom_chain(b); b[256] = ACTB
put("p_voc_hcom.bin", b)            # voc(78) < hcom(90); -t hcom decodes 9

b = bytearray(300); b[0:17] = SMP; hcom_chain(b); b[256] = ACTB
put("p_smp_hcom.bin", b)            # smp(79) < hcom(90)

# --- mutual exclusivity voc/smp vs gsrt -------------------------------------
b = bytearray(300); b[0:20] = VOC; b[256] = ACTB
put("p_voc_intact.bin", b)          # voc complete -> voc; gsrt sig absent

b = bytearray(300); b[0:20] = VOC; b[16:25] = GSRT; b[256] = ACTB
put("p_voc_broken_gsrt.bin", b)     # voc bytes 16-19 killed -> gsrt detects

b = bytearray(300); b[0:17] = SMP; b[256] = ACTB
put("p_smp_intact.bin", b)          # smp complete -> smp

b = bytearray(300); b[0:17] = SMP; b[16:25] = GSRT; b[256] = ACTB
put("p_smp_broken_gsrt.bin", b)     # smp byte 16 'A'->'r' kills smp -> gsrt

# --- tracked round-66 members under the boundary matrix ----------------------
R66 = "../round-66"
for m in ("pair_dec_hcom.wav", "pair_dec_act.wav",
          "pair_lengate_gsrt_24.wav", "pair_lengate_gsrt_25.wav",
          "pair_lengate_hcom_131.wav", "pair_lengate_hcom_132.wav"):
    src = os.path.join(R66, m)
    dst = "t_" + m
    if os.path.exists(src):
        put(dst, open(src, "rb").read())
    else:
        print(f"WARN missing tracked member {src}")

for name, d in sorted(W.items()):
    with open(os.path.join(P, name), "wb") as f:
        f.write(d)
print(f"{len(W)} supplementary fixtures -> {P}/")
