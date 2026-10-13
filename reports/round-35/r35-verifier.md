# Round 35 independent verifier — NON-AUTHOR

## Verdict and scope

**Replay verified; movement fixture's analytic checks pass.** I serially ran 33 invocations: initial normal (#1), the prior Round 34 32-run sequence without its duplicate initial normal (#2–#32: mixed, joint, orientation, lower/upper centroid, duration, clone, legacy section/loop probes and invalid run, followed by three normal restores), then an extra final normal (#33). Counts: **12 exit 0, 21 expected exit 1, 0 other exits or runner setup failures**. The prior32 subset (#1–#32) is **11 exit 0 / 21 exit 1**.

All valid-mode receipts (#1–#28 and #30–#33) contain **16 canonical measurements**. `movement_third` passes ordinary checks: **0.30 s / 14,400 frames, 48 kHz mono PCM16**; peak `0.489501953125` FS, RMS `-14.025186267550422` dBFS, centroid `4553.583280111138` Hz; no ordinary failures; SHA-256 `0e5f815e1987e13646170571e1f1e977b25e3566d90ebcca558c72ed07851d44`.

Explicit `movement_family_comparisons` pass both arms for both pairs: `movement`→`movement_third`, duration delta `0.06` s / relative centroid delta `0.6184516010427937`; `movement_alt`→`movement_third`, `0.06` s / `0.6212989100908565`. **Duration alone passes** the existing OR predicate for both, so these numeric comparisons do not establish perceived or spectral-distribution novelty.

All **15** pre-existing canonical WAVs retain their exact SHA-256 values versus clean-before `HEAD` `56f2b0f8d244966c13ebfd7b28d521e3825dd3aa`; their initial-normal measurement records equal the Round 34 pre-integration normal receipt. Five generic `_alt` records and the UI and impact family comparison records equal that prior normal receipt. Threshold scalar values are unchanged (48 kHz; duration tolerance .001 s; peak <.95; RMS >.001; loop endpoint <.03; loop slope <.001; section contrast ≥6 dB; join delta <.03; join slope <.001; section amplitude ≥.01; section RMS ≥.001; distinctness duration ≥.020 s OR baseline-relative centroid ≥.10). The centroid-band map only adds the new movement-third band. Invalid receipt #29 has no threshold or canonical measurement set. Normal receipts #1/#30/#31/#32/#33 match after excluding each measurement `path`.

This establishes **analytic fixture coverage only**, not perceptual/spectral-distribution novelty or sound quality. It is not production, rights, engine, publishing, or promotion evidence.

## Exact serial commands, exits, receipts, and failure kinds

Expected exit-1 probe outcomes are fixture failures, not runner setup failures. Exact invalid-probe statuses are enumerated above and in receipt #29.

| # | Exact command | Exit | Receipt (repo-relative) | Failure kind / invalid statuses |
|---:|---|---:|---|---|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T034131375782Z-normal/measurements.json` | none |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-mixed-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T034132404744Z-ui-mixed-pass/measurements.json` | none |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-joint-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T034133431467Z-ui-joint-below/measurements.json` | ui_joint_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-forward` | 1 | `.shokunin/audio/corpus/live/runs/20261013T034134459206Z-ui-orientation-forward/measurements.json` | ui_orientation_forward_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-reverse` | 0 | `.shokunin/audio/corpus/live/runs/20261013T034135484581Z-ui-orientation-reverse/measurements.json` | none |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T034136502870Z-ui-lower-centroid-below/measurements.json` | ui_lower_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T034137524619Z-ui-lower-centroid-above/measurements.json` | none |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T034138549565Z-ui-centroid-below/measurements.json` | ui_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T034139579531Z-ui-centroid-above/measurements.json` | none |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T034140603912Z-ui-duration-below/measurements.json` | ui_duration_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 | `.shokunin/audio/corpus/live/runs/20261013T034141636383Z-ui-duration-at/measurements.json` | none |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 | `.shokunin/audio/corpus/live/runs/20261013T034142671109Z-ui-clone/measurements.json` | ui_clone_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T034143700008Z-layer-third-join-edge-pass/measurements.json` | none |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T034144718548Z-layer-third-join-edge-fail/measurements.json` | join200_edgefail_probe: sections: internal join adjacent sample gap > .03 full scale |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T034145741473Z-layer-third-join/measurements.json` | join200_probe: sections: internal join adjacent sample gap > .03 full scale |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T034146757412Z-layer-third-slope-edge-pass/measurements.json` | none |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T034147763453Z-layer-third-slope-edge-fail/measurements.json` | edgefail_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T034148769829Z-layer-third-slope/measurements.json` | slope200_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T034149789816Z-layer-alt-reverse/measurements.json` | reverse180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T034150796343Z-layer-alt-slope/measurements.json` | slope180_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T034151806698Z-layer-alt-join/measurements.json` | join180_probe: sections: internal join adjacent sample gap > .03 full scale |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T034152830818Z-layer-alt-flat/measurements.json` | flat180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T034153859264Z-layer-slope/measurements.json` | layer_slope_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T034154871544Z-layer-join/measurements.json` | join_probe: sections: internal join adjacent sample gap > .03 full scale |
| 25 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T034155898168Z-flat/measurements.json` | flat30_probe: sections: 30 Hz component amplitude contrast < 6 dB or invalid |
| 26 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T034156908736Z-layer-flat/measurements.json` | flat120_probe: sections: 120 Hz component amplitude contrast < 6 dB or invalid |
| 27 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T034157915004Z-slope/measurements.json` | slope_probe: loop seam: slope mismatch > .001 full scale per sample |
| 28 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261013T034158866699Z-failing/measurements.json` | ambience: spectrum: centroid outside fixture band / loop seam: endpoint jump > .03 full scale |
| 29 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261013T034159221919Z-invalid/measurements.json` | invalid statuses: short_sections=expected_failure(section count), corrupt=expected_failure(decode), wrong_format=expected_failure(format), odd_sections=expected_failure(section count), native16_probe=expected_pass, native24_probe=expected_failure(format), stereo48_probe=expected_failure(format), mono441_probe=expected_failure(format) |
| 30 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T034200170405Z-normal/measurements.json` | none |
| 31 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T034201108194Z-normal/measurements.json` | none |
| 32 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T034202060745Z-normal/measurements.json` | none |
| 33 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T034217598670Z-normal/measurements.json` | none |

## Prior canonical SHA-256 invariants

The following 15 canonical WAVs were compared with `HEAD` at declared clean-before `56f2b0f8d244966c13ebfd7b28d521e3825dd3aa`; all match current artifact bytes. Their ordinary metric records also match the Round 34 pre-integration normal receipt.

| Canonical WAV | SHA-256 |
|---|---|
| `ambience.wav` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` |
| `ambience_alt.wav` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` |
| `impact.wav` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` |
| `impact_alt.wav` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` |
| `impact_third.wav` | `d14376241f409f07edde30fbcef86b5f060ff36f731b7578fd9934d1dc1b39bf` |
| `movement.wav` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` |
| `movement_alt.wav` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` |
| `stem.wav` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` |
| `stem_layer.wav` | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` |
| `stem_layer_alt.wav` | `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` |
| `stem_layer_third.wav` | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` |
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` |
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` |
| `ui_third.wav` | `734a0a47077f5b614b5d51d486b88a51940c7d61ecea0878642b60a0103513bc` |

The added `movement_third.wav` is the 16th canonical item and has SHA-256 `0e5f815e1987e13646170571e1f1e977b25e3566d90ebcca558c72ed07851d44`. Existing five generic `_alt` comparison records, explicit UI and impact family comparisons, and threshold constants are preserved; explicit movement-family comparisons are additive. The invalid receipt's eight statuses: `short_sections=expected_failure(section count)`, `corrupt=expected_failure(decode)`, `wrong_format=expected_failure(format)`, `odd_sections=expected_failure(section count)`, `native16_probe=expected_pass`, `native24_probe=expected_failure(format)`, `stereo48_probe=expected_failure(format)`, `mono441_probe=expected_failure(format)`.

## Setup failures and allowed writes

**Verifier replay setup failures: none.** Separate wave-one setup issues documented in the reports: executor's malformed shell invocation exited 127 before candidate execution; alt measurement first attempt exited 1 on a relative-path setup error; reviewer first two helper calls exited 1 (wrong argument type and relative-path resolution). Corrected candidate measurements succeeded; these are not candidate-fit failures. The reports additionally record a pre-shell REPL quoting syntax error (no command/exit) and scribe's missing report-directory `find` exit 1 (inspection only). They are not replay failures or evidence against the candidate. See `r35-executor.md`, `r35-alt.md`, `r35-reviewer.md`, and `r35-scribe.md`.

I read the Round 35 wave-one reports, Round 34 verifier, and runner receipts. I wrote only this verifier report and runner-generated receipts under `.shokunin/audio/corpus/live/runs/`; no shared source, LOG, SCORECARD, canonical artifact, or other report was edited. No commits or pushes.
