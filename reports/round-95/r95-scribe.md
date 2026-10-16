# r95 scribe — custody audit of the r95 landing

Seat: SCRIBE (leaf). Lane repo `/home/vgpnk/Projects/shokunin/audio-shokunin`.
Dispatched HEAD was `ffeb5155`; HEAD at audit time is **`021bde86`**
(`r89 adjudicate: ADMIT-with-findings, gate closed at 5755be5b`, parent
`ffeb5155`). Both were audited; the r95 landing is `ffeb5155`.

**Zero tracked writes. Zero commits.** The only write this seat makes is this
report file itself (`reports/round-95/r95-scribe.md`, new, untracked). Scratch
was written under `/tmp/r95audit/` only.

Not judged: this seat reports; the canonical judge decides.

## 1. Custody verdict

**INTACT-with-findings.** The integrator's block-identity claim survives
re-verification, with one honesty correction (§4.1: 4 extra blank lines, and
§4.2: the green receipts bind the *branch* bytes, not the *landed* bytes).

| claim under audit | verdict |
| --- | --- |
| wt-r95 branch commit reachable | PASS — `refs/heads/wt-r95` = `2f46b1ed` |
| r95 family block in HEAD byte-identical to author worktree bytes | PASS with caveat — block *content* verbatim; +2 leading blank lines |
| 3 splice regions carry both families' terms correctly | PASS — 5 wiring hunks, not 3 (§4.6); both families present in every shared line |
| `r95jack.c` matches wt-r95 blob | PASS — `55d4d411…` identical in HEAD/`ffeb5155`/`2f46b1ed`/both worktrees |
| `r95-author.md` matches wt-r95 blob | PASS — `46e20f42…` identical in HEAD/`ffeb5155`/`2f46b1ed`/both worktrees |
| `corpus/live/r95-author/` receipts resolve | PASS — in the **wt-r95 worktree** (untracked); absent from the main tree |
| no unclaimed tracked writes | PASS — main worktree clean of tracked modifications; `ffeb5155` touched exactly the 3 claimed paths |

## 2. Topology and provenance

```
021bde86 (ci@local, 06:01:12) r89 adjudicate            <- HEAD
└─ ffeb5155 (ci@local, 06:00:50) r95 author (landed)     <- parent aaf56d30
   └─ aaf56d30 (ci@local, 05:53:57) Merge branch 'wt-r94'
      └─ f46dce00 (05:4x) r94 author

2f46b1ed (Devin <devin@cognition.ai>, 05:56:16) r95 author   <- refs/heads/wt-r95
└─ 5a632a4f (ci@local, 05:33:44) r87+r88 fold                 <- branch base
```

The landed commit and the branch tip are **divergent commits** with the same
message shape: `ffeb5155`'s parent is the r94 merge; `2f46b1ed`'s parent is
`5a632a4f`. `git diff --name-status 021bde86 wt-r95` = `LOG.md`,
`corpus/fixtures/measure_audio.py`, and 4 report files (deletions) — the branch
carries **neither** the r94 family **nor** the r89 foldfix/adjudication. Block
extraction from the branch was therefore the only way to land r95 on top of
r94, and that is what `ffeb5155` is.

`git diff --name-status aaf56d30 ffeb5155` = exactly three paths:
`M corpus/fixtures/measure_audio.py`, `A corpus/fixtures/r95jack.c`,
`A reports/round-95/r95-author.md`.

### Hashes

| artifact | hash | where |
| --- | --- | --- |
| `measure_audio.py` (landed) | `dca4dc9bc87e006b534a50d80270bfb27492fadecfe75fbbd89f37342bd87ed7` | HEAD == `ffeb5155` == main worktree; 36403 lines |
| `measure_audio.py` (branch) | `164a915825dd054b4d0e20d9eee83df9c3196b73531ac58b1622e93d7c1d79da` | `2f46b1ed` == wt-r95 worktree; 34062 lines |
| `measure_audio.py` (pre-r95 base) | `d278458501a966cf621ff3f858ae6b932c0621df1083bf30559cf5f0325a4dd9` | `5a632a4f`; 32260 lines |
| `measure_audio.py` (r94 base) | `4808c4cfb17c311204398c9858bea3582d512090cc4a075cf31c01f4a064ee26` | `aaf56d30`; 34597 lines |
| `r95jack.c` | `55d4d4111bd8d46be743d0425a40dc8d938d15e071ce37f460db70de0df997be` | all four locations; 778 lines |
| `r95-author.md` | `46e20f42bbb77d811a4f6641ba176e8945a2de8badff960a00395bed443e881f` | all four locations |

Both hashes in the landed pair are the hashes the author report itself declares
(`r95-author.md` §Evidence) — the byte binding is intact.

