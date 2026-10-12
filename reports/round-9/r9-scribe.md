# Round 9 migration mapping draft — r9-scribe

## Decision table

| Receipt location / meaning before | Proposed after-state | Migration treatment |
|---|---|---|
| `thresholds.section_component_hz: 30` | Remove this misleading global frequency entry. Each `sections[name].component_hz` is the authoritative measured component frequency (30 for `stem_sections`/`flat30_probe`; 120 for `stem_layer`/`flat120_probe`). | New receipts only; do not rewrite historical JSON. Frequency is per result, not a universal threshold. |
| `sections[name].section_energy_delta_db` | `sections[name].component_amplitude_contrast_db` | Preserve exact signed `20*log10(A2/A1)` calculation, units dB, and numeric value; change the key only. |
| `sections[name].component_amplitudes_full_scale` | Same key | Amplitudes remain the inputs to the contrast; they are not integrated section energies. |
| `sections[name].section_rms_full_scale` | Same key | RMS validity data remain distinct from the single-frequency component contrast. |
| Historical receipts with old names | Remain byte-for-byte historical records | Readers comparing generations must use explicit mapping above; no silent rewrite or compatibility alias is proposed. |

This is a disclosure/schema migration, not calibration or threshold tuning. Keep the `component_amplitude_contrast_db >= 6.0` acceptance rule and all numeric calculations unchanged. The top-level `thresholds` object still carries genuine common thresholds (for example `section_contrast_min_db` and component amplitude floor); do not move those to per-section frequency metadata.

## Read-only evidence inspected

The round-9 declaration in `.shokunin/audio/LOG.md` defines this as a calibration/auditability claim: eliminate the ambiguous top-level frequency, rename the result field, preserve values, and do not rewrite historical receipts. Source inspection of `corpus/fixtures/measure_audio.py` confirms `section_contrast(path, component_hz=30)` returns per-result `component_hz`, component amplitudes and `section_energy_delta_db` computed as `20*np.log10(amps[1]/amps[0])`; the receipt also independently writes top-level `thresholds.section_component_hz: 30`. Normal/probe receipts inspected:

| Mode / receipt (existing) | Section | `component_hz` | Old contrast key value (dB) | Amplitudes FS |
|---|---|---:|---:|---|
| normal `172620813098Z-normal` | `stem_sections` | 30 | 13.979508033945462 | .011999465108689048 / .05999807118785472 |
| normal `172620813098Z-normal` | `stem_layer` | 120 | 13.979372282981668 | .011999587449951306 / .05999774519524399 |
| flat30 `172638021452Z-flat` | `flat30_probe` | 30 | 0.0 | .0359986154757334 / .0359986154757334 |
| flat120 `172637297691Z-layer-flat` | `flat120_probe` | 120 | 0.0 | .035997209705667964 / .035997209705667964 |

Both probe receipts also contain the normal sections and show top-level 30, even when a 120-Hz result is present. This supports the ambiguity diagnosis and demonstrates why the per-section value must be authoritative; it does not itself verify a post-migration implementation.

## Caveats / boundaries

- “Energy” is inaccurate here: this is a signed ratio of one projected component's amplitudes using `20 log10`, not integrated section energy, total mix energy, loudness, or RMS ratio. Preserve the sign and formula; do not absolute-value or reverse the ratio.
- The per-section `component_hz` describes the component actually analyzed. It is not itself an acceptance threshold. `section_contrast_min_db`, amplitude/RMS floors, and all other rules should retain current values.
- This breaks field-name compatibility for consumers of newly generated receipts. Do not dual-write an old alias: two names would revive ambiguity. If downstream historical analysis is needed, handle the old/new field mapping explicitly outside the receipt, without mutating archived JSON.
- Existing receipts are historical evidence and should not be edited/re-serialized. Do not claim all historical artifacts satisfy a new schema.
- Nothing here establishes perceptual quality, audibility, engine/adaptive behavior, mix behavior, security, rights, or production readiness. No shell commands were run; this is source/receipt inspection only.
