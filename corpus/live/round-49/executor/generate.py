#!/usr/bin/env python3
import sys, wave
import numpy as np
path, rate = sys.argv[1], int(sys.argv[2])
n = 5760
t = np.arange(n) / 48000
x = .28 * np.sin(2*np.pi*1000*t) * np.hanning(n)
pcm = np.rint(np.clip(x, -1, 1) * 32767).astype("<i2")
with wave.open(path, "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(rate)
    w.writeframes(pcm.tobytes())
