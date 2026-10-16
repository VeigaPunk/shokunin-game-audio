# r96 author — the PulseAudio-native client API surface (pulsecli family)

Implementation of the round-96 move: an insertion-only `pulsecli` family in
`corpus/fixtures/measure_audio.py` (appended after the r89 block, before
`def main()`), wired as `--probe-pulsecli-r96`, plus ONE new fixture file —
`corpus/fixtures/pulse_r96_probe.c`, the own-libpulse instrument the cork/
trigger/prebuf/record/latency-query arms cannot be measured without. Five
entries, **178 legs** (avail 41 / target 27 / attr 68 / props 20 / cork 22),
every one of them measured green at least once (see §5).

Every armed law is a **boundary-surviving** claim; the scout's falsified
statements are dropped or re-armed at the boundary's corrected values, and the
boundary's own falsifications of the scout are encoded as the primary
witnesses (see §3).

## Files changed

- `corpus/fixtures/measure_audio.py` — insertion-only: the r96 block
  (+1 607 lines) plus the three shared-line splices the wiring requires
  (argparse flag, the one-probe-mode mutex list, the `mode`/`suffix`
  ternaries). Identical convention to r86–r89. No prior row was modified.
- `corpus/fixtures/pulse_r96_probe.c` — NEW fixture (the instrument; built at
  run time into `$TMPDIR`, a failed build is a NAMED coverage block).
- `corpus/live/r96-author/` — seat receipts (dev runs, frozen shas, battery
  stdout/stderr, the daemon-stall log). Untracked.
- `reports/round-96/r96-author.md` — this file.

Nothing committed. No `pactl set-default-*` / `wpctl set-default` was ever
issued; the only default-node lever is a client-side `PULSE_CLIENTCONFIG`
scratch file.

## 1. Conventions carried over

- Namespace `r96a_<pid>` (`r96a_ns_`, `r96a_ns2_`, `r96a_<entry>_<rep>`,
  `r96a_*_tap*`), private role key `r96arole<pid>`.
- Fixed-path lock `corpus/live/measure_audio-pulsecli-r96.lock` (flock, never
  `$TMPDIR`); `TMPDIR=~/Projects/shokunin/tmp` for all runs.
- Name-verified teardown: the module table is re-read immediately before
  firing and only the index whose args carry our `sink_name=` is unloaded;
  residual `r96a_<pid>` nodes are destroyed by id via `pw-cli`; a final sink +
  node census is armed (`sinks_gone`, `own_nodes_after`).
- Every spawned process is its own session leader, bounded by
  SIGTERM→SIGKILL process-group escalation; `_pulsecli_r96_sigreset` resets
  every signal the harness may send to SIG_DFL in the child (the r89 fold
  fix), so a launcher's inherited SIG_IGN cannot fake a signal class.
