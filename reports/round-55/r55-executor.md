# Round 55 executor — PCM16 container-header matched UI pair

## Construction

Read the R55 declaration in `.shokunin/audio/LOG.md`. Generated an original 5,760-frame (0.120 s), mono 48,000 Hz signed PCM16 UI-shaped signal in `.shokunin/audio/corpus/live/round-55/executor/`. The sample values are rounded `32767 * (.25*sin(2*pi*1000*t) + .08*sin(2*pi*1500*t))` and shared byte-for-byte between the two containers. `pcm16-tag1.wav` is conventional `WAVE_FORMAT_PCM` (tag 1, 16-byte fmt). `extensible-40.wav` is `WAVE_FORMAT_EXTENSIBLE` (tag `0xfffe`, 40-byte fmt, `cbSize=22`, valid bits 16, channel mask `0x4`, PCM subtype GUID `0100000000001000800000aa00389b71`). Both use block align 2, byte rate 96000, and identical 11,520-byte sample data.

Generation command (exit **0**):

```sh
python3 ".shokunin/audio/corpus/live/round-55/executor/generate.py"
```

| File | Bytes | WAV SHA-256 |
|---|---:|---|
| `pcm16-tag1.wav` | 11,564 | `9ac26f38a7df9b1dd60c6130049d1e37056811fcd241f15a03559b5766bb4ba9` |
| `extensible-40.wav` | 11,588 | `bd7d95901935c0effe21fd64e44a47487372be9d0c80f86cc725380df0352f47` |

## Actual metadata and UI gate

Ran ffprobe on each candidate (each exit **0**):

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json <file>
```

Both report `codec_name=pcm_s16le`, `sample_fmt=s16`, `bits_per_sample=16`, 48,000 Hz, one channel, duration `.120000` s. The project measure call (one per file, each exit **0**) was:

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.measure("ui",m.SPECS["ui"],Path("<absolute-file-path>")))'
```

Both receipts: 5760 decoded samples; duration `.12 s`; peak `0.31536865234375`; RMS `-14.628519169868087 dBFS`; centroid `1123.322704293326 Hz`; bandwidth `276.15444981222976 Hz`; integrated LUFS `null`; failures `[]`. Thus both satisfy the existing UI duration, level, spectral, channel/rate and PCM16 checks. This is the project measurement function with the unchanged UI spec, not evidence of an integrated runner receipt.

## Decoder equality

Each SoX decoder command exited **0**:

```sh
sox ".shokunin/audio/corpus/live/round-55/executor/pcm16-tag1.wav" -t f32 -e floating-point ".shokunin/audio/corpus/live/round-55/executor/tag1.f32"
sox ".shokunin/audio/corpus/live/round-55/executor/extensible-40.wav" -t f32 -e floating-point ".shokunin/audio/corpus/live/round-55/executor/extensible.f32"
```

Compared resulting little-endian float32 vectors: 5,760 samples each, `array_equal=True`, maximum absolute difference `0.0`. Both decoded files have SHA-256 `d80f13858e4fdcf641f2164b440a99a42711fd4213239ad809c8136ee4620ce7`.

## Limits

Evidence is bounded to these matched mono PCM16 fixtures, this exact valid-16/mask-0x4 extensible header, ffprobe/SoX in this environment, and the existing UI measurement function. No claim about all extensible headers, other channel layouts/subtypes, integrated runner exits or validation replay, perceptual quality, general conversion/fidelity, production, rights, engine behavior, or publishing. Scratch files are confined to `corpus/live/round-55/executor/`; no shared source, LOG, SCORECARD, canonical artifact, or other report was changed, and no commit/push was made.
