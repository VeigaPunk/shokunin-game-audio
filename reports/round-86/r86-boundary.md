# R86 boundary — falsification of the r86 scout under host-state variation and load

**Seat: BOUNDARY (executor-class, leaf).** Host `plazir27`, lane
`~/Projects/shokunin/audio-shokunin` @ HEAD **`1abd954`** (the scout measured
`a2616f7`). Window **2026-10-15 17:05–17:15 UTC−3** (20:05–20:15Z).
Toolchain re-verified on this boot: pw-cli/pw-dump/pw-metadata/pw-top all
**PipeWire 1.6.8**, `pactl 17.0-98-gb096`, Python **3.14.7**; `/usr/bin/pw-jack`
is the POSIX script with its `LD_LIBRARY_PATH` lines **commented out**;
`/usr/lib/libjack.so.0.3.1608` `ldd`s onto `libpipewire-0.3.so.0`;
**no `jack_*` tool exists** (`jackd jack_lsp jack_connect jack_alias
jack_control jack_server_control` all MISSING).

**The host rebooted between the scout and this seat** (`uptime` 3:27 at 17:05;
the scout measured 03:40–04:05 local). Every absolute id/serial in the scout's
tables is therefore boot-relative and stale: their 9 metadata stores were
`31,37,38,39,40,41,42,43,44`, today they are `31,34,35,36,37,38,39,41,42`;
their self-serials `40399/40400` are now `~116 5xx–116 8xx`. Only the *laws*
were testable, not the pins.

**Zero tracked-file edits, no commits, no `set-default-*`, no engine writes.**
Every write is under `corpus/live/r86-boundary/` (harness `r86b_probe.py`,
`receipts/*.json|*.txt`, `keep/**`) plus this report. Every audio object this
seat created is named **`r86b_*`**; every module unload was index-verified
against its own `sink_name=` line immediately before the call
(`receipts/clean.json` `unloads[*].verified_line`), nothing was unloaded by
name, and **no process was ever killed by pattern** — only PIDs this seat
started. Exit state (17:13): `pactl list short modules | grep -cF r86b` → 0,
`pw-dump | grep -cF r86b_` → 0, `pw-metadata -n default | grep -cF r86b_` → 0,
defaults unchanged (`…HiFi__SPDIF__sink` / `…HiFi__Line__source`).

**Labrat.** The single permitted `probeParent` labrat was dispatched once
(H1: *is the pw-top crash class signal-path-wide rather than TUI-specific?*).
Its substrate exposed **no shell/exec tooling**; it returned **UNTESTED** with
zero evidence and zero side effects. This seat measured H1 directly and
**falsified** it (§7).

---

## 0. Verdict table

