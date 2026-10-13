# Round 32 reviewer — minimal opt-in mode

## Recommendation

Add exactly one opt-in builder/runner mode for the declared mixed case, e.g. `--probe-ui-duration-below-centroid-above`. Source-generate a 5,760-frame 48 kHz mono PCM16 UI-shaped baseline and a 6,719-frame variant. Use the canonical `SPECS["ui"]` for the baseline and a separate scratch expected duration `(6719 / 48000, *SPECS["ui"][1:])` for the variant. Select and report the variant analytic coefficient from an empirical measured fit; do not infer the centroid from the coefficient. The requirement is actual measured duration delta nonzero and `< .020 s`, and actual baseline-denominator absolute centroid-relative delta `>= .10`, with both files passing their applicable ordinary checks. The variant duration is about `.139979 s`; it does **not** conform to canonical `.120 s` UI duration.

Leave the existing `_alt` comparator and its `.020 OR .10` thresholds untouched. With the requested measured signs, the existing OR should pass solely through the centroid arm while the duration arm is false. Keep implementation to one opt-in source-generated pair and one branch that applies the variant's separately declared scratch duration; no new threshold, comparator, generalized fitting mode, or canonical WAV change. Record unsuccessful numeric fits separately from setup/command errors, and report actual runner receipt values and exits.

This is one observed mixed-signals comparator case, not causal independence, exact cutoff behavior, or a general rule. It supports no claim of perceptual or audible distinctness, rights, engine behavior, publication, or promotion.

## Inspection and command status

I read the Round 32 declaration in `.shokunin/audio/LOG.md`, the existing builder and measurement runner, and the Round 31 reports for the established paired-probe pattern. No shell command, test, builder, runner, or coefficient fit was run; there are no command exits, fit failures, or setup failures from this review. This is design guidance only, not empirical evidence that a coefficient or integrated probe passes.
