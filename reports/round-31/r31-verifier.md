# Round 31 independent verifier — NON-AUTHOR

## Verdict

**The joint-below control is reproduced narrowly.** I serially replayed 29 invocations: initial normal, `--probe-ui-joint-below`, then the Round 30 verifier's 28-mode sequence with its duplicate initial normal omitted (forward/reverse orientation, two lower-centroid probes, two upper-centroid probes, duration below/at, clone, the 17 legacy probes including invalid, and restored normal). All 29 commands ran successfully as runner invocations; no setup failures occurred. Counts: 8 exit 0 and 21 exit 1, with no exit 2. Of these, the prior-Round-30 28-mode subset (this replay #1 plus #3–#29) has 8 exit 0 / 20 exit 1, matching the Round 30 verifier.

The joint probe exits 1 solely because `ui_joint_below_alt` fails distinctness. The receipt measures base 5,760 frames / 0.120000 s and variant 6,719 frames / 0.139979 s. Measured duration delta is `0.019978999999999997` s (nonzero, `< .020`); baseline-denominator relative centroid delta is `0.09964036511023265` (nonzero, `< .10`). Thus both existing distinctness branches are false and the existing OR rejects. Both files' ordinary checks pass under the variant's separately declared scratch expected duration `6719/48000`; the variant is **not** a canonical `.12 s` UI-duration fixture. The variant failure list contains only `distinctness: duration < .020 s and centroid delta < 10%`; no per-file duration failure masquerades as distinctness.

This supports only this measured numeric joint-below case. It does not isolate causality or establish perception, codec, rights, engine, publish readiness, or promotion.

## Serial replay (29 invocations)

Commands ran serially from repository root. Receipt paths are relative to root. Exit 1 failure kinds are taken from each receipt; no setup failures occurred.

