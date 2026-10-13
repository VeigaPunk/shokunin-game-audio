# R54 scout — PCM32 metadata, unchanged predicate, and historical coverage

## Scope and current gate

Read-only inspection of `.shokunin/audio/corpus/fixtures/measure_audio.py` confirms `format_failures(stream)` is unchanged: it first requires `sample_rate == 48000` and `channels == 1`, otherwise `format: expected 48kHz mono`; independently it requires `codec_name == "pcm_s16le"` **and** `bits_per_sample == 16`, otherwise `format: expected PCM16`. `measure()` probes stream metadata, decodes through SoX to f32, and then applies duration, peak/RMS, centroid, and optional seam checks. The f32 measurement buffer is not an input-format acceptance rule. For 48 kHz mono PCM32, both rate/channel checks pass and the existing codec/bit-depth check predicts only `format: expected PCM16` if the other UI measurements fit.

## R54 scratch pair evidence

I inspected the executor, alternate, and critic scratch pairs under `corpus/live/round-54/`; no scratch was changed. Exact ffprobe command used for each WAV (each invocation exited **0**):

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json <wav>
```

Observed candidate/control stream tuples, all mono 48000 Hz and `.120000` seconds:

| Scratch | Candidate metadata / SHA-256 | PCM16 control metadata / SHA-256 |
|---|---|---|
| executor | `pcm_s32le`, `s32`, 32 bits; `fcbdd5aa0862fddabad017388aba24bedc9e6c98202ccbc04a40125413de47c7` | `pcm_s16le`, `s16`, 16 bits; `9ac26f38a7df9b1dd60c6130049d1e37056811fcd241f15a03559b5766bb4ba9` |
| alt | `pcm_s32le`, `s32`, 32 bits; `5cd1711de2ed2dc76fc2505a2f0584f1fd31d523994818168fba18f1cbb49b9a` | `pcm_s16le`, `s16`, 16 bits; `37a1eb68e0a870d3b3a58e4d45d5686de12e0cb4bcabaffa15c079f50da51436` |
| critic | `pcm_s32le`, `s32`, 32 bits; `3d78174340f2465299bd745bd102ef73981f2bf58c10d0ff959f4f3d3eeef81b` | `pcm_s16le`, `s16`, 16 bits; `2d201f849ecb416401b15c88e172527f9beec852c8998123f5f06131c712fee0` |

Executor's direct existing-project measurement command `python3 .shokunin/audio/corpus/live/round-54/executor/measure.py` exited **0**. Its PCM32 result: duration `.12`, peak `.31536865234375`, RMS `-14.628519169868087 dBFS`, centroid `1123.322704293326 Hz`, bandwidth `276.15444981222976 Hz`, failures exactly [`format: expected PCM16`]. PCM16 control has the same reported numeric metrics and `failures=[]`. The alternate's direct command was:

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m",".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); p=Path(".shokunin/audio/corpus/live/round-54/alt"); print(m.measure("ui",m.SPECS["ui"],(p/"candidate_pcm32.wav").resolve())); print(m.measure("ui",m.SPECS["ui"],(p/"control_pcm16.wav").resolve()))'
```

It exited **0**; candidate: duration `.12`, peak `.3634033203125`, RMS `-15.105666206939194 dBFS`, centroid `2718.417873898037 Hz`, bandwidth `3712.599544713593 Hz`, sole failure [`format: expected PCM16`]; control has identical metrics and no failures. These constructed pairs therefore fit the UI numeric gates (duration ±.001 s; peak <.95; RMS >=.001; centroid 250–4000 Hz), with format as the observed distinction.

SoX-f32 vector checks were made on each original candidate/control pair. For each file I ran `sox <wav> -t f32 -e floating-point <role-dir>/<pcm32-decoded.f32 or pcm16-decoded.f32>`; all six commands exited **0**. I compared each pair with:

```sh
python3 -c 'import numpy as n; from pathlib import Path; p=Path("<role-dir>"); a=n.fromfile(p/"pcm32-decoded.f32",dtype="<f4"); b=n.fromfile(p/"pcm16-decoded.f32",dtype="<f4"); print(len(a),len(b),n.array_equal(a,b),float(n.max(n.abs(a-b))),float(n.max(n.abs(a))),float(n.sqrt(n.mean(a.astype(n.float64)**2))))'
```

Each comparison exited **0** and printed `5760 5760 True 0.0 ...`: executor peak/RMS `0.31536865234375` / `0.18559832032281998`; alt `0.3634033203125` / `0.17567772131673257`; critic `0.315399169921875` / `0.18560763156982443`. The scripts explicitly form PCM32 as PCM16 sample integers multiplied by 65536, so exact decoded equality is expected by construction; this is not a test of additional 32-bit precision or arbitrary PCM32 values.

## Historical coverage (bounded inspection)

The existing invalid bundle contains `native24_probe`, not PCM32. The source builder creates it as 3-byte signed PCM24; `ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt,duration:format=duration -of json .shokunin/audio/corpus/live/round-22/native24_probe.wav` exited **0**, identifying `pcm_s24le`, `sample_fmt=s32`, 24 bits, 48000 Hz mono, 4.000000 seconds. The paired `native16_probe` is `pcm_s16le`, `s16`, 16 bits, same rate/channels/duration. The historic `--probe-invalid` receipt classifies native24 as a format failure and native16 as expected pass. `sample_fmt=s32` here is FFmpeg's decoded sample representation for **24-bit** PCM, not evidence of a signed PCM32 stream.

R22 through R53 reports/LOG inspected for explicit PCM32 or `pcm_s32le` evidence show prior format comparisons for PCM24, PCM8, and float32, but no prior dedicated signed PCM32 fixture or matched UI-shaped PCM32-vs-PCM16 comparison. The historic 24-bit invalid probe is a 4-second metadata-format control, not the R54 ordinary UI-shaped pair; it does not itself show all UI numeric gates. This search is bounded to tracked source, round reports, declarations and referenced historical probes inspected, not every untracked scratch WAV.

No source, LOG, SCORECARD, canonical artifact, or other report was changed; no runner receipt was generated. Findings concern only the observed constructed pairs and existing local metadata predicate. They do not establish arbitrary PCM32 handling, additional precision, general conversion/fidelity, perception, quality, rights, engine behavior, production suitability, or promotion.