| # | r86 scout claim | verdict | sharpest measured fact |
| --- | --- | --- | --- |
| 1 | `pw-cli ls <N>` = `object.serial`, `info <N>` = `object.id` | **CONFIRMED (decisive)** | on seat node id **181** / serial **116556**: `ls 116556` → the node (7 lines, `object.serial = "116556"`), `info 116556` → `Error: "info: unknown global '116556'"`, `info 181` → the node, `ls 181` → **empty**. Same number, two families |
| 2 | unknown/lowercase class → empty rc=0, indistinguishable from real empty | **CONFIRMED** | `ls Bogus` ≡ `ls node` ≡ `ls PORT` ≡ `ls node_` ≡ `ls Session` → 0 lines, rc=0; `SecurityContext` is *listable* (`ls` 2 lines) even though the REPL path errors on it |
| 3 | enum-params typed per object class | **CONFIRMED + Module measured** | Node={Props,PropInfo,EnumFormat}; Port={EnumFormat,Latency,IO,Meta}; Device={Profile,EnumProfile,Route,EnumRoute}; **Client/Factory/Link/Module → `not implemented on object`**; everything else ENOENT; numeric `3` ≡ `EnumFormat` byte-for-byte |
| 4 | `Format` absent pre-negotiation, EIO text racy | **CONFIRMED + widened** | pre-negotiation refusal text ∈ **{silent 11/12, bind-race pair 1/12}**, and `res:-5 EIO` in two other runs of the same object/param; **post-negotiation it dumps** (`node_format` 863 B, `port_format` 456 B) and reverts to refusal after stop |
| 5 | rc discipline: every pw-cli/pw-metadata/pw-dump refusal is rc=0 | **CONFIRMED for those three tools** | 20+ refusals, all rc=0 (`ls Bogus`, `info bogus`, `enum-params Bogus`, `set-param` usage/bad global, `pw-dump <bad>` 0 bytes, `pw-metadata -n bogus`) — **but the scout's own `pwlink_eexist … rc=0` row is FALSE: pw-link refusals are rc=255** |
| 6 | `Props.channelVolumes` is live DSP on a linear scale; `pactl %` cubic; `Props.volume` a dead key | **CONFIRMED under load** | own 12000-peak tone: `0.25`→**3000**, `0.5`→**6000**, `mute:true`→**0**, `volume:0.25`→**12000 unchanged** (store reads Float 0.250000, pactl 100 %), `pactl … 25%`→**188** (= 12000·0.25³); pactl reads back 63 %/79 % (= ∛) after the channelVolumes writes |
| 7 | port `set-param … Latency` "accepted-rc0, silently dropped" | **FALSIFIED as "silently"** | rc=0 + pod echo `Float 2.000000` **but stderr carries a local refusal** `Error: "set-param not implemented on object 134 type:PipeWire:Interface:Port"` and re-enum still `Float 0.000000` |
| 8 | `set-param EnumFormat` "accepted, no effect" | **refined** | pod echo + rc=0, but the remote **does** refuse: `remote 0: error id:88 seq:410 res:-95 (Operation not supported): set param id:3 (Spa:Enum:ParamId:EnumFormat) flags:00000000 failed` |
| 9 | `pw-dump` is "BYTE-STABLE MODULO SELF" | **FALSIFIED as a general arm** | 2×5 snaps 0.5 s apart: canonical hash (self rows dropped) takes **3 distinct values in round 0, 4 in round 1**; object counts 126→121→114→114→114 and 113→112→108→113→113; changed rows include foreign node/port `info.params` + `info.state`, links' `change-mask`, and 10 added objects |
| 10 | `pw-dump <bad-id>` → zero bytes, rc=0 | **CONFIRMED + two new traps** | `pw-dump 99999` / `bogus` → 0 B rc=0; **`pw-dump <serial>` also resolves** (116556 → the id-181 object); **`pw-dump -C always` (two tokens) → 0 bytes rc=0** because `WHEN` is eaten as the positional `<id>` |
| 11 | `pw-metadata -l` lists 9 stores | **CONFIRMED, but `pw-dump` sees only 4** | `pw-metadata -l` = 9 names, `pw-cli ls Metadata` = same 9 ids, **`pw-dump` = 4 (31,34,36,39)**, stable 3/3 and across the window; `Metadata` is the only class where the two censuses disagree (3 tight iterations) |
| 12 | pw-metadata store laws (echo, typed values, live-subject persist, dead-subject drop, `-d` semantics) | **CONFIRMED verbatim** | `set property:`/`update:`/`delete property:`/`delete properties:` all reproduced; `99997` echoes then never reads back; `-d <subject>` wipes all keys under it; absent-key read and absent-key delete are silent no-ops |
| 13 | `default.audio.*` is writable AND functional | **NOT ARMED (constraint)** | wave spec forbids touching the shared session defaults; this seat only *read* subject 0: `default.audio.sink` + `default.configured.audio.sink` + `default.configured.audio.source` present, **`default.audio.source` absent** (matches the scout's asymmetry claim, no write issued) |
| 14 | `pw-top -b -n N` headless clean exit | **CONFIRMED + edges** | `-b -n 2` rc=0 66 lines 3/3; **`-n 0` → one table then rc=0**; `-n -1` and no `-n` → unbounded (SIGKILL 137) |
| 15 | pw-top TERM/INT → SIGABRT 134 (`loop.c:189`), KILL clean | **CONFIRMED + NARROWED (H1 falsified)** | TUI+TERM → rc=134 with the assertion 2/2 today; **batch `-b -n 100000` + TERM → rc=0, no assertion, 3/3; batch + INT → rc=0**; TUI+KILL → 137 |
| 16 | pw-jack only exports REMOTE/DEBUG/QUANTUM; commented LD_LIBRARY_PATH | **CONFIRMED + extended** | `-p 512`→`512/48000`, `-s 44100 -p 256`→`256/44100`, **`-s` alone → QUANTUM unset**, `-v`→DEBUG 3, `-vv`→4, preset 4→**5**, `-r`→REMOTE, `-h`→usage rc=0, **no args → silent rc=0**, `-Z`→usage + `illegal option -- Z` rc=0, bogus payload → rc=127 |
| 17 | `pw-cli </dev/null` prints banner then **exits rc=0 on EOF** | **FALSIFIED** | `pw-cli </dev/null` → **SIGABRT rc=134, 5/5**, same `remove_from_poll()` assertion; **pipe stdin never exits** (rc=124 under a 3–6 s bound, streaming registry events); only an explicit `quit` exits rc=0 (3/3) |
| 18 | `pw-link` duplicate → `File exists` **rc=0** | **FALSIFIED** | create rc=0; duplicate **rc=255** `failed to link ports: File exists`; bogus ports rc=255; **usage rc=255** (on stderr) |
| 19 | `pw-link -I`/`-v`/`-m` are list modes | **FALSIFIED (they are modifiers)** | `-I`/`--id` alone → rc=255 `-I option needs one or more of -l, -i or -o`; `-v`/`-m`/`--monitor` alone → rc=255 `missing output and input port names to connect`; `-l -I`, `-l -v`, `-l -t`, `-l -m` all rc=0 (the last streams `+`-prefixed lines, unbounded) |
| 20 | `info <link-id>` is the live-format census arm | **CONFIRMED** | `info 258` → `output-node-id/output-port-id/input-node-id/input-port-id`, `state: "active"`, and the negotiated `Format` pod (`AudioFormat F32P`, `dsp`) |
| 21 | *(not claimed)* stderr is the verdict channel | **NEW HAZARD** | remote error lines can appear **while the dump succeeds** (`enum-params … EnumFormat` dumped 460 B *and* printed `no global 211` / `unknown resource 135`); in a clean 10-rep run the artifact rate was 0/10, so it is a rare bind race, not a verdict |
| 22 | `seq:` numbers "churn per connection" | **refined** | identical commands give identical `seq` (`enum params id:2 …` printed `seq:432` 3/3); the numbers are per-operation-sequence, not random |
| 23 | registry order, not id-sorted, stable | **CONFIRMED for the stable prefix** | first ids `[0,1,3,2,5,4,6,7,8,9,…]` in both rounds; the full id list is not stable under sibling churn (expected) |

---

## 1. Host state, reboot and contention (mandatory disclosure)

- **The scout's window was quiet; this seat had no quiet window at all.** The
  whole 17:05–17:15 window ran under a **foreign `yes` storm** (32 procs from
  17:02:34 + 16 from 17:02:42, growing to 76 by 17:13), cwd
  `/home/vgpnk/Projects/shokunin/game-dev-3d-shokunin`, orphaned to
  `systemd --user` — i.e. a **g3d-lane hog set**, not this seat's. Loadavg per
  stage: b0 **64.4**, b0b **68.8**, b1 **66.3**, b2 **56.4**, b2b **63.4→64.7**,
  b3 **56.4**, b4 **71.2→71.6**, b4b **70.1**, b5 **73.7→77.9**, b6 **78.3→75.8**
  (per-leg 72.9–80.8), b7 **75.4**, b8 **74.7**, clean **77.2→81.3** — on
  **32 cores**. Every "verbatim replay" in this report is therefore also a
  *load* replay; there is no quiet/load contrast available on this host today.
- **Live sibling seats in the same lane** (observed in the graph or process
  table, never touched): `r80md_*` (`measure_audio.py --probe-module-r80`),
  `r89b_*` (`pw-play --target r89b_ns`, `corpus/live/r89-boundary`), `r82ff_*`
  (`r82_probe.py` ffmpeg, links on the SPDIF sink), `r87bmr` (a MIDI-remap leg
  with live links), a `paplay` client, plus g2d/g3d batteries
  (`run_battery.py … /tmp/r93batt_full2`, godot `discover.gd`, blender cores).
  r85-boundary's report landed at 17:02 in the same window.
- **Naming collision (kill hazard).** A g3d sibling's Godot run uses paths
  under `…/app_userdata/MechanicOneShotTest-…/r86bt/…` — a naive
  `pkill -f r86b` would have killed that sibling leg. This seat never killed by
  pattern; the `pgrep -f r86b` count of 8 in `clean.json` is **those foreign
  processes plus my own `bash -lc` wrapper self-matches**, not leftovers.
- **Cores**: `coredumpctl` count moved 3470 → 3473 across the two TUI TERM
  aborts (2 attributable to this seat) and 3473 → 3485 across the REPL abort
  reps (5 attributable) — the pw-top/pw-cli abort class is core-generating.
- Deliberate **non-arms** (disclosed, not attempted): `default.audio.*`
  writes (shared host default — the wave spec's `NEVER pactl set-default-*`
  covers this door too), `set-param <device> Profile|Route`, and any
  `pactl unload-module` not index-verified as `r86b_*`.

---

## 2. FRONTIER — addressing and census (`receipts/b0.json`, `b0b.json`,
`b0c…b0g`)

