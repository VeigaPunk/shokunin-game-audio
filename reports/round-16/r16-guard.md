# Round 16 guard inventory — no fresh replay

## Scope and provenance

I read the Round 16 LOG declaration and the prior Round 15 independent verifier report. This is a historical inventory only: **I did not invoke `measure_audio.py` or run any fixture mode.** The 12 hashes below are transcribed from `audio/reports/round-15/r15-verifier.md`, whose binary-safe comparison was against Git base `0928e9e`; Round 16 names `35d978c` as its clean before-state. LOG records no canonical artifact change in Round 15, so those hashes are the recorded pre-Round-16 inventory. This report does not independently revalidate them against `35d978c` or current bytes.

## Twelve canonical artifact hashes (recorded prior inventory)

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

## Prior 12-mode outcome/failure-set inventory (Round 15)

Transcribed from `r15-verifier.md`; these are **prior** outcomes, not Round 16 replay evidence. Mode order and process exits were:

| Mode | Exit | Recorded expected failure set |
|---|---:|---|
| normal | 0 | none; five `_alt` distinctness checks passed |
| `--probe-layer-alt-slope` | 1 | `slope180_probe`: internal join side-slope mismatch only |
| `--probe-layer-alt-join` | 1 | `join180_probe`: internal join gap only |
| `--probe-layer-alt-flat` | 1 | `flat180_probe`: section contrast only |
| `--probe-layer-slope` | 1 | `layer_slope_probe`: slope only |
| `--probe-layer-join` | 1 | `join_probe`: gap only |
| `--probe-flat` | 1 | `flat_probe`: section contrast only |
| `--probe-layer-flat` | 1 | `layer_flat_probe`: section contrast only |
| `--probe-slope` | 1 | outer slope probe: slope only |
| `--probe-failing` | 1 | failing ambience: centroid and endpoint failures |
| `--probe-invalid` | 1 | invalid fixture: short/odd section count, decode, and format errors |
| normal restore | 0 | none; complete JSON equaled initial normal |

Round 15 verifier described existing join controls as gap-only, flat controls as contrast-only, slope controls as slope-only, and failing/invalid controls as above. The exact receipts and commands remain in that report. This inventory does not assert fresh preservation in Round 16.

## Commands run for this guard task

No fixture/replay commands were run. I ran only repository status and canonical artifact diff against the declared Round 16 base:

```text
git status --short
```
Exit **0**; output showed `M .shokunin/audio/LOG.md`, `?? .shokunin/audio/corpus/live/round-16/`, and `?? .shokunin/audio/reports/round-16/` at inspection time.

```text
git diff --quiet 35d978c -- .shokunin/audio/corpus/artifacts
```
Exit **0** (`artifact_diff_exit=0`), meaning no tracked canonical artifact diff versus `35d978c`. This is a Git diff check, not a current hash recalculation or replay. No failed setup occurred. No source, LOG, SCORECARD, canonical artifact, or other report was edited by me.

No audio, engine, perceptual, or production claim is made.
