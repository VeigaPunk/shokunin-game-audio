# Round 29 alternate negative-centroid fit

## Result

Independent scratch fit for a lower-centroid variant against the existing UI-shaped source. The measured pair is suitable for testing the existing absolute-centroid relative-difference predicate, subject to parent integration and runner verification. This is numerical fixture evidence only.

The scratch baseline reproduces the source formula at 5760 frames, 48 kHz, mono PCM16:
`0.38 * sin(2*pi*(700*t + 800*t*t)) * exp(-30*t)`, where `t = arange(5760)/48000`.
For variants I multiplied the phase argument by `k`: `0.38 * sin(2*pi*k*(700*t + 800*t*t)) * exp(-30*t)`. The lower-centroid candidates selected are `k=0.95` (below) and `k=0.94` (above). `measure_audio.measure` was called with unchanged `SPECS["ui"]` for both files, against the actual scratch WAVs via ffprobe, SoX, FFT and level measurements.

| file | k | duration (s) | centroid (Hz) | relative delta from base | ordinary failures |
|---|---:|---:|---:|---:|---|
| `r29_base.wav` | 1.00 | 0.120000 | 966.896659 | — | none |
| `r29_k0.95.wav` | 0.95 | 0.120000 | 871.155505 | 0.0990190 | none |
| `r29_k0.94.wav` | 0.94 | 0.120000 | 862.026457 | 0.1084606 | none |

Both variants are lower than baseline; duration delta is zero at reported precision. Format is 48 kHz mono PCM16, peak is about 0.376 FS, RMS about -19.992 dBFS, and centroid remains in the unchanged UI 250–4000 Hz band. Both pass ordinary checks using the same UI spec. Based on these values, the existing absolute relative difference is below `.10` for k=.95 and above `.10` for k=.94. No exact cutoff equality is asserted. A signed `(variant-base)/base` implementation would yield negative deltas for both and would fail to recognize the above-cutoff lower-centroid case; no code was changed here.

## Search observations and nonmonotonicity

Measured exploratory candidates (same baseline centroid 966.896659 Hz): k=.99 -> 941.760301 Hz, relative .0259969; .98 -> 919.118281 Hz, .0494142; .95 -> 871.155505 Hz, .0990190; .90 -> 865.698025 Hz, .1046633; .85 -> 911.275903 Hz, .0575250; .80 -> 845.464245 Hz, .1255899; .70 -> 669.329005 Hz, .3077554; .60 -> 713.766662 Hz, .2617963; .50 -> 503.940015 Hz, .4788067. The k=.99/.98 candidates did not reach the below-cutoff failing side, while k=.90 was a passing-above candidate but was not used in the closer pair. The centroid response is plainly nonmonotonic across this parameter sweep (for example, centroid rises from k=.90 to .85 as k decreases). Thus k is a fit parameter, not a monotonic proxy for centroid delta; the two measured points are not evidence of smoothness.

## Commands and setup

- `python3 .shokunin/audio/corpus/live/round-29/alt/fit.py` first attempt: **exit 1**. The script passed a relative scratch path to the project measurement helper, which calls `Path.relative_to(ROOT)`; the resulting path was not under its absolute project root. Setup/path issue, not a candidate-fit failure. I corrected only the scratch script to pass resolved absolute paths.
- `python3 .shokunin/audio/corpus/live/round-29/alt/fit.py` after correction: **exit 0**. This scratch script generated the source and variants, then called project `measure_audio.measure(..., SPECS["ui"], path)` for each and printed the recorded values above and exploratory values. There were no failed ordinary format/level/band/duration checks in the listed candidates.

All generated inputs/scripts are confined to `.shokunin/audio/corpus/live/round-29/alt/`; this report is the only report written. No fixture source, runner, LOG, scorecard, canonical artifact, or other report was edited. No exact `.10` equality, smoothness, perceptual, rights, engine, publication, or promotion claim.
