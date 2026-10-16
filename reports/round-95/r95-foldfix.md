# r95 foldfix — the JACK ↔ PipeWire family: C1–C5 + F1–F8 folded, fresh green on the responsive daemon

Seat: **foldfix-author** (leaf). Lane repo `~/Projects/shokunin/audio-shokunin`,
basis **HEAD `6fcff79280193fcf54ccc98adb3a193ed3575eaa`** (the r95 author commit
`ffeb5155` is an ancestor and carries the same pre-fold
`corpus/fixtures/measure_audio.py` blob `dca4dc9b…`). Window **2026-10-16
06:26–06:45 local (09:26–09:45Z)**, host `plazir27`, loadavg 9–15 with 6–15
concurrent sibling `measure_audio.py` batteries. **Zero commits, zero pushes,
no `set-default-*`, no `wpctl set-default`.** One file changed:
`corpus/fixtures/measure_audio.py` — **+773 / −263**. `corpus/fixtures/r95jack.c`
is untouched (`55d4d411…`).

## 0. Verdict

**The union is folded and the family is green on the archive tree on the
now-responsive daemon — with legs, per-leg census and the new discriminators
populated on the green receipt.**

| claim | status |
| --- | --- |
| every C1–C5 + F1–F8 item has a landed, anchored fix | **DONE** — §2, each with the probe that shows the path live |
| the frozen (pre-fold) bytes on the responsive daemon are green | **NO** — my own run reds `d_metadata: stale after remove = '', want 'value1'` (rc 1); independently matches `r95-verifier.md` §8.1 |
| the fold bytes are green | **YES** — 3 runs (`…093502…`, `…093554…`, `…093944…`), **rc 0, `failures: {}`, 24/24 legs, `coverage_blocked` empty in all five entries**, 38.9 s wall |
| the green is *substantive*, not a vacuous `failures: {}` | **YES** — every entry carries `measured: true`, `legs_measured`, 3/4/2/10/5 legs, `daemon_gate.ok`, and a non-vacuous `sinks_gone` census (§4) |
| a blocked run can no longer read as green | **YES** — probed live: daemon refusal (rc 1), daemon hang (SIGKILL at bound), entry abort, family-lock busy → all five entries `measured: false`, `legs_measured: 0`, **named** coverage block (§5) |
| the family lock is family-global and bounded | **YES** — `/run/user/1000/ufo-measure_audio-jack-r95.lock`, cross-tree exclusion measured, 2 s cap → named block, truncated on release, stale text recorded not trusted (§5) |
| host state is left clean | **YES** — no `r95a` module/sink/node/row anywhere, `clock.force-quantum = "0"` restored by the harness (§6) |

One **out-of-union hunk** is included and flagged: the `d_metadata`
post-removal getter arm (§2.9). It is required by this task's own green
contract, it is the fix the *independent verifier seat* recommends, and it is
a two-line change that can be dropped alone if the orchestrator judges it out
of scope.

## 1. Bytes, tree discipline, method

- **Implementation sha (the number to re-derive against):**
  before `dca4dc9bc87e006b534a50d80270bfb27492fadecfe75fbbd89f37342bd87ed7`
  → after `740d9ce39f589e781792e552976713b25c085e460a072b88417c546d50040e87`.
  Derivation: `sha256sum corpus/fixtures/measure_audio.py` and
  `git show HEAD:corpus/fixtures/measure_audio.py | sha256sum`.
- **Diff arithmetic** (`git diff --numstat -- corpus/fixtures/measure_audio.py`):
  **773 added / 263 deleted**, 93 hunks, every hunk inside the r95 region
  (first hunk at 33370, last added line 36173). File `wc -l`: 36 403 →
  **36 913**. The deletions are
  dominated by the re-indentation of the `s_shape` witness arms into a nested
  `shape_witness_arms()` (the C2 gate) — no prior family's code is touched.
