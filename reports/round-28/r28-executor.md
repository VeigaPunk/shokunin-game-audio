# Round 28 executor — fixed-duration centroid-proxy pair

## Result

Found a source-generated, 5760-frame (0.120 s), 48 kHz mono PCM16 triplet using the baseline UI-shaped decaying chirp and changing only its initial chirp-frequency parameter `f0`. Direct project measurement passes ordinary format, duration, level, and UI centroid-band checks for all three. Both comparisons have duration delta 0. The `f0=630 Hz` variant lies below the existing 0.10 centroid-relative cutoff and therefore fails the distinctness OR; `f0=626 Hz` lies above and passes. Values are measured, not predicted. No exact 0.10 equality is claimed.

Generator: `x = 0.38 * sin(2*pi*(f0*t + 800*t*t)) * exp(-30*t)`, with `t = arange(5760)/48000`; clip to [-1,1], multiply by 32767, `numpy.round`, cast little-endian signed 16-bit PCM. Baseline `f0=700`, below candidate `f0=630`, above candidate `f0=626`. These are original synthesized scratch WAVs, not edits to canonical fixtures or the runner.

## Direct receipt table

Source: `corpus/live/round-28/executor/fit-receipt.json`; WAVs and exact generator/reproduction script are in the same scratch directory. Table entries are direct outputs of project `measure_audio.measure()` (which invokes `ffprobe`, SoX and ffmpeg) and the runner's distinctness calculation against baseline.

| WAV | f0 Hz | frames | ffprobe duration s | PCM format | peak FS | RMS dBFS | centroid Hz | relative delta vs base | duration delta s | ordinary checks | distinctness |
|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---|---|
| `baseline.wav` | 700 | 5760 | 0.120000 | 48k mono PCM16 | 0.3759460 | -19.991688 | 966.896659 | — | — | pass | reference |
| `below.wav` | 630 | 5760 | 0.120000 | 48k mono PCM16 | 0.3754883 | -19.991732 | 926.745935 | 0.041525352 | 0.000000 | pass | fail (`< .10`) |
| `above.wav` | 626 | 5760 | 0.120000 | 48k mono PCM16 | 0.3754578 | -19.991742 | 839.450341 | 0.131809658 | 0.000000 | pass | pass (`>= .10`) |

`measure_audio.measure()` returned empty `failures` for each. Centroids all fall within the ordinary UI 250–4000 Hz band. Distinctness is `duration_delta >= .020 OR abs(variant_centroid-baseline_centroid)/baseline_centroid >= .10`. This isolates the centroid arm with duration zero.

## Reproduction commands and fit failures

All commands run from project root using its `python3` executable/environment.

- `python3 .shokunin/audio/corpus/live/round-28/executor/sweep.py` — exit 1: first scratch integration attempt passed a relative path to `measure()`, which requires path under its absolute fixture ROOT; setup/path error only, no measurement.
- `python3 .shokunin/audio/corpus/live/round-28/executor/sweep.py` — exit 0 after script was changed to resolve scratch WAV paths; initial sweep of the existing `700*t + k*t*t` form showed parameter variations here do not yield a useful bracket.
- `python3 .shokunin/audio/corpus/live/round-28/executor/sweep_f0.py` — exit 0, coarse sweep of `f0*t + 800*t*t`; ordinary checks passed.
- `python3 .shokunin/audio/corpus/live/round-28/executor/bracket.py`, `local.py`, `nearfit.py`, `nearfit2.py` — each exit 0; parameter exploration, not selected fit. The `625 Hz` trial measured relative delta 0.09213 (still below cutoff); `624 Hz` measured 0.04569, `626 Hz` 0.13181, and `630 Hz` 0.04153. Quantized/finite FFT response is not monotonic across nearby parameter values, so chosen values are empirical sweep hits, not an assumed interpolation.
- `python3 .shokunin/audio/corpus/live/round-28/executor/fit.py` — exit 0, final three-file direct receipt and table above. It regenerates baseline/selected pair and writes `fit-receipt.json`.

Earlier sweep and fit scripts plus all trial WAVs are under `corpus/live/round-28/executor/`; no out-of-scope paths were written by this worker. Runner modes, thresholds, canonical artifacts, prior-mode receipts, and source fixtures were not changed.

## Limit

This establishes only numeric polarity of this project's whole-waveform FFT magnitude-weighted spectral-centroid proxy for this generated pair on this toolchain. It is not an audibility, perception, quality, rights, engine, publishing, or promotion result. The candidate pair is not integrated into runner modes.
