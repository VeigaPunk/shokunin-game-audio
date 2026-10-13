# R53 simplifier — keep the format pair local

## Recommendation

Keep R53 as two opt-in measurements over one scratch pair. Reuse the existing UI `measure(..., SPECS["ui"], path)` and the current runner's one-probe guard / receipt path. Add only the float32 and R53 PCM16 flags, scratch-file selection, and mode/suffix labels needed to reach that pair. Do not generalize a media-format framework, modify the shared format predicate or thresholds, duplicate the UI gate calculations, or add this scratch pair to canonical fixtures / family comparisons. The measured source of truth remains `measure_audio.py`; the pair is evidence, not a second specification.

The existing PCM8 / PCM16 and PCM24 / PCM16 opt-ins illustrate the local pattern, though the accumulated long nested mode/suffix expressions are already hard to audit. For R53 avoid expanding this scope into refactoring those historical options. If integrating the new options would require another broad selector rewrite, keep the smallest adjacent additions or stop and report the maintainability tradeoff rather than building a new dispatch abstraction for one pair.

## Independently observed pair

I ran the alternate generator and unchanged project measurement helper from repository root:

```sh
python .shokunin/audio/corpus/live/round-53/alt/generate_pair.py
```

Exit **0**. Its original pair is in the permitted alternate scratch directory. WAV SHA-256 / byte counts:

| File | Bytes | SHA-256 |
|---|---:|---|
| `candidate_float32.wav` | 23084 | `9b2f8914d569d51fb79b2f59c8b5db002cad77f5b9559784238dc304fabc1349` |
| `control_pcm16.wav` | 11564 | `8b00b7211ccf0ee60094c1c1a6ceb8c2127ea60c536c6e95c65a00b066bc3f95` |

```sh
python .shokunin/audio/corpus/live/round-53/alt/measure_pair.py
```

Exit **0**. Both are 5760 decoded samples, 48000 Hz mono, duration 0.120 s. Both report peak `0.35980224609375`, RMS `-14.057671832408172 dBFS`, spectral centroid `1102.604530408539 Hz`, bandwidth `539.2878585450499 Hz`, and `integrated_lufs=null`. Float32 (`pcm_f32le`, 32 bits) reports only `format: expected PCM16`; control (`pcm_s16le`, 16 bits) has no failures. Both meet the unchanged numeric UI gates: duration ±1 ms, peak <.95, RMS >=.001, centroid 250–4000 Hz.

I separately ran `ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json <file>` on each file; each exited **0**. Actual metadata was `pcm_f32le`/32 bits and `pcm_s16le`/16 bits, both 48000 Hz, mono, `0.120000` seconds.

The project measurer uses SoX float32 decoding. Independent direct comparison of the decoded arrays returned 5760 samples each, exact equality (`array_equal=True`, max absolute difference `0.0`). This equality is expected from intentionally encoding the same PCM16-grid samples as float32 (`s16/32768`), not evidence of general float/PCM16 equivalence.

## Limits and disposition

This is alternate-pair evidence and design guidance only: I did not edit source, run runner integration, replay receipts, alter thresholds, or claim a round verdict. An initial shell attempt used malformed quoting and returned exit **127** (“No such file or directory”); the correctly invoked commands above succeeded. This was command setup, not an audio-gate result. No numeric-fit failure or transcription correction occurred. The test does not establish arbitrary float WAV conversion/acceptance, higher dynamic range, fidelity, perception, quality, rights, engine behavior, production suitability, or promotion. No commit or push was made.
