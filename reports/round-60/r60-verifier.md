# R60 non-author verifier — 80-command serial replay

## Verdict and bounded scope

**PASS for this specified malformed/unspecified header pair and this host's runner path.** Exactly 80 runner commands were executed serially once, each with a distinct, new receipt path: **42 exit 0 / 38 expected validation exit 1**. The designated R59 78-command sequence was replayed as commands #1 and #4–#80: **40 exit 0 / 38 exit 1**. Every selected command produced a receipt; valid0, valid16, initial normal, and final normal exited 0. Initial/final normal receipts are equal as complete JSON. No author, historical, or rehearsal receipt path was reused.

The test does **not** establish universal valid-bit enforcement, conforming valid-bit metadata, zero-bit precision, signal resolution, fidelity, audibility, quality, production suitability, rights, engine behavior, publishing, or promotion. The `wValidBitsPerSample=0` field is malformed/unspecified and is **not** a conforming positive test vector. Results are limited to the specified files, installed ffprobe/SoX, unchanged project measurement gate, and this host. I made no source changes, commits, or pushes. This verifier report is the only report file I wrote; the runner generated the receipts.

## Integrated diff against clean-before

Compared integrated source against clean-before `4894d074b29b6585bafc71682cbde1e0048b906c`. `build_artifacts.py` adds a deterministic R60 builder for a matched pair and two builder selections. `measure_audio.py` adds the two mutually exclusive R60 flags, forwards the selection, measures the chosen R60 WAV with the existing UI spec, and labels its mode/receipt suffix. No `format_failures()` predicate, UI spec or threshold, canonical fixture, or prior probe meaning changed. R60 does not add a check for `wValidBitsPerSample`.

## Pair construction, byte comparison, and decode

The integrated files are `.shokunin/audio/corpus/live/round-60/pair_valid_0.wav` and `pair_valid_16.wav`. Both are 11,588-byte RIFF/WAVE extensible files with fmt size 40, extensible tag `0xfffe`, mono 48,000 Hz, 16-bit container, `cbSize=22`, channel mask `0x4`, PCM subtype GUID, and 5,760 signed-16 samples (0.120 s). Their data payloads are identical. The only file-byte difference is offset 38 (`wValidBitsPerSample`: 0 vs 16).

| file | SHA-256 | valid bits |
|---|---|---:|
| `pair_valid_0.wav` | `5ab169fc3f43b29c0bb17cc86e6b76fb424e590b7d788a503a002501c8a2f394` | 0 |
| `pair_valid_16.wav` | `d7f08d659b608e003e5ef2aaccf325dae3bd4e961caeaa450bd933c406b4cc46` | 16 |

Independent ffprobe invocations for both returned exit 0 and reported `pcm_s16le`, `s16`, 48 kHz, mono, 16 bits/sample, duration `0.120000`. Independent SoX f32 decode invocations each returned exit 0; both yielded 5,760 samples and exactly equal float vectors (0 unequal samples; max absolute difference 0). SoX decoded-vector SHA-256 for both is `adc56a24cd7a2bc4c34ef6112b384b3567f6d6b1e4568aef0c8722f6170dca6c`. This shows only that these installed tools decoded this pair; ffprobe's PCM16 report does not mean valid-bit metadata was validated.

The two runner receipts have no failures. Both R60 target measurements are 0.120 s, 48,000 Hz mono, `pcm_s16le`/16-bit, peak `0.082489013671875`, RMS `-26.87354274685677 dBFS`, centroid `2139.5871109211243 Hz`, and bandwidth `3627.575019576501 Hz`; LUFS is null. Both selected commands exited 0 with clean receipts. Thus this fixture shows local acceptance and equal decoding of an invalid/unspecified valid-bits declaration, not that zero bits is valid or meaningful audio.

## R59 designated replay, canonical fixtures, and unchanged controls

