# r97 VERIFIER — frozen-tree gate on committed `b8ff4efc` (the WirePlumber policy lattice)

Seat: **verifier** (non-author, audio-shokunin r97). Lane
`~/Projects/shokunin/audio-shokunin`; basis **`git archive HEAD`** (`b8ff4efc`,
`r97 author: wppol WirePlumber policy lattice (5 entries/69 legs, +2156/-3)`)
extracted to `corpus/live/r97-verifier/tree/` — the committed bytes, **not** the
worktree. Window **2026-10-16 10:02Z–10:26Z** (local UTC−3), host loadavg
**2.7–6.1** during the runs (32 cores; the r97-boundary window ran at 98–121,
the author's final battery at 12–16 — this gate is the quietest window of the
three). `TMPDIR=~/Projects/shokunin/tmp`. **Zero tracked writes by this seat,
zero commits, zero pushes, no `pactl set-default-*` anywhere**; every artifact
under `corpus/live/r97-verifier/` (untracked) plus this report.

Duty: re-run the full `--probe-wppol-r97` family fresh on the archived tree,
re-derive all 69 legs with an independent law set, probe forgery/mutation
sensitivity, confirm the exit census (0 `r97a` objects/processes, kill guard
honored) and confirm `coverage_blocked` cells are named classes. The frozen
`probeParent` slot spawned exactly **one** read-only `ufo-labrat` (§6).

## 0. Verdict

**PASS on committed bytes, with six recorded findings/nuances and one
self-inflicted incident disclosed and contained (§7).**

- The committed r97 block is **byte-identical** to the author's measured
  worktree bytes (2118 lines, sha256 `f58f0290fff2f76c…` both sides), the
  dispatch splice (34 lines) is byte-identical, and the merge is
  **insertion-only + 3 declared shared-line rewrites** (`git diff HEAD~1 HEAD`
  = `+2156/−3`; the 3 deletions are exactly the mutex-list, mode-select and
  suffix-select lines).
