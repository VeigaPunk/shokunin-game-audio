# R89 boundary — falsification of the r89 scout under load

**Seat: BOUNDARY (executor-class, leaf).** Host `plazir27`, lane
`~/Projects/shokunin/audio-shokunin` @ HEAD **`1abd9549`** (the scout measured
`ee6d684`; the tree moved on — no file this seat touched is tracked). Window
**2026-10-15 17:04–17:20 UTC−3** (20:04–20:20Z). Toolchain re-verified:
`pw-profiler` Compiled/Linked libpipewire **1.6.8**, pactl 17.0-98-gb096,
pw-top 1.6.8, Python 3.14.7, 32 cores. Resident profiler module id **4**
(args still `{ #profile.interval.ms = 0 }`), Profiler object id **5**.

**Zero tracked-file edits, no commits, no `set-default-*`.** Every write is
under `corpus/live/r89-boundary/` (harness `r89b_probe.py`, `r89b_adhoc*.py`,
`receipts/*.json`, `runs/**`, `raw/manual-idle/`) plus this report. Every
audio object created is named **`r89b_*`** (`r89b_ns`, `r89b_ns44`,
`r89b_ns_b`); every unload is index-verified against its own
`sink_name=r89b_*` line immediately before the call. **Exit state:** 3/3
modules unloaded by verified index, `pw-dump` → zero `r89b_*` nodes, zero
stray `pw-play`/`pw-profiler`, my 64 hogs killed (pidfile, `comm` checked),
tracked dirty set = `corpus/fixtures/measure_audio.py` only (sibling-owned,
never touched — the sibling pycache entry that was dirty at entry flipped
clean during the window without my involvement; my harness never imports it).
Receipts: `receipts/cleanup.json`.

**Labrat.** The single permitted `probeParent` labrat was dispatched once
(read-only static audit, no PipeWire, no writes). It returned
**CONFIRMED ×3** on the scout's preserved artifacts: (a) both concurrent
`e3` stdout pairs byte-identical (6462 B sha `d8e32fe3…`, 6454 B sha
`0a2f37ab…`, 33 recs); (b) `e2` SIGKILL stdout 20480 B, rc −9, ends
mid-token (`…"dela`), `json.loads` impossible; (c) `sig_int_j` ×3 stdout
exactly `[{ } ]\n` (7 B, sha `395c1472…`). Every measurement below is
seat-owned; the labrat's substrate had no exec, so it quoted artifact
metadata + full reads.

---

## 0. Verdict table

