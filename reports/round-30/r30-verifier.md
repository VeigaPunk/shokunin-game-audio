# Round 30 independent verifier — NON-AUTHOR

## Verdict

**The integrated runner verifies baseline-denominator orientation sensitivity at these two points, narrowly.** I serially replayed 28 runner invocations: initial normal; `--probe-ui-orientation-forward`; `--probe-ui-orientation-reverse`; then the prior 26-mode historical subset excluding its duplicated initial normal (prior #1 and #4–#28); and normal restore. The forward invocation exits 1 solely on its alternate distinctness check; reverse exits 0. Both orientation pairs satisfy the ordinary checks under the same unchanged canonical UI `.120 s` specification: 5760 frames, 48 kHz, mono PCM16, no individual ordinary-check failures; duration delta is 0 in both.

The shared waveform bytes are exactly swapped by role. Forward base equals reverse alternate SHA-256 `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9`; forward alternate equals reverse base SHA-256 `6e626b9b5b177cd6f7ba986758b12ec612cf003f9947bd170b766f1652d9bac2`. Their corresponding reversed files hash identically as well. The receipt centroids are forward base 966.8966593379727 Hz and forward alternate 871.155504521436 Hz. Applying the existing baseline-denominator formula:

- Forward: `abs(871.155504521436 - 966.8966593379727) / 966.8966593379727 = 0.09901901500217196` (< .10), with duration delta 0; exit 1 solely because distinctness fails.
- Reverse: `abs(966.8966593379727 - 871.155504521436) / 871.155504521436 = 0.10990133715464667` (>= .10), with duration delta 0; exit 0.

The comparator remains absolute difference divided by the baseline, and existing distinctness remains duration delta `>= .020 s OR` relative centroid delta `>= .10`; receipt threshold objects are identical and unchanged. This demonstrates numeric orientation sensitivity caused by the denominator for this byte-swapped pair, not a normative symmetry expectation or exact-threshold claim.

## Serial replay (28 invocations)

Commands ran serially from repository root. Receipt paths are relative to repository root. Exit 1 is an expected gate rejection except where a setup error is separately called out below.

| # | Exact command | Exit | Receipt | Failure kind |
|---:|---|---:|---|---|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T023817208830Z-normal/measurements.json` | none |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-forward` | 1 | `.shokunin/audio/corpus/live/runs/20261013T023818100104Z-ui-orientation-forward/measurements.json` | ui_orientation_forward_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-reverse` | 0 | `.shokunin/audio/corpus/live/runs/20261013T023818983830Z-ui-orientation-reverse/measurements.json` | none |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T023819872317Z-ui-lower-centroid-below/measurements.json` | ui_lower_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T023820766429Z-ui-lower-centroid-above/measurements.json` | none |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T023821652956Z-ui-centroid-below/measurements.json` | ui_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T023822545215Z-ui-centroid-above/measurements.json` | none |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T023823453358Z-ui-duration-below/measurements.json` | ui_duration_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 | `.shokunin/audio/corpus/live/runs/20261013T023824382953Z-ui-duration-at/measurements.json` | none |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 | `.shokunin/audio/corpus/live/runs/20261013T023825298565Z-ui-clone/measurements.json` | ui_clone_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T023826220796Z-layer-third-join-edge-pass/measurements.json` | none |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T023827104501Z-layer-third-join-edge-fail/measurements.json` | join200_edgefail_probe: sections: internal join adjacent sample gap > .03 full scale |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T023827997999Z-layer-third-join/measurements.json` | join200_probe: sections: internal join adjacent sample gap > .03 full scale |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T023828874661Z-layer-third-slope-edge-pass/measurements.json` | none |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T023829749758Z-layer-third-slope-edge-fail/measurements.json` | edgefail_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T023830630642Z-layer-third-slope/measurements.json` | slope200_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T023831513852Z-layer-alt-reverse/measurements.json` | reverse180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T023832382346Z-layer-alt-slope/measurements.json` | slope180_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T023833262027Z-layer-alt-join/measurements.json` | join180_probe: sections: internal join adjacent sample gap > .03 full scale |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T023834144275Z-layer-alt-flat/measurements.json` | flat180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T023835011824Z-layer-slope/measurements.json` | layer_slope_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T023835887834Z-layer-join/measurements.json` | join_probe: sections: internal join adjacent sample gap > .03 full scale |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T023836763546Z-flat/measurements.json` | flat30_probe: sections: 30 Hz component amplitude contrast < 6 dB or invalid |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T023837632134Z-layer-flat/measurements.json` | flat120_probe: sections: 120 Hz component amplitude contrast < 6 dB or invalid |
| 25 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T023838487241Z-slope/measurements.json` | slope_probe: loop seam: slope mismatch > .001 full scale per sample |
| 26 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261013T023839303723Z-failing/measurements.json` | ambience: spectrum: centroid outside fixture band, loop seam: endpoint jump > .03 full scale |
| 27 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261013T023839657513Z-invalid/measurements.json` | short_sections: section count; corrupt: decode; wrong_format: format; odd_sections: section count; native16_probe: expected_pass; native24_probe: format; stereo48_probe: format; mono441_probe: format |
| 28 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T023840471149Z-normal/measurements.json` | none |

Totals: **28 runner invocations: 8 exit 0, 20 exit 1, no exit 2.** Historical prior-26 subset is this replay's #1 plus #4–#28: **7 exit 0, 19 exit 1**, matching historical outcomes. The orientation probes are #2–#3 and excluded from that subset. In #27, all eight invalid-control statuses matched expectations: `short_sections` expected_failure (section count), `corrupt` expected_failure (decode), `wrong_format` expected_failure (format), `odd_sections` expected_failure (section count), `native16_probe` expected_pass, `native24_probe` expected_failure (format), `stereo48_probe` expected_failure (format), and `mono441_probe` expected_failure (format).

## Orientation pair and preservation checks

Forward receipt `.shokunin/audio/corpus/live/runs/20261013T023818100104Z-ui-orientation-forward/measurements.json` and reverse receipt `.shokunin/audio/corpus/live/runs/20261013T023818983830Z-ui-orientation-reverse/measurements.json` record:

| Mode member | Centroid (Hz) | Duration | Ordinary checks | SHA-256 |
|---|---:|---:|---|---|
| forward base | 966.8966593379727 | .120 s | pass | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` |
| forward alternate | 871.155504521436 | .120 s | pass | `6e626b9b5b177cd6f7ba986758b12ec612cf003f9947bd170b766f1652d9bac2` |
| reverse base | 871.155504521436 | .120 s | pass | `6e626b9b5b177cd6f7ba986758b12ec612cf003f9947bd170b766f1652d9bac2` |
| reverse alternate | 966.8966593379727 | .120 s | pass | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` |

All 13 canonical WAV SHA-256 hashes match `HEAD` `6a3696822741388d862243745f653a76eec21d1f`:
- `ambience.wav` `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198`
- `ambience_alt.wav` `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc`
- `impact.wav` `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc`
- `impact_alt.wav` `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6`
- `movement.wav` `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d`
- `movement_alt.wav` `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639`
- `stem.wav` `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0`
- `stem_layer.wav` `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9`
- `stem_layer_alt.wav` `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9`
- `stem_layer_third.wav` `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445`
- `stem_sections.wav` `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702`
- `ui.wav` `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9`
- `ui_alt.wav` `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f`

Five pre-existing alternate comparisons remain present and pass in initial and restored normal receipts: `ui_alt` duration `.04000000000000001`, centroid relative `.47187731004956435`; `impact_alt` 0 / `.9563048992406177`; `movement_alt` `.12` / `.007518618572621081`; `ambience_alt` 0 / `.5845136323520758`; `stem_layer_alt` 0 / `.46179931396667484`. Threshold objects are identical across orientation and normal receipts, including distinctness duration `.02` and centroid `.1`. Initial and restored normal receipts have identical distinctness results; measurement `path` fields are the only expected differences. Prior-26 outcomes, eight invalid statuses, five variants, and 13 canonical hashes are preserved.

## Setup errors, scope, and limits

Before the successful serial replay, I mistakenly passed each whole command string as a single executable to the shell wrapper. This produced 28 exit-127 “No such file” setup errors and no receipts; I then invoked the commands correctly and completed the 28 runner executions above. The erroneous wrapper attempts are **setup failures, not runner invocations or gate evidence**, and excluded from the counts.

This is a numeric spectral-centroid proxy and baseline-denominator orientation demonstration only. It establishes no normative symmetry, exact equality, smoothness, perceptual or auditory property, rights clearance, engine/runtime behavior, publish readiness, or promotion. I wrote only `.shokunin/audio/reports/round-30/r30-verifier.md`; all additional new artifacts from this replay are runner-generated receipts under `.shokunin/audio/corpus/live/runs/`. I did not edit shared source, LOG, SCORECARD, canonical assets, or another report, and did not commit or push.
