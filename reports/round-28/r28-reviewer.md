# Round 28 reviewer: minimal integrated runner modes

## Recommendation

Use two explicit, mutually exclusive opt-in flags:

- `--probe-ui-centroid-below`: build and measure one matched UI pair whose duration delta is zero and whose measured centroid-relative delta is below `.10`; the pair should fail only the existing distinctness predicate.
- `--probe-ui-centroid-above`: build and measure the corresponding matched UI pair whose duration delta is zero and whose measured centroid-relative delta is at least `.10`; the pair should pass distinctness.

“Below/above” names describe the measured centroid-relative comparator, not a guaranteed waveform parameter ordering. If a chosen “above” pair lands exactly on `.10`, it is a valid `>= .10` pass, but do not claim exact-equality calibration unless the receipt actually shows it. Keep each mode self-contained and mutually exclusive, following the existing `--probe-ui-duration-below` / `--probe-ui-duration-at` pattern. Build source-generated 5760-frame 48 kHz mono PCM16 base/alternate files in a round-28 scratch directory; measure both against the ordinary UI spec, then let the existing `_alt` comparison calculate duration and centroid deltas. Do not add a new predicate, threshold, generic sweep framework, or custom UI spec.

## Gate for accepting the integrated pair

Check the receipts rather than trusting waveform parameters: both files must pass format, `.12 s` duration, level, and 250–4000 Hz centroid-band checks; duration delta must be exactly zero as reported; below mode must have centroid relative delta `< .10` and only the distinctness failure; above mode must have centroid relative delta `>= .10` and no failures. Preserve the existing `.020` and `.10` constants, canonical hashes, prior mode outcomes, and invalid-control statuses. If either candidate misses these conditions, call it a failed fit and do not relax a gate or threshold to force it through.

## Scope and evidence

The runner reports a numeric spectral-centroid proxy from the whole waveform. This proposal supports only two-point numeric polarity under the measured toolchain. It does not establish audibility, perceived similarity/difference, rights clearance, engine behavior, publishing readiness, or promotion.

No shell commands or project runs were performed for this reviewer task, so there are no command exit codes, receipts, or observed fit/setup failures to report. The round-28 declared LOG entry is the source of the target conditions; this report proposes names and a minimal integration shape, not evidence that candidates fit.
