# r89 REVIEWER — wave-B gate on committed `0d732989`

**Seat: REVIEWER (executor-class, leaf, frozen `probeParent`).** Lane
`/home/vgpnk/Projects/shokunin/audio-shokunin`. Scope **only** the r89
pwprof landing: `git show 0d732989 -- corpus/fixtures/measure_audio.py`
(committed blob sha256
`623c25cc55521472dc54a1ab2b4ccb4a9836fda3ca1a71dcca06092a4317cd22`,
32 062 lines) plus `reports/round-89/r89-author.md` (+215) and the two
green receipts under `corpus/live/runs/`. The worktree fixture was
**byte-identical to the committed blob at entry and at exit**
(`623c25cc…`); every replay ran against a **frozen `git archive 0d732989`
tree** (`corpus/live/r89-reviewer/tree/`), never the worktree fixture.
**Zero tracked writes** — this seat's only writes are
`?? corpus/live/r89-reviewer/**` and the new `reports/round-89/r89-reviewer.md`;
nothing committed, nothing pushed; **no `set-default-*`, no subject-0
write**; every audio object this seat created is `r89r_*`-tagged,
name-verified-unloaded and census-confirmed gone (§7). The tracked dirty
set at exit is unchanged from entry (` M …measure_audio.cpython-314.pyc`,
pre-existing). `TMPDIR=~/Projects/shokunin/tmp`,
`PYTHONDONTWRITEBYTECODE=1`. **Load preferred:** every replay ran at
loadavg **53–89** (1-min), with the **r89 verifier's own frozen-tree
replay live during r89r1–r89r6** (its `r89a_<pid>` seat objects appear in
my receipts as `foreign_r89a_nodes`, `host_is_quiet: false` — the designed
witness-not-verdict behavior; §5.3).

The frozen `probeParent` seat dispatched **exactly one** `ufo-labrat`
(bounded, read-only, no edits) on an arm-quality static hypothesis. Its
three strongest findings (C1/C2-class latent crashes, A1-class vacuity
path, B1-class census arms) were **re-derived by this seat** in code and
are reported as F7/F8 below; the rest of its output was noise or
duplicate.

---

## 0. Verdict

**PASS with findings.** The r89 family is **insertion-only** (surgery
proof: dropping the inserted block and reversing the five wiring splices
reproduces the parent blob **byte-for-byte**, sha256 `ad9d59b1…`,
30 504 lines — the exact blob the r88 reviewer pinned), `py_compile` is
clean, prior rows are untouched, and **every armed verdict re-derives
independently from receipt data alone — 99 checks/run, 198/198 on both
committed receipts and 884/891 across nine receipts**, the seven misses
being exactly the recorded arm failures (6× `g_hup`, 1× `x_top`). The
encoded boundary corrections are armed as data and all reproduce:
exact-N completions summed over driver domains, exact-4096 B stream
blocks, the {INT,TERM} graceful class vs the truncating class, the
`-o` incremental write (**SIGKILL leaves exactly 49 152 B / 46 rows in
9/9 receipts**), the strtol full-string `-n` lattice, the own-driver
schema invariants, the suspension arm, and the xw witness set. The
sharpest finding is **launcher sensitivity, not law-breaking**: the
`g_hup` arm pins `rc == -1`, so a run started with **SIGHUP ignored**
(`nohup`, `disown`, systemd/cron) false-FAILs — 6/6 of my `nohup`-launched
replays reddened with the *identical* signature, and a no-`nohup` replay
at loadavg 86→89 is **green** (F1). Secondary findings are fail-closed
arm-quality items (F2–F8) and one reporting-accuracy miss (F3).

