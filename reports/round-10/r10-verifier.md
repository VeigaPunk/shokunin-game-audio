# Round 10 independent serial replay — `r10-verifier`

## Scope and result

I independently replayed the integrated measurement entry point serially: clean battery, internal-join control, all prior negative controls, invalid-input mode, and clean restoration. The new join control has exactly one failure: `join_probe` reports only `sections: internal join adjacent sample gap > .03 full scale`. The five older negative modes retain their expected rejection; both normal runs pass with eleven canonical files and four passing SFX distinctness checks.

The new predicate measures the magnitude of one adjacent decoded-PCM sample difference at the 2-second split (samples 95,999 and 96,000). The `.03 FS` bound is reused as a fixture-local comparator, not calibrated for audibility. This evidence does not establish click-free or smooth transitions, slope continuity at the internal boundary, audible quality, runtime behavior, or production suitability.

## Exact serial commands, exits and durable receipts

Commands ran from the repository root in this order. Every successful invocation prints the receipt path shown below.

| Mode | Exact command | Exit | Receipt / result |
|---|---|---:|---|
| normal | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261012T174636828394Z-normal/measurements.json`; no failures |
| new internal-join negative | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `corpus/live/runs/20261012T174637561631Z-layer-join/measurements.json`; only `join_probe`: internal join adjacent sample gap > .03 FS |
| old flat 30 Hz negative | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `corpus/live/runs/20261012T174638305858Z-flat/measurements.json`; only `flat30_probe` section contrast failure |
| old flat 120 Hz negative | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `corpus/live/runs/20261012T174639024112Z-layer-flat/measurements.json`; only `flat120_probe` section contrast failure |
| old slope negative | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `corpus/live/runs/20261012T174639723477Z-slope/measurements.json`; only `slope_probe` slope-mismatch failure |
| old broken-amplitude negative | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `corpus/live/runs/20261012T174640374223Z-failing/measurements.json`; only `ambience` fails (centroid and endpoint) |
| invalid-input battery | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `corpus/live/runs/20261012T174640598542Z-invalid/measurements.json`; four named expected failures: short count, corrupt decode, wrong format, odd count |
| normal restoration | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261012T174641251161Z-normal/measurements.json`; no failures |

No command setup failures occurred in this replay.

## Isolated join-control measurements

The independently generated scratch `corpus/live/round-10/join_probe.wav` SHA-256 is `2c3b158b6ea3c29f03f785f900b18b36b5c7e26010262ecd4f9285c61bceabe4`, matching the declared selected recipe. In the join receipt, `join_probe` is 4.0 s, 48 kHz mono; generic `measure()` failures are empty. Peak is 0.0820618 FS, centroid 1769.518 Hz (inside its 100–2000 Hz band), outer endpoint delta 0.00119019 FS, and outer slope delta 0.000732422 FS/sample. Its 120 Hz section amplitudes are 0.01199958745 and 0.05999774520 FS, contrast 13.9793722835 dB, valid and passing. The internal adjacent-sample gap is 0.030914306640625 FS, above .03; that is the sole reported failure.

On clean `stem_layer`, the same field is 0.00018310546875 FS. It passes alongside its 13.97937228298 dB 120 Hz component-amplitude contrast. The normal receipts each contain eleven canonical measurements, all generic failure lists empty, four distinctness entries all passing, and two section records.

## Canonical hashes and unchanged guards

Compared each current `corpus/artifacts/*.wav` SHA-256 against the Git blob at before-state `f32ab7fa9415d5957aeb8846133756b36a11114f` (`f32ab7f`). All **11 of 11** hashes match:

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
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` |
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` |

The new scratch negative-control WAV hash matches the selected candidate hash. Old flat30, flat120, slope, failing and invalid controls all continue to reject as expected; clean restoration passes. # Round 10 independent serial replay — `r10-verifier`

## Scope and result

I independently replayed the integrated measurement entry point serially: clean battery, internal-join control, all prior negative controls, invalid-input mode, and clean restoration. The new join control has exactly one failure: `join_probe` reports only `sections: internal join adjacent sample gap > .03 full scale`. The five older negative modes retain their expected rejection; both normal runs pass with eleven canonical files and four passing SFX distinctness checks.

The new predicate measures the magnitude of one adjacent decoded-PCM sample difference at the 2-second split (samples 95,999 and 96,000). The `.03 FS` bound is reused as a fixture-local comparator, not calibrated for audibility. This evidence does not establish click-free or smooth transitions, slope continuity at the internal boundary, audible quality, runtime behavior, or production suitability.

## Exact serial commands, exits and durable receipts

Commands ran from the repository root in this order. Every successful invocation prints the receipt path shown below.

