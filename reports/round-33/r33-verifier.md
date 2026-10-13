# Round 33 independent verifier — NON-AUTHOR

## Verdict and scope

I serially ran **31 exact runner invocations** from the repository root: initial normal, then the 29 non-initial commands of the prior Round 32 replay (mixed-pass; 27 prior modes through invalid; prior restore), then one additional normal restore. This yields **10 exit 0, 21 expected exit 1, 0 runner exit 2**. The carried-forward prior-30 subset is exactly replay #1 plus #2–#30 here: **9 exit 0 / 21 exit 1**. Replay #31 is the added final normal restoration. No runner setup failures occurred.

The prior Round 32 verifier's command sequence was 30 commands. This replay deliberately omits its initial normal and appends a separate final normal, while retaining the mixed-pass as #2. So prior30 is #1 + #2–#30; #31 is the extra restore. All commands ran serially and each runner invocation produced a receipt.

Every valid-mode receipt (#1–#28 and #30–#31) contains all **14 canonical measurement entries**, including `ui_third`. In those receipts the new canonical fixture's ordinary checks pass. The expected failing `--probe-failing` mode (#28) still has its intended ambience failures; this is not a `ui_third` failure. The invalid mode (#29) intentionally emits eight invalid-probe rows rather than canonical measurements. Its eight statuses match expectation (listed below).

The new fixture is `ui_third`: 9,600 frames / 0.200 s, 48 kHz mono PCM16; peak `0.375946044921875`, RMS `-22.20695387316763 dBFS`, centroid `966.7216217320357 Hz`, no ordinary failures, SHA-256 `734a0a47077f5b614b5d51d486b88a51940c7d61ecea0878642b60a0103513bc`. The new explicit UI family comparisons are present and pass: `ui`→`ui_third` duration delta `0.08000000000000002` s, centroid-relative delta `0.00018103031409457665` (**duration arm only**); `ui_alt`→`ui_third` `0.04000000000000001` s / `0.3207185389302337` (**both arms**). These numeric OR outcomes are not perceptual distinctness.

Initial and restored normal receipts (#1/#30/#31) match exactly after removing each measurement `path`, including thresholds, measurements, generic comparisons, and UI-family comparisons. The existing generic five `_alt` comparisons and `.020 s OR .10` thresholds are unchanged. The 13 pre-existing canonical WAV hashes all match `HEAD` `b8e3e5c8de6ee0f82d87f6187437991b73b56073`; the new fixture hash is as above. Old canonical measurements in the replay normal match the prior Round 32 normal receipt exactly except for path fields; existing canonical metrics did not change.

The prior-30 outcomes and eight invalid statuses are reproduced below with exact commands, exits, receipts, and failure details. This is **analytical fixture coverage only**—not listening, sound quality, production readiness, rights, engine, publishing, or promotion evidence.

## Exact commands, exits, receipts, and failures

| # | Exact command | Exit | Receipt (repository-relative) | Failure / invalid statuses |
|---:|---|---:|---|---|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T031508389221Z-normal/measurements.json` | none |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-mixed-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T031509315186Z-ui-mixed-pass/measurements.json` | none |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-joint-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T031510244281Z-ui-joint-below/measurements.json` | ui_joint_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-forward` | 1 | `.shokunin/audio/corpus/live/runs/20261013T031511170797Z-ui-orientation-forward/measurements.json` | ui_orientation_forward_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-reverse` | 0 | `.shokunin/audio/corpus/live/runs/20261013T031512100631Z-ui-orientation-reverse/measurements.json` | none |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T031513026066Z-ui-lower-centroid-below/measurements.json` | ui_lower_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T031513959289Z-ui-lower-centroid-above/measurements.json` | none |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T031514889230Z-ui-centroid-below/measurements.json` | ui_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T031515820656Z-ui-centroid-above/measurements.json` | none |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T031516753960Z-ui-duration-below/measurements.json` | ui_duration_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 | `.shokunin/audio/corpus/live/runs/20261013T031517687442Z-ui-duration-at/measurements.json` | none |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 | `.shokunin/audio/corpus/live/runs/20261013T031518613528Z-ui-clone/measurements.json` | ui_clone_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T031520002936Z-layer-third-join-edge-pass/measurements.json` | none |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T031520916286Z-layer-third-join-edge-fail/measurements.json` | join200_edgefail_probe: sections: internal join adjacent sample gap > .03 full scale |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T031521829466Z-layer-third-join/measurements.json` | join200_probe: sections: internal join adjacent sample gap > .03 full scale |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T031522748810Z-layer-third-slope-edge-pass/measurements.json` | none |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T031523653646Z-layer-third-slope-edge-fail/measurements.json` | edgefail_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T031524568559Z-layer-third-slope/measurements.json` | slope200_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T031525477206Z-layer-alt-reverse/measurements.json` | reverse180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T031526383218Z-layer-alt-slope/measurements.json` | slope180_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T031527290651Z-layer-alt-join/measurements.json` | join180_probe: sections: internal join adjacent sample gap > .03 full scale |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T031528189641Z-layer-alt-flat/measurements.json` | flat180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T031529120792Z-layer-slope/measurements.json` | layer_slope_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T031530016208Z-layer-join/measurements.json` | join_probe: sections: internal join adjacent sample gap > .03 full scale |
| 25 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T031530971419Z-flat/measurements.json` | flat30_probe: sections: 30 Hz component amplitude contrast < 6 dB or invalid |
| 26 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T031531892845Z-layer-flat/measurements.json` | flat120_probe: sections: 120 Hz component amplitude contrast < 6 dB or invalid |
| 27 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T031532789471Z-slope/measurements.json` | slope_probe: loop seam: slope mismatch > .001 full scale per sample |
| 28 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261013T031533639924Z-failing/measurements.json` | ambience: spectrum: centroid outside fixture band |
| 29 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261013T031533982443Z-invalid/measurements.json` | 8 invalid rows: short_sections=expected_failure(section count); corrupt=expected_failure(decode); wrong_format=expected_failure(format); odd_sections=expected_failure(section count); native16_probe=expected_pass; native24_probe=expected_failure(format); stereo48_probe=expected_failure(format); mono441_probe=expected_failure(format) |
| 30 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T031534824288Z-normal/measurements.json` | none |
| 31 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T031542838399Z-normal/measurements.json` | none |

## Preserved invariants and comparisons

The five pre-existing generic `_alt` pair records in initial normal #1 (also equal in #30 and #31) remain:

| Pair | Duration delta (s) | Relative centroid delta | Outcome |
|---|---:|---:|---|
| `ui_alt` | 0.04000000000000001 | 0.47187731004956435 | pass |
| `impact_alt` | 0.0 | 0.9563048992406177 | pass |
| `movement_alt` | 0.12 | 0.007518618572621081 | pass |
| `ambience_alt` | 0.0 | 0.5845136323520758 | pass |
| `stem_layer_alt` | 0.0 | 0.46179931396667484 | pass |

Threshold objects are identical across all 31 receipt payloads: rate 48,000 Hz; duration tolerance 0.001 s; peak `<.95`; RMS `>.001`; loop endpoint `<.03`; loop slope `<.001`; section contrast `>=6 dB`; join delta `<.03`; join slope `<.001`; section amplitude `>=.01`; section RMS `>=.001`; distinctness duration `>=.020 s OR` baseline-relative centroid `>=.10`. No threshold was changed.

All 13 pre-existing canonical artifact digests match the working-tree files and `HEAD`:

| Canonical artifact | SHA-256 |
|---|---|
| ambience.wav | b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198 |
| ambience_alt.wav | 2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc |
| impact.wav | a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc |
| impact_alt.wav | a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6 |
| movement.wav | 23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d |
| movement_alt.wav | 51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639 |
| stem.wav | fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0 |
| stem_layer.wav | ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9 |
| stem_layer_alt.wav | 74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9 |
| stem_layer_third.wav | 3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445 |
| stem_sections.wav | 49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702 |
| ui.wav | 4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9 |
| ui_alt.wav | 166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f |

Invalid probe #29 statuses: `short_sections` expected_failure (section count); `corrupt` expected_failure (decode); `wrong_format` expected_failure (format); `odd_sections` expected_failure (section count); `native16_probe` expected_pass; `native24_probe` expected_failure (format); `stereo48_probe` expected_failure (format); `mono441_probe` expected_failure (format).

No setup failures occurred during this replay. The historical Round 32 verifier documents 30 initial mistyped-script-path attempts (exit 2, no receipts), excluded from its corrected replay; those were not repeated here and are not gate outcomes.

## Boundary and allowed writes

I read the round-33 wave-one reports and prior Round 32 verifier before replay. I wrote only this report and runner-generated receipts under `corpus/live/runs/`; no source, LOG, SCORECARD, canonical artifact, or other report was edited. No commits or pushes. No audition or claim about sound quality, production suitability, rights, engine behavior, publishing, or promotion.
