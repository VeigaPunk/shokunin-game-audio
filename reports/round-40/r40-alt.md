# R40 alternate independent fit (LEAF)

## Scope and method
Read the R40 declaration in `.shokunin/audio/LOG.md`. This independent numeric fit used only `.shokunin/audio/corpus/live/round-40/alt/` for scratch WAVs. No shared sources, LOG, SCORECARD, canonical assets, other reports, or constants were edited. No runner mode exists for this new test yet, and I did not invoke or modify the runner. I did not audition. The claim here is limited to decoded PCM fixture calibration, not sound quality, production, rights, engine, publish, or promotion.

Created two original source-generated 2.0 s loops, each 96,000 frames, mono 48 kHz PCM16. Both use a 60 Hz, 0.2-amplitude cosine plus a tiny endpoint ramp; the first decoded PCM value is 6554 counts (0.20001220703125 FS). I set the last PCM value to first + the target count and set the penultimate value to match the first-side sample increment, making decoded outer side-slope mismatch zero. Values shown below are measured after SoX decoded each WAV to float32, then analyzed as float64. Relative endpoint delta is exact integer PCM-count delta / 32768.

## Selected fit: ordinary checks and endpoint bracket

| fixture | SHA-256 | decoded frames / format | first → last (PCM16 counts) | endpoint delta FS | outer slope mismatch FS/sample | peak FS | RMS dBFS | centroid Hz | expected endpoint result |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| `edge983.wav` | `97bd1cd798108981338888ddb5c972f5bd6db3ab5311d65abdb14191f1b8a090` | 96000, 48k mono PCM16, 2.000 s | 6554 → 7537 | 983/32768 = 0.029998779296875 | 0.0 | 0.23004150390625 | -16.925057863412828 | 823.4143890979104 | pass (`<= .03`) |
| `edge984.wav` | `5cc7de5f8d65d78ccb270936d2e5054ebc1d447d2914016409a7dbbaed9c19a6` | 96000, 48k mono PCM16, 2.000 s | 6554 → 7538 | 984/32768 = 0.030029296875 | 0.0 | 0.230072021484375 | -16.925057863412828 | 824.1228156393917 | fail (sole expected `> .03` endpoint check) |

Both candidates are far above the `.001` RMS minimum and below `.95` peak ceiling. Centroid lies in the ambience 5–200 Hz band? **No**: it is 823–824 Hz, so this pair does *not* satisfy the declared ordinary centroid check and is not a qualifying fit. This is a failed numeric fit, not a runner result. The endpoints and slope bracket correctly, but the primary component choice was unsuitable for this fixture band. Do not use this pair as an accepted calibration candidate.

## Candidate misses (separate from setup errors)

I explored low-frequency sine/ramp candidates and discovered that the endpoint correction/ramp introduced broadband spectral energy; measured centroids landed around 800–1023 Hz, above the 200 Hz ambience ceiling. Several sine candidates also missed slope: at 0.6 amplitude/30 Hz, side-slope mismatch was 0.03235 FS/sample; 0.6/100 Hz was 0.03787; 0.8/50 Hz was 0.03522. A 0.15-amplitude/30 Hz variant had a slope within limit (0.00061035) but centroid 959.4447 Hz. A 0.2-amplitude/60 Hz variant initially had slope 0.00158691 (over limit), before explicit penultimate-sample matching; the corrected selected pair then had slope zero but still failed centroid. These are numeric failed fits, not setup failures.

## Commands and execution status

Exact shell commands used for the final WAV decode/probe, with exit status:

- `ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-40/alt/edge983.wav` — exit 0; reported 48000 Hz, mono, `pcm_s16le`, 16 bits, duration 2.000000 s.
- `sox .shokunin/audio/corpus/live/round-40/alt/edge983.wav -t f32 -e floating-point -` — exit 0; produced decoded float32 PCM (96000 samples; stdout was captured by the inspection wrapper).
- `ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-40/alt/edge984.wav` — exit 0; same format/duration.
- `sox .shokunin/audio/corpus/live/round-40/alt/edge984.wav -t f32 -e floating-point -` — exit 0; produced decoded float32 PCM (96000 samples; stdout captured).
- `sox .shokunin/audio/corpus/live/round-40/alt/edge983.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-40/alt/edge983.f32` — exit 0; temporary decode file removed after measurement.
- `sox .shokunin/audio/corpus/live/round-40/alt/edge984.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-40/alt/edge984.f32` — exit 0; temporary decode file removed after measurement.

No runner command was run; therefore there is no observed pass/fail receipt or runner exit code. No setup errors occurred. The output of this independent task is a **failed fit** because centroid is outside range, despite correct endpoint counts and slope. A future candidate must keep its decoded centroid in 5–200 Hz while retaining the endpoint bracket and slope pass, then be tested by the integrated runner.
