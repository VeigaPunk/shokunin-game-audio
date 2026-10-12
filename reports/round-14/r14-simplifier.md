# Round 14 simplifier review

## Scope and evidence

Static review of the Round 14 declaration in `.shokunin/audio/LOG.md`, `corpus/fixtures/build_artifacts.py`, `corpus/fixtures/measure_audio.py`, and the Round 13 simplifier report. No probe was generated or measured. No source, declaration, scorecard, canonical asset, or shared corpus file was edited.

The only shell command run was `find .shokunin/audio -maxdepth 4 -type f | sort | sed -n '1,200p'` (exit 0), to inspect the existing report/corpus layout. No shell audio or test command was run.

## Reuse and integration review

- Reuse `section_contrast(path, component_hz=180)` for the new scratch. It already reports section validity, amplitude contrast, and internal-join adjacent delta and side-slope mismatch; do not add a second decoder, metric helper, or gap comparator.
- The generic `measure()` already checks format, duration, level, centroid band, and outer endpoint/slope for `stem_layer_alt`'s spec. Measure the scratch with the existing `SPECS["stem_layer_alt"]`; do not add the scratch to `SPECS` or to the `_alt` distinctness pairing.
- The minimal runner wiring must carry the new probe name consistently through argument parsing / build invocation, scratch measurement, the sections comprehension at 180 Hz, existing internal-gap gate, mode/suffix receipt labels, and generation into `corpus/live/round-14/`. The internal side-slope gate already applies to canonical `stem_layer_alt` and the existing `layer_slope_probe`, but not to `join_probe`; include the new probe in that same existing condition so the slope metric is checked, without creating a new gate or threshold.
- Keep the current internal-gap comparison `> .03` and side-slope comparison `> .001` unchanged and strict. A correctly isolated case should have gap `> .03` (thus fail that existing gate) and slope mismatch `<= .001` (thus pass); it should remain valid with 180 Hz contrast `>= 6 dB`, and pass generic/outer checks and existing canonical `_alt` distinctness. Expected runner failure should therefore be only the existing internal adjacent-gap failure.
- Leave `section_contrast`'s shared `passed`/6 dB result and existing failure text unchanged. Its `passed` value reflects component contrast, while the gap and slope checks are independently appended to measurement failures; do not recast “passed” as a combined result or suppress any other failure.
- The existing `join_probe` is 120 Hz and intentionally has gap-only rejection without a side-slope check. This new 180 Hz case is a separate opt-in scratch probe; do not change old probe semantics or canonical artifacts. Keep the new output outside `artifacts/` and out of normal `SPECS` measurement.

The `.03` and `.001` values are already local fixture checks, not new or calibrated bounds. A single-sample discontinuity is only a numeric proxy: this test cannot establish audibility, a musically meaningful transition, engine behavior, or production quality. The candidate must be original synthetic PCM as specified; no claim about listening or external audio is made.
