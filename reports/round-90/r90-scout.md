# R90 scout — WirePlumber settings/restore persistence · pipewire-pulse module namespace edges · pw-v4l2 bridge · pw-link grammar · EnumFormat mid-stream

Round 90 pre-measurement. Host `plazir27`, measured **2026-10-15 11:12–11:28
UTC−3** (14:12–14:28Z). Repo `~/Projects/shokunin/audio-shokunin` @ HEAD
`ee6d684` (`r79 LOG: ADMIT-corr`). Toolchain: PipeWire **1.6.8**
(pipewire / pipewire-audio / pipewire-pulse / pipewire-alsa / pipewire-jack
1:1.6.8-1; **pipewire-zeroconf and pipewire-v4l2 NOT installed**), WirePlumber
**0.5.17-1**, libpulse **17.0-98-gb096** (protocol 35), avahi-daemon **active**
(pid 1364, `plazir27.local`), Python 3.14.7, Linux 7.2.3-arch1-3.

**Seat: SCOUT (leaf). Zero tracked-file edits.** `git status` tracked-dirty at
entry and exit is exactly `SHONEN.md` + `corpus/fixtures/measure_audio.py`
(sibling-owned, never read/imported/executed here; own tone synth + own
classifiers). Every write is under `corpus/live/r90-scout/` (5.6 MB: `runs/`
3.0 MB, `receipts/` 940 KB, 3 tone WAVs, 4 harnesses) plus this report. **Not
committed. No `--probe-*` was ever invoked.**

**Teardown verified.** 60 leg dirs / 423 stdout captures / 1269 raw files.
Exit graph: **0 `r90*` nodes, 0 links**, module set = baseline
`1,2,4,6,8,10,12,14,16,17,18,20,22,536870912–915` (the last four are the
config-preloaded pulse stubs). Every mutating leg loaded seat-owned
`module-null-sink`/streams named `r90*` and unloaded **by ID** — with one
exception that is itself a finding (C13) and one interference event caused by
this seat (§5).

**Sibling-scope conflict observed.** The dispatch brief says r89 scouts
"pw-jack/metadata/spa". The *live* r89 harness on disk is
`corpus/live/r89-scout/r89_probe.py`, whose docstring reads "r89 scout harness —
**pw-profiler output lattice** on PipeWire 1.6.8", with receipt keys
`profiler_module_id`, `clock_cycles`, `driver_latencies`, `j_n8`, `plain_o_n4`.
The brief's profiler candidate was therefore **dropped from this seat** and
profiler was not measured; pw-jack and PipeWire metadata objects were not
exercised either (the `default`/`sm-settings` metadata objects are used only as
read-only witnesses for the restore law, §1.2).

---

## 0. Headline — the frontier cells

