# Round 4 loop feasibility review

## Scope and evidence

The declared round-4 target is a new 4.0 s, 48 kHz mono PCM16 soundtrack loop, split into two 2.0 s sections. The candidate `corpus/live/round-4/stem_sections.wav` was not present when I reviewed the lane, so this is a measurable design recommendation, not a result for an artifact. No audio was borrowed, rendered, or listened to. I did not run shell commands.

The existing loop checks in `corpus/fixtures/measure_audio.py` operate on decoded mono samples and check only the full-file wrap: `abs(x[0]-x[-1]) <= 0.03` and `abs((x[-1]-x[-2])-(x[1]-x[0])) <= 0.001` FS/sample. Those indices correctly compare the incoming and outgoing first differences across the periodic boundary. They do not inspect the internal 2.0 s section boundary. Both bounds are local fixture rules, not audibility standards.

## Minimal feasible edge treatment

A small raised-cosine edge envelope is a simple way to make the full-loop wrap feasible without changing the two-section architecture. At 48 kHz, taper the first and last 20 ms (960 samples) smoothly to zero, using the same raised-cosine shape mirrored at both ends. The envelope should reach zero with zero endpoint derivative; do not use a linear fade. This makes the endpoint difference zero (or within PCM quantization) and makes the two boundary first differences very small. Verify the actual decoded PCM values against the exact `0.03` and `0.001` limits; do not infer a pass from the envelope formula alone. The 20 ms choice is a design starting point, not a validated universal duration. It minimally affects section energy relative to 2 s windows, but section contrast must still be recalculated after envelope and PCM16 quantization.

If the existing candidate already has compatible edge samples, make no edge change: measure first. If it misses either seam limit, use the same short smooth edge treatment and remeasure. Avoid adding a separate global normalization unless required by existing level bounds; normalization does not repair a seam ratio or slope discontinuity.

The full-loop check does not ensure a smooth transition at the 2.0 s section join. If the two sections are concatenated and that join is intended to be a transition, use a short (e.g. 20 ms) complementary smoothstep/cosine crossfade around the join, then preserve a total length of exactly 192,000 samples. Crossfading is optional if the section boundary is intentionally a sharp structural cut, but that choice must not be presented as a loop-seam result. Check boundary-local adjacent differences there as a separate descriptive measurement if desired; do not silently apply the full-loop thresholds as a declared requirement unless the round spec is amended.

## Checks to report on the candidate

For decoded PCM samples `x` of length 192,000, report:

- rate/channel/frame count and duration (expected 48,000 Hz, mono, 192,000 frames, 4.000 s);
- `endpoint_delta = abs(x[0]-x[-1])`;
- `slope_gap = abs((x[-1]-x[-2])-(x[1]-x[0]))`;
- full-file peak and RMS, plus the existing centroid/bandwidth and level-check outcomes;
- the two section windows `[0:96000]` and `[96000:192000]`, with the chosen component measurement stated (e.g., narrow-band RMS around a named frequency, identical filter/windowing for each section, and `20*log10(E2/E1)` where `E` is band-limited RMS). State the component, bandwidth/filter, and section-window convention. Reject/mark undefined if either measured energy is zero or below a declared floor; do not hide a silent denominator behind epsilon.

A sinusoid's phase need not itself be periodic over 4 s for the endpoint and slope tests to pass after edge shaping; likewise those tests alone say nothing about internal structure, encoded playback, or perceived seamlessness. Check the measured section contrast after all shaping and encoding to PCM16. This report only assesses numerical feasibility.
