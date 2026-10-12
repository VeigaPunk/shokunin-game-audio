# Round 16 simplifier review

## Scope and evidence

Static review of the Round 16 declaration in `.shokunin/audio/LOG.md` and current `corpus/fixtures/build_artifacts.py` / `measure_audio.py`. I did not run a shell command, generate or measure a WAV, or edit source, LOG, SCORECARD, canonical assets, or shared corpus data. This report is my only write.

## Reuse and narrow wiring

- Reuse `section_contrast(path, component_hz=180)`. It already decodes once and returns both section amplitudes, signed `20*log10(second/first)` contrast, validity, internal join gap and side-slope mismatch. A reversed `.050/.015` candidate should yield negative contrast and fail the existing `>=6.0 dB` comparison; do not create a second analyzer or a reverse-specific comparator.
- Reuse `measure(..., SPECS["stem_layer_alt"], scratch_path)` for format, duration, level, centroid band and outer endpoint/slope gates. The scratch should remain outside `SPECS` and not become an `_alt` distinctness pair.
- Add only an opt-in builder probe flag and its scratch generation in `live/round-16/`; add the corresponding runner argument, exclusivity/forwarding, scratch measurement, and section receipt plumbing. The new probe name must flow through the existing 180 Hz selection, section list, and internal-gap and side-slope check lists. Reuse the current `.03` gap, `.001` slope, `.01` amplitude-validity and `6 dB` contrast rules and existing failure reporting. No added constant or special-case acceptance logic.
- Existing probe invocations call the builder, whose normal build writes the canonical artifact files before writing a probe. Keep the probe out of canonical `OUT` and do not alter canonical synthesis. The deterministic rebuild is expected to reproduce the baseline bytes, but that is a property to verify, not assume: compare all twelve canonical hashes with `35d978c` after runs. Do not count a result if the hashes differ.
- The fit qualifies only if both section amplitudes/rms are valid, the reversed contrast is the sole failure, and generic/outer plus internal gap/slope checks pass. If synthesis introduces another failure, log it as a failed fit rather than broadening the gate.

## Limits

This is static wiring/safety guidance, not measurement or verification. It supports only a deterministic fixture test of the existing local numeric rule; it does not establish audible seamlessness, musical quality, engine behavior, external compatibility, or production suitability.
