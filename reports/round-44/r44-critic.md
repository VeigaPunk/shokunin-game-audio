# R44 critic: duration isolation and boundary limits

## Scope and verdict

I read the R44 declaration in `.shokunin/audio/LOG.md`. I did not find any R44 scratch fixture under `corpus/live/round-44/` at inspection, and did not alter shared source, LOG, SCORECARD, canonical artifacts, or other reports. This is a numerical fixture-calibration critique only.

The proposed 5807/5809-frame pair is a plausible **interior** pass/fail bracket for the ordinary duration check, but the evidence does not justify an exact `1 ms` equality claim. The threshold is strict `> .001` after parsing ffprobe's six-decimal duration string into binary float. At 5808 frames ffprobe reports `0.121000`; Python computes `0.121 - 0.12` as `0.0010000000000000009`, which is greater than `.001`, so exact mathematical equality is liable to fail. The advertised pass/fail pair avoids that equality point, but tests only these two samples and this ffprobe/reporting path.

## Independent numerical probe

I generated disposable temporary mono PCM16 WAVs from the declared UI-shaped chirp formula, at 48 kHz, frame counts 5760/5807/5808/5809. I did not write these probes into the repository. For each WAV, the exact ffprobe argument vector was:

```text
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json <temporary-wav-path>
```

Each ffprobe invocation returned exit 0. Measured ffprobe duration and delta from the UI spec `.12`:

| frames | ffprobe duration (s) | parsed `duration - .12` (s) | intended strict predicate `abs(delta) > .001` |
|---:|---:|---:|---|
| 5760 | 0.120000 | 0.0 | pass |
| 5807 | 0.120979 | 0.0009790000000000076 | pass |
| 5808 | 0.121000 | 0.0010000000000000009 | **fail** |
| 5809 | 0.121021 | 0.001021000000000008 | fail |

This differs from the ideal unrounded sample-time deltas: +47/48000 = .0009791666666666666, +48/48000 = .001 exactly, and +49/48000 = .0010208333333333334. ffprobe's decimal output is rounded to microseconds here, and the subsequent float subtraction means the 5808 result is not treated as equality by the existing code.

Across the 5807/5809 pair, decoded PCM metrics were comfortably inside the other UI limits: peak `.375946044921875`, RMS `.09969218956170649` / `.09967508366737497`, weighted FFT centroid `1012.675992854734` / `1000.3681209361287 Hz`; both are 48 kHz mono `pcm_s16le`, 16-bit. Thus this temporary construction does not reveal a level/centroid/format confound for the proposed pair. The numbers do not establish exact equality behavior in the integrated runner, nor general robustness to different ffprobe versions, duration formats, sample rates, specs, or signals.

## Errors and inference limits

No setup errors occurred in the disposable probe. No integrated R44 mode was available to run, so there were no numeric failed fits to report; the 5808 boundary result is a direct evaluation of the currently inspected predicate using the measured ffprobe string, not an integrated runner receipt. The 5807 and 5809 measurements are supportive but do not falsify their expected outcomes.

No audition, quality, production, rights, engine, publishing, or promotion inference is made. In particular, do not describe 5808 frames / exactly `.001 s` as passing: with the current strict float comparison and observed ffprobe output it fails.