- **Run tree**: `corpus/live/r95-foldfix/tree/` = `git archive HEAD` extracted
  at 09:30:35Z (3.2 GB; `find`-counted 44 568 files / 11 778 dirs at the end of
  the session, i.e. the archive plus this seat's four run dirs and one lock
  file), then `patch -p1 < fold.patch` applied to
  `corpus/fixtures/measure_audio.py` only. Before each run the file's sha256 was
  printed and matched against the revision under test
  (`dca4dc9b…` / `540b918e…` / `740d9ce3…`), so "committed-bytes archive tree"
  means *HEAD bytes plus exactly this fold*, not the dirty worktree. The
  worktree file and the tree file are byte-identical at the final revision.
- **Seat method disclosure**: this seat's tool surface exposes **no `lsp`
  device** (only a reverse-engineering MCP server), so the edits were made by
  hand with exact-string replacements and verified by (a) `ast.parse`, (b) the
  full battery runs, (c) three negative-path probes. Symbol-aware renames were
  not needed — every change is local to the r95 block plus its dispatch. The
  frozen `probeParent` slot **spawned no labrat**: every mechanism in this fold
  is directly drivable by this seat (the daemon, the lock, the fixture client,
  the graph), so an advisory depth-2 probe would have re-run work this seat
  already owned; disclosed, not silently skipped.
- **Provenance of the numbers in this report**: every count below was derived
  from a receipt or a command, never transcribed from prose (§8).

## 2. The union, item by item

Line anchors are in the final `corpus/fixtures/measure_audio.py`.

### C1 + F2 — the block path is no longer a vacuous green, and it keeps its legs

`_jack_r95_block` (`:34159`) now carries `entry["legs"] = legs` on **every**
exit path, sets `legs_measured`, sets `measured: false`, and runs the same exit
census as the normal path; every one of the 22 call sites was updated to pass
its local `legs` (positional or keyword). The normal path closes through the
new `_jack_r95_finish` (`:34182`) which sets `legs`, `legs_measured` and
`measured: true`.

*Evidence*: intermediate receipt `intermediate-run-legsbug-measurements.json`
shows the discriminator working — `measured` was already `true` while `legs`
was empty, i.e. the flag is not a restatement of the leg payload; the final
receipts carry both. Probes A1/A2/B1/C1 (§5) show `measured: false` +
`legs_measured: 0` + a **named** block for four different failure modes.

### C2 + F3 — the census runs on blocked/aborted paths too

`_jack_r95_teardown` (`:34041`) gained the `census=` parameter (sinks this seat
already unloaded mid-entry) and is now called from `_jack_r95_block`, from all
five `except` handlers, and from `_jack_r95_finish`. An abort inside an entry
therefore still produces `sinks_gone`, `sinks_censused`, `own_nodes_after` and
`stream_properties_own_rows`; a teardown that itself throws is caught and named
rather than losing the receipt.

*Evidence*: `probes/except-path-probe.json` — a monkeypatched mid-entry abort
gives `measured: false`, `coverage_blocked: ["entry aborted: RuntimeError: …"]`
**and** a full census (`sinks_gone`, `sinks_censused`, `own_nodes_after: []`,
`stream_properties_own_rows: []`). A1/A2 show the same on the block path, where
the pre-fold bytes ran **no census at all**.

### C3 (task item 3) — daemon unavailable / graph unreadable / open-timeout are named blocks

Three new gates, none of which existed:

- `_jack_r95_daemon_gate` (`:33522`) — one bounded `pactl info` in
  `_jack_r95_entry_head`; a daemon that does not answer is an entry-level
  `jack_r95_daemon_unresponsive` block with rc/killed/wall/stderr diagnostics,
  **before any leg is armed**.
- `_jack_r95_probe_state` (`:33544`) — the open-state of every probe
  invocation: `ok`, `jack_r95_open_timeout` (killed at the bound with no
  `R95AJSON`), `jack_r95_no_daemon`, `jack_r95_no_record`.
