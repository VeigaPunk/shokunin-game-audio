# r91 author — the gst capture-freeze mechanism lattice

Implementation of the round-91 move: an insertion-only `gstfrz` family in
`corpus/fixtures/measure_audio.py` (appended after the r89 block, before
`def main()`), wired as `--probe-gstfrz-r91`, plus one new fixture app
(`corpus/fixtures/gstfreeze_r91_resume.py`). Five entries, **15 legs + 1
fixture process**. Every armed law is a boundary-surviving claim; the
scout's and the boundary's over-generalizations are dropped or re-armed at
this seat's own measured values, and each such decision is named below.

**Headline.** The freeze is now *mechanism-armed at default verbosity*: the
same capture argv without `-q` prints `gst-launch-1.0`'s own
`Clock lost, selecting a new one` on stdout with empty stderr — the
launcher's forced `PLAYING→PAUSED→PLAYING` round-trip, the boundary's root
cause, is a first-class cell of the battery rather than a `GST_DEBUG=*:5`
log hunt. And the boundary's "client is not sticky" control is armed live:
the fixture app observes `CLOCK_LOST`, never touches the pipeline state, and
resumes on a manual link (204844 → 340012 B).

## Files changed

- `corpus/fixtures/measure_audio.py` — **+1501 / −3**. The only deletions
  are the three shared-line splices the wiring requires (probe-mutex list,
  mode select, receipt suffix; the r86–r89 convention). The r91 block is
  1464 inserted lines at line 30982.
- `corpus/fixtures/gstfreeze_r91_resume.py` — **new fixture** (155 lines):
  the application that does not take the CLOCK_LOST pause. Its own wall
  clock, byte cap, per-tick status file (a hard kill still leaves a valid
  witness), SIGTERM/SIGINT flush, `set_state(NULL)` before exit.
- `corpus/live/r91-author/` — the battery wrapper, the two isolated
  connect-law probes, all dev/attempt receipts, `evidence-summary.txt`,
  `RECEIPTS.md`.
- `corpus/live/runs/*-gstfrz-r91/` — 15 canonical run dirs (every attempt).
- `corpus/live/measure_audio-gstfrz-r91.lock` — fixed-path family lock
  (created at runtime; mutual exclusion proven live).
- `reports/round-91/r91-author.md` — this file.

**Nothing committed.** HEAD stays `5a632a4f`; the only tracked source
modification is `measure_audio.py`. The tracked build artifact
`corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` is recompiled
by this seat's runs (fresh bytecode for the new source, not stale — Python
invalidates it by mtime/size) and the new fixture adds its own untracked
`.pyc`; both are disclosed, not hidden.

## Conventions carried over

- Namespace `r91a_<pid>` (`r91a_ns_`, `r91a_ns2_`, `r91a_src_`,
  `gst_r91a_<pid>`), private role key `r91arole<pid>` on every tone
  follower.
- Fixed-path lock `corpus/live/measure_audio-gstfrz-r91.lock` (flock, never
  `$TMPDIR`); `TMPDIR=~/Projects/shokunin/tmp` for all runs.
- Name-verified teardown: `_pactlmon_r85_unload_own` re-reads the module
  table immediately before firing and unloads only the index whose args
  carry our `sink_name=` / `source_name=`; residual `r91a_<pid>` nodes are
  destroyed by id; final census armed (`sinks_gone`, `own_nodes_after`).
- Never `set-default-*` in the r91 block (the file's only such legs are the
  pre-existing r78/r79 capture-family legs, untouched and never executed by
  this family); every spawn is its own session leader bounded by
  SIGTERM→SIGKILL process-group escalation.
- stdout/stderr are drained to capped **files**, never pipes (the r89
  backpressure law) — the `GST_DEBUG` leg cannot wedge.
- r91-local error classes checked before the r81 chain:
  `gstfrz_no_target_node` (`no target node available`),
  `gstfrz_target_not_found` (`stream error: target not found`),
  `gstfrz_negotiation` (`error during negotiation`).
- Volatile ids/serials/nsecs scrubbed in recorded text; they are never
  verdict inputs.

## Entries and legs

### 1. `gstfrz_prop_r91_probe` — the prop lattice (4 legs)

- `p_cap`: the live `pipewiresrc` node carries `node.dont-reconnect` as the
  **JSON boolean `true`** (the element sets `PW_STREAM_FLAG_DONT_RECONNECT`
  unconditionally), `stream.capture.sink` lands as the literal `"TRUE"`,
  `target.object` names the seat sink.
- `p_cap_false`: the CLI override lands as the literal **string `"FALSE"`**
  (gst passes structure values through as written).