| # | candidate | verdict | the single sharpest measured fact |
| --- | --- | --- | --- |
| 1 | WirePlumber settings persistence | **25 settings, all at default; no persistence file exists** | `wpctl settings` prints 25 typed settings; `~/.local/state/wireplumber/` contains **only** `default-nodes` (410 B) and `stream-properties` (402 KB) — **no `settings` file**, so every shown value is the built-in default and `wpctl settings -s` (save) has never been used here; the live values are the `sm-settings` metadata object (id 39, 25 keys), the schema is `schema-sm-settings` (id 37) |
| 2 | session-manager restore | **PINNED, four laws** | the store is `~/.local/state/wireplumber/stream-properties` (2691→2750 rows in-seat), keyed `formKey` = `<media.class minus "Stream/">:{application.id\|application.name\|media.name\|node.name}:<value>`; **writes are debounced ≈1.0–1.2 s** (creation 1.10 s, target 1.03 s, `pw-cli` volume 1.22 s, 3/3 each) but a pulse-protocol volume write lands **≤0.01 s**; **replay with the same key is routed to the stored target** (3/3, link + `default` metadata `target.object` witness); opt-out props `state.restore-props=false` / `sink_properties=state.restore-props=false` suppress the row (3/3, late witness) |
| 3 | pipewire-pulse module edges (tunnel / zeroconf / roc) | **4 of 10 loadable; the id can be a phantom** | `pactl load-module module-tunnel-sink server=127.0.0.1:1` → **rc 0 + module id, but the module is already gone at the first probe (≈0 ms) and `unload-module <id>` → `Failure: No such entity`** (8 probes over 2 s, 3/3); `module-zeroconf-discover` → `No such entity` while **`module-zeroconf-publish` loads** (rc 0) — publish yes, discover no, on the same build; `module-roc-sink sink_name=…` → `Invalid argument`, `module-roc-source` → `No such entity`; the four preloaded stubs re-load as `Failure: Entity exists` |
| 4 | `pactl unload-module <name>` | **LANDMINE — name form unloads EVERY module of that name** | with four `module-null-sink` modules loaded (2 mine + 2 leftovers) one `pactl unload-module module-null-sink` left **0** (3/3); this seat's own by-name probe destroyed a sibling's `r79lb_ns_*` sinks (§5) |
| 5 | pw-link grammar | **single-pair grammar, extras silently ignored; `-w` blocks forever** | `pw-link A B A2 B2` links **only the first pair** (rc 0, no warning, 3/3); `pw-link -d A B A2 B2` disconnects **only the first pair** (2→1 links); `pw-link -d <id1> <id2>` → rc 255 `failed to unlink ports: No such file or directory` **and nothing is unlinked**; `pw-link -w A <missing>` **does not return** (killed at 2–3 s, 3/3, both directions); globs work for listing (`-o 'r90a:*'`) but **not** for connecting (`failed to link ports: No such file or directory`) |
| 6 | EnumFormat mid-stream | **capability set is invariant; Format is write-only until negotiated; a mid-stream sink-side write is rejected −5** | sink-node `EnumFormat` is byte-identical at rest / mid-stream / after (`sha 1735b473…`, 3/3) while the stream node's `Format` tracks the **file** rate (S16LE/48000 vs S16LE/44100) and the sink node's `Format` stays the **graph** rate (F32P/48000); `pw-cli set-param <sink-node> Format {…44100…}` mid-stream → `res:-5 (Input/output error)` while **stdout still echoes the pod** (rc 0) |
| 7 | pw-v4l2 bridge | **ABSENT-CLASS, structurally unmeasurable** | `pw-v4l2` binary and man page absent; `extra/pipewire-v4l2 1:1.6.8-1` exists in the repo but is **not installed**; `libspa-v4l2.so` (137704 B) ships with pipewire; **no `/dev/video*`, no `/sys/class/video4linux`, no v4l2/uvc kernel module**; yet `session.services` still advertises `api.v4l2` and `pw-cli ls Device \| grep -c v4l2` = **0** — the r88 bluez lesson (advertisement ≠ objects) repeats |

---

## 1. Author-ready cells (with the falsifier that was actually tried)

Each cell: **claim** · **evidence** (receipt + reps) · **falsifier attempted** ·
**residual risk**.

### 1.1 Settings & state-file lattice
- **C1 — `wpctl settings` is a 25-entry typed lattice and nothing on this host
  has been saved.** `f1` s1 (`receipts/f1.json`, 3/3 byte-identical): 25 ids,
  each with Name/Desc/Type/Default/Value; types seen: Boolean, Float (with
  `[Min: Max]`), Integer, String (with `null` default). Persistence flags from
  `wpctl settings -h`: `-d/--delete`, `-s/--save`, `-r/--reset` (s2, 3/3).
  *Cross-witness:* the live `sm-settings` metadata object (pw-dump id 39)
  carries **exactly the same 25 keys, key-for-key** as `wpctl settings`
  (25/25 set-equal), so the CLI is a view of that metadata object.
  *Falsifier tried:* state-dir inventory (s3) and settings-module strings (s7) —
  no `settings` file, and the module's strings carry
  `adding persistent setting to %s metadata: %s = %s` / `persistent setting
  updated` / `sm-settings` (so the file would appear on first save).
  *Residual:* `wpctl settings -s` was **not** run (it would write operator state)
  — the file name is therefore *named*, not observed.
