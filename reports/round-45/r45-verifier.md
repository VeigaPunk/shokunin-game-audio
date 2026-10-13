# Round 45 non-author verifier — fresh 50-command replay

## Verdict

**The negative-side ordinary UI duration calibration reproduces on current source.** I executed all 50 runner commands serially: initial normal (#1), new `--probe-ui-lower-tolerance-5713` (#2) and `--probe-ui-lower-tolerance-5711` (#3), then the complete R44 48-command sequence #2–#48 shifted to #4–#50, including final normal restore. Result: **21 exit 0 / 29 expected fixture-validation exit 1**. The prior48 subset (#1 and #4–#50) is **20 exit 0 / 28 expected exit 1**. All 50 receipt paths below are unique, newly generated during this replay; no historical or author receipt was reused. No replay setup failures occurred.

## Negative-side probe evidence

The two original executor WAVs were measured by their new integrated runner modes. Their hashes match the source scratch WAVs, and the receipts report the unchanged ordinary `SPECS["ui"]` check:

| Probe | SHA-256 | Frames / format | ffprobe duration | Parsed signed delta from .12 s | Absolute delta | Peak FS | RMS dBFS | Centroid Hz | Result |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| 5713 | `94f1ad9459fbfc06120668e3ebe5743a2d8690c66238d586f05006102811dd99` | 5713; 48 kHz mono PCM16 | 0.119021 s | -0.0009789999999999938 s | 0.0009789999999999938 s | 0.27947998046875 | -16.399347369151716 | 1663.1001045998237 | exit 0; no failures |
| 5711 | `2b4b0323f040a65b431a984e4fde5866f5c412754206c928e1fa21358adb9ab8` | 5711; 48 kHz mono PCM16 | 0.118979 s | -0.0010209999999999941 s | 0.0010209999999999941 s | 0.27947998046875 | -16.3992750775437 | 1627.5978467387597 | exit 1; sole `duration: outside ±1 ms` |

The values are computed from actual ffprobe decimal durations parsed as Python floats. Both signals pass the unchanged format, peak (<.95), RMS (>=.001 FS), and UI centroid (250–4000 Hz) checks. The failing probe is a completed numeric fixture validation, not a setup/decode/format error. This establishes only that these two measured fixtures fall on opposite sides of the existing negative-side tolerance; it does not test the 5712-frame point or assert exact ±.001 equality. The disposable critic 5712 case probed `.119000`; Python's strict-float comparison yields `abs(.119 - .12) > .001`, so that case fails—not an equality pass, and not integrated.

## Source diff and preserved baselines

Clean-before: `4de93bf829f539d77c0ebc4706dfe95903ab2f17`. Against it, the source diff is limited to the declared opt-in pair in `corpus/fixtures/build_artifacts.py` and `measure_audio.py` (28 insertions, 5 deletions). The ordinary comparator and thresholds are unchanged. `git diff --check 4de93bf -- .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/corpus/fixtures/measure_audio.py` exited 0. `git diff --quiet 4de93bf -- .shokunin/audio/corpus/artifacts` exited 0: canonical artifact bytes are unchanged. Fresh normal receipts #1 and #50 are exactly equal as JSON: the same 17 canonical measurements, no failures; neither probe leaks into the normal run.

The old 17 canonical SHA/measurement values below are historical R44 verifier evidence, not separately rerun here; they match the fresh normal receipt and remain unchanged. R44’s fresh verifier report is `reports/round-44/r44-verifier.md`.

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




## Preserved broader checks (carried forward)

The prior48 subset in this run reproduces the historical R44 count of **20 exit 0 / 28 expected exit 1**. R44’s five generic `_alt` comparisons, four family groups/eight comparisons, thresholds, and artifact/invalid-fixture checks are carried forward, not independently re-scored as extra gates here. See the R44 verifier for their measurements and distinctions. In this fresh prior sequence, #45 `--probe-invalid` completed expected fixture validation (not setup failure): short_sections—section count; corrupt—decode; wrong_format—format; odd_sections—section count; native16_probe—pass; native24_probe, stereo48_probe, mono441_probe—format. All exit-1 invocations are expected fixture-validation cases; no runner invocation failed to set up.

## Serial command ledger

Exact command, exit code, new receipt path, and result for every invocation (paths repo-relative). `none` means the receipt recorded no measurement failures.

| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T063747667567Z-normal/measurements.json` | none |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-tolerance-5713` | 0 | `.shokunin/audio/corpus/live/runs/20261013T063748725989Z-ui-lower-tolerance-5713/measurements.json` | none |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-tolerance-5711` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063749795923Z-ui-lower-tolerance-5711/measurements.json` | ui_lower_tolerance_5711_probe: ['duration: outside ±1 ms'] |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-tolerance-5807` | 0 | `.shokunin/audio/corpus/live/runs/20261013T063751067705Z-ui-tolerance-5807/measurements.json` | none |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-tolerance-5809` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063752145782Z-ui-tolerance-5809/measurements.json` | ui_tolerance_5809_probe: ['duration: outside ±1 ms'] |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-crest-46` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063753204246Z-ui-crest-46/measurements.json` | ui_crest_46_probe: ['level: clipping headroom or near silence'] |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-crest-47` | 0 | `.shokunin/audio/corpus/live/runs/20261013T063754272778Z-ui-crest-47/measurements.json` | none |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-peak-31129` | 0 | `.shokunin/audio/corpus/live/runs/20261013T063755346964Z-ui-peak-31129/measurements.json` | none |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-peak-31130` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063756396534Z-ui-peak-31130/measurements.json` | ui_peak_31130_probe: ['level: clipping headroom or near silence'] |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-32` | 0 | `.shokunin/audio/corpus/live/runs/20261013T063757476122Z-outer-slope-32/measurements.json` | none |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-33` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063758571643Z-outer-slope-33/measurements.json` | slope_33_probe: ['loop seam: slope mismatch > .001 full scale per sample'] |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-endpoint-983` | 0 | `.shokunin/audio/corpus/live/runs/20261013T063759648539Z-outer-endpoint-983/measurements.json` | none |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-endpoint-984` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063800709854Z-outer-endpoint-984/measurements.json` | endpoint_984_probe: ['loop seam: endpoint jump > .03 full scale'] |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-forward` | 0 | `.shokunin/audio/corpus/live/runs/20261013T063801841617Z-ambience-orientation-forward/measurements.json` | none |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063803027414Z-ambience-orientation-reverse/measurements.json` | ambience_orientation_alt: ['distinctness: duration < .020 s and centroid delta < 10%'] |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T063804162624Z-ambience-centroid-above/measurements.json` | none |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063805296434Z-ambience-centroid-below/measurements.json` | ambience_probe_alt: ['distinctness: duration < .020 s and centroid delta < 10%'] |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-mixed-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T063806387401Z-ui-mixed-pass/measurements.json` | none |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-joint-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063807494479Z-ui-joint-below/measurements.json` | ui_joint_below_alt: ['distinctness: duration < .020 s and centroid delta < 10%'] |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-forward` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063808599340Z-ui-orientation-forward/measurements.json` | ui_orientation_forward_alt: ['distinctness: duration < .020 s and centroid delta < 10%'] |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-reverse` | 0 | `.shokunin/audio/corpus/live/runs/20261013T063809722212Z-ui-orientation-reverse/measurements.json` | none |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063810832406Z-ui-lower-centroid-below/measurements.json` | ui_lower_centroid_below_alt: ['distinctness: duration < .020 s and centroid delta < 10%'] |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T063811935077Z-ui-lower-centroid-above/measurements.json` | none |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063813028762Z-ui-centroid-below/measurements.json` | ui_centroid_below_alt: ['distinctness: duration < .020 s and centroid delta < 10%'] |
| 25 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T063814137293Z-ui-centroid-above/measurements.json` | none |
| 26 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063815245761Z-ui-duration-below/measurements.json` | ui_duration_below_alt: ['distinctness: duration < .020 s and centroid delta < 10%'] |
| 27 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 | `.shokunin/audio/corpus/live/runs/20261013T063816346742Z-ui-duration-at/measurements.json` | none |
| 28 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063817477077Z-ui-clone/measurements.json` | ui_clone_alt: ['distinctness: duration < .020 s and centroid delta < 10%'] |
| 29 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T063818564631Z-layer-third-join-edge-pass/measurements.json` | none |
| 30 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063819661993Z-layer-third-join-edge-fail/measurements.json` | join200_edgefail_probe: ['sections: internal join adjacent sample gap > .03 full scale'] |
| 31 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063820769974Z-layer-third-join/measurements.json` | join200_probe: ['sections: internal join adjacent sample gap > .03 full scale'] |
| 32 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T063821857695Z-layer-third-slope-edge-pass/measurements.json` | none |
| 33 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063822958619Z-layer-third-slope-edge-fail/measurements.json` | edgefail_probe: ['sections: internal join side slope mismatch > .001 full scale per sample'] |
| 34 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063824053109Z-layer-third-slope/measurements.json` | slope200_probe: ['sections: internal join side slope mismatch > .001 full scale per sample'] |
| 35 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063825135822Z-layer-alt-reverse/measurements.json` | reverse180_probe: ['sections: 180 Hz component amplitude contrast < 6 dB or invalid'] |
| 36 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063826211291Z-layer-alt-slope/measurements.json` | slope180_probe: ['sections: internal join side slope mismatch > .001 full scale per sample'] |
| 37 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063827312049Z-layer-alt-join/measurements.json` | join180_probe: ['sections: internal join adjacent sample gap > .03 full scale'] |
| 38 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063828399867Z-layer-alt-flat/measurements.json` | flat180_probe: ['sections: 180 Hz component amplitude contrast < 6 dB or invalid'] |
| 39 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063829474267Z-layer-slope/measurements.json` | layer_slope_probe: ['sections: internal join side slope mismatch > .001 full scale per sample'] |
| 40 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063830557145Z-layer-join/measurements.json` | join_probe: ['sections: internal join adjacent sample gap > .03 full scale'] |
| 41 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063831639388Z-flat/measurements.json` | flat30_probe: ['sections: 30 Hz component amplitude contrast < 6 dB or invalid'] |
| 42 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063832722730Z-layer-flat/measurements.json` | flat120_probe: ['sections: 120 Hz component amplitude contrast < 6 dB or invalid'] |
| 43 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063833784802Z-slope/measurements.json` | slope_probe: ['loop seam: slope mismatch > .001 full scale per sample'] |
| 44 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063834813944Z-failing/measurements.json` | ambience: ['spectrum: centroid outside fixture band', 'loop seam: endpoint jump > .03 full scale'] |
| 45 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261013T063835161115Z-invalid/measurements.json` | invalid fixtures: short_sections(section count), corrupt(decode), wrong_format(format), odd_sections(section count), native16_probe(pass), native24_probe(format), stereo48_probe(format), mono441_probe(format) |
| 46 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T063836197943Z-normal/measurements.json` | none |
| 47 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T063837219807Z-normal/measurements.json` | none |
| 48 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T063838241241Z-normal/measurements.json` | none |
| 49 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T063839257554Z-normal/measurements.json` | none |
| 50 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T063840271762Z-normal/measurements.json` | none |

## Scope and limits

This report verifies numerical fixture calibration only. The executor’s first report draft transcribed R44 positive-side magnitudes into four negative-side delta cells; parent corrected those four report cells from the actual ffprobe values before integration and noted the correction. It was a report transcription error, not a numeric fit or setup failure. Alt’s initial helper relative-path mistake was a separate setup issue; its corrected helper run succeeded. The new serial replay itself had no setup errors.

No audition or inference about audible/perceptual duration, quality, production suitability, rights, engine behavior, publishing, ranking, or promotion is made. No exact-boundary claim is made. I edited only this verifier report; the 50 fresh receipts were generated by the runner.