- **Split, decisively** (seat node `r86b_ns`, id **181**, serial **116556**):
  `pw-cli ls 116556` → `\tid 181, type PipeWire:Interface:Node/3` +
  `object.serial = "116556"`; `pw-cli info 116556` → `Error: "info: unknown
  global '116556'"`; `pw-cli info 181` → the node (`\tid: 181`, `permissions:
  rwxm-`, `state: "suspended"`); `pw-cli ls 181` → **empty**.
  `pw-cli enum-params 116556 Props` → `unknown global '116556'` (id family).
- **`pw-dump <N>` is not id-only**: `pw-dump 116556` → 6026 B, the id-181
  object (identical to `pw-dump 181`). The scout's "`pw-dump <id>`" is really
  "`<id|serial>`"; no true id↔serial collision exists in this id space
  (`serial_min_max [0,116808]` vs `id_min_max [0,258]`, 0 collisions) so the
  tie-break could not be forced.
- Class census at entry (pw-dump, 83 objects): Core 1, Module 13, Factory 13,
  Device 3, Node 11, Port 26, Client 10, Metadata **4**, Profiler 1,
  SecurityContext 1, Link 0 — vs the scout's quiet 82. `ls <class>` counts at
  the same moment (b0b): Node 19, Port 16, Client 18, Link 7, Metadata 9 —
  i.e. **the graph churned by the second**; only Metadata's 9-vs-4 gap is
  systematic (§5).
