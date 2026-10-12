# Round 8 reviewer — minimum integration proposal

## Review scope

I read the round-8 claim in `.shokunin/audio/LOG.md` and inspected `corpus/fixtures/build_artifacts.py` and `corpus/fixtures/measure_audio.py`. I did not edit shared code or run shell commands (therefore no shell exit codes). This is an integration proposal, not evidence that the candidate passes.

## Minimum builder/measure integration

- Keep the existing ten canonical fixture recipes and names intact. Add one deterministic original `stem_layer.wav` recipe on the same four-second, 48 kHz, 192,000-frame time grid as `stem_sections.wav`. A continuous 120 Hz sine with amplitude `.012` for samples `[0:96000]` and `.060` for `[96000:192000]` matches the declared contrast claim. Since four seconds contains an integer number of 120 Hz cycles, it also naturally supports the existing endpoint/slope checks. Do not copy or mix samples from the companion fixture; generate the layer analytically.
- Add `stem_layer` to the measurement specs with duration `4.0`, centroid band `100–2000 Hz`, and the existing loop checks. Its measured level/centroid/format/seam should use the existing `measure()` path, not new gates.
- Generalize the existing `section_contrast(path)` narrowly with a `component_hz` parameter defaulting to 30. Preserve its existing 30 Hz call/results for `stem_sections` and `flat30_probe`; for the new layer use 120 Hz. On each 96,000-sample half, use the exact bin `component_hz * section_samples / sample_rate` (240 for 120 Hz) and retain the existing amplitude floor, RMS floor, and >=6 dB section ratio rule. This reuses the local two-section method rather than adding another checker. The computed ratio is component **amplitude** ratio; consider naming its JSON field accordingly rather than calling it energy delta.
- Add `--probe-layer-flat` as a separate probe mode. Generate only the matched scratch flat120 control (`.036` amplitude in both halves) under `live/round-8/`; measure it with the same 120 Hz section check. The intended result is a valid control near 0 dB that fails only the section-contrast criterion. Do not include it among canonical assets.
- Normal mode should build and measure eleven canonical WAVs, include a 120 Hz section receipt for `stem_layer`, and preserve the ten pre-round hashes and four SFX distinctness checks. The flat-layer mode should not alter the existing flat30/slope/failing/invalid mode behavior or their controls.

The cleanest small change is a parameterized existing section checker plus one call site for the new frequency. Avoid a second near-duplicate FFT routine, generic validation/catch logic, threshold tuning, and unrelated schema or fixture changes. Ensure the per-section amplitude receipt reports `[approximately .012, .060]`, and the matched flat control reports equal sections; values may differ slightly from PCM16 quantization.

## Scope limits

These checks support only a source-generated, synchronized numeric companion layer and this exact-bin amplitude-contrast proxy. They do not establish adaptive engine behavior, mix quality, audible transitions, perceptual suitability, or loop seamlessness in playback. A small endpoint/slope delta is a numeric fixture check, not an audibility conclusion. The declared threshold retains its fixture-local meaning.
