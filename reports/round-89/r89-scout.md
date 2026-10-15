# R89 scout — pw-profiler output lattice on PipeWire 1.6.8 (scout-finisher)

Round 89 pre-measurement. Host `plazir27`, measured **2026-10-15
12:34–13:09 UTC−3** (15:34–16:09Z). Repo
`~/Projects/shokunin/audio-shokunin` @ HEAD `ee6d684` (`r79 LOG:
ADMIT-corr`). Toolchain: PipeWire **1.6.8** (`pw-profiler` Compiled/Linked
libpipewire 1.6.8), WirePlumber **0.5.17-1**, libpulse **17.0-98-gb096**
(pactl 17.0, protocol 35), Python 3.14.7, Linux 7.2.3-arch1-3. Resident
profiler: `libpipewire-module-profiler` module id **4** (args literally
`{ #profile.interval.ms = 0 }` — interval commented out, i.e. module
default), Profiler interface object id **5**
(`PipeWire:Interface:Profiler`).

**Seat: SCOUT-FINISHER (leaf). Zero tracked-file edits.** `git status`
tracked-dirty set at entry and exit is identical: `SHONEN.md`,
`corpus/fixtures/measure_audio.py` + its `__pycache__` (sibling-owned,
never read/imported/executed). Every write is under
`corpus/live/r89-scout/` (≈7.2 MB, 419 files) plus this report. **Not
committed.**

