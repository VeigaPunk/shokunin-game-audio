# R98 boundary — the native `pw_stream` laws attacked: load, clock axes, and session-manager attribution

Round 98 **boundary seat**. Host `plazir27`, measured **2026-10-15T20:52Z →
21:15Z** (host local UTC−3). Repo `~/Projects/shokunin/audio-shokunin` @ entry
HEAD `51a98e54`, exit HEAD `25d89bdb` (sibling commits landed during the seat:
`28cc128f r99 scout` at 20:57Z, `25d89bdb r95 boundary` at 21:11Z).
Toolchain identical to the r98 scout: PipeWire **1.6.8** (`1:1.6.8-1`),
WirePlumber **0.5.17-1**, libpulse **17.0-98-gb096**, gcc **16.2.1+r23**,
Python **3.14.7**, 32 CPUs (Ryzen 9 9950X).

Target: `reports/round-98/r98-scout.md` — its 16 headline laws (§1), 8
predeclared falsifications (§2) and the proposed author rows (§4).

**Seat: BOUNDARY (leaf). Zero tracked-file writes.** All writes are under
`corpus/live/r98-boundary/` (untracked) plus this report. `git status` shows one
tracked modification in the worktree — `corpus/fixtures/measure_audio.py`
(+2263 lines, mtime **21:09:10Z**, i.e. *inside* this window) — which is a
**sibling author's** edit; this seat never opened that path and did not touch it.

**Namespace `r98b_*`** for every object created. Only own PIDs are ever
signalled: the 16 load hogs are recorded at spawn with their `/proc` starttime
and re-verified (comm + starttime) before the kill. No `pactl set-default-*`
was ever issued; defaults SPDIF/Line unchanged at exit. Exit census: **0 `r98b`
nodes, 0 `r98b` modules, 0 seat processes**; the private sandbox core's socket
is gone and the shared graph contains no `r98b_sb` object.

**Contention disclosure (first-order, see §6).** The host was **never quiet**.
A fleet of **64–96 foreign `yes` processes** (PPID = `systemd --user`, i.e.
orphaned; starttime **20:02:34Z**, ~50 min before this seat) dominated the box:
ambient loadavg **56–67** with zero audio work. Sibling seats were live in the
shared graph throughout (`r92b_*`, `r93b_*` filter chain, `r95b_ns`,
`r96b_ns` + `r96b_cli`/`pacat`/`paplay`/`pw-record` at forced quanta
**1440/2048/8192**, `r95bjack`), plus two private-core WirePlumbers from
`r97-boundary`, plus a `godot --headless` audio run. Loadavg rose to **133**
during the watch window. A *quiet* arm is therefore not attainable on this host
(§7 blocker B1); "quiet-ish" below means **no self-induced load**.

---

## 1. Method

| arm | load | legs |
| --- | --- | --- |
| **ambient** ("quiet-ish") | 0 self hogs; foreign loadavg 56–67 | replay of the scout's armed cells, 118 legs, fresh process per rep |
| **load** | **+16 own `yes` hogs** (pids recorded, all 16 killed, `refused=[]`), loadavg 76–84 | same 118 legs |
| **axes** | ambient | flag order, argv order, env-override precedence (39 legs) |
| **attack** | ambient | crash class ×6 shapes, drain×quantum, routing, 44 legs |
| **ext** | ambient | untruncated observation windows via `hold=` (13 legs) |
| **sandbox** | private PipeWire core (± private WirePlumber), `PIPEWIRE_RUNTIME_DIR`/`XDG_*` redirected into `sandbox/` | clock axes: server quantum 512/1024/2048, server rate 44100, bare core (no session manager), default-node state |

