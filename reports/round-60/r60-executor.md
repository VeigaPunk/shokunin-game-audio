# Round 60 executor — extensible PCM16 valid-bits 0/16 pair

## Setup and original payload

Used the repository's existing Python/NumPy environment and host `ffprobe`/`sox`; no new dependencies or project/source edits. Scratch scripts, WAVs, and decoded vectors are confined to `.shokunin/audio/corpus/live/round-60/executor/`. The pair was generated from scratch as 5,760 signed PCM16 mono samples at 48 kHz (120 ms), with the same 11,520-byte payload in both files. The payload SHA-256 is `6e76d877b1e153b636b883f06dea7d3fd7f43374a72fa2cba678c8f4560c9711`; sample range is −2703..2702. Generation formula: `round(8191*(.24*sin(2π·997*i/48000)+.09*sin(2π·1633*i/48000)))` for `i=0..5759`.

Exact generation command (exit **0**):

```sh
python3 ".shokunin/audio/corpus/live/round-60/executor/generate.py"
```

## Direct RIFF header inspection

Exact command (exit **0**):

```sh
python3 ".shokunin/audio/corpus/live/round-60/executor/inspect.py"
```

The parser found for both files: RIFF/WAVE, file size 11,588, RIFF size 11,580, `fmt ` size 40, format tag `0xfffe`, one channel, 48,000 Hz, byte rate 96,000, block align 2, 16-bit container, `cbSize=22`, channel mask `0x4`, PCM subtype GUID `0100000000001000800000aa00389b71`, data size 11,520 bytes, and identical payload SHA-256 above. Only valid-bits differs:

| File | `wValidBitsPerSample` | WAV SHA-256 |
|---|---:|---|
| `valid-0.wav` | 0 (invalid/unspecified declaration; not a conforming positive case) | `5ab169fc3f43b29c0bb17cc86e6b76fb424e590b7d788a503a002501c8a2f394` |
| `valid-16.wav` | 16 (control) | `d7f08d659b608e003e5ef2aaccf325dae3bd4e961caeaa450bd933c406b4cc46` |

## ffprobe metadata

Exact command for valid0 (exit **0**):

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json ".shokunin/audio/corpus/live/round-60/executor/valid-0.wav"
```

The same command with `valid-16.wav` in place of `valid-0.wav` also exited **0**. Both report `pcm_s16le`, sample format `s16`, 48,000 Hz, mono, 16 bits/sample, and duration `0.120000`. ffprobe exposes container/codec metadata here; it did not report or validate the distinct valid-bits field.

## SoX decode

Exact commands (each exit **0**):

```sh
sox ".shokunin/audio/corpus/live/round-60/executor/valid-0.wav" -t f32 -e floating-point ".shokunin/audio/corpus/live/round-60/executor/valid-0.f32"
sox ".shokunin/audio/corpus/live/round-60/executor/valid-16.wav" -t f32 -e floating-point ".shokunin/audio/corpus/live/round-60/executor/valid-16.f32"
```

Each decoded vector has 5,760 float32 samples, SHA-256 `adc56a24cd7a2bc4c34ef6112b384b3567f6d6b1e4568aef0c8722f6170dca6c`, range −0.082489013671875..0.08245849609375. Vector comparison: exactly equal; maximum absolute difference `0.0`.

## Direct unchanged project UI measurement

For each file, I called the unchanged `measure_audio.measure("ui", SPECS["ui"], Path(file))` function directly. Exact valid0 command (exit **0**):

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.measure("ui",m.SPECS["ui"],Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-60/executor/valid-0.wav")))'
```

The exact same command with the final filename changed to `valid-16.wav` exited **0**. Both outputs have `duration_s: 0.12`, 48,000 Hz mono `pcm_s16le`/16-bit, peak `0.082489013671875`, RMS `-26.87354274685677 dBFS`, integrated LUFS `null`, centroid `2139.5871109211243 Hz`, bandwidth `3627.575019576501 Hz`, and `failures: []`. These are direct local measurements, not integrated runner receipts.

## Bounded result

On this host and this one malformed valid-bits=0 fixture, ffprobe and SoX accepted and decoded it as PCM16; the unchanged direct UI measurement also passed. This is evidence only that this local path did not reject the zero declaration. It does not establish standards conformance, universal decoder behavior, valid-bit enforcement, real zero-bit audio, precision/fidelity, audibility, quality, production, rights, engine, publishing, or promotion. No project measurement code, gates, thresholds, canonical artifacts, shared source, LOG, SCORECARD, or other reports were changed. No commit or push was made.
