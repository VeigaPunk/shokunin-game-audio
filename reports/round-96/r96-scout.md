# R96 scout — the PulseAudio-native client API surface via pipewire-pulse (pactl/pacat/paplay, PULSE_* vectors, stream properties, cork/prebuf, sink-input/source-output introspection)

Round 96 pre-measurement. Host `plazir27`, measured **2026-10-15 20:03Z → 20:31Z**
(host local UTC−3: 17:03–17:31). Repo `~/Projects/shokunin/audio-shokunin` @ entry
HEAD **`1abd9549`** (`r85 boundary`), exit HEAD **`97bd351a`** — siblings landed 12
commits during the window (r82 ×5 author/scribe/reviewer/simplifier/verifier,
r93 ebur128 scout, r98 pw_stream C-API scout, r86/r87/r88/r89/r90 boundary); none is
this surface. Tracked-dirty at entry = the sibling-owned `corpus/fixtures/measure_audio.py`
(+ `.pyc`), never read/imported/executed here; tracked-dirty at exit = the same
sibling-owned `__pycache__/measure_audio.cpython-314.pyc` (a sibling battery recompiled
it mid-window) — **no r96 path is tracked**. Toolchain: **pactl/pacat/paplay/parec 17.0-98-gb096**
(libpulse **17.0.0**, protocol 35), **pipewire-pulse `1:1.6.8-1`**, server string
`PulseAudio (on PipeWire 1.6.8)` / server version `15.0.0`, socket
`/run/user/1000/pulse/native`, gcc 16.1.1 (own C client), Python 3.14.7, Linux
7.2.3-arch1-3.

**Seat: SCOUT (leaf). Zero tracked-file writes; the only file written outside
`corpus/live/r96-scout/` is this report.** Every child is triple-bounded (wall cap +
process-group kill + byte caps; `start_new_session` + `os.killpg`, `RLIMIT_CORE=0`).
Seat-owned names only (`r96s_*`); the one seat module was unloaded **by exact id after
a name check**; **no `pactl set-default-*` was ever issued**. Fallback-routing legs
used a −60 dBFS quiet tone so the operator default sink was never driven audibly.
Exit census: **0 `r96s` sinks/sources/modules/nodes, 0 seat processes, defaults
unchanged, `clock.force-quantum=0`**; 12 permanent `stream-properties` rows remain
(r90 class, §12). One disclosed pre-harness smoke contact with the operator default
sink (§12).

**Label legend.** `[O]` = directly observed on this host in this window (probe output
or on-disk read). `[I]` = read from the version-matched upstream source (URLs + shas
in `sources/FETCHED-SOURCES.sha256`) or inferred from measured laws. `[?]` = not
resolved by this seat.

---

## 0. Why this surface (the pick, and what it displaces)

The brief's assigned surface is the **PulseAudio-native client API as served by
pipewire-pulse**: pactl/pacat/paplay/pacmd-equivalents, PULSE_* env vectors, stream
properties, cork/prewait semantics, source-outputs/sink-inputs introspection.
Prior rounds touched pieces of it — r75 (paplay transport classes), r76/r78 (parec
capture, monitor roundtrip), r80 (pactl load-module lattice), r84 (ALSA + *pulse-compat*
deep params: the `PULSE_PROP_*` env vector and the pactl write surface), r90
(pipewire-pulse *module namespace* + restore persistence) — but **no round measured the
client API itself**: server/env resolution, device targeting, the buffer-attribute law
(`pulse.attr.*`, `PULSE_LATENCY_MSEC`), `--property` vs `PULSE_PROP`, cork/trigger/prebuf
semantics, or the introspection field semantics (`Corked:`, `Buffer Latency: 0 usec`,
monitor Source index). r93 (ebur128) is excluded by the brief and had not landed at
entry; r95 (JACK) and r94 (SoX) are other surfaces.

**Headline: the pulse surface is a faithful emulation with four sharp edges — the
buffer-attr law is source-exact and reproducible to the byte (46/46 rows), the
playback/capture target-miss asymmetry is real (silent fallback vs `No such entity`),
`trigger` cannot start a corked stream, and `prebuf=0` permanently silences a starved
stream while every latency field the introspection exposes is hardcoded zero.**

---

## 1. Headline claims

