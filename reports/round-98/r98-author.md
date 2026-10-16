# r98 author — the native `pw_stream` C-API family

Implementation of the round-98 author move: an insertion-only `pwstream`
family in `corpus/fixtures/measure_audio.py` (appended after the r89
block, before `def main()`), wired as `--probe-pwstream-r98`, plus the
committed C fixture it compiles and drives,
`corpus/fixtures/r98stream.c`. **Six entries, 67 legs.** Two full
batteries on the final bytes: **`failures: {}` in both**.

Every armed row is a **boundary-surviving** claim
(`reports/round-98/r98-boundary.md`); the r98 scout's falsified and
re-attributed rows are dropped or re-armed at the boundary's values
(§3 is the mapping). Nothing committed.

## Files changed

| file | change |
|---|---|
| `corpus/fixtures/r98stream.c` | **new fixture** (1005 lines) — the r98 scout's probe with three boundary-derived deltas (namespace `r98a_*`, `hold=`, NULL-context hardening) and one author correction to `hold` (§5.2) |
| `corpus/fixtures/measure_audio.py` | **+2385 / −2** — the only deletions are the two shared-line splices the wiring requires (the mode select and the receipt suffix; identical convention to r86–r89). No import, helper or prior row is touched |
| `reports/round-98/r98-author.md` | this file |
| `corpus/live/r98-author/` | untracked seat evidence (block source, splice script, scratch driver, fixture shas, poll + battery logs) |

Fixture sha256 (final bytes, `corpus/live/r98-author/fixture-sha256.txt`):

- `corpus/fixtures/measure_audio.py` —
  `c9d7627b25179616bee489c1093a525d25dd1812c96a6b969bb2eff01607d768`
- `corpus/fixtures/r98stream.c` —
  `9f840a6b8b23196124270d96532b3b35b2b868d089aef4eb58ad2d6b0950d323`

## Conventions carried over

- Namespace `r98a_<pid>` (`r98a_ns_`, `r98a_ns2_`, `r98a_*_pl`), private
  role key `r98arole<pid>` on the capture tone.
- Fixed-path family lock `corpus/live/measure_audio-pwstream-r98.lock`
  (flock, never `$TMPDIR`); `TMPDIR=~/Projects/shokunin/tmp` for runs.
- Name-verified teardown: re-read `pactl list modules` immediately before
  firing and unload only the index whose args carry our `sink_name=`;
  residual `r98a_<pid>` nodes destroyed by id; final sink/node census
  armed (`sinks_gone`, `own_nodes_after`).
- Never `pactl set-default-*`; every spawned process is its own session
  leader, bounded by SIGTERM→SIGKILL group escalation; `RLIMIT_CORE=0`
  on the crash-class legs (the r86 convention).
- Volatile text (ids, serials, cookies, wall times, `cpu_load`, foreign
  driver names) is recorded, never armed.
- The launcher's `PIPEWIRE_*` levers are cleared from every leg's
  environment (`inherited_env_levers` records any that were set) — a
  sibling shell that exported `PIPEWIRE_QUANTUM` would otherwise
  silently re-arm every geometry row.

## 1. Entries and legs (67)

### `pwstream_core_r98_probe` — 15 legs
Availability + version agreement (`library_version == core_version`, core
name/props); the connect/bind state machine (`node_id` =
`SPA_ID_INVALID` at connect, `get_time` −5, `disconnect` 0,
`connecting → paused`, `node.loop.class=main`); the only-if-absent
flag→prop projection (`node.dont-reconnect`, `node.autoconnect`) with its
explicit-`false` and `PIPEWIRE_PROPS` overrides; the env-overridable
AUTOCONNECT gate (`PIPEWIRE_AUTOCONNECT` false/true); env-over-prop
precedence (`PIPEWIRE_NODE` serial vs a garbage `target=`), plus the
deliberate default-sink fallback witness; the error rc lattice
(−5/−5/0/−5/−95 pre-connect, −16 second connect, direction 99 → rc 0 +
`unconnected`, 0-params → rc 0 + `paused`, bad remote → rc 1 + −112
`EHOSTDOWN`, pre-connect `dequeue` NULL).

