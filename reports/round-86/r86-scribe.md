# r86 scribe — wave-B gate on the committed pwctl landing (fa5994a0)

host: `plazir27` (local = UTC−3). Lane `~/Projects/shokunin/audio-shokunin`.
Seat: SCRIBE (wave-B gate, r86). Scope: audit the committed r86 landing
`fa5994a0` — `corpus/fixtures/measure_audio.py` (+1758/−3, sha
`5ceba940…`), `reports/round-86/r86-author.md`, and the two cited green
receipts — for claim→sha chains, arithmetic reconciliation (5 entries /
149 legs / 2 green runs), file existence, hash re-derivation, unreported
evidence, the caveat rows (`d_route`, `dump_color_eq` record-only;
`n_format` armed rc-only), and (the round's assigned focus) **whether the
r84-fold family lock is at a fixed lane path rather than TMPDIR-scoped**.

**Read-only on everything except this report and `corpus/live/r86-scribe/`;
no commits, no judgment passed** — every discrepancy below is handed to the
canonical judge as an adjudication item.

Entry state: HEAD `fa5994a029507e666315cd40257988510579284f` (`r86 author:
5 entries pwctl lattice`, 03:31:47 −0300; parent `f309e856`). Every fixture
claim was re-derived from a **commit pin** (`git archive fa5994a0` →
`~/Projects/shokunin/tmp/r86-scribe-work/tree`), not from the worktree;
worktree fixture sha == pin sha. Ambient at audit: loadavg ≈ 85 / 32 cores,
and **sibling wave-B seats were executing r86 work live** (seat dirs
`r86-simplifier` 03:33, `r86-verifier` 03:34, `r86-reviewer` 03:35,
`r86-critic` 03:36; the lane lock file was rewritten by a sibling lock test
at 03:34 — see ADJ-13). No r86 claim below depends on live state; the cited
receipts are the three canonical run dirs, whose shas were unchanged for
the whole audit.

---

## 0. Verdict

| # | question | answer |
| --- | --- | --- |
| 1 | Do the claim→sha chains hold? | **Yes.** Pin fixture sha `5ceba94019eaaa8f1db9ac18ea15023f7e4891e844defe86711f37873059b780` (26 655 lines) = worktree copy; diff is **+1758/−3 (1761 changed lines, 7 hunks)** with exactly 3 deleted lines (mutex sum, `mode`, `suffix` — the r82-r85 convention) plus `import resource`; both cited receipt shas re-derive (`1097d9f1…fc515b`, `fe57c1cb…2390a`); the canonical inventory holds **exactly three** r86 runs, and all three are cited (the red dev run by stamp in prose). **Nit: the report's “+1761/−3” is the total-changed figure, not insertions (ADJ-1); the receipts are host-only, not in the commit (ADJ-3), and carry no fixture sha (ADJ-4).** |
| 2 | Does the arithmetic reconcile? | **Yes.** 34+43+16+22+34 = **149 family legs × 2 green runs**; `failures: []` ×5 ×2; `coverage_blocked` absent (no blocked coverage); every unload `verified_index == captured`, `recycled: False`, `field: sink_name`, rc0; `sinks_gone` all true; `own_nodes_after []`; `foreign_r86a_nodes []`; `meta_keys_gone: true`. **263/263 re-derivation checks pass** (`laws-recheck.txt`), covering every headline law of all five entries. Cross-run: 240 pid-normalized differing leaves, **zero** `exit_code`/`signal`/`killed_at_bound` differences; the 27 volatile fields are identity text, host-churn stdout volumes, one 0.5 LSB median jitter, and one foreign subject-0 key drift (ADJ-7/8/11). |
| 3 | Do the claimed files exist? | **Yes.** Every repo path in the report resolves (`path-existence.txt`; the six “MISS” tokens are env-value strings, an ellipsis, a bare pyc name and a key list — no path defect). Toolchain strings re-verify live (pipewire 1.6.8, wireplumber 0.5.17, pactl 17.0-98-gb096, python 3.14.7, numpy 2.5.3, kernel 7.2.3-arch1-3, `/usr/bin/pw-jack` a POSIX shell script, `libjack.so.0.3.1608` present, no jackd/jack_lsp). |
| 4 | **Is the family lock fixed-path, not TMPDIR-scoped?** | **YES — verified three ways.** Statically: L26 `ROOT = Path(__file__).resolve().parents[1]`, L24124 `path = ROOT / "live" / "measure_audio-pwctl-r86.lock"`, blocking `LOCK_EX` at L24129, acquired at dispatch L25964 “held to exit”; **no `tempfile.gettempdir()` anywhere in the r86 family** (the three hits L14764/L19846/L22318 are the r82/r84/r85 locks, untouched). Dynamically: two concurrent acquirers with **different TMPDIRs** resolved the identical path and serialized 0.000→2.001 / 2.008→4.009 s, with the lock file outside both TMPDIRs; a dead holder does not block (0.0000 s). Independently corroborated by the sibling r86-critic seat's lock test (cross-TMPDIR 2.2064 s; r85 negative control 0.0001 s at two different paths). Caveat: the path is fixed **per checkout** (derived from the fixture's own location), and `os.open` failure silently skips exclusion (L24127-24128) — neither is a TMPDIR dependence. |
| 5 | Are the caveat rows as claimed? | **Yes.** `dump_color_eq` `armed: False` (rc255 `Unknown color: =never` this boot), `d_route` `armed: False` (rc0 0B), `n_format` `armed: "rc_only"` with `has_pod: True` — all re-read from the receipts and the committed verdict lines (L24454/L24657/L24648). The dev run's single red failure was the pre-fix `n_format` pod-presence arm, disclosed in the report. |
| 6 | Custody verdict | **INTACT (pin, receipt chain, teardown witnesses) · GREEN ×2 (both cited receipts re-derive) · LOCK FOCUS VERIFIED · NO VERDICT-BEARING DEFECT FOUND.** Defects are preservation/prose-level: receipts host-only and source-unpinned (ADJ-3/4), line-ref and delta-count prose (ADJ-1/2), two unmentioned armed rows (ADJ-5), an unrecorded filter setup write (ADJ-6), and inherited/host-observation nits (ADJ-7…13). No falsified measurement, no residue, no write-scope violation. |

