# Round 48 guard — adjacent sample-rate fixture and preservation audit

## Declaration and evidence boundary

I read the Round 48 declaration in `.shokunin/audio/LOG.md`. It declares one calibration move against the existing exact `ffprobe` sample-rate predicate: original deterministic UI-shaped mono PCM16 scratch files at 47,999 and 48,000 Hz, each with 5,760 frames, target duration .12 s within ±.001 s, peak <.95, RMS >=.001, and project SoX-f32 whole-wave centroid in 250–4000 Hz. The expected outcomes are 47,999 Hz exit 1 with only `format: expected 48kHz mono`, and 48,000 Hz exit 0. This report covers guard measurements, not the declared 56-run non-author replay (not run by me).

No audition, audio-quality, perception, production, rights, engine, publishing, or promotion inference is made. The pair tests the fixture's numerical format gate; it does not establish general resampling or converter behavior.

## Candidate measurements

Both files are from the existing executor's deterministic `generate.py`. It builds one PCM sample sequence on a 48 kHz grid and writes that sequence at the two container sample rates. I independently confirmed the decoded PCM payload SHA-256 is identical (`058cacc8a6cdf19afa215c4d386bb903ede8641b9aed0468ff4678ef327c9eea`, 11,520 bytes); WAV-file hashes differ because their headers encode different rates.

| File | WAV SHA-256 | Frames | ffprobe codec / sample format / rate / channels / bits | ffprobe duration | Peak FS | RMS dBFS | SoX-f32 whole-wave centroid | Project failures |
|---|---|---:|---|---:|---:|---:|---:|---|
| `ui-47999.wav` | `71551e200633e62b1b9db4ee5a582f8d4d996cd693f2e4a040a96023b130a210` | 5760 | `pcm_s16le` / `s16` / 47999 / 1 / 16 | .120003 s | .27996826171875 | -18.327858226717105 | 1022.5148421151724 Hz | `format: expected 48kHz mono` only |
| `ui-48000.wav` | `387500a620fbfdfb38e044ebb1ec8e0a82be14be9dc71e2bd18e45ec9625ed8c` | 5760 | `pcm_s16le` / `s16` / 48000 / 1 / 16 | .120000 s | .27996826171875 | -18.327858226717105 | 1022.536144951523 Hz | none |

Both pass duration, level, and spectrum checks; exact integer sample rate alone separates their format outcomes. These are project-measured decoded values, not nominal generator values. The identical PCM payload does not mean identical decoded timing or centroid: the sample-rate metadata differs.

## Exact command record

The following ffprobe loop exited **0** and emitted the metadata transcribed above:

```sh
cd /home/vgpnk/Projects/prymeagnt/audio && for f in .shokunin/audio/corpus/live/round-48/executor/ui-47999.wav .shokunin/audio/corpus/live/round-48/executor/ui-48000.wav; do printf '%s\n' "$f"; ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_fmt,sample_rate,channels,bits_per_sample,duration,nb_frames -show_entries format=duration -of json "$f"; done
```

The project's `measure_audio.py` measurement command exited **0**:

```sh
cd /home/vgpnk/Projects/prymeagnt/audio && python3 -c 'import importlib.util; from pathlib import Path; p=Path(".shokunin/audio/corpus/fixtures/measure_audio.py").resolve(); s=importlib.util.spec_from_file_location("ma",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); spec=m.SPECS["ui"]; [(print(name, m.measure(name, spec, (Path(".shokunin/audio/corpus/live/round-48/executor")/(name+".wav")).resolve()))) for name in ("ui-47999","ui-48000")]'
```

I also attempted a shell-wrapped version of the measurement command, but malformed quoting caused shell parse exit **2** before Python ran (`unexpected EOF while looking for matching '"'`). This is a setup/command-construction error, not a measurement or numeric-fit failure; the corrected command above ran successfully. No other failed numeric fits or report transcription corrections were observed by this guard. I did not run either fixture through the serial measurement runner and do not claim runner exits here.

## Historical preservation baseline (not re-measured here)

Round 47's named non-author verifier documents a **54-run fresh serial replay: 23 exit 0 / 31 expected fixture-validation exit 1**, no setup failures, prior-52 subset **22/30**, and matching first/final normal JSON with 17 canonicals and no failures. Round 48's declared next verifier run is 56 commands; the Round 47 replay is historical baseline, not a Round 48 result. Its normal restoration and the other historical checks below are likewise not rerun by this guard.

The canonical 17 SHA-256 values and decoded metrics were carried forward from the Round 47 guard's prior baseline (ultimately transcribed there from the R45 verifier); I did not independently hash or measure canonical artifacts:

