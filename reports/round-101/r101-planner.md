# r101 PlannerR101 — claim plan, counting commands, separability (read-only seat; transcribed verbatim by the L1)

Seat: `W2RoundAudio-8.PlannerR101-2` (planner, lane-dispatched — still the lane).

## Axes and observations

- Proposed axes: **C1 calibration**, **C2 coverage** (including the `sources-registry` capability), **C3 depth**.
- Base is `defbe128`. All commands below are read-only baseline inspections; no worktree files were written.
- The dossiers are leads, not evidence for the new SOURCES rows. ExecSources must reopen each row it writes this round.

## Ordered steps and gates

1. Preserve the C1 ledger baseline; add the 87–100 record and correct SHONEN/PROVINCE without rewriting historical reports.
2. Build C2’s lesson, quality bar, index/coverage map, and four knowledge entries; reopen only the SOURCES rows actually used.
3. Add C3 as an opt-in mode with analytic controls; keep normal mode and existing modes unchanged.
4. Verify claims independently, reverting the other claims’ hunks; run the no-harm checks below.

## C1 — calibration

**Before; commands run from the lane root:**
```sh
git show defbe128:SCORECARD.md | awk 'index($0,"## Round ")==1 {n++; if ($3+0 >= 87 && $3+0 <= 100) r++} index($0,"unadjudicated") {u++} END {printf "verdict_sections=%d rounds_87_100=%d unadjudicated_mentions=%d\n", n,r,u}'
git show defbe128:LOG.md | awk 'index($0,"## Round 87")==1 || index($0,"## Round 88")==1 {h++} /GATE FAIL/ {g++} END {printf "round_87_88_headings=%d any_gate_fail_lines=%d\n",h,g}'
git show defbe128:SHONEN.md | awk 'NR <= 12 {printf "%d:%s\n",NR,$0}'
git show defbe128:PROVINCE.md | awk 'NR <= 22 {printf "%d:%s\n",NR,$0}'
```
**Observed:** 86 verdict sections, 0 for 87–100, 0 `unadjudicated` mentions; no 87/88 LOG headings. The two verifier reports contain “GATE FAIL — NOT VERIFIED as a reproducible green landing” (87) and “GATE FAIL as a reproducible green landing” (88). All four SHONEN boxes are `[x]`; PROVINCE says it only writes `.shokunin/audio/**`.

**After counting gate (pasteable):**
```sh
python3 - <<'PY'
from pathlib import Path
import re
s=Path("SCORECARD.md").read_text()
ms=list(re.finditer(r"(?m)^## Round (\d+) verdict\b",s))
r={int(m[1]):s[m.end():ms[i+1].start() if i+1<len(ms) else len(s)] for i,m in enumerate(ms) if 87<=int(m[1])<=100}
u={n for n,b in r.items() if "unadjudicated" in b.lower()}
want={87,88,93,98,99,100}
missing={n for n in range(87,101) if not Path(f"reports/round-{n}/r{n}-adjudicator.md").is_file()}
log=Path("LOG.md").read_text()
for n,q in ((87,"GATE FAIL — NOT VERIFIED as a reproducible green landing"),(88,"GATE FAIL as a reproducible green landing")):
 m=re.search(rf"(?m)^## Round {n}\b",log); assert m
 e=re.search(r"(?m)^## ",log[m.end():]); b=log[m.end():m.end()+e.start()] if e else log[m.end():]
 assert q in b
assert set(r)==set(range(87,101)) and u==want and missing==want
print(f"rounds={len(r)} unadjudicated={len(u)} missing-adjudicator={len(missing)} LOG GATE FAILs=2")
PY
```
Also compare SHONEN’s four checklist lines to the canonical template, with no unsupported `[x]`, and inspect the appended PROVINCE correction for the real `corpus/` and `reports/` scope. **Falsifier:** any 87–100 section missing, wrong adjudicator status, absent/misplaced GATE FAIL text, noncanonical checklist, or stale scope left uncorrected. **No-harm:** C1-only changes stay in SCORECARD/LOG/SHONEN/PROVINCE; do not rewrite prior reports, receipts, fixture tests, or pins.

## C2 — coverage

**Before; command run:**
```sh
for p in corpus/QUALITY.md corpus/lessons/round-101.md corpus/README.md corpus/SOURCES.md corpus/knowledge/2026-10-19-loudnorm-short-sfx-regimes.md corpus/knowledge/2026-10-19-ebur128-dualmono-and-true-peak-on-fixtures.md corpus/knowledge/2026-10-19-godot-wav-import-default-qoa.md corpus/knowledge/2026-10-19-game-loudness-whole-mix-protocol.md; do if git cat-file -e "defbe128:$p" 2>/dev/null; then echo "$p present"; else echo "$p absent"; fi; done
git ls-tree -r --name-only defbe128 corpus/knowledge | awk '$0 ~ /^corpus\/knowledge\/[^/]+\.md$/ {n++} END {printf "existing_knowledge_md=%d\n",n}'
```
**Observed:** all eight target paths absent; 14 existing knowledge entries.

