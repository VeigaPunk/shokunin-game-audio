# Round 37 reviewer — minimal opt-in scratch design

## Recommendation

Keep the 17 canonical artifacts, their `SPECS`, threshold table, five generic `_alt` comparisons, and four existing explicit family-comparison records untouched. Add only a separate, opt-in scratch mode that creates two files under `corpus/live/round-37/` and passes them through the existing `measure()` and generic `_alt` distinctness calculation. Do not add scratch entries to canonical `SPECS` or canonical `measurements`.

## Two scratch specs and generic route

Use the names `ambience_probe` and `ambience_probe_alt`; the baseline key is necessary because the current generic route resolves each `_alt` key by stripping that suffix and looking up the baseline in `measurements`.

Both local-only specs are `(2.0, 5, 200, True)`: exactly 2.0 seconds, centroid band 5–200 Hz, loop enabled. The builder writes `corpus/live/round-37/ambience_probe.wav` and `corpus/live/round-37/ambience_probe_alt.wav`, each 48 kHz mono PCM16. Generate original deterministic analytical loops with equal sample counts. Make the variant coefficients differ, while fitting the project-measured centroid relative delta to `0 < delta < .10` (preferably `.05 < delta < .10`). Avoid claiming that coefficient difference means perceptual difference.

The runner's opt-in branch should create a local `probe_specs` mapping for these two names, call existing `measure(name, spec, explicit_live_path)` for each, and add only these two results to the run's measurement dictionary. The existing `for name, variant in measurements.items(): if name.endswith("_alt")` logic then naturally compares `ambience_probe_alt` with `ambience_probe`, using unchanged duration-or-centroid thresholds. Do not add a family comparison: this is a generic-path negative control, not a new canonical family member. The runner must explicitly label the mode `probe-ambience-centroid-below` and produce a suffixed receipt (for example `-ambience-centroid-below`) with both measurements, generic distinctness entry, and normal unchanged threshold receipt.

## Outcome and evidence boundary

A successful setup has both measurements free of ordinary and loop-seam failures, exactly zero measured duration delta, and measured nonzero centroid-relative delta below `.10`. The generic comparison must be `passed: false`; the variant receives only the existing distinctness failure and runner exits **1**. This is the intended numeric negative-control outcome, not setup failure. A missing file/tool, decode/measurement exception, invalid format, band/level/seam failure, or inability to meet the requested centroid interval is setup/fit failure, not evidence of threshold behavior; report it separately and do not count it as a passing control. Do not weaken the generic rule or recast exit 1 as a runner defect.

The local mode should be isolated from the default path: absent the flag, no scratch files are built or read and normal output remains canonical. One opt-in run can also retain the unchanged 17 canonical measurements in its receipt for direct preservation checking, but scratch keys must remain visibly noncanonical and must not alter canonical asset hashes. Preserve existing UI/impact/movement/ambience family records and all prior invalid-probe semantics.

This single equal-duration pair tests that this selected pair falls below both numeric OR cutoffs while ordinary numeric and seam checks pass. It does not establish general calibration, perceived similarity, audible seamlessness, spectral-distribution similarity, or any audio quality. No audition/quality, production, rights, engine, publishing, or promotion claim is made.

## Commands and exits

No shell commands were run for this review. I read the Round 37 LOG declaration and inspected the existing builder, runner, and shell wrapper in Python. Therefore there are no command exit codes or numeric fit results to report; this is a design review only.
