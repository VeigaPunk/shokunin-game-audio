# Round 59 executor — extensible PCM16 valid-bits 13/16 pair

## Original fixture and RIFF evidence

Generated from scratch in `.shokunin/audio/corpus/live/round-59/executor/`: 120 ms, mono 48 kHz, 5,760-frame signed PCM16 UI-shaped two-tone signal. Quantized signed samples are all divisible by eight (13-bit left-aligned values). Both WAVs have the same 11,520-byte payload; only `wValidBitsPerSample` differs (13 versus 16).

Generation command (exit **0**):

```sh
python3 ".shokunin/audio/corpus/live/round-59/executor/generate.py"
```

Payload was synthesized as `round(8191*(.24*sin(2π·997t)+.09*sin(2π·1633t)))*8`. Payload SHA-256: `88cac2a0475a0fdbedc4be3758a2215b3937219f13a5c8ff0515a10f1e09ccd1`; 5,760 signed samples, range −21,624..21,616; all divisible by eight.

Direct RIFF parser command (exit **0**):

```sh
python3 ".shokunin/audio/corpus/live/round-59/executor/inspect_headers.py"
```

| File | Bytes | WAV SHA-256 | Valid bits | RIFF size | fmt/tag | cbSize | Mask | Payload bytes/SHA-256 |
|---|---:|---|---:|---:|---|---:|---:|---|
| `valid-13.wav` | 11,588 | `873485d5dd0d5108f0523ab974cbba6ce792e715861d481db0ad68ea35f2f2e0` | 13 | 11,580 | 40 / `0xfffe` | 22 | `0x4` | 11,520 / `88cac2a0475a0fdbedc4be3758a2215b3937219f13a5c8ff0515a10f1e09ccd1` |
| `valid-16.wav` | 11,588 | `c8f327e38f34125a15bfe3e490905852a228ba26436b0a3b1633a6f58a4a1f3b` | 16 | 11,580 | 40 / `0xfffe` | 22 | `0x4` | 11,520 / same |

Both direct parses also report WAVE, 1 channel, 48,000 Hz, byte rate 96,000, block align 2, 16-bit container and PCM subtype GUID `0100000000001000800000aa00389b71`. This confirms the valid-bits field is the only file difference; payload equality and all-divisible-by-eight were checked from raw bytes/samples.

## ffprobe and SoX

For `valid-13.wav`, exact ffprobe command (exit **0**):

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json ".shokunin/audio/corpus/live/round-59/executor/valid-13.wav"
```

The same command substituting `valid-16.wav` also exited **0**. Both report `pcm_s16le`, `s16`, 48,000 Hz, mono, 16 bits/sample, duration `0.120000`; these are codec/container observations, while RIFF parsing established valid-bits values.

Exact SoX decode commands (each exit **0**):

```sh
sox ".shokunin/audio/corpus/live/round-59/executor/valid-13.wav" -t f32 -e floating-point ".shokunin/audio/corpus/live/round-59/executor/valid-13.f32"
sox ".shokunin/audio/corpus/live/round-59/executor/valid-16.wav" -t f32 -e floating-point ".shokunin/audio/corpus/live/round-59/executor/valid-16.f32"
```

Both vectors contain 5,760 float32 samples, SHA-256 `afb6ad28ef01a4ed9f3a9ebf4423ee7fc7324982f1ed3fd5ad2a711c6c84c3b7`, range −0.659912109375..0.65966796875. Direct vector comparison found exact equality and maximum absolute difference `0.0`.

## Direct unchanged project UI measurements

For valid13, exact direct measurement command (exit **0**):

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.measure("ui",m.SPECS["ui"],Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-59/executor/valid-13.wav")))'
```

The same command substituting `valid-16.wav` also exited **0**. Both measured 5,760 samples, `.12` s, 48 kHz mono `pcm_s16le`/16-bit, peak `0.659912109375`, RMS `-8.811743007017897 dBFS`, integrated LUFS `null`, centroid `2139.5871109211243 Hz`, bandwidth `3627.575019576501 Hz`, and `failures: []`. These are direct calls to the unchanged UI measurement function and show both candidates pass its local UI gates; they are not integrated runner receipts.

## Scope and limitations

This is one original matched extensible PCM16 pair, one all-divisible-by-eight payload, and the observed local ffprobe/SoX/project path. Equal decoding here does not show that these tools enforce valid-bit metadata or that 13-bit precision is preserved; nor does it generalize to other headers, payload alignment, decoders or formats. No audibility, quality, production, rights, engine, publishing or promotion claim. All scratch scripts, WAVs and decoded vectors are confined to `.shokunin/audio/corpus/live/round-59/executor/`; this report is the only report written. No shared source, LOG, SCORECARD, canonical artifact, or other report was changed; no commit or push was made.