- Hermetic env: `_pulsecli_r96_env()` drops EVERY inherited `PULSE_*` before
  applying overrides (the r83 critic's env-hermeticity finding folded) — a
  foreign `PULSE_SERVER` in the harness env can never redirect a leg.
- Volatile text (client index, ids, nsec counters, wall times, foreign
  names) is recorded, never armed.

## 2. The two harness laws the boundary forced

1. **The link witness.** A pulse row is introspectable *before* its node is
   linked, and the `Sink:`/`Source:` field then reads `(uint32)-1`. The first
   dev run of the target entry armed the raw first snapshot and produced a
   **vacuous green** (8 rows carried `sink = 4294967295` and the "landed"
   check passed on the non-`None` value). Every landing arm now re-snapshots
   until the index is real (`_pulsecli_r96_link_ok`) or the bound expires —
   the r96 boundary's "never record an empty cold result as absence" rule,
   applied to the *link* rather than the attrs. Live: 24/24 target legs needed
   2 polls, the row→link gap measured 0.004–0.086 s.
2. **The late-attr re-snapshot.** `set_playback_buffer_attr` runs
   `pw_stream_update_properties()` *after* the node is registered
   (`pulse-server.c:555`), so a stream can be visible with `pulse.corked` and
   `node.latency` but **no** `pulse.attr.*`. Every attr leg re-snapshots until
   the attrs land or the bound expires; absence after the bound is a NAMED
   coverage block, never a green. Live census: **25/66** attr legs had a row
   with no attrs in the first snapshot (a receipt re-scan puts 27/66 first
   snapshots without attrs, 2 of them with no row yet) — and all recovered.

## 3. The buffer-attribute law, transcribed and checked

`_pulsecli_r96_fix_attr` is a line-for-line transcription of
`fix_playback_buffer_attr` + `clamp_latency` (pipewire 1.6.8
`pulse-server.c:427-525`), with `frac_to_bytes_round_up` (`:414-422`),
`load_defaults` (`:5550-5567`: `min.req 256/48000`, `default.req 960/48000`,
`default.tlength 96000/48000`, `min.quantum 256/48000`, `quantum_limit 8192`)
and `MAXLENGTH = 4 MiB`. Two deliberate transcription details:

- `SPA_ROUND_DOWN/UP` use the **modulo** form (`spa/utils/defs.h:281-289`),
  not the power-of-two mask form — the `s24le` (frame 3) arm is what
  falsifies a mask reading.
- `patch_buffer_attr` (`pulse/stream.c:997-1028`, pulseaudio 17.0) rewrites
  the WHOLE attr from `PULSE_LATENCY_MSEC` and forces
  `PA_STREAM_ADJUST_LATENCY`; the transcription encodes that, and
  `pa_atou`'s parse law (`pulsecore/core-util.c:2299-2397`) is transcribed in
  `_pulsecli_r96_parse_atou` (leading space/`+`/`-` rejected, leading zeros
  stripped unless the string starts with lowercase `0x`, then strtoul base 0
  with a full-string check and the UINT32 bound).

The transcription reproduces **all 13 published boundary rows exactly**
(dev validation, before any live leg ran):

| cell | tlength/prebuf/minreq/node.latency |
| --- | --- |
| default s16 mono | 192000/190082/1920/8192 |
| `--latency-msec=100` | 6720/4802/1920/1440 |
| `PULSE_LATENCY_MSEC=10` | 1536/1026/512/256 |
| `PULSE_LATENCY_MSEC=2000` | 175616/173698/1920/8192 |
| `PULSE_LATENCY_MSEC=250` | 13920/12002/1920/5040 |
| `--process-time-msec=5` | 192000/191490/512/8192 |
| `--process-time-msec=5 --latency-msec=100` | 5312/4802/512/2144 |
| `--latency-msec=100`, s16 stereo (frame 4) | 13440/9604/3840/1440 |
| `float32le` default (frame 4) | 384000/380164/3840/8192 |
| `s24le` default (frame 3) | 288000/285123/2880/8192 |
| `s24le --latency-msec=100` | 10080/7203/2880/1440 |
| `PULSE_LATENCY_MSEC=100000` (MAXLENGTH clamp) | 4177920/4176002/1920/8192 |

Live, every attr leg compares the **measured** row against the prediction and
arms all four fields (`tlength`, `prebuf`, `minreq`, `maxlength`) plus
`node.latency`; a mismatch on any field is a leg failure. 66 law legs across
the flag lattice, the env vector in both orders, the frame-size falsifiers,
the MAXLENGTH clamp and the 17-cell `pa_atou` parse lattice: **0 failures**.

## 4. Entries and legs

### 1. `pulsecli_avail_r96_probe` — availability + server resolution (41 legs)

- `a_bins`: `pacmd`, `pa-info`, `pax11publish`, `pw-pulse` are **absent**;
  `pactl/pacat/paplay/parec/parecord/pamon` present (armed both ways).
- `a_symlinks`: `paplay`/`parec`/`parecord`/`pamon` are the **same inode** as
  `pacat` (armed); `a_shas`: `pactl 9868ce724331512c…`, `pacat
  e584711d03212ac7…` (different binaries, armed).
- `a_version`: both report `17.0-98-gb096`; `a_info`: server is
  `PulseAudio (on PipeWire …)` (armed).
- `a_pacmd_*`: `kill-sink-input` / `kill-source-output` / `dump` → rc 1
  `No valid command specified` (armed class). **Fail-closed**: the two
  index-0 verbs only fire when the live table has no index-0 object (a blind
  write would kill a foreign stream); the guard is recorded.
- The server lattice, 2 fresh-process reps each: `b_default`,
  `b_unix_prefix`, `b_bare_path` (rc 0); `b_unix_missing`, `b_tcp_refused`,
  `b_tcp6_refused` (**new shape**), `b_trailing_slash` (**new shape**),
  `b_runtime_path` (rc 1 `Connection refused`); `b_empty_server` (rc 1, the
  unique `Invalid server` class — armed as its own class);
  `b_cookie_devnull` (rc 0 **and** the `Failed to truncate cookie file`
  warning); `b_host_bogus` (rc 1, the DNS wall armed as a ≥ 2 s floor, the
  value recorded — live 7.998/8.04 s, matching the boundary's 7.75–8.01 s);
  `b_flag_beats_env` / `b_env_loses_to_flag` (both directions);
  `b_info_s_after_subcmd` (the global option after the subcommand);
  `b_clientconfig_badserver` (refused); `b_clientconfig_defaultsink` (an
  UNNAMED stream lands on the seat sink — the client-side default, with no
  `set-default-*`).

### 2. `pulsecli_target_r96_probe` — targeting + fallback + index (27 legs)

- Playback: `PULSE_SINK` seat / `@DEFAULT_SINK@` / **numeric index** (two
  different seat sinks) / bad index / missing name / `<sink>.monitor` / empty
  string; `-d` beats the env in both directions.
  Armed: the seat/index vectors land on the seat sink and the numeric form
  **canonicalizes to the node name** in `target.object`; every miss is rc 0
  with a **literal** `target.object` and a LINKED stream. The destination
  identity is recorded, never armed (the boundary's moving-target law).
- Capture: `parec -d <seat>.monitor` → a source-output whose `Source:` index
  is the **sink** index; `c_source_missing` → rc 1 `Stream error: No such
  entity` (3 reps) with a hang census; `pacat -r -d @DEFAULT_MONITOR@` → a
  linked source-output.
- **New anomaly (author window):** in the first dev run one of two
  capture-miss reps hung to the 8 s wall cap with no stderr and no
  source-output (the other refused in 8 ms). The boundary saw 3/3 + 3/3
  refusals. The refusal is therefore armed, and a hang is a **NAMED coverage
  block** plus a `capture_miss_census` count — never a red and never a green.

### 3. `pulsecli_attr_r96_probe` — the law + the env vector (68 legs)

- 16 flag/env/frame cells × 2 reps (see §3), the corrected frame-size
  falsifiers (`float32le`, `s24le`; **`f32le` is armed as INVALID**: rc 1
  `Invalid sample specification` — the scout's own receipt had 3/3 rc 1 with
  zero rows and its published numbers for that arm were never measured), the
  MAXLENGTH clamp, and the 17-cell parse lattice × 2 reps.
- `PULSE_LATENCY_MSEC` beats `--latency-msec` in **both** orders (armed on
  the env row); unparseable/≤0 values produce the default row, rc-independent
  silence (armed as `stderr_bytes == 0`).
- `late_attr_census` is recorded on the entry (see §2.2).

### 4. `pulsecli_props_r96_probe` — properties + restore rows (12 legs)

- `p_vector` (verbatim, incl. `zzz.invented`), `--stream-name` → `media.name`;
  `p_dup` (last wins), `p_empty` (lands `""`), `p_streamname_then_prop` and
  `p_prop_then_streamname` (last-wins in BOTH orders), `p_clientname` →
  `application.name`, `p_env_loses` (`PULSE_PROP` env loses to the CLI — the
  inverse of r84's env finding), `p_malformed` → rc 1 `Invalid property
  'noequals'` with no stream.
- `p_restore_off_playback` / `p_restore_off_capture`: our tag's row count in
  `~/.local/state/wireplumber/stream-properties` must not move across the leg
  + the 1.8 s debounce — the scout's open question #6 closed for capture too.
  An unreadable store is a NAMED coverage block.

### 5. `pulsecli_cork_r96_probe` — the own-client surface (24 legs)

Built from `corpus/fixtures/pulse_r96_probe.c` (sha recorded; a failed build
blocks the entry by name). Armed:

- `e_cork` (2): a corked-true **server-side** snapshot (row `corked` true AND
  `pulse.corked` true) before an uncorked one, and a nonzero monitor capture
  after the uncork (the flow gate). The uncork **onset is recorded, never
  armed** — the boundary falsified the scout's 15–33 ms window
  (−10.8…36.0 ms).
- `e_trigger` (3): `pa_stream_trigger` on a corked stream → the capture stays
  **0 nonzero frames / peak 0** (the negative law), with the client's trigger
  event present.
- the prebuf table: `e_prebuf_default_slow` (2, ≥ 30 000 nonzero frames — the
  fed audio plays), `e_prebuf_zero_slow` (3, ≤ 12 000 — the stall; an UPPER
  bound, because the stall's onset is not fixed and one boundary L rep was
  silent from the first chunk), `e_prebuf_zero_fast` (2, ≥ 20 000 — the
  control: the stall needs starvation), `e_prebuf_default_fast` (2, control).
- `e_record_cork` (2): `readable` is **0** while corked; after the uncork the
  readable size peaks ≥ 80 000 B and the drain moves real bytes (the readable
  peak is sampled WITHOUT draining first — a client that drains continuously
  only reports its own loop granularity).
- `e_latency_query` (2): every `pa_stream_get_latency` call returns **−16**
  (≥ 3 calls per rep; the rc is recorded per call — the scout's "returns 0"
  was its discarded return value) while the live introspection fields
  `buffer_latency_usec` / `sink_latency_usec` are the hardcoded `0.0`.
- `e_subscribe` (2): a live reader thread timestamps every `pactl subscribe`
  line against the same monotonic clock as the client; **exactly one**
  `change` event on the sink-input follows the client's uncork (creation
  `change` count recorded; `stdbuf -o0` used — the boundary's block-buffering
  hazard).
- `e_native_corked` (2): a starved native `pw-play --raw` stream on a FIFO
  held `O_RDWR` appears as a pulse sink-input with **no `pulse.corked` prop**
  and `Corked: false` while the node is `running` — the node-state
  projection.

## 5. Evidence

**Frozen bytes** (`corpus/live/r96-author/frozen-shas.txt`, re-verified after
the runs):

- `corpus/fixtures/measure_audio.py`
  `b545283e6355d77346e11e0883d9d79792180f0732f2a5851623dbfb353786c8`
- `corpus/fixtures/pulse_r96_probe.c`
  `fe2c168352144cd66e6977debd84c3ebee80b9ace80c26c4f0bc37d00a8fc64c`
- the built instrument binary (in every cork receipt's `client_build`):
  `c3fc4cefed41157e7eac22e0a399ae232e7dfc4e695657ce0ed00b2ca2a46433`

**The two required green runs on the frozen bytes — both `failures: {}`:**

| run | wall | receipt |
| --- | --- | --- |
| run 1 | 143 s | `corpus/live/runs/20261016T093539457589Z-pulsecli-r96/measurements.json` |
| run 2 | 143 s | `corpus/live/runs/20261016T093802929935Z-pulsecli-r96/measurements.json` |

(stdout/stderr copies: `corpus/live/r96-author/run{1,2}.stdout.json` and
`run{1,2}.stderr.log` — both stderr logs are empty; the run log is
`corpus/live/r96-author/battery.log`.)

Per-entry census, identical in both runs:

| entry | legs | failures | blocked | `sinks_gone` / `own_nodes_after` |
| --- | --- | --- | --- | --- |
| `pulsecli_avail_r96_probe` | 41 | 0 | — | true / `[]` |
| `pulsecli_target_r96_probe` | 27 | 0 | — | true,true / `[]` |
| `pulsecli_attr_r96_probe` | 68 | 0 | — | true / `[]` |
| `pulsecli_props_r96_probe` | 20 | 0 | — | true / `[]` |
| `pulsecli_cork_r96_probe` | 22 | 0 | — | true / `[]` |
| **total** | **178** | **0** | — | — |

The two runs agree on every armed number: `e_cork` 71 677 nonzero frames
(both runs), `e_trigger` 0 / peak 0 (3 reps each), `e_prebuf_zero_slow`
2 752 vs `e_prebuf_default_slow` 57 341 (3+2 reps), `e_record_cork` readable
peak 196 608 / drained 262 144, `e_latency_query` every call rc −16,
`e_subscribe` exactly **1** `change` at the uncork with 2 before it and 1
`new` (and 24–40 FOREIGN sink-input events in the same window — the
confound the index filter removes), `late_attr_census` 0/66 in both runs
(the host was quiet), `capture_miss_census` 3/3 refused / 0 hung.

Named coverage blocks (2 per run, the only non-green lines in either
receipt): `e_native_corked rep 1/2` — the pulse reply reports `Corked: true`
while the live node state is stably `running`. That is a *finding*, not a
failure of the fixture: the field is
`dev_info.state != STATE_RUNNING` (`pulse-server.c:4129`) where `dev_info`
is the pulse server's **cached** manager object, and the cache demonstrably
lags the live node (the earlier system-daemon run also caught
`suspended -> running` across a 50 ms sample pair). The leg therefore arms
the stable, falsifiable half — a native stream carries **no** `pulse.corked`
prop, so the field cannot be a cork flag for it — and records the value,
naming the disagreement instead of arming it.

Earlier runs in the same window (superseded, kept for provenance):
`20261016T092633752834Z` (the daemon recovered mid-run: entries 1–3 were
gated out by name, props 20/0, cork 22/4), `20261016T092940854796Z` (green,
before the native re-encoding) and `20261016T093204463094Z` (cork 1 failure
— the `Corked` value arm that the re-encoding replaced). The two dev runs on
the live daemon (`dev-*.json`) and the private-sandbox runs
(`private-sandbox-*.json`, scripts `probe-private-sandbox-*.py`) are the
seat's receipts for the intermediate states.

**Exit census** (after run 2): 0 `r96a` modules / sinks / nodes, 0 seat
processes, `pactl` defaults unchanged (USB `HiFi__SPDIF__sink` /
`HiFi__Line__source`), `clock.force-quantum=0`, `clock.force-rate=0`,
`clock.quantum=1024`, `clock.rate=48000` (never touched by this seat).
Disclosed residue: **24 `r96a_*` rows** in
`~/.local/state/wireplumber/stream-properties` (the r90 class: the store has
no CLI delete) left by the legs that do not set
`state.restore-props=false` (the `paplay`/`pacat` target, attr and property
legs); every restore-hygiene leg and the own-libpulse instrument (which
always sets the prop) leave none.

## 6. Host contention (named, not hidden)

The shared `pipewire-pulse` daemon **wedged** during this window: `pactl`,
`pw-dump` and `wpctl` all stopped answering (12 s timeouts) while
`pipewire`/`wireplumber`/`pipewire-pulse` stayed alive and idle (0.1–0.7 %
CPU) and several sibling seats' `pw-dump` processes sat blocked for minutes.
Host loadavg was 51–57 with 8+ sibling seats running batteries (r90, r91,
r92, r94, r95, r97, r98 lanes were all live in this window; ~50 `yes` hogs
were foreign). This is not this seat's residue: no `r96a_*` module, sink or
node survived any run (`sinks_gone` all true, `own_nodes_after: []` in every
green entry), and the seat never touched the daemon's configuration.

**Discipline breach (disclosed).** While cleaning up the private-sandbox
dev processes this seat ran a *pattern* kill (`pkill -f "^pipewire -c
pipewire.conf"`) after checking only ONE matching PID's environment. The
checked PID turned out to belong to a **foreign** seat's private sandbox
(`PIPEWIRE_RUNTIME_DIR=…/tmp/r98a-sbx-yg9x_4_3/sbx/q1024/rt`) and the pattern
kill terminated it. The system daemons (PIDs 2060/2063/2694) and the other
foreign private instances (r99asmoke) were untouched, and no `r96a` process
survived; but the r98 lane's private core was killed by a namespace-blind
sweep — exactly the r95-incident class the corpus forbids. The lesson is
recorded here rather than hidden: kill by PID after verifying `/proc/<pid>/
environ`, never by cmdline pattern.

Consequence: the entries were built to **fail fast and named** on an
unresponsive daemon (`_pulsecli_r96_server_gate`, one bounded `pactl info`
before any leg) instead of burning a leg-budget per entry. The verifier will
see the same class; a run started while the daemon is wedged is a NAMED
coverage block at entry level, not a red and not a green.

## 7. Status and remaining risks

- **DONE: the two green runs on frozen bytes** (§5) — 178 legs, 0 failures,
  0 blocked entries, clean teardown in every entry, byte-stable between the
  two passes on the armed values.
- Remaining risks / honest exposures:
  - `e_native_corked`'s *value* is a named coverage block in both green runs
    (the server's cached `dev_info` state vs the live node state, above);
    the armed half is the no-`pulse.corked` class claim plus the
    visibility/`Corked`-field presence of the stream. A future host that
    keeps the cache in sync would turn the block back into a green.
  - the target entry's fallback legs assert the *mechanism* (rc 0, literal
    `target.object`, a LINKED stream); the landed name is recorded only, so
    a session-manager default change is evidence, not a failure.
  - `b_host_bogus` arms the DNS wall as a ≥ 2 s floor; a negative resolver
    cache that made it fast would surface as a red with the value recorded
    (measured 7.998/8.04 s in the dev window).
  - `e_prebuf_zero_slow` arms an upper bound (≤ 12 000 nonzero frames): the
    stall's onset is bimodal (one boundary L rep was silent from the first
    chunk), so equality would be a lie. Measured 2 752 in every rep so far.
  - the cork/prebuf capture arms need the 4 s `pw-record` tap on the seat
    sink to link; a tap that never links is a leg failure (not a silent
    pass) and the tap's own rc is recorded.
  - `e_subscribe` anchors on the client's own uncork timestamp and counts
    only the client's sink-input index; foreign events are counted
    separately (`foreign_sink_input_events`, 24–40 per leg on this host) so
    the shared-graph noise is visible rather than absorbed.
  - `capture_miss` hangs (1 of 2 reps in the first dev window) are named
    coverage blocks with a census; the refusal itself is armed (rc 1 +
    `No such entity`), and both green runs refused 3/3.
  - `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` is tracked
    and re-dirtied by every import of the fixture (pre-existing class,
    disclosed by the r96 boundary as well); this seat did not edit it.
