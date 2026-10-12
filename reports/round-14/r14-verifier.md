# Round 14 independent serial replay — Luna verifier

Read the round-14 LOG, wave-1 reports, integrated builder/runner and fixture knowledge before replay. Ran the following exact commands serially from the repository root. No setup errors occurred.

| Exact command | Exit | Receipt (repo-relative) |
|---|---:|---|
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261012T183638307546Z-normal/measurements.json` |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 | `corpus/live/runs/20261012T183639108669Z-layer-alt-join/measurements.json` |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 | `corpus/live/runs/20261012T183639892581Z-layer-alt-flat/measurements.json` |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 | `corpus/live/runs/20261012T183640680968Z-layer-slope/measurements.json` |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 | `corpus/live/runs/20261012T183641462699Z-layer-join/measurements.json` |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 | `corpus/live/runs/20261012T183642254687Z-flat/measurements.json` |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 | `corpus/live/runs/20261012T183643048143Z-layer-flat/measurements.json` |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 | `corpus/live/runs/20261012T183643827130Z-slope/measurements.json` |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 | `corpus/live/runs/20261012T183644549883Z-failing/measurements.json` |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 | `corpus/live/runs/20261012T183644778496Z-invalid/measurements.json` |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261012T183645508917Z-normal/measurements.json` |

## New 180Hz join probe

`--probe-layer-alt-join` exits 1 with **only** `join180_probe: sections: internal join adjacent sample gap > .03 full scale`. The decoded gap is `0.044403076171875` FS (> .03); side-slope mismatch is `0.0` FS/sample (within .001). The 180Hz section record is valid and passes: amplitudes `[0.014999176755147345, 0.04999840864865898]` FS, contrast `10.457775175842691` dB, `valid: true`, `passed: true`. Generic and outer checks pass: endpoint delta `0.005218505859375` FS, outer slope mismatch `0.00079345703125` FS/sample; centroid `1678.5871008347167` Hz is within the existing 100–2000 Hz band. Probe SHA-256 `e81f0a2331c718748a94c34218c9e956b4e5464901afc8d3cee5d71804b03781` matches the selected worker candidate byte-for-byte.

The worker's direct floating calculation reports gap `.044404431288` FS, which differs from the integrated runner's decoded-PCM value. The runner's decoded value is authoritative for this check; the two conversion results are not treated as equal.

**Scope caveat:** the selected candidate adds the original smooth common 220/330Hz bed to the stepped 180Hz component before the two join-frame edits. It is not a waveform-identical corruption of canonical `stem_layer_alt`; evidence supports isolation against the named deterministic fixture gates only. The unused alternate is not counted.

## Existing modes and canonical assets

- The clean alternate layer has valid 180Hz contrast `10.457250572050896` dB and its internal controls pass.
- Existing negative controls retain their intended outcomes: flat180 and flat30/flat120 contrast controls, layer side-slope control, prior 120Hz gap control, outer slope control, failing ambience, and four invalid-fixture categories each show the expected named failure. The five `_alt` distinctness records all pass.
- Normal and restore `measurements.json` objects are exactly equal.
- All 12 canonical WAVs match pre-round Git commit `ce3233a` via binary-safe `git show ce3233a:.shokunin/audio/corpus/artifacts/<name> | sha256sum`; all 12 comparisons matched and each command exited 0.

No audible, musical, engine/adaptive-behavior, threshold-calibration, external-compatibility, or production-quality claim follows from this deterministic fixture replay.
