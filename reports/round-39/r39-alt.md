# R39 alt — independent original loop orientation fit

## Scope and method

Generated two original deterministic 2.0 s, 48 kHz mono PCM16 sine loops in `.shokunin/audio/corpus/live/round-39/alt/`. Independently measured each with `measure_audio.measure(name, (2.0, 5, 200, True), absolute_path)` from `.shokunin/audio/corpus/fixtures/measure_audio.py`; the helper uses ffprobe, SoX, and FFmpeg and returns the project's whole-waveform magnitude-weighted FFT centroid plus ordinary and loop checks. The selected source sinusoids are 108 Hz and 114 Hz at amplitude 0.22. Both contain 96,000 frames. Measurements and hashes are also in scratch `measurements.json`.

Shell setup command: `mkdir -p .shokunin/audio/corpus/live/round-39/alt` — exit **0**. No shell command generated or measured the WAVs; those operations ran in the Python REPL through the project helper, so there are no shell exits for them. No runner mode was executed. No setup errors occurred.

## Selected measured pair — strict orientation split

| Role | Source | Measured centroid | Duration | Ordinary/loop failures | SHA-256 |
|---|---:|---:|---:|---|---|
| Lower-centroid baseline | 108 Hz | 125.06515861515496 Hz | 2.0 s | none | `7f4cdfefa6e52a8ff44268396b5c09ea459a648a5ac4cad0f42722fe5fc29938` |
| Higher-centroid variant | 114 Hz | 138.2410529357521 Hz | 2.0 s | none | `24203978fe84384db6686e8cf065e1f06f2eb966e88e92578f5da1bb9c5b9482` |

Absolute centroid gap is 13.175894320597138 Hz; duration delta is exactly 0.0 s. With lower-centroid baseline, `abs(138.2410529357521 - 125.06515861515496) / 125.06515861515496 = 0.10535223771747193`, strictly above .10. Swapping roles gives `abs(125.06515861515496 - 138.2410529357521) / 138.2410529357521 = 0.09531100957919258`, strictly below .10. Thus the same measured pair meets the requested strict baseline-relative orientation split with duration held equal. Checks report baseline peak 0.220001220703125, RMS −16.162110806691068 dBFS, endpoint delta 0.00311279296875, slope mismatch 0.0; variant peak 0.220001220703125, RMS −16.162119643156377 dBFS, endpoint delta 0.0032958984375, slope mismatch 0.000030517578125. Both failure lists are empty.

## Failed fits (separate from selected fit)

These ordinary/seam-valid exploratory pairs failed the *strict orientation-split fit*; they are not runner outcomes or setup errors:

| Source frequencies | Measured centroids (Hz) | Gap/lower centroid | Gap/higher centroid | Why fit failed |
|---|---|---:|---:|---|
| 55 / 60 Hz | 81.1592352376286 / 67.37182625966985 | 0.20464650794559466 | 0.1698809622538972 | Both orientations exceed .10 |
| 65 / 75 Hz | 91.03372963007341 / 81.62439856673954 | 0.11527596194954381 | 0.10336093117979261 | Both orientations exceed .10 |

Numerical control only. This reports the project's measured centroid proxy and checks; no audition, perceived distinction/seamlessness, quality, production, rights, engine, publishing, or promotion claim is made. No project threshold or source constant was changed.
