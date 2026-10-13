# R54 critic — signed PCM32/PCM16 format isolation

## Scope

I read the R54 declaration in `.shokunin/audio/LOG.md` and the R53 executor/reviewer/critic evidence. I tested only a critic-owned, original ordinary UI-shaped pair under `.shokunin/audio/corpus/live/round-54/critic/`. No shared source, LOG, SCORECARD, canonical artifact, or other report was changed. This is a falsification attempt for the declared fixture-local isolation, not general PCM32 conversion, precision, or codec coverage.

## Construction and exact evidence

Generation command (exit **0**):

```sh
python3 .shokunin/audio/corpus/live/round-54/critic/generate.py
```

The script synthesizes 5,760 mono samples at 48,000 Hz from `.25*sin(2*pi*1000*t)+.08*sin(2*pi*1500*t)`, rounds to signed PCM16 `s`, then writes PCM32 integers exactly as `s*65536` (little-endian). Thus this PCM32 fixture's lower 16 bits are zero by construction; it does not exercise additional PCM32 precision. WAV SHA-256 / bytes: candidate PCM32 `3d78174340f2465299bd745bd102ef73981f2bf58c10d0ff959f4f3d3eeef81b` / 23084; PCM16 control `2d201f849ecb416401b15c88e172527f9beec852c8998123f5f06131c712fee0` / 11564.

Metadata command (exit **0**):

```sh
for f in .shokunin/audio/corpus/live/round-54/critic/*.wav; do echo "$f"; ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json "$f"; done
```

ffprobe identified candidate as `pcm_s32le`, `s32`, 32 bits, 48000 Hz mono, `.120000` s; control as `pcm_s16le`, `s16`, 16 bits, 48000 Hz mono, `.120000` s. This is signed integer PCM32 (not IEEE float).

Unchanged project UI measurer command (exit **0**):

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m",".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); p=Path(".shokunin/audio/corpus/live/round-54/critic").resolve(); [print(m.measure("ui",m.SPECS["ui"],p/f)) for f in ("candidate-pcm32.wav","control-pcm16.wav")]'
```

Both project SoX-f32 paths report 0.12 s, 48 kHz mono, peak `0.315399169921875`, RMS `-14.628083420045229 dBFS`, centroid `1123.8154138173777 Hz`, bandwidth `292.5430341707052 Hz`, and no integrated LUFS. Both pass the non-format UI duration (±.001 s), peak (<.95), RMS (>=.001), centroid (250–4000 Hz), rate, and channel checks. PCM32 failures are exactly [`format: expected PCM16`]; PCM16 failures are `[]`. The unchanged format predicate uses ffprobe codec name and bit depth, not the file extension.

Exact decoder/comparison command (exit **0**):

```sh
sox .shokunin/audio/corpus/live/round-54/critic/candidate-pcm32.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-54/critic/pcm32-decoded.f32 && sox .shokunin/audio/corpus/live/round-54/critic/control-pcm16.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-54/critic/pcm16-decoded.f32 && python3 -c 'import numpy as n; from pathlib import Path; p=Path(".shokunin/audio/corpus/live/round-54/critic"); a=n.fromfile(p/"pcm32-decoded.f32",dtype="<f4"); b=n.fromfile(p/"pcm16-decoded.f32",dtype="<f4"); print(len(a),len(b),n.array_equal(a,b),float(n.max(n.abs(a-b))),float(n.max(n.abs(a))),float(n.sqrt(n.mean(a.astype(n.float64)**2))))'
```

Output: `5760 5760 True 0.0 0.315399169921875 0.18560763156982443`. Both SoX conversions succeeded; no warning was printed. Decoded vectors are elementwise equal for this constructed pair.

## Falsification result and limits

I found no counterexample to the stated local isolation: ffprobe distinguishes signed PCM32 from PCM16; the project's unchanged UI measurer decodes both, the non-format gates agree and pass, and only the candidate trips the existing PCM16 format condition. Equality follows from PCM32 being PCM16 values shifted by 16 bits, so the result demonstrates no extra low-order information. The probe does not exercise arbitrary PCM32 samples, nonzero lower bits, resampling, alternate WAV headers, other codecs/decoders, general fidelity/audibility/quality, rights, engine or production behavior, or promotion. I did not exercise the runner's opt-in wiring, historical receipt replay, or canonical-set invariants; those are outside this critic test. No failed numeric fit or transcription correction occurred.