| # | r89 scout claim | verdict | sharpest measured fact |
| --- | --- | --- | --- |
| 1 | idle `-n N>0` hangs; wall = N ÷ Σ driver rates; no seat scoping | **CONFIRMED (mechanism) — idle branch reproduced only in one window** | idle window 17:04–17:05: `-n 1` hung 2.5 s ×4 with only the 7 B `[{ } ]\n` SIGTERM flush and **pw-top all `I`/`S`, zero `R` rows**; 17:07+ every leg completed on sibling drivers in **10–88 ms**; `-n 40` = **0.285 s** vs predicted 0.284 s (SPDIF 512/48 k ≈ 94 rec/s + two 2048/48 k sinks ≈ 23.4 rec/s each); under 32 hogs `-n 40` = **0.285/0.296 s (unchanged)** |
| 2 | `-J` streams live in ~4 KiB blocks; SIGINT/SIGTERM → rc 0 flush; SIGKILL truncates; `-o` ignored | **CONFIRMED + 4 refinements** | block boundaries are exact **4096 B multiples** (49 152 @0.25 s, 94 208 @0.5 s, …); **graceful stop deadlocks on a full undrained pipe** (`state S`, `wchan anon_pipe_write`, `exited_before_drain=False`; rc 0 + valid JSON only **after** the reader drains); signal class is **exactly {SIGINT, SIGTERM}** — HUP rc −1, QUIT rc −3, USR1 rc −10, USR2 rc −12, all truncated invalid JSON; `-o` under `-J` → wd `{}`, stderr 0 B ×3 |
| 3 | `-o` creates 0-byte file eagerly, ALL content at exit, aux set on graceful exit | **PARTLY FALSIFIED** | eager ✓ but with live data the file is **4096 B at 150 ms**; **SIGKILL at 1.5 s leaves 36 864 B / 33 rows** and stderr already carries `logging 24 samples 0 seconds [CPU …]` — content is flushed incrementally and that message is periodic, not shutdown-only; graceful aux set (Timing1–5.plot + Timings.html 1087 B + generate_timings.sh 105 B) reproduced; existing file is **truncated** (marker gone); default `profiler.log` ✓; `Logging to` on stderr ✓ |
| 4 | `-n` is atoi with zero validation (`2.5`→2, overflow→truncation) | **MECHANISM FALSIFIED, outcome kept** | on a live driver: `007`→7, `+3`→3, `" 3"`→3 (exact completions); **`2.5`, `3abc`, `1e1`, `4294967298`, `-4294967294`, `4294967296`, `1e20`, `-1e20` all ran unbounded** (killed at 3 s with ≥64 KiB streamed) — i.e. full-string validation, no int truncation; `-1`/`abc`/`0` unbounded ✓; **no error output ever** ✓ |
| 5 | `info.count` persists per driver across clients; position += duration; `next_nsec−nsec` = duration/rate exactly; `diff` exactly 1.000000 on virtual | **CONFIRMED + 2 FALSIFIED + 1 sharpened** | count: Midi-Bridge 0–9 → 10–19 → 20–24 → 25–30 (+1 across 1.5 s detach gaps ≈ 35 cycles), fresh sink starts 0; **`position += duration` has a real counterexample** (r93s_in delta 1024 vs duration 2048 — a quantum transition; r82ff_ns showed 512→2048 in one window); **nsec deltas deviate in 59/180 blocks** (33 ns for 1024/48 k, 8.7 µs for 2048/48 k, 230 µs under load); **virtual `diff` is not always exactly 1.0** (1.000001–1.000291; Midi-Bridge 1.000001–1.000007) |
| 6 | `prev≤signal≤awake≤finish`; count +1/cycle; transport `stopped`; xrun = 0 throughout | **CONFIRMED except xrun** | order violations 0 / count-step violations 0 / transport `stopped` 0-exceptions across 450 blocks; seat's own two drivers: **134 blocks, 0 violations of every invariant under loadavg 146**; **xrun ≠ 0**: SPDIF `clock.xrun` = **937** (cumulative, frozen all session) + driver-row `xrun_count` = 1; the scout's own raw data is 698× `"xrun": 0` / 1207× `"xrun_count": 0` → host-state variation |
| 7 | refusals rc 255 (remote/out/opt), `-r ""` = default, extra positionals ignored | **CONFIRMED + 1 new law** | rc 255 ×3 each with byte-identical texts; `-r ""`/extra positional completed rc 0 on a live graph; **`PIPEWIRE_REMOTE` env is honored** — `PIPEWIRE_REMOTE=r89b_bogus_env` → rc 255 `Can't connect: Host is down` ×2 (the scout's named env gap, closed) |
| 8 | profiler footprint = 1 Client; pw-top WAIT/BUSY ≈ awake−signal / finish−awake; Profiler object refuses introspection | **CONFIRMED** | census during a run: exactly **1** `pw-profiler` client, 0 nodes, 0 modules added; pw-top frame 3 row `R 239 2048 48000 6.0us 26.3us` vs profiler block `awake−signal 6.02 µs`, `finish−awake 26.3 µs` — **exact match under loadavg 148**; `pw-cli info 5` / `enum-params 5 Props` → rc 0 + `unsupported type PipeWire:Interface:Profiler` ×2 |
| 9 | two concurrent `-J -n 8` produce byte-identical stdout | **FALSIFIED as stated (record-level law survives)** | 3/3 simultaneous pairs **differ** (6545/6543, 6583/6541, 6537/6499 B) from the first `count` onward; overlapping (driver,count) blocks are **dict-identical and nsec-identical** (7/7, 4/4, 7/7; `nsec_diff` 0) — the module broadcasts one stream, but each client's *window* depends on attach phase; byte-identity is a low-rate-graph artifact |
| 10 | `pactl list … short` blank lines crash naïve parsers | **CONFIRMED + localized** | blank line at **line 28 of `modules` only**; `cards`, `sinks`, `sources`, `clients`, `samples` short output is line-clean in the same census |
| 11 | *(not claimed)* xruns / small quanta | **NEW, mostly negative** | `PIPEWIRE_QUANTUM=64/32/128` is **ignored** (quanta seen only 1024/2048 in all four legs); virtual null-sink drivers produced **no xruns at loadavg 112–121**; the only nonzero counters are the real ALSA SPDIF domain's (937/1, frozen) |
| 12 | *(not claimed)* shutdown under backpressure | **NEW HAZARD** | with a full, undrained stdout pipe, SIGINT/SIGTERM **do not terminate** — the process sits `S` in `anon_pipe_write`; draining completes the flush → rc 0 valid JSON (261 904 B); SIGKILL at the pipe boundary truncates at **exactly 65 536/69 632 B**; a closed reader → **SIGPIPE death rc −13**; stdout to `/dev/full` → **silent** (rc 0, 0 B stderr) |

---

## 1. The gating law, both branches (`receipts/idle.json`, `idlewatch.json`,
`driver.json`, `load.json`, `raw/manual-idle/`)

