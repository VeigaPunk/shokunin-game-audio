# Round 37 simplifier review

## Recommendation
Keep this to one opt-in `--probe-ambience-centroid-below` control. Do not add a reusable family framework, alter shared comparison logic or thresholds, or change canonical fixtures. The probe can generate its named scratch pair under `corpus/live/round-37/` and use the existing project measurement and distinctness rule.

## Minimal control shape
The mode should generate two original, deterministic 2.0 s / 48 kHz / mono PCM16 analytical ambience signals: a baseline and a nonidentical variant. Run the existing measurements on both and report the normal format, level, 5–200 Hz centroid, and loop endpoint/slope checks. Preserve the existing generic `_alt` comparison; the opt-in pair should expose the same existing OR distinctness calculation, without a new cutoff or comparison abstraction.

For the intended negative, the measured durations must be equal (delta exactly 0.0 s), and the measured nonzero baseline-relative centroid delta must be strictly below 0.10 (preferably above 0.05). Thus neither existing OR arm passes. Both samples must still pass ordinary and seam checks; the receipt should identify the distinctness rejection separately from those checks. Fail closed if a generated pair does not numerically fit; do not relabel a setup failure as a fit or as evidence about the rule.

## Scope and interpretation
This is one local numerical negative control. It can demonstrate that this measured equal-duration pair is rejected by the current rule. It does not calibrate all signals or establish spectral/perceptual similarity, audible seamlessness, or asset quality. No audition, quality, production, rights, engine, publishing, or promotion claim is made.

## Execution status and commands
No shell commands were run, so there are no shell exit codes. I inspected the round-37 LOG declaration and current builder/measurement source by Python file reads only. No probe was generated or numerically measured: this is a setup/design recommendation, not a successful or failed numeric fit. No source, canonical asset, LOG, SCORECARD, or other report was edited.