- `p_rec`: `pw-record` carries **no** `node.dont-reconnect`.
- `p_sink`: `pipewiresink` carries **no** `node.dont-reconnect`; the sink
  stream is `running` before the loss (6/6 pre-loss samples); its post-loss
  life is armed as a **two-class envelope** (`survived_running | exited`),
  because the same argv produced both realizations (run-1 window: rc 1 and
  no post sample; every other window: `running` 9/9).

### 2. `gstfrz_clock_r91_probe` — the freeze + the mechanism witness (4 legs)

- `c_quiet` / `c_verbose` / `c_keepalive`: alive at the wall cap (SIGKILL by
  our own bound), **flat** post-loss, the pinned wavenc streaming header
  (`riff_size 0x7FFF0024`, `data_declared 0x7FFF0000`), **no re-created
  link** (`fed_by == []`), and the stream state leaving `running`
  (`idle`). The frozen **size** is recorded, never armed: this seat froze at
  135212 / 202796 / 204844 / 229420 / 413740 B with identical argv.
- `c_verbose` (no `-q`): stdout must carry `Setting pipeline to PLAYING` and
  **`Clock lost, selecting a new one`** with **empty stderr** — the
  launcher's own CLOCK_LOST handler, witnessed at default verbosity.
- `c_keepalive` (`keepalive-time=20` + `GST_DEBUG=pipewiresrc:5`): flat, and
  **0** `timeout, send keepalive buffer` lines and **0** `popped buffer`
  lines in the 6958 B debug stderr — keepalive cannot reach the resend path
  once the source is flushing (the boundary's falsification, re-armed).
- `c_alive`: the same argv with the target alive GROWS and stays `running`
  (the positive control that the loss, not the harness, causes the freeze).

### 3. `gstfrz_resume_r91_probe` — the positive control (1 leg + app)

The fixture app runs the **same** pipeline on the **same** target, observes
`CLOCK_LOST` (t ≈ 1.21–1.23 s) and **never** calls `set_state` after the
initial PLAYING (`forced: null`, state changes `null→ready→paused→playing`
only). Armed: flat while no link exists (204844), the manual `pw-link` rc 0
(2 pairs, discovered by port name — never guessed), the artifact **grows**
after the link (204844 → 274476/340012), the node is `running` and fed by
the seat's tone-fed monitor, and the app bounds itself at its own wall
(`exit: "wall"`, rc 0, the battery never had to kill it).

### 4. `gstfrz_srcloss_r91_probe` — the pw-record source-loss envelope (2 legs)

- `s_norelink` and `s_relink` both stay **alive** at the wall cap and land
  in one of two named classes with identical argv: **`grows_running`**
  (keeps producing unlinked buffers — the boundary's B12 / r85 shape) or
  **`freeze_idle`** (drops to `idle` and freezes — the scout's F1s /
  boundary B11 pre-link shape). Both classes were realized by this seat
  (dev1: `grows_running`; dev2–final: `freeze_idle`).
- `s_relink` additionally arms the boundary's surviving law: after the
  manual link the stream is `running` and the artifact grows
  (229420 → 761900/770092) — **the freeze is a "no link" state, not a
  client that refuses data**.

### 5. `gstfrz_connect_r91_probe` — the connect law (4 legs)

- `x_rec_sink` (bare, follower-free sink, verified in `pw-dump`
  immediately before): **rc 1**, artifact stops at the **44 B** header,
  class `gstfrz_no_target_node`.
- `x_gst_sink` (same configuration): **rc 255**, class
  `gstfrz_target_not_found`.
- `x_rec_sink_remapfed` (**envelope cell, not a claim**): the same no-prop
  capture against a sink whose monitor is consumed by the seat's
  remap-source. This seat measured `linked_live` (rc −9 at the wall cap,
  ~573484 B, fed by the seat remap-source) in both final runs — while the
  *identical* arm against a bare sink refuses. The class is armed only as
  `{refused | linked_live}` and named as a residual unknown.
- `x_rec_src` (the direction control): a no-prop capture x a **source**
  target links (`fed_by` non-empty) and records (761900/770092 B).

## Boundary/scout cells: what was dropped and why

| cell | decision | this seat's fact |
| --- | --- | --- |
| frozen size is a constant (`204844`) | **dropped** — recorded | 135212 / 202796 / 204844 / 229420 / 413740 across legs |
| frozen payload is 4096-aligned | **dropped** (falsified) | 202796 = 44 + 49.5 × 4096 in attempt-3 run1 |
| "the client is sticky" (scout Gate B) | **falsified**; the resume control is armed instead | app resumes 204844 → 340012 with no `set_state` |
| sink stream state survives the loss | **re-armed as an envelope** | `survived_running` and `exited` (rc 1) both realized |
| the source-loss shape is universally "grows" | **re-armed as an envelope** | `grows_running` (dev1) and `freeze_idle` (final) |
| the no-prop x sink target law is a direction law | **armed only for the bare-sink configuration** | the monitor-consumed configuration linked live |
| keepalive is the element's resend path | **armed as non-rescue** | 0 resend / 0 popped lines, flat artifact |
| the frozen header `0x7FFF0024` / `0x7FFF0000` | **armed** (the boundary's firmest re-confirmation) | every frozen leg |
| `on-disconnect` / `resend-last` reachability | **not armed** (unmeasured at the boundary too) | — |

## The two harness laws this round added

1. **Gated loss events.** Every loss/relink event fires only once the leg
   has *measured flow* (artifact ≥ 65536 B) or a 3.0 s deadline passes;
   the relink additionally requires its unload to have fired. A fixed 1.2 s
   loss under host load can land before the stream ever negotiated — the
   attempt-1 run2 defect (0-byte artifact, "state stayed running") — and
   the leg would then measure a startup race, not the law. Final gates fired
   at 1.203–1.208 s with 204844 B on hand, no fallback.
2. **Loader liveness.** `_ns_ensure` / `_src_ensure` reuse a name only when
   its module is still in the pactl table (and, for the relink arm, the node
   is still in `pw-dump`); otherwise they wait (bounded) for a dying
   same-name module to clear and load fresh. A listed name whose module is
   gone makes a leg bind a lingering node and every later unload skip — the
   attempt-2 run1 defect.

## Evidence

- Implementation sha256 (final bytes, re-verified after both green runs):
  `corpus/fixtures/measure_audio.py`
  `b0ab6fda8b35eafa76b753ce8e31687b14ec278396fbdd00c8efc2b432124af0`;
  `corpus/fixtures/gstfreeze_r91_resume.py`
  `066d6fff7ba74ef40d11b2f3a71ae336d4ee21c6d73d0975d6dc94fe714b1dc2`.
- Green run #1: `corpus/live/runs/20261016T093036393664Z-gstfrz-r91/measurements.json`
  — `failures: {}`, `coverage_blocked` empty in all five entries.
- Green run #2: `corpus/live/runs/20261016T093129552702Z-gstfrz-r91/measurements.json`
  — `failures: {}`, `coverage_blocked` empty in all five entries.
- Non-volatile cells dict-identical between the pair: prop lattice
  (`true` / `"FALSE"` / absent / absent), frozen header + flat + idle +
  no-link (204844 all three legs, `align_ok` true), keepalive 0/0 (6958 B
  debug stderr), resume (pre 204844, relink rc 0, growth, `forced: null`),
  source-loss classes (`freeze_idle` + `grows_running`), connect
  (rc 1 / rc 255 / control links), `remapfed` class `linked_live`
  (573484 B both runs).
- Run wrapper + every attempt: `corpus/live/r91-author/` (`RECEIPTS.md`,
  `commands.log`, `impl-shas.txt`, `frozen-shas.txt`, `evidence-summary.txt`).
- Post-run census: 0 `r91a` modules, 0 `r91a_` nodes, 0 seat processes;
  defaults unchanged (`…HiFi__SPDIF__sink` / `…HiFi__Line__source`);
  teardown `sinks_gone` all-true and `own_nodes_after: []` in every entry of
  both runs; every fired unload `verified_index == captured`, `recycled:
  false`, rc 0 (the three `not_listed` skips are the legs' own earlier
  gated unloads, not foreign kills).
- Lock: a second acquisition is refused while the seat holds the family
  lock (proven live).
- **Labrat: not dispatched.** The seat is the frozen `probeParent`; the
  assigned attack resolved to on-host measurement (plus two isolated
  probes), and no residual bounded unknown could be settled better by a
  read-only probe. Budget retained.

## Remaining risks / blockers

- **No blockers.**
- Three cells are *class-armed* (`p_sink` post-loss, `s_norelink`,
  `remapfed`): a third realization would surface as a real failure. The
  armed classes are exactly the ones this host produced.
- `x_rec_sink_remapfed` is **recorded, not claimed**: the boundary's
  direction-law mechanism does not explain the live-linked class, and the
  discriminator was not isolated (candidate: the target's published
  monitor ports / a monitor consumer). Named residual unknown.
- The resume arm's pre-link flatness tolerance is 8192 B with the window
  stopped before the relink sample; an in-flight flush landing *inside* that
  window (a 32768 B buffer) would fail the arm.
- Host load is real: attempt-2 ran 843 s under loadavg ≈ 52 with `pw-dump`
  timeouts; the dump is now bounded at 6 s, but an extreme window can still
  produce honest contention failures.
- The resume fixture requires PyGObject + GStreamer bindings; absent
  bindings are a named coverage block, never a silent failure.
- The family lock excludes same-family runs only; it cannot exclude foreign
  lanes (they are recorded as contention witnesses).

*author leaf — implemented, measured, not judged.*
