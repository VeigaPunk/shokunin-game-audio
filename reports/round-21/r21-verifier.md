# Round 21 independent verifier (r21-verifier)

Independent serial replay from repository root. No fixtures, canonical WAVs, runner, LOG, SCORECARD, SHONEN, or other reports were edited. Runner-created receipts are under `.shokunin/audio/corpus/live/runs/`. Exit 1 is the expected outcome for intentional measured negatives; any exit 2/setup error would invalidate the replay. No exit 2 occurred.

## Serial replay (19 executions)

| # | Exact shell command | Exit | Receipt | Failure set |
|---:|---|---:|---|---|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T005819679327Z-normal/measurements.json` | {} |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T005820541153Z-layer-third-join-edge-pass/measurements.json` | {} |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T005821409013Z-layer-third-join-edge-fail/measurements.json` | join200_edgefail_probe: sections: internal join adjacent sample gap > .03 full scale |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T005822269527Z-layer-third-join/measurements.json` | join200_probe: sections: internal join adjacent sample gap > .03 full scale |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `.shokunin/audio/corpus/live/runs/20261013T005823130196Z-layer-third-slope-edge-pass/measurements.json` | {} |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 | `.shokunin/audio/corpus/live/runs/20261013T005823987995Z-layer-third-slope-edge-fail/measurements.json` | edgefail_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T005824847511Z-layer-third-slope/measurements.json` | slope200_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T005825713809Z-layer-alt-reverse/measurements.json` | reverse180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T005826574853Z-layer-alt-slope/measurements.json` | slope180_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T005827440513Z-layer-alt-join/measurements.json` | join180_probe: sections: internal join adjacent sample gap > .03 full scale |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T005828302962Z-layer-alt-flat/measurements.json` | flat180_probe: sections: 180 Hz component amplitude contrast < 6 dB or invalid |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T005829159571Z-layer-slope/measurements.json` | layer_slope_probe: sections: internal join side slope mismatch > .001 full scale per sample |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261013T005830015761Z-layer-join/measurements.json` | join_probe: sections: internal join adjacent sample gap > .03 full scale |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T005830897320Z-flat/measurements.json` | flat30_probe: sections: 30 Hz component amplitude contrast < 6 dB or invalid |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261013T005831756311Z-layer-flat/measurements.json` | flat120_probe: sections: 120 Hz component amplitude contrast < 6 dB or invalid |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261013T005832602033Z-slope/measurements.json` | slope_probe: loop seam: slope mismatch > .001 full scale per sample |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261013T005833388376Z-failing/measurements.json` | ambience: spectrum: centroid outside fixture band; loop seam: endpoint jump > .03 full scale |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261013T005833620171Z-invalid/measurements.json` | short_sections: section count; corrupt: decode; wrong_format: format; odd_sections: section count |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T005834425700Z-normal/measurements.json` | {} |

Exit vector: `[0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0]`. Historical round-20 verifier rows 2–16 were replayed in their recorded order between the new edge pair and restored normal. All expected historical outcomes and failure kinds held; invalid-probe records were the expected four malformed-input outcomes. Initial and restored normal receipts are equal after removing measurement path identity (the only path-varying field).

## New paired 200 Hz bracket

| Control | Receipt | Probe failure set | Gap | Side-slope mismatch | 200 Hz contrast | Centroid | Other key checks |
|---|---|---|---:|---:|---:|---:|---|
| 983-count pass | `.shokunin/audio/corpus/live/runs/20261013T005820541153Z-layer-third-join-edge-pass/measurements.json` | `{}` | 0.029998779296875 FS | 0.000000000000000 FS/sample | 10.457519260401 dB | 1208.586973213594 Hz | valid/passed `True/True`; duration 4.0 s, 48000 Hz mono; peak 0.163604736328; RMS -23.296643478 dBFS |
| 984-count fail | `.shokunin/audio/corpus/live/runs/20261013T005821409013Z-layer-third-join-edge-fail/measurements.json` | `{'join200_edgefail_probe': ['sections: internal join adjacent sample gap > .03 full scale']}` | 0.030029296875000 FS | 0.000000000000000 FS/sample | 10.457519263296 dB | 1209.639718919080 Hz | valid/passed `True/True`; duration 4.0 s, 48000 Hz mono; peak 0.163604736328; RMS -23.296643462 dBFS |

### Numerical interpretation and scope

The decoded pair brackets the existing strict full-scale adjacent-gap predicate: 983/32768 = 0.029998779296875 (not greater than 0.03) passes; 984/32768 = 0.030029296875 (greater than 0.03) is the sole failure. Both preserve 0.0 FS/sample side-slope mismatch, valid 200 Hz section contrasts well above the existing 6 dB minimum, and otherwise normal generic/outer measurements. `section.passed` means section contrast/validity only, not the full gate; the whole-run failure set is decisive. No threshold or comparator was changed: runner applies `internal_join_adjacent_delta_full_scale > .03`, and the threshold receipt remains `internal_join_adjacent_delta_max_full_scale: 0.03`; side slope remains `> .001` against the recorded `.001` maximum. The join predicate is applied to the new probe names in the same existing check. Builder generation makes the original 220/330 Hz bed plus stepped 200 Hz layer, quantizes PCM16, sets `frames[96000] = frames[95999] + gap_counts`, then computes frame 96001 to preserve the left side-slope. This is reproducible from the checked-in builder/runner and emits scratch only under `live/round-21/`, not a canonical artifact.

New scratch SHA-256: `join200_edgepass_probe.wav` `2f26852b2a0eb19f08afbe5189bb41c875f9ff78c072f96d19140d0a02586600`; `join200_edgefail_probe.wav` `5194bd8e2cc9929d5287d3ddd910d32b3c24aa2f76ba66f267d83dbbe84d97fd`. The latter is byte-identical to historical round-20 selected `corpus/live/round-20/join200_probe.wav` (same hash), but is at a separately generated round-21 scratch path and is not a new canonical WAV. The failed-fit receipt was the separate `20261012T231846536176Z-layer-third-join` run, which failed both centroid and gap; it is not the selected round-20 result. The shared `5194...` hash belongs to the selected round-20 scratch and this round-21 fail endpoint, not the failed-fit scratch. This identity means the 984 bracket endpoint is the already-known selected negative waveform re-generated by the round-21 builder; it does not make it canonical.

## Canonical artifacts and distinctness

Compared all 13 current `.wav` canonical artifact hashes to `git show b1af040:.shokunin/audio/corpus/artifacts/<name>` (HEAD before the round): **13/13 match**. No canonical changes detected.

| Canonical file | SHA-256 | Match |
|---|---|---|
| `ambience.wav` | `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198` | True |
| `ambience_alt.wav` | `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc` | True |
| `impact.wav` | `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` | True |
| `impact_alt.wav` | `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6` | True |
| `movement.wav` | `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d` | True |
| `movement_alt.wav` | `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639` | True |
| `stem.wav` | `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0` | True |
| `stem_layer.wav` | `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9` | True |
| `stem_layer_alt.wav` | `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` | True |
| `stem_layer_third.wav` | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` | True |
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` | True |
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` | True |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` | True |

All five `_alt` distinctness records were present and passed in both new edge receipts (`ui_alt`, `impact_alt`, `movement_alt`, `ambience_alt`, `stem_layer_alt`). Their thresholds/records were unchanged: UI duration delta 0.04 s, impact centroid relative delta 0.9563, movement duration delta 0.12 s, ambience centroid relative delta 0.5845, stem-layer-alt centroid relative delta 0.4618. The historic 15 rows held as expected, including the prior 200 Hz gap negative; initial/restored normal receipts match excluding path identity.

## Calibration limits and verdict

**Verifier result: replay and narrow numerical calibration bracket verified.** Depth and coverage are not assessed as improved here. The evidence supports only this runner/fixture decode-path-specific PCM16 adjacent-gap boundary and source-generated paired scratch controls. It does not establish audible quality, perceptual suitability, external portability, a universal tolerance, or engine behavior. SHONEN box 4 remains open; this report is not a separate whole-lane review.
