# Round 30 guard — baseline preservation

## Scope and state

This guard follows the Round 30 declaration in `.shokunin/audio/LOG.md`. It records the 13 canonical WAV hashes, five original `_alt` comparisons, historical prior-26 runner outcomes, and eight invalid-control statuses. Prior-26 and invalid-mode details are carried forward from `.shokunin/audio/reports/round-29/r29-verifier.md`; I did not rerun those modes or invalid controls. The current normal run below independently checks the five original comparisons. This guard does not adjudicate the new orientation candidate or runner behavior.

Declared clean-before revision: `6a3696822741388d862243745f653a76eec21d1f`.

Exact shell commands and exits observed in this guard:

- `git rev-parse HEAD` — exit 0; returned `6a3696822741388d862243745f653a76eec21d1f`.
- `git status --short --branch` — exit 0; showed branch `craft/audio-r1`, modified `.shokunin/audio/LOG.md`, and untracked `.shokunin/audio/corpus/fixtures/__pycache__/`, `.shokunin/audio/corpus/live/round-30/`, and `.shokunin/audio/reports/round-30/` at inspection. These round-30 paths were already present; this task writes only this guard report.
- `sha256sum .shokunin/audio/corpus/artifacts/*.wav` — exit 0 (hashes below).
- `git ls-files '.shokunin/audio/corpus/artifacts/*.wav' | sort` — exit 0 (13 tracked WAVs).
- `git diff --quiet HEAD -- .shokunin/audio/corpus/artifacts` — exit 0.
- `git diff --quiet HEAD -- .shokunin/audio/corpus/fixtures` — exit 0.
- `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` — exit 0, empty failures; receipt `.shokunin/audio/corpus/live/runs/20261013T023305034298Z-normal/measurements.json`.

No commit or push.

## Canonical artifact hashes

All 13 tracked hashes match the prior guard baseline; canonical artifact tree is unchanged from HEAD.

| Canonical WAV | SHA-256 |
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

## Five original variant comparisons

The observed normal command above reported no failures. Its original `_alt` results:

| Variant | Baseline | Duration delta (s) | Relative centroid delta | Result |
|---|---|---:|---:|---|
| `ui_alt` | `ui` | `0.04000000000000001` | `0.47187731004956435` | pass |
| `impact_alt` | `impact` | `0.0` | `0.9563048992406177` | pass |
| `movement_alt` | `movement` | `0.12` | `0.007518618572621081` | pass |
| `ambience_alt` | `ambience` | `0.0` | `0.5845136323520758` | pass |
| `stem_layer_alt` | `stem_layer` | `0.0` | `0.46179931396667484` | pass |

The existing rule remains duration delta `>= 0.020 s` OR relative centroid delta `>= 0.10`. No threshold was changed by this guard. Centroid is the project's whole-waveform FFT numeric proxy, not a perceptual measure.

## Historical prior-26 runner outcomes

These are historical outcomes from the R29 independent verifier, not executions by this guard. The declared R30 prior-26 subset is R29's initial normal and both lower-centroid probes plus R29's prior-24 modes, in their serial order; equivalently the complete 26-row R29 replay below. Expected fixture failures exit 1. R29 verifier reported no setup failures, tracebacks, or exit 2 in these 26 executions.

| # | Exact command | Exit |
|---:|---|---:|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | 1 |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | 0 |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | 1 |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | 0 |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 |
| 25 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 |
| 26 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` (normal restore) | 0 |

This is 7 exit-0 and 19 expected exit-1 results; prior-26 preservation is inherited from the cited R29 verifier, not independently replayed here.

## Eight invalid-control statuses

From historical R29 replay command #25 and receipt `.shokunin/audio/corpus/live/runs/20261013T022618102481Z-invalid/measurements.json`; not rerun by this guard:

| Probe | Expected status | Result |
|---|---|---|
| `short_sections` | `expected_failure` | section count |
| `corrupt` | `expected_failure` | decode |
| `wrong_format` | `expected_failure` | format |
| `odd_sections` | `expected_failure` | section count |
| `native16_probe` | `expected_pass` | none |
| `native24_probe` | `expected_failure` | format |
| `stereo48_probe` | `expected_failure` | format |
| `mono441_probe` | `expected_failure` | format |

The R29 verifier reports all eight matched expected status. These are prior historical control results, not this guard's fresh test.

## Fit/setup evidence exclusions and limits

No Round 30 fit, orientation probe, candidate runner mode, or setup command was run for this guard. R30 leaf fit/setup reports are not gate evidence for this preservation report. In particular, R30 executor describes an initial direct-measure command that exited 1 because relative scratch paths were outside the project corpus root; that was a setup/path failure, excluded from measurement evidence. Its corrected absolute-path command exited 0. The R30 executor and alt fit results are candidate evidence in their own reports; I do not reclassify or adjudicate them here. Failed fits/setup are not evidence for a successful orientation outcome.

This guard makes no claim about perceptual similarity, whether symmetry is normative, rights, engine/runtime, publishing, or promotion. It does not claim new orientation behavior. No source, LOG, SCORECARD, canonical artifact, or other report was edited; no commit or push. Only `.shokunin/audio/reports/round-30/r30-guard.md` was written.
