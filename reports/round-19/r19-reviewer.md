# Round 19 reviewer — minimal paired edge-probe wiring

## Recommendation
Add two opt-in flags, `--probe-layer-third-slope-edge-pass` and `--probe-layer-third-slope-edge-fail`, implemented as scratch variants of the existing round-18 200 Hz probe. Both should derive from `artifacts/stem_layer_third.wav`, change only PCM frame 96001, and write distinct files under `live/round-19/` (for example `slope200_edge_pass.wav` and `slope200_edge_fail.wav`). The pass flag adds +2 counts (43→45); the fail flag adds +3 (43→46). Do not change canonical synthesis or thresholds.

In the runner, add each flag to argparse and the mutual-exclusion check, forward the selected builder flag, measure the matching scratch path with `SPECS["stem_layer_third"]`, and emit a distinct mode/suffix and measurement key for each. Include both keys in the existing 200 Hz `section_contrast` dispatch and the same existing internal-gap and internal-side-slope applicability checks used by `slope200_probe`. Leave `section_contrast`, comparator `> .001`, 200 Hz validity/contrast rules, generic measurement, outer seam, and all threshold values untouched. Aggregate failures normally: expected numeric gate failure is runner exit 1, not a setup error.

## Source review and expected arithmetic
The existing builder already has an opt-in `layer_third_slope_probe` pattern: it reads the generated canonical PCM16 WAV and edits frame 96001 into a separate live WAV. The runner maps that scratch through `SPECS["stem_layer_third"]`, applies the same 200 Hz section, internal join gap, internal side-slope, and generic/outer-seam checks. The existing source confirms the gate uses strict `> .001`; do not add a special case, second comparator, permissive boundary, or changed threshold.

The LOG/scout arithmetic predicts the local outcomes: baseline four counts `[-26,-13,0,43]`; +2 yields 32 counts of side-slope mismatch, `32/32768 = .0009765625`, below .001; +3 yields 33 counts, `33/32768 = .001007080078125`, above .001. These are hypotheses until SoX decode plus complete runner receipts show both candidates satisfy all other relevant gates. Scope the interpretation to these one-frame PCM16 controls and this decode path; this is numeric threshold-resolution disclosure, not perceptual calibration.

## Inspection evidence
Exact source-inspection command:

```sh
grep -nE 'def section_contrast|internal_join_side_slope|probe-layer-third-slope|stem_layer_third|def main|layer_third_slope_probe' .shokunin/audio/corpus/fixtures/measure_audio.py .shokunin/audio/corpus/fixtures/build_artifacts.py
```

Exit: **0**. It showed the existing third-layer spec, section function, strict slope-gate call sites, round-18 runner option/dispatch, and builder option/edit.

Exact source-baseline comparison:

```sh
git diff --quiet 010f88b -- .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/corpus/fixtures/measure_audio.py
```

Exit: **0**. At inspection time, neither fixture source file had changed from baseline `010f88b`. I did not modify source, invoke either new mode, or assert candidate pass/fail outcomes. No shell setup errors occurred. No audible, engine, or production assertion is made.