| check | required | measured | verdict |
| --- | --- | --- | --- |
| committed-blob pin | `0d732989` fixture | `623c25cc…`, 32 062 lines; worktree byte-identical at entry **and** exit | PASS |
| diff shape | insertion-only, +1561/−3 | numstat `1561 3`; 1 insertion hunk + 5 wiring splices; exactly **3** deleted lines | PASS |
| surgery proof | parent reconstructible | reversed diff → sha256 `ad9d59b1…` **BYTE-EXACT** (30 504 lines) | PASS |
| `py_compile` | clean | rc=0 on the pinned blob | PASS |
| committed receipts ×2 | `failures: {}` | `…T074733533774Z` + `…T074816877001Z`: 4 entries, 0 failures, no `coverage_blocked` | PASS |
| independent law re-derivation | armed law set | **99 checks × 9 receipts = 891**, 884 passed; 198/198 on the committed pair; the 7 misses reproduce the recorded red surface exactly | PASS |
| exact-N gate completions | `-n` budget summed over drivers | `g_own` 8/8 infos (2 drivers), `g_two` 4/4 (hist `[2,2]`), wall 0.081–0.153 s — 9/9 receipts | PASS |
| 4096 B stream blocks | all samples % 4096 | 8192/20480/32768 (A,B,r89r7) and 20480/45056/65536 (co-tenant window) — 9/9 | PASS |
| INT/TERM vs KILL/HUP/USR1 | graceful vs truncating | rc 0 + `term_ok` vs rc −9/−10 + parse error — 9/9; HUP rc −1 in 3/9 (the 6 reds are the `nohup` context, **F1**) | PASS-with-finding |
| `-o` incremental write | SIGKILL leaves content | `o_kill` rc −9, **49 152 B / 46 rows** in 9/9 receipts (boundary falsification folded) | PASS |
| strtol parser lattice | 3 exact + 7 unbounded | `007`→7, `+3`→3, `" 3"`→3; `2.5`,`3abc`,`1e1`,huge,`-1`,`abc`,`0` all `alive_at_sig` → TERM-flush rc 0 — 9/9 | PASS |
| schema invariants | own-driver laws | 40/40 own blocks in A/B/r89r7 (14/27 under co-tenancy), 0 violations of order/count/quantum/transport/diff/id/xrun/fclock/nsb | PASS |
| suspension | own stops when follower dies | 21→0 in A/B/r89r7 (stall-confounded, **F4**); discriminating case realized under co-tenancy: 21→0 with **42 foreign blocks after the kill** | PASS-with-finding |
| xw witnesses | 8 legs | modreg, blank-line 28, 1-Client footprint, record-level broadcast, pw-top µs band, Profiler refusal, SIGPIPE −13, `/dev/full` silent — 9/9 (one `x_top` red, **F2**) | PASS-with-finding |
| fixed-path lock | NOT TMPDIR-scoped | `/proc/self/fd` resolution invariant; same-ROOT cross-TMPDIR serialized (3.43 s lock-child; **33.6 s real-probe wait**); cross-ROOT not serialized (**F6**, known class) | PASS-with-finding |
| leg count | headline "47 legs" | receipts carry **52** leg keys (27/12/4/9) — **F3** | PASS-with-finding |

---

## 1. Landing integrity

- `git show --stat 0d732989`: exactly two files — the fixture
  (`+1561/−3`) and the 215-line author report. The two green receipts and
  the family lock are **untracked** `corpus/live/` artifacts (the r83–r88
  convention; the orchestrator commits seat receipts later).
- **Insertion-only surgery** (`scripts/r89-landing.diff`,
  `scratch/`): reverse-applying the landing diff to the pinned blob
  (`patch -R -p1`) reproduces the parent `f1ef7071` blob **byte-for-byte**,
  sha256 `ad9d59b1e0dc5e2be4274f4966e571dabefed94076c06093eed1bf4cd2aef4c4`
  (30 504 lines). The five splices are the `--probe-pwprof-r89` argument
  line, the `sum([…])` mutex term, the `if args.probe_pwprof_r89:` branch
  (34 lines), the `mode` chain and the `suffix` chain; those are the
  **only 3 deleted lines** in the whole landing.
- `python3 -m py_compile` on the pinned blob: rc 0.
- Wiring is complete and collision-free: arg, mutex term, mode, suffix,
  branch, family lock; only one `--probe-*` mode can be selected. The
  inserted block is `measure_audio.py` lines 29293–30781 (constants
  `PWPROF_R89_*`, helpers `_pwprof_r89_*`, the four `*_r89_entry`
  functions), appended after the r88 block and before `def main()`.
