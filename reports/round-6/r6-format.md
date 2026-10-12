# Round 6 wrong-format WAV fixture (executor)

Created the assigned synthetic analytic control at `corpus/live/round-6/wrong_format.wav`. It is a 4.000 s, 44,100 Hz, stereo, signed PCM16 WAV (left: 440 Hz sine at 0.30 full scale; right: 660 Hz sine at 0.25 full scale). This deliberately violates the expected 48 kHz mono format; it does not establish any codec-security, robustness, perceptual, or production claim.

Reproducible recipe (Python standard library; run from repository root):

```python
import math, struct, wave
rate = 44100
with wave.open(".shokunin/audio/corpus/live/round-6/wrong_format.wav", "wb") as wav:
    wav.setnchannels(2)
    wav.setsampwidth(2)
    wav.setframerate(rate)
    frames = bytearray()
    for i in range(rate * 4):
        t = i / rate
        left = 0.30 * math.sin(2 * math.pi * 440 * t)
        right = 0.25 * math.sin(2 * math.pi * 660 * t)
        frames.extend(struct.pack("<hh", round(left * 32767), round(right * 32767)))
    wav.writeframes(frames)
```

Validation command and exit: `ffprobe -v error -show_entries stream=sample_rate,channels,sample_fmt,bits_per_sample,duration -of json .shokunin/audio/corpus/live/round-6/wrong_format.wav` — exit 0. ffprobe reported sample rate 44100, 2 channels, `s16`, 16 bits/sample, duration 4.000000 s. File size: 705644 bytes. SHA-256: `a753c610ccfdc26729e4694f52a34a4bc4b0a116731fe52f6bc6a133fa190712`.