- **Two fresh full-family runs on committed bytes** (this seat's own): both
  **exit 0, `failures: {}`, no blocked classes, 69 leg keys (14/15/21/15/4)**,
  and both re-derive the 17 pre-existing base entries green (14 legs each).
- This seat's **independent law set (260 laws)** — expectations taken from the
  *tracked cross-seat receipts* (boundary `f_settings`, scout `b_wpexec`), not
  from the fixture's own constants — re-derives **260/260 PASS, 0 FAIL,
  0 BLOCKED** on both runs, on the author's two declared greens and on both
  pre-freeze smoke receipts.
- **36 fabricated receipts + 2 controls**: 34 caught by `FAIL`, 2 by
  `BLOCKED` (never green), 2 controls correctly a no-op — **0 missed**.
  Fixture-level mutations red the family and/or the law set, and the
  readiness-gate starvation mutation (`WP_READY_CAP 30.0→0.01`) makes the
  whole family read never-green (4 entries blocked, 1 failed, 0 legs beyond
  the arming entry); the comment-only control stays green.
- **Exit census PASS**: 0 `r97a` objects in the operator's graph, 0 `r97a`
  processes, 0 live private roots, the shared session daemons' pid+start time
  unchanged, and the environ-aware kill guard verified in three arms (foreign
  pid **REFUSED and survived**; own pid killed; a live private core recognised
  and left alone).
- All 69 legs re-derive cell-for-cell against the tracked scout/boundary
  receipts (§3.3); the two runs are identical on every armed cell modulo the
  pid-namespaced node names.

## 1. Frozen tree and byte identity

| check | required | measured | verdict |
| --- | --- | --- | --- |
| archive | `git archive HEAD` | `r97v-head.tar` sha256 `91c500ad66c482130f49f1bd898e171dd3bc6116bc99582ddc366d7b8f7aee88` (3 318 609 920 B) | PASS |
| census | — | **44 581 files / 11 772 dirs / 0 symlinks**; file-set symdiff vs `git ls-tree -r b8ff4efc` = **0** after excluding the three run artifacts the runs themselves wrote into the tree (`runs/r97v-symdiff-b8ff4efc.txt`) | PASS |
| fixture identity | committed blob | `corpus/fixtures/measure_audio.py` sha256 `7a070fa817c4de6f4ae5eb5be38e7cfc2cdbb18cad605ee52427afcf0a6ca2bc` = `HEAD:` blob = tree copy | PASS |
| `py_compile` in the frozen tree | clean | rc 0 | PASS |
| **block byte-identity** | author's worktree bytes | the r97 block (banner → `def main()`) is **2118 lines / sha256 `f58f0290fff2f76c5c343db643585d3b9bb32912dee99aa7e129f262cc8243f5` on both sides** — the author's `wt-r97` file (`f0eb6c509ecc…`, r89-foldfix base `5755be5b`) and the committed file (`7a070fa817c4…`, r96 base `7358f13b`) | PASS |
| dispatch splice | author's worktree bytes | the 34-line `if args.probe_wppol_r97:` dispatch block is **byte-identical**; the `--probe-wppol-r97` arg line is byte-identical | PASS |
| merge shape | insertion-only + 3 splices | `git diff HEAD~1 HEAD -- corpus/fixtures/measure_audio.py` = **+2156 / −3**; hunks: one 2118-line block insertion, the arg line, the mutex `sum([...])`, the 34-line dispatch block, the `mode` select, the `suffix` select; the **only 3 deletions are the 3 declared shared lines** | PASS |
| shared-line lineage | — | the three rewritten lines (mutex/mode/suffix) each carry the r97 term **first** and differ from the author's file only by the *other* rounds' terms the author's r89-era base predates (r90/r91/r92/r95/r96) — an expected base-lineage difference, not a defect | PASS |
| tree content | archive members | `tar -df` over all 44 581 members: **0 “Contents differ”**; only extraction metadata (uid/gid/mode) and 17 artifact `.wav` mtime-only entries (contents sha-identical to the archive); after the §7 restoration the targeted re-check on the fixture + pyc reports **0 size/mtime diffs** and the full post-restore `tar -df` reports **0 “Contents differ”, 0 “Size differs”** | PASS |

**Foreign state, observed and not touched:** while this gate ran, a concurrent
r90 lane committed **`a2c6e3b7`** (10:14:28Z, “r90 adjudicate … wave-B
reports”), moving the repository HEAD from `b8ff4efc` to `a2c6e3b7` and adding
six `reports/round-90/*.md` files. `b8ff4efc` is still an **ancestor** of the
new HEAD, so the archived tree is the assigned commit; a symdiff against the
*moved* HEAD would show those six foreign files — the symdiff above is taken
against `b8ff4efc` and is the valid record. A second foreign edit landed in the
**shared worktree** at 10:17:45Z: `corpus/fixtures/measure_audio.py` is now
`+658/−194` against `HEAD` (new `_wpstate_r90_*` gate/attribution/lock helpers
— the r90 lane's foldfix), i.e. the worktree file is no longer the committed
blob (`5e4150d9…` vs `7a070fa8…`). It was equal to `HEAD` when this seat
archived it (10:02Z) and this seat never wrote to it; every number in this
report comes from the **frozen tree copies**. The operator should decide
whether that worktree edit is folded into a later commit before the next
freeze.

The frozen tree carries the **tracked** r97 scout and boundary receipts
(`corpus/live/r97-scout/`, `corpus/live/r97-boundary/` — 284 tracked files under
`corpus/live/r97*`), so the cross-seat re-derivation in §3.3 runs against
committed bytes.

## 2. Fresh runs on committed bytes

### 2.1 Run A — `20261016T100837483839Z-wppol-r97`

`tree/` → `python3 corpus/fixtures/measure_audio.py --probe-wppol-r97`
(launched 10:03:30Z, ~5 min wall, `TMPDIR=~/Projects/shokunin/tmp`,
`PYTHONDONTWRITEBYTECODE=1`). Receipt sha256
`0096e03e778c9890c0a99e308e54e0d1ef1724edf7dcc02d422eaade648c1f24`.

| entry | keys | legs | failures | coverage_blocked |
| --- | --- | --- | --- | --- |
| `wppol_arming_r97_probe` | 26 | 14 | 0 | 0 |
| `wppol_defaults_r97_probe` | 30 | 15 | 0 | 0 |
| `wppol_linking_r97_probe` | 34 | 21 | 0 | 0 |
| `wppol_wpexec_r97_probe` | 29 | 15 | 0 | 0 |
| `wppol_settings_r97_probe` | 17 | 4 | 0 | 0 |
| 17 pre-existing base entries | — | 14 each | 0 | 0 |

### 2.2 Run B — `20261016T101552851385Z-wppol-r97`

Identical command on the same tree, ~5 min wall. Receipt sha256
`60e05efb4eec384c2f31a1c03226f607767b3de937dcac8f922aeed8de4b5bf0`.
Per-entry shape identical to run A (26/30/34/29/17 keys, 14/15/21/15/4 legs,
`failures: {}`, no blocks, all 17 base entries green).

### 2.3 Determinism and the unarmed cell

23 armed headline cells compared across runs A and B: **21 identical**, 2
“different” only because the value is the pid-namespaced node name
(`d12.default_after` / `d13.default_after`, `…_sq_788475` vs `…_sq_944416`).
Byte-stable values across both runs: `a1_pair_up.wp_ready_s` 0.256,
`a3 rc` 78, `a9 rc` 69, `a11 rc` 0, `d9 set_default_rc` 0, `d9_lag_s` 1.002 s,
`d12 t_set_to_restart_s` 1.304 s, `d13 state_file_row_secs` 1.003 s,
`d12 flushed_before_restart` False, `l4 rc` None, `l7 rc` 1, `l8 alive_at_cap`
True, `l18 sm_settings_row_after` False, `w7 rc` −9, `w10 rc` 64,
`w13 identical` True, `s1 n_keys` 25, `s1 sha256`
`56526540bdc17f52…`, `s2 sm-settings` {id 31, rows 25}, `s4 same_key_set` True,
`s3 shared_before/after` both `Value: true`.

The **deliberately unarmed movement** (`l18`) reproduced in both runs: with
`linking.follow-default-target` written `false` (read-back and `sm-settings`
row both armed), a live stream moved B→A when the default flipped
(`links_before [[str, sb]] → links_after [[str, sa]]`, `default_after = sa`) —
recorded, never asserted, exactly as the boundary directed.

## 3. Law re-derivation — `runs/r97v_laws.py`

**260 laws** over the receipts' **recorded fields only**; an entry's own
`failures` / `coverage_blocked` lists are never an input (they are used at the
end as a cross-check). Expectations come from the **tracked cross-seat
receipts** where one exists — the 25-name lattice and the listing sha from
`r97-boundary/receipts/f_settings.json`, the four Lua inventory lines from
`r97-scout/receipts/b_wpexec.json` — and from the committed block's armed
values otherwise. Absent witnesses and named vacuities are `BLOCKED`, never
green.

| receipt | laws | PASS | FAIL | BLOCKED |
| --- | --- | --- | --- | --- |
| author green #1 (`…T094737705611Z`) | 260 | **260** | 0 | 0 |
| author green #2 (`…T095258906395Z`) | 260 | **260** | 0 | 0 |
| author pre-freeze smoke ×2 (`…T093309501241Z`, `…T093830854971Z`) | 260 | **260** | 0 | 0 |
| **this seat run A** (committed bytes) | 260 | **260** | 0 | 0 |
| **this seat run B** (committed bytes) | 260 | **260** | 0 | 0 |
| `mutready` (full family, readiness-gate starvation) | 157 | 71 | **24** | **62** |
| `mut-sha` (settings entry) | 25 | 24 | **1** | 0 |
| `mut-nop` (comment-only control, settings entry) | 25 | **25** | 0 | 0 |
| `mut-getreg` (wpexec entry) | 51 | 50 | **1** | 0 |
| `mut-stim` (wpexec entry) | 51 | 49 | **2** | 0 |

Coverage: the arming lattice (core/pair, the `wpctl status` non-gate, all five
`WIREPLUMBER_*_DIR`/XDG/HOME arming shapes, the modules-less core, the
`module.access` pair, the shared-graph census); the default-node rank lattice
(first-wins, session rank, ties, no-priority, driver fallback rank, the
explicit default + both metadata rows + the state-file row, clear-default,
removed-default fallback, the restart race with its vacuity guard, the durable
restart); the linking lattice (serial vs id namespaces, the three failure
faces, the flag-order matrix, the role null, the recorded movement); the
wpexec sandbox (closed global set, compile vs runtime error worlds, the
argument forms, unbound `Settings` with and without a daemon); the settings
lattice (25 keys + sha, two metadata faces, write scope); plus per-entry
custody (`own_procs_after == []`, shared-graph `own_hits == []`, no
`REFUSED foreign pid`, ownership predicate) and cross-entry laws (leg census
14/15/21/15/4 = 69, single pid, no coverage blocks, no `pactl set-default`).

### 3.1 The 69-leg census re-derives exactly

The counting rule declared in the block header (context keys not counted;
custody sub-records counted) yields, on every receipt above:
**14 / 15 / 21 / 15 / 4 = 69**. The author's corrected headline is right; the
first draft's “63” was arithmetic drift, as disclosed.

### 3.2 Cross-seat re-derivation (committed scout/boundary receipts)

| cell | cross-seat receipt (tracked) | this seat's runs |
| --- | --- | --- |
| conf-dir missing | boundary `a_arming` V1: rc **78**, fragments `[]`, chain marks absent, naming mark True | `a3`: rc 78, fragments `[]`, chain absent, `wppol_config_missing` |
| data-dir replaces | boundary `a_arming` V5: rc **78**, fragments opened ≥2 | `a7`: rc 78, script mark, 2 fragments |
| access off | boundary `b_access` B1: socket present, `pw-cli`/`pw-dump` timed out at 8.012 s, 0 bytes | `a10`: socket present, both timed out, 0 bytes |
| access untouched | boundary B2: `pw-cli` rc 0 with a Client object | `a11`: rc 0, `has_client` True |
| rank laws | boundary `c4_priority` n1 (no priority keys ⇒ no displace), n2 (driver-only 999 takes over), n3 (session 200 does **not** beat driver-only 999) | `d6`, `d7`, `d8` identical outcomes |
| target namespaces | boundary `d_linking` d1 (`--target 0` ⇒ 0 links), d3 (global id ⇒ default B), d4 (serial ⇒ A), d5 (name ⇒ A), d6 (bogus ⇒ default B), d7 (dont-fallback ⇒ 0 links), d8 (linger ⇒ 0 links) | `l2`, `l4`, `l3`, `l5`, `l6`, `l7`, `l8` identical outcomes |
| restart race | boundary `c3_restart_race` immediate: `state_file_at_set` `""`, `state_file_before_restart` `""`, `t_set_to_restart_s` 0.028 | `d12`: unflushed at 1.304 s ⇒ lost + no configured row (both runs) |
| lattice | boundary `f_settings`: 25 keys, sha `56526540bdc17f52…`, `f4_diff` only_private/only_shared `[]`, `same_order` True | `s1`/`s4`: same 25 keys, same sha, `same_key_set` True |
| Lua surface | scout `b_wpexec` inventory (4 lines) | `w1`: byte-equal lines 1–4 (law set compares to the scout's own string) |

**One apparent divergence, explained:** the boundary's `a_arming` V4 records
the operator's real `~/.config/wireplumber` fragment being opened (the leak
law, measured with the operator's HOME). The family does **not** re-arm the
leak: `a6` arms the *safe* shape (shim HOME ⇒ the shim fragment opens and the
operator's path is asserted **absent**). The boundary observation and the
family arm are consistent; the leak itself stays recorded-only.

## 4. Mutation / negative controls

### 4.1 Receipt forgery suite (`runs/r97v_forge.py`, base = author green #2)

| group | fabrications | result |
| --- | --- | --- |
| controls | `none`, blank both verdict lists | **CONTROL-OK** (0 FAIL / 0 BLOCKED) — the verdict lists are not the detector |
| arming | a3 rc 78→0; a2 rc 0→1; a7 script mark removed; a8 alive→False; a10 hang→False; a11 client→False; a12 own_hits injected | 7/7 **CAUGHT (FAIL)** |
| defaults | d1 got→B; d7 got→K; d9 configured row→None; d9 state file→""; d10 configured→C; d12 flush→True (**BLOCKED**, vacuity never green); d12 default→P; d13 state row→None | 8/8 **CAUGHT** (1 BLOCKED) |
| linking | l1 links→[]; l4 target→A; l6 stderr→nonempty; l7 node_gone→False; l8 alive→False; l18 row→True | 6/6 **CAUGHT** |
| wpexec | w1 FOUND line mutated; w2 rc→0; w7 timeout→False; w13 identical→False; w14 inventory→False | 5/5 **CAUGHT** |
| settings | s1 n_keys→24; s1 sha→deadbeef; s2 rows→24; s3 shared changed; s4 same_key_set→False | 5/5 **CAUGHT** |
| structure | pop `l3` leg; pop `own_procs_after`; rename an own node to a foreign pid; inject a coverage block; inject `pactl set-default` text | 5/5 **CAUGHT** (1 BLOCKED, 4 FAIL) |

Totals: **36 fabrications + 2 controls → 34 FAIL-caught, 2 BLOCKED-caught, 0
missed, controls clean.**

### 4.2 Fixture mutations (single-entry driver `runs/r97v_entry.py`; full family for `mutready`)

| mutation | tree | family's own verdict | law set |
| --- | --- | --- | --- |
| `WP_READY_CAP 30.0 → 0.01` (readiness gate starved) | `tree-mutready/` (full family, receipt `…T101109929906Z`) | 4 entries `coverage_blocked` “private pair not ready”, arming entry 1 failure; legs collapse to 14 | 71 PASS / **24 FAIL** / **62 BLOCKED** — never green |
| `SETTINGS_SHA → deadbeef…` (recorded-but-not-armed constant) | `mut/min-sha/` (settings entry) | `failures: []` — the fixture **records** the sha match but does not arm it | **1 FAIL** (`settings.s1.sha_matches_boundary`) — the law set arms it via the boundary's sha |
| `LUA_GETREG → nil` (armed constant) | `mut/min-getreg/` (wpexec entry) | 1 failure (`w1_inventory` line 4 vs the mutated expectation) | **1 FAIL** (the fixture's own verdict surfaces through the cross-check law) |
| `w_no_quit.lua` gains `Core.quit()` (stimulus) | `mut/min-stim/` (wpexec entry) | 1 failure (`w7_no_quit: not killed at the cap (rc 0, timed_out False)`) | **2 FAIL** — the independent `wpexec.w7.killed_at_cap` law catches it plus the cross-check |
| comment-only append (no-op control) | `mut/min-nop/` (settings entry) | `failures: []` | **25/25 PASS** — irrelevant bytes do not trip the gate |

### 4.3 Kill-guard control (`runs/r97v_guardctl.py`, three arms)

| arm | process | result |
| --- | --- | --- |
| A | foreign `sleep` (no private root in cmdline/environ) | `own()` **False**; kill **REFUSED foreign pid**; process **survived** |
| B | own `sleep` carrying the private root **in its environ only** (the private `wireplumber -c … -p main` shape) | `own()` **True**; killed (SIGKILL after the 2 s grace) |
| C | the live run's private core (read-only) | `own()` **True**, process left alive |

## 5. Exit census (`runs/r97v_exit_census.py`)

| census | required | measured | verdict |
| --- | --- | --- | --- |
| operator's graph | 0 `r97a` objects | **0 hits** (graph readable, `pw-dump` rc 0) | PASS |
| processes | 0 `r97a` processes | **0** (`/proc` scan of cmdline+environ) | PASS |
| private instances | 0 live | **0** live private roots (all `$TMPDIR/wppol-r97-*` pid files dead) | PASS |
| shared daemons | untouched | shared session daemon pid+start time **identical** to the 10:03:10Z pre-census; no kill returned `REFUSED foreign pid` in any receipt | PASS |

Every family entry in both runs recorded `own_procs_after: []`,
`shared_census.own_hits: []`, `shared_census.unreadable: false`; the arming
entry's `a12_shared_untouched` recorded the operator's graph with **0** own
hits; `s3_write_scope` recorded the operator's `linking.follow-default-target`
unchanged (`Value: true` before and after the private write).

## 6. Labrat fold (frozen `probeParent` — exactly one child, read-only, advisory)

One `ufo-labrat` was dispatched with a single falsifiable hypothesis: **H1 —
the `sm-settings`/`schema-sm-settings` metadata object is created by
WirePlumber's own script layer (so its presence is a WirePlumber-up witness),
while the core `settings` metadata object is PipeWire-side.** It returned
**CONFIRMED** with no contradiction:

- `/usr/share/wireplumber/wireplumber.conf:284-286` loads
  `libwireplumber-module-settings` with `arguments = { metadata.name =
  sm-settings }`, `provides = metadata.sm-settings`; `:70,103` mark
  `metadata.sm-settings = required` in the main/policy profiles; `:294-297`
  gates `settings-instance` `after = [ metadata.sm-settings ]`.
- The 25-key schema is declared in `wireplumber.conf:948…` (e.g.
  `linking.follow-default-target` at `:1027`, `node.stream.restore-props` at
  `:1081`) and consumed by `Settings.get_boolean` in
  `scripts/node/state-stream.lua` / `scripts/linking/prepare-link.lua`.
- The literal `schema-sm-settings` appears in no installed WP file — it is
  derived at runtime as `schema-` + `metadata.name`, consistent with
  WP ownership.
- **One inference flagged, not a sighting:** the core `settings` object's
  PipeWire-side creation is inferred from the metadata factory being
  PipeWire-side (`/usr/share/pipewire/pipewire.conf:149`,
  `minimal.conf:230-233`) and from no WP file declaring
  `metadata.name = settings`; the daemon code was not greppable.

This is an implementation-side cross-witness for `a1`/`a2`/`s2` that the
behavioural re-run cannot provide: the readiness gate the family arms is the
daemon's own object, and `wpctl status`'s rc-0-with-WP-down face (re-derived
in both runs) does not require it.

## 7. Disclosed incident — hardlink write-through (self-inflicted, contained)

While preparing mutation trees this seat ran `cp -al tree tree-mutready`
(hardlink copy) and then `cp /tmp/mutready.py
tree-mutready/corpus/fixtures/measure_audio.py`. The destination was a
**hardlink** to the frozen tree's fixture, so the write went **through** the
shared inode and mutated both trees; a later `python3 -m py_compile` on the
hardlinked copy likewise touched the tracked
`corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`.

- **Detected** by the sha check in §1 (`7bb3c3f1…` ≠ `7a070fa8…`), i.e. the
  corruption never reached a green verdict: the second full-family run
  launched on the mutated bytes was killed mid-flight, its orphaned private
  core was stopped through the family's own guard, and the fixture **and** the
  tracked pyc were restored from `r97v-head.tar`.
- **Contained and verified:** a full `tar -df` over all 44 581 members reports
  **0 “Contents differ”**; after restoration the full re-run reports **0
  “Contents differ” and 0 “Size differs”**, and the fixture and pyc match the
  archive exactly; the file-set symdiff against `b8ff4efc` is clean apart from
  the runs' own receipts.
- **Effect on the evidence:** run A started *before* the on-disk mutation and
  executed the original bytes from memory — the cap-sensitive readiness gate
  passed at 0.256 s in run A (it cannot pass with the mutated 0.01 s cap), and
  run A's 260/260 law set is identical to run B's, which ran on the restored
  bytes. Both runs are reported; the timeline is stated here rather than
  buried.
- No other file was written through a hardlink (only the fixture and the pyc
  were affected; both restored).

## 8. Findings, nuances and risks

1. **F1 — recorded but not armed: the settings listing sha.** The fixture
   computes `sha_matches_boundary` and records the sha, but does not add a
   failure when the sha mismatches its constant (`mut-sha` stays green in the
   fixture's own verdict list). The cross-witness therefore lives in the law
   set and in the receipt field; the family's own `failures` list does not
   protect it. Minor, since the same object is armed via `n_keys`, the key set
   and the boundary cross-check.
2. **F2 — `a9`'s `errclass` is always `[None, None]`** in the modules-less-core
   variant shape (the variant's stderr is empty; the daemon logs to file). The
   armed witness for that cell is the scan marks, which the family does assert.
   Recorded, not a defect.
3. **F3 — the family lock is tree-relative.** `_wppol_r97_family_lock()` opens
   `ROOT/live/measure_audio-wppol-r97.lock`, so it excludes **same-tree** runs
   only. A sibling lane (`critic-r97`) ran the same family concurrently from
   its own tree during this gate and both lanes' runs were green — the family
   is safe under that overlap because every daemon, socket and node name is
   pid-namespaced and private. The lock's declared “cross-TMPDIR same-family”
   intent is only achieved within one tree; worth a note for the next lane
   that expects cross-tree serialization.
4. **F4 — the `wpctl status` non-gate is confirmed from both sides.** Run A/B
   re-derive rc 0 + a well-formed empty listing with `sm-settings` verified
   gone, and the labrat's `wireplumber.conf:284-286` witness shows the gate
   object is the daemon's own (`sm-settings`), not anything `wpctl status`
   consults.
5. **F5 — the ~1 s deferred save re-derives with a consistent value.**
   `d9_lag_s = 1.002 s` and `d13 state_file_row_secs = 1.003 s` in both runs;
   `d12`'s restart at `t_set_to_restart_s = 1.304 s` still caught the window
   unflushed (`flushed_before_restart` False, no configured row after) — the
   race is armed, not vacuous, in both runs, and the vacuity guard is proven by
   `forge-d12-flush` (BLOCKED, never green). The flush timeout itself remains
   C-side (the author's labrat flagged it as a partial).
6. **F6 — base-entry cost.** Every family run also executes the 17 pre-existing
   base entries (14 legs each, all green); unchanged by this round, recorded
   for the next fold.

## 9. Remaining risks (for the operator)

- **Author base lineage.** The author's worktree is `5755be5b` (r89 foldfix),
  not the committed lineage; the *r97 text* is byte-identical and the committed
  merge is insertion-only, so the greens transfer — but the author's full-file
  sha (`f0eb6c50…`) is not the committed sha (`7a070fa8…`), and the author's
  receipts were produced on a base that lacks r90–r96. Both verifier runs were
  produced on the committed base and are green, which is the transfer test.
- **Timing cells are load-conditional.** `d9`/`d12`/`d13`/`w7`/`a10` carry caps
  (8 s flush, 30 s ready, 6 s access) that held at loadavg 2.7–6.1; the family's
  own vacuity/named-block paths are the safety net under load, and the
  `mutready` run shows the failure mode when the gate is starved.
- **Tracked `.pyc` churn.** Any run without `PYTHONDONTWRITEBYTECODE=1`
  refreshes the tracked `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`
  (the author disclosed the same); it was restored here and the tree is clean.
- **Cross-lane overlap (F3)** is safe for this family but not for families that
  share a daemon; do not read the fixed-path lock as a global exclusion.

## 10. Evidence index (all untracked, under `corpus/live/r97-verifier/`)

- `r97v-head.tar` — `git archive HEAD` (sha256 `91c500ad…`); `tree/` — extracted.
- `runs/r97v_lstree.sorted.txt`, `runs/r97v-tree-files.sorted.txt`,
  `runs/r97v-symdiff.txt` (0 at archive time),
  `runs/r97v-lstree-b8ff4efc.sorted.txt`,
  `runs/r97v-symdiff-b8ff4efc.txt` (run artifacts only),
  `runs/r97v-tar-diff.txt` (pre-restore), `runs/r97v-tar-diff-after.txt`
  (post-restore, 0 content/size diffs).
- `runs/r97v-block-committed.txt` / `runs/r97v-block-author.txt` — the 2118-line
  block from both sides (sha-identical).
- `tree/corpus/live/runs/20261016T100837483839Z-wppol-r97/measurements.json`
  (sha256 `0096e03e…`), `…T101552851385Z-wppol-r97/measurements.json`
  (sha256 `60e05efb…`) — the two committed-bytes runs.
- `runs/r97v_laws.py` + `runs/laws-{run1,run2,author-*}.json` — the 260-law set
  and its verdicts; `runs/r97v_forge.py` + `runs/r97v-forge.json` — the 37-case
  forgery suite.
- `runs/r97v_entry.py` (single-entry driver), `mut/min-{sha,getreg,stim,nop}/`,
  `tree-mutready/` + `runs/{mut-*,mutready}.{log,json}` — fixture mutations.
- `runs/r97v_guardctl.py` + `runs/r97v-guardctl.json` — the 3-arm kill-guard
  control; `runs/r97v_exit_census.py` + `runs/r97v-exit-census.json` +
  `runs/r97v-precensus.txt` — the exit census and its baseline.

**This seat made no tracked write and no commit; the shipping decision is the
operator's.**
