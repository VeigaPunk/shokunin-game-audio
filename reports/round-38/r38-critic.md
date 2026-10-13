# R38 critic — confounds and interpretation limits

## Scope and evidence

I read the Round 38 declaration in `.shokunin/audio/LOG.md`, the R38 scout report, and inspected the current below-probe source wiring in `build_artifacts.py` and `measure_audio.py`. I did not generate scratch audio, run the project measurement helper or runner, or make a numeric fit. Accordingly, this review has **no R38 positive numeric result** to validate; the absence of a fit is not a failed fit. No setup failure occurred in this review.

Exact shell command and exit:
- `git status --short && find .shokunin/audio/reports/round-38 -maxdepth 1 -type f -printf "%f\n" | sort && git diff -- .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/corpus/fixtures/measure_audio.py` — exit **0**. At inspection, the only tracked modified path shown was `.shokunin/audio/LOG.md`; only `r38-scout.md` was present in the target report directory; the diff for the two source paths was empty. I did not edit any of those paths.

The scout records the prior equal-duration R37 negative: 2.0s baseline/variant, measured centroid-relative delta `0.06585562259644766`, duration delta `0.0`, both ordinary/loop failure lists empty, and only generic distinctness failure. That is useful local negative evidence, but not an R38 positive result or universal threshold validation.

## Confound audit for the declared positive

A follow-up validation command, `git status --short -- .shokunin/audio/reports/round-38/r38-critic.md && git diff --check -- .shokunin/audio/reports/round-38/r38-critic.md && git diff --no-index /dev/null .shokunin/audio/reports/round-38/r38-critic.md >/dev/null; printf "report_diff_exit=%s\n" "$?"`, exited **0** overall, printed the report as untracked, and printed `report_diff_exit=1` because `git diff --no-index` reports the expected difference between `/dev/null` and a new file. `git diff --check` succeeded.

The declaration's equal 2.0s durations and required receipt `duration_delta_s == 0.0` are the right control for the duration arm: with exact zero, the `duration_delta >= .020` arm cannot explain an acceptance. Require the receipt to show the generic `_alt` comparison actually used, and `centroid_relative_delta > .10`; then acceptance is attributable to the centroid arm for that recorded pair. A rounded display such as `0.10` cannot establish strictness. Record sufficient precision and compare the unrounded measured value, which must also be `< .13` per the preferred band.

Likewise, require each pair member's own format, duration, level, centroid-band, and loop-check failure lists to be empty. Passing ordinary checks rules out those **specified** checks as the reason for the outcome; it does not prove that all other waveform differences are absent. Require distinct file hashes to rule out exact byte identity, but do not treat hash inequality as perceptual distinctness.

The endpoint jump and endpoint-slope checks are narrow loop-boundary proxies. Clean values establish only that these measured boundary quantities meet their limits. They do not rule out other audible seams, internal modulation/repetition, or dissimilarity elsewhere in a waveform. The pure sine baseline/variant approach described for R37 is analytically loopable, but its clean seam does not make a centroid comparison a perceptual test.

## Centroid and near-boundary honesty

The project helper computes a magnitude-spectrum-weighted centroid across the whole waveform. This is one scalar summary, not a spectrum comparison. Distinct spectra can share a centroid, while a small centroid shift can occur with otherwise similar spectra; a centroid-only pass therefore neither proves broad spectral change nor perceptual novelty. Do not describe the `.10` predicate as a perceptual or universal dissimilarity threshold.

For the positive, report the full-precision helper outputs for both centroids, their exact baseline-relative calculation, both durations, hashes, ordinary/seam measurements and failure lists, the generic comparison record, and runner exit/receipt. The threshold is strictly `> .10`, not `>= .10`; if the measured number is equal to `.10`, below it, outside `< .13`, or only rounds above it, the declared positive has not been demonstrated. If tuning is needed, label each actual measured candidate a numeric fit attempt; label missing tools, wrong paths, malformed command invocation, or unavailable runner as setup failures instead. Do not imply either category where none occurred.

This is numerical control evidence only. No audition, audio-quality, production, rights, engine, publish, or promotion claim is supported or made.
