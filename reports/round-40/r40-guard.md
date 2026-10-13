# Round 40 guard — canonical preservation and outer-endpoint fit audit

## Scope and verdict

I read the Round 40 declaration in `.shokunin/audio/LOG.md`. It tests the outer-loop first/last decoded PCM endpoint comparator at adjacent PCM16 values around `.03`; this differs from R21's internal section join. I inspected existing scratch WAVs only; no fixture runner or shell command was run. Four candidates hit the requested endpoint counts, but all miss the required 5–200 Hz ambience centroid band. None is a qualifying full numeric fit or runner-verified control.

No shared source, LOG, SCORECARD, canonical asset, or other report was edited. I did not audition audio or assess sound quality, production, rights, engine suitability, publishing, or promotion. No commits or pushes.

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

The unchanged generic predicate is duration delta `>= .020 s OR` baseline-relative centroid delta `>= .10`. The five generic comparisons are unchanged and all pass, as recorded in the Round 38 normal receipt / Round 39 guard:

| Generic pair | Duration delta (s) | Relative centroid delta | Result |
|---|---:|---:|---|
| `ui` → `ui_alt` | 0.04000000000000001 | 0.47187731004956435 | pass |
| `impact` → `impact_alt` | 0.0 | 0.9563048992406177 | pass |
| `movement` → `movement_alt` | 0.12 | 0.007518618572621081 | pass |
| `ambience` → `ambience_alt` | 0.0 | 0.5845136323520758 | pass |
| `stem_layer` → `stem_layer_alt` | 0.0 | 0.46179931396667484 | pass |


The four family groups (UI, impact, movement, ambience; two comparisons each) and all eight comparisons remain as recorded in the Round 38 verifier, all passing. These measurements are carried forward, not independently rerun here. No thresholds changed.

## Prior38 replay and invalid statuses

## Prior outcomes and invalid statuses

Round 36 independent verifier records 34 serial invocations: 13 exit 0 and 21 expected fixture-validation exit 1, with no other replay exits or corrected-replay setup failures. Its prior-33 subset was 12 exit 0 / 21 expected exit 1; invocation #34 was a normal restore. Round 37 independent replay preserved prior34 as 13 exit 0 / 21 expected exit 1 and added one expected negative control (full 13/22). Round 38 independent replay preserved prior35 as **13 exit 0 / 22 expected exit 1**, and its full 36-run sequence was **14 exit 0 / 22 expected exit 1**, with final normal restore. Round 39 LOG declares preservation of all prior36 outcomes, eight invalid statuses, and restore behavior. I did not run Round 39 replay, so these are carried-forward records, not my replay verdict.

The eight invalid statuses carried forward are: `short_sections` expected failure (section count); `corrupt` expected failure (decode); `wrong_format` expected failure (format); `odd_sections` expected failure (section count); `native16_probe` expected pass; `native24_probe`, `stereo48_probe`, and `mono441_probe` expected failure (format).


Round 39's independent verifier records 38 invocations: 15 exit 0 / 23 expected validation exit 1; its prior36 subset was 14/22, with eight invalid statuses preserved and a final normal restore. I did not independently replay them in this guard; that is carried-forward evidence, not a Round 40 replay result. Round 40's separately assigned verifier must confirm preservation.

## Decoded scratch candidate measurements

I read the four existing WAV files under `.shokunin/audio/corpus/live/round-40/` as PCM16 and computed endpoint, slope, peak, RMS, and centroid from decoded samples. Each is 96,000 frames, 48 kHz mono PCM16; SHA values are distinct. Endpoint values hit 983/984 counts exactly, and all side slopes are within `.001` FS/sample. All four centroids exceed the required 5–200 Hz band. These are local calculations, not SoX runner receipts; full ordinary-gate status and runner exits remain unverified.

| Candidate | SHA-256 | First / last sample | Endpoint delta | Slope mismatch | Duration | Peak FS | RMS dBFS | Centroid Hz | Numeric result |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| `executor/loop983.wav` | `67e91c188809cf616701c5a3243e85b80ed9b2541e009728b8a56c8c906928bf` | 0.05999755859375 / 0.089996337890625 | 983/32768 = 0.029998779296875 | 0.0 | 2.0 s | 0.089996337890625 | -26.777874215442846 | 1347.4443970064556 | **fit miss: centroid > 200 Hz** |
| `executor/loop984.wav` | `ea9bb1aaebb4f66f1f7b0ff9b2498333479086f8aa1a382bde662aeee5acb962` | 0.05999755859375 / 0.09002685546875 | 984/32768 = 0.030029296875 | 0.0 | 2.0 s | 0.09002685546875 | -26.776607810103812 | 1348.0101089372424 | **fit miss: centroid > 200 Hz** |
| `alt/edge983.wav` | `dc2d8591f06eae59039f15b07d80365dd713d1da1eb5bb4ad87294635aa77f12` | 0.0 / 0.029998779296875 | 983/32768 = 0.029998779296875 | 0.0006103515625 | 2.0 s | 0.17962646484375 | -19.383174296399382 | 959.4447235467705 | **fit miss: centroid > 200 Hz** |
| `alt/edge984.wav` | `4c529dab929ac8236630a309454eeb2aa5b1cc1656ddea39f47d77d5c1ebbb04` | 0.0 / 0.030029296875 | 984/32768 = 0.030029296875 | 0.0006103515625 | 2.0 s | 0.179656982421875 | -19.38294721628338 | 959.8227022766018 | **fit miss: centroid > 200 Hz** |

The bracket arithmetic is `983/32768 = 0.029998779296875` (not greater than `.03`) versus `984/32768 = 0.030029296875` (greater than `.03`). This establishes only the endpoint values and expected comparator polarity. As every candidate misses the centroid band, none establishes the required 983 clean pass or 984 sole endpoint failure. This does not validate SoX decoded values, runner behavior, or other ordinary gates.

## Setup errors versus numeric failed fits; commands

- **Setup errors:** none; no shell/helper command was run, so there are no setup exit codes.
- **Numeric fit failures:** four candidates hit the intended endpoint count but miss the centroid band. These are numeric failures, not setup errors and not runner outcomes.
- **Runner outcomes:** neither mode was executed by this guard; no runner exit or receipt is claimed.

There are no shell commands/exits to quote. This is local numeric fixture evidence only—not a claim about exact equality at `.03`, audible clicks/seams, quality, rights, engine, production, publishing, or promotion.
