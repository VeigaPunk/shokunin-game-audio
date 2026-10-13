# Round 34 independent verifier — NON-AUTHOR

## Verdict and scope

**Replay verified; the impact fixture's analytic checks pass.** I serially ran 32 exact runner invocations: initial normal (#1), the prior Round 33 sequence with its initial normal omitted (#2–#31: mixed-pass, remaining probes including invalid, and two prior restores), then an extra final normal (#32). Counts: **11 exit 0, 21 expected exit 1, 0 runner exit 2**. The carried-forward prior31 subset is #1–#31: **10 exit 0 / 21 exit 1**. No runner setup failures occurred.

Every valid-mode receipt (#1–#28 and #30–#32) has **15 canonical measurements**. `impact_third` passes ordinary checks: 0.40 s / 19,200 frames, 48 kHz mono PCM16; peak 0.45611572265625 FS, RMS −20.84958464133168 dBFS, centroid 6838.143302962279 Hz, no ordinary failures; SHA-256 `d14376241f409f07edde30fbcef86b5f060ff36f731b7578fd9934d1dc1b39bf`.

The explicit `impact_family_comparisons` records pass both arms for both pairs: `impact`→`impact_third`, duration delta `0.08000000000000002` s / relative centroid delta `0.36935690461299725`; `impact_alt`→`impact_third`, `0.08000000000000002` s / `13.432810187572105`. **Duration alone would pass** the existing OR distinctness predicate, so these numeric comparisons do not establish perceived distinction.

The 14 pre-existing canonical WAVs retain their exact SHA-256 values against clean-before `HEAD` `d6bfc6ea374e634fd6eb1322030d014612ff98cb`; their normal-receipt metrics also match the Round 34 author normal receipt exactly. The five generic `_alt` comparison records, `ui_family_comparisons`, and threshold values are unchanged from that pre-integration normal receipt. Thresholds remain: rate 48,000 Hz; duration tolerance .001 s; peak <.95; RMS >.001; loop endpoint <.03; loop slope <.001; section contrast ≥6 dB; join delta <.03; join slope <.001; section amplitude ≥.01; section RMS ≥.001; distinctness duration ≥.020 s OR baseline-relative centroid ≥.10. Initial normal #1 and prior restores #30/#31 and extra restore #32 match after excluding each measurement `path`.

This is **analytic fixture coverage only**, and confirms neither perceptual/spectral-distribution novelty nor sound quality. It is not production, rights, engine, publishing, or promotion evidence.

## Exact commands, exits, receipts, and failures

| # | Exact command | Exit | Receipt (repository-relative) | Failure / invalid statuses |
|---:|---|---:|---|---|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T032822674797Z-normal/measurements.json` | none |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-mixed-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T032823671946Z-ui-mixed-pass/measurements.json` | none |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-joint-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T032824643445Z-ui-joint-below/measurements.json` | ui_joint_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-forward` | 1 | `.shokunin/audio/corpus/live/runs/20261013T032825626184Z-ui-orientation-forward/measurements.json` | ui_orientation_forward_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-reverse` | 0 | `.shokunin/audio/corpus/live/runs/20261013T032826603162Z-ui-orientation-reverse/measurements.json` | none |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T032827574237Z-ui-lower-centroid-below/measurements.json` | ui_lower_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T032828546563Z-ui-lower-centroid-above/measurements.json` | none |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T032829514942Z-ui-centroid-below/measurements.json` | ui_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T032830494137Z-ui-centroid-above/measurements.json` | none |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T032831459762Z-ui-duration-below/measurements.json` | ui_duration_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 | `.shokunin/audio/corpus/live/runs/20261013T032832423908Z-ui-duration-at/measurements.json` | none |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 | `.shokunin/audio/corpus/live/runs/20261013T032833383166Z-ui-clone/measurements.json` | ui_clone_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T032834338201Z-layer-third-join-edge-pass/measurements.json` | none |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T032835283316Z-layer-third-join-edge-fail/measurements.json` | join200_edgefail_probe: sections: internal join adjacent sample gap > .03 full scale |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T032836243071Z-layer-third-join/measurements.json` | join200_probe: sections: internal join adjacent sample gap > .03 full scale |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T032837202616Z-layer-third-slope-edge-pass/measurements.json` | none |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T032838156554Z-layer-third-slope-edge-fail/measurements.json` | edgefail_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T032839115142Z-layer-third-slope/measurements.json` | slope200_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T032840064884Z-layer-alt-reverse/measurements.json` | reverse180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T032841030462Z-layer-alt-slope/measurements.json` | slope180_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T032842003140Z-layer-alt-join/measurements.json` | join180_probe: sections: internal join adjacent sample gap > .03 full scale |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T032842963044Z-layer-alt-flat/measurements.json` | flat180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T032843930411Z-layer-slope/measurements.json` | layer_slope_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T032844906429Z-layer-join/measurements.json` | join_probe: sections: internal join adjacent sample gap > .03 full scale |
| 25 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T032845874158Z-flat/measurements.json` | flat30_probe: sections: 30 Hz component amplitude contrast < 6 dB or invalid |
| 26 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T032846840668Z-layer-flat/measurements.json` | flat120_probe: sections: 120 Hz component amplitude contrast < 6 dB or invalid |
| 27 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T032847794002Z-slope/measurements.json` | slope_probe: loop seam: slope mismatch > .001 full scale per sample |
| 28 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261013T032848687602Z-failing/measurements.json` | ambience: spectrum: centroid outside fixture band | loop seam: endpoint jump > .03 full scale |
| 29 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261013T032849025031Z-invalid/measurements.json` | invalid statuses: short_sections=expected_failure(section count), corrupt=expected_failure(decode), wrong_format=expected_failure(format), odd_sections=expected_failure(section count), native16_probe=expected_pass, native24_probe=expected_failure(format), stereo48_probe=expected_failure(format), mono441_probe=expected_failure(format) |
| 30 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T032849918068Z-normal/measurements.json` | none |
| 31 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T032850816511Z-normal/measurements.json` | none |
| 32 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T032851712243Z-normal/measurements.json` | none |

## Baseline hashes and invariants

The following 14 canonical WAV hashes were independently read from `HEAD` at the declared clean-before commit and equal the current files:

| Canonical WAV | SHA-256 |
|---|---|
| `ambience.wav` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` |
| `ambience_alt.wav` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` |
| `impact.wav` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` |
| `impact_alt.wav` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` |
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

The newly added `impact_third.wav` has SHA-256 `d14376241f409f07edde30fbcef86b5f060ff36f731b7578fd9934d1dc1b39bf`. Canonical count is 15. All prior 14 SHA values match the clean-before baseline; all 14 old metric records in the initial normal receipt match the Round 34 author normal receipt exactly. Five generic `_alt` records and explicit UI family comparisons equal the pre-integration normal receipt; no generic variant behavior was changed. All valid receipts carry the same thresholds; invalid receipt #29 has no threshold object or canonical measurement set.

Invalid-probe #29 statuses (all matched expected): `short_sections` expected_failure (section count); `corrupt` expected_failure (decode); `wrong_format` expected_failure (format); `odd_sections` expected_failure (section count); `native16_probe` expected_pass (none); `native24_probe` expected_failure (format); `stereo48_probe` expected_failure (format); `mono441_probe` expected_failure (format).

## Setup failures and allowed writes

There were **no verifier setup failures**. Wave-one setup failures, separate from this verifier replay: executor helper attempt 1 exited 1 (`AttributeError: 'str' object has no attribute 'relative_to'`); attempt 2 exited 1 (`ValueError` because relative paths were outside the helper's corpus `ROOT`). Both were setup/path errors with no measurement result and are documented in `r34-executor.md`; its corrected helper succeeded (exit 0). The `r34-alt.md` scratch fit command exited 0; it reports no failed setup attempt. These are not verifier replay outcomes. The 21 exit-1 results above are expected probe outcomes; #28 is the intended failing ambience probe, and #29 is the intended invalid-probe run.

I read the Round 34 wave-one reports, Round 33 verifier, and runner output/receipts. I wrote only this report and runner-generated receipts under `.shokunin/audio/corpus/live/runs/`; no shared source, LOG, SCORECARD, canonical artifact, or other report was edited. No commits or pushes.
