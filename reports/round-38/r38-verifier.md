# Round 38 independent verifier — NON-AUTHOR

## Verdict and scope

**The declared local positive control is independently reproduced.** I ran the requested 36 runner invocations serially: initial normal (#1), new `--probe-ambience-centroid-above` positive (#2), then the prior Round 37 sequence with its duplicate initial normal removed (#3–#36). Counts: **14 exit 0 and 22 expected fixture-validation exit 1; zero replay runner setup errors**. The prior-35 subset (#1 and #3–#36) is **13 exit 0 / 22 expected exit 1**. The final prior restore is #36. Prior-35 outcomes, all eight invalid statuses and ordering are preserved.

The new positive receipt #2 has **17 canonical plus two scratch measurements**. The scratch pair is 2.0 s / 96,000 frames / 48 kHz mono PCM16. Baseline SHA-256: `04d8d334553ecb0c155a4be37397edda8f01cfbe992df4bd2e9b3e474d1189e0`; variant SHA-256: `7bd6ae805a6a5ff2c15ba14470ba1d312c40768c97c1704629382ed76292bd77`. Both ordinary and loop/seam failure lists are empty. Project-measured duration delta is exactly **0.0 s**; centroids are **91.03372963003302 Hz** and **81.6243985667145 Hz**, baseline-relative delta **0.10336093117966988** (strictly > .10 and < .13). Existing generic `_alt` comparison `ambience_above_alt` passes (`true`); no failures; command exit **0**. The prior Round 37 negative has duration delta 0.0, centroid-relative delta **0.06585562259644766**, and exits 1 solely for generic distinctness. This gives one local positive polarity alongside one local negative.

I compared the 17 canonical WAVs with their Git blobs at clean-before `HEAD` `c713fb62a195da947cc3f06e6b0f3a101afd0f23`: every SHA matches. Their metrics and measurements match the prior Round 37 initial-normal receipt. The five generic `_alt` comparisons, all UI/impact/movement/ambience family comparisons, thresholds, and section records also match. Normal #1 and final normal #36 are equal on all receipt fields except generated measurement paths.

This supports **one local positive polarity beside one local negative only**; it is not exact-boundary or universal threshold calibration, nor a perception/spectral-similarity, quality, production, rights, engine, publishing, or promotion claim.

## Exact serial commands, exits, receipts, and failure kinds

All paths are repository-relative. Exit-1 runs are expected fixture-validation outcomes, not replay setup failures. Failure kinds below are the runner-reported receipt failures. The prior-35 subset is exactly #1 plus #3–#36.

| # | Exact command | Exit | Receipt | Failure kind / invalid statuses |
|---:|---|---:|---|---|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T042523680425Z-normal/measurements.json` | none |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T042524821658Z-ambience-centroid-above/measurements.json` | none |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T042525960066Z-ambience-centroid-below/measurements.json` | ambience_probe_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-mixed-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T042527048375Z-ui-mixed-pass/measurements.json` | none |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-joint-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T042528191101Z-ui-joint-below/measurements.json` | ui_joint_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-forward` | 1 | `.shokunin/audio/corpus/live/runs/20261013T042529282612Z-ui-orientation-forward/measurements.json` | ui_orientation_forward_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-reverse` | 0 | `.shokunin/audio/corpus/live/runs/20261013T042530368847Z-ui-orientation-reverse/measurements.json` | none |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T042531445331Z-ui-lower-centroid-below/measurements.json` | ui_lower_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T042532524485Z-ui-lower-centroid-above/measurements.json` | none |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T042533673532Z-ui-centroid-below/measurements.json` | ui_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T042534762998Z-ui-centroid-above/measurements.json` | none |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T042535860777Z-ui-duration-below/measurements.json` | ui_duration_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 | `.shokunin/audio/corpus/live/runs/20261013T042536938045Z-ui-duration-at/measurements.json` | none |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 | `.shokunin/audio/corpus/live/runs/20261013T042538087098Z-ui-clone/measurements.json` | ui_clone_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T042539145240Z-layer-third-join-edge-pass/measurements.json` | none |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T042540209077Z-layer-third-join-edge-fail/measurements.json` | join200_edgefail_probe: sections: internal join adjacent sample gap > .03 full scale |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T042541275549Z-layer-third-join/measurements.json` | join200_probe: sections: internal join adjacent sample gap > .03 full scale |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T042542333258Z-layer-third-slope-edge-pass/measurements.json` | none |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T042543396549Z-layer-third-slope-edge-fail/measurements.json` | edgefail_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T042544451037Z-layer-third-slope/measurements.json` | slope200_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T042545541534Z-layer-alt-reverse/measurements.json` | reverse180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T042546593658Z-layer-alt-slope/measurements.json` | slope180_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T042547684294Z-layer-alt-join/measurements.json` | join180_probe: sections: internal join adjacent sample gap > .03 full scale |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T042548761160Z-layer-alt-flat/measurements.json` | flat180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 25 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T042549821880Z-layer-slope/measurements.json` | layer_slope_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 26 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T042550907672Z-layer-join/measurements.json` | join_probe: sections: internal join adjacent sample gap > .03 full scale |
| 27 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T042551989672Z-flat/measurements.json` | flat30_probe: sections: 30 Hz component amplitude contrast < 6 dB or invalid |
| 28 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T042553072090Z-layer-flat/measurements.json` | flat120_probe: sections: 120 Hz component amplitude contrast < 6 dB or invalid |
| 29 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T042554120827Z-slope/measurements.json` | slope_probe: loop seam: slope mismatch > .001 full scale per sample |
| 30 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261013T042555128269Z-failing/measurements.json` | ambience: spectrum: centroid outside fixture band, loop seam: endpoint jump > .03 full scale |
| 31 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261013T042555475513Z-invalid/measurements.json` | invalid probe statuses: short_sections section count; corrupt decode; wrong_format format; odd_sections section count; native16 expected_pass; native24/stereo48/mono441 format expected_failure |
| 32 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T042556474391Z-normal/measurements.json` | none |
| 33 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T042557474599Z-normal/measurements.json` | none |
| 34 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T042558472868Z-normal/measurements.json` | none |
| 35 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T042559483898Z-normal/measurements.json` | none |
| 36 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T042600483763Z-normal/measurements.json` | none |

## Canonical hashes and measured metrics

Clean-before `HEAD`: `c713fb62a195da947cc3f06e6b0f3a101afd0f23`. I independently compared every canonical WAV's SHA-256 with the Git blob at that revision. All 17 hashes match. Current initial-normal metrics below are copied from receipt #1 and match the prior Round 37 initial-normal receipt; the new run contains the same canonical records.

| Canonical WAV | SHA-256 | Duration (s) | Peak FS | RMS dBFS | Centroid Hz |
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

The unchanged distinctness predicate is duration delta **≥ .020 s OR** baseline-relative centroid delta **≥ .10**. The five generic `_alt` comparisons remain unchanged: `ui→ui_alt` duration `.04000000000000001`, centroid `.47187731004956435`; `impact→impact_alt` `0.0`, `.9563048992406177`; `movement→movement_alt` `.12`, `.007518618572621081`; `ambience→ambience_alt` `0.0`, `.5845136323520758`; `stem_layer→stem_layer_alt` `0.0`, `.46179931396667484`. All pass. All eight family comparisons (UI, impact, movement, ambience, two each) match their baseline values and pass. Thresholds and the section records match the prior baseline. The positive scratch pair adds only its generic `_alt` comparison; it does not change canonical comparisons.

### Prior invalid-probe outcomes

The preserved prior invalid receipt (#31 in this replay, `--probe-invalid`) reports:

- `short_sections`: expected failure, `section count`.
- `corrupt`: expected failure, `decode`.
- `wrong_format`: expected failure, `format`.
- `odd_sections`: expected failure, `section count`.
- `native16_probe`: expected pass.
- `native24_probe`, `stereo48_probe`, `mono441_probe`: expected failure, `format`.

The prior-35 subset retained **13 exit 0 / 22 expected exit 1**, including these eight invalid statuses. #36 is its final normal restore.

## Setup attempts and numeric-fit disclosure

All 36 serial invocations used `python3 .shokunin/audio/corpus/fixtures/measure_audio.py [mode]` and generated runner receipts; no invocation had a setup error. Before the serial replay, my first shell-wrapper attempt quoted the entire command as one executable; it exited **127** before reaching the runner and generated no receipt. I corrected the invocation and excluded that wrapper mistake from the 36 replay outcomes. The Round 38 wave-1 fit notes separately report a corrected relative-helper-path setup error (exit 1); that is setup, not a numeric miss. Numeric fits that missed the declared band are distinct: the `.070` candidate measured `.14123783252085534` (above preferred `<.13`); earlier executor sweeps/candidates likewise missed. The selected positive's runner receipt is authoritative and matches the alt candidate hashes. No failed setup or fit is presented as a runner gate result.

I wrote only `.shokunin/audio/reports/round-38/r38-verifier.md` and the runner-generated receipts under `.shokunin/audio/corpus/live/runs/`. I made no edits to shared source, LOG, SCORECARD, canonical assets, or other reports, and made no commit or push.
