# Round 12 independent verifier replay

## Scope

Named non-author replay of the integrated fixture runner, performed serially from repository root. I read the Round 12 declaration and wave-1 reports, the integrated source diff against `f986933`, and the fixture-battery knowledge extension. I edited only this report; runner-generated measurement receipts are scratch evidence. No source, LOG, SCORECARD, or canonical fixture was edited by me.

## Setup failures (not test evidence)

The first normal command, `python3 .shokunin/audio/corpus/fixtures/measure_audio.py`, ran correctly and exited 0 (receipt `corpus/live/runs/20261012T180908513824Z-normal/measurements.json`). My subsequent harness calls mistakenly quoted each entire command as one shell word, causing Bash to seek an executable whose name contained spaces. They returned exit 127 (`No such file or directory`) and produced no valid receipts. This happened for intended normal and each of `--probe-layer-slope`, `--probe-layer-join`, `--probe-flat`, `--probe-layer-flat`, `--probe-slope`, `--probe-failing`, and `--probe-invalid`; a second batch repeated the seven negative modes and normal. One second-batch command also misspelled `.shokunin` as `.shokun`, exit 127. These setup attempts are excluded; below are the corrected exact command runs.

## Corrected serial replay

| Mode | Exact command | Exit | Receipt |
|---|---|---:|---|
| Normal | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261012T181138537075Z-normal/measurements.json` |
| Layer side-slope | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `corpus/live/runs/20261012T181139329793Z-layer-slope/measurements.json` |
| Layer join | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `corpus/live/runs/20261012T181140115256Z-layer-join/measurements.json` |
| Flat-30 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `corpus/live/runs/20261012T181140900892Z-flat/measurements.json` |
| Flat-120 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `corpus/live/runs/20261012T181141704446Z-layer-flat/measurements.json` |
| Outer slope | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `corpus/live/runs/20261012T181142488683Z-slope/measurements.json` |
| Broken amplitude | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `corpus/live/runs/20261012T181143212511Z-failing/measurements.json` |
| Invalid inputs | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `corpus/live/runs/20261012T181143444635Z-invalid/measurements.json` |
| Normal restore | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261012T181144168274Z-normal/measurements.json` |

Both normal receipts have empty failure maps. Negative modes fail only in their expected control: layer side-slope threshold; layer-join adjacent gap; flat30 contrast; flat120 contrast; outer-loop slope; and ambience centroid/endpoint in the broken-amplitude control. Invalid mode reports the four expected categories: short_sections=`section count`, corrupt=`decode`, wrong_format=`format`, odd_sections=`section count`. The layer-slope and layer-join controls are isolated to their named probes.

## New layer, hashes, and receipt comparison

The restored normal receipt measures 12 canonical WAVs and five passing `_alt` distinctness records. `stem_layer_alt` is 4.0 s, 48,000 Hz mono; its canonical SHA-256 is `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9`, equal to the selected original scratch candidate at `corpus/live/round-12/layer_alt_candidate.wav`. Its measurement has no generic or outer-seam failures: outer endpoint delta `.001190185546875` FS and outer slope mismatch `.00079345703125` FS/sample. Its 180 Hz section result is valid/passing with amplitudes `.014999921578770435` and `.04999787162649197` FS, contrast `10.457250572050896 dB`, internal adjacent gap `.0003662109375` FS and internal side-slope mismatch `.0008544921875` FS/sample. The existing `_alt` comparison against `stem_layer` passes with centroid-relative delta `.46179931396667484`; duration delta is zero.

I directly SHA-256 hashed each of the 11 existing canonical WAVs and each corresponding blob from `git show f986933:.shokunin/audio/corpus/artifacts/<name>`. All 11 current-vs-baseline comparisons are equal. In particular, `impact.wav` is `a462019d1189cbafb8d1240d972d99959401ca249a0c074b9b1a7f913d8bc8bc` (64 hex characters) both in the current file and baseline blob. An earlier draft of `r12-guard.md` contained a one-character transcription error in that hash; this was a report-text typo, not a hash mismatch. The guard report has since been corrected. The new layer hash also equals the selected executor scratch hash.

I compared the pre-integration normal receipt `corpus/live/runs/20261012T175755823615Z-normal/measurements.json` with the restored normal receipt. After removing only the new `stem_layer_alt` entry from `measurements`, `distinctness`, and `sections`, plus its new centroid-band entry from `thresholds`, the remaining receipt objects are exactly equal. No other measurement, distinctness result, section result, or threshold value changed.

## Limits

This verifies deterministic synthetic fixture coverage and existing numeric checks only. It does not establish audibility, music quality, engine synchronization/adaptive behavior, or production suitability. Reused thresholds are fixture-local; this replay is not threshold calibration.
