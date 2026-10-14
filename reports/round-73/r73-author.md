# R73 author — CONSUMER class expansion (pw-cat + mpv)

Round: 73. Wave: `shokunin-train-20261101-w12`. Work commit `febf34b`.

> **Disclosure (operator substitution):** the author seat measured and
> implemented the arm but was rate-limit-killed before writing this
> report; operator authored this report from the committed diff + the
> measured receipt (`runs/20261014T145502288182Z-consumers-r73`, fork
> pins reproduced) + sibling-seat evidence. Convention per r70.

## Landed changes

`corpus/fixtures/measure_audio.py` (+466/−3):

- `pwcat_leg(transport, path, data, hold_s)` — `pw-cat -p <in|->`
  bounded by `CONSUMER_R73_TIMEOUT_S`; SIGKILL via subprocess timeout
  (pw-cat is SIGTERM-immune while blocked in fifo open); stderr parsed
  for the libsndfile-layer `sndfile:` verdict + trailing `error:` line;
  `_consumer_tail` normalizes mpv log tags / quoted paths / ASLR tags.
- `mpv_leg(transport, path, data, hold_s)` — `mpv --no-config
  --vo=null --ao=null --audio-display=no --really-quiet
  --log-file=<tmp>`; log is the parse surface (detected format, probe
  score, stream_not_seekable, refresh_seek, seek_failed, audio_track,
  playback reason). `--ao=null` pinned (fifo + `--ao=pipewire` + dead
  runtime flips rc0→rc2 — measured by boundary).
- `consumer_transport_entry(member, path)` — both consumers × 4
  transports; per-consumer verdict groups keyed on
  (exit_code, sndfile_error) for pw-cat and (exit_code, lavf_detected,
  seek_failed) for mpv — rc alone collapses mpv's two rc=2 classes
  (simplifier C6).
- `consumer_ops_entry()` — member-independent pw-cat surface:
  (a) `daemon_live` via pactl + `daemon_gate` via
      `PIPEWIRE_RUNTIME_DIR=<empty>` (gate precedes open; rc=1
      "Host is down" ~2 ms);
  (b) `fifo_no_writer` (killpg SIGKILL + `/proc/<pid>/wchan` =
      `wait_for_partner`) + `fifo_empty_writer` (rc=1, `Format not
      recognised.`);
  (c) `pacing_instant` (wall ≈ 4.03 s ≥ 0.75×content for a 4.0 s
      member) + `pacing_trickle` (8 chunks × 0.75 s gap → wall ≈ 6.0 s,
      rc=0 — starved stream blocks to EOF);
  (d) `pwcat_name_axis` (critic's 2×2 fold): identical `.snd` member
      bytes through fifos named `axis.snd`/`.wav`/`.bin` →
      rc {0,1,1} — isolates the name axis inside the arm.
- Flag `--probe-consumers-r73` wired through the mutex + mode + suffix
  chains (`probe-consumers-r73` / `-consumers-r73`).

## Measured (committed receipt `20261014T145502288182Z-consumers-r73`)

- `consumer_dec_hcom_r73_probe`: mpv forks {file, redirected_fd}=rc2
  (hcom detected, seek `Operation not permitted`) vs
  {stdin_pipe, fifo_path}=rc0 — inverted seekability fork, member-local.
- `consumer_extsuffix_snd_r73_probe`: pw-cat forks {file, fifo}=rc0 vs
  {stdin, rfd}=rc1 `Format not recognised.` — the name axis through
  pw-cat's libsndfile decode layer.
- All 7 other members transport-invariant on both consumers.
- `pwcat_name_axis`: {.snd:0, .wav:1, .bin:1} on identical bytes.
- Ops: daemon gate rc=1 `pw_context_connect() failed: Host is down`
  in 0.002 s; no-writer fifo `blocked=True` wchan `wait_for_partner`;
  empty writer rc=1; pacing 4.032 s / trickle 6.003 s rc=0.
- `failures` carries exactly the 2 expected member forks.

## Claim outcome

Briefed claim falsified corpus-wide / confirmed member-locally — see
adjudicator. `wall_s` leaves are measured realtime jitter; semantic
pins live on `playback_paced`/`starved_ok`/verdict signatures.

## Known bounds / risks

- PipeWire daemon is a hard gate — the whole pw-cat arm is viability-
  conditional on it (this host: live, 1.6.8).
- pw-cat `--target 0` deliberately NOT exercised (undrained-stream
  hang class — boundary measured rc=137@8s; recorded, not pinned).
- mpv keyed on playback-reason/lavf fields, never bare rc.
- wall_s granularity: realtime pacing values jitter ~1 ms between runs.