- **Leg count (F3).** The commit message, the author report and the wave
  task card all say **47 legs**; both committed receipts carry **52 leg
  keys** — gate 27, oart 12, schema 4, xw 9 (identical key sets in both
  runs, no duplicates). The author's own per-entry list (27+12+4+8) omits
  `x_link` and then subtracts four link legs, double-counting the
  omission; the receipts are the record. Not verdict-changing.

## 2. Independent re-derivation (receipt-only)

`scripts/r89r_audit.py` re-implements **every armed verdict branch** of
the four entries (lines 29799–30781 of the pinned blob) against receipt
JSON only — no fixture import, no live host. One check per armed law:
gate 46 (incl. teardown/unloads), oart 14, schema 26, xw 13 = **99
checks/run**. For the 17 legs that retain `stdout_raw` the derived fields
(`parse_error`, `n_info`, `term_ok`, the per-driver info histogram) are
**re-computed from the raw bytes and cross-checked against the recorded
values**; for the popped-raw legs the recorded derived fields are used and
their internal consistency is re-derived from recorded primitives
(e.g. `count_step_ok` from `own_counts`, `seq_order_ok` from
`own_seq_shapes`).

| receipt | checks | passed | failed | note |
| --- | --- | --- | --- | --- |
| A `…T074733533774Z` | 99 | 99 | 0 | committed green |
| B `…T074816877001Z` | 99 | 99 | 0 | committed green |
| r89r1 (frozen tree, `nohup`) | 99 | 97 | 2 | `g_hup` (F1) + `x_top` (F2) |
| r89r2–r89r6 (frozen tree, `nohup`) | 99 each | 98 each | 1 each | `g_hup` (F1) |
| r89r7 (frozen tree, direct launch) | 99 | 99 | 0 | **green at loadavg 86→89** |
| **total** | **891** | **884** | **7** | 7/7 misses = the recorded arm failures |

The audit therefore reproduces the recorded verdict surface **exactly**,
including every red run — it neither hides a recorded failure nor invents
one. Volatile-text discipline holds: all normed fields scrub
`id:<n>`/`object <n>`/`<ns>`; the only raw counters live in the
explicitly-raw `stdout_raw` channels (recorded, never armed).

## 3. The brief-named claims — exact evidence

- **Exact-N gate completions.** `g_own` (`-n 8`): rc 0, exactly 8 `info`
  records, drivers `[r89a_ns2_<pid>, r89a_ns_<pid>]` — the budget is
  summed across driver domains. `g_two` (`-n 4`): rc 0, 4 infos, hist
  `{ns2: 2, ns: 2}`, wall 0.081 s. 9/9 receipts.
- **4096 B stream blocks.** `g_blocks` samples
  `0.3 s→8192`, `0.6 s→20480`, `0.9 s→32768` (quiet window) and
  `20480/45056/65536` (co-tenant window) — every nonzero sample a multiple
  of 4096, 9/9.
- **INT/TERM graceful vs KILL truncation.** A/B/r89r7: `g_term`/`g_int`
  rc 0 with `term_ok: true` (`…, { } ]`), `g_kill` rc −9, `g_hup` rc −1,
  `g_usr1` rc −10, all three truncating with a parse error. 9/9 for
  KILL/USR1; HUP is launcher-dependent (**F1**).
- **SIGKILL leaves 49 152 B.** `o_kill` (`-o k -n 0`, SIGKILL @2.0 s):
  rc −9, **49 152 B / 46 rows in all nine receipts** — the boundary's
  incremental-write falsification is armed and byte-stable. `o_eager`
  sees the path at t≈0.01 s (0 B at that instant, 46 KiB by the kill),
  `o_int` 32 KiB graceful, `o_exist` truncates the MARKER, `o_default`
  4312–4314 B `profiler.log`, `o_dash` a literal `-` file, `o_devnull`
  still writes the aux set, `o_dir`/`o_empty`/`o_proc` refuse rc 255
  `pwprof_cant_open`.
