# R52 independent alternate: matched PCM8/PCM16 UI pair

## Scope

This is an independent original pair under `corpus/live/round-52/alt/`, made without source changes. It tests only the declared PCM8-vs-PCM16 UI format polarity for this constructed pair and the unchanged project UI measurement. It does not support general codec, fidelity, audibility, quality, production, rights, engine, or promotion claims.

## Generation and artifact identity

Generated 5,760 mono frames at 48,000 Hz (0.120 s). The signal is a 733 Hz sine at amplitude .23 plus a 1,469 Hz sine at amplitude .11 with phase .31, multiplied by a 96-sample linear onset/release envelope, then rounded on the unsigned 8-bit grid. PCM16 stores those exact quantized signed values scaled by 256. Consequently the intended normalized sample values match.

Command `python3 .shokunin/audio/corpus/live/round-52/alt/generate_pair.py` — exit **0**.

- `candidate_pcm8.wav`: 5,804 bytes; SHA-256 `0020bae326c373083f0e25be9b9362ef628b3ae0f2daf3942e5dee14d48c706c`.
- `control_pcm16.wav`: 11,564 bytes; SHA-256 `40ba4ae4a7231b9072a29b734005a4f64e87331d91b49c4cd93582daecbb6db2`.

## Actual codec metadata

Ran the following command once for each filename below; each exited **0**:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json <file>
```

| File | codec_name | bits_per_sample | sample_rate | channels | duration |
|---|---|---:|---:|---:|---:|
| `candidate_pcm8.wav` | `pcm_u8` | 8 | 48000 | 1 | 0.120000 s |
| `control_pcm16.wav` | `pcm_s16le` | 16 | 48000 | 1 | 0.120000 s |

## Project measurement and gate polarity

Command `python3 .shokunin/audio/corpus/live/round-52/alt/measure_pair.py` — exit **0**. This calls unchanged `measure(..., SPECS["ui"], path)` from `corpus/fixtures/measure_audio.py`, including its SoX-f32 decode and unchanged gates.

| File | decoded samples | duration | peak | RMS dBFS | centroid | bandwidth | failures |
|---|---:|---:|---:|---:|---:|---:|---|
| PCM8 | 5760 | 0.120 s | 0.34375 | -14.981981404018596 | 2897.653252566734 Hz | 5023.065492084627 Hz | `format: expected PCM16` only |
| PCM16 | 5760 | 0.120 s | 0.34375 | -14.981981404018596 | 2897.653252566734 Hz | 5023.065492084627 Hz | none |

Both pass the non-format UI predicates: duration within ±0.001 s, peak < .95, RMS >= .001 amplitude, and centroid within 250–4000 Hz. PCM8 has the intended sole format rejection; PCM16 passes cleanly. Integrated LUFS was null for both.

Explicit decoder commands, each exit **0**:

```sh
sox .shokunin/audio/corpus/live/round-52/alt/candidate_pcm8.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-52/alt/pcm8.f32
sox .shokunin/audio/corpus/live/round-52/alt/control_pcm16.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-52/alt/pcm16.f32
```

Direct float32 vector comparison command exited **0**: `python3 -c 'import numpy as np, pathlib; p=pathlib.Path(".shokunin/audio/corpus/live/round-52/alt"); a=np.fromfile(p/"pcm8.f32",dtype="<f4"); b=np.fromfile(p/"pcm16.f32",dtype="<f4"); print("count8",len(a),"count16",len(b),"exact",bool(np.array_equal(a,b)),"max_abs_diff",float(np.max(np.abs(a-b))),"decoded_peak",float(np.max(np.abs(a))),"decoded_rms",float(np.sqrt(np.mean(a.astype(np.float64)**2))))'`. Result: 5760 samples each, exact equality true, maximum absolute difference 0.0, decoded peak 0.34375, decoded linear RMS 0.1781972221910576. This is equality for this deliberately grid-matched construction only.

No iteration, failed numeric fit, command failure, or transcription correction occurred.
