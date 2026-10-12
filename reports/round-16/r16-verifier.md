# Round 16 independent verifier replay

## Replay

I independently ran the declared 13 serial modes from the repository root. Every invocation was exactly `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` with the listed optional flag; exits and durable receipts:

| Mode | Flag | Exit | Receipt | Observed failure set |
|---|---|---:|---|---|
| normal | `none` | 0 | `corpus/live/runs/20261012T185900519223Z-normal/measurements.json` | none |
| layer-alt-reverse | `--probe-layer-alt-reverse` | 1 | `corpus/live/runs/20261012T185901324537Z-layer-alt-reverse/measurements.json` | `reverse180_probe`: 180 Hz section contrast <6 dB or invalid (sole failure) |
| layer-alt-slope | `--probe-layer-alt-slope` | 1 | `corpus/live/runs/20261012T185902115885Z-layer-alt-slope/measurements.json` | `slope180_probe`: internal side-slope >.001 |
| layer-alt-join | `--probe-layer-alt-join` | 1 | `corpus/live/runs/20261012T185902922413Z-layer-alt-join/measurements.json` | `join180_probe`: internal gap >.03 |
| layer-alt-flat | `--probe-layer-alt-flat` | 1 | `corpus/live/runs/20261012T185903722668Z-layer-alt-flat/measurements.json` | `flat180_probe`: 180 Hz contrast <6 dB or invalid |
| layer-slope | `--probe-layer-slope` | 1 | `corpus/live/runs/20261012T185904521987Z-layer-slope/measurements.json` | `layer_slope_probe`: internal side-slope >.001 |
| layer-join | `--probe-layer-join` | 1 | `corpus/live/runs/20261012T185905321923Z-layer-join/measurements.json` | `join_probe`: internal gap >.03 |
| flat | `--probe-flat` | 1 | `corpus/live/runs/20261012T185906113983Z-flat/measurements.json` | `flat30_probe`: 30 Hz contrast <6 dB or invalid |
| layer-flat | `--probe-layer-flat` | 1 | `corpus/live/runs/20261012T185906908802Z-layer-flat/measurements.json` | `flat120_probe`: 120 Hz contrast <6 dB or invalid |
| slope | `--probe-slope` | 1 | `corpus/live/runs/20261012T185907685902Z-slope/measurements.json` | `slope_probe`: outer slope >.001 |
| failing | `--probe-failing` | 1 | `corpus/live/runs/20261012T185908411219Z-failing/measurements.json` | `ambience`: centroid out of band; endpoint jump >.03 |
| invalid | `--probe-invalid` | 1 | `corpus/live/runs/20261012T185908640403Z-invalid/measurements.json` | `short_sections` and `odd_sections`: section count; `corrupt`: decode; `wrong_format`: format (all expected failures) |
| normal-restore | `none` | 0 | `corpus/live/runs/20261012T185909363116Z-normal/measurements.json` | none |

The normal and restore receipts are exactly equal as parsed JSON. All five `_alt` distinctness entries pass: `ui_alt`, `impact_alt`, `movement_alt`, `ambience_alt`, and `stem_layer_alt`. Both receipts contain the same three canonical section-check records. The failure sets above were read from each receipt; exit 1 corresponds to the listed expected probe failure(s), while normal modes have no failures.

## Reverse control result

The reverse probe is the sole failure in its run: `reverse180_probe` reports only `sections: 180 Hz component amplitude contrast < 6 dB or invalid`. Decoded section component amplitudes are `0.04999787162649197` and `0.014999921578770435` FS; section RMS values are `0.03535383510924688` and `0.010606549683873855` FS, with `valid: true`. Signed contrast is **-10.457250572050894 dB** (existing pass rule is >= +6 dB). Internal join gap is `0.001190185546875` FS (<= .03) and side-slope mismatch `0.00079345703125` FS/sample (<= .001). Generic measurements pass: 4 s, 48 kHz mono, peak .04998779296875 FS, centroid 277.95138460286523 Hz; outer seam delta .0003662109375 FS and slope .0008544921875 FS/sample. Candidate `reverse180_candidate.wav`, alternate `reverse180_other.wav`, and generated `reverse180_probe.wav` have identical bytes and SHA-256 `c04441ef1ef6c02970e0c946efe0c750b19d3f41ef26865ce37e608ecda4e7d8`.

## Canonical artifact integrity

All 12 canonical WAVs were hashed from current bytes and compared to Git blobs at declared before-state `35d978c`; all 12 hashes match. Hashes:

| Artifact | SHA-256 |
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

## Limits

This establishes only the named deterministic fixture gates and this toolchain replay. Thresholds remain local numeric proxies; no auditory, musical, engine/adaptive, rights, external-reader, security, or production claim follows. No setup attempts failed. This is independent execution evidence, not final axis adjudication.