**Finisher disclosure.** The dispatched r89 seat died mid-run: its
`r89_probe.py` had completed only `j_n8` rep0–2 (all 30 s timeout-kills,
zero output) and died inside `plain_o_n4/rep0` (no meta.json written;
`wd/p` left as the 0-byte eager artifact). Dead-seat artifacts preserved
verbatim in `recon/dead-seat-snapshot/`; original probe preserved as
`recon/r89_probe.orig.py`. This seat re-ran the full probe (all stages;
the dead seat's `j_n8` result reproduced identically). During the `drv`
stage the probe's own latent `pactl` blank-line parse bug crashed the
unload path — patched in place (orig preserved), missing stages
`drv`/`top`/`foot` then completed, and 6 edge legs added
(`r89_edge.py`, `runs_edge/`). Two transient leak events occurred and
were cleaned (§9).

---

## 0. Headline — the laws

| # | surface | law | sharpest measured fact |
| --- | --- | --- | --- |
| 1 | `-n` gating | **`-n N` counts emitted `info` records — driver cycles summed across ALL driver domains; an idle graph produces zero cycles, so `-n N>0` hangs forever** | idle: `-J -n {1,2,3,8}` ×9 and plain `-n 4` ×6 all SIGKILL'd at timeout with 0 stdout; live: `-n 4` completes rc 0 in proportion to cycles (1.68 s for 40 cycles @ 42.67 ms quantum); two seat drivers ⇒ `-n 4` done in **0.062 s** (2 cycles × 2 drivers, interleaved) |
| 2 | `-J` mode | **`-J` streams records live (≈4 KiB stdio blocks); SIGINT/SIGTERM → rc 0 + flushed `[{ } ]` — a parseable zero-record array indistinguishable from a successful empty run; SIGKILL → truncated, invalid JSON; `-o` is fully ignored under `-J`** | mid-run pipe reads: 16 384 B @1.0 s, 20 480 B @2.0 s, +11 679 B at exit (e1); SIGKILL mid-run: 20 480 B ending mid-token (`…"dela`), no ` ]` (e2); idle SIGINT ×4 legs: rc 0, stdout exactly `[{ } ]\n`, **no file, no "Logging to"** even with `-o` passed (sig_int_j/sig_term_j wd=[], stderr=0 B) |
| 3 | `-o` artifact mode | **the output file is created eagerly as 0-byte at startup; ALL content is written at exit; graceful exit also emits Timing{1..5}.plot + Timings.html + generate_timings.sh; "Logging to" goes to stderr** | `-o p -n 4` idle×3: `p` = 0 B (sha of empty) with stderr `Logging to p`; live `-o art -n 20`: `art` 21 593 B columnar dump + 5 .plot + .html + .sh, stderr `dumping scripts for 1 followers`, stdout `run 'sh generate_timings.sh'…`; SIGINT adds stderr `logging 24 samples  0 seconds [CPU …]` |
| 4 | `-n` parsing | **atoi with zero validation: `-1`, `abc`, `2.5` all silently accepted (idle → all hang); `-n 0` = unbounded (SIGINT → rc 0 `[{ } ]`)** | n_neg/n_abc/n_float ×9: zero error output, killed at 10 s; n_zero ×2: rc 0 at SIGINT, stdout `[{ } ]\n` |
| 5 | record schema | **per-cycle block = {info, clock, driver, follower(, followerClock)}; `info.count` is the emitting driver's own profiled-cycle counter (NOT per-run, NOT global); `clock.cycle` counts driver scheduling cycles; `clock.nsec` is CLOCK_MONOTONIC ns inside the run's monotonic window** | same sibling driver over 3 sequential `-n 30` runs: counts resume 2→31, 32→61, 62→91; fresh seat sink: counts start 0; two-driver run: interleaved counts `[0,0,1,1]` keyed by driver id 146/148 while `clock.cycle`=20/21 |
| 6 | invariants | **`prev`/`signal`/`awake`/`finish` are monotonic; `position` += `duration` per cycle; `next_nsec − nsec` = duration/rate exactly; `transport:"stopped"` while cycling; `diff` = driver-clock drift ratio; `followerClock` is a frozen zero-template emitted only for clock-exposing followers** | order_ok + pos_step_ok 3/3 on 30-cycle windows; quantum_ns 21 333 333 (=1024/48000) and 42 666 666 (=2048/48000); null-sink diff 1.000000 vs live ALSA SPDIF diff **1.0057**; followerClock rows all-zero (`position 0, next_nsec 0, diff 0.0`, id 158 = r80 loopback follower) and **absent entirely** under a pw-play follower |
| 7 | refusals | **pw-profiler refuses with rc 255 fast (unlike pw-cli's rc-0-with-stderr class); bad remote 2 ms `Can't connect: Host is down`; `-r ""` silently means the default remote (connects → idle hang); extra positional args silently ignored** | rc 255 ×3: remote_bogus, out_unwritable (`Can't open file …`), opt_bogus (usage→stderr); remote_empty ×3: 15 s hang, 0 output; extra_arg rep2 **completed rc 0 in 0.574 s** because a sibling driver (r80md) happened to be live — positional arg ignored |
| 8 | cross-witness | **profiler `awake−signal` ≈ pw-top `WAIT`, `finish−awake` ≈ `BUSY` (µs); pw-profiler registers only a `Client` — no node, no module; `pactl list modules` (17) ⊋ pw-dump Module objects (13) — the four pipewire-pulse stubs and every pactl-loaded module never appear as native Modules; the Profiler object (id 5) refuses pw-cli introspection** | seat driver window: profiler busy 4.4–6.5 µs / wait 4.7–7.4 µs vs pw-top `WAIT 5.4us BUSY 5.9us` same instants; footprint legs: only +1 `pw-profiler` client during run; `pw-cli info 5`/`enum-params 5 Props` → rc 0 + stderr `Error: "unsupported type PipeWire:Interface:Profiler"` ×4 |
| 9 | concurrency | **the profiler module broadcasts one identical record stream to every attached client** | two concurrent `-J -n 8`: both rc 0, **byte-identical stdout** (sha match, 6462 B / 6454 B, 33 recs), 0.32 s wall |
| 10 | process-level hazards | **`pactl list <kind> short` emits genuinely blank lines (multi-line `{args}` blocks) — `line.split()[0]` IndexError kills naïve parsers; this exact bug killed the dead seat's teardown and re-hit this seat's edge harness** | blank line reproduced at line 28 of `pactl list modules short` (persistent, not churn); crash trace in `recon/probe-all.log`; leaked `r89prof_ns` module 536870939 unloaded by verified index |

---

## 1. The gating law: `-n` counts driver cycles; idle ⇒ infinite hang

The dead seat's three `j_n8` reps (`pw-profiler -J -o prof89 -n 8`) all
ended `rc=-9, timed_out, wall 30.0 s, stdout_len=0, stderr_len=0,
wd_files=[]`. Reproduced verbatim by this seat (3/3 identical), and the
same holds for every idle `-n N>0` leg: `n_1`, `n_2`, `n_3` (6 runs,
30 s kills), `n_neg`, `n_abc`, `n_float` (9 runs, 10 s kills),
`remote_empty`, `extra_arg` reps 0–1 (15 s kills). On the idle graph
**not even the `[` preamble is emitted** — stdout stays 0 bytes ≥2.7 s
(timing probe, `recon/recon-notes.md`).

Mechanism evidence, not just assertion:

- With a seat-owned driver (`module-null-sink r89prof_ns` + `pw-play`
  tone), `-n 40` completes rc 0 in **1.681 s** — 40 cycles ×
  2048/48000 = 42.666 ms ⇒ 1.707 s expected, observed 1.681 (last cycle
  partial); `-n 60` ⇒ 2.534 s (e1); `-n 30` on a 1024-quantum sibling
  driver ⇒ 0.635–0.640 s; `-n 8` ⇒ 0.316 s (e3). Wall time is
  **quantum-driven**, not timer-driven.
- `-n` counts **info records summed over all live drivers**: two seat
  drivers (48 k+44.1 k null sinks) ⇒ `-n 4` done in **0.062 s** with
  records interleaved per driver (e4); three drivers (incl. a live ALSA
  domain) ⇒ 0.060 s.
- A **sibling** driver satisfies it identically: `schema_n30` ×3 rode
  `r80md_1212874_lnk_a` (rc 0, 0.64 s each); `extra_arg` rep2 completed
  in 0.574 s on the same sibling driver while reps 0–1 hung on the idle
  graph. There is no seat/domain scoping — `-n` watches the whole
  graph.
- Corollary (inference, labeled): if the last active driver suspends
  mid-run, a `-n` leg stalls indefinitely — the "run" is only as
  bounded as the loudest driver's lifetime.

Author-facing rule: **always bound pw-profiler with your own driver or
an outer timeout; rc 0 means data, a silent hang means none.**

## 2. `-J` stream semantics

- Records are written **as they are produced**, block-buffered
  (~4 KiB boundaries observed: 16 384 B at t=1.0 s, 20 480 B at t=2.0 s
  on a 42.7 ms-cycle driver — e1). The `[` opening is emitted lazily
  *with the first record*, not at startup.
- **SIGINT or SIGTERM** → graceful rc 0 and the array is closed:
  `[{ } ]\n` when zero records were collected, or `…, { } ]` after
  streamed records. The trailing empty object is the stream terminator —
  `parse_j` treats `arr[-1] == {}` as the end marker.
- **SIGKILL** mid-run leaves the streamed prefix unterminated and cut
  mid-token (20 480 B ending `…"dela`) — **invalid JSON** (e2). A
  consumer must tolerate truncation; treat "parses cleanly" as the
  only completeness witness.
- **The `[{ } ]` trap:** on an idle graph, SIGINT produces a
  *syntactically complete* array whose only element is the end marker —
  `json.loads` succeeds, `n_records == 0`. This is indistinguishable
  from "profiled a graph with zero driver activity"; there is no
  field marking it as aborted. Distinguish by wall time / expected
  driver liveness, not by the JSON.
- **`-o` under `-J` is fully ignored**: `sig_int_j`/`sig_term_j`
  (`pw-profiler -o <name> -J`) produced `wd_files=[]` and 0-byte stderr —
  no file created, no "Logging to" line. `-J` writes *only* the JSON
  stream to stdout.

## 3. `-o` artifact mode (the gnuplot lattice)

- `pw-profiler -o NAME` creates `NAME` **eagerly, 0-byte**, at startup
  and announces `Logging to NAME` on **stderr** (channel verified).
  Default name `profiler.log` (verified: `plain_default_n4` created it).
- The file gets content only at exit. **SIGKILL leaves the 0-byte
  husk** — an artifact that looks produced but is empty (all 9 plain-mode
  timeout legs show sha of the empty string).
- Graceful exit with data (`-o art -n 20`, 20 cycles): writes `art`
  (21 593 B, columnar text — 20 rows; col 1 = "Audio period (current
  wakeup − prev wakeup)" µs, col 3 = "Audio driver delay (h/w ptr −
  wakeup time)", col 4 = "estimated (cycle period or quantum)" per the
  generated `Timing1.plot` titles; remaining columns are per-follower
  series used by Timing2–5 — **full column semantics undecoded, named
  gap**), plus `Timing{1..5}.plot` (gnuplot scripts), `Timings.html`
  (1087 B loader page), `generate_timings.sh` (105 B), and prints
  `run 'sh generate_timings.sh' and load Timings.html in a browser` on
  **stdout**. SIGINT adds stderr `logging N samples  S seconds [CPU a b
  c]`.
- With **zero data** even graceful SIGINT/SIGTERM writes nothing into the
  file and emits no aux files (sig_int_plain/sig_term_plain: wd =
  [0-byte file] only). The aux set appears iff samples exist.
- `-o` to an unwritable path refuses fast: rc 255, `Can't open file
  /proc/r89prof/x: No such file or directory` (3/3).

## 4. `-n` semantics and parsing

| arg | behavior observed |
| --- | --- |
| `-n N>0` | collect N info records (driver cycles, all domains); hang forever if fewer cycles ever occur |
| `-n 0` | unbounded; SIGINT → rc 0, `[{ } ]\n` at 3.001 s (2/2) |
| `-n -1` | no error; hangs (atoi −1 → behaves unbounded); 3/3 |
| `-n abc` | no error; hangs (atoi → 0); 3/3 |
| `-n 2.5` | no error; hangs (atoi → 2; needs 2 cycles); 3/3 |
| no `-n` | unbounded (e6B ran until SIGINT; `logging 24 samples`) |

There is **no CLI validation of `-n`** — bad values silently become
other behaviors. `man pw-profiler` does not document `-n` or `-J` at
all (1.6.8 man page stops at `-r/-h/--version/-o`); the `--help` text
is the only built-in doc for them.

## 5. Record schema — verified invariants and traps

From `schema_n30` ×3 (30-cycle windows on a live sibling driver,
48 k/1024 quantum) and `own_driver` ×3 (40-cycle windows on the seat's
48 k/2048 sink):

- **Per-cycle block order:** `info` → `clock` → `driver` → `follower`
  (→ `followerClock` when applicable). One block per driver cycle.
- **`info.count` is the emitting driver's profiled-cycle counter**, and
  it persists across clients: three sequential `-n 30` runs on the same
  sibling driver resumed 2→31, 32→61, 62→91; a *fresh* seat sink starts
  at 0. Under two drivers the stream interleaves `[0,0,1,1]` keyed by
  driver (e4). Do **not** use `count` as a per-run sample index.
- **`clock.cycle`** = driver's own scheduling counter — 20 at attach on a
  sink that had ticked ~20 cycles before the profiler client connected;
  **`clock.position`** += `duration` each cycle (pos_step_ok 3/3), and
  position at attach ≈ elapsed cycles × duration (20×2048 = 40 960,
  observed 40 960 in the manual live run).
- **`clock.nsec`/`next_nsec`** are CLOCK_MONOTONIC ns: `next_nsec − nsec`
  = duration/rate exactly (21 333 333 ns for 1024/48000; 42 666 666 ns
  for 2048/48000); the nsec range falls inside the run's
  `time.monotonic_ns()` bounds ±5 s (3/3 `inside_window=True`) — so
  profiler timestamps can be cross-correlated with host monotonic time.
- **Timing chain:** `prev ≤ signal ≤ awake ≤ finish` on every
  driver/follower row (3/3), and `prev` of cycle k+1 equals `signal` of
  cycle k (`prev_is_last_signal` true). `awake−signal` (wait) and
  `finish−awake` (busy) are sub-µs-to-15 µs on null sinks; they match
  pw-top's WAIT/BUSY columns at the same instant (§7).
- **`driver.status` = "finished"** for every observed completed cycle;
  follower status `"triggered"`/`"awake"` for rows still in-flight at
  emit time. `latency` `"0/0"` on the null-sink driver vs
  `"4800/48000"` on the pw-play follower (its configured latency prop).
- **`transport:"stopped"` is a trap**: the field reads `stopped` while
  the driver is actively cycling — it reports the graph transport state,
  not driver liveness. Do not gate "is it running" on it.
- **`diff`** = driver-clock drift ratio vs monotonic: exactly `1.000000`
  on virtual drivers, **1.0057 / 1.0044** on the live ALSA SPDIF domain
  (real hardware drift — observed, interpretation labeled).
- **`followerClock`** rows appear only for followers that expose clock
  info: present as a frozen all-zero template under the sibling
  `pw-loopback` follower (30 identical rows — `fclock_frozen` true,
  `position 0, next_nsec 0, diff 0.0`), **absent entirely** under a plain
  `pw-play` follower (own_driver types = {info,clock,driver,follower}
  only). Emission condition is inferred, not fully resolved.
- **`info.cpu_load0/1/2`** are NOT an ordered triple
  (`cpu_load_sorted_desc` = False on all 3 schema reps — e.g. load1
  0.000621 > load0 0.00023 ranges overlap); treat as three windowed
  averages whose exact windows are undecoded (named unknown).
- `xrun`/`xrun_count` = 0 throughout (underrun-free windows only — no
  xrun events were ever induced; semantics untested, named gap).

## 6. Refusal lattice (each ×3 fresh processes)

| probe | rc | channel | exact text / behavior |
| --- | --- | --- | --- |
| `-r r89_no_such_remote -J -n 2` | 255 | stderr | `Can't connect: Host is down` (2 ms — errno-string quirk) |
| `-r "" -J -n 2` | — | — | **connects as default remote**, then idle-hangs (15 s kill ×3) |
| `-o /proc/r89prof/x -n 2` | 255 | stderr | `Can't open file /proc/r89prof/x: No such file or directory` |
| `--r89bogus` | 255 | stderr | `unrecognized option '--r89bogus'` + full usage |
| `-J -n 2 extrapositional` | — | — | **silently ignored** → behaves as plain `-J -n 2` (hangs idle ×2; rep2 completed on a sibling driver) |
| `--version` | 0 | stdout | `pw-profiler\nCompiled with libpipewire 1.6.8\nLinked with libpipewire 1.6.8` |
| `-h` | 0 | stdout | usage text |

Contrast with r88's law: `pw-cli`/`pw-dump` report errors at rc 0;
`pw-profiler` refuses properly at rc 255 — but *only* for argument/
connection failures it detects. Semantic dead-ends (bad `-n`, empty
remote, stray positionals) are silent.

## 7. Cross-witness lattice

- **pw-top vs profiler, same instant** (3 reps, seat driver live):
  pw-top `WAIT`/`BUSY` µs columns track the profiler's `awake−signal` /
  `finish−awake` within the same few-µs band (e.g. wait 5.4 µs vs
  profiler wait_ns 5.4–7.4 µs). pw-top row shows the driver `R` with
  `2048 48000 F32P`; the follower row is prefixed `=` (`= pw-play`,
  S16LE). pw-top `-b -n 3` wall ≈ 1.003 s — consistent with r88's
  ~1 s/frame idle cadence.
- **pw-profiler's own footprint is one Client object** (`foot` legs ×2:
  census during run adds `[169, "pw-profiler", serial]` and nothing else
  — no node, no module, no link). It is the lightest observer measured
  so far; a `pw-dump` during the same window also appears as one client.
