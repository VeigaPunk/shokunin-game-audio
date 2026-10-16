# r89 critic — wave-B gate on committed `0d732989`

Seat: `ufo-executor` (critic duties as assigned by
`.ufo/waves/shokunin-train-20261015-w22/tasks/audio-r89-critic.md`).
**Committed tree only** (`0d732989`), zero tracked writes, nothing
committed. Receipts: `corpus/live/r89-critic/` (`MANIFEST.shas.txt`
carries every artifact sha and the commands that produced it).

**Verdict: GATE FAIL as a reproducible green landing — PASS on every
encoded law.**

Every claim the r89 landing encodes **re-derives** from the committed
receipts and is independently corroborated read-only on the live host:
the four committed verdict blocks replay **8/8 clean with no pid binding
and no substitutions** (all arm inputs are recorded — better than r88's
F4/F10), **127 mutations × 2 runs = 254 evaluations behave exactly as
designed**, the `-n` strtol lattice, the exact-4096 B stream blocks, the
INT/TERM-graceful-vs-KILL-truncating classes, the SIGKILL-leaves-49152 B
incremental write (12 × 4096, 46 rows), the schema invariants, the
suspension 21→0, and the xw witnesses all hold on both green receipts;
the fixed-path lock excludes cross-`TMPDIR` **5/5 as designed**; the
refusal/version/Profiler-object laws reproduce live with byte-exact
stderr sizes.

But the landing is **not reliably green under the wave's own execution
mode**: on the *identical committed bytes* the wave's sibling seats
(r89-verifier and r89-reviewer, running right now) produced **6 red
runs out of 8** across **three distinct classes** — `g_hup` (5/8, a
**launcher-inherited SIGHUP disposition**, mechanism proven below),
`x_foot` (1/8, a client-census bracket race whose natural-rate false-FAIL
rate this gate measured at **17.6 %** of 0.35 s windows), and `x_top`
(2/13, a WAIT/BUSY ratio lottery). The author's two runs were **solo**
and green; the reds are the arms and the launcher, not the laws. This is
the r88-verifier's GATE-FAIL shape (`f1ef7071`) in new clothes, landed on
top of it.

