# Round 51 guard — PCM24 format calibration and preservation audit

## Declaration and scope

I read the Round 51 declaration in `.shokunin/audio/LOG.md`. It calls for one calibration comparison: deterministic 5,760-frame mono 48,000-Hz signed PCM24 versus PCM16, target duration .12 s ±.001, peak <.95 FS, RMS >=.001 FS and project SoX-f32 whole-wave centroid 250–4,000 Hz for both. Expected result: PCM24 exit 1 with sole `format: expected PCM16`; PCM16 exit 0 clean, through unchanged `measure(..., SPECS["ui"])`. The predicate and thresholds are not changed.

This report's numerical result is limited to the measured files and project gate. It makes no broad codec, conversion, quality, perception, production, rights, engine, publishing, or promotion inference. Historical checks below are carried forward, not re-run by this guard.

## Original executor pair measurements

Original executor scratch is `.shokunin/audio/corpus/live/round-51/executor/`. The generator builds a 5,760-sample 1-kHz plus 1.5-kHz sequence, quantizes to PCM16, and represents that same integer sample sequence in PCM24 by multiplying each PCM16 integer by 256. Project `measure()` runs SoX floating-point decode and evaluates the unchanged ordinary UI spec.

| Candidate | WAV SHA-256 | Frames | ffprobe codec / sample_fmt / rate / channels / bits | ffprobe duration | Project SoX-decoded peak FS | Project RMS dBFS | Project whole-wave centroid | Failures |
|---|---|---:|---|---:|---:|---:|---:|---|
| PCM24 | `6d3f804579124af4fb14f8d7313b25fb87231ca9729a434661475939cae601c8` | 5760 | `pcm_s24le` / `s32` / 48000 / 1 / 24 | .120000 s | .315399169921875 | -14.628083420045229 | 1123.8154138173777 Hz | `format: expected PCM16` only |
| PCM16 control | `2d201f849ecb416401b15c88e172527f9beec852c8998123f5f06131c712fee0` | 5760 | `pcm_s16le` / `s16` / 48000 / 1 / 16 | .120000 s | .315399169921875 | -14.628083420045229 | 1123.8154138173777 Hz | none |

Both pass duration, peak, RMS and centroid UI gates. ffprobe reports actual PCM24 as `pcm_s24le`, `s32` sample format, 24 bits; PCM16 as `pcm_s16le`, `s16`, 16 bits. The generator encodes the same normalized sample levels in these exact candidates; the matching reported project decoded metrics are measured outputs, not a bit-exact-decoding claim for all bit depths.

The executor's initial measurement attempt used relative path strings, and exited **1** with `ValueError` at `Path.relative_to(ROOT)` before returning measurements. This was a path/setup error, not a gate result or failed numeric fit. Retried with absolute file paths; no threshold or comparator was tuned.

## Alternate independent scratch pair

The independent alt candidate pair under `.shokunin/audio/corpus/live/round-51/alt/` also passes the numeric checks and has the same result polarity:

| Candidate | WAV SHA-256 | ffprobe codec / sample_fmt / rate / channels / bits | Duration | Project peak FS | RMS dBFS | Project centroid | Failures |
|---|---|---|---:|---:|---:|---:|---|
| PCM24 | `1b800add20c7ea7a2093d61e8070ac8f58beb3d314f84075f883b44bd4d42bc7` | `pcm_s24le` / `s32` / 48000 / 1 / 24 | .120000 s | .25 | -15.051713380047701 | 1001.4515079742339 Hz | `format: expected PCM16` only |
| PCM16 control | `d2fb12b0a2b110baa63990184404aaf038d8acf80373c5ca1d6734e738fb7d49` | `pcm_s16le` / `s16` / 48000 / 1 / 16 | .120000 s | .25 | -15.051713380047701 | 1001.4515079742339 Hz | none |

## Exact commands and exits

From repository root, I ran the following ffprobe loop for executor, alt, and reviewer scratch WAVs; exit **0**. Exact stream metadata/duration are summarized in the tables above (all are 5760-frame, .120000-s mono 48-kHz files).

```sh
cd /home/vgpnk/Projects/prymeagnt/audio && for d in executor alt reviewer; do echo ===$d===; for f in .shokunin/audio/corpus/live/round-51/$d/*.wav; do echo ---$f; ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_fmt,sample_rate,channels,bits_per_sample,duration,nb_frames -show_entries format=duration -of json "$f"; done; done
```

Corrected executor project measurement command, exit **0**:

```sh
cd /home/vgpnk/Projects/prymeagnt/audio && python3 .shokunin/audio/corpus/live/round-51/executor/measure_pair.py .shokunin/audio/corpus/fixtures/measure_audio.py /home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-51/executor/pair_pcm24.wav /home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-51/executor/pair_pcm16.wav
```

Alt project measurement command, exit **0**:

```sh
cd /home/vgpnk/Projects/prymeagnt/audio && python3 .shokunin/audio/corpus/live/round-51/alt/measure_pair.py
```

The executor's first attempt (setup failure), exit **1**:

