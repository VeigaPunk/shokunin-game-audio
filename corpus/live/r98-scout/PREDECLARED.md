# R98 predeclared hypotheses — native pw_stream C-API surface

Frozen before the r98 battery was run (2026-10-15T20:4xZ). Namespace `r98s_*`.
Every leg is bounded (wall cap + element bound), seat-owned, and touches no
hardware sink for audio (silence to a private null-sink; the only real-sink
contact is a *silent* link witness for the autoconnect-fallback legs).

## Pins to confirm (each ×3 reps unless noted)

- **P1 version/core** — `pw_get_library_version()` == `1.6.8`; `pw_core_info`
  name `pipewire-0`, version `1.6.8`, user `vgpnk`, host `plazir27`;
  `pw_context_connect` rc 0.
- **P2 state machine (no autoconnect)** — `pw_stream_connect(NONE)` rc 0;
  transitions `unconnected→connecting→paused`; never `streaming`;
  `pw_stream_get_time_n` rc `<0` before running; `pw_stream_get_node_id`
  right after connect is the invalid id (4294967295).
- **P3 autoconnect + target** — state `streaming`; callbacks > 0; process
  thread == main thread when `RT_PROCESS` is unset; default buffer geometry
  2 × 49152 B (`requested` 1024 frames), callback cadence ≈ one per buffer
  (~256 ms), not per quantum.
- **P4 DONT_RECONNECT** — after connect the stream props carry
  `node.dont-reconnect=true` (r91's mechanism, now a native witness).
- **P5 INACTIVE + activate** — `INACTIVE|AUTOCONNECT` → `paused`, 0 callbacks;
  `pw_stream_set_active(true)` rc 0 → `streaming` + callbacks.
- **P6 TRIGGER** — `TRIGGER` stream: 0 callbacks until
  `pw_stream_trigger_process()`; triggers then produce callbacks.
- **P7 RT_PROCESS** — process callback runs on a *different* tid than main.
- **P8 time** — `get_time_n` fields (rate 1/48000, ticks, delay, queued,
  buffered, queued_buffers, avail_buffers, size) valid while streaming.
- **P9 drain** — `pw_stream_flush(drain=true)` rc 0; `drained` event fires;
  stream returns to `paused`.
- **P10 negotiation** — `param_changed` ids observed; negotiated Format =
  F32 48000 mono; `pw_stream_update_params` mid-stream rc 0 and a new
  `param_changed`.
- **P11 target.object resolution** — serial resolves to the target; garbage
  name → autoconnect falls back to the *default sink* (silent link witness);
  `object.id` arm measured (prior CLI law says fallback).
- **P12 set_rate** — on a non-resampler stream `pw_stream_set_rate(0.5)` → -ENOTSUP.
- **P13 buffers** — dequeue non-NULL, queue rc 0, chunk/stride as set.
- **P14 stall/xrun** — a 300 ms stall inside the RT process callback produces
  a visible xrun witness (pw-top ERR and/or pw-profiler `xrun_count`), then
  callbacks resume.

## Falsifications (predeclared attacks)

- **F1** "connect rc signals the media.class refusal" — expect rc 0 + state
  `error` for `media.class=Audio/Sink` on a playback stream (r92's wpexec
  error is a native-level refusal).
- **F2** "node id is usable right after connect" — expect invalid id until bound.
- **F3** "a stream without AUTOCONNECT still runs" — expect `paused`, 0 callbacks.
- **F4** "NO_CONVERT + 44100 into a 48000 null-sink refuses at connect" —
  expect connect rc 0 and a *later* failure/error, not a connect rc.
- **F5** "`target.object` = `object.id` resolves like serial" — prior CLI law
  says it falls back; test natively.
- **F6** "an explicit `node.dont-reconnect=false` loses to the flag" — r91
  source law says only-if-absent; expect the prop stays `false`.
- **F7** "a stalled follower is invisible to xrun accounting" — the r89 named
  gap; either close it (counter increments) or record it as still invisible.
- **F8** "capture targeting a sink works without `stream.capture.sink`" —
  r77/r78 CLI law says no; expect a native `no target node available` error
  state (rc 0).
