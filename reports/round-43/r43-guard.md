# Round 43 guard — RMS-branch numeric fixture audit

## Scope and finding

I read the Round 43 declaration in `.shokunin/audio/LOG.md`: preserve existing combined level predicate `peak >= .95 or rms < .001`; isolate its RMS branch with deterministic 0.12 s / 5,760-frame / 48 kHz mono PCM16 UI-shaped fixtures, decoded crest counts 46 and 47, with decoded peak below .95 and centroid inside 250–4000 Hz. Required outcome: count 46 fails solely the combined level check because RMS < .001; count 47 passes with RMS > .001. No threshold change.

The executor scratch fixtures in `corpus/live/round-43/executor/` numerically meet those requirements under the project `measure_audio.measure()` helper. Both have decoded peaks far below .95; their RMS values straddle .001 FS, and their centroids are in-band. The 46-count candidate has only `level: clipping headroom or near silence`; the 47-count candidate has no helper failures. This is numerical fixture calibration only, not an audition or quality assessment.

## Candidate decoded measurements

| Crest count | SHA-256 | Frames / format | Decoded peak FS | RMS FS | RMS dBFS | Centroid Hz | Helper outcome |
|---:|---|---|---:|---:|---:|---:|---|
| 46 | `869d1e5ada618a3c9daaa7be3100c9a01dc1342df63d732355a23a306130adfc` | 5760; 48 kHz mono PCM16 | 0.00140380859375 (46/32768) | 0.0009918604133909925 | -60.07098885448798 | 1333.1671762128672 | sole `level: clipping headroom or near silence` |
| 47 | `4c8c67a08558f14ad0642cac99563056407eeeecdc6b05e974f7b24cf74804b3` | 5760; 48 kHz mono PCM16 | 0.001434326171875 (47/32768) | 0.0010130695326051166 | -59.88721491134572 | 2221.180142174043 | none |

These are adjacent **crest counts**, not a claim of adjacent RMS values. The helper's weighted centroid puts both measurements in the declared UI band. Count 46 is below `.001 FS` and count 47 above it; neither is an exact equality case. Both peak values are well below `.95`, so the numeric measurements isolate the RMS side of the combined predicate. No threshold was altered.

## Old 17 canonical baseline

Round 43 clean-before SHA in LOG: `fc638d9d133c7dc2e4d77d44036181d52675eb00`. Old-17 SHA/metrics below are carried forward from Round 42's non-author verifier, not rerun by this guard. Round 43 canonical preservation and normal-run restoration are not verified by this guard; they remain for the declared non-author replay.

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

Carried forward from Round 42 verifier; not independently rerun here. Generic predicate is duration delta >= .020 s OR baseline-relative centroid delta >= .10; all five pass. The four family groups are UI, impact, movement, and ambience, each with the third variant compared to base and `_alt` (eight comparisons total); all carried-forward comparisons passed.

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

Carried forward unchanged; no threshold adjustment in this guard:

Carried-forward thresholds: 48,000 Hz mono PCM16; duration tolerance ±.001 s; peak < .95 FS (the tested comparator is `peak >= .95`); RMS >= .001 FS; canonical centroid bands (UI 250–4000 Hz); loop endpoint delta <= .03 FS; outer loop slope mismatch <= .001 FS/sample; section contrast >= 6 dB with component amplitude >= .01 FS and section RMS >= .001 FS; internal section join gap <= .03 FS and slope mismatch <= .001 FS/sample; distinctness duration delta >= .020 s OR relative centroid delta >= .10. `.95*32768=31129.6`, so adjacent counts 31,129 and 31,130 straddle .95; they do not test exact equality at .95.

## Prior 44-run baseline and invalid statuses

Round 42's named non-author verifier reports 44 fresh serial invocations: 18 exit 0 / 26 expected fixture-validation exit 1. Its prior42 subset was 17/25; final normal restore was invocation #44. These are carried-forward prior-round figures, not Round 43 replay evidence. Eight invalid-mode statuses from its `--probe-invalid` invocation: `short_sections` expected failure (section count), `corrupt` expected failure (decode), `wrong_format` expected failure (format), `odd_sections` expected failure (section count), `native16_probe` expected pass, and `native24_probe`, `stereo48_probe`, `mono441_probe` expected failure (format). Round 43 declaration calls for a fresh 46-run non-author replay; this guard did not run that replay.

## Commands, exits, and error classification

I ran no shell command, no fixture runner invocation, and no fit-search command. Thus there are no shell command exit codes or runner receipts to report from this guard. I decoded both WAVs and called the project `measure_audio.measure()` helper directly in the Python REPL; its results are tabulated above. No candidate-generation/measurement setup error occurred here, and no numeric fit failed: the two target crests were directly generated and both satisfy their intended respective pass/fail outcomes. The executor report separately records its initial relative-path helper invocation exiting 1 with `ValueError` from `Path.relative_to(ROOT)`; this is a path setup error, not a numeric failed fit or candidate failure. No numeric fit search was attempted. Prior replay's expected fixture-validation exit-1 cases are not setup errors.

## Limits

Numerical fixture calibration only. No exact `.001` equality, perceptual/audible silence boundary, audio quality, production, rights, engine, publishing, or promotion inference. No audition was performed. No shared source, LOG, SCORECARD, canonical asset, or other report was edited; no commit or push was made.
