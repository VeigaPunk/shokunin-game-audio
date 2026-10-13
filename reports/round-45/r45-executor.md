# Round 45 executor — negative-side UI duration controls

## Scope and result

Generated two original deterministic 48 kHz mono PCM16 UI-shaped WAV controls only under `.shokunin/audio/corpus/live/round-45/executor/`. Measured them with the project helper and unchanged ordinary `SPECS["ui"]` checks. The 5713-frame fixture passes all checks. The 5711-frame fixture fails only `duration: outside ±1 ms`; format, level, and centroid checks pass. This is numerical fixture calibration only—not an audition, quality assessment, or inference about production, rights, engine behavior, publishing, or promotion. I did not edit shared source, LOG, SCORECARD, canonical fixtures, or other reports, and made no commits or pushes.

## Recipe and pinned artifacts

For frame count `N` in `(5713, 5711)`: `n = np.arange(N)`, `t = n / 48000`, `samples = .28 * sin(2*pi*(700*t + 700*t*t)) * exp(-5*t)`, clip to `[-1,1]`, quantize with `np.rint(samples * 32767).astype("<i2")`, and write raw PCM as mono, 16-bit, 48000-Hz WAV. Reproduction script: `generate.py` in the executor scratch directory. Exact WAV SHA-256 and project-helper measurements:

| Frames / file | SHA-256 | ffprobe duration | Signed delta vs .12 s | Absolute delta | Peak FS | RMS dBFS | Centroid Hz | Ordinary helper result |
|---|---|---:|---:|---:|---:|---:|---:|---|
| 5713 `pass-5713.wav` | `94f1ad9459fbfc06120668e3ebe5743a2d8690c66238d586f05006102811dd99` | 0.119021 s | -0.0009789999999999938 s | 0.0009789999999999938 s | 0.27947998046875 | -16.399347369151716 | 1663.1001045998237 | no failures |
| 5711 `fail-5711.wav` | `2b4b0323f040a65b431a984e4fde5866f5c412754206c928e1fa21358adb9ab8` | 0.118979 s | -0.0010209999999999941 s | 0.0010209999999999941 s | 0.27947998046875 | -16.3992750775437 | 1627.5978467387597 | sole failure: `duration: outside ±1 ms` |

Both files are 48 kHz mono `pcm_s16le`, 16-bit. Both peak below .95, RMS above .001 FS, and centroid within the unchanged UI band (250–4000 Hz). Distinct hashes. Deltas use the actual ffprobe decimal durations parsed as Python floats against `.12`, not ideal frame fractions. The first report draft transcribed both signed/absolute float deltas using the R44 positive-side magnitudes; the parent corrected these four text cells by direct Python subtraction from unchanged ffprobe durations before integration. This was a report transcription error, not a measured numeric failed fit or setup error. The measured negative-side pass/fail pair brackets the ordinary predicate; this does not test or claim the 5712-frame equality case.

## Commands, exits, and errors

Generation command (exit **0**):

```sh
python3 .shokunin/audio/corpus/live/round-45/executor/generate.py
```

The project-helper invocation (exit **0**; expected fixture-level failures are returned as measurement data, not shell failure):

```sh
python3 -c 'import importlib.util; from pathlib import Path; p=Path(".shokunin/audio/corpus/fixtures/measure_audio.py"); s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); [print(m.measure("ui",m.SPECS["ui"],Path(f".shokunin/audio/corpus/live/round-45/executor/{name}.wav").resolve())) for name in ("pass-5713","fail-5711")]'
```

Measured ffprobe command, run once per file, each exit **0**:

```sh
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 .shokunin/audio/corpus/live/round-45/executor/pass-5713.wav
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 .shokunin/audio/corpus/live/round-45/executor/fail-5711.wav
```

No setup errors occurred. One numeric failed fit occurred: the 5711-frame control's ordinary duration check only. No other numerical gate failed. No inference is made about audible/perceptual duration, sound quality, production, rights, engine, publishing, or promotion.
