# Round 45 simplifier — two-mode diff review

## Recommendation

Keep this as two explicit opt-in fixture modes, `5713` and `5711`; do not add a generic probe framework, alter the duration predicate/thresholds, or tune other fixtures. Based on the R45 LOG declaration, both modes should synthesize one deterministic original UI-shaped 48 kHz mono PCM16 WAV in `corpus/live/round-45/<mode>/`, then measure that WAV against the existing `SPECS["ui"]` with the existing `measure` function. Preserve ordinary artifacts and all existing behavior.

The minimal source shape is two explicit CLI flags, one small builder function taking only the selected fixed frame count/label (or two explicit branches), and one measurement branch selecting that WAV and existing UI spec. Add their mode names to the existing one-mode guard, builder invocation, receipt mode/suffix selection. Do not generalize mode dispatch, spec handling, duration comparison, or validation. Pin each generated file's SHA in its report/evidence; distinctness is a requirement, not a new comparator.

At 48 kHz, 5760 frames is the `.12 s` UI target. The frame-count design deltas are signed `5713/48000 - .12 = -0.0009791666666666666 s` and `5711/48000 - .12 = -0.0010208333333333334 s`; these are predictions, not measurements. Record the actual ffprobe duration and calculate signed `duration - .12` and absolute delta from the resulting receipt. A valid numerical result requires the first mode to pass and the second to fail only with `duration: outside ±1 ms`; confirm format, peak, RMS, and centroid all pass for both. Distinguish builder/CLI/ffprobe setup errors from a completed numerical failed fit. Do not infer behavior at 5712 frames or exact `.001 s` equality.

## Scope and evidence

I read the R45 declaration in `.shokunin/audio/LOG.md`, the current measurement and fixture-builder source, and the R44 simplifier report for the already established two-mode pattern. Current source contains the R44 `5807`/`5809` modes and no `round-45` implementation. I ran no shell commands, builder, runner, or ffprobe; there are no command exits, measured durations, deltas, hashes, or numerical fit outcomes from this review. Thus this is a minimal-diff recommendation, not validation of the declared pair.

This is numerical fixture calibration only. No audition or inference about perceived duration/quality, production, rights, engine, publishing, or promotion.