- **Metadata is not `info`-able**: `pw-cli info 31` / `info 35` → **zero bytes,
  no error, rc=0**, while the same ids are listed by `ls Metadata` and
  `pw-metadata -l`. A new silent-empty arm (the scout's taxonomy has it for
  `ls <unknown-class>` and bad ids, not for a *live* object).
- Output-shape claim re-confirmed from receipts: `ls` prints
  `id 181, type PipeWire:Interface:Node/3` (space), `info` prints
  `type: PipeWire:Interface:Node/3` (colon).

---

## 3. FRONTIER — enum-params (`receipts/b2.json`, `b2b.json`)

Node 181 (null-sink), its `playback_FL` port 134, Device 44, Client 32,
Factory 7, Module 1, Link 121:

| param | Node | Port | Device | Client/Factory/Link/Module |
| --- | --- | --- | --- | --- |
| Props / PropInfo | dump | ENOENT | ENOENT | `not implemented` |
| EnumFormat / `3` | dump | dump (460 B) | ENOENT | `not implemented` |
| Format | **silent (pre-negotiation)** | **refusal text racy** | ENOENT | `not implemented` |
| Latency | silent | **dump (725 B)** | ENOENT | `not implemented` |
| ProcessLatency | silent | ENOENT | ENOENT | `not implemented` |
| IO / Meta | ENOENT | **dump (528/276 B)** | ENOENT | `not implemented` |
| Profile/EnumProfile/Route/EnumRoute | ENOENT | ENOENT | **dump** | `not implemented` |
| Bogus / 999 / all | local unknown type | local unknown type | local unknown type | local unknown type |

- **Format is a negotiation artifact, measured within one run**: before any
  stream, port 134 `Format` → 11/12 zero output; with a tone playing,
  `port_format` dumps 456 B and `node_format` 863 B (`Format (4)`, mediaType
  audio, mediaSubtype dsp, `AudioFormat F32P`); after the player exits, the
  port is back to a refusal (`res:-5`).
- **The Format refusal text is 3-valued**, not just "racy EIO": 11/12 silent,
  1/12 the bind-race pair `no global 127` + `unknown resource 130`, and
  `res:-5 (Input/output error): enum params id:4 (Spa:Enum:ParamId:Format)
  failed` in the matrix and post-stop runs of the same object. **Arm on pod
  presence/absence only** — the scout's rule stands, its label is too narrow.
- **Error text can coexist with success**: `enum-params 134 EnumFormat` while
  playing dumped 460 B *and* printed `no global 211` / `unknown resource 135
  op:7`. The artifact is rare (0/10 in a dedicated clean 10-rep run) and is a
  bind race on a vanishing global, not a param verdict.
- `pw-cli info 134` (port, while playing) → 678 B with `direction: "input"`,
  `format.dsp = "32 bit float mono audio"`, `audio.channel = "FL"` — the
  port-level witness the scout's format arm implies.

---

## 4. FRONTIER — `set-param` DSP and write refusals (`receipts/b6.json`,
`b7_followups.txt`)

Instrument: own 1 kHz stereo s16 tone, peak **12000**, into `r86b_ns`; monitor
tap `pw-record -P stream.capture.sink=true --target r86b_ns`; write at t≈2.0 s;
0.25 s windows; the tap link was re-validated in every leg (r85's gain hazard
did not appear: every solo window read exactly 12000). All legs ran at
loadavg 72.9–80.8 with 56 `yes` procs live.

