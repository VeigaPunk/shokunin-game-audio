# Round 28 guard — baseline preservation

## Scope

I read the Round 28 declaration in `.shokunin/audio/LOG.md`. This guard records the pre-existing baseline: thirteen canonical WAV hashes, five existing `_alt` comparisons, the prior 22 runner outcomes, and eight invalid-control statuses. It does not assess the Round 28 candidate fits or make a calibration verdict. I did not edit source, LOG, SCORECARD, canonical files, or any other report; no commit or push.

Declared before-state: `13a19e2ea39f7bb3d04ee42b5a2e458b4bde461b`. Current `git rev-parse HEAD` also returned that revision. `git status --short --branch` exited 0 and showed `## craft/audio-r1`, modified `.shokunin/audio/LOG.md`, and untracked `.shokunin/audio/corpus/live/round-28/` and `corpus/fixtures/__pycache__/`. These pre-existing changes are not mine. The guard's report is the only path I create.

## Thirteen canonical WAVs

Exact command `sha256sum .shokunin/audio/corpus/artifacts/*.wav` exited 0. `git ls-files .shokunin/audio/corpus/artifacts/*.wav | sort` exited 0 and listed thirteen tracked files. Hashes match the prior Round 27 guard baseline:

| WAV | SHA-256 |
|---|---|
| `ambience.wav` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` |
| `ambience_alt.wav` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` |
| `impact.wav` | `a462019d1189cbafb8d1240d972d99959401ca249a0c0749b1a7f913d8bc8bc` |
| `impact_alt.wav` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` |
| `movement.wav` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` |
| `movement_alt.wav` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` |
| `stem.wav` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` |
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` |
| `stem_layer.wav` | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` |
| `stem_layer_alt.wav` | `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` |
| `stem_layer_third.wav` | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` |
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` |

Exact command `git diff --quiet HEAD -- .shokunin/audio/corpus/artifacts .shokunin/audio/corpus/fixtures` exited 0 (`fixture_diff_exit=0`): no tracked canonical-artifact or fixture-source diff against HEAD. This is not a historical replay.

## Five original variant comparisons

I ran the project runner with exact command `python3 .shokunin/audio/corpus/fixtures/measure_audio.py`; it exited 0 and wrote `.shokunin/audio/corpus/live/runs/20261013T021100212192Z-normal/measurements.json` with empty failures. This confirms the five existing `_alt` rows on current baseline, not their perceptual qualities:

| Variant | Baseline | Duration delta (s) | Relative centroid delta | Runner result |
|---|---|---:|---:|---|
| `ui_alt` | `ui` | `0.04000000000000001` | `0.47187731004956435` | pass |
| `impact_alt` | `impact` | `0.0` | `0.9563048992406177` | pass |
| `movement_alt` | `movement` | `0.12` | `0.007518618572621081` | pass |
| `ambience_alt` | `ambience` | `0.0` | `0.5845136323520758` | pass |
| `stem_layer_alt` | `stem_layer` | `0.0` | `0.46179931396667484` | pass |

The numeric distinctness predicate remains duration delta `>= 0.020 s OR` relative spectral-centroid delta `>= 0.10`; this guard changed no constants. These are numeric centroid-proxy outcomes only.

## Prior 22 runner outcomes (historical baseline)

The Round 27 non-author replay at `reports/round-27/r27-verifier.md` records these exact commands and exits (the first normal, two round-27 modes, and prior 20-mode sequence). These are cited historical outcomes; this guard did not rerun all 22. Negative-control exit 1s were expected fixture failures, not command/setup failures.

| # | Exact command | Exit |
|---:|---|---:|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 |

Round 27 verifier reports no setup failure, traceback, or exit 2 in those 22 invocations; initial and restored normal receipts matched after excluding path fields. The prior 20 outcomes are invocations #1 and #4–#22 above. New round-28 run behavior is not part of this baseline.

## Eight invalid-control statuses (historical)

The Round 27 verifier's `--probe-invalid` receipt is `.shokunin/audio/corpus/live/runs/20261013T020355945654Z-invalid/measurements.json`; exact command `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` exited 1. This was expected invalid fixture behavior; not rerun separately by this guard.

| Probe | Prior expected status | Recorded result |
|---|---|---|
| `short_sections` | `expected_failure` | section count |
| `corrupt` | `expected_failure` | decode |
| `wrong_format` | `expected_failure` | format |
| `odd_sections` | `expected_failure` | section count |
| `native16_probe` | `expected_pass` | none |
| `native24_probe` | `expected_failure` | format |
| `stereo48_probe` | `expected_failure` | format |
| `mono441_probe` | `expected_failure` | format |

## Failed fits and setup outcomes

No round-28 candidate fit or setup command was run by this baseline guard, so it records no round-28 fit success/failure and does not infer the intended centroid polarity. The single normal runner invocation above succeeded (exit 0, empty failures). Historical round-27 verifier reports no setup failures in its 22-mode replay. The round-27 report separately discloses a corrected relative-path setup error (exit 1) during an unrelated alternate direct-fit helper; it was excluded from evidence and is not an outcome in the 22-mode replay. Keep failed candidate fits and setup errors distinct from expected negative predicate exits.

## Scope limits

This report records hashes and numeric fixture-runner outcomes only. The centroid value is a numeric proxy, not evidence of audibility or perception. No rights, engine/runtime, publishing, clearance, promotion, or perceptual claim is made. No source, LOG, SCORECARD, canonical artifact, or other report was edited; no commit or push.
