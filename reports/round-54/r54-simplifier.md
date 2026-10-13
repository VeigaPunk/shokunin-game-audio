# R54 simplifier — keep the PCM32 pair local

## Recommendation

Use the existing R53 paired-probe pattern, narrowly applied to the declared PCM32/PCM16 case. Add one builder helper that writes the deterministic matched pair under `corpus/live/round-54/`, plus the two opt-in runner flags and their existing one-probe guard, builder forwarding, supplemental `measure(..., SPECS["ui"], path)` calls, mode labels, and run-directory suffixes. Build the PCM32 values from the same signed PCM16 integers (`s16 * 65536`); use WAV PCM format and verify the resulting codec/bit depth rather than relying on the filename. Keep the scratch measurements outside canonical fixtures and all family/section comparisons.

Do not add a format-conversion framework, alter `format_failures()`, `SPECS["ui"]`, thresholds, or existing probes. Do not refactor the accumulated mode/suffix selectors as part of this one-pair change; add only the R54 cases and stop/report if the local additions cannot be made without a broader rewrite. The existing measurement helper stays the source of truth.

## Basis and evidence limits

I read the standing brief, the R54 LOG declaration, the R53 integration source, and R53 reviewer/simplifier reports. R53 shows a local paired-probe design that reuses the UI measurement predicate and keeps the scratch pair out of canonical comparisons. The current runner already has an adjacent R53 float32/PCM16 pair branch; mirror that shape for the new R54 paths rather than generalizing across formats.

No shell/build/measurement/ffprobe command was run for R54. Therefore this report has no observed R54 exit codes, hashes, metadata, decoded-array comparison, or metrics to report. The declaration's 5760 frames at 48000 Hz implies the target duration of 0.120 s; that is a declared construction, not an observed measurement. The expected PCM32-only format failure and clean PCM16 result remain hypotheses until measured. Any additional UI-gate failure or unequal decoded vectors should be reported as contrary evidence and fixed in scratch, not by changing predicates or thresholds.

This recommendation concerns only integration scope and the declared matched fixture. It makes no general PCM32 conversion, precision, fidelity, audibility, quality, rights, engine, production, or promotion claim. No source or shared ledger was edited; no commit or push was made.
