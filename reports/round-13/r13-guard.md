# Round 13 guard inventory — canonical hashes and Round 12 mode baseline

## Scope and method

Read the Round 13 declaration in `.shokunin/audio/LOG.md`, the Round 12 verifier and adjudicator reports, and the current fixture runner. I only inventoried the twelve current canonical artifact files by SHA-256 and transcribed the corrected Round 12 independent replay matrix. I did not run/replay any fixture command, modify source or fixtures, or inspect audio by listening. This report is the only file I wrote.

## Current canonical inventory

SHA-256 over the current bytes under `.shokunin/audio/corpus/artifacts/`:

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
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` |

There are twelve current canonical WAVs. The Round 12 verifier separately reported that the eleven pre-existing files matched their Git blobs at `f986933`; the new `stem_layer_alt.wav` hash matched the selected original synthetic scratch candidate. This inventory itself is not a new before/after comparison.

## Round 12 corrected independent mode matrix (historical; not replayed here)

All commands below were run serially from the repository root in the Round 12 non-author verification. Receipt paths are under `.shokunin/audio/corpus/` (the report abbreviates the leading `.shokunin/audio/` as `corpus/`). Exit 1 is the expected rejection for negative probes, not a replay failure.

| Mode | Exact command | Exit | Corrected receipt | Expected behavior recorded |
|---|---|---:|---|---|
| Normal | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261012T181138537075Z-normal/measurements.json` | Empty failure map; 12 canonical measurements, five passing `_alt` comparisons. |
| Layer side-slope | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `corpus/live/runs/20261012T181139329793Z-layer-slope/measurements.json` | Named slope probe fails its side-slope gate only. |
| Layer join | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `corpus/live/runs/20261012T181140115256Z-layer-join/measurements.json` | Named join probe fails its adjacent-gap gate only. |
| Flat-30 control | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `corpus/live/runs/20261012T181140900892Z-flat/measurements.json` | Flat 30 Hz component control fails contrast only. |
| Flat-120 control | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `corpus/live/runs/20261012T181141704446Z-layer-flat/measurements.json` | Flat 120 Hz component control fails contrast only. |
| Outer slope | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `corpus/live/runs/20261012T181142488683Z-slope/measurements.json` | Slope probe fails the outer loop slope gate. |
| Broken amplitude | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `corpus/live/runs/20261012T181143212511Z-failing/measurements.json` | Two expected ambience failures: centroid and endpoint seam. |
| Invalid inputs | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `corpus/live/runs/20261012T181143444635Z-invalid/measurements.json` | Four expected categories: short=`section count`, corrupt=`decode`, wrong-format=`format`, odd-sections=`section count`. |
| Normal restore | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261012T181144168274Z-normal/measurements.json` | Empty failure map; restored normal receipt. |

The Round 12 verifier explicitly excluded earlier setup attempts that exited 127 (whole-command quoting and one `.shokun` typo), and exploratory duplicate receipts. They are not evidence in the matrix above. Round 12 had no `--probe-layer-alt-flat` mode; the absence of a matched flat-180 control was the declared depth gap for Round 13.

## Limits

This is a byte inventory and a transcription of existing deterministic test receipts. No tests were run for this report. No audible, engine/adaptive behavior, security, threshold-calibration, or production-quality claim is made. The existing component contrast and seam thresholds remain fixture-local numeric checks.