- **C2 — two settings rows are cross-observable in live graph state.**
  `device.routes.default-sink-volume: 0.064` (C1) matches the SPDIF sink node's
  live `Props.channelVolumes [0.063997, 0.063997]` (`pw-dump` node 46);
  `node.stream.restore-props: true` / `node.stream.restore-target: true` are the
  switches the restore hooks subscribe to
  (`/usr/share/wireplumber/scripts/node/state-stream.lua:489-520`).
  *Falsifier tried:* `wp-cli`/`pw-dump` read of the same node — values agree.
  *Residual:* one host, one node class.
- **C3 — the restore DB file name and key grammar are source-traceable.**
  `State ("stream-properties")` at `state-stream.lua:491`;
  `State ("default-nodes")` at `default-nodes/state-default-nodes.lua:182`;
  `State ("default-routes")` at `device/state-routes.lua:352`;
  `formKey()` at `state-stream.lua:462-487` (order `application.id` →
  `application.name` → `media.name` → `node.name`, with
  `media.role == "Notification"` → `<class>:media.role:Notification`).
  *Live confirmation:* all 13 observed key shapes in the file match the function
  (f1 s5/s6), including `Output/Audio/Midi:application.name:*` and
  `Audio/Source/Sink:application.name:*` from earlier sibling experiments.

### 1.2 Restore write/read law (session-manager behaviour)
- **C4 — the store is debounced ≈1 s for node-Props changes.** New stream with a
  unique `application.name` → row appears at **1.10 s** (f2c D, 3/3; null at
  0.01/0.16/0.32/0.47 s). `pw-cli set-param Props {volume:0.5}` → stored
  `volume: 0.5` at **1.22 s** (f6b A, 3/3). `pactl move-sink-input` → stored
  `target: "r90b"` at **1.03 s** (f2d, 3/3). *Falsifier tried:* short-window polls
  (f6, 0.1 s) — those **missed** the update and are reported as invalidated, not
  as absence; the long-window polls are the evidence.
- **C5 — a pulse-protocol volume write is stored in `channelVolumes`, not
  `volume`, and lands immediately.** `pactl set-sink-input-volume <idx> 50%` →
  row `channelVolumes: [0.125, 0.125]` with `volume: 1.0` and poll hit at
  **0.01 s** (f2c V, 3/3) — 0.125 = 0.5³, i.e. the pulse cubic curve. A raw
  `Props.volume` write stores in `volume` instead (C4). *Falsifier tried:*
  a `volume`-field poll (f6b B) stayed 1.0 → that check is the negative control
  for the field split. *Residual:* why the pulse path bypasses the ~1 s debounce
  is **unresolved** (mechanism not traced).
- **C6 — restore replays what was stored.** Same key replayed with no `--volume`:
  live `Props` show `volume 1.0` + `channelVolumes 0.125` (f2c V, 3/3) —
  i.e. the pulse-written field is restored, the untouched field is not.
  *Falsifier tried:* the pre-store replay baseline showed 1.0/1.0 (f6b C).
- **C7 — target restore works and is witnessable two ways.** Store
  `target: r90b` (C4), then replay **without** `--target` → `pw-link -l` shows
  `r90b:playback_FL |<- r90z{rep}b:output_FL` (f6b D + f2d, 3/3) and the
  `default` metadata object carries `{subject: <node bound-id>, key:
  "target.object", type: "Spa:Id", value: <object.serial>}` (f2d, 3/3).
  *Falsifier tried:* the f6 t5 replay — the move leg never ran there because
  `pactl list sink-inputs short` carries no `application.name` (index parse
  returned None), so that replay had no stored target and landed on the
  **operator's SPDIF default sink** (`pactl list sink-inputs short` → sink index
  63, `pw-link -l` → `…SPDIF__sink:playback_FL |<- r90t{rep}b:output_FL`).
