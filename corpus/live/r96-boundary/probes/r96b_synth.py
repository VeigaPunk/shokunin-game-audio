#!/usr/bin/env python3
"""r96-boundary own stimulus synth — stdlib only (wave + math). No repo fixtures.

Usage: r96b_synth.py OUT.wav SECONDS [FREQ] [AMP] [RATE]
997 Hz default, amp 0.5, s16le mono 48 kHz. Deterministic: same args -> same sha.
(Adapted from the r96 scout's r96s_synth.py; same waveform so cross-receipt
onset/peak comparisons are apples-to-apples.)
"""
import math
import struct
import sys
import wave


def main() -> int:
    out = sys.argv[1]
    secs = float(sys.argv[2])
    freq = float(sys.argv[3]) if len(sys.argv) > 3 else 997.0
    amp = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
    rate = int(sys.argv[5]) if len(sys.argv) > 5 else 48000
    n = int(round(secs * rate))
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        frames = bytearray()
        for i in range(n):
            v = int(round(amp * 32767.0 * math.sin(2.0 * math.pi * freq * i / rate)))
            frames += struct.pack("<h", max(-32768, min(32767, v)))
        w.writeframes(bytes(frames))
    print(f"{out} frames={n} freq={freq} amp={amp} rate={rate}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
