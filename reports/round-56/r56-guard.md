# R56 guard — prior battery, canonical, and scope audit

## Scope and verdict

This is a bounded guard audit of the R56 declaration and the available R55 evidence. **No R56 integration, runner replay, gate result, or round admission is claimed.** At inspection, the available R56 wave-one reports are `r56-alt.md`, `r56-critic.md`, `r56-executor.md`, `r56-reviewer.md`, `r56-scout.md`, `r56-scribe.md`, and `r56-simplifier.md`; the fixture builder and runner have R55 modes but no R56 mask-zero/center flags, and there are no integrated R56 receipts. R56 executor/alt/critic/scout scratch files exist under their own round-56 role directories; they are not integrated runner evidence. The R56 reviewer and simplifier reports are source-only recommendations, not execution results. This guard wrote no shared source, LOG, SCORECARD, canonical fixture, or other report.

## R55 prior-70 baseline and replay audit

I read the standing brief, append-only R55 LOG declaration/closeout, R55 verifier and guard, and R55 executor/reviewer/scribe/adjudicator reports. I parsed the R55 verifier ledger and raw receipt JSON files read-only. The ledger contains **70 distinct receipt paths, all present**, with **32 exit 0 / 38 expected fixture-validation exit 1**. The two R55 probe commands in rows 2–3 both report exit 0 and empty failures. Its prior-68 R54 battery mapping (R55 rows 1 and 4–70) was compared by parsed JSON here: **68/68 full receipt objects match** their R54 counterparts, including the canonical measurements and battery maps. First and last R55 normal receipt objects match exactly. This guard did not rerun the commands; command exits below are the verifier's recorded exits, checked against its receipts.

The bounded R55 positive-control artifacts and measurements recorded by the executor/verifier are:

| Artifact | WAV SHA-256 | ffprobe metadata |
|---|---|---|
| `corpus/live/round-55/pair_standard_pcm16.wav` | `9ac26f38a7df9b1dd60c6130049d1e37056811fcd241f15a03559b5766bb4ba9` | `pcm_s16le`, `s16`, 16 bit, mono, 48000 Hz, `.120000` s |
| `corpus/live/round-55/pair_extensible_pcm16.wav` | `bd7d95901935c0effe21fd64e44a47487372be9d0c80f86cc725380df0352f47` | `pcm_s16le`, `s16`, 16 bit, mono, 48000 Hz, `.120000` s; tag `0xfffe`, `fmt` 40, valid bits 16, mask `0x4`, PCM subtype |

The R55 verifier's serial runner commands and receipts are `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-pcm16` (exit 0, `.shokunin/audio/corpus/live/runs/20261013T115709281095Z-ui-extensible-pcm16/measurements.json`, failures `[]`) and `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-standard-pcm16-r55` (exit 0, `.shokunin/audio/corpus/live/runs/20261013T115710311368Z-ui-standard-pcm16-r55/measurements.json`, failures `[]`). The verifier reports both `ffprobe` calls exit 0, and SoX-f32 decoded vectors byte-identical (SHA-256 `d80f13858e4fdcf641f2164b440a99a42711fd4213239ad809c8136ee4620ce7`). Both receipts report duration `.12 s`, peak `0.31536865234375`, RMS `-14.628519169868087 dBFS`, centroid `1123.322704293326 Hz`, bandwidth `276.15444981222976 Hz`. The verifier's exact command forms for independent checks are `ffprobe -v error -show_entries stream=codec_name,sample_fmt,bits_per_sample,sample_rate,channels,duration -of json <file>` and `sox <file> -t f32 -e floating-point - | sha256sum`; it records exit 0 for each. These are R55 verifier results, not commands run by this guard. R55 guard contains a malformed transcription of the extensible WAV digest; this audit relies on the verifier's receipt/artifact table and adjudicator's direct RIFF/hash check above, not the guard's mistyped value.

R55's ordinary PCM16-vs-valid-16/mask-`0x4` extensible positive control is not evidence for R56's mask-`0x0` case. No mask-0 metadata, decoded equality, metrics, or runner status has been verified here.

## Canonical 17, comparisons, thresholds, and invalid classifications

I SHA-256 checked the 17 current `corpus/artifacts/*.wav` files read-only and compared them with the R55 verifier's canonical list. All 17 match. Their duration, peak, RMS dBFS, and centroid values below are from the verified clean normal receipt and match the verifier's canonical table.

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

The verified normal battery has **five** generic `_alt` distinctness comparisons; four family comparison maps (UI, impact, movement, ambience), two comparisons each; and four section records (stem sections plus three stem layers). R55 verifier records unchanged thresholds: rate 48,000 Hz; duration ±0.001 s; peak `<0.95`; RMS `>=0.001`; per-fixture centroid bands (UI 250–4,000 Hz, impact 50–15,000 Hz, movement 100–16,000 Hz, ambience 5–200 Hz, stem family 100–2,000 Hz); loop endpoint delta `<=0.03`; loop slope `<=0.001` full-scale/sample; section contrast `>=6 dB`; section component amplitude `>=0.01`; section RMS `>=0.001`; internal-join adjacent delta `<=0.03`; internal-join side-slope mismatch `<=0.001` full-scale/sample; distinctness duration delta `>=0.020 s` or relative centroid delta `>=10%` as recorded by the battery's predicate.

The `--probe-invalid` receipt retains all eight classifications: `short_sections`—section count; `corrupt`—decode; `wrong_format`—format; `odd_sections`—section count; `native16_probe`—pass; `native24_probe`—format; `stereo48_probe`—format; `mono441_probe`—format. This is the prior invalid battery, not a new R56 test.

## Commands, limits, and disposition

This guard did not invoke the project runner, `ffprobe`, or SoX, and therefore has no guard-run command exits or new audio measurements to report. Read-only audit actions were Python inspection/parsing of the listed Markdown/JSON receipts and SHA-256 hashing of the 17 canonical WAVs; no audio was generated or mutated. The only report written by this guard is `.shokunin/audio/reports/round-56/r56-guard.md`.

Conclusion is limited to confirming the recorded prior-70 (R55) receipt battery and current canonical hashes/metrics. R56 mask-zero remains unverified: no claim about that mask, R56 integration, or R56 runner success/failure. No claim about other channel masks/layouts, universal WAVE_FORMAT_EXTENSIBLE behavior, standards conformance, codec support, fidelity, audibility, quality, production, rights, engine behavior, publication, or promotion.
