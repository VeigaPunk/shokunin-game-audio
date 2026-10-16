# r90 foldfix — the wpstate / pw-link / wp-format family: FF1–FF6 folded, fresh green on the landed bytes

Seat: **foldfix** (leaf). Lane repo `~/Projects/shokunin/audio-shokunin`, basis
**lane HEAD `a2c6e3b7`** (the r90 landing `f50cf66a` is an ancestor; the r90
block is byte-identical to the landing there — the critic's A1/A2). Window
**2026-10-16 07:18–07:25 local (10:18–10:25Z)**, host `plazir27`, loadavg
**1.8–6.6** with sibling `r99`/`r100` batteries live. **Zero commits, zero
pushes, no `set-default-*`, no `wpctl set-default`.** Two files changed:
`corpus/fixtures/measure_audio.py` (**+659 / −194**, 24 hunks) and
`reports/round-90/r90-author.md` (**+109 / −16**, 7 hunks).

## 0. Verdict

**The union is folded and the family is green on the landed bytes, with the
new discriminators, the host-global lock, the retry branches, the residue
census and the attribution populated on the green receipts — and every
counterexample the critic named is now a named block instead of a vacuous
green.**

| claim | status |
| --- | --- |
| FF1 — legs on every block path, receipt written after the teardown | **DONE** — forced-block probe: 4/4 entries carry `legs`, `legs_measured`, `measured: false` and a census-bearing receipt (§2.1, §5) |
| FF2 — host-global bounded family lock with stale handling | **DONE** — `/run/user/1000/ufo-measure_audio-wpstate-r90.lock`, 2 s cap → named busy block, stale text recorded, 0 bytes after release, dispatch branch probed (§2.2, §5) |
| FF3 — phantom-tunnel + `k_w_late` retry-once-record-both, unknown refusal named | **DONE** — both legs record two attempts and arm only the branch-invariant claim; `wpstate_unknown_refusal` classifies the real refusal (§2.3, §5) |
| FF4 — receipts carry seat + fixture_sha256; untracked paths no longer cited as evidence | **DONE** — receipts carry `seat`/`pid`/`fixture_sha256`/`run_id` and are filed under `corpus/live/<seat>/receipts/`; the doc's evidence section names every `corpus/live/**` path untracked (§2.4) |
| FF5 — store-residue census leg | **DONE** — `w_store_residue` leg + armed host-wide ceiling on every entry's teardown (§2.5, §5) |
| FF6 — doc fixes (k_w_late attribution, stderr shape, hunk count, sha provenance) | **DONE** — plus the undisclosed `_pwprof_r89_stream` delta and the mutex-guard accounting (§2.6) |
| fresh green on the landed bytes | **YES** — two runs on `e2e5a002…` (16/15/24/6 = **61 legs**), `rc 0`, `failures: {}`, `measured_all: true`, run census 4/4 (§4) |
| the pre-fold counterexamples re-derived on the frozen bytes | **YES** — block path (no `legs`, receipt without census, `failures: []`), tree-local lock, no residue leg, author-named receipts (§3) |

One **disclosed addition outside the FF list**: a bounded entry-level daemon
gate (the r95 C3 pattern the task names as the reference). It is what turns a
wedged shared daemon into a named block instead of a red or a silent green —
the r90 author's own third battery hit exactly that wedge. Drop it alone if
the orchestrator judges it out of scope; nothing else depends on it.

## 1. Bytes, tree discipline, method

- **Implementation sha (the number to re-derive against).** Lane HEAD blob
  `7a070fa817c4de6f4ae5eb5be38e7cfc2cdbb18cad605ee52427afcf0a6ca2bc` (47 424
  lines) → folded `e2e5a002a701bf5165cc04ee2f20e473148723df379b0f72058716187df18923`
  (47 889 lines). Derivation: `sha256sum corpus/fixtures/measure_audio.py`
  and `git show HEAD:corpus/fixtures/measure_audio.py | sha256sum`. The
  report file: `d51f6385…` → `d8effb5ec8c437a935bfdea770440e21e81956348efca457a0b2bbd1f22c50c6`.
- **Diff arithmetic** (`git diff --numstat`): fixture **659 added / 194
  deleted, 24 hunks**; report **109 / 16, 7 hunks**. Every fixture hunk is
  inside the r90 block (first hunk at 35 617) plus the single r90 dispatch
  hunk in `main()` (`@@ -46573,14 +46989,63 @@`); no other family's code is
  touched, and the argparse mutex still refuses
  (`--probe-wpstate-r90 --probe-sox-r94` → **rc 2**, `error: choose one probe
  mode`).
- **Run tree**: `/home/vgpnk/Projects/shokunin/r90f-tree` = `git archive HEAD`
  (tracked content only, 62 MB). The **before** battery and both before-probes
  ran on the pristine bytes (sha verified `7a070fa8…`); `fold.patch` was then
  applied with `patch -p1` and the tree sha re-verified `e2e5a002…` before the
  **after** runs. The lane worktree file and the tree file are byte-identical
  at the final revision.
- **Seat method disclosure**: this seat's tool surface exposes **no `lsp`
  device**, so the edits were made by hand with exact-string replacements and
  verified by (a) `ast.parse` on the final bytes, (b) the full battery runs,
  (c) four probe scripts (eight probe runs). No symbol-aware rename was needed
  — every change is local to the r90 block plus its dispatch and the doc. The
  frozen `probeParent` slot **spawned no labrat**: every mechanism here (the
  daemon, the lock, the fixture client, the graph, the store) is directly
  drivable by this seat, so an advisory depth-2 probe would have re-run work
  this seat already owned — disclosed, not silently skipped.
- **Provenance of every number below**: derived from a receipt, a probe JSON
  or a command in §5/§7, never transcribed from prose.

## 2. The union, item by item

### 2.1 FF1 — legs preserved and the receipt written AFTER the teardown

- `_wpstate_r90_block` now takes `legs`/`census`/`extra_nodes`, sets
  `entry["legs"]`, `legs_measured`, `measured: false`, and runs the **same**
  teardown + exit census as the normal path; `_wpstate_r90_finish` is the new
  normal-path close (`legs`, `legs_measured`, `measured: true`).
- `_wpstate_r90_teardown` gained `census=` (sinks already unloaded mid-entry:
  the vanished-target sink, the module-control sink) so `sinks_gone` is never
  a vacuous `{}`; it names `sinks_censused` and adds a `sinks_gone_note` when
  nothing was loaded.
- All four entries were restructured: the `try/finally` pair is gone, every
  early `return` and a new `except Exception` handler go through the block
  (a named abort), and **the dispatch writes the receipt after the entry
  function returns** — i.e. after the teardown/census. The dispatch also adds
  a run-level `wpstate_r90_run_census` record (`entries_measured`,
  `entries_blocked`, `legs_total`, `measured_all`).
- *Evidence*: `before-block.json` — forced refusal of `_wpstate_r90_load_ns`
  on the frozen bytes gives **4/4 entries with no `legs` key, no `measured`
  key, `failures: []`, and an on-disk receipt whose keys are
  `['blocked','contention','coverage_blocked','failures','foreign_r90a_nodes',
  'inventory','loadavg','oracle_at_start','probe','tools','unloads']`** —
  no census, while the *returned* dict does carry it (the critic's
  counterexample 3, re-derived). `after-block.json` on the same stimulus:
  4/4 `legs_present: true`, `measured: false`, `receipt_has_census: true`;
  the store entry keeps its 5 partial legs (`w_settings`,
  `w_settings_flags`, `w_meta`, `w_state_dir`, `w_cross_volume`).
- The lock-blocked entry is the one admissible `failures: []` + 0-legs shape:
  it is a **named block** (`blocked` + `coverage_blocked` set), `measured:
  false`, and the dispatch writes its receipt too (§5 dispatch probe).

### 2.2 FF2 — host-global, bounded, stale-aware family lock

`_wpstate_r90_lock_path` resolves
`$XDG_RUNTIME_DIR/ufo-measure_audio-wpstate-r90.lock` (fallback
`~/.local/state/…`); `_wpstate_r90_family_lock(wait_s=600)` acquires with
`LOCK_EX|LOCK_NB` in a bounded retry loop (poll 0.25 s) and returns a record
(`fd`, `block`, `path`, `waited_s`, `holder_text`, `stale_text`); expiry names
`wpstate_r90_family_lock_busy` instead of waiting; `_wpstate_r90_lock_release`
truncates **and** closes; `_wpstate_r90_lock_blocked_entry` gives every entry a
named block when the lock is not acquired, and the dispatch records the lock
as a measurement entry (path/waited/holder/stale/block) and writes receipts
for the blocked entries.

*Evidence*: `before-lock.json` — path
`<tree>/corpus/live/measure_audio-wpstate-r90.lock`, `host_global: false`,
`old_path_is_tree_local: true` (the lane repo's and the tree's paths differ →
two trees, two locks, both families run), acquire is an uncapped
`flock(LOCK_EX)` (not called while the holder was live), no stale handling,
and the pre-fold dispatch left its holder text behind at that tree-local path
(73 B at 07:18; the before-lock probe then overwrote it with its own holder
text, 36 B — the tree-local file is used by every process in that tree and by
no one else).
`after-lock.json` — `host_global: true`, a live holder started from a
**different directory** is refused after **2.001 s** with the named block
quoting the holder text, a stale text naming a dead pid is recorded
(`stale_text`, `stale_pid_dead`), and the file is **0 bytes** after release.
`after-dispatch-lock.json` — the dispatch branch: 4/4 entries
`measured: false`, `legs: {}`, named block, receipts written; run census
`entries_measured: 0`, `legs_total: 0`.

### 2.3 FF3 — the two race legs retried once, both attempts recorded, unknown refusal named

- `_WPSTATE_R90_ERR_CLASSES` gains **`wpstate_unknown_refusal`**
  (`Failure: Unknown error code`) — the refusal the critic actually measured
  on the phantom load, which was `error_class: null` before.
- `m_phantom` now runs the load up to **twice** (the family's own `w_settings`
  pattern), records both attempts with their 8 args-aware probes, and names
  each attempt's branch: `rc0_with_id` | `refused` | `unexplained`. Armed:
  every attempt is one of the admissible branches, a `refused` attempt has a
  **named** class, no `r90a_tun_<pid>` node/sink appears, and no probe holds
  **my** module row for the tunnel's `sink_name=`. `rc 0 + id` is a recorded
  field (`rc0_with_id_seen`), not a law.
- `k_w_late` now runs up to **twice** with a **fresh late sink per attempt**
  (an already-existing port would make the second `-w` return immediately and
  fake a different red), records both attempts, and arms only
  `linked` | `refused` | `stimulus_failed` (the last is a named coverage
  block, not a red); the wall band is armed only on the linked branch.
- *Evidence*: `after-retry2.json` — first `-w` forced into the refused branch
  (late sink loaded by the hook, rc 255 `wpstate_link_failed`, no edge):
  `attempts_run: 2`, branches `["refused","linked"]`, final `linked` at
  1.524 s, **no `k_w_late` failure**. First tunnel load forced into the
  refusal: `attempts_run: 2`, branches `["refused","rc0_with_id"]`, classes
  `["wpstate_unknown_refusal", null]`, no failure. A **real** race was also
  caught live: in the first retry pass both tunnel attempts refused on the
  genuine load (`Failure: Unknown error code` twice), and the leg stayed
  green with `refused_seen: true`. The two full batteries saw
  `k_w_late.branch: linked` (1.525 / 1.514 s) and
  `m_phantom.branch: rc0_with_id` — so both branches of both legs have now
  been measured on this host.

### 2.4 FF4 — seat + fixture sha + run id on every receipt; untracked paths named

`_wpstate_r90_attribution()` (seat, pid, full `fixture_sha256`, `run_id`) is
folded into every entry and every receipt; `_wpstate_r90_receipt` files under
`corpus/live/<seat>/receipts/` where `seat` is `$UFO_SEAT` when the harness
declares one and otherwise **the tree the fixture executes from**
(`ROOT.parent.name`) — so a critic's forced-block probe can no longer be filed
under the author's name. `run_id` is set by the dispatch before any entry
runs.

*Evidence*: the after-run receipts live under
`r90f-tree/corpus/live/r90f-tree/receipts/` and carry
`seat: r90f-tree`, `pid`, `fixture_sha256: e2e5a002…`, `run_id`; the pre-fold
receipts live under `corpus/live/r90-author/receipts/` with **none** of those
fields (grep for either fixture sha over the pre-fold runs/receipts: 0 hits).
`reports/round-90/r90-author.md` now states that every `corpus/live/**` path
it cites is untracked and was never in the landing tree (the integrate note's
own intent), and names the landed blob as the landing's bytes.

### 2.5 FF5 — the store-residue census leg and the armed ceiling

`_wpstate_r90_store_census` gains `family_rows` (host-wide `r90a_` rows, any
seat/tree) and `family_rows_by_pid`; `_wpstate_r90_teardown` records
`store_at_exit` + `store_residue` and **arms** the host-wide count against
`WPSTATE_R90_RESIDUE_CEILING = 1000` on **every** entry (not only the store
one); the store entry adds a read-only `w_store_residue` leg with the
entry/leg-end delta.

*Evidence*: run 1's `w_store_residue` = `at_entry 327 → at_leg_end 336`
(`delta_rows: 9`, `own_keys: 5`, `ceiling: 1000`); the battery's
`store_at_exit.family_rows` walks 336 → 337 → 341 → 341 as each entry writes
its rows. The ceiling arm fires when lowered: `after-paths.json.ceiling` with
`ceiling: 1` → `store residue: the host-wide r90a_ row count is 355 > the
declared ceiling 1 — the store accumulates without a deletion path and needs
an operator sweep`. The fixture never edits the store (read-only, named in the
leg).

### 2.6 FF6 — the doc corrections

In `reports/round-90/r90-author.md`:

1. **hunk count / numstat** — the worktree diff is +2182/−2, the **landed
   commit `f50cf66a` is +2183/−3 across 6 hunks**, and the third replaced
   wiring line is the `if sum([…]) > 1:` mutex guard (the worktree branch base
   predates it). `r90-integrate.md`'s "in 4 hunks" is named as a counting
   slip.
2. **sha provenance** — `d9a07b14…` is the **author worktree** file; the
   **landed blob is `d3119c5d…`**; no run bundle or receipt recorded any
   fixture hash, so "both green runs are byte-identical to this file" was
   seat-attested, not artifact-witnessed.
3. **the undisclosed helper delta** — of the 49 module-level functions the
   block calls, one differs: `_pwprof_r89_stream` (landed adds
   `preexec_fn=_pwprof_r89_sigreset`, ancestor `5755be5b`), and it is the
   spawn path of the family's four streaming legs.
4. **k_w_late attribution** — the two greens are **1.520 s / 1.527 s**;
   **1.526 s belongs to the superseded run** `20261016T085112273969Z` (whose
   receipt has `late_edges: []`), and the leg is a readiness race, not a law.
5. **stderr shape** — the full run-1 line is `remote 0: error id:<id>
   seq:<seq> res:-5 (Input/output error): set param id:4
   (Spa:Enum:ParamId:Format) flags:<seq> failed` (123 B); green run 2's same
   leg carries **295 B** with two preceding `res:-2 (No such file or
   directory)` lines. Only the `res:-5 … set param id:4 … failed`
   subsequence is invariant (the armed class), the full text is not.

A short **Foldfix** section pointing at this report closes the file, so the
cross-reference the reviewer asked for exists in both directions.

## 3. Before — the frozen bytes on the responsive daemon

Bounded `pactl info` first (`rc 0`, `Server Name:` present), then
`python3 corpus/fixtures/measure_audio.py --probe-wpstate-r90` in
`r90f-tree/` on the pristine bytes (`7a070fa8…`).

Bundle `corpus/live/runs/20261016T101922340578Z-wpstate-r90/measurements.json`:
**rc 0, `failures: {}`, 4 entries, 60 legs** (15/15/24/6). Per entry:

| entry | legs | `measured` | `legs_measured` | `store_residue` | census |
| --- | --- | --- | --- | --- | --- |
| `wpstate_store_r90_probe` | 15 | key absent | key absent | absent | `sinks_gone`, `own_nodes_after`, `own_modules_after`, `store_at_exit` |
| `wpstate_pmod_r90_probe` | 15 | key absent | key absent | absent | 3 keys |
| `wplink_r90_probe` | 24 | key absent | key absent | absent | 3 keys |
| `wpformat_r90_probe` | 6 | key absent | key absent | absent | 3 keys |

The frozen bytes were **green in this run** — `k_w_late` rc 0 at 1.523 s with
one late→L3 edge, `m_phantom` rc 0 + id. This adds one more green sample to
the critic's tally; it does **not** reproduce the F2/F7 reds (their rate is
~1 in 4), and the report says so rather than implying the fold fixed a red.
What the before-run does carry, structurally:

- the store census walks `rows 8741 → 8754` with `own_keys 0 → 5` — the
  residue is real, and nothing in the pre-fold code counts it host-wide or
  arms it;
- the family lock is left behind at
  `r90f-tree/corpus/live/measure_audio-wpstate-r90.lock` (**73 B**, the
  tree-local path) and **no host-global lock file exists**;
- the receipts are filed under `corpus/live/r90-author/receipts/` (4 files)
  by a tree that is not the author's, with no seat and no sha;
- the block-path counterexample is re-derived by `before-block.json` (§2.1)
  and the lock counterexample by `before-lock.json` (§2.2).

## 4. After — the fold bytes (two greens)

Both runs on `e2e5a002…`, both preceded by a bounded `pactl info` (`rc 0`):

| receipt | stamp (UTC) | entries | legs | failures | run census |
| --- | --- | --- | --- | --- | --- |
| `after-run1` | `20261016T102137287133Z` | 4 | **61** (16/15/24/6) | `{}` | 4/4 measured, 61 legs |
| `after-run2` | `20261016T102231559518Z` | 4 | **61** | `{}` | 4/4 measured, 61 legs |

Per entry (run 1; run 2 identical in every armed cell):

| entry | legs | `measured` | `legs_measured` | `coverage_blocked` | `sinks_gone` | `sinks_censused` | `own_nodes_after` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `wpstate_store_r90_probe` | 16 | true | 16 | — | 5 names, all true | 5 names | `[]` |
| `wpstate_pmod_r90_probe` | 15 | true | 15 | — | 3 names | 3 names | `[]` |
| `wplink_r90_probe` | 24 | true | 24 | — | 4 names | 4 names | `[]` |
| `wpformat_r90_probe` | 6 | true | 6 | — | 1 name | 1 name | `[]` |

