# R96 boundary — the pulse client surface replayed under load and four axes

Seat: **BOUNDARY (executor-class leaf, falsification)**. Host `plazir27`, window
**2026-10-15 20:53–21:17Z** (17:53–18:17 local, UTC−3). Repo
`~/Projects/shokunin/audio-shokunin` @ entry HEAD **`51a98e54`** → exit HEAD
**`cd70263f`** (siblings landed r94 boundary, r98 boundary, r95 boundary and the
r82 reviewer during the window). Toolchain re-verified: `pactl`/`pacat`
**17.0-98-gb096** (libpulse 17.0.0, protocol 35), pipewire-pulse 1.6.8, server
`PulseAudio (on PipeWire 1.6.8)` v15.0.0, Python 3.14.7, gcc 16.1.1.

**Conditions.** Two full replays of the scout's armed cells, fresh process every
rep:

- **Q** — no own hogs; foreign load only. Per-leg loadavg **59.1–84.5**
  (median 65.1). The host was *never* quiet: ~60 foreign `yes` processes plus
  live sibling seats (r95-boundary 14 own hogs, r93/r97/r99/r90 lanes).
- **L** — **12 own CPU hogs** (own PIDs, recorded; `start_new_session`), leg
  loadavg **67.6–149.1** (median 101.2, peak 148.19 at stop).
- Spot cells after the two arms: `post` / `postload` (parse-law and quantum
  retests; postload also used 12 own hogs).

**Discipline.** Object namespace `r96b_*` only. Modules unloaded **by exact id
after a name+args guard** (`module-null-sink` + `r96b_ns` in args). Kill
discipline: hogs by recorded PID list; probe processes by `/proc` cmdline path
match (`corpus/live/r96-boundary/probes/`) — no namespace-blind sweep (r95
incident precedent honored). **No `pactl set-default-*`/`wpctl set-default`
ever issued.** `clock.force-quantum`/`clock.force-rate` were set for short
windows and restored to `0`, verified in the same receipts and at exit.
**Zero tracked writes; nothing committed.** The only tracked-dirty file is the
pre-existing sibling-owned `corpus/fixtures/measure_audio.py` (mtime 18:09
local, +2263 lines — a sibling battery; never read/imported/executed here).
Exit census: **0 `r96b` sinks/sources/modules/nodes, 0 seat processes**.

**Labrat: not dispatched** (frozen `probeParent` budget retained). The assigned
attack resolved to on-host measurement; the one residual mechanism question
(why `pulse.attr.*` can be missing on an already-visible stream) was settled by
reading the version-matched source directly (§9).

**Headline.** The scout's four sharp edges survive: the buffer-attr law is
**244/244 rows exact** across both load conditions, two graph-quantum values, a
forced rate, and all flag orders; the target-miss asymmetry is real; `trigger`
still cannot start a corked stream; `prebuf=0` + starvation still goes
permanently silent. Three scout statements do **not** survive: (a)
`pa_stream_get_latency` does not "return 0" — every one of **676** client calls
returns **−16 (`PA_ERR_NODATA`)** and the `0` the scout reported is the
uninitialized caller variable (the return value was discarded); (b) the
`--format=f32le` "frame-size-4 falsifier" was **never measured** — the scout's
own receipt shows 3/3 `rc 1 Invalid sample specification` and zero rows; (c) the
"uncork resumes in 15–33 ms" window is not a law — fresh-process onsets ranged
**−10.8…36.0 ms** across the two conditions. Two load-only findings extend the
surface: the `pulse.attr.*` props are set by a **second** `pw_stream_update_properties`
call after the node is already visible, so under contention introspection can
catch a stream *before* its attrs exist (11 rows) and `paplay` can hang past the
9 s bound (7 legs, all `rc −9`); and `prebuf=0` starvation silenced a stream
**from the first chunk** (0 nonzero frames) in one L rep, not merely after it.

---

## 0. Verdict table

