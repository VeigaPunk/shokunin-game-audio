# R47 scout — ordinary absolute UI upper band vs lower band and pairwise distinctness

## Predicates are different

The ordinary UI measurement uses the absolute inclusive centroid predicate `250 <= spectral_centroid_hz <= 4000` (`SPECS["ui"] == (.12, 250, 4000, False)`); outside that interval `measure()` records `spectrum: centroid outside fixture band`. This is evaluated for each waveform independently, alongside its format, duration, level, and (where applicable) seam checks. R46 supplied a lower-bound calibration bracket around 250 Hz. The R47 declaration addresses the missing *upper* 4000 Hz pass/fail bracket. This scout did not generate or fit candidates, so it makes no upper-bound bracket claim.

Pairwise distinctness is a separate comparison between an `_alt` waveform and its baseline. The runner maps `ui_alt` to `ui` and calculates `abs(variant_centroid - base_centroid) / base_centroid`; the centroid arm passes at `>= .10`, OR the duration arm passes at `>= .020 s`. It is relative to the baseline, not an absolute frequency interval. Thus a pair can be distinct while both centroids are ordinary-band-valid; conversely, each waveform's ordinary absolute-band result does not establish that pairwise delta passes. The OR means a duration delta at/above .020 s does not isolate the centroid arm.

## Project measurement and evidence

`measure()` invokes SoX to decode each WAV as floating point (`sox PATH -t f32 -e floating-point -`), reads little-endian float32 then casts to float64, and calculates `abs(np.fft.rfft(samples))` across the whole waveform. It weights the positive-frequency `np.fft.rfftfreq(N, 1/rate)` bins by magnitude, not squared magnitude. This is a project numerical fixture metric, not a timbre or perception judgment. Format/duration come from ffprobe; peak and RMS come from the same decoded samples.

I inspected the existing normal receipt `corpus/live/runs/20261013T065654336632Z-normal/measurements.json`; no commands were run by this scout and no WAVs were measured/generated. The project-decoded canonical UI metrics are: duration **0.12 s**, **48 kHz mono PCM16**, peak **0.375946044921875 FS**, RMS **-19.991687666366516 dBFS**, whole-wave magnitude-FFT centroid **966.8966593379727 Hz**, bandwidth **1576.3372648411953 Hz**, no failures. This centroid lies within the ordinary 250–4000 Hz band; one normal fixture is not an upper-bound test.

The same receipt gives `ui_alt` centroid **1423.1532540422852 Hz** and baseline `ui` centroid **966.8966593379727 Hz**. Their absolute relative centroid delta is **0.47187731004956435** (47.19%), while duration delta is **0.04000000000000001 s**. Both centroids are within 250–4000 Hz, but this ordinary fixture pair's distinctness pass is not an isolated centroid-arm demonstration because duration alone exceeds .020 s.

For a centroid-arm example, the inspected R29 direct-project receipt `corpus/live/round-29/executor/direct_project_measure.json` records equal-duration candidates versus baseline: baseline centroid **966.8966593379727 Hz**; `k_0.95.wav` **871.155504521436 Hz**, relative delta **0.09901901500217196** (below .10); `k_0.94.wav` **862.0264574403602 Hz**, relative delta **0.1084606104331939** (above .10). Durations are all **0.120 s** and all three absolute centroids are inside 250–4000 Hz. This illustrates the distinctness threshold, not the ordinary upper limit. It does not test exactly .10 or 4000 Hz. R46's measured lower bracket is separately documented in `r46-executor.md`: 249.71389590882862 Hz (below) and 250.3250670185918 Hz (above); it says nothing about upper-bound calibration.

## Command and fit record / scope

No shell commands were run; I only read LOG/source and existing receipts. No candidate fitting or generation was attempted, so there are no setup errors or failed numeric fits to report. No report transcription or arithmetic correction was needed. This is fixture-numerics mapping only: no audition, quality, perception, production, rights, engine, publishing, or promotion inference; no exact 4000 Hz equality or causal single-variable spectral claim.
