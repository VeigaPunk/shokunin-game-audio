# Round 16 scribe — before/after decision-table draft

## Status and scope

This is a planning/evidence-limits draft, not a report of a completed candidate, integration, replay, or verdict. I read the round-16 source log and the fixture builder/measurement source. They describe the baseline and proposed test, but do not provide a round-16 candidate WAV, runner receipt, independent replay, or adjudication result. I did not run shell commands or measure audio. The proposed after-state below is a hypothesis and acceptance condition only.

## Decision table

| Question | Before `35d978c` (as declared in round-16 log/source) | Proposed after-state | Evidence/status |
|---|---|---|---|
| Canonical `stem_layer_alt` 180 Hz section amplitudes | First/second approximately `.015/.050` FS; signed contrast about `+10.4572506 dB`, above the existing `>=6 dB` rule | Keep canonical artifact and its behavior unchanged | Declared baseline only in round-16 log; this scribe did not re-decode or fingerprint it. |
| Existing flat 180 Hz negative | `flat180_probe` uses equal `.036/.036` FS sections and has `0 dB` contrast, so exercises rejection of insufficient contrast without reversing direction | Preserve this control and its existing failure set | Round-16 log/source declaration; no fresh run in this report. |
| Reversed-section 180 Hz negative | No valid reversed `.050/.015` control is declared | Add opt-in `--probe-layer-alt-reverse` scratch, nominally first/second `.050/.015` FS at 180 Hz; it should fail only the existing contrast rule if all other checks pass | Proposed, not implemented or measured here. The sign and approximate magnitude (about `-10.457 dB` under the stated amplitudes) are arithmetic expectations, not decoded runner results. |
| Reversed candidate validity and other gates | No reversed control to assess | Both component amplitudes remain above existing `.01` FS validity minimum; internal join gap `<=.03` FS and slope mismatch `<=.001` FS/sample; generic and outer fixture checks pass; sole rejection is existing signed contrast `<6 dB` | Acceptance criteria only. A failed fit or any additional failure cannot count as the intended sole-contrast negative. |
| Prior behavior and canonical files | Twelve canonical WAVs, five `_alt` records, and prior mode failure sets are baseline | Preserve all twelve canonical hashes, five `_alt` records, and every prior failure set versus `35d978c` | Required regression checks, not demonstrated by this scribe. The round plan calls for independent replay. |
| Axis judgment | Existing positive contrast and flat/equal negative do not cover the reversed signed direction | Could improve **depth** if a reversed candidate is independently shown to fail solely on contrast, with validity/other gates passing and controls/artifacts unchanged | No axis result or no-harm conclusion established here. Coverage/calibration also remain unadjudicated. |

## Evidence limits and follow-up

The source describes `section_contrast` as measuring the 180 Hz FFT-bin amplitude in each 96,000-sample half, requiring each amplitude to be at least `.01` FS and each half's RMS at least `.001` FS, then calculating signed contrast as `20*log10(second/first)`. Its passing condition is valid input and contrast `>=6.0 dB`. The generic stem-layer fixture bounds and outer distinctness checks are separate checks; a candidate must actually pass those too. These source-code rules explain what a later receipt should report; they do not establish that a proposed WAV meets them.

The round-16 log proposes first→second `.050/.015` FS as a synthesis target, not a measured result. Exact decoded amplitudes, signed contrast, validity, internal-join values, generic/outer results, generated-vs-selected byte identity, and the complete failure list must come from candidate/runner evidence. Independent replay, unchanged canonical hashes and prior failure sets, then adjudication are distinct subsequent evidence steps. Failed setup is not a pass.

This is strictly a deterministic-fixture numeric gate proposal. It supports no inference about audible smoothness or seamlessness, musical quality, adaptive-engine behavior, sample rights, external JSON-reader compatibility, security, or production readiness.

No shell command was run for this report; there are no command exits or run receipts to claim. No result is invented here.