Everything else the fold must show on a green receipt:

- **lock record** — `wpstate_r90_family_lock`:
  `path=/run/user/1000/ufo-measure_audio-wpstate-r90.lock`, `acquired: true`,
  `waited_s: 0.0`, `holder_text: null`, `stale_text: null`, `block: null`.
- **run census** — `entries: 4`, `entries_measured: 4`, `entries_blocked: []`,
  `legs_total: 61`, `measured_all: true`, `lock_block: null`.
- **FF3** — `k_w_late`: `attempts_run 1`, `branch linked`, `wall_s 1.525`
  (run 2: 1.514), `linked_seen true`, `refused_seen false`, the late→L3 edge
  present; `m_phantom`: `attempts_run 1`, `branch rc0_with_id`,
  `node_present false`, `sink_present false`, `rc0_with_id_seen true`.
- **FF5** — `w_store_residue`: `at_entry 327 → at_leg_end 336`
  (`delta_rows 9`), `own_keys 5`, `ceiling 1000`; `store_at_exit` carries
  `family_rows`/`family_rows_by_pid`/`rows`.
- **FF4** — every receipt on disk carries `seat: r90f-tree`, `pid`,
  `fixture_sha256: e2e5a002…`, `run_id` (e.g. run 1's store receipt
  `run_id: 20261016T102054396656Z`), and lives under
  `r90f-tree/corpus/live/r90f-tree/receipts/`.
