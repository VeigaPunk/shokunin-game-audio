# Round 41 guard — preservation and decoded numeric-fit audit

## Scope and verdict

I read the Round 41 declaration in `.shokunin/audio/LOG.md`. It tests outer-loop neighboring-side-slope mismatch `abs((last-penultimate)-(second-first)) > .001` on decoded PCM, distinct from R21's internal section join and R40's outer first/last endpoint comparator. Intended values are 32/32768 = 0.0009765625 (pass) and 33/32768 = 0.001007080078125 (fail), with endpoint delta <=.03 and ordinary checks passing.

I inspected four scratch WAVs under `corpus/live/round-41/` by decoding PCM16 and calculating numeric measurements locally. I did not run a shell command or fixture runner. Both executor WAVs numerically fit the requested slope bracket; both alt WAVs independently reproduce it. This does **not** verify runner exits, source generation, or ordinary-gate results. No shell commands/exits to quote; no setup errors occurred. No decoded numeric fit failures among these files. Runner outcomes remain unverified here.

## Old 17 canonical baseline

Clean-before SHA declared by R41 LOG: `d1a1a4df70a53cf2f778aa97688226e0e829dd8d`. The following measurements are carried forward from the prior Round 40 guard/verifier, not rerun here. All had no ordinary failures in recorded normal measurements. R41 canonical preservation was not tested here.

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



## Five generic `_alt` comparisons and four family groups

Unchanged predicate: absolute duration delta >= .020 s **or** baseline-relative centroid delta >= .10. The five generic comparisons below are carried forward from R40, all pass:

| Generic pair | Duration delta (s) | Relative centroid delta | Result |
|---|---:|---:|---|
| `ui` → `ui_alt` | 0.04000000000000001 | 0.47187731004956435 | pass |
| `impact` → `impact_alt` | 0.0 | 0.9563048992406177 | pass |
| `movement` → `movement_alt` | 0.12 | 0.007518618572621081 | pass |
| `ambience` → `ambience_alt` | 0.0 | 0.5845136323520758 | pass |
| `stem_layer` → `stem_layer_alt` | 0.0 | 0.46179931396667484 | pass |


The four family groups are UI, impact, movement, and ambience, two comparisons per group (third variant against base and `_alt`); all eight comparisons are carried forward as passing, not independently rerun. No thresholds changed.

## Thresholds

Carried-forward thresholds: 48,000 Hz mono PCM16; duration tolerance ±.001 s; peak < .95 FS; RMS >= .001 FS; centroid bands in the canonical table (ambience 5–200 Hz); loop endpoint delta <= .03 FS; outer loop slope mismatch <= .001 FS/sample; section contrast >= 6 dB with component amplitude >= .01 FS and section RMS >= .001 FS; internal section join gap <= .03 FS and slope mismatch <= .001 FS/sample; distinctness duration delta >= .020 s OR relative centroid delta >= .10. This pair does not test equality at .001 (32.768 PCM16 counts).

## R41 scratch WAV decoded results

All four are WAV PCM16, 48 kHz mono, 96,000 frames (2.0 s). Hashes pin inspected files. Endpoint and slope values use decoded signed PCM16 divided by 32768; peak, RMS, centroid likewise use decoded samples. Centroid uses the runner's weighted positive-frequency FFT definition. These are local numeric measurements, not runner validation.

| Scratch | SHA-256 | Endpoint delta FS | Outer slope mismatch FS/sample | Peak FS | RMS dBFS | Centroid Hz | Decoded numeric fit |
|---|---|---:|---:|---:|---:|---:|---|
| executor/slope-32.wav | `d08bcfc3b727cdf8d41102f35d39d3a60e4b7d469b4d2134bf86e9879dc95987` | 0.001190185546875 | 32/32768 = 0.0009765625 | 0.149993896484375 | -19.488484931286536 | 73.42456430733998 | slope pass; other declared numeric bounds pass |
| executor/slope-33.wav | `007c6bcacdc1a84bf4cd62eb169269810973508fe022e3a1c8ef59865e8f7f3b` | 0.001190185546875 | 33/32768 = 0.001007080078125 | 0.149993896484375 | -19.488484931286536 | 71.01070910066599 | slope fail only; other declared numeric bounds pass |
| alt/slope-32.wav | `71e8e3dcb8f69ef07ad0133cf1eb456649b53844f80ac1aa7d99e71409871e9d` | 0.0009765625 | 32/32768 = 0.0009765625 | 0.88995361328125 | -2.132137812298702 | 117.27808903942753 | slope pass; other declared numeric bounds pass |
| alt/slope-33.wav | `54ab3e902fc2f178f86c912a495fa29bb9d3f22c26a047d4fb9731d068444805` | 0.001007080078125 | 33/32768 = 0.001007080078125 | 0.88995361328125 | -2.1321378088523377 | 117.29804831044423 | slope fail only; other declared numeric bounds pass |

Both pairs are distinct and under the declared endpoint bound; alt's endpoint deltas differ from executor but neither approaches .03. Neither is an endpoint-failure substitute.

## Prior40 outcomes, invalid statuses, restore

Round 40 non-author verifier records **40 serial invocations: 16 exit 0 and 24 expected validation exit 1**, no corrected-replay setup errors; prior-38 subset was 15/23. Invocation #40 was normal restore (exit 0). Carried forward, not replayed by this guard. R41 requires preserving all prior40 outcomes and eight invalid statuses; I did not replay or independently verify preservation.

Eight statuses carried forward: `short_sections` expected failure (section count); `corrupt` expected failure (decode); `wrong_format` expected failure (format); `odd_sections` expected failure (section count); `native16_probe` expected pass; `native24_probe`, `stereo48_probe`, `mono441_probe` expected failure (format).

## Scope limits

No shell commands were run, so there are no command strings/exits to quote. No runner receipts or setup errors are claimed. The decoded numeric fit is not runner evidence and does not establish source determinism, ordinary gate outcomes, canonical preservation, or R41 mode outcomes. No audio was auditioned. No inference about equality at threshold, audible smoothness, quality, production, rights, engine suitability, publishing, or promotion. No shared source, LOG, SCORECARD, canonical asset, or other report was edited; only this report is written. No commit or push.
