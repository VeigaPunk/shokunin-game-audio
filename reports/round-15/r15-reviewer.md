# Round 15 reviewer — minimal opt-in slope-probe wiring

## Recommendation

Keep this as a single opt-in synthetic fixture probe, not a new general-purpose mode or threshold. Add `--probe-layer-alt-slope` as a distinct Boolean through the existing builder and runner, generate one PCM16 scratch WAV under `corpus/live/round-15/`, then measure it using the existing `stem_layer_alt` spec and 180 Hz section analysis. Do not change canonical fixture generation, shared thresholds, or default-mode behavior.

## Minimal builder branch

In `build_artifacts.py`:

1. Add the parser flag `--probe-layer-alt-slope` and pass it through `main(...)` like the other probe booleans.
2. Add an `layer_alt_slope_probe=False` parameter to `main`.
3. Under that flag, construct the original synthetic 180 Hz stepped layer with the existing 220/330 Hz common bed (same recipe as `layer_alt_join_probe`):
   `base = np.where(t < 2, .015, .050)*np.sin(2*np.pi*180*t) + .08*np.sin(2*np.pi*220*t) + .04*np.sin(2*np.pi*330*t)`.
   Quantize once using the same `round/clip * 32767` PCM16 recipe as the existing join probe. Perturb only frame `96001` by the smallest practical PCM16 count(s) needed to exceed the existing slope mismatch bound, leaving frame `96000` untouched. Save as `slope180_probe.wav` in `OUT.parent / "live" / "round-15"`.

Use the recipe as a proposal, not a presumed fit: the exact quantized increment must be established from the decoded runner receipt. The scout's `+0.0004` FS was only a hypothesis. Preserve the `.03` gap, `.001` side-slope, and `6 dB` contrast bounds; do not add another cutoff or change existing logic to force a result.

## Minimal runner mapping

In `measure_audio.py`:

- Declare `--probe-layer-alt-slope`, include it in the mutually exclusive probe-mode count, and forward it to the builder.
- Measure `corpus/live/round-15/slope180_probe.wav` with `SPECS["stem_layer_alt"]` and expose it as a clearly named measurement (for example `slope180_probe`).
- Include that measurement in the `section_contrast` selection with component frequency **180 Hz**. Include it in both existing internal-join validation lists: the adjacent-gap check (`>.03` FS) and side-slope check (`>.001` FS/sample). Reuse the returned section result; do not duplicate decoding or recompute gates.
- Add the new mode and suffix in the existing receipt naming expressions, taking precedence for this flag, and include it in the build invocation. Keep the normal path and all old flags unchanged.

A successful isolated negative should therefore report the new measurement's complete failure list containing only `sections: internal join side slope mismatch > .001 full scale per sample`; the internal gap must be `<=.03`, section validity/contrast must pass at 180 Hz, and generic format/duration/level/centroid plus outer seam checks must pass. A candidate that fails any other check is a failed fit, not evidence for the proposed depth move.

## Evidence reviewed and limits

I read the round-15 LOG proposal and the current `build_artifacts.py` and `measure_audio.py`. The existing code already has 180 Hz component mapping for `stem_layer_alt`, `flat180_probe`, and `join180_probe`, while internal gap/slope enforcement is an explicit name list; the new measurement must be added to both lists. `layer_slope_probe` is currently mapped to 120 Hz and should remain so. The builder's existing `layer_alt_join_probe` provides a nearby example of a common-bed scratch recipe and `live/round-14` destination.

No shell commands were run; no exit codes, candidate measurements, or canonical-hash results are claimed. This recommendation is source-level wiring guidance only. The samples are original synthetic PCM fixture data, and these local numeric proxies do not establish audible smoothness, musical quality, engine behavior, security, external compatibility, or production suitability. Independent replay and canonical-hash verification remain necessary after any integration.