- `_jack_r95_witness_gate` (`:33571`) — a concurrent `pw-dump`/`pw-metadata`
  witness that could not read the snapshot names a block instead of arming
  laws; `_jack_r95_shape_slice` (`:33771`) and the edge witness
  (`_jack_r95_edges_witness`, `:33717`) now carry `error`/`graph_ok`, and the
  entry head records `graph_error_at_start`. The gates wrap the PW-side arms of
  `s_shape`, `s_liveness`, all four `x_*` legs, both byte legs, every `q_*`
  witness arm, `q_cross`'s second client, and `d_metadata`.
- The discriminator pair `measured` / `legs_measured` (§C1) is what makes
  "`failures: []` while measuring nothing" impossible to read as green.

*Evidence*: A1 (refusal, rc 1, `Connection failure: Timeout`) and A2 (the
incident's SIGKILL-at-bound mode, `rc=-9 killed_at_bound=True wall_s=12.006`)
both produce five named blocks with `measured: false` and **no failures** — the
pre-fold behaviour was four entries with `failures: {}` while measuring
nothing plus one false red (`r95-critic.md` C1/C2, `r95-reviewer.md` F4).

### C4 + F6 — host-global, bounded, stale-aware family lock

`_jack_r95_lock_path` (`:33898`) resolves
`$XDG_RUNTIME_DIR/ufo-measure_audio-jack-r95.lock` (fallback
`~/.local/state/…`) — tree-independent, so `git archive`/per-seat trees share
it. `_jack_r95_family_lock` (`:33940`) acquires with `LOCK_EX|LOCK_NB` in a
bounded retry loop (`wait_cap_s = 600`, poll 0.25 s); expiry returns a named
`jack_r95_family_lock_busy` block instead of waiting forever. The dispatch
(`:36181`) records the lock as a receipt entry and, on a busy lock, writes a
`_jack_r95_lock_blocked_entry` (`:34006`) for each of the five entries instead
of running them.

### C5 — the lock file no longer reads as a live holder

`_jack_r95_lock_release` (`:33925`) truncates **and** closes on release; the
text is only ever evidence (`_jack_r95_lock_text`), a text naming a dead pid is
recorded as `stale_text` + `stale_pid_dead`, and the flock probe is the witness.

*Evidence*: `probes/helpers-probe.json` — a waiter started from a **different
directory** is refused after 2.001 s with the holder text quoted; a stale file
written by a dead pid is displaced and recorded (`stale_text`,
`stale_pid_dead`); after release the file is `""`; the green receipts record
`path=/run/user/1000/…`, `waited_s: 0.0`, `acquired: true`, `stale_text: null`.

### F1 — the metadata witness is per-client

`_jack_r95_meta_rows` (`:33735`) now returns `rows_by_subject` in addition to
the display map. The `d_metadata` mid hook resolves **our** subjects — the
client's node id plus the global ids of our own ports — and the armed rows are
the subject-keyed ones; a surviving row is checked against **our** subjects,
and a sibling's row is recorded (`foreign_r95a_rows_while_running`), never
armed. A completeness arm names a block if either own key
(`r95a/key1`, `r95a/portkey`) is not attributable to our subjects.

The mapping was measured, not assumed (fixture `metadata` mode + concurrent
`pw-dump`): `jack_set_property` on the client uuid lands on the **node id**
(156), on the port uuid on the **port's global id** (127) — the key-only
collapse could not tell those from a sibling's.

*Evidence*: final receipts `own_subjects: [160, 185]`, `own_port_ids: [160]`,
`own_rows: {r95a/key1, r95a/portkey}`, `foreign_r95a_rows_while_running: {}`.
The intermediate `…pre-f1census…` receipt is kept because it caught the
first-draft bug (a `port_id` key that `_jack_r95_graph()` never sets) — the
same class of silent-empty census this round is about.

### F4 — a client that never opened is a block, not a version-law red

`a_avail` now runs `_jack_r95_probe_state` on the version probe **before**
arming the version/export laws (`:34248`): a non-`ok` state blocks the entry
with the state, the bound, the stdout byte count and the stderr, and carries
the partial legs. `q_cross`'s second client and `q_global_second` get the same
treatment.

### F5 — the harness owns the force-quantum restore

`_jack_r95_settings_restore` (`:34133`) is called from teardown, so it fires on
the normal, blocked **and** aborted paths. The quantum entry arms
`settings_global_moved = True` *before* the `q_global` writer runs (`:35163`),
so a writer killed at the bound is still repaired. It writes exactly one key —
`pw-metadata -n settings 0 clock.force-quantum 0` — and re-reads the store.

*Evidence*: green receipts carry `settings_restore` (rc 0) and
`settings_after_restore["clock.force-quantum"] = "0"`; the failure path is
probed directly (`probes/except-path-probe.json` →
`restore_on_failure_path`).

### F7 — `sinks_gone` measures something in every entry

The exit census is built from `census ∪ loads`, so the two entries that unload
their null sink mid-entry (`jack_surface`, `jack_bytes`) now report
`{"r95a_ns_<pid>": true}` instead of `{}`; `sinks_censused` names what was
measured and `sinks_gone_note` names the (now unreachable in practice) empty
case. `own_nodes_after` filters on the same name set.

*Evidence*: before receipt `sinks_gone: {}` in surface + bytes (2/5 vacuous);
all three final receipts non-empty in 5/5.

### F8 + C6 — report arithmetic

Every number in this report is re-derived in §8 from a command; the
implementation sha names the **lane HEAD + fold** bytes, and the receipts'
provenance is per-run (§1, `RECEIPTS.md`).

### 2.9 The one out-of-union hunk (disclosed)

`r95-reviewer.md` §8.1 / the verifier's risk 1: `d_metadata`'s post-removal
getter arm (`stale after remove`, `want 'value1'`) is a **cache race** between
the fixture's fixed 250 ms sleep and the metadata round-trip, armed as a hard
equality — 13/13 prior observations recorded the stale hit under loadavg 50+,
while the verifier's 4 runs on committed bytes (loadavg ≈ 9.5) and this seat's
own direct fixture probe on the responsive daemon recorded the refreshed
`(-1, '')`. I reproduced the red **on the frozen bytes** before touching it
(`before-frozen-measurements.json`). The fold arms the admissible **pair**
`(0, 'value1') | (-1, '')`, records the branch
(`get_after_remove_branch: refreshed`), and still reds on any third state.

This is a correction of a false law, not a weakening to buy green — but it is
**not** in the C1–C5/F1–F8 union, so it is called out here as its own hunk for
the orchestrator to accept or drop. Without it, the contract's green is
unreachable on this host by any run, folded or not.

## 3. Before — the frozen bytes on the responsive daemon

`tree/` file reset to `git show HEAD:…` (`dca4dc9b…`),
`python3 corpus/fixtures/measure_audio.py --probe-jack-r95`,
receipt `…20261016T093303717601Z…`, `corpus/live/r95-foldfix/receipts/before-frozen-measurements.json`.

| entry | legs | `measured` | `legs_measured` | `daemon_gate` | failures | `sinks_gone` |
| --- | --- | --- | --- | --- | --- | --- |
| `jack_surface_r95_probe` | 3 | key absent | key absent | key absent | 0 | **`{}` (vacuous)** |
| `jack_addr_r95_probe` | 4 | key absent | key absent | key absent | 0 | 2 names true |
| `jack_bytes_r95_probe` | 2 | key absent | key absent | key absent | 0 | **`{}` (vacuous)** |
| `jack_quantum_r95_probe` | 10 | key absent | key absent | key absent | 0 | 1 name true |
| `jack_defects_r95_probe` | 5 | key absent | key absent | key absent | **1** | 1 name true |

**rc 1**, `failures: {"jack_defects_r95_probe": ["d_metadata: stale after remove = '', want 'value1'"]}`.
The run also created the **tree-local** lock
`tree/corpus/live/measure_audio-jack-r95.lock` (F6's counterexample, produced
by this seat), and `d_metadata` carries no `get_after_remove_branch` and no
subject-keyed rows (`own_subjects: null`).

## 4. After — the fold bytes

Three runs, all on `740d9ce3…`, all `rc 0`:

| receipt | stamp | entries | legs | failures | `coverage_blocked` | wall |
| --- | --- | --- | --- | --- | --- | --- |
| `after-run2-measurements.json` | `…T093502250819Z` | 23 | **24** | `{}` | absent (empty) ×5 | — |
| `after-run3-measurements.json` | `…T093554883701Z` | 23 | **24** | `{}` | absent (empty) ×5 | — |
| `after-run4-measurements.json` | `…T093944949769Z` | 23 | **24** | `{}` | absent (empty) ×5 | **38.876 s** |

Per-entry on run 2 (identical shape in runs 3/4):

| entry | legs | `measured` | `legs_measured` | `daemon_gate.ok` | `coverage_blocked` | `sinks_gone` | `sinks_censused` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `jack_surface_r95_probe` | 3 (`a_avail`,`s_shape`,`s_liveness`) | true | 3 | true | — | `{r95a_ns_<pid>: true}` | 1 name |
| `jack_addr_r95_probe` | 4 (`x_rendered`,`x_native`,`x_fillalias`,`x_corner`) | true | 4 | true | — | 2 names true | 2 names |
| `jack_bytes_r95_probe` | 2 (`b_jack2pw`,`b_pw2jack`) | true | 2 | true | — | `{r95a_ns_<pid>: true}` | 1 name |
| `jack_quantum_r95_probe` | 10 (`q_default`…`q_global_reset`) | true | 10 | true | — | `{r95a_ns_<pid>: true}` | 1 name |
| `jack_defects_r95_probe` | 5 (`d_xrun_stall`…`d_metadata`) | true | 5 | true | — | `{r95a_ns_<pid>: true}` | 1 name |

Everything else the fold must show on a green receipt:

- **census** — `own_nodes_after: []`, `stream_properties_own_rows: []` in all
  five; `ns_gone_after_unload: true` where the sink is unloaded mid-entry.
- **lock record** — `jack_r95_family_lock` (23rd measurement entry):
  `path=/run/user/1000/ufo-measure_audio-jack-r95.lock`, `acquired: true`,
  `waited_s: 0.0`, `stale_text: null`, `block: null`, `failures: []`.
- **F1** — `d_metadata`: `own_subjects [160, 185]`, `own_port_ids [160]`,
  `own_rows {r95a/key1, r95a/portkey}`, `foreign_r95a_rows_while_running {}`,
  `rows_after_exit {}`, `rows_after_exit_subject_keyed {}`,
  `get_after_remove_branch: refreshed`.
- **F5** — `settings_restore` rc 0, `settings_after_restore.clock.force-quantum
  "0"`, `settings_moved []`, `settings_final.clock.force-quantum "0"`.
- **F4/byte witnesses** — `s_shape.driver_name: Dummy-Driver` in all three
  runs; `b_jack2pw` mag² ratio **0.954104 / 0.954104 / 0.976686** (band
  0.90–1.03); `b_pw2jack` ratio **0.999929576 / 0.999981214 / 0.999981214**
  (band 0.985–1.005) with `in_peak = 0.499969482` in all three — exactly the
  source int16 peak/32768.
- **Determinism** — the only differing cells between run 2 and run 3 are the
  pid-bearing sink names (`r95a_ns_4072801` vs `r95a_ns_4097697`): every exit
  code, `measured`, `legs_measured`, `coverage_blocked` and census shape is
  identical.

## 5. Negative-path probes (the new discipline, live)

Artifacts: `probes/helpers-probe.json`, `probes/paths-probe.json`,
`probes/except-path-probe.json`.

| probe | stimulus | result |
| --- | --- | --- |
| **A1** | `pactl` stub refuses (`Connection failure: Timeout`, rc 1 — the reviewer's own signature) | 5/5 entries `measured: false`, `legs_measured: 0`, block `jack_r95_daemon_unresponsive … rc=1 … stderr='Connection failure: Timeout'`, `failures: []`, census keys present |
| **A2** | `pactl` stub hangs (the incident: SIGKILL at the bound) | 5/5 entries `measured: false`, `legs_measured: 0`, `rc=-9 killed_at_bound=True wall_s=12.006`, **plus** the named `teardown: pactl sink reader failed — sinks_gone unmeasured`; 22.1 s per entry (bounded) |
| **B1** | synthetic mid-entry abort | `measured: false`, `coverage_blocked: ["entry aborted: RuntimeError: …"]`, full census still produced |
| **B2** | `_jack_r95_teardown` with `settings_global_moved: true` | `pw-metadata -n settings 0 clock.force-quantum 0` fired, rc 0, store reads `"0"` |
| **C1** | a live holder on the host-global lock, dispatch expression, 2 s cap | bounded wait 2.001 s → `jack_r95_family_lock_busy …` with the holder text; 5/5 entries become lock-blocked entries (`measured: false`, `legs_measured: 0`, named block) instead of running or waiting |
| **helpers** | direct helper calls | daemon gate `ok` in 12 ms; `probe_state` classifies `ok`/`open_timeout`/`no_daemon`/`no_record` correctly; a waiter **from another directory** is excluded; stale dead-pid text recorded and displaced; file `""` after release; `rows_by_subject` keeps the subject dimension; `_jack_r95_settings_restore` is a no-op unless the entry says the arm ran |

## 6. Host hygiene (measured after the three green runs)

`pactl list short modules | grep r95a` → 0; `pactl list short sinks` → 0;
`pw-dump | grep '"node.name": "r95a'` → 0;
`~/.local/state/wireplumber/stream-properties` → 0 `r95a` rows;
`pw-metadata -n default` → 0 `r95a` rows; `clock.force-quantum` → `"0"`;
host-global lock file → **0 bytes** (truncated on release); no
`--probe-jack-r95` process alive; default sink/source unchanged. No
`set-default-*` was ever issued by this seat (the receipts' `settings_moved []`
and the unchanged default sink/source are the witnesses).

Two tree-local lock files exist as **pre-existing** artifacts and were left
alone: `corpus/live/measure_audio-jack-r95.lock` (52 B, `pid=3228981` — a dead
pid, i.e. the exact stale text `r95-critic.md` C5 cites) and, from my
frozen-bytes run, `corpus/live/r95-foldfix/tree/corpus/live/measure_audio-jack-r95.lock`.
The fold no longer creates or consults that path at all — the family lock is
host-global, is truncated on release, and treats file text as evidence only.

## 7. Remaining risks (named, not hidden)

1. **`b_pw2jack` energy band is a latent flake** (`r95-verifier.md` §8.2): the
   ±1 % band around the Goertzel ratio can false-red when the `pw-play` link
   lands late (the verifier measured 0.9103 once with `cb_in_nonzero 25`).
   **Not fixed** — it is outside the union, and it did not fire in any of my
   three runs (0.99993/0.99998). Recommended fold, if the orchestrator wants
   it: make the energy law conditional on `cb_in_nonzero ≥ 40`.
2. **The `d_metadata` pair correction is out-of-union** (§2.9). Drop it alone if
   judged scope-widening; the family then reds one cell on any quiet host.
3. **The host-global lock only excludes folded runs.** A sibling seat running
   the *old* bytes (tree-local lock) can still run concurrently with a folded
   run — exactly what happened at 06:25Z (a `tree-mutstim` lane) — and the two
   would contend on `clock.force-quantum`. The green receipts were taken with no
   other `--probe-jack-r95` process alive (`ps` checked before each run).
4. **`measured: true` means "the entry ran to the end", not "every arm was
   measured".** A named confound (e.g. a foreign driver in `s_shape`) can
   coexist with `measured: true`; the gate must read `coverage_blocked` too.
   My intermediate `…093348…` receipt is an example (driver resolved to the USB
   SPDIF sink, named as a confound, no red).
5. **The except-path census is conservative**: it censuses the entry's own sink
   name even when the abort happened before the load, so `sinks_gone` can claim
   "gone" for a sink that was never created. That is the safe direction (a
   leftover sink is still caught) but it is not a load witness.
6. **The 17 non-r95 SPECS entries run in every `--probe-jack-r95` battery** and
   were green in all four of my runs; they are unaffected by the fold and are
   not part of the family's ledger.
7. `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` is a
   **tracked-dirty interpreter artifact** (already dirty at r95 authoring time;
   my import-based probes may have regenerated it). It is not part of the fold;
   the orchestrator should exclude it from the commit.

## 8. Report arithmetic, re-derived (the C6/F8 class)

| number in this report | command |
| --- | --- |
| `+773 / −263`, 93 hunks | `git diff --numstat -- corpus/fixtures/measure_audio.py`; `git diff -U0 … \| grep -c '^@@'` |
| 36 403 → 36 913 lines | `wc -l corpus/fixtures/measure_audio.py`; `git show HEAD:corpus/fixtures/measure_audio.py \| wc -l` |
| implementation shas | `sha256sum corpus/fixtures/measure_audio.py`; `git show HEAD:corpus/fixtures/measure_audio.py \| sha256sum`; tree file sha printed before each run |
| 24 legs / 3-4-2-10-5 | `{k: len(v["legs"]) for k,v in receipt["measurements"].items() if "r95" in k}` over each receipt |
| `measured` / `legs_measured` / `coverage_blocked` / `sinks_gone` tables | the same receipts, field-by-field (§3, §4) |
| 22 vs 23 measurement entries | `len(receipt["measurements"])` — the fold adds the `jack_r95_family_lock` record |
| 38.876 s wall | `time` around run 4 (`after4.time`) |
| residue census | the commands quoted in §6 |
| `r95jack.c` untouched | `sha256sum corpus/fixtures/r95jack.c` = `55d4d411…` (the reviewer's declared fixture sha) |

## 9. Artifacts and exact commands

```
# tree (git archive HEAD + fold)
git archive HEAD | tar -x -C corpus/live/r95-foldfix/tree
git show HEAD:corpus/fixtures/measure_audio.py > tree/corpus/fixtures/measure_audio.py   # before
cd tree && patch -p1 < ../fold.patch                                                     # after
sha256sum corpus/fixtures/measure_audio.py            # 740d9ce3… must equal the worktree

# runs (each bounded, no PYTHONDONTWRITEBYTECODE pollution)
cd tree && TMPDIR=~/Projects/shokunin/tmp PYTHONDONTWRITEBYTECODE=1 \
  timeout 900 python3 corpus/fixtures/measure_audio.py --probe-jack-r95
```

- `corpus/live/r95-foldfix/fold.patch` — the working-tree diff (the exact bytes
  the orchestrator will commit, modulo the report).
- `corpus/live/r95-foldfix/tree/` — the archive tree (untracked, 3.2 GB).
- `corpus/live/r95-foldfix/receipts/` — 6 receipts + `manifest.sha256`.
- `corpus/live/r95-foldfix/probes/` — `helpers-probe.json`, `paths-probe.json`,
  `except-path-probe.json`, the two probe scripts.
- `corpus/live/r95-foldfix/RECEIPTS.md` — implementation sha per receipt.
- `reports/round-95/r95-foldfix.md` — this file.

**Not committed** (orchestrator owns the commit). The commit should carry
`corpus/fixtures/measure_audio.py` only; everything else above is untracked
evidence.

*Leaf seat — implemented, ran, probed; did not judge, admit, integrate or ship.*
