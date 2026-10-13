# Round 38 reviewer — minimal opt-in scratch design

## Recommendation

Use one opt-in `--probe-ambience-centroid-above` path that builds two scratch-only 2.0-second, 48 kHz mono PCM16 loop files under `corpus/live/round-38/`, measures them with local specs `(2.0, 5, 200, True)`, and feeds their two results through the runner’s existing generic `_alt` distinctness loop. Keep canonical `SPECS`, the 17 canonical WAVs, thresholds, generic comparison code, and family comparisons unchanged. Do not create a new family record or make any canonical additions.

Use local names `ambience_probe` and `ambience_probe_alt`; `_alt` stripping resolves the baseline in the generic path. Generate source-controlled waveforms with equal sample counts and identical duration, then fit coefficients/frequencies empirically against `measure()`'s project centroid. The acceptance interval is strictly `0.10 < centroid_relative_delta < 0.13` (not a coefficient ratio or nominal-frequency estimate). Require distinct file hashes, exact measured duration delta `0.0`, and empty ordinary format/level/centroid-band and loop-seam failures for both files. Only the variant should have no generic distinctness failure and runner exit 0. Receipt should label `probe-ambience-centroid-above`, include both scratch measurements and generic distinctness, plus the unchanged canonical results and threshold receipt.

## Setup versus numeric result

A missing tool/file, generation or decode error, invalid format, ordinary/seam failure, hash collision, unequal measured duration, or a measured centroid outside the strict interval is setup/fit failure; it does not count as a threshold result. Report fit attempts and their measured values separately. A valid numeric positive requires all setup checks above and the generic `_alt` result passing with its centroid arm true; do not adjust the `.020 s OR .10` constants to obtain that outcome. Since durations are equal, the duration arm must be false and only the centroid arm can explain the pass.

This is one local equal-duration positive control paired with Round 37’s selected negative at relative delta `0.06585562259644766`. It is not an exact-boundary or universal calibration. No audition, perceptual similarity, audible seamlessness, quality, production, rights, engine, publishing, or promotion claim is supported.

## Commands and exits

No shell commands were run for this review. I read the Round 38 LOG declaration and inspected the existing builder/runner source in Python; this is a design review only. No waveform fit or numeric outcome is claimed.