**Clients.** (a) `probes/r98bstream` — the scout's `r98stream.c` **byte-identical
except the namespace prefix and the app name** (source sha `ce1a98ed…`; binary
`f5524552…`, same 61192 bytes as the scout's build), so the replay is the same
client semantics. (b) `probes/r98bhold` (sha `5283ebdd…`) — the same source plus
one option, `hold=<ms>`, which suppresses the probe's **early-quit paths**; the
scout probe quits ~20 ms after the activation arm fires and after the 30th
trigger, truncating those windows (this is the §3 extension, not a rewrite;
`hold=0` is timing-identical to the scout client). Raw stdout/stderr for every
leg is in `raw/`, per-leg receipts in `receipts/battery-*.json`.

**Harness corrections of my own (disclosed).** (i) First sandbox run gave
`rc=-11` on every leg: `PIPEWIRE_CONFIG_DIR` made clients fail to find
`client.conf`, `pw_context_new()` returned NULL and the probe (like the scout's)
does not check it — fixed by shipping `client.conf` per variant; the sandbox
receipts are post-fix. (ii) My first profiler parse took `driver_xrun_max` over
*all* driver records and reported `dxrun=1`; re-scoped to `r98b` records the
scout's "driver 0" is confirmed and the `1` is a **foreign** ALSA driver's xrun
(§6). Both corrections are visible in the receipts.

---

## 2. Verdict table

Verdicts: **CONF** = confirmed (fresh reps, both arms unless noted);
**CONF-L** = confirmed under load; **EXT** = extended/pinned further;
**FALS** = falsified; **REATTR** = observation holds but the *cause* is not
where the scout put it; **UNRES** = not resolved.

| # | scout law (abridged) | verdict | key numbers from this seat | receipts |
| --- | --- | --- | --- | --- |
| 1 | client API == daemon API; version/core agree; connect is a round-trip | **CONF** | `library_version=1.6.8`, core `pipewire-0/1.6.8/vgpnk/plazir27`, connect rc 0; core props `default.clock.quantum=1024`, `rate=48000`, `quantum-limit=8192`, `link.max-buffers=16` (3/3) | `battery-quiet.json` `info` ×3 |
| 2 | connect-then-bind; node id invalid at connect | **CONF** | `node_id=4294967295` 3/3 ambient + 3/3 load; `node_id_final` 52…220 (id churn); `get_time_pre_rc=-5`; `disconnect_rc=0` | `state` ×6 |
| 3 | AUTOCONNECT is the gate; buffers are 12-quanta, not quantum-sized | **CONF + EXT** | no flag → `paused`, cb 0, param ids `20,15,17` (6/6); flag → `streaming`, cb 6, `maxsize=49152`, `requested=1024`, `nbufs=12288`, stride 4 (6/6). **EXT:** the gate is the *prop*, not the flag — `PIPEWIRE_AUTOCONNECT=false` + flag → paused/cb 0 (3/3); `PIPEWIRE_AUTOCONNECT=true` **without** the flag → streaming/cb 5 (3/3) | `run_autoconnect`, `run_no_autoconnect`, `env_ac_*` |
| 4 | flag→prop is only-if-absent; explicit `false` wins | **CONF + EXT** | `node.dont-reconnect=true` from the flag; explicit prop `false` stays `false` (3/3); **EXT:** `PIPEWIRE_PROPS=node.dont-reconnect=false` also wins over the flag (3/3) | `dont_reconnect*`, `env_props_false_over_flag` |
| 5 | INACTIVE/TRIGGER park the stream; activation/trigger are the movers | **FALS (trigger half) / EXT (activation half)** | INACTIVE → `paused`, cb 0, `set_active(true)` rc 0 → `streaming` (3/3). **Trigger: 29–30 `trigger_process()` calls, rc 1 each, produced only 3 callbacks** — 6/6 fresh reps (cb_log 3 entries: e.g. 327/809/1294) *and* 3/3 in the scout's own receipts (`cb_count=3`, `trigger_count=30`) | `trigger`, `ext_trigger_hold`, `ext_activate_hold` |
| 6 | `RT_PROCESS` moves the callback to another thread, not RT-scheduled | **CONF-L** | `proc_tid≠main_tid`, `sched_getscheduler=1073741824` (`OTHER\|RESET_ON_FORK`), prio 0, nice 0 — 3/3 ambient + 3/3 load; without the flag `proc_tid==main_tid`, `sched=0` | `rt_process`, `run_autoconnect` |
| 7 | buffer geometry is fixed at 12288 frames; the request follows the quantum | **FALS as a universal / CONF per axis** | Quantum axis **CONF**: server quantum 512/1024/2048 → `maxsize=49152` (12288 frames) in all variants, `requested`=512/1024/2048. **Rate axis FALS**: graph rate 44100 + stream 48000 → `maxsize=53500` = **13375 frames = 12288 × 48000/44100**, `requested`=30/31 (sandbox 2/2 streaming; shared graph 4/4 during a foreign-induced 44100 window, §3) | `sandbox-geometry.json`, `sandbox-ratios.json`, `raw/control_run-r0.out` |
| 8 | `pw_time` fields structural; queryable after deactivate | **CONF / `ticks` claim FALS** | `rate=1/48000`, `queued=12288`, `queued_buffers=1`, `avail_buffers=0/1`, `size=1024`, `delay=1024`; after `set_active(false)` rc **0** (6/6). `ticks` is **not** an advancing sampled value: 37888 in 6/6 run legs and 62464 in 6/6 time legs — sample-point-deterministic | `time`, `run_autoconnect` |
| 9 | `flush(drain=true)` rc 0; `drained` repeats, state stays streaming | **CONF + EXT** | rc 0; `n_drained` 40 (callback arm) / 34–35 (timer arm); state stays `streaming` in both arms (6/6 + 6/6 load). **EXT (§4):** the period is exactly **2 × graph quantum / graph rate** — 20–22 ms @512, 40–45 @1024, 82–88 @2048, 43–50 @44100/1024 (4 server configs) | `drain_cb`, `drain_timer`, `sandbox-geometry.json` |
| 10 | param lattice `20,15,17,20,15,17,4`; mid-stream `update_params` silent | **EXT (conditional)** | the 7-event lattice holds **only without `RT_PROCESS`**; with `RT_PROCESS` it is 5 events `20,15,17,17,4` (my `rt_process`/`time` 3/3; the scout's own `rt_process`/`time`/`trigger`/`early_process` receipts agree). Ordering is not stable: `20,15,17,4,17` and `20,15,17,4,20,15,17` also observed. `update_params` rc 0, `n_param_changed=0` after the reset window | `neg_stream`, `rt_process`, `quantum2048`, scout `battery-all.json` |
| 11 | `target.object` resolves by name/serial; id and garbage fall back to the default sink | **CONF (observation) + REATTR + EXT** | serial → `r98b_ns` (3/3), name → `r98b_ns` (3/3), **prefix collision**: with `r98b_ns2` present `target=r98b_ns` links to `ns`, not `ns2` (3/3); id → SPDIF default (3/3), garbage → SPDIF (3/3). **REATTR:** the fallback is WirePlumber policy, not the client/core (§3.4). **EXT:** fallback arms create **two distinct Link objects** to the same sink (3/3 in 3 leg types) while exact-target arms create exactly one | `target_*`, `atk_target_ns2_*`, `env_node_*`, `sandbox-bare.json` |
| 12 | `set_rate` is `-ENOTSUP` only before the rate-match exists | **CONF** | pre-connect `-95` (3/3 both arms); while streaming rc **0** (6/6) | `err_set_active_pre`, `time` |
| 13 | buffer lifecycle rc-clean; `ALLOC_BUFFERS` hands a NULL data pointer | **CONF** | `dequeue_null=0`, `queue_err=0`; `add_buffer_data_null=1` then streams (cb 5); `MAP_BUFFERS` → `data=set` | `run_autoconnect`, `alloc_buffers`, `map_buffers` |
| 14 | capture works only with `stream.capture.sink=true`; refusal is native; no default-source fallback | **CONF (sample pins) / FALS (Goertzel "identical") / REATTR (refusal)** | with prop: `streaming`, 35 cb, **71680 frames, nz 69629, peak 0.499969** (3/3 ambient + 3/3 load); without: state `error`, `"no target node available"`, rc 0 (3/3); no target: same (3/3). Goertzel: two alignment states exist (302935207.678/4.212 vs the scout's 302944141.055/4.542) — see §3.3. **REATTR:** the error string is WirePlumber's (§3.4) | `cap_prop`, `cap_noprop`, `cap_default_source`, `sandbox-bare.json` |
| 15 | rich rc lattice; rc is not a verdict | **CONF-L** | pre-connect `set_active -5`, `get_time -5`, `flush -5`, `set_rate -95`, `disconnect 0`, `dequeue NULL` (3/3); second connect **-16**; direction 99 rc 0 → `unconnected`; 0-params rc 0 + `paused`; bad remote rc 1 **-112** — all 3/3 ambient + 3/3 load | `err_*`, `remote_bad` |
| 16 | induced xruns: 300 ms → ERR 27, 600 ms → 55, driver 0, linear | **CONF-L** | follower `xrun_count` **27/27/27** (300 ms) and **55/55** (600 ms) in **both** arms; negative-wait 26/54; `r98b` driver `xrun_count=0` in every rep; pw-top ERR 27 with `+` reproduced | `stall300`, `stall600`, `scratch/prof-stall*-r*.json` |
| F1 | crash class: `media.class=Audio/Sink` on playback → SIGSEGV | **CONF + EXT** | **32/32 rc −11** across 6 shapes: valid target (5/5), no target (5/5), 44100 (5/5), `INACTIVE` (3/3, never streams), `RT_PROCESS` (5/5), serial target (3/3), plus the replay arms (3/3 + 3/3). `Audio/Source` twin: 0/3 crashes (rc 0, paused) | `media_class_*`, `atk_mcsink_*` |
| F2 | node id usable right after connect | **FALS** (agrees with scout) | 4294967295 at connect, 6/6 | `state` |
| F3 | stream without AUTOCONNECT still runs | **FALS** (agrees) | `paused`, cb 0, no Format param, 6/6 | `run_no_autoconnect` |
| F4 | NO_CONVERT+44100 refuses at connect | **FALS** (agrees) + `requested` instability | `streaming`, cb 4, `maxsize=49152`, `requested` **796** (6/6 here) vs **738** in my sandbox for the same shape — the mismatch-case `requested` is not stable across windows | `noconvert_44100`, `convert_44100`, `sandbox-ratios.json` |
| F5 | `target.object=<object.id>` resolves like serial | **FALS** (agrees) | id → default sink 3/3 ambient + 3/3 load | `target_object_id`, `target_ns2_by_id` |
| F6 | explicit `node.dont-reconnect=false` loses to the flag | **FALS** (agrees) | prop stays `false`, 3/3 | `dont_reconnect_false_prop` |
| F7 | stalled follower invisible to xrun accounting | **FALS** (gap closed, agrees) | see law 16 | `stall300`, `stall600` |
| F8 | capture to a sink without the prop fails loudly | **CONF (agrees) / REATTR** | the state/error is real, but it is **WirePlumber's** refusal; the bare core produces no error and no link at all | `cap_noprop`, `sandbox-bare.json` |

---

## 3. Falsified and re-attributed claims (exact receipts)

### 3.1 "each `pw_stream_trigger_process()` returns rc 1 **and yields a callback**" — FALSIFIED
The scout's own receipt already contradicts the sentence: `trigger` legs show
`cb_count=3` with `trigger_count` 29/30/30 and a 3-entry `cb_log`
(`327,809,1294`). My fresh reps (both arms, 6/6) reproduce it exactly:
`trigger_count` 29–30, `trigger_rc=1`, `cb_count=3`, and the extended-window
variant (`hold=2000`, 2 s instead of 1.5 s) still yields **3** callbacks — the
callbacks are the *buffer* cadence (gaps 485/492 ms), not the trigger cadence.
Mechanism (inference, consistent with the source the scout cites): the process
callback is suppressed while no free buffer exists (`stream.c:449-477`), so a
trigger only produces work when a buffer has been consumed.
Receipts: `battery-quiet.json`/`battery-load.json` `trigger`, `battery-ext.json`
`ext_trigger_hold`, scout `battery-all.json` `trigger`.

### 3.2 "buffer geometry is fixed at 12288 frames" — FALSIFIED as a universal
A controlled private core (no foreign clients) gives the lattice:

| graph rate | stream rate | `maxsize` | frames | `requested` |
| --- | --- | --- | --- | --- |
| 48000 | 48000 | 49152 | 12288 | 1024 |
| 48000 | 44100 | 49152 | 12288 | 738 (796 in the shared graph) |
| **44100** | **48000** | **53500** | **13375 = 12288×48000/44100** | **30/31** |
| 44100 | 44100 | 49152 | 12288 | 1024 |

So the 12288-frame size is **rate-relative**: it is 256 ms of *graph* frames,
expressed in the client's frames whenever the client upsamples. The scout varied
only the *quantum* (and only via the client's own `force-quantum`); the graph
**rate** axis was never varied, and that is the axis that moves the constant.

**This is not hypothetical on the shared graph.** During my attack stage, the
identical control shape (`run target=r98b_ns flags=autoconnect`) produced
**13375 frames** — the r44100 signature, i.e. `maxsize=53500 B` for f32 and
`26750 B` for the s16 variant, with `requested=30` — 4 times
(`raw/control_run-r0.out`, `raw/repro_ns2_serial-r0.out`,
`raw/repro_time_q512-r0.out`, `raw/repro_run_s16_q512-r0.out`), and the
sandbox r44100 variant reproduces those three numbers *exactly*. The graph was
therefore running at 44100 while a foreign client held it there (a direct
`pw-top` witness of that instant was not captured — the fingerprint match is the
evidence; the same window also shows 9 consecutive legs failing to link, §3.5).
Immediately before and after, the same shape gives 49152/1024/12288 (3/3 in the
`geom_state` re-run, and 15/17 samples of the 210 s shared-clock watch).

### 3.3 "capture magnitudes identical to the last digit ×3" — alignment-locked, not universal
`peak=0.499969`, `frames=71680`, `nz=69629` are stable (3/3 ambient + 3/3 load).
The Goertzel pair is not: ambient 3/3 = `g997 302935207.678 / g440 4.212`,
load 2/3 = the same, but **load r1 = `302944141.055 / 4.542`** — precisely the
scout's value. So there are (at least) two capture-alignment states; the scout's
"identical to the last digit ×3" was true inside one window and is not a stable
pin across windows. Receipt: `battery-quiet.json`/`battery-load.json` `cap_prop`.
**Independent corroboration:** the sibling `r95-boundary` seat hit the same class
on the JACK capture surface in the same hour (`reports/round-95/r95-boundary.md`
F2: "170/171 quanta captured in different reps … the scout's 3/3 identity was a
lucky alignment; arm the invariants … never the file hash"). Both seats point the
same way: arm `peak`/frame-count invariants, never a whole-window digest.

### 3.4 "the native refusal is loud" / "silent fallback to the default sink" — RE-ATTRIBUTED to WirePlumber
Two independent lines of evidence:

1. **The string is WirePlumber's.** `/usr/share/wireplumber/scripts/linking/prepare-link.lua:114`
   contains `lutils.sendClientError (event, node, -2, reconnect and "no target node available" or "target not found")`
   — exactly the scout's observed `error` text and `core res:-2`. `src/pipewire/stream.c`
   only *sets* `node.autoconnect` (2085-2087); it contains no linking code.
2. **A bare core has no refusal and no fallback.** With a private PipeWire core
   and no session manager, all five shapes — `run target=<sink>`,
   `run target=garbage`, `cap` with `stream.capture.sink=true`, `cap` without,
   `cap` with no target — return **`paused`, `stream_error=-`, cb 0, no link**
   (2 reps each). No error state, no default-sink fallback, no capture refusal.
   A session manager also *chooses* the fallback: the shared WP falls back to the
   SPDIF sink, a private WP fell back to `alsa_output.pci-0000_01_00.1.hdmi-stereo.9`.

So laws 11 and 14 (and F8's "native refusal") describe **WirePlumber 0.5.17
policy**, not the native client/core surface. The scout's own §3.9 evidence
(`stream.c:2121-2123` is a `pw_log_warn` only) already pointed this way.
Receipts: `sandbox-bare.json`, `sandbox-default.json`, `sources` (scout's
`stream.c`), plus the shipped WP lua.

### 3.5 NEW: autoconnect linking has a silent transient failure mode
9 consecutive legs (`atk_target_serial_ns2` 3/3, `atk_time_q512` 3/3,
`atk_run_s16_q512` 3/3) stayed `paused` with **no link and no error**
(`stream_error=-`, rc 0) in a ~40 s window, while the *same* leg shapes stream
normally before and after (`battery-attack.json` vs the immediate re-run in
`raw/geom_state-r*.out` and the 210 s watch: 15/17 streaming). Flake census:
ambient 0/118, load 0/118, axes 0/39 (the 3 paused are the intended
`PIPEWIRE_AUTOCONNECT=false` arm), attack 9/44. It is **not** my CPU load (the
load arm is clean) and it coincided with the 44100/53500 window. Any author row
built on autoconnect must therefore tolerate an occasional
`paused`/no-link/no-error outcome; the scout's §4 arming note does not mention it.

### 3.6 "`node.latency=1024/48000` changed nothing" — FALSIFIED (and unreceipted)
No receipt exists for that claim (`raw/` has no latency leg). With
`PIPEWIRE_LATENCY=512/48000` (→ `node.latency=512/48000`) `requested` becomes
**512** (3/3) while `maxsize` stays 49152 — i.e. `node.latency` *is* a request
lever; the scout's test value (1024) was indistinguishable from the ambient
quantum, so the arm could not have detected anything. Receipts:
`battery-axes.json` `env_latency512`, `sources/stream.c:2162`.

---

## 4. Extensions and new pins (beyond confirm/falsify)

1. **Drain period = 2 × graph quantum / graph rate** (pins the scout's `[?]` §6.2):
   20–22 ms @ q512, 40–45 @ q1024, 82–88 @ q2048 (all 48000) and 43–50 ms at
   graph 44100/q1024 — the shared graph's 42.5 ms is the q1024/48000 case.
   `n_drained` 49/33/17/10 over a 2.2 s window scales the same way.
2. **The AUTOCONNECT gate is prop-level and environment-overridable**
   (`PIPEWIRE_AUTOCONNECT`, `PIPEWIRE_NODE`, `PIPEWIRE_PROPS`, `PIPEWIRE_QUANTUM`,
   `PIPEWIRE_LATENCY`; `stream.c:2142-2163`): env beats the flag *and* the
   explicit `target=` prop — `PIPEWIRE_NODE=<serial>` + `target=garbage` links to
   the serial's sink (3/3), `PIPEWIRE_NODE=garbage` + `target=<serial>` falls
   back to the default sink (3/3). Precedence: **env > explicit prop > flag**.
3. **Flag-list order and argv order are inert**: 3 permutations of
   `autoconnect,dont_reconnect,rt_process` give identical props
   (`node.autoconnect=true`, `node.dont-reconnect=true`, no `node.async`) and
   identical state/cadence/geometry; reversed argv is identical (3/3 each).
4. **The activation arm was truncated by the probe, not by the library**: with
   `hold=1500` the stream produces 5 callbacks at the exact 256 ms cadence
   (408/664/920/1176/1432) after `set_active(true)`; the scout's `cb_count=1`
   was a 20 ms window. Law 5's activation half is therefore *stronger* than the
   scout could show.
5. **Fallback arms create two Link objects** (distinct ids, same sink) — 3/3 in
   `target_object_id`, `target_garbage`, `target_ns2_by_id`,
   `env_node_garbage_over_serial_prop`; exact-target arms create exactly 1
   (`target_serial`, `target_name`, `target_prefix_collide`). Reproduced across
   three stages; port-level cause not resolved.
6. **Exact-name resolution survives a prefix collision** (`r98b_ns` vs
   `r98b_ns2`): the target links to `ns` (3/3) — no substring matching.
7. **Cadence is load-invariant**: 256 ms (255–258) in 100+ legs across both arms,
   including under 16 own hogs at loadavg 80; the extended 3 s window gives
   12 callbacks at 256/256/256 ms spacing.
8. **`ticks` is sample-point-deterministic** (37888 / 62464 in 6/6 each) — see law 8.

---

## 5. Receipt index (this seat)

`corpus/live/r98-boundary/` (4.9 MB, 528 files):

- `probes/r98bstream.c` (`ce1a98ed…`) + binary (`f5524552…`) — frozen replay client.
- `probes/r98bhold.c` (`d4c82505…`) + binary (`5283ebdd…`) — `hold=` extension client.
- `r98bd.py` — shared-graph driver (arms, hog lifecycle, census, link/port witnesses).
- `r98bsb.py` — private-core sandbox (geometry / ratios / bare / default).
- `r98bwatch.py` — 210 s shared-clock watcher (`receipts/shared-clock-watch.json`).
- `r98baudit.py` — zero-load audit of the scout's own receipts
  (`scratch/audit-scout-receipts.json`, `scratch/quiet-verdicts.txt`, `scratch/diff-quiet-load.txt`).
- `receipts/battery-{quiet,load,axes,attack,ext}.json`, `receipts/summary-*.json`,
  `receipts/census-{entry,exit}.json`, `receipts/sandbox-*.json`,
  `receipts/shared-clock-watch.json`, `runs/*.log`, `raw/*.out|err` (per-leg
  verbatim), `scratch/prof-stall*-r*.json` (pw-profiler witnesses),
  `scratch/audit-scout-receipts.json`.
- `MANIFEST.sha256` — sha256 of every file in this tree.

---

## 6. Contention ledger (foreign — observed, never touched)

| window | contact | effect |
| --- | --- | --- |
| whole seat | **64–96 foreign `yes`** (PPID `systemd --user`, starttime 20:02:34Z; r85-boundary owns the only hog-spawning probe in that window and its `hogs.pid` is now empty; r96's log recorded `host_yes_remaining=112` at 20:16Z) | loadavg 56–67 ambient, 76–84 with my +16, 133 by 21:14Z; the *dominant* contention. Ownership not proven; not signalled. |
| whole seat | sibling nodes in the shared graph: `r92b_in/fc_in/fc_out/play/rec/ref`, `r93b_in/fc_in/fc_out/ref`, `r95b_ns`, `r95b_probe`, `r96b_ns` | appear in my dumps/top rows; never addressed by my legs (all targets are `r98b_*` or the default sink for the deliberate fallback witnesses) |
| whole seat | sibling clients at forced quanta: `r96b_cli` **8192**, `r96b_pulse_cork` 8192, `pacat` 8192/1440, `paplay` 8192, `r96b_ns` 2048, `pw-record`, `r95bjack` | explains the ambient `requested` drift I observed (512 ↔ 1024 ↔ 2048 across legs/arms); the *verdict* fields stayed stable |
| attack window | foreign reconfiguration fingerprint: graph at 44100 (13375-frame geometry, `requested` 30) + 9 unlinked legs | §3.2/§3.5; not attributable to a named client (no instant `pw-top` witness) |
| stall windows | **foreign ALSA driver `alsa_output…SPDIF__sink` `xrun_count=1`** (2 of 5 profiler dumps) | a foreign driver xrun, not mine; it is why the profiler parse must be namespace-scoped |
| 20:5x–21:1xZ | `godot --headless … audio_lattice.gd --arm=gen`, `r96b_cli.py server load`, two `r97-boundary` private cores + private WirePlumbers | CPU + audio-stack contention; the r97 private cores are separate sockets (no shared-graph objects) |
| whole seat | sibling seats on the same host: `r95-boundary` (JACK surface, commit `25d89bdb` at 21:11Z), `r96-*`, `r97-boundary`, `r99-scout`, `r82-author` | their probes/clients are the ones appearing as `r9xb_*`/`pacat`/`paplay` rows; their findings are cited where they corroborate (§3.3). No sibling artifact was written by this seat. |
| residue | `~/.local/state/wireplumber/stream-properties` gains **2 rows** (`Audio/Sink:node.name:r98b_ns`, `…:r98b_ns2`) — the r90/r95 class; file now 4684 lines, incl. 1 `r98s` row from the scout | disclosed, not hidden; no CLI deletes them |

---

## 7. Remaining `[?]`, risks, blockers

1. **B1 (blocker for a true baseline): no quiet arm exists on this host.** The
   ambient loadavg never fell below ~56 during this seat (foreign orphaned
   hogs). The load arm's delta (+16 hogs, loadavg 76–84) changed **no** verdict
   field — cadence, xruns, rc lattice, geometry, capture pins are identical —
   so the laws are load-robust as far as this host can tell, but a
   zero-contention baseline is unavailable. Any future "quiet" claim on this
   host must be qualified the same way.
2. `[?]` The 13375-frame/`requested=30` excursion was fingerprinted, not
   witnessed in the act: no `pw-top` sample was taken at that instant. The
   mechanism (graph rate 44100 + 48000 stream) is proven in the sandbox; the
   *shared-graph* cause (which client held the rate) is not.
3. `[?]` Why a foreign rate change coincides with unlinked legs is not resolved
   (link teardown/recreate race in WP vs. adapter renegotiation). Reproducing it
   deliberately would need a private core with a controllable rate flip while a
   stream is live.
4. `[?]` The **duplicate Link object** on fallback arms is pinned as an
   observation (with ids and ports) but not explained; `prepare-link.lua`'s
   `was_handled`/reconnect path is the prime suspect.
5. `[?]` `requested` under rate mismatch is *unstable across windows*
   (796 in the shared graph 6/6, 738 in the sandbox 2/2, 30/31 at 44100) — any
   author row must not pin it in the mismatch case.
6. `[?]` The sandbox private WirePlumber **enumerated and probed the host's PCI
   HDMI sink** (`alsa_output.pci-0000_01_00.1.hdmi-stereo.9`) while it ran — a
   bounded, disclosed side effect (no audio routed, no default changed, core
   stopped, socket gone). A future sandbox should disable the ALSA monitor in
   its private WP config.
7. `[?]` The sandbox WP has a startup race (first legs of a fresh private core
   can land unlinked, e.g. 3/3 paused in the first ratios variant); rep counts in
   `sandbox-ratios.json` should be read as "streaming reps only".
8. **Not measured (bounded scope):** `pw_stream_return_buffer`,
   `pw_stream_emit_event`, `pw_stream_set_control`, `pw_stream_new_simple`,
   freewheel/lazy, `DRIVER` as an actual driver, and the exact dereference behind
   the `media.class` SIGSEGV (crash *class* is now 32/32; the frame is not).

*boundary leaf — attacked, measured, not judged.*
