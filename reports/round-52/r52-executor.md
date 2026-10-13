# Round 52 executor — PCM8/PCM16 matched UI-shaped pair

## Scope and construction

Read the R52 declaration in `.shokunin/audio/LOG.md`. Generated an original 5760-frame, mono, 48000 Hz unsigned PCM8 WAV and paired signed PCM16 WAV in this role's scratch directory. PCM8 samples are a 1 kHz plus 1.5 kHz two-sine signal quantized to unsigned bytes as `round(x*127+128)` and clipped to 0–255. PCM16 was constructed exactly as `(unsigned8 - 128) * 256`. Both WAVs therefore contain 5760 frames / 0.120 s. This is a deliberately matched integer-grid pair, not a general conversion test.

Generation command (exit 0):

```sh
python3 .shokunin/audio/corpus/live/round-52/executor/generate.py
```

WAV SHA-256: PCM8 `74dd0a3d7a5218e9ead995d14f118beb2118c0f163ce086d406415ce368efb37`; PCM16 `b09eb7e624813cd9734e6f4c3b373f7842fb44900737138d7c841c1ad2333344`. Encoded stream SHA-256: PCM8 `94c51f39c644ffaa4da3792e221ef20dca6af8f67f7f9ed7c2085f0ffbbba966`; PCM16 `5e3ece2a1609be5e5a315b83e6594bb1a9a688812f4921bb51b8da9ed89f2af3`.

## ffprobe and project measurements

For each file, this command exited 0:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json <candidate.wav>
```

PCM8 reported `codec_name=pcm_u8`, 8 bits, 48000 Hz, mono, duration `0.120000`; PCM16 reported `codec_name=pcm_s16le`, 16 bits, 48000 Hz, mono, duration `0.120000`.

The project-measurer invocation exited 0:

```sh
python3 .shokunin/audio/corpus/live/round-52/executor/measure.py .shokunin/audio/corpus/live/round-52/executor .shokunin/audio/corpus/fixtures/measure_audio.py
```

It calls the unchanged `measure(path, SPECS["ui"], path)` implementation. Both SoX-f32 project measurements: duration `0.12 s`; rate 48000 Hz; mono; peak `0.3125` full scale; RMS `-14.699802598426999 dBFS`; spectral centroid `1581.8516662990894 Hz`; spectral bandwidth `2515.291000915814 Hz`; integrated LUFS `null`. PCM8 failures were exactly [`format: expected PCM16`]; PCM16 failures were `[]`. Thus both pass the UI numeric gates: duration within ±1 ms, peak below .95, RMS above .001, centroid within 250–4000 Hz. Rate/channel pass on both; PCM8's sole failed gate is the intended format/depth check.

Explicit SoX decode commands, each exit 0:

```sh
sox .shokunin/audio/corpus/live/round-52/executor/pcm8.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-52/executor/pcm8.f32
sox .shokunin/audio/corpus/live/round-52/executor/pcm16.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-52/executor/pcm16.f32
```

Each output contains 5760 little-endian float32 samples. Compared decoded vectors: exact elementwise equality, maximum absolute difference `0.0`; decoded peak `0.3125`, RMS `0.1840813836609962` (linear full scale). The project measurement values above are from the project's own SoX-f32 stdout decode path.

## Setup event and limits

An initial project-measurement attempt against scratch under repository-root `corpus/live/round-52/executor/` exited 1 with `ValueError: ... is not in the subpath .../.shokunin/audio/corpus`, because the project measurer returns paths relative to its corpus root. I moved the scratch to the allowed `.shokunin/audio/corpus/live/round-52/executor/` location and reran the measurement successfully; the initial path error is setup, not a gate failure. No candidate iteration or failed numeric fit occurred. No transcription was performed. This report is limited to this constructed pair and these measurements; decoded equality does not establish general PCM8/PCM16 equivalence, fidelity, audibility, quality, production, rights, engine behavior, or promotion.