- **C8 — opt-out is per-stream *and* per-device-node.** Streams:
  `-P state.restore-props=false` → no row after 4 s (f6 x3, 3/3), no `r90x*`
  residue at stage end. Device nodes: `pactl load-module module-null-sink
  sink_name=… sink_properties=state.restore-props=false` → no row, while the
  control sink's row appears (f6b F, 3/3 **late witness**: the in-leg check at
  1.0 s was too early for the ≈1.1 s debounce and is reported as invalidated).
- **C9 — the store also keys route-less device nodes, so every named null sink
  leaves a permanent row.** This seat's 57 residue rows split
  `19 Audio/Sink:node.name` + `29 Output/Audio:application.name` +
  `6 Input/Audio:application.name` + `3 Output/Audio:application.id`; the operator's file already held **669**
  `Audio/Sink:node.name:*` rows and 2468 `:r\d\d*` sibling rows before this seat
  (f1). Row deletion is **not exposed** by `wpctl`/`pactl` on this host
  (`wpctl settings -d` covers settings keys, not the stream store).
  *Falsifier tried:* full-file re-parse at entry/exit (2691 → 2749 rows).
- **C10 — capture streams need the r77-pinned prop, and a dying stream still
  stores.** `pw-record --target <sink>` (with/without `.monitor`, or with a
  bogus name) fails `no target node available` (rc 1) — **already pinned in
  r76/r77** (`reports/round-76/r76-scout.md:33,39,104-105`;
  `reports/round-77/r77-author.md:328`), so this seat's first capture legs are
  **invalidated by design**, not new evidence. With `-P
  stream.capture.sink=true` the capture runs and stores
  `Input/Audio:application.name:r90k{rep}` (f2c K, 3/3, rc 0 alive). A stream
  that errors out in <1 s (`r90g{rep}`, f6b E) **still wrote its row** — the
  store is keyed on node/Props creation, not on a successful flow.

### 1.3 Pulse module namespace
- **C11 — the pulse module namespace on this build, measured by load+unload
  (3 reps each).**

  | module | rc | error / effect | object created |
  | --- | --- | --- | --- |
  | `module-null-sink sink_name=r90ns` (control) | 0 | id | sink node, unload rc 0 |
  | `module-tunnel-sink server=127.0.0.1:1 sink_name=r90tun` | 0 | **id is a phantom** | none |
  | `module-tunnel-source server=127.0.0.1:1 source_name=r90tuns` | 0 | **id is a phantom** | none |
  | `module-tunnel-sink … reconnect_interval_ms=1000` | 0 | **stays resident** | none until remote answers |
  | `module-tunnel-sink server=` (empty) | 0 | stays resident | none |
  | `module-tunnel-sink sink_name=…` (no server) | 1 | `Failure: Invalid argument` | — |
  | `module-zeroconf-discover` (+`latency_msec=100`) | 1 | `Failure: No such entity` | — |
  | `module-zeroconf-publish` | 0 | loads; unload rc 0 | none (avahi-linked impl; publishes, not traced) |
  | `module-roc-sink sink_name=…` | 1 | `Failure: Invalid argument` | — |
  | `module-roc-source` | 1 | `Failure: No such entity` | — |
  | `module-raop-discover` | 1 | `Failure: No such entity` | — |
  | `module-pipe-tunnel` | 1 | `Failure: No such entity` | — |
  | `module-stream-restore` / `-device-restore` / `-always-sink` | 1 | `Failure: Entity exists` | preloaded by config |
  | `module-switch-on-connect` | 0 | loads; alive at first check; unload rc 0 | none |
  | `module-rtp-send source=r90a.monitor` | 0 | loads; alive at first check; unload rc 0 | none named r90* |
  | `module-not-a-module` | 1 | `Failure: No such entity` | — |

  Static support: 49 `module-*` names embedded in
  `libpipewire-0.3/libpipewire-module-protocol-pulse.so`; `libavahi-client.so.3`
  linked into it; **no** `libpipewire-module-zeroconf-*.so` and **no**
  `libpipewire-module-roc-*.so` in `/usr/lib/pipewire-0.3/`;
  `libpipewire-module-pulse-tunnel.so` present. The four stub rows are the
  `pulse.cmd` list in `/usr/share/pipewire/pipewire-pulse.conf:70-79`.
  *Falsifier tried:* name-only vs arg-complete variants, `find`, `pacman -Ql`,
  man pages `pipewire-pulse-module-{tunnel-sink,tunnel-source,zeroconf-discover,
  zeroconf-publish,roc-sink}(7)` (all shipped — **a shipped man page is not a
  present implementation**).