---

## 1. Claim→sha chain, re-derived

### 1.1 Fixture chain (commit pin)

| revision | sha256 | re-derivation |
| --- | --- | --- |
| `fa5994a0` (pin) | `5ceba94019eaaa8f1db9ac18ea15023f7e4891e844defe86711f37873059b780` | pinned archive file = worktree copy; 26 655 lines; matches the sha the report cites |
| diff | `1758 + / 3 −` (stat: 1761 changed), 7 hunks | `@@ -9,6 +9,7 @@` (`import resource`), `@@ -23726,6 +23727,1728 @@` (family block, added lines **L23730–L25451**), `@@ -23852,6 +25575,7 @@` (add_argument **L25578**), `@@ -23859,7 +25583,7 @@` (mutex sum **L25586**), `@@ -24217,6 +25941,37 @@` (dispatch **L25944–25974**), `@@ -24867,7 +26622,7 @@` (mode **L26625**), `@@ -24887,7 +26642,7 @@` (suffix **L26645**) |
| deleted lines | exactly 3 | the pre-r86 mutex sum, `mode`, `suffix` — each replaced in place with the `probe_pwctl_r86` head; insertion-only otherwise |
| commit totals | 2 files, 1907 insertions, 3 deletions | fixture + report; **the receipts are not in the commit** |

Namespace/wiring census on the pinned copy: `PWCTL_R86_` ×107, `r86a_`
×13 (namespace tags), `probe-pwctl-r86` ×4, `probe_pwctl_r86` ×4
(add_argument, mutex sum, dispatch guard, mode/suffix heads); prior
families untouched. The report's enumeration of wiring omits the
`import resource` line (ADJ-2).

### 1.2 Receipts — three canonical executions, all cited

| canonical dir (untracked) | wall (local) | sha256 | status | landed as |
| --- | --- | --- | --- | --- |
| `20261016T062922907396Z-pwctl-r86` | 03:29:22 | `090a50abc0aab98c…` | **red — exactly 1 failure** (`n_format: rc=0 pod=True — the pod-absence law fails`) | cited in prose (“the earlier dev run … failed once”) |
| `20261016T063006268243Z-pwctl-r86` | 03:30:06 | `1097d9f10ccab4245df4c8624d680e4bb59228c33c52314bb6196d8337fc515b` | green, 149 legs | cited (`1097d9f1…f515b`) |
| `20261016T063043717745Z-pwctl-r86` | 03:30:43 | `fe57c1cb10508dd50b173d334df7bbc10f9af3d0296d0b8e3c674b3a8bb2390a` | green, 149 legs | cited (`fe57c1cb…3920a`) |

