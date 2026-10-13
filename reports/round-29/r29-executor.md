# Round 29 executor — lower-centroid fit evidence

## Result

Found an original source-generated 5760-frame candidate pair on opposite sides of the existing `.10` centroid-relative comparison, with both variants below the baseline centroid and zero duration delta. The selected nearby candidates are chirp multiplier `k=0.95` (below) and `k=0.94` (above). This is fit evidence only; no source/runner integration was performed.

All three WAVs were generated directly in `corpus/live/round-29/executor/` by `fit.py`, using `x=.38*sin(2*pi*(700*k*t + 800*k*t*t))*exp(-30*t)`, `t=arange(5760)/48000`, rounded/clipped to little-endian PCM16. Baseline uses `k=1.0`. Both variants retain the same waveform form and length; only `k` differs.

| File / k | Duration | Frames / format | Peak | RMS dBFS | Centroid | Relative delta from baseline | Ordinary failures |
|---|---:|---|---:|---:|---:|---:|---|
| baseline / 1.0 | 0.120 s | 5760, 48kHz mono PCM16 | 0.375946 | -19.99169 | 966.896659 Hz | — | none |
| `k_0.95.wav` | 0.120 s | 5760, 48kHz mono PCM16 | 0.375732 | -19.99171 | 871.155505 Hz | 0.099019015 (<.10) | none |
| `k_0.94.wav` | 0.120 s | 5760, 48kHz mono PCM16 | 0.375671 | -19.99170 | 862.026457 Hz | 0.108460610 (>.10) | none |

The deltas are `abs(variant_centroid - baseline_centroid)/baseline_centroid`; variant-minus-baseline is negative for both, confirming the fit is on the lower side. The relative values are not equality claims. Both candidates pass the unchanged ordinary UI measurement spec: `.12 s`, 48kHz mono PCM16, peak below `.95`, RMS above the near-silence floor, centroid in 250–4000Hz. Direct project measurements also report duration delta exactly `0.0 s` between each variant and baseline.

## Direct evidence and exact commands

Scratch files are confined to `corpus/live/round-29/executor/`: `fit.py`, `fine.py`, the generated WAVs, `sweep.json`, `direct_project_measure.py`, and `direct_project_measure.json`.

1. `python3 .shokunin/audio/corpus/live/round-29/executor/fit.py` — exit **0**. Coarse sweep of `k=[.98,.95,.92,.90,.88,.85,.80,.75,.70,.65,.60,.55,.50]`; measurements saved to `sweep.json`. All sampled candidates passed ordinary checks, but many landed on the same side or far from the cutoff; the sweep is visibly non-monotonic.
2. `python3 .shokunin/audio/corpus/live/round-29/executor/fine.py` — exit **0**. Fine sweep of `k=[.960,.955,.950,.945,.940,.935,.930,.925,.920]`; it likewise saved direct candidate metrics to `sweep.json`. Notably `k=.950` yielded relative delta `.099019015` and `k=.940` yielded `.108460610`; intervening values do not establish monotonicity.
3. `python3 .shokunin/audio/corpus/live/round-29/executor/direct_project_measure.py` — exit **0**. This invokes the repository's `fixtures/measure_audio.py` `measure()` function against the generated baseline and selected candidates with the exact UI spec tuple `(.12,250,4000,False)`, and saves `direct_project_measure.json`. The project's `ffprobe`, `sox`, and `ffmpeg` calls all completed successfully.

## Failed candidate fits and setup

No sampled candidate had an ordinary duration, format, level, or centroid-band failure. This is distinct from fit failures: in the coarse sweep, `k=.98` and `.95` were both below `.10`, while `.92` and `.90` were above; several other points were far from the cutoff. In the fine sweep, `k=.955` and `.945` were below, while `.940` and `.930` were above; those points did not form a monotonic trend. I did not present such sweep points as evidence of smoothness or use a search/interpolation assumption. The selected `.950/.940` pair are an observed two-point polarity fit only.

Setup notes: no setup failure or corrective retry occurred. The scripts and generated WAVs stayed within the assigned executor scratch directory. There was no invocation of the mutating fixture builder or runner, no edits to project source, canonical assets, LOG/SCORECARD, or other reports, and no commit/push.

## Interpretation limits

The centroid is the existing whole-waveform weighted FFT spectral-centroid **proxy**, measured on quantized PCM using the project's SoX-to-float path. This does not establish audible/perceptual difference. The pair illustrates the measured absolute-value branch for lower-centroid variants; it says nothing about smoothness, exact `.10` equality, rights, engine behavior, publishing, promotion, or changing any threshold. No runner integration or round admission is claimed.
