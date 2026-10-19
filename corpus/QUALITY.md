# QUALITY — audio-shokunin admission bar

Tier definitions live in [corpus/SOURCES.md](SOURCES.md) (contract v1); this file defines claim and round admission. A round without an adjudicator is `unadjudicated`, not admitted.

## Criteria

| id | admission criterion | lesson |
|---|---|---|
| Q1 | An entry opens with all three provenance fields: `source:`, `verified-at:`, and `recheck:`. Missing or incomplete fields block admission. | lesson: `corpus/lessons/round-101.md#M11`, `#M13` |
| Q2 | Every audio claim is a measurement backed by a re-runnable command or a named receipt, never by listening alone. Every reported number is re-derivable by a verifier or explicitly marked attestation-only. This is the lane's own rule: [seed.md:14-20](knowledge/seed.md#L14). | lesson: `corpus/lessons/round-101.md#M11` |
| Q3 | Pin tool and document versions; source-line citations must resolve at the pinned revision actually checked, not a moving branch such as `master`. | lesson: `corpus/lessons/round-101.md#M13` |
| Q4 | A Tier C source is never the sole support for an admitted claim. | lesson: `corpus/lessons/round-101.md#M11` |
| Q5 | The recheck reproduces the stated numbers on this host, and every count in an entry is derived from its own observed table or a re-run command, never carried from a brief. A mismatch, missing prerequisite, or non-reproducible value blocks the claim or is stated as a limitation; it is not silently accepted. | lesson: `corpus/lessons/round-101.md#M11`, `#M15` |
| Q6 | A regime or threshold claim names its actual trigger. Do not state input length as the cause when a gate or other mechanism is the trigger. | lesson: `corpus/lessons/round-101.md#M14` |
| Q7 | Every gate has a positive control; a zero-energy signal must not satisfy a content or TERM gate. | lesson: `corpus/lessons/round-101.md#M7` |
| Q8 | Name co-tenancy as a confound wherever arms share host resources; a single red run under co-tenancy is not a verdict. | lesson: `corpus/lessons/round-101.md#M8` |
| Q9 | Disclose every arm actually executed in the round's own record at run time. Post-hoc disclosure is a calibration failure. | lesson: `corpus/lessons/round-101.md#M3` |
| Q10 | Physical-network emission is default-off. An arm may emit only when its invocation explicitly names the interface. | lesson: `corpus/lessons/round-101.md#M4` |
| Q11 | A round without an adjudicator is `unadjudicated` and cannot be called ADMIT; a fold or later green repair does not replace a verdict. | lesson: `corpus/lessons/round-101.md#M1`, `#M2`, `#M25` |
| Q12 | A cited commit is reachable from the published branch, or its evidence is explicitly marked `branch-scoped`. | lesson: `corpus/lessons/round-101.md#M6` |
| Q13 | Verdict and evidence headers give the observation date. Planned wave dates are not observation dates. | lesson: `corpus/lessons/round-101.md#M10` |
| Q14 | Lane commits use `audio-shokunin <audio@shokunin.local>` identity; CI or another identity is not substituted. | lesson: `corpus/lessons/round-101.md#M5` |
| Q15 | Generated test work-products stay under `corpus/live/<round>/`; root-level generated artifacts are not admitted. Ignore regenerable scratch by class and prove the census before admission. | lesson: `corpus/lessons/round-101.md#M9`, `#M12` |
| Q16 | A change to a dispatch or selector expression (mode/suffix chains, flag routing) is admitted only with an exhaustive old-vs-new evaluation over every input it routes, showing identical outputs except the intended new arm; a diff-size or "insertions only" argument is not evidence. | lesson: `corpus/lessons/round-101.md#M16` |
| Q17 | For a filter-rate claim, distinguish the selected filter's negotiated rate from the downstream output stream; tap immediately after the named filter to verify the stage. | lesson: `corpus/lessons/round-101.md#M17` |
| Q18 | Preserve a primary source's qualifying words and scope; do not generalize a phase-specific example into a phase-independent limit. | lesson: `corpus/lessons/round-101.md#M18` |
| Q19 | State the complete quality-criteria revision applied by a gate, including criteria added during the same round. | lesson: `corpus/lessons/round-101.md#M21` |
| Q20 | Each source row's `used-by` lists every knowledge entry and lesson that cites it; a valid cited path is not enough if it is omitted from the row. | lesson: `corpus/lessons/round-101.md#M22` |
| Q21 | Truepeak mode MUST read existing canonical inputs without invoking `build_artifacts.py` or rewriting `corpus/artifacts`; generated controls, FFmpeg logs, and its receipt MUST all stay under `corpus/live/round-101-truepeak/`. | lesson: `corpus/lessons/round-101.md#M23` |
| Q22 | A control acceptance oracle MUST be independent of the signal-generation and measurement paths; for the 12 kHz controls use name-keyed analytic references (phase-π/4: ≈+3.0103 dB, phase-0: ≈0.0 dB, ±0.08 dB). A quantized-PCM expectation MAY be retained only as a separate accuracy cross-check, not as the acceptance threshold. | lesson: `corpus/lessons/round-101.md#M24` |