The r85 “uncited execution” class (r85 ADJ-1/2) does **not** recur: no
fourth r86 run exists. Timeline: dev 03:29:22 → fixture mtime 03:29:36 →
run1 03:30:06 → run2 03:30:43 → commit 03:31:47. The pre-fix byte set the
dev run measured is not recoverable (no snapshot), but its receipt is
consistent with the disclosure: `n_format` carries `has_pod: True` and no
`armed` key, while both green runs carry `armed: "rc_only"`; dev-vs-run1
shows **0** `exit_code`/`signal`/`killed_at_bound` differences and the
other four entries green.

**ADJ-3 (custody/completeness).** No `pwctl-r86` file is tracked
(`git ls-files | grep -c pwctl-r86` = 0): the landed commit contains the
fixture and the report only, so the two green receipts and the lock witness
are host-only. r85 committed byte-identical seat copies of its two
receipts; r86 did not. The report also still marks the fixture
“**Uncommitted.**”, which was true pre-commit but is stale in the landed
artifact. Preservation-level, not a measurement defect.

**ADJ-4 (custody, inherited).** The receipts embed no fixture sha / git
HEAD (r84-ADJ-6/r85 class), so “two green runs on identical source bytes”
is re-derivable only from the host timeline (fixture mtime between dev and
run1; commit after run2), not from the receipts themselves.

---

## 2. Arithmetic reconciliation

### 2.1 Assigned cells (both cited runs)

| entry | legs | content verified |
| --- | --- | --- |
| `pwctl_addr_r86_probe` | 34 | addressing split (`ls <serial>` resolves / `ls <id>` 0B; `info <id>` resolves / `info <serial>` rc0 unknown global), class census (`typed_rows` > 0, all rows of the named class), indistinguishable-empty law (`ls Bogus`≡`ls node`≡`ls Session` → 0B rc0), pw-dump surface (`<id>`≡`<serial>` byte-identical; bad id 0B rc0; `-C never` 0B vs `-Cnever` full dump; `-C=never` record-only), self-Client law (1 fresh client/invocation), `-r bogus` rc255, `info all`/`list-vars`/`list-remotes` rc0, self-loop info+destroy census |
| `pwctl_params_r86_probe` | 43 | typed enum matrix (pod / remote `res:-2` / local `not implemented`), numeric `3` ≡ `EnumFormat` byte-identical, `Bogus`/`999`/`all` → unknown param type, Format rows (Port pod-absent, Node rc-only), `d_route` record-only, set-param refusals (None echo / empty pod / unknown key stripped / wrong-type None slot / EnumFormat `res:-95` / port Latency echo + not-impl / minQuantum unchanged / bad id / missing json / bogus param) |
| `pwctl_dsp_r86_probe` | 16 | link-validated tap (2 monitor→input edges before the player spawns), windowed medians run-2: 8192 → **2048.0** → **4096.0** → **0.0** → **8191.5** → **8192.0** → **128.0** → **8192.0**; cube-root read-back 63 %; dead scalar key leaves pactl at 100 % while the store reads `Float 0.25`; all writes rc0; player alive at end |
| `pwctl_meta_r86_probe` | 22 | 9 stores (`-l` ≡ `ls Metadata` ≡ store ids), pw-dump strict subset `{31,34,36,39}`, bare ≡ `-n default` byte-equal, bogus store 0B rc0, set-echo/read-back, full replace, `Spa:String` verbatim, absent-key Found-only, delete + absent-delete echoes, dead-subject echo-lies, subject wipe, `-m` filter kill-bounded with all rows carrying the id, `-m 0` subject-0 rows only, subject-0 baseline read-only |
| `pwctl_tools_r86_probe` | 34 | pw-top batch `-n 2`/`-n 0` rc0, batch+TERM rc0 clean vs TUI+TERM **SIGABRT** (`loop.c:189 remove_from_poll`), TUI+KILL SIGKILL, pw-cli stdin trichotomy (`/dev/null` SIGABRT, pipe never exits kill-bounded, `quit` rc0), pw-jack env lattice (Q 512/48000, 256/44100, `-s` alone unset; D 3/4/5; R passthrough; rc0 `-h`/no-args/`-Z`; rc127 exec not found), pw-link rc lattice (create 0, duplicate 255 `File exists`, bogus 255, usage 255, `-I`/`-v` 255, `-l`/`-l -I` 0, `-d <port>` 255, `-d <link>` 0, junk props accepted) |
| **total** | **149** | `failures: []` ×5 ×2; teardown witnesses clean in every entry |

