# Round 1 calibration — planner evidence and proposed rubric

## Findings and contract

Only proposed move: **calibration of migrated promotion evidence**. No audio/decoder functionality, replay, promotion decision, or changes to existing files are part of this slice. This report is lane-author evidence, not an independent promotion verification.

Evidence inspected:
- `SCORECARD.md:3-10` leaves depth, coverage, and calibration unmeasured and explicitly distinguishes row counts from quality scores. `SCORECARD.md:16-24` contains historical verdicts, not current re-execution.
- `SHONEN.md:3-6` has four checked boxes citing legacy paths. Its header, box wording, and inline evidence also differ from the canonical seed.
- Canonical `/home/vgpnk/Projects/kimi-shokunin/skills/shokunin/protocol/PROTOCOL.md:63-73` defines substantive gates and excludes the lane's dispatched subagents from independent verification; `:327-346` requires resolvable evidence, commands for numbers, and distinguishes re-execution from historical claims; `:406-431` requires canonical SHONEN form and reproducible 0–10 score claims; `:483-490` requires measured revisions and preserves file-contract obligations.
- Fleet `/home/vgpnk/Projects/shokunin/AXES.md:11-15,25-39` defines the three owned axes and score fields. Canonical skill `skills/shokunin/SKILL.md:70-78` separates numeric measurements from categorical axis verdicts; `protocol/LEARNING.md:39-43` also excludes dispatched subagents from outside spot-checks.

### Observed read-only count

Executed from the lane root; exit 0. Checklist bytes came from supplied baseline `d9aa6f95eed751694337f15ef485f384c3b6c033`; path existence was inspected in the current working tree, **not a reconstructed baseline filesystem**:

```sh
python3 -c 'import pathlib,re,subprocess; rev="d9aa6f95eed751694337f15ef485f384c3b6c033"; text=subprocess.check_output(["git","show",rev+":SHONEN.md"],text=True); rows=[s for s in text.splitlines() if re.match(r"^- \[[x~ ]\] ",s)]; print("input_commit="+rev); print("boxes="+str(len(rows))); print("checked="+str(sum(s.startswith("- [x]") for s in rows))); ok=0; exec("for i,row in enumerate(rows,1):\n refs=re.findall(r\"`([^`]+\\.md)`\",row)\n present=[p for p in refs if pathlib.Path(p).is_file()]\n ok+=bool(present)\n print(f\"box={i} refs={refs!r} existing={present!r}\")"); print("boxes_with_existing_cited_path="+str(ok)); print("required_files="+repr({p:pathlib.Path(p).is_file() for p in ["SKILL.md","corpus/README.md","corpus/QUALITY.md"]}))'
```

Observed: `boxes=4`, `checked=4`, every box `existing=[]`, `boxes_with_existing_cited_path=0`; the three required files each returned `False`. A targeted `glob` for those exact files also reported them missing. These are metadata observations, not audio tests. The existence count is a **diagnostic only**: replacing every citation with an unrelated existing README would raise it without satisfying a single gate.

## Proposed axes, numeric rubric, and ordering

Retain owned axes **depth / coverage / calibration**, increasing direction. Select **calibration first** because its contradiction is immediately falsifiable. Initial evidence is insufficient to rank actual domain competence: `depth = coverage = calibration = unmeasured`. This is an uncertainty tie, not evidence of equal expertise. No depth-versus-coverage priority is established; leave those tied after selecting calibration. Do not invent fractional ordering or expand this round into either axis.

For the required numeric field, propose this explicitly named **bounded evidence-assurance rubric v1**, not an expertise scale:

`S(axis) = (5 / n) × sum(A_i + E_i)`; each indicator is 0 or 1 and `E_i <= A_i`.

- `A_i = 1` only when the required current evidence unit exists, a resolvable audit note names exact source locations and gaps, its claim is bounded to what was inspected, and all unit-specific conditions below hold. Otherwise 0. An unknown condition earns no credit, without becoming a claim of domain inability.
- `E_i = 1` only when a named **outside, non-author** reviewer independently checks that same current unit and records agreement against the measured revision. A self-described legacy verifier or this round's dispatched subagents cannot supply this half. Agreement that a gap is honestly disclosed is not approval of the substantive promotion gate.
- Freeze the units and indicators before measurement, retain the binary audit rows, and attach the counting command and exact measured commit to each adopted score. Score arithmetic is `5 * (sum(A) + sum(E)) / len(A)`; do not round to integers. Author-only maximum is 5; 10 means this bounded evidence audit has outside agreement, never domain mastery or promotion.

| Axis | Fixed units and condition for author credit | Initial evidence-only score under proposed rubric |
|---|---|---|
| depth | `n=3`: one real decision table, error-pattern list, and checklist in current `SKILL.md`, each actionable, sourced with resolving citations, and inspected against its claim. A mere heading or source row count earns nothing. | `0/10` documented-evidence floor: required SKILL is absent, so `A=(0,0,0)`, `E=(0,0,0)`. This says nothing about technical detail elsewhere. |
| coverage | `n=2`: the two coarse declared content families, SFX and soundtrack (`PROVINCE.md:3-5`). Each needs a current `corpus/README.md` mapping its declared subareas and gaps to resolving, actionable SKILL/corpus evidence. All declared subareas must be addressed or explicitly marked unexplored; an honest gap does not count as governed coverage. | `0/10` documented-evidence floor: index and SKILL absent, so `A=(0,0)`, `E=(0,0)`. This is not “0% of all audio covered”; the coarse family units cannot establish within-family breadth. |
| calibration | `n=4`: one unit per canonical promotion box. Each needs canonical form, a current resolving audit pointer, explicit distinction between historical claims and present support, missing prerequisites named, and a justified mark. `[x]` requires established outside authority; `[~]` requires a bounded substantive author assertion; `[ ]` records an unsupported gate without claiming success. Correctly documenting a gap may earn calibration credit, never depth/coverage/gate credit. | Before `0/10`: four broken checked assertions, `A=(0,0,0,0)`, `E=(0,0,0,0)`. Conditional after full four-box author audit: `5/10`, `A=(1,1,1,1)`, `E=(0,0,0,0)`. **After is proposed, not observed here.** |

These zeros are proposed reproducible evidence floors, not measured expertise scores or replacements silently applied to the existing rows. Leaving every numeric field simply unmeasured would leave the AXES/file-contract numeric requirement unresolved; the parent should either adopt the explicitly proxy-labeled rubric or record that conformance limitation. Do not call any scalar a round verdict. Missing `corpus/QUALITY.md` remains a separate documented file-contract gap; neither this score nor a calibration correction repairs it.

## Representative case: box 2, then four-box audit

Box 2 is the smallest useful end-to-end case because both a migrated report and a log pointer survive:
1. **Before:** `SHONEN.md:4` claims `[x]` using `.shokunin/audio/reports/round-2/r2-verifier.md`; the exact citation does not resolve in the observed tree.
2. **Locate evidence:** `reports/round-2/r2-verifier.md:3-14` records historical command outcomes; `:61-67` recommends box 2 with explicit local-fixture limitations. `LOG.md:28-35` records the dispatch and historical closure. In particular `LOG.md:30` shows the lane dispatched `r2-verifier`; calling itself non-author does not override the current independence rule.
3. **Present assessment:** a surviving historical report is evidence that execution was reported, not a fresh execution of the migrated checkout. The report's commands retain legacy paths. Parent may use **at most `[~]`** for a narrowly explained historical logged end-to-end assertion, with current report and log pointers, never `[x]`; use `[ ]` if the substantive claim cannot be supported to the intended scope. This slice does not validate receipts or reproduce audio results.
4. **Proposed after observable:** one canonical box with an indented resolving audit note, no independent-verification claim, and the historical/current distinction preserved. This earns at most one author calibration unit (1.25/10), not a promotion-box pass.
5. **Falsification:** retaining `[x]`, treating a relocated report as fresh replay, omitting the historical limitations, or merely citing an unrelated existing file invalidates author credit for this unit.

Generalize the same audit without broadening the move:

| Box | Current observation and useful surviving pointer | Proposed conservative assessment |
|---|---|---|
| 1 | `SHONEN.md:3` cites missing `.shokunin/reports/audio-r1-verifier.md`; current SKILL is absent. A targeted `reports/**/audio-r1-verifier.md` search found no migrated match. | `[ ]`; do not replace missing craft content with fixture counts. |
| 2 | Historical report and log above survive; old command paths and lane-dispatched verifier prevent current independent certification. | At most historical `[~]`, otherwise `[ ]`. |
| 3 | `reports/round-3/r3-adjudicator.md:9,23-25` describes historical no-oral-context replay; `reports/round-3/r3-verifier.md:3,40-44` bounds it to numerical fixtures. Their legacy invocations are not current executable instructions. | `[ ]`; current executable migrated instructions are unestablished. |
| 4 | `reports/round-24/r24-verifier.md:3,29-45` limits its audit to old endpoints/cases, not current state. `PROVINCE.md:17,21,31` still carries migrated-away scope/evidence paths. | `[ ]`; preserve the historical bounded result without certifying current province accuracy or all behavior. |

## Ordered integration advice and evidence gate

1. **Pin input evidence and declare rubric/axis.** Use baseline above, `SCORECARD.md:1-24`, count output, and canonical rules; parent authors its plan. No UFO runtime, routing change, or nested delegation is needed.
2. **Complete box 2's bounded audit first.** Evidence: current report/log locations above; demonstrate one correct canonical assessment and resolving current pointer before repeating the pattern.
3. **Apply the four-box audit and canonical form.** Parent alone edits SHONEN, preserving seed wording and using indented evidence lines. Record missing SKILL/index/quality files and stale province scope as gaps, not repairs performed this round. Evidence: per-box table and absence sweep above.
4. **Record only the calibration delta.** Proposed observable: unsupported independent checked assertions `4 → 0`; adequately documented current assessments `0 → 4`; outside verifications supplied by this batch `0 → 0`; local calibration assurance `0/10 → 5/10` only if all four author predicates are actually met. Depth and coverage retain their bounded evidence floors/unknown expertise; no new audio capability is claimed. Append the correction rather than rewriting historical LOG entries.
5. **Parent's single bounded final gate.** Re-read canonical seed/mark placement; check all four audit pointers for relevance and resolution, read the actual evidence rather than count files, recompute the binary table/score, and attach the delivered commit to the measurements. Fail the proposed calibration claim for any surviving unsupported `[x]`, unrelated placeholder citation, unlabelled old result presented as current replay, noncanonical seed, or unrecorded required-file gap. Any parent smoke is separate evidence and must report only what actually ran; planner ran no build, test, formatter, or audio battery.

## Accepted/rejected claims, risks, blockers

**Accepted:** the observed checklist overstates its currently resolving evidence; migrated historical reports can support a bounded audit; calibration has the cheapest falsifiable tie-break. **Rejected:** path existence proves gate satisfaction; legacy “non-author” labels establish present independence; an author audit or 5/10 proxy establishes expertise, production/perceptual quality, or promotion.

Risks: a coarse rubric can reward paperwork, and family-level coverage units conceal uneven knowledge. Fixing pointer syntax alone can launder unsupported claims; assessment relevance and gate prerequisites are required. Numeric floors are rubric-relative, not portable comparisons with old rounds or other lanes. Concurrent working-tree changes are not baseline-commit measurements; parent must pin its final measured revision. Resume continuity, if asserted by the parent, remains an unverified continuity assumption, not proof of execution or authority.

No blocker to the proposed calibration-only documentation move. Current gate confirmation is blocked by absent required craft/index artifacts, stale scope/instruction paths, and lack of qualifying outside verification; do not solve those by expanding this round or marking boxes checked. This report supplies a plan and evidence, not admission, integration, shipping, or a completion verdict.