| write at t=2.0 | windows before | windows after | law |
| --- | --- | --- | --- |
| *(solo, no write)* ×2 | 12000 | 12000 | reference |
| `{ channelVolumes: [0.25,0.25] }` ×2 | 12000 | **3000** | linear ×0.25 |
| `{ channelVolumes: [0.5,0.5] }` | 12000 | **6000** | linear ×0.5 |
| `{ mute: true }` ×2 | 12000 | **0** | live |
| `{ volume: 0.25 }` ×2 | 12000 | **12000** | **dead key** |
| `pactl set-sink-volume r86b_ns 25%` ×2 | 12000 | **188** | cubic (12000·0.25³=187.5) |

- Store/scale coupling re-confirmed: after `channelVolumes=0.25` pactl reads
  **63 %** (41285), after `0.5` **79 %** (52016) — ∛ of the linear value; after
  the dead-key write pactl is still **100 %** while `enum-params Props` shows
  `volume … Float 0.250000` and `mute … Bool false`.
- Write-refusal lattice (verbatim, all rc=0): `garbage` → `None`;
  `{ }` → empty pod (size 8); `{ zzz.r86b: 7 }` → empty pod and the key is
  absent on re-enum (`grep -c zzz` → 0); `{ volume: "high" }` → pod echo with
  `None` in the volume slot.
- **Two corrections to the scout's "accepted, no effect" rows**:
  - `set-param 134 Latency '{ minQuantum: 2.0 }'` → rc=0, echo `Float
    2.000000`, re-enum still `Float 0.000000`, **and stderr
    `Error: "set-param not implemented on object 134 type:PipeWire:Interface:Port"`**.
    Ports are not "read-mostly" by convention — `set-param` on a Port is
    *not implemented*; the pod echo is a local print, not an acceptance.
  - `set-param 181 EnumFormat '{…}'` → rc=0, echo, no effect, **and stderr
    `res:-95 (Operation not supported): set param id:3 (Spa:Enum:ParamId:EnumFormat)
    flags:00000000 failed`**.
- An accidental arm worth keeping: `set-param 0 Latency` → rc=0 with
  `Error: "set-param not implemented on object 0 type:PipeWire:Interface:Core"`
  (Core joins the not-implemented class).

---

## 5. FRONTIER — `pw-dump` (`receipts/b1.json`, `b0d_modes_meta.txt`,
`b0c/b0e/b0f/b0g`)

### 5.1 FALSIFICATION 9 — "byte-stable modulo self" does not survive a live host

Two rounds of 5 snaps, 0.5 s apart, canonicalised by dropping every object
whose `info.props["application.name"] == "pw-dump"` and hashing the rest:

| round | hashes (5 snaps) | distinct | object counts |
| --- | --- | --- | --- |
| 0 | `f9077416`, `4975fb2b`, `61596dc3`, `5b00eb2f`, `5b00eb2f` | **3** | 126, 121, 114, 114, 114 |
| 1 | `023d5150`, `434f6229`, `3b68638a`, `f6c346a6`, `f6c346a6` | **4** | 113, 112, 108, 113, 113 |

Back-to-back triples show the same: `pair_diff 0` has 0 added/removed but
changes on the foreign ALSA node 61 (`.info.params.Format: len 1->0`,
`.info.props.api.alsa.*` added) and on the dump's own Client 127
(`application.process.id`, `core.name`, `object.serial`, `pipewire.sec.pid`);
`pair_diff 1` adds **10 objects** (52, 56, 103, 112, 142, 185, 232, 236, 249,
258) and flips node/port `info.params` and link `change-mask`. The scout's
5/5 quiet-graph result is not contradicted on its own terms — but **the
canonical arm they propose is unsafe on any host with live siblings**: the
self-row is not the only volatile row. The self-Client law itself is confirmed
(each invocation adds one Client with a fresh serial: 126/142/103/…).

### 5.2 Mode lattice (untruncated byte counts, rc=0 everywhere)

| invocation | bytes | notes |
| --- | --- | --- |
| *(bare)* | 420 288 | no ANSI escapes when piped |
| `-N`, `-Cnever`, `--color=never` | 420 288 | identical to bare |
| `-R` | 255 457 | raw |
| `-i 0` | 270 130 | indentation removed |
| `-s` | 388 238 | SPA syntax (`id = 0`, `type = "…"`) |
| `-s 181` | 10 663 | SPA, single object |
| **`-C always` / `-C never`** | **0** | **silent-empty trap**: `WHEN` is consumed as the positional `<id>` |
| `-C=never` | **0** | same trap in `=` form |
| `-m` (1.5 s) | 64 925 / 1 912 lines | unbounded stream, must be killed |

`-C always` under a PTY (`script -qec`) also produced 0 escapes/0 bytes, and
`pw-cli ls Node` under a PTY was line-identical to the piped form (257 lines,
0 escapes) — one-shot paths are tty-independent; only the REPL path is not
(§7).