**Idle branch (17:04–17:05).** Four fresh `pw-profiler -J -n 1` processes each
survived 2.5 s with no records; SIGTERM (via `timeout`) flushed exactly
`[{ } ]\n` — 7 B, sha `395c14721d7fb39b…` ×4 (the **same sha the scout's own
`sig_int_j` artifacts carry**, independently confirming the flush bytes). A
concurrent `pw-top -b -n 2` during the 4th hang shows **no `R` row** (all
`I`/`S`, `---` WAIT/BUSY) — the cross-witness that the graph was truly
cycle-free. This is the *only* idle window in the session: `idlewatch` then
polled 90 × `-n 1` (1 s bound) from 17:15:50 to 17:16:11 and **all 90
completed** (drivers `SPDIF, r87b_ns, r89b_ns, r89b_ns44, r90b_ra, r90b_rc,
r96s_ns, r98s_ns`), so the idle branch was not re-catchable later.

**Live branch (17:07+).** Every `-n` leg completed, and completion tracked
the summed driver rates: `-n 8` 61–67 ms, `-n 40` 285/290 ms (predicted
0.284 s), `-n 90` 973–980 ms, `-n 120` 0.88–1.10 s. Two seat sinks + SPDIF
gave the scout's `two-driver` effect: `-n 4` in **40 ms**. Under my 32 hogs
(plus 32 foreign `yes` already running; loadavg 74 → 93) `-n 40` was
**0.285/0.296 s — indistinguishable from quiet**. The no-seat-scoping law is
loudest in the `idle` stage: legs launched as "idle replays" were completed
in 10–88 ms by sibling driver `r82ff_ns_2422178` (§9).

**Suspension (clean, `receipts/adhoc2.json`).** With all seat players killed
first, one player on `r89b_ns` was SIGKILLed at t=1.0 s of a 3 s `-n 0` run:
`r89b_ns` contributed **24 blocks, count span 23** (≈1 s at 2048/48 k) while
**154 blocks from r93s_in/r96s_ns/r98s_ns** kept the run alive for the other
two seconds. A sink with **zero** followers (`r89b_ns_b`, SUSPENDED)
contributed **0 blocks** in the same windows. So: per-driver records stop
when that driver suspends; the leg stalls iff **no** driver cycles (the idle
branch). The scout's labeled inference is now measured, with that caveat.

**Disclosed confound.** My first suspension probe (`adhoc.json`) was
confounded by a stale seat player from the schema2 stage (90 s tone still
alive); its "span 69" is void and was redone cleanly above.

## 2. `-n` parsing — the atoi reading is falsified (`driver.json`)

