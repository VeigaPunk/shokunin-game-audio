# Round 35 alt — independent movement candidate fit

## Scope and result

Independent numerical candidate fit for the declared .30 s movement-family coverage target. Candidate is scratch only at `corpus/live/round-35/alt/movement_third_candidate.wav`; it is not canonical and has not been integrated. No shared source, LOG, SCORECARD, canonical fixture, or other report was edited. No commits or push.

## Candidate construction

Scratch generator: `corpus/live/round-35/alt/create_candidate.py`. It generates 14,400 samples at 48 kHz, mono PCM16: a decaying 1.8 kHz tone plus a short seeded broadband attack (NumPy RNG seed 3501), with a short onset ramp. Candidate SHA-256: `0e5f815e1987e13646170571e1f1e977b25e3566d90ebcca558c72ed07851d44`.

## Project-helper measurements

Measured with the declared project helper `corpus/fixtures/measure_audio.py` via `measure()` (not a hand-implemented proxy):

| Fixture | duration | centroid | peak | RMS | failures |
|---|---:|---:|---:|---:|---|
| Candidate | 0.300 s | 4553.5833 Hz | 0.48950 FS | -14.0252 dBFS | none |
| movement | 0.240 s | 11934.4840 Hz | 0.53949 FS | -23.7799 dBFS | none |
| movement_alt | 0.360 s | 12024.2149 Hz | 0.63931 FS | -21.9873 dBFS | none |

Pair deltas (candidate relative to baseline centroid):

| Pair | duration delta | centroid relative delta |
|---|---:|---:|
| candidate vs movement | 0.060 s | 0.618452 (61.8452%) |
| candidate vs movement_alt | 0.060 s | 0.621299 (62.1299%) |

Candidate met requested duration, 48k mono PCM16 format, movement centroid band, peak/RMS checks; helper reported no failures. The .06 s duration deltas exceed the declared .020 s OR branch; centroid relative deltas also exceed the stated .10 selection criterion for both comparisons. These are numeric proxies only, not evidence of perceived distinction, sound quality, production fitness, rights, engine compatibility, publication, or promotion.

## Exact shell commands and exits

1. `python3 .shokunin/audio/corpus/live/round-35/alt/create_candidate.py` — exit **0**; generated candidate and printed frame count and SHA above.
2. `python3 .shokunin/audio/corpus/live/round-35/alt/measure_candidate.py` — first attempt exit **1**. Setup issue: helper returned a path relative to the project corpus root, but the candidate path passed as relative to repository root, causing `ValueError` in `Path.relative_to`; this was a path setup failure, not a failed numerical fit.
3. After resolving candidate path in the scratch measurement script: `python3 .shokunin/audio/corpus/live/round-35/alt/measure_candidate.py` — exit **0**; measured candidate and both baselines above.

An initial attempt to compose the helper invocation as a Python REPL string had a quoting syntax error before any shell command was executed; no shell exit code applies.

## Scratch contents

- `corpus/live/round-35/alt/create_candidate.py`
- `corpus/live/round-35/alt/measure_candidate.py`
- `corpus/live/round-35/alt/movement_third_candidate.wav`

No canonical adoption or integration claim. Parent integration and independent verification remain pending.
