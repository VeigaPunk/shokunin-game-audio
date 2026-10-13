# Round 32 guard — preservation record

## Scope and evidence boundary

The declared Round 32 task in `.shokunin/audio/LOG.md` asks for one mixed-signals case: duration delta nonzero and below `.020 s`, centroid-relative delta nonzero and at least `.10`, with the existing OR passing through the centroid arm. This guard did not run a candidate fit or runner mode. It records the existing baseline preservation evidence and carries forward the 29-run non-author replay from `.shokunin/audio/reports/round-31/r31-verifier.md`; that replay predates Round 32 and therefore is **not** evidence that the Round 32 candidate was integrated or passed. The variant's 6,719 frames at 48 kHz is about `.139979 s`, and does **not** conform to canonical UI `.120 s` duration; prior round-31 scratch spec separately declared `6719/48000`.

Exact shell command run by this guard:

- `sha256sum .shokunin/audio/corpus/artifacts/*.wav` — exit 0; hashes below.
- No runner, fit, `git`/setup command, or other shell command was run by this guard. No commit or push. No guard fit/setup failures occurred because neither was attempted; any earlier unsuccessful fits or command-wrapper/setup errors are not conflated with runner outcomes or counted as evidence.

## Canonical artifacts

The command above returned 13 canonical WAV hashes:

| WAV | SHA-256 |
|---|---|
| `ambience_alt.wav` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` |
| `ambience.wav` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` |
| `impact_alt.wav` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` |
| `impact.wav` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` |
| `movement_alt.wav` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` |
| `movement.wav` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` |
| `stem_layer_alt.wav` | `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` |
| `stem_layer_third.wav` | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` |
| `stem_layer.wav` | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` |
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` |
| `stem.wav` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` |
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` |

These match the historical baseline list in `.shokunin/audio/reports/round-31/r31-guard.md`. This guard did not check tracked status or compare to a Git revision.

## Five original variant comparisons

Historical original `_alt` normal-run measurements carried from `.shokunin/audio/reports/round-31/r31-guard.md`; no runner executed by this guard. The rule remains duration delta `>= .020 s` OR baseline-relative absolute centroid delta `>= .10`.

| Variant | Duration delta (s) | Relative centroid delta | Result |
|---|---:|---:|---|
| `ui_alt` | `0.04000000000000001` | `0.47187731004956435` | pass |
| `impact_alt` | `0.0` | `0.9563048992406177` | pass |
| `movement_alt` | `0.12` | `0.007518618572621081` | pass |
| `ambience_alt` | `0.0` | `0.5845136323520758` | pass |
| `stem_layer_alt` | `0.0` | `0.46179931396667484` | pass |

## Prior-29 outcomes (historical; not rerun)

Exact runner commands and exit codes copied from the non-author Round 31 replay at `.shokunin/audio/reports/round-31/r31-verifier.md`:

| # | Exact command | Exit |
|---:|---|---:|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-joint-below` | 1 |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-forward` | 1 |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-reverse` | 0 |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | 1 |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | 0 |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | 1 |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | 0 |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 |
| 25 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 |
| 26 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 |
| 27 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 |
| 28 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 |
| 29 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 |

That replay reported 8 exit 0, 21 expected gate-rejection exit 1, no exit 2, and no setup failures. Its prior-28 subset (replay #1 and #3–#29) was 8 exit 0 / 20 exit 1. These are historical Round 31 results, not Round 32 validation.

## Eight invalid control statuses (historical)

Copied from the Round 31 non-author replay's `--probe-invalid` receipt; not rerun here:

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

Round 31's verifier reported all eight matched expectations. This is carried-forward evidence only.

## Limits

This report does not establish Round 32 fit or runner outcome. It makes no equality, causal, perceptual/audibility, rights, engine/runtime, publishing, or promotion claim. In particular, the longer scratch variant does not meet canonical `.12 s` UI duration. No thresholds or canonical artifacts were changed by this guard.
