# r89 author — the pw-profiler output lattice

Implementation of the round-89 move: an insertion-only `pwprof` family in
`corpus/fixtures/measure_audio.py` (appended after the r88 block, before
`def main()`), wired as `--probe-pwprof-r89`. Four entries, 47 legs total.
Every armed law is a boundary-surviving claim; the scout's falsified claims
are dropped or re-armed at the boundary's corrected values.

## Files changed

- `corpus/fixtures/measure_audio.py` — +1561/−3 (the only deletions are the
  three shared-line splices the wiring requires: mutex list, mode select,
  receipt suffix; identical convention to r86–r88).
- `corpus/live/measure_audio-pwprof-r89.lock` — fixed-path family lock
  created at runtime (untracked, same convention as the r86–r88 locks).
- `corpus/live/runs/20261016T074733533774Z-pwprof-r89/` — green receipt #1.
- `corpus/live/runs/20261016T074816877001Z-pwprof-r89/` — green receipt #2.
- `reports/round-89/r89-author.md` — this file.

Nothing committed.

## Conventions carried over

- Namespace `r89a_<pid>` (`r89a_ns_`, `r89a_ns2_`, `r89a_nsb_`, `r89a_*_pl`),
  private role key `r89arole<pid>` on every pw-play follower.
- Fixed-path lock `corpus/live/measure_audio-pwprof-r89.lock` (flock, never
  `$TMPDIR`); `TMPDIR=~/Projects/shokunin/tmp` for all runs.
- Name-verified teardown: re-read `pactl list modules` immediately before
  firing, unload only the index whose args carry our `sink_name=`; residual
  `r89a_<pid>` nodes destroyed by id via `pw-cli destroy`; final sink/node
  census armed (`sinks_gone`, `own_nodes_after`).
- Never `set-default-*`; every spawned process is its own session leader,
  bounded by SIGTERM→SIGKILL process-group escalation.
- Volatile ids/nsec scrubbed in recorded text; `-J` legs keep a
  `stdout_raw` verbatim channel for parsing (recorded, never armed).
- r89-local error classes checked before the inherited tables:
  `pwprof_connect_down` (`Can't connect … Host is down`),
  `pwprof_cant_open` (`Can't open file …`), `pwprof_opt`
  (`unrecognized option '…'`).

## The one harness law the boundary added

`_pwprof_r89_stream` is the only spawn path for `pw-profiler`: **stdout is
continuously drained by nonblocking `os.read` for the whole run** — the
boundary's backpressure law says a full undrained pipe turns a graceful
INT/TERM into an `anon_pipe_write` stall, so `communicate()` alone cannot
host the signal legs. The same loop timestamps `watch` paths (the `-o`
eager-creation arm), samples cumulative drained bytes (the exact-4096 B
block law), fires `sig` at `sig_at` recording `alive_at_sig` (the
unbounded-class witness), and runs `hooks` inside the loop (the suspension
leg kills its own follower mid-stream).

## Entries and legs

### 1. `pwprof_gate_r89_probe` — gating + stream + parse + refusal (27 legs)

- `g_link`: seat pw-play (`r89a_<pid>_pl`, role `r89arole<pid>`) links into
  `r89a_ns_<pid>` before any `-n` leg runs — a null-sink driver cycles only
  while a follower is attached, so a dead player silently turns every `-n`
  leg into an idle-graph hang.
- `g_own` (`-n 8`): rc 0, exactly 8 `info` records, `…, { } ]` terminator.
- `g_two` (`-n 4`, two cycling seat sinks): completes in 0.071 s with the
  info budget **summed across drivers** — measured
  `{'r89a_ns2_…': 2, 'r89a_ns_…': 2}`; the exact-N law is per-run, not
  per-driver.
- `g_term`/`g_int`: SIGTERM/SIGINT at 1 s → rc 0, 47 infos, clean
  `{ } ]` close (the graceful class).
- `g_kill`/`g_hup`/`g_usr1`: rc −9/−1/−10, JSON unparseable — the
  truncating class; only INT/TERM flush.
- `g_blocks`: stdout arrives in exact multiples of 4096 B
  (8192→20480→32768 at 0.3/0.6/0.9 s).
- `g_o_ignored`: `-o <path>` under `-J` creates nothing and logs nothing —
  `-o` is fully ignored in JSON mode.
