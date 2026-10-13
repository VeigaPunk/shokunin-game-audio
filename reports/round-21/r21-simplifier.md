# Round 21 simplifier

## Recommendation

Make this a paired scratch-fixture extension, not a gate refactor. Reuse the existing `stem_layer_third`/`join200_probe` construction and existing `section_contrast()` plus `internal_join_adjacent_delta_full_scale > .03` check. Generate exactly two non-canonical 200 Hz WAVs by applying the declared 983- and 984-count target at the same join sample while preserving the left-step construction; expose the pair through two mutually exclusive CLI modes and route both through the existing 200 Hz measurement path. Keep the strict comparator and all existing checks unchanged. The checker should remain single-source-of-truth; do not add a parallel boundary predicate or modify thresholds.

For maintainability, share the scratch-generation operations for the pair (small loop over `(flag, count, name)` is sufficient) rather than duplicating the read/build/write block. Keep the existing mode dispatch style unless the new pair makes it materially harder to read; do not refactor all historical flags or measurement routing for this one addition. Do not add a canonical WAV, a general grid utility, compatibility schema, or a new artifact beyond the two required scratch controls and their normal receipts.

## Evidence and scope

Inspected `.shokunin/audio/LOG.md` round-21 declaration and the current builder and measurement entry point. Current code already has the strict internal-gap predicate in the shared section-result loop and a 200 Hz route for `join200_probe`; the simplification is to feed two scratch files to that existing path. The declaration's expected outcomes are numeric: 983/32768 = 0.029998779296875 should pass the `> .03` gate; 984/32768 = 0.030029296875 should fail it. The pair is only a bracket for the declared generated waveform and decode path, not audibility or a universal PCM boundary claim.

No audio commands or tests were run for this report; source inspection is not an integration test. In particular, this does not establish that both new runner modes are correctly wired, that either control has the intended isolated result, or that the full historical mode set remains unchanged. The parent should rely on the declared independent replay before any admission.

## Commands and exit codes

No shell commands were run; inspection was performed by reading the declared log and source through the Python REPL. There are no shell exit codes to report.
