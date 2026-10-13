# Round 39 guard — canonical preservation and denominator-orientation fit

## Scope and limits

I read the Round 39 declaration in `.shokunin/audio/LOG.md`. This guard records the declared 17 canonical WAV SHA-256/metrics, prior replay context, generic comparison records, and local numerical fit evidence. I ran no serial runner replay and make no claim that either newly declared opt-in mode is integrated or runner-verified. I did not audition audio or assess sound quality, production, rights, engine suitability, publishing, or promotion. I did not edit shared source, LOG, SCORECARD, canonical assets, or any other report, and made no commits or pushes.

## Old 17 canonical WAVs

Clean-before revision declared in the Round 39 LOG: `03fc02d386328742e6f7ae727d1c18d08c4a0b48`. The following established 17-file measurements and SHA-256 values are carried forward from the Round 38 guard and independent verifier; all are 48 kHz mono PCM16, with no ordinary failures in the recorded normal measurements. These are numeric fixture measurements, not perceptual assessments.

| Canonical | SHA-256 | Duration (s) | Rate | Ch | Encoding | Peak FS | RMS | Centroid | Ordinary failures |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| `ui` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` | 0.12 | 48000 | 1 | pcm_s16le/16 | 0.375946044921875 | -19.991687666366516 dBFS | 966.8966593379727 Hz | none |
| `ui_alt` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` | 0.16 | 48000 | 1 | pcm_s16le/16 | 0.31878662109375 | -20.525534144496497 dBFS | 1423.1532540422852 Hz | none |
| `ui_third` | `734a0a47077f5b614b5d51d486b88a51940c7d61ecea0878642b60a0103513bc` | 0.2 | 48000 | 1 | pcm_s16le/16 | 0.375946044921875 | -22.20695387316763 dBFS | 966.7216217320357 Hz | none |
| `impact` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` | 0.32 | 48000 | 1 | pcm_s16le/16 | 0.80877685546875 | -20.40218668053459 dBFS | 10843.127202979935 Hz | none |
| `impact_alt` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` | 0.32 | 48000 | 1 | pcm_s16le/16 | 0.75616455078125 | -17.32957040921516 dBFS | 473.79153568100764 Hz | none |
| `impact_third` | `d14376241f409f07edde30fbcef86b5f060ff36f731b7578fd9934d1dc1b39bf` | 0.4 | 48000 | 1 | pcm_s16le/16 | 0.45611572265625 | -20.84958464133168 dBFS | 6838.143302962279 Hz | none |
| `movement` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` | 0.24 | 48000 | 1 | pcm_s16le/16 | 0.53948974609375 | -23.779940832329185 dBFS | 11934.484045946316 Hz | none |
| `movement_alt` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` | 0.36 | 48000 | 1 | pcm_s16le/16 | 0.639312744140625 | -21.987315616484317 dBFS | 12024.214879348818 Hz | none |
| `movement_third` | `0e5f815e1987e13646170571e1f1e977b25e3566d90ebcca558c72ed07851d44` | 0.3 | 48000 | 1 | pcm_s16le/16 | 0.489501953125 | -14.025186267550422 dBFS | 4553.583280111138 Hz | none |
| `ambience` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` | 2.0 | 48000 | 1 | pcm_s16le/16 | 0.174591064453125 | -18.153351293681563 dBFS | 36.61640767851373 Hz | none |
| `ambience_alt` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` | 2.0 | 48000 | 1 | pcm_s16le/16 | 0.199737548828125 | -17.67032381358842 dBFS | 58.01919713436623 Hz | none |
| `ambience_third` | `c2c8e0bb2385bc93b39c70b719d0f56553c771969986ef1f732d24af5677d404` | 2.0 | 48000 | 1 | pcm_s16le/16 | 0.225006103515625 | -16.92261930553234 dBFS | 112.03210352691181 Hz | none |
| `stem` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` | 2.0 | 48000 | 1 | pcm_s16le/16 | 0.32379150390625 | -14.881434973008286 dBFS | 272.6756827789141 Hz | none |
| `stem_sections` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` | 4.0 | 48000 | 1 | pcm_s16le/16 | 0.17236328125 | -23.066521225821248 dBFS | 201.87069023000652 Hz | none |
| `stem_layer` | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` | 4.0 | 48000 | 1 | pcm_s16le/16 | 0.05999755859375 | -30.28756654598196 dBFS | 190.1433267529918 Hz | none |
| `stem_layer_alt` | `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` | 4.0 | 48000 | 1 | pcm_s16le/16 | 0.04998779296875 | -31.667277345674258 dBFS | 277.9513846028647 Hz | none |
| `stem_layer_third` | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` | 4.0 | 48000 | 1 | pcm_s16le/16 | 0.04998779296875 | -31.66724765274306 dBFS | 287.93805923844434 Hz | none |

## Generic five and four family groups

The generic distinctness predicate remains duration delta `>= .020 s OR` baseline-relative centroid delta `>= .10`. The five unchanged generic `_alt` measurements, carried forward in the Round 38 normal receipt, are:

| Generic pair | Duration delta (s) | Relative centroid delta | Result |
|---|---:|---:|---|
| `ui` → `ui_alt` | 0.04000000000000001 | 0.47187731004956435 | pass |
| `impact` → `impact_alt` | 0.0 | 0.9563048992406177 | pass |
| `movement` → `movement_alt` | 0.12 | 0.007518618572621081 | pass |
| `ambience` → `ambience_alt` | 0.0 | 0.5845136323520758 | pass |
| `stem_layer` → `stem_layer_alt` | 0.0 | 0.46179931396667484 | pass |

