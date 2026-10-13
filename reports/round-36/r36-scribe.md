# Round 36 scribe — ambience before/after decision table

## Scope and evidence status

This report records the declared Round 36 decision logic and the evidence available in this leaf workspace. The Round 36 declaration in `.shokunin/audio/LOG.md` sets a coverage move: add one original deterministic `ambience_third.wav` only if it fits the specified loop/level/band checks and has a centroid delta of at least 0.10 against **each** existing ambience. The duration comparison is deliberately zero for both pairs; therefore the centroid arm—not duration—must carry each comparison under the unchanged `.020 s OR .10` rule.

At inspection, there was no `reports/round-36/` or `corpus/live/round-36/` evidence directory. I did not run candidate generation, setup, or measurement commands, and have no candidate result to report. This is not a failed fit: no fit was attempted. No source, canonical artifact, shared log, scorecard, or other report was changed.

## Before/after decision table

| Check / decision | Before (declared baseline) | Proposed after (required for a candidate; not observed here) | Decision significance |
|---|---|---|---|
| Canonical fixture count | 16 | 17 only if independently fit and integrated | No admission from this scribe report alone. |
| Existing ambience pair | `ambience.wav` and `ambience_alt.wav`; each 2.0 s, 48 kHz mono PCM16; centroid ~36.6164 Hz and ~58.0192 Hz; loop seam checks pass | Preserve both existing files and measurements; add one original third file | Old 16 hashes/metrics must remain unchanged in later verification. |
| Candidate setup/format | No third candidate in declared baseline | Deterministically generated original `ambience_third.wav`, exactly 2.0 s / 96,000 frames, 48 kHz mono PCM16 | Generation/setup success is separate from passing acoustic proxy fit. |
| Ordinary fit | Existing ambience checks pass; band 5–200 Hz | Candidate peak <.95 FS, RMS >.001, centroid in 5–200 Hz | Any failure means candidate does not fit; report actual failure separately from setup errors. |
| Loop fit | Existing seam checks pass | Endpoint delta <.03 and side-slope mismatch <.001 | These are numeric seam proxies, not proof of seamless perception. |
| `ambience` → candidate | Existing generic `_alt` pair passes centroid arm; duration is equal for old pair | Duration delta exactly 0; relative centroid delta ≥.10 | **Zero-duration arm fails** `.020 s`; centroid arm must pass for OR comparison to pass. |
| `ambience_alt` → candidate | Generic `_alt` pair passes centroid arm; both old durations equal | Duration delta exactly 0; relative centroid delta ≥.10 | **Zero-duration arm fails** `.020 s`; centroid arm must pass independently. |
| Change/admission | 16 canonical fixtures | At most one third ambience fixture, explicit `ambience_family_comparisons`; generic `_alt` loop and thresholds unchanged | Candidate is not canonical until parent integration and verification; no admission finding here. |

## Setup versus fit

No shell command was run, so there are no shell command strings or exit codes to quote. No setup failure occurred, and no setup success or fit result is claimed. In a future candidate trial, report setup/generation/command failures separately from a successfully generated candidate that fails format, level, band, seam, or pair-delta fit. In particular, a missing/malformed path or failed invocation is not evidence that the sound candidate itself failed the numeric fit.

All criteria above are numeric proxies only. This report makes no audition, perceptual-quality, production, rights, engine, publishing, or promotion claim.
