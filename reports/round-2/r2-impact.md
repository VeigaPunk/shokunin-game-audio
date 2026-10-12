# Round 2 impact alternate: source and raw-file measurements

## Synthesis

Created `corpus/live/round-2/impact_alt.wav` from a newly synthesized sum of decaying sinusoids; no source audio or existing WAV samples were used. The generator rate is 48,000 Hz and duration is 0.32 s (`n = round(0.32 * 48000) = 15360` samples). There is no RNG and no seed: all samples are deterministic from the expression below.

```python
import numpy as np
import wave

rate = 48000
duration = 0.32
t = np.arange(round(duration * rate)) / rate
samples = (
    0.55 * np.sin(2 * np.pi * 95 * t) * np.exp(-14 * t)
    + 0.25 * np.sin(2 * np.pi * 340 * t) * np.exp(-35 * t)
    + 0.12 * np.sin(2 * np.pi * 900 * t) * np.exp(-50 * t)
)
pcm16 = np.round(np.clip(samples, -1, 1) * 32767).astype("<i2")
with wave.open("impact_alt.wav", "wb") as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(rate)
    wav.writeframes(pcm16.tobytes())
```

## Measurement rationale and result

Measured PCM decoded from the written WAV, using the same whole-file magnitude-weighted FFT centroid definition as the fixture battery (`abs(rfft(samples))`, weighted by `rfftfreq`). Baseline `impact.wav` was also read from its raw artifact. The centroid difference is `abs(473.792 - 10843.127) / 10843.127 = 95.63%`, exceeding the clarified >=10% criterion. Duration is unchanged, so distinctness relies on centroid only. The distinctness rule is a numerical fixture criterion, not a claim about perceived or functional sound difference.

| Artifact | Rate | Channels | Duration | Centroid | RMS | Peak |
|---|---:|---:|---:|---:|---:|---:|
| `corpus/artifacts/impact.wav` baseline | 48,000 Hz | 1 | 0.320 s | 10,843.127 Hz | 0.09548 | 0.80878 |
| `corpus/live/round-2/impact_alt.wav` | 48,000 Hz | 1 | 0.320 s | 473.792 Hz | 0.13599 | 0.75616 |

The alternate meets impact's existing local fixture checks: mono 48 kHz PCM16; expected 0.32 s duration; centroid within 50–15,000 Hz; peak <0.95 and RMS >0.001. These are fixture bounds, not production or perceptual-quality standards. No shell commands were run in this lane.
