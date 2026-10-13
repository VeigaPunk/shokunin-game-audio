# r29-simplifier

## Recommendation

Keep the round-29 change to a narrow signedness control, not a generic search or refactor. The claim to test is that the existing absolute relative-centroid delta accepts a lower-centroid variant once its measured magnitude reaches `.10`, while a lower-centroid variant below `.10` fails only the existing distinctness check. Use one baseline and two source-generated variants in scratch; hold 5760 frames, 48 kHz, mono PCM16, envelope, and level fixed, and vary one explicitly named analytic parameter. Select and record measured candidate values before any runner integration.

Use the existing comparator and unchanged UI specification for both variants. Keep probes opt-in and outside canonical specs/artifacts; do not add a search framework, alter thresholds or the `.020 OR .10` predicate, duplicate comparator logic, or broaden the integration. Confirm duration delta is zero and both files pass the ordinary UI checks. A signed `(variant - baseline)` implementation should reject the above-cutoff lower-centroid case; that is the targeted false implementation, not a request to change the absolute-value rule.

If no compact measured pair meets all conditions, report the failed fit and stop. Do not tune limits or integrate a substitute. Record exploratory failures and setup failures distinctly; do not call nonmonotonic sweep points a smooth trend. No exact `.10` equality is needed or claimed.

## Scope and evidence

No project command, fit, or measurement was run for this simplification review. Therefore there are no project-command exit codes, failed candidate fits, or setup failures to report. This is a scope recommendation only, not evidence that a candidate pair works. Centroid is a numeric FFT proxy; no smoothness, perceptual/auditory, rights, engine, publish, or promotion claim is made.