### 2.2 Cross-run stability (run1 vs run2)

240 pid-normalized differing leaves, **zero** verdict-class
(`exit_code`/`signal`/`killed_at_bound`) differences. The 27
error_class/error_hit/has_pod/stdout-volume fields and 4 law-field paths
that differ are all explainable and none is armed:

- **identity text**: serial/object ids inside `error_hit`/`error_class`
  strings, `destroy_census.link_id` (231↔98), `lk_census` ids, self-Client
  serial pairs (run1 `242898→242899`, run2 `243277→243278`).
- **host churn volumes** (unarmed): `ls_Link` 48→0 rows, `ls_Port`
  616→342, `ls_Node` 154→99, `ls_Client` 170→110, `info_all` 3509→2205
  lines / 109 353→68 913 B, `dump_color_join` 13 948→8 296,
  `top_batch` 30→24, `top_tui_term` 25→5, `cli_pipe` 168→3 lines (its
  recorded `error_class` flips `pwcli_remote_enoent`↔`None` on the same
  churn).
- **reader heuristic (unarmed)**: `info_all.has_pod` True↔False — the
  field is `"Object:" in stdout`, and the 40 KB of foreign churn moves it.
- **law jitter**: dsp `reset` median 8192.0 (run1) vs 8191.5 (run2) — 0.5
  LSB, both inside the armed x8192 envelope; the report quotes the run-2
  realization and says so.
- **foreign store drift**: subject-0 keys 4 (run1, incl.
  `default.audio.source`) → 3 (run2) (ADJ-7).

---

## 3. The assigned focus — the fixed-path family lock

Method: the committed `ROOT` expression, the `PWCTL_R86_PID/NS/ROLE`
constants and the `_pwctl_r86_family_lock` body were extracted **verbatim**
from the pin (L26, L23842–23846, L24118–24136) and exec'd with `__file__`
pointed at the pin; two child processes with **different TMPDIRs** then
raced for the lock. Independently, the frozen-probeParent `ufo-labrat` (one
dispatch, read-only, advisory; no exec substrate → static trace only)
hand-traced the same committed lines and reached the same conclusion with
matching line numbers (`labrat` reported `ROOT` L26, lock L24118–24136,
path L24124, call L25964, prior locks L14764/L19846/L22318).

| probe | result |
| --- | --- |
| resolved path, child A (`TMPDIR=…/tmpx1`) | `…/r86-scribe-work/tree/corpus/live/measure_audio-pwctl-r86.lock` |
| resolved path, child B (`TMPDIR=…/tmpx2`) | **identical** — outside both TMPDIRs |
| acquire windows | A 0.000→2.001 s, B **2.008**→4.009 s (driver wall 4.03 s) — strict serialization |
| witness written | `pid=… ns=r86a_ns_… role=r86arole…` (52 B, same format as the lane file) |
| dead holder (lane file, O_RDONLY flock) | acquired in **0.0000 s**, content unchanged (flock releases on process death; the file is never unlinked) |
| sibling r86-critic seat (read-only peek at its receipt) | cross-TMPDIR **2.2064 s** at the lane path; same-TMPDIR 2.2105 s; **r85 negative control 0.0001 s** at two different paths — i.e. the harness can detect non-exclusion and the r86 lock does not exhibit it |