- **strtol parser lattice.** `n_007`→7, `n_plus3`→3, `n_space3`→3 (rc 0,
  `alive_at_sig` never true); `n_2_5`, `n_3abc`, `n_1e1`, `n_huge`
  (4294967298), `n_neg` (−1), `n_abc`, `n_zero` all `alive_at_sig: true`
  at 1.4 s with 65–66 infos, then TERM-flush rc 0. `g_lastwins`
  (`-n 4 -n 0`) alive at 1.4 s, 66 infos, rc 0. 9/9.
- **Schema invariants.** `s_window` (`-n 40`): 40 own blocks in A/B/r89r7,
  every armed invariant green — block order `info→clock→driver→follower`,
  `count` +1/cycle, `position += duration`,
  `next_nsec − nsec == duration/rate` (2048/48000), `transport ==
  "stopped"` while cycling, `diff == 1.0`, `prev ≤ signal ≤ awake ≤
  finish`, `prev[k+1] == signal[k]`, driver `finished` / latency `0/0`,
  ids == the seat node, `clock.system.monotonic`, nsec in the host window,
  `xrun == 0`, 0 `followerClock` rows, `nsb_blocks == 0`. Under
  co-tenancy the same invariants hold over the 14/27 own blocks that the
  summed-N budget leaves the seat driver.
- **Suspension 21→0.** `s_suspend`: kill the seat follower at 0.9 s inside
  a `-n 0` run → `own_pre_kill` 21, `own_after_kill` 0 in A/B/r89r7 —
  but see **F4** for the stall confound; the discriminating realization
  (own stops while **42 foreign blocks** keep the run alive) happened in
  my co-tenant replays.
- **xw witnesses.** `x_modreg` pactl index 536870922 added, node in
  `pw-dump`, **not** in the 13 native `Module` objects; `x_blank` blank
  line 28 of `pactl list modules short` survived by the guarded parse;
  `x_foot` exactly 1 `pw-profiler` client added, `nodes_delta == 0`;
  `x_conc` rc 0/0, 7–8 overlapping `(driver,count)` blocks
  **dict-identical**; `x_top` own row vs profiler medians; `x_profobj`
  rc 0 + `unsupported type PipeWire:Interface:Profiler` ×2; `x_sigpipe`
  rc −13; `x_devfull` rc 0 / 0 B stderr. 9/9 except F2.
- **Fixed-path lock.** See §6.

## 4. Findings

**F1 — the `g_hup` arm is launcher-sensitive: an inherited `SIG_IGN` on
SIGHUP false-FAILs the leg (fail-closed; root-caused, reproduced 6/6).**
My first six frozen-tree replays — all launched through **`nohup`** —
reddened on `g_hup` with a single signature: `exit_code −9`,
`killed_at_bound: true`, wall ≈9.05 s, 393 216–688 128 B streamed, i.e.
the leg **survived SIGHUP** and was SIGKILLed by the harness's own 9 s
bound. Live `/proc` sampling of the failing leg (`receipts/watch-hup-r89r6.json`:
fixture pid 1869080, the 4th `-J -n 0` child = pid 1872914, 279 samples
6.104→15.078 s) shows the process **ignoring SIGHUP, SIGINT and SIGQUIT
the whole time**: `SigIgn = 0000000000000007`, `SigBlk = 0000000000004002`
(INT+TERM blocked), `SigCgt = 0000000100000000` (glibc's internal RT
signal only). Controls:
`nohup sleep 40` → `SigIgn 0x1000007`; a plain background `sleep` →
`0x1000000` (no HUP bit); the fixture launched **without** `nohup` →
`SigIgn 0x1001000` (no HUP bit). Mechanism: `kill()`-generated signals
with an `SIG_IGN` disposition are **discarded at generation unless
blocked**; `pw-profiler` blocks INT/TERM (so its graceful path still
works — `g_int` is green even under `nohup`), but HUP is unblocked, so
the signal never lands. Independent HUP spots outside `nohup`:
**12/12** (sig_at 0.2/0.8/2.0/4.0 s), **3/3** with the seat's own two
null sinks + `pw-play` followers, **3/3** while a co-tenant probe was
live, **1/1** replaying the exact four-leg sequence
(`g_term,g_int,g_kill,g_hup`), and **1/1 full-probe replay green**
(r89r7, loadavg 86→89). **Verdict-changing? No — fail-closed** (never a
false green) and the committed receipts were produced in a non-`nohup`
context, so their `rc −1` is real. But the leg measures the *launcher*
as much as `pw-profiler`: any wave seat, cron job or systemd unit that
runs the fixture with SIGHUP ignored will redden it. Fold fix: reset the
armed signals to `SIG_DFL` in the spawned child (e.g. a `preexec_fn`),
or arm `rc == −1 OR (alive_at_sig and killed_at_bound and HUP provably
ignored)` and record the inherited disposition. Same class as r87-F1
(measured false-FAIL under load) but a different mechanism.

