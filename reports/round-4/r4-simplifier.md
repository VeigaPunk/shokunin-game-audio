# Round 4 simplifier: smallest builder/measure integration

## Recommendation

Keep the existing `build_artifacts.py` and `measure_audio.py` as the only fixture builder and measurement path. Add one generated fixture (`stem_sections.wav`) and one named section-contrast check; do not add a separate analyzer, fixture registry, or framework.

### Builder

Add a deterministic `stem_sections` construction to `main()` and save it through existing `save()`. Make it four seconds at 48 kHz, with section A and B each exactly 96,000 samples. Use an explicit shared synthesis helper or direct sample slices so the target-component change is intentional and reproducible. Keep all existing fixture generation untouched. For the flat control, add one `--probe-flat` switch that writes `flat_probe.wav` under `live/round-4/`: its two sections should be copies of the same section (or otherwise have equal target-component ratios), so it retains duration/format/level/seam properties while removing only the claimed contrast. Avoid a new output mode if builder can write this one probe alongside normal fixtures without changing canonical files.

### Measurement

Add `stem_sections` to `SPECS` as a 4.0-second looped stem with the existing stem centroid band (100–2000 Hz). Reuse `measure()` for all current and new general checks. Add a small helper for the one section proxy: on the already decoded `sox` float samples, split at the exact midpoint; compute each section's 220-Hz component power by projecting onto sine/cosine at 220 Hz (the 2-second sections contain an integer number of cycles), divide by that section's total mean-square power, then report the two ratios and their dB difference. Reject zero/near-zero denominators explicitly. State the sign convention, e.g. `abs(10*log10(ratio_B/ratio_A)) >= 6 dB`; for a directional design, report signed delta and require the declared direction. This is a fixture-local proxy, not motif recognition or a musicality judgment.

Run the same proxy on `flat_probe.wav` and fail the probe expectation if its absolute contrast is below 6 dB (or, equivalently, verify it fails the canonical contrast criterion); keep its regular loop and format checks. Put the proxy values, threshold, and probe result in the existing JSON receipt. Do not weaken or replace the existing endpoint/slope guards or distinctness checks. A special-case `stem_sections`/probe check in the current measurement script is smaller and clearer than generalizing `SPECS` into a new framework.

## Why this is the minimum

The current script already owns decoded-PCM inspection, per-fixture checks, probe modes, and JSON receipts. One fixture spec, one narrowly named helper, and one probe mode exercise the claim using that same route. The 220-Hz projection is exact for the declared two-second sections, while normalization by section power makes the result relative rather than just a loudness change. A duplicated section is a direct flat negative control. This proposal does not establish audible structure, engine behavior, or production suitability; it only measures the declared analytic property.

No shell commands were run.
