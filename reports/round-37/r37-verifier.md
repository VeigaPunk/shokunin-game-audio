# Round 37 independent verifier — NON-AUTHOR

## Verdict and scope

**The declared local negative control is reproduced; its bounded numeric claim is verified.** I ran 35 runner invocations serially: initial normal (#1), the new `--probe-ambience-centroid-below` negative (#2), then the prior Round 36 sequence without its duplicate initial normal (#3–#35). Counts: **13 exit 0 and 22 expected fixture-validation exit 1; no other runner exits or corrected replay setup errors**. The prior-34 subset (#1 and #3–#35) is **13 exit 0 / 21 expected exit 1**. The final prior restore is #35; no extra restore was added.

The new opt-in receipt #2 contains **17 canonical measurements plus two scratch measurements**. Both scratch files are 2.0 s / 96,000 frames / 48 kHz mono PCM16. The baseline SHA-256 is `281e9a25191825bd062f854de6f9b85f6a5902200e0cd1027e36a225422a901c`; variant SHA-256 is `cd48ad3f1e4020c10225d65904358a1ea1e7f18d28050e858dec9a9b7feed8a9`. The project-measured duration delta is exactly **0.0 s**; baseline centroid is `67.37182625964924 Hz`, variant centroid `71.80863982343814 Hz`, baseline-relative delta `0.06585562259644766` (nonzero and strictly below `.10`). Both individual measurements have empty ordinary/loop failure lists. Existing generic `_alt` distinctness is `passed: false`; the sole failing measurement is `ambience_probe_alt`, with exactly `distinctness: duration < .020 s and centroid delta < 10%`. Runner exit is **1**, as expected for the negative control.

The 17 canonical WAVs retain their SHA-256 values against clean-before `HEAD` `83395d1b4241582463d9d5fbdece619180610372`; their measured records match the Round 36 initial normal baseline (excluding paths). The five generic `_alt` comparisons, all explicit UI/impact/movement/ambience family comparisons, thresholds, and section records match that baseline. Valid receipts contain the same 17 canonical measurements/metrics (excluding paths); #30 is the invalid-probe receipt and has no canonical measurements. Normal #1 and prior restore #35 match on all receipt fields except measurement paths. Prior 34 commands and exits are preserved in order, with the only inserted invocation being this new #2.

This verifies **one local numeric negative control**, not a universal distinctness-threshold calibration, perceptual or spectral-similarity claim, audible seamlessness, audio quality, production suitability, rights, engine suitability, publishing, or promotion.

## Exact serial commands, exits, receipts, and failure kinds

Every path below is repository-relative. Exit-1 probes are expected fixture-validation outcomes, not shell/setup errors. Failure entries are reported exactly from each generated runner receipt.

| # | Exact command | Exit | Receipt | Failure kind / invalid statuses |
|---:|---|---:|---|---|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T040846835874Z-normal/measurements.json` | none |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T040857198401Z-ambience-centroid-below/measurements.json` | ambience_probe_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-mixed-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T040858254012Z-ui-mixed-pass/measurements.json` | none |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-joint-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T040859319232Z-ui-joint-below/measurements.json` | ui_joint_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-forward` | 1 | `.shokunin/audio/corpus/live/runs/20261013T040900394812Z-ui-orientation-forward/measurements.json` | ui_orientation_forward_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-reverse` | 0 | `.shokunin/audio/corpus/live/runs/20261013T040901470063Z-ui-orientation-reverse/measurements.json` | none |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T040902533650Z-ui-lower-centroid-below/measurements.json` | ui_lower_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T040903598969Z-ui-lower-centroid-above/measurements.json` | none |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T040904656650Z-ui-centroid-below/measurements.json` | ui_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T040905724836Z-ui-centroid-above/measurements.json` | none |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T040906784478Z-ui-duration-below/measurements.json` | ui_duration_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 | `.shokunin/audio/corpus/live/runs/20261013T040907852487Z-ui-duration-at/measurements.json` | none |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 | `.shokunin/audio/corpus/live/runs/20261013T040908919967Z-ui-clone/measurements.json` | ui_clone_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T040909969482Z-layer-third-join-edge-pass/measurements.json` | none |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T040911016490Z-layer-third-join-edge-fail/measurements.json` | join200_edgefail_probe: sections: internal join adjacent sample gap > .03 full scale |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T040912056520Z-layer-third-join/measurements.json` | join200_probe: sections: internal join adjacent sample gap > .03 full scale |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T040913095700Z-layer-third-slope-edge-pass/measurements.json` | none |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T040914130973Z-layer-third-slope-edge-fail/measurements.json` | edgefail_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T040915196195Z-layer-third-slope/measurements.json` | slope200_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T040916241776Z-layer-alt-reverse/measurements.json` | reverse180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T040917289092Z-layer-alt-slope/measurements.json` | slope180_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T040918331960Z-layer-alt-join/measurements.json` | join180_probe: sections: internal join adjacent sample gap > .03 full scale |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T040919377527Z-layer-alt-flat/measurements.json` | flat180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T040920420309Z-layer-slope/measurements.json` | layer_slope_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 25 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T040921466313Z-layer-join/measurements.json` | join_probe: sections: internal join adjacent sample gap > .03 full scale |
| 26 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T040922507727Z-flat/measurements.json` | flat30_probe: sections: 30 Hz component amplitude contrast < 6 dB or invalid |
| 27 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T040923558240Z-layer-flat/measurements.json` | flat120_probe: sections: 120 Hz component amplitude contrast < 6 dB or invalid |
| 28 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T040924589216Z-slope/measurements.json` | slope_probe: loop seam: slope mismatch > .001 full scale per sample |
| 29 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261013T040925567443Z-failing/measurements.json` | ambience: spectrum: centroid outside fixture band, loop seam: endpoint jump > .03 full scale |
| 30 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261013T040925901903Z-invalid/measurements.json` | invalid probe statuses: short_sections section count; corrupt decode; wrong_format format; odd_sections section count; native16 expected_pass; native24/stereo48/mono441 format expected_failure |
| 31 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T040926879583Z-normal/measurements.json` | none |
| 32 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T040927874681Z-normal/measurements.json` | none |
| 33 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T040928854429Z-normal/measurements.json` | none |
| 34 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T040929834637Z-normal/measurements.json` | none |
| 35 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T040930813687Z-normal/measurements.json` | none |

## Canonical hashes and measured metrics

Clean-before `HEAD`: `83395d1b4241582463d9d5fbdece619180610372`. I independently hashed all 17 current canonical WAVs and compared them with the Git blobs at that revision; all match. The table's metrics come from receipt #1 and were unchanged in the prior Round 36 verifier's initial normal receipt.

| Canonical WAV | SHA-256 | Duration | Peak FS | RMS dBFS | Centroid Hz |
|---|---|---:|---:|---:|---:|
| `ambience.wav` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` | 2.0 | 0.174591064453 | -18.153351293682 | 36.616407678514 |
| `ambience_alt.wav` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` | 2.0 | 0.199737548828 | -17.670323813588 | 58.019197134366 |
| `ambience_third.wav` | `c2c8e0bb2385bc93b39c70b719d0f56553c771969986ef1f732d24af5677d404` | 2.0 | 0.225006103516 | -16.922619305532 | 112.032103526912 |
| `impact.wav` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` | 0.32 | 0.808776855469 | -20.402186680535 | 10843.127202979935 |
| `impact_alt.wav` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` | 0.32 | 0.756164550781 | -17.329570409215 | 473.791535681008 |
| `impact_third.wav` | `d14376241f409f07edde30fbcef86b5f060ff36f731b7578fd9934d1dc1b39bf` | 0.4 | 0.456115722656 | -20.849584641332 | 6838.143302962279 |
| `movement.wav` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` | 0.24 | 0.539489746094 | -23.779940832329 | 11934.484045946316 |
| `movement_alt.wav` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` | 0.36 | 0.639312744141 | -21.987315616484 | 12024.214879348818 |
| `movement_third.wav` | `0e5f815e1987e13646170571e1f1e977b25e3566d90ebcca558c72ed07851d44` | 0.3 | 0.489501953125 | -14.025186267550 | 4553.583280111138 |
| `stem.wav` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` | 2.0 | 0.323791503906 | -14.881434973008 | 272.675682778914 |
| `stem_layer.wav` | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` | 4.0 | 0.059997558594 | -30.287566545982 | 190.143326752992 |
| `stem_layer_alt.wav` | `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` | 4.0 | 0.049987792969 | -31.667277345674 | 277.951384602865 |
| `stem_layer_third.wav` | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` | 4.0 | 0.049987792969 | -31.667247652743 | 287.938059238444 |
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` | 4.0 | 0.172363281250 | -23.066521225821 | 201.870690230007 |
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` | 0.12 | 0.375946044922 | -19.991687666367 | 966.896659337973 |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` | 0.16 | 0.318786621094 | -20.525534144496 | 1423.153254042285 |
| `ui_third.wav` | `734a0a47077f5b614b5d51d486b88a51940c7d61ecea0878642b60a0103513bc` | 0.2 | 0.375946044922 | -22.206953873168 | 966.721621732036 |

### Unchanged comparisons and thresholds

The existing distinctness rule remains duration delta **≥ .020 s OR** baseline-relative centroid delta **≥ .10**. All five generic comparisons and all eight explicit family comparisons match the Round 36 baseline; thresholds are unchanged. In the new probe, both arms are false (`0.0 < .020`, `0.06585562259644766 < .10`), while ordinary checks and the loop endpoint/slope proxies pass.

- Generic `_alt`: `ui→ui_alt` duration `.04000000000000001`, centroid `.47187731004956435`; `impact→impact_alt` `0.0`, `.9563048992406177`; `movement→movement_alt` `.12`, `.007518618572621081`; `ambience→ambience_alt` `0.0`, `.5845136323520758`; `stem_layer→stem_layer_alt` `0.0`, `.46179931396667484`. All pass.
- UI family: `ui→ui_third` `.08000000000000002`, `.00018103031409457665`; `ui_alt→ui_third` `.04000000000000001`, `.3207185389302337`. Both pass.
- Impact family: `impact→impact_third` `.08000000000000002`, `.36935690461299725`; `impact_alt→impact_third` `.08000000000000002`, `13.432810187572105`. Both pass.
- Movement family: `movement→movement_third` `.06`, `.6184516010427937`; `movement_alt→movement_third` `.06`, `.6212989100908565`. Both pass.
- Ambience family: `ambience→ambience_third` `0.0`, `2.059614818322321`; `ambience_alt→ambience_third` `0.0`, `.9309488765840295`. Both pass.

The five generic pairs pass under the OR rule; ambience family comparisons pass via centroid alone, with zero duration delta. Their centroid and seam measurements remain lossy/local numeric proxies, not perceived novelty or seamlessness. This Round 37 run does not establish general threshold calibration.

### Prior invalid-probe outcomes

The preserved prior invalid receipt (#30, `--probe-invalid`) records:

- `short_sections`: expected failure, `section count`.
- `corrupt`: expected failure, `decode`.
- `wrong_format`: expected failure, `format`.
- `odd_sections`: expected failure, `section count`.
- `native16_probe`: expected pass.
- `native24_probe`, `stereo48_probe`, `mono441_probe`: expected failure, `format`.

The prior-34 subset retains 13 exit-0 and 21 expected exit-1 outcomes. The new control is the extra expected exit-1; final prior restore remains invocation #35.

## Setup attempts and limits

No Round 37 replay setup failures occurred; every invocation yielded a runner-generated receipt. Wave-one setup reports separately disclose the executor's initial unavailable-SciPy invocation (exit 1), the alt's relative-path helper invocation (exit 1), and the critic's relative-path helper invocation (exit 1). These are setup/path failures, not failed numeric fits; corrected fits succeeded. No wave-one numeric candidate fit was reported as failed; the selected executor pair matches the runner's hashes/measurements. The alternate fit was not used. Round 36's verifier disclosed 34 initial wrapper attempts exiting 127 before runner execution; those prior setup attempts are not part of this replay and are not counted as gate outcomes.

The result only demonstrates that this selected equal-duration scratch pair falls below both arms of the current numeric OR predicate while its individual checks pass. It does not calibrate the threshold universally or establish perceptual/spectral similarity or quality. I wrote only this report and runner-generated receipts under `.shokunin/audio/corpus/live/runs/`; I did not change shared source, LOG, SCORECARD, canonical WAVs, or other reports, and made no commit or push.