- **Determinism** — `measured`, `legs_measured` and `failures` are identical
  across the two runs for all four entries; the differing cells are the
  pid-bearing names, the wall times, the store row counts and the run ids.

## 5. Negative-path probes (the new discipline, live)

Artifacts in `/home/vgpnk/Projects/shokunin/r90f-probes/` (scripts +
JSON). "Before" = pristine `7a070fa8…`; "after" = `e2e5a002…`.

| probe | stimulus | result |
| --- | --- | --- |
| `before-block.json` | forced `_wpstate_r90_load_ns` refusal | 4/4: **no `legs` key**, no `measured`, `failures: []`, receipt on disk **without** census; returned dict *with* census — the critic's counterexample, re-derived |
| `after-block.json` | same stimulus | 4/4: `legs` present, `measured: false`, `legs_measured` set, receipt **with** census (`sinks_gone`, `sinks_censused`, `own_nodes_after`, `own_modules_after`, `store_at_exit`, `store_residue`) |
| `before-lock.json` | live holder, path inspection | tree-local path, `host_global: false`, uncapped `flock(LOCK_EX)` (not called), no stale handling |
| `after-lock.json` | live holder from another directory, 2 s cap | named `wpstate_r90_family_lock_busy` after 2.001 s with the holder text; stale dead-pid text recorded; **0 bytes** after release |
| `after-dispatch-lock.json` | the dispatch's lock-blocked branch | 4/4 `measured: false`, `legs: {}`, named block, receipts written; run census `entries_measured: 0`, `legs_total: 0` |
| `after-paths.json` (daemon) | synthetic `pactl info` refusal (the r95 C3 stimulus) | 4/4 named `wpstate_r90_daemon_unresponsive` blocks, `measured: false`, legs present, census present, `failures: []` |
| `after-retry2.json` (`k_w_late`) | first `-w` forced into the refused branch (late port loaded, no link) | `attempts_run 2`, `["refused","linked"]`, final `linked` 1.524 s, `refused_seen true`, **no failure** |
| `after-retry2.json` (`m_phantom`) | first tunnel load forced into the refusal | `attempts_run 2`, `["refused","rc0_with_id"]`, classes `["wpstate_unknown_refusal", null]`, **no failure** |
| `after-retry.json` (`m_phantom`) | first load forced **and** the real load raced into the refusal | `attempts_run 2`, `["refused","refused"]`, both classes named, **no failure** — a live instance of the F2 race staying green |
| `after-paths.json` (ceiling) | ceiling lowered to 1 | `store residue: … 355 > the declared ceiling 1 …` — the arm fires |

