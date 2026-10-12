# Round 12 alternate 180 Hz candidate (r12-alt)

Scope: independently synthesized original mono PCM16 candidate `layer_alt_other.wav` in the assigned round-12 scratch. No source, LOG, SCORECARD, canonical artifact, or commit changes. No shell commands were run; calculations below used Python/NumPy and Python's WAV reader. Thus there are no shell command exits to report.

## Recipe and artifact

At 48,000 Hz for 192,000 samples, with `t = arange(192000)/48000`, synthesize

`x(t) = A(t) sin(2π·180·t) + 0.006 sin(2π·90·t)`,

where `A(t)=0.016` for `t<2` and `A(t)=0.055` otherwise. Quantize using `round(clip(x,-1,1)*32767)` to little-endian signed PCM16, mono WAV. This is an original synthetic candidate, not a borrowed sample. Scratch path: `.shokunin/audio/corpus/live/round-12/layer_alt_other.wav`. SHA-256: `1fd0d1f57d92b03a26d15cd75d5e441de4cc739bec13e2af2e8e3a02a75eb3ee`.

## Numeric fit (decoded PCM)

- Format/duration: 48,000 Hz, mono, 16-bit, 192,000 frames, 4.000 s; passes expected format and ±1 ms duration.
- Peak: `0.0592974639` FS (<.95); RMS `0.0289523556` FS, `-30.7663219 dBFS` (> .001 FS).
- Whole-file weighted positive-frequency spectral centroid: `288.3517524 Hz`; bandwidth `1143.6035747 Hz`. Compared with canonical `stem_layer` centroid `190.1434178 Hz` measured with the same float32 decode/FFT method, relative centroid delta is `0.516` (51.6%; threshold .10). Duration delta is 0.000 s. Generic `_alt`-style distinctness passes by centroid.
- Outer endpoint delta: `0.00137333293` FS (≤.03); endpoint slope mismatch: `0.00091555528` FS/sample (≤.001).
- 180 Hz component amplitude in 2 s halves: `[0.0159995990, 0.0549997109]` FS. Section RMS: `[0.0120827856, 0.0391214019]` FS. Both component amplitudes ≥.01 and RMS values ≥.001. Amplitude contrast: `10.72502618 dB` (≥6 dB), valid.
- Internal join adjacent-sample gap: `0.00045777764` FS (≤.03). Internal join side-slope mismatch: `0.00094607379` FS/sample (≤.001).
- Result against stated fixture-local checks: **no fit failures**. This is numeric fixture evidence only; no audible, engine/adaptive playback, music, threshold calibration, security, or production claim.

## Iteration note

I initially explored a single-component `.015/.050` 180 Hz waveform and a `.018/.060` 180 Hz plus 60 Hz waveform; the former also fit these numeric checks, while the latter's outer slope was `0.00100711081` FS/sample and would miss the `.001` limit. I replaced the scratch candidate with the independent 180+90 Hz recipe above. These were local exploratory calculations, not fixture-runner invocations or accepted source changes. Final scratch contains only `layer_alt_other.wav` plus the executor-owned `layer_alt_candidate.wav`; I did not modify the latter.
