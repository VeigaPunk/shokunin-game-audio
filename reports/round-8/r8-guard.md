# Round 8 guard inventory — before-state

Scope: requested read-only inventory for the declared round-8 coverage claim. I did not replay any audio command, modify shared code, fixtures, LOG, SCORECARD, or canonical assets. This report is the only file written by this lane.

## Before-state canonical inventory

Declared round-8 before commit: `75c95d9`. The ten canonical WAVs are the same named set compared in the round-7 non-author report against `cba2748`; round 7 changed only the invalid-probe scratch path/list, not canonical WAVs. Current-worktree byte hashes, cross-checked in `r7-verifier.md` against the earlier baseline, are:

| Canonical WAV | SHA-256 |
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

The declared before-state has ten canonical WAVs, including `stem_sections.wav` (4.0 s, two 2.0 s sections), and no separate synchronized layer. The round-8 proposed layer is an additional analytic companion on a 192000-frame/4.000 s grid, not an existing canonical asset.

## Existing modes and controls (inventory only; no replay)

The existing checker modes are normal, `--probe-flat` (the matched flat30 section control), `--probe-slope`, `--probe-failing`, and `--probe-invalid`. Round-7 independent verifier recorded corrected command exits and receipts:

| Mode / exact command | Recorded exit | Recorded outcome / receipt |
|---|---:|---|
| Normal: `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | 10 fixtures, no failures; receipt `corpus/live/runs/20261012T171605486878Z-normal/measurements.json`; later restore receipt `20261012T171615709159Z-normal/measurements.json`, exit 0. |
| Flat30: `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `flat30_probe` rejected for section contrast only; `20261012T171613915489Z-flat/measurements.json`. |
| Slope: `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `slope_probe` rejected for slope mismatch; `20261012T171614543341Z-slope/measurements.json`. |
| Failing: `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `ambience` rejected for centroid and endpoint; `20261012T171615125782Z-failing/measurements.json`. |
| Invalid: `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `20261012T171718939143Z-invalid/measurements.json`: four named expected failures, no traceback: short_sections (144000/192000, section count), corrupt (ffprobe exit 1, decode), wrong_format (44100 Hz/stereo, format), odd_sections (101/192000, section count). Exit 1 is the intentional negative-control result. |

Prior to the odd-length addition, round-6 independent receipt `20261012T170607093097Z-invalid/measurements.json` recorded the first three invalid modes. Mode exit and receipt details above are transcribed from the durable `r7-verifier.md`; I did not rerun them. The round-7 verifier also disclosed nine malformed setup attempts exiting 127; these are not passes and are excluded from the table.

## Existing numeric thresholds relevant to preservation

Thresholds remain fixture-local implementation rules, not calibration claims:

- Format: exactly 48,000 Hz and mono.
- Duration: expected duration within ±0.001 s (reject only if absolute error is greater than 0.001 s).
- Peak: strictly less than 0.95 full scale; RMS: at least 0.001 full scale.
- Centroid: inclusive per-fixture bands: UI 250–4000 Hz; impact 50–15000 Hz; movement 100–16000 Hz; ambience 5–200 Hz; stems 100–2000 Hz.
- Loop endpoint jump: at most 0.03 FS; loop slope gap: at most 0.001 FS/sample. Applied to ambience, ambience_alt, stem, stem_sections, and slope probe.
- SFX variants: duration delta at least 0.020 s **or** centroid relative delta at least 10%.
- Existing `stem_sections` check: exact 192000 decoded samples split into two 96000-sample halves; each projected 30 Hz component amplitude at least 0.01 FS and each half RMS at least 0.001 FS; signed `20 log10(A2/A1)` at least 6.0 dB. Existing flat30 matches section amplitudes (~0.036 FS each) and fails contrast at ~0 dB.
- Loudness has no acceptance window; ebur128 values at/below −70 LUFS are represented as null. Bandwidth is reported but not gated.

Round-8's proposed 120 Hz component-contrast check is a new coverage measure and must not be conflated with the existing 30 Hz rule or treated as perceptual evidence. No conclusion about engine adaptation, mix quality, audible transition, loop seamlessness, malformed-file security, or production readiness follows from this inventory.

## Commands/exits for this lane

No shell commands were run; no audio replay occurred. Hash inventory was read from the worktree and cross-referenced with the existing round-7 verifier's byte-comparison report. All mode exits above are prior recorded evidence, not executions by this lane.
