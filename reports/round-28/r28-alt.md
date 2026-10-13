# r28-alt — independent fixed-duration centroid fit

## Result

I independently tested a source-side multiplier on the existing UI-shaped analytic chirp, preserving 5,760 samples (0.120000 s at 48 kHz) for every file. A close two-point polarity bracket was found using multiplier 1.10 (centroid-relative delta **0.1045465**, above the existing 0.10 comparison) and 1.11 (**0.0943408**, below it). Relative to the unchanged multiplier-1.0 baseline, these sides correspond to the expected numeric distinctness pass/fail respectively, with duration delta 0 for both. This is a candidate fit only; no fixture, runner, or canonical data was changed.

| Multiplier | ffprobe duration | centroid (Hz) | relative delta from baseline | peak FS | RMS FS | UI band 250–4000 Hz |
|---:|---:|---:|---:|---:|---:|---|
| 1.00 baseline | 0.120000 s | 966.896659 | — | 0.375946 | 0.100096 | pass |
| 1.10 | 0.120000 s | 1067.982318 | 0.1045465 (>= .10) | 0.375854 | 0.100096 | pass |
| 1.11 | 0.120000 s | 1058.114433 | 0.0943408 (< .10) | 0.376068 | 0.100096 | pass |

All three are 48 kHz mono PCM16; format, duration (±1 ms), level (peak < .95 and RMS > .001), and UI centroid band checks pass. Measured centroid gap between the two bracket variants is only 9.868 Hz (about 1.02% of baseline centroid), but their ratios lie about 0.45 and 0.57 percentage points on opposite sides of the 10% cutoff. This does not claim exact equality at 10%.

## Method and receipts

Scratch only: `.shokunin/audio/corpus/live/round-28/alt/` (`sweep.py`, `sweep.json`, `fine.py`, `fine.json`, plus stderr files). Commands from repository root:

- `python3 .shokunin/audio/corpus/live/round-28/alt/sweep.py > .shokunin/audio/corpus/live/round-28/alt/sweep.json 2> .shokunin/audio/corpus/live/round-28/alt/sweep.stderr` — exit 0.
- `python3 .shokunin/audio/corpus/live/round-28/alt/fine.py > .shokunin/audio/corpus/live/round-28/alt/fine.json 2> .shokunin/audio/corpus/live/round-28/alt/fine.stderr` — exit 0.

Both scripts synthesize WAVs in the allowed scratch directory, then directly call `ffprobe` for stream/duration metadata and `sox` for float PCM before computing the same whole-waveform, positive-frequency magnitude-weighted FFT centroid formula as the declared checker. The coarse sweep (multipliers 1.08–1.16) and fine sweep (1.104–1.110) are recorded in the JSON receipts. No failed setup or fit occurred.

## Confounds / limits

The multiplier changes the chirp's full frequency trajectory (`700*k*t + 800*k*t*t` cycles), not a single isolated spectral component. The checker computes one global FFT magnitude-weighted centroid, so phase, finite-window leakage, and quantization can affect this proxy; the fine sweep is visibly non-monotonic (for example, 1.104 gives 0.11253, 1.105 gives 0.07657). Thus parameter closeness does not imply a perceptual-distance bracket or smoothly varying centroid. The threshold result establishes only numeric polarity for this measured source pair. Centroid is a numeric proxy, not audibility or perception; no rights, engine, publishing, or promotion claim is made. No constants or canonical artifacts were changed.