The source of the historical sequence and expected receipts was the R59 verifier designated 78-command ledger/receipts `131241`–`131403`. I did not use or duplicate the earlier extra78 sequence `131110`–`131231` as historical baseline. For each of the 78 mapped commands (fresh R60 #1 and #4–#80), I compared exact command text, exit status, and complete parsed JSON receipt against the corresponding R59 designated entry. All **78/78** match. R60 receipts are new paths and distinct from all previously existing runner receipts. The earlier R59 verifier's separate rehearsal is disclosed only as history: its paths `131110133069Z`–`131231893990Z` are excluded from baseline/comparison and from the R60 count. No extra R60 rehearsal occurred.

Canonical artifacts are **17/17 SHA-256 identical** to R59. Their exact SHA and metric ledger (duration, peak, RMS, centroid) is:

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

The initial and final normal receipts are exactly equal complete JSON. They retain the five generic `_alt` distinctness results; two comparisons in each UI, impact, movement, and ambience family; and section records for `stem_sections`, `stem_layer`, `stem_layer_alt`, and `stem_layer_third`. The eight invalid-probe classifications are unchanged: `short_sections` section count; `corrupt` decode; `wrong_format` format; `odd_sections` section count; `native16_probe` expected pass; `native24_probe`, `stereo48_probe`, and `mono441_probe` format. The unchanged threshold set is recorded in each receipt and matches R59 (48,000 Hz; duration ±0.001 s; peak <0.95; RMS >0.001; existing centroid bands; loop endpoint ≤0.03; loop slope ≤0.001; section contrast ≥6 dB; component amplitude and RMS minima; internal-join delta/slope limits; distinctness duration/centroid limits).

There were no receiptless runner errors and no numeric failed fits in the selected 80-command sequence. The 38 exit-1 outcomes are expected validation failures captured in their JSON receipts (including the existing invalid battery classifications), not decoder/setup failures.

## Exact 80-command serial ledger

Exit-1 entries are expected validation outcomes, not setup errors. Each receipt path below is unique and new; the table includes exact command, exit, path, and receipt failure/classification.

| # | Exact command | Exit | Fresh receipt path | Failure / classification |
|---:|---|---:|---|---|
| 01 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133202557584Z-normal/measurements.json` | none |
| 02 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-0-r60` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133203624235Z-ui-extensible-valid-0-r60/measurements.json` | none |
| 03 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-16-r60` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133204718244Z-ui-extensible-valid-16-r60/measurements.json` | none |
| 04 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-13-r59` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133205794033Z-ui-extensible-valid-13-r59/measurements.json` | none |
| 05 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-16-r59` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133206859535Z-ui-extensible-valid-16-r59/measurements.json` | none |
| 06 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-14-r58` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133207926790Z-ui-extensible-valid-14-r58/measurements.json` | none |
| 07 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-16-r58` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133208995722Z-ui-extensible-valid-16-r58/measurements.json` | none |
| 08 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-15` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133210073666Z-ui-extensible-valid-15/measurements.json` | none |
| 09 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-valid-16` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133211151836Z-ui-extensible-valid-16/measurements.json` | none |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-mask-zero` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133212232523Z-ui-extensible-mask-zero/measurements.json` | none |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-mask-center` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133213297309Z-ui-extensible-mask-center/measurements.json` | none |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-extensible-pcm16` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133214379655Z-ui-extensible-pcm16/measurements.json` | none |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-standard-pcm16-r55` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133215471545Z-ui-standard-pcm16-r55/measurements.json` | none |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm32` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133216544164Z-ui-pcm32/measurements.json` | ui_depth_pcm32_r54_probe: format: expected PCM16 |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16-r54` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133217606851Z-ui-pcm16-r54/measurements.json` | none |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-float32` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133218677109Z-ui-float32/measurements.json` | ui_depth_float32_r53_probe: format: expected PCM16 |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16-r53` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133219748946Z-ui-pcm16-r53/measurements.json` | none |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm8` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133220834067Z-ui-pcm8/measurements.json` | ui_depth_pcm8_r52_probe: format: expected PCM16 |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16-r52` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133221931084Z-ui-pcm16-r52/measurements.json` | none |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm24` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133223053897Z-ui-pcm24/measurements.json` | ui_depth_pcm24_probe: format: expected PCM16 |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133224135625Z-ui-pcm16/measurements.json` | none |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-channel-stereo` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133225222665Z-ui-channel-stereo/measurements.json` | ui_channel_stereo_probe: format: expected 48kHz mono |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-channel-mono` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133226336533Z-ui-channel-mono/measurements.json` | none |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-48001` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133227436457Z-ui-rate-48001/measurements.json` | ui_rate_r49_48001_probe: format: expected 48kHz mono |
| 25 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-48000-r49` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133228543433Z-ui-rate-48000-r49/measurements.json` | none |
| 26 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-47999` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133229645272Z-ui-rate-47999/measurements.json` | ui_rate_47999_probe: format: expected 48kHz mono |
| 27 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-48000` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133230745194Z-ui-rate-48000/measurements.json` | none |
| 28 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-upper-centroid-below` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133231839158Z-ui-upper-centroid-below/measurements.json` | none |
| 29 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-upper-centroid-above` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133232936211Z-ui-upper-centroid-above/measurements.json` | ui_upper_centroid_above_probe: spectrum: centroid outside fixture band |
| 30 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-absolute-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133234058901Z-ui-absolute-centroid-below/measurements.json` | ui_absolute_centroid_below_probe: spectrum: centroid outside fixture band |
| 31 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-absolute-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133235163359Z-ui-absolute-centroid-above/measurements.json` | none |
| 32 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-tolerance-5713` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133236285153Z-ui-lower-tolerance-5713/measurements.json` | none |
| 33 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-tolerance-5711` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133237384776Z-ui-lower-tolerance-5711/measurements.json` | ui_lower_tolerance_5711_probe: duration: outside ±1 ms |
| 34 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-tolerance-5807` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133238480671Z-ui-tolerance-5807/measurements.json` | none |
| 35 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-tolerance-5809` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133239569260Z-ui-tolerance-5809/measurements.json` | ui_tolerance_5809_probe: duration: outside ±1 ms |
| 36 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-crest-46` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133240661045Z-ui-crest-46/measurements.json` | ui_crest_46_probe: level: clipping headroom or near silence |
| 37 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-crest-47` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133241765631Z-ui-crest-47/measurements.json` | none |
| 38 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-peak-31129` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133242851288Z-ui-peak-31129/measurements.json` | none |
| 39 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-peak-31130` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133243940261Z-ui-peak-31130/measurements.json` | ui_peak_31130_probe: level: clipping headroom or near silence |
| 40 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-32` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133245042157Z-outer-slope-32/measurements.json` | none |
| 41 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-33` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133246134712Z-outer-slope-33/measurements.json` | slope_33_probe: loop seam: slope mismatch > .001 full scale per sample |
| 42 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-endpoint-983` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133247235112Z-outer-endpoint-983/measurements.json` | none |
| 43 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-endpoint-984` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133248344695Z-outer-endpoint-984/measurements.json` | endpoint_984_probe: loop seam: endpoint jump > .03 full scale |
| 44 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-forward` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133249527942Z-ambience-orientation-forward/measurements.json` | none |
| 45 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133250693861Z-ambience-orientation-reverse/measurements.json` | ambience_orientation_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 46 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133251850496Z-ambience-centroid-above/measurements.json` | none |
| 47 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133253036255Z-ambience-centroid-below/measurements.json` | ambience_probe_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 48 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-mixed-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133254165967Z-ui-mixed-pass/measurements.json` | none |
| 49 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-joint-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133255313922Z-ui-joint-below/measurements.json` | ui_joint_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 50 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-forward` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133256451627Z-ui-orientation-forward/measurements.json` | ui_orientation_forward_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 51 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-reverse` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133257602623Z-ui-orientation-reverse/measurements.json` | none |
| 52 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133258733365Z-ui-lower-centroid-below/measurements.json` | ui_lower_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 53 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133259875633Z-ui-lower-centroid-above/measurements.json` | none |
| 54 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133301013703Z-ui-centroid-below/measurements.json` | ui_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 55 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133302131247Z-ui-centroid-above/measurements.json` | none |
| 56 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133303261198Z-ui-duration-below/measurements.json` | ui_duration_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 57 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133304404824Z-ui-duration-at/measurements.json` | none |
| 58 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133305539948Z-ui-clone/measurements.json` | ui_clone_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 59 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133306645541Z-layer-third-join-edge-pass/measurements.json` | none |
| 60 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133307776911Z-layer-third-join-edge-fail/measurements.json` | join200_edgefail_probe: sections: internal join adjacent sample gap > .03 full scale |
| 61 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133308920586Z-layer-third-join/measurements.json` | join200_probe: sections: internal join adjacent sample gap > .03 full scale |
| 62 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133310064065Z-layer-third-slope-edge-pass/measurements.json` | none |
| 63 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133311205554Z-layer-third-slope-edge-fail/measurements.json` | edgefail_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 64 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133312334438Z-layer-third-slope/measurements.json` | slope200_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 65 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133313456331Z-layer-alt-reverse/measurements.json` | reverse180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 66 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133314572255Z-layer-alt-slope/measurements.json` | slope180_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 67 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133315672095Z-layer-alt-join/measurements.json` | join180_probe: sections: internal join adjacent sample gap > .03 full scale |
| 68 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133316767147Z-layer-alt-flat/measurements.json` | flat180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 69 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133317857240Z-layer-slope/measurements.json` | layer_slope_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 70 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133318966179Z-layer-join/measurements.json` | join_probe: sections: internal join adjacent sample gap > .03 full scale |
| 71 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133320073323Z-flat/measurements.json` | flat30_probe: sections: 30 Hz component amplitude contrast < 6 dB or invalid |
| 72 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133321197656Z-layer-flat/measurements.json` | flat120_probe: sections: 120 Hz component amplitude contrast < 6 dB or invalid |
| 73 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133322306855Z-slope/measurements.json` | slope_probe: loop seam: slope mismatch > .001 full scale per sample |
| 74 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133323362370Z-failing/measurements.json` | ambience: spectrum: centroid outside fixture band; ambience: loop seam: endpoint jump > .03 full scale |
| 75 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261013T133323717760Z-invalid/measurements.json` | invalid battery: short_sections=section count, corrupt=decode, wrong_format=format, odd_sections=section count, native16_probe=pass, native24_probe=format, stereo48_probe=format, mono441_probe=format |
| 76 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133324762469Z-normal/measurements.json` | none |
| 77 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133325819646Z-normal/measurements.json` | none |
| 78 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133326873220Z-normal/measurements.json` | none |
| 79 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133327919348Z-normal/measurements.json` | none |
| 80 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T133328973523Z-normal/measurements.json` | none |
