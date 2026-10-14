#!/usr/bin/env python3
"""r65 reviewer: preemptor latent-collision scan over ALL tracked pair fixtures.

Checks, per tracked pair_* file, the byte predicates recorded in
corpus/knowledge/2026-10-13-sox-act-autodetect-predicate.md:
  act  : len>=257 AND file[0:4]=='RIFF' AND file[256]==0x84
  gsrt : file[16:25]==b'ring.bin\\x00'      (pre-act CHECK row, no offset-0 anchor)
  hcom : file[65:69]==b'FSSD' AND file[128:132]==b'HCOM'  (pre-act, no offset-0 anchor)
Collision classes:
  LATENT-PREEMPTOR: any preemptor predicate matches (autodetect would take that
                    row before act is consulted)
  COLLIDES-ACT    : preemptor AND act predicate both match -> 'routes act' claims
                    for that fixture are falsified under autodetect
"""
import subprocess, sys

FILES = subprocess.run(
    ["git", "ls-files"], cwd="/home/vgpnk/Projects/shokunin/audio-shokunin",
    capture_output=True, text=True, check=True,
).stdout.split()
FILES = [f for f in FILES if "pair_" in f]

rows = []
for rel in FILES:
    p = "/home/vgpnk/Projects/shokunin/audio-shokunin/" + rel
    d = open(p, "rb").read()
    n = len(d)
    riff   = d[0:4] == b"RIFF"
    b256   = d[256] if n > 256 else None
    act    = n >= 257 and riff and b256 == 0x84
    gsrt   = d[16:25] == b"ring.bin\x00"
    fssd   = d[65:69] == b"FSSD"
    hcom128= d[128:132] == b"HCOM"
    hcom   = fssd and hcom128
    vb     = int.from_bytes(d[38:40], "little") if n >= 40 else None
    rows.append((rel, n, riff, b256, act, gsrt, fssd, hcom128, hcom, vb))

hdr = ("file","size","RIFF@0","b[256]","act_pred","gsrt(ring.bin\\0@16)",
       "FSSD@65","HCOM@128","hcom_pred","vb@38")
print("\t".join(hdr))
for r in rows:
    rel,n,riff,b256,act,gsrt,fssd,h128,hcom,vb = r
    print("\t".join([rel, str(n), str(riff),
                     "0x%02x" % b256 if b256 is not None else "SHORT",
                     str(act), str(gsrt), str(fssd), str(h128), str(hcom),
                     str(vb)]))

print("\n== collision summary ==")
coll = [r for r in rows if r[5] or r[8]]
act_coll = [r for r in rows if (r[5] or r[8]) and r[4]]
print("files matching a preemptor predicate:", [r[0] for r in coll] or "NONE")
print("files where preemptor AND act both match:", [r[0] for r in act_coll] or "NONE")
print("act-predicate fixtures:", sum(1 for r in rows if r[4]), "of", len(rows))
