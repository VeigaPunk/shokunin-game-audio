# R51 critic — codec branch isolation and decoded PCM equivalence

## Boundary and claim tested

I inspected the R51 LOG declaration and the executor's original scratch pair at `corpus/live/round-51/executor/`. I did not change source, LOG, scorecard, canonical artifacts, or other reports. The tested proposition is narrowly: with this paired UI fixture, the PCM24 container/codec is rejected only by the existing PCM16 format check while duration, level, and centroid pass; the PCM16 control passes. This is not a test of a full-resolution 24-bit signal or of broad conversion behavior.

## Exact evidence

Commands run from the repository root:

1. `python3 .shokunin/audio/corpus/live/round-51/executor/generate_pair.py` — exit 0. Generator printed intended PCM16 sample-payload SHA-256 `3b26aaa8b60745085717b8ffa2fb8ab62e4f619222a29992ea2ef282a558cd90` and PCM24 scaled-int payload SHA-256 `40985c8f7f8978b8c5c06c0ab90e3e357e65b1ac0e085bb68ff6ba498bcc0df1` (lengths 11520 and 23040 bytes). The PCM24 values are the PCM16 integer samples multiplied by 256; the fixture does not exercise additional 24-bit precision.

2. For each file, `ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json <file>` — exit 0. Actual metadata:
   - `pair_pcm16.wav`, file SHA-256 `2d201f849ecb416401b15c88e172527f9beec852c8998123f5f06131c712fee0`: `codec_name=pcm_s16le`, `sample_fmt=s16`, `sample_rate=48000`, `channels=1`, `bits_per_sample=16`, duration `0.120000`.
   - `pair_pcm24.wav`, file SHA-256 `6d3f804579124af4fb14f8d7313b25fb87231ca9729a434661475939cae601c8`: `codec_name=pcm_s24le`, `sample_fmt=s32`, `sample_rate=48000`, `channels=1`, `bits_per_sample=24`, duration `0.120000`.

3. Ran the unchanged project `measure()` against each scratch file, without editing project code. Exact command (from repository root):

```sh
python3 -c 'import sys,json; sys.path.insert(0,".shokunin/audio/corpus/fixtures"); import measure_audio as m; from pathlib import Path; root=m.ROOT; print(json.dumps({name:m.measure(name,m.SPECS["ui"],root/"live/round-51/executor"/file) for name,file in [("pcm16","pair_pcm16.wav"),("pcm24","pair_pcm24.wav")]},indent=2))'
```

Exit 0. Returned metrics:
   - PCM16: rate 48000, mono, `pcm_s16le`/16-bit; duration `0.12`; peak `0.315399169921875`; RMS `-14.628083420045229 dBFS`; centroid `1123.8154138173777 Hz`; bandwidth `292.5430341707052 Hz`; failures `[]`.
   - PCM24: rate 48000, mono, `pcm_s24le`/24-bit; duration `0.12`; peak `0.315399169921875`; RMS `-14.628083420045229 dBFS`; centroid `1123.8154138173777 Hz`; bandwidth `292.5430341707052 Hz`; sole failure `format: expected PCM16`.

Returned metrics:
   - PCM16: rate 48000, mono, `pcm_s16le`/16-bit; duration `0.12`; peak `0.315399169921875`; RMS `-14.628083420045229 dBFS`; centroid `1123.8154138173777 Hz`; bandwidth `292.5430341707052 Hz`; failures `[]`.
   - PCM24: rate 48000, mono, `pcm_s24le`/24-bit; duration `0.12`; peak `0.315399169921875`; RMS `-14.628083420045229 dBFS`; centroid `1123.8154138173777 Hz`; bandwidth `292.5430341707052 Hz`; sole failure `format: expected PCM16`.

4. For each file, `sox <file> -t f32 -e floating-point -` — exit 0, empty stderr. The project decodes each to 5760 float32 samples. Decoded byte SHA-256 for both is `f8b9869aa517d5a1e84451610c82a25fc971335328aa1f1fab2141ec06399943`; direct array comparison: `array_equal=True`, maximum absolute difference `0.0`, differing sample count `0`. Thus on these fixtures SoX's decoded samples are exactly equal, with no observed normalization change. The independent file/container bytes and PCM payload bytes are not equal; this equivalence is of the decoded sample vectors only.

The only rejected gate is the PCM24 codec/bits predicate. The 16-bit control is clean. Both satisfy the remaining ordinary UI measurement gates. No numeric candidate fit failed; there was no transcription. No command/setup error occurred in this critic check.

## Falsification limit / assessment

This evidence supports isolation of the format branch for this deliberately matched pair. It does **not** establish that full-resolution PCM24, with nonzero lower eight bits, decodes equivalently to PCM16; the executor's PCM24 samples are PCM16-quantized values shifted into the 24-bit container. It also does not establish general SoX conversion or normalization behavior. `sample_fmt=s32` in ffprobe describes FFmpeg's reported representation for this PCM24 stream; the measured SoX float output is the direct evidence used for sample equality. No codec-family, sound-quality, perception, production, rights, engine, publishing, or promotion inference follows.