## 6. Host hygiene (measured after the runs and after all probes)

`pactl list short modules | grep r90a_` → **0**; `pactl list short sinks` →
**0**; `pw-dump | grep '"node.name": "r90a'` → **0**;
`~/.local/state/wireplumber/stream-properties` → **370** `r90a_` rows (the
structural residue, below the declared 1000 ceiling; 313 at fold start);
host-global lock file → **0 bytes**; no `--probe-wpstate-r90` process alive;
default sink `alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink` and the
`default-nodes` file unchanged (its mtime predates this session, 06:24:37).
No `set-default-*` was ever issued (the receipts' inventory records the same
default sink/source in the before and both after runs).

## 7. Residual risks, blockers, disclosures

- **The races are not eliminated, only made admissible and named.** A final
  `refused` branch on `k_w_late`/`m_phantom` is recorded (and, for
  `k_w_late`, added to `coverage_blocked`) rather than armed; a run that hits
  only refusals stays green by design, which is exactly the invariant the
  critic asked for. The alternative — arming `rc 0 + id` — was falsified
  live on this host.
- **`run_id` is the battery invocation id, not the run-dir stamp.** The run
  dir is stamped at exit (≈43 s later in run 1), so the correlation is by
  pid + timestamp proximity; both are in the receipt. Named, not hidden.
- **The residue ceiling is a declared policy number** (1000) with ~630 rows
  of headroom at fold time. The family has no deletion path by design, so the
  number will need raising or an operator sweep as the host accumulates.
- **The before battery was green**, so this fold's race evidence is the
  critic's flake tally plus the forced-branch probes — not a re-derived red.
  The F3/F5 counterexamples *are* re-derived structurally.
- **No `lsp` device** was available for this tree (hand edits + `ast.parse` +
  battery runs, disclosed in §1).
- **One out-of-union addition** (the daemon gate) is flagged in §0 for the
  orchestrator to accept or drop; the store probe's leg count moves 60 → 61
  because of the FF5 residue leg.
- Every `corpus/live/**` artifact cited here is **untracked by design**;
  `fold.patch` in `r90f-probes/` is the exact diff applied to the archive
  tree and matches the lane worktree bytes at the shas in §1. Nothing was
  committed; the shipping decision is the operator's.

**Verdicts here are seat-side; the canonical Rust runtime remains the only
judge.**
