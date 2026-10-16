# r91 VERIFIER — frozen-tree gate on committed bytes (the gst capture-freeze mechanism lattice)

Seat: **verifier** (non-author, audio-shokunin r91). Lane
`~/Projects/shokunin/audio-shokunin`; basis **`git archive HEAD`** taken at
**2026-10-16T10:01:0xZ** — HEAD then **`7358f13b`** (r96 author), whose chain
carries the r91 landing **`d78f1cc9`** — extracted to
**`/home/vgpnk/r91-verify-tree`** (3.2 GB, tar sha256
`5a6a10007560163db43881a9e98bfe3a49c123c247f38f42bcb5ffd1b754a6f4`). The
committed bytes, **not** the worktree. Window **10:00Z–10:20Z** (local UTC−3),
loadavg **5.2–6.5** (32 cores) with 5–7 concurrent sibling batteries live.
`TMPDIR=~/Projects/shokunin/tmp`.
**Zero tracked writes, zero commits, zero pushes, no `set-default-*`**; every
artifact under `corpus/live/r91-verifier/`.

Duty: run the full `--probe-gstfrz-r91` family fresh on the archived tree,
re-derive all 15 legs **plus the resume fixture process** cell-by-cell with
this seat's own logic, run mutation/negative controls on the armed gates, and
confirm the exit census is clean.

**Provenance note (HEAD moved under this seat).** The archive was taken before
the next landings; HEAD went `7358f13b` → `b8ff4efc` (r97 author, 10:01:30Z) →
`a2c6e3b7` (r90 adjudication + wave-B reports, 10:14:28Z) during this window.
The r91 family block is **byte-identical** in `d78f1cc9`, `7358f13b`,
`b8ff4efc` and `a2c6e3b7` (sha256 `6fe734a8…`, §1), so no later landing touches
this gate.

## 0. Gate result

- **The committed lattice re-derives on committed bytes.** One full battery
  run on the archived tree is green (15/15 legs, `failures: {}`,
  `coverage_blocked` empty), and this seat's **independent re-derivation —
  128 checks over the 15 legs + the fixture process — is 128/128 PASS** on
  that receipt. Every declared cell value reproduces exactly (frozen
  `204844` + pinned header, keepalive 0/0, resume `204844 → 483372` with
  `forced: null`, shapes `freeze_idle` + `grows_running`, connect
  rc 1 / rc 255, `remapfed linked_live` 573 484 B, direction control
  761 900 B).
