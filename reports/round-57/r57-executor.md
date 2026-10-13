# Round 57 executor — extensible PCM16 valid-bits pair

## Construction

Read the R57 declaration in `.shokunin/audio/LOG.md`. Generated original mono 48 kHz, 5,760-frame signed PCM16 UI-shaped audio from `round(32767 * (.25*sin(2*pi*1000*t) + .08*sin(2*pi*1500*t))`, with identical 11,520-byte PCM payloads. Both files use RIFF/WAVE, `fmt ` tag `0xfffe`, 40-byte format payload, `cbSize=22`, mono mask `0x4`, PCM subtype GUID bytes `0100000000001000800000aa00389b71`, and 16-bit container samples. Only `wValidBitsPerSample` differs: 15 vs 16.

Generation command (exit **0**):

```sh
python3 ".shokunin/audio/corpus/live/round-57/executor/generate.py"
```

| File | Bytes | WAV SHA-256 | Payload SHA-256 |
|---|---:|---|---|
| `valid-15.wav` | 11,588 | `d3835a35014b3536c1710aafed8a104ef32eaa84acb37c87213127785f18175c` | `67ea695da5665554f467cae513d0c2d3d62d588516299f7eb4872bf79d58df4e` |
| `valid-16.wav` | 11,588 | `bd7d95901935c0effe21fd64e44a47487372be9d0c80f86cc725380df0352f47` | `67ea695da5665554f467cae513d0c2d3d62d588516299f7eb4872bf79d58df4e` |

Independent RIFF field inspection command (exit **0**):

```sh
python3 ".shokunin/audio/corpus/live/round-57/executor/inspect.py"
```

Observed for each file: RIFF declared size 11,580; WAVE; fmt size 40; tag `0xfffe`; one channel; 48,000 Hz; block align 2; container bits 16; `cbSize=22`; mask `0x4`; PCM subtype GUID above. `valid-15.wav` reports valid bits 15 and `valid-16.wav` 16. Payload SHA-256 is identical, so the only header difference is the declared valid-bit field.

## ffprobe and unchanged project UI measurement

Ran this command separately for each absolute WAV path; both ffprobe commands exited **0**:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json <absolute-file-path>
```

Both returned `codec_name=pcm_s16le`, `sample_fmt=s16`, `sample_rate=48000`, `channels=1`, `bits_per_sample=16`, duration `0.120000` s. ffprobe reports container/decoded format, not the WAVE valid-bit field (verified directly from RIFF above).

Ran the unchanged project UI measurement function on each file; both commands exited **0**:

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.measure("ui",m.SPECS["ui"],Path("<absolute-file-path>")))'
```

Both results: decoded sample count **5,760**; duration **0.12 s**; peak **0.31536865234375**; RMS **-14.628519169868087 dBFS**; centroid **1123.322704293326 Hz**; bandwidth **276.15444981222976 Hz**; integrated LUFS `null`; failures `[]`. Thus each independently passes the unchanged project UI format and numeric checks in the direct project measurement function. This was not an integrated runner receipt or runner exit status.

## SoX decoding

Each command exited **0**:

```sh
sox ".shokunin/audio/corpus/live/round-57/executor/valid-15.wav" -t f32 -e floating-point ".shokunin/audio/corpus/live/round-57/executor/valid-15.wav.f32"
sox ".shokunin/audio/corpus/live/round-57/executor/valid-16.wav" -t f32 -e floating-point ".shokunin/audio/corpus/live/round-57/executor/valid-16.wav.f32"
```

The two outputs each contain 5,760 float32 samples and have SHA-256 `d80f13858e4fdcf641f2164b440a99a42711fd4213239ad809c8136ee4620ce7`. Direct array comparison: exactly equal, maximum absolute difference `0.0`. This is the measured outcome for this generated matched pair; it does not imply general valid-bit decoding behavior.

## Setup attempts and limits

Two executor command-construction attempts failed before any probe/measurement: an initial malformed shell command quoting of the generator returned exit **127** (`python3 <path>: No such file or directory`); the corrected exact generator command above then exited 0. A first inspection one-liner incorrectly constructed `valid-verifier.wav` and exited **1** with `FileNotFoundError`; it touched no fixture and produced no measurement. The corrected `inspect.py` command above exited 0. These are setup errors, not ffprobe/SoX decode failures, project fixture-format failures, or runner receipts. There was **no receiptless decode failure**: ffprobe, SoX, and direct UI measurement all succeeded for both files. No integrated runner was available/run by this executor.

Evidence is limited to these original matched mono PCM16-container files, valid bits 15 and 16, the stated headers, and this environment's ffprobe/SoX/project-measurement path. It does not establish universal WAVE_FORMAT_EXTENSIBLE conformance, other valid-bit/container combinations or decoders, conversion/fidelity, audibility/quality, production suitability, rights, engine behavior, or publishing. Scratch and generator/inspection scripts are confined to `.shokunin/audio/corpus/live/round-57/executor/`; this report is the only report written. No shared source, LOG, SCORECARD, canonical artifact, or other report was changed; no commit or push was made.
