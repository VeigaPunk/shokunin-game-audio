# R87 scout — pw-cat/pw-midi*/pw-cli device-binding + remote-sink surface

Round 87 pre-measurement. Host `plazir27`, measured **2026-10-15
~06:40–07:20 UTC**. Repo `~/Projects/shokunin/audio-shokunin` @ HEAD
`a2616f73`. Toolchain: PipeWire **1.6.8** (pipewire/pipewire-audio/
pipewire-pulse 1:1.6.8-1), WirePlumber **0.5.17**, libpulse **17.0-98-gb096**
(protocol 35), alsa-utils **1.2.16**, avahi **1:0.9rc5-1** (daemon running),
Python **3.14.7** (numpy 2.5.3), Linux **7.2.3-arch1-3**.
`corpus/fixtures/measure_audio.py` is dirty (foreign seat edit in flight) —
**this seat never imported it**; own harness `r87_probe.py` + `r87_probe_b.py`,
own tone synth + windowed-RMS classifier.

**Seat: SCOUT (leaf). Zero tracked-file edits. Every write is under
`corpus/live/r87-scout/` (receipts + raw logs) and this report.** All routing
measurements ran against seat-owned `module-null-sink` nodes (`r87_ns`,
`r87_kill`, `r87_adp`), loaded/unloaded by index after `sink_name=`
verification. Every stream carried `-P node.name=r87*` so `pw-link -l`
witnesses are unambiguous under contention. Exit state: **0 `r87*` objects**
in `pw-dump` (verified twice).

