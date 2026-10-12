# Round 11 independent serial replay — verifier

## Scope and method

Independent serial replay of the integrated round-11 measurement script from the working tree, without editing source, fixtures, canonical WAVs, LOG, or SCORECARD. Exact command and process exit for each replay are listed below. Expected negative-control process exit is 1; it is not described as a generic success. Receipt paths are the exact stdout paths. Normal restore was run at end. The canonical artifacts were compared to commit `f15fe55a2f04a457f035f3ae57c6f31275f4b74a`.

## Orchestration issue

The first Python orchestration loop mistakenly did `r=await bash(cmd); x=await r`; `bash()` had already returned a `BashResult`, so it raised `TypeError: object BashResult can't be used in 'await' expression` after the first normal run. This was an orchestration error, not a project command result. No later commands in that failed loop ran. I corrected it to `x=await bash(cmd)` and serially ran every remaining mode. All receipts/exits below are from the corrected, completed serial replay (plus the first and final normal runs). A separate exploratory Python receipt-inspection loop hit `KeyError: 'measurements'` on the invalid-mode receipt because that receipt uses `invalid_probes`; this was report-inspection only and did not interrupt/alter the replay or imply a test result.

## Exact commands, exits, and receipts

| mode | exact command | exit | receipt |
|---|---|---:|---|
| normal before controls | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261012T175735059859Z-normal/measurements.json` |
| internal side-slope | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `corpus/live/runs/20261012T175746702789Z-layer-slope/measurements.json` |
| internal join-gap prior control | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `corpus/live/runs/20261012T175747429236Z-layer-join/measurements.json` |
| flat 30 Hz | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `corpus/live/runs/20261012T175748161231Z-flat/measurements.json` |
| flat 120 Hz | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `corpus/live/runs/20261012T175748914277Z-layer-flat/measurements.json` |
| outer slope | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `corpus/live/runs/20261012T175749627491Z-slope/measurements.json` |
| failing control | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `corpus/live/runs/20261012T175750282070Z-failing/measurements.json` |
| invalid-input battery | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `corpus/live/runs/20261012T175750512664Z-invalid/measurements.json` |
| normal restore | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261012T175755823615Z-normal/measurements.json` |

The side-slope exit 1 was solely `layer_slope_probe: sections: internal join side slope mismatch > .001 full scale per sample`. The generated probe WAV at `corpus/live/round-11/slope_probe.wav` hashes to `cf5ca8467a7943060f038e9e98bd4b8b8551725b7432bc728d22c27b8ea12e9d`, matching the selected `r11-slope` candidate (and not the unused alternate `79b79e5150b0a8e517dc9cda8d3019f929723696dd993c0a7cb245cdfc05c2e5`). Its section receipt has 120 Hz contrast `13.979372301776372 dB`, `valid: true`, internal adjacent gap `.00018310546875` FS (below `.03`), and side-slope mismatch `.00115966796875` FS/sample (above `.001`). Generic checks and outer loop checks for the probe had no failures. Clean `stem_layer` side-slope mismatch is `.000762939453125`, and its section passes. The old join-gap control failed solely its original adjacent-gap rule: gap `.030914306640625` FS; its slope mismatch `.029693603515625` FS/sample is telemetry only because the new gate excludes `join_probe`. Source uses absolute mismatch and strict `> .001` (`measure_audio.py` lines 207–210), so equality passes. All four alternate variants are `passed: true` in each normal receipt (`distinctness` records). Flat30, flat120, outer-slope, failing, and invalid modes each recorded their corresponding expected failure; invalid battery categorized all four probes as expected failures (short section count, corrupt decode, wrong format, odd section count). Both normal modes had empty failures.

The selected scratch candidate and generated probe both exist and SHA-256 to `cf5ca8467a7943060f038e9e98bd4b8b8551725b7432bc728d22c27b8ea12e9d`.

## Canonical asset comparison

All eleven WAV hashes in `.shokunin/audio/corpus/artifacts/` match their respective blobs at `f15fe55a2f04a457f035f3ae57c6f31275f4b74a`. Hashes: ambience `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198`; ambience_alt `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc`; impact `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc`; impact_alt `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6`; movement `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d`; movement_alt `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639`; stem `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0`; stem_layer `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9`; stem_sections `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702`; ui `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9`; ui_alt `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f`.

## Limits

This verifies this fixture-local discrete PCM proxy and deterministic controls only. The `.001` threshold is reused from the outer-slope limit, not calibrated for audibility. No perceptual, playback, engine, or production-quality claim follows. No command remains unrun in the declared replay set.
