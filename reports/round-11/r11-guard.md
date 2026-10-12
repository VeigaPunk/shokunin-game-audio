# Round 11 guard inventory — internal side-slope claim

## Scope and method

Report-only inventory for the declared `stem_layer` internal-join side-slope mismatch claim. I read round-11's declaration in `.shokunin/audio/LOG.md`, inspected the current measurement script and round-10 verifier evidence, and computed SHA-256 for the eleven current canonical WAVs. I did not run shell commands or replay measurements; there are no new command exits or receipts. I changed no source, candidate/scratch WAV, canonical asset, receipt, LOG, SCORECARD, or other report. This report is the only file written by this lane.

## Canonical asset inventory

Current filesystem hashes (11 files):

| WAV | SHA-256 |
|---|---|
| `ambience.wav` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` |
| `ambience_alt.wav` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` |
| `impact.wav` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` |
| `impact_alt.wav` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` |
| `movement.wav` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` |
| `movement_alt.wav` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` |
| `stem.wav` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` |
| `stem_layer.wav` | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` |
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` |
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` |

These are current filesystem hashes, not an independent comparison to a Git revision in this lane. Round-10 verifier reported all eleven matching before-state `f32ab7f`; round-11 verification must independently re-establish its requested before-state comparison. No playback or measurement replay was performed.

## Existing measurement modes, prior commands and exits

The current inspected `measure_audio.py` exposes normal mode and the existing options `--probe-layer-join`, `--probe-flat`, `--probe-layer-flat`, `--probe-slope`, `--probe-failing`, and `--probe-invalid`. It does not yet expose a round-11 `--probe-layer-slope` option. The exact commands and exits below are transcribed from round-10 verifier's recorded serial replay; **they were not run by this guard lane**. Negative-control exit 1 is the documented expected outcome, not a generic pass.

| Existing mode | Exact command | Prior exit | Prior outcome |
|---|---|---:|---|
| normal | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | Clean battery passed |
| internal join control | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | Selected join probe failed its internal adjacent-sample-gap check |
| flat 30 Hz | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | Flat30 section-contrast control rejected |
| flat 120 Hz | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | Flat120 section-contrast control rejected |
| outer slope | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | Outer slope negative control rejected |
| failing | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | Declared broken-amplitude control rejected |
| invalid-input battery | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | Four invalid probes classified as expected failures |
| normal restore | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | Clean battery passed after controls |

These prior exits/characterizations are evidence transcribed from `.shokunin/audio/reports/round-10/r10-verifier.md`, not independently checked here. The round-11 declared new internal side-slope probe is not an old mode and has no command/exit evidence in this report.

## Existing limits and declared before-state

Relevant existing numeric checks inspected in `measure_audio.py`:

- 48,000 Hz mono and duration within ±0.001 s of each fixture's declared duration.
- Peak `< 0.95` full scale and RMS `>= 0.001` full scale.
- Centroid bands: UI 250–4000 Hz; impact 50–15000 Hz; movement 100–16000 Hz; ambience 5–200 Hz; stem families 100–2000 Hz.
- For loop fixtures, outer endpoint jump must be `<= 0.03` FS and outer slope mismatch `<= 0.001` FS/sample.
- Section fixture has 192,000 decoded samples, divided into 96,000-sample halves; section component amplitude must be `>= .01` FS and RMS `>= .001` FS in each half; contrast must be `>= 6 dB`. `stem_layer` checks the 120 Hz component.
- Each of four alternate variants must differ by at least 20 ms duration or 10% relative centroid.
- Round-10 internal adjacent-sample-gap rule is strict `> .03` FS for `stem_layer` and its join control. This is separate from the proposed round-11 slope-mismatch value.

Round-11 LOG declares before-state `f15fe55`. Its four decoded samples around the clean layer join are `[-0.0003662109375, -0.00018310546875, 0, 0.000946044921875]` FS at indices 95,998–96,001. The join gap is `.00018310546875` FS; the proposed side-slope mismatch is `.000762939453125` FS/sample, compared against a proposed strict `> .001` failure rule (equality passes). The `.001` value reuses the outer-slope numeric bound as a fixture-local proxy; it is not calibrated for audibility. The declared intended isolation requires the new original PCM control to pass the `.03` join-gap rule, 120 Hz section contrast, generic checks and outer checks, and fail solely on internal side-slope mismatch. No candidate was generated or measured in this lane, so that isolation remains unverified here.

## Limits

This inventory makes no perceptual, engine, security, or production claim. A decoded-PCM adjacent-difference comparison does not by itself establish audible smoothness, click-free transitions, runtime behavior, or an empirically calibrated threshold. No replay was performed.