The r89 landing also carries **report-vs-receipt numeric drift** (8
values, independently corroborated by the frozen probeParent's labrat)
and one **evidence claim with no recorded witness** (`modules_delta`).

Nothing here is a shipping decision.

---

## 0. Method (what was actually executed)

| check | evidence |
|---|---|
| commit custody + diff shape + wiring (static) | `custody.py` → `custody.json`; blob sha; per-hunk census; programmatic wiring assertions |
| receipt census + per-leg claim table (both green runs) | `replay.py` → `census.json`, `claims.json` |
| **arm replay** — the four committed verdict blocks sliced **verbatim** out of the commit object and `exec`'d against each committed receipt's own recorded `legs`/`entry` | `replay.py` → `arm-replay.json`; slices `verdict-*.py` (sha'd) |
| **mutation battery** — 127 mutations × 2 runs (**254 evaluations**), each declaring its designed outcome | `mutate.py` → `mutations.json` |
| **vacuity sweep** — 682 top-level leg-key deletions + 67 nested deletions + 52 whole-leg deletions | `sweep.py` → `sweep.json`; `nested_sweep.py` → `nested-sweep.json` |
| error-class lattice (sliced verbatim, whole r86–r89 chain) | `nested_sweep.py` (class section) |
| **lock either-way proof** — committed r89 lock sliced verbatim, scratch trees only, r85 `$TMPDIR` lock as negative control | `locktest.py` → `locktest.json`; `lockfn-r89.py`, `lockfn-r85.py` |
| bounded **read-only** live corroboration | `live_readonly.py` → `live-readonly.json` (read verbs + self-terminating refusal/version legs only; no object created, loaded, unloaded, linked or destroyed; no stream spawned) |
| **co-tenancy arm-class diagnosis** — natural-rate census of the arms' own inputs + `/proc` signal-disposition watcher + inheritance experiment | `churn.py` → `churn.json`; `churn_analysis.py` → `churn-analysis.json`; `sigdisposition.py` → `sigdisposition.json`; `sig_inherit.py` → `sig-inherit.json`; `co-tenancy-witness.txt` |
| frozen probeParent labrat (exactly one, read-only) | `labrat/labrat-report.md` (agent `4d05f9e0`) |

**No probe battery was run by this seat.** A battery would mutate the
shared host and would contend with the sibling wave-B seats that were
live on this lane throughout the gate (both the r89-verifier and the
r89-reviewer were running the same probe from copied trees — §7). The
read-only corroboration touches no graph object; the only processes this
gate spawned were read verbs, four self-terminating refusal/version
legs, three `python -c sleep` inheritance children, and the scratch-tree
lock children. Every run used
`TMPDIR=/home/vgpnk/Projects/shokunin/tmp`,
`PYTHONDONTWRITEBYTECODE=1`; host loadavg during the gate **52–82**
(load preferred, as the task directs).

---

## 1. Custody and wiring — verified

- committed fixture sha256
  `623c25cc55521472dc54a1ab2b4ccb4a9836fda3ca1a71dcca06092a4317cd22`
  == `git show 0d732989:corpus/fixtures/measure_audio.py` == worktree ==
  the sha the author report claims for **both** runs (and the sha the
  r89-verifier pinned independently in
  `corpus/live/r89-verifier/runs/fixture-sha.txt`). `git diff --quiet
  0d732989 -- corpus/fixtures/measure_audio.py` → IDENTICAL.
- diff shape: `+1561/−3` in the fixture (numstat) + 215 lines of report.
  Six hunks: one **1535-line insertion** (the r89 block, appended between
  `pwtop_r88_entry()`'s `return` and `def main()`), plus five wiring
  hunks (`+1` arg, `+1/−1` mutex sum, `+20` dispatch, `+1/−1` mode,
  `+1/−1` suffix). **The only 3 deleted lines are exactly the three
  replaced wiring lines** (`mutex-sum`, `mode-ternary`,
  `suffix-ternary`, classified programmatically). No prior-family line is
  touched.
- wiring present and correct (programmatic assertions): the
  `--probe-pwprof-r89` arg exists; `args.probe_pwprof_r89` is in the
  133-member mutex sum; the dispatch `if args.probe_pwprof_r89:` runs
  with `_r89_family_lock = _pwprof_r89_family_lock()` **before** the
  first entry and held to exit; all four entries are dispatched
  (`pwprof_{gate,oart,schema,xw}_r89_probe`); `mode`/`suffix` carry
  `-pwprof-r89` first in the ternary.
- guards checked statically in the committed block: private restore key
  `r89arole<pid>` (never the shared `music`); **no `set-default-*` call
  anywhere in the r89 block** (the only occurrence is the comment saying
  so); every unload goes through `_pactlmon_r85_unload_own`; residual
  `r89a_<pid>`-tagged nodes are destroyed by id before the final sweep;
  `sinks_gone`/`own_nodes_after` armed; every spawn is bounded and killed
  by process group (`_alsapw_r84_killpg`, 63 call sites in the file).
- `compile()` of the committed source is clean (no `py_compile` run —
  bytecode is never written by this seat).

## 2. Receipt census — the landed artifact

Both receipts are green: **52 recorded legs across 4 entries**
(`gate 27 / oart 12 / schema 4 / xw 9`), `failures: []` in all four
entries, and `coverage_blocked` **absent** (not just empty) in all four
on both runs.

| field | run A `…074733533774Z` | run B `…074816877001Z` |
|---|---|---|
| mode | `probe-pwprof-r89` | `probe-pwprof-r89` |
| legs | 27 / 12 / 4 / 9 | 27 / 12 / 4 / 9 |
| failures | `[]` ×4 | `[]` ×4 |
| `coverage_blocked` | absent ×4 | absent ×4 |
| `sinks_gone` | all-true | all-true |
| `own_nodes_after` | `[]` | `[]` |
| `unloads[*].exit_code` | 0 ×2 / 0 / 0 ×2 / 0 | 0 ×2 / 0 / 0 ×2 / 0 |
| `contention.host_is_quiet` | true | true |
| `foreign_r89a_nodes` | `[]` | `[]` |
| loadavg (1-min, 4 entries) | 56.86 / 54.98 / 54.98 / 54.66 | 53.90 / 52.78 / 52.56 / 52.35 |

**Leg-count discrepancy (F7).** The report, the task text and the commit
message all say **47 legs**; the receipts carry **52**. The report's own
per-entry counts (27 + 12 + 4 + **8**) sum to 51 — its xw section says
"8 legs" while the receipt records **9** (`x_link` is omitted from the
prose). The r88 convention counts every recorded leg key (r88: 28+41+10 =
79 = receipt), so 47 matches no artifact. This is documentation drift,
not a verdict defect: every leg is recorded and every leg is read by an
arm (§4).

## 3. Arm replay — verbatim, no substitutions, 8/8 clean

The four `# ---------------- verdicts ----------------` sections were
sliced **byte-exact** out of the commit object (sha'd as
`verdict-pwprof_*_r89_probe.py`) and `exec`'d inside `if True:` against
each committed receipt's **own recorded** `legs`/`entry`:

| run | gate | oart | schema | xw |
|---|---|---|---|---|
| A `…074733533774Z` | 0 failures | 0 | 0 | 0 |
| B `…074816877001Z` | 0 failures | 0 | 0 | 0 |

`coverage_blocked` stays absent in all eight replays.

**This is a genuine improvement over r88**: the replay needed **no pid
binding** (the schema id law compares against the recorded
`entry["refs"]["own_node_id"]`, not against `r89a_ns_<pid>`), and **no
arm input had to be reconstructed** — unlike r88's `pt_n3` (F4) and
`wd_cli_id` (F10). The committed receipt is a complete re-derivation
witness for the committed verdict surface.

## 4. Mutation battery — 254 evaluations, 0 not-as-designed

127 mutations × 2 runs. Each mutation declares its designed outcome;
"as designed" means the arm did exactly that.

| designed | evaluations | as designed |
|---|---|---|
| RED (the arm must catch it) | 208 | **208** |
| CB (named `coverage_blocked`, unmeasured) | 16 | **16** |
| CRASH (loud, not a failure row) | 2 | **2** |
| GREEN (volatile control must stay green) | 28 | **28** |

Headline arms that go RED as designed: `g_own` rc/term/n_info,
`g_two` rc/n_info/wall/term, `g_term`/`g_int` rc+term, `g_kill`/`g_hup`/
`g_usr1` rc+parse, `g_blocks` non-4096 and all-zero, `g_o_ignored`
creation + "Logging to", `g_extra`, `g_remote_empty`, both rc-255 remote
refusals, `g_opt_bogus` wrong-class, `g_version`, `g_lastwins`, the
3 strtol-parse legs, the 7 unbounded legs, all 11 `-o` arms, all 21
schema sub-arms, and all 8 xw arms.

Volatile controls that stay GREEN (proving the arms are not pinned to
volatile text): `wall_s` on every leg except `g_two` (whose wall bound
*is* armed), `stdout_bytes`, `loadavg`, `unloads`, `g_own.drivers`,
`g_two.driver_info_hist`, all schema witnesses (driver/follower names,
`own_counts`, durations, rates, block types, statuses, follower
latencies, wait/busy ranges, `cpu_load_sorted_desc`, seq shapes), leg
text, `x_conc` byte sizes + `byte_identical` (**correctly unarmed** — the
boundary falsified byte-identity, and both receipts record
`byte_identical: true` anyway), `x_top` frame metadata, `x_foot`
metadata, `x_modreg` module count, and a consistent `refs` re-point.

## 5. Vacuity sweep — where the arms are fail-open

682 top-level leg-key deletions (568 unarmed / 105 RED / 9 CB), 67
nested deletions, 52 whole-leg deletions:

- **All 52 whole-leg deletions CRASH** (`KeyError` out of the verdict
  block — loud, aborts the run, never a silent pass). No leg is
  conditionally absent, and `x_profobj`'s conditional `info`/`enum`
  sub-legs are guarded fail-closed (`rc None != 0` → RED).
- **The schema lattice is fail-closed**: `seq_order_ok`,
  `quantum_relation_ok`, `pos_step_ok`, `order_ok`,
  `prev_is_last_signal`, `nsec_in_window` are all `is not True`-armed,
  and `transports`/`diffs`/`driver_statuses`/`driver_latencies`/
  `clock_ids`/`driver_ids`/`clock_names`/`xruns`/`xrun_counts`/
  `count_step_ok`/`own_blocks`/`own_counts` all go RED when deleted. This
  is the first r8x family in this wave whose headline invariants are
  absence-fail-closed (the r88 F1–F3/F5 class is *not* repeated here).
- **Fail-open claim inputs found (F4)** — fields the arms read but treat
  as absent-is-fine:
  - `s_window.stats.nsb_blocks` — the suspension law's *static* half
    (`if (st.get("nsb_blocks") or 0) != 0`) passes when the field is
    missing;
  - `s_window.stats.fclock_rows` — the "zero followerClock rows" claim
    (`if st.get("fclock_rows")`) passes when missing;
  - `s_suspend.own_after_kill` — the suspension law's *dynamic* half
    (`elif (l.get("own_after_kill") or 0) != 0`) passes when missing;
  - `g_o_ignored.file_created` — the "`-o` is ignored under `-J`" claim
    passes when the field is missing;
  - `x_conc.parse1`/`parse2` — the "clean parse" claim passes when
    missing (`rc` is correctly fail-closed);
  - `x_foot.pwprof_before` — defaults to 0 when missing.
  All six are latent (the recorder writes them in the same update), but
  they are the same class the wave has flagged four rounds running: a
  receipt with the field stripped is read as a pass.
- **Unarmed claim halves (F5)** — `s_suspend` records but never arms
  `exit_code`, `alive_at_sig`, `killed_at_bound`: the "the profiler run
  itself stays alive until TERM'd at 2.4 s" half of the suspension claim
  is recorded-only. `x_top.own_row.id` is recorded but not armed (the row
  is picked by id at record time; a re-derivation from the receipt cannot
  check that the row *is* the seat node, even though
  `entry["refs"]["own_node_id"]` is right there and arming is free).

## 6. Error-class lattice (sliced verbatim, whole r86–r89 chain)

| synthetic text | resolved class |
|---|---|
| `Can't connect to server: Host is down` | `pwprof_connect_down` |
| `Can't open file '.': Is a directory` | `pwprof_cant_open` |
| `unrecognized option '--r89bogus'` | `pwprof_opt` |
| both `Can't connect …` and `unrecognized option` | `pwprof_connect_down` (table order) |
| both r88 `invalid option --` and r89 `unrecognized option` | `pwprof_opt` (**r89-local table shadows the inherited chain**) |
| `unsupported type PipeWire:Interface:Profiler` | `cli_unsupported_type` (inherited r88 fallback — matches the receipts) |
| empty / `logging 12 samples` | `None` |

The r89 table is checked **before** the inherited chain, and it shadows
the byte-identical r88 `pwtop_connect_down` regex, so r89 receipts report
r89-local class names — correct precedence, verified by execution. The
within-r89 precedence is table-order (connect_down > cant_open > opt);
unreachable in practice (mutually exclusive argv paths), recorded so a
later reader does not mistake it for most-specific-first.

## 7. The fixed-path lock — either-way proof, and F8 live again

The committed r89 lock function was sliced verbatim and run on **scratch
trees** (`corpus/live/r89-critic/locktest/`) so the live lane lock file
was never written. The r85 `Path(tempfile.gettempdir())` shape — also
sliced from the same committed file — is the **negative control**.
**5/5 as designed:**

| case | lock | trees | TMPDIRs | expected | result |
|---|---|---|---|---|---|
| A | r89 | same | same | SERIALIZED | **SERIALIZED** (1.094 s) |
| B | r89 | same | **different** | SERIALIZED | **SERIALIZED** (1.097 s) |
| C | r85 | same | different | RACED (control) | **RACED** (0.000 s) |
| D | r89 | **different** | same | RACED | **RACED** (0.000 s) |
| E | r85 | same | same | SERIALIZED | **SERIALIZED** (1.106 s) |

Case B is the task's claim: the r89 lock is a **fixed lane path**
(`ROOT/live/measure_audio-pwprof-r89.lock`, never `$TMPDIR`), so
cross-`TMPDIR` same-family runs exclude. Case C proves the harness can
detect racing. Case D is F8 (below). The live lane lock was untouched
throughout: sha `d4fb899e…` before and after, still carrying the author's
run-B witness `pid=1728427 …` (mtime 04:47:42).

**F8 — the fixed-path lock is *tree-relative* (inherited, fifth round,
live-witnessed again).** `ROOT = Path(__file__).resolve().parents[1]`,
so the lock lives at `<tree>/corpus/live/…`. Proven by locktest case D
and **realized live during this gate**: at `2026-10-16T07:53:34Z` the
wave's own **r89-verifier** (pid 1774466) was mid-run on the same probe
from `corpus/live/r89-verifier/tree`, holding
`…/r89-verifier/tree/corpus/live/measure_audio-pwprof-r89.lock`, while
the **lane** lock was **FREE** — the two runs were not serialized. Its
objects (`r89a_ns_1774466`, `r89a_1774466_pl`, one `r89a` module) were
live in the graph. This is r86 F1/F6 → r87 F10 → r88 F8 → r89 again, and
again by the wave's own sibling seat. Within one tree the fixed path does
exclude.

## 8. Co-tenancy — the headline: the landing is not reliably green

The wave's own seats replayed the committed bytes while this gate was
running. Their receipts are on disk and were read read-only by this seat.
**8 replays, 6 red**, three distinct classes:

| receipt (committed bytes, sha `623c25cc…`) | reds | failing arm |
|---|---|---|
| author A1 / A2 (solo, foreground) | 0 / 0 | — |
| verifier `r89v1` (07:52:07Z) | 2 | `g_hup` rc −9; `x_foot` `{before:1, during:1, nodes_delta:−4}` |
| verifier `r89v2` | 1 | `g_hup` rc −9 |
| verifier `r89v3-orphan` | 1 | `g_hup` rc −9 |
| verifier `r89v3` | 1 | `x_top` `top 2.2/0.6us vs profiler 3.43/2.96us` (busy ratio 0.20) |
| verifier `r89v4` (HUP-corrected launcher) | 0 | — |
| reviewer r1 (07:52:18Z) | 2 | `g_hup` rc −9; `x_top` `top 0.0/0.0us vs profiler 4.87/4.04us` |
| reviewer r2 / r3 | 1 / 1 | `g_hup` rc −9 |

The reviewer's own receipt documents the co-tenancy itself
(`contention.host_is_quiet: false`, `fixture_runs: 1`). The reds are at
loadavg **52–61** — they are not load-driven.

### 8.1 `g_hup` (5/8) — launcher-inherited SIGHUP disposition (mechanism proven)

The leg requires SIGHUP at 0.8 s to kill `pw-profiler` (rc −1). Bimodal
on identical bytes:

| run | `g_hup` rc | signal | wall | bytes |
|---|---|---|---|---|
| author A1 / A2 | −1 | SIGHUP | 0.816 / 0.816 s | 28672 |
| verifier v4 | −1 | SIGHUP | 0.820 s | 57344 |
| verifier v1 / v2 / v3o, reviewer r1 / r2 / r3 | **−9** | SIGKILL | **9.03–9.08 s** | 376832–688128 |

`g_usr1` (SIGUSR1, same 0.8 s point) never flakes: rc −10 in **all** runs
— so the flake is HUP-specific. Mechanism, proven three ways:

1. **Live `/proc` masks** (`sigdisposition.json`, 43 `pw-profiler`
   processes observed): the six processes with `SigIgn = 0x7` =
   **{SIGHUP, SIGINT, SIGQUIT}** are the surviving ones. Read live: the
   sibling fixture
   `pid=1821763 python3 corpus/fixtures/measure_audio.py --probe-pwprof-r89`
   carries `SigIgn: 0000000001001007` ({HUP, INT, QUIT, PIPE, XFSZ}) and
   its child `pid=1825023 pw-profiler -J -n abc` carries
   `SigIgn: 0000000000000007` ({HUP, INT, QUIT}) — the ignored set is
   **inherited across `execve`**, while `restore_signals=True` cleared
   PIPE/XFSZ exactly as documented.
2. **Inheritance experiment** (`sig-inherit.json`, spawns only
   `python -c sleep`): parent default → child `{PIPE, XFSZ}`; parent
   ignores HUP/INT with `restore_signals=True` → child
   `{SIGHUP, SIGINT, PIPE, XFSZ}`. **`restore_signals` does not cover
   SIGHUP.**
3. **The sibling verifier diagnosed the same mechanism independently**
   and fixed its launcher: `corpus/live/r89-verifier/runs/battery-v5b.sh`
   is headed *"HUP-disposition-corrected launcher. Each fixture run is
   exec'd through runone.py (SIGHUP/SIGINT/SIGQUIT -> SIG_DFL) so the
   g_hup leg measures the host's default-terminate law, not the
   launcher's inherited SIG_IGN."* After that correction its replays
   `r89v4`, `r89v5`, `r89v6` are **green 3/3**.

So the law (HUP terminates `pw-profiler`) is intact; the committed
harness *cannot* measure it when the fixture itself is launched with
SIGHUP ignored — which is exactly how wave-B seats launch their
batteries (background job from a non-interactive shell). The author's
green runs are foreground runs; the wave's are not. Fix is one line in
`_pwprof_r89_stream` (`preexec_fn`/`restore` that resets SIGHUP to
`SIG_DFL`, as the verifier's `runone.py` already does).

### 8.2 `x_foot` (1/8) — a client-census bracket race

The arm requires `pwprof_during == pwprof_before + 1 and nodes_delta == 0`
across a ~0.35 s bracket, with `pwprof_during` counting **`pw-profiler`
clients**. A sibling seat running the same probe spawns ~25 `pw-profiler`
clients per run (its gate legs, `x_foot`, `x_conc` ×2, `x_top`,
`x_sigpipe`, …). Measured **read-only at natural rate** with two sibling
seats live (`churn.json` / `churn-analysis.json`): 164 samples over 24 s
via `pw-cli ls Client` / `ls Node` / `pactl list modules short`; observed
pw-profiler client counts `{0, 1, 2}`, node counts **15–19** (nine
sibling `r89a_*` nodes from two seats visible).

Over 165 sliding 0.35 s windows (background delta == 0 is the pass
condition, since the seat's own foot contributes the +1):

- **arm would PASS: 136/165 (82.4 %)**; **arm would FAIL: 29/165 (17.6 %)**
- client half alone (`pwprof_delta != 0`): **21/165 = 12.7 %**
- node half alone (`node_delta != 0`): **12/165 = 7.3 %**

The author disclosed only the node half ("a foreign node appearing inside
it would surface as a real failure"); the dominant half is the
undisclosed **client** half, and the realized red (`before:1, during:1`,
`nodes_delta:−4`) is precisely it. Fail-closed (a red run, not a
false-green), but it makes the landing a lottery in the wave's own
execution mode.

### 8.3 `x_top` (2/13) — a ratio lottery

The `_close` band is 0.25–4.0 on both WAIT and BUSY ratios. Across all
13 receipts available to this gate:

| run | own row | profiler medians | ratio wait/busy | in band |
|---|---|---|---|---|
| author A1 / A2 | 2.3/0.9, 1.6/0.6 | 4.09/2.22, 2.55/1.40 | 0.56/0.41, 0.63/0.43 | yes |
| verifier v1 / v2 / v3o / v3 | 2.4/1.9, 3.0/2.9, 6.8/5.8, 2.2/0.6 | 3.92/2.53, 8.49/7.03, 7.52/6.05, 3.43/2.96 | 0.61/0.75, 0.35/0.41, 0.90/0.96, 0.64/**0.20** | **no (v3)** |
| verifier v4 / v5 / v6 | 2.4/2.2, 5.5/5.9, 3.1/2.0 | 8.93/5.65, 7.06/4.65, 2.79/1.73 | 0.27/0.39, 0.78/1.27, 1.11/1.16 | yes |
| reviewer r1 | **0.0/0.0** | 4.87/4.04 | **0.00/0.00** | **no** |
| reviewer r2 / r3 | 3.8/4.4, 6.9/7.3 | 5.55/4.42, 7.91/7.31 | 0.68/1.00, 0.87/1.00 | yes |

Two of thirteen out of band (0.20, 0.00), including a pw-top row reading
`0.0/0.0 µs`. The cross-witness is real but its band is tight enough to
flake ~15 % under co-tenancy.

### 8.4 What is *not* co-tenancy-fragile (checked, positive)

- The refusal/version/object arms use **containment**, not emptiness
  (`x_profobj` checks rc 0 **and** the phrase; extra foreign stderr lines
  cannot flip it — the r88 class 2 does not recur here).
- `g_own`/`n_*` exact-N legs sum over **all** driver domains, so a
  foreign driver cannot break them.
- The schema arms are name-scoped to the seat's own driver
  (`r89a_ns_<pid>`) and are absence-fail-closed.
- `x_blank`'s hazard is the **resident** `libpipewire-module-access`
  multiline `{args}` (line 28, confirmed live and in both receipts), not
  a seat-owned module — it does not vanish when seats unload.
- `x_conc` arms record-level dict identity only (byte-identity correctly
  unarmed).
- The author's post-run census is corroborated live: **zero** `r89a`
  nodes/modules/sinks and zero `r89a`-named modules now; the pre-round
  foreign residue `r84a_probe_548706` and `r87t_ns` is untouched, exactly
  as the report claims.

## 9. Report-vs-receipt numeric drift (labrat-corroborated)

Eight values the report presents as measurements match **neither**
receipt (the report appears to quote run B, or a dev observation, where
the runs differ). All are volatile/unarmed, so **no verdict impact** —
but the report reads as if both runs matched, and the wave's scribe will
fold these numbers forward.

| claim | report | run A | run B |
|---|---|---|---|
| total legs | 47 | **52** | **52** |
| xw legs | 8 | **9** | **9** |
| `g_term`/`g_int` infos | 47 | **46** | **46** |
| `g_two` wall | 0.071 s | **0.081** | 0.071 |
| `o_int` bytes | 32347 | **32362** | **32340** |
| `o_default` `profiler.log` bytes | 4320 | **4314** | **4312** |
| `o_dash` `-` bytes | 6468 | **6472** | 6468 |
| `x_conc` bytes | 6471 | **6503** | 6471 |
| `x_top` row / medians | 1.6/0.6, 2.55/1.40 | **2.3/0.9, 4.09/2.22** | 1.6/0.6, 2.55/1.40 |

The frozen probeParent's labrat (`4d05f9e0`) independently produced the
same eight counterexamples from the report + receipts alone
(`labrat/labrat-report.md`); two seats, same table. **Independently
corroborated a third time during this gate**: the r89-scribe commit
`df0dd8bf` ("r89 scribe: INTACT — 222/222 checks, lock proven; **ADJ-1:
52 legs not 47 (x_link uncounted)**") flags the same leg-count drift as
its adjudication item.

**F6 — an evidence claim with no witness.** The report's `x_foot` bullet
cites `nodes_delta == 0`, **`modules_delta == 0`** — but `modules_delta`
**does not exist anywhere in the committed fixture** (0 occurrences) and
is absent from both receipts. The footprint claim's "never a module" half
is neither measured nor armed; the comment in the block says the same
thing the report claims. Either measure it or drop the clause.

**F8-note — `-o` artifact content is not retained.** `o_kill`'s
`bytes=49152` (= 12 × 4096) and `rows=46` support the incremental-write
falsification, but the artifact itself is deleted with the temp dir, so
"flushed in 4096 B blocks matching the stderr `logging N samples`
cadence" is supported by size only (the recorded 46 rows against 24
logged samples is ≈2 rows/sample, not 1:1 as the phrasing suggests).

**Dev measurement without a receipt (disclosed).** The `-o -n 4`
eats-`-n` behaviour is cited as "measured in dev" with no dev receipt on
disk (only the two green runs exist for r89) — unlike r88's F7/ADJ-1 this
is *disclosed* in both the report and the leg comment, so it is a
provenance note, not a concealment.

## 10. Live read-only corroboration (independent of the author's receipts)

`live-readonly.json` (full rc/stdout/stderr per leg); every command a
read verb or a self-terminating refusal/version leg, all bounded.

- `pw-profiler --version` → rc 0, `Compiled with libpipewire 1.6.8` (74 B)
  — corroborates `g_version` and the block's stated toolchain.
- `pw-profiler --help` → documents `-n, --iterations  Collect this many
  samples` and **`-o, --output  Profiler output name (default
  "profiler.log")`** — the `o_default` law is in the binary's own usage
  text. Nothing documents "0 = unbounded": that is a measured
  implementation detail, correctly claimed as such.
- `pw-profiler --r89criticbogus` → rc 255, `unrecognized option
  '--r89criticbogus'`, 455 B stderr (receipts: 449 B) — `g_opt_bogus`.
- `pw-profiler -r r89a_bogus_remote_critic -J -n 2` → rc 255,
  `Can't connect: Host is down`, **28 B** stderr — byte-identical to the
  receipts' `g_remote_bogus`/`g_env_bogus`.
- `pw-cli info 5` and `pw-cli enum-params 5 Props` → rc 0,
  `unsupported type PipeWire:Interface:Profiler`, **54 B** — exactly the
  receipts' `x_profobj` shape (Profiler object id 5).
- `pw-dump`: 85 objects, 13 native `Module` ids, Profiler id 5, **0**
  `pw-profiler` clients, **0** `r89a` nodes, foreign residue
  `['r84a_probe_548706', 'r87t_ns']` — corroborates `x_modreg`'s
  13-vs-pactl mismatch and the author's post-run census.
- `pactl list modules short`: 43 lines, **blank line 28** (from the
  resident `libpipewire-module-access` multiline args), 0 `r89a` modules
  — corroborates `x_blank` and the clean teardown.
- `pw-top -b -n 1` → one frame, `C` rows; loadavg 73.78 at capture.

**Non-perturbation of the siblings:** this gate spawned no `pw-profiler`
client and no `pw-play`, and its read verbs create only transient
`pw-cli`/`pw-dump`/`pactl` clients. The only armed census that could see
them is `x_foot`'s `pw-profiler` count (unaffected) and its
`clients_added` list (unarmed); `contention` counts only
pw_play/pw_record/pw_cat/paplay/parec/pacat/aplay/arecord/ffmpeg and
`fixture_runs` (none of mine). No node, module, sink, link or stream was
created, destroyed or retargeted by this seat.

## 11. Findings (ranked)

| # | severity | finding |
|---|---|---|
| **F1** | **high** | **The landing is not reliably green under the wave's execution mode.** 6 of 8 sibling replays of the committed bytes are red across three classes (§8); the author's two green runs are solo *and* foreground. |
| **F2** | **high** | **`g_hup` is unpassable when the fixture is launched with SIGHUP ignored** (5/8 reds). `restore_signals=True` does not reset SIGHUP; the ignored disposition is inherited across `execve`. Mechanism proven by `/proc` masks + inheritance experiment; independently diagnosed and fixed by the sibling verifier's `runone.py` (its next three replays are green). One-line fix in `_pwprof_r89_stream`. |
| **F3** | medium | **`x_foot` client-census bracket race**: 17.6 % of live 0.35 s windows fail the arm (12.7 % client half, 7.3 % node half) with two sibling seats running; realized as a red in the verifier's `r89v1`. The disclosure in the report names only the node half. |
| **F4** | medium-low | **Six fail-open claim inputs** in the verdict blocks (`nsb_blocks`, `fclock_rows`, `s_suspend.own_after_kill`, `g_o_ignored.file_created`, `x_conc.parse*`, `x_foot.pwprof_before`): absent ⇒ pass (§5). Same class as r87 F1/F2, r88 F1–F3/F5, but *latent* here (the recorder always writes them). |
| **F5** | medium-low | **Unarmed claim halves**: `s_suspend.exit_code`/`alive_at_sig`/`killed_at_bound` (the "run stays alive" half of the suspension claim) and `x_top.own_row.id` (the row's identity vs `refs.own_node_id`, free to arm). |
| **F6** | medium-low | **`modules_delta == 0` is cited but never measured** — 0 occurrences in the committed fixture, absent from both receipts (§9). |
| **F7** | low | **Leg-count drift**: report/task/commit say 47 legs, receipts carry 52; the report's own xw count (8) omits `x_link` (§2). Plus 8 volatile values quoted that match neither run (§9). |
| **F8** | medium (inherited) | **The fixed-path lock is tree-relative** — locktest case D + live witness: the r89-verifier ran the same probe from a copied tree while the lane lock was free (§7). Fifth consecutive round. |
| **F9** | low | **`x_top` ratio band flake**: 2 of 13 receipts out of band (0.20, 0.00), including a `0.0/0.0 µs` row (§8.3). |
| **F10** | informational | **`-o` artifact content is not retained** (bytes/rows only), so the "4096 B block cadence" phrasing is supported by size alone (§9). |
| **F11** | informational | **Dev measurement with no receipt** for `-o -n 4` (disclosed in report + leg comment) (§9). |
| **F12** | informational | **No in-receipt implementation sha**: the receipts carry no source hash; "two green on identical bytes" rests on worktree == commit == claimed sha and the author's statement (the r89-verifier pinned it separately). |
| **F13** | informational (inherited, not this landing) | A pre-r89 leg still calls `pactl set-default-sink` (r78-era `garbage-target` leg, with restore); the r89 block itself contains none — the wave constraint ("never `set-default-*`") is honored by this landing. |

**Improvements this landing deserves credit for** (verified, not
assumed): the committed verdict surface is **fully re-derivable from the
receipt alone** (8/8, no pid binding, no reconstruction — r88 F4/F10 not
repeated); the schema invariants are **absence-fail-closed** (r88
F1–F3/F5 class not repeated); byte-identity is **correctly unarmed** after
the boundary's falsification; and the refusal/object arms use
**containment** so foreign stderr cannot flip them (r88 class 2 not
repeated).

## 12. Blockers / remaining risks

- **Blockers: none for this seat's custody** (zero tracked writes, lane
  lock untouched, no battery run, host left as found).
- **F1/F2 are the landing's blockers as a *reproducible green***, and they
  are cheap to close: reset SIGHUP in the child (F2) and make the
  `x_foot` bracket census-based rather than exact-count (F3). The
  r89-verifier has already demonstrated the F2 fix end-to-end.
- **F3/F9 are fail-closed** (red runs, never false-greens): a red run
  costs a re-run, not a wrong verdict.
- **F4/F5 are latent** and only matter if a receipt is read without its
  recorder — the audit path the wave actually uses.
- The labrat had no exec (file-inspection only, r88 precedent) and made
  no edits; its hypothesis check is recorded verbatim in
  `labrat/labrat-report.md`.

## 13. Custody notes

- **Zero tracked writes.** The fixture in the worktree is byte-identical
  to the commit object; nothing was staged or committed. The only dirty
  tracked path is `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`,
  which was **already `M`** in this session's first `git status`
  (mtime 04:46:12 −0300, before this seat started); every gate run used
  `PYTHONDONTWRITEBYTECODE=1`, and no `__pycache__` exists under
  `corpus/live/r89-critic/`.
- **Lock-file disclosure.** The live lane lock
  `corpus/live/measure_audio-pwprof-r89.lock` was **never written** by
  this gate (sha `d4fb899e…`, still the author's run-B witness): the
  either-way proof ran on scratch trees under
  `corpus/live/r89-critic/locktest/`.
- **HEAD moved during the gate** (not by this seat): `df0dd8bf` (the
  **r89 scribe** lane, "INTACT — 222/222 checks, lock proven; ADJ-1: 52
  legs not 47") landed on top of `0d732989`. The r89 fixture is
  unaffected (`git diff --quiet 0d732989 HEAD -- corpus/fixtures/measure_audio.py`
  → identical), and this gate's custody is the r89 author commit named in
  the task. Disclosed so a later reader is not surprised by the sha.
- All gate receipts live under `corpus/live/r89-critic/` (untracked); the
  report is `reports/round-89/r89-critic.md` (untracked, uncommitted).
- **Disclosed co-tenancy**: the r89-verifier and r89-reviewer seats ran
  the same probe on this lane throughout the gate; this seat read their
  untracked receipts read-only (§8) and disclosed the overlap rather than
  hiding it.
