# Round 14 guard inventory — canonical hashes and Round 13 mode expectations

## Scope and method

I read the Round 14 declaration in `.shokunin/audio/LOG.md`, the Round 13 independent verifier and adjudicator reports, and the current fixture runner. I computed SHA-256 over the twelve current canonical WAV files. I did not replay any fixture command, listen to audio, or modify source, fixtures, or canonical assets. This report is my only write.

## Current canonical inventory

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

There are twelve canonical WAVs. The Round 13 non-author verifier recorded that all twelve matched the Git blobs at pre-change `db36a69`; this report is a current-byte inventory, not a new before/after check.

## Round 13 mode expectations (historical; not replayed here)

The Round 13 verifier independently ran the following serial matrix. Exit 1 is the expected rejection for negative probes. Receipt paths are quoted as recorded by that verifier.

| Mode | Exact command | Exit | Expected behavior recorded |
|---|---|---:|---|
| Normal | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | Empty failure map; all 12 canonical measurements and five passing `_alt` comparisons. |
| New flat-180 negative | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `flat180_probe` fails only existing 180 Hz section contrast; valid equal component amplitudes, 0 dB contrast; generic/outer/internal checks pass. |
| Layer side-slope | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | Named side-slope probe fails side-slope only. |
| Layer join | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | Named join probe fails adjacent-gap only. |
| Flat-30 control | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | Flat-30 component control fails contrast only. |
| Flat-120 control | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | Flat-120 component control fails contrast only. |
| Outer slope | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | Slope probe fails outer-loop slope only. |
| Broken amplitude | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | Expected ambience centroid and endpoint-seam failures. |
| Invalid inputs | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | Short=`section count`, corrupt=`decode`, wrong-format=`format`, odd-sections=`section count`. |
| Normal restore | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | Empty failure map; restored normal receipt. |

Recorded receipt directories, in the same order, were `20261012T182214210060Z-normal`, `20261012T182214989477Z-layer-alt-flat`, `20261012T182215794825Z-layer-slope`, `20261012T182216581164Z-layer-join`, `20261012T182217372876Z-flat`, `20261012T182218152931Z-layer-flat`, `20261012T182218921091Z-slope`, `20261012T182219639313Z-failing`, `20261012T182219870138Z-invalid`, and `20261012T182220588396Z-normal`, each under `.shokunin/audio/corpus/live/runs/` with `measurements.json`.

The verifier reported ten initial whole-command-quoted attempts exited 127 and produced no receipts; these are not test evidence. Its corrected commands above are the only credited replay. The Round 13 adjudicator admitted a narrow depth improvement; the baseline included no matched flat-180 negative before that round.

## Limits

This is a byte inventory plus transcription of historical deterministic fixture expectations; no tests were run for this report. The measurements do not establish audibility, an engine behavior, security, threshold calibration, or production quality. Numeric thresholds remain fixture-local.
