# Round 15 independent serial replay — Luna verifier

I read the round-15 LOG, wave-1 reports, integrated builder/runner, and fixture knowledge before replay. Ran commands serially from repository root; no setup errors occurred. No source, LOG, SCORECARD, or canonical artifact edits were made.

## Exact commands, exits, receipts

| # | Exact command | Exit | Receipt (`measurements.json`) |
|---:|---|---:|---|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261012T184817402790Z-normal/measurements.json` |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261012T184818195955Z-layer-alt-slope/measurements.json` |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261012T184819001822Z-layer-alt-join/measurements.json` |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261012T184819795852Z-layer-alt-flat/measurements.json` |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261012T184820584760Z-layer-slope/measurements.json` |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261012T184821377846Z-layer-join/measurements.json` |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261012T184822168475Z-flat/measurements.json` |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261012T184822958807Z-layer-flat/measurements.json` |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261012T184823723496Z-slope/measurements.json` |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261012T184824448802Z-failing/measurements.json` |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261012T184824678600Z-invalid/measurements.json` |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261012T184825401717Z-normal/measurements.json` |

All runs completed. An exit of 1 is the expected negative-control process status; it is not counted as a setup error.

## New slope probe and scratch identity

The new mode receipt `.shokunin/audio/corpus/live/runs/20261012T184818195955Z-layer-alt-slope/measurements.json` reports exactly one failure: `slope180_probe: sections: internal join side slope mismatch > .001 full scale per sample`. Its 180 Hz section evidence is:

- component amplitudes `[0.014999921578770435, 0.04999787182121829]` FS; valid and passed;
- amplitude contrast `10.457250605879763 dB` (>= 6 dB);
- internal adjacent gap `0.0003662109375` FS (<= .03);
- internal side-slope mismatch `0.001251220703125` FS/sample (> .001).

The measurement's generic format/duration/level/centroid checks and outer loop checks pass; no other failure is present. Source uses strict `>` comparisons for internal gap and side-slope (`measure_audio.py` lines 224–227), so equality at a bound would not fail. This is numeric fixture evidence, not a perceptual claim.

Generated `.shokunin/audio/corpus/live/round-15/slope180_probe.wav` has SHA-256 `b1678716839c2fada2a46f6771039c758500ac5621e9e874122930177cf4ac57`; corrected selected worker candidate has SHA-256 `b1678716839c2fada2a46f6771039c758500ac5621e9e874122930177cf4ac57`; files are byte-identical. Compared decoded PCM16 arrays against canonical `stem_layer_alt.wav`, exactly one frame differs: frame 96001, count 39 -> 52 (+13); all other frames match. This confirms corrected direction, not the initial reversed count statement in executor's first draft.

## Existing behavior and canonical integrity

- Normal and restore receipts are equal as complete parsed JSON objects: **yes**.
- All five `_alt` distinctness results in the normal receipt pass: **yes** (`ui_alt`, `impact_alt`, `movement_alt`, `ambience_alt`, `stem_layer_alt`). Clean 180 Hz `stem_layer_alt` section remains valid and passes internal gap/slope plus contrast checks.
- Existing negative controls preserve expected named failure sets: join180 and prior join are gap-only; flat180 / flat30 / flat120 are contrast-only; prior layer-slope and outer slope are slope-only; failing ambience has centroid and endpoint failures; invalid mode reports short/odd section count, decode, and format errors. Full JSON is retained in each receipt above.
- Each of the twelve canonical WAV files was compared byte-for-byte to its Git blob with `git show 0928e9e:.shokunin/audio/corpus/artifacts/<name>` and SHA-256. All matched:

| Canonical WAV | SHA-256 (Git blob = working file) |
|---|---|
| `ambience.wav` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` |
| `ambience_alt.wav` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` |
| `impact.wav` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` |
| `impact_alt.wav` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` |
| `movement.wav` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` |
| `movement_alt.wav` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` |
| `stem.wav` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` |
| `stem_layer.wav` | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` |
| `stem_layer_alt.wav` | `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` |
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` |
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` |

No audible, musical, engine/adaptive-behavior, threshold-calibration, external compatibility, security, or production-quality inference follows from this deterministic replay. Numeric limits are existing local fixture gates only.
