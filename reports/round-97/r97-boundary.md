# R97 boundary — the WirePlumber policy laws re-armed under load: one sharp falsification (the restart race) and one unsupported failure chain

**Seat: BOUNDARY (executor-class, leaf, falsification).** Host `plazir27`, lane
`~/Projects/shokunin/audio-shokunin` @ HEAD **`51a98e54`**. Window
**2026-10-15 20:50Z–21:47Z** (17:50–18:47 local). Toolchain re-verified on this
host: PipeWire **1.6.8**, WirePlumber **0.5.17** (`libwireplumber 0.5.17`),
`wpexec`/`wpctl` from the same install, Python 3.14.

**Zero tracked writes; nothing committed.** Entry and exit tracked-dirty set is
foreign-owned and byte-identical: `corpus/fixtures/measure_audio.py` (+2264/−3,
mtime 18:22, another seat's author work) and its
`corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`. Every file this seat
wrote is untracked, under `corpus/live/r97-boundary/` (plus this report).

**Namespace.** Every object this seat created is `r97b_*`; every process is
killed by an **own pid file** whose target is checked against the seat identity
in `/proc/<pid>/cmdline` **or** `/proc/<pid>/environ` (see §2.5 — the cmdline
alone is *not* sufficient for `wireplumber`). No namespace-blind sweeps: no
`pkill` pattern is used anywhere in this seat's teardown. Exit census in §6.

**Labrat: not dispatched.** The seat is the frozen `probeParent`; the assigned
attack resolved entirely to on-host measurement, and the one bounded unknown
worth a read-only probe (whether the wedge's trigger is visible in a log the
parent had not opened) was settled by the parent's own forensics stage. Budget
retained.

**Arms.** Each stage ran in an **ambient** arm (no seat-added load; the host
already carried 48–96 foreign `yes` hogs — §6) and a **seat-hog** arm (12 of
this seat's own `r97b_hog` processes, pids recorded in `run/hogs.pid`, killed by
that list only). One-minute load average recorded in-receipt across the window:
**62.5 → 145.9** on 32 cores. A genuinely quiet arm was **not attainable** and was not faked: the
foreign hogs are not this seat's to kill.

---

## 0. Verdict table

| # | r97 scout claim (report §) | verdict | sharpest fact from this seat |
| --- | --- | --- | --- |
| 1 | `WIREPLUMBER_CONFIG_DIR` **replaces** the search path; a dir without `wireplumber.conf` ⇒ **rc 78 (EX_CONFIG)** | **CONFIRMED** (rc) | 3/3 rc **78** in 0.004–0.009 s; V2 (dir *with* a copy) reads only the copy's `alsa-vm.conf`, the shipped `wireplumber.conf.d` is gone (`a_arming`) |
| 1b | …and the failure reads `no modules loaded from context.modules` → `can't find protocol 'PipeWire:Protocol:Native'` → `Failed to connect to PipeWire`, and **never names the missing file** | **FALSIFIED** | the message is `Failed to load configuration: Could not locate configuration file 'wireplumber.conf'` — it *names the file*; 3/3, 293 B; the scout's own `a_arming.json` V1 leg holds **no matching line** (§2.1) |
| 2 | a private WirePlumber needs only a private `XDG_CONFIG_HOME` + runtime dir; the operator's user fragment is only loaded when `XDG_CONFIG_HOME` is not overridden | **CONFIRMED** | V3 opens `alsa-vm.conf` + own `10-r97b.conf`; V4 opens `alsa-vm.conf` + `~/.config/…/bluetooth-a2dp-autoconnect.conf`; 3/3 each |
| 3 | a private core must keep `libpipewire-module-access`; with `module.access = false` clients hang with no error | **CONFIRMED** | B1: socket present, `pw-cli ls Client` **and** `pw-dump` both killed at the 8 s cap, 0 B; B2/B3 answer in 0.007–0.017 s; 3/3, loadavg 82.8 |
| 4a | default = first sink; strictly higher `priority.session` takes over; lower does not; a tie keeps the incumbent | **CONFIRMED** | `c1`/`c2`/`c3`/`c8a`/`c8b` 3/3, both creation orders |
| 4b | …and an explicit `wpctl set-default` outranks every later priority **and survives a WirePlumber restart** | **CONFIRMED** (outranks) / **FALSIFIED as unconditional** (restart) | `c5` 3/3 explicit wins; but the restart clause is a **race**: restart ≤0.57 s after `set-default` ⇒ configured default **lost** (3/3), restart after the state file flushes (≈1.0 s) ⇒ survives (3/3) (§2.2) |
| 4c | `priority.driver` is the **fallback** rank when `priority.session` is absent | **CONFIRMED, sharpened** | a driver-only `999` node takes the default from a `session=100` incumbent (3/3) **and keeps it against a `session=200` newcomer** (3/3) — the fallback rank is compared across nodes, so it is not a tie-breaker |
| 5 | `wpctl set-default` writes both `default.audio.sink` and `default.configured.audio.sink`, and the state hook writes `$XDG_STATE_HOME/wireplumber/default-nodes` | **CONFIRMED** | both metadata rows present 3/3; state file body `[default-nodes]\ndefault.configured.audio.sink=r97b_c0\n`; the file lags the metadata by **0.97–1.01 s** (fine 50 ms poll, 3/3) |
| 6 | a numeric `pw-cat --target` is an `object.serial`; a **global id silently falls back to the default sink**, as does a bogus target | **CONFIRMED** | `d3` id → default `r97b_sb*`; `d4` serial → `r97b_sa*`; `d6` 99999 → default, rc 0, empty stderr; 3/3 |
| 7 | `node.dont-fallback = true` + unresolvable target ⇒ no link, client error `-2 "defined target not found"`, **and WirePlumber destroys the stream node** | **CONFIRMED** | `d7` 3/3: `links=[]`, stderr `…res:-2 (No such file or directory): defined target not found`, and the stream node is **absent** from the dump (`props: null`) |
| 8 | `wpexec`'s Lua environment is a curated sandbox with no `_G`, no `io`/`load`/`dofile`/`require_api`/`rawget`/`unpack`, `debug` present, Lua 5.5 | **CONFIRMED byte-for-byte** | FOUND/MISSING/ENV lines are **byte-identical** to the scout's receipt (39 present / 26 absent, same order) |
| 9 | every runtime error ⇒ rc 70 with the bare `Lua runtime error`; compile errors carry a location | **CONFIRMED** | 4 runtime shapes (`error()`, nested `error(...,2)`, nil index, `pairs(_G)`) all rc 70 + `Lua runtime error`; syntax rc 70 + `Failed to compile: [string "e_syntax.lua"]:1: …`; 3/3 |
| 10 | `Settings.get_*` inside `wpexec` returns false/0.0/"" for every key and does not track the live value | **CONFIRMED** | 6 keys, before and after a verified `wpctl settings … false`, byte-identical; 3/3 |
| 11 | the live settings lattice is 25 keys, published twice (`schema-sm-settings`, `sm-settings`) | **CONFIRMED, extended** | 25 keys, rc 0, **sha256 `56526540…` identical** to the scout's `settings_list.txt` *and* to the operator's shared instance read read-only (§3.6) |
| 12 | `linking.follow-default-target = false` did not stop a stream from following a new default (`[?]`) | **CONFIRMED inert, extended** | `d12` 3/3 moved; **`linking.allow-moving-streams=false` is inert in the same shape too** (`d11` 3/3 moved) — two candidate gates, both inert |

**Row-level additions** (cells the scout's row list did not arm): `node.target`
vs `target.object` prop forms (§4.1), the `node.linger` branch (§4.2), the
`--target` flag-order matrix (§4.3), the `wpexec` JSON-argument form (§4.4), the
clock/quantum axis (§4.5), sibling-pair isolation (§4.6), and a 400-dump
connection storm as a wedge trigger test (§5).

---

## 1. Design, arms and axes

- **Replay**: every armed cell of the scout that has a byte-stable observable was
  re-armed with **fresh processes** (a new `pw-cat`/`wpexec`/`pw-cli`/`wireplumber`
  per leg; the private pair re-armed per stage), in the private instance shape of
  the scout §2.2, with this seat's own conf, runtime dir and state dir.
- **Load arm**: 12 concurrent `r97b_hog` (`yes`) processes of this seat, plus the
  ambient 48–96 foreign hogs. Load average is recorded **in every receipt**
  (`loadavg_start`, `loadavg_end`, per-step `loadavg`).
- **Independent axes varied**: (a) PipeWire clock/quantum — a non-default core
  (`rate=44100`, `quantum=64`, `allowed-rates=[44100 48000]`) replays the
  load-bearing cells (§4.5); (b) CLI flag order — four `--target` placements plus
  the equals form (§4.3); (c) default-node state — configured default present /
  absent / stale-in-file (§2.2, §3.3); (d) sibling seat presence — real foreign
  seats censused read-only (§6) plus a *second private pair of this seat* armed
  simultaneously (§4.6).
- **Bounded everywhere**: every external process has a wall cap and is killed by
  process group; every node is `r97b_*`; the private pair is reached only through
  this seat's runtime dir.

---

## 2. Falsified and corrected claims

### 2.1 The scout's V1 failure chain is not the one this shape produces

The scout's claim 1 (and its §7 falsification row) attaches a three-message chain
to `WIREPLUMBER_CONFIG_DIR=<dir without wireplumber.conf>`:

> `no modules loaded from context.modules` → `can't find protocol
> 'PipeWire:Protocol:Native'` → `Failed to connect to PipeWire`

Three independent facts from this seat:

1. **The chain is in no scout receipt.** `grep -rn` over the scout's whole
   `runs/` tree finds **zero** occurrences of `no modules loaded` and **zero** of
   `can't find protocol`. The scout's own `receipts/a_arming.json` V1 leg has
   `raw_len = 293` and an **empty** matching-line list (`lines: []`) — the text in
   the report is not supported by the receipt it cites.
2. **The real V1 message names the missing file.** 3/3 reps, rc **78** in
   0.004–0.009 s, 293 B, exactly:
   `Failed to load configuration: Could not locate configuration file 'wireplumber.conf'`.
   A 6th variant (`WIREPLUMBER_CONFIG_DIR` holding an *empty* `wireplumber.conf`,
   V6) adds `Ignoring empty configuration file at '<path>'` and still ends with
   the same naming message — so the "no modules loaded" branch is not reached by
   any conf-dir shape.
3. **The chain belongs to a different shape, and it exits 69, not 78.** `strings`
   puts `no modules loaded from context.modules` and `can't find protocol '%s'`
   in **`libpipewire-0.3.so.0`**, and `Failed to connect to PipeWire` in
   `/usr/bin/wireplumber`. Arming a **PipeWire core whose config has no
   `context.modules`** (own runtime dir `run2/`) gives exactly
   `no modules loaded from context.modules` (a **warning**; the core keeps
   running — L1, 3/3), and putting a real `wireplumber -c wireplumber.conf -p main`
   on that core gives `Failed to connect to PipeWire` and **rc 69 (EX_UNAVAILABLE)**
   (L2, 3/3). The middle message did not appear in either leg.

So: the scout's *observable* (rc 78, replacement semantics) is right, its
*mechanism text* is wrong, and the text it printed belongs to a core-side shape
with a different exit status. A row that asserts the chain would fail; a row that
asserts rc 78 and the naming message will pass.

### 2.2 The "configured default survives a WirePlumber restart" law is a race

The scout asserts both (claim 5) that `set-default` writes the state file and
(claim 4) that the configured default survives a restart, and separately notes in
§3.2 that "the file lags the metadata by up to ~1 s". Those cannot both be
unconditional. Armed directly (`c3_restart_race`, fresh pair, fresh `pw-cli`, 3
reps × 3 timings):

| restart timing after `wpctl set-default <low-priority P>` | state file at restart | default after the private WP restart | reps |
| --- | --- | --- | --- |
| **immediate** (0.042–0.058 s) | `''` (empty) | **`r97b_rrq*`** — the high-priority sink, configured choice **lost** | 3/3 |
| **0.5 s** (0.533–0.568 s) | `''` (still empty) | **`r97b_rrq*`** — **lost** | 3/3 |
| **after the row appears** (0.965–1.011 s) | `[default-nodes]\ndefault.configured.audio.sink=r97b_rrp*` | **`r97b_rrp*`** — configured choice **survives** | 3/3 |

The lag is a hard, repeatable **≈1.00 s** (fine 50 ms polling: 0.965, 0.967,
1.011), and after a restart inside the window the `default.configured.audio.sink`
row is **absent** from the metadata entirely (not merely outranked). Consequence
for other lanes: a `set-default` followed by a daemon restart, a crash, or a
session teardown inside ~1 s is **not** durable — which is exactly the window a
seat that sets a default and then restarts its instance occupies.

This also explains the first r97b pass, which failed to reproduce the scout's
restart cell for this reason (the state file was read and the restart performed
inside the lag).

### 2.3 `priority.driver` is a comparable rank, not only a tie-breaker

The scout's law "`priority.session`, else `priority.driver`, else 0" is confirmed
and sharpened by two cells the scout's row list does not contain (`c4_priority`,
3/3):

- incumbent `session=100` vs challenger **`driver=999` only** ⇒ challenger takes
  the default (`n2`, 3/3);
- then a newcomer `session=200` appears ⇒ **the driver-only node keeps it**
  (`n3`, 3/3). Rank 999 (from `driver`) beats rank 200 (from `session`).

A reading of the scout's claim as "`priority.session` always wins when present"
is wrong: the fallback rank participates in the same comparison. Cell `n1` (a
node with **no** priority keys at all) does not displace a 100 — 3/3.

### 2.4 Harness defect (inherited): `wpctl status` is not a WirePlumber readiness gate

With the private WirePlumber **stopped** (own pid killed, guarded), `wpctl status`
still exits **0** and prints a well-formed but empty listing
(`e13c`, 3/3; `Audio ├─ Sinks: │` … `Settings └─ Default Configured Devices:`).
`wpctl` talks to the **core**, not to WirePlumber. The scout's `up.sh` (and this
seat's, which copied it) gates "wp up" on exactly that exit status, so a
"WirePlumber is up" claim from that gate is unfalsifiable-by-rc.

This seat added and used a real gate: WirePlumber's `sm-objects` component is what
publishes the **`sm-settings` metadata object**, so `wp-dump | grep sm-settings`
is the readiness test (`r97blib.wp_ready`). It is also the reason the first
`f_settings` pass returned rc 3 and a 35 B listing: the stage ran while WP was
down and only the core's own `settings` metadata (8 rows) existed. After gating
on `sm-settings`, the same stage returns 25 keys (3/3).

**A related chain-order trap, measured:** stage E's `e13` legs stop WirePlumber
*on purpose*, and the stage's own `ensure_up` only probed the **core** — so the
stage that ran next in the hogs chain (`f_settings`) started with WP down,
returned rc 3 / 0 keys and looked like a policy failure. `ensure_up` now requires
the `sm-settings` object unless the caller explicitly asks for core-only. The
same trap is why the scout's `up.sh` can report "wp up" for a daemon that is not
there.

### 2.5 Harness defect (own): the namespace guard must read `/proc/<pid>/environ`

A seat `wireplumber -c wireplumber.conf -p main` carries **no seat path in its
cmdline** — its seat identity lives in the environment. A cmdline-only guard
therefore *refuses to kill this seat's own WirePlumber* (`wf2`, first pass:
`REFUSED (foreign cmd=wireplumber …)`), which is how a wedged core's daemon
survived its own teardown, and how the first sibling-isolation test produced a
vacuous result (the "sibling" `pw-cli` inherited the **main** pair's env, so the
sibling sink was created in the main graph and `main_sees_sibling_sink` read
`true`). Both are fixed: `probes/down.sh` and the Python guards now accept a pid
whose **cmdline or environ** names the seat, and `PwCli` takes an explicit env.
The corrected sibling run (§4.6) shows clean isolation.

