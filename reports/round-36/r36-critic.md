# Round 36 critic — centroid/seam and zero-duration arm

Scope: numeric proxy falsification only. I did not audition or infer sound quality, perception, production, rights, engine, publish, or promotion status. No source, canonical artifact, LOG, SCORECARD, or other report was edited. This report is candidate analysis only; nothing here is canonical.

## Falsification attempt

The declared comparison is `duration_delta >= .020 OR centroid_relative_delta >= .10`; for two exactly 2.0 s files, the duration arm is necessarily zero, so the centroid arm is the sole route to `passed`. This is a real logical distinction from the recent unequal-duration cases, but it does not fix centroid's information loss: a single weighted-average frequency cannot distinguish spectra with the same mean, nor establish perceptual novelty.

Analytic adversarial pair: a 2-second 100 Hz sinusoid versus a 2-second equal-amplitude sum of 50 Hz and 150 Hz sinusoids. In the unquantized integer-cycle construction both have the same amplitude-weighted positive-frequency centroid (100 Hz), although their line-frequency distributions differ. Their endpoints and first-difference seam measures are not identity checks; both measure only the boundary samples/slopes. For the sampled PCM16-rounded construction, applying the project measure's whole-signal `abs(rfft)`-weighted centroid produced baseline **106.3529 Hz**, variant **108.9702 Hz**, relative delta **0.02461**, duration delta **0**. Both are inside 5–200 Hz, with peak **0.2000 / 0.1540 FS**, RMS **−17.0 / −20.0 dBFS** (approximately), endpoint delta **0.002625 FS** each, and side-slope mismatch **0** each. Thus both satisfy the stated level/band/seam bounds, yet the family distinctness OR would reject this changed line distribution: it demonstrates a false-negative limitation, not a passed comparison or an accepted fixture. PCM16 quantization and whole-signal centroid weighting explain the measured values not being exactly 100 Hz.

This test does not establish that a centroid delta >=10% will accept a perceptually unchanged pair, and I did not claim it does. A sufficient counterexample to *interpretation* is already mathematical: equal scalar centroids permit different spectral distributions. Seam endpoint and slope checks likewise do not establish a perceptually seamless loop or inspect interior discontinuities. Treat these as narrow numeric gates only.

## Setup / execution evidence

- No shell command, project measurement command, fixture builder, or fit was run. There is no shell exit code to report and no setup/fit failure. Values above came from in-memory NumPy construction and calculation, not a canonical fixture or project receipt.
- No artifacts were written by the experiment. The only file written is this report.

## Disposition

The zero-duration arm is correctly inactive for this declared equal-duration case; centroid is still a lossy scalar and seam checks are local boundary proxies. Do not infer sound/perceptual novelty, quality, readiness, rights, or any production/publishing status from these values. Parent integration and verification remain required.
