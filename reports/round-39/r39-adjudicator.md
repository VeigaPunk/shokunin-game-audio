# Round 39 Sol adjudication — looping ambience orientation

## Verdict

**ADMIT the one declared calibration move**, scoped only to `.shokunin/audio/**`. The gate requires at least one improved axis and no demonstrated harm on another scoped axis. This is a numeric, baseline-relative orientation control; it is not an audio-quality verdict.

| Axis | Judgment | Evidence and bound |
|---|---|---|
| Depth | Unchanged | Existing generic `_alt` predicate and thresholds are reused, not deepened or made universal. |
| Coverage | Unchanged | Two opt-in orientation probes extend the local observed cases, but this round declared a calibration move, not general coverage or a new class of validator. Prior 36 outcomes and canonical fixture scope remain intact. |
| Calibration | **Improved** | The *same* equal-duration looping ambience pair changes result only when denominator roles swap: low-baseline forward passes at .10535223771748284; high-baseline reverse fails solely on distinctness at .09531100957920152. Non-author replay reproduces both. |

No demonstrated scoped harm: old 17 canonical WAV SHA-256 and metrics, generic five `_alt` plus four family comparison groups, threshold and section records, prior 36 outcomes, all eight invalid statuses, and final normal restore held under independent replay. SHONEN four checked; **no promotion**. Admission does not authorize commit, push, merge, release, or publishing.

## Evidence inspected

I read the Round 39 LOG declaration and subsequent fit/integration/replay entries; all eight wave-1 reports (`r39-scout`, `r39-executor`, `r39-alt`, `r39-critic`, `r39-reviewer`, `r39-simplifier`, `r39-scribe`, `r39-guard`); named **non-author** `r39-verifier.md`; the raw forward/reverse, initial/final normal and invalid replay JSON receipts; and the source diff against clean-before `03fc02d386328742e6f7ae727d1c18d08c4a0b48`. Source diff adds opt-in CLI/build modes and maps shared generated files to generic `ambience_orientation`/`ambience_orientation_alt` in opposing orders. No canonical specification, distinctness formula, thresholds, or existing family logic changes. Builder generates 108/114 Hz sinusoids at amplitude .22 for 2 seconds; both modes regenerate the same two filenames. Raw file SHA-256 values match the reported pair:

- `orientation_low.wav`: `7f4cdfefa6e52a8ff44268396b5c09ea459a648a5ac4cad0f42722fe5fc29938`.
- `orientation_high.wav`: `24203978fe84384db6686e8cf065e1f06f2eb966e88e92578f5da1bb9c5b9482`.

Both files have 96,000 frames, 48 kHz, mono PCM16, duration 2.0 seconds; raw replay measurements show centroids **125.06515861511004** and **138.2410529357038 Hz**, no ordinary/seam failures, and **0.0-second duration delta** in either order. These values are runner-recomputed floats, rather than wave-1 scratch last digits. Exact runner commands and exits in the non-author serial replay:

| Mode | Command | Exit | Raw receipt and consequence |
|---|---|---:|---|
| Forward | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-forward` | 0 | `.shokunin/audio/corpus/live/runs/20261013T044308048763Z-ambience-orientation-forward/measurements.json`; low baseline/high `_alt`, .10535223771748284 > .10, generic pass, failures empty. |
| Reverse | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-reverse` | 1 | `.shokunin/audio/corpus/live/runs/20261013T044309164400Z-ambience-orientation-reverse/measurements.json`; high baseline/low `_alt`, .09531100957920152 < .10, sole failure `ambience_orientation_alt: distinctness: duration < .020 s and centroid delta < 10%`. |
| Initial/final normal | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 each | `20261013T044306919296Z-normal` and `20261013T044346196309Z-normal` under `.shokunin/audio/corpus/live/runs/`, each `measurements.json`; raw receipt objects equal. |
| Invalid | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1, expected | `.shokunin/audio/corpus/live/runs/20261013T044341150218Z-invalid/measurements.json`; seven expected failures and native16 expected pass, unchanged. |

The verifier's exact per-command/per-exit table covers all **38 serial calls**: **15 exit 0 / 23 expected validation exit 1**, with **no corrected-run setup error**; old prior-36 subset **14 / 22**. Generic five comparisons retain their values; UI/impact/movement/ambience family groups (four family groups) and section/threshold fields are preserved. The old 17 WAV hashes and normal metrics were compared with clean-before, not inferred from mere path presence.

Failed fitting and setup are separate evidence classes. Critic's transient concurrently overwritten executor B gave forward **.475587818471419** and reverse **.3223039744012571**, a *failed numeric fit*, not the settled SHA-pinned executor pair or selected alt pair. The alt 55/60 and 65/75 tests, and executor .085/.4 tests, were also numeric misses. Early wrapper exit **127** and helper-path exit **1** were setup/path errors, not fixture outcomes; none belongs to the corrected 38-run count.

## Limits and adjudicator command record

No exact-threshold-boundary claim, universal validity, perceptual or spectral-similarity claim, audible seamlessness claim, quality/production/rights/engine/publish claim follows from these numeric checks. “Seam pass” means only that the project's ordinary/seam helper reported no failure for these two loops. I did not run the runner anew or edit shared files. Inspection shell command: `git diff 03fc02d386328742e6f7ae727d1c18d08c4a0b48 -- .shokunin/audio/corpus/fixtures/measure_audio.py; git status --short` — exit **0**. Inspection shell command: `git diff 03fc02d386328742e6f7ae727d1c18d08c4a0b48 -- .shokunin/audio/corpus/fixtures/build_artifacts.py` — exit **0**. Reads, receipt parsing, and file hashing were Python REPL operations without shell exits. This report is the sole file I wrote; no commit or push.
