# Round 13 independent verifier — serial replay

## Scope and failed setup telemetry

I independently replayed the integrated fixture runner serially from the repository root. An initial orchestration attempt used `r=await bash(...)` followed by `await r`; `bash()` had already returned a completed `BashResult`, so the second await raised `TypeError` **before a runner command was issued**. No command ran in that attempt.

I then incorrectly wrapped each whole command in shell quotes. All ten attempts below exited **127** (`python3 ... [args]` was treated as one executable name); none created receipts and none count as test results:

```text
python3 .shokunin/audio/corpus/fixtures/measure_audio.py
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid
python3 .shokunin/audio/corpus/fixtures/measure_audio.py
```

The corrected calls used one `r = await bash(command)` per unquoted command string, with no second await. The following ten modes then ran serially and each wrote a receipt:

| Mode | Exact command | Exit | Receipt |
|---|---|---:|---|
| `normal` | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261012T182214210060Z-normal/measurements.json` |
| `probe-layer-alt-flat` | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261012T182214989477Z-layer-alt-flat/measurements.json` |
| `probe-layer-slope` | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261012T182215794825Z-layer-slope/measurements.json` |
| `probe-layer-join` | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `.shokunin/audio/corpus/live/runs/20261012T182216581164Z-layer-join/measurements.json` |
| `probe-flat` | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261012T182217372876Z-flat/measurements.json` |
| `probe-layer-flat` | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `.shokunin/audio/corpus/live/runs/20261012T182218152931Z-layer-flat/measurements.json` |
| `probe-slope` | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `.shokunin/audio/corpus/live/runs/20261012T182218921091Z-slope/measurements.json` |
| `probe-failing` | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `.shokunin/audio/corpus/live/runs/20261012T182219639313Z-failing/measurements.json` |
| `probe-invalid` | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `.shokunin/audio/corpus/live/runs/20261012T182219870138Z-invalid/measurements.json` |
| `normal` | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261012T182220588396Z-normal/measurements.json` |

All receipts are under `.shokunin/audio/`. Exit 0 is expected for normal runs; exit 1 is the runner's expected negative-probe rejection.

## Results

- Both normal receipts have an empty failure map; each measures all 12 canonical WAVs, with all five `_alt` distinctness comparisons passing.
- `--probe-layer-alt-flat` receipt reports only `flat180_probe` failing the existing 180 Hz section-contrast rule. The two measured component amplitudes are `0.03599800833461317` FS, each section RMS is `0.02545443723242487` FS, contrast is `0.0 dB`, and `valid` is true. Generic/outer checks pass; internal join gap is `0.0008544921875` FS and side-slope mismatch is `0.0` FS/sample. Thus the declared contrast branch is isolated.
- Existing controls preserve their reported failure sets: layer side-slope only; layer join adjacent-gap only; flat30 contrast only; flat120 contrast only; outer slope only; broken ambience centroid and endpoint failures; invalid-input statuses are short `section count`, corrupt `decode`, wrong-format `format`, and odd-section `section count`.
- The source-generated `flat180_probe.wav` SHA-256 is `3c2ff9741fcfc35f660676da1e9f81c5678654fdaa0ea07b1cffeee3945f03ce`, matching the selected executor candidate. It is scratch, not a canonical asset.

## Canonical hash guard

All 12 current canonical WAVs match the Git blobs at before-state `db36a69`. For each, `git show db36a69:.shokunin/audio/corpus/artifacts/<name>.wav | sha256sum` matched the independently computed SHA-256 of the working file. `git diff --quiet db36a69 -- .shokunin/audio/corpus/artifacts/<name>.wav` also exited 0 for each of the 12 files.

A first attempted Python comparison used the text returned by `bash()` and re-encoded it before hashing; it produced false mismatches for all 12 and was discarded. The binary-safe shell SHA-256 and Git diff checks above are the corrected evidence.

## Before/after and comparator semantics

The Round 12 independent normal receipt `20261012T181138537075Z-normal/measurements.json` and this replay's first normal receipt `20261012T182214210060Z-normal/measurements.json` compare exactly equal as parsed JSON (`old == new`, true); all fields, including measurements, thresholds, distinctness and section records, match. The added flat probe is opt-in and does not alter clean normal output.

Source inspection of the integrated diff and runner confirms the existing decision polarity is unchanged: `section_contrast` requires `valid and delta_db >= 6.0`; component amplitudes must be finite and >= .01 FS, and section RMS >= .001 FS. The new failure is added when `passed` is false. Internal gap rejects only `> .03` FS; internal side-slope mismatch rejects only `> .001` FS/sample. Equality passes those strict upper bounds. No threshold literal was added or changed in the integrated diff. The flat control is not named `_alt` and has no distinctness record; the five canonical `_alt` comparisons remain passing.

## Limits

This verifies deterministic numeric control polarity and retained fixture hashes only. It does not establish audible flatness/quality, adaptive engine behavior, music quality, threshold calibration, or production readiness. The 6 dB and continuity bounds remain fixture-local.
