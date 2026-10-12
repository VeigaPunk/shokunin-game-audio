# Audio round 2 independent verification

Verifier: `r2-verifier` (non-author). I independently replayed the integrated builder/measurement entry point. I changed no builder, measurement code, fixture definition, log, scorecard, or canonical artifact by hand. Entry-point runs rebuild canonical WAVs; the clean restore returned all nine hashes to the pre-probe set.

## Commands and outcomes

All successful commands ran from the repository root:

1. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` — exit **0**, receipt `corpus/live/runs/20261012T161812132927Z-normal/measurements.json`; all nine failure lists empty.
2. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` — exit **0**, receipt `corpus/live/runs/20261012T161815632474Z-normal/measurements.json`; all nine failure lists empty. SHA-256s of all nine raw WAVs after run 1 and run 2 were identical.
3. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` — exit **1** as expected, receipt `corpus/live/runs/20261012T161822938808Z-failing/measurements.json`. Only ambience failed: centroid outside band and endpoint seam delta > 0.03.
4. `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` — exit **0**, receipt `corpus/live/runs/20261012T161825061249Z-normal/measurements.json`; all failures empty and all nine hashes matched the clean set.

Telemetry: an earlier malformed shell invocation `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` (the path was passed as part of the executable name) exited **127** with `/usr/bin/bash: line 4: python3 .shokunin/audio/corpus/fixtures/measure_audio.py: No such file or directory`. This was a command-construction error, not a fixture/toolchain failure; the corrected commands above succeeded.

## Determinism and baseline integrity

All nine WAV SHA-256s were identical across the two consecutive clean runs and after the failing-probe/restore cycle:

| WAV | SHA-256 |
|---|---|
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` |
| `impact.wav` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` |
| `impact_alt.wav` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` |
| `movement.wav` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` |
| `movement_alt.wav` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` |
| `ambience.wav` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` |
| `ambience_alt.wav` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` |
| `stem.wav` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` |

Compared the five original WAV byte streams from `git show 31d8e9e:.shokunin/audio/corpus/artifacts/<name>` to current built outputs. `ui.wav`, `impact.wav`, `movement.wav`, `ambience.wav`, and `stem.wav` all match their HEAD hashes exactly. The four `_alt.wav` files are additions and have no baseline comparison.

## Measured results

Normal receipt measurements (decoded PCM; duration, RMS dBFS, centroid Hz, endpoint delta where applicable):

| Fixture | Duration | RMS dBFS | Centroid Hz | Endpoint delta | Failure |
|---|---:|---:|---:|---:|---|
| ui | 0.12 s | -19.99 | 966.90 | n/a | none |
| ui_alt | 0.16 s | -20.53 | 1423.15 | n/a | none |
| impact | 0.32 s | -20.40 | 10843.13 | n/a | none |
| impact_alt | 0.32 s | -17.33 | 473.79 | n/a | none |
| movement | 0.24 s | -23.78 | 11934.48 | n/a | none |
| movement_alt | 0.36 s | -21.99 | 12024.21 | n/a | none |
| ambience | 2.00 s | -18.15 | 36.62 | 0.000671 | none |
| ambience_alt | 2.00 s | -17.67 | 58.02 | 0.001892 | none |
| stem | 2.00 s | -14.88 | 272.68 | 0.011383 | none |

All nine were mono 48 kHz, within declared duration tolerances and level/centroid bounds. Variant distinctness uses decoded duration delta >= 0.020 s OR relative whole-file magnitude-weighted FFT centroid delta >= 0.10:

| Variant | Duration delta | Relative centroid delta | Passing basis | Result |
|---|---:|---:|---|---|
| ui_alt vs ui | 0.040 s | 0.471877 (47.19%) | both | pass |
| impact_alt vs impact | 0.000 s | 0.956305 (95.63%) | centroid | pass |
| movement_alt vs movement | 0.120 s | 0.007519 (0.75%) | duration | pass |
| ambience_alt vs ambience | 0.000 s | 0.584514 (58.45%) | centroid | pass |

Ambience and ambience_alt endpoint deltas are below the local 0.03 threshold. The positive control is rejected by both centroid and endpoint checks; the seam failure is directly observed.

## Decision and limits

Independent evidence supports the declared round-2 coverage claim: all four variants are generated, present, satisfy the numeric distinctness rule and existing fixture bounds, while all five originals remain byte-identical to commit `31d8e9e`. Repeated clean builds are byte-identical; corrupted ambience is rejected before clean restoration.

**SHONEN box 2 (end-to-end domain task executed and logged): supported for the lane lead to check**, with this report as named non-author evidence and the receipts above. The task ran end-to-end as source generation, headless measurement, negative control, and restoration. I do not edit SHONEN state. This does not establish other boxes.

Scope caveats: bounds are fixture-local, not mastering standards. Endpoint sample difference does not establish slope/phase continuity, codec/runtime loop behavior, or perceptual seamlessness. Whole-file centroid is a coarse spectral summary. No perceptual-quality, production-readiness, publishing, or rights claim is made. Three short SFX report null integrated LUFS due to documented ebur128 gated-floor handling; RMS is reported separately. No auditory evaluation was performed.
