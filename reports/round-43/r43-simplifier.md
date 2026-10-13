# R43 simplifier — minimal two-mode diff

## Scope and recommendation

Keep the move limited to two opt-in calibration modes; do not refactor the fixture framework, alter thresholds, or touch canonical artifacts. The existing comparator is `peak >= .95 or rms < .001` in `corpus/fixtures/measure_audio.py` (lines 80–81), with RMS measured after SoX f32 decode (lines 55–64). Both modes should use the existing UI spec and that unchanged comparator.

Minimal integration surface:

1. In `build_artifacts.py`, add one helper that writes two files under `corpus/live/round-43/`, from `n = np.arange(5760)` and `np.rint(counts * np.cos(2*np.pi*1000*n/RATE)).astype("<i2")`, for `counts` 46 and 47. Add only the two requested flags and route either flag to this helper, as the existing UI peak probe does. Use distinct filenames, e.g. `ui-rms-46.wav` and `ui-rms-47.wav`.
2. In `measure_audio.py`, add the same two flags to the existing mutually-exclusive probe option list and dispatch each to its corresponding WAV through `measure(name, SPECS["ui"], path)`. Keep the UI duration/frequency bounds, combined level predicate, measurement schema, and normal run untouched. Record the mode in the existing receipt metadata using the existing mode/suffix convention.

There is no need for a generic waveform abstraction or a new RMS-specific gate. Keep the builder/runner flags paired by crest count; avoid a combined flag that creates both while measuring only one, which would complicate the two-mode replay.

## Arithmetic / evidence boundary

I calculated quantized PCM estimates in the Python REPL, not via shell or the project's SoX decode: with `np.rint(k*cos(2*pi*1000*n/48000))` over 5760 frames, k=46 gives integer crest 46 and RMS `0.0009918604133909925` (about −60.07099 dBFS); k=47 gives crest 47 and RMS `0.0010130695326051164` (about −59.88721 dBFS). These estimates indicate a plausible bracket, not validated decoded measurements. No shell command was run, so there are no shell exit codes to report. No numeric fixture fit was attempted; thus there is no numeric failed fit, and no setup error occurred.

Before interpreting either mode as a result, confirm SoX-decoded peak remains below .95, decoded RMS is respectively below/above .001, centroid remains in the UI band, format/duration checks pass, and only the 46-count mode fails for `level: clipping headroom or near silence`. If the decoded fit differs, classify a numeric failed fit separately from a command/setup error; do not adjust a threshold or silently relabel a mode.

## Limits

This narrow pair could bracket the RMS branch with adjacent integer crest counts if those decoded conditions hold; it would not establish exact equality at .001, perceptual silence, audio quality, or any production, rights, engine, publish, or promotion claim. No source, LOG, SCORECARD, canonical artifact, or other report was changed.