- **C12 — "id returned" ≠ "module alive".** For an unreachable remote the
  tunnel module self-destructs before `pactl` returns: 8 probes at
  0/31/63/122/251/502/1003/2004 ms all show the id absent from
  `pactl list modules short`, no node, no sink, and `unload-module <id>` →
  `Failure: No such entity` (f2b, 3/3). Any harness that trusts the returned id
  will leak or mis-attribute.
- **C13 — `pactl unload-module <name>` is an all-matching unload.** Controlled:
  4 `module-null-sink` modules → one by-name unload → **0** remain (f2c U, 3/3).
  Use the id.

### 1.4 pw-link
- **C14 — the connect/disconnect grammar is strictly one pair.** Connect takes
  `output input`; extra positionals are **silently ignored** (`pw-link A B A2 B2`
  → 1 link, rc 0); a bad first pair fails the whole call in order
  (`bogus bogus A B` → rc 255, nothing linked; `A B bogus bogus` → rc 0, first
  pair linked); reversed direction `in out` → `No such file or directory`
  (no auto-swap); duplicate → `failed to link ports: File exists`; self-link
  (monitor→playback of one node) is accepted; globs are rejected for connect.
  Disconnect takes a single link id **or** one pair; two ids → rc 255 and
  **nothing unlinked** (f4/f4b, 3/3).
- **C15 — `-w` blocks indefinitely.** `pw-link -w <missing-output> <in>` and
  `-w <out> <missing-in>` both fail to return within 2–3 s (killed by the
  harness, `timed_out=True`, 3/3). Never call `-w` without an external bound.
- **C16 — listing patterns are slot-bound.** `pw-link -o 'r90a:*'` filters
  outputs, but `pw-link -i 'r90b:*'` prints **all** inputs — the glob landed in
  the *out-pattern* slot; `pw-link -i '' 'r90b:*'` filters correctly (manual,
  reproduced). `pw-link -l <pattern>` printed nothing in a no-link window (not
  conclusive — named as unmeasured).
- **C17 — link ids and link objects.** `pw-link -I -l` puts the **link id as the
  first token of the `|->` row** (the port id is the second); `pw-dump` Link
  objects carry `factory.id 21, link.input.node/port, link.output.node/port,
  object.linger true` — **`pw-link -P` (passive) produces props indistinguishable
  from a normal link** (no `link.passive` key, 3/3) and `pw-link -t` printed
  **no rows** for a null-sink↔null-sink link, with or without a live tone stream
  (`-t`, `-t -v`, `-t -I`, 3/3). Whether `-t` ever prints rows on this host is
  **unmeasured** (needs a device-backed link).

### 1.5 EnumFormat / Format
- **C18 — EnumFormat is capability, Format is instance.** Null-sink node
  `EnumFormat` = `{raw, format Enum[F32P,F32P,F32LE], rate Range[48000, min 1,
  max 2147483647], 2ch FL/FR}` and is **byte-identical** at rest / mid-stream
  48 k / after (3/3, sha `1735b473…`); the SPDIF device node's range is
  `[48000, 44100, 192000]` (i.e. 44100–192000) — the *node* advertises rates,
  the *port* advertises the dsp format (`mediaSubtype dsp, F32P`, size-80 pod).