Static properties: blocking `fcntl.flock(fd, LOCK_EX)` (no `LOCK_NB`
fallback); fd held to exit (L25964), so release is process-scoped;
`os.ftruncate` + witness write guarded by `except OSError: pass`; the
function returns `None` if `os.open` fails (exclusion silently skipped —
open-failure path, not TMPDIR-dependent); no `unlink` of the lock path
anywhere. The lane lock file is therefore a **last-writer-wins witness**,
not a lock record: at audit entry it held run2's pid (mtime 03:30,
`pid=2675030`, matching run2's `r86a_ns_2675030`), and by 03:34 a sibling
seat's lock test had rewritten it (`pid=2808000`, dead) — see ADJ-13.
The r84 fold (r84 critic F1, 3-seat consensus) is **applied for r86**;
r82/r84/r85 locks remain `$TMPDIR`-scoped and untouched.

---

## 4. Caveat rows and the dev-run disclosure

| row | committed arm line | run1 | run2 |
| --- | --- | --- | --- |
| `dump_color_eq` | L24454 `armed = False` (bimodal — data only) | rc255 `Unknown color: =never` | same |
| `d_route` | L24657 `armed = False` (realization — data only) | rc0, 0 B, no pod | same |
| `n_format` | L24648 `armed = "rc_only"` | rc0, `has_pod: True` | same |
| dev run `n_format` (pre-fix) | — | failure recorded: `rc=0 pod=True — the pod-absence law fails` (no `armed` key) | — |

`set-default-*`: no invocation inside the r86 family (the only
`pactl set-default-sink` calls in the file are in a pre-r86 family at
L7088/L7107, outside the r86 block). Crash-class legs do zero
`RLIMIT_CORE` in the child: `_pwctl_r86_no_core` (L23902) is the
`preexec_fn` for `cli_devnull` (L25245 `nocore=True`) and for **every**
`_pwctl_r86_sigleg` (L23971), which covers `top_batch_term`,
`top_tui_term`, `top_tui_kill`. Teardown reuses the r85 name-verified
unload (`_pactlmon_r85_unload_own`, L21879) — `verified_index == captured`,
`recycled: False` in all 10 unload records. Reader failures land in
`coverage_blocked` with the witness marked `reader_error` (L24176-24179),
never a vacuous pass.

---

## 5. Adjudication items (no judgment passed — for the canonical judge)

| # | seat | severity | item | evidence |
| --- | --- | --- | --- | --- |
| ADJ-1 | author | nit | Report (and commit subject) say “+1761/−3”; numstat is **+1758/−3** (1761 = total changed lines). | `fixture-refs.txt` |
| ADJ-2 | author | nit | Wiring list omits the fourth wiring change `import resource` (L12, needed for `RLIMIT_CORE`); all line refs after L25500 are **~10 low** (family block end 25 451 not ~25 500; add_argument 25 578; mutex 25 586; dispatch 25 944–25 974; mode 26 625; suffix 26 645 vs ~26 615/26 635). Refs are marked “~”, so shape-only. | `fixture-refs.txt` |
| ADJ-3 | author | custody/completeness | The two cited green receipts are **not in the landing commit** (0 tracked `pwctl-r86` files; commit = fixture + report only), unlike r85's committed byte-identical seat copies; the report still marks the fixture “Uncommitted” (stale post-commit). | `receipt-chain.txt`; `git show --stat fa5994a0` |
| ADJ-4 | author | custody (inherited) | Receipts embed no fixture sha / git HEAD (r84-ADJ-6/r85 class): “identical source bytes” rests on the host timeline, not on the receipt bytes. | receipts' wrapper keys |
| ADJ-5 | author | minor (report completeness) | Two **armed** rows are absent from the report's param-matrix prose: Node `Latency` and `ProcessLatency` (`n_latency`/`n_proclat`) are armed pod-absent in the same verdict group as `p_format` (L24632) and pass 0 B/rc0 in both runs. | L24632; receipts |
| ADJ-6 | author | nit | Unrecorded meta setup write `_pwctl_r86_meta("-n","default",nid,"r86a_k_f","fv")` (L25084) creates the row the `m_filter` leg displays; its cleanup `-d <nid>` (L25089) is also unrecorded. The row is visible in `m_filter` stdout but has no leg of its own. | L25084/L25089; `legs-run*.txt` |
| ADJ-7 | lane/host | observation | Subject-0 key set **drifts across the two cited runs** (run1 4 keys incl. `default.audio.source`, 514 B; run2 3 keys, 416 B) — foreign shared-store churn; the r86 family never writes subject 0 (all `_pwctl_r86_meta` writes target the probe node; reads only for subject 0), and `meta_keys_gone` holds. “Defaults enumerated” is run-dependent. | `legs-run*.txt`; L25091, L25194 |
| ADJ-8 | lane/host | observation | Unarmed fields move with host churn between the two runs: `info_all.has_pod` True↔False and stdout volumes (e.g. `ls_Link` 48→0 rows, `info_all` 3 509→2 205 lines, `cli_pipe` 168→3 lines with `error_class` flipping `pwcli_remote_enoent`↔`None`). Recorded evidence only; no arm reads them. | `run-diff.txt` |
| ADJ-9 | author | nit | Prose shapes: “`failures: {}`” (actual `[]`); “`coverage_blocked: []`” (the key is **absent** in all five entries both runs). | receipts |
| ADJ-10 | author | nit | “serials 243277→243278 across two runs” quotes the **run-2** pair; run1's pair is `242898→242899`. The law (exactly 1 fresh pw-dump client, consecutive serials) holds in both. | `legs-run*.txt` |
| ADJ-11 | author | observation | The dsp headline medians are labelled “run-2 realizations” and match run2 exactly; run1's `reset` median is 8192.0 vs run2's 8191.5 (0.5 LSB jitter, inside the armed envelope). No claim defect. | `legs-run1.txt` |
| ADJ-12 | lane | custody (inherited) | Tracked `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` is still dirty in the worktree (sha `e5a32d87…` unchanged since r85, 1 369 991 B, mtime 03:20:10 — before this seat). Operator item; this seat wrote no tracked file (`PYTHONDONTWRITEBYTECODE=1`, fixture never imported). | `host-live.txt` |
| ADJ-13 | lane | ambient | Sibling wave-B seats ran r86 work during the audit (dirs 03:33–03:36; loadavg ~85); the lane lock file was rewritten at 03:34 by a sibling lock test (`pid=2808000`, dead) — it is a last-writer-wins witness, never unlinked. No new canonical runs dirs appeared, so the author's 3-run inventory stands. The sibling's lock test independently corroborates the fixed-path claim (and includes the r85 negative control). | `lock-verify.txt`; `receipt-chain.txt` |

