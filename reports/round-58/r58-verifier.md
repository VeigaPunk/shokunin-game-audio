# R58 non-author verifier — 76-command serial replay

## Verdict and scope

**PASS for the specified constructed pair and integrated runner probes.** Both new R58 valid-bit probe modes exited 0 with empty measurement failure lists. I serially executed all 76 commands below; the split is **38 exit 0 / 38 expected validation exit 1**. The prior R57 74-command subset (new #1 and #4–#76) is **36 exit 0 / 38 exit 1**. Every command produced a distinct fresh receipt; all receipt JSON was independently parsed. For the 74 mapped prior commands, command text, process exit, and the complete parsed JSON object (including mode and all failure mappings) match the corresponding R57 receipt exactly. Initial and final normal JSON also match.

This shows only what this specified pair produced through this project/host path. It is not general valid-bit metadata enforcement, precision/fidelity, decoder conformance, audibility, quality, production, rights, engine, or promotion evidence. No general valid-bit enforcement was added; existing format predicate, UI spec, thresholds, and canonical artifacts remain unchanged. I made no source edits, commits, or pushes. I wrote only this verifier report; runner receipts and corpus pair are runner/generated outputs.

## Integrated source diff against clean-before

Compared to clean-before `0e7a31f7645a8d4c8094612047a6f89d74d69bdb`, the integrated fixture builder adds the deterministic pair and two explicit opt-in flags; the runner adds the two probe modes and corresponding measurements. Pair construction is 5,760 mono/48 kHz signed-16 samples (`rint((.25*sin(2π·1000t)+.08*sin(2π·1500t))*8191)*4`). In both WAV headers the `fmt` chunk is 40 bytes, tag `0xfffe`, `cbSize=22`, channel mask `0x4`, PCM subtype GUID `0100000000001000800000aa00389b71`, and container width 16; only `wValidBitsPerSample` differs (14 versus 16). The unchanged format check does not inspect valid-bits metadata. Existing `SPECS["ui"]`, thresholds, canonical17, and other probe semantics are unchanged.

## Pair/header and independent decode

The fresh integrated pair under `corpus/live/round-58/` matches the specified hashes. Both payloads are 11,520 bytes (5,760 samples), SHA-256 `0b40e3c0f28aa6a50937f87c0fa260b2100f97572dbc8fdf517cea981e79b4fc`; all signed values are divisible by four. Payload bytes are identical; only the valid-bits header field differs.

| File | WAV SHA-256 | Valid bits | Header summary |
|---|---|---:|---|
| `pair_valid_14.wav` | `6b4b07d1eee022f99116a043b444821914acc68110544a644ba7204f3a63fb26` | 14 | tag `0xfffe`, fmt40, cb22, mask `0x4`, PCM subtype, 16-bit container |
| `pair_valid_16.wav` | `738263969d226d31a0525bbad1c7dda8609b270dd3ec8fa82645905d4667a7f2` | 16 | same; valid-bits byte is the sole difference |

Independent ffprobe on both exited 0 and reported `pcm_s16le` / `s16`, 16 bits/sample, mono, 48,000 Hz, `0.120000` s. Independent SoX float32 decoding exited 0 for both; vectors each contain 5,760 samples and compare exactly equal. This is strictly the observed result for this pair/decoder path. Runner probes #2 and #3 both exit 0; each supplemental measurement has 5,760 samples, duration 0.12 s, peak `0.3153076171875`, RMS `-14.629479252569332 dBFS`, centroid `1129.9910331085607 Hz`, bandwidth `412.58546294347246 Hz`, and `failures: []`. These values fit the existing UI gates; no numeric failed fit or decoder rejection occurred.

## R57 exact replay and baseline battery

I mapped prior R57 #1 to fresh #1 and prior R57 #2–#74 to fresh #4–#76. Every mapped command, exit code, and entire parsed JSON object equals its R57 counterpart. The 74 paths here are new and distinct from each other and from the historical R57 receipt paths. The two new probes (#2/#3) each have a new receipt and clean supplemental measurement. All paths and exact commands are in the ledger.

Canonical17 artifact SHA-256 and core measurements were recomputed from `corpus/artifacts/` and match the previous verifier and normal receipt. Generic distinctness still has five `_alt` comparisons. Each UI, impact, movement, and ambience family map has two comparisons (baseline and `_alt`); section output covers `stem_sections`, `stem_layer`, `stem_layer_alt`, and `stem_layer_third`. The eight invalid-probe statuses and observed failure classes match the prior baseline exactly: short_sections expected section-count failure; corrupt expected decode failure; wrong_format expected format failure; odd_sections expected section-count failure; native16 expected pass; native24 expected format failure; stereo48 expected format failure; mono441 expected format failure.

Unchanged thresholds: rate 48,000 Hz; duration tolerance 0.001 s; peak <0.95; RMS >0.001; loop endpoint delta ≤0.03; loop slope ≤0.001 full-scale/sample; section contrast ≥6 dB; internal-join adjacent delta ≤0.03; internal-join side slope mismatch ≤0.001 full-scale/sample.

Canonical17 SHA and metrics (equal to prior R57):

| Fixture | SHA-256 | Duration s | Peak FS | RMS dBFS | Centroid Hz |
|---|---|---:|---:|---:|---:|
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` | 0.12 | 0.375946044921875 | -19.991687666366516 | 966.8966593379727 |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` | 0.16 | 0.31878662109375 | -20.525534144496497 | 1423.1532540422852 |
| `ui_third.wav` | `734a0a47077f5b614b5d51d486b88a51940c7d61ecea0878642b60a0103513bc` | 0.2 | 0.375946044921875 | -22.20695387316763 | 966.7216217320357 |
| `impact.wav` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` | 0.32 | 0.80877685546875 | -20.40218668053459 | 10843.127202979935 |
| `impact_alt.wav` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` | 0.32 | 0.75616455078125 | -17.32957040921516 | 473.79153568100764 |
| `impact_third.wav` | `d14376241f409f07edde30fbcef86b5f060ff36f731b7578fd9934d1dc1b39bf` | 0.4 | 0.45611572265625 | -20.84958464133168 | 6838.143302962279 |
| `movement.wav` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` | 0.24 | 0.53948974609375 | -23.779940832329185 | 11934.484045946316 |
| `movement_alt.wav` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` | 0.36 | 0.639312744140625 | -21.987315616484317 | 12024.214879348818 |
| `movement_third.wav` | `0e5f815e1987e13646170571e1f1e977b25e3566d90ebcca558c72ed07851d44` | 0.3 | 0.489501953125 | -14.025186267550422 | 4553.583280111138 |
| `ambience.wav` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` | 2.0 | 0.174591064453125 | -18.153351293681563 | 36.61640767851373 |
| `ambience_alt.wav` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` | 2.0 | 0.199737548828125 | -17.67032381358842 | 58.01919713436623 |
| `ambience_third.wav` | `c2c8e0bb2385bc93b39c70b719d0f56553c771969986ef1f732d24af5677d404` | 2.0 | 0.225006103515625 | -16.92261930553234 | 112.03210352691181 |
| `stem.wav` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` | 2.0 | 0.32379150390625 | -14.881434973008286 | 272.6756827789141 |
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` | 4.0 | 0.17236328125 | -23.066521225821248 | 201.87069023000652 |
| `stem_layer.wav` | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` | 4.0 | 0.05999755859375 | -30.28756654598196 | 190.1433267529918 |
| `stem_layer_alt.wav` | `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` | 4.0 | 0.04998779296875 | -31.667277345674258 | 277.9513846028647 |
| `stem_layer_third.wav` | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` | 4.0 | 0.04998779296875 | -31.66724765274306 | 287.93805923844434 |

## Exact 76-command ledger

Commands were run serially, in this order. `none` means no measurement failures. For #71 the listed eight classifications are the invalid-probe receipt's expected outcomes and observed classes.

| # | Exact command | Exit | Fresh receipt path | Failure(s) / expected classifications |
|---:|---|---:|---|---|
| 01 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125321021838Z-normal/measurements.json` | none |
| 02 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-14-r58` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125322047317Z-ui-extensible-valid-14-r58/measurements.json` | none |
| 03 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-16-r58` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125323076433Z-ui-extensible-valid-16-r58/measurements.json` | none |
| 04 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-15` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125324116798Z-ui-extensible-valid-15/measurements.json` | none |
| 05 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-16` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125325154972Z-ui-extensible-valid-16/measurements.json` | none |
| 06 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-mask-zero` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125326192451Z-ui-extensible-mask-zero/measurements.json` | none |
| 07 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-mask-center` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125327237771Z-ui-extensible-mask-center/measurements.json` | none |
| 08 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-pcm16` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125328280778Z-ui-extensible-pcm16/measurements.json` | none |
| 09 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-standard-pcm16-r55` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125329313053Z-ui-standard-pcm16-r55/measurements.json` | none |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm32` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125330361182Z-ui-pcm32/measurements.json` | ui_depth_pcm32_r54_probe: format: expected PCM16 |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16-r54` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125331410861Z-ui-pcm16-r54/measurements.json` | none |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-float32` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125332440888Z-ui-float32/measurements.json` | ui_depth_float32_r53_probe: format: expected PCM16 |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16-r53` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125333477959Z-ui-pcm16-r53/measurements.json` | none |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm8` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125334515247Z-ui-pcm8/measurements.json` | ui_depth_pcm8_r52_probe: format: expected PCM16 |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16-r52` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125335539886Z-ui-pcm16-r52/measurements.json` | none |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm24` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125336566997Z-ui-pcm24/measurements.json` | ui_depth_pcm24_probe: format: expected PCM16 |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125337585020Z-ui-pcm16/measurements.json` | none |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-channel-stereo` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125338619806Z-ui-channel-stereo/measurements.json` | ui_channel_stereo_probe: format: expected 48kHz mono |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-channel-mono` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125339652868Z-ui-channel-mono/measurements.json` | none |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-48001` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125340682546Z-ui-rate-48001/measurements.json` | ui_rate_r49_48001_probe: format: expected 48kHz mono |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-48000-r49` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125341720942Z-ui-rate-48000-r49/measurements.json` | none |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-47999` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125342767886Z-ui-rate-47999/measurements.json` | ui_rate_47999_probe: format: expected 48kHz mono |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-48000` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125343801497Z-ui-rate-48000/measurements.json` | none |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-upper-centroid-below` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125344832452Z-ui-upper-centroid-below/measurements.json` | none |
| 25 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-upper-centroid-above` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125345857802Z-ui-upper-centroid-above/measurements.json` | ui_upper_centroid_above_probe: spectrum: centroid outside fixture band |
| 26 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-absolute-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125346885082Z-ui-absolute-centroid-below/measurements.json` | ui_absolute_centroid_below_probe: spectrum: centroid outside fixture band |
| 27 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-absolute-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125347912333Z-ui-absolute-centroid-above/measurements.json` | none |
| 28 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-tolerance-5713` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125348952013Z-ui-lower-tolerance-5713/measurements.json` | none |
| 29 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-tolerance-5711` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125349994210Z-ui-lower-tolerance-5711/measurements.json` | ui_lower_tolerance_5711_probe: duration: outside ±1 ms |
| 30 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-tolerance-5807` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125351032904Z-ui-tolerance-5807/measurements.json` | none |
| 31 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-tolerance-5809` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125352085541Z-ui-tolerance-5809/measurements.json` | ui_tolerance_5809_probe: duration: outside ±1 ms |
| 32 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-crest-46` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125353122850Z-ui-crest-46/measurements.json` | ui_crest_46_probe: level: clipping headroom or near silence |
| 33 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-crest-47` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125354157394Z-ui-crest-47/measurements.json` | none |
| 34 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-peak-31129` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125355197912Z-ui-peak-31129/measurements.json` | none |
| 35 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-peak-31130` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125356238090Z-ui-peak-31130/measurements.json` | ui_peak_31130_probe: level: clipping headroom or near silence |
| 36 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-32` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125357280306Z-outer-slope-32/measurements.json` | none |
| 37 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-33` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125358335433Z-outer-slope-33/measurements.json` | slope_33_probe: loop seam: slope mismatch > .001 full scale per sample |
| 38 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-endpoint-983` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125359397544Z-outer-endpoint-983/measurements.json` | none |
| 39 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-endpoint-984` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125400460375Z-outer-endpoint-984/measurements.json` | endpoint_984_probe: loop seam: endpoint jump > .03 full scale |
| 40 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-forward` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125401569923Z-ambience-orientation-forward/measurements.json` | none |
| 41 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125402662705Z-ambience-orientation-reverse/measurements.json` | ambience_orientation_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 42 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125403760485Z-ambience-centroid-above/measurements.json` | none |
| 43 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125404873742Z-ambience-centroid-below/measurements.json` | ambience_probe_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 44 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-mixed-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125405979781Z-ui-mixed-pass/measurements.json` | none |
| 45 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-joint-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125407083812Z-ui-joint-below/measurements.json` | ui_joint_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 46 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-forward` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125408194644Z-ui-orientation-forward/measurements.json` | ui_orientation_forward_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 47 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-reverse` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125409302754Z-ui-orientation-reverse/measurements.json` | none |
| 48 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125410411367Z-ui-lower-centroid-below/measurements.json` | ui_lower_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 49 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125411522514Z-ui-lower-centroid-above/measurements.json` | none |
| 50 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125412598598Z-ui-centroid-below/measurements.json` | ui_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 51 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125413680706Z-ui-centroid-above/measurements.json` | none |
| 52 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125414760295Z-ui-duration-below/measurements.json` | ui_duration_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 53 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125415838349Z-ui-duration-at/measurements.json` | none |
| 54 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125416913175Z-ui-clone/measurements.json` | ui_clone_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 55 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125417981299Z-layer-third-join-edge-pass/measurements.json` | none |
| 56 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125419042553Z-layer-third-join-edge-fail/measurements.json` | join200_edgefail_probe: sections: internal join adjacent sample gap > .03 full scale |
| 57 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125420109117Z-layer-third-join/measurements.json` | join200_probe: sections: internal join adjacent sample gap > .03 full scale |
| 58 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125421164979Z-layer-third-slope-edge-pass/measurements.json` | none |
| 59 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125422214278Z-layer-third-slope-edge-fail/measurements.json` | edgefail_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 60 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125423289468Z-layer-third-slope/measurements.json` | slope200_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 61 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125424352008Z-layer-alt-reverse/measurements.json` | reverse180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 62 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125425405731Z-layer-alt-slope/measurements.json` | slope180_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 63 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125426479894Z-layer-alt-join/measurements.json` | join180_probe: sections: internal join adjacent sample gap > .03 full scale |
| 64 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125427538773Z-layer-alt-flat/measurements.json` | flat180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 65 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125428595276Z-layer-slope/measurements.json` | layer_slope_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 66 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125429652488Z-layer-join/measurements.json` | join_probe: sections: internal join adjacent sample gap > .03 full scale |
| 67 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125430724914Z-flat/measurements.json` | flat30_probe: sections: 30 Hz component amplitude contrast < 6 dB or invalid |
| 68 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125431789642Z-layer-flat/measurements.json` | flat120_probe: sections: 120 Hz component amplitude contrast < 6 dB or invalid |
| 69 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125432858391Z-slope/measurements.json` | slope_probe: loop seam: slope mismatch > .001 full scale per sample |
| 70 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125433862079Z-failing/measurements.json` | ambience: spectrum: centroid outside fixture band; loop seam: endpoint jump > .03 full scale |
| 71 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261013T125434206724Z-invalid/measurements.json` | invalid: short_sections=expected_failure(section count), corrupt=expected_failure(decode), wrong_format=expected_failure(format), odd_sections=expected_failure(section count), native16_probe=expected_pass(None), native24_probe=expected_failure(format), stereo48_probe=expected_failure(format), mono441_probe=expected_failure(format) |
| 72 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125435204704Z-normal/measurements.json` | none |
| 73 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125436197107Z-normal/measurements.json` | none |
| 74 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125437202552Z-normal/measurements.json` | none |
| 75 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125438191312Z-normal/measurements.json` | none |
| 76 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T125439182373Z-normal/measurements.json` | none |

## Setup/decode boundary

There was no receiptless/setup error in this verifier run: all 76 runner invocations yielded fresh receipt JSON. The pre-existing R57 verifier documents its earlier setup error separately from its measured replay; that old event is not a R58 command or a decode/gate failure. The selected R58 probes produced receipts and passed their numeric fit. A successful decode here does not establish generalized valid-bits semantics or arbitrary-header/decoder behavior.