| # | Exact command | Exit | Receipt | Failure kind / invalid statuses |
|---:|---|---:|---|---|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T025122849530Z-normal/measurements.json` | none |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-joint-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T025133084611Z-ui-joint-below/measurements.json` | ui_joint_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-forward` | 1 | `.shokunin/audio/corpus/live/runs/20261013T025133982467Z-ui-orientation-forward/measurements.json` | ui_orientation_forward_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-reverse` | 0 | `.shokunin/audio/corpus/live/runs/20261013T025134905256Z-ui-orientation-reverse/measurements.json` | none |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T025135810336Z-ui-lower-centroid-below/measurements.json` | ui_lower_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T025136723117Z-ui-lower-centroid-above/measurements.json` | none |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T025137629197Z-ui-centroid-below/measurements.json` | ui_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T025138534807Z-ui-centroid-above/measurements.json` | none |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T025139445472Z-ui-duration-below/measurements.json` | ui_duration_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 | `.shokunin/audio/corpus/live/runs/20261013T025140364301Z-ui-duration-at/measurements.json` | none |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 | `.shokunin/audio/corpus/live/runs/20261013T025141279307Z-ui-clone/measurements.json` | ui_clone_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T025142169664Z-layer-third-join-edge-pass/measurements.json` | none |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T025143061821Z-layer-third-join-edge-fail/measurements.json` | join200_edgefail_probe: sections: internal join adjacent sample gap > .03 full scale |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T025143950460Z-layer-third-join/measurements.json` | join200_probe: sections: internal join adjacent sample gap > .03 full scale |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T025144832903Z-layer-third-slope-edge-pass/measurements.json` | none |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T025145714958Z-layer-third-slope-edge-fail/measurements.json` | edgefail_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T025146599717Z-layer-third-slope/measurements.json` | slope200_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T025147483274Z-layer-alt-reverse/measurements.json` | reverse180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T025148376362Z-layer-alt-slope/measurements.json` | slope180_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T025149268449Z-layer-alt-join/measurements.json` | join180_probe: sections: internal join adjacent sample gap > .03 full scale |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T025150144749Z-layer-alt-flat/measurements.json` | flat180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T025151012516Z-layer-slope/measurements.json` | layer_slope_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T025151882721Z-layer-join/measurements.json` | join_probe: sections: internal join adjacent sample gap > .03 full scale |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T025152748271Z-flat/measurements.json` | flat30_probe: sections: 30 Hz component amplitude contrast < 6 dB or invalid |
| 25 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T025153615180Z-layer-flat/measurements.json` | flat120_probe: sections: 120 Hz component amplitude contrast < 6 dB or invalid |
| 26 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T025154465431Z-slope/measurements.json` | slope_probe: loop seam: slope mismatch > .001 full scale per sample |
| 27 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261013T025155281517Z-failing/measurements.json` | ambience: spectrum: centroid outside fixture band; ambience: loop seam: endpoint jump > .03 full scale |
| 28 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261013T025155622067Z-invalid/measurements.json` | short_sections: expected_failure (section count); corrupt: expected_failure (decode); wrong_format: expected_failure (format); odd_sections: expected_failure (section count); native16_probe: expected_pass (none); native24_probe: expected_failure (format); stereo48_probe: expected_failure (format); mono441_probe: expected_failure (format) |
| 29 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T025156430512Z-normal/measurements.json` | none |

Totals: **29 runner invocations: 8 exit 0, 21 exit 1, no exit 2.** Prior-28 subset (#1 plus #3–#29) totals 8 exit 0 / 20 exit 1, matching the prior verifier's 28-mode outcomes. The 17-mode legacy subset within it (#11–#27) is unchanged. Invalid-mode receipt #28 reports all eight expected statuses: `short_sections` expected_failure (section count), `corrupt` expected_failure (decode), `wrong_format` expected_failure (format), `odd_sections` expected_failure (section count), `native16_probe` expected_pass, `native24_probe` expected_failure (format), `stereo48_probe` expected_failure (format), and `mono441_probe` expected_failure (format).

## Joint comparator and preservation evidence

Joint receipt: `.shokunin/audio/corpus/live/runs/20261013T025133084611Z-ui-joint-below/measurements.json`.

| Member | Frames | Measured duration | Centroid | Ordinary failures |
|---|---:|---:|---:|---|
| `ui_joint_below` base | 5,760 | 0.120000 s | 966.8966593379727 Hz | none |
| `ui_joint_below_alt` | 6,719 | 0.139979 s | 870.5547231776728 Hz | distinctness only |

The receipt's comparator values are duration delta `0.019978999999999997` s and relative centroid delta `0.09964036511023265`; thresholds remain duration `0.02` s and centroid `0.1`. It records ordinary checks passing for each file with the variant scratch duration expectation, and `passed: false` for this alternate only. This is not a test that the long variant conforms to canonical UI duration `.12 s`.

The joint receipt and both normal receipts retain the five original alternate comparisons, all passing:

| Alternate | Duration delta (s) | Relative centroid delta | Result |
|---|---:|---:|---|
| `ui_alt` | 0.04000000000000001 | 0.47187731004956435 | pass |
| `impact_alt` | 0 | 0.9563048992406177 | pass |
| `movement_alt` | 0.12 | 0.007518618572621081 | pass |
| `ambience_alt` | 0 | 0.5845136323520758 | pass |
| `stem_layer_alt` | 0 | 0.46179931396667484 | pass |

All 13 canonical artifact hashes match both the working-tree `sha256sum` and `HEAD` `c1c6c965e7a347597caea0f4ddeab42dd7fdcff2`:

- `.shokunin/audio/corpus/artifacts/ambience_alt.wav` — `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc`
- `.shokunin/audio/corpus/artifacts/ambience.wav` — `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198`
- `.shokunin/audio/corpus/artifacts/impact_alt.wav` — `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6`
- `.shokunin/audio/corpus/artifacts/impact.wav` — `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc`
- `.shokunin/audio/corpus/artifacts/movement_alt.wav` — `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639`
- `.shokunin/audio/corpus/artifacts/movement.wav` — `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d`
- `.shokunin/audio/corpus/artifacts/stem_layer_alt.wav` — `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9`
- `.shokunin/audio/corpus/artifacts/stem_layer_third.wav` — `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445`
- `.shokunin/audio/corpus/artifacts/stem_layer.wav` — `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9`
- `.shokunin/audio/corpus/artifacts/stem_sections.wav` — `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702`
- `.shokunin/audio/corpus/artifacts/stem.wav` — `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0`
- `.shokunin/audio/corpus/artifacts/ui_alt.wav` — `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f`
- `.shokunin/audio/corpus/artifacts/ui.wav` — `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9`

Threshold objects in the initial normal, joint-below, and restored normal receipts are identical; distinctness thresholds remain `.020` and `.10`. Initial and restored normal receipts are equal after excluding measurement `path` fields (in this replay, even those path fields are equal); normal exit is 0 in both.

## Scope

Only `.shokunin/audio/reports/round-31/r31-verifier.md` and runner-generated receipts under `.shokunin/audio/corpus/live/runs/` were written. No shared source, LOG, SCORECARD, canonical artifact, or other report was edited; no commit or push was made. The observed result is a numeric comparator case only, not causal isolation or any perception, codec, rights, engine, publishing, or promotion claim.
