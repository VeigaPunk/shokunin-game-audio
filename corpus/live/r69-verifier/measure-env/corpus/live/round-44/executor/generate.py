import numpy as np
import wave
from pathlib import Path

RATE = 48000
OUT = Path(__file__).resolve().parent
for count, label in ((5807, "pass-5807"), (5809, "fail-5809")):
    n = np.arange(count)
    t = n / RATE
    samples = 0.28 * np.sin(2 * np.pi * (700 * t + 700 * t * t)) * np.exp(-5 * t)
    pcm = np.rint(np.clip(samples, -1, 1) * 32767).astype("<i2")
    with wave.open(str(OUT / f"{label}.wav"), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(pcm.tobytes())