## 3. Commands run and outcomes

| command | outcome |
| --- | --- |
| `git rev-parse HEAD`, `git log --oneline -12` | HEAD `021bde86`; `ffeb5155` present as parent |
| `git rev-list --parents -1 {021bde86,ffeb5155,2f46b1ed}` | landed parent `aaf56d30`; branch parent `5a632a4f` |
| `git status --porcelain=v1 \| grep -v '^??'` (main) | **empty** → no tracked modifications |
| `git -C …-wt-r95 status --porcelain=v1` | only `??` (lock, `r95-author/`, 4 run dirs) |
| `git diff --stat {5a632a4f 2f46b1ed \| aaf56d30 ffeb5155} -- …/measure_audio.py` | `+1805/−3` / `+1809/−3` |
| `git diff 5a632a4f 2f46b1ed -- …/measure_audio.py` | 6 hunks (table in §4.6) |
| `git diff aaf56d30 ffeb5155 -- …/measure_audio.py` | same 6 hunks, landed contexts |
| added-line stream extraction + `diff` | 10 changed lines total (§4.1) |
| substring test of author block/dispatch block in HEAD | `True` / `True` (§4.1) |
| declared-flag ↔ census-attr bijection script | 135 ↔ 135, no gaps, no dups (§4.4) |
| leg-registration structural count | 3+4+2+10+5 = **24** (§4.5) |
| `ast.parse` (parse-only, no `__pycache__` write) | both files PARSE OK; 554 top-level defs, 0 duplicates |
| `sha256sum -c manifest.sha256` (wt-r95 `r95-author/`) | 4/4 **OK** |
| copy-vs-canonical `measurements.json` sha256 | `1c22eb48…` / `0ed24eec…` — identical both sides |
| `sha256sum` of verifier tree copy of landed `measure_audio.py` | `dca4dc9b…` (byte capture, not a run) |

## 4. Findings

### 4.1 Block identity — VERIFIED, with a 4-blank-line caveat

The landed insertion was compared to the author's insertion line-by-line, both
extracted from the two diffs (not from file offsets):

- family block: branch 1771 lines / 85759 bytes; landed 1773 lines.
  `landed[2:] == branch` → **True**. Independent substring test: the 85759-byte
  author block is a **verbatim substring** of HEAD's file → `True`.
- dispatch block: branch 30 lines / 1773 bytes; landed 32 lines.
  Independent substring test in HEAD → `True`.
- the three replaced lines: each landed line equals the branch line with the
  r94 term prepended byte-exactly (`args.probe_sox_r94, `, `"probe-sox-r94" if
  args.probe_sox_r94 else `, `"-sox-r94" if args.probe_sox_r94 else `) → all
  three `True`.

So the **content** of the r95 block is byte-identical to the author's worktree
bytes. What the integrator's "byte-identical" phrasing does not cover: the
landed splice adds **4 blank lines** (2 immediately before the
`# r95: the JACK <-> PIPEWIRE INTEROP LATTICE` banner, 2 appended at the end of
the dispatch block). That is the entire `+1805` → `+1809` delta, and it is why
HEAD has **4** consecutive blank lines before the banner where the branch file
has 2. Whitespace-only; `ast.parse` passes; no semantic effect observed. Report
it rather than round it: the landed *file* is not byte-identical to the branch
file, only the block is.

### 4.2 The green receipts bind the branch bytes, not the landed bytes — read this before judging

- `corpus/live/r95-author/RECEIPTS.md` declares the implementation bytes covered
  by both green runs as `measure_audio.py 164a9158…` — the **branch** file.
- Both CLI logs write their receipt into
  `/home/vgpnk/Projects/shokunin/audio-shokunin-wt-r95/corpus/live/runs/…`, i.e.
  the worktree.
- The landed file is `dca4dc9b…` (r94 family + 4 blank lines).

Therefore: **no execution receipt in this repo binds the landed bytes.** The
two green batteries are real, resolve, and cover the pre-splice file. The
landed artifact's support is block-identity + parse + census coherence + the
disjointness of the r94 arm — it is *not* a green run on the landed bytes, and
it must not be reported as one. I did not run the battery (out of seat scope and
explicitly forbidden as decoration); a seat that may run the landed bytes can
close this.

### 4.3 No post-landing jack receipt exists in the main tree

`grep -rl '"mode": "probe-jack-r95"' corpus/live --include=measurements.json`
(excluding `tree/` snapshots) → **no match**. Main's newest run dir is
`20261016T085514726246Z-sox-r94`. The r95-verifier seat *did* capture the
landed bytes (`corpus/live/r95-verifier/tree/corpus/fixtures/measure_audio.py` =
`dca4dc9b…`, `r95jack.c` = `55d4d411…`) but that is a byte capture, not a run.

