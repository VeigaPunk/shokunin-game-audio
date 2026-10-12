# Round 4 composer report

## Output and scope

Created from analytic terms only, without borrowed samples or an audio engine: `.shokunin/audio/corpus/live/round-4/stem_sections.wav`. This report and that scoped scratch WAV are the only outputs. No shell command was run. The recipe below is a complete deterministic NumPy/Python generation and raw-PCM measurement procedure; it uses only NumPy and the Python standard library.

The 4-second mono PCM16/48 kHz file has exact 2-second sections. Both contain the same 220 Hz and 330 Hz motif components at peak amplitudes 0.08 and 0.04. A named 30 Hz component is also present in both sections, at peak amplitude 0.012 in section 1 and 0.060 in section 2. Its measured energy ratio therefore develops while the common motif remains present. This is an analytic construction, not a claim about musical or perceptual recognition.

## Reproduction

Run this from any working directory with NumPy available. It writes the fixed relative output path shown, then decodes the saved WAV and prints raw measurements. Quantization uses `rint(x*32767)` to little-endian signed PCM16; readback normalizes by 32768, the standard signed-PCM scale.

```python
from pathlib import Path
import wave
import hashlib
import numpy as np

fs = 48000
n = 4 * fs
t = np.arange(n, dtype=np.float64) / fs
amplitude_30 = np.where(t < 2.0, 0.012, 0.060)
x = (0.08 * np.sin(2 * np.pi * 220 * t)
     + 0.04 * np.sin(2 * np.pi * 330 * t)
     + amplitude_30 * np.sin(2 * np.pi * 30 * t))
pcm = np.rint(np.clip(x, -1.0, 1.0) * 32767).astype('<i2')
out = Path('.shokunin/audio/corpus/live/round-4/stem_sections.wav')
out.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(out), 'wb') as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(fs)
    wav.writeframes(pcm.tobytes())

with wave.open(str(out), 'rb') as wav:
    params = (wav.getnchannels(), wav.getsampwidth(),
              wav.getframerate(), wav.getnframes())
    samples = np.frombuffer(wav.readframes(wav.getnframes()), dtype='<i2').astype(np.float64) / 32768.0

measurements = []
for section in range(2):
    s = samples[section * 2 * fs:(section + 1) * 2 * fs]
    tt = np.arange(len(s), dtype=np.float64) / fs
    basis = np.column_stack((np.sin(2 * np.pi * 30 * tt),
                             np.cos(2 * np.pi * 30 * tt)))
    sin_coef, cos_coef = np.linalg.lstsq(basis, s, rcond=None)[0]
    amplitude = float(np.hypot(sin_coef, cos_coef))
    measurements.append((float(sin_coef), float(cos_coef), amplitude, amplitude**2 / 2))
ratio = measurements[1][3] / measurements[0][3]
endpoint_delta = abs(float(samples[-1] - samples[0]))
slope_gap = abs(float((samples[-1] - samples[-2]) - (samples[1] - samples[0])))
print('format', params)
print('sections (sin coefficient, cos coefficient, fitted peak amplitude, fitted mean-square energy)', measurements)
print('30-Hz section energy delta dB', 10 * np.log10(ratio))
print('endpoint delta', endpoint_delta, 'slope gap', slope_gap)
print('peak', float(np.max(np.abs(samples))), 'RMS', float(np.sqrt(np.mean(samples**2))))
print('sha256', hashlib.sha256(out.read_bytes()).hexdigest())
```

## Measurements from saved WAV

- Format `(channels, sample width bytes, sample rate, frames)`: `(1, 2, 48000, 192000)`; duration 4.000 s.
- Section 1: 96,000 decoded samples; 30 Hz sine coefficient `0.01199946510868905`, cosine coefficient `2.586577747025593e-16`, fitted peak amplitude `0.01199946510868905`, fitted mean-square energy `7.199358144732296e-05`.
- Section 2: 96,000 decoded samples; 30 Hz sine coefficient `0.059998071187854725`, cosine coefficient `1.293589753452758e-15`, fitted peak amplitude `0.059998071187854725`, fitted mean-square energy `0.0017998842731314416`.
- Section 2/1 fitted 30 Hz energy ratio `25.000621401901` (computed directly from values); energy change `13.97950803394546 dB`, above the declared >=6 dB target.
- Whole-file decoded peak absolute amplitude `0.17236328125`; RMS `0.07025446626309474`.
- End-to-start absolute sample delta `0.0042724609375` (<=0.03); absolute difference-of-adjacent-slopes gap `0.000152587890625` (<=0.001).
- SHA-256 `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702`.

The 30 Hz estimate is least-squares sine/cosine projection on each exact 2-second section; energy is fitted sinusoidal peak amplitude squared divided by two. Both sections contain an integer number of 30 Hz cycles, and the target component is nonzero in each. These are fixture-local analytic measurements, not perceptual evidence. I did not execute the shared battery or claim independent verification; parent integration and verifier remain necessary.