| # | r96 scout claim (report §) | verdict | sharpest fact from this seat |
| --- | --- | --- | --- |
| 1 | `pacmd`/`pa-info` absent; `paplay`/`parec` are symlinks to `pacat`; `pactl` lacks `kill-sink-input`/`kill-source-output`/`dump` | **CONFIRMED** | `which` empty for all four; `paplay -> pacat`/`parec -> pacat`; pacat sha `e584711d…`, pactl `9868ce72…`; the three verbs `rc 1 No valid command specified` (`r96b_cli_avail_post.json`) |
| 2 | `PULSE_SERVER` 5-shape lattice; empty string → `Invalid server`; bogus host ~7.5 s DNS wall; `PULSE_COOKIE=/dev/null` warns but connects | **CONFIRMED + extended** | walls **7.75/7.83 s (Q)** and **7.84/8.01 s (L)**; empty → `Invalid server` 3/3 both; cookie warning + `rc 0` 3/3 both; **new shapes**: `tcp6:[::1]:4713` refused, `unix:…/pulse/native/` (trailing slash) **refused** (`r96b_cli_server_{quiet,load}.json`) |
| 3 | `-s` beats `PULSE_SERVER` both directions; `PULSE_CLIENTCONFIG` honored | **CONFIRMED + extended** | 3/3 each direction; bad `default-server` refuses 3/3; `default-sink` steers when no device is named (3/3 both) but does **not** rescue a named-but-missing `PULSE_SINK`; **new**: `pactl info -s …` (global option *after* the subcommand) `rc 0` 2/2 both |
| 4 | Playback target miss falls back silently to the default; capture miss refuses (`No such entity`) | **CONFIRMED** | playback `rc 0` + literal `target.object` + landing on the *runtime* default 3/3 both; `parec -d no_such_r96b` `rc 1 Stream error: No such entity` 3/3 both. Destination identity is volatile (§4) |
| 5 | A numeric device string resolves by sink index server-side | **CONFIRMED** | own C client passes `--device 163848` verbatim → lands `r96b_ns`, `target.object` canonicalized to `r96b_ns` 3/3 (Q and postload); bad index/missing name → fallback with the literal string (`r96b_cork_resolve_*.json`) |
| 6 | Buffer-attr law is source-exact, 46/46 rows | **CONFIRMED (law) / OVERSTATED (row set)** | **244/244** boundary rows exact (Q+L+quantum+rate+order, frame sizes 2/3/4); but the scout's `d_f32_100` arm produced **no row at all** in its own receipt (3/3 `rc 1 Invalid sample specification`) — corrected `float32le`/`s24le` arms measured instead |
| 7 | `prebuf = tlength + frame_size − minreq` | **CONFIRMED** | every default-attr row, frame sizes 2/3/4 (e.g. `float32le` default 384000/380164/3840/8192; `s24le` 288000/285123/2880/8192) |
| 8 | `PULSE_LATENCY_MSEC` beats `--latency-msec` in both orders; invalid values silently ignored | **CONFIRMED + parse law pinned** | env 250 + flag 100 → `13920/12002/1920/5040`; inverse → `6720/4802/1920/1440`; parse law (`pa_atou`): `0x64`→100 ms, `0100`→100 ms, `007`→7 ms; `0X64`, `00x64`, ` 100`, `\t100`, `+100`, `+0x64`, `-0x64`, `100.5`, `1e3`, `99999999999`, `""`, `abc`, `0`, `-5` → default row, `rc 0`, no stderr |
| 9 | CLI `--property` lands verbatim; `application.name`/`media.name` win here | **CONFIRMED + extensions** | 3/3 byte-identical both conditions; duplicate key → **last wins**; empty value lands as `""`; `--stream-name` vs `--property=media.name` → **last one wins** (order-dependent); env `PULSE_PROP=application.name` loses to the CLI 3/3 |
| 10 | `--property=state.restore-props=false` suppresses the WirePlumber restore row | **CONFIRMED for playback *and* capture** (resolves scout `[?]` #6) | row count 13→13 across the leg + 1.6 s debounce, both conditions; total rows stable 4684→4684 (`r96b_cli_props_{quiet,load}.json`) |
| 11 | Cork = server-side node pause + `pulse.corked`; uncork resumes in 15–33 ms | **mechanism CONFIRMED / timing FALSIFIED** | `Corked: true` + `pulse.corked=true` while held; onsets **27.9/35.6/34.4 (Q)** and **36.0/−10.8/20.0 (L)** — a sign flip, not a window; nonzero frames 67909…68893 |
| 12 | `trigger` does not uncork | **CONFIRMED** | 3/3 Q and 3/3 L: `nonzero = 0`, `peak = 0` over the full capture |
| 13 | prebuf is not an audible-start gate; `prebuf=0` + starvation is permanently silent | **CONFIRMED + extended** | default prebuf slow feed plays **55099** frames 3/3 both; `prebuf=0` slow feed **2645/2645/4612 (Q)** and **2645/2645/0 (L)** — one load rep was silent from the *first* chunk |
| 14 | Record cork works the same way | **CONFIRMED** | `readable` 0 while corked → **86400/86400/81600**, drained **52800** 3/3 both |
| 15 | Every latency field the introspection exposes is hardcoded zero | **PARTIAL — introspection CONFIRMED, client query FALSIFIED** | `pactl` JSON fields `buffer_latency_usec 0.0` / `sink_latency_usec 0.0` / `source_latency_usec 0.0`; but **676** `pa_stream_get_latency` calls all returned **−16** (`PA_ERR_NODATA`), 80 at ready, 80 at final, 516 mid-run |
| 16 | For native streams `Corked:` is a node-state projection | **REFINED / re-measured** | starved linked native `pw-play --raw` stream *is* visible as a pulse sink-input: `Corked: false`, no `pulse.corked`, node `running`, `stream.is-live=true`, `target.object=r96b_ns` (Q and L). The scout's own receipt's cell was **empty**; its cited `runs/native_idle_corked.txt` is pw-dump node props |
| 17 | Cork/uncork emits exactly one `change`; piped subscribe is block-buffered | **CONFIRMED** | timestamped `stdbuf -o0` trace: `new` + 2 `change` at creation, **exactly one `change` at uncork** (t≈1.55 s), `remove`; creation emits 2–3 changes, not a fixed count |

---

## 1. What was replayed and how much

43 receipts, **596 leg results**, **388 stream rows**, 205 files / 13 MB under
`corpus/live/r96-boundary/`. Every leg is a fresh process, bounded (wall cap +
`start_new_session` + `killpg` + byte caps + `RLIMIT_CORE=0`), and carries its
own loadavg. Replayed: availability, the 13-leg server lattice, the 16-arm
target lattice, the full latency/attr matrix (plus 7-point `PULSE_LATENCY_MSEC`
sweep and both frame-size-4 falsifiers), properties (6 arms), introspection
(full text + short forms + native stream), cork/trigger/prebuf/record/subscribe,
device resolution via the own C client — under **both** conditions — then the
axes: CLI flag order, `PULSE_CLIENTCONFIG` default-node state, PipeWire
`clock.force-quantum` (256, 2048) and `clock.force-rate` (44100), sibling-object
targeting, and the sharpened parse-law cells.

The C client (`probes/r96b_pulse`, a copy of the scout's with three additive
changes: `r96b_` label default, `--amp`, `--latency-mid` sampling **with the
return code recorded**, and a `state.restore-props=false` proplist so it leaves
no restore rows) is the instrument for every timing/`latency_rc` claim.

---

## 2. The buffer-attr law survives everything (244/244)

`runs/analysis-bufferattr.txt` re-checks every measured `pulse.attr.*` row
against the same source transcription the scout used
(`pulse-server.c:434-525`, constants `:60-65`): **244/244 exact** —
tlength, prebuf, minreq and `node.latency`, across:

- **Q** 68/68 rows, **L** 54/54 rows (fresh processes, loadavg 59–149);
- `clock.force-quantum` 256 (8/8), 2048 (6/6 Q, 8/8 L, 8/8 post, 8/8 postload);
- `clock.force-rate` 44100 (4/4) — `clock.rate` stayed 48000
  (`allowed-rates=[48000]`), the forced value never reached the graph;
- CLI flag order (8/8 quiet, 8/8 load): `--latency-msec` before/after
  `--device`, and `--process-time-msec`/`--latency-msec` in both orders
  (`5312/4802/512/2144` identical);
- corrected frame-size falsifiers: `float32le` default
  `384000/380164/3840/8192` and 100 ms `13440/9604/3840/1440`; `s24le`
  default `288000/285123/2880/8192` and 100 ms `10080/7203/2880/1440`.

**MAXLENGTH clamp** (new): `PULSE_LATENCY_MSEC=100000` (9.6 MB request) →
`tlength 4177920` (4 MiB rounded down to frame, minus the 16384 B ADJUST
latency), `prebuf 4176002`, `node.latency 8192/48000`, `rc 0` 2/2 both.

**Parse law** (new, from the fetched `pulsecore/core-util.c:2299-2397`):
`prepare_number_string` rejects a leading `isspace`, `+`, or (for `NUMTYPE_UINT`)
`-`; strips leading zeros **unless the string starts with lowercase `0x`**;
then `strtoul(…, 0)` full-string with a `UINT32_MAX` bound. Measured exactly:
`0x64`→100 ms, `0100`→100 ms (decimal, **not** octal 64), `007`→7 ms,
`0X64`/`00x64`→rejected (the `x` check is case-sensitive / the zero-strip eats
the prefix), ` 100`/`\t100`/`+100`/`+0x64`/`-0x64`/`100.5`/`1e3`/`99999999999`
→ default row, `rc 0`, silent.

**Scout row-set correction.** The scout's `d_f32_100` arm
(`--format=f32le`) never produced a stream: in the scout's **own** receipt
`r96s_cli_latency.json` all three reps are `rc 1` / `Invalid sample
specification` / **0 rows**. The report's §5 table and claim 6 nevertheless
cite `13440/9604/3840/1440` for it — those numbers were never measured (they
are the stereo row's values). The frame-size dependence is real; the corrected
arms above measure it on `float32le` (frame 4) and `s24le` (frame 3).

---

## 3. Server-resolution lattice — 16 legs, both conditions

`runs/analysis-server.txt` (verbatim stderr in the receipts). All rc/stderr
classes reproduce; the only quantitative shift is the DNS wall:
`b_host_bogus` **7.8271/7.7532 s (Q)** and **7.84/8.0068 s (L)** vs the scout's
7.49/7.50 s. New shapes: `tcp6:[::1]:4713` → refused; `unix:…/pulse/native/`
(trailing slash) → refused with `pa_context_connect() failed` — the bare path
and the `unix:` prefix both work, the trailing slash does not. `pactl info -s
<server>` (global option after the subcommand) works `rc 0` 2/2 both
conditions; `pactl info --server=…` also `rc 0`.

---

## 4. Targeting, fallback and the (contended) default-node state

Playback-miss and capture-miss behaviour reproduce 3/3 in both conditions.
The scout's "record the name landed on" rule earned its keep: during **L** the
runtime default sink moved repeatedly — the USB `HiFi__SPDIF__sink` disappeared
from the main instance while the kernel card remained present
(`/proc/asound/cards` still lists `USB-Audio`; the `r97-boundary` private
PipeWire process held **no** ALSA fds when checked, so that lane is not the
demonstrated cause) and WirePlumber re-registered duplicates with `.N` suffixes. Our
legs recorded the session default at each rep: `hdmi-stereo.55/.59/.60/.61/.64/.65/.67/.70`,
`SPDIF__sink.5`, and **`r96b_ns` itself** (the default flapped to our own seat
sink six times). `c_source_default` under L even returned `rc 1 No such entity`
once and landed on `hdmi-stereo.59.monitor` another time. This matches the
r95-boundary seat's independently observed `hdmi-stereo.6 → SPDIF.5` /
`SPDIF.24 → hdmi-stereo.99` churn (their §contention). **The law is the
mechanism — silent fallback to the runtime default at link time — never the
destination identity.**

**Default-node axis without `set-default-*`:** a client-side
`PULSE_CLIENTCONFIG` `default-sink=r96b_ns` steers an *unnamed* stream to
`r96b_ns` (`target.object=r96b_ns`, 3/3 both), but an unresolvable
`PULSE_SINK=no_such_r96b` is **not** rescued by it — the fallback still lands on
the runtime default (`SPDIF` in Q, `hdmi-stereo.6` in L). So the two "defaults"
are independent: the client-conf default is applied client-side when no device
is named; the server-side miss fallback consults the session manager.

**Sibling-object targeting:** at the time of the target battery no foreign
`r9*_ns` sink was registered in the default instance (r92b_in had just been
unloaded; r93b_in appeared later), so `c_foreign_target` was not armed; the
`c_foreign_target_note` receipts record that. Foreign sinks *were* observed in
the censuses (`r92b_in`, `r93b_in`, `r93b_fc_in`, `r98b_ns`, `r98b_ns2`,
`r98b_stall`, `r95b_info`) — none was touched.

---

## 5. Properties

All six scout property findings reproduce in both conditions
(`r96b_cli_props_{quiet,load}.json`): the `--property` vector lands verbatim
(`application.name=r96b_prop`, `media.name=r96b_streamname`,
`media.role=game`, `zzz.invented=42`); `--property=noequals` `rc 1` and no
stream; `--client-name` → `application.name`; CLI wins over `PULSE_PROP` env.
Extensions: duplicate key → **last wins** (`media.role=second`); empty value
lands as `""`; `--stream-name` and `--property=media.name` are **last-wins**
(property-first → flag wins; flag-first → property wins); `state.restore-props=false`
suppresses the WirePlumber row for **capture** streams too (13→13 tag rows,
4684→4684 total, +1.6 s debounce) — the scout's `[?]` #6 is closed.

---

## 6. Cork / trigger / prebuf / record / subscribe

| arm | Q | L | scout | verdict |
| --- | --- | --- | --- | --- |
| cork onset (ms, rel. client uncork event) | 27.9 / 35.6 / 34.4 | 36.0 / **−10.8** / 20.0 | 15.1 / 32.7 / 32.5 | window falsified; mechanism holds |
| cork nonzero frames | 68893 / 68893 / 67909 | 67909 / 67909 / 68893 | 68893 / 68893 / 67909 | identical set |
| trigger nonzero frames | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | confirmed |
| prebuf default slow feed | 55099 ×3 | 55099 ×3 | 55099 | confirmed |
| prebuf=0 slow feed | 2645 / 2645 / 4612 | 2645 / 2645 / **0** | 2645 / 2645 / 4612 | confirmed + first-chunk silence |
| prebuf=0 fast feed | 38385 ×2 | 38385 ×2 | 38385 | confirmed |
| prebuf default fast feed | 38384 ×2 | 38384 ×2 | (not armed) | control |
| record readable corked→uncorked | 0 → 86400 ×3 | 0 → 86400 / 86400 / 81600 | 0 → 86400 | confirmed; drained 52800 ×3 both |

**Subscribe** (timestamped, `stdbuf -o0`, L): `new` + 2 `change` at creation
(0.53–0.56 s), **one `change` at uncork** (1.55 s), `remove` (2.35 s); Q count
is the same shape with 3 creation changes. The scout's "3×change at creation"
is not fixed; "exactly one change per uncork" is.

---

## 7. Latency: introspection is zero, the client query is an error

`pactl` JSON exposes `buffer_latency_usec 0.0`, `sink_latency_usec 0.0`,
`source_latency_usec 0.0` in every snapshot — the hardcoded-zero claim stands
for the **introspection fields**. The scout's other half — "`pa_stream_get_latency`
also returns 0" — is **falsified**: the instrumented client called it **676**
times (80 stream-ready, 80 final, 516 mid-run samples at ~5 Hz across cork,
trigger, prebuf and record legs) and **every call returned −16
(`PA_ERR_NODATA`)**; `usec` stayed at the caller's `0` initializer because the
scout's code (and ours, at ready/final, before the change) discarded the return
value. Mid-run sampling was the scout's `[?]` #7 — it never once succeeded.

---

## 8. Native-stream `Corked:` (claim 16, re-measured)

The scout's *receipt* cell for this was empty (`f_native_idle_corked.rows = []`);
its cited `runs/native_idle_corked.txt` is a pw-dump node-props listing, not a
`pactl` row. Re-armed with `pw-play --raw` on a FIFO held open with `O_RDWR`
(without `--raw`, pw-play blocks in format sniffing and creates **no** stream —
a trap the scout's harness may have hit): the starved stream **is** visible as a
pulse sink-input — `Corked: false`, `stream.is-live=true`,
`node.latency 4800/48000`, **no `pulse.corked` prop** — while `pw-dump` shows
the node `state: running` (Q and L, two samples 1 s apart). The code path
(`pulse-server.c:4129-4132`: prop if present, else `state != RUNNING`) is thus
observable as stated; only the scout's evidence path was mislabelled.

---

## 9. Axes

- **PipeWire quantum** (`clock.force-quantum` 256 and 2048, restored to 0 and
  verified): the attr law is unchanged (all rows exact). The lever is a
  *no-op for this surface*: the pulse attrs are computed from the client
  request and the source constants (`QUANTUM_LIMIT = 8192` frames), and the
  active graph is the null-sink graph — `pw-top -b` shows `QUANT=0` for every
  node (no driven quantum), so the forced value has no witness in the pulse
  path. One anomaly cluster (below) happened to fall in the first 2048 window.
- **Rate** (`clock.force-rate 44100`): `clock.rate` stayed 48000
  (`allowed-rates=[48000]`); the forced value never reached the graph; attrs
  unchanged (4/4).
- **CLI flag order**: `--latency-msec` before/after `--device` identical;
  `--process-time-msec`+`--latency-msec` identical both orders
  (`5312/4802/512/2144` — a combined cell the scout never armed; both requests
  apply: minreq from process-time, tlength+ADJUST from latency);
  `pactl info -s …` accepted after the subcommand; `paplay FILE --device=…`
  accepted after the positional file (GLib parses options after positionals).
- **Default-node state**: see §4 (client conf vs runtime default; no
  `set-default-*`).
- **Sibling presence**: whole window overlapped r95-boundary (whose census saw
  our `r96b` sinks and `pacat`→`r96b_ns` streams), r97-boundary (private
  PipeWire holding the USB ALSA device), r93-boundary, r99-scout, r90-author
  battery, game-dev-3d. Their load is in every loadavg receipt; the default
  churn is theirs, not ours.

---

## 10. Anomalies under contention (new)

1. **Late `pulse.attr.*` props.** 13 measured rows show a live stream row
   (`pulse.corked`, `node.latency`, `target.object`, `application.*`) with **no
   `pulse.attr.*` props at all** — 9 during L, 2 in the post window (loadavg
   143–144), 2 in the first quantum-2048 window. Source anchor:
   `set_playback_buffer_attr` runs `pw_stream_update_properties()`
   (`pulse-server.c:555`) *after* the stream node is registered, so the node is
   introspectable before its attrs land; the window widens with scheduler
   contention. Consequence for authors: never read `pulse.attr.*` from a single
   early snapshot and treat absence as "no attr law" — re-snapshot or check
   `node.latency` as the presence witness.
2. **Hung legs.** 7 legs exceeded the 9 s bound and were `SIGKILL`ed
   (`rc −9`): 6 in L (loadavg 71–108), 1 in the post window (loadavg 144).
   `paplay` of a 1.5 s file hung; the stream row was present. Both classes are
   nondeterministic — the same cells passed 3/3 elsewhere, including at
   loadavg 138.
3. **`prebuf=0` can be silent from the first chunk** (L rep: 0 nonzero frames
   vs 2645 in the other two) — the stall's onset is not always after the first
   fed chunk.

---

## 11. Falsification list (what was tried that could have killed each claim)

| claim attacked | falsifier attempted | outcome |
| --- | --- | --- |
| `pa_stream_get_latency` returns 0 | instrumented client, rc recorded, 676 calls incl. mid-run | **FALSIFIED** — all `−16 PA_ERR_NODATA` |
| the `--format=f32le` arm falsified the byte reading of the law | re-run + read the scout's own receipt | **FALSIFIED as evidence** — 3/3 `rc 1`, 0 rows; corrected `float32le`/`s24le` arms measured instead |
| uncork resumes in 15–33 ms | 6 fresh-process reps, Q and L | **FALSIFIED as a window** — −10.8…36.0 ms |
| the buffer-attr law is load-sensitive | 54 L rows + quantum/rate/order axes | **CONFIRMED immune** — 244/244 exact |
| invalid `PULSE_LATENCY_MSEC` values are "ignored" (parse unknown) | 15 parse cells + fetched `pa_atou` | **refined to a parse law** — hex/zero-strip accepted, space/sign/case rejected |
| the fallback destination is the pulse default | legs record the session default per rep | **refined** — it is the runtime default at link time; it moved 10+ times in L (foreign) |
| `PULSE_SINK` miss is rescued by client-conf default | `PULSE_CLIENTCONFIG` + miss | **falsified** — miss still falls back to the runtime default |
| native streams are invisible to pulse introspection | `pw-play --raw` starved stream | **falsified** — visible sink-input, `Corked: false`, no `pulse.corked` |
| creation emits a fixed number of `change` events | timestamped subscribe, Q+L | **refined** — 2–3 at creation, exactly 1 at uncork |
| `prebuf=0` silence starts after the first chunk | 3 L reps | **refined** — one rep was silent from frame 0 |
| the seat perturbs host state | census before/after, module guard, metadata restore | only disclosed items: 13 restore rows, 12 hog PIDs, short metadata windows |

---

## 12. Author directives

**Verbatim-ready cells** (≥2 reps each, both conditions unless noted; exact argv
in the receipts):

1. **Latency-query negative.** `pa_stream_get_latency` → `−16` in 676/676
   calls; `pactl` latency fields `0.0`. (`r96b_cork_*.json`, instrumented
   `probes/r96b_pulse.c`.)
2. **Parse law.** `0x64`→100 ms, `0100`→100 ms, `007`→7 ms; `0X64`/`00x64`/
   `+100`/`-0x64`/` 100`→default; source cite
   `pulseaudio-v17.0 core-util.c:2299-2397`. (`r96b_cli_latency_*`,
   `r96b_cli_extra2_*`.)
3. **Frame-size falsifiers (corrected).** `float32le` 100 ms
   `13440/9604/3840/1440`; `s24le` 100 ms `10080/7203/2880/1440`; `f32le` is
   **invalid** in this pacat (`Invalid sample specification`).
4. **MAXLENGTH clamp.** 100000 ms → `4177920/4176002/1920`, latency
   `8192/48000`.
5. **Fallback law + moving destination.** Playback miss → silent fallback,
   `target.object` literal, destination = runtime default (record it);
   capture miss → `rc 1 No such entity`.
6. **Default-node axis.** client-conf `default-sink` steers unnamed streams;
   it does not override a named-but-missing `PULSE_SINK`.
7. **Cork timing is not a window.** Onsets −10.8…36.0 ms across 6 reps; use
   nonzero-frame counts (67909–68893) as the stable witness.
8. **Trigger negative.** 0 nonzero frames 6/6.
9. **prebuf table.** default slow 55099 ×6; zero slow 2645/2645/4612 +
   2645/2645/0; fast controls 38384/38385.
10. **Subscribe.** one `change` per uncork, 2–3 at creation, `stdbuf -o0`.
11. **Late-attr race.** 11 rows without `pulse.attr.*`; source anchor
    `pw_stream_update_properties` after registration.

**Bimodal / envelope cells** (do not pin): uncork onset; fallback destination
identity; creation `change` count; hung-leg rate under load; `prebuf=0` stall
onset.

---

## 13. Contention ledger + exit state

| window | contact | effect |
| --- | --- | --- |
| whole window | foreign lanes: ~60 `yes` (not ours), r95-boundary (14 own hogs + full boundary battery 20:52–21:09Z), r97-boundary (private PipeWire; no ALSA fds when checked), r93-boundary (`r93b_in`, `r93b_fc_in`), r99-scout, r90-author battery, game-dev-3d, run_battery | read-only contact; their rows appear in our censuses; our sinks/streams appear in theirs (their report names `r96b` sinks and `pacat`→`r96b_ns`) |
| ~21:00–21:15Z | **runtime default sink/source churn**: USB SPDIF vanished from the default instance; default became `hdmi-stereo.NN` with WirePlumber `.N` re-registration suffixes; default source flapped to an HDMI monitor; for six of our reps the runtime default was our own `r96b_ns` | destination identity in §4 is a moving target; never pinned; no `set-default-*` issued by this seat |
| whole window | `corpus/fixtures/measure_audio.py` tracked-dirty (sibling, mtime 18:09 local, +2263 lines) | not read/imported/executed here |
| 20:53–21:17Z | this seat: 596 bounded legs, 1 null sink module (unloaded by id+guard), own C client, 12 own hogs (recorded, killed), 4 metadata windows (restored) | own residue: 0 r96b objects, 0 processes; 13 `r96b_*` rows left in `~/.local/state/wireplumber/stream-properties` (r90 class: no CLI delete; C-client legs after the proplist change leave none) |
| exit | `pactl list modules short \| grep r96b` = 0; `pw-dump` r96b nodes = 0; seat procs = 0; `clock.force-quantum=0`, `clock.force-rate=0`, `clock.quantum=1024`, `clock.rate=48000` | clean (census `r96b_census_exit.json`) |

---

## 14. Artifacts & provenance

`corpus/live/r96-boundary/` (untracked, 205 files, 13 MB, `manifest.sha256`
205 lines):

- `probes/`: `r96b_lib.py`, `r96b_census.py`, `r96b_hogs.py`,
  `r96b_cli.py` (battery A + `extra`/`extra2`), `r96b_cork.py` (battery B),
  `r96b_axes.py`, `r96b_native.py`, `r96b_analyze.py`, `r96b_teardown.py`,
  `r96b_synth.py`, `r96b_pulse.c` + `r96b_pulse` (final binary sha
  `b3a48fd822e55108…`; the pre-instrumentation build was `c82ec183…`).
- `receipts/`: 43 JSON — `r96b_cli_{avail,server,target,latency,props,introspect,extra,extra2}_{quiet,load,post,postload}`,
  `r96b_cork_{cork,trigger,prebuf,record,subscribe,resolve}_*`,
  `r96b_axes_{order,quantum_256,quantum_2048,rate_44100}_*`,
  `r96b_native_{native_idle,client_short}_*`, `r96b_census_{entry,exit}.json`.
- `runs/`: `analysis-{bufferattr,server,target,cork,props,anomalies}.txt`,
  `analysis-summary.json`, `batteryA_*.log`, `batteryB_*.log`.
- `scratch/`: own tones, 25 monitor captures (`cap_*.wav`, exact frame count),
  client configs, FIFO.
- Sources read (not written): `corpus/live/r96-scout/sources/*` (scout-fetched,
  version-matched) plus `pulseaudio v17.0 pulsecore/core-util.c` fetched to
  `/tmp/core-util.c` for the `pa_atou` transcription (sha not in the corpus;
  the parse cells are the on-host witness).

Report: `reports/round-96/r96-boundary.md` (this file).