- **Module-registry mismatch:** `pactl list modules` = 17 ids (13 native
  `1,2,4,6,8,10,12,14,16,17,18,20,22` + 4 pipewire-pulse stubs
  `536870912–915`); `pw-dump` Module objects = **13**. Every
  pactl-loaded module (our `r89prof_ns`/`r89edge_*` null sinks,
  pulse ids ≥5368709xx) creates a native **Node** but **no native
  Module object** — correlate pactl module rows by sink_name/node name,
  never by expecting a pw-dump Module twin.
- **The Profiler object (id 5)** has `props={}` in pw-dump and refuses
  pw-cli introspection: `info` and `enum-params … Props` both → rc 0 +
  stderr `Error: "unsupported type PipeWire:Interface:Profiler"` (4/4).
  The profiler interface is observable only through pw-profiler itself.

## 8. Concurrency

Two simultaneous `pw-profiler -J -n 8` clients on one live driver: both
rc 0 in 0.32 s, **byte-identical stdout** (sha match, both 6462 B / both
6454 B — rep pair differ only because graph content differed between
reps), 33 records each (8 blocks ×4 + terminator). The module broadcasts
one stream; clients neither split nor serialize. A second seat can
profile the same domain without disturbing the first.

## 9. Hazards & side-effects ledger (what future authors must survive)

