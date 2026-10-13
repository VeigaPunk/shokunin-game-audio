# R55 independent alternate — PCM16 standard/extensible WAV pair

## Construction

Read the R55 declaration in `.shokunin/audio/LOG.md`. Independently generated an original UI-shaped signal (5760 frames, mono, 48,000 Hz, 0.120 s) as signed PCM16 and wrote identical audio payload bytes in two RIFF/WAVE containers under `.shokunin/audio/corpus/live/round-55/alt/`:

- `standard_pcm16.wav`: ordinary `WAVE_FORMAT_PCM` (`fmt ` size 16, format tag `0x0001`).
- `extensible_pcm16.wav`: `WAVE_FORMAT_EXTENSIBLE` (`fmt ` size 40, format tag `0xfffe`), `cbSize=22`, valid bits 16, mono front-center mask `0x4`, PCM subtype GUID `00000001-0000-0010-8000-00aa00389b71` (on-disk little-endian encoding).

The source is `.19*sin(2π·613t)+.095*sin(2π·1733t)+.04*sin(2π·2963t)`, rounded/clipped to signed 16-bit. This is an independent positive container-header comparison, not additional audio-format coverage beyond this pair.

Generation command (exit **0**):

```sh
python3 .shokunin/audio/corpus/live/round-55/alt/generate_pair.py
```

| WAV | Bytes | SHA-256 |
|---|---:|---|
| `standard_pcm16.wav` | 11,564 | `2990a941350fb33f6dbf7aa240c3b5d0406e89028a62830660d783da46c1a328` |
| `extensible_pcm16.wav` | 11,588 | `01a31143b9dd3d152171907e6d0054eb2cee645929d4ae61af2a7a7f38a2ca9d` |

## Actual ffprobe metadata and project-path gate measurements

Ran this command separately on each WAV; both exited **0**:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json <absolute-WAV-path>
```

For **both**, ffprobe returned `codec_name=pcm_s16le`, `sample_fmt=s16`, `bits_per_sample=16`, `sample_rate=48000`, `channels=1`, and `duration=0.120000`.

Ran the project's unchanged measurement function separately on each WAV; each command exited **0** and returned an empty `failures` list:

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.measure("ui",m.SPECS["ui"],Path("<absolute-WAV-path>")))'
```

Both measured: duration `.12 s`; 48,000 Hz mono; peak `0.323333740234375`; RMS `-16.315817708608765 dBFS`; integrated LUFS `null`; centroid `1648.5403647314727 Hz`; bandwidth `2740.7132308931346 Hz`. Both pass the unchanged UI checks: duration within ±1 ms, peak <.95, RMS >=.001, centroid 250–4000 Hz, mono/48 kHz, and PCM16 codec/bit depth.

## Decode comparison

SoX decoded each file to f32; each command exited **0**:

```sh
sox .shokunin/audio/corpus/live/round-55/alt/standard_pcm16.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-55/alt/standard.f32
sox .shokunin/audio/corpus/live/round-55/alt/extensible_pcm16.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-55/alt/extensible.f32
```

Comparison command (exit **0**):

```sh
python3 -c 'import numpy as n; from pathlib import Path; p=Path(".shokunin/audio/corpus/live/round-55/alt"); a=n.fromfile(p/"standard.f32",dtype="<f4"); b=n.fromfile(p/"extensible.f32",dtype="<f4"); print(len(a),len(b),n.array_equal(a,b),float(n.max(n.abs(a-b))),int(n.count_nonzero(a!=b)))'
```

Output: `5760 5760 True 0.0 0`; vectors were elementwise equal for this constructed pair.

## Limits

Evidence is bounded to these two ordinary mono PCM16 WAV headers, this payload, ffprobe, SoX, and the current project UI measurement path. It does not establish support for every extensible WAV subtype, channel mask, valid-bit arrangement, channel count, or codec; nor arbitrary audio fidelity, audibility, quality, production suitability, rights, engine behavior, or promotion. I did not change shared source, LOG, SCORECARD, canonical fixtures, or other reports, and did not commit or push.
