# Round 38 executor — measured above-threshold ambience pair

## Result

Found an original equal-duration looping PCM16 pair, measured with the project helper `measure_audio.measure`, within the declared strict band `.10 < centroid-relative delta < .13`:

- Scratch baseline: `corpus/live/round-38/executor/base.wav`
- Scratch variant: `corpus/live/round-38/executor/var_0.050.wav`
- Both: 48 kHz, mono, PCM16, 96,000 frames / 2.0 s.
- Baseline centroid: **36.6164076785 Hz**; variant: **41.2475246227 Hz**.
- Baseline-relative delta: **0.1264765508** (strictly > .10 and < .13).
- Duration delta: **0.0 s**.
- Both ordinary and loop-seam failure lists are empty. Baseline endpoint/slope deltas: 0.0006713867 / 0.0000305176; variant: 0.0010375977 / 0.0000305176 full scale units (the latter measured below).
- SHA-256 baseline `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198`; variant `e6dbfa42c6d5dabebad65b2e2f3e13a87f0916d523775b6abc5b535439956fb4`.

The source formula is `.15*sin(2π*12*t) + .09*sin(2π*36*t)` for baseline and the same plus `.05*sin(2π*60*t)` for variant, with PCM16 rounding at 48kHz for 96,000 samples. This reports numerical fixture checks only; it makes no audition, quality, production, rights, engine, publish, or promotion claim.

## Attempts and setup distinction

The initial pure 60/64 Hz sine pair repeated the Round 37 negative (project centroids 67.3718263/71.8086398 Hz, relative delta .0658556): valid ordinary/seam checks, but a numeric fit below the new strict target. Single-frequency trials from 60–75 Hz also skipped directly around the target due to the helper's full-waveform centroid/window behavior; multi-tone trials were explored next. The selected additive 60 Hz component yielded the required measured value. These are numeric experiments, not runner/integration outcomes.

One helper invocation initially passed a relative scratch path to `measure`, which raised `ValueError` because the helper serializes paths relative to its corpus root. This was setup only, not a measurement failure. Re-running with absolute scratch paths succeeded. No SciPy or external dependency was used.

Exact invoked commands and exits (Python `subprocess.run` argument vectors; project cwd `/home/vgpnk/Projects/prymeagnt/audio`):

- `['python3', '.shokunin/audio/corpus/live/round-38/executor/generate.py', '60', '67']` — exit 0; coarse single-frequency setup.
- `['python3', '-c', <measure helper script with relative scratch paths>]` — exit 1; setup/path error above.
- `['python3', '-c', <same helper script with absolute scratch paths>]` — exit 0; measured initial tones.
- `['python3', '.shokunin/audio/corpus/live/round-38/executor/generate.py', '61', '62', '63', '64', '65']` — exit 0; exploratory singles.
- `['python3', '.shokunin/audio/corpus/live/round-38/executor/generate.py', '60', '60.1', ..., '75']` — exit 0; 151 single-tone candidates; none met target.
- `['python3', '.shokunin/audio/corpus/live/round-38/executor/generate.py']` — exit 0; two-tone 12/36 vs 13/39 exploratory candidate measured .
- `['python3', '.shokunin/audio/corpus/live/round-38/executor/generate.py', '0.005', '0.010', ..., '0.100']` — exit 0; added-100Hz amplitude sweep did not reach target.
- `['python3', '.shokunin/audio/corpus/live/round-38/executor/generate.py', '0.01', '0.02', ..., '0.10']` — exit 0; 60+100Hz harmonic sweep did not reach target.
- `['python3', '.shokunin/audio/corpus/live/round-38/executor/generate.py', '0.03', '0.05', '0.07', '0.09', '0.11', '0.13', '0.15', '0.18', '0.20']` — exit 0; final 12/36 plus 60Hz amplitude sweep, selected .050 fit measured .1264765508.
- `['python3', '-c', <measure helper script for final pair>]` — exit 0.

No source, LOG, scorecard, canonical fixture, or other report was edited. No commits or pushes.
