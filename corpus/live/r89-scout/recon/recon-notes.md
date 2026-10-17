# r89 recon — dead-seat state + verification (scout-finisher)

Host plazir27, 2026-10-15 12:3x UTC−3. PipeWire 1.6.8 / WP 0.5.17-1 /
pactl 17.0-98-gb096. Repo HEAD ee6d684.

## Dead-seat forensics

- Probe `r89_probe.py` docstring: "pw-profiler output lattice on
  PipeWire 1.6.8". Stages: mode, nsem, sig, refuse, schema, drv, top, foot.
- It completed only `j_n8` rep0–2 and died mid-`plain_o_n4/rep0`
  (meta.json never written). receipts/ holds census-entry.json only; no
  s-*.json was ever written. recon/ and raw/ are empty.
- Snapshot of the dead seat's runs/ + census copied verbatim to
  `recon/dead-seat-snapshot/` before this seat re-ran the probe
  (run_leg rewrites rep dirs in place).
- Dead-seat j_n8 ×3: `pw-profiler -J -o prof89 -n 8` all timed out at
  30 s, SIGKILL (rc=-9), stdout_len=0, stderr_len=0, wd_files=[].
- Dead-seat plain_o_n4/rep0: `pw-profiler -o p -n 4` left wd/p as a
  **0-byte file** — eager create, no data.

## Verified on this host before re-run (manual, /tmp)

- Idle graph: `pw-profiler -J -n 2` under `timeout 8` → rc 124,
  stdout `[{ } ]` flushed only at signal.
- Idle graph: `pw-profiler -o f -n 2` → stderr `Logging to f`, file
  created 0-byte eagerly, rc 124 at timeout. "Logging to" is stderr.
- Emission timing (`-J -n 4` idle): stdout empty at t=1.2 s and t=2.7 s;
  SIGINT → rc 0, stdout `[{ } ]\n` flushed at shutdown. The zero-record
  array is a *signal-flush* artifact, not a startup artifact — a parser
  cannot distinguish it from a successful empty measurement.
- Live driver (seat null-sink r89prof_ns + pw-play tone): `-J -n 4` →
  rc 0, 17 records = 4×{info,clock,driver,follower} + trailing {}.
  Driver name `r89prof_ns`, follower `pw-play`. So `-n` counts driver
  cycles; an idle graph produces zero cycles → `-n` unsatisfiable → hang.
- Profiler object: `PipeWire:Interface:Profiler` id 5; module id 4
  `libpipewire-module-profiler` args `{ #profile.interval.ms = 0 }`
  (interval commented → module default).
- Seat's own manual r89prof_ns (module 536870936) unloaded by index,
  rc 0; `pactl list sinks` zero r89 names after.

## Hazards carried into the run

- Every idle-graph `-n N>0` leg is a 30 s hang by design (timeout kills).
- drv/top stages self-load `module-null-sink sink_name=r89prof_ns` and
  unload **by index verified against the sink name** — consistent with
  the r90 landmine (by-name unload destroys same-name modules).
- No stray pw-profiler/pw-play at handoff; module set at entry =
  1,2,4,6,8,10,12,14,16,17,18,20,22,536870912–915.