---

## 6. Write-scope / custody notes

- Committed in `fa5994a0`: fixture (+1758/−3) and the author report — 2
  files, 1 907 insertions, 3 deletions. Nothing else.
- This seat wrote only `reports/round-86/r86-scribe.md` and
  `corpus/live/r86-scribe/` (9 receipts + `manifest.json`; the manifest
  lists each receipt's bytes+sha256 and this report's sha). **No tracked
  file was modified**, no commit, no push, no PipeWire object created
  (only read-only `pw-cli`/`pactl`/`pw-dump`/`pw-metadata` queries), no
  `set-default-*`, no unload. All scratch lived in
  `~/Projects/shokunin/tmp/r86-scribe-work`; every python invocation ran
  with `PYTHONDONTWRITEBYTECODE=1` and never imported the fixture.
- The pin-copy dynamic lock test wrote its witness only into the pin copy
  under scratch; the single lane-file touch was an `O_RDONLY` flock whose
  content was unchanged during the test.
- Exactly one descendant was spawned: the frozen-probeParent `ufo-labrat`
  (read-only, advisory, no exec substrate, no edits).

---

## 7. Remaining risks / blockers

1. No verdict-bearing defect was found. The assigned focus is verified
   statically, dynamically (cross-TMPDIR serialization; dead-holder
   non-blocking), and independently by a sibling seat's negative-control
   test; all 263 re-derivation checks pass on the two cited receipts.
2. The residual risks are preservation-level: the receipts are host-only
   (ADJ-3) and do not pin their source bytes (ADJ-4); the r84-fold lock is
   fixed per checkout, so a fixture copied elsewhere locks its own
   `corpus/live` — TMPDIR-independence holds, global exclusion does not.
3. ADJ-13 means the live lock witness no longer shows run2's pid; the
   author's three-run inventory and both receipt shas were stable
   throughout, and later sibling runs may add their own (non-author) dirs.
4. ADJ-12 is the only tracked-file item and is an operator decision
   (unchanged from r84/r85); no shipping decision is made or implied here.
5. No blockers for the round.

*Seat stop. Read-only; no commits; no judgment — the canonical Rust runtime
remains the sole judge.*
