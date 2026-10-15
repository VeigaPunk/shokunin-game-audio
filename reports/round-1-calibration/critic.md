# Round 1 calibration — critic

## Scope and evidence

Read-only review of the proposed checklist calibration, not a promotion review or audio replay. Baseline revision supplied by the assignment: `d9aa6f95eed751694337f15ef485f384c3b6c033`; observations below are worktree reads, not a fresh execution against that commit. No shell commands, tests, battery runs, or judging runtime were executed.

Observed inspection calls: `read SHONEN.md:1-210`, `read SCORECARD.md:1-150`, `read README.md:1-60`; `glob SKILL.md;corpus/README.md;corpus/QUALITY.md` returned all three paths absent. `glob reports/round-2/*;reports/round-3/*;reports/round-24/*;reports/*audio-r1*` found the round-2/3/24 reports but no matching top-level audio-r1 report. Canonical rule references below are under `/home/vgpnk/Projects/kimi-shokunin/skills/shokunin/protocol/`.

- `SHONEN.md:3-6`: four checked claims, all citing old `.shokunin/...` paths. The supplied baseline measurement is four checked boxes and zero boxes with an existing cited evidence path; I did not rerun that counting command.
- `SCORECARD.md:3-10`: no quality rubric; all three initial axis scores unmeasured. `SCORECARD.md:20-24,30-34,40-44` also retains historical improvement/admission claims. Repairing only the top rows does not make these historical claims current measurements.
- `PROTOCOL.md:63-73`: the lane's dispatched subagents remain the lane; named identity alone does not confer independent promotion authority. Box 1 specifically requires content in `SKILL.md`.
- `PROTOCOL.md:413,419-431`: exact canonical seed, four fixed predicates, marks and one indented evidence line per box. `PROTOCOL.md:416` requires a counting command and measured commit for scores. Fleet `/home/vgpnk/Projects/shokunin/AXES.md:11-15` distinguishes depth, coverage, and calibration.

## Counterexamples and findings

### 1. Four resolvable paths are not four supported predicates

**Decisive adversarial input, proposed and not executed:** retain all four canonical checklist predicates and put the same existing `README.md` in each box's evidence line. For a path-count probe this is the four-element evidence input `['README.md', 'README.md', 'README.md', 'README.md']`. `README.md:1-22` is an actual regular file, but lines 10-11 explicitly allow `SKILL.md` to be absent in seed form. With `SKILL.md` absent, the first predicate remains false regardless of the four resolvable citations.

Any probe that counts only successful `exists()` or `is_file()` evaluations yields four successes for this input. That implication follows from the probe definition; no probe was run here. Requiring distinct filenames would not establish semantic support either. A count of paths must not become a count of satisfied promotion gates.

**Smallest correction:** name the metric precisely: four fixed checklist predicates with explicit, evidence-linked **dispositions**, where a disposition may be “not satisfied,” “historical evidence only,” or “not currently verified.” Evidence of a missing prerequisite can justify an open box; it cannot justify asserting that predicate. Record separate counts for readable citations, supported self-assertions, and independently verified gates. Never silently change the denominator when marks are removed.

### 2. Removing checked marks can correct overclaim, but cannot demonstrate sufficiency

The proposed `4 → 0` unsupported checked marks is falsifiable and useful as a withdrawal of unjustified current certification. It is not a gain in audio capability. A document with no boxes at all would also have zero unsupported checked marks, so mark count alone is vacuous without canonical four-box preservation and explicit reasons.

An indiscriminate `[x] → [~]` substitution is unsafe. `[~]` means the lane asserts the predicate, not “the lane has reviewed why the predicate is unmet.” Box 1 must remain `[ ]` while `SKILL.md` is missing. Conservative minimum: keep any other predicate `[ ]` until current support warrants a bounded self-assertion. Box 2 has a candidate historical basis, not a current replay; boxes 3 and 4 require checking current instructions and province accuracy, not copying report titles. No child in this batch can supply `[x]` authority.

**Smallest correction:** regenerate the exact canonical seed with `<name> = audio-shokunin`; preserve all four predicates; use `[ ]` for unmet/unverified predicates and `[~]` only for actually supported self-assertions. Keep detailed negative dispositions and legacy provenance in the integrated report/LOG/SCORECARD rather than altering canonical predicate prose.

### 3. Migration must not manufacture current execution or independence

`reports/round-2/r2-verifier.md:9-14,65-67` records historical commands under `.shokunin/audio/...`, a scoped end-to-end task, and limits. `reports/round-3/r3-adjudicator.md:9-11,23-25` records historical replay and a narrow instruction claim. `reports/round-24/r24-verifier.md:3,29,34-35,56,60` names the old checkout, historical commit `2a198118a527baf749dbd2e23b6667a79a1ccf31`, a 47-commit audit, and explicitly says the normal receipt was existing evidence, not a replay.

These are real readable historical reports. Repointing a citation does not re-execute their commands, transport their audited history to this checkout, establish present instruction executability, or prove reviewer independence under the current contract. Conversely, broken migrated citations do not prove the old experiments never occurred.

**Smallest correction:** preserve historical attribution and original scope; label present work as citation/disposition inspection only. Do not rewrite old reports into current passes or count their self-described “non-author” labels as current promotion authorization.

## Accepted/rejected claims and minimum honest scoring recommendation

- **Accept as bounded targets, not observed after-results:** `0 → 4` evidence-resolvable **dispositions** of the unchanged four predicates, and `4 → 0` unsupported current checked marks, conditional on the delivered document meeting the corrections above. Reject wording that equates the first delta with four satisfied gates.
- **Accept narrowly:** withdrawing unsupported certification can improve self-assessment honesty when the reasons and historical evidence remain accessible. Reject “deleting `[x]` alone proves calibration” or indiscriminate conversion to `[~]`.
- **Reject:** “10/10 local score implies expertise,” global calibration saturation, promotion readiness, new depth/coverage, perceptual quality, or production readiness. Even a perfect four-item bookkeeping ratio is not a rubric for domain expertise.
- **Minimum honest scoring:** retain the initial depth/coverage/calibration axis scores as **unmeasured** absent a grounded axis rubric; report raw fixed-denominator observations separately, with command, measured revision, and worktree/commit distinction. If a local ratio is used, call it checklist-disposition completeness, not a calibration-axis score or verdict. No scalar verdict or admission recommendation is supplied here.

## Impacted axes and residual risks

**Calibration:** primary risk is replacing false certification with false assertion or a saturated bookkeeping score. **Depth/coverage:** no new domain evidence was produced; existing gaps must not disappear merely because metadata improves. **Operability/freshness (diagnostic only):** old executable paths and historical receipt scope can still be stale after citation migration. These are fixable reporting defects within the one calibration move; requiring new audio functionality or promoting on a bookkeeping trade would exceed it. The canonical judge, not this critic, owns any eventual axis verdict.