**After counting gate (pasteable):**
```sh
python3 - <<'PY'
from pathlib import Path
new=[Path("corpus/knowledge/2026-10-19-"+s+".md") for s in ("loudnorm-short-sfx-regimes","ebur128-dualmono-and-true-peak-on-fixtures","godot-wav-import-default-qoa","game-loudness-whole-mix-protocol")]
need=[Path("corpus/QUALITY.md"),Path("corpus/lessons/round-101.md"),Path("corpus/README.md"),Path("corpus/SOURCES.md"),*new]
assert all(p.is_file() and p.stat().st_size for p in need)
assert "## Mistakes" in need[1].read_text() and "## Frontier" in need[2].read_text()
assert all(p.name in need[2].read_text() for p in Path("corpus/knowledge").glob("*.md"))
assert all(p.read_text().splitlines()[:3][0].startswith("source: ") and p.read_text().splitlines()[1].startswith("verified-at: ") and p.read_text().splitlines()[2].startswith("recheck: ") for p in new)
print(f"knowledge_entries={len(list(Path('corpus/knowledge').glob('*.md')))} indexed=all target_files={len(need)}")
PY
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF!=13 {n++} END {print "malformed_source_rows=" n+0}' corpus/SOURCES.md
```
Manually gate that every QUALITY criterion cites a lesson, SOURCES rows were opened this round and have lesson-gate evidence, and README/PROVINCE maps agree. **Falsifier:** a missing/unindexed entry, malformed or unopened source row, uncited criterion, absent `## Mistakes`/`## Frontier`, or map mismatch. **No-harm:** preserve the 14 existing knowledge files and all fixtures/receipts; add only the four named entries and assigned docs/report.

## C3 — depth

**Before; command run:**
```sh
printf 'harness_lines='; git show defbe128:corpus/fixtures/measure_audio.py | wc -l
printf 'probe_option_occurrences='; git show defbe128:corpus/fixtures/measure_audio.py | awk '/--probe-truepeak-r101/ {n++} END {print n+0}'
printf 'fixture_tests='; git ls-tree -r --name-only defbe128 corpus/fixtures | awk '$0 ~ /^corpus\/fixtures\/test[^/]*\.py$/ {n++} END {print n+0}'
printf 'canonical_wavs='; git ls-tree -r --name-only defbe128 corpus/artifacts | awk '$0 ~ /^corpus\/artifacts\/[^/]+\.wav$/ {n++} END {print n+0}'
```
**Observed:** 56,096 harness lines, no probe option, 10 existing fixture tests, 17 canonical WAVs. Base `measure()` calls `ebur128=peak=true` but parses integrated loudness only.

**After gate (pasteable):** `python3 corpus/fixtures/test_truepeak_r101.py && python3 corpus/fixtures/measure_audio.py --probe-truepeak-r101`. Test must assert all 17 artifacts expose sample peak, true peak (dBTP), and mono/dual-mono LUFS, plus isolated analytic positive and negative controls; probe must emit its receipt under `corpus/live/runs/`. **Falsifier:** wrong artifact count, missing metric, indistinguishable/bad controls, or probe failure. **No-harm:** keep normal receipt byte identity, canonical WAVs, and existing mode behavior. The base normal receipt SHA is `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b`; r81 records it across 371 landed normal receipts (352 tracked). Keep the probe opt-in and avoid changing common normal receipt fields.

## Separability, lowest axis, blockers

- C1 and C3 are separable. C1’s SHONEN box 4 depends on the PROVINCE correction: correct scope first; use `[x]` only with a named non-author verifier and resolvable evidence.
- C2 has shared-file coupling: README/PROVINCE coverage-map agreement requires a PROVINCE map change, and `sources-registry` capability belongs in SCORECARD; both files are C1-owner paths. Keep the C1 correction/verdict and C2 map/capability as distinct hunks, with ExecLedger coordinating those hunks, so each can be reverted independently.
- C2/C3 couple if K3 cites only the new probe receipt. Cut that dependency with a standalone FFmpeg recheck for K3; the probe then independently demonstrates the harness capability.
- **Lowest-axis blocker:** SCORECARD has no 0–10 scores. “Calibration lowest by defect density” is not a lowest-scoring result; the raw defect counts are not normalized against comparable axis opportunities. Honest wording: **“Scores remain unassigned; lowest-scoring axis is undefined. Calibration is selected as a defect-density priority (inference), not as the lowest-scoring axis.”** Thus the round cannot claim to satisfy the lowest-scoring-axis obligation on that basis.
- No environmental blocker observed. Strict claim separability depends on the shared-file hunk split; SOURCES admission still depends on this round’s actual source openings.
