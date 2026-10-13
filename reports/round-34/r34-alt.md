# Round 34 alt — independent impact fit

## Scope and setup
Independent scratch-only .40 s impact candidate fit using the project measurement helper. No canonical artifact, fixture builder, LOG, SCORECARD, or other report was changed. Candidate remains in scratch and is not canonical pending parent integration and verification.

Exact shell command run: `python3 .shokunin/audio/corpus/live/round-34/alt/fit.py` — exit 0.

## Measured candidate
Scratch WAV: `.shokunin/audio/corpus/live/round-34/alt/impact_third_candidate.wav`
SHA-256: `d14376241f409f07edde30fbcef86b5f060ff36f731b7578fd9934d1dc1b39bf`
Project helper `measure_audio.measure()` result: duration 0.400000 s; 48,000 Hz mono PCM16; peak 0.4561157 full scale; RMS −20.849585 dBFS; spectral centroid 6,838.143303 Hz; spectral bandwidth 6,893.935963 Hz; failures `[]`. Fit passes specified ordinary numerical format/level/band checks.

## Pair deltas
Used existing round-34 distinctness rule: duration delta ≥0.020 s **OR** centroid relative delta ≥0.10. Relative centroid delta is absolute difference divided by baseline centroid.

| Baseline | Baseline duration | Baseline centroid | Candidate duration delta | Candidate centroid relative delta | Existing OR rule |
|---|---:|---:|---:|---:|---|
| `impact.wav` | 0.320 s | 10,843.127203 Hz | 0.080000 s | 0.369357 | Pass (both) |
| `impact_alt.wav` | 0.320 s | 473.791536 Hz | 0.080000 s | 13.432810 | Pass (both) |

Both pair deltas meet preferred centroid-relative ≥0.10 and duration ≥0.020 requirements. Baseline figures are from the declared round-33 normal helper receipt; candidate was measured directly with the same project helper.

## Limits
This is an independent numerical fit only. Duration and weighted positive-frequency spectral centroid are proxies, not evidence of perceptual distinctness or auditory quality. No audition, production, rights, engine, publishing, or promotion claim is made. Candidate is scratch, not canonical; parent must integrate and independently verify before any admission.
