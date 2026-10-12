# Round 9 migration proposal — `r9-migration`

## Scope

This is a source/schema proposal only, based on the round-9 declared claim in `.shokunin/audio/LOG.md` and read-only inspection of `corpus/fixtures/measure_audio.py`. I made no source, receipt, LOG, SCORECARD, canonical, or commit changes. No shell commands were run. This makes no perceptual, engine, security, or production claim.

## Proposed smallest new-receipt shape

For each entry in `sections`, keep the per-section frequency and measured values, but rename the ambiguous result field:

```json
"sections": {
  "stem_layer": {
    "component_hz": 120,
    "section_samples": 96000,
    "component_amplitudes_full_scale": ["…", "…"],
    "section_rms_full_scale": ["…", "…"],
    "component_amplitude_contrast_db": "…",
    "valid": true,
    "passed": true
  }
}
```

The ellipses are illustrative, not receipt values. Preserve the current numeric computation exactly: when valid, `component_amplitude_contrast_db = 20 * log10(component_amplitudes_full_scale[1] / component_amplitudes_full_scale[0])`; otherwise it remains `null`. Keep the existing validity rules, 6 dB pass threshold, and all other thresholds unchanged. The key is explicitly an amplitude ratio in dB, not integrated section energy.

Remove `thresholds.section_component_hz` from newly generated receipts. Do not add a replacement top-level frequency constant: each section's existing `component_hz` is the sole frequency declaration for that section. Other threshold metadata remains as-is. The receipt-level schema change is therefore only removal of that top-level key and rename of `sections[*].section_energy_delta_db` to `sections[*].component_amplitude_contrast_db`; no duplicate old-key alias or compatibility shim.

## Mapping and historical boundary

| Historical field | New receipt field / handling |
| --- | --- |
| `sections[*].section_energy_delta_db` | `sections[*].component_amplitude_contrast_db`; preserve the exact value and formula, with no recomputation or threshold change. |
| `thresholds.section_component_hz` (legacy `30`) | Omit in new receipts. Read frequency from each `sections[*].component_hz` (`30` for the ordinary section probes; `120` for `stem_layer`/`flat120_probe`). |
| Any already-written receipt | Leave byte-for-byte immutable; do not rewrite, migrate in place, or claim it conforms to the new schema. |

Consumers that read historical receipts must interpret the old contrast key by its actual amplitude-ratio formula, and must not assume the legacy top-level `30` applies to every section. A separate historical-reader adapter is not part of this proposal; if one is needed, it should be an explicitly scoped follow-up, not a second key in newly emitted receipts.

## Boundary

This proposes a disclosure/auditability schema clarification only. It does not establish any runtime behavior, listening/perceptual quality, engine or mix behavior, security property, production readiness, or new fixture coverage. No receipt replay or numeric invariance was performed for this source-review assignment.
