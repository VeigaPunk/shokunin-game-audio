# r98 scribe — provenance audit: report → receipt → author bytes → integrated bytes → pin

## 1. Identity, scope, commands executed

- **Seat / wave**: scribe, wave `shokunin-train-20261016-w24`, round **N=98**, role **scribe**, family flag **pwstream-r98**.
- **Source pin**: `bb177513a615a32d3bc150ecbdcf78302e110d8c` — verified equal to the repo's current `main` HEAD (`git rev-parse`); the r98 author commit `d41cfa68` is an ancestor of the pin.
- **Scope**: provenance and byte audit only. Read pinned tracked source via `git show PIN:path`; read the round's scout/boundary/author/integration reports; quoted frozen receipts without re-running their derivation. **No live family was executed** (verifier-only per assignment), no source/fixture/report/LOG/SCORECARD/MANIFEST edits, no routing or configuration edits, no subagents, no commits/pushes.
- `glmseat` skill loaded as first action (model pin `glm-5-3-flash-max`; the skill has no executable steps). No routing, profile, or session state was touched.
- **LSP gap**: LSP was not used; all inspection is literal source/text inspection plus `python3 ast`/`json` reads of frozen artifacts. Grep hits below are byte facts, not semantic proof.
- Commands actually executed (full transcript with outputs in the scratch path): `git show/rev-parse/worktree list/merge-base --is-ancestor/status --short/log --oneline/show --stat/--numstat`, `sha256sum` on pinned blobs, worktree files and extracted line ranges, `sed -n` block extractions, `python3` byte-containment + `ast` symbol census + `json` receipt reads, `python3 -m py_compile` on a `/tmp` copy of the pin blob (rc 0), `grep` over reports/LOG/SCORECARD, `find` for MANIFEST, `mkdir -p` of the scratch dir. Nothing else.

## 2. Findings (ordered by severity)

### F1 (medium) — LOG.md and SCORECARD.md carry no r98 entry (stale documentation chain)
- **Where**: `LOG.md` (repo root, tracked, 459,201 B), `SCORECARD.md` (tracked, 130,906 B).
- **Failure path**: a reader auditing the corpus from LOG/SCORECARD finds no trace of round 98: `grep -ic 'r98'` and `'round 98'` return **0** in both files. LOG.md's round entries end at ROUND 97 (lines 1461–1479 cover 94/95/90/90-FOLD/91/92/96/97); SCORECARD.md's mtime (2026-10-16 03:43) predates the r98 commit (07:37:55 −03). The round's only committed narrative is `reports/round-98/r98-author.md` + `r98-integrate.md`.
- **Evidence**: observed (greps above; LOG tail quoted in scratch).
- **Smallest correction**: the lead appends a ROUND 98 entry to LOG.md and the SCORECARD at integration closure (out of this seat's scope — reviewers must not edit LOG/SCORECARD).
- **Observed, not inferred.** Same gap exists for r93/r99/r100; recorded here for r98 only.

### F2 (medium) — the committed author report cites evidence paths that resolve only inside an untracked linked worktree
- **Where**: `reports/round-98/r98-author.md` (pinned) cites `corpus/live/r98-author/fixture-sha256.txt`, `corpus/live/r98-author/dump-poll.log`, and receipts `corpus/live/runs/20261016T101046237597Z-pwstream-r98/measurements.json` and `…101258039942Z-pwstream-r98/measurements.json`.
- **Failure path**: none of these paths exist in the main checkout (`ls corpus/live/runs | grep pwstream` → 0 of 5,786 dirs; no `corpus/live/r98-author/` in main). They exist **only** in the linked worktree `/home/vgpnk/Projects/shokunin/audio-shokunin/audio-shokunin-wt-r98` (branch `wt-r98` @ `5755be5b`, uncommitted author delta ` M corpus/fixtures/measure_audio.py` + untracked fixture/lock/evidence). The receipts' internally recorded absolute paths carry the worktree prefix (`…/audio-shokunin-wt-r98/corpus/live/runs/…`, quoted in `battery-final.log`). The integration note discloses "untracked, not carried" for the receipts, but the author report itself does not mark its paths as worktree-local.
- **Evidence**: observed (path existence checks both sides; worktree `git status --short`; `battery-final.log` receipt lines).
- **Risk**: if the `wt-r98` worktree is ever pruned, the receipt chain behind the committed report becomes unrecoverable — the report would cite paths that resolve nowhere.
- **Smallest correction**: the lead records the worktree-local absolute location of `corpus/live/r98-author/` and the 11 `*-pwstream-r98` run dirs in the round's integration/adjudication record (or relocates them per corpus policy — lead's call; this seat moved nothing).
- **Observed.** These receipts are local-only: not committed, not pushed, not remotely available.

