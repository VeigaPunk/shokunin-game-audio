# r9-scout — receipt schema and read-site map

Scope: inventory only; no source edits or receipt rewriting.

## Before-state implementation

At `aaf4801` (`Audio round 8: final coverage report`), `corpus/fixtures/measure_audio.py` defines `section_contrast(path, component_hz=30)` (lines 83–100). For a 192000-sample input it splits into two 96000-sample halves, computes the unwindowed FFT bin `component_hz * 96000 // 48000`, measures each component amplitude as `2*abs(rfft[bin])/96000`, and stores signed `20*log10(A2/A1)` under `section_energy_delta_db`. Thus the value is component-amplitude contrast in dB, not integrated section energy. For bad sample count, same key is null and `failure_kind` is `section count`.

The generated receipt has a top-level `thresholds.section_component_hz: 30`; it is misleading for 120 Hz layer checks. Actual frequency is selected by call site and appears under each section result as `component_hz`: 30 for `stem_sections`/`flat30_probe`, 120 for `stem_layer`/`flat120_probe`. `section_contrast_min_db: 6.0`, amplitude/RMS floors, and all other threshold constants are independent of these labels.

## Consumers and related references

- Producer: `measure_audio.py` writes `thresholds.section_component_hz: 30` only while assembling the receipt in `main()`; it is a fixed literal, not derived from measurement calls. No source code reads that top-level key. `section_contrast()` produces `sections[*].component_hz` plus `section_energy_delta_db` in both the wrong-sample-count and normal-result branches. The actual frequency is passed by the caller (default 30 Hz; 120 Hz for layer/flat120). Thus the per-section frequency is the producer's actual measurement metadata; the top-level value has no corresponding read site.
- Runtime consumers of the returned section object: `main()` appends a failure based on `result["passed"]` and uses `result["component_hz"]` in failure text. `invalid_probes()` reads `failure_kind` for the short/odd section-count probes. No source code reads `section_energy_delta_db`; it is emitted for receipt inspection only. No repository Python consumer of either old schema key was found.
- Historical generated JSON under `corpus/live/runs/**/measurements.json` contains the old names; these are immutable historical evidence and should not be rewritten.
- Human-facing current documentation: `corpus/knowledge/2026-10-12-fixture-battery.md` explicitly discloses both ambiguities; `LOG.md` records round-8 caveats and declares r9 schema rename; `SCORECARD.md` mentions both old fields; round-8 reports and `.shokunin/reports/round-8/audio.md` cite them as historical findings. These reports describe the old receipts and should retain their historical wording.
- `corpus/knowledge/2026-10-12-threshold-calibration.md` explains the section formula under threshold semantics; check/update only if its literal old field label is presented as current schema.

Search performed with exact shell command `git grep -n -E 'section_energy_delta_db|section_component_hz' -- . ':!*.json'` (exit 0). Outside `measure_audio.py`, direct mentions are explanatory round-8/round-5 historical prose and knowledge docs; no consumer depends on the old machine key.

## Minimal integration implications

For newly generated receipts only: remove `thresholds.section_component_hz`; retain per-section `component_hz` as the sole frequency source; rename `section_energy_delta_db` to `component_amplitude_contrast_db` in both valid and invalid section results, keeping the signed `20*log10(A2/A1)` calculation and all acceptance rules unchanged. Document explicit old→new key mapping and historical JSON boundary. Do not add an alias/compatibility shim or rewrite archived receipts. Round-5 reports' statement that dB amplitude ratio is equivalently energy-ratio dB is mathematically true, but doesn't alter that the value is not integrated section energy; retain as historical rationale, clarify current output semantics rather than retroactively edit old findings.
