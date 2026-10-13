# Round 46 non-author verifier — fresh 52-command replay

## Verdict

**The declared lower-band absolute UI centroid bracket reproduces on current source.** I executed all 52 runner commands serially, with a unique newly generated receipt for each: initial normal (#1), below and above probes (#2–#3), the prior R45 50-command sequence #2–#50 shifted to #4–#52 (including final normal restore). The total is **22 exit 0 / 30 expected fixture-validation exit 1**. The prior50 subset (#1 and #4–#52) is **21 exit 0 / 29 expected exit 1**. No historical or author receipt was reused. No setup failures occurred in this replay.

The below probe exited 1 for its **sole** `spectrum: centroid outside fixture band` failure; the above probe exited 0 with no failures. The probes retain the ordinary format/duration/level checks and unchanged `SPECS["ui"]` band. Evidence is a measurement-gate bracket, not causal isolation of a single physical variable.

## New probe evidence

| Probe | SHA-256 | Frames / format | Duration | Peak FS | RMS dBFS | Project SoX-f32 whole-wave centroid | Result |
|---|---|---|---:|---:|---:|---:|---|
| below | `fff9d981fe76c9163ba6a0db851e498b15fe193a1597427c8b73993b4666bfdf` | 5760; 48 kHz mono PCM16 | 0.12 s | 0.279754638671875 | -18.327838866709165 | 249.71389590882862 Hz | exit 1; sole spectrum failure |
| above | `6e453ff6cdf02e3fb72e0ebb0734f39a566a823841da8949187ad73d74a90a2a` | 5760; 48 kHz mono PCM16 | 0.12 s | 0.27984619140625 | -18.32783946042307 | 250.3250670185918 Hz | exit 0; no failures |

The nominal sinusoidal frequencies are 225/226 Hz; those are not the measured centroids. Both probes pass format, duration, peak (<.95), and RMS (>=.001) controls. Only below fails the ordinary 250–4000 Hz UI centroid band. Exact 250 Hz equality is untested.

The executor's first nominal 230/270 pair decoded to 253.80451803986455/293.3534382718592 Hz, both in band, and thus failed as a **numeric bracket fit**, not as a runner setup or gate result. The independent alternate initial decaying 180/300 and 60/300 pairs also decoded in-band and failed numeric fits; one relative-path helper error was a setup failure corrected for that alternate work. The final alternate pair was 200/300 nominal, decoded to 202.48468234677034/302.47893043755806 Hz, and produced the same polarity with a broader bracket; it is not the integrated executor pair. Reviewer draft's below peak transcription `.279754150390625` was corrected to `.279754638671875`; this was a report transcription correction, not a gate result.

## Source diff and preserved baselines

Clean-before is `803c5fbbc19576d980acc5578138522f91e644b0`. The source diff against it is limited to two opt-in modes in `corpus/fixtures/build_artifacts.py` and `measure_audio.py`; `SPECS["ui"]`, its ordinary comparator, and thresholds are unchanged. `git diff --check 803c5fb -- .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/corpus/fixtures/measure_audio.py` exited 0. `git diff --quiet 803c5fb -- .shokunin/audio/corpus/artifacts` exited 0. Fresh normal #1 and #52 receipts compare exactly equal JSON: the same 17 canonical measurements and no failures; no probe leaks into normal measurement.

Old canonical SHA/metrics are historical R45 verifier evidence, not separately recomputed as source hashes here. The fresh normal matches those metrics. Five generic `_alt` comparisons, four family groups/eight comparisons, thresholds/sections, and eight invalid-fixture outcomes are carried forward from the R45 verifier. The fresh prior50 subset reproduces its 21/29 expected count; details of the prior controls are in `reports/round-45/r45-verifier.md`.

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




## Serial command ledger

Every invocation below was actually run serially. Exact command, exit code, fresh unique receipt, and recorded runner failures are shown. Exit 1 rows are completed fixture validation failures, not runner setup failures.

| # | Exact command | Exit | New receipt | Recorded result |
|---:|---|---:|---|---|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T065600343881Z-normal/measurements.json` | none |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-absolute-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065601381736Z-ui-absolute-centroid-below/measurements.json` | ui_absolute_centroid_below_probe: ['spectrum: centroid outside fixture band'] |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-absolute-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T065602421400Z-ui-absolute-centroid-above/measurements.json` | none |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-tolerance-5713` | 0 | `.shokunin/audio/corpus/live/runs/20261013T065603464485Z-ui-lower-tolerance-5713/measurements.json` | none |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-tolerance-5711` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065604500333Z-ui-lower-tolerance-5711/measurements.json` | ui_lower_tolerance_5711_probe: ['duration: outside ±1 ms'] |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-tolerance-5807` | 0 | `.shokunin/audio/corpus/live/runs/20261013T065605552075Z-ui-tolerance-5807/measurements.json` | none |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-tolerance-5809` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065606600707Z-ui-tolerance-5809/measurements.json` | ui_tolerance_5809_probe: ['duration: outside ±1 ms'] |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-crest-46` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065607643619Z-ui-crest-46/measurements.json` | ui_crest_46_probe: ['level: clipping headroom or near silence'] |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-crest-47` | 0 | `.shokunin/audio/corpus/live/runs/20261013T065608693445Z-ui-crest-47/measurements.json` | none |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-peak-31129` | 0 | `.shokunin/audio/corpus/live/runs/20261013T065609740673Z-ui-peak-31129/measurements.json` | none |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-peak-31130` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065610805461Z-ui-peak-31130/measurements.json` | ui_peak_31130_probe: ['level: clipping headroom or near silence'] |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-32` | 0 | `.shokunin/audio/corpus/live/runs/20261013T065611873212Z-outer-slope-32/measurements.json` | none |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-33` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065612930248Z-outer-slope-33/measurements.json` | slope_33_probe: ['loop seam: slope mismatch > .001 full scale per sample'] |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-endpoint-983` | 0 | `.shokunin/audio/corpus/live/runs/20261013T065614046213Z-outer-endpoint-983/measurements.json` | none |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-endpoint-984` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065615098954Z-outer-endpoint-984/measurements.json` | endpoint_984_probe: ['loop seam: endpoint jump > .03 full scale'] |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-forward` | 0 | `.shokunin/audio/corpus/live/runs/20261013T065616235480Z-ambience-orientation-forward/measurements.json` | none |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065617362407Z-ambience-orientation-reverse/measurements.json` | ambience_orientation_alt: ['distinctness: duration < .020 s and centroid delta < 10%'] |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T065618483230Z-ambience-centroid-above/measurements.json` | none |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065619612893Z-ambience-centroid-below/measurements.json` | ambience_probe_alt: ['distinctness: duration < .020 s and centroid delta < 10%'] |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-mixed-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T065620701453Z-ui-mixed-pass/measurements.json` | none |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-joint-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065621790632Z-ui-joint-below/measurements.json` | ui_joint_below_alt: ['distinctness: duration < .020 s and centroid delta < 10%'] |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-forward` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065622896274Z-ui-orientation-forward/measurements.json` | ui_orientation_forward_alt: ['distinctness: duration < .020 s and centroid delta < 10%'] |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-reverse` | 0 | `.shokunin/audio/corpus/live/runs/20261013T065623984859Z-ui-orientation-reverse/measurements.json` | none |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065625075021Z-ui-lower-centroid-below/measurements.json` | ui_lower_centroid_below_alt: ['distinctness: duration < .020 s and centroid delta < 10%'] |
| 25 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T065626162782Z-ui-lower-centroid-above/measurements.json` | none |
| 26 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065627249827Z-ui-centroid-below/measurements.json` | ui_centroid_below_alt: ['distinctness: duration < .020 s and centroid delta < 10%'] |
| 27 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T065628331675Z-ui-centroid-above/measurements.json` | none |
| 28 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065629483110Z-ui-duration-below/measurements.json` | ui_duration_below_alt: ['distinctness: duration < .020 s and centroid delta < 10%'] |
| 29 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 | `.shokunin/audio/corpus/live/runs/20261013T065630582883Z-ui-duration-at/measurements.json` | none |
| 30 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065631675701Z-ui-clone/measurements.json` | ui_clone_alt: ['distinctness: duration < .020 s and centroid delta < 10%'] |
| 31 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T065632757898Z-layer-third-join-edge-pass/measurements.json` | none |
| 32 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065633841855Z-layer-third-join-edge-fail/measurements.json` | join200_edgefail_probe: ['sections: internal join adjacent sample gap > .03 full scale'] |
| 33 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065634939304Z-layer-third-join/measurements.json` | join200_probe: ['sections: internal join adjacent sample gap > .03 full scale'] |
| 34 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T065636019426Z-layer-third-slope-edge-pass/measurements.json` | none |
| 35 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065637083016Z-layer-third-slope-edge-fail/measurements.json` | edgefail_probe: ['sections: internal join side slope mismatch > .001 full scale per sample'] |
| 36 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065638201696Z-layer-third-slope/measurements.json` | slope200_probe: ['sections: internal join side slope mismatch > .001 full scale per sample'] |
| 37 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065639275534Z-layer-alt-reverse/measurements.json` | reverse180_probe: ['sections: 180 Hz component amplitude contrast < 6 dB or invalid'] |
| 38 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065640343448Z-layer-alt-slope/measurements.json` | slope180_probe: ['sections: internal join side slope mismatch > .001 full scale per sample'] |
| 39 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065641419164Z-layer-alt-join/measurements.json` | join180_probe: ['sections: internal join adjacent sample gap > .03 full scale'] |
| 40 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065642505603Z-layer-alt-flat/measurements.json` | flat180_probe: ['sections: 180 Hz component amplitude contrast < 6 dB or invalid'] |
| 41 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065643587258Z-layer-slope/measurements.json` | layer_slope_probe: ['sections: internal join side slope mismatch > .001 full scale per sample'] |
| 42 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065644657371Z-layer-join/measurements.json` | join_probe: ['sections: internal join adjacent sample gap > .03 full scale'] |
| 43 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065645747373Z-flat/measurements.json` | flat30_probe: ['sections: 30 Hz component amplitude contrast < 6 dB or invalid'] |
| 44 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065646839351Z-layer-flat/measurements.json` | flat120_probe: ['sections: 120 Hz component amplitude contrast < 6 dB or invalid'] |
| 45 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065647903285Z-slope/measurements.json` | slope_probe: ['loop seam: slope mismatch > .001 full scale per sample'] |
| 46 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065648907418Z-failing/measurements.json` | ambience: ['spectrum: centroid outside fixture band', 'loop seam: endpoint jump > .03 full scale'] |
| 47 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261013T065649253843Z-invalid/measurements.json` | short_sections: section count; corrupt: decode; wrong_format: format; odd_sections: section count; native16_probe: None; native24_probe: format; stereo48_probe: format; mono441_probe: format |
| 48 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T065650258332Z-normal/measurements.json` | none |
| 49 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T065651271766Z-normal/measurements.json` | none |
| 50 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T065652299123Z-normal/measurements.json` | none |
| 51 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T065653305884Z-normal/measurements.json` | none |
| 52 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T065654336632Z-normal/measurements.json` | none |

## Scope and limits

The evidence supports only this numerical fixture-gate bracket for the existing whole-wave magnitude-FFT centroid predicate. The waveforms differ; their nominal frequencies, quantized samples, and full FFT distributions differ, so this is **not causal single-variable isolation**. It makes no claim about exact 250 Hz equality, timbre, quality, perceptual behavior, universal calibration, production suitability, rights, engine behavior, publishing, ranking, or promotion. No source, LOG, SCORECARD, canonical artifact, other report, commit, or push was changed by this verifier. I wrote only this report; the runner generated fresh receipts under `corpus/live/runs/`.