- **But the battery is not deterministically green on this host.** Two of
  **six** full-family executions returned rc 1, from **two different
  class-armed/control cells**:
  1. `c_alive` (the target-alive positive control) — battery run 1: the
     capture node never links (`suspended`, 0 B, silent stderr) → 2 failures;
  2. `s_norelink` (the source-loss envelope) — instrumented replay fam3: a
     **third** post-loss shape (`state=running, tail_grow=4096`) that lands
     outside both armed classes → 1 failure.
  Both are exactly the cells the landing report itself flags as
  class-armed/fragile ("a third realization would surface as a real
  failure"). Neither falsifies a *law* of the lattice: in the red run 1 the
  other 14 legs and all three frozen cells re-derived green, and in fam3 the
  other four entries re-derived green.
- **Mutation + negative controls are live**: a mutated armed constant reds
  exactly the three frozen legs; the missing-tools path is a named block on
  all five entries; a stimulus mutation of the resume fixture (taking the
  launcher's CLOCK_LOST pause) reds the resume leg and shows the artifact
  does *not* resume (§5).
- **Exit census clean** (§6): 0 `r91*` modules/sinks/sources/nodes/processes,
  defaults unchanged, tree fixture shas still equal the committed blobs.
- **Labrat: dispatched once, returned a capability refusal** (its tool
  surface exposes no process execution — `find_file_by_name`/`grep`/`read`
  only). The `x_rec_sink_remapfed` discriminator therefore stays
  **untested** (§7), recorded rather than hidden.
- This seat does not judge the landing: the numbers below are the gate
  evidence; admit/reject belongs to the adjudicator.

## 1. Frozen tree and byte identity

| check | required | measured | verdict |
| --- | --- | --- | --- |
| archive | `git archive HEAD` | HEAD `7358f13b` at 10:01:0xZ; tar sha256 `5a6a1000…`; 3.2 GB | PASS |
| census | extraction == the commit | **44 582 files** extracted vs **44 579** in `git ls-tree -r 7358f13b`; symdiff = exactly this seat's 3 files (lock + 2 run receipts) | PASS |
| fixture identity | committed blob | `corpus/fixtures/measure_audio.py` `97ed1b1c586d2d54…` = `HEAD:` blob = tree copy; `gstfreeze_r91_resume.py` `066d6fff7ba74ef4…` = blob = tree copy | PASS |
| **family block** | author's measured bytes | 1464 lines, sha256 **`6fe734a8ff7cd530b8790c4ada4cec6fae58216955ef3cbe7d5bc6fc0a52570d`** — identical in `d78f1cc9`, `7358f13b`, `b8ff4efc`, `a2c6e3b7`, and the author worktree (`wt-r91` lines 30982–32445); equals the integrate report's declared block sha | PASS |
| **dispatch block** | author's bytes | 33 lines / 1888 B, sha256 **`91bb18f8decae5beb30232ead31c03e3be917c59200705530419dde747f2e562`** — identical `d78f1cc9` (39878–39910) vs `7358f13b` (44493–44525); equals the integrate report's declared value | PASS |
| wiring | 4 shared-line splices | argparse row byte-identical; mutex token exactly 1× (at the landing it is the list's **last** token, index 136 of 137 — later landings appended theirs after it); `mode`/`suffix` r91 clauses byte-identical | PASS |
| `py_compile` in the frozen tree | clean | rc 0 | PASS |
| other declared shas | — | author report `de9e9ecd…` MATCH; the author's WT file sha `b0ab6fda…` differs from the merged file as expected (the **block** is what is byte-identical) | PASS |

Foreign state, observed and not touched: the shared worktree fixture was
being written by a sibling lane at 10:01:02Z and was committed as `b8ff4efc`
(r97 author) at 10:01:30Z, after this archive; `git status
--untracked-files=no` was empty before and after this seat's window. Another
lane ran **the same family** from its own tree
(`~/Projects/shokunin/r91c-tree`, 10:00:58–10:01:42Z, green) — the family lock
is a tree-relative fixed path, so same-family runs from different trees do
**not** exclude each other (the landing report's own risk note says the lock
"cannot exclude foreign lanes"; this is the sharper statement).

## 2. Fresh runs on committed bytes

### 2.1 Run 1 — RED: the target-alive control never links

`tree/` → `python3 corpus/fixtures/measure_audio.py --probe-gstfrz-r91`
(10:02:0xZ → 10:02:57Z, receipt `20261016T100257559587Z-gstfrz-r91`):

```
failures: {"gstfrz_clock_r91_probe": [
  "c_alive: with the target alive the same argv must GROW — sizes [0, 0]..[0, 0]",
  "c_alive: the control's stream state must be running — suspended"]}
```

Raw leg data for the red cell (`c_alive`, the **4th** clock leg, `-q` capture
of the same sink the previous three legs destroyed and this iteration
re-loaded):

| field | measured |
| --- | --- |
| samples (12, 0.15 s cadence) | `size 0` every sample; our node state **`suspended`** every sample |
| artifact | 0 B, `riff_size`/`data_declared` `None` |
| stdout / stderr | 0 B / 0 B (no element error) |
| killed | `wallcap` (2.609 s, our own SIGKILL), rc −9 |
| fired hooks | none (the control has no loss event) |
| target sink | module alive and listed at teardown; name-verified unload rc 0 |

Everything else in run 1 was green: the three frozen legs (204 844 B, flat,
`idle`, pinned header `0x7FFF0024`/`0x7FFF0000`, `fed_by == []`), keepalive
0/0 (6957 B debug stderr), resume `204844 → 348204` with `forced: null`,
source-loss classes `freeze_idle`/`grows_running`, connect rc 1 / rc 255 /
control 761 900 B, `remapfed linked_live`.

### 2.2 Run 2 — GREEN (15/15)

Same command, 10:04:5xZ → 10:05:51Z, receipt
`20261016T100551473978Z-gstfrz-r91`: `failures: {}`, `coverage_blocked`
empty in all five entries. `c_alive` = `[413740, 413740, 483372]`, stream
`running` — the author's exact declared values.

### 2.3 Execution tally (committed bytes, this seat)

| # | execution | result |
| --- | --- | --- |
| 1 | battery run 1 (`20261016T100257559587Z`) | **RED** — `c_alive` |
| 2 | battery run 2 (`20261016T100551473978Z`) | green |
| 3–5 | instrumented full-family replays `fam1`, `fam2`, `fam4` (stress) | green |
| 6 | instrumented full-family replay `fam3` | **RED** — `s_norelink` |
| 7–9 | instrumented clock-entry runs `diag1–3` | green |
| 10–15 | clock-entry repeats (`repeat_clock` i0–i5) | green |

So the family returned rc 1 in **2 of 6 full-family executions** and 0 of 9
clock-entry-only executions; loadavg was the same in the red and green
windows (5.2–6.5), so this is not a load-threshold effect.

## 3. Independent leg re-derivation (15 legs + the fixture process)

`derive.py` re-computes every armed cell from the raw leg data (samples,
fired hooks, artifact inspection, stdout/stderr, line counts, status file)
with this seat's own logic — it does not read the family's `failures` to
decide. **128 checks**:

- run 2 (green): **128 PASS / 0 FAIL**;
- run 1 (red): **125 PASS / 3 FAIL** — the three are exactly the family's own
  two `c_alive` cells plus its entry-level `failures` list. No extra red, no
  silently-green cell.

| # | leg | re-derived on run 2 (committed bytes) | verdict |
| --- | --- | --- | --- |
| 1 | `p_cap` | `node.dont-reconnect` is the JSON boolean **`true`**; `stream.capture.sink == "TRUE"`; `target.object == r91a_ns_827185` | PASS |
| 2 | `p_cap_false` | CLI override lands as the literal string **`"FALSE"`** | PASS |
| 3 | `p_rec` | `pw-record` node carries **no** `node.dont-reconnect` | PASS |
| 4 | `p_sink` | `pipewiresink` carries no such prop; pre-loss state `running` (all pre samples); post-loss class **`survived_running`** | PASS |
| 5 | `c_quiet` | alive at the wall cap; **flat** 204 844 B; header `0x7FFF0024`/`0x7FFF0000`; `fed_by == []`; state `idle`; stdout+stderr empty | PASS |
| 6 | `c_verbose` | same frozen cells; stdout carries `Setting pipeline to PLAYING` **and** `Clock lost, selecting a new one` (218 B), stderr **empty** (0 B) | PASS |
| 7 | `c_keepalive` | same frozen cells; `keepalive-time=20` in argv; **0** `timeout, send keepalive buffer` and **0** `popped buffer` lines in 6957 B of debug stderr | PASS |
| 8 | `c_alive` | target alive → grows `413740 → 483372`, state `running`, no loss hook fired | PASS (run 2) / **RED in run 1** |
| 9 | `r_app` (leg) | manual relink at 1.804 s, 2 discovered `monitor_* → input_*` pairs, both rc 0; flat pre-link window `[204844, 204844]` (armed, span 0); growth `204844 → 278572`; post-link producer `r91a_ns2_827185` | PASS |
| 10 | fixture process | `gstfreeze_r91_resume.py` (committed blob) ran under the battery: `clock_lost: true` @ 1.21 s, `forced: null`, `errors: []`, `exit: "wall"`, `rc: 0`, state changes exactly `null→ready→paused→playing` (one `playing`), bus trace carries the clock-lost message, pipeline desc is the canonical capture shape, its own witness `first 0 → last 278572` agrees with the battery's file sampling | PASS |
| 11 | `s_norelink` | alive at the wall cap, class **`freeze_idle`** (0 B tail growth, `idle`) | PASS (run 2) / **RED in fam3** (third shape) |
| 12 | `s_relink` | unload rc 0, relink rc 0, growth `237612 → 770092`, state `running`, producer `r91a_ns2_827185` | PASS |
| 13 | `x_rec_sink` | bare sink, target verified present: **rc 1**, artifact stops at the **44 B** header, class `gstfrz_no_target_node` | PASS |
| 14 | `x_gst_sink` | **rc 255**, class `gstfrz_target_not_found` | PASS |
| 15 | `x_rec_sink_remapfed` | **`linked_live`**, rc −9 at the wall cap, 573 484 B, fed by `r91a_src_827185` | PASS (envelope) |
| — | `x_rec_src` (the 15th leg's direction control) | alive at the wall cap, producer seen, 761 900 B | PASS |

Cross-entry cells: every entry has `failures == []` (run 2) and empty
`coverage_blocked`; every **gated** unload is name-verified
(`verified_index == captured`, `recycled: false`, rc 0); the three teardown
`not_listed` skips are the legs' own earlier gated unloads (prop `p_sink`,
resume `unload_sink`, srcloss `unload_source`) — matching the landing
report's disclosure; `sinks_gone` all true and `own_nodes_after == []` in all
five entries; `foreign_r91a_nodes == []`.

**Claim-coverage notes (not failures).** (a) The prose claim "c_verbose …
with empty stderr" is measured true (0 B) but the family only arms
stderr-silence for `c_quiet`. (b) The resume flatness arm is only armed with
≥2 pre-link samples — run 2 armed it (2 samples, span 0); in a slower window
it can be unarmed. (c) The frozen size is recorded, never armed — as
declared.

## 4. The two intermittent reds (findings)

### 4.1 `c_alive` — the target-alive control (run 1)

Signature: our capture node `suspended` from the first sample, 0 B artifact,
empty stdout/stderr, no element error — i.e. the stream was created but never
linked to the target, and `pipewiresrc` sets `PW_STREAM_FLAG_DONT_RECONNECT`
unconditionally, so nothing re-links it. The cell is the family's own
positive control: when it reds, the battery exits 1 without any lattice law
being falsified.

Non-reproduction: 12 subsequent clock-entry executions were green (3 `diag`,
6 `repeat`, plus the clock entries inside fam1–fam4). In every instrumented
replay the target sink was **fully alive at every leg start** (sink +
`.monitor` listed, node present, 2 monitor ports) — including `c_alive`, and
the module index is visibly **recycled** by the daemon between legs
(e.g. the same index appears for all four legs in `diag1`), so module-id
equality is not module identity. The one failing realization therefore has
the shape of a **target-binding race at the leg boundary** (the previous leg
destroys the shared sink; the next iteration re-loads it), not of a
comparison error in the cell. The discriminator was **not isolated** — I
could not reproduce the red with the failure-mode instrumentation attached,
so this stays a named residual unknown.

### 4.2 `s_norelink` — a third post-loss shape (instrumented replay fam3)

Measured (committed entry code, committed leg argv, same order as the
battery; the harness only probes the graph *between* legs):

```
s_norelink: the post-loss shape must land in one of the two named classes —
  other:state=running,tail=4096 (sizes [237612, 237612]..[237612, 241708],
  states ['idle', 'idle', 'running'])
```

The stream went `idle` after the source unload and then **trickled** 4096 B
in the final 0.45 s window with state `running` — neither `grows_running`
(needs ≥32768 B tail growth) nor `freeze_idle` (needs a non-running state).
The landing report predicted exactly this class of failure ("Three cells are
*class-armed* … a third realization would surface as a real failure"); this
is the third realization, measured. The sibling leg `s_relink` was green in
the same execution (770 092 B, `running`, relink rc 0).

## 5. Mutation / negative controls

| control | mutation | result |
| --- | --- | --- |
| **negative** (`neg`) | `shutil.which → None` for all tools | all **five** entries emit a **named** block `missing tools: [...]`, `failures == []` — a tool-less host is named coverage, never a silent pass (5/5 PASS) |
| **armed constant** (`mut`) | `GSTFRZ_R91_RIFF_SIZE 0x7FFF0024 → 0x7FFF0025` | exactly **3** failures, one per frozen leg, all `frozen artifact must carry the pinned wavenc streaming placeholders` (message prints the measured `2147418148 = 0x7FFF0024` vs the mutated constant). Nothing else reds — the gate is live and surgical |
| **stimulus** (`stim`) | resume fixture patched to take the launcher's `PAUSED→PLAYING` round-trip on `CLOCK_LOST` | the resume leg reds with `the app must never set_state(PLAYING) — forced=clock_lost_roundtrip`, `the app must bound itself at its own wall — exit=None rc=None`, `the battery must not have to kill it — killed=wallcap`, and `the artifact must GROW after the manual link — at_relink=204844 post=[213036, 213036, 213036]` — i.e. **the sticky app does not resume**, the causal variable the committed fixture isolates |

The mutated fixture was written as a **new** file inside this seat's own
archive copy, used, and deleted; the tree's committed fixture sha is
re-verified after the controls (§6).

## 6. Exit census (after every run of this seat)

```
== census at 2026-10-16T10:14:30Z ==
defaults: sink=…HiFi__SPDIF__sink  source=…HiFi__Line__source   (unchanged vs preflight)
r91* modules: 0   r91* sinks: 0   r91* sources: 0   r91* nodes: 0   r91* processes: none
tree fixture shas: 97ed1b1c… / 066d6fff…   (still the committed blobs)
family lock: /home/vgpnk/r91-verify-tree/corpus/live/measure_audio-gstfrz-r91.lock
  (49 B, pid=827185 — the flock is released at process exit; the file persists by design)
repo tree: no r91 lock, no tracked modification (`git status --untracked-files=no` empty)
```

The only files this seat added to the extracted tree are the family lock and
its own two run receipts; the archive's file set is otherwise untouched
(§1 census).

## 7. Labrat

Dispatched **once** (the frozen `probeParent` budget) as a bounded read-only
probe of the landing's own named residual unknown: *"a no-prop
`pw-record` × sink target stops refusing exactly when the sink's monitor has
a live consumer"* (the `x_rec_sink_remapfed` discriminator). The seat
returned a **capability refusal**: its tool surface exposes no process
execution (`find_file_by_name`/`grep`/`read` only), so it ran nothing and
fabricated nothing, and reported a trivially clean census. **The
discriminator remains untested** — recorded here, not silently skipped; the
three-arm protocol (bare / monitor-consumed / reversibility) is written out
in the dispatch and can be run by any seat with a shell.

## 8. Remaining risks / blockers

- **No blockers to the lattice's laws**: every armed law re-derives on
  committed bytes, and the two reds are in the control/envelope cells.
- **The battery is not a deterministic green**: 2 of 6 full-family
  executions returned rc 1 (one `c_alive`, one `s_norelink`). A CI-style gate
  that expects rc 0 from a single run will flake at roughly this rate on a
  loaded host. `s_norelink`'s third shape (`running` + small tail growth) is
  a *measured* realization; `c_alive`'s binding race is an *unresolved*
  discriminator.
- `x_rec_sink_remapfed` remains the landing's open mechanism question
  (untested here; §7).
- The family lock excludes same-family runs only **within one tree**; a
  second tree runs the same family concurrently (observed live).
- Host contention is real and recorded per entry (`host_is_quiet: false`,
  5–7 concurrent sibling batteries); the frozen-tree runs are immune to
  foreign *names* but not to daemon scheduling.
- This seat did not judge the landing and made no shipping decision.

*verifier leaf — measured on committed bytes, not judged.*
