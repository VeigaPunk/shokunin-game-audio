# R98 scout — the native `pw_stream` C API (libpipewire 1.6.8), measured with an own C client

Round 98 **capstone surface sweep**. Host `plazir27`, measured **2026-10-15
20:06Z → 21:2xZ** (host local UTC−3). Repo `~/Projects/shokunin/audio-shokunin`
@ entry HEAD `1abd9549`, exit HEAD `fd0bc8b0` (sibling commits landed during the
seat: `fd0bc8b0 r87 boundary`, `aa03c347 r82 author`, `1278e964 r89 boundary`,
`e8a0600b r86 boundary`, `4653c135 r88 boundary` — none is this surface).
Toolchain: PipeWire **1.6.8** (`1:1.6.8-1`), WirePlumber **0.5.17-1**,
libpulse **17.0-98-gb096** (protocol 35), gcc **16.2.1+r23**, Python **3.14.7**,
Linux **7.2.3-arch1-3**. All probe legs ran against `libpipewire-0.3` 1.6.8
(`pkg-config --modversion` = 1.6.8).

**Seat: SCOUT (leaf). Zero tracked-file writes.** Entry tracked-dirty set was
two sibling-owned files (`corpus/fixtures/measure_audio.py` + its `.pyc`), which
a sibling committed mid-session (`aa03c347 r82 author`); this seat made no
tracked edit at any point, and the index shows only sibling staged files plus
this seat's untracked additions (`corpus/live/r98-scout/`, `reports/round-98/`).
The only files written outside `corpus/live/r98-scout/` are this report. Every
object created is `r98s_*`;
the private null-sink was loaded/unloaded by name-verified module index; **no
`pactl set-default-*` was ever issued**; audio was silence except the bounded
tone legs, and those targeted only the private null-sink. Exit census: **0
`r98s` nodes, 0 `r98s` modules, 0 seat processes**; defaults SPDIF/Line
unchanged. One persistent residue remains and is disclosed in §5 (1
`stream-properties` row, the r90/r95 class).

**Label legend.** `[O]` = directly observed on this host in this window;
`[I]` = read from the version-matched upstream source (fetched over the network,
URLs + shas in `sources/`) or installed 1.6.8 headers; `[?]` = not resolved.

---

## 0. Why this surface (the pick, and what it displaces)

Every other client class on this host has been measured: CLI consumers (r73–r79),
GStreamer (r81), ffmpeg (r82), pw-loopback (r79), filter-chain (r92), JACK via
`pipewire-jack` (r95), control planes (r86/r88/r89/r90). The one thing **never
built in 97 rounds is a native `pw_stream` client** — the C API every one of
those clients rides. Grep of `corpus/live/**` for `pw_stream_connect` finds only
GStreamer/wpexec internals and two report sentences (r91: *"the pw_stream
internals would need a …"*; r92 §S4: a `pw_stream_connect()` refusal seen
through `wpexec`). This seat closes that gap with `probes/r98stream.c`
(own client, modes: info/state/run/stall/flags/time/drain/neg/props/cap/error).

Named gaps it closes or attacks:

- **r89 §11** — *"xrun/fault injection: no underrun was ever induced; xrun
  semantics untested"* → §3.12: induced, counted, linear, reproducible.
- **r91 §** — the `pw_stream` state machine/flags were inferred from gst/CLI
  witnesses → §3.1/§3.2: measured natively, with `stream.c` anchors.
- **r92 §S4** — the `media.class` direction refusal was a `wpexec`-level
  death → §3.9: the native shape is *worse* (client SIGSEGV).
- **r95** — JACK is a *projection* of this API; the projection's broken families
  (xrun callback, RT accessors) are now contrasted with the native path.
- **r86/r88** — `pw-top` ERR column was only ever seen at 0 (plus the standing
  SPDIF 937) → §3.12 exercises it.

Displaced candidates: pw-top/graph introspection (r86 §7 + r88 + r89 cover the
CLI lattice), MIDI (r83 §3 + r87 §5 measure the CLI surface), bluetooth (r88 §6
absent-class, no device exists), file-format edges (r62–r74 + r85 + r85-boundary),
PulseAudio-native (r96, in flight this wave) and WirePlumber policy (r97, in
flight) — all smaller or already claimed.

