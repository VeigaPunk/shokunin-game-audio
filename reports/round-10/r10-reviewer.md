# Round 10 reviewer — minimal integration proposal

The declared depth claim is appropriately bounded: detect the decoded PCM sample jump at the `stem_layer` internal 2-second boundary. The relevant boundary in the existing 4-second, 48 kHz mono fixture is between samples 95,999 and 96,000 (zero-based), not the outer loop seam. `measure()` currently records only the first/last endpoint gap and endpoint slope difference; `section_contrast()` checks the 120 Hz amplitude contrast of the two halves but has no join-continuity measurement.

## Smallest measurement change

Add one nullable field to each applicable per-section result from `section_contrast()`, e.g. `internal_join_sample_gap_full_scale`, computed as `abs(samples[section_samples] - samples[section_samples - 1])` for the exactly-two-equal-sections layout. This is a decoded adjacent-sample magnitude difference, not integrated section energy, slope continuity, or a perceptual measure. Keep the calculation beside section sizing and leave the existing endpoint/slope metrics intact. For unsupported layouts, report null (or an explicit invalid layout result); do not invent an index. Gate only `stem_layer` on `<= 0.03` if the claim is specifically layer-join coverage; a broader gate would need an explicit rationale. The 0.03 value is a reused fixture-local bound, not an empirically calibrated audible threshold. Include the value in receipt thresholds only if it is actually used for the gate.

## Smallest probe branch

Add `--probe-layer-join` as a mutually exclusive mode. Generate a separate original PCM scratch WAV under `corpus/live/round-10/` from the same deterministic `stem_layer` construction, perturbing only the sample at/near index 96,000 enough to make the new gap exceed 0.03. Do not overwrite the canonical artifact. Measure it with the existing format, duration, peak/RMS, spectrum, outer endpoint/slope, and 120 Hz section-contrast logic, plus the new join metric. The intended isolated outcome is exactly the join-gap failure while all those existing checks pass; the branch should return the established probe failure exit only if that isolation is verified. If any other check fails, label it a failed fit rather than an isolated control. A single-sample modification is a plausible candidate, but its actual decoded metrics and sole-failure status require execution and independent replay, not assertion in this proposal.

Preserve canonical source hashes and all existing normal/flat30/flat120/slope/failing/invalid semantics. The receipt should identify the mode and scratch path and show the measured gap. No history rewrite or unrelated schema/threshold edits are needed.

## Scope boundary

This only measures the magnitude difference between two adjacent decoded PCM samples at one section boundary. It does not test waveform slope continuity at that boundary, runtime synchronization/adaptive engine behavior, click-free transitions, or audible quality. It makes no perceptual, engine, security, or production claim. No shell commands were run for this review.
