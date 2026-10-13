#!/usr/bin/env python3
"""r63-simplifier: position + structural sweep on pair_valid_17.wav.
Each case mutates a copy; probe = sox -V3 <f> -n → detected type + exit.
"""
import subprocess, re, os

base = open("base.wav", "rb").read()          # byte256 = 0x84
DET = re.compile(rb"detected file format type `([a-zA-Z0-9_-]+)'")

def probe(name, buf):
    path = f"pos_{name}.wav"
    open(path, "wb").write(buf)
    p = subprocess.run(["sox", "-V3", path, "-n"], capture_output=True)
    m = DET.search(p.stderr)
    det = m.group(1).decode() if m else "NONE"
    err = b""
    for line in p.stderr.splitlines():
        if b"FAIL" in line or b"can't" in line or b"exceeds" in line:
            err = line.strip()[:110]
    print(f"{name:28s} detected={det:6s} exit={p.returncode}  {err.decode(errors='replace')}")

def mut(base, edits):
    b = bytearray(base)
    for off, v in edits:
        b[off] = v
    return bytes(b)

# --- position sweep: byte256 cleared to 0x00, single 0x84 elsewhere ---
for off in [68, 128, 200, 255, 257, 260, 324, 384, 512, 1024, 8191, 11587]:
    probe(f"b{off}=84_b256=00", mut(base, [(256, 0x00), (off, 0x84)]))
# adjacent both sides occupied + 256 clear
probe("b255+257=84_b256=00", mut(base, [(256, 0x00), (255, 0x84), (257, 0x84)]))
# 0x84 everywhere-ish incl 256 (sanity re-run of base shape)
probe("base_b256=84      ", base)
# --- structural gates with 0x84 kept at 256 ---
probe("RIFF->XIFF,b256=84 ", mut(base, [(0, ord('X'))]))                      # kill RIFF
probe("WAVE->XAVE,b256=84 ", mut(base, [(8, ord('X'))]))                      # kill WAVE, keep RIFF
probe("RIFF+WAVE dead,84  ", mut(base, [(0, ord('X')), (8, ord('X'))]))
# --- length floor: act needs len>=257 ---
probe("trunc256_b255=84   ", base[:255] + b"\x84")                            # 256 bytes, 0x84 at 255
t257 = bytearray(base[:257]); t257[256] = 0x84
probe("trunc257_b256=84   ", bytes(t257))                                     # 257 bytes, 0x84 at 256
probe("trunc256           ", base[:256])                                      # no byte 256 at all
