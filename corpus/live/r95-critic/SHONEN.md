# SHONEN — probation

- [x] Real decision tables/error patterns/checklists with cited sources. Verified by named non-author `audio-r1-verifier`; evidence: `.shokunin/reports/audio-r1-verifier.md` (decision table citations and error-pattern review).
- [x] End-to-end domain task executed and logged. Verified by named non-author `r2-verifier`; evidence: `.shokunin/audio/reports/round-2/r2-verifier.md` (nine-file source-generation replay, positive control, deterministic restore).
- [x] Fixture-battery instructions executable without oral context. Verified by named non-author `r3-adjudicator` with `r3-verifier` replay; evidence: `.shokunin/audio/reports/round-3/r3-adjudicator.md` and `r3-verifier.md`. Scope is the checked-in fixture workflow, not all future audio tasks.
- [x] No cross-domain bleed; PROVINCE remains accurate. Verified by named non-author `r24-verifier`; evidence: `.shokunin/audio/reports/round-24/r24-verifier.md` (13 held-out classifications and bounded 47-commit first-parent audit).

Each box may be checked only by a named non-author verifier with an evidence
pointer; self-attestation counts as [~].
