# Round 58 executor — extensible PCM16 valid-bits 14/16 pair

## Build and header evidence

Generated a new UI-shaped 120 ms, mono 48 kHz, 5,760-frame signed16 signal: two sine components at 1,000 Hz and 1,500 Hz, quantized to multiples of four (14-bit left-aligned signed samples). The two files have byte-identical 11,520-byte PCM payloads; only `wValidBitsPerSample` changes. Files and generator are confined to `corpus/live/round-58/executor/`.

Generation command (exit **0**):

```sh
python3 ".shokunin/audio/corpus/live/round-58/executor/generate.py"
```

| File | Bytes | WAV SHA-256 | Payload SHA-256 |
|---|---:|---|---|
| `valid-14.wav` | 11,588 | `6b4b07d1eee022f99116a043b444821914acc68110544a644ba7204f3a63fb26` | `0b40e3c0f28aa6a50937f87c0fa260b2100f97572dbc8fdf517cea981e79b4fc` |
| `valid-16.wav` | 11,588 | `738263969d226d31a0525bbad1c7dda8609b270dd3ec8fa82645905d4667a7f2` | same |

Independent direct RIFF byte parsing found for both: RIFF size 11,580; WAVE; fmt size 40; tag `0xfffe`; channels 1; sample rate 48,000; byte rate 96,000; block align 2; container bits 16; `cbSize=22`; speaker mask `0x4`; PCM subtype GUID `0100000000001000800000aa00389b71`; data size 11,520. `wValidBitsPerSample` is 14 and 16 respectively. All 5,760 signed16 payload values are divisible by four. Payload bytes and SHA are identical; valid-bits field is the sole file difference.

## ffprobe, SoX, and project measurement

For each file, this exact ffprobe command exited **0**:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json ".shokunin/audio/corpus/live/round-58/executor/valid-14.wav"
```

Same command with `valid-16.wav` also exited **0**. Both reported `codec_name=pcm_s16le`, `sample_fmt=s16`, 48,000 Hz, 1 channel, 16 bits/sample, duration `0.120000`. The RIFF parse, not ffprobe, established the valid-bit fields.

SoX command for each file exited **0** (second path substituted `valid-16.wav`):

```sh
sox ".shokunin/audio/corpus/live/round-58/executor/valid-14.wav" -t f32 -e floating-point ".shokunin/audio/corpus/live/round-58/executor/valid-14.wav.f32"
```

Each output contains 5,760 float32 samples and has SHA-256 `ca42332f650f6e2361ebd56649629322a85bb3d72d03e2b2861a112c36915aa8`. Direct vector comparison found exact equality, max absolute difference `0.0`.

Ran the unchanged project measurement function separately for each absolute file path. The exact command for valid14 (exit **0**) was:

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.measure("ui",m.SPECS["ui"],Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-58/executor/valid-14.wav")))'
```

The same command using `valid-16.wav` also exited **0**. Both results: 5,760 samples; duration `.12`; 48 kHz mono `pcm_s16le`/16-bit; peak `0.3153076171875`; RMS `-14.629479252569332 dBFS`; integrated LUFS `null`; centroid `1129.9910331085607 Hz`; bandwidth `412.58546294347246 Hz`; failures `[]`. These are direct calls to the unchanged measurement function, not integrated runner receipts or runner exit statuses. The project UI gates passed for both.

## Setup note and limits

My first direct-measurement commands used relative WAV paths; each exited **1** because the unchanged function's returned path is required to be relative to its corpus root. This was a path/setup error after the probe/SoX computations, not a format or decode failure and not a runner receipt. Re-running with absolute input paths produced the successful direct measurements above. No selected ffprobe or SoX decode failed; no numeric gate failed.

Evidence covers only this matched, synthetic 14-versus-16-valid-bit extensible PCM16 pair, the stated payload/header, and this host's ffprobe/SoX/project measurement path. It does not establish general valid-bit metadata enforcement, 14-bit fidelity, universal WAVE extensible/decoder compatibility, audible quality, production suitability, rights, engine behavior, or publishing. No shared source, LOG, SCORECARD, canonical artifact, or other report was changed; no commit or push was made.
