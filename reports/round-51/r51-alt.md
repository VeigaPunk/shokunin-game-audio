# R51 alternate independent PCM24/PCM16 UI pair

## Scope and result

Independent original deterministic fixture pair measured with the unchanged project `measure(..., SPECS["ui"])` path. The sole codec failure is isolated: PCM24 has only `format: expected PCM16`; PCM16 is clean. This is evidence for this fixture and UI measurement only. No broad codec, conversion, quality, perception, production, rights, engine, publishing, or promotion inference.

## Generation

Generated 5,760 mono samples at 48,000 Hz: 1 kHz sinusoid at 0.25 full scale, with PCM16 integers `round(0.25*32767*sin(2*pi*1000*i/48000))`. PCM24 uses each PCM16 integer multiplied by 256, the corresponding signed 24-bit scaling. Both WAVs are original and under `corpus/live/round-51/alt/`; source: `generate_pair.py`.

Command: `python3 .shokunin/audio/corpus/live/round-51/alt/generate_pair.py` — exit **0**.

- `candidate_pcm24.wav`: SHA-256 `1b800add20c7ea7a2093d61e8070ac8f58beb3d314f84075f883b44bd4d42bc7`; 17,324 bytes.
- `control_pcm16.wav`: SHA-256 `d2fb12b0a2b110baa63990184404aaf038d8acf80373c5ca1d6734e738fb7d49`; 11,564 bytes.

## Actual ffprobe metadata

Commands, both exit **0**:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-51/alt/candidate_pcm24.wav
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-51/alt/control_pcm16.wav
```

| File | codec_name | bits_per_sample | sample_rate | channels | duration |
|---|---|---:|---:|---:|---:|
| candidate_pcm24.wav | pcm_s24le | 24 | 48000 | 1 | 0.120000 s |
| control_pcm16.wav | pcm_s16le | 16 | 48000 | 1 | 0.120000 s |

## Project SoX-f32 decoded metrics and gate result

Project analysis command: `python3 .shokunin/audio/corpus/live/round-51/alt/measure_pair.py` — exit **0**. It imports `corpus/fixtures/measure_audio.py`, uses the unchanged `measure(..., (.12,250,4000,False), path)` implementation, including SoX float32 decode. Thresholds were not changed.

| File | SoX decoded count | duration_s | peak_full_scale | rms_dbfs | whole-wave spectral_centroid_hz | bandwidth_hz | failures |
|---|---:|---:|---:|---:|---:|---:|---|
| candidate_pcm24.wav | 5760 | 0.12 | 0.25 | -15.051713380047701 | 1001.4515079742339 | 145.4016831789917 | `format: expected PCM16` only |
| control_pcm16.wav | 5760 | 0.12 | 0.25 | -15.051713380047701 | 1001.4515079742339 | 145.4016831789917 | none |

Both meet UI duration (±0.001 s), peak (<0.95), RMS (>=0.001 amplitude), and centroid (250–4000 Hz) conditions. `measure` records RMS in dBFS; decoded linear RMS is 0.17677234819088997 for both. `integrated_lufs` was null for both.

Independent direct decoder comparison command: `python3 .shokunin/audio/corpus/live/round-51/alt/decode_compare.py` — exit **0**. Both decode to 5,760 samples; the float arrays are exactly equal in this test (`decoded_exact_equal=True`, maximum absolute difference `0.0`; decoded range −0.25 to +0.25). This result describes only this constructed pair; it does not generalize to PCM depths.

## Setup / failures

No fixture generation, ffprobe, or project measurement command failed. One REPL orchestration call mistakenly awaited the already-returned `BashResult`, raising `TypeError` after the generator command had completed; no shell command failure or measurement was involved. No failed numeric fits or corrected report transcription.
