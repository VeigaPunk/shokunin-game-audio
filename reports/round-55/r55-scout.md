# R55 scout — WAVE_FORMAT_EXTENSIBLE PCM16 metadata and prior coverage

## Scope and declaration

Read `.shokunin/audio/LOG.md` R55 declaration and R54 source/reports. The unchanged `format_failures()` requires 48 kHz mono, `codec_name == "pcm_s16le"`, and `bits_per_sample == 16`; `measure()` independently decodes to SoX f32 and applies the UI numeric checks. R55 declares a calibration comparison between conventional tag-1 PCM16 (`fmt` size 16) and a particular WAVE_FORMAT_EXTENSIBLE PCM subtype (tag `0xfffe`, 40-byte `fmt`, valid bits 16, mono front-center mask `0x4`). It predicts both should meet the same UI gates. This is a positive control for these headers, not an assertion about every extensible WAV.

## Original scratch probe

Generated an original 5,760-frame mono/48,000-Hz PCM16 stream (`.25*sin(2*pi*1000*t)+.08*sin(2*pi*1500*t)`, rounded to signed16), writing identical sample bytes in the two declared headers. Scratch is only under `corpus/live/round-55/scout/`. The conventional WAV is 11,564 bytes, SHA-256 `9ac26f38a7df9b1dd60c6130049d1e37056811fcd241f15a03559b5766bb4ba9`; extensible WAV is 11,588 bytes, SHA-256 `bd7d95901935c0effe21fd64e44a47487372be9d0c80f86cc725380df0352f47`. The extensible file has 40-byte fmt with `cbSize=22`, `wValidBitsPerSample=16`, mask `0x4`, and PCM subtype GUID `00000001-0000-0010-8000-00aa00389b71`.

For each WAV, this exact command (each ffprobe exit **0**) produced the metadata below:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json <wav>
```

Both report `codec_name=pcm_s16le`, `sample_fmt=s16`, 48,000 Hz, one channel, 16 bits/sample, and `.120000` seconds. SoX header inspection used `sox --i <wav>` (exit **0** for each); it reports one channel, 48 kHz, 16-bit signed integer PCM, 0.12 s / 5,760 samples for both. Explicit decode commands (each exit **0**) were:

```sh
sox .shokunin/audio/corpus/live/round-55/scout/pcm16-classic.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-55/scout/pcm16-classic.wav.f32
sox .shokunin/audio/corpus/live/round-55/scout/pcm16-extensible.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-55/scout/pcm16-extensible.wav.f32
```

Comparison command (exit **0**):

```sh
python3 -c 'import numpy as n; from pathlib import Path; p=Path(".shokunin/audio/corpus/live/round-55/scout"); a=n.fromfile(p/"pcm16-classic.wav.f32",dtype="<f4"); b=n.fromfile(p/"pcm16-extensible.wav.f32",dtype="<f4"); print(len(a),len(b),n.array_equal(a,b),float(n.max(n.abs(a-b))),float(n.max(n.abs(a))),float(n.sqrt(n.mean(a.astype(n.float64)**2))))'
```

Output: `5760 5760 True 0.0 0.31536865234375 0.18559832032281998`.

The unchanged project measurer was called for both files using `m.measure("ui", m.SPECS["ui"], path)`; exact invocation (exit **0**):

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m",".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); p=Path(".shokunin/audio/corpus/live/round-55/scout").resolve(); [print(m.measure("ui",m.SPECS["ui"],p/f)) for f in ("pcm16-classic.wav","pcm16-extensible.wav")]'
```

Both returned no failures and identical results: duration `.12 s`, peak `.31536865234375`, RMS `-14.628519169868087 dBFS`, centroid `1123.322704293326 Hz`, bandwidth `276.15444981222976 Hz`, LUFS `null`, PCM16/48 kHz/mono. Thus both pass this project measurer’s UI duration, level, spectrum and format checks on this pair; exact decoded equality follows from writing the same sample bytes.

## Existing coverage and limits

The historical R22 alternate report (`reports/round-22/r22-alt.md`) documents WAVE_FORMAT_EXTENSIBLE 24-bit PCM, including a 24-bit container with 20 valid bits. In the queried ffprobe metadata, these appear as `pcm_s24le` / 24 bits; the report cautions that this does not expose the valid-bit distinction. R22/R23 records explicitly say this did not establish an extensible-WAV valid-bit predicate. R53 tested a simple 16-byte IEEE-float fmt and reported a SoX warning about missing the extended fmt part, while decode still succeeded; that was not an extensible-header test. R54’s dedicated comparison was signed PCM32 versus PCM16, not extensible versus standard PCM16. I found no prior dedicated matched ordinary PCM16 standard/extensible-header UI pair in the inspected LOG and round reports. This historical check is bounded to those tracked declarations/reports and the cited probes, not every WAV or scratch artifact.

Observed behavior supports only the declared subtype/layout/valid-bits/sample-rate/channel pair with the local ffprobe, SoX, and project measurement path. It does not establish support for other extensible channel masks, subtypes, bit depths or valid-bit values, multiple streams, other containers, arbitrary WAVs, all decoder versions, or universal WAVE_FORMAT_EXTENSIBLE behavior. No inference about fidelity beyond these identical decoded vectors, audibility, quality, production, engine, rights, or promotion. I changed no shared source, LOG, SCORECARD, canonical artifact, or other report and generated no runner receipt.
