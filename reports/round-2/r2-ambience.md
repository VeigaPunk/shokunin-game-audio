# Round 2 ambience variant (author report)

## Artifact and synthesis

Created `.shokunin/audio/corpus/live/round-2/ambience_alt.wav` from analytic oscillators only. It is mono, signed PCM16, 48,000 Hz, 96,000 frames (2.000 s). No random generator was used; seed: none.

Exact reproducible NumPy recipe (same quantization and WAV encoding):

```python
import numpy as np, wave
rate = 48000
t = np.arange(round(2.0 * rate)) / rate
samples = (0.15 * np.sin(2*np.pi*20*t)
           + 0.09 * np.sin(2*np.pi*60*t)
           + 0.06 * np.sin(2*np.pi*100*t))
pcm = np.round(np.clip(samples, -1, 1) * 32767).astype("<i2")
with wave.open("ambience_alt.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
    w.writeframes(pcm.tobytes())
```

## Measurements and rationale

Compared to `.shokunin/audio/corpus/artifacts/ambience.wav`, both are 2.000 s, so duration is unchanged. Using the fixture battery's full-waveform magnitude-weighted FFT centroid on decoded PCM (NumPy `rfft` and `rfftfreq`): baseline centroid is 36.6164 Hz and variant is 58.0192 Hz, a +58.45% difference relative to baseline (requirement: at least 10%). Variant peak is 0.19974 full scale, RMS is 0.13076, and endpoint absolute delta is 0.001892 full scale (limit: 0.03). It is built from components with integer cycle counts over two seconds; the endpoint metric remains a proxy only, not proof of perceptual or playback seamlessness. Centroid is a global spectrum statistic, not a timbre/perceptual claim.

The variant is distinct by measured centroid, and duration/format/level and endpoint checks are consistent with the local round-2 fixture rules. No listening, engine, publishing, or production-readiness claim is made.

## Shell commands

Exact shell commands run and exit codes:

- `ffprobe -v error -show_entries stream=sample_rate,channels,sample_fmt,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-2/ambience_alt.wav` — exit 127 (the filename was not shell-quoted and was parsed as a command).
- `ffprobe -v error -show_entries stream=sample_rate,channels,sample_fmt,bits_per_sample:format=duration -of json '.shokunin/audio/corpus/live/round-2/ambience_alt.wav'` — exit 0; reports s16, mono, 48000 Hz, duration 2.000000 s.
