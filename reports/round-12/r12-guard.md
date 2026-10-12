# Round 12 guard inventory — Luna LEAF

Scope: pre-integration baseline inventory for the declared coverage move. I did not replay any measurement mode, modify source/LOG/SCORECARD/canonical artifacts, or make a commit. All eleven hashes below are SHA-256 of the existing canonical WAVs under `.shokunin/audio/corpus/artifacts/`; they are author-computed inventory, not a claim of independent round-12 verification.

## Existing canonical WAV inventory

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
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` |
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` |

## Round 11 nine-mode baseline receipts (historical LOG declaration)

These are historical parent/verifier receipts recorded in `.shokunin/audio/LOG.md`; I did not replay or inspect their raw files in this task. Paths are relative to `.shokunin/audio/`.

| Mode | Exit | Receipt |
|---|---:|---|
| Normal | 0 | `corpus/live/runs/20261012T175735059859Z-normal/measurements.json` |
| New layer side-slope negative control | 1 | `corpus/live/runs/20261012T175746702789Z-layer-slope/measurements.json` |
| Old layer-join control | 1 | `corpus/live/runs/20261012T175747429236Z-layer-join/measurements.json` |
| Flat-30 control | 1 | `corpus/live/runs/20261012T175748161231Z-flat/measurements.json` |
| Flat-120 control | 1 | `corpus/live/runs/20261012T175748914277Z-layer-flat/measurements.json` |
| Outer-slope control | 1 | `corpus/live/runs/20261012T175749627491Z-slope/measurements.json` |
| Failing control | 1 | `corpus/live/runs/20261012T175750282070Z-failing/measurements.json` |
| Invalid-input control | 1 | `corpus/live/runs/20261012T175750512664Z-invalid/measurements.json` |
| Normal restore | 0 | `corpus/live/runs/20261012T175755823615Z-normal/measurements.json` |

The LOG says the round-11 slope probe was the sole new slope-probe failure, the old join control remained a sole adjacent-gap failure, and all eleven canonical SHA-256 values matched baseline commit `f15fe55`. Those statements are historical evidence, not results of my replay. The LOG separately records an extra exploratory receipt `175738612676Z-layer-slope` that is not counted among the nine modes, plus verifier orchestration `TypeError` and receipt-inspection `KeyError`; neither is a pass.

## Guard implications for round 12

- Preserve all eleven canonical bytes and the existing `stem_layer` (120 Hz) behavior; the declared proposed addition is a distinct 180 Hz `stem_layer_alt`, not replacement of the existing layer.
- Before accepting twelve canonical files/five measured layer/SFX variants, compare old eleven hashes byte-for-byte and document the new artifact's hash. Recheck all nine old modes against the historical exits/receipts, then verify new normal receipt contains the additional measurement. Historical receipt schemas should remain unchanged.
- This inventory establishes neither that the proposed fixture passes nor distinctness, audible quality, engine/adaptive behavior, security, or production readiness. Synthetic PCM only.

## Commands / exits

No shell commands or measurement commands were run; therefore there are no command exits to report. The inventory above was read from the declared LOG/source and computed over canonical file bytes only.
