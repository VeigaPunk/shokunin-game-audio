# Round 5 control replay analysis

Scope: I inspected the round-4 non-author replay report and its raw JSON receipts, plus the checked-in measurement logic. I did not edit shared source or run the generator again (it rewrites fixtures and creates receipts). I make no perceptual/mastering claim.

## Receipt provenance

The existing replay report records these exact commands, run from repository root, and exits:

```sh
python3 .shokunin/audio/corpus/fixtures/measure_audio.py
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing
python3 .shokunin/audio/corpus/fixtures/measure_audio.py
```

The recorded exits are `0, 1, 1, 1, 0`, respectively. Receipts are `corpus/live/runs/20261012T164313398133Z-normal/measurements.json`, `...164318673149Z-flat/measurements.json`, `...164319311023Z-slope/measurements.json`, `...164319899564Z-failing/measurements.json`, and `...164320494590Z-normal/measurements.json` (under `.shokunin/audio/`). Final normal restore has no failures.

## What these probes do and do not exercise

| Probe | Observed result | Threshold it exercises / isolates | Does not establish |
|---|---|---|---|
| `--probe-flat` (`flat30_probe`) | 30 Hz amplitudes `.0359986155/.0359986155` FS; per-section RMS `.06817450/.06817450`; valid=true; contrast `0.0 dB`; only failure is section contrast `<6 dB` | Exercises the 30 Hz component contrast acceptance (`>=6 dB`) with a valid, non-silent matched negative: both component-amplitude floors (`>=.01`) and section RMS floors (`>=.001`) pass; ordinary format, peak/RMS, centroid and seam checks pass. Thus it isolates contrast rejection, not invalid-input rejection. | It does not test the exact 6 dB boundary or prove a general musical threshold. It does not test rejection below either section component-amplitude floor or section-RMS floor. Flat30 endpoint `.00418091 <.03`, slope `.000030518 <.001`; neither seam bound is challenged. |
| `--probe-slope` (`slope_probe`) | Endpoint delta `0`; slope gap `.46997070` FS/sample; sole failure is slope mismatch `>.001` | Exercises the seam-slope upper bound with a gross failing value while endpoint check passes. The custom probe centroid range is 5–24000 Hz, so this is a slope-specific failure in the receipt. | Not the exact `.001` boundary; no passing near-boundary slope case. Does not challenge endpoint `.03` (observed 0), section guards, or other fixture-specific boundaries. |
| `--probe-failing` (broken `ambience`) | Peak `.49932861`, RMS `-17.791 dBFS`; centroid `2690.1877 Hz` vs ambience band `[5,200]`; endpoint jump `.49932861` vs `.03`; slope gap `0`; failures only centroid and endpoint | Exercises gross rejection by the ambience centroid upper bound and endpoint-jump upper bound together. It is not an isolated single-threshold control because both fail. | Does not exercise peak ceiling `.95` or RMS floor `.001` (both are comfortably passed), nor seam slope, duration/format, or section-contrast limits. It does not locate either failing bound near its boundary. Broken-amplitude label should not imply it tests the peak/RMS level guards. |
| Normal / final restore | Ten WAVs clean; section fixture has amplitudes `.01199947/.05999807`, RMS `.06381031/.07615526`, contrast `13.979508 dB`; seam endpoint `.00427246`, slope `.000152588` | Provides clean examples passing applicable checks; section component floors are passed relatively close to `.01` by section 1 (`.00199947` margin). | A clean pass is not a boundary probe and cannot validate the threshold cutoffs. The near-floor section amplitude is still above the floor, not a below-floor rejection. |

The old `flat_probe.wav` at 440 Hz is not the integrated checker control: the checker measures 30 Hz. The matched `flat30_probe.wav` is the relevant control. The 440-Hz scratch cannot be counted as exercising the integrated 6 dB test.

## Bounds left untested by this control set

No listed receipt deliberately places a value at/just across the format or duration limits (48 kHz mono; nominal duration ±0.001 s), peak cutoff (`peak < .95`), RMS cutoff (`RMS >= .001` linear), centroid band edges, endpoint cutoff (`delta <= .03`), or the exact slope cutoff (`delta <= .001`). Existing slope and broken-amplitude probes fail these last two bounds by very large margins; flat30 and normal merely pass them. Distinctness is evaluated in clean receipts (the paired variants pass via duration delta `>=.020 s` OR relative centroid delta `>=10%`), but no negative variant is provided to exercise rejection when both are below their cutoffs. Likewise no invalid/low-amplitude section control tests the `.01` component and `.001` section-RMS floors. These are gaps in control coverage, not evidence that the checks are wrong.

No loudness acceptance window is tested: integrated LUFS is observational, with `None` for gated/undefined or `<= -70 LUFS`, not an acceptance criterion. The controls here do not calibrate loudness.

## Evidence source / shell record

I read the raw JSON receipts named above and `corpus/fixtures/measure_audio.py`. Exact replay commands and exit statuses above are transcribed from the existing independent report `reports/round-4/r4-verifier-replay.md`; I did not independently execute those commands in this lane. No new shell validation was performed. This distinction prevents claiming my own execution where there was none.