| Mode | Exact command | Exit | Receipt / result |
|---|---|---:|---|
| normal | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261012T174636828394Z-normal/measurements.json`; no failures |
| new internal-join negative | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `corpus/live/runs/20261012T174637561631Z-layer-join/measurements.json`; only `join_probe`: internal join adjacent sample gap > .03 FS |
| old flat 30 Hz negative | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `corpus/live/runs/20261012T174638305858Z-flat/measurements.json`; only `flat30_probe` section contrast failure |
| old flat 120 Hz negative | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `corpus/live/runs/20261012T174639024112Z-layer-flat/measurements.json`; only `flat120_probe` section contrast failure |
| old slope negative | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `corpus/live/runs/20261012T174639723477Z-slope/measurements.json`; only `slope_probe` slope-mismatch failure |
| old broken-amplitude negative | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `corpus/live/runs/20261012T174640374223Z-failing/measurements.json`; only `ambience` fails (centroid and endpoint) |
| invalid-input battery | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `corpus/live/runs/20261012T174640598542Z-invalid/measurements.json`; four named expected failures: short count, corrupt decode, wrong format, odd count |
| normal restoration | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261012T174641251161Z-normal/measurements.json`; no failures |

No command setup failures occurred in this replay.

## Isolated join-control measurements

The independently generated scratch `corpus/live/round-10/join_probe.wav` SHA-256 is `2c3b158b6ea3c29f03f785f900b18b36b5c7e26010262ecd4f9285c61bceabe4`, matching the declared selected recipe. In the join receipt, `join_probe` is 4.0 s, 48 kHz mono; generic `measure()` failures are empty. Peak is 0.0820618 FS, centroid 1769.518 Hz (inside its 100–2000 Hz band), outer endpoint delta 0.00119019 FS, and outer slope delta 0.000732422 FS/sample. Its 120 Hz section amplitudes are 0.01199958745 and 0.05999774520 FS, contrast 13.9793722835 dB, valid and passing. The internal adjacent-sample gap is 0.030914306640625 FS, above .03; that is the sole reported failure.

On clean `stem_layer`, the same field is 0.00018310546875 FS. It passes alongside its 13.97937228298 dB 120 Hz component-amplitude contrast. The normal receipts each contain eleven canonical measurements, all generic failure lists empty, four distinctness entries all passing, and two section records.

## Canonical hashes and unchanged guards

Compared each current `corpus/artifacts/*.wav` SHA-256 against the Git blob at before-state `f32ab7fa9415d5957aeb8846133756b36a11114f` (`f32ab7f`). All **11 of 11** hashes match:

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
| `stem_sections.wav` | `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702` |
| `ui.wav` | `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9` |
| `ui_alt.wav` | `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f` |

The new scratch negative-control WAV hash matches the selected candidate hash. Old flat30, flat120, slope, failing and invalid controls all continue to reject as expected; clean restoration passes. These are finite fixture/control checks, not generalized audio validation.


## Independent hash and source-diff procedure

For each canonical WAV, I computed `sha256sum .shokunin/audio/corpus/artifacts/*.wav` and compared the files against the requested before-state with `git diff --quiet f32ab7f -- .shokunin/audio/corpus/artifacts` (exit 0). The command output listed all eleven hashes in the preceding table; all match the Git blobs at `f32ab7f`. Thus no canonical WAV bytes changed.

I inspected `git diff f32ab7f -- .shokunin/audio/corpus/fixtures/measure_audio.py .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/corpus/knowledge/2026-10-12-fixture-battery.md`. The code diff adds the opt-in join-probe builder/CLI path, internal-join telemetry, and one gate for `stem_layer` and `join_probe`; it does not change the existing generic format/duration/peak/RMS/spectrum rules, section contrast rule, loop endpoint/slope rules, or invalid-probe categories. Existing controls replayed with their declared isolated outcomes. The knowledge note documents the metric, scope, and limits.

The implemented predicate is strict `internal_join_adjacent_delta_full_scale > .03`; therefore equality passes and only a value greater than .03 fails. The receipt declares `.03` as the maximum. In the selected negative control the decoded value is `0.030914306640625`, so it exceeds that bound. Clean `stem_layer` is `0.00018310546875`, so it passes. No threshold was loosened; `.03` is reused as a fixture-local comparator, not established as a perceptual/audibility limit.

## Candidate telemetry distinction

The selected final candidate is `r10-probe`'s PCM16 `join_candidate.wav` (SHA-256 `2c3b158b6ea3c29f03f785f900b18b36b5c7e26010262ecd4f9285c61bceabe4`). The generated `live/round-10/join_probe.wav` hash independently matches it exactly. The selected recipe adds the 60 Hz component and changes frame 96000; despite that spectral adjustment, its measured centroid remains inside the existing `stem_layer` band and it has the required sole join-predicate failure.

The earlier failed-fit telemetry in `r10-scribe.md` (including the candidate with centroid 2526 Hz above the 2000 Hz upper bound) predates the final `r10-probe` revision. It is not evidence for the selected candidate, is not silently erased, and does not contradict the final selected candidate's measured outcome. The separate `r10-control.md` float32 `join_alt_candidate.wav` uses a different amplitude schedule; it was exploratory only and was **not** selected, generated by this integrated probe mode, or used for the replay verdict.

This replay establishes only the named decoded adjacent-sample numerical proxy and its finite fixture/control behavior. It does not establish audible smoothness, click-free transitions, internal slope continuity, engine/adaptive behavior, or general audio quality.