**Contention.** Foreign seats live for most of the window: `r86ctl_*`
(null-sink + remap-source, present at start, unloaded mid-window),
`r79lb_*` (**three pid generations observed**: 3770658 → 3835457 → 3943556 —
loopback streams, `a6_tap` on the SPDIF monitor, link churn visible inside
my own pw-cli event logs), plus idle waybar/xdg-desktop-portal. §9 is the
ledger. No foreign object was mutated except: identical-value Props write
on WP-owned `hdmi-stereo` (value unchanged, §4.2) and manual `pw-link`
reader-pins onto `Midi-Bridge` capture ports (midi surface, adds a reader
only — cannot alter another seat's audio).

---

## 0. Headline — the frontier cells

| # | frontier item | verdict | the single sharpest measured fact |
| --- | --- | --- | --- |
| 1 | pw-cat ↔ pw-play `--target` lattice | **SAME LATTICE, both directions** | `pw-play`, `pw-record`, `pw-midiplay`, `pw-midirecord` are **symlinks to `pw-cat`** (same sha256 `1cd5f309…`); `-P target.object=` **beats `--target`** on playback exactly as r78 measured for capture; serial resolves, `object.id` falls back; `.monitor`/source-name/garbage → **current default sink** |
| 2 | `--playback`/`--capture` "duplex" | **NO DUPLEX EXISTS; mode flags last-wins** | no `--capture`/`--duplex` option at all (`unrecognized option` usage refusal); `-p -r` → capture node, `-r -p` → playback node; flags **override argv0** (`pw-play -r` captures); **bare `pw-cat` has no mode** — `error: one of the playback/record options must be provided`; `-m` is an orthogonal media mode, not a direction (`pw-cat -m` alone → same usage error) |
| 3 | pw-cli on a live stream node | **PROPS LAND MID-STREAM (exact ratio); FORMAT IS SEALED** | `set-param Props {volume:0.25}` on a playing node → monitor RMS **8485→2121** (exactly 0.25×), `mute:true` → **0.0**, both reversible live; `set-param Format` (valid pod AND empty pod) → **silently discarded**, negotiated `S16LE/48000` unchanged; `send-command <id> Suspend|Pause {}` → node `state: "suspended"` |
| 4 | refusal/steal/FOREIGN classes | **NO OWNERSHIP GATE ON THIS SOCKET** | foreign WP-owned sink accepted `enum-params`+`set-param` (identical-value) with **zero errors** — `remote 0 node N changed` event fired; only classes observed: `unknown global '<id>'`, `unknown param type`, `invalid pod`, `unknown factory name`, `-22 usage:` — none are permission classes |
| 5 | pw-midi* binding | **`--target` IS DEAD; PORT PIN CARRIES REAL EVENTS** | every `--target` (name, `.server`, serial, obj.id, garbage) AND every prop path (`target.object`, `node.target`) → `no target node available` + `res:-2` + node removed; `--target 0` publishes `Stream/Output/Midi` ports; manual `pw-link` pin → aplaymidi injection lands **both notes** in `pw-midirecord` file (45 B SMF) and `pw-mididump` stdout |
| 6 | remote-sink / RAOP | **SURFACE ABSENT — refusal classes pinned** | no `remote*` graph objects, no raop/zeroconf `.so` on disk (34 native modules, none match); avahi daemon **is** running but nothing consumes it; `pactl load-module` → `Failure: No such entity` ×3; `pw-cli load-module` → `Could not load module` — one class regardless of why the module is missing |

---

## 1. FRONTIER — pw-cat/pw-play `--target` lattice (`receipts/s1-target-lattice.json`)

### 1.1 The binaries are one

`pw-play`, `pw-record`, `pw-midiplay`, `pw-midirecord` are **symlinks to
`pw-cat`** (`-rwxr-xr-x 149672`, sha256 `1cd5f309…` — `pw-mididump` and
`pw-cli` are distinct binaries). argv[0] selects mode+direction; `-P`,
`--target`, `-R`, `-n` are a shared option parser.

### 1.2 Playback target lattice (link witness, every leg a fresh process)

| leg | links observed at ~1.6 s | verdict |
| --- | --- | --- |
| `pw-play --target r87_ns` | `output_F{LR} → r87_ns:playback_F{LR}` | baseline honored |
| `pw-cat -p --target r87_ns` | identical | **pw-cat ≡ pw-play** |
| `pw-cat --target r87_ns` (no mode) | no node | **usage refusal** (`pwcat_mode_required`) |
| `--target r87_no_such` | `→ alsa_...SPDIF__sink` (= live default) | fallback to default |
| `--target r87_ns -P target.object=r87_no_such` | `→ SPDIF` | **prop beats flag** |
| `--target r87_no_such -P target.object=r87_ns` | `→ r87_ns` | prop beats flag, other direction |
| `-P node.target=r87_ns` (no flag) | `→ r87_ns` | `node.target` routes |
| `--target 0` | node present, **links {}** | published-unlinked (class `target_zero_unlinked`) |
| `--target r87_ns.monitor` | `→ SPDIF` | `.monitor` unresolvable → fallback |
| `--target <Line source name>` | `→ SPDIF` | wrong-direction object → fallback |
| `-P stream.capture.sink=true --target garbage` | `→ SPDIF` | prop is decoration on playback |
| `PIPEWIRE_PROPS={target.object=r87_ns} --target garbage` | `→ r87_ns` | **env is a second prop vector** (r78 law extends to playback) |
| `--media-role Communication --target garbage` | `→ SPDIF` | role is decoration |
| `--target <object.serial 41546>` | `→ r87_ns` | **serial resolves** |
| `--target <object.id 84>` | `→ SPDIF` | object.id does NOT resolve → fallback |

**The playback lattice is the capture lattice.** Precedence
`target.object` (prop or env) > `node.target` > `--target` flag > absent;
serial is a first-class name; `object.id` never resolves; every
unresolvable string (including `.monitor` and a source name) lands the
**current default sink** — for playback **without** needing
`stream.capture.sink` (the capture-side prop gate is one-directional).

### 1.3 Byte-stability ×3 (fresh processes)

`p_own` ×3 → identical `{output_F{LR}→r87_ns}`; `p_garbage` ×3 → identical
`{→SPDIF}`; `--capture`/`--duplex`/`PIPEWIRE_REMOTE=bogus`/`pactl` refusals
×3 → byte-identical normalized stderr + rc (receipts s6/s7).

---

## 2. FRONTIER — mode flags (`receipts/s2-mode-flags.json`)

| argv | created node class | ports | verdict |
| --- | --- | --- | --- |
| `pw-cat` (no flag) | — | — | `error: one of the playback/record options must be provided` + usage, rc=1 |
| `pw-cat --capture` / `--duplex` | — | — | `pw-cat: unrecognized option '--capture'` + usage, rc=1 — **the options do not exist** |
| `pw-cat --record` +capture.sink+target | `Stream/Input/Audio` | `input_*` + `monitor_*` | capture stream, real 176 KB wav |
| `pw-cat -p -r` | `Stream/Input/Audio` | input | **last flag wins** |
| `pw-cat -r -p` | `Stream/Output/Audio` | output | last flag wins |
| `pw-play -r` | `Stream/Input/Audio` | input | flag overrides argv0 |
| `pw-record -p` | `Stream/Output/Audio` | output | flag overrides argv0 |
| `pw-cat -m` (midi, no direction) | — | — | same `one of the playback/record options` usage error — **`-m` is orthogonal to direction** |
| `pw-cat -m -p --target 0` | `Stream/Output/Midi` | `output_1` | = `pw-midiplay` semantics |
| `pw-cat -d -p tone.wav` | — | — | `dsdfile: can't read dsd file '…': Invalid argument` + `open failed` — class `dsd_read_fail` |

**Answer to the duplex question:** there is no duplex shape in pw-cat
1.6.8 — `-p`/`-r` are a mutually exclusive last-wins pair, media modes
(`-m -d -s -c`) are orthogonal and still need a direction flag, and a
record-direction stream *does* publish `monitor_*` out-ports (self-monitor
surface — visible in `m_record_long`).

---

## 3. FRONTIER — pw-cli on a live stream node
(`receipts/s3-cli-mutation.json`, `s8-supplement.json`,
raw `runs/s3-mutate.pwcli`, `runs/sb-format.pwcli`)

### 3.0 Protocol caveats (needed to reproduce any of this)

- **`pwcli_cold_registry`:** commands sent before registry sync return
  `Error: "<verb>: unknown global '<id>'"` — **even for live ids**
  (`info <live-id>` at t=0 → `unknown global '106'`). All timed legs use a
  1.4 s warmup. A `unknown global` verdict on a cold session means nothing.
- Piped-mode pw-cli prints **async registry events** interleaved with
  responses (`remote 0 added/removed global`, `node N changed`); under a
  churning seat this is hundreds of lines — drain stdout continuously or
  pw-cli deadlocks on a full pipe (observed, fixed in harness).
- `info <id>` shows `permissions: rwxm-` on every object and the param
  permission map: `EnumFormat r-`, `PropInfo r-`, **`Props rw`**,
  **`Format rw`**, `EnumPortConfig r-`, `PortConfig rw`, `Latency rw`,
  `ProcessLatency rw`, `Tag rw`.

### 3.1 The mid-stream mutation witness

`pw-record` on `r87_ns` monitor (windowed RMS of the captured wav) while
a `pw-play` 1 kHz/1.5 kHz dual-tone plays and pw-cli mutates node 152:

| window | set-param applied ~t | RMS L (amp 12000 tone) | verdict |
| --- | --- | --- | --- |
| tone @volume 1.0 | — | **8485.0** | baseline |
| volume 0.25 | sent+~0.3 s | **2121.3** (=0.2500×) | **exact-ratio live mutation** |
| volume 1.0 | | **8485.0** | exact restore |
| mute true | | **0.0** | absolute mute |
| mute false | | **8485.0** | exact restore |
| post-Format attempts | | 8484.8 | unchanged |

**`set-param Props` on a running stream node mutates the running graph
mid-stream, at exact ratio, with no renegotiation and no stream restart.**
`enum-params` echoes each write; the daemon also emits `remote 0 node N
changed` events other clients can see.

### 3.2 Format is sealed once running

`set-param <id> Format { mediaType:1, mediaSubtype:1, format:3, rate:96000,
channels:2 }` (invalid enum id — echoed as `Id 3 ((null))`), `Format {}`
(empty), AND a fully-valid pod `{ format:259(=S16LE), rate:96000, position:"[FL,FR]"}`:
**all silently discarded** — subsequent `enum-params Format` shows the
negotiated `S16LE/48000/2ch/[FL,FR]` unchanged, stream keeps flowing,
no error anywhere. `Format` is `rw` in the param map but writes are
no-ops post-negotiation. (Contrast: a malformed pod — bare `mediaType:
audio` words — fails **client-side** at parse: `set-param: invalid pod:
Expected object key`.)

### 3.3 send-command / destroy / create-node

| command | result |
| --- | --- |
| `send-command <sink> Suspend {}` | **`state: "suspended"`** on next `info` — lands |
| `send-command <sink> Pause {}` | also `"suspended"` (alias-equivalent here) |
| `send-command <id>` (no cmd) | `Error: "send-command <object-id> <command-id> <command-json>"` — 3-arg usage |
| `send-command <id> 0 {}` / `bogus {}` | `Error: "send-command: unknown node command type: X"` |
| `destroy <own-stream-node>` | node gone; client stream dies → `pw-play` exits rc=1 `stream node N unconnected` |
| `destroy <own-null-sink node>` | **the whole `module-null-sink` unloads** (module idx gone from pactl list) |
| `destroy 99999999` | `unknown global '99999999'` |
| `create-node adapter {factory.name="support.null-audio-sink" node.name="r87_adp" media.class="Audio/Sink"}` | `1 = @proxy:N`, node+ports **appear in-session**, then **die when pw-cli disconnects** — session-bound object |
| `create-node nonexistent_factory` | `@proxy:N` then async `error id:N res:-2: unknown factory name X` |
| `create-node adapter` missing `factory.name` | `res:-22: usage: factory.name=<f> (library.name=<l>) node.name=<s>` |

---

## 4. FRONTIER — FOREIGN / steal / refusal classes
(`receipts/s4-foreign.json`, raw `runs/s4-foreign*.pwcli`)

Foreign target: `alsa_output.pci-0000_01_00.1.hdmi-stereo` (id 57, owned by
WirePlumber client 33 — not mine on any reading).

| op on foreign node | result |
| --- | --- |
| `info <fid>` | full dump — allowed |
| `enum-params <fid> Props/Format/PropInfo` | full pods — allowed |
| `set-param <fid> Props { volume: 1.0 }` (the value already in force) | **accepted — echo + `remote 0 node 57 changed`, no error**; post-enum still 1.0 |
| `set-param <fid> Props { no_such_prop: 3 }` | parsed to empty Props (size 8), **silently dropped** |
| `set-param <fid> BogusType {}` | `unknown param type: BogusType` |
| `get-permissions <wp-client 33>` | `default: rwxm-` — unrestricted |
| every verb on `99999999` | `unknown global '99999999'` — one class across verbs |

**There is no FOREIGN-only refusal on the default socket** (`pipewire.access
= "unrestricted"` on every client; `module-access` legacy default). Param
reads and writes on foreign nodes behave identically to own nodes; the only
refusals are name/param/pod/factory/usage classes. "Steal" primitives that
exist as verbs (`destroy`, `send-command`, `permissions`-write, link-creation
via `pw-link`/`create-link`, `pactl move-sink-input` on a foreign stream) were
**not exercised against foreign objects** — they are destructive under
concurrent seats; predicted allowed by the same no-gate, recorded as unknowns
§10 rather than measured.

Refusal classes pinned (verbatim, normalized): `unknown global '<id>'` |
`unknown param type: <T>` | `invalid pod: Expected object key` |
`unknown factory name <f>` (async, `res:-2`) | `usage: factory.name=…`
(`res:-22`) | `unknown node command type: <x>` | props-unknown-key
**silent drop** | `get-permissions` non-client id → `unknown global`.

---

## 5. FRONTIER — midi binding (`receipts/s5-midi.json`, `s8-supplement.json`)

Host midi surface: `Midi-Bridge` (id 50, ALSA `Midi Through` bridge, ports
`…Port-0 (playback)`=in / `…(capture)`=out) + `bluez_midi.server` (out/in).
ALSA seq `14:0` works (r78 fixture row).

| leg | result |
| --- | --- |
| `pw-midiplay` (no target) | `stream node N error: no target node available` + `remote error res:-2`, node removed, rc=1 |
| `--target` = `Midi-Bridge` / `Midi Through` / `bluez_midi.server` / garbage / **bridge object.serial** / **bridge object.id** | **identical refusal for all six** — name and number are the same dead path on midi |
| `-P target.object=` / `-P node.target=` (any value) | identical `no_target_node` — **props do not unlock midi routing** (contrast audio §1) |
| `--target 0` or `-P node.autoconnect=false` | `Stream/Output/Midi` node publishes unlinked — the publish path works, only resolution fails |
| `pw-midirecord --target Midi-Bridge` + `aplaymidi -p 14:0` | no link, but writes a **26-byte skeleton SMF** (`MThd`+`MTrk`+EOT only) — class `midirecord_skeleton_on_refusal` |
| `pw-midirecord --target 0` + `pw-link "Midi-Bridge:…(capture)" "r87mr_pin:input_1"` + `aplaymidi` | **rc=0 link, 45-byte SMF containing both events** (C4 on/off, E4 on/off — `90 3c 60`/`80 3c 00`/`90 40 60`/`80 40 00` in payload hex) — **end-to-end midi through the bridge works via pin** |
| `pw-mididump` bare | creates `midi-dump` node (`media.type=Midi`, `media.category=Filter`, `media.role=DSP`, `node.want-driver=true`, no `media.class`), single `input` port, silent |
| `midi-dump` + pin bridge→`midi-dump:input` + `aplaymidi` | **stdout: `Note On C4 vel 96` @0.42 s, Off @2.42, E4 on @3.42, off @4.42** — live dump works through the pin |
| `pw-mididump <file.mid>` | **offline SMF parser** — prints track/sec-stamped events, exits rc=0 |

Port-pin law is **media-agnostic**: the same `pw-link` that pinned audio in
r78 carries midi events with real payloads. (`pw-link -l` prints the bridge
port's long name verbatim — a `Midi-Bridge:Midi` short string seen in one
receipt is a parser display artifact; only one real link existed per the
`-o`/`pw-dump` cross-check.)

---

## 6. FRONTIER — remote-sink / RAOP (`receipts/s6-remote.json`)

- **No `remote*` graph objects exist** (`pw-dump` scan: `remote.name` props
  only on Client objects — `[pipewire-0-manager,pipewire-0]` sockets; no
  remote node/sink classes). No RAOP/AirPlay/zeroconf objects of any kind.
- **No RAOP path exists on disk**: `/usr/lib/pipewire-0.3/` carries 34
  `libpipewire-module-*.so` — nearest network surfaces are `rtp-sink`,
  `rtp-source`, `rtp-sap`, `netjack2-*`, `vban-*`, `pulse-tunnel`,
  `pipe-tunnel`. No raop/zeroconf/airplay `.so`, no spa plugin, no pulse
  module dir. `pacman -Qs raop` empty; **avahi-daemon IS running** — the
  discovery backend exists but nothing consumes it.
- Refusal classes (×3 each, identical):

| attempt | class |
| --- | --- |
| `pactl load-module module-raop-discover` / `module-zeroconf-discover` / `module-raop-sink` / `module-totally-bogus` | rc=1 `Failure: No such entity` — **one class, indistinguishable reasons** |
| `pw-cli load-module libpipewire-module-raop-discover` / `-zeroconf-discover` / `-null-sink` / `module-null-sink` | `Error: "Could not load module"` — one class (native dir lacks all four; `module-null-sink` works only through pulse-protocol, not the native name) |
| `pw-cli connect r87_no_such_remote` | `Error: "failed to connect: Host is down"` |
| `pw-cat -R r87_no_such_remote -p` / `PIPEWIRE_REMOTE=… pw-play` | rc=1 `error: pw_context_connect() failed: Host is down` (class `remote_host_down`, identical ×3) |
| `pw-cat -R pipewire-0 -p --target 0 -n 48000` (valid remote, unlinked) | connects fine, then **stalls unlinked** >15 s (consistent with r78 `unlinked_stall`) |

---

## 7. Arm table (verbatim-armable)

`NS` = seat-owned `module-null-sink` (`pactl load-module module-null-sink
sink_name=r87_ns …`, unload by index after `sink_name=` verify);
`DEF` = `pactl get-default-sink` (was SPDIF); `T.wav` = 48 k s16 stereo
dual-tone 12 s; `T.mid` = SMF fmt0 (C4/E4, 4 s); all fresh processes.

| # | arm | expected |
| --- | --- | --- |
| A1 | `pw-play -P node.name=X --target NS T.wav` | links `X:output_F{LR} → NS:playback_F{LR}` |
| A2 | `pw-cat -p …` (A1 otherwise) | identical witness |
| A3 | `pw-cat --target NS T.wav` (no mode) | rc=1 `one of the playback/record options must be provided` + usage, **no node** |
| A4 | `pw-cat --capture T.wav` / `--duplex` | rc=1 `unrecognized option` + usage |
| A5 | `pw-cat -p -r …` vs `-r -p …` | `Stream/Input/Audio` vs `Stream/Output/Audio` (last wins) |
| A6 | `pw-play -r` / `pw-record -p` | Input / Output — flag overrides argv0 |
| A7 | `--target garbage` | links to `DEF` (playback fallback) |
| A8 | `--target NS -P target.object=garbage` / inverse | fallback / NS — **prop beats flag** |
| A9 | `--target <object.serial>` / `<object.id>` | NS / fallback to DEF |
| A10 | `--target 0` | node publishes, links {} |
| A11 | `--target <source-name>` / `NS.monitor` | fallback to DEF |
| A12 | `PIPEWIRE_PROPS='{target.object=NS}' --target garbage` | NS |
| A13 | spawn playback on NS; `pw-cli` (≥1 s warmup): `set-param <id> Props {volume:0.25}` while monitor-recording NS | monitor RMS drops to **0.25×** then restores on `{volume:1.0}`; `{mute:true}` → **0** |
| A14 | `set-param <id> Format { …valid pod… }` on the running node | `enum-params Format` **unchanged** (silent discard) |
| A15 | `send-command <NS-id> Suspend {}` then `info` | `state: "suspended"` |
| A16 | `destroy <own-stream-id>` | node gone; pw-play exits rc=1 `stream node N unconnected` |
| A17 | `enum-params <foreign-sink> Props`; `set-param …Props {volume:<same>}` | full pods; echo + `node changed`, no error — **no FOREIGN gate** |
| A18 | `info/enum-params/set-param/destroy/get-permissions 99999999` | `unknown global '99999999'` every verb |
| A19 | `pw-midiplay --target {Midi-Bridge, serial, garbage} T.mid` | `no target node available` + `res:-2`, rc=1 — all dead |
| A20 | `pw-midirecord --target 0 rec.mid`; `pw-link "Midi-Bridge:Midi Through: Port-0 (capture)" "rec:input_1"`; `aplaymidi -p 14:0 T.mid` | pw-link rc=0; rec.mid ≈45 B with `90 3c 60`/`80 40 00` events |
| A21 | bare `pw-mididump` + pin bridge capture → `midi-dump:input` + aplaymidi | stdout `Note On C4 vel 96` … `Note Off E4` with sec stamps |
| A22 | `pw-mididump T.mid` | offline parse: `sec:0 Note On C4`, `sec:2 Note Off`, … rc=0 |
| A23 | `pactl load-module module-raop-discover` | rc=1 `Failure: No such entity` |
| A24 | `pw-cli load-module libpipewire-module-raop-discover` | `Error: "Could not load module"` |
| A25 | `pw-cat -R r87_no_such_remote -p T.wav` / `PIPEWIRE_REMOTE=…` | rc=1 `pw_context_connect() failed: Host is down` |
| A26 | `pw-cli info <live-id>` at **zero warmup** | `unknown global '<live-id>'` — cold-registry artifact, not absence |

---

## 8. Named classes added this round

| class | signature | where |
| --- | --- | --- |
| `pwcat_mode_required` | `error: one of the playback/record options must be provided` + usage rc=1 | bare `pw-cat`, `pw-cat -m` |
| `pwcat_unknown_longopt` | `pw-cat: unrecognized option '--X'` + usage rc=1 | `--capture`, `--duplex` |
| `pwcat_flag_last_wins` | `-p -r`→record, `-r -p`→playback; overrides argv0 | mode flags |
| `dsd_read_fail` | `dsdfile: can't read dsd file '…': Invalid argument` + `open failed` | `pw-cat -d -p` on wav |
| `prop_beats_flag_playback` | `target.object`/`node.target` prop > `--target`, playback direction | s1 legs |
| `playback_fallback_default` | any unresolvable/wrong-class `.monitor`/source target → current default sink | s1 legs |
| `pwcli_cold_registry` | `unknown global '<id>'` on live ids pre-sync | zero-warmup leg A26 |
| `pwcli_unknown_global` | `"<verb>: unknown global '<id>'"` all verbs | info/enum/set/destroy/get-perm |
| `pwcli_unknown_param` | `set-param: unknown param type: <T>` | NoSuchType/BogusType |
| `pwcli_invalid_pod` | `set-param: invalid pod: Expected object key` | malformed pod |
| `props_unknown_key_silent_drop` | `{no_such_prop:…}` → size-8 empty Props, no error | own + foreign nodes |
| `props_live_mutation` | Props volume/mute writes land mid-stream at exact ratio | §3.1 |
| `format_sealed_running` | `set-param Format` (any valid pod) silently discarded on running node | §3.2 |
| `sendcommand_state_lands` | `Suspend`/`Pause` → `state:"suspended"`; `unknown node command type: X` refusal | §3.3 |
| `pwcli_unknown_factory` | `@proxy:N` then async `res:-2 unknown factory name` | create-node/-device |
| `pwcli_factory_usage` | `res:-22 usage: factory.name=…` | create-node missing req prop |
| `pwcli_session_bound_node` | `create-node` object lives only while pw-cli is connected | §3.3 |
| `pwcli_destroy_module` | `destroy <module node's id>` → whole `module-null-sink` unloads | destroy_sink leg |
| `no_foreign_gate` | foreign-node enum/set-param accepted identically | §4 |
| `no_target_node_midi` | `no target node available`+`res:-2` on ALL midi targets/props | s5 |
| `midirecord_skeleton_on_refusal` | 26-B `MThd`+`MTrk`+EOT file despite target failure | s5 |
| `midi_pin_works` | manual `pw-link` on midi ports rc=0, carries real events | s5/s8 |
| `remote_host_down` | `pw_context_connect() failed: Host is down` rc=1 | -R/env/pw-cli connect |
| `pactl_module_no_such_entity` | `Failure: No such entity` for every missing module name | s6 |
| `pwcli_module_load_fail` | `Could not load module` for every native missing name | s6 |

---

## 9. Contention ledger

| time (UTC) | foreign actor | observation / effect |
| --- | --- | --- |
| ~06:40 | `r86ctl_*` (round-86 seat) | `r86ctl_ns` + `input.r86ctl_src` remap-source present and linked; **unloaded by its seat mid-window** (gone by ~06:55) — my foreign-node arm re-resolved and used the WP-owned HDMI sink instead |
| 06:50–07:20 | `r79lb_*` (round-79 loopback seat) | **three respawning instances** (pid 3770658 → 3835457 → 3943556): `ns_a/ns_b` null sinks, `a2_space`/`b06_zero`/`d2c` streams, `a6_tap` on SPDIF monitor; their `pw-link`/client churn is visible inside my pw-cli logs (hundreds of async events). **My verdicts never depend on their objects** — all routing legs are `pw-link` link-witness, not content, and my sinks are name-spaced |
| whole window | waybar, xdg-desktop-portal, wireplumber, pipewire-pulse | idle-present; unmeasured |
| ~07:05 | SPDIF monitor | foreign `a6_tap` present — any content-leveraging default-sink fallback legs are therefore pinned by **link witness**, not payload |

My own side-effects: identical-value Props write on HDMI sink (unchanged);
reader-pins onto `Midi-Bridge` (adds readers, touches nothing else's flow);
`Suspend` on my own `r87_ns`; all `r87*` objects unloaded (0 left).

---

## 10. Falsification list (must-differ inputs)

1. "prop beats flag on playback" — a `--target NS -P target.object=garbage`
   leg that links to NS, or a `--target garbage -P target.object=NS` leg
   that falls back.
2. "serial resolves, id doesn't" — a `--target <object.id>` leg that links
   to the named node, or an `<object.serial>` leg that falls back.
3. "playback falls back to DEF" — a garbage-target leg that links to
   anything that is not the live `pactl get-default-sink`, or refuses.
4. "mode flags last-wins" — a `-p -r` leg publishing `output_*` ports, or
   `-r -p` publishing `input_*`.
5. "no duplex" — a single pw-cat node carrying both `input_*` and
   `output_*` (non-monitor) ports produced by flags alone.
6. "Props mutate mid-stream" — a `set-param Props {volume:0.25}` leg where
   monitor RMS ≠ ~0.25×±1 %, or a `mute:true` leg with nonzero window RMS.
7. "Format is sealed" — an `enum-params Format` **after** a valid-pod
   set-param that shows a different rate/format than before, on a RUNNING
   node (the claim is scoped to running streams; on an unlinked/
   `node.autoconnect=false` node it is not measured).
8. "no FOREIGN gate" — any `Error:`/refusal line from `set-param` or
   `enum-params` on a foreign-owned node that does not also occur on an
   own node (permission-denied class).
9. "midi --target is dead" — ANY `--target`/`-P target.object` leg that
   produces a link to a Midi/* node.
10. "midi pin carries events" — a pinned capture whose SMF payload lacks
    the injected `0x90/0x80` events, or where `pw-link` on midi ports
    refuses (rc≠0).
11. "remote surface absent" — appearance of a raop/zeroconf `.so` in
    `/usr/lib/pipewire-0.3/` or any `remote*`-classed object in `pw-dump`;
    a `pactl load-module module-raop-discover` returning a module index.
12. "refusal classes uniform" — a missing-name module load that returns a
    *differentiated* error (e.g. names raop vs zeroconf differently).
13. "cold-registry artifact" — a zero-warmup `pw-cli info <live-id>` that
    succeeds, or a warm `info <bogus-id>` that fails differently.

---

## 11. Source anchors

- `corpus/live/r87-scout/r87_probe.py`, `r87_probe_b.py` — harnesses.
- `receipts/s0-inventory.json` … `s7-stability.json`, `s8-supplement.json`,
  `summary.json` — consolidated legs.
- `runs/s3-mutate.pwcli` (full session incl. volume/mute/Format/send-command
  marks), `s4-foreign*.pwcli`, `s6-remote.pwcli`, `sb-*.pwcli`,
  `s3_monitor.wav` (the mutation witness), `midirec_pin.mid` (45 B pinned
  capture), `m_*.wav` (mode-leg captures).
- Prior-law context: `reports/round-78/r78-scout.md` (prop lattice, pin law,
  `no_target_node`, `unlinked_*`), `round-85/r85-scout.md` (serial/id
  namespace split, module unload discipline).

---

## 12. Unknowns / not exercised

- **`destroy`/`send-command`/`permissions`-write/`pactl move-sink-input` on
  FOREIGN objects** — deliberately unexercised (destructive under live
  seats); `no_foreign_gate` predicts them allowed. Needs a quiesced host
  or a consenting foreign node to verify.
- **`set-param Format` on an UNLINKED/pre-negotiation node** — may
  renegotiate; only the running-state seal is pinned.
- `send-command` resume direction (`Start`/`Resume` command names) and the
  full command-id table — `Suspend`/`Pause` measured, others unknown.
- `create-node` non-adapter factories + `create-device` with a real
  factory; whether a created node can outlive its session
  (`object.linger` semantics) — only the session-bound shape measured.
- `pw-mididump` `-M ump` (UMP mode) and `pw-cat -s`/`-c` (SysEx/midi-clip)
  mode nodes — flagged but not characterized.
- Whether `Format`/`PortConfig`/`Latency`/`Tag` writes on **sinks/sources**
  (driver nodes) vs stream nodes differ — Props measured on both shapes,
  Format only on a stream.
- The `-R`/`PIPEWIRE_REMOTE` surface beyond refusal (`pipewire-0` control
  leg only); no second socket was opened.
- `pw-mididump` file-arg on non-SMF input; `pw-midirecord` UMP capture;
  event-timing fidelity of the bridge (deltas re-encoded vs SMF input).

---
*scout leaf — measured, not judged.*
