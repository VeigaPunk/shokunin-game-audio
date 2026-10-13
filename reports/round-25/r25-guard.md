# Round 25 guard — baseline hashes and historical runner inventory

## Scope and point-in-time state

I read the Round 25 declaration in `.shokunin/audio/LOG.md`. This is the guard's baseline inventory only; I did not build, fit, or replay controls, and did not edit source, fixtures, canonical WAVs, `LOG.md`, `SCORECARD.md`, or any other report. The declared before `HEAD` was `30530e17a4f20ba28d7f81cda41c8949f4652697`. At my inspection, `git status --short --branch` (exit 0) showed `## craft/audio-r1`, pre-existing ` M .shokunin/audio/LOG.md`, plus untracked round-25 scratch/report directories from the parallel round work. I wrote only this report. `git diff --quiet HEAD -- .shokunin/audio/corpus/artifacts .shokunin/audio/corpus/fixtures` exited 0, so tracked canonical artifacts and fixture source were unchanged from HEAD. No commit or push was made.

## Canonical WAV baseline

The 13 tracked canonical artifact files and their SHA-256 digests at the declared before-state are:

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

These digests are unchanged from the recorded round-22 before baseline. The canonical inventory is thirteen WAVs and the normal receipt records five `_alt` distinctness records. The local format rule recorded in the baseline is 48 kHz, mono, encoded `pcm_s16le`, 16 bits. No threshold comparison or sound assessment was performed in this task.

## Six existing invalid records (before Round 25)

The last historical non-author invalid receipt cited in `.shokunin/audio/reports/round-23/r23-verifier.md` is `.shokunin/audio/corpus/live/runs/20261013T011828577717Z-invalid/measurements.json`; the associated exact command was `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` (exit 1, expected for negative controls). The six records and expected outcomes as recorded in that report are:

| Probe | Existing expected result |
|---|---|
| `short_sections` | `section count` |
| `corrupt` | `decode` |
| `wrong_format` | `format`; 44.1 kHz **and** stereo, so rate and channel causes are confounded |
| `odd_sections` | `section count` |
| `native16_probe` | expected pass; no failure, 48 kHz mono `pcm_s16le`, 16 bits |
| `native24_probe` | expected failure `format`; 48 kHz mono `pcm_s24le`, 24 bits |

Thus the prior controls do not isolate rate from channels: `wrong_format` changes both. The paired native-width records hold rate/channels at 48 kHz mono and vary encoding width, not those format dimensions. These are historical report/receipt facts, not a new Round 25 execution.

## Historical 19-mode inventory

The round-22 independent verifier records 19 serial runner executions, with exit vector `[0,0,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0]`. Exact invocations and exits are listed below; intentional negative-mode exit 1 is expected. This is the Round 22 recorded replay, not a replay by me in Round 25.

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

The prior verifier reports expected failure categories for negative modes and normal/restore success; see `.shokunin/audio/reports/round-22/r22-verifier.md` for receipts and details. The historical replay reported no runner setup error or exit 2. Round 23 separately reports some malformed exploratory wrapper attempts (exit 127) excluded from its replay; no such commands were run by me. I did not attempt a Round 25 sample fit or setup, so there is no fit/setup result to report. No new format predicate, gate, or threshold is evidenced here.

## Boundaries

This guard report does not establish Round 25 control fit, isolation, or rejection results; independent replay is still required. It makes no sound-quality, engine/runtime, rights, publishing, or universal WAV-handling claim.

## Commands I ran and exits

| Exact command | Exit | Result |
|---|---:|---|
| `git status --short --branch` | 0 | Branch and pre-existing/parallel untracked state described above. |
| `git rev-parse HEAD` | 0 | `30530e17a4f20ba28d7f81cda41c8949f4652697`. |
| `git diff --quiet HEAD -- .shokunin/audio/corpus/artifacts .shokunin/audio/corpus/fixtures` | 0 | Tracked canonical artifacts and fixture source unchanged. |
| `sha256sum .shokunin/audio/corpus/artifacts/*.wav` | 0 | Thirteen hashes listed above. |
| `git ls-files .shokunin/audio/corpus/artifacts/*.wav \| sort` | 0 | Thirteen tracked canonical WAV paths. |
