# Round 24 — audio boundary preparation

## Classification rule

Classify the requested *change and its effects*, not just the file extension or the person asking. A task is audio-province work only when its deliverable is audio content or headless audio analysis, and all writes stay within `.shokunin/audio/**` plus this lane’s own `.shokunin/audio/reports/round-24/r24-boundary.md` (for this leaf; normal round-level reports belong under `.shokunin/reports/round-N/audio.md`). Respect existing source/read-only boundaries. A task that also changes another province’s state is not made audio-only by putting the edit in an audio folder.

| Classification | Audio-domain examples | Boundary / disposition |
|---|---|---|
| **Allowed** | Generate or revise an SFX, ambience, soundtrack loop/stem, or adaptive-layer audio asset; create audio-only source-generation fixtures; run or document headless duration, loudness, spectral, format, or loop-seam checks; preserve reproducible measurements and hashes. | Keep work and generated artifacts inside `.shokunin/audio/**`; report in the lane’s own report location. Claims must match measured proxies and tested files. The current fixture corpus has 13 canonical WAVs; its gates are evidence about those fixtures, not a general sound-quality or production guarantee. |
| **Refused** | Publish, submit to a store, or represent an asset as cleared for use; perform or assert sample-rights clearance; edit engine source or integration/runtime behavior; change game mechanics or narrative canon. | Do not perform the out-of-province action or imply that audio checks authorize it. Route to the responsible owner. Audio provenance/attribution notes do not constitute rights clearance; a ledger/reference does not grant permission. |
| **Uncertain / hold for scope decision** | Request mixes sound design with gameplay timing/trigger logic; asks for an in-engine mix or runtime behavior change; asks whether a sample/reference may be used, trained on, or distributed; asks for “better,” “immersive,” “natural,” or “professional” sound without a stated measurable proxy; asks for an audio file whose intended use or write target is unclear. | Ask for the exact deliverable, intended use, owner, write paths, and measurable acceptance proxy. Until clarified, do not change files or make the external/subjective claim. Split a separable audio-only task from the refused/uncertain portion; route the rest to the relevant owner. If the split is not clear, treat as refused for this lane rather than silently taking it on. |

## Ambiguous cases

- **Audio asset versus game behavior:** composing a short cue or preparing timing variants as audio files is allowed. Changing when the game triggers the cue, adding a gameplay response, or modifying an engine mixer is refused here, even if motivated by sound quality. If a requested timing is a creative constraint on the audio file only, clarify that no runtime logic is being changed.
- **“Make it sound better”:** allowed only as an audio production task after agreeing on a measurable proxy or concrete revision brief. Existing duration/loudness/spectral/seam measurements can support those specific properties; they do not establish perceived quality. If acceptance is solely subjective, mark uncertain and do not claim verification.
- **Sample/reference material:** analyzing a cited reference or documenting provenance is not clearance. Unknown ownership, licenses, training permission, attribution requirements, or intended distribution stay uncertain and require the responsible rights decision; this lane must not decide that use is lawful.
- **Export/format request:** generating a requested audio file within the audio tree can be allowed. The current tested native PCM16/PCM24 behavior is limited to its fixtures and must not be generalized into broad codec, compatibility, or quality assurance. Changes to a downstream engine importer or build pipeline are outside this province.
- **Mixed-path deliverable:** an audio asset under the permitted tree plus edits to game, engine, publishing, or narrative files is cross-domain work, not an allowed audio task. Keep only a genuinely separable audio-only request; otherwise hold and route.
- **Evidence and history:** a green fixture run establishes only the measured checks for that run. A repository-history audit can describe the commits and paths actually inspected; it cannot establish that all past, untracked, external, or future behavior is free of cross-domain work.

## Evidence limits and decision

The round-24 proposal is a checklist for classification, not a promotion or blanket authorization. The round-23/22 record describes a 13-file source-generated fixture set and measured gates; those checks cannot establish subjective perception, sample rights, publishing readiness, engine compatibility, gameplay correctness, or narrative fit. SHONEN box 4 remains unchecked unless a named non-author verifier applies the checklist to held-out tasks and explicitly scopes any history audit to inspected tracked history. A discovered cross-domain edit or unresolved boundary means leave the box open and report the ambiguity; do not broaden this lane’s writes.

## Commands run in this preparation

- `git status --short --branch` — exit **0**; branch `craft/audio-r1`; working tree already had `.shokunin/audio/LOG.md` modified. This is a point-in-time status, not an attribution of the modification.
- `git log --oneline --name-only -12` — exit **2**; output displayed recent history beginning with round 23 and round 22 paths, but the command did not exit successfully. I do not treat it as a complete or successful history audit.

No source, shared documentation, artifacts, other reports, commits, or publishing state were changed by this leaf. This report is not a whole-history finding; a verifier must perform and document its own scoped review.
