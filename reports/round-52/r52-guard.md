# R52 guard — preservation and replay readiness

## Result

**Guard status: preservation checks pass for the currently available R51 baseline; the R52 integrated 64-command replay cannot yet be certified.** At inspection, `corpus/fixtures/measure_audio.py` contains no `--probe-ui-pcm8` flag (`'probe-ui-pcm8' in source` evaluated `False`), and no R52 runner receipts exist. I did not edit shared source, LOG, SCORECARD, canonical artifacts, or other reports. This is a guard report only; no conclusion on an integrated R52 candidate.

## Canonical 17 and established metrics

Read-only audit found 17 WAVs in `.shokunin/audio/corpus/artifacts/`. I hashed each current WAV with Python `hashlib.sha256` and read the corresponding measurements from fresh R51 normal receipts `20261013T102814760288Z-normal/measurements.json` and `20261013T102917940108Z-normal/measurements.json`. Their 17 measurement objects are exactly equal, all failures are empty, and every current canonical WAV hash/measurement is listed below. R51's named non-author verifier independently recorded all 17 hashes matching its first normal run and compared that normal result with R50. Thus these form a preserved baseline for a future R52 replay; this guard did not independently retrieve or compare the pre-R51 committed canonical hash manifest.

| Fixture | Current SHA-256 | duration s | peak FS | RMS dBFS | centroid Hz |
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

## Prior 62-mode replay and structural checks

I parsed all 62 receipt JSON files from the R51 non-author replay (`20261013T102814760288Z` through `20261013T102917940108Z`): 62 distinct receipt paths, 27 records with no fixture failure (expected process exit 0), 35 records with expected fixture validation failure (expected process exit 1). Order begins normal, PCM24, PCM16; the remaining 60 modes preserve the R50 suite in sequence. Receipt #2 reports only `format: expected PCM16`; #3 has no failures. First and last normal measurements are identical (17 canonical entries, no failures). This is R51 replay evidence, **not** a fresh R52 64-run replay or validation of R52 wiring.

The first normal receipt retains all five generic `_alt` distinctness comparisons (`ui_alt`, `impact_alt`, `movement_alt`, `ambience_alt`, `stem_layer_alt`), all four family-comparison sections (`ui`, `impact`, `movement`, `ambience`; two rows each), and all three section records (`stem_sections`, `stem_layer`, `stem_layer_alt`). It contains the unchanged numeric threshold table, including duration ±0.001 s, peak `<0.95`, RMS `>=0.001`, centroid bands, loop/seam and section limits. The invalid receipt records the same eight classifications: `short_sections` section count; `corrupt` decode; `wrong_format` format; `odd_sections` section count; `native16_probe` expected pass; `native24_probe`, `stereo48_probe`, and `mono441_probe` format.

The raw R51 receipt check was performed in the REPL by loading each JSON and counting nonempty `measurements[*].failures` plus `invalid_probes[*].status == expected_failure`; result `{exit 0: 27, exit 1: 35}`. No commands were run against a R52 flag. The written R51 verifier ledger identifies each exact invocation as `python3 .shokunin/audio/corpus/fixtures/measure_audio.py [flag]`; its first and final commands were `python3 .shokunin/audio/corpus/fixtures/measure_audio.py`, each reported exit 0. The two PCM-depth invocations in that ledger were `--probe-ui-pcm24` exit 1 (sole expected format failure) and `--probe-ui-pcm16` exit 0.

## Guard handoff

Before treating R52 as verified, rerun the complete 64-command serial suite against integrated current source with two new R52 modes in the declared first positions; require 29 exit 0 / 35 expected exit 1, exact prior62 mode/failure-map preservation, canonical17 hashes/metrics unchanged, prior five generic and four family comparisons, thresholds/sections/eight invalid classifications retained, and clean normal restoration. Record any setup errors separately from gate outcomes. No broad codec, fidelity, audibility, quality, production, rights, engine, or promotion claim follows from this guard.
