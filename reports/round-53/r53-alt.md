# R53 independent alternate: matched float32/PCM16 UI pair

## Scope and construction

Read the R53 declared calibration claim in `.shokunin/audio/LOG.md`. This independently generated pair is under the permitted `corpus/live/round-53/alt/` scratch directory. It contains 5,760 mono samples at 48,000 Hz (0.120 s): a pulsed two-tone signal (887 Hz at .27 amplitude plus 1,777 Hz at .09 amplitude, with a 128-sample linear endpoint envelope). I quantized the signal once to signed PCM16 and encoded the same normalized samples as float32 (`s16 / 32768`). This is an intentionally matched pair, not a general float conversion or dynamic-range test.

Generation command — exit **0**:

```sh
python3 .shokunin/audio/corpus/live/round-53/alt/generate_pair.py
```

| File | Bytes | WAV SHA-256 |
|---|---:|---|
| `candidate_float32.wav` | 23,084 | `9b2f8914d569d51fb79b2f59c8b5db002cad77f5b9559784238dc304fabc1349` |
| `control_pcm16.wav` | 11,564 | `8b00b7211ccf0ee60094c1c1a6ceb8c2127ea60c536c6e95c65a00b066bc3f95` |

## Actual codec metadata and measurements

Ran this command separately on each WAV; both commands exited **0**:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json <file>
```

| File | Codec | Bits | Rate | Channels | Duration |
|---|---|---:|---:|---:|---:|
| `candidate_float32.wav` | `pcm_f32le` | 32 | 48000 | 1 | 0.120000 s |
| `control_pcm16.wav` | `pcm_s16le` | 16 | 48000 | 1 | 0.120000 s |

Project-measurement command — exit **0**:

```sh
python3 .shokunin/audio/corpus/live/round-53/alt/measure_pair.py
```

This calls the unchanged project `measure(..., SPECS["ui"], path)` function and its SoX-f32 decode. Both yielded 5,760 samples, 0.120 s, 48 kHz mono, peak `0.35980224609375`, RMS `-14.057671832408172 dBFS`, centroid `1102.604530408539 Hz`, bandwidth `539.2878585450499 Hz`, and `integrated_lufs=null`. Float32 failed only `format: expected PCM16`; PCM16 had no failures. Both pass non-format UI gates (duration within ±1 ms, peak < .95, RMS >= .001, centroid 250–4000 Hz).

For an explicit decoder comparison, each command exited **0**:

```sh
sox .shokunin/audio/corpus/live/round-53/alt/candidate_float32.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-53/alt/float.f32
sox .shokunin/audio/corpus/live/round-53/alt/control_pcm16.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-53/alt/pcm16.f32
```

SoX emitted `WARN wav: wave header missing extended part of fmt chunk` for the float WAV, but returned exit 0. The subsequent comparison command exited **0** and found 5,760 decoded float32 samples in each vector, exact equality, maximum absolute difference `0.0`, peak `0.35980224609375`, and linear RMS `0.1982058225892811`. Both raw decoded files had SHA-256 `a56fc891ce5bc4a34af81133b30995f5c7d7fd8edba31faffb954da61e9588dc`.

## Limits

No other gate failure, numeric-fit iteration, or transcription correction occurred. The equality results from constructing both encodings from the same PCM16 grid; they do not establish general float/PCM16 equivalence, float acceptance, fidelity, higher dynamic range, audibility, quality, production suitability, rights, engine behavior, or promotion. This lane made no shared-source or LOG edits and did not commit or push.
