# R53 scout — float WAV predicate and historical format coverage

## Current predicate

Read-only inspection of `corpus/fixtures/measure_audio.py` shows `format_failures(stream)` has two independent checks:

- `sample_rate == 48000` and `channels == 1`, otherwise `format: expected 48kHz mono`.
- `codec_name == "pcm_s16le"` **and** `bits_per_sample == 16`, otherwise `format: expected PCM16`.

There is no float-specific acceptance branch. An IEEE float WAV identified as `pcm_f32le`/32 bits therefore fails the existing second predicate as `format: expected PCM16`. `measure()` independently decodes with SoX to f32 and then measures duration, peak, RMS and spectrum; its f32 measurement representation does not mean the input file's encoding is accepted. The UI spec is `.12s`, centroid 250–4000 Hz; the ordinary checks include duration ±.001 s, peak `<.95`, RMS `>=.001` and the spec centroid band.

## ffprobe evidence (generated R53 alt matched pair)

I ran these exact commands; both exited **0**:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt,duration:format=duration -of json .shokunin/audio/corpus/live/round-53/alt/candidate_float32.wav
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt,duration:format=duration -of json .shokunin/audio/corpus/live/round-53/alt/control_pcm16.wav
```

Float stream metadata: `codec_name=pcm_f32le`, `sample_fmt=flt`, `bits_per_sample=32`, `sample_rate=48000`, mono, stream/format duration `.120000`. PCM control: `pcm_s16le`, `s16`, 16 bits, 48000 Hz, mono, `.120000` seconds. The candidate and control SHA-256 values are respectively `9b2f8914d569d51fb79b2f59c8b5db002cad77f5b9559784238dc304fabc1349` and `8b00b7211ccf0ee60094c1c1a6ceb8c2127ea60c536c6e95c65a00b066bc3f95` (metadata identifies these particular original WAVs; no general conversion claim).

I also ran `python3 .shokunin/audio/corpus/live/round-53/alt/measure_pair.py` (exit **0**). Its project `measure()` results: float WAV sole failure `format: expected PCM16`; PCM16 control `failures=[]`. Both decode to 5760 samples and report duration `.12`, peak `.35980224609375`, RMS `-14.057671832408172 dBFS`, centroid `1102.604530408539 Hz`, bandwidth `539.2878585450499 Hz`. These are alt pair measurements, not a runner receipt. The alt generator constructs float32 values from signed16 integers divided by 32768; equal reported measurements are not evidence for arbitrary float WAV handling.

Additional shell telemetry: `sox .shokunin/audio/corpus/live/round-53/alt/candidate_float32.wav -t f32 -e floating-point -` exited **0** and emitted 22462 bytes, with warning `wav: wave header missing extended part of fmt chunk`; the PCM16 equivalent exited **0**, 22401 bytes. This is only a decode-command observation, not an independent vector-equality test. A malformed command-construction attempt for the PCM16 ffprobe command exited **127** (`/usr/bin/bash: ...: No such file or directory`); it invoked the whole command text as a filename, produced no probe result, and is setup error, not a format/gate outcome.

## Historical coverage and bounds

The source's `invalid_probes()` has eight entries: `short_sections`, `corrupt`, `wrong_format`, `odd_sections`, `native16_probe`, `native24_probe`, `stereo48_probe`, and `mono441_probe`. `native24_probe` is the explicit bit-depth format-invalid control (24-bit `pcm_s24le`); none is a float WAV. Format-invalid probes call ffprobe and `format_failures()` and record metadata/status; they do **not** demonstrate ordinary UI numeric gates on the same probe. The R52 scout likewise found no dedicated PCM8 control, while R51/R52 round records cover integer PCM24/PCM8 matched fixtures, respectively. In the checked source, invalid-probe list, and round records through R52, there is no dedicated IEEE-float input acceptance/invalid fixture or prior float-vs-integer matched comparison. This is a bounded search statement, not proof that no untracked float WAV exists anywhere in historical scratch.

I did not change source, run canonical tests, modify LOG/SCORECARD, or create a probe receipt. No conclusion about general float conversion, full-precision content, fidelity, audibility, or production behavior.