- **C19 — Format readability is negotiation-state dependent.** `pw-cli
  enum-params <node|port> Format` → `res:-5 (Input/output error)` at rest; the
  **port** becomes readable only while linked, the **node** stays readable after
  the stream ends (sticky) — 3/3. `pw-dump` shows `Format: []` for the same
  objects (write-only flag) — consistent with r88's `-w` finding.
- **C20 — the graph rate is the adapter's, the file rate is the stream's.**
  Live stream node `Format` = `S16LE @ 48000` for the 48 k file and
  `S16LE @ 44100` for the 44.1 k file (distinct sha, 3/3), while the sink node's
  `Format` stays `F32P @ 48000` in both (identical sha `91f73422…`, 3/3).
- **C21 — mid-stream sink-side `set-param Format` is rejected, and stdout
  lies.** `pw-cli set-param <sink-node> Format { mediaType:1, mediaSubtype:1,
  format:259, rate:44100, channels:2 }` mid-stream → stderr
  `res:-5 (Input/output error): set param id:4 failed`, **rc 0**, stdout prints
  the full 128-byte pod it parsed, link survives, stream stays alive, node
  `Format` unchanged (3/3). r87's stream-node variant was "silently discarded";
  the sink-node variant is an explicit error — the seal is **node-class
  dependent**. General rule: **`pw-cli` rc is not a validity witness; parse
  stderr.**

### 1.6 pw-v4l2
- **C22 — the bridge cannot be measured on this host, and the advertisement is
  decoupled from objects.** `which pw-v4l2` empty, no `pw-v4l2` man page,
  `pacman -Qs pipewire-v4l2` empty (`extra/pipewire-v4l2 1:1.6.8-1` is available
  but not installed), `libspa-v4l2.so` present (137704 B, 44 `v4l2` strings),
  `ls /dev/video*` → absent, `/sys/class/video4linux` absent, `lsmod | grep -icE
  'v4l2|uvcvideo'` → 0, `pw-cli ls Device | grep -c v4l2` → 0, `pw-dump`
  `device.api` set = `["alsa"]` — while `pactl list` still advertises
  `api.v4l2` in `session.services` (3/3). Same decoupling law as r88's bluez.

---

## 2. Falsification list (what was tried that could have killed each claim)

| claim | falsifier attempted | outcome |
| --- | --- | --- |
| settings are persisted on this host | state-dir inventory + settings-module strings + `wpctl settings -h` flags | **no `settings` file**; values = defaults; save path *named*, not executed |
| the store write is visible immediately | 0.1 s poll windows (f6) | **check invalidated** — the 0.1 s window only ever saw the pre-existing row; the long-window re-measure is 1.03–1.22 s (C4) |
| store write is always ~1 s | pulse-protocol volume write | **falsified** — lands ≤0.01 s, in `channelVolumes` |
| store fires only at stream teardown | creation-time poll with the stream alive | **falsified** — row appears ~1.1 s after creation |
| restore replays the field that was written | replay of a pulse-written key (f2c V) | **field split measured**: `volume` stayed 1.0 while `channelVolumes 0.125` was applied; the `pw-cli`-written `volume` field was stored (1.22 s) but **not** replay-tested |
| `pactl load-module` success means a live module | 8 timed probes + unload + node/sink search | **falsified 3/3** for unreachable tunnel (phantom id) |
| zeroconf is all-or-nothing on this build | discover and publish loaded separately | **split**: discover `No such entity`, publish rc 0 |
| `unload-module <name>` removes one module | 4 same-named modules, one by-name unload | **falsified 3/3** — removes all |
| pw-link takes multiple pairs (bulk) | 4-arg connect and 4-arg disconnect with 2 links present | **falsified 3/3** — first pair only, extras ignored |
| pw-link `-d` accepts two link ids | two real link ids | **falsified 3/3** — rc 255, nothing unlinked |
| pw-link patterns work for connect | `pw-link 'r90a:monitor_*' 'r90b:playback_*'` | **falsified 3/3** — rc 255; patterns work only for listing |
| `-w` fails fast on a missing port | 2–3 s bounded runs | **falsified 3/3** — it blocks |
| passive links are visible in pw-dump | normal vs `-P` link objects, all props | **no marker found** (negative result) |
| EnumFormat shrinks after negotiation | rest vs 48 k vs 44.1 k vs post-stream | **falsified 3/3** — invariant |
| a sink can be renegotiated mid-stream | `set-param Format` on the live sink node | **rejected −5**, no renegotiation (3/3) |
| pw-record capture legs (first attempt) | r76/r77 pinned law re-read | **invalidated by design** (missing `stream.capture.sink`), re-run correctly in f2c |
| refusal probes changed host state | module-id set + `r90*` node/link search at every stage exit | unchanged at every stage **except** the by-name unload event (§5) |

