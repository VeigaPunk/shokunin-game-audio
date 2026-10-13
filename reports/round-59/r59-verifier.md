# R59 non-author verifier — 78-command serial replay

## Verdict and scope

**PASS for the specified integrated pair and runner path.** The designated serial replay completed all 78 commands: **40 exit 0 / 38 expected validation exit 1**, and every command yielded a fresh, independently parsed receipt. The mapped R58 76-command subset (fresh #1 and #4–#78) is **38 exit 0 / 38 exit 1**; its command text, exit codes, and complete parsed JSON values match all 76 R58 verifier entries exactly. All 78 receipt paths are unique and distinct from the R58 historical paths. Initial and final normal receipts have identical complete JSON.

This is evidence for the particular constructed files, unchanged local measurement gates, and this host's execution. It does **not** establish valid-bit metadata enforcement, meaningful precision/fidelity, general decoder or format behavior, audibility, quality, production suitability, rights, engine behavior, publishing, or promotion. No source edits, commits, or pushes were made. I wrote only this verifier report; the 78 receipt JSON files are runner output.

## Integrated source diff against clean-before

Compared the integrated source with clean-before `fe96f1b1948360cb089aad0a23b69864406453d1`. The builder adds `build_ui_extensible_valid13_probe()` and its two `--probe-ui-extensible-valid-(13, 16)-r59` build selections; the runner adds those two mutually exclusive flags, forwards the selected builder flag, measures only the selected R59 file using the existing UI spec, and selects R59-specific mode and receipt suffixes. Pair path is `corpus/live/round-59/pair_valid_{13,16}.wav`. The existing format predicate, UI spec/thresholds, canonical inputs, and prior probe meanings are unchanged. No valid-bits enforcement was added; existing format metadata checks do not inspect `wValidBitsPerSample`.

## Pair, headers, probes, and decode

The integrated files have the expected WAV hashes:

| File | WAV SHA-256 | Valid bits | Payload SHA-256 |
|---|---|---:|---|
| `pair_valid_13.wav` | `873485d5dd0d5108f0523ab974cbba6ce792e715861d481db0ad68ea35f2f2e0` | 13 | `88cac2a0475a0fdbedc4be3758a2215b3937219f13a5c8ff0515a10f1e09ccd1` |
| `pair_valid_16.wav` | `c8f327e38f34125a15bfe3e490905852a228ba26436b0a3b1633a6f58a4a1f3b` | 16 | same |

I parsed both raw RIFF files: 11,588 bytes, RIFF size 11,580, WAVE, `fmt` size 40, tag `0xfffe`, mono/48,000 Hz, byte rate 96,000, block align 2, 16-bit container, `cbSize=22`, channel mask `0x4`, PCM subtype GUID `0100000000001000800000aa00389b71`, data size 11,520 bytes (5,760 samples). The signed-16 payload is identical and every sample is divisible by eight. Byte comparison found exactly one differing file byte: offset 38, valid-bits 13 versus 16. Both target opt-in runner commands (#2/#3) exited 0 and their receipt measurements have no failures:

- valid13: 0.120 s, 48,000 Hz mono, `pcm_s16le`/16-bit container, peak `0.659912109375`, RMS `-8.811743007017897 dBFS`, centroid `2139.5871109211243 Hz`, bandwidth `3627.575019576501 Hz`, LUFS null.
- valid16: same values and no failures.

Independent ffprobe commands for each WAV exited 0; both report `pcm_s16le`, `s16`, 48,000 Hz, mono, 16 bits/sample, duration `0.120000`. SoX f32 decodes for both exited 0; vectors each have 5,760 samples, compare exactly equal (0 different samples, max absolute difference 0.0), decoded-vector SHA-256 `afb6ad28ef01a4ed9f3a9ebf4423ee7fc7324982f1ed3fd5ad2a711c6c84c3b7`. ffprobe reports container/decoder metadata, not the valid-bits distinction.

## R58 replay and unchanged battery

For each mapped prior command, I independently parsed both new and historical receipt JSON and compared whole objects (not selected fields). The 76 comparisons all match, including mode, metrics, failure mappings, and thresholds. R58's 38/38 exit split is preserved. The fresh receipt paths are separate from all historical paths. First and last normal JSON are equal.

Canonical artifacts are 17/17 SHA-256-identical to the R58 verifier ledger. The complete canonical SHA/metric ledger (duration, peak, RMS, centroid) is unchanged:

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

Fresh normal receipts retain five generic `_alt` distinctness comparisons, two comparisons in each UI/impact/movement/ambience family map, and the four section records `stem_sections`, `stem_layer`, `stem_layer_alt`, `stem_layer_third`. The eight invalid-probe classifications match R58: `short_sections` section count; `corrupt` decode; `wrong_format` format; `odd_sections` section count; `native16_probe` expected pass; `native24_probe`, `stereo48_probe`, and `mono441_probe` format.

Unchanged thresholds: rate 48,000 Hz; duration tolerance ±0.001 s; peak <0.95; RMS >0.001; UI centroid 250–4,000 Hz, impact 50–15,000 Hz, movement 100–16,000 Hz, ambience 5–200 Hz, stem 100–2,000 Hz; loop endpoint delta ≤0.03; loop slope ≤0.001 full-scale/sample; section contrast ≥6 dB; section component amplitude ≥0.01; section RMS ≥0.001; internal-join adjacent delta ≤0.03; internal-join side-slope mismatch ≤0.001 full-scale/sample; distinctness duration delta ≥0.020 s or relative centroid delta ≥10%.

## Exact 78-command serial ledger

The following is the designated 78-command run in order. Exit-1 entries are expected validation outcomes, not setup errors. Every command has a fresh JSON receipt; the invalid-battery row expands the receipt classifications.

| # | Exact command | Exit | Fresh receipt | Failure(s) / classifications |
|---:|---|---:|---|---|
| 01 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131241531728Z-normal/measurements.json` | none |
| 02 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-13-r59` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131242584048Z-ui-extensible-valid-13-r59/measurements.json` | none |
| 03 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-16-r59` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131243646181Z-ui-extensible-valid-16-r59/measurements.json` | none |
| 04 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-14-r58` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131244720337Z-ui-extensible-valid-14-r58/measurements.json` | none |
| 05 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-16-r58` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131245789514Z-ui-extensible-valid-16-r58/measurements.json` | none |
| 06 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-15` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131246865626Z-ui-extensible-valid-15/measurements.json` | none |
| 07 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-16` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131247944746Z-ui-extensible-valid-16/measurements.json` | none |
| 08 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-mask-zero` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131249007615Z-ui-extensible-mask-zero/measurements.json` | none |
| 09 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-mask-center` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131250065565Z-ui-extensible-mask-center/measurements.json` | none |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-pcm16` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131251136313Z-ui-extensible-pcm16/measurements.json` | none |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-standard-pcm16-r55` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131252205074Z-ui-standard-pcm16-r55/measurements.json` | none |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm32` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131253267545Z-ui-pcm32/measurements.json` | ui_depth_pcm32_r54_probe: format: expected PCM16 |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16-r54` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131254340549Z-ui-pcm16-r54/measurements.json` | none |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-float32` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131255389496Z-ui-float32/measurements.json` | ui_depth_float32_r53_probe: format: expected PCM16 |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16-r53` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131256474238Z-ui-pcm16-r53/measurements.json` | none |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm8` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131257554882Z-ui-pcm8/measurements.json` | ui_depth_pcm8_r52_probe: format: expected PCM16 |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16-r52` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131258633958Z-ui-pcm16-r52/measurements.json` | none |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm24` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131259706028Z-ui-pcm24/measurements.json` | ui_depth_pcm24_probe: format: expected PCM16 |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131300802428Z-ui-pcm16/measurements.json` | none |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-channel-stereo` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131301886744Z-ui-channel-stereo/measurements.json` | ui_channel_stereo_probe: format: expected 48kHz mono |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-channel-mono` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131302948581Z-ui-channel-mono/measurements.json` | none |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-48001` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131303999648Z-ui-rate-48001/measurements.json` | ui_rate_r49_48001_probe: format: expected 48kHz mono |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-48000-r49` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131305059747Z-ui-rate-48000-r49/measurements.json` | none |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-47999` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131306118481Z-ui-rate-47999/measurements.json` | ui_rate_47999_probe: format: expected 48kHz mono |
| 25 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-48000` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131307181901Z-ui-rate-48000/measurements.json` | none |
| 26 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-upper-centroid-below` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131308247887Z-ui-upper-centroid-below/measurements.json` | none |
| 27 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-upper-centroid-above` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131309311128Z-ui-upper-centroid-above/measurements.json` | ui_upper_centroid_above_probe: spectrum: centroid outside fixture band |
| 28 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-absolute-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131310371715Z-ui-absolute-centroid-below/measurements.json` | ui_absolute_centroid_below_probe: spectrum: centroid outside fixture band |
| 29 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-absolute-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131311427780Z-ui-absolute-centroid-above/measurements.json` | none |
| 30 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-tolerance-5713` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131312501043Z-ui-lower-tolerance-5713/measurements.json` | none |
| 31 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-tolerance-5711` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131313575176Z-ui-lower-tolerance-5711/measurements.json` | ui_lower_tolerance_5711_probe: duration: outside ±1 ms |
| 32 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-tolerance-5807` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131314627624Z-ui-tolerance-5807/measurements.json` | none |
| 33 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-tolerance-5809` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131315698484Z-ui-tolerance-5809/measurements.json` | ui_tolerance_5809_probe: duration: outside ±1 ms |
| 34 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-crest-46` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131316755408Z-ui-crest-46/measurements.json` | ui_crest_46_probe: level: clipping headroom or near silence |
| 35 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-crest-47` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131317816870Z-ui-crest-47/measurements.json` | none |
| 36 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-peak-31129` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131318873483Z-ui-peak-31129/measurements.json` | none |
| 37 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-peak-31130` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131319943385Z-ui-peak-31130/measurements.json` | ui_peak_31130_probe: level: clipping headroom or near silence |
| 38 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-32` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131321022301Z-outer-slope-32/measurements.json` | none |
| 39 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-33` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131322091567Z-outer-slope-33/measurements.json` | slope_33_probe: loop seam: slope mismatch > .001 full scale per sample |
| 40 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-endpoint-983` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131323162945Z-outer-endpoint-983/measurements.json` | none |
| 41 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-endpoint-984` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131324240123Z-outer-endpoint-984/measurements.json` | endpoint_984_probe: loop seam: endpoint jump > .03 full scale |
| 42 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-forward` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131325368304Z-ambience-orientation-forward/measurements.json` | none |
| 43 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131326497152Z-ambience-orientation-reverse/measurements.json` | ambience_orientation_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 44 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131327635676Z-ambience-centroid-above/measurements.json` | none |
| 45 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131328769425Z-ambience-centroid-below/measurements.json` | ambience_probe_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 46 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-mixed-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131329879672Z-ui-mixed-pass/measurements.json` | none |
| 47 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-joint-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131330968980Z-ui-joint-below/measurements.json` | ui_joint_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 48 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-forward` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131332073243Z-ui-orientation-forward/measurements.json` | ui_orientation_forward_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 49 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-reverse` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131333168183Z-ui-orientation-reverse/measurements.json` | none |
| 50 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131334269829Z-ui-lower-centroid-below/measurements.json` | ui_lower_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 51 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131335367542Z-ui-lower-centroid-above/measurements.json` | none |
| 52 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131336483175Z-ui-centroid-below/measurements.json` | ui_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 53 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131337573223Z-ui-centroid-above/measurements.json` | none |
| 54 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131338684155Z-ui-duration-below/measurements.json` | ui_duration_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 55 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131339793113Z-ui-duration-at/measurements.json` | none |
| 56 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131340893796Z-ui-clone/measurements.json` | ui_clone_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 57 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131341990406Z-layer-third-join-edge-pass/measurements.json` | none |
| 58 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131343087861Z-layer-third-join-edge-fail/measurements.json` | join200_edgefail_probe: sections: internal join adjacent sample gap > .03 full scale |
| 59 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131344180527Z-layer-third-join/measurements.json` | join200_probe: sections: internal join adjacent sample gap > .03 full scale |
| 60 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131345246512Z-layer-third-slope-edge-pass/measurements.json` | none |
| 61 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131346320914Z-layer-third-slope-edge-fail/measurements.json` | edgefail_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 62 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131347400801Z-layer-third-slope/measurements.json` | slope200_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 63 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131348495520Z-layer-alt-reverse/measurements.json` | reverse180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 64 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131349579282Z-layer-alt-slope/measurements.json` | slope180_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 65 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131350667205Z-layer-alt-join/measurements.json` | join180_probe: sections: internal join adjacent sample gap > .03 full scale |
| 66 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131351761646Z-layer-alt-flat/measurements.json` | flat180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 67 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131352832037Z-layer-slope/measurements.json` | layer_slope_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 68 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131353919985Z-layer-join/measurements.json` | join_probe: sections: internal join adjacent sample gap > .03 full scale |
| 69 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131354989792Z-flat/measurements.json` | flat30_probe: sections: 30 Hz component amplitude contrast < 6 dB or invalid |
| 70 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131356102367Z-layer-flat/measurements.json` | flat120_probe: sections: 120 Hz component amplitude contrast < 6 dB or invalid |
| 71 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131357170798Z-slope/measurements.json` | slope_probe: loop seam: slope mismatch > .001 full scale per sample |
| 72 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131358190172Z-failing/measurements.json` | ambience: spectrum: centroid outside fixture band; loop seam: endpoint jump > .03 full scale |
| 73 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261013T131358546073Z-invalid/measurements.json` | short_sections=expected_failure(section count); corrupt=expected_failure(decode); wrong_format=expected_failure(format); odd_sections=expected_failure(section count); native16_probe=expected_pass; native24_probe=expected_failure(format); stereo48_probe=expected_failure(format); mono441_probe=expected_failure(format) |
| 74 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131359552497Z-normal/measurements.json` | none |
| 75 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131400566747Z-normal/measurements.json` | none |
| 76 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131401631252Z-normal/measurements.json` | none |
| 77 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131402642260Z-normal/measurements.json` | none |
| 78 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T131403651634Z-normal/measurements.json` | none |

## Setup and receipt boundary

The designated 78-command replay had no receiptless runner command, decode failure, or unexpected numeric-fit failure. One preliminary malformed shell invocation exited 127 before starting the runner and produced no receipt; it is setup-only and excluded from all replay counts.

Chronology correction: filesystem timestamps show another complete 78-receipt sequence from `20261013T131110133069Z-normal` through `20261013T131231893990Z-normal` **before** the designated ledger run (`131241…` through `131403…`). It was a discarded earlier rehearsal/replay, not a post-run duplicate and not receiptless. I inspected its receipts: all 78 JSON files exist, follow the same mode sequence, and their complete parsed JSON objects match the designated sequence. The first run was already valid. I unnecessarily ran the second complete sequence because I mistakenly believed the first run’s in-memory results had been lost after the separate malformed shell attempt; they had not. The second loop overwrote that list. The later run supplies the designated, ordered ledger, but it was not needed to establish fresh evidence. The designated run's paths are disjoint from all 78 rehearsal paths, all 76 R58 historical paths, and the three author-created R59/normal paths (`20261013T130806550621Z`, `130807593391Z`, `130808600777Z`). Only the designated receipts appear in the ledger and its 78/40/38 verdict. The rehearsal receipts remain runner outputs but are excluded from that count. No numeric threshold was adjusted and no failure was forced into a receipt count.
