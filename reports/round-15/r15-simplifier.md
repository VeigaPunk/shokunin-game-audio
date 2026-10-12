# Round 15 simplifier review

## Scope and evidence

Static review of the Round 15 declaration in `.shokunin/audio/LOG.md`, plus the current `corpus/fixtures/build_artifacts.py` and `measure_audio.py`, and the Round 13–14 simplifier guidance. I did not generate or measure a scratch WAV. No source, LOG, SCORECARD, canonical asset, or shared corpus file was edited. This report is the only file I wrote.

No shell command was run; there are no command exits or receipts to report.

## Reuse / minimal integration

- Reuse `section_contrast(path, component_hz=180)` for the new scratch. It already decodes the WAV once and reports section validity, 180 Hz component amplitudes/contrast, internal adjacent gap, and side-slope mismatch. Do not add a decoder, second section analyzer, or a new comparator.
- Reuse `measure(..., SPECS["stem_layer_alt"], path)` for generic format, duration, level, centroid band, and outer endpoint/slope checks. Keep the scratch out of `SPECS`, canonical assets, and `_alt` distinctness pairing.
- Builder currently has no `--probe-layer-alt-slope` option. Wire the opt-in generation through its existing parser/`main` path, making the original synthetic scratch in the assigned round-15 live directory based on the 180 Hz layer. Do not modify or rewrite the canonical WAV.
- Runner currently has no new mode. Follow the existing alt-probe plumbing consistently: argument/exclusivity check; builder invocation; scratch measurement; 180 Hz name selection and `sections` inclusion; internal gap and side-slope name lists; mode and receipt suffix. Add the new scratch name to the existing slope-check condition so the already-computed slope metric is judged. Reuse the existing `>.001` comparison and failure text; retain the existing `>.03` gap, 6 dB contrast, and validity behavior. No additional threshold or special-case failure suppression.
- Keep existing probe branches and normal-mode JSON behavior unchanged. A qualifying negative must have gap `<=.03` FS, valid 180 Hz contrast `>=6dB`, generic/outer checks passing, and only the existing side-slope failure (`>.001` FS/sample). If a fit trips centroid or any other gate, it is failed-fit evidence, not a slope-only negative.

The declaration's proposed `+0.0004` FS sample edit is a hypothesis, not evidence. Use the runner's decoded receipt for results; compare all twelve canonical hashes to the declared pre-round Git baseline during independent verification. Existing local bounds are reused, not newly established or calibrated.

## Limits

These checks establish only behavior of the deterministic synthetic fixture and this local measurement pipeline. They do not establish audible smoothness, a musical transition, engine behavior, security, external consumer compatibility, or production quality. No audible claim is made.