---

## 3. Named coverage (not measured, and why)

- **Tunnel positive branch** (a real local sink appearing and carrying audio):
  needs a second PipeWire/Pulse server to answer on a socket — a daemon-level
  mutation, out of a scout's teardown-by-ID budget. `reconnect_interval_ms`
  keeps the module resident but exposes **no** node until the remote answers
  (measured), so the positive branch stays named.
- **zeroconf-discover positive branch**: the module refuses (`No such entity`)
  because no `libpipewire-module-zeroconf-discover.so` is installed
  (pipewire-zeroconf absent); publishing works but was not exercised end-to-end
  against a peer.
- **pw-profiler lattice**: owned by the live r89 harness (§ header conflict) —
  deliberately not measured here.
- **pw-jack, PipeWire metadata objects**: sibling r89 scope; the `default` /
  `sm-settings` metadata were read only as restore-law witnesses.
- **`pw-link -t` on a device-backed link**: never printed a row for a
  null-sink↔null-sink link with a live stream; whether it ever prints rows here
  is unknown.
- **Passive-link scheduling semantics**: only the prop surface was checked
  (no marker); whether `-P` changes scheduling was not measured.
- **`wpctl settings --save` / `--delete` write path**: not executed (would write
  operator state). The state file name is source/strings-derived, not observed.
- **WirePlumber user journal**: `journalctl --user -u wireplumber --since -2h`
  → `-- No entries --` (3/3) — the unit logs nothing to the user journal here;
  log-level behaviour is unmeasured.
- **Tunnel/roc/raop error taxonomy internals**: only the pulse-server error
  strings were captured; the mapping from string to native module file is
  inference (native files for zeroconf/roc are absent, pulse-tunnel is present).

---

## 4. Artifacts & provenance

`corpus/live/r90-scout/` (untracked, 5.6 MB):

- `scripts/r90_probe.py` (stages f1–f6), `r90_probe_b.py` (f2b/f4b/f6b),
  `r90_probe_c.py` (f2c), `r90_probe_d.py` (f2d) — leg functions, per-step raw
  capture, census before/after.
- `receipts/{f1,f2,f2b,f2c,f2d,f3,f4,f4b,f5,f6,f6b}.json` — per-leg/per-step
  argv, rc, stdout/stderr sha256, lengths, heads, parsed summaries, entry/exit
  census, `census_restored`.
- `runs/` — 60 leg dirs, 423 stdout captures, 1269 files; tone WAVs
  `r90_tone48.wav` / `r90_tone441.wav` / `r90_toneq.wav` (seat-synthesized).

