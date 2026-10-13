# Round 27 simplifier review

## Recommendation
Keep the existing distinctness predicate and thresholds unchanged. The declared calibration question is narrowly whether the existing duration arm treats a just-below `.020 s` delta as false and an exactly `.020 s` delta as true. Two explicit opt-in comparison cases are sufficient; do not add a generic tolerance, configurable threshold, generalized probe framework, or refactor of distinctness handling.

## Declared cases and evidence needed

| Baseline → variant | Frames at 48 kHz | Expected duration delta | Expected duration-arm result |
|---|---:|---:|---|
| 5760 → 6719 | 959 | `959/48000 = 0.0199791666667 s` | false; distinctness fails only if centroid-relative delta is also `< .10` |
| 5760 → 6720 | 960 | `960/48000 = 0.020 s` | true; distinctness passes even if centroid-relative delta is `< .10` |

The declared baseline duration is `.120 s`. These are source-generated analytical PCM16 samples, not perceptual comparisons. Preserve the existing `.020` and `.10` constants and OR predicate. Record measured ffprobe duration deltas and centroid-relative deltas; do not infer outcome from nominal frame arithmetic alone. The comparator uses floating-point durations (`duration_delta >= .020`), so if the 6720-frame observation falls below `.020` due to representation, report the failed fit as observed rather than adding epsilon or moving the threshold.

Because the longer variant exceeds the ordinary UI `.120 s` duration spec, each scratch file needs an explicit matching declared duration spec for its own measurement, with other UI constraints held fixed. A duration-spec failure is not evidence about distinctness. Confirm both measured candidates pass their individual format/level/centroid and duration checks, and that centroid-relative deltas stay `< .10`; otherwise the duration arm is not isolated. If truncation changes centroid too much or a file misses its declared duration, label that candidate a failed fit, not a predicate result.

## Scope / claims
This is a numeric polarity check around one duration comparator, not a change to the distinctness rule or a general boundary guarantee. It supports no perceptual, rights, engine, publishing, or promotion claim. Existing canonical samples and prior modes should remain untouched and be verified by the integrator.

## Commands and exits
No shell commands were run by this reviewer; no exit codes or runtime measurements are claimed. The calculations in the table are nominal frame-count arithmetic only.