Observation, unexplained, needs the downstream seats' own receipts:
`corpus/live/measure_audio-jack-r95.lock` exists in the **main** worktree
(mtime 06:02, content `pid=3228981 ns=r95a_ns_3228981 role=r95arole3228981`).
`_jack_r95_family_lock()` is called only at line 35682, inside
`if args.probe_jack_r95:` (line 35663) — so something invoked the jack probe in
the main tree after the landing and wrote no receipt under main's `runs/`.
Untracked; no tracked write. Not a defect claim — a hole in the record that the
critic/reviewer/simplifier/verifier receipts should explain.

### 4.4 Both families' terms are present and coherent in every shared region

- argparse: `--probe-sox-r94` (line 35190) then `--probe-jack-r95` (35191),
  adjacent.
- mutex census `if sum([...]) > 1:` (line 35199): **135 declared flags ↔ 135
  census attributes, bijective** — no declared flag missing, no census-only
  attribute, no duplicate. r94 term first, r95 term last.
- `mode` chain (36373) and `suffix` chain (36393): both head with
  `sox-r94` then `jack-r95`; every other family's term and order preserved from
  the branch.
- dispatch: `if args.probe_sox_r94:` (35632) then `if args.probe_jack_r95:`
  (35663) then `if args.probe_pwprof_r89:` (35695) — the r95 arm is inserted
  directly after the r94 arm, as spliced.

### 4.5 The "5 entries / 24 legs" census agrees with a scribe-side structural count

`legs[…]` registrations in the landed block: `jack_surface` 3
(`a_avail`, `s_liveness`, `s_shape`), `jack_addr` 4 (the `arms` tuple:
`x_rendered`, `x_native`, `x_fillalias`, `x_corner`), `jack_bytes` 2
(`b_jack2pw`, `b_pw2jack`), `jack_quantum` 8 static + 2 loop-generated
(`q_env`, `q_wrapper`) = 10, `jack_defects` 5 (`d_latency`, `d_metadata`,
`d_rtprio_poison`, `d_transport`, `d_xrun_stall`). **Total 24.** Exactly five
`jack_*_r95_entry` functions; 554 top-level defs, 0 duplicates; no conflict
markers. This is a structural count of the landed text, not a re-run.

### 4.6 The splice-region count in the dispatch is short by two

The prompt names "3 splice regions (arg list, mutex census line, mode/suffix
chains, dispatch block)" — three and four at once. The landed diff has **6
hunks**: 1 family block + **5** wiring hunks.

| # | hunk (branch / landed headers) | region | Δ |
| --- | --- | --- | --- |
| 1 | `@@ -30979,6 +30979,1777 @@` / `@@ -33284,6 +33284,1779 @@` | r95 family block | +1771 / +1773 |
| 2 | `@@ -31109,6 +32880,7 @@` / `@@ -33415,6 +35188,7 @@` | `--probe-jack-r95` declaration | +1 |
| 3 | `@@ -31116,7 +32888,7 @@` / `@@ -33422,7 +35196,7 @@` | mutex `sum([...])` line | replace |
| 4 | `@@ -31549,6 +33321,36 @@` / `@@ -33886,6 +35660,38 @@` | dispatch block | +30 / +32 |
| 5 | `@@ -32227,7 +34029,7 @@` / `@@ -34564,7 +36370,7 @@` | `mode` chain | replace |
| 6 | `@@ -32247,7 +34049,7 @@` / `@@ -34584,7 +36390,7 @@` | `suffix` chain | replace |

The author's own report says "the only deletions are the three shared-line
splices … (mutex `sum([...])` list, `mode` select, receipt `suffix`)" — which
matches the measured **−3** exactly. So "3" is right for *deleted-line splices*
and wrong for *wiring hunks* (5). Also a naming note: the "mutex census line" is
hunk 3 (the `if sum([...]) > 1:` count); hunk 2 is the argparse declaration.

### 4.7 Report-vs-artifact count discrepancies (cosmetic, hash binding intact)

- `r95-author.md` §Files changed says `r95jack.c` is "**764 lines**". The
  artifact is **778 lines** (`wc -l`, identical in HEAD blob, `2f46b1ed` blob
  and both worktrees; 31 blank, 46 comment). The declared sha256 `55d4d411…`
  binds the real bytes, so this is a report-side count error only.
- `r95-author.md` §Files changed says
  `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` "was already
  tracked-dirty at entry". Two pyc files under that path **are** tracked
  (`measure_audio`, `build_artifacts`); at audit time the main worktree is clean
  and the pyc blob is identical between HEAD and `wt-r95`. Consistent with
  dirty-at-entry-then-landed, but not verifiable from here.
