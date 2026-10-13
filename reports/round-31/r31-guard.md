# Round 31 guard — baseline preservation

## Scope and evidence boundary

This guard records the declared Round 31 preservation checks. Historical prior-28 runner outcomes and eight invalid-control statuses below are carried forward from `.shokunin/audio/reports/round-30/r30-verifier.md` (correct path: `.shokunin/audio/reports/round-30/r30-verifier.md`), not rerun here. Five original `_alt` comparison results are likewise carried from the Round 30 guard's normal receipt. I did not run the fixture runner, candidate probe, fit, or setup command; this report does not verify the proposed joint-below behavior. No commit or push.

Exact commands run for this guard:

- `sha256sum .shokunin/audio/corpus/artifacts/*.wav` — exit 0; output hashes listed below.
- No `git ls-files` command was run; the 13-file count is historical from the cited Round 30 verifier/guard.

Correction: the hash command is the only shell command run by this guard. No fitting/setup failure occurred in this guard because no fit or setup was attempted. The Round 31 declaration's target measurements and the scout/reviewer descriptions are not fresh guard measurements. The longer 6,719-frame scratch variant is not claimed to conform to canonical UI `.120 s` duration.

## Canonical artifact hashes

The 13 canonical artifact SHA-256 hashes observed by `sha256sum`:

| WAV | SHA-256 |
|---|---|
| `ambience.wav` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` |
| `ambience_alt.wav` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` |
| `impact.wav` | `a462019d1189cbafb8d1240d972d99959401ca249a0c0749b1a7f913d8bc8bc` |
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

These match the Round 30 guard's recorded baseline hashes. I did not independently compare them to a Git revision or establish current tracked status in this guard.

## Five existing variant comparisons

Historical normal-run results from `.shokunin/audio/reports/round-30/r30-guard.md`; no runner execution in this guard. Existing distinctness rule is duration delta `>= 0.020 s` OR baseline-relative absolute centroid delta `>= 0.10`.

| Variant | Duration delta (s) | Relative centroid delta | Historical result |
|---|---:|---:|---|
| `ui_alt` | `0.04000000000000001` | `0.47187731004956435` | pass |
| `impact_alt` | `0.0` | `0.9563048992406177` | pass |
| `movement_alt` | `0.12` | `0.007518618572621081` | pass |
| `ambience_alt` | `0.0` | `0.5845136323520758` | pass |
| `stem_layer_alt` | `0.0` | `0.46179931396667484` | pass |

No canonical fixture or threshold change is made or claimed by this report.

## Historical prior-28 runner outcomes

From the non-author Round 30 replay in `r30-verifier.md`. The 28 serial invocations yielded 8 exit 0 and 20 expected gate-rejection exit 1, with no exit 2. Commands and exits:

| # | Exact command | Exit |
|---:|---|---:|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-forward` | 1 |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-reverse` | 0 |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | 1 |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | 0 |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | 1 |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | 0 |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 |
| 25 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 |
| 26 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 |
| 27 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 |
| 28 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` (normal restore) | 0 |

Historical outcomes, not Round 31 runs. The two orientation runner outcomes at #2–3 are reported only as prior statuses here; this guard draws no new claim about them.

## Eight invalid-control statuses

From historical command #27 and receipt `.shokunin/audio/corpus/live/runs/20261013T023839657513Z-invalid/measurements.json`; not rerun here:

| Control | Expected status | Recorded outcome |
|---|---|---|
| `short_sections` | `expected_failure` | section count |
| `corrupt` | `expected_failure` | decode |
| `wrong_format` | `expected_failure` | format |
| `odd_sections` | `expected_failure` | section count |
| `native16_probe` | `expected_pass` | none |
| `native24_probe` | `expected_failure` | format |
| `stereo48_probe` | `expected_failure` | format |
| `mono441_probe` | `expected_failure` | format |

The cited non-author replay reports all eight statuses matched expectations. This is historical evidence, not fresh Round 31 validation.

## Failed fits, setup, and limits

No fit or runner/setup command was run by this guard; therefore there are no guard fit failures or setup errors to classify. I have not received an executor/alt measurement report in the reports directory at time of writing, so I do not infer success or failure from their scratch files. Any failed candidate fit or command-wrapper/setup failure must remain separate from runner outcomes and cannot count as gate evidence. No exact cutoff equality, perceptual/audio-quality, rights, engine/runtime, publishing, or promotion claim is made. No claim is made that the longer scratch variant satisfies canonical UI `.120 s` duration.
