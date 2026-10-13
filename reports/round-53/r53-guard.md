# R53 guard — baseline and replay readiness

## Result

**Preservation baseline checks pass; R53 integration/replay is not yet present, so this is not an R53 validation or integration claim.** The declared R53 entry in `.shokunin/audio/LOG.md` specifies a 5,760-frame mono 48 kHz IEEE-float32-vs-signed-PCM16 UI-shaped pair and a 66-command future replay. At inspection, `measure_audio.py` contains the R52 `--probe-ui-pcm8` and `--probe-ui-pcm16-r52` flags but no R53 float-pair flag; `.shokunin/audio/reports/round-53/` did not exist. No R53 command was run. I did not edit shared source, LOG, SCORECARD, canonical artifacts, or other reports.

## Canonical 17 baseline

I read the R52 guard's canonical measurement table and independently SHA-256 hashed the current 17 WAVs in `corpus/artifacts/`; all current file hashes agree with that table. The measurements below are the table's fresh R51 normal-receipt metrics preserved by R52 guard, not newly measured by this R53 guard. R52's verifier further reports the canonical paths/measurements unchanged in its fresh replay. This is a current baseline cross-check, not a pre-R51 committed-manifest comparison.

| Fixture | SHA-256 | Duration s | Peak FS | RMS dBFS | Centroid Hz |
|---|---|---:|---:|---:|---:|
| ui | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` | 0.12 | 0.375946044921875 | -19.991687666366516 | 966.8966593379727 |
| ui_alt | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` | 0.16 | 0.31878662109375 | -20.525534144496497 | 1423.1532540422852 |
| ui_third | `734a0a47077f5b614b5d51d486b88a51940c7d61ecea0878642b60a0103513bc` | 0.20 | 0.375946044921875 | -22.20695387316763 | 966.7216217320357 |
| impact | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` | 0.32 | 0.80877685546875 | -20.40218668053459 | 10843.127202979935 |
| impact_alt | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` | 0.32 | 0.75616455078125 | -17.32957040921516 | 473.79153568100764 |
| impact_third | `d14376241f409f07edde30fbcef86b5f060ff36f731b7578fd9934d1dc1b39bf` | 0.40 | 0.45611572265625 | -20.84958464133168 | 6838.143302962279 |
| movement | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` | 0.24 | 0.53948974609375 | -23.779940832329185 | 11934.484045946316 |
| movement_alt | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` | 0.36 | 0.639312744140625 | -21.987315616484317 | 12024.214879348818 |
| movement_third | `0e5f815e1987e13646170571e1f1e977b25e3566d90ebcca558c72ed07851d44` | 0.30 | 0.489501953125 | -14.025186267550422 | 4553.583280111138 |
| ambience | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` | 2.0 | 0.174591064453125 | -18.153351293681563 | 36.61640767851373 |
| ambience_alt | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` | 2.0 | 0.199737548828125 | -17.67032381358842 | 58.01919713436623 |
| ambience_third | `c2c8e0bb2385bc93b39c70b719d0f56553c771969986ef1f732d24af5677d404` | 2.0 | 0.225006103515625 | -16.92261930553234 | 112.03210352691181 |
| stem | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` | 2.0 | 0.32379150390625 | -14.881434973008286 | 272.6756827789141 |
| stem_sections | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` | 4.0 | 0.17236328125 | -23.066521225821248 | 201.87069023000652 |
| stem_layer | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` | 4.0 | 0.05999755859375 | -30.28756654598196 | 190.1433267529918 |
| stem_layer_alt | `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` | 4.0 | 0.04998779296875 | -31.667277345674258 | 277.9513846028647 |
| stem_layer_third | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` | 4.0 | 0.04998779296875 | -31.66724765274306 | 287.93805923844434 |

## R52 prior-64 replay audit

Read `.shokunin/audio/reports/round-52/r52-verifier.md` and its complete 64-row ledger. Its reported fresh serial replay contains 64 unique receipts in this order: R52 normal, `--probe-ui-pcm8`, `--probe-ui-pcm16-r52`, then R51's complete 62-command sequence in unchanged order (ending normal). Reported exits: **28 exit 0 / 36 expected validation exit 1**. The exact prior-62 subset is **27/35**, with modes and raw receipt contents equal to the R51 sequence; no reused receipts. The two R52 probes: PCM8 sole `format: expected PCM16` (exit 1), PCM16 clean (exit 0). R52's 64-run replay is the established prior baseline, not a fresh R53 replay.

R52 normal receipt preserved five generic `_alt` distinctness comparisons (`ui_alt`, `impact_alt`, `movement_alt`, `ambience_alt`, `stem_layer_alt`) and four family-comparison groups (UI, impact, movement, ambience; two rows each). The threshold table remained: rate 48000 Hz; duration tolerance 0.001 s; peak `<0.95`; RMS `>=0.001`; loop endpoint delta `<=0.03`; loop slope delta `<=0.001` full scale/sample; section contrast `>=6 dB`; internal join adjacent delta `<=0.03`; side-slope mismatch `<=0.001` full scale/sample; section component amplitude `>=0.01`; section RMS `>=0.001`; distinctness duration delta `>=0.02 s`, centroid relative delta `>=0.1`, with the existing per-fixture centroid bands. The four section records are `stem_sections`, `stem_layer`, `stem_layer_alt`, `stem_layer_third`. The invalid probe classifications are preserved: `short_sections` section count; `corrupt` decode; `wrong_format` format; `odd_sections` section count; `native16_probe` expected pass; `native24_probe`, `stereo48_probe`, `mono441_probe` format. R52 verifier reports first/final normals identical, canonical hashes matching measurements, and prior-62 raw receipts exactly preserved.

## R53 handoff / bounded limitation

Per R53 LOG, the planned new float32 probe and PCM16 control should precede those exact 64 modes in the non-author replay; if both behave as declared, the 66-run total would be **29 exit 0 / 37 expected exit 1** (one new expected format rejection and one clean control). That is a prediction, not an observed count. Validate actual flags, pair metadata, measurements, receipts, and sequence only after integration. The R53 comparison is limited to its constructed float32/PCM16 pair and existing UI format predicate; this guard supplies no float codec metadata, candidate metrics, pair-fit, or integration evidence. No broader format, fidelity, quality, perceptual, production, rights, engine, or promotion claim follows.

## Guard actions / command record

No shell or measurement commands were run. In the Python REPL I read `LOG.md`, the R52 guard and verifier reports, `measure_audio.py`, and checked file presence/flags; I SHA-256 hashed the 17 current canonical WAV byte streams with `hashlib.sha256(path.read_bytes()).hexdigest()`. The checked current hashes matched the R52 guard table (all 17 listed above). No exit code applies to these in-process inspections; no ffprobe, SoX, fixture runner, or R53 validation exit is claimed. Exact future replay command list is intentionally not reproduced here: R52's verifier ledger contains the 64 unchanged prior commands; R53 LOG declares the two new modes but source does not yet expose them.
