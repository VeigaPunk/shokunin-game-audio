# Round 10 alternate isolated join control — r10-control

## Result
Created the independent original analytic PCM candidate at `corpus/live/round-10/join_alt_candidate.wav`. It is 4.000 s, 48 kHz, mono, 192,000 float32 samples (WAV payload 768,000 bytes). Its internal boundary is between sample indices 95,999 and 96,000 (the boundary time is 2.000 s). The only deliberately altered sample is index 96,000: add +0.04 to the second section's 120 Hz sine sample. This creates an adjacent decoded-sample gap of **0.04062829 FS**, above the declared 0.03 FS bound, while retaining the outer loop endpoint and slope equality.

Formula used: for integer sample index `i`, `x[i] = A(i) * sin(2*pi*120*i/48000)`, where `A=.04` for `i<96000`, otherwise `.12`; then `x[96000] += .04`. The result was serialized as IEEE float32 little-endian PCM in mono WAV. No borrowed audio or perceptual judgment was used.

## Measurements (analytic PCM / decoded indexing)

- Section 120 Hz FFT amplitudes, using `2*abs(rfft(section)[240])/96000`: **0.04**, **0.12** FS; contrast `20*log10(0.12/0.04)` = **9.54243 dB** (>=6 dB).
- Internal join jump `abs(x[96000]-x[95999])`: **0.04062829 FS** (>0.03).
- Outer endpoint delta `abs(x[0]-x[-1])`: **0 FS**; outer slope delta `abs((x[-1]-x[-2])-(x[1]-x[0]))`: **0 FS/sample**.
- Peak: **0.12 FS** (<.95); RMS: **0.06324562 FS** (above .001); whole-signal weighted FFT magnitude centroid: **1577.75 Hz**, inside `stem_layer`'s 100–2000 Hz band. Duration/rate/channel count match the fixture spec. These are the generic numeric bounds inspected; this is a candidate-only calculation, not a run of the harness against this scratch path.
- SHA-256: `8ab505d1151edbe43bdef6f323ab7fb6fd3d0a3f8fa40397248f5919a3f26c7a`.

## Commands / exits

- `ffprobe -v error -show_entries stream=sample_rate,channels:format=duration -of json .shokunin/audio/corpus/live/round-10/join_alt_candidate.wav` — exit **0**; reported 48,000 Hz, one channel, duration 4.000000 s.
- `sox .shokunin/audio/corpus/live/round-10/join_alt_candidate.wav -t f32 -e floating-point - stats` — exit **0**. This emitted raw binary float samples to stdout (not a textual stats summary); no quantitative claim above relies on that output.

This independent alternate is numerically consistent with an isolated *sample-gap* negative control under the declared bounds. The measurement is only an adjacent-sample gap proxy. It does not show click-free transitions, slope continuity at the internal join, adaptive engine timing, audible quality, or production readiness. Parent/verifier should replay this exact candidate through the eventual measurement path before treating isolation as validated there.