1. **`pactl list <kind> short` emits blank lines.** Multi-line `{args}`
   blocks leave genuinely empty rows (blank line reproduced at line 28
   of `pactl list modules short`, persistent). `line.split()[0]`
   → `IndexError`. The dead seat's probe carries this latent bug in its
   unload-verification (×2 sites): on this seat's re-run it crashed the
   `own_driver` rep0 teardown (traceback `recon/probe-all.log`), and it
   **re-hit this seat's own edge harness** once before patching —
   measured twice, independently. Parse with
   `l.split() and l.split()[0] == idx` (patched; orig preserved).
2. **Crash ⇒ leaked module.** The drv-stage crash left `r89prof_ns`
   (module 536870939, node 301 + port/link children) loaded and
   `top`/`foot` unrun; this seat unloaded it by index after verifying
   the `module-null-sink` name on the row (r90's by-name-unload
   landmine honored), then re-ran the missing stages. A second leak of
   `r89edge_a` (module id 536870939 — pulse ids recycle) from my own
   harness bug was likewise verified-unloaded; stray `pw-play` pids
   were killed. Any seat-owned teardown must survive blank-line parses
   and verify `index → module-null-sink` before unloading.
3. **Eager 0-byte `-o` files** pollute the cwd even when the run dies —
   treat existence as no evidence of content; check size/closed-`]` .