### `pwstream_run_r98_probe` — 18 legs
The AUTOCONNECT gate (paused/0-callbacks/no-Format vs streaming); buffer
geometry (`stride 4`, `maxsize == nbufs*stride`, `nbufs ∈ {12288,
13375}`, the 256 ms callback cadence) with a two-rep stability arm and
the law-8 streaming sample (`queued == one buffer`, `queued_buffers 1`,
`size == request`, `get_time` rc 0); `node.latency=512/48000` as a
request lever; the RT_PROCESS thread (separate tid, SCHED_OTHER class,
the 5-event RT param lattice) and its main-thread twin (7-event lattice);
the activation arm and the **trigger FALS**, both in the `hold` window;
`pw_time` on the deactivated sample (rc −5, nothing queued — §5.3) plus
the `ticks` sample-point-determinism row; drain (callback and timer arms,
period armed **relative to the leg's own measured request**);
`ALLOC_BUFFERS` NULL data pointer; the s16 stride/size twin; `EXCLUSIVE`
and `DRIVER`.

### `pwstream_route_r98_probe` — 12 legs
Exact serial and exact-name resolution (×2 each), the prefix-collision
control (a live `r98a_ns2` neighbour must not match), the id and garbage
fallback arms to the **resolved** default sink (×2 each), and a three-rep
exact-target stability census.

### `pwstream_cap_r98_probe` — 4 legs
The `stream.capture.sink=true` gate with a mono 997 Hz /
amplitude-16383 tone on the private null sink (frames ≥ 40000, nz ≥ 90 %,
peak ∈ [0.49, 0.51], 997 Hz dominant over 440 Hz by ≥ 100×); the
target-less refusal (state `error`, the `no target node available`
string, rc 0, no frames — the scout's no-default-source-fallback law);
the prop-less policy row (recorded, see §5.4); an explicit source target.

### `pwstream_xw_r98_probe` — 4 legs
Induced xruns (300 ms and 600 ms stalls, each with a `pw-profiler -J`
overlap scoped to our own follower/driver names, ≥ 10 / ≥ 40 follower
xruns, driver 0, negative-wait records, the 600/300 ratio in [1.4, 2.6])
with probe-side `stall_gap_ms` arms so the injection itself never depends
on the profiler window; plus the `media.class` crash-class negative
control (recorded, **never gated**).

### `pwstream_sbx_r98_probe` — 14 legs
A private PipeWire core (+ private WirePlumber with the hardware monitors
**disabled**) under a redirected runtime/config dir: the quantum axis
(q512/q1024/q2048), the rate axis (a 44100 graph with a 48000 client vs
the rate-matched twin), the no-ALSA enumeration arm, and the bare-core
twins (no session manager → `paused`, no link, no refusal, no fallback,
no error).

## 2. Evidence

Two full `--probe-pwstream-r98` batteries on the final bytes
(`TMPDIR=~/Projects/shokunin/tmp`, `PYTHONDONTWRITEBYTECODE=1`, launched
under `nohup`; the family lock serialized them):

| run | receipt | verdict |
|---|---|---|
| 1 | `corpus/live/runs/20261016T101046237597Z-pwstream-r98/measurements.json` | **`failures: {}`**, 67 legs |
| 2 | `corpus/live/runs/20261016T101258039942Z-pwstream-r98/measurements.json` | **`failures: {}`**, 67 legs |

Per-entry leg census (identical in both runs): core 15 / run 18 / route 12
/ cap 4 / xw 4 / sbx 14 = **67**; **one** coverage cell in each run
(the `cap_noprop` policy row, §5.4). Key measured values, identical
across the two runs unless noted:

| row | run 1 | run 2 |
|---|---|---|
| gate geometry (2 reps) | 49152 B / 12288 frames / stride 4 / requested 1024 | same |
| `pw_time` streaming sample | `queued` 12288, `queued_buffers` 1, `size` 1024, `get_time` rc 0 | same |
| `ticks` (two identical `time` legs) | 87040 == 87040 | 87040 == 87040 |
| drain period (own request 1024) | 43.0 ms (2·1024/48000 = 42.7) | 43.0 ms |
| trigger FALS | 30 calls, rc 1, **3** callbacks at 421/901/1381 ms | 30 calls, **3** at 422/902/1382 ms |
| activation arm | 4 callbacks at 602/858/1114/1370 ms | 4 at 602/858/1114/1370 ms |
| param lattice non-RT / RT | `20,15,17,20,15,17,4` (7) / `20,15,17,17,4` (5) | same |
| deactivated `get_time` / `queued` | rc −5 / 0 | rc −5 / 0 |
| induced xruns 300 / 600 ms, ratio | 27 / 55, 2.037 | 27 / 55, 2.037 |
| crash class (`Audio/Sink`) | rc −11 SIGSEGV, recorded, not gated | same |
| sandbox q512/q1024/q2048 | 49152/12288 with requested 512/1024/2048 (2/2 each) | same |
| sandbox 44100 graph | 53500 B = 13375 frames (upsampled) and 49152/12288 (matched) | same |
| capture pins | 71680 frames, nz 69629, peak 0.499969 | same |
| teardown | `sinks_gone` all-true, `own_nodes_after: []`, unloads rc 0 | same |

The wedge-affected first attempt is retained at
`corpus/live/runs/20261016T092555426767Z-pwstream-r98/` — it shows the
named-block path (`pwstream_null_sink_unavailable`) and the arm defects
§5.1/§5.4 exposed; it is **not** a green run.

## 3. Boundary corrections actually encoded

| scout row | boundary verdict | what the author armed |
|---|---|---|
| law 1 (client API == daemon API) | CONF | `library_version == core_version`, core name/props present |
| law 2 / F2 (node id at connect) | CONF / FALS | `node_id == SPA_ID_INVALID`, `get_time` −5, `connecting → paused` |
| law 3 / F3 (AUTOCONNECT gate) | CONF + **EXT** | the gate at the **prop** level: `PIPEWIRE_AUTOCONNECT=false` beats the flag, `=true` opens it without the flag |
| law 4 / F6 (flag→prop) | CONF + **EXT** | only-if-absent, explicit `false` wins, `PIPEWIRE_PROPS` also wins |
| law 5 trigger half | **FALS** | 30 `trigger_process()` calls → ≤ 4 callbacks whose minimum gap ≥ 350 ms (the ~480 ms buffer cadence, not the 40 ms trigger cadence) |
| law 5 activation half | **EXT** | 4 callbacks at the exact 256 ms cadence after `set_active(true)` |
| law 6 (RT_PROCESS) | CONF-L | `proc_tid != main_tid` **and** `sched & 3 == SCHED_OTHER` (the law is "not realtime", not the raw `0x40000000`) |
| law 7 (12288 frames) | **FALS as a universal** | `maxsize == nbufs*stride`, `nbufs ∈ {12288, 13375}`; the rate axis armed in the sandbox at 53500/13375 and 49152/12288 |
| law 8 (`ticks`) | **FALS** | `ticks` equality only across structurally equal legs, else a named block — never "monotonic"; the structural fields armed on the streaming sample (§5.3) |
| law 9 (drain) | CONF + **EXT** | `flush` rc 0, ≥ 8 drained, state stays `streaming`, period ∈ [0.6, 1.6] × (2 × the leg's own request / 48000) |
| law 10 (param lattice) | **EXT (conditional)** | non-RT ≥ 7 events with Format; RT ≤ 6 — ordering never armed |
| law 11 (routing) | CONF obs + **REATTR** + EXT | serial/name/prefix exact; id and garbage → the resolved default sink; the bare-core twin shows the fallback is policy |
| law 12 (`set_rate`) | CONF | −95 pre-connect vs 0 while streaming |
| law 13 (buffer lifecycle) | CONF | `dequeue_null == 0`, `queue_err == 0`, `ALLOC_BUFFERS` NULL data |
| law 14 (capture) | CONF pins / **FALS** Goertzel / **REATTR** | frames/nz/peak/dominance floor — never the magnitude pair; the refusal row re-armed per §5.4 |
| law 15 (rc lattice) | CONF-L | the full −5/−5/0/−5/−95, −16, −112 lattice |
| F4 (`requested` under mismatch) | FALS + instability | `requested` is **not pinned** in the mismatch case anywhere |
| §3.5 (silent link transient) | new host class | one named retry, then a `coverage_blocked` — never a red, never a silent green |
| §3.6 (`node.latency` inert) | **FALS** | `requested ∈ [480, 540]` with `maxsize` unchanged |
| §4.5 (duplicate Link) | EXT | **not armed** — see §5.1 |

## 4. Host incident and hygiene (disclosed)

The window was **not quiet**, and two incidents are part of the record:

1. **A graph-wide enumeration wedge** (≈09:0xZ → 09:26:50Z). `pw-dump`
   produced **0 bytes** at 40 s, 200 s and 3 m 20 s bounds (`rc=124`),
   `pw-cli ls <Type>` returned partial output then stalled, and every
   `pactl` subcommand timed out — while targeted queries (`pw-cli info 0`)
   still answered. It lifted on its own (`pw_dump_rc=0`,
   `pactl_info_rc=0`; poll log `corpus/live/r98-author/dump-poll.log`).
   Two effects are kept in the record: the wedge-affected receipt (its
   named blocks, not greens) and the arm defects it exposed (§5).
2. **Foreign pulse-server interposition, and this seat's residue.** The
   final two green receipts record `sinks_gone: True` /
   `own_nodes_after: []` / unload `exit_code 0`, yet afterwards two
   `r98a_ns_<pid>` module-null-sinks were again present in the pulse
   module table, their nodes owned by a **foreign** `pipewire-pulse`
   (client `application.process.id = 3549294`, a sibling seat's server
   started mid-window). This seat removed both by name-verified index
   (`pactl unload-module 536870920 / 536870925`, rc 0) and re-verified:
   **0 `r98a` modules, 0 `r98a` sinks, 0 `r98a` nodes, 0 seat
   processes.** The confound is a real limit of a pactl-based teardown on
   a shared host (§6) — it is disclosed, not hidden. A private-core
   orphan from a crashed scratch driver was killed (`kill -9` on this
   seat's own pid, verified dead) and its scratch dirs removed.
3. **Foreign load, observed and never touched.** Ambient loadavg was
   51–55 for most of the window (a fleet of foreign orphaned processes;
   the boundary's §6 ledger documents the same class), with ≥ 10
   concurrent foreign `pactl`/`pw-dump` clients and one foreign `pactl`
   hung for 12 h 35 min (PPID `systemd --user`). The sandbox entry starts
   its own core and WirePlumber; the private WirePlumber's hardware
   profile is disabled, so **no ALSA node is enumerated** (armed; the
   boundary's sandbox had probed the host's PCI HDMI sink). The battery
   never issues `set-default-*`.

## 5. Findings that changed the fixture (author-window falsifications)

1. **The boundary's exact-1 / fallback-2 Link split did not reproduce.**
   In this window *all four* arm types (serial, name, id, garbage) showed
   the same **duplicate** Link pair at 0.6 s (`link_snapshot.count == 2`,
   identical `out`/`in`/`state`). The count is therefore **recorded,
   never armed**; arming it would encode a window artifact. (The boundary
   itself flagged the duplication `[?]`.)
2. **The boundary's `hold=` draft made its own arms unreachable.** Its
   guard `if (hold > 0 && el < hold) return;` sat *before* the
   activate/trigger branches, so at `hold=1500/2000` the probe measured
   `activate_done=0`, `trigger_count=0` — no arm ever fired (measured
   live in this seat, then fixed). The guard now sits **after** the arms
   and immediately before the fall-through quit, so the arms fire and the
   window stays open to `hold`. The C header records the correction; the
   corrected client is the one both receipts come from.
3. **`get_time_n` after a real deactivation is −5, not 0.** The
   scout's/boundary's "after `set_active(false)` `get_time_n` still rc 0"
   row came from legs that never reached cb 8 (their 1.5 s window yields
   6 callbacks), so the deactivation never fired. With the deactivation
   actually armed (`ms=2600` → cb 8) this host reports **rc −5 (EIO)** and
   `queued 0`, twice per battery in two batteries; that is what the
   fixture arms, and the streaming sample's `queued == 12288 /
   queued_buffers == 1 / size == request / rc 0` is armed on the run legs
   where it reproduces.
4. **The prop-less capture row did not reproduce either.** The boundary
   (and the scout) measured `error "no target node available"` for a
   capture targeting a sink without `stream.capture.sink`; in this window
   the same leg **streamed and captured the tone** (frames 57344, peak
   0.499969 — i.e. the sink monitor) in both batteries. The row is a
   named coverage block with the outcome recorded, and only the
   **target-less** arm is armed as the refusal (which does reproduce, with
   no default-source fallback).
5. **Smaller defects the receipts caught, all fixed before the final
   bytes**: the probe prefixes `name=` with `r98a_` (the entry-1 legs had
   snapshotted the wrong node name); the transient retry must not recurse
   (the first draft looped a paused leg for 15 min); the profiler's wall
   time for the same `-n` varied 2× between batteries (0.44 s vs 0.86 s
   per 120 infos) and clipped the 600 ms stall (23 xruns instead of 55) —
   the window is now `-n 900` and the injection is also armed probe-side;
   the capture legs need the AUTOCONNECT flag; `pactl info` can render
   the default as the symbolic `@DEFAULT_SINK@` in the pulse socket's
   degraded mode, so the default sink is resolved through
   `pactl get-default-sink` first and the row is named unmeasured when it
   cannot resolve to a real node name; `stream_error` is free text and the
   token parser truncated it to `no`.

## 6. Remaining risks / blockers

- **The `hold` semantics are now this seat's**, not the boundary's
  verbatim (§5.2): the fixture diverges from `r98bhold.c` by design. The
  boundary's extended-window numbers are reproduced by the corrected
  client, but the corrected client is the fixture the receipts come from.
- **The pactl-based teardown can be interposed by a foreign pulse
  server** (§4.2): `sinks_gone`/`own_nodes_after` are green in both
  receipts while two of this seat's sinks later reappeared owned by a
  sibling's `pipewire-pulse`. A later seat should gate the teardown on
  the core's node list (pw-dump) as the primary witness and treat the
  pactl table as the secondary one.
- The **duplicate-Link** observation is unresolved (boundary `[?]` 4 and
  §5.1): two windows disagree on the exact-vs-fallback count split; a
  later seat should settle it with a port-level witness rather than a
  0.6 s `pw-dump` snapshot.
- The **prop-less capture** row is a policy observation this window
  contradicted (§5.4) — recorded, not armed; a later seat may pin which
  WirePlumber condition gates the refusal.
- Sandbox legs absorb the private-WirePlumber startup race with **one**
  named retry and then a `coverage_blocked`; a run that lands there is
  honestly unmeasured, not green.
- No resume mutation attempted; no commit, no push — the orchestrator
  commits.

Seat stop — files changed by THIS seat:
`corpus/fixtures/r98stream.c` (new),
`corpus/fixtures/measure_audio.py` (+2385/−2),
`reports/round-98/r98-author.md`, evidence under `corpus/live/r98-author/`
and the receipts under `corpus/live/runs/*-pwstream-r98/`.
The canonical Rust runtime remains the sole judge.