**Stability.** All 11 stages ran 3 reps. Byte-stable across reps (except ids,
serials, timestamps, and the deliberately churning stream legs): f1 8/8 legs,
f2 10/10 module classes, f3 5/5, f4 19/19 signatures, f4b 8/8, f5 all format
shas (3/3 identical: EnumFormat `1735b473…`, sink Format `91f73422…`, stream
Format `e718690a…`/`684a7c8d…`), f6 6/7 findings (its capture leg invalidated by
design, C10), f6b 4/4, f2d 8/8. f2c's own P/T/Y legs were **invalidated**
(their `r90a`/`r90b` ports had been removed by the stage's own by-name unload
event, §5) and the valid ones (U, D, V, K) were 3/3 stable; P/T/Y were re-run
on per-rep sinks in f2d and are 3/3 there.
Stage windows: 11:20:26 (f1) → 11:28:0x (f2d end); harness wall per rep
0.02–24 s, whole seat ≈8 min of instrument time plus recon.

**Confidence.** High: the settings/state-file lattice; the restore write/read/
target/opt-out laws (multiple independent witnesses: store file, live Props,
`pw-link -l`, `default` metadata, source lines); the pulse module class table
(load + error string + file inventory, 3/3); the pw-link grammar (3/3);
EnumFormat/Format invariance and the −5 rejection (3/3, sha-identical);
the v4l2 absence class (5 independent witnesses). Medium: the pulse-volume
≤0.01 s store path (measured, mechanism unresolved); the `-t`/passive-link
negatives (scope-limited). Low: none of the headline cells rests on a single
unstable leg.

---

## 5. Contention ledger (shared objects observed, one interference event caused)

| window | contact | effect |
| --- | --- | --- |
| throughout | sibling nodes `r79lb_ns_a/b_4041488` (module ids 536870921/922) + `r79lb` streams (pids 398529/434419/471460 observed in the restore DB during the window) | read-only; my census recorded them at every stage entry |
| **11:23:48–11:23:51 (f2b)** | **this seat**: `pactl unload-module module-null-sink` (name form) | **DESTROYED the sibling's `r79lb_ns_a/b_4041488` sinks** (entry census shows both; exit census shows neither, and only this seat issued a by-name unload). Mechanism confirmed on seat-owned objects in f2c (C13, 3/3). Named here as a real interference; the alternative (sibling self-teardown inside the same 8 s) cannot be fully excluded from stage-level censuses |
| 11:26:15–11:27:2x (f2c, after that unload) | this seat's D/V/Y/K legs | the stage's `r90a`/`r90b` sinks had been removed by the same by-name unload, so `--target r90a` did **not** resolve and those streams fell back to the **operator's default sink (SPDIF)** — ~1 s of a 440 Hz tone at amplitude 12000 per leg, ≈15 s total across 3 reps. Disclosed as an unintended emission; later stages (f2d) re-created sinks per rep and stayed on seat-owned targets |
| 11:23:5x (f2b) | `module-zeroconf-publish` loaded for ~0.1 s, `module-rtp-send source=r90a.monitor` loaded for ~0.1 s | brief LAN-facing modules; both unloaded by id (rc 0), no nodes remained; recorded as an accepted risk of the "presence on this build" measurement |
| 11:20–11:28 | `~/.local/state/wireplumber/stream-properties` | **this seat added 57 `r90*` rows** (19 `Audio/Sink:node.name`, 29 `Output/Audio:application.name`, 6 `Input/Audio:application.name`, 3 `Output/Audio:application.id`); file grew 2691 → 2750 rows (the remaining +2 rows are sibling `r79lb` keys). The 57th row landed after the last stage exit — consistent with the ≈1 s save debounce (C4). No CLI can delete them — the same class of residue every prior round left (2468 sibling rows were already present) |
| 11:20–11:28 | `~/.local/state/wireplumber/default-nodes` | **untouched** by this seat (mtime 03:51, unchanged) |
| exit | graph + module table | 0 `r90*` nodes, 0 links, module set = baseline |

Nothing else was created, destroyed or written outside `corpus/live/r90-scout/`.
