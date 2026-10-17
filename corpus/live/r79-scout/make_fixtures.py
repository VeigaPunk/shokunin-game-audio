#!/usr/bin/env python3
"""Regenerate this seat's tone/silence fixtures deterministically.

Run before re-running any probe driver (the 40 s tone is trimmed from the seat
footprint; the JSON records keep every measured number).

  tone_r79_long.wav  40 s, 2 ch, L 1 kHz / R 1.5 kHz, amp 8192, 48 kHz s16
  tone_r79.wav        6 s, same
  silence_r79.wav     2 s, 2 ch digital silence
"""
import math
import os
import struct
import wave

SCRATCH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scratch")
RATE, AMP = 48000, 8192


def tone(path, dur):
    buf = bytearray()
    for i in range(int(RATE * dur)):
        t = i / RATE
        buf += struct.pack("<hh", int(AMP * math.sin(2 * math.pi * 1000 * t)),
                           int(AMP * math.sin(2 * math.pi * 1500 * t)))
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(bytes(buf))
    return os.path.getsize(path)


def silence(path, dur):
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"\x00" * (int(RATE * dur) * 4))
    return os.path.getsize(path)


if __name__ == "__main__":
    os.makedirs(SCRATCH, exist_ok=True)
    print("tone_r79_long.wav", tone(os.path.join(SCRATCH, "tone_r79_long.wav"), 40.0))
    print("tone_r79.wav", tone(os.path.join(SCRATCH, "tone_r79.wav"), 6.0))
    print("silence_r79.wav", silence(os.path.join(SCRATCH, "silence_r79.wav"), 2.0))