The four explicit family groups (UI, impact, movement, ambience; two comparisons apiece) remain as previously recorded. Round 38 verifier reports all eight match baseline and pass. The unchanged pre-existing UI, impact, and movement records are:

| Family | Pair | Duration delta (s) | Relative centroid delta |
|---|---|---:|---:|
| UI | `ui` → `ui_third` | 0.08000000000000002 | 0.00018103031409457665 |
| UI | `ui_alt` → `ui_third` | 0.04000000000000001 | 0.3207185389302337 |
| Impact | `impact` → `impact_third` | 0.08000000000000002 | 0.36935690461299725 |
| Impact | `impact_alt` → `impact_third` | 0.08000000000000002 | 13.432810187572105 |
| Movement | `movement` → `movement_third` | 0.06 | 0.6184516010427937 |
| Movement | `movement_alt` → `movement_third` | 0.06 | 0.6212989100908565 |
| Ambience | `ambience` → `ambience_third` | 0.0 | 2.059614818322321 |
| Ambience | `ambience_alt` → `ambience_third` | 0.0 | 0.9309488765840295 |

The Round 39 declaration says these five generic records, four family groups, thresholds, and canonical metrics are invariants; I did not rerun the suite to independently revalidate them.

## Prior outcomes and invalid statuses

Round 36 independent verifier records 34 serial invocations: 13 exit 0 and 21 expected fixture-validation exit 1, with no other replay exits or corrected-replay setup failures. Its prior-33 subset was 12 exit 0 / 21 expected exit 1; invocation #34 was a normal restore. Round 37 independent replay preserved prior34 as 13 exit 0 / 21 expected exit 1 and added one expected negative control (full 13/22). Round 38 independent replay preserved prior35 as **13 exit 0 / 22 expected exit 1**, and its full 36-run sequence was **14 exit 0 / 22 expected exit 1**, with final normal restore. Round 39 LOG declares preservation of all prior36 outcomes, eight invalid statuses, and restore behavior. I did not run Round 39 replay, so these are carried-forward records, not my replay verdict.

The eight invalid statuses carried forward are: `short_sections` expected failure (section count); `corrupt` expected failure (decode); `wrong_format` expected failure (format); `odd_sections` expected failure (section count); `native16_probe` expected pass; `native24_probe`, `stereo48_probe`, and `mono441_probe` expected failure (format).

## Round 39 local numerical fit

I ran the executor's project-helper measurement script on its two scratch WAVs. Project helper `measure()` with ambience spec `(2.0, 5, 200, True)` reports:

| Scratch role | Duration | Format | Centroid | Peak FS | RMS dBFS | Seam endpoint delta | Seam slope delta | Ordinary/loop failures |
|---|---:|---|---:|---:|---:|---:|---:|---|
| A / baseline | 2.0 s | 48 kHz mono PCM16 | 70.7623033885285 Hz | 0.218170166015625 | -18.633069022379566 | 0.0013427734375 | 0.000030517578125 | none |
| B / variant | 2.0 s | 48 kHz mono PCM16 | 78.18153634552728 Hz | 0.2581787109375 | -17.61980253353166 | 0.001953125 | 0.000030517578125 | none |

Measured absolute centroid gap is `7.419232956998783 Hz`; forward lower-baseline relative delta is **0.10484725060831668** (> .10), reverse higher-baseline relative delta is **0.09489750782344704** (< .10). Durations are equal (delta **0.0 s**), so the duration arm is false in both orientations; the measured denominator change yields the declared strict split on centroid alone. Both ordinary/seam failure lists are empty. This is only a local numerical fit; no runner mode receipt was produced by this guard.

Executor scratch SHA-256 values, calculated for this report: baseline `d516b687e91b983e60a7353cd19bb62f544be99ea9ec31a8bd7b5b2b4457d062`; variant `4f9c5365744b22643ca9fb48c6656529550f3457243871cc9a4c1503d035baec`. Hashes differ. The independent alt scratch fit is also a qualifying numerical candidate: 108/114 Hz source-labelled files measure centroids `125.06515861515496` / `138.2410529357521` Hz, forward relative `0.10535223771747193`, reverse `0.09531100957919258`, equal 2.0 s durations, empty ordinary/loop failures, hashes `7f4cdfefa6e52a8ff44268396b5c09ea459a648a5ac4cad0f42722fe5fc29938` / `24203978fe84384db6686e8cf065e1f06f2eb966e88e92578f5da1bb9c5b9482`. These are candidate measurements, not integrated-mode evidence. Its recorded other numeric attempts did not fit the strict condition: source 55/60 measured centroids `81.1592352376286` / `67.37182625966985`, lower-base relative `0.20464650794559466`, higher-base relative `0.1698809622538972`; source 65/75 measured `91.03372963007341` / `81.62439856673954`, lower-base relative `0.11527596194954381`, higher-base relative `0.10336093117979261`. Both are numerical fit misses; ordinary/loop failures were empty. These failed fits are not setup errors.

## Exact command and exit

Exact shell command run from repository root:

- `python3 .shokunin/audio/corpus/live/round-39/executor/measure_pair.py` — **exit 0**. Output gave the project-helper records above and forward/reverse deltas. I did not run runner commands, a canonical hash command, or another shell command for this report. No failed setup attempt occurred in this guard.

The available evidence supports only that a local candidate pair numerically straddles the baseline-relative `.10` condition when the denominator is reversed. It is not runner validation, an exact-boundary or universal OR-rule calibration, nor an assessment of perception, spectrum similarity, audible seam, sound quality, production, rights, engine, publishing, or promotion.
