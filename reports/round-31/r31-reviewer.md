# Round 31 reviewer — minimal runner mode

## Recommendation

Implement one opt-in `--probe-ui-joint-below` mode, source-generating a 48 kHz mono PCM16 baseline of 5760 frames and a variant of 6719 frames. In the runner, measure the baseline with `SPECS["ui"]` and the variant with a separate scratch spec `(6719 / 48000, *SPECS["ui"][1:])`. This keeps the variant's own expected duration (about 0.139979 s) distinct from the canonical UI duration of 0.120 s; do not describe or test the longer variant as canonical-UI-duration conformant.

Retain the existing distinctness computation and thresholds without edits: duration absolute delta `>= .020` OR baseline-denominator absolute centroid relative delta `>= .10`. The intended measured pair has both deltas nonzero and strictly below their respective cutoffs, so it should be rejected for distinctness while each file passes its own ordinary checks. A pass/fail from this case exercises that combined below-cutoff observation only; it does not establish exact cutoff equality, perceptual similarity, a universal OR law, or calibration of the ordinary ±1 ms duration check.

Keep the implementation narrow: one flag, one source-generated pair, one branch to measure the variant with its per-variant scratch duration, and no new thresholds, generalized mode framework, or canonical WAV changes. Report actual measured values and any unsuccessful coefficient fits rather than inferring centroid movement from the phase multiplier.

## Evidence and command status

I read the Round 31 declared claim and wave specification in `.shokunin/audio/LOG.md`, and inspected the existing fixture measurement/build code to check the runner shape. I ran no shell commands or tests, so there are no command exit codes or fit/setup failures to report. No empirical fit result is available in this review; the proposed behavior remains to be measured by the implementation and replay.

## Limits

This is a runner-design review only. It makes no claim about exact threshold equality, perceptual/audio quality, engine behavior, rights, publication, or promotion. The longer variant is not represented as satisfying the canonical 0.12 s UI duration.
