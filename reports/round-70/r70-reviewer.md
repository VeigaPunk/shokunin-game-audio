# R70 reviewer — integration-base audit of committed r69 state (pre-diff)

Lane `audio`, round r70. Reviewer-seat task from the brief: audit the committed
r69 state as the integration base — replay the 119-row ledger, verify receipts
byte-stable, census whether `fifo_writer_hold_s` is the only untested timing
constant on the transport axis, and pin what the author's diff must NOT break.

Base audited: canonical lane repo `~/Projects/shokunin/audio-shokunin` at HEAD
`939fe47` ("corpus ignore: close the non-tree snapshot side-channel"), with
`fe4c1d1` r69 report-last and `30bb86d` the r69 diff commit.
`corpus/fixtures/measure_audio.py` last touched at `30bb86d`
(sha256 `09d426b5c1d4b9b0…`); committed ledger
`corpus/live/r69-author/ledger-r69.tsv` (sha256 `74ed54b3f377610f…`).
Toolchain pinned per `corpus/knowledge/2026-10-14-sox-transport-axis.md`:
`sox --version` → SoX_ng v14.8.0.1, `ffmpeg -version` → n9.0.1 (verified live).

No `lsp` device is exposed on this substrate — caller/definition checks done by
targeted read + text grep per the fallback rule (same as r64–r69 seats).

## Result 1 — full 119-row replay: SURVIVES, byte-exact

Method: independent copy of the committed runner —
`corpus/live/r70-reviewer/r70rev_ledger.py` (verbatim MODES order from
`r69-author/run_ledger.py`, only the TSV path retargeted), run from the
worktree root `~/Projects/prymeagnt/audio` so `.shokunin/audio` resolves
through the symlink into the canonical repo (the runner's documented
invocation contract). Stderr progress:
`corpus/live/r70-reviewer/ledger-r70rev-stderr.log`; output TSV:
`ledger-r70rev.tsv`; comparator: `r70rev_compare.py`; output:
`ledger-r70rev-compare.txt`.

| check | committed | fresh replay | verdict |
|---|---|---|---|
| rows | 119 | 119 | identical |
| exit tally | 49 exit-0 / 70 exit-1 | 49 exit-0 / 70 exit-1 | identical |
| exit sequence position-wise | — | — | 0 mismatches |
| failure_summary column | — | — | byte-identical (`diff` of `idx␉exit␉failsum` empty) |
| UNPARSED rows | 0 | 0 | identical |
| missing receipts (`-`) | 0 | 0 | identical |
| receipt bytes (all 119, incl. the 5 r69 extsuffix rows) | — | — | **119/119 byte-identical to committed `runs/` receipts** |

Compare exit 0: `committed rows: 119  fresh rows: 119 / mismatches:
exit=0 failsum=0 receipt_bytes=0`. Strongest level: full ledger, every row's
receipt re-derived byte-for-byte on HEAD.

