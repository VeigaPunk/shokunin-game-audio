# Round 29 guard — baseline preservation

## Scope and state

This report follows the Round 29 declaration in `.shokunin/audio/LOG.md`. I record the 13 canonical WAV hashes, five original `_alt` comparisons, historical prior-24 runner outcomes, and eight invalid-control statuses. The prior-24/invalid details are carried forward from the Round 28 non-author verifier; I did not rerun those 24 modes or invalid controls in this guard. This guard does not adjudicate Round 29 candidate fits or runner behavior.

Declared clean baseline: `99b6c0afb121fd7f1a85623a3a5854493c38ccf8`. Exact command `git rev-parse HEAD` exited 0 and returned that revision. `git status --short --branch` exited 0; at inspection it showed branch `craft/audio-r1`, modified `.shokunin/audio/LOG.md`, untracked `.shokunin/audio/corpus/fixtures/__pycache__/`, `.shokunin/audio/corpus/live/round-29/`, and `.shokunin/audio/reports/round-29/`. These changes pre-existed this report; I created only this report. No commit or push.

## Canonical artifact hashes

Exact command `sha256sum .shokunin/audio/corpus/artifacts/*.wav` exited 0. Exact command `git ls-files '.shokunin/audio/corpus/artifacts/*.wav' | sort` exited 0 and listed 13 tracked files. All hashes match the prior R28 guard baseline:

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

Exact command `git diff --quiet HEAD -- .shokunin/audio/corpus/artifacts` exited 0. Exact command `git diff --quiet HEAD -- .shokunin/audio/corpus/fixtures` exited 0. No tracked canonical WAV or fixture-source difference from HEAD was present when checked.

## Five original variant comparisons

Exact project command `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` exited 0 with empty failures. Receipt: `.shokunin/audio/corpus/live/runs/20261013T022216152431Z-normal/measurements.json`. Existing original comparison results:

| Variant | Baseline | Duration delta (s) | Relative centroid delta | Result |
|---|---|---:|---:|---|
| `ui_alt` | `ui` | `0.04000000000000001` | `0.47187731004956435` | pass |
| `impact_alt` | `impact` | `0.0` | `0.9563048992406177` | pass |
| `movement_alt` | `movement` | `0.12` | `0.007518618572621081` | pass |
| `ambience_alt` | `ambience` | `0.0` | `0.5845136323520758` | pass |
| `stem_layer_alt` | `stem_layer` | `0.0` | `0.46179931396667484` | pass |

The existing distinctness OR limits remain duration delta `>= 0.020 s` or relative centroid delta `>= 0.10`. This report changed no limits. Centroid is the project's numeric whole-waveform FFT proxy, not a perceptual measure.

## Historical prior-24 runner outcomes

The Round 28 independent verifier at `.shokunin/audio/reports/round-28/r28-verifier.md` reports the 24 serial commands below. These are historical baseline evidence, not runs by this guard. Its Round 28 new centroid probes were modes #2–#3; Round 29's requested prior-24 subset is initial normal #1 plus prior modes #4–#24, i.e. the following 22 rows. The other two rows are the Round 28 additions. Expected fixture failures exit 1; the verifier reported no setup failures, tracebacks, or exit 2 across all 24.

| # | Exact command | Exit | Prior-24 subset? |
|---:|---|---:|:---:|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | yes |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | 1 | no |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | 0 | no |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 | yes |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 | yes |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 | yes |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | yes |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | yes |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | yes |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | yes |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | yes |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | yes |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | yes |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | yes |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | yes |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | yes |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | yes |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | yes |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | yes |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | yes |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | yes |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | yes |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | yes |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` (normal restore) | 0 | yes |

The Round 28 verifier says initial and restored normal receipts matched after removing path fields. Prior-24 means the 22 rows marked yes above (not all 24 table rows).

## Eight invalid-control statuses

From that same historical `--probe-invalid` command/receipt, `.shokunin/audio/corpus/live/runs/20261013T021610820962Z-invalid/measurements.json`:

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

All eight matched their expected statuses in the cited verifier. They were not rerun by this guard.

## Candidate fits and setup, kept distinct

I did not run Round 29 fit generators or candidate runner modes. Existing leaf reports show exploratory scratch evidence, not integrated runner outcomes. In particular, `r29-alt.md` reports `python3 .shokunin/audio/corpus/live/round-29/alt/fit.py` first exited **1** due to passing a relative scratch path to the project measurement helper (`Path.relative_to(ROOT)`); after correcting that scratch script to pass resolved paths, the same exact command exited **0**. This first failure is setup/path error, not a failed waveform fit. Its measured chosen candidates are k=.95 (relative absolute centroid delta .0990190) and k=.94 (.1084606), both ordinary UI checks passing. Its separate sweep points include k=.99/.98 that do not reach the below-cutoff side; centroid responses are nonmonotonic.

`r29-scribe.md` reports a separate successful scratch fit command, `python3 .shokunin/audio/corpus/live/round-29/alt/fit.py`, exit **0**, with measured baseline and k=.95/.90; its k=.90 value (.1046633) predicts the above-cutoff case. `r29-reviewer.md`'s k=.85/.80 values and unsuccessful-candidate notes are numerical-only estimates, not a project runner execution. These reports differ on proposed above-cutoff candidate; do not conflate them or treat their candidate predictions as integrated comparator evidence. No integrated Round 29 modes or independent replay are recorded in the evidence available to this guard. Failed fits that miss the requested side, and setup/path errors, are separate categories from expected negative runner exits.

## Scope limits

This guard records baseline hashes and numeric runner outcomes only. It makes no claim of exact cutoff equality, smoothness, or perceptual/audible difference; nor any rights, engine/runtime, publishing, production, or promotion claim. I wrote only `.shokunin/audio/reports/round-29/r29-guard.md`. No source, LOG, SCORECARD, canonical artifact, or other report was edited; no commit or push.
