# Round 54 executor — PCM32/PCM16 matched UI-shaped pair

## Construction and artifacts

Read the R54 declaration in `.shokunin/audio/LOG.md`. Generated an original 5760-frame mono 48,000 Hz PCM16 control and signed PCM32 WAV candidate in `.shokunin/audio/corpus/live/round-54/executor/`. The signal uses `x=.25*sin(2*pi*1000*t)+.08*sin(2*pi*1500*t)`; each PCM16 integer `s` is rounded from `x*32767`, and each PCM32 integer is exactly `s*65536`. Thus this fixture compares widths on a matched integer grid; it does not add signal precision.

Generation command (exit **0**):

```sh
python3 .shokunin/audio/corpus/live/round-54/executor/generate.py
```

WAV SHA-256: PCM32 `fcbdd5aa0862fddabad017388aba24bedc9e6c98202ccbc04a40125413de47c7` (23084 bytes); PCM16 `9ac26f38a7df9b1dd60c6130049d1e37056811fcd241f15a03559b5766bb4ba9` (11564 bytes).

## Probe and project gate results

Command (exit **0**):

```sh
for f in .shokunin/audio/corpus/live/round-54/executor/*.wav; do echo "$f"; ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json "$f"; done
```

ffprobe reports PCM32 as `pcm_s32le`, 32 bits, mono, 48000 Hz, duration `.120000`; PCM16 as `pcm_s16le`, 16 bits, mono, 48000 Hz, duration `.120000`.

Project measurer command (exit **0**):

```sh
python3 .shokunin/audio/corpus/live/round-54/executor/measure.py
```

The wrapper invokes unchanged `measure(path, SPECS["ui"], path)` from `.shokunin/audio/corpus/fixtures/measure_audio.py`. For both, it reports 5760 decoded samples, duration `.12 s`, peak `0.31536865234375`, RMS `-14.628519169868087 dBFS`, spectral centroid `1123.322704293326 Hz`, bandwidth `276.15444981222976 Hz`, and integrated LUFS `null`. Both pass the numeric UI duration (±1 ms), peak (<.95), RMS (>=.001), centroid (250–4000 Hz), mono and 48 kHz checks. PCM32 failure list is exactly [`format: expected PCM16`]; PCM16 failure list is `[]`.

Explicit SoX-f32 decoded-vector commands (each exit **0**):

```sh
sox .shokunin/audio/corpus/live/round-54/executor/pcm32.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-54/executor/pcm32-decoded.f32
sox .shokunin/audio/corpus/live/round-54/executor/pcm16.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-54/executor/pcm16-decoded.f32
```

Comparison command (exit **0**):

```sh
python3 -c 'import numpy as n; from pathlib import Path; p=Path(".shokunin/audio/corpus/live/round-54/executor"); a=n.fromfile(p/"pcm32-decoded.f32",dtype="<f4"); b=n.fromfile(p/"pcm16-decoded.f32",dtype="<f4"); print(len(a),len(b),n.array_equal(a,b),float(n.max(n.abs(a-b))),float(n.max(n.abs(a))),float(n.sqrt(n.mean(a.astype(n.float64)**2))))'
```

Output: `5760 5760 True 0.0 0.31536865234375 0.18559832032281998`. The decoded vectors are elementwise equal for this constructed pair.

## Limits

This is evidence only for the matched integer-grid pair and the existing UI format predicate. It isolates a PCM32-vs-PCM16 metadata case; it does not test extra PCM32 precision, arbitrary PCM32, general conversion/fidelity, audibility, quality, rights, engine, production, or promotion. No shared source, LOG, SCORECARD, canonical artifact, or other report was changed.
