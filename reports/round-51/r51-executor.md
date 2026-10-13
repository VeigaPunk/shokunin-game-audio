# Round 51 executor — PCM24/PCM16 matched UI-shaped pair

## Scope and method

Read the Round 51 declaration in `.shokunin/audio/LOG.md`. Generated two original, 5760-frame, mono, 48000 Hz WAV candidates in this report's scratch directory. Both encode the same quantized sample sequence: a 1 kHz sine plus a 1.5 kHz sine, quantized to PCM16; for PCM24 the same signed integer samples were scaled by 256. This intentionally makes normalized decoded samples identical, rather than assuming different-depth encodings decode identically. No source, LOG, SCORECARD, canonical fixtures, or other reports were changed.

Generation command (exit 0):

```sh
python3 .shokunin/audio/corpus/live/round-51/executor/generate_pair.py
```

The sample-stream SHA-256s printed by the generator were PCM16 `3b26aaa8b60745085717b8ffa2fb8ab62e4f619222a29992ea2ef282a558cd90` (11520 bytes) and PCM24 integer sequence bytes `40985c8f7f8978b8c5c06c0ab90e3e357e65b1ac0e085bb68ff6ba498bcc0df1` (23040 bytes). The underlying intended PCM16 samples hash is the same as the PCM16 stream hash. WAV-file SHA-256: PCM24 `6d3f804579124af4fb14f8d7313b25fb87231ca9729a434661475939cae601c8`; PCM16 `2d201f849ecb416401b15c88e172527f9beec852c8998123f5f06131c712fee0`.

## Probe results

Exact ffprobe command, exit 0 for each candidate:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json <candidate.wav>
```

Actual stream metadata for PCM24: `codec_name=pcm_s24le`, `sample_rate=48000`, `channels=1`, `bits_per_sample=24`; format duration `0.120000`. PCM16: `codec_name=pcm_s16le`, `sample_rate=48000`, `channels=1`, `bits_per_sample=16`; format duration `0.120000`.

Actual project measurement command (exit 0):

```sh
python3 .shokunin/audio/corpus/live/round-51/executor/measure_pair.py .shokunin/audio/corpus/fixtures/measure_audio.py .shokunin/audio/corpus/live/round-51/executor/pair_pcm24.wav .shokunin/audio/corpus/live/round-51/executor/pair_pcm16.wav
```

This calls the unmodified `measure(path, SPECS["ui"], path)` from the project fixture measurer, which decodes with SoX as `sox <candidate.wav> -t f32 -e floating-point -` and measures that whole-wave float vector. Project receipts for both give duration `0.12 s`, rate `48000 Hz`, mono, peak `0.315399169921875`, RMS `-14.628083420045229 dBFS`, centroid `1123.8154138173777 Hz`, bandwidth `292.5430341707052 Hz`, and integrated LUFS `null`. PCM24 has the sole failure `format: expected PCM16`; PCM16 has no failures. Thus each passes the intended duration (±1 ms), peak (<.95), non-silence (RMS >= .001), and centroid (250–4000 Hz) UI checks; format differs as intended.

Explicit SoX decoded-file checks (both commands exit 0):

```sh
sox .shokunin/audio/corpus/live/round-51/executor/pair_pcm24.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-51/executor/pair_pcm24.f32
sox .shokunin/audio/corpus/live/round-51/executor/pair_pcm16.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-51/executor/pair_pcm16.f32
```

Each decoded file is 23040 bytes = 5760 little-endian float32 samples. Both decoded vectors have peak `0.315399169921875`, RMS `0.18560763156982443` (−14.628083420045229 dBFS), and are elementwise identical (maximum normalized decoded difference `0.0`). The separate file-output SoX invocation confirms decoded count/equality; project centroid values above come from the fixture measurer's stdout decode path.

## Fits and limits

No candidate iteration or failed numeric fit occurred. Both satisfy the intended numeric UI gates on the first generated pair; the PCM24 expected format failure is the sole intentional predicate failure, and PCM16 passes cleanly. No transcription was performed. This reports only these candidates and the specified probe; it makes no broader codec, audio-quality, perception, production, rights, engine, publishing, or promotion claim.
