# Fleet round-1 calibration measurement — 2026-10-15

## Reproduce

From the audio lane root, run the same counting command for each recorded commit:

```sh
python3 reports/round-1-calibration/count_checklist.py d9aa6f95eed751694337f15ef485f384c3b6c033
python3 reports/round-1-calibration/count_checklist.py HEAD
```

For the after measurement, substitute the full measured work-commit hash recorded in SCORECARD.md for HEAD. The instrument is delivered by this round; it reads the selected revision's SHONEN.md and tracked paths using Git, not the mutable worktree. `before.json` records the observed baseline. The instrument does not need to exist in the historical revision.

## Meaning and falsification

- Fixed denominator: four promotion predicates. `canonical_predicates` compares their exact canonical wording and order; it does not inspect semantic support.
- `boxes_with_resolvable_evidence` counts boxes with at least one cited Markdown path present in the selected Git tree. It is citation reachability, not the number of satisfied gates. Line suffixes are stripped for this count; content and line validity require inspection.
- `checked_without_resolvable_evidence` counts checked boxes with no such path. `checked_boxes`, `asserted_boxes` and `open_boxes` are separate; a missing checklist cannot masquerade as successful withdrawal.
- The probe is read-only and prints observations. Exit 0 means the counting command ran, not promotion, semantic correctness, a clean gate, or audio quality. Invalid revisions or missing SHONEN.md fail through Git/Python errors.
- Decisive counterexample: citing existing README.md for every box yields four reachable citations even while SKILL.md is absent. The critic rejects the inference to four satisfied gates in `critic.md:18-30`. Current dispositions require the actual evidence content, not this ratio alone.

## Current evidence limits

Only historical fixture execution is asserted. Missing SKILL.md, an obsolete documented entry command, and obsolete province write paths leave three predicates open. No current audio battery, perceptual evaluation, engine integration, rights clearance, independent promotion review, or promotion is claimed. The round's dispatched reviewers remain part of the author lane under the canonical protocol.

The external steer is round-1; earlier training rounds in LOG.md and reports/ remain historical, unmodified records. The append-only entry explicitly labels this fleet relaunch rather than inventing a later round number.
