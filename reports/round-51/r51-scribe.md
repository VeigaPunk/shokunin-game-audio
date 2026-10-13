# R51 scribe — measured metadata and decoded metrics

Scope: report only measurements available in the workspace at scribing time. R51 is **integrated pending**; this is not a round verdict. The declared comparison is a 5760-frame mono 48 kHz PCM24 versus PCM16 UI-shaped pair, checked against unchanged `SPECS["ui"]` (`.12 s`, centroid 250–4000 Hz; rate/channel, PCM16, duration ±1 ms, peak <.95, RMS ≥.001). No broad inference follows.

## Decision table

| Candidate | ffprobe metadata (exit 0) | SoX-decoded project metrics | `measure(..., SPECS["ui"])` result |
|---|---|---|---|
| `corpus/live/round-51/executor/pair_pcm16.wav` | `pcm_s16le`, 16 bits, 48000 Hz, mono, `.120000 s` | peak `.315399169921875`; RMS `-14.628083420045229 dBFS`; whole-vector positive-frequency centroid `1123.8154138173777 Hz`; bandwidth `292.5430341707052 Hz`; 5760 samples | no failures; clean exit-equivalent measurement |
| `corpus/live/round-51/executor/pair_pcm24.wav` | `pcm_s24le`, 24 bits, 48000 Hz, mono, `.120000 s` | peak `.315399169921875`; RMS `-14.628083420045229 dBFS`; centroid `1123.8154138173777 Hz`; bandwidth `292.5430341707052 Hz`; 5760 samples | sole failure: `format: expected PCM16` (the intended format distinction); no duration, level, or centroid numeric failure |

The original generator at `corpus/live/round-51/executor/generate_pair.py` says it quantizes one common normalized signal to PCM16 and represents the same integer values at PCM24 by scaling ×256. Both generated WAV whole-file SHA-256 values differ as expected for separate encodings: PCM16 `2d201f849ecb416401b15c88e172527f9beec852c8998123f5f06131c712fee0`; PCM24 `6d3f804579124af4fb14f8d7313b25fb87231ca9729a434661475939cae601c8`. The SoX-decoded f32 byte streams have identical SHA-256 `f8b9869aa517d5a1e84451610c82a25fc971335328aa1f1fab2141ec06399943`, consistent with these particular inputs; this is not a general bit-depth conversion claim.

## Commands and exits

Executed from repository root. Each ffprobe command below exited **0** and returned the metadata shown above:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-51/executor/pair_pcm16.wav
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-51/executor/pair_pcm24.wav
```

Both decoded-stream hash commands exited **0**:

```sh
sox .shokunin/audio/corpus/live/round-51/executor/pair_pcm16.wav -t f32 -e floating-point - -V0 | sha256sum
sox .shokunin/audio/corpus/live/round-51/executor/pair_pcm24.wav -t f32 -e floating-point - -V0 | sha256sum
```

The project measurement was performed for both inputs using the existing `measure_audio.py` module’s `measure("ui", SPECS["ui"], path)` (its implementation invokes ffprobe, SoX `-t f32 -e floating-point`, and ffmpeg ebur128). Both returned measurement objects above. An initial ad hoc invocation with *relative* WAV paths raised `ValueError` at `path.relative_to(ROOT)`; this was a **setup/path issue**, not a failed candidate measurement. Retrying with resolved absolute WAV paths worked. The resulting PCM24 `format: expected PCM16` is an expected predicate result, not setup failure or a numeric fit failure.

No speech/transcription command or transcription result was present in this check. Treat transcription as **not tested**, not as a pass or failure. No candidate had a failed numeric fit. Scope is only these two measured files and the project’s flattened decoded-vector metrics; this says nothing broader about codecs, perception, quality, production, rights, engines, publishing, or promotion.
