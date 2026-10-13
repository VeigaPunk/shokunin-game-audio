# Round 27 guard — prior baseline preservation

## Scope

I read the Round 27 calibration claim in `.shokunin/audio/LOG.md`. Its proposed 6719/6720-frame duration comparison and `< .10` centroid condition are a new calibration test. This guard establishes the prior-state baseline only; it does **not** run or verify either new mode, judge whether either fit succeeds, or infer comparator behavior from rounded values. I made no source, fixture, canonical WAV, LOG, SCORECARD, or other report edits. I did not commit or push.

The declared pre-round revision is `666688827adc3bcf0e4c67b481fc827d900ae2e7`. At inspection, `git status --short --branch` showed `## craft/audio-r1`, a pre-existing ` M .shokunin/audio/LOG.md`, and the untracked round-27 report directory. No claim is made here about the origin of other session work.

## Canonical thirteen WAVs

`sha256sum .shokunin/audio/corpus/artifacts/*.wav` exited 0. The current hashes match the canonical values recorded by the prior Round 26 independent verifier, and all thirteen paths are tracked (`git ls-files .shokunin/audio/corpus/artifacts/*.wav | sort`, exit 0).

| WAV | SHA-256 |
|---|---|
| `ambience.wav` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` |
| `ambience_alt.wav` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` |
| `impact.wav` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` |
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

`git diff --quiet HEAD -- .shokunin/audio/corpus/artifacts .shokunin/audio/corpus/fixtures` exited 0 (`fixture_diff_exit=0`), so no tracked artifact or fixture-source diff against current HEAD was present. This comparison is to HEAD, not a historical replay.

## Five existing variant comparisons

The prior normal receipt and Round 26 verifier report record all five `_alt` comparisons passing under the unchanged rule `duration_delta >= 0.020 s OR relative_centroid_delta >= 0.10`. Their recorded values are:

| Variant | Baseline | Duration delta (s) | Relative centroid delta | Prior result |
|---|---|---:|---:|---|
| `ui_alt` | `ui` | 0.04000000000000001 | 0.47187731004956435 | pass |
| `impact_alt` | `impact` | 0.0 | 0.9563048992406177 | pass |
| `movement_alt` | `movement` | 0.12 | 0.007518618572621081 | pass |
| `ambience_alt` | `ambience` | 0.0 | 0.5845136323520758 | pass |
| `stem_layer_alt` | `stem_layer` | 0.0 | 0.46179931396667484 | pass |

These are prior runner measurements, not new executions by this guard or perceptual judgments.

## Twenty-mode baseline (historical, not rerun here)

The latest independent baseline is Round 26's non-author replay (`reports/round-26/r26-verifier.md`). It ran 20 commands serially, including the exact-duplicate `--probe-ui-clone` mode introduced in Round 26, then the prior 17 probe flags and restored normal. Thus the 20 comprise the normal run, clone run, 17 historical probe modes, and normal restoration. The exact commands and exits from that successful historical replay are:

| # | Exact command | Exit |
|---:|---|---:|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 |

These are citations to the prior verifier's replay, not commands run for this guard. Negative-control exit 1 was expected. That verifier reported no setup errors, tracebacks, or exit 2; initial and restored normal receipts matched after path fields were removed. The earlier Round 25 report disclosed 19 wrapper attempts with exit 127 before corrected runs; these setup failures were excluded from its successful replay and are not part of the 20-mode Round 26 result.

## Eight invalid-control baseline (historical)

The prior verifier's receipt `.shokunin/audio/corpus/live/runs/20261013T015355707136Z-invalid/measurements.json`, produced by `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` (historical exit 1), records:

| Probe | Prior status | Observed failure |
|---|---|---|
| `short_sections` | `expected_failure` | `section count` |
| `corrupt` | `expected_failure` | `decode` |
| `wrong_format` | `expected_failure` | `format` |
| `odd_sections` | `expected_failure` | `section count` |
| `native16_probe` | `expected_pass` | none |
| `native24_probe` | `expected_failure` | `format` |
| `stereo48_probe` | `expected_failure` | `format` |
| `mono441_probe` | `expected_failure` | `format` |

This is the pre-round eight-control record; I did not rerun it.

## Commands run by this guard

| Exact command | Exit | Result |
|---|---:|---|
| `git status --short --branch` | 0 | `## craft/audio-r1`; pre-existing modified LOG and untracked report directory noted above |
| `git rev-parse HEAD` | 0 | `666688827adc3bcf0e4c67b481fc827d900ae2e7` |
| `sha256sum .shokunin/audio/corpus/artifacts/*.wav` | 0 | Thirteen hashes listed above |
| `git ls-files .shokunin/audio/corpus/artifacts/*.wav | sort` | 0 | Thirteen tracked canonical paths |
| `git diff --quiet HEAD -- .shokunin/audio/corpus/artifacts .shokunin/audio/corpus/fixtures` | 0 | No tracked diff in those paths |

## Calibration and limits

For the proposed 6719-frame case, the mathematical duration delta described in LOG is `959/48000 = 0.0199791666667… s`; for 6720 frames it is `960/48000 = 0.020 s`. Decimal display and binary floating-point representation are not proof of the exact value or branch taken after the runner's duration probe/measurement. I did not inspect or run the new fits. Therefore I cannot establish whether float subtraction rounds below, to, or above `.020`, whether either comparison passes its own duration specification, or whether centroid remains `< .10`. Any failed fit must remain labeled failed; no inference that a measured edge behaved as intended is supported by this baseline report. No shell invocations/exits for the two new modes are claimed here.

This report makes no perceptual, rights, engine/runtime, publishing, or promotion claim. It does not adjudicate the calibration claim.