**F2 — `x_top` accepts a zero row and false-FAILs (fail-closed;
reproduced once).** The `own_row` selection (30633–30638) takes the last
frame's row for the seat id with `status != "C"` and a parseable
`wait_us`; `"0.0us"` parses to `0.0`, so a refresh row
(`quant 0, rate 0, wait 0.0us, busy 0.0us` — r89r1, id 78) is selected
and the 0.25–4.0 ratio arm then fails against the profiler's 4.87/4.04 µs
medians. The r88 refresh trap (`C`/`0.0us`) is documented; here the row
carried **status `R` with `quant 0`**, which the predicate does not
exclude. 1/7 replays (co-tenant live); the other six selected real rows
(`quant 2048, rate 48000`) and passed. Fold fix: require `quant > 0`
(or `wait_us > 0`) before accepting the row, else record
`coverage_blocked`.

**F3 — the "47 legs" headline is wrong; the receipts carry 52.** See §1.
Reporting-accuracy item for the scribe/fold; no behavioral consequence.

**F4 — the committed `s_suspend` realization is stall-confounded
(fail-open; the law itself is separately established).** In A, B and
r89r7 `foreign_after_kill == 0`: after the follower is killed **no**
driver emitted anything, so the whole graph went idle and
`own_after_kill == 0` is satisfied trivially — the arm cannot distinguish
"per-driver suspension" from "the run stalled". The discriminating case
*was* realized in my co-tenant replays (r89r1/r89r2: `own_pre_kill` 21/22,
`own_after_kill` 0, `foreign_after_kill` **42** — the verifier's drivers
kept the run alive while the seat driver stopped), consistent with the
boundary's clean measurement. So the claim is true; the author report's
wording ("the per-driver suspension law measured live") overstates what
the committed receipts alone show. Fold fix: arm
`foreign_after_kill > 0` as the non-vacuity witness (or record it as a
coverage requirement).

**F5 — byte-identity is recorded, never armed — and my replays supply the
counterexample (positive).** A/B/r89r7 have `byte_identical: true`
(quiet, 2-driver windows) while r89r1/r89r2 have `false` (6 498 vs 6 503,
6 503 vs 6 500 B) with the overlapping `(driver,count)` blocks still
dict-identical (7/7, 8/8 shared, `shared_identical: true`). The boundary's
"byte-identity is a low-rate-window artifact" falsification is thus
reproduced by an independent window, and the author's decision to arm
record-level identity only is correct.

