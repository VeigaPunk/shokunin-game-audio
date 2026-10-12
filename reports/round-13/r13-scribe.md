# Round 13 scribe — proposed depth decision table

## Scope and status

This is a draft from the Round 13 declaration in `.shokunin/audio/LOG.md`, not a verification or adjudication. I did not run shell commands, generate or measure PCM, or inspect runtime receipts. No Round 13 candidate fit, integration, replay, or pass is established. No source, LOG, SCORECARD, canonical artifact, or commit was changed.

The declared single move is **depth**: add a same-format, same-length synthetic flat 180 Hz component negative control for the existing two-half `stem_layer_alt` 180 Hz contrast check. The intended result is exactly one additional failure: `sections: 180 Hz component amplitude contrast < 6 dB or invalid`. Existing gates and numeric thresholds stay unchanged. The flat control tests this measurement branch only; it does not demonstrate audible flatness or engine behavior.

## Before / proposed-after decision table

| Decision item | Before (`db36a69`, per declaration) | Proposed after (must be demonstrated; not established here) | Evidence required |
|---|---|---|---|
| Canonical fixture inventory | 12 canonical PCM WAVs including passing 180 Hz `stem_layer_alt` | Exactly the same 12 canonical assets and hashes; control is scratch-only, not canonical | Hash all 12 and compare to the declared baseline; inspect builder and paths to establish no canonical addition or mutation. |
| 180 Hz contrast depth | `stem_layer_alt` has two 2 s sections measured at 180 Hz and passes the existing >=6 dB contrast rule; no matched flat180 control | An original same-format, same-length control has equal per-half 180 Hz component amplitude and trips only the existing contrast failure | Receipt section telemetry confirms measured frequency, equal component amplitudes/contrast below 6 dB; control's generic and seam metrics pass. Clean alt normal receipt continues to pass. |
| Other validations | Existing `_alt` distinctness and generic, outer seam, internal join gap and side-slope gates apply to clean alt | Clean alt still passes all existing checks; control passes generic/outer/internal gap and side-slope, plus `_alt` distinctness where applicable; only contrast fails | Full receipt and failure list for both control and clean alt. Ensure control is not treated as a variant if it is not in measured variant data; if included, explicitly establish distinctness result. |
| Old modes / fixture identity | Round 12 established normal, layer-slope, layer-join, flat30, flat120, outer-slope, failing, invalid and normal restore expectations | All old expectations unchanged; exact 12 canonical hashes unchanged | Non-author serial replay with exact commands, exit codes, receipt paths and failure sets. Compare normal/restore receipts and old mode expectations rather than assuming. |
| Axis claim | Component contrast has a positive stepped 180 Hz fixture but no matched flat negative control | **Depth may improve** only if the matched control isolates the existing contrast branch and clean alt/old behavior remain intact | Independent verifier receipts and source review. Do not claim calibration improved: thresholds are reused, not tuned. No claim of audible, adaptive-engine, music, production, or security behavior. |

## Source-review cautions

Current source inspected for this draft already measures `stem_layer_alt` at 180 Hz, uses the shared section contrast helper and applies internal gap/side-slope checks to the clean alternate. It also includes existing flat30, flat120, layer-join, layer-slope, outer-slope, failing, and invalid probe branches. I found no `--probe-layer-alt-flat` branch in the inspected parser/measurement flow. Therefore a proposed integration must minimally add a scratch-generating mode and a measured flat180 probe path/section inclusion at 180 Hz, without adding a new threshold or making the control canonical. Reuse existing measurement and failure logic rather than copying gates. Review that any `stem_layer_alt` distinctness comparison is meaningful for the control and does not accidentally make another unrelated failure.

## Evidence still outstanding

1. Executor and independent alternate reports: original synthetic PCM recipes, hashes, format/duration, equal 180 Hz half amplitudes, contrast, generic and outer seam measurements, internal gap/slope, distinctness where applicable, and complete failures including failed-fit telemetry. No borrowed or canonical PCM.
2. Minimal source review confirming only the intended probe path, shared existing gates/thresholds, no canonical asset/hash changes, and no old-mode behavior change.
3. Independent verifier's exact command strings and exits for normal, flat180, layer-slope, layer-join, flat30, flat120, outer-slope, failing, invalid and normal restore; receipt paths and actual failure classifications. Author runs are not independent verification. No missing run should be inferred.
4. All 12 canonical hashes against the baseline and actual receipts showing clean alt passes, flat180 has exactly the declared sole failure, and all old mode failure sets remain expected.
5. Independent per-axis adjudication. Depth can be called improved only if the control isolates the intended contrast branch. Coverage should remain unchanged; calibration should remain unchanged absent tuning evidence; harm must be assessed from receipts, not presumed away.

**Decision: pending.** This table records a falsifiable proposed outcome and its evidence requirements; it does not certify any proposed-after result.
