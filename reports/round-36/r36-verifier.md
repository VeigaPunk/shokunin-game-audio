# Round 36 independent verifier — NON-AUTHOR

## Verdict and scope

**Replay verified; the third ambience fixture passes the declared analytic checks.** I ran 34 serial invocations: initial normal (#1), the prior Round 35 33-run sequence without its duplicate initial normal (#2–#33: mixed pass, UI and section/loop probes including invalid, then four normal restores), followed by an extra final normal (#34). Counts: **13 exit 0, 21 expected fixture-failure exit 1, zero other replay exits and zero replay runner setup failures**. The prior-33 subset (#1–#33) has **12 exit 0 / 21 exit 1**.

Every valid receipt (#1–#28 and #30–#34) has **17 canonical measurements**. `ambience_third` is exactly **2.0 s / 96,000 frames, 48 kHz mono PCM16**, with peak `0.225006103515625` FS, RMS `-16.92261930553234` dBFS, weighted positive-frequency centroid `112.03210352691181` Hz, endpoint delta `0.002777099609375` FS, side-slope mismatch `0.0` FS/sample, and no ordinary failures. Its canonical SHA-256 is `c2c8e0bb2385bc93b39c70b719d0f56553c771969986ef1f732d24af5677d404`.

The explicit `ambience_family_comparisons` records are:

| Pair | Duration delta | Relative centroid delta | Result |
|---|---:|---:|---|
| `ambience` → `ambience_third` | 0.0 s | 2.059614818322321 | pass, centroid arm only |
| `ambience_alt` → `ambience_third` | 0.0 s | 0.9309488765840295 | pass, centroid arm only |

The unchanged predicate is duration delta ≥.020 s **OR** baseline-relative centroid delta ≥.10. For both equal-duration pairs, duration is zero and fails its arm; each passes solely on centroid. The loop endpoint/slope checks are local numeric seam proxies, not perceptual seamlessness. A scalar centroid is lossy and does not establish spectral-distribution novelty.

All **16 pre-existing canonical WAV SHA-256 values** match their bytes at clean-before `HEAD` `1fdccc41e936772150fae74131bda1a1ef7e3520`; their normal measurement records are unchanged versus the Round 35 pre-integration normal receipt. The five generic `_alt` records and explicit UI, impact, and movement family comparison records also match that receipt. All threshold constants are unchanged; `centroid_bands_hz` only adds the expected `ambience_third: [5, 200]` entry. Normal receipts #1/#30/#31/#32/#33/#34 match after excluding measurement `path` fields.

This establishes **analytic fixture coverage only**, not perceptual seamlessness, spectral-distribution novelty, sound quality, production, rights, engine suitability, publishing, or promotion.

## Exact serial commands, exits, receipts, and failure kinds

The command column shows the exact runner command for each numbered invocation. Every receipt is repository-relative. Exit-1 probes are expected fixture-validation failures, not setup errors.

| # | Exact command | Exit | Receipt | Failure kind / invalid statuses |
|---:|---|---:|---|---|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T035441105253Z-normal/measurements.json` | none |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-mixed-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T035442203152Z-ui-mixed-pass/measurements.json` | none |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-joint-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T035443299028Z-ui-joint-below/measurements.json` | {"ui_joint_below_alt":["distinctness: duration < .020 s and centroid delta < 10%"]} |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-forward` | 1 | `.shokunin/audio/corpus/live/runs/20261013T035444380070Z-ui-orientation-forward/measurements.json` | {"ui_orientation_forward_alt":["distinctness: duration < .020 s and centroid delta < 10%"]} |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-reverse` | 0 | `.shokunin/audio/corpus/live/runs/20261013T035445522892Z-ui-orientation-reverse/measurements.json` | none |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T035446599778Z-ui-lower-centroid-below/measurements.json` | {"ui_lower_centroid_below_alt":["distinctness: duration < .020 s and centroid delta < 10%"]} |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T035447814862Z-ui-lower-centroid-above/measurements.json` | none |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T035448901582Z-ui-centroid-below/measurements.json` | {"ui_centroid_below_alt":["distinctness: duration < .020 s and centroid delta < 10%"]} |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T035449975855Z-ui-centroid-above/measurements.json` | none |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T035451044695Z-ui-duration-below/measurements.json` | {"ui_duration_below_alt":["distinctness: duration < .020 s and centroid delta < 10%"]} |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 | `.shokunin/audio/corpus/live/runs/20261013T035452120536Z-ui-duration-at/measurements.json` | none |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 | `.shokunin/audio/corpus/live/runs/20261013T035453208078Z-ui-clone/measurements.json` | {"ui_clone_alt":["distinctness: duration < .020 s and centroid delta < 10%"]} |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T035454273948Z-layer-third-join-edge-pass/measurements.json` | none |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T035455332481Z-layer-third-join-edge-fail/measurements.json` | {"join200_edgefail_probe":["sections: internal join adjacent sample gap > .03 full scale"]} |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T035456384792Z-layer-third-join/measurements.json` | {"join200_probe":["sections: internal join adjacent sample gap > .03 full scale"]} |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T035457435225Z-layer-third-slope-edge-pass/measurements.json` | none |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T035458482305Z-layer-third-slope-edge-fail/measurements.json` | {"edgefail_probe":["sections: internal join side slope mismatch > .001 full scale per sample"]} |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T035459538194Z-layer-third-slope/measurements.json` | {"slope200_probe":["sections: internal join side slope mismatch > .001 full scale per sample"]} |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T035500585306Z-layer-alt-reverse/measurements.json` | {"reverse180_probe":["sections: 180 Hz component amplitude contrast < 6 dB or invalid"]} |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T035501630070Z-layer-alt-slope/measurements.json` | {"slope180_probe":["sections: internal join side slope mismatch > .001 full scale per sample"]} |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T035502691231Z-layer-alt-join/measurements.json` | {"join180_probe":["sections: internal join adjacent sample gap > .03 full scale"]} |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T035503738046Z-layer-alt-flat/measurements.json` | {"flat180_probe":["sections: 180 Hz component amplitude contrast < 6 dB or invalid"]} |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T035504787651Z-layer-slope/measurements.json` | {"layer_slope_probe":["sections: internal join side slope mismatch > .001 full scale per sample"]} |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T035505841795Z-layer-join/measurements.json` | {"join_probe":["sections: internal join adjacent sample gap > .03 full scale"]} |
| 25 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T035506911168Z-flat/measurements.json` | {"flat30_probe":["sections: 30 Hz component amplitude contrast < 6 dB or invalid"]} |
| 26 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T035507958778Z-layer-flat/measurements.json` | {"flat120_probe":["sections: 120 Hz component amplitude contrast < 6 dB or invalid"]} |
| 27 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T035509010623Z-slope/measurements.json` | {"slope_probe":["loop seam: slope mismatch > .001 full scale per sample"]} |
| 28 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261013T035510003228Z-failing/measurements.json` | {"ambience":["spectrum: centroid outside fixture band","loop seam: endpoint jump > .03 full scale"]} |
| 29 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261013T035510345434Z-invalid/measurements.json` | {"short_sections":"section count","corrupt":"decode","wrong_format":"format","odd_sections":"section count","native16_probe":null,"native24_probe":"format","stereo48_probe":"format","mono441_probe":"format"} |
| 30 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T035511352003Z-normal/measurements.json` | none |
| 31 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T035512342168Z-normal/measurements.json` | none |
| 32 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T035513330599Z-normal/measurements.json` | none |
| 33 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T035514322525Z-normal/measurements.json` | none |
| 34 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T035515310749Z-normal/measurements.json` | none |

## Canonical invariants and comparisons

Clean-before revision: `1fdccc41e936772150fae74131bda1a1ef7e3520`. These 16 prior fixture bytes were independently hashed against that revision; all match. Their measured values below are the unchanged Round 35 baseline records (duration, peak FS, RMS dBFS, centroid Hz); Round 36's normal receipt agrees for every field except `path`.

| Canonical WAV | SHA-256 | Duration | Peak | RMS dBFS | Centroid Hz |
|---|---|---:|---:|---:|---:|
| `ambience.wav` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` | 2.00 s | 0.174591 | -18.153351 | 36.616408 |
| `ambience_alt.wav` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` | 2.00 s | 0.199738 | -17.670324 | 58.019197 |
| `impact.wav` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` | 0.32 s | 0.808777 | -20.402187 | 10843.127203 |
| `impact_alt.wav` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` | 0.32 s | 0.756165 | -17.329570 | 473.791536 |
| `impact_third.wav` | `d14376241f409f07edde30fbcef86b5f060ff36f731b7578fd9934d1dc1b39bf` | 0.40 s | 0.456116 | -20.849585 | 6838.143303 |
| `movement.wav` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` | 0.24 s | 0.539490 | -23.779941 | 11934.484046 |
| `movement_alt.wav` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` | 0.36 s | 0.639313 | -21.987316 | 12024.214879 |
| `movement_third.wav` | `0e5f815e1987e13646170571e1f1e977b25e3566d90ebcca558c72ed07851d44` | 0.30 s | 0.489502 | -14.025186 | 4553.583280 |
| `stem.wav` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` | 2.00 s | 0.323792 | -14.881435 | 272.675683 |
| `stem_layer.wav` | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` | 4.00 s | 0.059998 | -30.287567 | 190.143327 |
| `stem_layer_alt.wav` | `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` | 4.00 s | 0.049988 | -31.667277 | 277.951384 |
| `stem_layer_third.wav` | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` | 4.00 s | 0.049987 | -31.667248 | 287.938059 |
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` | 4.00 s | 0.172363 | -23.066521 | 201.870691 |
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` | 0.12 s | 0.375946 | -19.991688 | 966.896659 |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` | 0.16 s | 0.318787 | -20.525534 | 1423.153254 |
| `ui_third.wav` | `734a0a47077f5b614b5d51d486b88a51940c7d61ecea0878642b60a0103513bc` | 0.20 s | 0.375946 | -22.206954 | 966.721622 |
| `ambience_third.wav` | `c2c8e0bb2385bc93b39c70b719d0f56553c771969986ef1f732d24af5677d404` | 2.00 s | 0.225006 | -16.922619 | 112.032104 |

Round 36 valid receipts all contain 17 canonical entries, including the added fixture; the invalid receipt #29 has no canonical measurement set. Existing generic `_alt` and family comparison values in the Round 36 initial normal receipt match the Round 35 initial-normal baseline exactly:

| Existing comparison | Duration delta | Relative centroid delta | Result |
|---|---:|---:|---|
| Generic `ui` → `ui_alt` | 0.04000000000000001 s | 0.47187731004956435 | pass |
| Generic `impact` → `impact_alt` | 0.0 s | 0.9563048992406177 | pass |
| Generic `movement` → `movement_alt` | 0.12 s | 0.007518618572621081 | pass |
| Generic `ambience` → `ambience_alt` | 0.0 s | 0.5845136323520758 | pass |
| Generic `stem_layer` → `stem_layer_alt` | 0.0 s | 0.46179931396667484 | pass |
| UI: `ui` → `ui_third` | 0.08000000000000002 s | 0.00018103031409457665 | pass |
| UI: `ui_alt` → `ui_third` | 0.04000000000000001 s | 0.3207185389302337 | pass |
| Impact: `impact` → `impact_third` | 0.08000000000000002 s | 0.36935690461299725 | pass |
| Impact: `impact_alt` → `impact_third` | 0.08000000000000002 s | 13.432810187572105 | pass |
| Movement: `movement` → `movement_third` | 0.06 s | 0.6184516010427937 | pass |
| Movement: `movement_alt` → `movement_third` | 0.06 s | 0.6212989100908565 | pass |

For the existing generic distinctness rule, values remain duration ≥.020 s OR relative centroid ≥.10. Other threshold values are unchanged: sample rate 48,000 Hz; duration tolerance .001 s; peak <.95; RMS >.001; loop endpoint <.03; loop slope <.001; section contrast ≥6 dB; join delta <.03; join slope <.001; section amplitude ≥.01; section RMS ≥.001. The only added centroid-band mapping is `ambience_third: [5, 200]`.

The prior-33 replay outcomes are preserved: #1–#33 have 12 successes and 21 expected failures; #34 is the extra normal restore. Invalid probe statuses in #29 are exactly: `short_sections=expected_failure(section count)`, `corrupt=expected_failure(decode)`, `wrong_format=expected_failure(format)`, `odd_sections=expected_failure(section count)`, `native16_probe=expected_pass`, `native24_probe=expected_failure(format)`, `stereo48_probe=expected_failure(format)`, and `mono441_probe=expected_failure(format)`.

## Setup failures, limits, and writes

**Separate replay setup attempts:** my initial wrapper mistakenly quoted each whole command as one shell executable (`"""<exact runner command>"""`); all 34 attempts exited 127 with “No such file or directory” and produced no receipts. These were harness invocation errors, not runner outcomes or fixture failures. I then reran the specified 34 commands serially with the correct shell invocation; the replay above had zero setup failures. Wave-one reports document separate issues: executor's first relative-path attempt exited 1 before a corrected successful measurement; no other candidate-fit failure is reported. The selected alt candidate fit and this replay passed. These setup incidents are distinct from expected exit-1 gate probes.

I read the Round 36 LOG and wave-one reports, Round 35 verifier, and Round 35 normal receipt. I wrote only this verifier report and runner-generated receipts under `.shokunin/audio/corpus/live/runs/`; no shared source, LOG, SCORECARD, canonical artifact, or other report was edited. No commits or pushes.
