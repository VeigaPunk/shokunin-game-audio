# Round 44 non-author verifier — fresh duration-tolerance replay

## Verdict

**The declared ordinary UI duration-tolerance calibration pair is reproduced on current source.** I executed all 48 runner commands serially: initial normal (#1), new `--probe-ui-tolerance-5807` (#2), new `--probe-ui-tolerance-5809` (#3), then the complete prior R43 46-command sequence shifted to #4–#48, including its final normal restore. Result: **20 exit 0 / 28 expected fixture-validation exit 1**. The prior46 subset (#1 and #4–#48) is **19 exit 0 / 27 expected exit 1**. All 48 receipt paths below are distinct and newly generated in this replay; none is an author or historical receipt. No runner setup errors occurred.

## New duration probe evidence

Selected executor WAVs were already integrated into current source's opt-in modes. Their SHA-256s match both the declared source-pinned pair and the runner-generated WAVs:

| Probe | SHA-256 | Frames / format | ffprobe duration | Parsed delta from .12 s | Peak FS | RMS dBFS | Centroid Hz | Runner result |
|---|---|---|---:|---:|---:|---:|---:|---|
| 5807 | `17890e483de91075569283a2bcfbada6a6402e1cd87ab52da53bdfbc605cf934` | 5807; 48 kHz mono PCM16 | 0.120979 s | 0.0009790000000000076 s | 0.27947998046875 | -16.431537076901346 | 1132.7351495568296 | exit 0; no failures |
| 5809 | `c0552b983ecd9230b16d6ac3441eb8be7b43e80130bbd413fb62272752d7d510` | 5809; 48 kHz mono PCM16 | 0.121021 s | 0.001021000000000008 s | 0.27947998046875 | -16.432818198672756 | 936.6642301482127 | exit 1; sole `duration: outside ±1 ms` |

Both peaks are below .95, RMS exceeds .001 FS, and centroids are within the UI 250–4000 Hz band; the measured failure is isolated to duration. Ideal frame arithmetic is +47/48000 = 0.0009791666666666666 s and +49/48000 = 0.0010208333333333334 s. The measured ffprobe-decimal durations parsed as floats govern the actual comparisons. Critic's disposable 5808-frame check reports `.121000`, with parsed delta `0.0010000000000000009`; it **fails** the strict `> .001` predicate in this path. This is not an equality pass, and 5808 was not integrated or part of this replay. No claim about exact mathematical equality is made.

## Source comparison, preserved state, and carried-forward checks

Clean-before is `8009269ade6fff69c95de3cbde6a2cd653c33dc9`. The source diff against clean-before is limited to the declared opt-in tolerance probe builder/mode wiring in `corpus/fixtures/build_artifacts.py` and `measure_audio.py` (28 insertions, 5 deletions); the unchanged duration predicate and thresholds are not modified. `git diff --check` for those source files exits 0. `git diff --quiet 8009269ade6fff69c95de3cbde6a2cd653c33dc9 -- .shokunin/audio/corpus/artifacts` exits 0: canonical artifact bytes remain unchanged. Fresh normal receipts #1 and #48 are exactly equal as JSON. They contain the same 17 canonical measurements, failures empty; the probes do not leak into the final normal run.

## Old 17 canonical baseline

Clean-before for this round: `8009269ade6fff69c95de3cbde6a2cd653c33dc9`. The old-17 SHA/normal metrics below are carried forward from the R43 verifier and match this replay's normal receipt. I checked canonical artifact preservation against clean-before with `git diff --quiet 8009269ade6fff69c95de3cbde6a2cd653c33dc9 -- .shokunin/audio/corpus/artifacts` (exit 0); all canonical artifact bytes match clean-before.

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



## Historical calibration context and preserved expectations

The R43 non-author report is `reports/round-43/r43-verifier.md`; its receipts are historical and were not reused here. Its 46-command prior subset was 19 exit0 / 27 expected exit1; this replay's embedded prior46 subset (#1 + #4–#48) is 19/27. The old 17 canonical SHA/normal metrics and canonical bytes remain unchanged. Five generic `_alt` comparisons and four family groups (eight comparisons) remain passing; their numbers and the old-17 table are carried forward from R43 verifier, not newly recalculated as a separate gate. Thresholds remain unchanged: 48 kHz mono PCM16; duration tolerance ±.001s; peak <.95; RMS >=.001; UI centroid 250–4000 Hz; endpoint delta <=.03; outer seam slope <=.001 FS/sample; section contrast >=6 dB, component amplitude >=.01 FS and section RMS >=.001; internal join delta <=.03 and slope <=.001; distinctness duration delta >=.020s OR relative centroid delta >=.10.

The eight invalid statuses were observed anew at #43: `short_sections` expected section-count failure; `corrupt` expected decode failure; `wrong_format` expected format failure; `odd_sections` expected section-count failure; `native16_probe` expected pass; and `native24_probe`, `stereo48_probe`, `mono441_probe` expected format failures. Their exit 1 is an expected fixture validation result, not setup failure.

## Serial command ledger

Exact command, exit code, **new** receipt path and observed failure for every serial run (paths are repo-relative):

| # | Exact command | Exit | NEW receipt | Failure kind / invalid statuses |
|---:|---|---:|---|---|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T060507805101Z-normal/measurements.json` | none |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-tolerance-5807` | 0 | `.shokunin/audio/corpus/live/runs/20261013T060508841398Z-ui-tolerance-5807/measurements.json` | none |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-tolerance-5809` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060509860666Z-ui-tolerance-5809/measurements.json` | sole `duration: outside ±1 ms` failure |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-crest-46` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060510899278Z-ui-crest-46/measurements.json` | sole RMS-side `level: clipping headroom or near silence` failure |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-crest-47` | 0 | `.shokunin/audio/corpus/live/runs/20261013T060511913846Z-ui-crest-47/measurements.json` | none |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-peak-31129` | 0 | `.shokunin/audio/corpus/live/runs/20261013T060512937620Z-ui-peak-31129/measurements.json` | none |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-peak-31130` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060513964508Z-ui-peak-31130/measurements.json` | ui_peak_31130_probe: level: clipping headroom or near silence |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-32` | 0 | `.shokunin/audio/corpus/live/runs/20261013T060514998559Z-outer-slope-32/measurements.json` | none |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-33` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060516022901Z-outer-slope-33/measurements.json` | slope_33_probe: loop seam: slope mismatch > .001 full scale per sample |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-endpoint-983` | 0 | `.shokunin/audio/corpus/live/runs/20261013T060517078580Z-outer-endpoint-983/measurements.json` | none |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-endpoint-984` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060518112786Z-outer-endpoint-984/measurements.json` | endpoint_984_probe: loop seam: endpoint jump > .03 full scale |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-forward` | 0 | `.shokunin/audio/corpus/live/runs/20261013T060519204847Z-ambience-orientation-forward/measurements.json` | none |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060520307392Z-ambience-orientation-reverse/measurements.json` | ambience_orientation_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T060521402102Z-ambience-centroid-above/measurements.json` | none |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060522488667Z-ambience-centroid-below/measurements.json` | ambience_probe_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-mixed-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T060523544174Z-ui-mixed-pass/measurements.json` | none |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-joint-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060524605399Z-ui-joint-below/measurements.json` | ui_joint_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-forward` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060525659052Z-ui-orientation-forward/measurements.json` | ui_orientation_forward_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-reverse` | 0 | `.shokunin/audio/corpus/live/runs/20261013T060526726395Z-ui-orientation-reverse/measurements.json` | none |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060527778447Z-ui-lower-centroid-below/measurements.json` | ui_lower_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T060528855326Z-ui-lower-centroid-above/measurements.json` | none |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060529919416Z-ui-centroid-below/measurements.json` | ui_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T060530973171Z-ui-centroid-above/measurements.json` | none |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060532033011Z-ui-duration-below/measurements.json` | ui_duration_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 25 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 | `.shokunin/audio/corpus/live/runs/20261013T060533102306Z-ui-duration-at/measurements.json` | none |
| 26 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060534160100Z-ui-clone/measurements.json` | ui_clone_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 27 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T060535220684Z-layer-third-join-edge-pass/measurements.json` | none |
| 28 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060536275974Z-layer-third-join-edge-fail/measurements.json` | join200_edgefail_probe: sections: internal join adjacent sample gap > .03 full scale |
| 29 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060537336551Z-layer-third-join/measurements.json` | join200_probe: sections: internal join adjacent sample gap > .03 full scale |
| 30 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T060538395700Z-layer-third-slope-edge-pass/measurements.json` | none |
| 31 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060539462763Z-layer-third-slope-edge-fail/measurements.json` | edgefail_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 32 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060540518914Z-layer-third-slope/measurements.json` | slope200_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 33 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060541588927Z-layer-alt-reverse/measurements.json` | reverse180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 34 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060542639117Z-layer-alt-slope/measurements.json` | slope180_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 35 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060543694989Z-layer-alt-join/measurements.json` | join180_probe: sections: internal join adjacent sample gap > .03 full scale |
| 36 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060544754942Z-layer-alt-flat/measurements.json` | flat180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 37 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060545804943Z-layer-slope/measurements.json` | layer_slope_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 38 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060546865033Z-layer-join/measurements.json` | join_probe: sections: internal join adjacent sample gap > .03 full scale |
| 39 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060547938189Z-flat/measurements.json` | flat30_probe: sections: 30 Hz component amplitude contrast < 6 dB or invalid |
| 40 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060549001515Z-layer-flat/measurements.json` | flat120_probe: sections: 120 Hz component amplitude contrast < 6 dB or invalid |
| 41 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060550054659Z-slope/measurements.json` | slope_probe: loop seam: slope mismatch > .001 full scale per sample |
| 42 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060551049905Z-failing/measurements.json` | ambience: spectrum: centroid outside fixture band, loop seam: endpoint jump > .03 full scale |
| 43 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261013T060551390085Z-invalid/measurements.json` | short_sections: section count; corrupt: decode; wrong_format: format; odd_sections: section count; native16_probe: expected pass; native24_probe: format; stereo48_probe: format; mono441_probe: format |
| 44 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T060552393111Z-normal/measurements.json` | none |
| 45 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T060553381334Z-normal/measurements.json` | none |
| 46 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T060554399209Z-normal/measurements.json` | none |
| 47 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T060555387902Z-normal/measurements.json` | none |
| 48 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T060556451471Z-normal/measurements.json` | none |

## Setup-error classification and limits

There were no setup errors in the 48-run replay and no failed numeric fits beyond expected fixture validation outcomes. Earlier wave1 scout had one malformed ffprobe invocation (exit 127); that shell/setup error is not a gate failure. Earlier alt/guard helper attempts failed because of relative-path handling; those are setup/path errors separate from their corrected numeric measurements. Neither error affected this replay or its candidate receipts. Critic's 5808 disposable probe is not a runner receipt or integrated mode.

This is limited to a numeric fixture calibration of the ordinary duration check. It does not establish perceptual duration or audio quality, production suitability, rights, engine behavior, publishing, or promotion. No audition was performed. No shared source, LOG, SCORECARD, canonical artifacts, or other reports were edited by this verifier; only this verifier report and runner-generated `corpus/live/runs/` receipts were written. No commit or push was made.
