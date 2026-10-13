# Round 42 guard — preservation and decoded numeric-fit audit

## Scope and verdict

I read the Round 42 declaration in `.shokunin/audio/LOG.md`. It asks for a numerical fixture calibration of the existing strict peak comparator (`peak >= .95` fails), using deterministic UI-shaped 0.12 s / 5,760-frame / 48 kHz mono PCM16 candidates at 31,129/32,768 = **0.949981689453125** (pass) and 31,130/32,768 = **0.95001220703125** (fail). The candidates must also meet ordinary numeric checks; this report makes no inference beyond fixture measurements. No production threshold is changed.

I inspected the executor pair and independent alt pair in `corpus/live/round-42/`, calculating their decoded PCM16 values and checking each with the repository measurement helper. All four satisfy the intended adjacent-count numerical fit: 31,129 has no ordinary failures and 31,130 fails solely with `level: clipping headroom or near silence`. This is numeric helper evidence, not runner-mode receipts; no runner command was run here. No shell commands/exits or setup errors to report. No numeric failed fits among these four candidates.

## Old 17 canonical baseline

Clean-before SHA declared in the Round 42 LOG: `3b4f10b8951b59dbbdb8ff82ca57bd3e890468ed`. The following old-17 SHA/metrics are carried forward from R41 guard/verifier, **not rerun in this guard**. R42 canonical preservation is unverified here.

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

Unchanged generic predicate: absolute duration delta >= .020 s **or** baseline-relative centroid delta >= .10. Five comparisons (carried forward; all pass):

| Generic pair | Duration delta (s) | Relative centroid delta | Result |
|---|---:|---:|---|
| `ui` → `ui_alt` | 0.04000000000000001 | 0.47187731004956435 | pass |
| `impact` → `impact_alt` | 0.0 | 0.9563048992406177 | pass |
| `movement` → `movement_alt` | 0.12 | 0.007518618572621081 | pass |
| `ambience` → `ambience_alt` | 0.0 | 0.5845136323520758 | pass |
| `stem_layer` → `stem_layer_alt` | 0.0 | 0.46179931396667484 | pass |


The four family groups are UI, impact, movement, and ambience, two comparisons per group (third variant against base and `_alt`); all eight comparisons are carried forward as passing, not independently rerun. No thresholds changed.

## Thresholds

Carried-forward thresholds: 48,000 Hz mono PCM16; duration tolerance ±.001 s; peak < .95 FS (the tested comparator is `peak >= .95`); RMS >= .001 FS; canonical centroid bands (UI 250–4000 Hz); loop endpoint delta <= .03 FS; outer loop slope mismatch <= .001 FS/sample; section contrast >= 6 dB with component amplitude >= .01 FS and section RMS >= .001 FS; internal section join gap <= .03 FS and slope mismatch <= .001 FS/sample; distinctness duration delta >= .020 s OR relative centroid delta >= .10. `.95*32768=31129.6`, so adjacent counts 31,129 and 31,130 straddle .95; they do not test exact equality at .95.

## Decoded Round 42 scratch candidates

The four inspected WAVs each have 5,760 frames, 48 kHz, mono, PCM16 and duration .12 s. Hashes are distinct. The repository helper computes the gate's weighted positive-frequency FFT centroid. RMS is reported in dBFS; both candidates in each pair exceed the RMS floor. These are local numeric helper results, not runner invocations or independent non-author receipts.

| Candidate | SHA-256 | Peak signed count / FS | RMS dBFS | Centroid Hz | Helper failures / numeric result |
|---|---|---:|---:|---:|---|
| executor `ui-peak-31129.wav` | `7e6c11325d27c1e0d2acaa11975fae1180a8186d2449816fa38f2eabbab93e14` | 31129 / 0.949981689453125 | -3.4559832611867107 | 1002.249073839976 | none; intended pass fit |
| executor `ui-peak-31130.wav` | `8e7cf36d2a78ee78446b12076361d69284928019ae2bc0072bd63a1fe3c57b3d` | 31130 / 0.95001220703125 | -3.455749141202171 | 1000.248226139511 | sole `level: clipping headroom or near silence`; intended fail fit |
| alt `peak-31129.wav` | `d56bb13fbc1894a11e2807c18d52c25d7877fc9d194f29747b90e5659d509130` | 31129 / 0.949981689453125 | -11.939951937178082 | 966.6827446669814 | none; intended pass fit |
| alt `peak-31130.wav` | `eb2e49dd60fd83484958dcb3ee85ea611fe88fbaf70323cfc427b8a21f106119` | 31130 / 0.95001220703125 | -11.939672328927625 | 966.6760815177989 | sole `level: clipping headroom or near silence`; intended fail fit |

Both independent pairs are hash-distinct. The pass and fail candidates within each pair differ by one decoded PCM16 peak count and both have centroid in 250–4000 Hz, RMS above .001 FS and the expected format/duration. Peak comparator remains unchanged.

## Prior42 replay, invalid statuses, restore

Round 41's named non-author verifier records **42 serial invocations: 17 exit 0 / 25 expected fixture-validation exit 1**, with no replay setup errors; its prior40 subset was 16/24 and invocation #42 was normal restore. This is carried-forward evidence only; Round 42's required 44-run replay, preservation check, eight invalid statuses, and final normal restore were not run or independently verified by this guard. The eight carried-forward statuses are `short_sections` expected failure (section count), `corrupt` expected failure (decode), `wrong_format` expected failure (format), `odd_sections` expected failure (section count), `native16_probe` expected pass, and `native24_probe`, `stereo48_probe`, `mono441_probe` expected failure (format).

## Commands, exits, and setup-versus-fit distinction

No shell command or fixture runner was run; therefore there are no command strings/exits to quote and no setup errors. The helper inspection completed successfully in the Python REPL; it is not represented as a shell exit or runner receipt. The four inspected fixtures have no numeric fit failures. No audition was performed.

## Scope limits

This is fixture-local numerical calibration only. The integer points do not test equality at exactly .95, audible clipping, perceived headroom quality, production, rights, engine suitability, publishing, or promotion. I wrote only `.shokunin/audio/reports/round-42/r42-guard.md`; no shared source, LOG, SCORECARD, canonical asset, or other report was edited, and no commit or push was made.