4. **`[{ } ]` is not "empty profile"** — see §2; an aborted `-J` run
   can masquerade as a valid zero-record result.
5. **No seat scoping:** `-n` counts *any* driver's cycles — a sibling's
   activity can silently complete (or stall) your leg; `extra_arg` rep2
   is the observed instance. Own-driver legs are the only controlled
   basis.
6. **`pw-play --target <name>` + `pactl` sink polling** were the
   seat's driver; `pw-play` on a 30 s WAV self-terminates but survives
   a harness crash — check `pgrep` in teardown.

## 10. Falsification list

| claim | falsifier attempted | outcome |
| --- | --- | --- |
| idle `-n` hangs because zero cycles | ran `-J -n {1,2,3,8}`, plain `-n 4`, `-n 0`, bad-`-n` variants, `-r ""`, stray positional — then same with seat driver and with 2–3 drivers | all 29 idle `-n`-gated legs hung (incl. dead seat's 3); completes iff cycles exist; completion time tracks quantum×N ÷ #drivers |
| `[{ } ]` emitted at startup | nonblocking pipe reads at 1.2 s/2.7 s idle | **falsified**: 0 B until signal; `[{ } ]` is a shutdown-flush artifact |
| `-J` writes the `-o` file too | `-o name -J` ×6 graceful stops | **falsified**: wd empty, stderr silent — `-o` fully ignored under `-J` |
| `-o` file written incrementally | SIGKILL vs SIGINT comparison | SIGKILL leaves the eager 0-byte husk; all content + aux files appear only at graceful exit |
| `info.count` = per-run sample index | sequential runs on same driver; fresh driver; two drivers | **falsified**: counter persists per driver across clients (2→31→62→91); fresh sink starts 0; per-driver interleave `[0,0,1,1]` |
| two profiler clients contend/split | concurrent `-J -n 8` | **falsified**: both complete, byte-identical streams |
| `transport` field = liveness | read it during active cycling | **falsified**: `stopped` while ticking |
| `cpu_load0≥1≥2` ordering | 90 info rows across 3 windows | **falsified**: 3/3 not sorted |
| pactl module list is line-clean | `cat -A` + `split()[0]` parse | **falsified**: persistent blank line 28 — crashed two harnesses |
| probe changed host state | module-set diff, `r89`/`r89edge` object search, pgrep, census entry↔exit | net-zero after leak cleanup (§9.2); module set identical entry/exit |

## 11. Named coverage (not measured, and why)

- **xrun/fault injection**: no underrun was ever induced; `xrun`,
  `xrun_count`, error paths and the `.log` error columns are unexercised
  semantics. Would need a deliberately starved/overloaded driver.
- **`art`/`.log` full column semantics**: col 1/3/4 named by the
  generated gnuplot titles (period, hw-delay, estimated period); the
  ~200-column follower tail is undecoded — read `Timing2..5.plot` titles
  if needed.
- **`cpu_load0/1/2` window semantics**: three values, unordered;
  window definitions not derivable from output alone.
- **`followerClock` emission condition**: present only under the
  loopback follower (frozen zero template); absent under pw-play.
  Whether it tracks real clock state on a non-idle adaptive follower is
  unmeasured.
- **`-r` to a non-default remote name that exists** (e.g. a second
  daemon): no second socket exists on this host; `-r pipewire-0`
  (canonical name) accepted — verified rc 0 with live records.
- **PipeWire-remote env vars / alternate sockets**: unprobed.
- **stdout buffering when attached to a TTY**: observed block-buffered
  to a pipe; tty behavior may differ.
- **Driver suspension mid-run**: inferred infinite stall (consistent
  with the idle law); not separately exercised.

## 12. Artifacts & provenance

`corpus/live/r89-scout/` — 419 files, ≈7.2 MB (du):

- `r89_probe.py` — dead seat's harness, **patched** at the two
  `l.split()[0]` sites (blank-line guard); original preserved at
  `recon/r89_probe.orig.py`. Stages run this seat: `all` (re-executed
  for a uniform receipt set), then `drv`, `top`, `foot` after the
  crash-fix.
- `r89_edge.py` — finisher addendum: 6 legs (e1 stream timing, e2
  SIGKILL truncation, e3 concurrent clients, e4 two-driver `-n`, e5
  named remote, e6 live `-o` artifact set), each unload-by-verified-index.
- `receipts/` — `census-entry.json`, `census-exit.json` (last stage),
  `s-mode.json`, `s-nsem.json`, `s-sig.json`, `s-refuse.json`,
  `s-schema.json`, `s-profobj.json`, `s-own-driver.json`,
  `s-top-xw.json`, `s-footprint.json`, `s-edge.json`.
- `runs/` — 28 leg dirs / 76 run_leg receipts (cmd.txt + stdout.bin +
  stderr.txt + meta.json; artifact legs keep `wd/` verbatim).
- `runs_edge/` — 6 leg dirs / 11 metas (e3 keeps dual stdout captures;
  e6 keeps both wd variants).
- `recon/` — `recon-notes.md` (dead-seat forensics + pre-run
  verification), `dead-seat-snapshot/` (verbatim pre-finisher runs +
  census), `probe-{all,drv,top,foot}.log`, `r89_probe.orig.py`.
- `raw/` — `manual-j-live-n4.json` (first live `-J` proof),
  `manual-plain-eager-empty`, `r89_{out,err}.txt` (channel split).
- `r89_tone.wav` — 30 s 1 kHz stereo 48 kHz sine, generated to the
  probe's own spec (used by drv/top/edge driver legs).

**Stability.** Idle-hang legs are deterministic (15/15 timeout-kill,
zero output); refusal texts byte-identical ×3; stream-content legs vary
in timestamps only (record *shape* stable; `extra_arg` rep2 is the
named contention exception, §13).

**Confidence.** High: the `-n` gating law (15 idle hangs + 6 live
completions across 1–3 drivers), `-J` stream/flush/truncation behavior
(timed pipe reads ×4 contexts), `-o` eager/exit-write asymmetry (9
timeout + 3 graceful + 2 live-artifact), `-n` no-validation (9/9),
refusal lattice (21 legs), concurrent broadcast (2 reps byte-identical),
module-registry mismatch (3 censuses), per-driver `count` semantics
(3 runs + e4 interleave). Medium: `diff`=clock-drift interpretation;
`followerClock` emission condition; `cpu_load` window semantics;
blank-line persistence across hosts (measured stable within this host).

## 13. Contention ledger & host-state verification

| window | contact | effect |
| --- | --- | --- |
| schema_n30 + extra_arg rep2 | sibling driver `r80md_1212874_lnk_a`/`lnk_b` (pw-loopback pair, r80 seat) | supplied the cycles that completed those legs — named driver in §5 data |
| e4 rep2, e5 | live ALSA domain `alsa_output.usb-…SPDIF__sink` (id 46, `api.alsa.p-0`) | third driver in the two-driver leg; real-hw `diff` 1.0057 evidence |
| own_driver/top reps | sibling sinks `r79lb_ns_*` in census | suspended; no interaction |
| 12:34–13:09 | this seat: ~90 probe subprocesses (76 run_leg + edge + manual) + census/pactl probes + ~18 module-null-sink load/unload cycles (`r89prof_ns`, `r89edge_{a,b}`) + pw-play/pw-top | all unloaded by verified index; **two transient leaks** (§9.2) cleaned same-session |
| ~12:5x | drv-stage crash leak: `r89prof_ns` module 536870939 + node 301 (+ port/link children); later `r89edge_a` reusing id 536870939 | both unloaded by verified index; zero residue at exit |

**Exit state (verified after last leg):** `pw-dump` = 76 objects, zero
`r89`/`r89edge` residue in any object JSON; `pactl list modules` =
baseline `1,2,4,6,8,10,12,14,16,17,18,20,22,536870912–915`; zero
`r89*` sinks; no stray `pw-profiler`/`pw-play`/`pw-top` processes; no
files written outside `corpus/live/r89-scout/` (+ this report); tracked
dirty set unchanged (`SHONEN.md`, `measure_audio.py`, pycache —
sibling-owned, untouched).
