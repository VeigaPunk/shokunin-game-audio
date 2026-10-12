# Round 19 independent verifier

## Replay

Ran the requested sixteen modes serially from the repository root using the fixture runner. Each row is an actual invocation in order; exit 1 is an intentional measured negative (including the invalid-input mode), not a setup failure. No replay command had a setup failure.

| # | Exact command | Exit | Receipt | Failure set / observed kinds |
|---:|---|---:|---|---|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261012T194313416491Z-normal/measurements.json` | `none` |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261012T194314266885Z-layer-third-slope-edge-pass/measurements.json` | `none` |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261012T194315116347Z-layer-third-slope-edge-fail/measurements.json` | `edgefail_probe: internal join side slope mismatch > .001 full scale per sample` |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261012T194315962524Z-layer-third-slope/measurements.json` | `slope200_probe: internal join side slope mismatch > .001 full scale per sample` |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261012T194316819969Z-layer-alt-reverse/measurements.json` | `reverse180_probe: 180 Hz component amplitude contrast < 6 dB or invalid` |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261012T194317674449Z-layer-alt-slope/measurements.json` | `slope180_probe: internal join side slope mismatch > .001 full scale per sample` |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261012T194318530324Z-layer-alt-join/measurements.json` | `join_probe: internal join adjacent sample gap > .03 full scale` |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261012T194319468760Z-layer-alt-flat/measurements.json` | `flat180_probe: 180 Hz component amplitude contrast < 6 dB or invalid` |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261012T194320317620Z-layer-slope/measurements.json` | `layer_slope_probe: internal join side slope mismatch > .001 full scale per sample` |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261012T194321177634Z-layer-join/measurements.json` | `join_probe: internal join adjacent sample gap > .03 full scale` |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261012T194322041320Z-flat/measurements.json` | `flat30_probe: 30 Hz component amplitude contrast < 6 dB or invalid` |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261012T194322899105Z-layer-flat/measurements.json` | `flat120_probe: 120 Hz component amplitude contrast < 6 dB or invalid` |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261012T194323732865Z-slope/measurements.json` | `slope_probe: loop seam slope mismatch > .001 full scale per sample` |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261012T194324519302Z-failing/measurements.json` | `ambience: centroid outside fixture band; endpoint jump > .03 full scale` |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261012T194324745715Z-invalid/measurements.json` | `invalid_probes: short_sections/odd_sections (section count), corrupt (decode), wrong_format (format)` |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261012T194325537157Z-normal/measurements.json` | `none` |

Receipt 15 contains the full `invalid_probes` records; the table names their observed failure kinds without duplicating that JSON.


## Edge-mode numerical inspection

Inspected complete `sections` and `measurements` objects in receipts 2 and 3. Both use the 200 Hz component, 96,000 samples per section, valid sections, and `sections.*.passed: true` (that field means section validity/contrast, not all internal join gates).

| Receipt | component amplitudes (first, second) FS | section RMS (first, second) FS | contrast | internal gap | internal side-slope | runner failure |
|---|---|---|---:|---:|---:|---|
| edge-pass `20261012T194314266885Z` | 0.014999984892417233, 0.049998039097271886 | 0.0106065941723389, 0.03535395352258335 | 10.457243003423983 dB | 0.000396728515625 FS | 0.0009765625 FS/sample | none |
| edge-fail `20261012T194315116347Z` | 0.014999984892417233, 0.049998039113914754 | 0.0106065941723389, 0.03535395353506875 | 10.45724300631526 dB | 0.000396728515625 FS | 0.001007080078125 FS/sample | sole `edgefail_probe` internal side-slope `> .001` |

Both runner records also show format/duration/level/spectrum checks and outer endpoint/slope checks passing. Relevant edge measurements: duration 4.0s, 48kHz mono, peak 0.04998779296875 FS, outer endpoint delta 0.001312255859375 FS, outer slope 0.00091552734375 FS/sample. The unchanged comparator is strict `>` .001: pass is 32/32768, fail 33/32768. The 200Hz component amplitude contrast, section RMS validity, and internal gap pass in both; only the fail control trips the internal side-slope gate.

## One-frame PCM and hashes

Compared decoded PCM16 frame arrays from both generated probe WAVs against canonical `stem_layer_third.wav`. Each is 192,000 samples and differs at exactly zero-based frame 96001: canonical `43`, edge-pass `45` (+2 counts), edge-fail `46` (+3 counts). SHA-256 of the full WAV files:

- canonical: `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445`
- edge-pass: `512b38026eb102fac4773bca1b61e7994261b6f6297e0ec544fb4b47b1104496`
- edge-fail: `48e2167dd405d05dc66aab304fc7b3c4712d2734dca021fdfd92d15a3e8d2a38`

## Canonical and restore checks

Independently SHA-256 hashed all 13 `corpus/artifacts/*.wav` files and compared each byte hash with `git show 7083a3f:<path>`; all 13 matched. The canonical list and hashes: `ambience.wav` b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198; `ambience_alt.wav` 2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc; `impact.wav` a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc; `impact_alt.wav` a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6; `movement.wav` 23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d; `movement_alt.wav` 51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639; `stem.wav` fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0; `stem_layer.wav` ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9; `stem_layer_alt.wav` 74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9; `stem_layer_third.wav` 3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445; `stem_sections.wav` 49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702; `ui.wav` 4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9; `ui_alt.wav` 166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f.

All five `_alt` distinctness records in initial normal and both edge receipts passed: `ui_alt`, `impact_alt`, `movement_alt`, `ambience_alt`, and `stem_layer_alt`. Compared first and restored normal parsed JSON recursively after excluding path/time identity fields; all remaining keys and numerical/outcome values were equal.

## Invalid-mode scope and limits

`--probe-invalid` returns `invalid_probes` for short sections, corrupt decode, wrong format, and odd section count. This verifies those malformed-input probes are rejected; it does not measure the 13 canonical WAVs or count as a normal canonical pass. The 200Hz boundary result is limited to these two one-frame PCM16 edits of this waveform and this runner/SoX float32 decode path. It establishes a local numeric threshold bracket, not a universal PCM grid, perceptual/audibility calibration, or production/engine behavior.
