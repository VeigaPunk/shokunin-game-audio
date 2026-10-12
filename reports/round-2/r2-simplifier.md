# Round 2 simplifier review

## Recommendation

Keep the existing builder as the single source for synthesis and the existing measurement entrypoint as the single source for checks and receipts. Add the four variants in `build_artifacts.py` and add their four artifact names to `measure_audio.py`'s existing `SPECS`; do not add a second builder, runner, or separately maintained manifest.

- Reuse the current generation formulas and seeded RNG. Add one deterministic synthesis call per category, saving `ui_alt.wav`, `impact_alt.wav`, `movement_alt.wav`, and `ambience_alt.wav` under the same artifacts directory as the baselines. Keep the current `--probe-failing` behavior scoped to the existing deliberate ambience break; do not make the new clean variant fail in that mode.
- Extend `SPECS` with one row for each `_alt` file. Keep each row's format, duration, centroid band, and loop-check values next to the existing baseline row so the current `measure()` checks apply uniformly. Keep ambience's loop flag true.
- In the same measurement pass, compare each `_alt` result with its base result (strip `_alt` from the name, rather than adding another baseline-to-variant mapping). Distinctness passes if absolute duration difference is nonzero at the relevant recorded precision, or centroid difference is at least 10% of the baseline centroid. Record the measured deltas and a distinctness pass/failure in the receipt; include it in the overall exit failure decision. This compares measured raw-artifact results and does not create a timbre/quality claim.
- Keep the existing receipt and threshold fields, adding only per-variant distinctness evidence. No separate script, config, or expected-centroid table is needed. The variant's allowed centroid band is a check bound, not the expected measurement.

A straightforward low-risk variant is to preserve each category's duration and envelope while changing its source frequencies/noise realization enough to clear the centroid criterion. For ambience, preserve a periodic, endpoint-matched waveform so it continues to meet the existing seam test. If a generated variant instead changes duration, set its expected duration in its `SPECS` row; do not loosen the shared ±1 ms check.

## Guardrails / review notes

- `measure_audio.py` currently rebuilds canonical artifacts on every run before measuring them. Adding variants only to the current builder keeps reproducibility intact; avoid having the measurement script separately generate or rewrite variants in `live/round-2`.
- The round spec's executors own `corpus/live/round-2/*.wav`; the shared fixture builder and measurement edits belong to the parent integration step. My lane made no fixture, script, engine, canon, or scorecard edits.
- The current measure script's base `SPECS` contains five names. Adding four explicit spec rows is the small necessary extension. Deriving expected format/bands from a second manifest would duplicate sources of truth; deriving category pairing from the `_alt` suffix avoids an extra pairing table.
- Nothing here establishes perceptual quality, runtime/codec seam continuity, production loudness, or production readiness. Existing checks and local fixture thresholds should retain their current limited interpretation.

## Commands

No shell commands were run. I read `.shokunin/audio/LOG.md`, `corpus/fixtures/build_artifacts.py`, and `corpus/fixtures/measure_audio.py` with Python and wrote this report only.
