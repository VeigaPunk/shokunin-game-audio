# Round 37 — independent alt ambience below-threshold fit

## Result

Generated an original pair of analytical looping WAVs in `.shokunin/audio/corpus/live/round-37/alt/`: `ambience_base.wav` and `ambience_alt.wav`. Both are 2.0 s, 48 kHz mono PCM16. The baseline is a sum of 50, 90, and 130 Hz sinusoids; the variant adds a 170 Hz sinusoid. They are nonidentical (SHA-256: baseline `c30d80d638264348cbbd500380823009bda4c9588736e979a21ade208a5ed93c`; variant `98f017c1e49344c74a225d970fb1ca3c6e3255ee54071d877ed810b825999b20`).

The project helper `corpus/fixtures/measure_audio.py` measured both using `(2.0, 5, 200, True)`. Baseline centroid: `81.12000109101983 Hz`; variant centroid: `85.4656028614171 Hz`; baseline-relative centroid delta: `0.05357004082780189` (nonzero and strictly below `.10`, also above `.05`). Duration delta: exactly `0.0 s`.

| Measurement | Baseline | Variant | Result |
|---|---:|---:|---|
| Duration | 2.0 s | 2.0 s | delta 0.0 s |
| Format | 48 kHz mono PCM16 | 48 kHz mono PCM16 | pass |
| Peak | 0.30999755859375 FS | 0.324981689453125 FS | both < .95 |
| RMS | -16.26194127560922 dBFS | -16.241322201081378 dBFS | both above .001 linear RMS |
| Centroid | 81.12000109101983 Hz | 85.4656028614171 Hz | both within 5–200 Hz |
| Endpoint delta | 0.002777099609375 FS | 0.003082275390625 FS | both < .03 |
| Slope mismatch | 0.000030517578125 FS/sample | 0.000030517578125 FS/sample | both < .001 |
| Project helper failures | `[]` | `[]` | ordinary/seam checks pass |

Under the existing generic distinctness OR rule, duration arm (`0.0 >= .020`) is false and centroid arm (`0.05357004082780189 >= .10`) is false. Thus this distinct, equal-duration pair falls below both arms; rejection would be solely for distinctness, with no ordinary or seam failure. This is a hand-calculated application of the existing rule: no new opt-in runner mode exists in the checked-in helper, so no gate/runner receipt or executed rejection is claimed.

## Search, setup, and fit record

Searched existing live-corpus ambience-named files before generation. Hits were `corpus/live/round-2/ambience_alt.wav`, `corpus/live/round-36/alt/ambience_alt_candidate.wav`, and `corpus/live/round-36/executor/ambience_third.wav`; no existing round-37 pair was present. The generated pair has distinct hashes and distinct analytic compositions. This is not evidence of perceptual uniqueness.

Generation was performed directly in the Python REPL, not by a shell command. First measurement invocation was a **setup/path error**, not a numeric fit: `python3 .shokunin/audio/corpus/live/round-37/alt/measure_pair.py` — exit `1`; the script passed relative paths and the helper's `path.relative_to(ROOT)` raised `ValueError` because those paths were not rooted under the helper's corpus root. After changing only the scratch script to pass absolute candidate paths, the exact same shell command `python3 .shokunin/audio/corpus/live/round-37/alt/measure_pair.py` exited `0` and produced the measurements above. No numeric fit attempt failed; there was no fit rejection.

All writes were limited to this report and `.shokunin/audio/corpus/live/round-37/alt/`. No shared source, LOG, SCORECARD, canonical asset, other report, or commit/push was touched.

## Limits

These results are numerical controls only. Centroid is a weighted positive-frequency centroid, not a full-spectrum or perceptual similarity measure. Endpoint/slope checks are seam proxies and do not establish seamless perception. No audition, sound-quality, production, rights, engine, publish, or promotion claim is made.