### F3 (low) — receipt hash scope pins the C fixture, binary and tone, but not the Python driver bytes
- **Where**: both green receipts' `measurements.<entry>.probe_build.*` fields.
- **Failure path**: every one of the six entries records `probe_build.source_sha256 = 9f840a6b…` (the committed `r98stream.c`), `probe_build.binary_sha256 = 79551d62…` (compiled probe), and the cap entry records `tone.sha256 = 1048fc6a…` — but the driver sha `c9d7627b…` (the author's `measure_audio.py` bytes) appears nowhere in either receipt (all 64-hex tokens enumerated). The Python-side binding rests on the author seat's separate `corpus/live/r98-author/fixture-sha256.txt` (worktree-local, untracked) plus the `battery-final.log` narrative.
- **Evidence**: observed (64-hex token enumeration over both receipt files; `fixture-sha256.txt` contents).
- **Smallest correction**: future instrument rounds record the driver sha in-receipt (source change — out of scope here).
- **Observed.**

### F4 (low) — integration note's symbol count is scope-dependent (52 vs 54), uniqueness claim verifies
- **Where**: `reports/round-98/r98-integrate.md`, "symbol census" row ("52 module-level names … 0 collisions").
- **Failure path**: none functional. `ast` count of the family block: **52 name-creating statements** (38 defs + 14 assigns, two of the assigns being tuple-unpackings) → **54 distinct module-level names**. Intersection with the rest of the pin's module-level namespace (1,579 names total): **empty** — 0 collisions under either count.
- **Smallest correction**: none required; note the counting scope if the note is ever revised.
- **Observed.**

### F5 (info) — eight intermediate run attempts retained but not itemized; original vs corrected distinction preserved
- **Where**: worktree `corpus/live/runs/` — 11 `*-pwstream-r98` dirs: the wedge-affected first attempt `…092555426767Z`, eight intermediates (`…094513479381Z` … `…100533120575Z`), and the two cited greens.
- **Evidence**: the author report names the wedge attempt and the two finals; §5.5 refers to intermediate receipts in aggregate ("smaller defects the receipts caught"). `battery3.log` holds only a truncated `BATTERY 1 start 09:43:10Z loadavg=12.66…` marker (no end) — a retained failed attempt. The wedge receipt is correctly distinct: 34 legs, named blocks (`pwstream_null_sink_unavailable` ×2, `x_stall300`/`x_stall600` profiler-window), and fixture sha `a9985e4b…` — the **pre-correction** bytes, versus the greens' `9f840a6b…`. The report keeps this original-vs-corrected distinction explicit ("it is not a green run").
- **Observed.** No correction needed; listed for the audit trail.

### F6 (info) — no MANIFEST file found
- `find -maxdepth 3 -iname '*MANIFEST*'` (excluding `.git`) returns nothing in the audio repo. The assignment's do-not-edit list references MANIFEST; its absence at this tree is recorded, not repaired.
- **Observed.**

## 3. What the evidence supports (verified chain)

Every load-bearing link of the chain **verifies byte-exactly** against the pin. All items below are source/byte facts or quoted frozen-receipt fields; no measurement was recomputed and no live family was run.

| chain link | claim | verification |
| --- | --- | --- |
| pin | `bb177513a615a32d3bc150ecbdcf78302e110d8c` | = current `main` HEAD; `d41cfa68` (r98 author+integrate) is its ancestor |
| author bytes (original) | worktree fixture `c9d7627b…` | worktree file sha matches; `fixture-sha256.txt` records exactly `c9d7627b…` + `9f840a6b…`; worktree diff vs base `5755be5b` measured **+2385/−2** (matches the author's claim) |
| integrated bytes | landed blob `b0678fb1…` (49,807 lines) | `git show d41cfa68:corpus/fixtures/measure_audio.py` sha matches; `--stat` 2,389 changed = measured **+2386/−3**; commit-message label `+2385/−3` discrepancy is disclosed in the integration note (disclosure 2) with the correct arithmetic |
| family block | 2,351 lines / 116,914 B, sha `ba7e3b58…` | byte-identical in four places: author's `r98block.py`, worktree file lines 31091–33441, landed blob lines 45906–48256, **pin blob lines 46326–48676**; occurs exactly once in the pin blob |
| dispatch block | 31 lines, sha `965e7e3d…` | present exactly once in both the landed blob (lines 49096–49126) and the pin blob |
| argparse row | sha `5b2c034f…` | pin line 54390; at landing (d41cfa68) placed after `--probe-wppol-r97`, before `--probe-sox-r94` (lines 48392–48394) exactly as the note claims; mutex token at list head (d41 line 48403); mode/suffix ternaries at d41 lines 49777/49797 as claimed |
| C fixture | `9f840a6b…` | identical at pin, worktree, and in the author's recorded sha list; header records the §5.2 `hold` correction (r98stream.c lines ~10–19, 103–104, 535–536) as claimed |
| six entries | core/run/route/cap/xw/sbx | six `_pwstream_r98_entry_head` call sites at pin lines 47214/47497/48005/48157/48333/48494 with exactly those names |
| receipts → report | two greens, `failures: {}`, 67 legs | both receipts exist (worktree-local), quoted: legs **15/18/12/4/4/14 = 67**, failures **0**, exactly **one** coverage cell each (`pwstream_cap_r98_probe.cap_noprop`, "…recorded, not armed") — matching the author report's census and §5.4; `battery-final.log` ties both batteries (start 10:08:32Z → rc=0 10:10:46Z; start 10:10:46Z → rc=0 10:12:58Z) with the two receipt paths and `failures {}` |
| receipts → bytes | greens ran on the author bytes | receipts pin the C fixture (`9f840a6b…`), binary (`79551d62…`), tone (`1048fc6a…`); the Python driver sha is not in-receipt (F3) — the driver binding is via `fixture-sha256.txt` + timing |
| timestamps | ordering consistent | wedge receipt 09:25:55Z (inside the disclosed ≈09:0x→09:26:50Z wedge); greens 10:10:46Z/10:12:58Z; commit 10:37:55Z (= 07:37:55 −03); SCORECARD mtime 03:43 local predates the round (F1) |
| upstream reports | scout/boundary committed before author | `d8441a17` (scout) and `7bf69dff` (boundary) are ancestors of `d41cfa68`; both files present at pin (shas in scratch); the author's citations resolve: boundary §3.1–3.6, §5, §6, §7 items 4/6/7 (`[?]` 4 = duplicate Link, 6 = sandbox PCI HDMI, 7 = WP startup race) |
| pin integrity after landing | no r98 byte changed later | the only later commit touching `measure_audio.py` before the pin's other additions is `bb177513` (r99 safety): single hunk `@@ -52605,34 +52605,42 @@ def rtp_e2e_r99_entry():` + new `test_rtp_r99_lan_control.py` — the r98 block/dispatch/argparse bytes are byte-identical at the pin (containment checks above) |
| operability | pin blob parses | `py_compile` of the pin's `measure_audio.py` (to a `/tmp` cfile): rc 0 |

**Measured vs blocked (as recorded, not re-derived):** both green receipts measure 67/67 legs with zero failures and exactly one named coverage cell (`cap_noprop` — the prop-less capture policy row, recorded-not-armed after it failed to reproduce in this window). The wedge-affected attempt is a named-block run (34 legs), retained as the original-bytes evidence. The r98 family's greens are author-worktree receipts on author bytes; **no green receipt exists for the integrated/landed bytes or for the pin** — the integration note says so explicitly ("the author's two frozen-byte batteries are the evidence of record"; integration ran only compile/help/mutex checks). That limitation is disclosed in the committed integration note and is the round's central calibration fact: the landed artifact's behavioral evidence is bytewise-transitive (identical family/dispatch/fixture blocks), not a fresh run.

## 4. Residual risks and explicit checks not run

- **No live family executed** (scribe is read-only; the verifier alone runs the family). The greens' quantitative values (geometry, cadences, xrun counts, sandbox axes) were **not** re-verified beyond the leg/coverage census — the lead checks quantitative outputs.
- `--help`, probe-mutex rc=2, and `gcc -fsyntax-only` checks were not rerun at the pin (integration-time claims); `py_compile` at the pin was run instead.
- Declared-leg recount from the source's arming convention was not performed; the declared 67 agrees across the author report, integration note, commit message, and the assignment, and the receipts census 67 measured legs.
- The receipts' environment claims (`TMPDIR=~/Projects/shokunin/tmp`, `nohup`, lock serialization) are attested by the author report and `battery-final.log` ordering but were not independently reconstructed.
- F2 is the standing risk: the entire r98 receipt chain lives in the untracked `wt-r98` worktree and would be lost if that worktree is pruned.
- The author-disclosed host incidents (graph-wide enumeration wedge, foreign `pipewire-pulse` interposition on the pactl teardown, ambient loadavg 51–55) are taken as recorded disclosures; this seat did not re-inspect host state.
- LOG/SCORECARD r98 entries are missing (F1); no MANIFEST found (F6). Neither was repaired — out of seat scope.

## 5. Artifact paths and attribution

- **This report**: `/home/vgpnk/Projects/shokunin/audio-shokunin/reports/round-98/r98-scribe.md` (the only report file this seat wrote).
- **Scratch (command transcript + outputs)**: `/home/vgpnk/Projects/shokunin/audio-waveb-resume/r98-scribe/commands-and-outputs.md`.
- **Audited artifacts (read-only)**: pinned reports `reports/round-98/r98-{scout,boundary,author,integrate}.md` at PIN; pinned sources `corpus/fixtures/measure_audio.py` (r98 block at pin lines 46326–48676, dispatch, argparse row) and `corpus/fixtures/r98stream.c`; author worktree `/home/vgpnk/Projects/shokunin/audio-shokunin/audio-shokunin-wt-r98` (uncommitted delta + `corpus/live/r98-author/*` + 11 `corpus/live/runs/*-pwstream-r98/` receipt dirs).
- **Attribution**: r98 scout `d8441a17`, boundary `7bf69dff`, author+integration `d41cfa68` (message label `+2385/−3`; measured landed stat `+2386/−3`, disclosed), pin `bb177513` (r99 safety; touches no r98 byte). Receipts and author evidence are **local, worktree-local and untracked** — nothing from this audit is committed or remotely available, and this seat committed, pushed, and edited nothing other than its own report and scratch.
- This is an advisory scribe audit; it admits no round and claims no canonical judge verdict. The canonical Rust runtime remains the sole judge.
