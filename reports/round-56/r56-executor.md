# Round 56 executor — extensible PCM16 channel-mask pair

## Construction

Read the R56 declaration in `.shokunin/audio/LOG.md`. Generated original UI-shaped signed PCM16 mono audio at 48,000 Hz for 5,760 frames (0.120 s): `round(32767 * (.25*sin(2*pi*1000*t) + .08*sin(2*pi*1500*t))`. Both files have the exact same 11,520-byte little-endian signed sample payload. Both are WAVE_FORMAT_EXTENSIBLE: `fmt ` tag `0xfffe`, 40-byte format payload, `cbSize=22`, valid bits 16, PCM subtype GUID bytes `0100000000001000800000aa00389b71`; only the channel mask differs (`mask-0.wav` = `0x0`; `mask-4.wav` = `0x4`).

Generation command (exit **0**):

```sh
python3 ".shokunin/audio/corpus/live/round-56/executor/generate.py"
```

| File | Bytes | SHA-256 |
|---|---:|---|
| `mask-0.wav` | 11,588 | `3399ae3661b0ebd6eb4fe7c3a7cf6f4f97cd2d5ec259638164d93c810952a193` |
| `mask-4.wav` | 11,588 | `bd7d95901935c0effe21fd64e44a47487372be9d0c80f86cc725380df0352f47` |

## Actual metadata and project measurements

Ran this ffprobe command separately on both absolute paths; both exited **0**:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json <absolute-file-path>
```

For both, ffprobe returned `codec_name=pcm_s16le`, `sample_fmt=s16`, 48,000 Hz, one channel, 16 bits/sample, and duration `0.120000` s.

Ran the project's unchanged UI measurement function separately on each file (each command exit **0**):

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.measure("ui",m.SPECS["ui"],Path("<absolute-file-path>")))'
```

Both receipts report 5,760 decoded samples; duration `.12 s`; peak `0.31536865234375`; RMS `-14.628519169868087 dBFS`; centroid `1123.322704293326 Hz`; bandwidth `276.15444981222976 Hz`; integrated LUFS `null`; failures `[]`. Thus both pass the unchanged UI format and numeric checks in the project measurer.

## SoX decode equality

Each following command exited **0**:

```sh
sox ".shokunin/audio/corpus/live/round-56/executor/mask-0.wav" -t f32 -e floating-point ".shokunin/audio/corpus/live/round-56/executor/mask-0.wav.f32"
sox ".shokunin/audio/corpus/live/round-56/executor/mask-4.wav" -t f32 -e floating-point ".shokunin/audio/corpus/live/round-56/executor/mask-4.wav.f32"
```

Compared little-endian float32 outputs: 5,760 samples each, `array_equal=True`, maximum absolute difference `0.0`. Since the same sample payload was written into both WAVs, these decodes establish equality for this matched pair.

## Limits

Observed results support only these matched mono PCM16 files, the exact valid-bits-16 PCM-subtype extensible headers with masks `0x0` and `0x4`, and this environment's ffprobe/SoX/project measurement path. This executor did not run the integrated runner, verifier replay, or malformed-header cases. It does not establish support for other masks/layouts, other valid-bit arrangements/subtypes, universal standards conformance, other decoder versions, general fidelity, audibility/quality, production suitability, rights, engine behavior, or publishing. No shared source, LOG, SCORECARD, canonical artifact, or other report was changed; scratch is confined to `corpus/live/round-56/executor/`; no commit or push was made.