All legs run on a live graph (so completion vs unbounded is measurable,
which the scout's idle legs could not do):

| arg | measured | scout's inference |
| --- | --- | --- |
| `007` | rc 0, **7** blocks in 0.072–0.075 s | (untested) |
| `+3` | rc 0, **3** blocks | (untested) |
| `" 3"` | rc 0, **3** blocks | (untested) |
| `2.5` | **unbounded** (killed 3 s, 65 536 B) | "atoi → 2; needs 2 cycles" |
| `3abc`, `1e1` | **unbounded** | (untested) |
| `4294967298`, `-4294967294`, `4294967296`, `1e20`, `-1e20` | **unbounded** | "silently accepted" (implied int) |
| `-1`, `abc`, `0` | unbounded (SIGINT at 2.5 s, still streaming) | unbounded ✓ |

A consistent model: `strtol` + **full-string validation** (`*end != '\0'` →
reject), non-positive/overflow → treated as 0 = unbounded, no error text. The
scout's *outcome* ("no CLI validation, no error") stands; its *mechanism*
("atoi", "2.5 → 2") does not. Repeated options: `-n 4 -n 0` → last wins
(unbounded); `-J -J` harmless.

## 3. `-J` stream, signals, backpressure, write errors (`jsig.json`, `bp.json`)

- **Streaming granularity**: exact multiples of 4096 B (49 152 @0.25 s,
  94 208 @0.5 s, 139 264 @0.75 s, 188 416 @1.0 s, …), first byte at 0.02 s —
  the `[` is lazy with the first record. Confirms the scout's block-buffer
  claim and pins the block size.
- **Graceful class = {INT, TERM}** with a draining reader: rc 0, 851–1697
  records, complete `…, { } ]` array ×6. With an **undrained** pipe: SIGINT
  and SIGTERM **do not exit** — state `S`, wchan `anon_pipe_write`,
  `exited_before_drain=False`; after draining, rc 0 and a valid array
  (261 904 / 189 803 B). This is the correct reading of the scout's
  "SIGINT → rc 0": it is conditional on the consumer draining.
- **Unhandled signals**: HUP rc −1 (348 160 B streamed), QUIT rc −3, USR1
  rc −10, USR2 rc −12 — all truncated invalid JSON, no flush.
- **SIGKILL**: rc −9, truncated at the pipe capacity (65 536/69 632 B),
  invalid JSON ×3 ✓.
- **Closed reader**: rc −13 (SIGPIPE), no handler.
- **`/dev/full` stdout**: rc 0, 0 B stderr — write errors silently ignored.
- **TTY** (scout's named gap): rc 0, 432 022 B, first byte at 0.01 s, stream
  shows **CRLF** line endings (kernel ONLCR) — the tty path is not
  block-quantized like the pipe.
- **`-o` ignored under `-J`**: wd `{}`, stderr 0 B ×3 ✓.

## 4. `-o` artifact mode — incremental, not exit-only (`oart.json`, `adhoc.json`)

| leg | result |
| --- | --- |
| `-o o_art -n 20` (graceful) | `o_art` **21 587 B / 20 rows**, aux set present, stdout 64 B, stderr `Logging to o_art` + `dumping scripts for 1 followers` |
| `-o o_int -n 0` + INT/TERM | rc 0, `o_int` 51 794–101 475 B, stderr `logging 24/47 samples  0 seconds [CPU …]`, aux set ×4 |
| `-o o_kill -n 0` + SIGKILL @1.5 s | **rc −9 but `o_kill` = 36 864 B / 33 rows**, stderr already had `logging 24 samples …` **before** the kill |
| `-o eager_x -n 0`, live | file exists at 150 ms with **4096 B** (final 46 536 B) — eager creation confirmed, "0-byte" is the idle/no-sample case |
| `-o o_exist` over a pre-written MARKER file | rc 0, **marker gone** (truncate), 10 rows; wall 4.508 s in a near-idle window (`logging 2 samples`) |
| `-o .` | rc 255 `Can't open file .: Is a directory` |
| `-o ""` | rc 255 `Can't open file : No such file or directory` (empty ≠ default) |
| `-o /dev/null` | rc 0, aux set still written to cwd |
| `-o /dev/stdout` | rc 0, the columnar dump appears **on stdout** (10 855 B) + aux set |
| `-o -` | rc 0, creates a file literally named `-` (10 790 B) |
| `-o /proc/r89b/x` | rc 255 `Can't open file /proc/r89b/x: No such file or directory` ×3 |
| default name | `profiler.log` created (11 020 B) ✓ |

So: created eagerly, **written incrementally** (SIGKILL content + periodic
`logging N samples`), aux set iff samples exist, truncating open, and the
write-error lattice extends to directories/empty/`/dev/stdout`/`-`.

## 5. Schema, counts, invariants, xrun (`schema.json`, `schema2.json`, `xrun.json`)

- **Count semantics (sharpened).** Across three sequential `-n 30` legs on
  the live seat driver: `r89b_ns` 1494–1498 | 1499–1503 | 1504–1506 — **+1
  across each 1.5 s detach gap** (≈35 driver cycles), so the per-driver
  counter is frozen while no client is attached. Midi-Bridge ran the same
  pattern 0–9 | 10–19 | 20–24 | 25–30 across four legs including a fresh
  sink's creation; a **fresh sink starts at 0** (0,1,2 ×1). The scout's
  persistence law confirmed; the freeze-while-detached mechanism is new.
- **Invariants, 450 blocks** (3×`-n 60` + 3×`-n 90`): order violations **0**,
  count-step violations **0**, transport `stopped` exceptions **0**;
  `position += duration` **1 counterexample** (r93s_in delta 1024 vs
  duration 2048 — the same window shows that driver changing quantum
  1024→2048); `next_nsec − nsec` deviations in **59/180** blocks
  (33 ns @1024/48 k, 8.7 µs @2048/48 k, and **230 µs** in a hogged leg);
  `diff` on virtual drivers 1.0 plus 1.000001–1.000291 (Midi-Bridge), SPDIF
  0.999048–1.000347; **seat's own 134 blocks: zero violations, diff exactly
  1.0, under loadavg 146**.
- **xrun.** SPDIF `clock.xrun` = **937 constant** across every window
  (driver/schema/load/xrun stages, ~1 h) and `xrun_count` = 1 on its driver
  rows — a cumulative pair, **not** the "0 throughout" the scout reported
  (their own raws: all zeros). Virtual drivers stayed 0 even at loadavg 112.
- **cpu_load0/1/2**: sorted-desc in 86 blocks, unsorted in 94 — unordered
  noise, not a triple (scout's "not sorted 3/3" confirmed on a larger sample).
- **followerClock**: 0 rows in every window this seat captured (450+ blocks);
  the emission condition remains unresolved.

## 6. Concurrency (`jsig.json` conc legs, `load.json`)

Three simultaneous `-J -n 8` pairs: **none byte-identical** (6545 vs 6543,
6583 vs 6541, 6537 vs 6499 B); `cmp` first difference at byte 29 — the first
`info.count`. Overlapping (driver,count) blocks: 7/7, 4/4, 7/7 **dict-equal
with identical nsec**. Staggered pairs (0.4 s) share **zero** blocks because
`-n 8` completes in ~60 ms at this graph rate. So the module's one-stream
broadcast law holds per cycle; the scout's byte-identity was a property of
their low-rate window, not a law. Under hogs: same non-identity (6/6 and
7/7 overlapping blocks equal).

## 7. Cross-witness, footprint, registry (`adhoc.json`, `adhoc2.json`, `state.json`)

- pw-top frame 3 for `r89b_ns44`: `R 239 2048 48000 6.0us 26.3us`; the
  profiler's first block for the same driver: `awake−signal 6.02 µs`,
  `finish−awake 26.3 µs` — **exact agreement** at loadavg 148. (Frames 1–2
  were `C`/`0.0us ???` — the r88 refresh trap again.)
- Footprint during a run: 25 clients total, exactly **1** `pw-profiler`, no
  node, no module added (13 modules before and during).
- `pactl list modules` = 21–25 ids (sibling churn) vs `pw-dump` Module
  objects = **13** — the registry mismatch stands; my own three pulse-loaded
  sinks created Nodes but no native Module objects, unloaded by index anyway.
- Profiler object 5 refuses `pw-cli info`/`enum-params` (rc 0 + unsupported
  type) ×2.

## 8. Hazards ledger (for future authors)

1. **Never capture `-J` stdout without draining.** A full pipe turns a
   graceful SIGINT/SIGTERM into a `anon_pipe_write` stall; SIGKILL then cuts
   the JSON at exactly the pipe capacity (65 536/69 632 B). This bit my own
   harness on `j_n0_int` (idle stage), the unbounded `badn_*` legs, the
   first `load` xrun attempts and the first `schema2` run — all
   classifications above are drawn from drained runs or from record volumes
   far exceeding `n`.
2. **A closed reader is SIGPIPE (rc −13), a full device is silent** (rc 0) —
   two different write-error fates.
3. **Only INT/TERM flush.** HUP/QUIT/USR1/USR2 truncate.
4. **`-o` files are not empty husks when data exists** — SIGKILL left 36 KiB;
   check size, not existence, and expect truncation of any pre-existing file.
5. **`pactl list modules short` blank line 28** (multi-line `{args}` blocks);
   the other `short` kinds are clean in this census. Parse with
   `l.split() and …`.
6. **No seat scoping.** Your `-n` leg completes on any sibling driver, and
   your hogs starve theirs. Kill only PIDs you own (`comm`-checked pidfiles),
   unload only indices whose own line matches your `sink_name=`.
7. **Quantum can change mid-window** (512→2048 on one driver) — a
   `position += duration` arm must allow one step at the previous quantum.
8. **The `[{ } ]` trap** (idle flush) is real and reproducible to the byte
   (`sha 395c1472…`); wall time / driver liveness is the only discriminator.

## 9. Contention ledger (by name) & host-state variation

| window | contact | effect |
| --- | --- | --- |
| 17:04–17:05 | (no live driver; pw-top all `I`/`S`) | the only true idle evidence |
| 17:07:56–17:08:58 | **r82ff_ns_2422178** (r82 seat), then **r93s_in** | completed every "idle replay" leg in 10–88 ms |
| 17:09:53+ | **alsa_output…SPDIF__sink** (real ALSA, cycle 179 829), **r87b_ns** | `diff` 0.999923, quantum 512; extra `-n` records |
| 17:11–17:13 | **r82ff_ns_2737990** (new instance), **Midi-Bridge**, **r93s_in**, **r96s_ns** | count-persistence witnesses; SPDIF xrun counter 937 |
| 17:13:39 (load) | **r96s_ns, r86b_ns, r87b_ns, r87b_ns2**; 32 foreign `yes` + my 32 | loadavg 74→93; timing unchanged |
| 17:14:46 (schema2) | **r90b_ra, r87b_ns**, SPDIF | loadavg 136–146; 134 own blocks clean |
| 17:15:50–17:16:11 | r87b_ns, r90b_ra, r90b_rc, r96s_ns, r98s_ns, SPDIF | idlewatch 90/90 completed — no idle window |
| 17:16 (adhoc) | r93s_in, r96s_ns, r98s_ns | suspension leg continued on these |

Host-state variation vs the scout's window: HEAD moved `ee6d684`→`1abd9549`;
pactl module ids 17→21–25; sibling drivers live throughout (the scout's
r79lb/r80 drivers were suspended then; `r79lb_fc_2224500` + its
`mix_output/mix_input.r79fc_2224500_live` followers supplied my first
out-of-harness cycle, then vanished); the SPDIF xrun counter is nonzero now
and was zero in all 698/1207 scout samples; loadavg 60–149 throughout.
This seat added: 3 null sinks, 5 `pw-play` players (2 stale ones disclosed
and cleaned), 32 hogs per load/xrun stage (killed; pidfile + `comm` check).

## 10. Remaining unknowns (honest edges)

- **`followerClock` emission condition** — never observed (0 rows in 450+
  blocks); the scout's frozen-template sighting is not reproducible here.
- **xrun semantics** — `clock.xrun` (cumulative 937) and `xrun_count` (1)
  stayed frozen for an hour of loadavg 60–149; no virtual-driver xrun was
  ever induced and `PIPEWIRE_QUANTUM` is not a route to small quanta.
- **`logging N samples` accounting** — 24 samples vs 33 rows vs 2 samples vs
  10 rows do not reconcile; flush granularity of the artifact file is
  incremental but its unit is unread.
- **`cpu_load0/1/2` windows** — still unordered (86/94 split).
- **Idle branch** is currently unreachable (sibling churn); the 17:04–17:05
  window is the only live reproduction this seat obtained.
- **The tracked pycache flip** (`corpus/fixtures/__pycache__/…pyc` went clean
  without my involvement) — sibling-owned, disclosed, not investigated.

## 11. Artifacts & receipts

Harness: `r89b_probe.py` (stages `state idle driver schema jsig oart load
bp idlewatch schema2 xrun cleanup`), `r89b_adhoc.py`, `r89b_adhoc2.py`;
tone anchors `r89b_tone48.wav`, `r89b_tone44.wav`; manual idle captures in
`raw/manual-idle/`.

| receipt | sha256 (prefix) | bytes |
| --- | --- | --- |
| `state.json` | `5cbc1b8db27cb6e8` | 17 103 |
| `idle.json` | `da7cb06fba0c60d5` | 81 396 |
| `driver.json` | `c46740a95c86f07b` | 57 297 |
| `schema.json` | `1372b93e0bbf3177` | 54 277 |
| `jsig.json` | `df885181f96392c5` | 297 211 |
| `oart.json` | `bb6035af74d77e98` | 21 899 |
| `load.json` | `ffe52e42fc110b8b` | 64 436 |
| `bp.json` | `654d40e3ca12133b` | 6 813 |
| `idlewatch.json` | `3944af21316365a8` | 11 136 |
| `schema2.json` | `ff54ee45cb2b9973` | 28 618 |
| `xrun.json` | `69c44a9146a433e0` | 107 544 |
| `adhoc.json` / `adhoc2.json` | `f13f8eebe73e9f69` / `b6dec949ed6c7c5b` | 1 254 / 1 830 |
| `cleanup.json` | `d178163bc56d7108` | 34 408 |

**Verdicts here are seat-side falsification attempts; the canonical Rust
runtime remains the only judge.**
