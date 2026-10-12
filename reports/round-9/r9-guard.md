# Round 9 guard inventory — declared before-state

Scope: report-only inventory for the round-9 receipt-semantics claim. I inspected the current measurement source and prior durable round-8 evidence; I did not replay any command, modify source, receipts, canonical assets, LOG, SCORECARD, or other report. No shell commands were run by this lane. Prior command results below are transcribed evidence, not executions by me.

## Canonical asset inventory

The ten canonical WAVs from before the round-8 layer addition, as documented against `75c95d9`, and the current eleven-asset set are:

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
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` |
| `stem_layer.wav` (round-8 addition) | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` |

The first ten hashes are the unchanged pre-layer inventory recorded in `r8-guard.md` and compared by the round-8 non-author verifier to `75c95d9`. The eleventh hash is recorded in the round-8 verifier as the candidate-matching generated canonical layer. I did not independently compare these against Git objects in this lane.

## Existing mode commands and recorded evidence

All commands use `python3 .shokunin/audio/corpus/fixtures/measure_audio.py`.

| Mode | Exact command | Recorded exit | Recorded receipt / result |
|---|---|---:|---|
| Normal | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261012T172620813098Z-normal/measurements.json`; eleven assets, no failures, four variant checks pass. Restore run also exit 0: `corpus/live/runs/20261012T172640257036Z-normal/measurements.json`. |
| Flat30 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `corpus/live/runs/20261012T172638021452Z-flat/measurements.json`; expected flat 30 Hz section-contrast failure. |
| Flat120 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `corpus/live/runs/20261012T172637297691Z-layer-flat/measurements.json`; expected flat 120 Hz contrast is the only failure. This is a round-8 control mode, not a production asset. |
| Slope | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `corpus/live/runs/20261012T172638719794Z-slope/measurements.json`; expected loop-slope failure. |
| Failing | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `corpus/live/runs/20261012T172639377325Z-failing/measurements.json`; expected centroid-band and endpoint-seam failures. |
| Invalid | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `corpus/live/runs/20261012T172639602990Z-invalid/measurements.json`; four expected failures: short section count, corrupt decode, wrong format, odd section count. |

These are the corrected serial replay commands and exits **0/1/1/1/1/1/0** documented by `r8-verifier.md`; the verifier separately disclosed seven initial malformed attempts with exit 127 and no receipts, excluded as failures. This lane did not replay any mode. The mode sequence exercised controls and restore; exits of 1 are expected negative-control outcomes, not generic pass codes.

## Receipt field/frequency facts and measured values

The currently inspected `measure_audio.py` source still has the pre-round-9 shape: top-level `thresholds.section_component_hz` is fixed to 30; each `sections` entry has `component_hz`; contrast is named `section_energy_delta_db`. `section_contrast()` splits exactly 192000 samples into two 96000-sample sections, computes the selected FFT component amplitude, then stores signed `20*log10(A2/A1)`. This is a component-amplitude contrast, not integrated section energy. The 30 Hz default is used for `stem_sections`/flat30; `stem_layer`/flat120 are passed 120 Hz. Thus per-entry `component_hz`, not the top-level 30, identifies the actual measured component. Round-8 evidence: layer amplitudes `.01199958745` and `.05999774520` FS, contrast `13.9793723 dB`; flat120 amplitudes `.03599720971` and `.03599720971` FS, contrast `0.0 dB`; flat30 likewise rejects equal amplitudes at approximately 0 dB. These are prior-receipt values, not new measurements.

## Numeric acceptance limits to preserve (inventory, not calibration)

- Format: exactly 48,000 Hz, mono.
- Duration: expected duration tolerance ±0.001 s.
- Peak: `< 0.95` FS; RMS: `>= 0.001` FS.
- Centroid bands (Hz): UI 250–4000; impact 50–15000; movement 100–16000; ambience 5–200; stems 100–2000.
- Loop endpoint jump: `<= 0.03` FS; loop slope gap: `<= 0.001` FS/sample.
- SFX variant distinction: duration difference `>= 0.020` s **or** relative centroid difference `>= 0.10`.
- Section check: exactly 192000 samples, split into 96000 per half; component amplitude floor `>= 0.01` FS per section; section RMS floor `>= 0.001` FS; signed amplitude ratio `20*log10(A2/A1) >= 6.0 dB`. Existing sections use 30 Hz; layer sections use 120 Hz.
- No loudness acceptance window; reported ebur128 values at/below −70 LUFS are null. Bandwidth is reported, not gated.

The round-9 declared change is a semantics-only receipt disclosure: use per-section frequency as the sole frequency source, rename the contrast output to `component_amplitude_contrast_db`, remove misleading top-level frequency metadata, retain numeric values/formula and thresholds, and leave historical JSON untouched. This inventory does not verify that proposed integration or its replay has occurred. It makes no perceptual, engine, security, production, or threshold-calibration claim.
