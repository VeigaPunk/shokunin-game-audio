# Round 44 executor — near-tolerance duration controls

## Scope and result

Generated two original, deterministic 48 kHz mono PCM16 UI-shaped WAV controls only in `.shokunin/audio/corpus/live/round-44/executor/`. Measured each with the project helper `measure_audio.py` and the ordinary `SPECS["ui"]` checks. The 5807-frame control passes all checks; the 5809-frame control fails only `duration: outside ±1 ms`. This is numerical fixture calibration only—not an audition, quality assessment, or inference about production, rights, engine behavior, publishing, or promotion. No source, LOG, SCORECARD, canonical fixture, or other report was edited.

## Recipe and pinned artifacts

For frame count `N` in `(5807, 5809)`, use `n = np.arange(N)`, `t = n / 48000`, `samples = .28 * sin(2*pi*(700*t + 700*t*t)) * exp(-5*t)`, clip to `[-1,1]`, quantize with `np.rint(samples * 32767).astype("<i2")`, and write raw PCM in a mono, 16-bit, 48000-Hz WAV. Generation code is `generate.py` in the executor scratch directory. Deterministic PCM recipe and exact WAV SHA-256:

| Frames / file | WAV SHA-256 | ffprobe duration | Delta from .12 s | Peak FS | RMS dBFS | Centroid Hz | Helper result |
|---|---|---:|---:|---:|---:|---:|---|
| 5807 `pass-5807.wav` | `17890e483de91075569283a2bcfbada6a6402e1cd87ab52da53bdfbc605cf934` | 0.120979 s | +0.000979 s | 0.27947998046875 | -16.431537076901346 | 1132.7351495568296 | no failures |
| 5809 `fail-5809.wav` | `c0552b983ecd9230b16d6ac3441eb8be7b43e80130bbd413fb62272752d7d510` | 0.121021 s | +0.001021 s | 0.27947998046875 | -16.432818198672756 | 936.6642301482127 | sole failure: `duration: outside ±1 ms` |

Both are mono `pcm_s16le`, 16-bit, 48kHz. Both peaks are below .95 and RMS exceeds .001 FS; centroids fall in the UI band 250–4000 Hz. Their hashes differ. Deltas are from ffprobe's reported decimal duration, not an assumed exact equality edge: 5807 passes, 5809 is outside the tolerance.

## Exact checks and exits

The deterministic generation recipe was executed in-session and saved as `generate.py` for reproducibility; it wrote both WAVs. I did not run that script as a shell command. The following exact project-helper shell command ran and exited **0**; the helper returns measurements rather than treating the expected fixture-level failure as process failure:

```sh
python3 -c 'import importlib.util; from pathlib import Path; p=Path(".shokunin/audio/corpus/fixtures/measure_audio.py"); s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); [print(m.measure("ui",m.SPECS["ui"],Path(f".shokunin/audio/corpus/live/round-44/executor/{name}.wav").resolve())) for name in ("pass-5807","fail-5809")]'
```

Observed measured JSON is tabulated above. No setup errors or numerical failed fits occurred. No whole runner/new feature was added, and no claim is made for the 5808-frame equality case.