| # | claim | label | sharpest single fact | evidence |
| --- | --- | --- | --- | --- |
| 1 | **`pacmd`/`pa-info` are absent; the whole CLI client family is one binary.** | `[O]` | `pacmd`, `pa-info`, `pax11publish`, `pw-pulse` absent from `$PATH`; `paplay`/`parec`/`parecord`/`pamon` are **symlinks to `pacat`** (sha `e584711d…`, 43128 B); `pactl` is its own binary (sha `9868ce72…`); pacmd verbs `kill-sink-input`, `kill-source-output`, `dump` have **no pactl equivalent** (`rc 1 No valid command specified`) | `receipts/r96s_cli_server.json` (`a1_avail`), `runs/pacmd_equiv.txt` |
| 2 | **`PULSE_SERVER` resolution is a 5-shape lattice with distinct error classes.** | `[O]` | `unix:/path` ≡ bare `/path` ≡ default (rc 0); `unix:/nonexistent` / `tcp:127.0.0.1:4713` / `PULSE_RUNTIME_PATH=/tmp/…` → rc 1 `Connection failure: Connection refused`; **empty `PULSE_SERVER=""` → rc 1 `Invalid server`** (unique class); bogus hostname → rc 1 but **7.49/7.50 s wall** (DNS) 2/2; `PULSE_COOKIE=/dev/null` → warning `Failed to truncate cookie file: Invalid argument` **and still connects** (unix socket peer-cred bypasses the cookie) | `r96s_cli_server.json` (`b_*`) |
| 3 | **`-s/--server` beats `PULSE_SERVER` in both directions; `PULSE_CLIENTCONFIG` is honored.** | `[O]` | `PULSE_SERVER=tcp:127.0.0.1:1 pactl -s unix:… info` → rc 0; the inverse → rc 1 (3/3 each). A `client.conf` with `default-server=tcp:127.0.0.1:1` → rc 1; with `default-sink=r96s_ns` → 3/3 paplay streams land on the seat sink (`target.object=r96s_ns`) | `r96s_cli_server.json` |
| 4 | **Targeting asymmetry: playback target misses fall back silently; capture misses refuse.** | `[O]` | `PULSE_SINK=no_such_r96s`/`r96s_ns.monitor`/`999999`/`""` → rc 0, stream lands on the **current default sink** while `target.object` keeps the literal string; `parec -d no_such_r96s` → **rc 1 `Stream error: No such entity`** (3/3) | `r96s_cli_target.json`, `r96s_cork_resolve.json` |
| 5 | **A numeric device string resolves by sink index — and it is resolved server-side.** | `[O]` | `PULSE_SINK=116459` → sink `116459`, `target.object="r96s_ns"` (3/3); same for a second seat sink `121820` (3/3); `999999` → fallback with `target.object="999999"`. The own libpulse client passes `--device` **verbatim** (no client-side lookup) and still resolves → the pulse server parses the index | `r96s_cork_resolve.json` (`g_resolve`), `r96s_cli_target.json` |
| 6 | **The buffer-attribute law is source-exact and reproduces every measured row (46/46).** | `[O]`+`[I]` | Transcription of `fix_playback_buffer_attr` + `clamp_latency` (`pulse-server.c:434-525`, constants `:60-65`) with `frame_size` reproduces all `pulse.attr.tlength/prebuf/minreq` and `node.latency` values exactly, including frame-size-4 falsifiers (`d_stereo100`, `d_f32_100` → 13440/9604/3840/1440) | `runs/analysis-bufferattr.txt`, `r96s_cli_latency.json` |
| 7 | **`prebuf = tlength + frame_size − minreq` for every default-attr stream.** | `[O]` | default: 192000/190082/1920 (frame 2); 100 ms: 6720/4802/1920; stereo/f32 100 ms: 13440/9604/3840; `--process-time-msec=5`: 192000/191490/512 | same as #6 |
| 8 | **`PULSE_LATENCY_MSEC` is a libpulse vector that overwrites the whole attr and beats `--latency-msec` in both orders; invalid values are silently ignored.** | `[O]`+`[I]` | `PULSE_LATENCY_MSEC=250` + `--latency-msec=100` → env row (13920/12002/5040) and the inverse → env row (6720/4802/1440); `0`, `-5`, `abc`, `""` → default row (192000/190082/8192) with **rc 0, no stderr**; mechanism: `patch_buffer_attr` (`pulse/stream.c:997-1028`) reads the env, rewrites tlength/minreq/prebuf/fragsize and sets `PA_STREAM_ADJUST_LATENCY` | `r96s_cli_latency.json` |
| 9 | **The CLI `--property` vector lands verbatim, and `application.name`/`media.name` WIN here (inverse of r84's `PULSE_PROP` env).** | `[O]` | `--property=media.role=game --property=application.name=r96s_prop --property=zzz.invented=42 --stream-name=r96s_streamname` → introspection shows `application.name=r96s_prop`, `media.name=r96s_streamname`, `media.role=game`, `zzz.invented="42"` (3/3 identical); malformed `--property=noequals` → rc 1 `Invalid property 'noequals'`, no stream; `--client-name=r96s_client` → `application.name=r96s_client` | `r96s_cli_props.json` |
| 10 | **`--property=state.restore-props=false` suppresses the WirePlumber restore row from the pulse path.** | `[O]` | seat `r96s` rows in `~/.local/state/wireplumber/stream-properties`: 10 before the leg, **10 after** (+1.6 s debounce); the next leg without the prop (client-name) took it to **11** | `r96s_cli_props.json` (`e_restore_props_off`), `r96s_census.json` |
| 11 | **Cork = server-side node pause + `pulse.corked` prop; uncork resumes in 15–33 ms.** | `[O]`+`[I]` | `PA_STREAM_START_CORKED` → introspection `Corked: true`/`pulse.corked=true`, monitor capture silent; `pa_stream_cork(0)` → monitor onset **15.1/32.7/32.5 ms** after the uncork event, 68893/68893/67909 nonzero frames of the 1.5 s tone; `stream_set_corked` sets the prop and `pw_stream_set_active(false)` (`stream.c:245-253`) | `r96s_cork_cork.json` (`h_cork`) |
| 12 | **`trigger` does not uncork: a corked + triggered stream stays silent for its whole life.** | `[O]` | 3/3 trigger legs: **nonzero frames = 0, peak = 0** over the full 4 s capture (the corked hold is 1.2 s, tail 1.5 s); server handler only does `stream->in_prebuf = false` (`pulse-server.c:2736-2740`) | `r96s_cork_cork.json` (`h_trigger`) |
| 13 | **prebuf is not an audible-start gate — but `prebuf=0` + starvation silences the stream permanently.** | `[O]` | slow feed (100 ms/250 ms): prebuf default 173698 → **55099 nonzero frames (≈1.15 s of the 1.2 s fed)**, in bursts across ~2.5 s; prebuf 0 → **2645/2645/4612 frames (first chunk only) then silence**; fast-feed control: prebuf 0 → 38385 frames (plays). Mechanism: the underrun branch consumes a full `size = SPA_MIN(d->maxsize, minreq)` from the ring **only when `prebuf == 0`** (`pulse-server.c:1448-1476`), so a starved stream's read index runs ahead and arriving data is discarded as padding | `r96s_cork_prebuf.json` |
| 14 | **Record cork works the same way (data flow gated, introspection flips).** | `[O]` | `PA_STREAM_START_CORKED` record: `pa_stream_readable_size` = **0** while corked; after uncork **86400** bytes readable (drained 52800); `pactl list source-outputs` `Corked:` true→false; the source-output's `Source:` index equals the **sink index** (monitor) | `r96s_cork_record.json` |
| 15 | **Every latency field the PA introspection exposes is hardcoded zero.** | `[O]`+`[I]` | `Buffer Latency: 0 usec`, `Sink Latency: 0 usec` (sink-input) and `Source Latency: 0 usec` (source-output) in every snapshot, and `pa_stream_get_latency` also returns 0; source: `TAG_USEC, 0LL` literals in the info replies (`pulse-server.c:4143-4144`, `:3827`, `:4025`) | `r96s_cli_introspect.json`, all cork receipts |
| 16 | **For native (non-pulse) streams the `Corked:` field is a node-state projection, not a cork flag.** | `[I]`+`[O]` | `pulse-server.c:4129-4132`: `pulse.corked` prop if present, else `dev_info.state != STATE_RUNNING`; a starved linked native `pw-play` stream (no `pulse.corked`) sampled `Corked: no` while its node was RUNNING | `runs/native_idle_corked.txt`, sources |
| 17 | **cork/uncork emit exactly one `change` event on the sink-input; subscribe output is block-buffered when piped.** | `[O]` | unbuffered trace (`stdbuf -o0`): `new` + 3×`change` at t=0.03 (creation, corked), **one `change` at t=0.95 = the uncork** (client uncork event at ≈0.95 s), `remove` at 1.66 | `runs/subscribe_cork_unbuffered.txt` |

---

## 2. Availability & provenance

### 2.1 Tools, packages, binaries
`[O]` `pactl` present (`17.0-98-gb096`, sha `9868ce724331512c…`); `pacat`, and its
symlinks `paplay`, `parec`, `parecord`, `pamon` (sha `e584711d03212ac7…`, 43128 B);
`libpulse.so.0` (`17.0.0`, sha `cf1020d2e4ee28a0…`); `pipewire-pulse 1:1.6.8-1`.
**Absent:** `pacmd`, `pa-info`, `pax11publish`, `pw-pulse`.
`pactl --version` / `pacat --version` = `17.0-98-gb096`, compiled and linked with
libpulse 17.0.0. Server: `Server Name: PulseAudio (on PipeWire 1.6.8)`,
`Server Version: 15.0.0`, protocol 35 both sides, socket
`/run/user/1000/pulse/native` + `pid` file, `Cookie: 17ac:13e6`.
`/etc/pulse/client.conf` (only file; no user copy): `autospawn = no`, all other keys
commented.

### 2.2 pacmd-equivalents
`[O]` `pactl` covers the pacmd verb set except three: `kill-sink-input`,
`kill-source-output`, `dump` → `rc 1 No valid command specified` (`runs/pacmd_equiv.txt`).
`pactl -f json list …` exists and parses (used throughout as the machine witness);
note `pactl -f json list modules short` uses the **singular** key `argument` and
**omits the module index** — parse the text short form when an id is needed.

---

## 3. Server resolution & env vectors (`receipts/r96s_cli_server.json`)

3 reps each (2 for the bogus host), all rc/stderr-stable unless noted:

| leg | env | rc | wall | stderr (verbatim) |
| --- | --- | --- | --- | --- |
| `b_default` | — | 0 | 0.02 s | — |
| `b_unix_prefix` | `PULSE_SERVER=unix:/run/user/1000/pulse/native` | 0 | 0.03 s | — |
| `b_bare_path` | `PULSE_SERVER=/run/user/1000/pulse/native` | 0 | 0.01 s | — |
| `b_unix_missing` | `PULSE_SERVER=unix:/nonexistent` | 1 | 0.01 s | `Connection failure: Connection refused` + `pa_context_connect() failed` |
| `b_tcp_refused` | `PULSE_SERVER=tcp:127.0.0.1:4713` | 1 | 0.01 s | `Connection failure: Connection refused` |
| `b_host_bogus` | `PULSE_SERVER=nonexistent-r96s` | 1 | **7.49/7.50 s** | `Connection failure: Connection refused` |
| `b_runtime_path` | `PULSE_RUNTIME_PATH=/tmp/r96s_nope` | 1 | 0.01 s | `Connection failure: Connection refused` + `pa_context_connect() failed` |
| `b_empty_server` | `PULSE_SERVER=""` | 1 | 0.01 s | **`Connection failure: Invalid server`** + `pa_context_connect() failed` |
| `b_cookie_devnull` | `PULSE_COOKIE=/dev/null` | 0 | 0.01 s | `Failed to truncate cookie file: Invalid argument` (stdout normal) |
| `b_flag_beats_env` | env `tcp:127.0.0.1:1` + `-s unix:…` | 0 | 0.01 s | — |
| `b_env_loses_to_flag` | env `unix:…` + `-s tcp:127.0.0.1:1` | 1 | 0.01 s | `Connection failure: Connection refused` |
| `b_clientconfig_badserver` | `PULSE_CLIENTCONFIG=<scratch conf: default-server=tcp:127.0.0.1:1>` | 1 | 0.01 s | `Connection failure: Connection refused` |
| `b_clientconfig_defaultsink` | `PULSE_CLIENTCONFIG=<scratch conf: default-sink=r96s_ns>` | 0 | 1.62 s | stream lands on seat sink 3/3, `target.object=r96s_ns` |

`[O]` Note the **~7.5 s cost** of a bogus `PULSE_SERVER` hostname (DNS), 2/2; a first
5 s-budget attempt was still inside the lookup (SIGINT at 5 s) — budget for it.

---

## 4. Sink/source targeting lattice (`r96s_cli_target.json`, `r96s_cork_resolve.json`)

3 reps each; landings read from `pactl -f json list sink-inputs`/`source-outputs`
matched by `application.process.id`.

| arm | device vector | rc | landed | `target.object` |
| --- | --- | --- | --- | --- |
| `c_env_sink_seat` | `PULSE_SINK=r96s_ns` | 0 | seat sink 116459 | `r96s_ns` |
| `c_env_sink_default` | `PULSE_SINK=@DEFAULT_SINK@` | 0 | default SPDIF 61 | `alsa_output…SPDIF__sink` |
| `c_env_sink_missing` | `PULSE_SINK=no_such_r96s` | 0 | default | `no_such_r96s` |
| `c_env_sink_index` | `PULSE_SINK=116459` | 0 | seat 116459 | `r96s_ns` |
| `c_env_sink_index2` | `PULSE_SINK=121820` (2nd seat sink) | 0 | 121820 | `r96s_ns2` |
| `c_env_sink_badindex` | `PULSE_SINK=999999` | 0 | default | `999999` |
| `c_env_sink_spdif_index` | `PULSE_SINK=61` | 0 | SPDIF 61 | SPDIF name |
| `c_env_sink_monitor` | `PULSE_SINK=r96s_ns.monitor` | 0 | default | `r96s_ns.monitor` |
| `c_env_sink_empty` | `PULSE_SINK=""` | 0 | default | `` (empty) |
| `c_flag_beats_env` | `PULSE_SINK=r96s_ns` + `pacat -d @DEFAULT_SINK@` | 0 | default | SPDIF name |
| `c_flag_seat` | `PULSE_SINK=@DEFAULT_SINK@` + `pacat -d r96s_ns` | 0 | seat | `r96s_ns` |
| `c_source_seat_monitor` | `PULSE_SOURCE=r96s_ns.monitor` + `parec -d …` | 0 | source-output on 116459 | `r96s_ns` |
| `c_source_default` | `PULSE_SOURCE=@DEFAULT_SOURCE@` | 0 | Line source 64 | `alsa_input…Line__source` |
| `c_source_missing` | `PULSE_SOURCE=no_such_r96s` | **1** | — | stderr `Stream error: No such entity` |
| `c_pacat_default_monitor` | `pacat -r -d @DEFAULT_MONITOR@` | 0 | SPDIF monitor | SPDIF name |
| `g_resolve index` (own C client, device passed verbatim) | `--device 116459` | 0 | 116459 | `r96s_ns` |
| `g_resolve badindex` | `--device 999999` | 0 | **default** | `999999` |
| `g_resolve missing` | `--device no_such_r96s` | 0 | default | `no_such_r96s` |

**Author rules.** (a) Playback: an unresolvable sink name/index is *silently* routed to
whatever the session manager considers default at link time (`target.object` keeps the
literal string — useful as a diagnostic). (b) Capture: the same miss is a hard refusal
(`No such entity`, rc 1) — arm capture legs with a resolvable source. (c) A bare sink
*index* works and is resolved to the node name server-side. (d) `-d`/`--device` beats
`PULSE_SINK`/`PULSE_SOURCE`; `@DEFAULT_SINK@`/`@DEFAULT_SOURCE@`/`@DEFAULT_MONITOR@`
resolve.
*Confound observed:* during the `g_resolve` window the fallback sink was
`r87b_ns` (a sibling's null sink) instead of the pulse-reported default SPDIF — the
session manager's `default.audio.sink` metadata was transiently reasserted by a sibling
lane (§12). The law is the fallback *mechanism*, not the destination identity.

---

## 5. The buffer-attribute law (`runs/analysis-bufferattr.txt`)

`[I]` Source anchors (tag `1.6.8`): `pulse-server.c:434-525`
(`fix_playback_buffer_attr`), `:427-432` (`clamp_latency`), `:60-65` constants:
`pulse.min.req = 256/48000`, `pulse.default.req = 960/48000`,
`pulse.default.tlength = 96000/48000`, `pulse.min.quantum = 256/48000`,
`quantum_limit = 8192`, `MAXLENGTH = 4 MiB`.
`[O]` **46/46 measured rows are reproduced exactly** by a transcription of that code
(tlength, prebuf, minreq, node.latency), across 3-rep legs, a 7-point `PULSE_LATENCY_MSEC`
matrix, the process-time arms and the frame-size-4 falsifiers.

Worked examples (s16 mono 48 k, frame 2; `ADJUST` = latency-request flag):

| request | tlength | minreq | prebuf | node.latency |
| --- | --- | --- | --- | --- |
| default (all −1, no ADJUST) | 192000 | 1920 | 190082 | 8192/48000 |
| `PULSE_LATENCY_MSEC=100` (9600 B, ADJUST) | 6720 | 1920 | 4802 | 1440/48000 |
| `PULSE_LATENCY_MSEC=10` (960 B, ADJUST) | 1536 | 512 | 1026 | 256/48000 |
| `PULSE_LATENCY_MSEC=2000` (192000 B, ADJUST) | 175616 | 1920 | 173698 | 8192/48000 |
| `--process-time-msec=5` (minreq 480, no ADJUST) | 192000 | 512 | 191490 | 8192/48000 |
| `--latency-msec=100`, s16 **stereo** (frame 4) | 13440 | 3840 | 9604 | 1440/48000 |
| `--latency-msec=100`, f32 mono (frame 4) | 13440 | 3840 | 9604 | 1440/48000 |

The law in one paragraph: `tlength` defaults to 2 s of frames; `minreq` defaults to
`min(20 ms, tlength/4)` floored at 5.33 ms (256 frames); when the client requests a
latency (`ADJUST`), `latency = min(8192 frames, (tlength − 2·minreq)/2)` is *subtracted*
from `tlength`; then `tlength = max(tlength, latency + 2·minreq)`; `node.latency` is the
latency clamped up to 256 frames; and **`prebuf = tlength + frame_size − minreq`** when
the client leaves prebuf at −1. The frame-size dependence is what the stereo/f32 arms
falsify the "bytes" reading of the law against.

**Env-vs-flag precedence:** `PULSE_LATENCY_MSEC` (read by libpulse, `pulse/stream.c:1003`)
rewrites `maxlength/tlength/minreq/prebuf/fragsize` and sets `ADJUST`, so it wins over
`pacat --latency-msec` **regardless of order** (both orders measured, 3/3). Values `0`,
`-5`, `abc`, `""` are parsed-failed/≤0 → **debug-log only**, attr stays default, rc 0.

---

## 6. Stream properties (`receipts/r96s_cli_props.json`)

- **`--property` vector (3/3 byte-identical):** `media.role=game`,
  `application.name=r96s_prop`, `zzz.invented=42` (string in the pactl view),
  `--stream-name=r96s_streamname` → `media.name` — all visible in
  `pactl list sink-inputs` Properties. Contrast with r84: the **env** `PULSE_PROP_application.name`
  *loses* to pacat's own proplist; the **CLI** `--property=application.name` *wins*
  (it is the client's proplist).
- **Malformed property:** `--property=noequals` → rc 1, `Invalid property 'noequals'`,
  **no stream created** (2/2).
- **`--client-name=r96s_client`** → `application.name=r96s_client` on the stream.
- **Hygiene:** `--property=state.restore-props=false` suppresses the WirePlumber restore
  row (row count stable 10→10 across the leg; the next leg without it → 11). This is the
  pulse-path equivalent of the native `state.restore-props=false` (r90 C8/C9) and the
  recommended way for probe streams not to touch operator state.
- **Server-written props on every pulse stream:** `pulse.corked`, `pulse.attr.{maxlength,tlength,prebuf,minreq}`,
  `node.rate`, `node.latency`, `target.object`, `client.api="pipewire-pulse"`,
  `pulse.server.type="unix"`, `media.format` (file-detected), `module-stream-restore.id`.

---

## 7. Cork / trigger / prebuf / record-cork (`receipts/r96s_cork_*.json`)

Own client `probes/r96pulse` (C, linked `-lpulse`; sha `9b5ebdb9…`), 3 reps per arm,
monitor captured with `pw-record -P stream.capture.sink=true --target r96s_ns`
(exact frame count; onset = first |x|>1000).

| arm | what happens | measured |
| --- | --- | --- |
| `cork` (START_CORKED, write 1.5 s, hold 1.2 s, uncork) | silent while corked; flows on uncork | introspection `Corked: true` + `pulse.corked=true` throughout the hold; onset **15.1/32.7/32.5 ms** after uncork; 68893/68893/67909 nonzero frames |
| `trigger` (same, `pa_stream_trigger` instead of uncork) | **stays silent** | 3/3 captures: **nonzero=0, peak=0** over the full window; `pa_stream_trigger` sent (prebuf>0 satisfied) and server-side only `in_prebuf=false` |
| `prebuf` slow feed (100 ms every 250 ms, prebuf default 173698) | plays, gapped by underruns | 55099 nonzero frames (≈1.15 s of 1.2 s fed) in bursts over ~2.5 s; 3/3 identical |
| `prebuf0` slow feed (same feed, prebuf 0) | **first chunk only, then permanent silence** | 2645/2645/4612 nonzero frames; 3/3 |
| `prebuf0` fast feed (single 1.2 s write) | plays normally | 38385 nonzero frames, 2/2 |
| `record` (START_CORKED from the seat monitor, hold 1.2 s, uncork) | no data while corked, then flows | `readable_corked=0`, `readable_uncorked=86400`, drained 52800 B; `pactl list source-outputs` `Corked:` true→false; 3/3 identical |

`[I]` Mechanisms: `stream_set_corked` sets the `pulse.corked` prop and calls
`pw_stream_set_active(false)` (`stream.c:245-253`); trigger/prebuf handlers only toggle
`in_prebuf` (`pulse-server.c:2736-2740`); the graph `process()` underrun branch
(`pulse-server.c:1448-1476`) emits a silence buffer **without touching the ring when
`prebuf != 0`**, but **copies the remaining data and advances the ring read index by the
full `size = SPA_MIN(d->maxsize, minreq)` when `prebuf == 0`** — with continued
starvation the read index runs ahead and every later chunk is consumed as padding.
`[?]` The exact `buffer->requested` value driving `size` in that branch was not
instrumented (the observable stall is independent of it).

**Author consequence for game audio:** a low-latency client that sets `prebuf=0` and
lets its buffer run dry (e.g. a stalled synth thread) will not merely glitch — it goes
permanently silent until the stream is recreated, while the same starvation with a
non-zero prebuf resumes. Uncork is the only reliable start/stop primitive; `trigger`
is not a substitute for uncorking.

---

## 8. Introspection surface (`receipts/r96s_cli_introspect.json`)

- **Sink-input full text** (verbatim in the receipt): `Driver: PipeWire`,
  `Owner Module: n/a`, `Client:`, `Sink:`, `Sample Specification`, `Channel Map`,
  `Format: pcm, …`, `Corked:`, `Mute:`, `Volume:` + balance, **`Buffer Latency: 0 usec`**,
  **`Sink Latency: 0 usec`**, `Resample method: PipeWire`, then the property list
  (client/server props, process props, `pulse.corked`, `node.rate`, `node.latency`,
  `target.object`, `media.class`, `node.*`, `pulse.attr.*`, `module-stream-restore.id`).
- **Source-output full text**: same shape with `Source:` and **`Source Latency: 0 usec`**;
  for a monitor capture the `Source:` index is the **sink index** and the stream carries
  `stream.capture.sink="true"` and `node.latency=96000/48000` (record default frag = 2 s).
- **Short forms**: `pactl list sink-inputs short` = `index<TAB>sink<TAB>client<TAB>driver<TAB>spec`
  (no application name — the r90 replay parse failure class); `pactl list clients short`
  names pulse clients by their binary (`pacat`), **not** by `application.name` (`paplay`).
- **Latency fields are constants** (claim 15): the info replies emit `TAG_USEC 0LL` for
  latency and sink/source latency; `pa_stream_get_latency` returned 0 in every leg.
  Any game-audio tool that schedules by the PA-reported latency gets a zero.
- **`Corked:` semantics** (claim 16): pulse streams report the `pulse.corked` prop;
  native streams (no prop) report `state != RUNNING`.
- **Subscribe**: events are object-level (`new`/`change`/`remove` on `sink-input #N`);
  uncork produces exactly one `change`; when piped the stream is block-buffered, so use
  `stdbuf -o0` if event *timing* matters (`runs/subscribe_cork_unbuffered.txt`).

---

## 9. Falsification list (what was tried that could have killed each claim)

| claim | falsifier attempted | outcome |
| --- | --- | --- |
| buffer-attr law is bytes-based | stereo s16 + f32 mono (frame 4) 100 ms arms | **falsified the byte reading**; frame-size-aware law holds (13440/9604/3840/1440) 3/3 each |
| env loses to flag (like most CLIs) | both orders of `PULSE_LATENCY_MSEC` vs `--latency-msec` | **falsified** — env always wins |
| invalid env values error out | `0`, `-5`, `abc`, `""` | **falsified** — rc 0, default attrs, no stderr |
| `PULSE_SERVER=""` falls back to default | empty-string leg | **falsified** — `Invalid server`, rc 1 |
| a bad hostname fails fast | 2 reps with wall timing | **falsified** — ~7.5 s DNS wait |
| a bad cookie blocks auth on the unix socket | `PULSE_COOKIE=/dev/null` | **falsified** — warning only, connects |
| numeric device strings only work client-side | own C client passing `--device 116459` verbatim | **falsified** — server-side index resolution |
| capture misses fall back like playback | `parec -d no_such_r96s` | **falsified** — rc 1 `No such entity` |
| cork is client-side bookkeeping only | monitor capture while corked + introspection | **falsified** — real node pause + prop + flow gate |
| `trigger` starts a corked stream | 3 trigger legs with capture | **falsified** — 0 nonzero frames 3/3 |
| prebuf gates audible start (PA classic) | slow feed with prebuf 173698 (never filled) | **falsified** — the fed audio plays anyway (55099 frames) |
| prebuf=0 is always silent | fast-feed control | **falsified** — plays when never starved (38385 frames); the stall needs starvation |
| latency introspection is computed | all snapshots + client query | **falsified** — hardcoded 0 (source literals) |
| `Corked:` is always the cork flag | native stream without `pulse.corked` | **refined** — state projection for native streams |
| the seat perturbs host state | census + defaults + metadata before/after | only the disclosed 12 restore rows + the pre-harness tone contact (§12) |

---

## 10. Author directives

### Verbatim-ready row proposals (≥3 reps unless noted, exact argv in the receipts)

1. **Availability row** — `pactl/pacat/paplay/parec 17.0-98-gb096`; `paplay/parec/parecord/pamon`
   are symlinks to `pacat` (sha `e584711d…`); `pacmd`/`pa-info` absent; `pactl` has no
   `kill-sink-input`/`kill-source-output`/`dump`; server `PulseAudio (on PipeWire 1.6.8)`
   v15.0.0, protocol 35. (`r96s_cli_server.json` `a1_avail`, `runs/pacmd_equiv.txt`)
2. **Server-resolution row** — the 13-leg table of §3 with the five distinct error
   classes and the ~7.5 s bogus-host wall. (`r96s_cli_server.json`)
3. **Precedence row** — `-s` beats `PULSE_SERVER` both directions; `PULSE_CLIENTCONFIG`
   read (bad `default-server` refuses; `default-sink` steers to `target.object=r96s_ns`).
   (`r96s_cli_server.json`)
4. **Targeting row** — playback miss → silent default fallback with literal
   `target.object`; capture miss → rc 1 `No such entity`; index form resolves
   server-side; `-d` beats env. (`r96s_cli_target.json`, `r96s_cork_resolve.json`)
5. **Buffer-attr row** — the 7-row worked table of §5 + the 46/46 law check
   (`runs/analysis-bufferattr.txt`), constants pinned (`256/48000`, `960/48000`,
   `96000/48000`, `quantum_limit 8192`).
6. **Latency-precedence row** — `PULSE_LATENCY_MSEC` beats `--latency-msec` in both
   orders; invalid values silently default. (`r96s_cli_latency.json`)
7. **Property row** — CLI `--property` vector verbatim + `application.name`/`media.name`
   win (inverse of r84's env finding); malformed property rc 1; `state.restore-props=false`
   suppresses the restore row. (`r96s_cli_props.json`)
8. **Cork row** — `Corked: true` + silent monitor while corked; onset 15.1/32.7/32.5 ms
   after uncork; 68893/68893/67909 nonzero frames. (`r96s_cork_cork.json`)
9. **Trigger negative row** — corked + trigger = 0 nonzero frames 3/3. (`r96s_cork_cork.json`)
10. **Prebuf row** — the four-arm table of §7 (default/zero × slow/fast) with
    attr_prebuf and nonzero-frame counts. (`r96s_cork_prebuf.json`)
11. **Record-cork row** — readable 0 → 86400, drained 52800, `Corked` flip; monitor
    source-output `Source:` index = sink index. (`r96s_cork_record.json`)
12. **Introspection row** — the hardcoded-zero latency literals + source cites; short-form
    field sets; monitor index semantics; `Corked` state-projection for native streams.
    (`r96s_cli_introspect.json`, `runs/native_idle_corked.txt`)
13. **Subscribe row** — one `change` per uncork; block-buffered unless `stdbuf -o0`.
    (`runs/subscribe_cork_unbuffered.txt`)

### Bimodal / envelope cells (do not arm as a single shape)

- **Fallback destination** for an unresolvable playback target is the session manager's
  current default at link time — record the *name landed on* as a witness, never pin the
  index; a sibling can transiently reassert a different default (§12).
- **`pulse.attr.prebuf` default depends on the client's tlength** — always read it from
  the live row; it is not a constant.
- **`node.latency`** is clamped at 256 frames low and 8192 frames high; mid-range values
  are `(tlength − 2·minreq)/2` only under `ADJUST`.
- **`pactl subscribe` event timing** is unreliable when piped (block buffering).
- **`Buffer/Sink/Source Latency`** must never be used as a measured value (constant 0).

---

## 11. Remaining unknowns

1. `[?]` Which `buffer->requested` value feeds the `prebuf==0` underrun `size` (the
   stall reproduces without it; the exact granularity was not instrumented).
2. `[?]` Whether the `prebuf=0` runaway also manifests through real clients (pacat with
   `--latency` arms never starve); only the own-client starvation arm was run.
3. `[?]` Why `pactl list clients short` shows pulse clients under their binary name
   while the full list has `application.name` (short form reads the client `name` field).
4. `[?]` Whether `PULSE_SERVER` also accepts `tcp6:`/`unix:path` variants beyond the
   three measured shapes (not armed).
5. `[?]` The DNS failure mode behind the ~7.5 s bogus-host wall (resolver retry policy).
6. `[?]` Whether the WirePlumber restore row suppression via
   `--property=state.restore-props=false` also applies to capture streams (only
   playback armed).
7. `[?]` `pa_stream_get_latency` was only sampled at stream-ready/final; no mid-run
   sweep (all samples 0).

---

## 12. Contention ledger + exit state

| window | contact | effect |
| --- | --- | --- |
| whole window | siblings live: r82 author/verifier/simplifier/scribe (ffmpeg↔PW battery, load up to 149), r93 ebur128 scout (landed mid-window), r98 pw_stream C-API scout (landed mid-window), r87/r89/r90 boundary lanes; leftover sinks `r80md_*`, `r86b_ns`, `r88b_ctl`, `r93s_in`, `r87b_ns*`, `r89b_ns` visible in censuses | read-only contact; my snapshots carry their rows and are pid-filtered |
| 20:06–20:12Z | **pre-harness smoke legs** (before isolation was in place) played 1.5 s 997 Hz tones (amp 0.5) to the **operator default SPDIF sink** (4 legs, ~6 s of tone) and one 20 s tone file was synthesized but never played | disclosed; from the battery onward every playback leg targets the seat null sink (or uses the −60 dBFS quiet tone for fallback-routing legs) |
| ~20:15Z (resolve battery) | fallback destination was a **sibling's null sink `r87b_ns`** instead of the pulse default SPDIF — session-manager `default.audio.sink` transiently reasserted by a sibling | named confound (§4); the law is unaffected |
| 20:06–20:31Z | this seat: ~120 bounded legs, 1 null sink module (`r96s_ns`, id 536870916) + a second for the index test (unloaded by id), own C client, pw-record captures | own residue zero at exit |
| exit | `pactl list modules short \| grep r96s` = 0; `pw-dump` r96s nodes = 0; seat procs = 0; defaults SPDIF/Line unchanged; `clock.force-quantum=0`, `clock.quantum=1024` | clean |
| exit (state left) | 12 `r96s_*` rows in `~/.local/state/wireplumber/stream-properties` (r90 class: no CLI delete; the C-client legs before the hygiene discovery + 2 CLI legs): `r96s_pulse_smoke`, `r96s_pulse`, `r96s_pulse_cork`, `r96s_pulse_trigger`, `r96s_pulse_pb_def`, `r96s_pulse_pb_0`, `r96s_pulse_pb_0f`, `r96s_pulse_pb_df`, `r96s_pulse_rec`, `r96s_pulse_sub`, `r96s_prop`, `r96s_client` | disclosed; all later legs used `--property=state.restore-props=false` |

---

## 13. Labrat fold (frozen `probeParent` — exactly one child, advisory)

One read-only `ufo-labrat` was dispatched with a single falsifiable hypothesis:
*the `prebuf=0` starvation stall is the unguarded ring read-index advance in the
underrun branch (`pulse-server.c:1448-1476`), and the `prebuf>0` branch preserves the
ring*. The child was asked to re-derive the mechanism from the fetched version-matched
sources and to report SUPPORTED / FALSIFIED / PARTIAL with file:line cites plus any
counter-path (ring-index re-sync, clamps, different `minreq`) it could find.

**Result: SUPPORTED** (read-only source re-derivation, no exec; receipt
`receipts/r96s_labrat.json`). The child's independent cites: the underrun gate
`:1448` (`avail < minreq || corked`), the `prebuf == 0` gate `:1461`, the copy of only
`avail` bytes `:1462-1468`, and the unclamped advance `:1470-1472`
(`index += size; pd.read_inc = size; spa_ringbuffer_read_update(...)`) propagated to the
protocol index at `:1321`; with `prebuf > 0` the `:1461` condition is false and **no**
read update occurs in the branch, so data survives to the normal path `:1491-1501` —
matching arms A/B exactly. The only resync it found is `stream_flush`
(`stream.c:173-175`, reached only via `COMMAND_FLUSH_*` at `pulse-server.c:2732-2735`);
`stream_prebuf_active` only gates REQUEST generation, not indices. **Residual
uncertainty (child's own):** the client-data write path (which bumps
`writeindex`/`write_index`) lives in a module file not among the fetched sources; if it
clamped `writeindex` forward to `readindex` on arrival, recovery could occur — nothing
in the fetched code suggests it, and the measured permanent silence is exactly what the
unclamped reading predicts. The child's verdict is advisory; the measured rows stand on
this seat's 3-rep captures.

---

## 14. Artifacts & provenance

`corpus/live/r96-scout/` (untracked, 64 files, ~10 MB; shas in `receipts.sha256`):
- `probes/r96s_lib.py`, `probes/r96s_cli.py` (battery A: server/target/latency/props/introspect),
  `probes/r96s_cork.py` (battery B: cork/trigger/prebuf/record/resolve),
  `probes/r96pulse.c` + `probes/r96pulse` (own libpulse client, sha `9b5ebdb9…`),
  `probes/r96s_synth.py` (own stdlib tone synth), `probes/r96s_analyze.py`
  (source-transcribed law checker), `probes/r96s_summary.py`, `probes/r96s_teardown.py`.
- `receipts/`: `r96s_cli_{server,target,latency,props,introspect}.json`,
  `r96s_cork_{cork,prebuf,record,resolve}.json`, `r96s_census.json`,
  `r96s_summary.json`, `receipts.sha256`.
- `runs/`: `analysis-bufferattr.txt` (46/46), `pacmd_equiv.txt`, `subscribe_cork*.txt`,
  `native_idle_corked.txt`, `batteryA.log`, `batteryB.log`, `smoke1.txt`.
- `scratch/`: own tones (`tone1k5.wav`, `tone1k5_quiet.wav`, `tone20s.wav`), monitor
  captures (`cap_*`), client configs, fifo.
- `sources/`: `pipewire-1.6.8-module-protocol-pulse-{stream,pulse-server}.c`,
  `pulseaudio-v17.0-src-pulse-stream.c`, `FETCHED-SOURCES.sha256`.