**F6 — cross-ROOT lock co-tenancy (residual, known class).** The
fixed-path lock is per-ROOT: the worktree lock
(`pid=1728427`), my frozen tree's lock and the r89 verifier's frozen-tree
lock (`pid=1757362`→`1783278`→…) all coexist. Witnessed live this round:
my replays and the verifier's replays ran **concurrently** with no
serialization between them (my receipts record its `r89a_<pid>` nodes as
foreign witnesses; its probe's legs appear in my `/proc` trace). This is
the r86-F1/r87-F7/r88-F7 class, already queued; not new.

**F7 — latent crash paths in the schema/aggregation code (fail-loud,
code-confirmed).** `_pwprof_r89_schema_stats` indexes records directly
(`b["info"]["count"]`, `c["next_nsec"]`, `c["nsec"]`, `o["prev"]`,
`b["info"]["cpu_load0"]`, …) and sorts `None` among numbers
(29738–29794); `signal.Signals(-proc.returncode).name` (29420) raises
`ValueError` for unnamed signal numbers; `_pwprof_r89_jparse` returns any
JSON value, so `arr[-1] == {}` raises if stdout parses to a non-list.
Each aborts the entry **without writing a receipt** (loud, not a false
green), and each needs schema drift, a partial block, an RT-signal kill or
a dict-shaped stdout to trigger — none observed in nine receipts.

**F8 — static arm-quality items (fail-open/latent, re-derived in code).**
(a) `own_pre_kill` counts own blocks with **no clock record** (`.get(…, 0)`
→ `nsec 0 ≤ kill_mono`), so a malformed block satisfies the `>0`
non-vacuity gate with no timing measured (30319–30326); (b) own/nsb block
attribution requires a `driver` record, so a driver-less block is invisible
to both the own-schema filter and the `nsb_blocks == 0` law
(29716–29717, 30277–30280); (c) the 600 ms post-kill grace is a hard
cutoff (30325–30326); (d) `o_live.rows == 10` is an exact pin on a
file whose row count tracks the summed `-n` budget (30159); (e) the
`x_foot` census arms (`pwprof_during == before+1`, `nodes_delta == 0`,
30561–30568) are the r87-F1/r88-F1 exact-census class — **not observed
red in 7/7 replays** (including windows with 100+ foreign nodes), but
unmitigated by the family lock; (f) stderr is drained only after exit
(29413), a latent stall if a child ever writes >64 KiB to stderr (observed
≤ ~110 B). All fail-closed or crash-loud.

## 5. Frozen-tree replays and the launcher experiment

### 5.1 Replays (all from `git archive 0d732989`, TMPDIR fixed)

| run | launcher | stamp (UTC) | rc | loadavg (1/5/15) | failures |
| --- | --- | --- | --- | --- | --- |
| r89r1 | `nohup` | `…T075218524764Z` | 1 | 53.5→64.9 | `g_hup` (F1), `x_top` (F2) |
| r89r2 | `nohup` | `…T075258137692Z` | 1 | 54.9→72.5 | `g_hup` |
| r89r3 | `nohup` | `…T075501656013Z` | 1 | 75.4→81.3 | `g_hup` |
| r89r4 | `nohup` | `…T075648365685Z` | 1 | 79.4→78.2 | `g_hup` |
| r89r5 | `nohup` | `…T075743613142Z` | 1 | 78.9→80.7 | `g_hup` |
| r89r6 | `nohup` | `…T075852904044Z` | 1 | 83.6→83.5 | `g_hup` |
| r89r7 | direct | `…T080028355088Z` | **0** | **86.3→88.7** | **none — green, 4/4 entries** |

Every red run is fail-closed (the receipts' `failures` lists are exactly
the arms above; no `coverage_blocked` was raised and no green claim is
weakened). The green r89r7 is the **highest-load** run of the set, which
also closes the r87-F1 question for this family: the r89 arms are
load-robust; the one environmental sensitivity is signal inheritance (F1).

### 5.2 Serialization pair (same ROOT, different TMPDIRs, real probes)

r89r1 07:52:16.33→07:52:18.55 (42.2 s); r89r2 started 07:52:24.99 and
ended 07:52:58.16 (73.2 s = **33.6 s lock wait** + 39.6 s own work);
receipt stamps strictly sequential (`…T075218524764Z` < `…T075258137692Z`).
**The fixed-path lock serialized two same-ROOT cross-TMPDIR probes
end-to-end** (held to process exit).

### 5.3 Co-tenancy

The r89 verifier's frozen-tree replay was live throughout r89r1–r89r6: my
receipts record its objects as foreign witnesses
(`foreign_r89a_nodes: ['r89a_1757362_pl', …]`, `fixture_runs: 1`,
`host_is_quiet: false`) and never as verdict inputs; my `/proc` trace
(`watch-hup-r89r6.json`) shows its fixture (pid 1872348) running its own
`-J -n 0` / `-o k -n 0` legs interleaved with mine. No arm reddened from
that churn (the `x_foot` census survived, §4/F8e).

## 6. Lock

- **Path invariance:** `scripts/lockchild.py` under two different TMPDIRs
  resolves both to `<ROOT>/live/measure_audio-pwprof-r89.lock` (realpath
  via `/proc/self/fd`) — never `$TMPDIR`; the written content is the
  child's own `pid=… ns=… role=…`.
- **Same-ROOT cross-TMPDIR:** holder locked at 0.000 s / released at
  4.001 s; second process (other TMPDIR, +0.5 s) locked at **3.432 s** —
  blocked, not raced. Real-probe pair §5.2 confirms end-to-end.
- **Cross-ROOT:** a second ROOT locks its own file immediately (0.000 s)
  while the first holds — **not serialized** (F6), as designed by the r84
  F1 consensus (family-scoped, not global).
- **Open failure:** `_pwprof_r89_family_lock` still returns `None`
  silently on `OSError` (29505–29521) — the r88-F5 class; in-lane the
  directory always exists, and both my replays wrote the lock file.

## 7. Hygiene

- `git status --short` at exit: only the pre-existing
  ` M corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` (dirty at
  entry) and `??` artifacts; the worktree fixture is still `623c25cc…`.
- Residue census after all work: **0** `r89a_`/`r89r_` modules, **0**
  matching nodes in `pw-dump`, no owned `pw-play`/`pw-profiler`/`pw-top`
  processes, all my 24 load hogs killed (pidfile + `comm`-checked), the
  two spot null sinks unloaded by verified `sink_name=` index (rc 0,
  `residue_nodes: []`), spot tone files unlinked. Every receipt's
  `unloads[*].exit_code == 0`, `sinks_gone` all-true,
  `own_nodes_after: []`, no `residual_destroy`.
- Receipts: `corpus/live/r89-reviewer/` — `pins/` (both blobs),
  `scripts/r89-landing.diff`, `scripts/r89r_audit.py`,
  `scripts/{run_replay,lockchild,spot_hup,spot_hup_state,spot_hup_ctx,spot_legseq,watch_hup,watch_hup2}.py`,
  `receipts/{audit-summary,replay-summary,spot-*,lock-*,watch-hup-r89r6}.json`,
  `runs/` (7 replay receipts + timeline + stdout/stderr logs), the frozen
  `tree/` (44 328 files) and the reverse-patch `scratch/`.
- Exit-state observation: three *other* wave-B seats were mid-run with the
  same family when this seat closed (`r89a_ns_1995525`,
  `r89a_ns_1995530`, `r89a_ns_1995535`, …) — their objects are foreign
  witnesses, and none of my seven replay pids leaves a module or node
  (checked by name: 0/0 for all seven).

## 8. Blockers and non-blocking notes

None blocking. Notes for the fold:

- **F1** is the actionable one: reset the armed signals to `SIG_DFL` in
  the spawned child (or arm the inherited-disposition alternative) so the
  `g_hup` leg measures `pw-profiler`, not the launcher. Every wave seat
  that runs the fixture from a `nohup`/`disown`/systemd context will
  otherwise see a red `g_hup` — as six of my seven replays did.
- **F2/F4/F8** are arm-quality items; the committed receipts contain the
  real measurements, so no green claim is unsupported today.
- **F3** is a citation-discipline item (52 legs, not 47).
- **F6** is the known cross-ROOT residual, live-witnessed for the fourth
  round running; the family lock's *same-ROOT* guarantee is proven.
- The author's "both runs identical bytes" claim is not
  receipt-derivable (no fixture hash is recorded in the receipt); the
  committed blob itself is pinned and replayed byte-exact here, and the
  two receipts' leg sets and class names are consistent with it.
- Foreign residue (`r87t_ns`, `r84a_probe_548706`, the verifier's
  `r89v_*`/`r89a_*` objects) was observed and never touched; the only
  foreign-object write anywhere in this seat was the two spot null sinks
  it created and name-verified-unloaded itself.