- `RECEIPTS.md` describes `manifest.sha256` as "sha256 of every file in this
  directory"; the manifest covers the 4 files under `receipts/` only — not
  `RECEIPTS.md`, not `exit-census.json`, not itself.

### 4.8 "Zero commits" is time-bounded

`r95-author.md` and `RECEIPTS.md` both say the seat made "**Zero commits**".
Branch `wt-r95` now points at `2f46b1ed` ("r95 author: jack family … green x2"),
authored/committed by `Devin <devin@cognition.ai>` at **05:56:16**, after the
receipts were frozen (05:55). The claim was true when written; the branch has
since moved. Recorded, not adjudicated.

### 4.9 Receipts resolve — in the worktree (custody location, stated plainly)

`corpus/live/r95-author/` exists **only** in
`~/Projects/shokunin/audio-shokunin-wt-r95` (untracked, not in HEAD, absent from
the main worktree). Verified there:

- `sha256sum -c manifest.sha256` → `receipts/green1-cli.log: OK`,
  `green1-measurements.json: OK`, `green2-cli.log: OK`,
  `green2-measurements.json: OK` (4/4, exit 0).
- Both copies are byte-identical to their canonical run-dir originals
  (`1c22eb487db779ce…`, `0ed24eecccc38c2e…`).
- All 4 run dirs exist: `…085246666582Z` (red by design, `any failures=True` —
  as `RECEIPTS.md` states), `…085334177280Z` (pre-hygiene green),
  `…085442157241Z` (green 1), `…085527000328Z` (green 2); each carries 5 r95
  entries under `mode: probe-jack-r95`, and the three documented greens report
  `failures: {}`.
- CLI logs are the harness's own lines, `{"receipt": …-jack-r95/measurements.json",
  "failures": {}}`, paths pointing into the worktree.
- `exit-census.json` present: 0 `r95a` modules/nodes/clients, 0 probe procs,
  0 `stream-properties` rows, `clock.force-quantum=0`, defaults untouched.

### 4.10 LOG.md / SCORECARD.md carry no r95 record — consistent with convention

`grep -c 'r95' LOG.md` → 0; `SCORECARD.md` → 0. Control: LOG.md records
adjudicated rounds only (ROUND 82, 83, 84, 85, 86, 89) and has **no** entry for
r87, r88, r90–r94 either. r95 is explicitly unjudged ("*not judged*"). Not a
gap against the landing; noted so the absence is not misread.

## 5. Gates

| gate | result |
| --- | --- |
| block-identity (byte comparison, both directions) | PASS, 4-blank-line caveat (§4.1) |
| blob-identity `r95jack.c`, `r95-author.md` vs `wt-r95` | PASS |
| splice-region coherence (both families, all shared lines) | PASS |
| declared-flag ↔ census bijection (135/135) | PASS |
| leg census vs author claim (24/24) | PASS |
| `ast.parse` landed + branch file (parse-only, no write) | PASS |
| receipt resolution (manifest, copies, run dirs, CLI logs) | PASS (worktree) |
| tracked-write cleanliness (main + worktree) | PASS — zero unclaimed |
| landed-bytes execution receipt | **NOT PRESENT** — see §4.2/§4.3 |
| judge gate / mutation / re-run of the battery | not attempted (out of seat scope) |

## 6. Touched surfaces

- Written: `reports/round-95/r95-scribe.md` (this file; new, **untracked**).
- Scratch: `/tmp/r95audit/*` (file snapshots, extracted diff hunks, diff of
  added-line streams) — outside the repo.
- Not touched: no tracked file modified, no commit, no product code, no
  worktree state changed, no lock touched, no runtime invoked, nothing
  re-run.

## 7. Out of scope (named, not acted on)

- Running the r95 battery against the landed bytes to close §4.2.
- The `corpus/live/r95-{critic,reviewer,simplifier,verifier}/` evidence dirs and
  the 06:02 lock in §4.3 — other seats' surfaces.
- Remediating `wt-r95`'s divergence (it lacks r94 + the r89 foldfix); it is not
  mergeable as-is, which is why block extraction was used.
- The `764` vs `778` line count, the 4 blank lines, and the manifest-coverage
  wording (§4.7) — reportable nits for the author/judge, not edits for a scribe.
- Any judgment of the move's admissibility.

## 8. Blockers

None for this seat. Two items block *upgrading* r95 to "green on the landed
bytes", and are stated so no downstream seat does it implicitly:

1. §4.2 — every green receipt binds `164a9158…` (branch), none binds
   `dca4dc9b…` (landed).
2. §4.3 — a post-landing jack invocation in the main tree left a lock and no
   receipt.

*Leaf seat — audited the r95 landing, wrote nothing tracked, committed nothing,
did not judge.*
