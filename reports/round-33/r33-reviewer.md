# Round 33 reviewer — minimal UI-third integration

## Review

The declared change is appropriately narrow: add one deterministic, source-generated UI fixture, validate it through the existing per-file measurement path, and emit explicit pair receipts for `ui_third` versus each existing UI fixture. Do not change the generic `_alt` comparison loop, its OR rule, thresholds, or existing fixture formulas.

## Minimal implementation recommendation

1. In `build_artifacts.py`, after the existing `ui` and `ui_alt` saves, add a `ui_third` save generated from a deterministic 0.20-second time vector at the existing 48 kHz rate. A chirp/envelope formula in the established style is suitable; keep peak below `.95` and RMS above `.001`. Do not rewrite existing WAVs or reuse a live-probe output as the canonical artifact.
2. In `measure_audio.py`, add exactly `"ui_third": (.20, 250, 4000, False)` to `SPECS`. That makes the normal measurement path enforce duration, format, level, and centroid-band checks and raises the canonical fixture count from 13 to 14.
3. Leave the existing `for name, variant in measurements.items()` `_alt` loop byte-for-byte unchanged. Separately compute two explicit UI-family records, using the already measured values and the same current numeric OR predicate:
   - baseline `ui`, variant `ui_third`
   - baseline `ui_alt`, variant `ui_third`

   Each record should include baseline/variant names, absolute duration delta, absolute centroid-relative delta (relative to that pair's baseline), and `passed = duration_delta >= .020 or centroid_relative_delta >= .10`. Store these in a distinct receipt field (for example `ui_family_comparisons`) rather than mislabeling them as `_alt` comparisons. If either fails, surface it as a failure on `ui_third` so runner exit status reflects the declared pair requirement. This is explicit pair reporting, not a new generic comparator.

At nominal durations, the duration legs alone should satisfy the existing rule: 0.20−0.12 = 0.08 s and 0.20−0.16 = 0.04 s. Still verify measured ffprobe durations and both pair receipts; do not treat nominal arithmetic as evidence that the generated file passed its ordinary checks.

## Evidence / limits

I read the round 33 declaration in `.shokunin/audio/LOG.md`, and inspected the existing builder and measurement scripts. I ran **no project shell commands**, so there are no command exit codes or execution results to report. This review therefore confirms the minimal integration shape, not a successful build or measured fit. If the candidate fails an ordinary check or either explicit pair comparison, report that and do not admit it.

This would add analytical fixture coverage only. Numeric duration/centroid distinctness is not an auditory-quality, perceptual-distinctness, production-readiness, rights, engine, publishing, or promotion claim. Independent replay should verify the new 14-fixture normal run, both pair receipts, all 13 prior canonical hashes, existing variants/thresholds, and historical-mode/invalid/restore invariants.
