# Round 9 historical receipt inventory — Luna LEAF

Scope: read-only inventory at commit `aaf4801`, for later exact comparison with the round-9 receipt schema. This report does not assess perceptual quality, engine behavior, security, or production readiness.

## Historical receipts

All paths below are repository-relative and point to `measurements.json` as committed at `aaf4801`. In every receipt, `thresholds.section_component_hz` is `30` and `thresholds.section_contrast_min_db` is `6.0`.

| Case | Receipt path | Section record(s) and values |
|---|---|---|
| Normal | `.shokunin/audio/corpus/live/runs/20261012T172640257036Z-normal/measurements.json` | `stem_sections`: `component_hz=30`, amplitudes `[0.011999465108689048, 0.05999807118785472]`, RMS `[0.06381031454542734, 0.0761552612590769]`, `section_energy_delta_db=13.979508033945462`, valid/passed. `stem_layer`: `component_hz=120`, amplitudes `[0.011999587449951306, 0.05999774519524399]`, RMS `[0.00848499400645195, 0.04242481323818833]`, `section_energy_delta_db=13.979372282981668`, valid/passed. |
| Flat30 control | `.shokunin/audio/corpus/live/runs/20261012T172638021452Z-flat/measurements.json` | Baseline `stem_sections` and `stem_layer` values match the normal receipt above. `flat30_probe`: `component_hz=30`, amplitudes `[0.0359986154757334, 0.0359986154757334]`, RMS `[0.06817450068577438, 0.06817450068577438]`, `section_energy_delta_db=0.0`, valid but failed. |
| Flat120 control (`layer-flat` mode) | `.shokunin/audio/corpus/live/runs/20261012T172637297691Z-layer-flat/measurements.json` | Baseline `stem_sections` and `stem_layer` values match the normal receipt above. `flat120_probe`: `component_hz=120`, amplitudes `[0.035997209705667964, 0.035997209705667964]`, RMS `[0.025453872584504544, 0.025453872584504544]`, `section_energy_delta_db=0.0`, valid but failed. |

The historical `section_energy_delta_db` figures are the values stored in the JSON. The round-8 LOG states that this legacy field is `20*log10(A2/A1)` for the measured component amplitudes, not integrated section energy. Thus the stored normal contrasts are 13.979508033945462 dB (30Hz sections) and 13.979372282981668 dB (120Hz layer); both flat controls are 0.0 dB. The three tested modes therefore illustrate why top-level 30Hz metadata is not the frequency for every section: `component_hz` on each section is the specific frequency.

## Commands and exits

Read-only commands used; all returned exit code 0:

- `git ls-tree -r --name-only aaf4801 -- .shokunin/audio/corpus/live/runs` — 0.
- `git show aaf4801:.shokunin/audio/corpus/live/runs/20261012T172620813098Z-normal/measurements.json` — 0 (schema spot-check).
- `git show aaf4801:.shokunin/audio/corpus/live/runs/20261012T172640257036Z-normal/measurements.json` — 0.
- `git show aaf4801:.shokunin/audio/corpus/live/runs/20261012T172638021452Z-flat/measurements.json` — 0.
- `git show aaf4801:.shokunin/audio/corpus/live/runs/20261012T172637297691Z-layer-flat/measurements.json` — 0.

No source, receipt, LOG, SCORECARD, canonical artifact, or commit was edited.
