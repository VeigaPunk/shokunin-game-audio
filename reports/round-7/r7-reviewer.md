# Round 7 reviewer — minimal integration proposal

## Scope and recommendation

Report-only review of the declared round-7 depth claim and current `build_artifacts.py` / `measure_audio.py` invalid-probe implementation. The smallest coherent change is to extend the existing opt-in invalid-probe path with one fourth, named `odd_sections` case. Do not change `section_contrast()` thresholds or normal fixture generation.

## Builder integration

In `build_invalid_probes()`, retain the three round-6 outputs unchanged and create `live/round-7/odd_sections.wav` using the existing `wave` writer conventions: mono, 16-bit PCM, 48 kHz, exactly 101 frames. Generate deterministic samples (the sample values are immaterial to the count check). Keep the output in its declared round-7 scratch directory; do not add it to `ARTIFACTS` or `SPECS`. Since `--probe-invalid` already calls this builder, this makes the scratch reproducible through the existing entry point. The builder should not truncate/regenerate other files beyond its current behavior.

## Receipt integration

Append `("odd_sections", "section count")` to the existing invalid-probe cases, but associate it with `ROOT / "live" / "round-7" / "odd_sections.wav"` rather than assuming every case lives in `live/round-6`. The existing non-corrupt/non-wrong-format branch already calls `section_contrast()` and records its result; on current source its expected `failure_kind` should yield `observed_failure: "section count"`, then the existing status logic yields `expected_failure`. This preserves the current receipt schema and aggregate exit rule (1 when all named invalid probes are rejected as expected; 2 for an unexpected result). Avoid broad exception catching: unexpected decode/programming errors should remain visible, consistent with the declared narrow scope.

## Evidence boundary / validation requested

The round-7 claim requires independent evidence that the exact odd scratch raises `ValueError` in the `3b02c31` baseline, while current opt-in mode emits a persisted `odd_sections` entry reporting actual count 101 versus expected 192000, category `section count`, with no traceback. Then replay existing invalid cases and the declared clean/negative controls and hash checks. This review did not run shell commands, create scratch files, or validate behavior; it makes no claim about those results. The odd scratch/report was not present when I inspected the report directory, so I did not assume it existed.

## Files / commands

Inspected `.shokunin/audio/LOG.md` round-7 declaration and current `corpus/fixtures/{measure_audio.py,build_artifacts.py}` source. No shell commands run; no exit codes to report. No source, LOG, SCORECARD, or artifact edits made.
