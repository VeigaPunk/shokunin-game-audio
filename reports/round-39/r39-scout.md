# R39 scout — denominator orientation and equal-duration ambience wiring

## Scope and inspection

Read the Round 39 declaration in `.shokunin/audio/LOG.md`, the Round 30 scout/declaration evidence, the Round 38 scout/declaration evidence, and inspected `.shokunin/audio/corpus/fixtures/measure_audio.py`. This is a source and prior-receipt map only. I did not generate audio, fit candidates, run the measurement helper/runner, or edit source.

No shell commands were run, so there are no shell command exits or new receipts. I used Python file reads to inspect the named files.

## R30 denominator orientation: measured strict split

The R30 declaration records the existing `_alt` calculation as `abs(variant_centroid - baseline_centroid) / baseline_centroid`; distinctness passes if duration delta is at least `.020` seconds **OR** that baseline-relative centroid delta is at least `.10`. Source inspection of the current runner confirms the same wiring: each `_alt` name maps to `measurements[name[:-4]]`; the ratio denominator is `base["spectral_centroid_hz"]`; `passed = duration_delta >= .020 or centroid_relative_delta >= .10`. It is not a symmetric denominator.

R30 used the same two waveforms in swapped roles. Recorded project-measured centroids and outcomes are:

| Role assignment | Baseline → `_alt` centroid (Hz) | Duration delta | Measured ratio | Result |
|---|---:|---:|---:|---|
| Forward, higher baseline | 966.8966593379727 → 871.155504521436 | 0.0 s | 0.09901901500217196 (< .10) | Expected negative: sole `_alt` distinctness failure, exit 1 |
| Reverse, lower baseline | 871.155504521436 → 966.8966593379727 | 0.0 s | 0.10990133715464667 (> .10) | Expected positive: passes, exit 0 |

The R30 author receipts and corrected non-author replay reported those same strict split values, exact byte identity after role swap (forward-base SHA equals reverse-`_alt`; forward-`_alt` SHA equals reverse-base), and clean ordinary UI checks. Thus the observed polarity follows which measurement occupies the baseline role for this fixed pair. It is not evidence of a universal or perceptual boundary.

R30 setup issue, separate from evidence: initial executor relative-path invocation exited 1 and was corrected; the initial non-author wrapper attempt yielded 28 exit-127 setup errors and no receipts. Those attempts were excluded; corrected replay provided 28 receipts. They are setup failures, not measured gate outcomes.

## R38 equal-duration ambience wiring and measured control

R38 added an opt-in above control beside R37’s below control, routed through the existing generic `_alt` comparator. The source measures the scratch pair explicitly with `(2.0, 5, 200, True)` (2-second target, centroid band 5–200 Hz, loop checks enabled) and retains the same generic duration-or-centroid rule; no family comparison or threshold change was needed. Both declared modes use 48 kHz mono PCM16 looping source-generated files.

Recorded non-author R38 positive receipt measured 2.0-second equal-duration files (delta exactly `0.0` s), centroids `91.03372963003302` and `81.6243985667145` Hz, and baseline-relative delta `0.10336093117966988` (> .10). Ordinary and loop failure lists were empty; the generic `_alt` passed on centroid alone. R37’s recorded negative was 60/64 Hz source tones, measured centroids `67.37182625964924` and `71.80863982343814` Hz, duration delta `0.0` s and relative delta `0.06585562259644766`; its sole distinctness failure produced expected exit 1. Together these are local opposite-polarity ambience controls, not an orientation test.

R38 numeric unsuccessful fits, separate from setup: executor’s 12/36 Hz plus `.05*60 Hz` candidate measured `0.1264765508` (inside its then-declared above band); 60/64 Hz measured `0.0658556`, and reported 151 Hz single-tone sweep/other multi-tone attempts did not reach the declared target. An attempted `.070`-amplitude later candidate measured `0.14123783252085534`, outside the declared `< .13` band. These are failed candidate fits, not runner failures or R39 evidence. R38 also had an initial helper-path error and a verifier wrapper attempt exiting 127 without receipt; corrected runs were used.

## R39 implication and limit

R39 is a separate test: use one equal-duration 2.0-second looping ambience pair with clean ordinary/seam checks and distinct hashes, selected by **project-measured** centroid floats such that lower-centroid baseline A → higher-centroid `_alt` B satisfies `abs(B-A)/A > .10`, while the swapped roles satisfy `abs(B-A)/B < .10`. The forward mode should pass and reverse should fail solely at distinctness, both duration deltas exactly zero. R30 establishes the denominator mechanism and demonstrates such a strict split for another measured pair; R38 establishes the ambience scratch routing and equal-duration controls. Neither alone nor together proves the R39 pair or its runner modes. I made no R39 fit or run, so there are no R39 measured split values, fit failures, setup errors, or outcome receipts to report.

Claim limit: numerical comparator orientation only. This report makes no audition, perceptual, audio-quality, production, rights, engine, publishing, or promotion claim. No constants, thresholds, canonical assets, or source files were changed.
