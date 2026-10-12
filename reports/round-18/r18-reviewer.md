.shokunin/audio Round 18 — reviewer

## Recommendation
Add one opt-in `--probe-layer-third-slope` mode to the fixture builder and runner. Keep the candidate scratch-only under `corpus/live/round-18/`; do not add it to `SPECS`, canonical artifacts, or normal measurements. Reuse the existing 200 Hz section analysis and the existing generic format/duration/level/centroid/outer-seam checks.

## Minimal wiring
- Builder: accept/thread one boolean flag. Read `artifacts/stem_layer_third.wav` as little-endian signed PCM16, copy frames, add **8 integer counts** to frame 96001 (the hypothesis is 43→51), and write mono/16-bit/48 kHz `live/round-18/slope200_probe.wav`. Do not synthesize a new tone or mutate the canonical input.
- Runner: add the opt-in flag and invoke the builder with it. Measure that path using `SPECS["stem_layer_third"]`; include the probe result in the receipt and failure aggregation. Add its section entry with component 200 Hz, and subject it to the same section contrast, internal adjacent-gap, and internal side-slope checks as `stem_layer_third`. Generic and outer-seam checks already run via `measure`. Record the mode and a unique `-layer-third-slope` receipt suffix, following existing opt-in patterns.
- Make no numeric threshold, other mode, normal-mode measurement, or canonical WAV change. A measured failure remains a failing receipt (runner exit 1), not a setup failure; the hypothesized single side-slope failure must be established by the receipt, not assumed from the proposed +8 edit.

## Evidence and limits
Read `.shokunin/audio/LOG.md`, `corpus/fixtures/build_artifacts.py`, and `corpus/fixtures/measure_audio.py`. Source shows `stem_layer_third` mapped to 200 Hz, and `section_contrast` already computes amplitude validity/contrast, adjacent join gap, and side-slope mismatch. The measurement function already applies the standard decoded format, duration, level, centroid-band, and outer seam checks. Current section-failure plumbing explicitly enumerates eligible names, so the new probe name must be added to those applicability checks; otherwise the new receipt would silently omit a gate.

No shell commands or candidate measurements were run for this reviewer role; no result is claimed for +8 or any audio behavior. No audible, engine, or production claim.
