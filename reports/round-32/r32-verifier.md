# Round 32 independent verifier — NON-AUTHOR

## Verdict and scope

I serially replayed the requested **30 runner invocations**: initial normal, `--probe-ui-mixed-pass`, then the prior Round 31 sequence with its duplicate normal omitted (joint-below; forward/reverse orientation; lower-centroid below/above; centroid below/above; duration below/at; clone; 17 legacy modes including invalid; restored normal). Result: **9 exit 0, 21 exit 1, 0 exit 2**. The prior-29 subset (this replay #1 and #3–#30) is **8 exit 0 / 21 exit 1**. All exit-1 invocations produced expected gate receipts; none were runner setup errors.

The mixed probe exits 0 and passes the existing `_alt` distinctness OR through its centroid arm only. Its receipt records baseline 5760 frames / 0.120000 s and variant 6719 frames / 0.139979 s, with duration delta `0.019978999999999997` s (nonzero, below `.020`) and baseline-denominator centroid-relative delta `0.1059638814557548` (nonzero, at/above `.10`). Baseline ordinary checks pass under canonical UI spec; variant ordinary checks pass under separately declared scratch duration `6719/48000` and the same UI band/format/level checks. The variant does **not** meet canonical `.120 s ± .001 s` duration. `passed: true`; no measurement failure in either member, and the duration arm is false while centroid arm is true. Thresholds and canonical WAVs were not changed by this replay.

This is a numeric mixed-input OR case only. Duration/sample support and centroid change together; no causal independence, perception/audibility, codec, rights, engine, publishing, or promotion claim follows.

## Commands and receipts

Commands were run serially from repository root. Receipt paths are repository-relative; exit-1 failure kind is parsed from each receipt. The invalid probe's individual statuses are listed below.

| # | Exact command | Exit | Receipt | Failure kind / statuses |
|---:|---|---:|---|---|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T030245226932Z-normal/measurements.json` | none |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-mixed-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T030246117183Z-ui-mixed-pass/measurements.json` | none |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-joint-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T030247001608Z-ui-joint-below/measurements.json` | ui_joint_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-forward` | 1 | `.shokunin/audio/corpus/live/runs/20261013T030247881159Z-ui-orientation-forward/measurements.json` | ui_orientation_forward_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-reverse` | 0 | `.shokunin/audio/corpus/live/runs/20261013T030248760379Z-ui-orientation-reverse/measurements.json` | none |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T030249650407Z-ui-lower-centroid-below/measurements.json` | ui_lower_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T030250554675Z-ui-lower-centroid-above/measurements.json` | none |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T030251461201Z-ui-centroid-below/measurements.json` | ui_centroid_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | 0 | `.shokunin/audio/corpus/live/runs/20261013T030252374721Z-ui-centroid-above/measurements.json` | none |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | 1 | `.shokunin/audio/corpus/live/runs/20261013T030253276566Z-ui-duration-below/measurements.json` | ui_duration_below_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | 0 | `.shokunin/audio/corpus/live/runs/20261013T030254192502Z-ui-duration-at/measurements.json` | none |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | 1 | `.shokunin/audio/corpus/live/runs/20261013T030255092717Z-ui-clone/measurements.json` | ui_clone_alt: distinctness: duration < .020 s and centroid delta < 10% |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T030255970423Z-layer-third-join-edge-pass/measurements.json` | none |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T030256855802Z-layer-third-join-edge-fail/measurements.json` | join200_edgefail_probe: sections: internal join adjacent sample gap > .03 full scale |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T030257732723Z-layer-third-join/measurements.json` | join200_probe: sections: internal join adjacent sample gap > .03 full scale |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T030258599931Z-layer-third-slope-edge-pass/measurements.json` | none |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T030259474581Z-layer-third-slope-edge-fail/measurements.json` | edgefail_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T030300337570Z-layer-third-slope/measurements.json` | slope200_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T030301204697Z-layer-alt-reverse/measurements.json` | reverse180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T030302072265Z-layer-alt-slope/measurements.json` | slope180_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T030302943522Z-layer-alt-join/measurements.json` | join180_probe: sections: internal join adjacent sample gap > .03 full scale |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T030303813994Z-layer-alt-flat/measurements.json` | flat180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T030304682912Z-layer-slope/measurements.json` | layer_slope_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T030305548566Z-layer-join/measurements.json` | join_probe: sections: internal join adjacent sample gap > .03 full scale |
| 25 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T030306415195Z-flat/measurements.json` | flat30_probe: sections: 30 Hz component amplitude contrast < 6 dB or invalid |
| 26 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T030307289914Z-layer-flat/measurements.json` | flat120_probe: sections: 120 Hz component amplitude contrast < 6 dB or invalid |
| 27 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T030308145081Z-slope/measurements.json` | slope_probe: loop seam: slope mismatch > .001 full scale per sample |
| 28 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261013T030308947808Z-failing/measurements.json` | ambience: spectrum: centroid outside fixture band / loop seam: endpoint jump > .03 full scale |
| 29 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261013T030309287969Z-invalid/measurements.json` | short_sections: expected_failure (section count); corrupt: expected_failure (decode); wrong_format: expected_failure (format); odd_sections: expected_failure (section count); native16_probe: expected_pass (none); native24_probe: expected_failure (format); stereo48_probe: expected_failure (format); mono441_probe: expected_failure (format) |
| 30 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T030310096088Z-normal/measurements.json` | none |

The first attempt to execute the sequence used the mistyped script path `python3 .shokhun/audio/corpus/fixtures/measure_audio.py`: **30 setup errors, each exit 2**, no receipts. I corrected the path to `.shokunin/...` and reran the full sequence above. Those setup failures are excluded from the 30 runner outcomes and are not gate failures.

## Mixed-mode receipt detail

Receipt: `.shokunin/audio/corpus/live/runs/20261013T030246117183Z-ui-mixed-pass/measurements.json`.

| Member | Frames | Duration | Sample rate / channels / encoding | Spectral centroid | Ordinary failures |
|---|---:|---:|---|---:|---|
| `ui_mixed_pass` | 5760 | 0.120000 s | 48000 Hz / mono / PCM s16le 16-bit | 966.8966593379727 Hz | none |
| `ui_mixed_pass_alt` | 6719 | 0.139979 s | 48000 Hz / mono / PCM s16le 16-bit | 1069.352782328027 Hz | none |

Comparator values: duration delta `0.019978999999999997`, relative centroid delta `0.1059638814557548`, `passed: true`. Duration condition `>= .020` is false; centroid condition `>= .10` is true. The longer alternate's ordinary pass uses the separately declared scratch expected duration, not canonical UI duration.

## Preservation and prior-mode outcomes

All **13 canonical WAV SHA-256 hashes** match the working tree and `HEAD` `ae9c941aeda44b29718ab97edb252ef1ed12e637`; `git diff --quiet HEAD -- .shokunin/audio/corpus/artifacts` exited 0. The five pre-existing variants pass in initial and restored normal receipts, with unchanged comparator thresholds `.020 s OR .10`:

| Variant | Duration delta (s) | Relative centroid delta | Outcome |
|---|---:|---:|---|
| `ui_alt` | 0.04000000000000001 | 0.47187731004956435 | pass |
| `impact_alt` | 0.0 | 0.9563048992406177 | pass |
| `movement_alt` | 0.12 | 0.007518618572621081 | pass |
| `ambience_alt` | 0.0 | 0.5845136323520758 | pass |
| `stem_layer_alt` | 0.0 | 0.46179931396667484 | pass |

| Canonical artifact | SHA-256 |
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

Eight invalid-mode statuses in replay #29:

| Probe | Status | Observed failure |
|---|---|---|
| `short_sections` | expected_failure | section count |
| `corrupt` | expected_failure | decode |
| `wrong_format` | expected_failure | format |
| `odd_sections` | expected_failure | section count |
| `native16_probe` | expected_pass | none |
| `native24_probe` | expected_failure | format |
| `stereo48_probe` | expected_failure | format |
| `mono441_probe` | expected_failure | format |

Initial and restored normal commands both exited 0; thresholds and five variants were restored. Prior R31 sequence outcomes are retained in the command/receipt table above; no replay mode was omitted.

## Changes / limitations

Only `.shokunin/audio/reports/round-32/r32-verifier.md` and runner-generated receipts under `.shokunin/audio/corpus/live/runs/` were written. No source, LOG, SCORECARD, canonical artifact, or other report was edited; no commit or push. No causal, perceptual, codec, rights, engine, publishing, or promotion inference.
