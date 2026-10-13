# r35-scribe — movement before/after and fit/setup ledger

## Decision table

| Item | Before (declared clean baseline) | Proposed after (Round 35 target) | Decision/evidence status |
|---|---|---|---|
| Canonical fixture count | 15 | 16 if admitted | No candidate or integration evidence found in the declared Round 35 paths during this task. |
| `movement.wav` | 0.24 s; centroid about 11,934 Hz | Unchanged | Baseline values are the LOG declaration, not independently remeasured here. |
| `movement_alt.wav` | 0.36 s; centroid about 12,024 Hz | Unchanged | Baseline values are the LOG declaration, not independently remeasured here. |
| Existing movement pair | Duration delta 0.12 s; centroid relative delta about 0.0075 | Generic `_alt` comparator/thresholds remain unchanged | LOG says pair passes existing duration OR branch; centroid arm does not pass. |
| `movement_third.wav` | Absent from declared baseline | Target 0.30 s, band 100–16,000 Hz; add `SPECS` entry and explicit comparisons to both existing movement fixtures | Not generated, measured, or integrated in evidence available here; admission undecided. |
| New pair comparisons | None declared | Each candidate-to-baseline duration delta nominally 0.06 s (>0.020 s); selection additionally requires centroid relative difference >=0.10 for each baseline | Targets only; do not treat nominal duration as measured result or as evidence that centroid criterion fits. |
| Preservation | 15 older canonical WAVs and generic behavior | Preserve all 15 older hashes/metrics, generic `_alt` logic, thresholds, prior replay/invalid statuses | No verification run by this scribe. |

## Setup errors versus candidate fits

- **Candidate fit attempts:** None found or run by this scribe. There is no candidate measurement, hash, or pairwise receipt to classify as fit/failure. The proposed 0.30 s duration and centroid requirements above are declared criteria, not results.
- **Setup/path inspection:** `find .shokunin/audio/reports/round-35 -maxdepth 1 -type f -print` exited 1 because the report directory did not yet exist. This is a missing-path inspection result, not a failed audio setup or candidate fit. `find .shokunin/audio/corpus/live/round-35 -maxdepth 3 -type f -print` exited 0 and printed no files. `git status --short` exited 0 and showed the pre-existing ` M .shokunin/audio/LOG.md`; this scribe did not modify it.
- No audio-generation, project measurement, test, or replay command was run. Therefore there are no candidate setup/fit command receipts to quote.

Only numeric proxies and the declared round specification are reported. No audition, perceptual or quality judgment, production/rights/engine/publishing readiness, or promotion claim is made. This is a leaf report only; the parent must integrate and verify any candidate before it is canonical.
