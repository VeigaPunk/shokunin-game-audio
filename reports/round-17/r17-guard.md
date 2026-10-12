# Round 17 guard inventory — historical only; no replay

## Scope and provenance

I read the Round 17 declaration in `.shokunin/audio/LOG.md`, the fixture runner source, and Round 16 guard/verifier reports. This is a historical inventory, not a current-state verification. I ran no fixture, replay, Git, or shell command and did not calculate current hashes. The twelve hashes and Round 16 outcomes below are transcribed from `reports/round-16/r16-verifier.md`, which says it hashed current files against Git blobs at `35d978c`; Round 17 declares clean before-state `6fb9e80`. The prior report does not itself establish those hashes against `6fb9e80`, so this is not a verified Round 17 baseline comparison.

## Twelve canonical WAV hashes (recorded Round 16 inventory)

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
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` |
| `ui.wav` | `4bb56ddf502e0d0249f191e90e57ebe0adff7bee7649efa2c402c905c4c53af9` |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` |

## Round 16 historical mode/failure inventory

Round 16 verifier records commands of the form `python3 .shokunin/audio/corpus/fixtures/measure_audio.py [flag]` from the repository root. The following exits/failure sets are copied from that report; **they are not Round 17 runs**.

| Mode | Exact command | Exit | Recorded failure set |
|---|---|---:|---|
| normal | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | none; five `_alt` distinctness checks pass |
| reverse180 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `reverse180_probe`: signed 180 Hz contrast <6 dB (sole failure) |
| slope180 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `slope180_probe`: internal side-slope >.001 |
| join180 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `join180_probe`: internal gap >.03 |
| flat180 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `flat180_probe`: 180 Hz contrast <6 dB or invalid |
| layer-slope | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `layer_slope_probe`: internal side-slope >.001 |
| layer-join | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `join_probe`: internal gap >.03 |
| flat30 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `flat30_probe`: 30 Hz contrast <6 dB or invalid |
| flat120 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `flat120_probe`: 120 Hz contrast <6 dB or invalid |
| outer-slope | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `slope_probe`: outer slope >.001 |
| failing | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | ambience centroid out of band and endpoint jump >.03 |
| invalid | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | short/odd sections: section count; corrupt: decode; wrong format: format |
| normal restore | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | none; parsed JSON equals initial normal receipt |

The Round 16 verifier reports all five `_alt` distinctness entries passing (`ui_alt`, `impact_alt`, `movement_alt`, `ambience_alt`, `stem_layer_alt`). That historical verifier run had no setup errors. Exit 1 on its negative-control modes represents expected fixture failures, not failed setup.

## Commands run for this guard task

No shell commands were run, so there are no command exits or setup failures for this task. I did not replay any mode or independently validate hashes. No source, LOG, SCORECARD, canonical artifact, or other report was edited by me.

No audible, engine, perceptual, production, or external compatibility claim is made.
