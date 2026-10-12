# Round 19 guard — historical baseline inventory

## Scope and provenance

I read `.shokunin/audio/LOG.md`, the fixture builder and measurement runner source, and the Round 18 guard/verifier reports. This is a historical inventory, not a fresh replay or current-file verification. The 13 canonical hashes below are transcribed from the Round 18 independent verifier’s inventory against baseline `7083a3f` (the declared Round 19 baseline is `010f88b`). The prior 14-mode outcomes and receipt IDs are transcribed from that verifier’s fresh Round 18 replay; they are historical results, not Round 19 runs. I ran no fixture command and calculated no hashes.

## Thirteen canonical WAV SHA-256 values

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
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` |

## Historical Round 18 14-mode replay

Commands were recorded from the repository root. These are the exact command strings, historical exits, receipt IDs, and outcomes in `r18-verifier.md`; they are not runs performed for Round 19. Exit 1 is the expected targeted failure for a negative/invalid probe, not a setup error.

| # | Exact command | Exit | Historical receipt | Historical result |
|---:|---|---:|---|---|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `20261012T192010370491Z-normal` | pass; no failures |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `20261012T192011238149Z-layer-third-slope` | `slope200_probe`: internal side-slope mismatch > .001 FS/sample |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `20261012T192012084965Z-layer-alt-reverse` | `reverse180_probe`: 180 Hz contrast < 6 dB or invalid |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `20261012T192012939855Z-layer-alt-slope` | `slope180_probe`: internal side-slope mismatch > .001 FS/sample |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `20261012T192013795795Z-layer-alt-join` | `join180_probe`: internal adjacent gap > .03 FS |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `20261012T192014666885Z-layer-alt-flat` | `flat180_probe`: 180 Hz contrast < 6 dB or invalid |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `20261012T192015528669Z-layer-slope` | `layer_slope_probe`: internal side-slope mismatch > .001 FS/sample |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `20261012T192016385023Z-layer-join` | `join_probe`: internal adjacent gap > .03 FS |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `20261012T192017253394Z-flat` | `flat30_probe`: 30 Hz contrast < 6 dB or invalid |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `20261012T192018105092Z-layer-flat` | `flat120_probe`: 120 Hz contrast < 6 dB or invalid |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `20261012T192018942177Z-slope` | `slope_probe`: outer seam slope mismatch > .001 FS/sample |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `20261012T192019728750Z-failing` | `ambience`: centroid outside band and endpoint jump > .03 FS |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `20261012T192019957962Z-invalid` | invalid inputs: short/odd section count, corrupt decode, wrong format |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `20261012T192020754277Z-normal` | pass; no failures, parsed JSON equal to initial normal |

The prior verifier reported five `_alt` distinctness checks passed and all 13 canonical artifact hashes matched baseline `7083a3f`. Its 200 Hz +8-count slope probe had contrast 10.457243020771665 dB and internal gap 0.000396728515625 FS, while the side-slope value 0.00115966796875 FS/sample exceeded the unchanged .001 limit; that was the sole failure. This paragraph summarizes prior evidence only. `--probe-invalid` checks invalid-input fixtures; it does not measure canonical WAVs. The verifier reported no setup errors in its historical replay; I made no attempts, so there are no task-run commands/exits or setup errors to report.

No audible, perceptual, musical, engine, rights, security, external JSON compatibility, or production claim is made. I edited only this assigned report; no source, LOG, SCORECARD, canonical artifact, or other report was edited by me.