### 5.3 `pw-dump` is not a metadata census oracle (NEW)

Same second, three surfaces: `pw-metadata -l` → 9 stores
(`settings 31, schema-sm-settings 34, persistent-sm-settings 35, sm-settings
36, sm-objects 37, default-profile 38, default 39, filters 41,
route-settings 42`); `pw-cli ls Metadata` → the same 9 ids; **`pw-dump` → only
`[31, 34, 36, 39]`**, stable 3/3 and over ~10 minutes of the window. A tight
3-iteration class census shows `Metadata` (9,4) as the **only** disagreeing
class (Client/Link deltas appeared once and were churn). `pw-dump 35/37/38/41/42`
→ 0 bytes each; `pw-dump 31/34/36/39` → 844/6823/3031/877 B. The five hidden
stores are owned by WirePlumber's client 33 like the visible ones
(`ls Metadata` props), and `get-permissions 33` shows `default: rwxm-`, so the
filter is not visible from the client side. **Mechanism unread; the law is
measurable and stable.**

---

## 6. FRONTIER — `pw-metadata` (`receipts/b3.json`, `b7_followups.txt`)

- Inventory, existence check, bare ≡ `-n default` (byte-identical, 4 lines),
  `-n bogus_store_r86b` → no `Found` line, 0 bytes, rc=0 — all confirmed.
- Live-subject cycle on **181** (≥3 cycles, all rc=0): `set property:` echo →
  `update:` read → overwrite (full replace) → `Spa:String` type persists
  verbatim (`type:'Spa:String'`) → absent-key read prints **no update row** →
  `delete property:` → key gone → deleting an absent key is the same echo and
  a no-op → **`-d <subject>` (bare) prints `delete properties: id:181` and
  wipes every key under that subject** (verified by a read-all before/after).
- Dead subject **99997**: write echoes, read prints only the `Found` line —
  the scout's "echo is a local print" law confirmed 2/2.
- **New: the `-m` subject argument filters.** With `r86b_mtest` written under
  181: `pw-metadata -m 181` printed exactly `Found "default" metadata 39` +
  the 181 row; `pw-metadata -m 0` printed only the subject-0 rows
  (`default.configured.audio.sink`, `…source`). Bounded with SIGKILL.
- Baseline subject 0 read (no writes): `default.audio.sink` +
  `default.configured.audio.sink` + `default.configured.audio.source`;
  `default.audio.source` **absent** — the scout's asymmetry holds at rest
  today too. The `.monitor`-name and `-d`-does-not-reset-default arms were
  **not run** (they require writing the shared default; §1).
- Other stores read clean: `settings` (9 rows), `filters`/`sm-objects`/
  `route-settings` exist with 0 rows.

---

## 7. FRONTIER — `pw-top` signals and the `pw-cli` REPL crash class
(`receipts/b5.json`, `b8_repl_link.txt`)

| arm | rc | evidence |
| --- | --- | --- |
| `pw-top -b -n 2` ×3 | 0 | 66 lines, plain table `S ID QUANT RATE WAIT BUSY W/Q B/Q ERR FORMAT NAME` |
| `pw-top -b -n 0` | 0 | one table (28 lines) then exit |
| `pw-top -b -n -1`, `pw-top -b` (no `-n`) | 137 (SIGKILL bound) | unbounded |
| TUI piped + TERM ×2 | **134** | `'source->loop == &impl->loop' failed at ../pipewire/spa/plugins/support/loop.c:189 remove_from_poll()` + core |
| TUI piped + KILL | 137 | silent |
| **`-b -n 100000` + TERM ×3** | **0** | no assertion, 230/230/317 lines printed |
| **`-b -n 100000` + INT** | **0** | no assertion |

So the scout's crash class reproduces on this boot for the TUI path (2/2) and
**H1 — "the crash class is signal-path-wide" — is falsified**: batch mode
handles TERM/INT gracefully. The arm consequence is the scout's, sharpened:
*the abort is a property of the interactive/curses path, not of pw-top as
such.*

**New crash surface with the same assertion: `pw-cli </dev/null` → rc=134,
5/5**, printing only the banner + `>> >> ` before aborting. The scout's
`pw-cli </dev/null` "exits rc=0 on EOF" is therefore falsified as a general
claim (either their rc was read through a pipe, or the EOF path is
nondeterministic). Related REPL modes, all measured:

- `printf '' | pw-cli` and `echo ls | pw-cli` → **never exit** (rc=124 under a
  3–6 s bound): on a pipe the REPL streams the registry
  (`remote 0 added global: …`, `remote 0 port 113 changed`) — 68 KB in 6 s.
