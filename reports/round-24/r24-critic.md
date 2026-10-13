# Round 24 — critic: falsification and no-bleed limits

## Verdict on the checklist / SHONEN box 4

The draft decision matrix is useful as a conservative task-routing aid, but it does **not** establish SHONEN box 4. It can make future classification more explicit; it cannot prove historical behavior, universal absence of cross-domain effects, nor that PROVINCE accurately captures every relevant boundary. Box 4 should remain unchecked absent a named non-author review with a bounded history audit and explicit treatment of exceptions. Even that evidence can support only a bounded finding, not a universal no-bleed claim.

## Attempts to falsify / ambiguity cases

1. **“Only writes `.shokunin/audio/**` and its own reports” is not a complete write rule.** `.shokunin/reports/round-N/audio.md` is outside that glob, while the reports for leaf lanes live under `.shokunin/audio/reports/`. The proposed checklist does name both locations, but should say exactly which report belongs where and prohibit other writes (including generated files, logs, commits, and external side effects) unless separately authorized. The phrase “plus this lane’s own report location” is especially easy to read as a general exception.
2. **Allowed adaptive-layer work is not necessarily audio-only.** Creating a stem/layer file is in-scope; changing layer selection, synchronization, triggers, runtime mixer behavior, or a build/import pipeline is not. A requested asset can also encode an unapproved narrative brief or be intended for an unlicensed sample. A file extension or destination directory does not establish ownership of its effects or provenance.
3. **“Uncertain” is not always safely resolvable by asking the user.** Rights, store/publishing, game mechanics, and narrative decisions require the responsible owner; the lane should not convert a user assertion into clearance or canon. Split only if the audio deliverable is genuinely separable, and do not make a “safe” audio change that implicitly implements the refused decision.
4. **Subjective requests are not automatically uncertain forever, nor automatically allowed.** The checklist should distinguish producing an exploratory asset from claiming it is “better,” “immersive,” or “professional.” Agreeing on a proxy does not make that proxy valid for the subjective construct; it supports only the measured property. A loudness or spectral target, for example, cannot silently stand in for perceived quality.
5. **History evidence can be incomplete even when commands succeed.** A local tracked-path audit misses untracked/ignored files, deleted work, external tools or services, unpublished branches not fetched, other repositories, and effects of runtime/build integration. A clean diff or a sequence of audio-only commits cannot prove the absence of cross-domain behavior. “No bleed found” must name inspected refs, commit range, path classes, and limitations.
6. **PROVINCE itself has unresolved breadth.** “Adaptive layers” can describe content creation or engine behavior; “loudness” and “loop-seam continuity” name measurement topics but not the checker’s limits. The current fixture set is synthetic/source-generated; passing it does not validate authored production content or actual game use. This does not necessarily make the province inaccurate, but it prevents a broad interpretation.

These are classification counterexamples/limitations, not evidence that a cross-domain mutation occurred. A held-out test should include at least: an audio file plus runtime trigger request (mixed); a stem constrained by unapproved lore (route lore decision); a sample with unclear training/distribution permission (hold for rights owner); a request for a measurable level change framed as “better” (separate measurable result from subjective claim); an audio-only file exported outside the permitted tree (write-scope violation); and a build/import edit framed as “audio compatibility” (engine/build owner). Mark unresolved rather than force a binary audio/refused answer.

## Scoped repository observations (not a whole-lane certification)

I observed the current checkout at `craft/audio-r1`, HEAD `2a198118a527baf749dbd2e23b6667a79a1ccf31`. The pre-existing worktree already had `.shokunin/audio/LOG.md` modified when first checked; I did not attribute or edit it. `git log --all -- .shokunin/audio` lists 25 commits in the available local refs. Inspecting changed paths for those commits found two commits with paths outside `.shokunin/audio/**`: the mint commit also changes `.shokunin/MANIFEST.json` and `.shokunin/mints/audio.md`; round 1 adds `.shokunin/reports/audio-r1-verifier.md`. The round-1 report is an explicitly planned verifier report; the mint files are initial lane setup/manifest. These are apparent authorized/documented exceptions, not evidence of game/engine/lore mutations, but they falsify a literal claim that every lane-related commit writes only `.shokunin/audio/**`.

The recent history and tracked paths I sampled showed no `game*`, `engine*`, `lore*`, or `.shokunin/l0-questions.md` path. This is only a path-name scan of local tracked history, not semantic review of every blob or proof that no cross-domain effect occurred. The verifier should inspect the precise declared range, including full changed-path inventory and any relevant diffs, and report these expected report/mint exceptions rather than silently counting them as audio-tree-only.

## Exact shell commands and statuses run here

- `git status --short --branch` — **0**; reported `## craft/audio-r1` and pre-existing ` M .shokunin/audio/LOG.md`.
- `git log --oneline --decorate -12` — **0**; HEAD was `2a19811`, round-23 report commit.
- `git rev-parse HEAD` — **0**; `2a198118a527baf749dbd2e23b6667a79a1ccf31`.
- `git show --stat --oneline 2a198118a527baf749dbd2e23b6667a79a1ccf31` — **0**; report-only round-23 final commit.
- `git log --format='%h %s' --name-only 2a198118a527baf749dbd2e23b6667a79a1ccf31..HEAD` — **0**, empty range.
- `git diff --name-status 2a198118a527baf749dbd2e23b6667a79a1ccf31..HEAD` — **0**, empty range.
- `git diff-tree --no-commit-id --name-status -r 2a198118a527baf749dbd2e23b6667a79a1ccf31` — **0**; `A .shokunin/reports/round-23/audio.md`.
- `git log --format='%h %ad %s' --date=short --name-only -- .shokunin/audio .shokunin/reports/round-1/audio.md .shokunin/reports/round-2/audio.md | head -250` — **0**; sampled recent commit/path records.
- `git log --format='%h %s' --name-status -40` — **0**; output begins with round 23/22 history.
- `git log --reverse --format='%H %s' --all -- .shokunin/audio | head -5` — **0**; showed mint and rounds 1–4.
- `git log --format='%H %s' --all -- .shokunin/audio | wc -l` — **0**, count **25**.
- `git branch -a --contains HEAD` — **0**; only `craft/audio-r1` was listed.
- `git log --all --format='%H' -- .shokunin/audio` — **0**; listed 25 relevant commits. For each hash from this list I ran `git show --format= --name-only <hash>` (each **0**) and compared returned paths to `.shokunin/audio/**`; two commits had the documented exceptions described above.
- `git log --all --format='%h %s' --name-status -- .shokunin/audio | grep -E '^([A-Z][[:space:]]+)?(game|lore|engine|\.shokunin/l0-questions|\.shokunin/reports)' | head -60` — **0**; no matching output. This is a path-pattern filter, not a semantic proof.
- `git ls-files | cut -d/ -f1-3 | sort -u | head -60` — **0**; broad top-level inventory, not an exhaustive external-workspace inventory.
- `git ls-tree -r --name-only HEAD .shokunin/audio/corpus/artifacts/ | wc -l` — **0**, **13** canonical paths.

One earlier scoped draft (`r24-boundary.md`) reports `git log --oneline --name-only -12` exit 2; I did not reproduce that exact command here, so I cannot validate its stated status. The successful history commands above are the evidence I rely on.

No source, province, checklist, canonical artifact, other report, commit, push, publication, or clearance was changed by this lane. This is a falsification critique and bounded checkout observation, not a SHONEN verifier decision or whole-lane history certification.
