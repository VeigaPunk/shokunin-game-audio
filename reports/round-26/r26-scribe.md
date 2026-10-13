# Round 26 scribe — duplicate-variant decision table draft

## Decision table

| Decision | Required observation | Decision if observed | Evidence status in this draft |
|---|---|---|---|
| Scratch pair identity | `ui_clone.wav` and `ui_clone_alt.wav` are the same generated 48 kHz mono PCM16 waveform (prefer identical file hashes or identical decoded samples); both are measured with the existing `ui` spec and the `ui_clone_alt` baseline is `ui_clone`. | Identity/baseline established; continue. | Pending independent receipt/hash evidence. The declared claim specifies a matched exact duplicate; this draft does not establish it. |
| Ordinary measurement eligibility | Each pair member has no ordinary measurement failures: PCM16, 48 kHz mono; duration within the UI spec; peak/RMS and centroid checks pass. | If both pass, continue; otherwise the proposed negative is not isolated. | Pending. Do not treat a distinctness failure as sufficient if either member has another failure. |
| Existing distinctness rule | For `ui_clone_alt`, measured `duration_delta_s` is 0 and `centroid_relative_delta` is 0; existing predicate remains `duration_delta >= .020 s OR relative_centroid_delta >= .10`; result is `passed: false` and the sole added failure is `distinctness: duration < .020 s and centroid delta < 10%`. | If all parts hold, classify as a bounded exact-duplicate negative for the existing rule. | Pending non-author replay. No threshold change is proposed. |
| Probe-mode outcome | Normal canonical mode remains successful; the opt-in duplicate mode exits 1 because of the matched variant's distinctness failure only, with a persisted receipt and no traceback or unrelated failures. | Attribute the mode's nonzero exit to the expected distinctness rejection only. | Pending. A nonzero exit alone would not establish this attribution. |
| Guard preservation | Thirteen canonical WAV hashes, five existing variant comparisons, and previously declared mode/invalid-input outcomes remain unchanged. | Coverage/depth guards preserved for this bounded move. | Requires independent replay and comparison to the declared before-state; not verified here. |
| Round verdict | A named non-author verifier reproduces the relevant outcomes; subsequent adjudication evaluates the per-axis claim. | Only then may the parent consider the declared depth move admitted. | Not a verdict. This report is a decision-table draft, not verifier or adjudicator evidence. |

## Scope and limitations

- The proposed result is an exact duplicate at `(duration delta, relative centroid delta) = (0, 0)`, jointly below both existing OR branches. It exercises one point well inside the rejection region; it does not test either cutoff, equality behavior, or isolate the contribution of either branch.
- Passing the existing numeric UI checks and failing this duplicate rule establishes only the behavior of this fixture pair under this runner. It does not establish auditory similarity, perceptual quality, a general deduplication method, or behavior for other formats or signals.
- Keep scratch inputs under the declared round-26 live scratch area. Do not add canonical assets or alter the thresholds, five existing variant comparisons, or shared source as part of this scribe report.
- Receipt/hash/control comparisons and independent replay are required before admission. If the pair has any ordinary failure, mismatched baseline, absent receipt, or an unexpected failure, classify the proposed probe as unproven/failed fit rather than broadening the claim.
- No auditory, engine, rights, publishing, production, or promotion claim is made.

## Commands and exits

No shell commands were run for this report; there are no shell exit codes to report. This is a proposal only and does not claim execution or independent verification.
