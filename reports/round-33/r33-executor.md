# Round 33 executor — direct UI third-fixture fit

## Result

A source-generated 9,600-frame (0.200 s nominal), 48 kHz mono PCM16 UI-shaped chirp fits the declared per-file numeric checks using `(0.20, 250, 4000, False)`. Direct project `measure()` result: ffprobe duration `0.2 s`; codec `pcm_s16le`, 16 bits, one channel at 48 kHz; peak `0.375946044921875`; RMS `-22.20695387316763 dBFS`; FFT centroid `966.7216217320357 Hz`; bandwidth `1592.8581459886468 Hz`; failures `[]`. Its waveform is the existing UI analytic chirp recipe extended to .20 s: `.38*sin(2*pi*(700*t + 800*t*t))*exp(-30*t)`, quantized by the builder's clipped/rounded PCM16 procedure. This is a numeric fixture fit, not a listening or quality judgment.

Scratch WAV: `.shokunin/audio/corpus/live/round-33/executor/ui_third.wav`
SHA-256: `734a0a47077f5b614b5d51d486b88a51940c7d61ecea0878642b60a0103513bc`

## Pair metrics (existing OR rule: duration delta >= .020 s OR centroid relative delta >= .10)

Baseline is the respective existing UI fixture; centroid relative delta is absolute centroid difference divided by that baseline centroid.

| baseline → proposed third | measured duration delta | absolute centroid delta | relative centroid delta | OR distinctness |
|---|---:|---:|---:|---|
| `ui` (.12 s; centroid 966.8966593379727 Hz) → `ui_third` | 0.08000000000000002 s | 0.17503760593695006 Hz | 0.00018103031409457665 | pass on duration only |
| `ui_alt` (.16 s; centroid 1423.1532540422852 Hz) → `ui_third` | 0.04000000000000001 s | 456.4316323102495 Hz | 0.3207185389302337 | pass on duration and centroid |

Both baselines and the candidate have no failures under their declared per-file specs. Measurements use the existing project SoX-decoded FFT centroid and ffprobe duration, not synthesis parameters. The rule therefore reports a numerical distinction; a duration difference can satisfy it despite almost identical measured centroids in the `ui` pair. This does not establish perceptual distinction. The .20 s candidate exceeds both existing durations and is not a replacement for either.

## Commands and setup accounting

Ran from project root. The initial two direct-measure invocations had helper-path/setup errors, not measurement failures; corrected invocations are included.

1. `python3 -c "import importlib.util; p='.shokunin/audio/corpus/fixtures/measure_audio.py'; s=importlib.util.spec_from_file_location('measure_audio',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.measure('ui_third',(.20,250,4000,False),'.shokunin/audio/corpus/live/round-33/executor/ui_third.wav'))"` — exit **1**, setup error: passed `str` where `measure` expects a `Path` (`AttributeError: 'str' object has no attribute 'relative_to'`). No fit conclusion.
2. `python3 -c "import importlib.util; from pathlib import Path; p='.shokunin/audio/corpus/fixtures/measure_audio.py'; s=importlib.util.spec_from_file_location('measure_audio',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.measure('ui_third',(.20,250,4000,False),Path('.shokunin/audio/corpus/live/round-33/executor/ui_third.wav')))"` — exit **1**, setup error: relative path was not under project `ROOT` as resolved by the imported module. No fit conclusion.
3. `python3 -c "import importlib.util; from pathlib import Path; p='.shokunin/audio/corpus/fixtures/measure_audio.py'; s=importlib.util.spec_from_file_location('measure_audio',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.measure('ui_third',(.20,250,4000,False),Path('.shokunin/audio/corpus/live/round-33/executor/ui_third.wav').resolve()))"` — exit **0**, direct candidate result above.
4. `python3 -c "import importlib.util; from pathlib import Path; p='.shokunin/audio/corpus/fixtures/measure_audio.py'; s=importlib.util.spec_from_file_location('measure_audio',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.measure('ui',m.SPECS['ui']))"` — exit **0**, baseline result above.
5. `python3 -c "import importlib.util; from pathlib import Path; p='.shokunin/audio/corpus/fixtures/measure_audio.py'; s=importlib.util.spec_from_file_location('measure_audio',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.measure('ui_alt',m.SPECS['ui_alt']))"` — exit **0**, baseline result above.

No builder/runner or canonical artifact was edited or run. The 13 canonical WAVs were hash-checked after measurement; every hash matched its initial value. The proposal is analytic scratch only; it is not integrated, adopted, auditioned, promoted, published, or evaluated for rights or engine behavior. No claim is made about production readiness or playable quality.
