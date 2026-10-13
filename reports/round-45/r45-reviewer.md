# Round 45 reviewer — minimal negative-duration tolerance pair

## Review scope

The declared move is a numerical fixture calibration of the existing ordinary UI duration check. It is not a new comparator or a change to `SPECS["ui"]`: keep target duration `.12 s` and the ordinary strict failure condition `abs(ffprobe_duration - .12) > .001`. Keep ordinary fixtures and canonical measurements unchanged. Add only two opt-in scratch modes, one for each control, with generated WAVs under `corpus/live/round-45/` (never under canonical `artifacts/`).

## Minimal pair and expected decision

Use original deterministic 48 kHz, mono, PCM16 UI-shaped signals with exactly 5713 and 5711 frames. Their ideal frame durations are `5713/48000 = 0.11902083333333333 s` and `5711/48000 = 0.11897916666666667 s`; relative to `.12 s`, the signed ideal deltas are `-0.00097916666666667 s` and `-0.00102083333333333 s`. These are not assumed ffprobe measurements. ffprobe reports duration to six decimal places in this fixture path, so anticipated measured values are `.119021` and `.118979 s`, giving signed parsed deltas `-0.000979` and `-0.001021 s` (absolute deltas `.000979` and `.001021 s`). The first should pass duration; the second should fail duration only. Record actual measured output and calculate the deltas from it when executed.

Both signals need to independently pass the ordinary 48 kHz mono PCM16, peak `< .95`, RMS `>= .001`, and UI centroid 250–4000 Hz checks. The 5711 receipt must list exactly `duration: outside ±1 ms` as its failure; a setup/decoder/format error is not evidence of a numeric fit. Keep mode-exclusive CLI switches and distinct scratch WAV hashes. No need to create a control at 5712 frames or claim exact-boundary behavior.

## Preservation and interpretation

The existing comparator, thresholds, canonical `ui` fixture, 17 canonical measurement results, and ordinary no-argument run should remain byte-for-byte/measurement-equivalent. The modes should measure the original canonical UI spec, not adjust its target to force a result. Existing fixture families, prior opt-in modes, invalid probes, and restoration behavior are outside this small addition and should remain untouched.

This pair can support only the narrow statement that these two measured numerical fixtures straddle the existing negative-side duration threshold. It does not establish behavior at exact equality, perceptual/audible duration, signal quality, or production suitability, and supports no rights, engine, publishing, or promotion inference.

## Execution evidence

No fixture-generation, measurement, or test command was run. The only shell command was `git status --short` (exit 0); it reported `M .shokunin/audio/LOG.md`. No ffprobe duration, observed signed/absolute delta, or numeric fit was measured. The values above are ideal frame arithmetic and anticipated six-decimal ffprobe values, explicitly not measured evidence.