```sh
cd /home/vgpnk/Projects/prymeagnt/audio && python3 .shokunin/audio/corpus/live/round-51/executor/measure_pair.py .shokunin/audio/corpus/fixtures/measure_audio.py .shokunin/audio/corpus/live/round-51/executor/pair_pcm24.wav .shokunin/audio/corpus/live/round-51/executor/pair_pcm16.wav
```

No selected candidate had a failed numeric fit; the PCM24 format failure is the expected gate outcome. No report transcription correction was needed. I did not run an integrated runner or serial replay.

## Old17 canonical SHA/metrics (carried forward)

The following table is carried forward from the prior guard and has not been independently rehashed or measured in this report:

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


**Prior replay baseline:** Round 49's named non-author verifier reports 58 fresh serial runner invocations and 58 distinct new receipts, **25 exit 0 / 33 expected fixture-validation exit 1**. The old58 comparison is represented by the prior58 baseline; the preceding Round 48 replay was 56 invocations, 24/32. Round 49 verifier separately compared its old56 subset with prior receipts. These counts are historical and are not Round 50 replay results. Round 49 discarded two wrapper-construction attempts (all attempts exit127 before Python, zero receipts); those were setup errors, not fixture gate outcomes.

Round 49 verifier reports initial and final normal JSON equal, 17 canonical measurements clean, and the old17 SHA baseline intact. These are prior verifier results, not a normal-restoration run by this guard.

**Existing checks carried forward unchanged:** five generic `_alt` comparisons (UI, impact, movement, ambience, stem_layer); four family groups/eight third-variant comparisons (UI, impact, movement, ambience). Thresholds: exact 48,000-Hz mono PCM16; duration ±.001 s; peak <.95 FS; RMS >=.001 FS; fixture-specific whole-wave centroid bands (UI 250–4,000, impact 50–15,000, movement 100–16,000, ambience 5–200, stems 100–2,000 Hz); loop endpoint jump <=.03 FS and outer slope mismatch <=.001 FS/sample; distinctness duration delta >=.020 s **or** relative centroid delta >=.10; section validity exact 192,000 samples, two 96,000-sample sections, 30-Hz amplitudes >=.01 FS and section RMS >=.001 FS; section contrast >=6 dB; internal section join gap <=.03 FS and slope mismatch <=.001 FS/sample.

Eight prior invalid-fixture outcomes: `short_sections` section-count failure; `corrupt` decode failure; `wrong_format` format failure; `odd_sections` section-count failure; `native16_probe` expected pass; `native24_probe`, `stereo48_probe`, and `mono441_probe` format failures. These are fixture-validation outcomes, not setup errors. Prior58 preservation records also include the five generic/four family comparisons, thresholds, invalid cases, and normal restoration. None were re-run by this guard.

## Scope / boundaries

I wrote only `.shokunin/audio/reports/round-50/r50-guard.md`. No shared source, LOG, SCORECARD, canonical artifact, or other report was edited; no commit or push. No channel-agnostic stereo handling, audition, quality, perception, production, rights, engine, publishing, or promotion inference is made.


## Prior60 replay and other preservation evidence (carried forward)

Round 50's named non-author replay ran **60** fresh serial commands and produced 60 distinct receipts: **26 exit 0 / 34 expected fixture-validation exit 1**. Its prior58 subset was **25/33**, matching the Round 49 ledger; first/final normal were identical JSON with 17 canonical measurements clean and no failures. This guard did not repeat that replay, normal restoration, or receipt comparison. Those are Round 50 verifier findings, not new Round 51 execution.

Carried-forward checks: five generic `_alt` comparisons (UI, impact, movement, ambience, stem_layer); four family groups and eight third-variant comparisons (UI, impact, movement, ambience). Thresholds: exact 48,000-Hz mono PCM16; duration ±.001 s; peak <.95 FS; RMS >=.001 FS; fixture-specific centroid bands (UI 250–4,000, impact 50–15,000, movement 100–16,000, ambience 5–200, stems 100–2,000 Hz); loop endpoint jump <=.03 FS and outer slope mismatch <=.001 FS/sample; distinctness duration delta >=.020 s or relative centroid delta >=.10; section validity exact 192,000 samples/two 96,000-sample sections, 30-Hz component amplitudes >=.01 FS and section RMS >=.001 FS; section contrast >=6 dB; internal join gap <=.03 FS and slope mismatch <=.001 FS/sample.

Eight invalid-probe outcomes carried forward: `short_sections` section-count failure; `corrupt` decode failure; `wrong_format` format failure; `odd_sections` section-count failure; `native16_probe` expected pass; `native24_probe`, `stereo48_probe`, and `mono441_probe` format failures. These are fixture-validation outcomes, not setup errors. Normal restoration and all these checks were recorded in prior replay evidence, not run by this guard.

## Scope and write boundary

I wrote only `.shokunin/audio/reports/round-51/r51-guard.md`. No shared source, LOG, SCORECARD, canonical artifact, or other report was edited; no commit or push. No broad bit-depth/codec/conversion or quality conclusion is made.
