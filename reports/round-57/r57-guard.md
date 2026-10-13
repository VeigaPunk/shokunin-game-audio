# R57 guard — prior battery, canonical baseline, and scratch pair audit

## Scope and disposition

Read the standing brief, R57 declaration in `.shokunin/audio/LOG.md`, R56 source/report evidence, and the R57 executor/alt scratch files. This is a read-only guard of the prior baseline and the locally constructed candidate; it is **not** an integrated runner replay or an integration claim. No shared source, LOG, SCORECARD, canonical artifact, or other report was changed. R57 executor/alt artifacts remain under `corpus/live/round-57/{executor,alt}/`; this guard wrote only this report. No commit or push.

## R57 candidate: observed decoder and project results

Executor scratch contains mono 48-kHz 5,760-frame signed PCM payload, WAVE_FORMAT_EXTENSIBLE `fmt` size 40, `cbSize=22`, channel mask `0x4`, PCM subtype GUID `00000001-0000-0010-8000-00aa00389b71`, and 16-bit container. The declared variable is `wValidBitsPerSample` 15 vs 16. Both WAVs are 11,588 bytes; their payloads are identical (11,520 bytes, SHA-256 `67ea695da5665554f467cae513d0c2d3d62d588516299f7eb4872bf79d58df4e`). WAV SHA-256: valid-15 `d3835a35014b3536c1710aafed8a104ef32eaa84acb37c87213127785f18175c`; valid-16 `bd7d95901935c0effe21fd64e44a47487372be9d0c80f86cc725380df0352f47`.

Exact ffprobe command, run separately on each file (both exit **0**):

```sh
ffprobe -v error -show_entries stream=codec_name,sample_fmt,bits_per_sample,sample_rate,channels,duration -of json <file>
```

Both report `codec_name=pcm_s16le`, `sample_fmt=s16`, `bits_per_sample=16`, `sample_rate=48000`, `channels=1`, `duration=0.120000`. This is the decoder's reported container/sample format; the `wValidBitsPerSample` header values remain 15 and 16 respectively. Do not conflate those fields.

Exact SoX commands (both exit **0**):

```sh
sox .shokunin/audio/corpus/live/round-57/executor/valid-15.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-57/executor/valid-15.wav.f32
sox .shokunin/audio/corpus/live/round-57/executor/valid-16.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-57/executor/valid-16.wav.f32
```

Each emits 5,760 float32 samples, 23,040 bytes, SHA-256 `d80f13858e4fdcf641f2164b440a99a42711fd4213239ad809c8136ee4620ce7`; vectors are elementwise equal (max absolute difference `0.0`) for this executor pair.