- `printf 'quit\n' | pw-cli` → **rc=0** (3/3) — the only clean exit.
- One-shot commands are unaffected: `pw-cli ls Node` piped vs PTY both 257
  lines, 0 ANSI escapes; the REPL banner/`>>` appears only on the interactive
  path.

---

## 8. FRONTIER — `pw-jack`, `pw-cli`, `pw-link` modes
(`receipts/b4.json`, `b4b.json`, `b4c/b4d/b4e`, `b7_followups.txt`)

- **pw-jack** (script re-read verbatim): `-p 512` → `512/48000`;
  `-s 44100 -p 256` → `256/44100`; **`-s 44100` alone → QUANTUM unset**
  (period-gated); `-v` → `PIPEWIRE_DEBUG=3`, `-v -v` → 4, preset 4 → **5**;
  `-r X` → `PIPEWIRE_REMOTE=X`; `-h` → usage rc=0; **no args → silent rc=0**;
  `-Z` → usage on stdout + `illegal option -- Z` on stderr, rc=0; bogus
  payload → `exec: …: not found`, **rc=127**.
- **pw-cli read-only modes**: `list-vars` (2 lines), `list-remotes`
  (`0 = @remote:… 'pipewire-0'`), `get-permissions <client>` → e.g.
  `remote 0 node 32 index 0 / default: rwxml` for a normal client vs
  `rwxm-` for WirePlumber's client 33 (**per-client permissions differ**);
  `info all` = 119 322 B with `info: unsupported type
  PipeWire:Interface:SecurityContext` / `…:Profiler` on stderr; `help`/`h`
  = 22 lines.
- **pw-link rc discipline (the scout's row is wrong)**: create rc=0; duplicate
  **rc=255** `failed to link ports: File exists` (reproduced after a fresh
  create, so not a stale-link artifact); bogus port rc=255 `No such file or
  directory`; usage rc=255 (stderr); `-d <link-id>` **rc=0** (link gone) while
  `-d <port-id>` rc=255 `failed to unlink ports: No such file or directory`.
- **pw-link modes**: `-l`/`-o`/`-i` rc=0; **`-I`, `-v`, `-m` are modifiers**
  (`-I` alone → rc=255 `-I option needs one or more of -l, -i or -o`; `-v`
  and `-m` alone → rc=255 `missing output and input port names to connect`);
  `-l -I` (port + link ids), `-l -v` (verbose props), `-l -t` (latency
  blocks), `-l -m` (`+`-prefixed live stream, unbounded) all rc=0.
- `-P`, `-w`, `-p '{ "link.passive": true }'`, `-p '{ "zzz_r86b": 1 }'`,
  `-L`, and even `-p garbage` → **all rc=0 and all create the link**: pw-link
  accepts a garbage props argument silently (a new silent-accept class
  alongside `pw-cli set-param … garbage` → `None`).
- `pw-cli info <link-id>` while playing → `output-node-id: 244`,
  `input-node-id: 234`, `state: "active"`, negotiated `Format` pod
  (`mediaSubtype dsp`, `AudioFormat F32P`), `object.linger = "true"` — the
  scout's live-format census arm confirmed.

---

## 9. Harness bugs, instabilities, disclosure

1. **Truncation artifact**: b1's mode table stored `out` through a 6 000-char
   cap, so `-N/-R/-i0/-s` all read "6028 B". Re-measured untruncated
   (`b0d_modes_meta.txt`); the capped numbers are superseded and no verdict
   rests on them.
2. **Port lookup bug**: b2's `pid_` was `None` (ports carry `node.id`, not
   `node.name`), so all b2 port rows and its 12-rep Format test were vacuous
   (`unknown global 'None'`). Fixed in **b2b**; the vacuous rows are disclosed
   and not cited.
3. **b6's `port_latency` row** also hit the bad lookup and measured
   `set-param 0 …` (Core) instead of port 134. Re-measured correctly in
   `b7_followups.txt` (§4); the b6 row is kept only as the Core
   not-implemented witness.
4. **rc masked by a pipe**: my first pw-link shell lattice piped through
   `head`, so `rc=$?` was `head`'s. Redone with direct capture
   (`b4d/b4e`); the piped numbers are not cited.
5. **A leaked credential line** (an agent token in a foreign process's
   `environ`) was captured by a recon command and **scrubbed from
   `contention0.txt`** before any other read; the file now carries a
   `[redacted-line-removed-by-seat]` marker. No secret is stored in the lane.
6. **Raw capture wavs trimmed** after analysis (r85 convention): the b6
   evidence kept is the per-window peak arrays, tap-link strings and byte
   counts inside `receipts/b6.json` (`runs/` is now empty; `keep/` holds the
   census dumps and the tone).
