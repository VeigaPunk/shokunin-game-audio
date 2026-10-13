# r25-reviewer — minimal invalid-control integration plan

## Recommendation (plan only; no source edits)

Use the existing `build_artifacts.py --probe-invalid` → `measure_audio.py --probe-invalid` path. Add only two generated WAVs and append them to the existing invalid-probe table; do not add a validator gate, adjust thresholds, or change the normal measurement path.

- `rate_only.wav`: analytic 440 Hz sine, 0.2 full-scale, 4 seconds, **44100 Hz mono PCM16**. Compare with `round-22/native16_probe.wav` (48000 Hz mono PCM16): rate is the sole format difference.
- `channels_only.wav`: same analytic sine and duration, **48000 Hz stereo PCM16**, duplicate the same mono sample into both channels. Compare with `round-22/native16_probe.wav`: channels is the sole format difference.
- Write both under `corpus/live/round-25/`. Use explicitly named rate/channel constants locally; do not modify the established `RATE`, `save()`, canonical artifacts, or thresholds.

In `invalid_probes()`, include both paths in the format-probe branch and receipt metadata already recorded there (`sample_rate_hz`, `channels`, codec, bits). Expected outcome for each: `expected_failure`, `observed_failure: "format"`; metadata respectively `(44100,1)` and `(48000,2)`. For a clear one-factor assertion, compare each metadata tuple with the positive native16 tuple and record/assert that exactly its intended field differs. The current `format_failures()` bundles sample rate and channels into one format failure; keep that predicate unchanged. The existing `wrong_format.wav` remains the combined rate+channels control.

## Proposed commands and expected exits (not run here)

Run from repository root after the integrating author makes the source change:

```sh
python3 .shokunin/audio/corpus/fixtures/build_artifacts.py --probe-invalid
```

Expected exit **0**; generated controls only beneath `corpus/live/round-25/` (the current builder instead creates the older invalid probes, so this exact command is a future-state check).

```sh
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid
```

Expected exit **1**: this mode uses 1 to mean all expected invalid controls were correctly classified, including the two new `format` controls; exit **2** means an unexpected result. It should print a receipt path and include both rows plus their format metadata. A command/setup failure before receipt is not a passing check.

```sh
python3 .shokunin/audio/corpus/fixtures/measure_audio.py
```

Expected exit **0**, confirming unchanged normal fixtures/thresholds. The named verifier should separately replay the prior 19 runner modes and six pre-existing invalid controls as the round declaration requires; do not infer that replay from these commands.

## Fit/setup status and limits

No controls were generated or measured in this reviewer task; no source was edited and no fit/setup command was run. Therefore the two proposed controls' numeric acoustic fit is **unverified**, not passed. Before accepting the move, inspect their WAV headers and ensure ordinary duration/level/centroid checks are in-range (or explicitly document a failed fit); do not weaken thresholds or silently count a confounded control. If synthesis or tool invocation fails, record the actual command and exit as setup failure, not evidence of a validator result. This is a narrow plan for isolating rate from channels; it establishes no broader WAV, codec, perceptual, engine, rights, or publishing claim.
