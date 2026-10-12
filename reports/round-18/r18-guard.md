# Round 18 guard — historical baseline inventory

## Scope and provenance

This is a historical inventory for the Round 18 guard assignment. I read `.shokunin/audio/LOG.md`, the fixture runner/builder source, and `.shokunin/audio/reports/round-17/r17-verifier.md`. I did **not** run the fixture runner, replay any mode, calculate hashes, or verify current files against Git blobs. The baseline SHA-256 values and Round 17 mode results below are transcribed from the Round 17 verifier report. Round 18's declared baseline is the 13 canonical artifacts at `7083a3f`; this report is not fresh verification of that baseline.

## Thirteen baseline canonical artifact hashes

| Canonical WAV | SHA-256 |
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
| `stem_layer_third.wav` | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` |
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` |
| `ui.wav` | `4bb56ddf502e0d0249f191e90e57ebe0adff7bee7649efa2c402c905c4c53af9` |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` |

## Round 17 historical serial mode outcomes

The following are the 13 commands and exits recorded in `r17-verifier.md`. They are historical outcomes, not Round 18 runs. Negative-control exit 1 denotes the expected probe failure; it is not setup failure. All commands were recorded as run from the repository root. The first and restore normal runs both exited 0, and the report states their parsed receipts were equal.

| Mode | Exact command | Exit | Historical expected failure/result |
|---|---|---:|---|
| normal | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | No failures; five `_alt` distinctness checks pass |
| layer-alt-reverse | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `reverse180_probe`: 180 Hz contrast below 6 dB or invalid |
| layer-alt-slope | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `slope180_probe`: internal join side-slope mismatch > .001 FS/sample |
| layer-alt-join | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `join180_probe`: internal join adjacent gap > .03 FS |
| layer-alt-flat | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `flat180_probe`: 180 Hz contrast below 6 dB or invalid |
| layer-slope | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `layer_slope_probe`: internal join side-slope mismatch > .001 FS/sample |
| layer-join | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `join_probe`: internal join adjacent gap > .03 FS |
| flat30 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `flat30_probe`: 30 Hz contrast below 6 dB or invalid |
| layer-flat | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `flat120_probe`: 120 Hz contrast below 6 dB or invalid |
| outer-slope | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `slope_probe`: outer loop slope mismatch > .001 FS/sample |
| failing | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `ambience`: centroid outside band and endpoint jump > .03 FS |
| invalid | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | Invalid-probe results: short/odd section count, corrupt decode, wrong format |
| restore normal | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | No failures; parsed JSON equal to initial normal receipt |

Important scope distinction: `--probe-invalid` records invalid-input checks only; it does not measure the canonical WAVs. Round 17's report records no setup failure in its replay. I made no setup attempt, so there is no setup error or command exit to report for my task.

No audible, engine, perceptual, musical, rights, security, external JSON compatibility, or production claim is made. No source, LOG, SCORECARD, canonical artifact, or other report was edited by me.
