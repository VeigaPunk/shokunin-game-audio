# Round 2 UI alternate: executor report

## Artifact

Created `.shokunin/audio/corpus/live/round-2/ui_alt.wav` from an analytic waveform (no samples borrowed). It is mono, 48,000 Hz, signed PCM16 little-endian, 7,680 frames / 0.160 s. The existing baseline `corpus/artifacts/ui.wav` is 0.120 s. The variant is 33.3% longer and has a 47.19% higher magnitude-weighted full-waveform FFT centroid, so it exceeds the declared 10% distinctness threshold by either duration or centroid.

## Reproduction

```python
import numpy as np
import wave

rate = 48000
t = np.arange(round(0.16 * rate)) / rate
samples = 0.32 * np.sin(2 * np.pi * (1200*t + 1200*t*t)) * np.exp(-18*t)
pcm = np.round(np.clip(samples, -1, 1) * 32767).astype("<i2")
with wave.open("ui_alt.wav", "wb") as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(rate)
    wav.writeframes(pcm.tobytes())
```

No random values are used; no seed is needed. For centroid I decoded the PCM16 samples as little-endian int16 and divided by 32768, then used `abs(np.fft.rfft(x))` weighted by `np.fft.rfftfreq(len(x), 1/rate)`, matching the existing measurement's whole-signal magnitude-weighted centroid method. Baseline UI: 966.8967 Hz; alternate: 1423.1533 Hz (+47.19%). Raw-waveform checks: peak 0.31879, RMS 0.09413 (−20.526 dBFS), rate 48 kHz, mono, duration 0.160 s. These are measured proxies, not perceptual or production-quality claims. The existing baseline UI duration spec is 0.120 s; integration must declare the alternate's 0.160 s expected duration rather than apply that baseline-only check unchanged.

## Shell-outs

None.
