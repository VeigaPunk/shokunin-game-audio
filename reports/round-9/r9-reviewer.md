# Round 9 source review — reviewer

## Scope and declared claim
Reviewed `.shokunin/audio/corpus/fixtures/measure_audio.py` read-only against the Round 9 claim in `.shokunin/audio/LOG.md`. I did not run shell commands or edit source, receipts, LOG, SCORECARD, canonical artifacts, or commits. This is a source/contract review only—not a claim about perception, engine behavior, security, or production.

The current source matches the stated ambiguity: `section_contrast()` already emits a per-section `component_hz`, but calls its signed `20*log10(A2/A1)` result `section_energy_delta_db`. Separately, receipt `thresholds` hard-codes `section_component_hz: 30`, although the section dispatch passes 120 for `stem_layer`/`flat120_probe` and 30 for the original stem/control.

## Intended after-state receipt contract

For newly generated receipts only:

- `sections.<name>.component_hz` remains the sole frequency declaration for that measured section.
- Rename `sections.<name>.section_energy_delta_db` to `sections.<name>.component_amplitude_contrast_db`. Preserve the exact existing float, sign, `20*log10(A2/A1)` computation, null-on-invalid behavior, and pass/fail decisions.
- Remove `thresholds.section_component_hz`; do not substitute another top-level copy of per-section values. Retain all actual thresholds, including the 6 dB minimum and amplitude/RMS floors, unchanged.
- Keep `component_amplitudes_full_scale`, `section_rms_full_scale`, `section_samples`, `valid`, `passed`, and failure categorization unchanged. The empty/invalid-length return must have the same new result key, with `None`.
- Do not rewrite archived JSON. Document the mapping for consumers: old `sections[*].section_energy_delta_db` → new `sections[*].component_amplitude_contrast_db`; old `thresholds.section_component_hz` is removed, and per-section `component_hz` is authoritative. Historical receipts remain historical schema.

## Minimal source edit recommendation

Within `section_contrast()`, change only the result-key spelling in both return dictionaries (invalid sample count and normal calculation). In the receipt `thresholds` literal, delete only the `section_component_hz: 30` entry. No formula, dispatch, threshold, mode, failure message, measurement, or fixture needs changing. The existing `component_hz` in each section result already supplies the needed frequency; the current calls for 30/120 should remain as-is. Update the knowledge/schema documentation separately to state the field mapping and historical boundary, without mass-editing old receipts.

## Review risks / verification boundary

The rename is intentionally a receipt schema change and may break consumers that read the old key; do not silently emit both names, since that preserves ambiguity and violates the declared single-source-of-truth contract. Verify generated normal, flat30, and flat120 receipts use only the new field and omit the top-level frequency; compare numerical values against the corresponding prior receipts, and verify mode/failure outcomes and all unrelated threshold literals are unchanged. This report makes no such runtime replay claim. No shell commands were run, so there are no command exit statuses to report.
