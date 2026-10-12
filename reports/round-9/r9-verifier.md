# Round 9 independent replay — Luna verifier

## Scope and review

Read the round-9 declaration in `LOG.md`, all eight wave-1 reports (`r9-scout`, `r9-receipts`, `r9-migration`, `r9-critic`, `r9-reviewer`, `r9-simplifier`, `r9-scribe`, `r9-guard`), the integrated `corpus/fixtures/measure_audio.py`, and `corpus/knowledge/2026-10-12-fixture-battery.md`. I independently ran the seven requested modes and compared the new receipts with the pre-change receipts as committed at `aaf4801`. This is receipt semantics/auditability verification, not tuned threshold calibration or compatibility assurance. Unknown external readers may exist.

## Commands, exits, and receipts

Executed serially in this order; each successful mode emitted the following receipt:

| Exact command | Exit | Receipt and result |
|---|---:|---|
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261012T173529588648Z-normal/measurements.json`; no failures |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `corpus/live/runs/20261012T173530301419Z-flat/measurements.json`; sole failure `flat30_probe` section contrast |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `corpus/live/runs/20261012T173531012671Z-layer-flat/measurements.json`; sole failure `flat120_probe` section contrast |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `corpus/live/runs/20261012T173531703686Z-slope/measurements.json`; expected slope failure |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `corpus/live/runs/20261012T173532346892Z-failing/measurements.json`; expected ambience centroid and endpoint failures |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `corpus/live/runs/20261012T173532571164Z-invalid/measurements.json`; expected short/odd section count, corrupt decode, wrong format failures |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261012T173533220319Z-normal/measurements.json`; clean restore, no failures |

All negative-control exit 1 outcomes correspond to their expected negative controls, not generic success. The flat modes each report exactly their probe as failing. Invalid probe statuses are all `expected_failure`.

## Schema checks

New normal, flat30 and flat120 receipts omit `thresholds.section_component_hz`. Every section record contains `component_hz` (30 Hz for `stem_sections`/flat30; 120 Hz for `stem_layer`/flat120). The old result key `section_energy_delta_db` is absent, and `component_amplitude_contrast_db` is present for all valid section records.

The `--probe-invalid` receipt checks invalid-count result shape too: `short_sections` reports `actual_samples: 144000`, `component_hz: 30`, empty amplitude/RMS arrays, `component_amplitude_contrast_db: null`, `valid: false`, `passed: false`, and `failure_kind: "section count"`. `odd_sections` likewise reports 101 samples and the same null/new-key invalid shape. Corrupt and wrong-format probes produce their expected classifications.

## Before/after comparison

Before records were read directly from Git using `git show aaf4801:<receipt-path>` (the old bytes are not inferred from a working-tree copy). Compared paths and new receipts:

| Mode | `aaf4801` receipt | New replay receipt |
|---|---|---|
| normal | `corpus/live/runs/20261012T172640257036Z-normal/measurements.json` | `corpus/live/runs/20261012T173529588648Z-normal/measurements.json` |
| flat30 | `corpus/live/runs/20261012T172638021452Z-flat/measurements.json` | `corpus/live/runs/20261012T173530301419Z-flat/measurements.json` |
| flat120 | `corpus/live/runs/20261012T172637297691Z-layer-flat/measurements.json` | `corpus/live/runs/20261012T173531012671Z-layer-flat/measurements.json` |

For each corresponding section record, I remapped the old `section_energy_delta_db` field to the new `component_amplitude_contrast_db` and compared the entire record. Values and all other fields matched exactly; numeric deltas are zero:

