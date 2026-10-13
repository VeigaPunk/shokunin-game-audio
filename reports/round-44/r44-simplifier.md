# Round 44 simplifier — two-mode diff review

## Recommendation
Keep the calibration probe to two explicitly named, opt-in modes: 5807 frames (pass) and 5809 frames (fail). Do not introduce a generic probe registry/helper, change the duration predicate or thresholds, or retune any other fixture.

The smallest coherent implementation is confined to the fixture builder and measurement CLI:

- Builder: add two explicit argparse flags and generate the corresponding original 48 kHz mono PCM16 UI-shaped scratch WAV for each selected mode. Use unique paths/names for 5807 and 5809, with no dependency on the other mode. Preserve normal artifact generation behavior.
- Measurement CLI: add the same two flags to the existing one-mode-only check and builder invocation; for the selected mode, call the existing `measure` once with `SPECS["ui"]` and the scratch WAV path. Existing UI spec already supplies the target `.12 s`, 250–4000 Hz centroid band, level checks, and format checks. Keep the ordinary `abs(duration - spec[0]) > .001` predicate unchanged. Add only the two corresponding receipt mode/suffix labels.

The frame counts predict offsets from .12 s of 47/48000 = 0.0009791666666666666 s and 49/48000 = 0.0010208333333333334 s. These are expected design values, not measured ffprobe results. The report must use each receipt's actual ffprobe duration and computed delta, and establish that all non-duration checks pass for each fixture. A 5809 exit 1 is a numeric failed fit only if its sole measurement failure is `duration: outside ±1 ms`; setup/build/probe errors are not a failed fit. Do not claim exact `.001 s` equality behavior.

## Scope / evidence
No fixture-generation or measurement command was run, so there are no ffprobe measurements, command exits, or numeric fit outcomes to report. The only shell command run was `git status --short && git diff -- .shokunin/audio/corpus/fixtures/measure_audio.py .shokunin/audio/corpus/fixtures/build_artifacts.py` (exit 0); it showed only `.shokunin/audio/LOG.md` as modified and no diff for the two source files. I made no source, LOG, scorecard, canonical, or other report edits; this file is the only file written by me.

This is numerical fixture calibration only. No audition, perceived-quality, production, rights, engine, publishing, or promotion inference is made.
