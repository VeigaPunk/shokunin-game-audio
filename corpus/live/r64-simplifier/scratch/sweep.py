#!/usr/bin/env python3
"""r64-simplifier: independent pin of the valid-bits -> codec step map.

Base = tracked corpus/live/round-61/pair_valid_17.wav (byte 256 = 0x84, so
SoX autodetect routes every mutant to the ffmpeg bridge). Only bytes 38-39
(wValidBitsPerSample, LE u16) are mutated. Per value: detected format via
`sox -V4 -n`, decoded f32 sample count via `sox -t f32 -`, ffmpeg codec via
`ffprobe`.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "live" / "round-61" / "pair_valid_17.wav"
OUT = Path(__file__).resolve().parent / "variants"
OUT.mkdir(exist_ok=True)
base = bytearray(BASE.read_bytes())
assert base[256] == 0x84 and base[38] == 17 and base[39] == 0

VALUES = [0, 1, 8, 9, 16, 17, 24, 25, 32, 33, 56, 57, 64, 65, 128, 255, 65535]
rows = []
for v in VALUES:
    mutant = bytearray(base)
    mutant[38] = v & 0xFF
    mutant[39] = (v >> 8) & 0xFF
    path = OUT / f"v{v}.wav"
    path.write_bytes(mutant)
    det = subprocess.run(["sox", "-V4", str(path), "-n"],
                         capture_output=True)
    err = det.stderr.decode(errors="replace")
    detected = next((ln.split("`")[1].rstrip("'") for ln in err.splitlines()
                     if "detected file format type" in ln), None)
    dec = subprocess.run(["sox", str(path), "-t", "f32", "-e", "floating-point", "-"],
                         capture_output=True)
    samples = len(dec.stdout) // 4 if dec.returncode == 0 else -dec.returncode
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                            "stream=codec_name,bits_per_sample", "-of", "json",
                            str(path)], capture_output=True)
    codec = bps = None
    if probe.returncode == 0 and probe.stdout.strip():
        s = json.loads(probe.stdout).get("streams", [{}])[0]
        codec, bps = s.get("codec_name"), s.get("bits_per_sample")
    rows.append((v, detected, codec, bps, samples,
                 dec.returncode, err.strip().splitlines()[-1] if dec.returncode else ""))

print("valid\tdetected\tcodec\tbps\tsamples\tsox_exit\tlast_stderr")
for r in rows:
    print("\t".join(str(x) for x in r))
