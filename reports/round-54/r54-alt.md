# R54 independent alternate: matched PCM32/PCM16 UI pair

## Construction and scope

Generated an independent, original signed-integer pair in `.shokunin/audio/corpus/live/round-54/alt/`: 5,760 mono samples at 48,000 Hz (0.120 s). The source signal is a three-tone sum (`.22` at 733 Hz, `.11` at 2,131 Hz, `.035` at 3,217 Hz). It is rounded to signed PCM16; the PCM32 control candidate stores those same integers multiplied by 65,536. This intentionally grid-matched fixture isolates the existing signed-width metadata predicate. It does not test added PCM32 precision or general PCM32 conversion.

Generation command (exit **0**):

```sh
python3 .shokunin/audio/corpus/live/round-54/alt/generate_pair.py
```

| File | Bytes | WAV SHA-256 |
|---|---:|---|
| `candidate_pcm32.wav` | 23,084 | `5cd1711de2ed2dc76fc2505a2f0584f1fd31d523994818168fba18f1cbb49b9a` |
| `control_pcm16.wav` | 11,564 | `37a1eb68e0a870d3b3a58e4d45d5686de12e0cb4bcabaffa15c079f50da51436` |

## Actual metadata, gate results, and decode comparison

Ran the following ffprobe command for each file; each exited **0**:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json <file>
```

PCM32 metadata: `pcm_s32le`, `s32`, 32 bits, 48,000 Hz, mono, `.120000` s. PCM16: `pcm_s16le`, `s16`, 16 bits, 48,000 Hz, mono, `.120000` s.

Project-measurement command for each file (both exit **0**):

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.measure("ui",m.SPECS["ui"],Path("<absolute-file-path>")))'
```

Both report 5,760 decoded samples, duration `.12 s`, peak `0.3634033203125`, RMS `-15.105666206939194 dBFS`, centroid `2718.417873898037 Hz`, bandwidth `3712.599544713593 Hz`, and `integrated_lufs=null`. Both pass non-format UI gates: duration ±1 ms, peak <.95, RMS >=.001, centroid 250–4000 Hz, and 48 kHz mono. PCM32 failures are solely [`format: expected PCM16`]; PCM16 failures are `[]`.

Explicit decoder commands, each exit **0**:

```sh
sox .shokunin/audio/corpus/live/round-54/alt/candidate_pcm32.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-54/alt/pcm32-decoded.f32
sox .shokunin/audio/corpus/live/round-54/alt/control_pcm16.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-54/alt/pcm16-decoded.f32
```

Comparison command (exit **0**):

```sh
python3 -c 'import numpy as n; from pathlib import Path; p=Path(".shokunin/audio/corpus/live/round-54/alt"); a=n.fromfile(p/"pcm32-decoded.f32",dtype="<f4"); b=n.fromfile(p/"pcm16-decoded.f32",dtype="<f4"); print(len(a),len(b),n.array_equal(a,b),float(n.max(n.abs(a-b))),int(n.count_nonzero(a!=b)))'
```

Output: `5760 5760 True 0.0 0`. Both decoded files have SHA-256 `925b7a0071e1566e32f32c0f6540a4937f3dc02493e796dba013cc7a9ee6d833`.

## Limits

No gate other than the intended PCM32 format rejection failed. Equality follows from constructing the pair on the PCM16 integer grid; it is not evidence about extra 32-bit precision, arbitrary PCM32 content, generic codec conversion/fidelity, audibility, quality, rights, engine behavior, production or promotion. No shared source, LOG, SCORECARD, canonical artifact, or other report was changed; no commit or push was made.
