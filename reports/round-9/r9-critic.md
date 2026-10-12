# Round 9 critic — `r9-critic`

## Verdict

The declared move is a reasonable *receipt-semantics disclosure/schema* change, but the evidence described in the LOG does not support calling it numeric calibration. It can improve auditability by making each section’s frequency explicit and labeling the computed contrast as amplitude dB. It neither calibrates thresholds nor establishes that their numerical values are appropriate. Keep the claim bounded to semantics/auditability; do not imply measured calibration improvement.

## Scope and backward compatibility

The current `measure_audio.py` source has a global receipt `thresholds.section_component_hz: 30`, while section results carry their own `component_hz` (30 for `stem_sections`/`flat30_probe`; 120 for `stem_layer`/`flat120_probe`). The function emits `section_energy_delta_db` using `20*log10(amps[1]/amps[0])`; that is component-amplitude contrast, not integrated section energy. These are genuine naming/placement ambiguities.

However, renaming a JSON key and removing the top-level field is a breaking receipt-schema change for any consumer that reads either key. A search of this repository found those strings in the producer, LOG/SCORECARD/knowledge/reports, and historical receipt JSON; it did not identify an in-repository downstream parser. That is not evidence that no consumer exists outside this checkout. The round-9 declaration's "no compatibility assumptions" needs to mean *no promise of compatibility*, not proven compatibility or consumer absence. Do not add a dual-key shim unless compatibility is an explicit requirement; instead call out the schema break and migration mapping, and retain historical JSON unchanged as declared.

The migration note should define the new result path precisely (e.g. `sections.<name>.component_amplitude_contrast_db`) and distinguish it from any similarly named measurement fields. Document `section_energy_delta_db` → `component_amplitude_contrast_db`; explain that historical receipts retain the old key and readers must handle old/new schemas if reading mixed history. Removing the top-level frequency means a consumer must read each `sections.<name>.component_hz`; it cannot infer the frequency from the fixture name or a hard-coded 30 Hz default.

## Evidence needed for the declared numeric-invariance claim

The source-level transformation should be limited to output key/metadata placement; preserve the same samples, section selection, FFT bin, validity floors, `20*log10(A2/A1)` calculation, 6 dB comparison, and failure behavior. Evidence should compare before/after values by measurement name and mode, not merely show that the new run passes. In particular compare the old `stem_sections` and `flat30_probe` values at 30 Hz and `stem_layer` and `flat120_probe` values at 120 Hz, including the flat control's sole contrast failure. Confirm old ten canonical measurement hashes and threshold literals are unchanged, and report exact numeric before/after deltas (zero to stated serialization precision). A clean 11-measurement receipt alone does not prove invariance.

Historical round-8 receipts and the LOG document examples (normal layer: 13.979372 dB at 120 Hz; matched flat120: 0 dB), but they are before-state examples, not after-state comparisons. The independent replay and old-hash check are still necessary. No evidence here establishes calibration quality, threshold sensitivity near 6 dB, or generality beyond these authored fixtures.

## Constraints / non-claims

No perceptual, engine/runtime, security, or production conclusion follows from this metadata/key rename. Numeric invariance would support only that the same deterministic fixture measurements and pass/fail decisions were retained under a clearer receipt schema. It does not establish compatibility with external consumers, nor validate threshold constants.

## Inspection record

Read the round-9 declaration in `.shokunin/audio/LOG.md`, inspected `corpus/fixtures/measure_audio.py`, the threshold-calibration knowledge note, and searched repository text for the old/new schema names. No shell command was run. This is source/report review only; no source, receipt, LOG, SCORECARD, canonical, or commit files were changed.
