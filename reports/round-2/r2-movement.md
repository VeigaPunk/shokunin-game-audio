# Round 2 movement alternate — executor report

## Artifact and reproducible recipe

Created `corpus/live/round-2/movement_alt.wav` from an analytic noise burst (no borrowed samples). Recipe:

```python
import wave
import numpy as np

RATE = 48000
rng = np.random.default_rng(20261013)
t = np.arange(round(0.36 * RATE)) / RATE
noise = rng.standard_normal(len(t))
samples = 0.30 * noise * (1 - np.exp(-180 * t)) * np.exp(-15 * t)
pcm = np.round(np.clip(samples, -1, 1) * 32767).astype("<i2")
with wave.open("movement_alt.wav", "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(RATE)
    w.writeframes(pcm.tobytes())
```

The generator rate is 48,000 Hz; duration is 0.36 s (17,280 samples). The dedicated seed makes the variant reproducible and independent of shared builder RNG call order.

## Measurements and rationale

Read PCM16 samples directly from the WAV and computed the full-signal magnitude-weighted FFT centroid as `dot(rfftfreq(N, 1/rate), abs(rfft(samples))) / sum(abs(rfft(samples)))`. This is a fixture-level spectral proxy, not a timbre or quality judgment.

| Asset | Rate | Channels | PCM | Duration | Peak FS | RMS FS | Centroid |
|---|---:|---:|---|---:|---:|---:|---:|
| Baseline `movement.wav` | 48,000 Hz | 1 | 16-bit | 0.24 s | 0.53949 | 0.06471 | 11,934.48 Hz |
| `movement_alt.wav` | 48,000 Hz | 1 | 16-bit | 0.36 s | 0.63931 | 0.07955 | 12,024.21 Hz |

The centroid difference is below 10%, but the variant duration is independently distinct from the 0.24 s baseline, satisfying the round's duration-OR-centroid distinction criterion. Its peak and RMS pass the existing upper-peak (<0.95) and non-silence (RMS >0.001) fixture checks. The existing movement duration limit is 0.24 s ±1 ms; parent integration must add an explicit variant spec (0.36 s) rather than incorrectly reuse that baseline duration. No production-readiness or auditory-quality claim.

SHA-256: `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639`.

## Commands

No shell commands were run; synthesis and raw-WAV measurement were performed in Python. Therefore there are no shell command/exit-code receipts.
