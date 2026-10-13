# R56 non-author verifier — 72-command serial replay

## Verdict and scope

**PASS for the bounded R56 pair:** both mask probes executed successfully with clean measurements under the integrated runner. This is one constructed valid-16-bit, mono, WAVE_FORMAT_EXTENSIBLE PCM-subtype pair differing only in channel mask (`0x0` vs `0x4`). It does not establish support for other masks/layouts, universal WAVE_FORMAT_EXTENSIBLE conformance, general codec support, fidelity, audibility, quality, production suitability, rights, engine behavior, or promotion.

I executed the Python runner serially 72 times. #1 was normal; #2 `--probe-ui-extensible-mask-zero`; #3 `--probe-ui-extensible-mask-center`; #4–#72 are the R55 verifier's prior 70-command sequence #2–#70 shifted by two. Results: **34 exit 0 / 38 expected validation exit 1**. The prior-70 subset (#1 and #4–#72) is **32 exit 0 / 38 exit 1**. All 72 commands generated a receipt, and all paths are new and unique. I independently parsed each receipt JSON and checked mode, exit outcome, and failure classification. The prior subset's complete raw JSON objects match the corresponding R55 verifier receipts exactly.

Both new probes (#2/#3) exit 0 with no failures. No receiptless runner command or numeric fit failure occurred. One malformed shell-quoting invocation before the replay returned command-not-found and generated no receipt; it is a setup-only attempt, excluded from the 72-command ledger. The successful serial replay used the exact `python3 .../measure_audio.py` command.

## Integrated source diff against clean-before

Compared integrated source with clean-before `b4249b3c2037ad3e438e52d4abb0e5cd45a7c511`. `build_artifacts.py` adds deterministic 5,760-frame mono48k signed PCM16 data in two tag-`0xfffe`, fmt-size-40 WAVs, `cbSize=22`, valid bits 16, PCM subtype GUID `00000001-0000-0010-8000-00aa00389b71`, with mask 0 or front-center `0x4`; the audio payload is identical. `measure_audio.py` adds two opt-in runner modes and supplemental measurements. Existing `format_failures`, `SPECS["ui"]`, thresholds, and canonical 17 remain unchanged; the supplemental probes do not replace or join the canonical set.

## Pair artifacts and independent decode checks

| WAV | SHA-256 | Header fields | ffprobe | SoX-f32 decode |
|---|---|---|---|---|
| `pair_mask_zero.wav` | `3399ae3661b0ebd6eb4fe7c3a7cf6f4f97cd2d5ec259638164d93c810952a193` | RIFF/WAVE, fmt40, tag `0xfffe`, cbSize22, valid16, mono mask `0x0`, PCM GUID `00000001-0000-0010-8000-00aa00389b71` | `pcm_s16le`, s16/16, mono, 48000 Hz, .120000 s | 5,760 f32 samples; SHA-256 `d80f13858e4fdcf641f2164b440a99a42711fd4213239ad809c8136ee4620ce7` |
| `pair_mask_center.wav` | `bd7d95901935c0effe21fd64e44a47487372be9d0c80f86cc725380df0352f47` | RIFF/WAVE, fmt40, tag `0xfffe`, cbSize22, valid16, mono mask `0x4`, same PCM GUID | `pcm_s16le`, s16/16, mono, 48000 Hz, .120000 s | 5,760 f32 samples; same SHA-256; byte-identical to mask-zero decode |

For both runner measurements, duration `.12 s`, peak `0.31536865234375`, RMS `-14.628519169868087 dBFS`, centroid `1123.322704293326 Hz`, bandwidth `276.15444981222976 Hz`, and no failures. `ffprobe` and SoX decode commands exited 0 for both WAVs. Equality is direct for these generated files, not an arbitrary header or decoder claim.

## Prior R55 70-command replay cross-check

Mapped prior R55 command #1 to fresh #1, and prior #2–#70 to fresh #4–#72. For all 70, the complete freshly parsed JSON object equals its R55 receipt JSON, including mode, thresholds, measurement values/failures, distinctness, family maps, sections, and invalid-probe results. The fresh subset exactly preserves the prior **32/38** exit distribution and every failure classification. Fresh #1 and #72 normal receipts are full-JSON identical.

## Canonical 17, structure, thresholds, invalid results

Fresh normal receipts each contain the same canonical 17 measurements. The 17 fixture SHA-256 values match the R55 ledger and were independently computed from current WAV files under `corpus/artifacts/`; all normal metrics match the prior replay. The pair modes have the same 17 canonical measurements plus only their one supplemental probe. Generic distinctness has five `_alt` comparisons; the four family maps (UI, impact, movement, ambience) each have two comparisons; section results cover `stem_sections` and the three stem layers. The eight invalid classifications remain: `short_sections` section count; `corrupt` decode; `wrong_format` format; `odd_sections` section count; `native16_probe` pass; `native24_probe` format; `stereo48_probe` format; `mono441_probe` format.

The unchanged thresholds are: 48 kHz; duration ±0.001 s; peak <0.95; RMS >=0.001; loop endpoint delta <=0.03; loop slope <=0.001 full-scale/sample; section contrast >=6 dB; internal-join adjacent delta <=0.03; internal-join side slope <=0.001 full-scale/sample.

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

## Exact 72-command ledger

Each row records the command actually run, process exit code, distinct new receipt path, and failure classification parsed from that receipt. `none` means no measurement/invalid-probe failures.

| # | Exact command | Exit | Fresh receipt | Receipt failures |
|---:|---|---:|---|---|
| 01 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121757674626Z-normal/measurements.json` | none |
| 02 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-mask-zero` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121758699860Z-ui-extensible-mask-zero/measurements.json` | none |
| 03 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-mask-center` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121759723986Z-ui-extensible-mask-center/measurements.json` | none |
| 04 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-pcm16` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121800756886Z-ui-extensible-pcm16/measurements.json` | none |
| 05 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-standard-pcm16-r55` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121801780879Z-ui-standard-pcm16-r55/measurements.json` | none |
| 06 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm32` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121802817852Z-ui-pcm32/measurements.json` | ui_depth_pcm32_r54_probe: format: expected PCM16 |
| 07 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16-r54` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121803832170Z-ui-pcm16-r54/measurements.json` | none |
| 08 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-float32` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121804847899Z-ui-float32/measurements.json` | ui_depth_float32_r53_probe: format: expected PCM16 |
| 09 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16-r53` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121805857583Z-ui-pcm16-r53/measurements.json` | none |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm8` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121806883584Z-ui-pcm8/measurements.json` | ui_depth_pcm8_r52_probe: format: expected PCM16 |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16-r52` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121807902194Z-ui-pcm16-r52/measurements.json` | none |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm24` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121808936486Z-ui-pcm24/measurements.json` | ui_depth_pcm24_probe: format: expected PCM16 |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121809953793Z-ui-pcm16/measurements.json` | none |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-channel-stereo` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121810980964Z-ui-channel-stereo/measurements.json` | ui_channel_stereo_probe: format: expected 48kHz mono |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-channel-mono` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121811999467Z-ui-channel-mono/measurements.json` | none |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-48001` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121813024473Z-ui-rate-48001/measurements.json` | ui_rate_r49_48001_probe: format: expected 48kHz mono |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-48000-r49` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121814043456Z-ui-rate-48000-r49/measurements.json` | none |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-47999` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121815071300Z-ui-rate-47999/measurements.json` | ui_rate_47999_probe: format: expected 48kHz mono |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-48000` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121816096791Z-ui-rate-48000/measurements.json` | none |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-upper-centroid-below` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121817125872Z-ui-upper-centroid-below/measurements.json` | none |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-upper-centroid-above` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121818160947Z-ui-upper-centroid-above/measurements.json` | ui_upper_centroid_above_probe: spectrum: centroid outside fixture band |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-absolute-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121819178624Z-ui-absolute-centroid-below/measurements.json` | ui_absolute_centroid_below_probe: spectrum: centroid outside fixture band |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-absolute-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121820210776Z-ui-absolute-centroid-above/measurements.json` | none |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-tolerance-5713` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121821247459Z-ui-lower-tolerance-5713/measurements.json` | none |
| 25 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-tolerance-5711` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121822278945Z-ui-lower-tolerance-5711/measurements.json` | ui_lower_tolerance_5711_probe: duration: outside ±1 ms |
| 26 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-tolerance-5807` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121823311729Z-ui-tolerance-5807/measurements.json` | none |
| 27 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-tolerance-5809` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121824357469Z-ui-tolerance-5809/measurements.json` | ui_tolerance_5809_probe: duration: outside ±1 ms |
| 28 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-crest-46` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121825392139Z-ui-crest-46/measurements.json` | ui_crest_46_probe: level: clipping headroom or near silence |
| 29 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-crest-47` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121826422518Z-ui-crest-47/measurements.json` | none |
| 30 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-peak-31129` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121827454697Z-ui-peak-31129/measurements.json` | none |
| 31 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-peak-31130` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121828487650Z-ui-peak-31130/measurements.json` | ui_peak_31130_probe: level: clipping headroom or near silence |
| 32 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-32` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121829531566Z-outer-slope-32/measurements.json` | none |
| 33 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-33` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121830574637Z-outer-slope-33/measurements.json` | slope_33_probe: loop seam: slope mismatch > .001 full scale per sample |
| 34 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-endpoint-983` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121831614266Z-outer-endpoint-983/measurements.json` | none |
| 35 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-endpoint-984` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121832661945Z-outer-endpoint-984/measurements.json` | endpoint_984_probe: loop seam: endpoint jump > .03 full scale |
| 36 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-forward` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121833755111Z-ambience-orientation-forward/measurements.json` | none |
| 37 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121834853994Z-ambience-orientation-reverse/measurements.json` | ambience_orientation_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 38 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121835963147Z-ambience-centroid-above/measurements.json` | none |
| 39 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121837076061Z-ambience-centroid-below/measurements.json` | ambience_probe_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 40 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-mixed-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121838146383Z-ui-mixed-pass/measurements.json` | none |
| 41 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-joint-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121839219784Z-ui-joint-below/measurements.json` | ui_joint_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 42 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-forward` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121840293483Z-ui-orientation-forward/measurements.json` | ui_orientation_forward_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 43 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-reverse` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121841369341Z-ui-orientation-reverse/measurements.json` | none |
| 44 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121842445822Z-ui-lower-centroid-below/measurements.json` | ui_lower_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 45 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121843527428Z-ui-lower-centroid-above/measurements.json` | none |
| 46 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121844590177Z-ui-centroid-below/measurements.json` | ui_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 47 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121845655161Z-ui-centroid-above/measurements.json` | none |
| 48 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121846734429Z-ui-duration-below/measurements.json` | ui_duration_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 49 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121847804411Z-ui-duration-at/measurements.json` | none |
| 50 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121848887202Z-ui-clone/measurements.json` | ui_clone_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 51 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121849947090Z-layer-third-join-edge-pass/measurements.json` | none |
| 52 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121851008935Z-layer-third-join-edge-fail/measurements.json` | join200_edgefail_probe: sections: internal join adjacent sample gap > .03 full scale |
| 53 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121852058838Z-layer-third-join/measurements.json` | join200_probe: sections: internal join adjacent sample gap > .03 full scale |
| 54 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121853119365Z-layer-third-slope-edge-pass/measurements.json` | none |
| 55 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121854171160Z-layer-third-slope-edge-fail/measurements.json` | edgefail_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 56 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121855224254Z-layer-third-slope/measurements.json` | slope200_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 57 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121856273309Z-layer-alt-reverse/measurements.json` | reverse180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 58 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121857315105Z-layer-alt-slope/measurements.json` | slope180_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 59 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121858367449Z-layer-alt-join/measurements.json` | join180_probe: sections: internal join adjacent sample gap > .03 full scale |
| 60 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121859408002Z-layer-alt-flat/measurements.json` | flat180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 61 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121900462703Z-layer-slope/measurements.json` | layer_slope_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 62 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121901506911Z-layer-join/measurements.json` | join_probe: sections: internal join adjacent sample gap > .03 full scale |
| 63 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121902562140Z-flat/measurements.json` | flat30_probe: sections: 30 Hz component amplitude contrast < 6 dB or invalid |
| 64 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121903610503Z-layer-flat/measurements.json` | flat120_probe: sections: 120 Hz component amplitude contrast < 6 dB or invalid |
| 65 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121904662089Z-slope/measurements.json` | slope_probe: loop seam: slope mismatch > .001 full scale per sample |
| 66 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121905643617Z-failing/measurements.json` | ambience: spectrum: centroid outside fixture band, loop seam: endpoint jump > .03 full scale |
| 67 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261013T121905981691Z-invalid/measurements.json` | short_sections: section count (expected_failure); corrupt: decode (expected_failure); wrong_format: format (expected_failure); odd_sections: section count (expected_failure); native24_probe: format (expected_failure); stereo48_probe: format (expected_failure); mono441_probe: format (expected_failure) |
| 68 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121906962052Z-normal/measurements.json` | none |
| 69 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121907938327Z-normal/measurements.json` | none |
| 70 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121908924121Z-normal/measurements.json` | none |
| 71 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121909942131Z-normal/measurements.json` | none |
| 72 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T121910955617Z-normal/measurements.json` | none |
