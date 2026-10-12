# Round 19 simplifier — reuse the existing analyzer and gate

## Finding

The current source already provides one measurement path for the 200 Hz layer and one strict internal-slope check. The proposed edge pair requires **no new analyzer, threshold, or gate**: route both scratch WAVs through the existing `measure(..., SPECS["stem_layer_third"], ...)`, `section_contrast(..., 200)`, generic/outer checks, and internal-join checks. Preserve `>` `.001` exactly; report the already-computed metric and failures. Do not special-case the pass/fail outcome.

The builder should make the two required one-frame files by invoking a small shared operation with `(delta=2, filename=...)` and `(delta=3, filename=...)`, both from the canonical source and into the round-19 scratch directory. That operation copies PCM16 frames, alters only index 96001, and writes the existing mono/48 kHz/PCM16 format. This avoids duplicating a near-identical builder block and preserves the existing +8 round-18 mode and output. Keep it opt-in. Do not rewrite the builder or measurement runner’s broader mode plumbing just to eliminate its existing nested mode/suffix selection; that would enlarge the change and risk older modes for no benefit.

For runner wiring, add the two opt-in names and paths, then feed both measured names into the *existing* 200 Hz contrast and internal-gate name sets. Their only intentional difference is the +2 versus +3 PCM count. Keep the canonical artifacts untouched and retain the current run receipt, thresholds, JSON structure, and prior command modes. This is a local numeric boundary pair only, not a new audible criterion.

## Source inspection evidence

Exact inspection command:

```sh
grep -n -E 'layer_third|probe-layer-third|section_contrast|internal_join_side_slope|sum\(\[' .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/corpus/fixtures/measure_audio.py
git diff -- .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/ corpus/fixtures/measure_audio.py
```

Exit **0** for the actual command below (the printed output showed relevant lines; no source diff):

```sh
grep -n -E 'layer_third|probe-layer-third|section_contrast|internal_join_side_slope|sum\(\[' .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/corpus/fixtures/measure_audio.py
git diff -- .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/corpus/fixtures/measure_audio.py
```

The builder currently exposes `layer_third_slope_probe`, writes only the existing +8 `slope200_probe.wav` under `live/round-18`, and its CLI has `--probe-layer-third-slope`. The runner currently has one corresponding flag, measures it against `SPECS["stem_layer_third"]`, includes `slope200_probe` in 200 Hz section analysis, and appends the existing internal-slope failure only when the observed value is `> .001`. The edge pair can share all of this logic; no second implementation of those calculations is warranted.

I also attempted this inspection command with a typo in the second grep path:

```sh
git status --short && grep -n -E 'layer_third|probe-layer-third|internal_join_side_slope|sum\(\[' .shokunin/audio/corpus/fixtures/build_artifacts.py .shokun/audio/corpus/fixtures/measure_audio.py
```

It exited **2** (`.shokun/audio/...` does not exist). This was an inspection setup error only; it is not test or audio evidence. The corrected inspection above exited 0. No project tests or runner modes were run in this lane.

## Scope

No source, LOG, SCORECARD, canonical WAV, threshold, or other report was edited by this lane. No setup success/failure or source inspection is evidence that either paired runner mode passes. No audible, engine, or production assertion.
