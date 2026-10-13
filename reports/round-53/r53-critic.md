# R53 critic — IEEE-float format isolation and UI gates

## Scope

I read the R53 declaration in `.shokunin/audio/LOG.md` and the R52 reports/source context. I made no changes to shared source, LOG, SCORECARD, canonical artifacts, or other reports. I tested a critic-owned local pair only at `.shokunin/audio/corpus/live/round-53/critic/`: mono 48 kHz, 5760 frames, a 1 kHz + 1.5 kHz UI-band signal. The PCM16 control contains signed integers `s`; the IEEE-float WAV contains float32 `s/32768`. This checks this constructed matched pair, not general float conversion or higher-precision signal content.

## Commands and results

Pair creation was performed in Python 3 (exit **0**). The signal was `x=.25*sin(2*pi*1000*t)+.08*sin(2*pi*1500*t)`, sampled at 48 kHz; `s=round(x*32767)` as little-endian signed 16-bit, and float32 samples were `s/32768`. I wrote PCM16 via Python `wave` and a RIFF WAV float file with format tag 3, one channel, 48000 Hz, 32 bits/sample, and 5760 float samples. This makes the samples equal on the PCM16 normalized grid; it is not an arbitrary float precision stress test.

For each WAV, the following command exited **0**:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json <wav>
```

Float candidate metadata: `pcm_f32le`, `flt`, 32 bits, 48000 Hz, mono, `.120000` s. PCM16 control: `pcm_s16le`, `s16`, 16 bits, 48000 Hz, mono, `.120000` s. WAV SHA-256: float `b9e29bb55c22282185799aa0cf4d2cb3c920425c985cc80cf05d5f55c94c7cd3`; control `9ac26f38a7df9b1dd60c6130049d1e37056811fcd241f15a03559b5766bb4ba9`.

I ran the current project measurer's unchanged `measure(..., SPECS["ui"], path)` directly for each file using this command template (each exited **0**):

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m",".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.measure("ui",m.SPECS["ui"],Path("<absolute-wav-path>")))'
```

Float: duration `.12` s, peak `.31536865234375`, RMS `-14.628519169868087 dBFS`, centroid `1123.322704293326 Hz`, bandwidth `276.15444981222976 Hz`, failures exactly [`format: expected PCM16`]. PCM16: identical reported numeric metrics, failures `[]`. Both pass UI duration ±.001 s, peak <.95, RMS >=.001, centroid 250–4000 Hz, rate and channel checks. Float is rejected by the existing PCM16 format predicate despite valid IEEE-float stream metadata and passing other UI checks; the control passes.

Direct SoX decoded-vector commands (each exit **0**):

```sh
sox .shokunin/audio/corpus/live/round-53/critic/candidate-float.wav -t f32 -e floating-point -
sox .shokunin/audio/corpus/live/round-53/critic/control-pcm16.wav -t f32 -e floating-point -
```

Each emitted 23,040 bytes / 5,760 float32 samples. The vectors were elementwise exactly equal (0 differing samples, maximum absolute difference `0.0`); both decoded-vector SHA-256 values are `d80f13858e4fdcf641f2164b440a99a42711fd4213239ad809c8136ee4620ce7`. Peak was `.31536865`, decoded RMS `.18559832032281998`.

SoX printed `WARN wav: wave header missing extended part of fmt chunk` while decoding the float WAVE (exit 0); it did not prevent decoding or project measurements. The test used a 16-byte `fmt ` chunk / WAVE format tag 3. This warning is a bounded header-variant caveat: this run does not cover `WAVE_FORMAT_EXTENSIBLE` float headers or other decoders. No failed numeric fit or transcription correction occurred.

## Assessment / limits

I found no falsifier for the declared local isolation: ffprobe identifies float32 IEEE PCM, the existing project path decodes it, SoX-f32 vectors equal the normalized PCM16 control for this deliberately grid-matched signal, and only the intended PCM16 format predicate fails on float. This does not establish acceptance or correct handling of arbitrary IEEE-float WAVs, extensible headers, out-of-range/non-grid float values, higher dynamic range, general fidelity, audibility, quality, rights, engine behavior, production, or promotion. No runner integration, canonical set, prior receipt replay, or other UI gates outside the unchanged UI measurer were exercised here.
