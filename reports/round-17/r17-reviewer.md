# Round 17 reviewer — minimal 200 Hz third-layer wiring

## Recommendation

Add `stem_layer_third.wav` as one additional canonical fixture, not as an opt-in probe. Use the existing two-section 4 s recipe shape and `save`/`SPECS`/`measure`/`section_contrast` path. Keep the existing 120 Hz `stem_layer` and 180 Hz `stem_layer_alt` definitions and all probe modes intact.

The smallest coherent source change is:

1. In `build_artifacts.py`, beside the existing two layer `save` calls, synthesize `np.where(t < 2, .015, .050) * np.sin(2*np.pi*200*t)` and save it under the canonical name `stem_layer_third`. This produces the requested 200 Hz component and section amplitude step without changing either old sample stream. No probe flag is needed for a new canonical fixture.
2. In `measure_audio.py`, add `"stem_layer_third": (4.0, 100, 2000, True)` to `SPECS`. Add `stem_layer_third` to the section measurement selection and map it to 200 Hz in the existing component-frequency expression. Add it to the existing internal-join gap and side-slope eligibility checks. Reuse the current 6 dB, .03 FS and .001 FS/sample rules; do not add thresholds or a second measurement implementation.
3. Leave the existing `_alt` distinctness loop untouched: this new name has no matching `_alt` pairing and is not a variant. Existing `stem_layer`/`stem_layer_alt` names, measurements, option flags, and failure modes should remain byte-for-byte behaviorally stable. The receipt naturally gains one canonical measurement and one section entry; do not rename or reinterpret existing receipt fields.

One code clarity option, if the explicit frequency expression becomes hard to maintain, is a small local mapping from section-fixture names to component frequency. It should replace (not duplicate) the nested conditional, and preserve the current mappings exactly: 30 Hz for `stem_sections`/`flat30_probe`, 120 Hz for the existing 120 Hz layer cases, 180 Hz for the existing 180 Hz cases, and 200 Hz only for `stem_layer_third`. This refactor is optional; explicit minimal additions are lower risk.

## Review and evidence boundary

Inspected the round-17 declared coverage spec in `.shokunin/audio/LOG.md` and current `build_artifacts.py` / `measure_audio.py`. I ran no shell commands, so there are no command exit codes or measurement results to report. In particular, the requested waveform is a proposed recipe, not a measured passing candidate. The 200 Hz centroid, decoded format/level, outer seam, internal join, section contrast, distinct canonical hash, and preservation of old mode receipts all require execution and independent verification. If this recipe fails a gate, report that fit and adjust source synthesis only; do not loosen a gate.

This is only a minimal fixture/measurement wiring recommendation. It supports no audible, engine, adaptive, or production claim.