| Mode | Section | Hz | Old (dB) | New (dB) | Delta |
|---|---|---:|---:|---:|---:|
| normal | `stem_sections` | 30 | 13.979508033945462 | 13.979508033945462 | 0.0 |
| normal | `stem_layer` | 120 | 13.979372282981668 | 13.979372282981668 | 0.0 |
| flat30 | `stem_sections` | 30 | 13.979508033945462 | 13.979508033945462 | 0.0 |
| flat30 | `stem_layer` | 120 | 13.979372282981668 | 13.979372282981668 | 0.0 |
| flat30 | `flat30_probe` | 30 | 0.0 | 0.0 | 0.0 |
| flat120 | `stem_sections` | 30 | 13.979508033945462 | 13.979508033945462 | 0.0 |
| flat120 | `stem_layer` | 120 | 13.979372282981668 | 13.979372282981668 | 0.0 |
| flat120 | `flat120_probe` | 120 | 0.0 | 0.0 | 0.0 |

For all three pairs, `measurements` and `distinctness` objects are exactly equal. All thresholds match except the removed `section_component_hz`; no other threshold key/value differs. Thus 30 Hz and 120 Hz sections continue to be identified by their individual records. No nonidentical values were found in these comparisons.

All four variants (`ui_alt`, `impact_alt`, `movement_alt`, `ambience_alt`) occur in the clean normal receipt and have `passed: true` distinctness results.

## Canonical assets and historical immutability

Independently compared SHA-256 of each current canonical WAV with the blob bytes retrieved using `git show aaf4801:<path>`. All eleven match exactly: `ambience.wav` `b18c81706fb03ecb51359bdf7045ef814dc28cbb51ce9b75fcda79a79fb5a198`; `ambience_alt.wav` `2f76e846b41a7337d29f4dd0eae29cd7407727344a38b3f98ac530edfeb7f0fc`; `impact.wav` `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc`; `impact_alt.wav` `a301a620981035d2a9f204aa661e10017fae5a62b5c7508ec6f879ea0ba95eb6`; `movement.wav` `23ca9d17930b9bfec6e1ba57e91d8583b1a4f0cb15e70174bf161d204723122d`; `movement_alt.wav` `51c740bd9af3f8ecc974a30f91aae306c8a38cc46afe99b627c6a5c993d54639`; `stem.wav` `fb9a9c4f8ef09a10c13f81c163cce3133fbff3aa254729dd7ecbf26abeade1d0`; `stem_layer.wav` `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9`; `stem_sections.wav` `49ca24fb325c372c370db07c6ce182865b7fe84abe56037e5a1c8bd3196e6702`; `ui.wav` `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9`; `ui_alt.wav` `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f`.

Historical receipt immutability was checked independently: `git diff --quiet aaf4801 -- <each of the three old receipt paths>` returned exit 0 for each, and `git diff --name-status` listed none of them. Their hashes from committed bytes were normal `fe581ba592a39a10fd04824b115061afccf3f6507247523ac1ffa147858e6796`, flat30 `5927e3adca781280984896bcbb2e38d4365314e46aac43b5349432d27c50c8c0`, flat120 `ec209770b045e63e1d9b822745e386d17ed2a57cbcf3418733d486b254f7c192`.

## Command correction disclosure

The earlier replay attempt had one misspelled restore command: `python3 .shokhun/audio/corpus/fixtures/measure_audio.py`. It exited 2 with stderr `python3: can't open file '/home/vgpnk/Projects/prymeagnt/audio/.shokhun/audio/corpus/fixtures/measure_audio.py': [Errno 2] No such file or directory`; stdout said restore:2. It produced no receipt. This is not counted as a successful mode. The corrected exact restore command is shown in the seven-mode table above and exited 0 with a receipt.

## Conclusion and limits

Independent replay confirms unchanged deterministic section values and fixture outcomes under the clarified receipt labels, including the invalid-count shape. This supports semantics/auditability only. It does not show that the 6 dB threshold or other numeric limits are calibrated, perceptually meaningful, or general beyond these fixtures. The receipt schema change is breaking for readers expecting the old key; unknown external consumers remain unknown, and backward compatibility is not claimed. Historical JSON is unchanged.
