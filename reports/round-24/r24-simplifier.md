# Round 24 — simplifier: province decision checklist

## Minimal checklist

For each proposed task, identify the requested **artifact/change** and **write path**, then apply these checks in order:

| Decision | Test | Examples |
|---|---|---|
| **In province** | Is the deliverable audio content or headless audio analysis for SFX/music, and does it stay within `.shokunin/audio/**` plus this lane’s own `.shokunin/reports/round-N/audio.md` final report? | Generate or measure an audio fixture; inspect duration, loudness, spectrum, or loop continuity; update audio fixture-analysis code or audio knowledge. |
| **Refuse / out of province** | Does it require publishing/store submission, rights clearance, engine-source changes, game-mechanics changes, or narrative-canon changes? | Release an asset; certify sample rights; change runtime playback/mixing code; change a rule or story fact. Do not perform that part. |
| **Uncertain / split** | Is the deliverable mixed, or can its boundary not be established from the request and allowed evidence? | An adaptive-audio task may request a measured audio fixture (in scope) and an engine behavior change (refused). Keep only the separable in-scope work; otherwise stop and ask the operator to resolve the boundary. |

Do not infer permission from an audio-related label. Classify the requested change, not the requester’s intent. A reference/sample requires the province’s cited reference ledger; attribution, rights, and training permission are distinct. A numeric proxy can support only the claim it measures; it does not establish perceived quality, clearance, playback behavior, or production readiness.

## Evidence boundary

The current tracked artifact inventory contains **13 WAVs**. This is a corpus count, not proof of all audio tasks or any perceptual, runtime, licensing, or production property. Git history inspected below is the checked branch history, not a universal audit of every branch, untracked file, external consumer, or future action. This checklist is a routing aid, not a new approval process or promotion claim. SHONEN box 4 remains unchecked unless the designated non-author whole-lane verifier independently meets its evidence condition.

## Commands run

Commands below were run from the repository root; status is the process exit code. An initial tool-quoting attempt failed and was not used as evidence; corrected commands and outcomes are listed.

- `git status --short --branch` — **0**; branch `craft/audio-r1`; existing modified `.shokunin/audio/LOG.md` and untracked round-24 directory observed.
- `git log -1 --format='%H %s'` — **0**; HEAD is `2a198118a527baf749dbd2e23b6667a79a1ccf31` (`Audio round 23: final calibration report`).
- `git rev-parse 2a198118a527baf749dbd2e23b6667a79a1ccf31` — **0**; the declared clean-before commit resolves.
- `git show --stat --oneline 2a198118a527baf749dbd2e23b6667a79a1ccf31` — **0**; commit changes only the round-23 final report.
- `git diff --name-only 2a198118a527baf749dbd2e23b6667a79a1ccf31..HEAD` — **0**, empty; no committed changes after that before-state at inspection.
- `git log --format='%h %s' -12 -- .shokunin/audio` — **0**; inspected latest 12 commits touching this path.
- `git log --name-only --format='commit %h %s' -8 -- .shokunin/audio` — **0**; inspected names in the latest eight path-touching commits. This is limited branch history, not an exhaustive all-branch scope audit.
- `git ls-files -- .shokunin/audio/corpus/artifacts` — **0**; 13 tracked canonical WAV paths.
- `git ls-files .shokunin/audio/corpus/artifacts/*.wav | wc -l` — **0**; count 13.
- `git diff --check` — **0**.

No source, artifacts, shared docs, or other reports were changed by this lane. No publishing, clearance, engine/game-mechanics/narrative mutation, or unmeasured perceptual claim is made.