7. **Instability named**: the Format refusal text (silent / bind-race pair /
   `res:-5`) is not stable across identical commands, and the bind-race pair
   can co-occur with a successful dump. Any arm reading stderr as a verdict
   will flake here.

---

## 10. Remaining unknowns (honest edges)

- **Why `pw-dump` omits 5 of 9 metadata stores** (§5.3) is unread; the
  omission is stable and reproducible but the filter (permission? owner?
  lazily-published globals?) was not visible from the client side.
- **Why `pw-cli </dev/null` aborts (134) while a pipe hangs** is unread; both
  are the same `loop.c:189 remove_from_poll()` teardown assertion family as
  pw-top's TUI abort, but the EOF-path trigger was not read.
- **The `-C always` trap** is measured (`WHEN` consumed as `<id>`), but I did
  not read getopt's optional-argument handling in the binary to confirm the
  mechanism.
- **`pw-dump <id|serial>` tie-break** could not be forced (no id↔serial
  collision exists in this id space after a reboot).
- The scout's **`default.audio.*` authority-split** arms remain untested by
  this seat by design (§1); their `.monitor`-ignored and `-d`-does-not-reset
  claims are therefore neither confirmed nor falsified here.
- Whether the **48→76 `yes` storm** (g3d lane) is a bounded sibling load
  stage or leaked hogs is unknown; it was still running at exit and was **not**
  touched.

---

## 11. Receipts index and exit state

| artifact | bytes | sha256 (prefix) |
| --- | --- | --- |
| `receipts/b0.json` (census, ls classes, sink create, rc sentinels) | 9 153 | `426b4553c12ed989` |
| `receipts/b0b.json` (id/serial split, ls counts, metadata census) | 24 747 | `c1eabbc4f5c3b46b` |
| `receipts/b0c_metadata_census.txt` / `b0e_meta_perms.txt` / `b0f_ls_metadata.txt` / `b0g_census_compare.txt` | 527 / 480 / 1 575 / 446 | `98e6c7adb2fff4f6` / `6137cca9dd55b79e` / `6a80a8a7ca7753dd` / `2ea4269f38ac1e5e` |
| `receipts/b0d_modes_meta.txt` (untruncated pw-dump modes) | 1 167 | `f9ba8e9b9320b802` |
| `receipts/b1.json` (pw-dump determinism ×2 rounds + modes) | 49 344 | `0be05cd90781a06f` |
| `receipts/b2.json` / `b2b.json` (enum matrix node/class; port + Format) | 50 078 / 16 968 | `b06038a6ab5f7c98` / `dda4a269d6d55198` |
| `receipts/b3.json` (pw-metadata laws) | 8 796 | `18e861caf47aac42` |
| `receipts/b4.json` / `b4b.json` (pw-jack, pw-cli modes, pw-top modes; pw-link) | 71 797 / 5 420 | `1322585ae71a3757` / `6dc57315adca4306` |
| `receipts/b4c_pwlink.txt` / `b4d_pwlink_rc.txt` / `b4e_pwlink_rc2.txt` | 4 085 / 1 629 / 1 480 | `62a302473c452645` / `6cfb178b24c4de0c` / `f19c88e9b5cb257c` |
| `receipts/b5.json` (pw-top signals; batch vs TUI) | 21 115 | `658da3fdb51b405e` |
| `receipts/b6.json` (set-param DSP + write lattice) | 21 589 | `4c28e9eb7aeddf3f` |
| `receipts/b7_followups.txt` (port latency, REPL EOF, `-m` filter, artifact rate) | 3 574 | `1839a7215f9ca26c` |
| `receipts/b8_repl_link.txt` (REPL crash ×5, link-format arm) | 2 072 | `9564814ffecca220` |
| `receipts/clean.json` (index-verified unloads + exit census) | 2 589 | `290df915a4dc143f` |
| `receipts/recon.txt` / `help.txt` / `contention0.txt` | 2 211 / 4 056 / 2 598 | `33d3f0ca4605d1b5` / `14cd182b76b8a0f6` / `f70e5a24107ccf69` |

Harness: `r86b_probe.py` (stages `b0 b0b b1 b2 b2b b3 b4 b4b b5 b6 clean`,
plus the shell receipts above). Exit state: **0 `r86b_*` modules, 0 nodes,
0 metadata keys, 0 seat processes, defaults unchanged**; the only
`pgrep -f r86b` hits are the foreign g3d `r86bt` paths and the wrapper
self-match. No tracked file was written; `git status` shows only
`?? corpus/live/r86-boundary/` from this seat (the modified
`corpus/fixtures/*` entries predate this window and belong to a live sibling
seat).

**Verdicts here are seat-side falsification attempts; the canonical Rust
runtime remains the only judge.**
