# Round 7 simplifier review

## Scope
Read the declared Round 7 claim/spec in `.shokunin/audio/LOG.md` and the current `corpus/fixtures/measure_audio.py` and `build_artifacts.py`. This is a source-level simplification review only; no shell commands were run and no audio was generated or measured.

## Finding
The existing `section_contrast(path)` already has one shared section-count validation: it returns the structured `failure_kind: "section count"` before `np.split` whenever sample count differs from 192000. The new odd-input case does not need a second validator or an exception wrapper. `invalid_probes()` already routes the current `short_sections` input through this helper and classifies its returned failure kind.

Minimal integration, if the declared probe is implemented: create the odd WAV in the existing opt-in invalid-probe builder; include `odd_sections` in `invalid_probes()` with expected failure `section count`; run it through the same `section_contrast()` branch as `short_sections`; let the existing generic expected/observed status comparison and receipt handle it. Keep the old failure path evidence separate (baseline demonstration), rather than adding runtime baseline logic. Do not catch broad `ValueError`/`Exception`: the new count guard should prevent the expected split exception, while unrelated programming errors should remain visible.

## Boundaries
This is a code-path recommendation, not proof of the baseline exception or the new receipt. I did not run either path, inspect generated receipts, check artifact hashes, or make perceptual/audio/security claims. No duplicate validator appears necessary in the current source; parent integration can verify the actual diff and independent evidence.
