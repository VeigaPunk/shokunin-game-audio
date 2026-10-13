# r32-alt — independent mixed-signals fit

## Result

Independent analytic/source-generated candidate: a 48 kHz mono PCM16 chirp with phase multiplier `k=0.8625`, 6719 frames, paired against the 5760-frame `k=1.0` UI-shaped baseline. I measured both using the declared fixture `measure()` implementation. Both files pass the ordinary per-file format, level, and centroid-band checks under the baseline canonical UI spec and the variant's separately declared `6719/48000 s` scratch duration. The measured pair has nonzero duration delta below `.020 s` and nonzero centroid-relative delta at/above `.10`; by direct evaluation of the already-declared OR predicate it passes by the centroid arm. This is independent measurement, not an integrated runner receipt or assertion that the runner currently supports this probe.

## Scratch artifacts

Only scratch artifacts are in `.shokunin/audio/corpus/live/round-32/alt/`:
- `ui_altfit_base.wav`: 5760 frames; spec duration `.12 s`.
- `ui_altfit_variant.wav`: 6719 frames; separately declared spec duration `6719/48000 s`.

Both were synthesized as `.38 * sin(2*pi*k*(700*t + 800*t*t)) * exp(-30*t)`, `t=arange(frame_count)/48000`, rounded/clipped to signed PCM16. Baseline `k=1.0`; variant `k=.8625`.

## Measurements

| Measurement | Baseline | Variant |
|---|---:|---:|
| ffprobe duration (s) | 0.120000 | 0.139979 |
| format | 48000 Hz, mono, PCM s16le, 16-bit | 48000 Hz, mono, PCM s16le, 16-bit |
| peak full scale | 0.375946044921875 | 0.375244140625 |
| RMS (dBFS) | -19.991687666366516 | -20.658303988850626 |
| spectral centroid (Hz) | 966.896659337973 | 859.206217538948 |
| ordinary-check failures | none | none |

Measured duration difference is `0.019978999999999997 s`, nonzero and `< .020 s`. Centroid-relative difference is `0.11137740601230323`, nonzero and `>= .10`. Thus the declared distinctness expression `duration_delta >= .020 or centroid_relative_delta >= .10` evaluates true, via centroid only. No equality claim.

Variant duration intentionally does **not** conform to canonical `.12 s ± .001 s`; it passes only with the separately declared scratch duration `6719/48000 s`. No changes to thresholds or canonical fixtures.

## Failed attempts / setup

The initial analytic coefficient `k=.86` gave centroid-relative delta `0.15259232673311568`, which exceeded the target `.10`; this is a failed coefficient fit, not a failed ordinary check or setup. A coarse coefficient sweep showed FFT/quantization non-monotonicity; `k=.8625` was measured directly and selected. No setup failures. No shell command was run. Measurements invoked the project `measure()` function, which internally calls `ffprobe`, `sox`, and `ffmpeg`; their individual shell exit codes were not separately recorded.

## Scope and limits

This is an independent parameter fit and measured ordinary-check result only. It does not establish causal independence, exact cutoff behavior, perceptual similarity/distinctness, equality, rights, engine behavior, publishing, or promotion. No shared source, LOG, SCORECARD, canonical fixture, or other report was modified; no commits or pushes.
