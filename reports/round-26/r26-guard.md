# Round 26 guard — baseline hashes, distinctness, and prior modes

## Scope and state

I read the Round 26 declared claim and scope in `.shokunin/audio/LOG.md`. This is a baseline guard only: I did not synthesize or evaluate a duplicate variant, replay runner modes, or edit source, fixtures, canonical WAVs, `LOG.md`, `SCORECARD.md`, or other reports. I wrote only this report. The declared before commit is `7c3241dd98709aa250f100612cbecd6e21568d9c`. At inspection `git status --short --branch` showed branch `craft/audio-r1` and pre-existing ` M .shokunin/audio/LOG.md`; no other status entries were shown. `git diff --quiet HEAD -- .shokunin/audio/corpus/artifacts .shokunin/audio/corpus/fixtures` exited 0.

## Thirteen canonical WAVs

`sha256sum .shokunin/audio/corpus/artifacts/*.wav` exited 0. Hashes match the declared before-state's tracked artifact blobs:

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

`git ls-files .shokunin/audio/corpus/artifacts/*.wav | sort` exited 0 and listed these 13 tracked paths. The declared normal runner receipt in `.shokunin/audio/corpus/live/runs/20261013T014011312756Z-normal/measurements.json` records 13 measurements and five passing `_alt` distinctness records. The thresholds are duration delta `>= 0.020 s OR` relative centroid delta `>= 0.10`; all five were already passing before this round:

| Variant | Baseline | Duration delta (s) | Relative centroid delta | Result |
|---|---|---:|---:|---|
| `ui_alt` | `ui` | 0.04000000000000001 | 0.47187731004956435 | pass |
| `impact_alt` | `impact` | 0.0 | 0.9563048992406177 | pass |
| `movement_alt` | `movement` | 0.12 | 0.007518618572621081 | pass |
| `ambience_alt` | `ambience` | 0.0 | 0.5845136323520758 | pass |
| `stem_layer_alt` | `stem_layer` | 0.0 | 0.46179931396667484 | pass |

This is the runner's recorded numerical distinctness criterion only, not an auditory judgment.

## Historical 19-mode baseline

The most recent cited non-author replay is the Round 25 verifier, `.shokunin/audio/reports/round-25/r25-verifier.md`. Its successful serial replay used the following exact commands and exits (the historical run, not a replay by this guard). Negative-mode exit 1 was expected; normal modes exited 0. The final normal receipt was restored successfully.

| # | Exact command | Exit |
|---:|---|---:|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 |

The Round 25 report notes 19 earlier wrapper attempts exited 127 before corrected invocations; those setup failures are excluded from the replay. This guard did not rerun any mode.

## Eight invalid-control baseline

Round 25's non-author invalid receipt is `.shokunin/audio/corpus/live/runs/20261013T014025494866Z-invalid/measurements.json`; historical invocation was `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` (exit 1, expected for negative controls). It records eight controls:

| Probe | Baseline status / observed failure |
|---|---|
| `short_sections` | expected failure: `section count` |
| `corrupt` | expected failure: `decode` |
| `wrong_format` | expected failure: `format` (44.1 kHz and stereo combined) |
| `odd_sections` | expected failure: `section count` |
| `native16_probe` | expected pass |
| `native24_probe` | expected failure: `format` |
| `stereo48_probe` | expected failure: `format` (48 kHz stereo PCM16) |
| `mono441_probe` | expected failure: `format` (44.1 kHz mono PCM16) |

Those records are a prior receipt baseline only; I did not rerun or independently assess them.

## Exact commands run for this guard

| Exact command | Exit | Result |
|---|---:|---|
| `git status --short --branch` | 0 | `## craft/audio-r1` and pre-existing ` M .shokunin/audio/LOG.md` |
| `git rev-parse HEAD` | 0 | `7c3241dd98709aa250f100612cbecd6e21568d9c` |
| `git diff --quiet HEAD -- .shokunin/audio/corpus/artifacts .shokunin/audio/corpus/fixtures` | 0 | No tracked artifact or fixture-source diff against HEAD |
| `sha256sum .shokunin/audio/corpus/artifacts/*.wav` | 0 | Thirteen hashes above |
| `git ls-files .shokunin/audio/corpus/artifacts/*.wav | sort` | 0 | Thirteen tracked artifact paths |

This guard does not establish the new duplicate control's fit or result; the independently replayed new mode and later adjudication remain separate. No sound/perceptual quality, engine/runtime, rights, publishing, or promotion claim is made. No source or canonical asset was changed; no commit or push was made.
