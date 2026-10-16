# r89 scribe — wave-B gate on the committed pwprof landing (0d732989)

host: `plazir27` (local = UTC−3). Lane `~/Projects/shokunin/audio-shokunin`.
Seat: SCRIBE (wave-B gate, r89). Scope: audit the committed r89 landing
`0d732989` — `corpus/fixtures/measure_audio.py` (+1561/−3, sha
`623c25cc…`), `reports/round-89/r89-author.md`, and the two cited green
receipts — for claim→sha chains, arithmetic reconciliation (4 entries /
47 claimed legs / 2 green runs), file existence, hash re-derivation,
unreported evidence, the caveat rows, and (the round's assigned focus)
**whether the r89 pwprof family lock is at a fixed lane path rather than
TMPDIR-scoped** — plus the encoded laws: exact-N gate completions, 4096 B
stream blocks, INT/TERM graceful vs KILL truncation, SIGKILL-leaves-49152 B
incremental write (boundary falsification folded), the strtol parser
lattice, schema invariants, suspension 21→0, and the xw witnesses.

**Read-only on everything except this report and `corpus/live/r89-scribe/`;
no commits, no judgment passed** — every discrepancy below is handed to the
canonical judge as an adjudication item.

Entry state: HEAD `0d732989d4c7f8c178902dd45bfa09ea156b5361` (`r89 author:
47 legs / 4 entries pwprof lattice`, 04:49:33 −0300; parent `f1ef7071`).
Ambient at audit (04:54–04:56): loadavg **75.2 / 63.5 / 63.4** (load
preferred, as the task directs); **sibling wave-B seats were live** — the
r89-critic was replaying/mutating the family (its `locktest/` receipts
04:50–04:53), the r89-verifier had extracted a tree (`r89v-tree.tar`), and
two live `r89a-gate-*` temp dirs (pids 1791602/1792203) showed the probe
being re-run by siblings. Tracked dirty set = `corpus/fixtures/__pycache__/
measure_audio.cpython-314.pyc` only; the cited receipts and lock witness
were sha-stable for the whole audit window. No r89 claim below depends on
live state.

**Labrat.** The single permitted `probeParent` labrat was dispatched once
(read-only static audit; no writes, no PipeWire, no processes). It returned
**CONFIRMED ×5** on the receipt arithmetic and the lock: 52 leg keys
(27/12/4/9) in both receipts; "47" reconciles with neither 52 nor 51;
`g_term`/`g_int` `n_info` = 46; the `o_int` 32347 / `o_default` 4320 /
`x_conc` / `x_top` / `x_foot` mismatches; and the fixed-path `LOCK_EX`
lock with `tempfile.gettempdir()` only outside the r89 family. Its one
imprecision (it guessed the xw undercount was `x_devfull`) is corrected
here: the extra receipt leg the report does not count is **`x_link`**.

---

## 0. Verdict

| # | question | answer |
| --- | --- | --- |
| 1 | Do the claim→sha chains hold? | **Yes.** Pin fixture sha `623c25cc55521472dc54a1ab2b4ccb4a9836fda3ca1a71dcca06092a4317cd22` (32 062 lines, 1 611 226 B) = worktree = the report's cited sha; the diff is **+1561/−3** with exactly 3 deleted lines (mutex sum, `mode`, `suffix` — each replaced in place) and 6 hunks; the commit is 2 files (fixture + report); both cited receipt shas re-derive (`1d7a24af…`, `3e756403…`). **Nits: the headline leg count does not reconcile (ADJ-1); three report figures match neither receipt (ADJ-2); four quoted figures are run-2-only provenance (ADJ-3); one claimed witness key does not exist (ADJ-4); prose/staleness nits (ADJ-5, ADJ-6).** |
| 2 | Does the arithmetic reconcile? | **No — the headline does not; everything verdict-bearing does.** The receipts contain **52 leg keys** (27+12+4+9) in *both* runs; the report's own section headers sum to **51** (xw says 8, the receipt has 9) and the headline/commit say **47** (reconciles with neither). **222/222 re-derivation checks pass** (`laws-recheck.txt`) on the two cited receipts: every encoded law (exact-N, 4096 B blocks, signal class, `-o` lattice, strtol lattice, schema invariants, suspension 21→0, xw witnesses) is present and green in both runs; all four entries have `failures: []` and the `coverage_blocked` key **absent** in both runs. |
| 3 | Do the claimed files exist? | **Yes.** Every repo path in the report resolves (`path-existence.txt`). The commit contains exactly 2 files; the receipts and the lock are untracked/host-only (`git ls-files` = 0 for `*pwprof-r89*`). |
| 4 | **Is the family lock fixed-path, not TMPDIR-scoped?** | **YES — verified statically, dynamically, and by the lane witness.** Static: `ROOT` L26, lock path L29509 `ROOT/"live"/"measure_audio-pwprof-r89.lock"`, blocking `LOCK_EX` L29514 (no `LOCK_NB`), dispatch L31355 / lock call L31373 “held to exit”; **no `tempfile.gettempdir()` anywhere in the r89 family** (the three hits are the r82/r84/r85 locks, untouched). Dynamic: two concurrent acquirers with **different TMPDIRs** resolved the identical path and serialized (B waited 1.9507 s, overlap −0.0025 s); same-TMPDIR serialized; dead holder re-acquired in 0.00008 s; the r84 TMPDIR-scoped control **raced** (overlap +1.9394 s). Caveats: the lock is fixed **per checkout** (cross-tree copies race — overlap +1.9647 s, the known r86–r88 residual), and `os.open` failure silently skips exclusion (L29510-29513). |
| 5 | Are the encoded claims as reported? | **Yes on every verdict-bearing law.** Exact-N: `g_own` 8 infos, `g_two` 4 (2+2 across drivers), parse class `007/+3/" 3"` → 7/3/3; the 7 unbounded legs alive at 1.4 s with 65–66 infos. Blocks: 8192→20480→32768 at 0.3/0.6/0.9 s, all %4096. Signal class: INT/TERM rc 0 flushed, KILL −9 / HUP −1 / USR1 −10 unparseable. `o_kill` rc −9 with **49152 B / 46 rows** (incremental write, the boundary falsification folded). Schema: all armed invariants green on 40 blocks; suspension **21 pre / 0 post**. xw: registry mismatch (536870922 in pactl+Node, not in 13 native Modules), blank line 28 survived, 0→1 Client footprint, 8 dict-identical shared blocks, µs-band `x_top`, Profiler refusal ×2, SIGPIPE −13, /dev/full silent. **The mismatches are arithmetic/prose/witness-absence level (ADJ-1…ADJ-6), not falsified measurements.** |
| 6 | Custody verdict | **INTACT (pin, receipt chain, teardown witnesses) · GREEN ×2 (both cited receipts re-derive; 222/222 checks) · LOCK FOCUS VERIFIED · NO VERDICT-BEARING DEFECT FOUND.** Defects: a headline leg count that matches nothing (ADJ-1), figures that match neither receipt (ADJ-2), run-2-only provenance (ADJ-3), a `modules_delta` witness that does not exist (ADJ-4), prose/staleness nits (ADJ-5), a wider-than-armed signal-class claim and unrecorded ambient claims (ADJ-6). No falsified measurement, no residue, no write-scope violation. |

---

## 1. Claim→sha chain, re-derived

### 1.1 Fixture chain (commit pin)

| revision | sha256 | re-derivation |
| --- | --- | --- |
| `0d732989` (pin) | `623c25cc55521472dc54a1ab2b4ccb4a9836fda3ca1a71dcca06092a4317cd22` | pinned archive file = worktree copy; 32 062 lines; matches the sha the report cites (L171-172) |
| diff | `+1561 / −3`, 6 hunks | `@@ -29252,6 +29252,1535 @@` (family block, appended after `pwtop_r88_entry`, before `def main()`), `@@ -29381,6 +30910,7 @@` (add_argument **L30913**), `@@ -29388,7 +30918,7 @@` (mutex sum **L30921**), `@@ -29821,6 +31351,34 @@` (dispatch **L31355–31381**), `@@ -30471,7 +32029,7 @@` (`mode` **L32032**), `@@ -30491,7 +32049,7 @@` (`suffix` **L32052**) |
| deleted lines | exactly 3 | the pre-r89 mutex sum, `mode`, `suffix` — each replaced in place with the `probe_pwprof_r89` head; insertion-only otherwise |
| commit totals | 2 files, 1 776 insertions, 3 deletions | fixture + report; **the receipts are not in the commit** |

Namespace/wiring census on the pin: `probe-pwprof-r89` ×4, `probe_pwprof_r89`
×4, `r89a_ns_`/`r89a_ns2_`/`r89a_nsb_` ×1 each, `r89arole` ×4; the only
`set-default` occurrences in the new block are 10 comment-prose lines
(“never set-default-*”); `tempfile.gettempdir()` = 0 in the family.

### 1.2 Receipts — two lane executions, both cited

| canonical dir (untracked) | wall (local) | sha256 | status | own pid | loadavg |
| --- | --- | --- | --- | --- | --- |
| `20261016T074733533774Z-pwprof-r89` | 04:47:33 | `1d7a24afd20d5ad8f02441288426bbfd940d5667c8bf36dc5980d4718b1310ee` | green, 52 legs (27/12/4/9) | 1723178 | 56.9–64.1 |
| `20261016T074816877001Z-pwprof-r89` | 04:48:16 | `3e756403ecca86d9d9c982812733c57aecdc8fd421428daadeef3aff097d4274` | green, 52 legs (27/12/4/9) | 1728427 | 52.4–63.5 |

Timeline: **fixture mtime 04:46:11** (size 1 611 226) → **pyc header
`src_mtime 04:46:11`, `src_size 1611226`** (compiled from the final bytes)
→ run 1 ends 04:47:33 → **lock witness 04:47:42 (`pid=1728427` = run 2)**
→ run 2 ends 04:48:16 → commit 04:49:33. Both cited runs therefore ran on
the committed bytes; no write follows. **Only two pwprof-r89 run dirs exist
on disk** — no third/red dev receipt (the r88 “uncited red run” class does
*not* recur). No author-pid temp-dir residue in TMPDIR.

**Custody (ADJ-5 class, r86–r88 recurrence).** No `pwprof-r89` receipt is
tracked and neither receipt embeds a fixture sha / HEAD (`grep 623c25cc` =
0 hits in both), so “identical bytes” is re-derivable only from the host
timeline + the pyc header. The report's “Files changed … Nothing committed.”
heading (L20) is stale in the landed artifact — the fixture and report *are*
the commit.

---

## 2. Arithmetic reconciliation

### 2.1 The assigned cells (both cited runs)

| entry | receipt leg keys | report header | report-listed legs | content verified |
| --- | --- | --- | --- | --- |
| `pwprof_gate_r89_probe` | **27** (17 `g_*` + 10 `n_*`) | 27 | 27 | exact-N (`g_own` 8, `g_two` 4 = 2+2), INT/TERM flush, KILL/HUP/USR1 truncate, 4096 B blocks, `-o` ignored, refusals rc 255 (connect_down ×2, opt), strtol lattice (7/3/3 exact; 7 unbounded) |
| `pwprof_oart_r89_probe` | **12** | 12 | 11 (`o_link` unlisted) | 10 rows + aux set, graceful bytes, **49152 B/46 rows after SIGKILL**, truncating open, eager at t=0.010, default `profiler.log`, literal `-`, `/dev/null` aux, 3 open refusals |
| `pwprof_schema_r89_probe` | **4** | 4 | 3 (`s_link` unlisted) | 40 blocks all invariants green, count continuity 39→40, suspension **21→0** |
| `pwprof_xw_r89_probe` | **9** | **8** (one low) | 8 (`x_link` unlisted) | registry mismatch, blank line 28, 1-Client footprint, 8 shared blocks, µs band, refusal ×2, SIGPIPE, /dev/full |
| **total** | **52** | **51** | **49** | `failures: []` ×4 ×2; `coverage_blocked` **absent** ×4 ×2; teardown witnesses clean in every entry |

**ADJ-1 (arithmetic).** The commit message and report L5 claim “**47 legs /
4 entries**”. The receipts carry **52** leg keys in both runs; the report's
own per-section headers sum to **51**; its listed legs sum to **49**. No
natural convention (armed legs, verdict-referenced legs = 32, non-link legs
= 48) yields 47. The claim is a count slip with no receipt basis; every
leg it *omits* is green in both receipts. The labrat confirmed 52/51/47
independently.

### 2.2 Re-derivation (`laws-recheck.txt`, 222/222)

Both runs, all four entries: entry integrity (failures `[]`, coverage key
absent, `own_nodes_after []`, `sinks_gone` all true, unloads rc 0, no
`residual_destroy`, no foreign `r89a_` nodes); the full gate/oart/schema/xw
law sets listed in the verdict table. One claim is wider than its armed
witness: the family docstring says “only INT/TERM flush (every other signal
truncates)” while the receipts arm KILL/HUP/USR1 as truncating — the
boundary seat's QUIT(−3)/USR2(−12) witnesses are not re-armed in this
family (ADJ-6).

### 2.3 Cross-run stability (run 1 vs run 2, pid/number-normalized keys+values)

993 normalized leaves; 133 differ; 97 are the volatile classes
(wall/stream text/bytes/argv/loadavg). The 36 others are volatile-by-design
or ambient: ids (`clock_ids`/`driver_ids`/`own_node_id`), µs medians/ranges,
`kill_mono`, artifact sizes, `x_conc` bytes, `n_abc` `n_info` 66→65 (the
report's own declared 65–66 band), and the xw `oracle_at_start.sink_meta`
`None→SPDIF` (an ambient snapshot, never a pwprof verdict input).
**Zero verdict-class differences** — green ×4 in both runs.

---

## 3. The assigned focus — the fixed-path family lock

Method: the committed `ROOT` expression (L26), the `PWPROF_R89_*` constants
and `_pwprof_r89_family_lock` (L29505-29523) were extracted **verbatim**
from the pin and exec'd with `__file__` pointed at two pinned tree copies;
children were raced with different TMPDIRs. The r84 TMPDIR-scoped lock
supplied the negative control.

| probe | result |
| --- | --- |
| resolved path, child A (`TMPDIR=…/tmpA1`) | `…/r89-scribe-work/corpus/live/measure_audio-pwprof-r89.lock` |
| resolved path, child B (`TMPDIR=…/tmpB1`) | **identical** — outside both TMPDIRs |
| acquire windows (A, different TMPDIRs) | A 0.0001 s; B waited **1.9507 s** → strict serialization (overlap −0.0025 s) |
| same-TMPDIR pair | serialized (overlap −0.0017 s) |
| dead holder | re-acquired in **0.00008 s** (flock released on process death; the file is never unlinked) |
| r84 TMPDIR-scoped control | two paths inside each TMPDIR, overlap **+1.9394 s** — RACED as expected |
| cross-tree copy of the same commit | two paths, overlap **+1.9647 s** — RACED: fixed **per checkout** (known r86–r88 residual) |
| lane file, `O_RDONLY` + `LOCK_SH\|LOCK_NB` probe | acquired in 5e-06 s (no exclusive holder at probe time); content unchanged (sha `d4fb899e…`) |

Static properties: blocking `fcntl.flock(fd, fcntl.LOCK_EX)` (no `LOCK_NB`
fallback); fd stored in a `main()`-local at L31373 (“held to exit”), so
release is process-scoped; witness write `pid=… ns=… role=…` guarded by
`except OSError: pass`; the function returns `None` if `os.open` fails
(exclusion silently skipped — open-failure path, not TMPDIR-dependent); no
`unlink()` of the lock path anywhere; the four entry calls (L31375–31381)
all follow the
lock line inside the same `if` block.

Lane witness timeline (last-writer-wins, never unlinked): at audit the file
held `pid=1728427 ns=r89a_ns_1728427 role=r89arole1728427` (52 B, sha
`d4fb899e…`, mtime **04:47:42**) — **run 2's pid**, matching that receipt's
`contention.own_pid`, sitting between run 1's end and run 2's end. It is
not a lock record, only a witness, and is volatile (sibling replays
overwrite it).

---

## 4. Caveat rows and the encoded claims

| encoded claim | committed arm | run 1 | run 2 |
| --- | --- | --- | --- |
| exact-N completions | `g_own`/`g_two` verdicts L29944-29956 | 8 / 4 (2+2) | 8 / 4 (2+2) |
| strtol parser lattice | `n_*` loop L29927-29933 | 7/3/3 exact; 7 unbounded | same |
| 4096 B stream blocks | `g_blocks` verdict L29971-29977 | 8192/20480/32768 | same |
| INT/TERM vs KILL truncation | signal verdicts L29957-29970 | rc 0 / rc 0; −9/−1/−10 | same |
| SIGKILL leaves 49152 B | `o_kill` verdict L30174-30180 | 49152 B, 46 rows | 49152 B, 46 rows |
| schema invariants | `s_window` stats + verdicts | all green, 40 blocks | all green, 40 blocks |
| suspension 21→0 | `s_suspend` verdict L30432-30443 | pre 21 / post 0 | pre 21 / post 0 |
| xw registry mismatch | `x_modreg` verdict | idx 536870922 ∉ 13 Modules | same |
| xw broadcast record-level | `x_conc` verdict (dict-identity only) | shared 8, identical | shared 8, identical |
| xw µs band 0.25–4.0 | `x_top` `_close` L30746-30748 | 2.3/0.9 vs 4.09/2.22 | 1.6/0.6 vs 2.55/1.40 |
| write-error / SIGPIPE | `x_devfull`/`x_sigpipe` | rc 0, 0 B; −13 | same |

**ADJ-2 (provenance).** Report numbers that match **neither** cited receipt:
L66 “47 infos” (receipt `n_info` = **46** for `g_term` and `g_int`, both
runs); L97 `o_int` “32347 B” (receipts 32362 / 32340); L106
`profiler.log` “4320 B” (receipts 4314 / 4312). These are volatile-by-design
fields, never verdict inputs, but the report presents them as measurements
of the cited runs; the likely source is an unpreserved dev observation (the
r89 report — unlike r88 — never mentions a dev run at all).

**ADJ-3 (provenance).** Run-2-only values presented without attribution:
`x_conc` “6471 B = 6471 B” (r1 6503), `x_top` “1.6us/0.6us” + medians
“2.55/1.40” (r1 2.3/0.9, 4.09/2.22), `o_dash` “6468 B” (r1 6472), `g_two`
“0.071 s” (r1 0.081). All still green in run 1 under the armed arms; only
the quoted figures are run-2.

**ADJ-4 (witness absence).** Report L153 claims `modules_delta == 0` for
`x_foot`. Neither receipt contains a `modules_delta` key (keys are exactly
`pwprof_before, pwprof_during, clients_added, nodes_delta, rc`) and the
fixture never computes one; the armed footprint law is
`pwprof_during == before+1` and `nodes_delta == 0`, both green. The
`modules_delta` clause is unsupported prose (the labrat independently
confirmed the key’s absence).

**ADJ-5 (prose/staleness nits).** “`failures: {}`” (L175/178) — the
receipts carry `[]` (empty list); “`coverage_blocked` empty” — the key is
**absent** (never `setdefault`ed), which is the stronger fact; “Nothing
committed.” (L20) is stale in the landed artifact; “no owned
`pw-play`/`pw-profiler` processes” (L180) has no process-census field in the
receipt (teardown code only); “(`r87t_ns`, `r84a_probe_548706` … untouched)”
(L182) names foreign residue that does not appear in the receipts
(0 hits — only `foreign_r89a_nodes` is recorded, and it is `[]`).

**ADJ-6 (class width).** The family docstring and report say “only INT/TERM
flush”; the receipts arm 3 truncating witnesses (KILL/HUP/USR1). The
boundary seat measured QUIT(−3)/USR2(−12) as truncating in its own
receipts, but this family does not re-arm them — the prose is wider than the
armed evidence (r88-ADJ-8 class).

---

## 5. Adjudication items (no judgment passed — for the canonical judge)

| # | seat | severity | item | evidence |
| --- | --- | --- | --- | --- |
| ADJ-1 | author | arithmetic | “47 legs / 4 entries” (commit + report L5) vs **52** receipt leg keys (27/12/4/9) and the report's own header sum **51** (xw says 8, receipt has 9 — the uncounted leg is `x_link`). | `receipt-chain.txt`; `laws-recheck.txt` §5; labrat |
| ADJ-2 | author | provenance | `g_term`/`g_int` “47 infos” (receipt 46 ×4); `o_int` “32347 B” (32362/32340); `profiler_log` “4320 B” (4314/4312) — no cited run matches. | `report-claims.txt`; labrat |
| ADJ-3 | author | provenance | Run-2-only figures quoted for `x_conc` (6471), `x_top` (1.6/0.6; 2.55/1.40), `o_dash` (6468), `g_two` (0.071 s); run 1 differs but passes the same arms. | `report-claims.txt`; `laws-recheck.txt` |
| ADJ-4 | author | witness absence | `x_foot` “`modules_delta == 0`” — key exists in neither receipt nor the fixture; only `nodes_delta` is armed. | `laws-recheck.txt` §4; labrat |
| ADJ-5 | author | prose/custody | `failures: {}` vs `[]`; “coverage_blocked empty” vs key absent; stale “Nothing committed.”; process-census and foreign-residue claims without a recorded witness; receipts untracked and embed no sha/HEAD. | `receipt-chain.txt`; `report-claims.txt` |
| ADJ-6 | author | class width | “only INT/TERM flush” armed with KILL/HUP/USR1 only; QUIT/USR2 witnesses live in the boundary seat's receipts, not re-armed here. | `laws-recheck.txt` §2 |

---

## 6. Evidence index (`corpus/live/r89-scribe/`)

- `laws-recheck.txt` — 222/222 checks on both receipts (all four entries).
- `lock-verify.txt` — static + dynamic lock evidence (the assigned focus).
- `receipt-chain.txt` — sha256 chain, entry integrity, timeline, lock witness.
- `fixture-diff.txt` — hunk map, the 3 splices, namespace census.
- `report-claims.txt` — claim → receipt re-derivation table (ADJ-1…ADJ-5).
- `cross-run.txt` — run1↔run2 stability (993 leaves, 0 verdict-class diffs).
- `path-existence.txt`, `host-live.txt`, `manifest.json`.

Nothing committed; no tracked file touched. The canonical judge owns the
verdict.
