# Round 18 simplifier — keep the probe opt-in and reuse existing checks

## Recommendation

Do not change the canonical WAV, numeric thresholds, or add another section analyzer. The existing `section_contrast(path, component_hz)` already measures section amplitudes/contrast, the join gap, and the internal side-slope mismatch. The runner already maps `stem_layer_third` to 200 Hz and applies the existing section and slope gates to it. For the declared depth experiment, the smallest viable implementation—if the parent chooses to wire it—is one opt-in scratch probe path based on the existing canonical 200 Hz fixture, with the one-count edit at frame 96,001 (+8 as the hypothesis), then send that scratch WAV through the existing `measure` and `section_contrast` functions. No duplicate analyzer or new threshold is needed. Avoid touching shared source here; this is a review/report only.

## Source inspection and command results

Inspected `.shokunin/audio/LOG.md`, `corpus/fixtures/measure_audio.py`, and `corpus/fixtures/build_artifacts.py` at HEAD `7083a3f`. The exact inspection command

```sh
grep -nE 'stem_layer_third|probe-layer-third-slope|section_contrast|loop_slope_delta_max' .shokunin/audio/corpus/fixtures/measure_audio.py; printf 'grep_exit=%s\n' "$?"; grep -nE 'stem_layer_third|layer.third.slope|layer_alt_reverse_probe|probe-layer-third-slope' .shokunin/audio/corpus/fixtures/build_artifacts.py; printf 'grep_exit=%s\n' "$?"
```

exited **0** (both grep exit values were 0). The inspection finds the existing canonical 200 Hz spec/mapping and existing slope gate, but **no** `probe-layer-third-slope` flag or probe implementation yet. Thus this report does not claim a probe was built or measured. There was no failed setup command.

The source has one `section_contrast` implementation; a second helper would duplicate existing calculations. The current runner thresholds include the existing strict `> .001` internal slope failure check and existing >=6 dB section-contrast gate; no new numeric threshold is recommended. The new fixture is already included in the regular measurement path; keep any depth probe opt-in and scratch-only rather than changing canonical fixture generation or ordinary-run outputs beyond the existing baseline.

The scout report records original join samples [-26, -13, 0, 43] and predicts +8 at frame 96,001 would raise the mismatch to 38/32768 = 0.00115966796875 FS/sample. That is a **prediction**, not a measured probe result; executor/replay evidence is needed before any sole-gate or fit conclusion. Do not relax the bound if a second gate fails; report and revise the scratch fit instead.

## Claim boundary

This simplification review concerns only the offline fixture runner and local numerical checks. It makes no audible, perceptual, musical, engine, production, security, rights, or compatibility claim. No source, canonical asset, LOG, SCORECARD, or other report was edited by this leaf.
