# Round 11 reviewer — smallest section-result and probe branch

## Recommendation

Add one field to each existing `sections` record:
`internal_join_slope_mismatch_full_scale_per_sample`. For the existing 96,000-frame split, compute the left slope as `samples[95999] - samples[95998]`, the right slope as `samples[96001] - samples[96000]`, and record the absolute difference. This is a local adjacent-slope comparison across frames 95998–96001, not a general derivative or perceptual smoothness measure. Existing join-gap and section-contrast fields remain unchanged.

Gate the new field only for `stem_layer` and the new `slope_probe` with strict `> .001`, using the existing outer slope bound as a fixture-local comparator. Append a distinct failure such as `sections: internal join slope mismatch > .001 full scale per sample`; do not alter the outer endpoint/slope checks or gate other section records. Add the threshold to the receipt thresholds. The selected probe must have join gap `<= .03`, 120 Hz contrast passing, and all generic/outer rules passing, with this new rule as its only failure. If not, report failed-fit rather than isolated evidence.

## Minimal reuse / branch shape

The current `measure()` and `section_contrast()` each decode via SoX. Avoid a second decode for section-bearing assets by having `main()` decode each relevant path once to a float64 sample array, then pass that same array to both `measure(..., samples=...)` and `section_contrast(..., samples=...)`. Keep the existing standalone helper behavior only if needed by `invalid_probes()`; that path can continue to decode itself. Calculate the new field inside the existing `section_contrast()` result from its supplied samples, alongside the existing internal gap, so there is one section split and one source of join indexing.

For the new CLI mode, mirror the existing layer-join branch narrowly: add `--probe-layer-slope`, reject combinations with other probe modes, have the builder write an original analytic `live/round-11/slope_probe.wav`, measure it as the extra `slope_probe` entry, include it among 120 Hz section records, gate its internal slope mismatch, and name its mode/receipt suffix `probe-layer-slope`/`-layer-slope`. Reuse decoded `stem_layer` for the normal section record and decoded scratch candidate for `slope_probe`; do not regenerate/redecode either to compute section metrics. Preserve the existing `--probe-slope` round-3 semantics separately.

## Scope and caveats

This is an implementation proposal only; I did not run shell commands or inspect a candidate waveform. The `.001` value is inherited fixture-local policy, not empirically calibrated. No claim about audible smoothness/clicks, engine timing, security, production, or general audio quality follows. Eleven canonical hashes, four variants, and prior controls still require replay by the integrating parent and independent verifier.