---

## 3. Confirmed laws (receipt index)

All cells below are 3/3 unless stated; receipts are pinned in
`corpus/live/r97-boundary/manifest.sha256` and summarised in
`receipts/*.json`.

### 3.1 Arming (`a_arming.json`, `a2_core_no_modules.json`)
V1 rc 78 + naming message; V2 replacement (only the copy's fragment); V3 shipped
+ own fragment; V4 operator fragment appears; V5 rc 78
`failed to load component 'metadata.sm-objects …': Could not locate script
'sm-objects.lua'` **after** both fragments are opened; V6 empty-conf variant.
The core-without-modules shape (L1/L2) is the home of the scout's text.

### 3.2 Core access (`b_access.json`)
B1 `module.access=false`: socket present, every client leg killed at the cap
(`pw-cli` 8.011/8.009/8.012 s, `pw-dump` 0 B), no error line. B2/B3: 0.007–0.017 s.
Also reproduced under the seat-hog arm (see §5 table).

### 3.3 Default-node policy (`c_defaults.json`, `c4_priority.json`, `c3_restart_race.json`)
First-sink-wins, strictly-higher takeover, lower-does-not, explicit-beats-later-
priority, `clear-default` → best, removing the default → best remaining, tie
keeps incumbent (both orders), no-priority node does not displace, driver-only
999 takes over, driver-999 keeps against session-200, configured-vs-priority
ranking. Timing: the default was already correct at the **first** poll after the
sink appeared in every cell (`polls=1`), i.e. within one `pw-dump` round trip
(0.015–0.065 s at loadavg 90–104) — the scout's "within ≤0.1 s" is confirmed at
that resolution, not below it.

### 3.4 Linking (`d_linking.json`)
`--target 0` → 0 links; auto → default; global id → default (silent); serial →
requested; `node.name` → requested; `99999` → default, rc 0, empty stderr;
`dont-fallback` → 0 links + `-2 defined target not found` + node destroyed;
`media.role=Communication` → default (no role target for a plain stream).
New: `linger` branch (§4.2), flag orders (§4.3), prop forms (§4.1).

### 3.5 `wpexec` (`e_wpexec.json`)
Inventory byte-identical to the scout (39/26, same order); `_G` nil, `_ENV`
table, Lua 5.5, `debug.getregistry` present; four runtime-error shapes rc 70 +
`Lua runtime error`; syntax rc 70 + location; no `Core.quit()` → killed at the
6 s cap (`rc -9`) with its `print` flushed; no argument → rc 70
`Could not locate script '(null)'`; missing file → rc 70 with the path;
`Settings.get_*` inert before/after a verified `wpctl settings` write; and the
**same inventory + inert Settings with WirePlumber down** (e13) — the sandbox and
the settings binding failure are both independent of a policy daemon.

### 3.6 Settings lattice (`f_settings.json`)
`wpctl settings` → 25 keys, rc 0, 4745 B, **sha256 `56526540bdc17f52…`**, 3/3
byte-identical, and **byte-identical to the operator's shared instance** read
read-only (same 25 keys, same order, same hash) — so the lattice is
install-scoped, not instance-scoped. Metadata faces in the private graph:
`settings` (8 rows, the core's own), `schema-sm-settings` (25), `sm-settings`
(25), `default` (1).

---

## 4. Extensions — cells the scout did not arm

### 4.1 `target.object` vs `node.target` (behavioural proof of the mechanism claim)
The scout inferred from `linking/find-defined-target.lua:45-51` that
`target.object` is resolved as an **`object.serial`** and `node.target` as a
**node id**. Armed as props (private pair, two sinks A(id 48/serial 6412) and
B(500, default)), 3/3:

| prop written | linked to | reading |
| --- | --- | --- |
| `target.object = <A serial>` | **A** | serial resolves |
| `target.object = <A global id>` | **default B** | id misses silently — same law as the CLI form |
| `node.target = <A global id>` | **A** | `node.target` is a **node id** |
| `node.target = <A serial>` | **default B** | serial misses silently |

This is the two-sided falsification of "a numeric target is a numeric target":
the *same number* means different things in the two properties, and each property
silently falls back when given the other's namespace.

### 4.2 The `node.linger` branch (scout `[?]`7)
Bogus target + `dont-fallback` + `linger` (3/3): **0 links, empty stderr, rc
`null` (process still alive at the 8 s cap), and the stream node is still in the
graph** with `node.dont-fallback=true`, `node.linger=true`. So the failure
envelope has three client-visible faces, as the scout suspected: silent fallback
(rc 0), destruction (`-2` + node gone), and **silent wait (node stays)**. The
WP-side info line the scout quotes (`waiting for defined target as dont-fallback
is set`) was **not** re-verified — this seat's private WirePlumber runs at
`WIREPLUMBER_DEBUG=2`, which suppresses info lines (the private `wp.log` is 0 B).

### 4.3 `--target` flag order and form (assigned axis)
Four placements + the equals form, each with the same serial target, 3/3 all
linked to **A**: `--target` before the mode flags, `--target=<serial>`, `--target`
**after** the input argument, and `--target` between `-P` and `-`. Flag order is
not a variable for this law; the *namespace of the number* is.

### 4.4 `wpexec` argument form (scout `[?]`2's surface, unarmed)
- `wpexec <script> extra1` → rc **64** (EX_USAGE), stderr `script argument must be
  a JSON object` (3/3).
- `wpexec <script> '{"x":1}'` → rc 0; inside the script `type(arg)` is `nil` and
  `select("#", ...)` is `1`, i.e. **the JSON argument is not exposed to the
  script** through `arg` or varargs in this shape (3/3).
- `wpexec --help` → rc 0.

### 4.5 The clock/quantum axis (assigned axis)
A second core configuration — `default.clock.rate=44100`,
`allowed-rates=[44100 48000]`, `quantum=64`, `min-quantum=32` — was re-armed and
the load-bearing cells replayed (`h_clock.json`, loadavg 128.0 → 112.2). The live
core read back `rate=44100 quantum=64 min-quantum=32 allowed-rates=[ 44100 48000 ]`
in all 3 reps (the fragment was removed again at the end). Results, 3/3:

| cell | result at 44100/64 |
| --- | --- |
| h1 first sink becomes default | ✓ (`r97b_ha*`, first poll, 0.011–0.020 s) |
| h2 strictly higher `priority.session` takes over | ✓ (`r97b_hb*`) |
| h3 explicit `set-default` survives a higher-priority newcomer (session 900) | ✓ (default stays `r97b_ha*`) |
| h4 `--target <object.serial>` | links the requested sink ✓ |
| h5 `--target <global id>` | **vacuous in this stage — disclosed**: h3 left the *requested* sink as the default, so the silent fallback and a successful resolution are indistinguishable here. The discriminating cell is `d3`/`d10b` in stage D (default = the other sink). |
| h6 bogus target + `dont-fallback` | 0 links + `defined target not found` ✓ |
| h7 a 44100 Hz stream into the 44100 Hz core | links the requested sink ✓ |

So none of the confirmed laws is clock-dependent in this shape, and the one
clock-arm cell that *looks* like a confirmation is recorded as vacuous rather
than as evidence — the same failure mode the scout warned about for the
`linking.follow-default-target` row.

### 4.6 Sibling seat presence (assigned axis)
Real foreign seats were live throughout (read-only `ps` census: r90-author,
r92-boundary, r95, r96, r97-scout, r98, r99-scout — §6), and a **second private
pair of this seat** (own conf, own runtime dir `run-sibling/`, own state dir) was
armed simultaneously (`g_sibling_exit.json`): the main pair saw
`["Dummy-Driver","Freewheel-Driver","r97b_main_g", …]` and **not** `r97b_sib_g`;
the sibling pair saw `["Dummy-Driver","Freewheel-Driver","r97b_sib_g"]` and
**not** the main pair's sink; neither appeared in the shared graph; both pairs'
WirePlumber passed the `sm-settings` gate. Isolation holds under sibling
presence.

---

## 5. Load arm, timing and the private-core wedge

### 5.1 What load did and did not change
| cell class | ambient | +12 seat hogs | effect |
| --- | --- | --- | --- |
| arming rc/messages (A) | rc 78, 293 B, 0.004–0.009 s | *(§5.3 table)* | none expected |
| core access hang (B1) | clients killed at 8 s, 0 B | *(§5.3)* | none |
| default-node cells (C) | first poll correct | *(§5.3)* | none |
| linking legs (D) | all cells as tabulated | *(§5.3)* | none |
| `wpexec` errors (E) | rc 70 / rc 70 / −9 | *(§5.3)* | none |
| settings lattice (F) | 25 keys, same sha | *(§5.3)* | none |
| **timing resolution** | `pw-dump` 0.015–0.065 s | *(§5.3)* | the *latency claims* are measurable only to one dump round trip |

### 5.2 The wedge (scout §2.5 / `[?]`3): characterized, not isolated
This seat's private core **wedged once**, during the first (unprotected) run of
the stage-C battery, at loadavg 118.7/97.8/85.6 with no seat hogs. Forensics
captured while still wedged (`wedge_forensics.json`, `wedge_ledger.jsonl`):

| probe | result |
| --- | --- |
| `pw-dump` | killed at 12 s (and 20 s, and 30 s), **0 bytes** |
| `pw-cli ls Client` | killed at 12 s, **no output at all** |
| `wpctl status` | killed at 12 s, 0 bytes |
| core process | alive, **2 threads**, `state R` at first probe (spinning) then `S` in `do_epoll_wait`, `utime=1 stime=1`, 27 fds |
| private WirePlumber | alive, 6 threads, all parked (`poll_schedule_timeout`, `do_epoll_wait`, `futex_do_wait`), 0 CPU |
| recovery | **full re-arm only** (kill core + start core) — the wedge survived the WP being killed; after the core was killed, `pw-dump` returned rc 255 instantly (no socket) |
| shared session | unaffected throughout: shared `pw-dump` answered in **75 ms** with 274 KB while the private core was wedged |

Trigger search (`w_wedge.json`) — four candidate triggers, each on a freshly
re-armed pair, liveness probed every step:

| variant | steps | wedge? |
| --- | --- | --- |
| W1 dump storm (sequential `pw-dump`) | 15 | no |
| W2 sink churn (create → dump → destroy → dump) | 15 | no |
| W3 `set-default`/`clear-default` churn | 15 | no |
| W4 WirePlumber restart churn (sinks alive) | 15 | no |
| W5 **rapid connection storm** (400 back-to-back `pw-dump`, no sleep) | 400 | **no** — every leg 0.016 s |

So the wedge is **not** connection churn, sink churn, set-default churn or WP
restart churn at these doses. It remains `[?]`, but the negative is now bounded
and the recovery procedure is pinned: re-arm, never trust the pid file, and
detect it with a **bounded** `pw-dump` (a wedge shows `timed_out` with 0 bytes;
an absent core shows rc 255 in <10 ms — the two must not be conflated).

### 5.3 Seat-hog arm (12 own hogs + the ambient 48–96 foreign ones)
Every load-bearing stage was re-run with 12 `r97b_hog` processes of this seat
live (`receipts/*.hogs.json`; loadavg 98.9–120.6 during the legs):

| cell class | ambient result | hogs-arm result | verdict |
| --- | --- | --- | --- |
| arming V1/V2/V3/V4/V5/V6 | rc 78 naming message; replacement; additive; rc 78 `sm-objects.lua` | **identical** (2 reps) | load-independent |
| core access B1/B2/B3 | hang / 0.009–0.014 s answer / answer | **identical** (B1 killed at 8.009 s, 0 B) | load-independent |
| default cells c1/c2/c3/c6/c8a/c8b | first-sink, takeover, no-steal, clear→best, tie-keeps both orders | **identical** (2 reps, first poll, 0.014–0.023 s) | load-independent |
| restart race | immediate/0.5 s ⇒ lost; after-file ⇒ survives; lag ≈1.00 s | **identical** (lag 1.004 / 1.006 s) | load-independent |
| linking, all 19 legs × 2 reps | as §3.4 / §4.1–4.3 | **identical**, leg for leg | load-independent |
| `wpexec` inventory + 4 error shapes + `--help` + arg forms | rc 70 / rc 70 / −9 / rc 64 | **identical**, and the FOUND/MISSING/ENV lines are byte-identical to the scout's receipt in **both** arms | load-independent |
| settings lattice | 25 keys, sha `56526540…` | **identical** sha in both arms, and identical to the operator's shared instance | load-independent |
| sibling-pair isolation | clean | **clean** (each pair sees only its own sink; shared graph 79 objects, 0 `r97b` hits) | load-independent |
| latency resolution | `pw-dump` 0.015–0.065 s | same | the *only* load-sensitive quantity in this seat's window |

Two anomalies in the hogs arm are recorded rather than smoothed over:

1. **`a_arming` V2 rep 1 was killed at 14.3 s with `rc -9` and `timed_out=False`**
   — i.e. something outside the harness SIGKILLed that one private WirePlumber
   (the other 5 variants and both reps of every other stage behaved normally).
   No foreign seat uses a broad `pkill` (checked read-only: every sibling sweep
   is seat-path-scoped), and no OOM message is visible from this seat's
   privilege level; memory pressure was real (10.7 GB swap in use at window
   start). Recorded as an unexplained single-leg kill.
2. **The first hogs `c_defaults` rep 0 was contaminated** by two `r97b_*` sinks
   (session 500) left alive by the duplicate chain this seat killed (§6); the
   affected cells (`c3`, `c6`, `c8a`) read the leftover as the default. Fixed by
   purging own-namespace sinks before each rep (`purge_own_sinks`) and re-running
   the stage: the clean run above is the receipt of record, and the contaminated
   pass is disclosed here rather than deleted.

---

## 6. Contention ledger and exit state

| window | contact | effect |
| --- | --- | --- |
| whole window | **foreign `yes` hogs: 48 → 96** concurrent (read-only `ps` census, never signalled) | the host was never quiet; the "ambient" arm is *ambient*, not *quiet* |
| whole window | foreign seats live and working: **r90-author** (godot + battery), **r92-boundary**, **r95**, **r96**, **r97-scout**, **r98**, **r99-scout** (own private pipewire + `pw-record` legs) | read-only census only; no foreign process signalled |
| whole window | this seat: private core + private WP + bounded clients in `run/`, plus `run2/` (modules-less core legs), `run3/` (access cells), `run-sibling/` (sibling pair) | own objects only; every kill by own pid + cmdline/environ guard |
| 21:24Z | **foreign mutation observed**: `~/.local/state/wireplumber/default-nodes` rewritten by another seat — the shared configured sink is now `alsa_output.pci-0000_01_00.1.hdmi-stereo.99` and the history stack grew to `.0=r93b_in`, `.1=…SPDIF__sink`, `.2=r87b_ns`, `.3=…Speaker…` (450 B at 17:15Z → 566 B at 21:24Z) | **not this seat**: this seat's state dir is its own, and the shared files hold **0 `r97b` rows** |
| whole window | shared `~/.local/state/wireplumber/stream-properties` grew 691 211 B (17:46Z) → **739 068 B** (21:47Z), rows from `r91b_ns` (13), `r96s_pulse` (10), `r90b_rc`/`r90b_rb` (7 each), `r96b_pulse` (4), `r91s_diag` (4), `r92s_fc`, `r91s_ns1` … | foreign lanes (r90/r91/r92/r96 class of residue); **0 `r97b` rows** |
| 21:31Z | one `health_fail` entry in the ledger with rc **255** in 9 ms | **not a wedge**: this seat's own two background chains collided and one killed the other's core. Disclosed, and the collision is why the second ambient chain was killed |
| exit | private pair stopped by pid file; pid files removed; 0 seat processes; 0 `r97b` objects in the shared graph; shared daemons 2060/2063/2694 alive with boot-time start times | §6.1 |

### 6.1 Exit census (`receipts/exit_census.json`, 21:47:28Z)
- private pair: `wp stopped (was 1773478)`, `core stopped (was 1773272)`; **0 pid
  files** left in `run/`; **0 `r97b_hog`** processes.
- **own seat processes: 0** — an env-or-cmdline scan of every `/proc` entry for
  this seat path returns only the census command itself.
- **shared graph: 121 objects, `r97b` hits: 0.**
- shared daemons **2060 (`pipewire`), 2063 (`wireplumber`), 2694
  (`pipewire-pulse`) all alive with `starttime` 2274/2274/2371** — i.e. all
  three have been up since ~37–40 min after boot, hours before this window: none
  was signalled, restarted or reconfigured by this seat.
- shared state fingerprints (never written by this seat): `default-nodes`
  566 B sha `ded82908…` mtime 21:24Z; `stream-properties` 739 068 B sha
  `ad028702…` mtime 21:47:30Z (still being written by foreign lanes at exit).

---

## 7. Remaining unknowns and risks

1. `[?]` **The wedge trigger.** Characterized, reproduced once, four candidate
   triggers falsified at 15–400 steps. Not isolated. Risk for every other lane
   that arms a private pair: a wedged core looks like "policy did nothing".
2. `[?]` **Which path moves a stream when the default changes.** Both
   `linking.follow-default-target=false` and `linking.allow-moving-streams=false`
   are inert in the plain-`pw-cat` shape (3/3 each). The movement therefore comes
   from a path neither setting gates in 0.5.17 — the scout's `[?]`2 is unchanged
   and now has a second inert gate recorded.
3. `[?]` **The WP-side log line for the `linger` branch** was not re-verified
   (info-level logging was off in this seat's daemon).
4. **The `≈1 s` state-file flush window** (§2.2) is measured for a private
   instance on this host under this load; whether the same 1 s window applies to
   the operator's shared WirePlumber was **not** tested (this seat does not write
   the shared instance). Any row asserting restart durability must arm the wait,
   not the set.
5. **Timing claims below one `pw-dump` round trip** (0.015–0.065 s here) are not
   measurable in this seat's shape; the scout's "≤0.1 s" is confirmed only at
   that resolution.
6. **Foreign tracked dirt** (`corpus/fixtures/measure_audio.py`, +2264/−3) is
   another seat's live work; this seat neither wrote nor reverted it.
7. **One unexplained SIGKILL** of a single private WirePlumber leg in the hogs
   arm (§5.3) — 14.3 s into a 20 s variant, no timeout, no OOM message visible,
   no foreign broad-`pkill` in any sibling seat's scripts. Any lane that runs a
   private daemon under this host's memory pressure should expect and detect it.
8. **A vacuous cell is not evidence** — `h_clock.h5` (§4.5) is recorded as
   vacuous because the fallback target equalled the requested target. Rows
   derived from this seat must use `d3`/`d10b`, not `h5`.

---

## 8. Hand-off: what an author row should and should not assert

- **Do assert**: rc 78 + `Could not locate configuration file 'wireplumber.conf'`
  for the empty `WIREPLUMBER_CONFIG_DIR` shape (never the scout's three-message
  chain); the restart-durability cell **only** with an explicit wait for the
  state-file row (or it will flake 3/3 in the other direction); `target.object`
  vs `node.target` as *different namespaces* (assert the sink, never the rc);
  the `linger` face as "0 links, node present, empty stderr"; the `sm-settings`
  metadata object as the WirePlumber-up witness (never `wpctl status` rc).
- **Do not assert**: `linking.follow-default-target` or
  `linking.allow-moving-streams` as behavioural gates in the plain-`pw-cat`
  shape (both inert 3/3); any latency claim below one `pw-dump` round trip; the
  `wpexec` JSON argument as reachable from the script (`arg` is nil); the
  WP-side `waiting for defined target` log line from client stderr (it is not
  there).

---

## 9. Artifacts and provenance

`corpus/live/r97-boundary/` (untracked): `probes/` (`r97blib.py` bounded runner +
private-env + wedge-aware `dump`/`health`, `up.sh`, `down.sh` environ-aware guard,
`hogs.sh`, `a_arming.py`, `a2_core_no_modules.py`, `b_access.py`, `c_defaults.py`,
`c3_restart_race.py`, `c4_priority.py`, `d_linking.py`, `e_wpexec.py`,
`f_settings.py`, `g_sibling_exit.py`, `h_clock.py`, `w_wedge.py`,
`wf_forensics.py`, `analyze.py`, `build_manifest.py`); `receipts/*.json`
(+ `*.ambient.json` arm copies, `wedge_ledger.jsonl`); `runs/` (stage logs,
`core.log`, `wp.log`); `conf/` (private core conf + fragments, WP fragment,
`wp-empty`, `wp-copy`, `wp-stub`, `wpdata`, sibling conf, per-cell core confs);
`scratch/` (Lua legs, `pw-cli` sessions, settings listings); `manifest.sha256`.

Version anchors: `pipewire` 1.6.8, `wireplumber` 0.5.17, `/usr/share/wireplumber/
wireplumber.conf`, `/usr/share/wireplumber/scripts/…`,
`/usr/lib/libpipewire-0.3.so.0`, `/usr/lib/wireplumber-0.5/libwireplumber.so.0.5`,
`/usr/bin/wpexec`.