The unchanged project UI measurement function was also run successfully on the two scratch files with this command form (each exit **0**; absolute paths were supplied):

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.measure("ui",m.SPECS["ui"],Path("<absolute-file-path>")))'
```

Both report duration `0.12 s`, 48,000 Hz mono, `pcm_s16le`, 16 bits/sample, peak `0.31536865234375`, RMS `-14.628519169868087 dBFS`, centroid `1123.322704293326 Hz`, bandwidth `276.15444981222976 Hz`, `integrated_lufs=null`, and no failures. These are scratch measurements, not runner receipts. The alt independently constructs a different payload pair (valid15 WAV SHA `4f41ace3a386c78217c991dae6972be49f3be4a9fa918211c58e3a019af47b2b`; valid16 SHA `95d180f4c894751924317eb9b7add4d5c84e714a7807eeb14d1319a6ff1f785f`; shared payload SHA `a6ec402df430818fd02a8437a85af7ab335e51084ca7e224f2b1b15cc2d2b89a`). I did not independently run ffprobe, SoX, or project measurement on the alt pair; no alt outcome is inferred.

One guard measurement invocation initially used relative `Path(...)` arguments and returned exit **1** with `ValueError: '<relative path>' is not in the subpath of '<absolute corpus root>'`; it created no runner receipt. This is a guard-command path/setup error, not a decode or validation result. Retrying the identical measurement with absolute file paths produced the two exit-0 results above. No receiptless decode/setup failure occurred for either valid-bit WAV: ffprobe, SoX, and measurement all produced results.

## Prior 72, canonical 17, predicate structure

R56's non-author verifier recorded 72 fresh serial runner receipts: **34 exit 0 and 38 expected validation exit 1**. Its exact prior-70 mapping is preserved in the R56 verifier report and compares complete parsed JSON to R55. R56 guard audited that report; this guard did not rerun those 72 commands and does not claim fresh R57 receipt replay. R57's declaration requires preserving those receipts/battery; none were modified.

I recomputed SHA-256 for every canonical file in `corpus/artifacts/` and compared with the R56 verifier table: **17/17 match**. The baseline hashes and normal-receipt metrics are:

| Fixture | SHA-256 | Duration s | Peak FS | RMS dBFS | Centroid Hz |
|---|---|---:|---:|---:|---:|
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` | 0.12 | 0.375946044921875 | -19.991687666366516 | 966.8966593379727 |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` | 0.16 | 0.31878662109375 | -20.525534144496497 | 1423.1532540422852 |
| `ui_third.wav` | `734a0a47077f5b614b5d51d486b88a51940c7d61ecea0878642b60a0103513bc` | 0.2 | 0.375946044921875 | -22.20695387316763 | 966.7216217320357 |
| `impact.wav` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` | 0.32 | 0.80877685546875 | -20.40218668053459 | 10843.127202979935 |
| `impact_alt.wav` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` | 0.32 | 0.75616455078125 | -17.32957040921516 | 473.79153568100764 |
| `impact_third.wav` | `d14376241f409f07edde30fbcef86b5f060ff36f731b7578fd9934d1dc1b39bf` | 0.4 | 0.45611572265625 | -20.84958464133168 | 6838.143302962279 |
| `movement.wav` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` | 0.24 | 0.53948974609375 | -23.779940832329185 | 11934.484045946316 |
| `movement_alt.wav` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` | 0.36 | 0.639312744140625 | -21.987315616484317 | 12024.214879348818 |
| `movement_third.wav` | `0e5f815e1987e13646170571e1f1e977b25e3566d90ebcca558c72ed07851d44` | 0.3 | 0.489501953125 | -14.025186267550422 | 4553.583280111138 |
| `ambience.wav` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` | 2.0 | 0.174591064453125 | -18.153351293681563 | 36.61640767851373 |
| `ambience_alt.wav` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` | 2.0 | 0.199737548828125 | -17.67032381358842 | 58.01919713436623 |
| `ambience_third.wav` | `c2c8e0bb2385bc93b39c70b719d0f56553c771969986ef1f732d24af5677d404` | 2.0 | 0.225006103515625 | -16.92261930553234 | 112.03210352691181 |
| `stem.wav` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` | 2.0 | 0.32379150390625 | -14.881434973008286 | 272.6756827789141 |
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` | 4.0 | 0.17236328125 | -23.066521225821248 | 201.87069023000652 |
| `stem_layer.wav` | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` | 4.0 | 0.05999755859375 | -30.28756654598196 | 190.1433267529918 |
| `stem_layer_alt.wav` | `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` | 4.0 | 0.04998779296875 | -31.667277345674258 | 277.9513846028647 |
| `stem_layer_third.wav` | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` | 4.0 | 0.04998779296875 | -31.66724765274306 | 287.93805923844434 |

The R56 verifier records five generic `_alt` distinctness comparisons; four family maps (UI, impact, movement, ambience), two comparisons each; and four section records (stem sections and three stem layers). Unchanged thresholds: 48,000 Hz; duration ±0.001 s; peak `<0.95`; RMS `>=0.001`; centroid bands UI 250–4,000 Hz, impact 50–15,000 Hz, movement 100–16,000 Hz, ambience 5–200 Hz, stem 100–2,000 Hz; loop endpoint delta `<=0.03`; loop slope `<=0.001` full-scale/sample; section contrast `>=6 dB`; section component amplitude `>=0.01`; section RMS `>=0.001`; internal-join adjacent delta `<=0.03`; internal-join side-slope mismatch `<=0.001` full-scale/sample; distinctness duration delta `>=0.020 s` or relative centroid delta `>=10%` per battery predicate. Eight invalid-battery classifications remain: `short_sections` section count; `corrupt` decode; `wrong_format` format; `odd_sections` section count; `native16_probe` pass; `native24_probe` format; `stereo48_probe` format; `mono441_probe` format.

## Guard boundary

Observed local scratch results show that ffprobe reports 16-bit `pcm_s16le` for both executor headers and that this project's direct UI measure accepts both with identical reported metrics; SoX decoded vectors match. This is not proof of arbitrary 15-valid-bit WAV behavior or universal standards/decoder conformance. No integrated R57 runner probe, new receipt battery, source diff, changed threshold, canonical update, integration, calibration verdict, promotion, audibility/fidelity, production, rights, engine, or publication claim is made here.
