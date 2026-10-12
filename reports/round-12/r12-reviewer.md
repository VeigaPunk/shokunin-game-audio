# Round 12 reviewer: minimum integration proposal

## Scope and evidence

Reviewed `corpus/fixtures/build_artifacts.py`, `corpus/fixtures/measure_audio.py`, and the round-12 declaration in `LOG.md`. No shell commands were run, no fixture was generated, and no source, declaration, scorecard, canonical artifact, or commit was changed. This is a source-integration proposal, not verification of a candidate. I did not listen to audio or make engine, security, production, or perceptual claims.

## Minimum source change

Add one original analytic 4.0 s, 48 kHz mono PCM16 artifact, `stem_layer_alt.wav`, as a 180 Hz section-varying companion to `stem_layer.wav`. The declared `.015/.050 * sin(2*pi*180*t)` is only a candidate recipe; accept it only if decoded measurements fit every existing applicable check. It is analytically distinct from the 120 Hz layer, uses no external sample, and leaves all existing waveform recipes intact.

Keep the change narrowly additive:

1. Add `stem_layer_alt` to `SPECS` with the existing layer specification `(4.0, 100, 2000, True)`.
2. In the builder, save the new 180 Hz two-half signal under that name. Do not replace or derive it from the existing canonical layer; preserve both original recipes.
3. Include `stem_layer_alt` in the existing `section_contrast` dispatch at 180 Hz and in the sections result selection. The per-record `component_hz` remains the frequency source of truth; do not reintroduce a top-level section-frequency constant.
4. Apply the existing internal-join adjacent-gap and side-slope gates to `stem_layer_alt`, just as for `stem_layer`, reusing `.03` and `.001` respectively. Do not add thresholds. The section contrast continues to use the existing exact-bin estimator, amplitude floor, RMS floor, and 6 dB minimum.
5. Let the existing `_alt` distinctness loop compare `stem_layer_alt` with `stem_layer`. It already computes decoded duration and centroid differences. Confirm the actual generated alternate passes that criterion; do not assume the 180 Hz source frequency alone makes it pass.

This should add one artifact and one measured section record while retaining the 120 Hz layer and the four existing SFX variants. Check that the new signal meets the existing 100–2000 Hz centroid band, outer endpoint/slope checks, levels, and duration, in addition to the distinctness and section checks. The candidate formula is not accepted absent those measurements.

## Compatibility and validation checks for the integrating author

Keep old command-line modes and their existing scratch inputs, receipt names/modes, and gates unchanged. The new canonical artifact is included in normal generation/measurement; do not change old historical JSON or old control recipes. Specifically test:

- Normal mode succeeds and reports 12 canonical WAVs, `stem_layer_alt` at 180 Hz, a passing layer distinctness result, and all applicable generic/outer/internal/section checks.
- The existing negative controls retain their documented expected exits and sole-failure meanings: `--probe-layer-slope`, `--probe-layer-join`, `--probe-flat`, `--probe-layer-flat`, `--probe-slope`, `--probe-failing`, and `--probe-invalid`. Finish with normal restore.
- Compare hashes for the previous 11 canonical artifacts against the pre-round-12 baseline. They should be unchanged; record the new artifact's hash separately.
- Independently decode and measure the candidate; do not treat a builder-authored receipt alone as verification. Keep any rejected candidate and failure telemetry in the round-12 scoped scratch/report, not canonical artifacts.

I did not run these commands, so there are no command exits or receipts to report. A failed fit should be reported as a failure, not hidden by tuning or claiming the proposed values passed. This coverage change can show only source-generated synthetic measurement coverage; it cannot show audible distinction, adaptive playback, or production suitability.
