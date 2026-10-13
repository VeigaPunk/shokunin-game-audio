# Round 41 independent verifier — NON-AUTHOR

## Verdict and scope

**The declared local outer-loop side-slope bracket is independently reproduced.** I ran 42 runner invocations serially: initial normal (#1), new slope-32 and slope-33 probes (#2–#3), then the prior Round 40 sequence #2–#40 shifted to #4–#42. Total: **17 exit 0 and 25 expected fixture-validation exit 1; no setup errors in the 42 runner invocations.** The prior-40 subset (#1 and #4–#42) is **16 exit 0 / 24 expected exit 1**. #42 is the final normal restore. All eight invalid statuses and prior40 outcomes are preserved.

New modes exercise R3's outer neighboring side-slope comparison, distinct from R21's internal section join and R40's outer endpoint check. The source-generated probes are distinct SHA-pinned WAVs, each 2.0 s / 96,000 frames / 48 kHz mono PCM16. Both pass ordinary format, duration, level, centroid and endpoint checks. 32 exits 0 with no failures; 33 exits 1 with only the outer slope-mismatch failure. No threshold changed. This demonstrates only a fixture-local numerical bracket, not exact `.001` equality (32.768 PCM16 counts), audible smoothness, perceived quality, rights, engine behavior, publishing, or promotion.

## Independent probe evidence

I independently SHA-256 checked the generated WAVs and inspected their runner receipts. I decoded the boundary signed PCM16 counts as well. Samples below are first, second, penultimate, last:

| Mode | WAV SHA-256 | Decoded boundary counts | Outer slope mismatch | Endpoint delta | Centroid | Runner result |
|---|---|---|---:|---:|---:|---|
| 32 | `0bc9c6f07b53b13336b253db069cc57702e9520634106eabf85fc27e329b4547` | `0, 6, -77, -39` | 32/32768 = **0.0009765625** | 39/32768 = **0.001190185546875** | 150.16139474032187 Hz | exit 0; no failures |
| 33 | `b86a34d343a57e943ab4289cb67b992b8597d93002f3b4a7ef9981e6b30952fb` | `0, 5, -77, -39` | 33/32768 = **0.001007080078125** | 39/32768 = **0.001190185546875** | 152.54369633957694 Hz | exit 1; sole failure `loop seam: slope mismatch > .001 full scale per sample` |

The strict outer comparator remains `> .001` FS/sample; the independent endpoints are identical, safely within the unchanged `.03` endpoint limit. Both centroids are within the ambience 5–200 Hz band. The modes each measure 17 canonical assets plus their one scratch WAV.

## Serial replay ledger — exact commands, exits, receipts, failure kinds

Commands ran serially from the repository root. Every row has a runner-generated receipt under `corpus/live/runs/`. All exit-1 results are expected fixture-validation outcomes; none is a setup/invocation error. The prior40 mapping is prior #1 then prior #2–#40 shifted to #4–#42. #42 is final normal restore.

| # | Exact command | Exit | Receipt | Failure kind / invalid statuses |
|---:|---|---:|---|---|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T051644443308Z-normal/measurements.json` | none |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-32` | 0 | `.shokunin/audio/corpus/live/runs/20261013T051645488524Z-outer-slope-32/measurements.json` | none |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-33` | 1 | `.shokunin/audio/corpus/live/runs/20261013T051646547685Z-outer-slope-33/measurements.json` | slope_33_probe: loop seam: slope mismatch > .001 full scale per sample |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-endpoint-983` | 0 | `.shokunin/audio/corpus/live/runs/20261013T051647626709Z-outer-endpoint-983/measurements.json` | none |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-endpoint-984` | 1 | `.shokunin/audio/corpus/live/runs/20261013T051648678775Z-outer-endpoint-984/measurements.json` | endpoint_984_probe: loop seam: endpoint jump > .03 full scale |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-forward` | 0 | `.shokunin/audio/corpus/live/runs/20261013T051649799885Z-ambience-orientation-forward/measurements.json` | none |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T051650907616Z-ambience-orientation-reverse/measurements.json` | ambience_orientation_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T051651999247Z-ambience-centroid-above/measurements.json` | none |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T051653113355Z-ambience-centroid-below/measurements.json` | ambience_probe_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-mixed-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T051654187487Z-ui-mixed-pass/measurements.json` | none |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-joint-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T051655262123Z-ui-joint-below/measurements.json` | ui_joint_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-forward` | 1 | `.shokunin/audio/corpus/live/runs/20261013T051656348762Z-ui-orientation-forward/measurements.json` | ui_orientation_forward_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-reverse` | 0 | `.shokunin/audio/corpus/live/runs/20261013T051657427878Z-ui-orientation-reverse/measurements.json` | none |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T051658509975Z-ui-lower-centroid-below/measurements.json` | ui_lower_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T051659586758Z-ui-lower-centroid-above/measurements.json` | none |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T051700672408Z-ui-centroid-below/measurements.json` | ui_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T051701753140Z-ui-centroid-above/measurements.json` | none |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T051702844065Z-ui-duration-below/measurements.json` | ui_duration_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 | `.shokunin/audio/corpus/live/runs/20261013T051703929851Z-ui-duration-at/measurements.json` | none |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 | `.shokunin/audio/corpus/live/runs/20261013T051705015607Z-ui-clone/measurements.json` | ui_clone_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T051706080992Z-layer-third-join-edge-pass/measurements.json` | none |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T051707144450Z-layer-third-join-edge-fail/measurements.json` | join200_edgefail_probe: sections: internal join adjacent sample gap > .03 full scale |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T051708224304Z-layer-third-join/measurements.json` | join200_probe: sections: internal join adjacent sample gap > .03 full scale |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T051709288139Z-layer-third-slope-edge-pass/measurements.json` | none |
| 25 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T051710346036Z-layer-third-slope-edge-fail/measurements.json` | edgefail_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 26 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T051711416831Z-layer-third-slope/measurements.json` | slope200_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 27 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T051712474325Z-layer-alt-reverse/measurements.json` | reverse180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 28 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T051713534654Z-layer-alt-slope/measurements.json` | slope180_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 29 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T051714604083Z-layer-alt-join/measurements.json` | join180_probe: sections: internal join adjacent sample gap > .03 full scale |
| 30 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T051715677207Z-layer-alt-flat/measurements.json` | flat180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 31 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T051716748471Z-layer-slope/measurements.json` | layer_slope_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 32 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T051717825359Z-layer-join/measurements.json` | join_probe: sections: internal join adjacent sample gap > .03 full scale |
| 33 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T051718886840Z-flat/measurements.json` | flat30_probe: sections: 30 Hz component amplitude contrast < 6 dB or invalid |
| 34 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T051719962553Z-layer-flat/measurements.json` | flat120_probe: sections: 120 Hz component amplitude contrast < 6 dB or invalid |
| 35 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T051721024136Z-slope/measurements.json` | slope_probe: loop seam: slope mismatch > .001 full scale per sample |
| 36 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261013T051722029376Z-failing/measurements.json` | ambience: spectrum: centroid outside fixture band; loop seam: endpoint jump > .03 full scale |
| 37 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261013T051722377228Z-invalid/measurements.json` | invalid statuses: short_sections expected_failure (section count), corrupt expected_failure (decode), wrong_format expected_failure (format), odd_sections expected_failure (section count), native16_probe expected_pass, native24_probe expected_failure (format), stereo48_probe expected_failure (format), mono441_probe expected_failure (format) |
| 38 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T051723376508Z-normal/measurements.json` | none |
| 39 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T051724372540Z-normal/measurements.json` | none |
| 40 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T051725371094Z-normal/measurements.json` | none |
| 41 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T051726373257Z-normal/measurements.json` | none |
| 42 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T051727365311Z-normal/measurements.json` | none |

## Preservation and prior Round 40 context

- **Old 17 canonical WAVs:** all 17 artifact files are byte-identical to clean-before `d1a1a4df70a53cf2f778aa97688226e0e829dd8d` (`git diff --quiet d1a1a4df70a53cf2f778aa97688226e0e829dd8d -- .shokunin/audio/corpus/artifacts` exit 0). Their SHA-256 hashes and normal metrics follow, carried forward from the R40 verifier. Normal #1 and #42 receipts are equal in every receipt field apart from generated paths. Old source diff is limited to the R41 builder/runner additions for two opt-in slope probes; thresholds, existing modes and canonical generation sources were not altered.
- **Five generic `_alt` comparisons:** unchanged and carried forward passing: `ui→ui_alt`, `impact→impact_alt`, `movement→movement_alt`, `ambience→ambience_alt`, and `stem_layer→stem_layer_alt`. Four family groups (UI, impact, movement, ambience; two comparisons each) and their metrics/sections are unchanged. Thresholds remain the same.
- **Prior40 serial results:** the 40-run prior sequence is preserved as #1+#4–#42: **16 exit 0 / 24 expected validation exit 1**, including its #40 final-normal restore now #42. In this replay the R40 endpoint-983 and endpoint-984 probes now appear as #4/#5 with the same expected pass/sole endpoint failure respectively.
- Eight invalid statuses are preserved in #37: `short_sections` expected failure (section count); `corrupt` expected failure (decode; ffprobe exit 1); `wrong_format` expected failure (format); `odd_sections` expected failure (section count); `native16_probe` expected pass; `native24_probe`, `stereo48_probe`, and `mono441_probe` expected failure (format).
- **Setup vs measured misses:** R41 author integration initially used `t=n/RATE`; its actual runner invocation `--probe-outer-slope-32` exited 1 with receipt `corpus/live/runs/20261013T051350076413Z-outer-slope-32/measurements.json`, measured centroid 296.04646400437895 Hz outside 5–200 and slope mismatch .002166748046875. The exact command was `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-32`; it exited 1. This was a measured failed numeric fit, not setup failure, and is not the final fixture. Integration corrected to the exact `n/96000` recipe; the final hashes and this verifier's runner receipts show the intended bracket. The initial build command `python3 .shokunin/audio/corpus/fixtures/build_artifacts.py --probe-outer-slope-32` exited 0 while building both final WAVs. Earlier worker helper path/type errors and exploratory numeric fit misses reported in wave reports are not runner invocations and are not included in the 42 outcomes. No setup errors occurred during this verifier replay.

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



### Old 17 canonical SHA-256 and normal metrics (carried forward)

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





Worker-reported setup errors, kept separate from numeric outcomes: executor command `python3 -c 'import runpy,pathlib,json; m=runpy.run_path(".shokunin/audio/corpus/fixtures/measure_audio.py"); root=pathlib.Path(".shokunin/audio/corpus"); print(json.dumps({str(p):m["measure"](p.stem,(2.0,5,200,True),p) for p in sorted((root/"live/round-41/executor").glob("*.wav"))},indent=2))'` exited 1 because helper paths were relative/outside its absolute ROOT; no receipt. Alt's first direct helper call exited 1 (`AttributeError: 'str' object has no attribute 'relative_to'`); second relative-Path call exited 1 (`ValueError: ... is not in the subpath ...`). These are setup/path errors, not runner failures or numeric fits. Alt's corrected absolute-path helper invocation exited 0, but is helper evidence only. Earlier exploratory numeric recipe exited 0 while both centroids were about 2801.8 Hz, outside 5–200; it was a numeric failed fit, not setup. Transient executor candidate pair also failed numeric slope fit (helper decoded 0/1 counts); it was regenerated. These helper outcomes are excluded from replay counts.

## Scope limits

I wrote only this non-author report and generated runner receipts under `corpus/live/runs/`; I did not edit shared source, LOG, SCORECARD, canonical assets, or other reports, and made no commit or push. No audio was auditioned. No inference is made about equality at threshold, audible seam/smoothness, quality, production suitability, rights, engine behavior, publishing, or promotion.