| Canonical | SHA-256 | Duration (s) | Rate | Ch | Encoding | Peak FS | RMS dBFS | Centroid Hz |
|---|---|---:|---:|---:|---|---:|---:|---:|
| `ui` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` | .12 | 48000 | 1 | pcm_s16le/16 | .375946044921875 | -19.991687666366516 | 966.8966593379727 |
| `ui_alt` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` | .16 | 48000 | 1 | pcm_s16le/16 | .31878662109375 | -20.525534144496497 | 1423.1532540422852 |
| `ui_third` | `734a0a47077f5b614b5d51d486b88a51940c7d61ecea0878642b60a0103513bc` | .20 | 48000 | 1 | pcm_s16le/16 | .375946044921875 | -22.20695387316763 | 966.7216217320357 |
| `impact` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` | .32 | 48000 | 1 | pcm_s16le/16 | .80877685546875 | -20.40218668053459 | 10843.127202979935 |
| `impact_alt` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` | .32 | 48000 | 1 | pcm_s16le/16 | .75616455078125 | -17.32957040921516 | 473.79153568100764 |
| `impact_third` | `d14376241f409f07edde30fbcef86b5f060ff36f731b7578fd9934d1dc1b39bf` | .40 | 48000 | 1 | pcm_s16le/16 | .45611572265625 | -20.84958464133168 | 6838.143302962279 |
| `movement` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` | .24 | 48000 | 1 | pcm_s16le/16 | .53948974609375 | -23.779940832329185 | 11934.484045946316 |
| `movement_alt` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` | .36 | 48000 | 1 | pcm_s16le/16 | .639312744140625 | -21.987315616484317 | 12024.214879348818 |
| `movement_third` | `0e5f815e1987e13646170571e1f1e977b25e3566d90ebcca558c72ed07851d44` | .30 | 48000 | 1 | pcm_s16le/16 | .489501953125 | -14.025186267550422 | 4553.583280111138 |
| `ambience` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` | 2.0 | 48000 | 1 | pcm_s16le/16 | .174591064453125 | -18.153351293681563 | 36.61640767851373 |
| `ambience_alt` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` | 2.0 | 48000 | 1 | pcm_s16le/16 | .199737548828125 | -17.67032381358842 | 58.01919713436623 |
| `ambience_third` | `c2c8e0bb2385bc93b39c70b719d0f56553c771969986ef1f732d24af5677d404` | 2.0 | 48000 | 1 | pcm_s16le/16 | .225006103515625 | -16.92261930553234 | 112.03210352691181 |
| `stem` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` | 2.0 | 48000 | 1 | pcm_s16le/16 | .32379150390625 | -14.881434973008286 | 272.6756827789141 |
| `stem_sections` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` | 4.0 | 48000 | 1 | pcm_s16le/16 | .17236328125 | -23.066521225821248 | 201.87069023000652 |
| `stem_layer` | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` | 4.0 | 48000 | 1 | pcm_s16le/16 | .05999755859375 | -30.28756654598196 | 190.1433267529918 |
| `stem_layer_alt` | `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` | 4.0 | 48000 | 1 | pcm_s16le/16 | .04998779296875 | -31.667277345674258 | 277.9513846028647 |
| `stem_layer_third` | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` | 4.0 | 48000 | 1 | pcm_s16le/16 | .04998779296875 | -31.6672476528647 | 287.93805923844434 |

Historical comparison and gate baseline: five generic `_alt` comparisons passed (UI duration delta .04000000000000001 s / relative centroid delta .47187731004956435; impact 0 s / .9563048992406177; movement .12 s / .007518618572621081; ambience 0 s / .5845136323520758; stem_layer 0 s / .46179931396667484). Four family groups (UI, impact, movement, ambience), eight third-variant comparisons, passed. Thresholds carried forward unchanged: 48 kHz mono PCM16; duration ±.001 s; peak <.95 FS; RMS >=.001 FS; UI centroid inclusive 250–4000 Hz; loop endpoint delta <=.03 FS and outer slope mismatch <=.001 FS/sample; section contrast >=6 dB, component amplitude >=.01 FS, section RMS >=.001 FS; internal section join gap <=.03 FS and slope mismatch <=.001 FS/sample; distinctness duration delta >=.020 s OR relative centroid delta >=.10.

Eight invalid-probe outcomes carried forward: `short_sections` section-count failure; `corrupt` decode failure; `wrong_format` format failure; `odd_sections` section-count failure; `native16_probe` expected pass; `native24_probe`, `stereo48_probe`, and `mono441_probe` format failures. These are expected fixture-validation outcomes, not setup errors. Old17 hashes/metrics, generic/family comparisons, thresholds/sections, eight outcomes, and normal restoration are preservation context only; I did not rerun them.

## Scope

I wrote only `.shokunin/audio/reports/round-48/r48-guard.md`. No source, LOG, SCORECARD, canonical artifact, or other report was edited; no commit or push. Conclusions are limited to numerical fixture calibration and the identified historical preservation evidence.
