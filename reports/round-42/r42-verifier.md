# Round 42 independent verifier — NON-AUTHOR

## Verdict and scope

**The declared decoded-PCM16 peak bracket is independently reproduced by the project runner.** I ran 44 runner invocations serially: initial normal (#1), new `--probe-ui-peak-31129` / `--probe-ui-peak-31130` (#2–#3), then the same 42-command R41 sequence freshly replayed at #4–#44. Total: **18 exit 0 and 26 expected fixture-validation exit 1**; no setup errors among the 44 invocations. The prior42 subset (#1 and #4–#44) is **17 exit 0 / 25 expected exit 1**. #44 is final normal restore. The eight invalid statuses and prior42 outcomes are retained below.

The two distinct source-generated UI probes are 0.12 s / 5,760-frame / 48 kHz mono PCM16. The runner receipt and decoded WAV inspection show absolute peak counts 31,129 and 31,130, with normalized peaks 0.949981689453125 and 0.95001220703125. The 31,129 probe exits 0 with no failures; the 31,130 probe exits 1 with the sole combined level failure. Both RMS values are far above `.001` and centroid values lie within the UI 250–4000 Hz band. This is a fixture-local adjacent integer bracket, not exact equality at `.95`.

## Independent peak evidence

| Probe | WAV SHA-256 | Decoded abs peak | RMS dBFS | Centroid Hz | runner result |
|---|---|---:|---:|---:|---|
| 31129 | `7e6c11325d27c1e0d2acaa11975fae1180a8186d2449816fa38f2eabbab93e14` | 31129/32768 = 0.949981689453125 | -3.4559832611867107 | 1002.249073839976 | exit 0; no failures |
| 31130 | `8e7cf36d2a78ee78446b12076361d69284928019ae2bc0072bd63a1fe3c57b3d` | 31130/32768 = 0.95001220703125 | -3.455749141202171 | 1000.2482261395106 | exit 1; sole `level: clipping headroom or near silence` |

Both are 5,760 frames, .12 s, 48 kHz, mono PCM16. The failure text alone does not identify whether peak or RMS caused the combined predicate. RMS numeric measurements isolate the peak condition: both are vastly above the `.001` RMS floor (respectively -3.46 and -3.46 dBFS), while decoded peaks straddle `.95`; thus the observed 31130 failure is attributable to peak, not near-silence RMS. Existing condition remains `peak >= .95 or rms < .001`; no threshold changed. Since `.95 * 32768 = 31129.6`, neither integer is equality at `.95`.

## Source and clean-before comparison

Clean-before is `3b4f10b8951b59dbbdb8ff82ca57bd3e890468ed`. The source diff versus that revision is limited to the two R42 opt-in peak modes and generator/dispatch wiring in `corpus/fixtures/build_artifacts.py` and `corpus/fixtures/measure_audio.py`; it leaves the combined level predicate, canonical source/checker logic, and other thresholds unchanged. The generated probes live under `corpus/live/round-42/`, not canonical assets.

The old 17 canonical WAV SHA-256 values and normal metrics below are carried forward from R41 verifier/guard; R42 replay receipts continue to contain the old 17 normal measurements, and initial/final normal receipts match exactly in all receipt fields (the per-run receipt paths are external to JSON). The original clean-before comparison at R41 used `d1a1a4df70a53cf2f778aa97688226e0e829dd8d`; R42 declaration names `3b4f10b8951b59dbbdb8ff82ca57bd3e890468ed` as its clean-before. Canonical bytes are preserved across R42 replay.

## Old 17 canonical baseline

Clean-before SHA declared in the Round 42 LOG: `3b4f10b8951b59dbbdb8ff82ca57bd3e890468ed`. The old-17 SHA/normal metrics below are carried forward from the R41 verifier/guard. I independently checked R42 canonical preservation with `git diff --quiet 3b4f10b8951b59dbbdb8ff82ca57bd3e890468ed -- .shokunin/audio/corpus/artifacts` (exit 0); all canonical artifact bytes match clean-before.

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



## Prior42 replay context and invalid statuses

Prior42 results in the serial ledger are the R41 verifier's prior sequence: invocation #1 is the initial normal; its #2–#42 become R42 #4–#44. This subset totals 17 exit 0 / 25 expected fixture-validation exit 1; final normal restore is #44. Those R41 receipt paths are historical references only, not evidence for this replay. The 44 receipt paths in the following table are all newly generated by this verifier on 2026-10-13 (prefix `20261013T0533`–`0534`). Eight invalid-mode statuses are preserved in R42 #39 (`--probe-invalid`): `short_sections` expected failure (section count), `corrupt` expected failure (decode), `wrong_format` expected failure (format), `odd_sections` expected failure (section count), `native16_probe` expected pass, and `native24_probe`, `stereo48_probe`, `mono441_probe` expected failure (format). Prior mode failures and receipt paths are listed command by command in the ledger.

The wave1 executor and independent alt pairs both fit their numeric helper targets; no numeric failed fit among final executor/alt peak pairs or final runner probes. Setup errors reported in wave1 are not runner outcomes: critic's initial helper relative-path error; alt's initial Python orchestration `TypeError` (`await` misuse); and this verifier's initial attempt to await the synchronous `BashResult` returned after replay command #1 (the runner itself had already completed exit 0 and its receipt is #1). These are setup/orchestration errors, not measured failures; the corrected helper calls succeeded and replay continued serially through #44. No replay runner command had a setup error. No numeric failed fit occurred in the final peak probes.

## Serial replay ledger — exact commands, exits, runner receipts, failure kinds

Every row below is an actual project runner invocation with a runner-generated receipt under `.shokunin/audio/corpus/live/runs/`. Exit 1s are expected fixture-validation outcomes, not helper inferences. Prior42 sequence is mapped as specified above.

| # | Exact command | Exit | Receipt | Failure kind / invalid statuses |
|---:|---|---:|---|---|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T053345353881Z-normal/measurements.json` | none |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-peak-31129` | 0 | `.shokunin/audio/corpus/live/runs/20261013T053355532533Z-ui-peak-31129/measurements.json` | none |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-peak-31130` | 1 | `.shokunin/audio/corpus/live/runs/20261013T053356576190Z-ui-peak-31130/measurements.json` | ui_peak_31130_probe: level: clipping headroom or near silence |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-32` | 0 | `.shokunin/audio/corpus/live/runs/20261013T053357628896Z-outer-slope-32/measurements.json` | none |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-33` | 1 | `.shokunin/audio/corpus/live/runs/20261013T053358697988Z-outer-slope-33/measurements.json` | slope_33_probe: loop seam: slope mismatch > .001 full scale per sample |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-endpoint-983` | 0 | `.shokunin/audio/corpus/live/runs/20261013T053359741589Z-outer-endpoint-983/measurements.json` | none |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-endpoint-984` | 1 | `.shokunin/audio/corpus/live/runs/20261013T053400901670Z-outer-endpoint-984/measurements.json` | endpoint_984_probe: loop seam: endpoint jump > .03 full scale |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-forward` | 0 | `.shokunin/audio/corpus/live/runs/20261013T053402023381Z-ambience-orientation-forward/measurements.json` | none |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T053403140989Z-ambience-orientation-reverse/measurements.json` | ambience_orientation_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T053404267596Z-ambience-centroid-above/measurements.json` | none |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T053405383288Z-ambience-centroid-below/measurements.json` | ambience_probe_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-mixed-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T053406505637Z-ui-mixed-pass/measurements.json` | none |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-joint-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T053407590535Z-ui-joint-below/measurements.json` | ui_joint_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-forward` | 1 | `.shokunin/audio/corpus/live/runs/20261013T053408670349Z-ui-orientation-forward/measurements.json` | ui_orientation_forward_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-reverse` | 0 | `.shokunin/audio/corpus/live/runs/20261013T053409766140Z-ui-orientation-reverse/measurements.json` | none |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T053410871449Z-ui-lower-centroid-below/measurements.json` | ui_lower_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T053411972104Z-ui-lower-centroid-above/measurements.json` | none |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T053413068638Z-ui-centroid-below/measurements.json` | ui_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T053414171627Z-ui-centroid-above/measurements.json` | none |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T053415344331Z-ui-duration-below/measurements.json` | ui_duration_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 | `.shokunin/audio/corpus/live/runs/20261013T053416448372Z-ui-duration-at/measurements.json` | none |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 | `.shokunin/audio/corpus/live/runs/20261013T053417550233Z-ui-clone/measurements.json` | ui_clone_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T053418670129Z-layer-third-join-edge-pass/measurements.json` | none |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T053419734389Z-layer-third-join-edge-fail/measurements.json` | join200_edgefail_probe: sections: internal join adjacent sample gap > .03 full scale |
| 25 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T053420820997Z-layer-third-join/measurements.json` | join200_probe: sections: internal join adjacent sample gap > .03 full scale |
| 26 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T053421888333Z-layer-third-slope-edge-pass/measurements.json` | none |
| 27 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T053423028491Z-layer-third-slope-edge-fail/measurements.json` | edgefail_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 28 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T053424108897Z-layer-third-slope/measurements.json` | slope200_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 29 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T053425194347Z-layer-alt-reverse/measurements.json` | reverse180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 30 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T053426277744Z-layer-alt-slope/measurements.json` | slope180_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 31 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T053427353083Z-layer-alt-join/measurements.json` | join180_probe: sections: internal join adjacent sample gap > .03 full scale |
| 32 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T053428435684Z-layer-alt-flat/measurements.json` | flat180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 33 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T053429515794Z-layer-slope/measurements.json` | layer_slope_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 34 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T053430599876Z-layer-join/measurements.json` | join_probe: sections: internal join adjacent sample gap > .03 full scale |
| 35 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T053431737909Z-flat/measurements.json` | flat30_probe: sections: 30 Hz component amplitude contrast < 6 dB or invalid |
| 36 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T053432850218Z-layer-flat/measurements.json` | flat120_probe: sections: 120 Hz component amplitude contrast < 6 dB or invalid |
| 37 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T053433889965Z-slope/measurements.json` | slope_probe: loop seam: slope mismatch > .001 full scale per sample |
| 38 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261013T053434888840Z-failing/measurements.json` | ambience: spectrum: centroid outside fixture band; ambience: loop seam: endpoint jump > .03 full scale |
| 39 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261013T053435226435Z-invalid/measurements.json` | invalid statuses: short_sections expected_failure (section count), corrupt expected_failure (decode), wrong_format expected_failure (format), odd_sections expected_failure (section count), native16_probe expected_pass, native24_probe expected_failure (format), stereo48_probe expected_failure (format), mono441_probe expected_failure (format) |
| 40 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T053436278475Z-normal/measurements.json` | none |
| 41 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T053437297991Z-normal/measurements.json` | none |
| 42 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T053438304597Z-normal/measurements.json` | none |
| 43 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T053439311297Z-normal/measurements.json` | none |
| 44 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T053440324793Z-normal/measurements.json` | none |

## Scope limits

Numerical fixture calibration only. No claim of exact `.95` equality, audible clipping or sound quality, production suitability, rights, engine behavior, publishing, or promotion. No audition was performed. I wrote only this report and runner-generated receipts under `corpus/live/runs/`; no shared source, LOG, SCORECARD, canonical asset, or other report was edited, and no commit or push was made.