- `g_extra`: a stray positional is silently ignored (rc 0, 4 infos).
- `g_remote_empty`: `-r ""` is the default remote (rc 0, 4 infos).
- `g_remote_bogus`/`g_env_bogus`: bad `-r` name and bad `PIPEWIRE_REMOTE`
  both refuse rc 255 `Can't connect … Host is down` — the env is honored
  (the scout's named gap, closed by the boundary).
- `g_opt_bogus`: `--r89bogus` → rc 255 `unrecognized option`.
- `g_version`: rc 0, `libpipewire` in stdout.
- `g_lastwins` (`-n 4 -n 0`): last `-n` wins → unbounded; still alive at
  1.4 s, 66 infos, TERM-flushed rc 0.
- The `-n` parser lattice (the boundary's strtol+full-string law, NOT the
  scout's atoi):
  - `n_007`→7, `n_plus3`→3, `n_space3`(`" 3"`)→3 — all parse and complete
    rc 0 before the 2.5 s bound.
  - `n_2_5`, `n_3abc`, `n_1e1`, `n_huge`(4294967298), `n_neg`(`-1`),
    `n_abc`, `n_zero` — all **unbounded**: alive at the 1.4 s SIGTERM with
    65–66 infos, then rc 0. The seat driver demonstrably cycled while the
    run never stopped.

### 2. `pwprof_oart_r89_probe` — the `-o` artifact lattice (12 legs)

- `o_live` (`-o art -n 10`): rc 0, exactly **10 data rows**, the full aux
  set `Timing1–5.plot` + `Timings.html` + `generate_timings.sh`,
  `Logging to` on stderr, `generate_timings` mentioned.
- `o_int` (`-o i -n 0` + TERM): rc 0, 32347 B — graceful writes are real.
- `o_kill` (`-o k -n 0` + SIGKILL @2 s): rc −9 **with 49152 B / 46 rows** —
  the boundary's falsification of the scout's "0-byte husk" claim; content
  is flushed incrementally (4096 B blocks, matching the stderr
  `logging N samples` cadence).
- `o_exist`: a pre-written MARKER file is truncated on open (marker gone).
- `o_eager`: the output path exists at t=0.010 s inside a running `-n 0`
  run — eager creation confirmed.
- `o_default`: plain `pw-profiler -n 4` (no `-o`) writes `profiler.log`
  (4320 B) — the default artifact name. (`-o` REQUIRES its filename on the
  next argv: `-o -n 4` eats `-n` as the filename and the run goes
  unbounded — measured in dev, documented in the leg comment.)
- `o_dash`: `-o -` creates a literal file named `-` (6468 B), not stdout.
- `o_devnull`: `-o /dev/null` rc 0 and the aux set still lands in cwd.
- `o_dir`/`o_empty`/`o_proc`: `-o .`, `-o ""`, `-o /proc/r89a_<pid>/x`
  all refuse rc 255 `Can't open file …` before connecting.

### 3. `pwprof_schema_r89_probe` — own-driver schema invariants (4 legs)

- `s_window` (`-n 40` raw window on `r89a_ns_<pid>`): 40 own blocks,
  every armed invariant green —
  - block order `info→clock→driver→follower` on all 40;
  - `info.count` steps exactly +1/cycle;
  - `position += duration` each cycle;
  - `next_nsec − nsec == duration/rate` exactly (2048/48000);
  - `transport == "stopped"` on every clock row while cycling — the
    liveness trap;
  - `diff == 1.0` on the virtual driver;
  - `prev ≤ signal ≤ awake ≤ finish` on every driver+follower row;
  - `prev[k+1] == signal[k]` — the prev chain;
  - driver `status == "finished"`, driver `latency == "0/0"`;
  - clock/driver `id` == the seat node's object.id; clock name
    `clock.system.monotonic`;
  - clock `nsec` inside the host monotonic window ±5 s;
  - `xrun == 0`, `xrun_count == 0` on all rows;
  - zero `followerClock` rows (pw-play followers emit none);
  - `nsb_blocks == 0` — the loaded-but-follower-less `r89a_nsb_<pid>` sink
    emitted zero blocks (suspension law, static half).
- `s_second` (`-n 10` second window): first own count continues past the
  last own count of window 1 — per-driver counts persist across detach.
- `s_suspend` (`-n 0` unbounded + in-loop hook): pw-play SIGKILLed at
  0.9 s mid-stream → **21 own blocks before, 0 after** (600 ms margin) —
  the per-driver suspension law measured live: kill the follower, the own
  driver stops emitting while the profiler run itself stays alive until
  TERM'd at 2.4 s.

### 4. `pwprof_xw_r89_probe` — the cross-witness lattice (8 legs)

- `x_modreg`: `pactl load-module` added index 536870922 in the pactl table
  **and** created a Node in pw-dump — but the native `Module` object list
  (13 objects) does NOT contain it; the pactl-vs-native registry mismatch
  is real.
- `x_blank`: `pactl list modules short` contained a blank line (line 28,
  the multiline `{args}` hazard) and the guarded `split()`-checked parse
  still found our index — the hazard survives, the parse survives it.
- `x_foot`: client census 0→1 `pw-profiler` clients during a run,
  `nodes_delta == 0`, `modules_delta == 0` — the footprint is exactly one
  Client object.
- `x_conc`: two simultaneous `-J -n 8` clients → rc 0/0, clean parses, 8
  overlapping `(driver,count)` blocks **dict-identical** between the two
  captures — the one-stream broadcast law at record level. Byte-identity
  is recorded (6471 B = 6471 B this window) but never armed — the
  boundary falsified it as a low-rate-window artifact.
- `x_top`: `pw-top -b -n 3` own row `R … 1.6us/0.6us` vs profiler medians
  wait 2.55 µs / busy 1.40 µs — same µs band (armed ratio 0.25–4.0).
- `x_profobj`: Profiler object id 5 refuses `pw-cli info` and
  `enum-params … Props` → **rc 0** +
  `unsupported type PipeWire:Interface:Profiler` ×2.
- `x_sigpipe`: closed stdout reader → SIGPIPE death, rc −13.
- `x_devfull`: stdout→/dev/full → rc 0, 0 B stderr — write errors
  silently ignored.

## Evidence

- Implementation sha256 (both runs identical bytes):
  `623c25cc55521472dc54a1ab2b4ccb4a9836fda3ca1a71dcca06092a4317cd22`
- Run 1:
  `corpus/live/runs/20261016T074733533774Z-pwprof-r89/measurements.json`
  — `failures: {}`, `coverage_blocked` empty in all four entries.
- Run 2:
  `corpus/live/runs/20261016T074816877001Z-pwprof-r89/measurements.json`
  — `failures: {}`, `coverage_blocked` empty in all four entries.
- Post-run census after run 2: zero `r89a` nodes in pw-dump, zero `r89a`
  modules, zero `r89a` sinks, no owned `pw-play`/`pw-profiler` processes,
  all `unloads[*].exit_code == 0`, `sinks_gone` all-true,
  `own_nodes_after: []` in all four entries. (`r87t_ns`,
  `r84a_probe_548706` and other pre-round foreign residue untouched.)

## Boundary corrections actually encoded

- **`-o` writes incrementally** (scout's exit-only claim dead): `o_kill`
  arms nonzero bytes/rows after SIGKILL; `o_eager` arms creation inside a
  running process.
- **`-n` is strtol-with-full-string-check, not atoi**: `2.5`/`1e1`/`3abc`/
  overflow/`-1`/`abc`/`0` all unbounded; `007`/`+3`/`" 3"` parse.
- **Broadcast is record-level, not byte-level**: `x_conc` arms
  dict-identity of overlapping `(driver,count)` blocks only.
- **Blank lines are a modules-table hazard, not universal**: `x_blank`
  arms the guarded parse against the real blank line; no claim that every
  `pactl … short` output has them.
- **`-o` consumes the next argv as its filename** (dev-measured): the
  default-name leg runs plain `-n 4`, never `-o` bare.
- Armed refusal rc is **255** for remote/env/opt/open classes — unlike
  pw-cli's rc-0 refusal family.
- Volatile-but-recorded: wall times, byte counts, ids, serials, cpu_load,
  foreign driver names — never verdict inputs.

## Remaining risks / blockers

- None blocking. Honest exposures recorded, not hidden:
  - `x_foot.nodes_delta` arms a 0.35 s foreign-churn-free window; a
    foreign node appearing inside it would surface as a real failure with
    the delta recorded.
  - `s_second`'s `c2 > c1` arm holds on both count-semantics hosts
    (frozen-gap → +1; live-count → larger gap) but assumes ≥1 own cycle
    between windows, which the seat follower guarantees while alive.
  - `x_conc`'s zero-overlap case lands in `coverage_blocked`, not
    failures — the streams were ~1 ms staggered in both green runs and
    always overlapped.