**Provenance/contamination note (shared worktree):** the r70-author lane's
in-flight diff to `corpus/fixtures/measure_audio.py` first appears in the
working tree with mtime **2026-10-14 09:14:33**; my replay's TSV finished
writing at **09:08:58** — all 119 rows executed the committed r69 code, so
the byte-exact verdict describes the pre-diff base uncontaminated. Observed
uncommitted diff head (not my audit target; recorded as evidence only):
`TRANSPORT_R70_HOLDS = (0.0, 0.05, 0.2, 0.5, 1.0, 2.0)`, `REPS=10`,
`FEEDS=("oneshot","chunked")`, `CHUNK_BYTES=100`, `CHUNK_GAP_S=0.05`,
`MEMBER="dec_act"`, env override `MEASURE_FIFO_WRITER_HOLD_S` with the
effective value recorded — and the pinned default stays `1.0` ("so every
prior member/receipt is byte-stable"), i.e. the compatible reading of
must-not-break rule 4 below.

## Result 2 — transport-axis timing-constant census: `fifo_writer_hold_s` is NOT the only unmeasured timing constant

`corpus/fixtures/measure_audio.py` complete inventory (the only timing surface
in the ledger protocol; `build_artifacts.py`, `check_table.py`,
`census_check_rows.py` carry none — grepped):

| constant | value | site | recorded in receipt? | measured? |
|---|---|---|---|---|
| `TRANSPORT_R67_FIFO_WRITER_HOLD_S` | 1.0 s | :197 def, :285 `time.sleep`, :295 join | yes, `fifo_writer_hold_s` | **the r70 target** — measured only at {bare/race (r67: 5/5 exit-2 au-magic + one >10 s python block), 1.0, 8.0 (r67 scout `fifo_hold`, agreeing)}; the open interval (0, 1.0) is unmeasured |
| `TRANSPORT_R67_ARM_TIMEOUT_S` | 10 s | :191 def, :240 leg bound, :247 verdict text | yes, `arm_timeout_s` | **unladdered chosen bound** — on trip it emits `blocked: no verdict within 10 s` with `exit_code: null`, a distinct verdict signature that rewrites both the fork description and the receipt. Per-leg wall-time is NOT recorded anywhere → its margin is as unmeasured as hold's. A guard, not a verdict selector — but it converts block→verdict and therefore *is* a determinism constant |
| join grace | `FIFO_WRITER_HOLD_S + 5` s | :295 `writer.join(timeout=…)` | **NO — absent from `transport_protocol`** | unmeasured; derived from hold so it silently tracks the ladder — if the author decouples it, that is an unrecorded protocol parameter |
| `fifo_feed` strategy | `"one-shot write then writer lingers"` | :320 recorded string, :281–285 impl | yes | the r70 chunked variant changes this; on the 17 prior rows it must stay verbatim |
| ledger-row timeout | **absent** | `run_ledger.py:142` `subprocess.run` w/o timeout | n/a | unbounded row wait — bounded today only transitively (4 legs × ≤10 s + hold + 5 s join ≈ ≤46 s/row). A chunked feed that can wait outside `transport_leg`'s bound (e.g. reader-side `fifo.open` block) removes this floor |

Asymmetry worth recording: `transport_leg` (:239) is the ONLY
timeout-bounded `subprocess` call site in the whole harness — every other leg
(:41, :731–885 ui/r66 legs) is unbounded. Safe today because non-transport
legs run regular files only.

**Answer to the brief's question:** `fifo_writer_hold_s` is the only untested
*verdict-selecting* timing constant — the one that chooses between race/stable
verdict classes — so it is the correct r70 target. But it is not literally the
only untested timing constant: `arm_timeout_s` (recorded, unladdered, unbounded
margin) and the join grace (unrecorded, derived) lurk beside it, and the ledger
runner has no row bound at all.

## Result 3 — scope caveat on the declared member choice (evidence, not a defect)

The ladder targets `dec_act` = `round-66/pair_dec_act.wav` = **600 B** — the
smallest of the THREE act-routed members (`preempt_act`, `preempt_both` =
11,588 B each, ~19×). The open-#2 race window the hold covers is
close-time-vs-bridge-`openat`, and the residual tail ffmpeg reads after
reader-#1's prefetch scales with member size. An `h*` measured on `dec_act`
therefore **bounds `dec_act`**; transferring it to `preempt_act`/`preempt_both`
— and to the non-bridge members whose fifo arm fails differently (early-EOF
flips detection at the len gate, knowledge doc :45) — is an assumption unless
the diff re-runs them at `h*`. Also committed evidence that the race regime
produces *harness-level* instability, not just verdict drift:
`corpus/live/r67-author/ledger-r67-run{1,2}-defect.tsv` carry UNPARSED rows
with `-` receipts (FFT(0) `ValueError`; `CalledProcessError`) — a hold=0 cell
may legitimately emit `blocked:`/`UNPARSED`/null-receipt classes; the author
should record them in `hold_ladder` groups rather than treat them as probe
failure.

## What the author's diff must NOT break (integration contract)

1. **119 prior rows, all three columns**: position-identical order; exits
   49×0 + 70×1; `failure_summary` verbatim; receipt bytes identical
   (today's baseline: 0 mismatches on every axis).
2. **`transport_protocol` on the 17 rows carrying it** (verified: exactly 17
   committed receipts embed `arm_timeout_s: 10`, `fifo_writer_hold_s: 1.0`,
   `fifo_feed: "one-shot write then writer lingers"` — r67×10 + r68×2 + r69×5):
   no added keys (`hold_ladder`, `join_grace_s`, …), no renames, no value
   changes — any of these mutates all 17 committed-verdict receipts.
3. **Shared builder scope**: `transport_entry`/`transport_matrix` serve all
   three member sets; r70's `hold_ladder` groups must be scoped to NEW r70
   entries — landing the field inside the shared entry mutates prior rows.
4. **Recorded hold stays `1.0` on prior rows even if measured `h*` ≠ 1.0.**
   Tension inside the declared claim to surface, not resolve silently:
   re-pinning the recorded constant to `h*` both re-runs the fifo verdict AND
   rewrites the 17 receipts — i.e., falsifies "all 119 prior rows + receipts
   byte-stable" by construction. The compatible reading is: recorded pin stays
   1.0, `h*` lands as measured evidence in new rows.
5. **Ledger structure conventions**: new modes newest-first at MODES[1:];
   mutual-exclusion `sum(…) > 1` extended by the new flag count; `mode`/`suffix`
   chains prepended; TSV stays `idx␉exit␉receipt␉failsum`, failsum single-line.
6. **Receipt determinism hygiene for new rows**: `stderr_tail` input-name +
   ASLR scrubs (:261–262) must cover any new leg output — no absolute paths,
   timestamps, PIDs in receipt text; `allow_nan=False` discipline holds.
7. **Fixture bytes frozen**: all `TRANSPORT_R67/R68/R69_MEMBERS` files
   sha-stable (dec_act 600 B, preempt_* 11,588 B, r69 extsuffix 512 B…);
   no `build_artifacts.py` regen during ledger runs — the non-atomic WAV
   rewrite hazard (knowledge doc :5) means replay is valid only under serial
   execution.
8. **Committed `corpus/live/runs/` receipts must keep resolving**: prior TSV
   receipt-path columns are absolute paths — no deletes/moves/rebases.
9. **Toolchain boundary**: verdicts are pinned to SoX_ng v14.8.0.1 +
   ffmpeg n9.0.1 on this host; a toolchain drift re-opens every transport
   verdict (recheck clause already in the knowledge entry).
10. **No new unbounded waits**: any chunked-feed/ladder leg must stay inside
    `transport_leg`'s 10 s arm bound + bounded join — `run_ledger.py` has no
    row timeout, so an unbounded wait converts a probe into a ledger hang.

## Residual risk / verification gaps

- `arm_timeout_s` margin is unmeasurable from receipts (no per-leg wall-time);
  on a loaded host a leg approaching 10 s flips to the `blocked` verdict
  nondeterministically. Cheap improvement if the author wants it: record leg
  durations in NEW r70 entries only (adding them to prior entries breaks
  rule 2).
- The `+5` join grace is unrecorded; if r70 needs a different grace it becomes
  a silent protocol parameter — record it in new `transport_protocol` blocks.
- `h*` transfer across the three act members is untested by the declared plan
  (600 B vs 11,588 B members) — flagged above as scope caveat.
- My replay wrote 119 fresh untracked `corpus/live/runs/<stamp>-*/` receipt
  dirs + `corpus/live/r70-reviewer/` scratch; I modified zero tracked files
  (the now-present ` M corpus/fixtures/measure_audio.py` is the r70-author
  lane's in-flight diff, post-dating my replay — see the provenance note).
  Pre-existing untracked `corpus/live/r68-author/__pycache__/` and sibling
  r70 lanes' scratch dirs untouched.
- Replay ran serial against a quiescent tree; concurrent artifact rebuild
  remains the known corruptor (knowledge doc :5).

Seat verdict (recommendation, not admission): integration base is exactly the
committed r69 state — ledger replays 119/119 byte-exact; `fifo_writer_hold_s`
is the right r70 target but shares the axis with two quieter timing constants
(`arm_timeout_s` margin, unrecorded `+5` join grace) the author's receipt
discipline must not silently mutate.