---

## 1. Headline claims (native pins, each ×3 reps unless noted)

| # | claim | label | sharpest single fact | evidence |
| --- | --- | --- | --- | --- |
| 1 | **The client API is the daemon API: version/core agree, connect is a plain round-trip.** | `[O]` | `pw_get_library_version()="1.6.8"`; core name `pipewire-0`, version `1.6.8`, user `vgpnk`, host `plazir27`; `pw_context_connect` rc 0; core props carry `default.clock.quantum=1024`, `max-quantum=2048`, `min-quantum=32`, `rate=48000`, `quantum-limit=8192`, `clock.power-of-two-quantum=true`, `settings.check-quantum=false`, `link.max-buffers=16` | `battery-all.json` `info` ×3 |
| 2 | **Connect-then-bind state machine; the node id is *not* usable at connect time.** | `[O]`+`[I]` | `connect(NONE)` rc 0 → `unconnected→connecting→paused`; `pw_stream_get_node_id()` **immediately after connect = 4294967295** (SPA_ID_INVALID), valid only after the node global is bound (later reads 117/256…); `get_time_n` before running = **-5 (EIO)**; `disconnect` rc 0 | `state` ×3; `stream.c:1230,1257,2265` |
| 3 | **`AUTOCONNECT` is the gate; the graph then asks for 12-quanta buffers, not quantum-sized ones.** | `[O]`+`[I]` | no-autoconnect: `paused`, **0 callbacks**, only PeerCapability/Latency/Tag params. autoconnect+target: `streaming`, 6 callbacks/1.5 s, `datas[0].maxsize=49152` (**12288 frames**), `pw_buffer.requested=1024` frames, chunk 49152, stride 4, negotiated `Format` = **F32LE (283), 48000, mono**, 2 add_buffer events | `run_autoconnect` ×3, `run_no_autoconnect` ×3; `stream.c:449-477,693-700` |
| 4 | **Flag→prop projection is *only-if-absent*, and `DONT_RECONNECT` lands as r91's prop.** | `[O]`+`[I]` | after connect with `dont_reconnect`: props contain `node.dont-reconnect=true`, `node.autoconnect=true`, `node.loop.class=main`, `node.async=true`; with explicit `node.dont-reconnect=false` the prop **stays `false`** | `dont_reconnect` ×3, `dont_reconnect_false_prop` ×3; `stream.c:2087-2098` |
| 5 | **`INACTIVE` and `TRIGGER` both park the stream; activation/trigger are the only movers.** | `[O]` | `INACTIVE|AUTOCONNECT` → `paused`, 0 callbacks; `pw_stream_set_active(true)` rc 0 → `streaming` + callbacks. `TRIGGER` stream: 0 callbacks for 300 ms; each `pw_stream_trigger_process()` returns **rc 1** and yields a callback (trigger_count 29/30/30 over the run) | `inactive_activate` ×3, `trigger` ×3; `impl-node.c:1550-1555` |
| 6 | **`RT_PROCESS` moves the callback to a separate data-loop thread — but the thread is not RT-scheduled here.** | `[O]` | `proc_tid != main_tid`; `sched_getscheduler` = **1073741824** (`SCHED_OTHER|SCHED_RESET_ON_FORK`), prio 0, nice 0; without the flag `proc_tid == main_tid` (`node.loop.class=main`, `node.async=true` from the source) | `rt_process` ×3, `rt_nice` ×1, `run_autoconnect` ×3 |
| 7 | **Buffer geometry is fixed at 12288 frames; the *request* follows the quantum.** | `[O]` | `node.force-quantum=512`/`2048` on the stream → `requested`/`delay`/`size` = 512/2048, but `maxsize` **stays 49152 B** and callbacks still fire once per ~256 ms; s16 stream → `maxsize=24576` (same 12288 frames), stride 2, Format 259; the forced quantum also moved the **whole graph** (pw-top: null-sink driver `QUANT 512`) while the client lived | `quantum512` ×2, `quantum2048` ×2, `s16_format` ×1 + manual pw-top witness |
| 8 | **`pw_time` is queryable whenever the stream exists, and its fields are structural.** | `[O]` | streaming: `rate=1/48000`, `ticks` monotonic, `queued=12288` (= one queued buffer), `queued_buffers=1`, `avail_buffers=0/1`, `size=1024`, `delay=1024` (0 for the time leg's cadence); after `set_active(false)` `get_time_n` still rc 0; `is_driving=0`, `is_lazy=0` | `time` ×3, `run_autoconnect` ×3 |
| 9 | **`flush(drain=true)` rc 0, and `drained` is a repeating "queue empty" signal, not a one-shot completion.** | `[O]` | timer-driven flush at 804 ms → first `drained` at **1057 ms** (+253 ms ≈ one 12288-frame buffer); callback-driven flush → first `drained` at **+1 ms**; thereafter **every ~42.5 ms**, `n_drained` 34–40 in 1.7 s, **state stays `streaming`** (no PAUSED), no resume needed | `drain2` `drain_timer2` ×3, `drain_cb` ×3 |
| 10 | **The param lattice is PeerCapability/Latency/Tag/Format; `update_params` mid-stream is accepted silently.** | `[O]`+`[I]` | `param_changed` ids on a streaming stream = `20,15,17,20,15,17,4` = PeerCapability, Latency, Tag, **Format(4)**; `pw_stream_update_params(EnumFormat 44100)` while streaming → rc 0, **no** param_changed within 700 ms, stream continues (no visible renegotiation) | `run_autoconnect` ×3, `neg_stream` ×3; `param.h` |
| 11 | **`target.object` resolves by name/serial only; id and garbage fall back to the *default sink*.** | `[O]` | link witness: `target=<serial>` → link to `r98s_ns` ×3; `target=<object.id>` → link to `…SPDIF__sink` ×3; `target=no_such_r98s` → link to `…SPDIF__sink` ×3 (silent fallback; stream still `streaming`) | `target_serial`, `target_object_id`, `target_garbage` ×3 each (pw-dump snapshots) |
| 12 | **`set_rate` is `-ENOTSUP` only before the rate-match exists.** | `[O]`+`[I]` | pre-connect → **-95**; while streaming (linked, null-sink) → **rc 0** (the stream carries a rate_match / `rate` control by default) | `err_set_active_pre` ×3, `time` ×3 (re-run with live `set_rate`); `stream.c:2776-2782` |
| 13 | **Buffer lifecycle: dequeue/queue are rc-clean; `ALLOC_BUFFERS` hands you a NULL data pointer to fill.** | `[O]` | `dequeue` non-NULL, `queue` rc 0 (`dequeue_null=0`, `queue_err=0`); `ALLOC_BUFFERS` → `add_buffer … data=null` then the app sets it and streams (cb 5); `MAP_BUFFERS` → `data=set` | `run_autoconnect` ×3, `alloc_buffers` ×1, `map_buffers` ×1 |
| 14 | **Capture is real and sample-exact — but only with `stream.capture.sink=true` when targeting a sink.** | `[O]` | with the prop: `streaming`, 35 callbacks, 71680 frames, peak **0.499969**, Goertzel²@997 Hz **302 944 141.06** vs @440 Hz **4.54** — identical to the last digit ×3; without it: state **error "no target node available"** (rc 0) ×3; no target at all: same error ×4; explicit *source* target: `streaming`, 45056 frames, all-zero content | `cap_prop` ×3, `cap_noprop` ×3, `cap_default_source` ×4, named-source manual leg |
| 15 | **The error-path rc lattice is rich and rc is not a verdict (except connect-to-nothing).** | `[O]` | pre-connect: `set_active` **-5**, `get_time` **-5**, `flush` **-5**, `set_rate` **-95**, `disconnect` **0**, `dequeue` NULL; second `connect` **-16 (EBUSY)**; invalid direction 99 → connect **rc 0** then `connecting→unconnected` (no node); `connect` with 0 params → rc 0 + `paused`; `PIPEWIRE_REMOTE=r98s_nonexistent` → rc 1, `-112 (EHOSTDOWN)` | `err_*` ×3 each, `remote_bad` ×3 |

---

## 2. Falsifications (predeclared attacks, with outcomes)

| id | predeclared attack | outcome |
| --- | --- | --- |
| **F1** | "connect rc signals the `media.class` refusal" | **FALSIFIED — stronger failure.** `media.class=Audio/Sink` on a *playback* stream: connect rc 0, then the client **SIGSEGVs** (rc −11; shell 139) with output ending right after the port events. Reproduced **3/3** in the battery and **9/9** in direct shell/Popen runs; **0/7 under `gdb -batch`** (slower startup changes the race). Core-dump backtrace (`coredumpctl`, PID 3394626): `#0 libpipewire-0.3.so.0+0x768c9` (nearest export `pw_impl_port_set_mix+0x389`) ← `libspa-audioconvert.so` (5 frames) ← `libpipewire-module-client-node.so` ← `protocol-native` ← `pw_main_loop_run`. Source only warns (`stream.c:2121-2123`). The `media.class=Audio/Source` playback twin does **not** crash: rc 0, `paused`, no error. |
| **F2** | "node id is usable right after connect" | **FALSIFIED** — 4294967295 until bound (`stream.c:1230/1257`). |
| **F3** | "a stream without AUTOCONNECT still runs" | **FALSIFIED** — `paused`, 0 callbacks, no Format negotiation (param ids only 20,15,17). |
| **F4** | "NO_CONVERT + 44100 into a 48000 null-sink refuses at connect" | **FALSIFIED** — `NO_CONVERT|AUTOCONNECT` at 44100 → `streaming`, negotiated Format **44100**, `buffered=28`, `size=796`, `delay=1024`, 4 callbacks — and byte-identical to the *convert* arm (no conversion-related difference observable at this level). |
| **F5** | "`target.object` = `object.id` resolves like serial" | **FALSIFIED** — id → default-sink fallback ×3 (prior CLI law now native). |
| **F6** | "an explicit `node.dont-reconnect=false` loses to the flag" | **FALSIFIED** — prop stays `false` ×3 (only-if-absent law). |
| **F7** | "a stalled follower is invisible to xrun accounting" (the r89 named gap) | **FALSIFIED — gap closed.** A 300 ms stall in the RT process callback → pw-top `ERR` **27** (3/3) and pw-profiler follower `xrun_count` **27** (3/3), with statuses `awake`/`triggered`, `negative_wait` records 26, driver `xrun_count` 0. A 600 ms stall → follower `xrun_count` **55** (2/2), negative-wait 54, pw-top ERR 21 (mid-stall snapshot). Counter scales ≈1 per 10.9 ms of stall (≈1 per 512 frames). |
| **F8** | "capture targeting a sink works without `stream.capture.sink`" | **CONFIRMED (not falsified)** — native refusal is *loud*: state `error`, `"no target node available"`, core `res:-2`, rc 0 ×3; with the prop it works end-to-end (peak 0.499969). Also: **no-target capture does not fall back to the default source** (error ×4) even though `pw-record` does — a native-vs-CLI divergence. |

**Harness correction (disclosed).** The first `drain` battery legs reported
`rc=timeout` with zero output. That was **not** a library hang: the drained
event re-armed the probe's own quit timer before it fired (timer starvation),
and the zero output was `Popen.communicate()`'s internal buffering. The client
was corrected (no re-arm on drained; drain-aware quit) and the legs re-ran
clean (`drain2`). The earlier timeout rows are retained in
`receipts/battery-all.json` as harness history.

---

## 3. Laws in detail

### 3.1 Connect / state machine (`state` ×3, `stream.c`)
`pw_stream_connect(…, PW_ID_ANY, NONE, EnumFormat)` rc 0 → `connecting` →
`paused`. `pw_stream_get_node_id()` right after connect is
`SPA_ID_INVALID` (4294967295) and becomes a real id later (`stream.c:1257` sets
it when the node global arrives). `pw_stream_get_time_n` before running = -5.
`pw_stream_disconnect` on a connected paused stream = 0. Post-connect props
(non-RT): `stream.is-live=true`, `node.want-driver=true`,
`node.loop.class=main`, `node.async=true`, plus `object.serial`/`client.id`.
`is_driving=0`, `is_lazy=0` throughout (this host does not use lazy
scheduling).

### 3.2 Flags → props (`dont_reconnect` ×3, `stream.c:2087-2098`)
`AUTOCONNECT`→`node.autoconnect=true`; `DONT_RECONNECT`→
`node.dont-reconnect=true` **only if the prop is absent**; `EXCLUSIVE`→
`node.exclusive` (only-if-absent); non-RT → `node.loop.class=main` +
`node.async=true`; `DRIVER`→`node.driver=true`. Measured: `EXCLUSIVE` is
accepted by the null-sink (rc 0, `streaming`) — it is not a refusal surface
here; `DRIVER` sets the prop but `pw_stream_is_driving()` still returns 0
(the null-sink stays the graph driver).

### 3.3 Buffer geometry and callback cadence (`run` ×3, `quantum*`, `s16`)
Default playback to the null-sink: 2 buffers × **49152 B** (12288 frames mono
f32), `pw_buffer.requested` = 1024 frames (the peer's `rate_match->size`, i.e.
one quantum), and **the process callback fires once per buffer refill**
(6 callbacks/1.5 s ≈ 256 ms), not per graph cycle. Source mechanism
(`stream.c:449-477`): `call_process()` returns early unless
`update_requested()` finds a free buffer; the requested size is
`impl->rate_match->size` (`stream.c:693-700`). `node.latency=1024/48000`
changed nothing; `node.force-quantum=512/2048` changed `requested`/`delay`/
`size` but **not** `maxsize`, and the callback cadence stayed ~4/s
(12288 frames ÷ quantum × 21.3 ms/quantum = constant 256 ms). `EARLY_PROCESS`
and `ALLOC_BUFFERS`/`MAP_BUFFERS` did not change the cadence. The
forced quantum **propagated to the whole graph** while the client lived
(pw-top: null-sink driver `QUANT 512`), auto-restored at client exit — the
native analogue of r95's JACK per-client quantum law.

### 3.4 Process thread (`rt_process` ×3, `rt_nice`)
With `RT_PROCESS`: separate tid (`proc_tid≠main_tid`), scheduler
`0x40000000` = `SCHED_OTHER|SCHED_RESET_ON_FORK`, prio 0, nice 0 — **the
"realtime thread" is not realtime-scheduled on this host**. Without it:
same tid as the main loop (`node.loop.class=main`).

### 3.5 Time (`time` ×3)
While streaming: `rate=1/48000`, `ticks` advancing, `queued=12288`,
`queued_buffers=1`, `avail_buffers=0`, `size=1024`, `delay` = graph quantum
(0 in the deactivated leg's snapshot). `get_time_n` still rc 0 after
`set_active(false)`. `set_rate(0.5)` while streaming rc **0** (rate_match
present); pre-connect rc **-95**.

### 3.6 Drain (`drain2` ×3 each arm)
`flush(drain=true)` rc 0 in both arms. Timer arm: first `drained` at
flush+253 ms (one 12288-frame buffer), then every ~42.5 ms, `n_drained` 34–35
over the remaining 1.45 s. Callback arm: first `drained` at flush+1 ms, then
every ~42.5 ms, `n_drained` 40. **State never leaves `streaming`; the app is
not asked for more data (`cb_count` 3–4), i.e. `drained` behaves as a repeating
"queue empty" notification, not a one-shot completion.** The doc's "resume by
setting active again" was not needed and no PAUSED transition was observed.

### 3.7 Params (`run` ×3, `neg_stream` ×3)
`param_changed` on a streaming stream: ids `20,15,17` (PeerCapability,
Latency, Tag) ×2 then `4` (Format) — decoded from `param.h`. Negotiated
Format = `SPA_AUDIO_FORMAT_F32_LE` (283), 48000, 1ch MONO. Paused streams see
only `20,15,17`. Mid-stream `update_params(EnumFormat 44100)` rc 0 with **no**
param_changed in the following 700 ms — the renegotiation is not observable at
this level `[?]`.

### 3.8 Target resolution (`target_*` ×3, pw-dump link witnesses)
`target.object=<serial>` → link to `r98s_ns` (3/3). `target.object=<id>` →
link to the **default sink** (3/3). `target=no_such_r98s` → default sink
(3/3). All three end `streaming` — the fallback is silent (rc 0, no error).

### 3.9 `media.class` on a playback stream (`media_class_*` ×3)
`Audio/Sink` → **SIGSEGV** (see F1; core backtrace in §2). `Audio/Source` →
rc 0, `paused`, no error, param ids 20,15,17 only. The source-level check is a
`pw_log_warn` only (`stream.c:2121-2123`).

### 3.10 Capture (`cap_*`)
With `stream.capture.sink=true` and a sink target: `streaming`, 35 callbacks,
71680 frames, peak **0.499969** (= the pw-play s16 tone's 16383/32768), Goertzel
magnitudes identical ×3 (`997 Hz` 302 944 141.055 vs `440 Hz` 4.542). Without
the prop: `error "no target node available"` (rc 0) — the native analogue of
r83/r87's MIDI refusal, now for audio capture. With **no target**: same error
×4 — **no default-source fallback** (a native-vs-`pw-record` divergence).
Explicit default-source target: `streaming`, 45056 frames, all-zero content
(the Line input is currently silent — passive read only).

### 3.11 Error rc lattice (`err_*` ×3, `remote_bad` ×3)
Pre-connect: `set_active` -5, `get_time` -5, `flush` -5, `set_rate` -95,
`disconnect` 0, `dequeue` NULL. `connect` twice → second **-16 EBUSY**.
Direction 99 → rc 0 then back to `unconnected` (no node, no error).
0-params connect → rc 0, `paused`. Bad remote → rc 1, **-112 EHOSTDOWN**.

### 3.12 Induced xruns (`stall` ×3, `stall600` ×2) — r89 gap closed
A 300 ms `usleep` inside the RT process callback (stall at cb 3 ≈ 520 ms):
pw-top `ERR` = **27** (3/3, row marked `+`), pw-profiler follower
`xrun_count` = **27** (3/3), `status` flips `finished`→`awake`→`triggered`,
`awake−signal` goes negative and accumulates (−21 330, −42 661, … µs = missed
cycles), `negative_wait` records 26, **driver `xrun_count` stays 0**. 600 ms
stall → follower `xrun_count` **55** (2/2), negative-wait 54; pw-top snapshot
mid-stall showed `ERR 21` with `+++` wait. Counter rate ≈ **1 per 10.9 ms**
(≈1 per 512-frame period), linear in stall duration. Callbacks resume after
the stall (`cb_log` gap = 300 ms + one buffer period).

---

## 4. Author-ready rows — proposed `--probe-pwstream-r98` entry

Each row is a candidate for the canonical battery (`corpus/fixtures/measure_audio.py`
opt-in probe), with the measured pin and the receipt file that proves it.
All rows are namespace-safe (`r98s_*`), silence-only, and need one private
null-sink (`pactl load-module module-null-sink sink_name=<ns> channels=1
rate=48000 sink_properties=state.restore-props=false`) unloaded by verified index.

1. **Availability/version row** — `pw_get_library_version()=1.6.8`; core info
   name/version/user/host; connect rc 0; core props (`default.clock.quantum=1024`,
   `max-quantum=2048`, `min-quantum=32`, `rate=48000`, `link.max-buffers=16`).
   (`battery-all.json` `info`)
2. **State row** — `unconnected→connecting→paused`; node id invalid at connect
   (4294967295) and valid after bind; `get_time_n` pre-run = -5; disconnect 0.
   (`state`)
3. **Gate row** — no-autoconnect: `paused`, 0 callbacks, no Format param;
   autoconnect: `streaming`, callbacks > 0. (`run_autoconnect`, `run_no_autoconnect`)
4. **Geometry row** — `maxsize=49152` B (12288 frames), `requested=1024` frames,
   chunk 49152, stride 4, cadence ≈1 callback/256 ms; `node.force-quantum`
   changes `requested`/`delay`/`size` but not `maxsize`; s16 → `maxsize=24576`,
   stride 2. (`run_autoconnect`, `quantum512/2048`, `s16_format`)
5. **Flag→prop row** — `node.dont-reconnect=true` from the flag; explicit
   `false` wins; `node.autoconnect=true`; `node.loop.class=main`;
   `node.async=true`. (`dont_reconnect`, `dont_reconnect_false_prop`)
6. **Activation row** — `INACTIVE` → `paused`, 0 callbacks; `set_active(true)`
   rc 0 → `streaming`. (`inactive_activate`)
7. **Trigger row** — 0 callbacks before trigger; `trigger_process()` rc 1 per
   call; callbacks follow. (`trigger`)
8. **Thread row** — `RT_PROCESS`: `proc_tid≠main_tid`,
   `sched_getscheduler=0x40000000` (`OTHER|RESET_ON_FORK`), prio 0, nice 0;
   without it same tid. (`rt_process`, `rt_nice`)
9. **Time row** — `rate=1/48000`, `queued=12288`, `queued_buffers=1`,
   `size=1024`, `delay` = quantum; rc 0 after deactivate; live `set_rate` rc 0
   vs pre-connect -95. (`time`)
10. **Drain row** — `flush(drain=true)` rc 0; `drained` repeats ~every 42.5 ms
    (34–40 events/1.7 s), first event +253 ms (timer arm) / +1 ms (callback
    arm); state stays `streaming`. (`drain2`)
11. **Params row** — param ids `20,15,17,20,15,17,4`; Format = F32LE 48000
    mono; paused = `20,15,17`; `update_params` rc 0 (no observable
    renegotiation). (`run_autoconnect`, `neg_stream`)
12. **Routing row** — serial resolves; `object.id` and garbage fall back to the
    default sink (link witness); stream stays `streaming`. (`target_*`)
13. **`media.class` row (negative control, crash class)** — playback +
    `Audio/Sink` → SIGSEGV rc −11 (dominant under normal invocation; not under
    gdb); playback + `Audio/Source` → rc 0 + `paused`. (`media_class_*`,
    coredump backtrace)
14. **Capture row** — with `stream.capture.sink=true`: streaming, peak
    0.499969, Goertzel 997 Hz ≫ 440 Hz; without it: `error "no target node
    available"` rc 0; no-target capture does not fall back. (`cap_prop`,
    `cap_noprop`, `cap_default_source`)
15. **Error-lattice row** — -5/-5/-5/-95/0/NULL pre-connect; -16 second
    connect; direction 99 rc 0 → unconnected; 0-params rc 0 + paused; bad
    remote -112 EHOSTDOWN. (`err_*`, `remote_bad`)
16. **Xrun row** — 300 ms stall → pw-top ERR 27 + profiler follower
    `xrun_count` 27, negative wait accumulating, driver 0; 600 ms → 55; linear
    ≈1/10.9 ms. (`stall`, `stall600`)

Arming note: rows 3–8/12–14 are **silence-only**; row 14's tone leg must keep
its target on the private null-sink (never the default sink). Row 13 is a
crash-class negative control — run it last, expect rc −11, and never gate the
battery on it.

---

## 5. Contention ledger, host-state, cleanup

| window | contact | effect |
| --- | --- | --- |
| whole window | sibling `r96-scout` live (PulseAudio env probes via `pactl`); sibling objects visible in pw-dump/pw-top: `r93s_in/fc_*`, `r89b_ns`, `r87b_ns*`, `r86b_ns`, `r82ff_ns_*` | read-only contact; never touched; my link listings carry their rows |
| whole window | quantum variance 1024↔2048 on the shared graph (sibling load, cf. r95 §11) | explains `ticks`/`delay` wobble between reps; verdict fields stable |
| seat legs | 1 private null-sink per stage, name-verified unload by index; ~130 probe executions (91 battery + 16 followup + 6 drain2 + 3 time re-run + manual) | own residue zero at exit |
| bounded host mutation | `node.force-quantum=512/2048` on the *client* node (quantum512/2048 legs) — propagates to the graph while the client lives, auto-restored at client exit; verified via pw-top (driver QUANT 512 during, 1024 after) | no metadata written; no `set-default-*` ever issued |
| bounded host mutation | `set_rate(0.5)` live for ~150 ms on a silence stream (time leg) | destroyed with the stream; no audible output (null-sink) |
| persistent residue | `~/.local/state/wireplumber/stream-properties` gains **1 row** `Audio/Sink:node.name:r98s_ns={volume…}` — the r90/r95 class (1202 such rows already exist; no CLI deletes them) | disclosed, not hidden |
| exit | `pactl list modules short \| grep r98s` = 0; `pw-dump` r98s nodes = 0; seat procs = 0; defaults SPDIF/Line unchanged | clean |

---

## 6. Remaining `[?]`, risks, blockers

1. `[?]` The **12288-frame/49152-B default** is not derivable from `stream.c`
   or `spa/plugins/audioconvert/audioadapter.c` (labrat falsified the constant
   hunt; the adapter takes the peer's `SPA_PARAM_BUFFERS_size` and my client
   port shows `size default 32768` while the dequeued buffer is 49152). The
   exact negotiation/owner (client-node module or the adapter's sizing with the
   sink) is **not pinned** — needs a pod-level trace or `module-client-node`
   source read. (First `adapter.c` fetch was a 404 HTML page — corrected to
   `audioadapter.c`; the labrat caught it.)
2. `[?]` The **42.5 ms `drained` period** (≈2 quanta) and its exact semantics
   ("queue empty" notification vs drain completion) are inferred from timing,
   not from source.
3. `[?]` Mid-stream `update_params` renegotiation is invisible at the client
   level (rc 0, no param_changed); whether the adapter silently renegotiated
   needs a server-side pod witness.
4. `[?]` The `media.class=Audio/Sink` SIGSEGV is timing-dependent (0/7 under
   gdb, 9/9 direct). The core backtrace pins the crash site
   (`pw_impl_port_set_mix` region via spa audioconvert) but not the exact
   dereference; no upstream issue was filed (out of seat scope).
5. `[?]` `pw_stream_return_buffer`, `pw_stream_emit_event`,
   `pw_stream_set_control` (volume/mute from the client), `pw_stream_new_simple`,
   freewheel/lazy scheduling and `PW_STREAM_FLAG_DRIVER` as an actual driver
   were not measured (named gaps, bounded scope).
6. `[?]` Reps are 3 for pins but 1–2 for exploratory flags (exclusive, driver,
   early_process, map/alloc buffers, s16); treat those as single-witness.
7. **Blocker for authoring**: none — the surface is fully drivable headless and
   self-cleaning; the crash-class row (13) must be excluded from pass/fail
   gating.

---

## 7. Artifacts & provenance

`corpus/live/r98-scout/` (untracked, 4.2 MB):

- `PREDECLARED.md` — hypotheses frozen before the battery.
- `probes/r98stream.c` (sha256 `90f96f122fee…`, final; earlier-stage shas in `receipts/summary-*.json`) + `probes/r98stream`
  (binary sha per stage recorded in `receipts/summary-*.json`: battery-all
  `7501bd7b2bf9…`, followup `73f696861733…`, drain2/time `aab37319e337…` /
  `d999e10fd486…`; the deltas are drain/quit/nice instrumentation only).
- `r98driver.py` — orchestration, receipts, pw-dump/pw-top/pw-profiler
  cross-witnesses, census.
- `receipts/` — `battery-all.json` (91 legs/35 types), `battery-followup.json`,
  `battery-drain2.json`, `battery-time.json`, `analysis.json` (per-leg
  stability; only `ticks`/timestamps vary across reps), `census-entry/exit.json`,
  `summary-*.json`.
- `raw/` — per-leg stdout/stderr verbatim; `runs/` — battery logs.
- `sources/` — version-matched upstream: `stream.c`
  (`3699792e732ec7a2…`, 2793 L), `stream.h` (`1ad58710f7487680…`), `impl-node.c`,
  `audioadapter.c` (`8ab982349c42321d…`), plus `SOURCES.md`; the original
  `adapter.c` fetch is retained as the 404 artifact it is.
- `scratch/` — pw-profiler JSON witnesses (`prof-stall2.json` 1264 records),
  manual run logs, `q512` pw-top witness.

Probe incident note: three `media_class_sink` legs and the `drain` legs produced
`rc=-11`/`timeout` rows that are explained in §2 (crash class + harness
correction); no sibling object was touched at any point.

*scout leaf — measured and read, not judged.*
