# Round 26 independent verifier — NON-AUTHOR LEAF

## Verdict and scope

**Replay verified; narrow duplicate-negative fit confirmed.** I independently ran 20 executions serially: baseline normal, `--probe-ui-clone`, the prior 17 flags in the Round 25 verifier order, and restored normal. All 20 produced receipts; there were no setup errors, tracebacks, or exit 2. Normal and restored-normal contents are equal after removing path fields. The clone mode exited 1 for exactly one failure: `ui_clone_alt`'s existing distinctness rejection. `ui_clone` and the alternate have empty ordinary failure sets before distinctness; the alternate's only failure is `distinctness: duration < .020 s and centroid delta < 10%`. This supports an exact matched duplicate at zero/zero only. It tests neither the `.020 s` nor `.10` edge, and makes no perceptual-deduplication claim.

## Serial replay: commands, exits, receipts, full failure kinds

All commands ran from `/home/vgpnk/Projects/prymeagnt/audio` using `python3`; each receipt is runner-generated under `corpus/live/runs/`.

| # | Exact command | Exit | Receipt | Failure set (empty means no failures) |
|---:|---|---:|---|---|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T015340732605Z-normal/measurements.json` | `{}` |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 | `.shokunin/audio/corpus/live/runs/20261013T015341619139Z-ui-clone/measurements.json` | `{"ui_clone_alt":["distinctness: duration < .020 s and centroid delta < 10%"]}` |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T015342484271Z-layer-third-join-edge-pass/measurements.json` | `{}` |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T015343348729Z-layer-third-join-edge-fail/measurements.json` | `{"join200_edgefail_probe":["sections: internal join adjacent sample gap > .03 full scale"]}` |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T015344210338Z-layer-third-join/measurements.json` | `{"join200_probe":["sections: internal join adjacent sample gap > .03 full scale"]}` |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T015345071801Z-layer-third-slope-edge-pass/measurements.json` | `{}` |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T015345933916Z-layer-third-slope-edge-fail/measurements.json` | `{"edgefail_probe":["sections: internal join side slope mismatch > .001 full scale per sample"]}` |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T015346801407Z-layer-third-slope/measurements.json` | `{"slope200_probe":["sections: internal join side slope mismatch > .001 full scale per sample"]}` |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T015347664242Z-layer-alt-reverse/measurements.json` | `{"reverse180_probe":["sections: 180 Hz component amplitude contrast < 6 dB or invalid"]}` |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T015348531104Z-layer-alt-slope/measurements.json` | `{"slope180_probe":["sections: internal join side slope mismatch > .001 full scale per sample"]}` |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T015349395459Z-layer-alt-join/measurements.json` | `{"join180_probe":["sections: internal join adjacent sample gap > .03 full scale"]}` |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T015350256558Z-layer-alt-flat/measurements.json` | `{"flat180_probe":["sections: 180 Hz component amplitude contrast < 6 dB or invalid"]}` |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T015351116571Z-layer-slope/measurements.json` | `{"layer_slope_probe":["sections: internal join side slope mismatch > .001 full scale per sample"]}` |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T015351978653Z-layer-join/measurements.json` | `{"join_probe":["sections: internal join adjacent sample gap > .03 full scale"]}` |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T015352852752Z-flat/measurements.json` | `{"flat30_probe":["sections: 30 Hz component amplitude contrast < 6 dB or invalid"]}` |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T015353714969Z-layer-flat/measurements.json` | `{"flat120_probe":["sections: 120 Hz component amplitude contrast < 6 dB or invalid"]}` |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T015354568479Z-slope/measurements.json` | `{"slope_probe":["loop seam: slope mismatch > .001 full scale per sample"]}` |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261013T015355370669Z-failing/measurements.json` | `{"ambience":["spectrum: centroid outside fixture band","loop seam: endpoint jump > .03 full scale"]}` |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261013T015355707136Z-invalid/measurements.json` | `invalid rows listed below` |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T015356509087Z-normal/measurements.json` | `{}` |

### Invalid receipt details

The `--probe-invalid` receipt has eight rows (statuses and observed failure kinds):

| Probe | Status | Observed failure |
|---|---|---|
| `short_sections` | `expected_failure` | `section count` |
| `corrupt` | `expected_failure` | `decode` |
| `wrong_format` | `expected_failure` | `format` |
| `odd_sections` | `expected_failure` | `section count` |
| `native16_probe` | `expected_pass` | `None` |
| `native24_probe` | `expected_failure` | `format` |
| `stereo48_probe` | `expected_failure` | `format` |
| `mono441_probe` | `expected_failure` | `format` |

These match the prior eight expected statuses: the original six unchanged, plus the two Round 25 format controls (`stereo48_probe`, `mono441_probe`).

## Clone pair and rule evidence

Scratch files are `.shokunin/audio/corpus/live/round-26/ui_clone.wav` and `.shokunin/audio/corpus/live/round-26/ui_clone_alt.wav`. Both SHA-256 values are `57b3061d6a1b3ea7d94dcf4ea9c1bf6638d22e5284adaff37d3caf3d07b59ce1` (byte-identical). Probe receipt: `.shokunin/audio/corpus/live/runs/20261013T015341619139Z-ui-clone/measurements.json`.

- Both measurements: 0.12 s, 48,000 Hz, mono, `pcm_s16le`/16-bit; peak `0.2978515625`, RMS `-20.316530244711558 dBFS`, centroid `971.86422306315 Hz`; ordinary checks empty.
- `ui_clone_alt` baseline: `ui_clone`; duration delta `0.0 s`; relative centroid delta `0.0`; `passed: false`.
- Existing rule remains `duration_delta >= 0.020 s OR relative_centroid_delta >= 0.10`; at (0,0), both branches are false. No threshold changed. `ui_clone_alt` has only `distinctness: duration < .020 s and centroid delta < 10%`.

## Preservation checks

### Thirteen canonical SHA-256 values

I compared current SHA-256 values to the files at pre-round commit `7c3241dd98709aa250f100612cbecd6e21568d9c`. All match:

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

### Five pre-existing `_alt` comparisons

All five remain passing in normal, clone, historical modes, and restored normal; metrics equal the prior normal receipt:

| Variant → base | Duration delta (s) | Relative centroid delta | Result |
|---|---:|---:|---|
| `ui_alt` → `ui` | 0.04000000000000001 | 0.47187731004956435 | pass |
| `impact_alt` → `impact` | 0.0 | 0.9563048992406177 | pass |
| `movement_alt` → `movement` | 0.12 | 0.007518618572621081 | pass |
| `ambience_alt` → `ambience` | 0.0 | 0.5845136323520758 | pass |
| `stem_layer_alt` → `stem_layer` | 0.0 | 0.46179931396667484 | pass |

Threshold objects equal the prior normal receipt (including `.001` duration tolerance, 48 kHz, and `.020`/`.10` distinctness bounds). Initial and restored normal receipts compare equal after removing measurement `path` fields.

## Limits and setup

This replay had no setup errors to disclose. Wave-1 reports describe their own corrected setup attempts; those are not verifier replay errors. Scratch is noncanonical under `live/round-26/`. This is an exact duplicate numerical negative, not perceptual deduplication or a claim of auditory similarity. No `.020`/`.10` edge was tested. No engine, rights, publication, or promotion claim is made. SHONEN four boxes were already checked; this verification changes neither rank nor promotion status.
