# Round 11 simplifier review

## Assigned question
Recommend the smallest integration that avoids a second decoder/checker and keeps the new gate off unrelated sections. I read the round-11 declaration in `.shokunin/audio/LOG.md`; I made no source, LOG, SCORECARD, canonical fixture, or receipt changes.

## Recommendation
Extend the existing `section_contrast()` measurement over its already-decoded `samples` array: calculate the one-sample left and right differences around frame 96000, and return the absolute difference of those slopes as one named telemetry field (for example, `internal_join_slope_mismatch_full_scale_per_sample`). Do not add another `sox` invocation or another PCM decoder for this metric. This function already obtains the exact 192000-sample float PCM and computes the join gap.

Add one comparison alongside the existing internal-join gap comparison, inside the same explicitly scoped condition `name in ("stem_layer", "join_probe")`. Gate strict `> .001` against the declared fixture-local bound; do not put this check in `measure()`'s general loop-seam branch, nor apply it to `stem`, `stem_sections`, or other unrelated sections. Keep existing generic outer-seam slope logic unchanged. Add the threshold to the receipt's `thresholds` object and leave all old threshold keys/semantics intact.

This reuses the current section decoding and gate dispatch; it avoids creating a parallel measurement path. Keep both measured values as telemetry on the scoped section records, but only append the new failure for the two declared records.

## Checks and limitations
The declared clean four samples around the join yield side-slope mismatch `0.000762939453125` FS/sample, below `.001`; the declared gap is `0.00018310546875` FS, below `.03`. These are LOG-provided facts, not independent measurements by me. Strict `>` means equality passes, consistent with existing threshold polarity. A candidate must show gap `<= .03`, existing contrast/outer/generic checks passing, and mismatch `> .001` before it demonstrates isolation. If the candidate fails another rule, treat it only as failed-fit telemetry. This is a sample-level numeric proxy, not evidence of perceptual smoothness, audible quality, engine timing, security, or production readiness; `.001` is not audibility-calibrated.

No shell commands were run; therefore there are no shell exits to report.
