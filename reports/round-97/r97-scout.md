# R97 scout — the WirePlumber 0.5.17 policy/scripting surface, measured in a private instance

Host `plazir27`, 2026-10-15 17:06–17:26Z, HEAD `1abd954`. WirePlumber 0.5.17
(`libwireplumber 0.5.17`), PipeWire 1.6.8, Lua 5.5 sandbox. Every measurement
below ran against a **private PipeWire core + private WirePlumber pair** under
`corpus/live/r97-scout/run` (own runtime dir ⇒ own socket). The shared daemons
(pid 2060/2063/2694) were never signalled, restarted or reconfigured, and no
`r97s` object ever appeared in the shared graph (exit check §10).

Labels: `[O]` measured on this host by this seat, `[I]` inferred from an
installed source artifact, `[?]` unresolved. Reps are ≥3 and are named in every
claim; receipts are pinned in `manifest.sha256` and rolled up in `summary.json`.

---

## 0. Why this surface (the pick, and what it displaces)

The wave assignment names the WirePlumber policy engine — Lua scripts,
prepare-link, default-device selection, device profiles, policy hooks,
`wpexec`, namespaced WP config overrides — as "the policy layer every other
lane's laws ride on". Three concrete debts pointed at it:

1. **r92 [?]8** — the `filter.smart` / `node.filter-graph.rules`
   `create-filter-graph` policy path was implemented on disk but "needs a config
   file + daemon reload (operator decision), so it was not armed".
2. **r92 [?]2** — `wpexec`'s global/API namespace "could not be narrowed
   further" (bare `Lua runtime error`, rc 70) and r90's 25-key Settings
   cross-witness was therefore not delivered.
3. Every linking lane (r81, r92, r95, r96) inherits *why* a stream ends up on
   the operator's SPDIF sink, and r95/r96 inherit *why* `set-default` is
   forbidden on the shared host. That is the default-node policy, unmeasured.

The way to measure all of it without touching the operator's session is a
private instance. That decision is itself the first law below (§2), because the
documented env overrides do not do what the man page says.

---

## 1. Headline claims

| # | claim | evidence | reps |
| --- | --- | --- | --- |
| 1 | `WIREPLUMBER_CONFIG_DIR` / `WIREPLUMBER_DATA_DIR` **replace** their search path instead of extending it; a dir without `wireplumber.conf` yields `no modules loaded from context.modules` → `can't find protocol 'PipeWire:Protocol:Native'` → `Failed to connect to PipeWire`, **exit 78 (EX_CONFIG)** — the message never names the missing file | `receipts/a_arming.json` V1, `runs/a_v5_full.log` | 3/3 identical |
| 2 | A private WirePlumber needs only a private `XDG_CONFIG_HOME` (fragment dir) + private `XDG_RUNTIME_DIR`/`PIPEWIRE_RUNTIME_DIR`: the shipped `wireplumber.conf` and its fragments stay in the search path, the operator's `~/.config/wireplumber` fragment does not | `receipts/a_arming.json` V3 vs V4 | 3/3 identical |
| 3 | A private **core** must keep `libpipewire-module-access`: with `module.access = false` the socket listens but the core never answers a handshake — `pw-cli`/`pw-dump`/`wpctl` hang with no error line | bisect in `runs/`, §2.4 | 3/3 identical |
| 4 | Default-node selection ranks by `priority.session`, **falls back to `priority.driver` only when `priority.session` is absent**, and a **tie keeps the incumbent**; an explicit `wpctl set-default` outranks every later priority and survives a WirePlumber restart | `receipts/c_default_nodes.json`, `c2_default_controls.json`, `c3_restart.json`, `e_residuals.json` | 3/3 each |
| 5 | `wpctl set-default <id>` writes **both** `default.audio.sink` and `default.configured.audio.sink` in the `default` metadata, and the state hook writes `$XDG_STATE_HOME/wireplumber/default-nodes` = `[default-nodes]\ndefault.configured.audio.sink=<name>` (54 B, 3/3 byte-identical); the previous configured value is kept as `…sink.0` | `receipts/c2_default_controls.json`, `c3_restart.json` | 3/3 |
| 6 | A numeric `pw-cat --target` is an **`object.serial`** (the property written is `target.object`); a **global id silently falls back to the default sink**, as does any bogus target — no error, rc 0 | `receipts/d_linking.json` | 3/3 |
| 7 | `node.dont-fallback = true` + an unresolvable target ⇒ **no link**, client error `-2 "defined target not found"`, and WirePlumber **destroys the stream node** (`find-defined-target.lua:120-133`); `node.linger` changes that to "wait" | `receipts/d_linking.json` | 3/3 |
| 8 | `wpexec`'s Lua environment is a curated sandbox with **no `_G`** (the `_ENV` upvalue exists but `_ENV._G` is nil), no `io`/`load`/`dofile`/`require_api`/`rawget`/`unpack`, and `debug` present; Lua 5.5 | `receipts/b_wpexec.json` | 3/3 byte-identical |
| 9 | **Every** runtime error in `wpexec` exits rc 70 with the bare stderr string `Lua runtime error` — no message, no line, no stack — while compile errors do carry a location (`Failed to compile: [string "x.lua"]:1: syntax error near 'is'`) | `receipts/b_wpexec.json` | 3/3 |
| 10 | `Settings.get_boolean/float/string` inside `wpexec` returns false/0.0/"" for every key and does not change when the live value changes (verified by `wpctl settings` read-back) — the `settings-instance` binding step (`wireplumber.conf:288-297`) is not run by `wpexec` | `receipts/b_wpexec.json`, labrat fold §11 | 3/3 |
| 11 | The live settings lattice is 25 keys, readable and writable with `wpctl settings [KEY] [VAL]`, published twice: `schema-sm-settings` (schema) and `sm-settings` (values) metadata objects | `scratch/settings_list.txt`, `receipts/b_wpexec.json` | 3/3 |
| 12 | `linking.follow-default-target = false` (verified `Value: false`) did **not** stop a stream from moving to a new default — the documented behaviour of that key is not observable in this shape `[?]` | `receipts/e_residuals.json` | 3/3 |

---

## 2. The arming law — how a private WirePlumber actually gets its config

### 2.1 The env matrix (`receipts/a_arming.json`, 3 reps each, byte-identical)

| variant | env | rc | fragments actually opened | verdict |
| --- | --- | --- | --- | --- |
| V1 | `WIREPLUMBER_CONFIG_DIR=<dir without wireplumber.conf>` | **78** | *(none)* | **EX_CONFIG**: no main conf ⇒ `no modules loaded from context.modules` ⇒ `can't find protocol 'PipeWire:Protocol:Native'` ⇒ `Failed to connect to PipeWire`. The log never says "wireplumber.conf not found" |
| V2 | `WIREPLUMBER_CONFIG_DIR=<dir with a copy of the conf>` | running (capped) | only the copy's `alsa-vm.conf` | the override **replaces** the whole config search path: `/usr/share/wireplumber/wireplumber.conf.d` is no longer read |
| V3 | private `XDG_CONFIG_HOME` + fragment at `$XDG_CONFIG_HOME/wireplumber/wireplumber.conf.d/` | running | `alsa-vm.conf` (shipped) + `10-r97s.conf` (mine) | **the arming shape used by every measurement in this report** |
| V4 | *(no override — default user config)* | running | `alsa-vm.conf` + `~/.config/wireplumber/…/bluetooth-a2dp-autoconnect.conf` | documents that a "private" instance that forgets `XDG_CONFIG_HOME` silently inherits the operator's fragments |
| V5 | private `XDG_CONFIG_HOME` **+ `WIREPLUMBER_DATA_DIR=<seat data dir>`** | **78** | `alsa-vm.conf` + my probe fragment | `failed to load required component 'metadata.sm-objects [script/lua: sm-objects.lua]': Could not locate script 'sm-objects.lua'` — **the data dir replaces the script search path too** |

`[O]` The two override variables therefore behave as *replacements*, not as the
man page's "searched first", and their failure modes differ in quality: the
`DATA_DIR` failure names the missing script, the `CONFIG_DIR` failure does not
name the missing config. Both exit 78.

### 2.2 The arming shape (verbatim)

```sh
# private core (never the shared one)
PIPEWIRE_RUNTIME_DIR=$SEAT/run XDG_RUNTIME_DIR=$SEAT/run \
  pipewire -c $SEAT/conf/pw/r97s-pipewire.conf
# private WirePlumber on top of it
PIPEWIRE_RUNTIME_DIR=$SEAT/run XDG_RUNTIME_DIR=$SEAT/run \
  XDG_CONFIG_HOME=$SEAT/conf/xdg-config XDG_STATE_HOME=$SEAT/conf/xdg-state \
  wireplumber -c wireplumber.conf -p main
```
`probes/up.sh` / `probes/down.sh` are target-aware (`core|wp|both`) and kill only
this seat's pid files; the core conf is a copy of the shipped `pipewire.conf`
plus `conf/pw/r97s-pipewire.conf.d/10-r97s.conf` which disables
`module.rt`/`module.profiler`/`module.portal` (host-scheduling and
desktop-integration side effects) and **keeps** `module.access` (§2.4).

### 2.3 Fragment merge semantics (`runs/a_v6*.log`)

- `[O]` `section 'wireplumber.profiles' is merged from multiple locations` and
  `section 'wireplumber.components' is merged from multiple locations` — arrays
  concatenate across the main conf and fragments.
- `[O]` A fragment setting `wireplumber.profiles.main.hardware.audio = disabled`
  **does** take effect: the private instance never enables `monitors/alsa.lua`,
  never enumerates udev, and never opens a host ALSA PCM. This is the safety
  property every measurement here relies on.
- `[?]` A component *added* by a fragment is present in the merged array
  (`pw_conf_find_match: 'provides' … 'r97s.probe'`, `runs/a_v6d.log:1008-1010`)
  but is **never loaded**, even when the same fragment's profile lists
  `r97s.probe = required` and the daemon starts normally (rc 124 = ran to the
  cap). A fragment therefore cannot inject a new Lua component into the `main`
  profile by this route — see §9.1.

### 2.4 The private core needs `module.access` (falsifier that found a trap)

Disabling the access module in the private core produced the worst possible
failure shape: `pipewire` starts, creates `pipewire-0` and `pipewire-0-manager`
sockets, registers the Dummy-Driver and Freewheel-Driver — and then **never
answers any client**. `pw-cli`, `pw-dump` and `wpctl status` all block until
killed; the core log has no error line. Bisect (3/3):

| core fragment | `pw-cli ls Client` |
| --- | --- |
| `module.access = false` (+ rt/profiler/portal off) | hangs, no output |
| rt/profiler/portal off, access untouched | `id 28, type PipeWire:Interface:Client/3 …` |
| no fragment at all | `id 32, type PipeWire:Interface:Client/3 …` |

### 2.5 Harness notes (recorded, not hidden)

- The private core was found **wedged twice** (process alive, sockets present,
  zero replies to any client) — once after a long battery and once after a
  WirePlumber restart. Recovery is a full re-arm; `r97lib.ensure_up()` now
  force-restarts the pair instead of trusting the pid file. Whether the wedge is
  a PipeWire defect or a harness/GC artifact was **not** isolated `[?]`.
- `PwCli.close()` (closing `pw-cli`'s stdin) destroys the nodes it created —
  every stage that needs persistent nodes keeps one `pw-cli` alive and one
  `pw-cat` per stream, and kills both by process group.
- The private pair must be re-armed per stage; this is cheap (≈1.5 s) and is
  done by `ensure_up()` at the top of each stage.

---

## 3. Default-node policy — the law every other lane rides on

### 3.1 Candidate ranking (`receipts/c_default_nodes.json`, `c2_default_controls.json`, `e_residuals.json`)

| # | cell (all 3/3 unless noted) | result |
| --- | --- | --- |
| 1 | first sink to appear becomes the default | default = A |
| 2 | a second sink with a **strictly higher** `priority.session` takes over | default = B (200 > 100) |
| 3 | a third sink with a **lower** priority does not | default stays B |
| 4 | `wpctl set-default <C>` (the low-priority sink) | default = C |
| 5 | a **new sink with the highest priority of all** (300) appears | default **stays C** — the explicit choice wins |
| 6 | `wpctl clear-default` | default = D (the best available) |
| 7 | the current default is destroyed | default = the best remaining (B) |
| 8 | equal `priority.session`, different `priority.driver` — created **low-driver first** | incumbent keeps (E) |
| 9 | equal `priority.session`, different `priority.driver` — created **high-driver first** | incumbent keeps (H) |
| 10 | a sink with **no** `priority.session`/`priority.driver` at all | does not displace a 100 |
| 11 | a sink with **no `priority.session` but `priority.driver = 999`** | **takes over** from an incumbent with `priority.session = 100` |

Cells 8–11 together falsify "priority.driver is irrelevant" and "creation order
decides": `[I]` `lib/node-utils.lua:11-18` resolves the rank as
`priority.session`, **else `priority.driver`**, else `0`; `:76-95`
(`compare_nodes`) compares priority first and then falls to serials; and
`default-nodes/find-best-default-node.lua:29-35` gives the already-selected node
`serial = math.mininteger` with the comment that this "keeps the selection
whenever a candidate merely ties with it on the priority" — the measured
tie-keeps-incumbent behaviour.

### 3.2 The configured default: metadata, state file, restart

| observation | value | reps |
| --- | --- | --- |
| after `set-default`: `default.audio.sink` | `{"name": "<sink>"}` | 3/3 |
| after `set-default`: `default.configured.audio.sink` | `{"name": "<sink>"}` (same row set) | 3/3 |
| state file `$XDG_STATE_HOME/wireplumber/default-nodes` | `[default-nodes]\ndefault.configured.audio.sink=<sink>\n` (54 B) | 3/3 byte-identical |
| all sinks destroyed | `default.audio.sink` gone, `default.configured.audio.sink` **stays** | 3/3 |
| after a private WirePlumber restart (sinks alive, configured = low-priority P, best = Q) | default = **P**, and the state file gains `default.configured.audio.sink.0=Q` | 3/3 |
| `wpctl clear-default` | configured row removed; the best available becomes default | 3/3 |

`[I]` `default-nodes/state-default-nodes.lua` is the hook that persists this;
the `.0`/`.1` keys are the history stack — which is exactly what the operator's
shared `~/.local/state/wireplumber/default-nodes` shows
(`default.configured.audio.sink=…SPDIF__sink`, `.0=r87b_ns`, `.1=…Speaker…`).
**Consequence for other lanes:** the shared host's default sink is a *configured
choice*, not a priority outcome; a new sink — even one with a huge
`priority.session` — will not steal it, which is why r81/r92/r95 streams
consistently landed on SPDIF.

---

## 4. Linking policy — prepare-link, target addressing, fallback

Stream armed with `pw-cat -p --raw --rate 48000 --channels 1 --format s16 -`
(stdin held open; `node.name=r97s_str`), against sinks A (`priority.session=100`)
and B (`500`, so B is the default). Links read from `pw-dump`
(`receipts/d_linking.json`, 3 reps each; the table lists the sink the stream
linked to):

| leg | argv / props | linked to | notes |
| --- | --- | --- | --- |
| `--target 0` | documented "don't link" | *(none)* | 3/3 no links |
| auto | *(no target)* | default (B) | 3/3 |
| `--target <A global id>` | 38 / 37 / 38 | **default (B)** | silent fallback, rc 0, empty stderr |
| `--target <A object.serial>` | 43 / 133 / 223 | **A** | the correct numeric form |
| `--target <A node.name>` | `r97s_sa*` | **A** | names resolve (unlike the JACK name path r95 measured) |
| `--target 99999` | bogus | default (B) | silent fallback, rc 0 |
| `--target 99999` + `node.dont-fallback=true` | | *(none)* | stderr `stream node 49 error: defined target not found`; the stream node is **gone** from the graph |
| `media.role=Communication` | no target | default (B) | no role-based target picked |

Mechanism, read on this host:

- `[I]` `linking/find-defined-target.lua:45-51` — `target.object` is looked up
  by **`object.serial`**, `node.target` by `node.id`. `[O]` a live dump of the
  stream node during both numeric legs shows the property `pw-cat --target`
  actually writes is **`target.object = <the number>`** (plus
  `node.autoconnect = true`) — `receipts/f_target_property.json`, 3 reps ×
  (serial leg, global-id leg): `target.object` 40/38, 63/38, 86/38 in the three
  reps, with the sink's `object.serial` = 40/63/86 and its global id = 38. In
  that stage only one sink existed, so *both* legs linked to it (the fallback
  lands on the default = that sink); the discrimination comes from stage D,
  where the id leg landed on the **other** (default) sink while the serial leg
  landed on the requested one. So: a numeric target is a serial, and a global id
  misses silently.
- `[I]` `linking/find-defined-target.lua:120-133` — on a defined target that is
  not found with `dont-fallback`: `sendClientError (…, -2, "defined target not
  found")` then `node:request_destroy ()` unless `node.linger`; with `linger`
  the hook logs "waiting for defined target as dont-fallback is set" instead.
  That is exactly the measured stderr and the vanished node.
- `[I]` `linking/find-default-target.lua:31-56` — when nothing was picked,
  `lutils.findDefaultLinkable(si)` supplies the default node: the fallback path.
- `[I]` `linking/find-media-role-sink-target.lua:38-60` — the role-based sink
  target only applies to `Stream/Output/Audio` nodes that are **virtual and
  carry a `node.link-group`** (role-based loopback streams), and it reads
  `policy.role-based.preferred-target` from the *input* node of that group.
  A plain `pw-cat` stream is neither, so the measured null is expected, not a
  failed arm.

### 4.1 `linking.follow-default-target` — measured inert in this shape `[?]`

With the stream linked to the default B and `linking.follow-default-target`
**verified as `Value: false`** by `wpctl settings <key>` read-back, switching
the default to A still moved the stream to A (3/3). The `true` arm behaves
identically, so this arming shape cannot discriminate the key. Either the key
does not gate this path in 0.5.17, or the movement is performed by another
policy path (e.g. `linking/rescan.lua` re-selecting an unset target). Recorded
as a measured negative for the row author: **do not** build a row that asserts
this key's documented behaviour.

---

## 5. `wpexec` — the Lua sandbox, closed from both sides

### 5.1 Inventory (`receipts/b_wpexec.json`, 3 reps byte-identical)

Probe: for each of 65 candidate names, `_ENV[n]`; `_G` and `_ENV` themselves are
not keys of the environment table, so `_G` can be *tested* but not enumerated.
Result: **39 present, 26 absent** (byte-identical across the 3 reps).

**Present (39):** `Core Settings Log LocalModule LocalNode SpaDevice ObjectManager
Node Device Link Interest Constraint Script Feature Features ImplMetadata GLib
utf8 table string math os debug require print type pairs ipairs next select
pcall xpcall error assert setmetatable getmetatable tonumber tostring _VERSION`

**Absent (26):** `_G StaticObject Object Client Metadata Session Endpoint SiLink
SiAdapter SiNode Wp utils io load loadstring dofile require_api rawget rawset
unpack json spa GObject bit32 ImplModule`

`[O]` `print("ENV=" .. type(_ENV) .. " G=" .. tostring(_G) .. " VERSION=" .. _VERSION)`
→ `ENV=table G=nil VERSION=Lua 5.5`; `type(debug.getregistry) == "function"`.
So: the compiler-level `_ENV` upvalue is real, `_G` is deliberately not in it,
file/process loading (`io`, `load`, `dofile`, `os.execute`) is removed, and the
reflective `debug` library is **kept**. `require` resolves WirePlumber's own Lua
library (`require("node-utils")` appears throughout the shipped scripts).

### 5.2 Error classes

| leg | rc | stderr (verbatim) |
| --- | --- | --- |
| syntax error | 70 | `Failed to compile: [string "b_syntax.lua"]:1: syntax error near 'is'` |
| `error("r97s deliberate")` | 70 | `Lua runtime error` |
| `error("r97s deep", 2)` inside a function | 70 | `Lua runtime error` |
| indexing `nil` | 70 | `Lua runtime error` |
| `for k,v in pairs(_G)` | 70 | `Lua runtime error` |
| script without `Core.quit()` | −9 (killed at the 6 s cap) | *(its `print` output did appear)* |
| no argument | 70 | `Could not locate script '(null)'` |
| missing file | 70 | `Could not locate script '/nonexistent/r97s.lua'` |

`[O]` `strings -a /usr/lib/wireplumber-0.5/libwireplumber-module-lua-scripting.so`
contains `Lua runtime error`, `Failed to compile: %s` and
`Could not locate script '%s'` (lines 1317/1323/1058), while `/usr/bin/wpexec`
contains only `script/lua` and the module name — `wpexec` is a thin loader and
the interpreter (and its diagnostic loss) lives in the module.

**This closes r92 [?]2**: the reason r92's W2/W3 died with a bare
`Lua runtime error` is that any script touching `_G` (or erroring at all) loses
its message, not that the API namespace is unknown. The namespace is now
enumerated above.

### 5.3 `Settings` is unbound in `wpexec`

| key | wpexec `get_boolean/float/string` | live value (`wpctl settings`) |
| --- | --- | --- |
| `linking.follow-default-target` | false / 0.0 / "" | true (and false after an explicit write) |
| `node.stream.restore-props` | false / 0.0 / "" | true |
| `node.features.audio.no-dsp` | false / 0.0 / "" | false |
| `device.routes.default-sink-volume` | false / 0.0 / "" | 0.064 |
| `bluetooth.profile-preference` | false / 0.0 / "" | "quality" |
| `node.stream.default-media-role` | false / 0.0 / "" | null |

3/3 byte-identical, before and after a `wpctl settings
linking.follow-default-target false` write that the CLI confirmed
(`Updated setting … to: false`) and read back (`Value: false`). `[I]`
`/usr/share/wireplumber/wireplumber.conf:288-297` explains it: settings reach
scripts only through the `settings-instance` built-in component, which
"Activates a global WpSettings instance, providing settings from the sm-settings
metadata object… blocks and waits for the sm-settings metadata object to become
available". `wpexec` runs no component graph, so its `Settings` object exists
but is never bound. **The r90 Settings cross-witness cannot be delivered from
`wpexec`** — it must come from a daemon-side witness (the shipped scripts'
behaviour) or from `wpctl settings`.

---

## 6. The settings lattice (25 keys) and its two metadata faces

`wpctl settings` (3/3) lists all 25 keys with `Name`, `Desc`, `Type`,
`Default [Min,Max]` and `Value`; `scratch/settings_list.txt` is the verbatim
listing. Defaults observed: `node.stream.restore-props true`,
`node.stream.default-capture-volume 1.0`, `bluetooth.autoswitch-to-headset-profile
true`, `linking.role-based.duck-level 0.3`, `device.restore-routes true`,
`linking.follow-default-target true`, `node.stream.restore-target true`,
`node.restore-default-targets true`, `device.routes.default-source-volume 1.0`,
`linking.allow-moving-streams true`, `device.restore-profile true`,
`device.routes.default-sink-volume 0.064`, `monitor.alsa.autodetect-hdmi-channels
false`, `linking.pause-playback true`, `node.features.audio.control-port false`,
`monitor.camera-discovery-timeout 1000`, `node.stream.default-playback-volume
1.0`, `node.features.audio.no-dsp false`,
`device.routes.mute-on-alsa-playback-removed false`,
`bluetooth.use-persistent-storage true`, `node.features.audio.monitor-ports true`,
`device.routes.mute-on-bluetooth-playback-removed false`,
`bluetooth.profile-preference "quality"`, `node.features.audio.mono false`,
`node.stream.default-media-role null`.

`[O]` The same lattice is published into the graph **twice**:
`pw-dump` shows a `schema-sm-settings` metadata object (each key's
`{name, description, type, default}` JSON, from
`wireplumber.conf:948+ wireplumber.settings.schema`) and an `sm-settings`
metadata object (the live values). Both are readable from any client on the
graph — a cheap, machine-readable lattice for an author row without shelling out
to `wpctl`.

---

## 7. Falsification list (what was tried that could have killed each claim)

| claim | falsifier attempted | outcome |
| --- | --- | --- |
| `WIREPLUMBER_CONFIG_DIR` "searched first" (man page) | a dir *with* a copy of the conf (V2) | **falsified** — it is a replacement: the shipped fragment dir stopped being read |
| `WIREPLUMBER_DATA_DIR` "searched first" (man page) | a dir with one script (V5) | **falsified** — rc 78, `Could not locate script 'sm-objects.lua'` |
| the private instance is isolated | the operator's user fragment appears in V4 only when `XDG_CONFIG_HOME` is *not* overridden | **confirmed isolated** for the arming shape used |
| `module.access` is optional for a headless core | disabled it | **falsified** — the core accepts and never answers |
| default selection is creation-order | equal-priority sinks in both orders | **falsified** — incumbent keeps in both |
| `priority.driver` is irrelevant | 999 vs 100 with equal `priority.session`; then a no-session node with `driver=999` | **refined** — irrelevant for ties, but it is the *fallback* rank and wins outright when `priority.session` is absent |
| an explicit default is just a priority | newcomer with the highest priority after `set-default` | **falsified** — the configured choice wins |
| the configured default is per-session only | private WirePlumber restart with the sinks alive | **falsified** — restored from the state file (and the history key `.0` appears) |
| a numeric `--target` is a global id | `--target <A id>` vs `--target <A serial>` | **falsified** — the id silently links to the default; the serial resolves |
| a bogus target is an error | `--target 99999` | **falsified** — silent fallback, rc 0, empty stderr |
| `node.dont-fallback` is cosmetic | bogus target + `dont-fallback=true` | **falsified** — no link, client error −2, node destroyed |
| `media.role` picks a role sink | `media.role=Communication`, no target | **falsified for plain streams** — the hook needs a virtual link-group stream (`find-media-role-sink-target.lua:38-42`) |
| `linking.follow-default-target=false` stops following | set + verified + switch default | **not observable** in this shape (3/3 moved) — recorded `[?]`, do not arm |
| `wpexec` has an unknown API | enumerated `_ENV` against 67 candidates | **falsified** — the surface is now a closed list |
| `pairs(_G)` should work (r92's W2/W3) | same script | **falsified** — `_G` is nil by design; the error text is lost, not the API |
| `Settings` is broken | read live values after a verified `wpctl settings` write | **refined** — `Settings` is fine in a daemon (40 shipped call sites, `settings-instance` binding); it is **unbound in `wpexec`** |
| the seat perturbs the host | exit census (§10) | only the private instance; shared graph has 0 `r97s` objects and 0 `r97s` state rows |

---

## 8. Author directives — proposed `--probe-wp-policy-r97` rows

All rows are ready to arm as verbatim cells: each has a fixed argv, a
byte-stable expectation and ≥3 reps. They require the **private pair** (§2.2);
they must never be pointed at the shared runtime dir.

**Verbatim-ready rows**

| row | arm | expect |
| --- | --- | --- |
| `wp.arming.private_instance` | §2.2 verbatim with a fresh `XDG_CONFIG_HOME`/`XDG_STATE_HOME`/runtime dir | rc 0, `wpctl status` answers, and the shipped + own fragment both opened |
| `wp.arming.config_dir_replaces` | `WIREPLUMBER_CONFIG_DIR=<empty>` | **rc 78**, stderr/log contains `no modules loaded from context.modules` and `can't find protocol 'PipeWire:Protocol:Native'` |
| `wp.arming.data_dir_replaces` | `WIREPLUMBER_DATA_DIR=<dir with one script>` | **rc 78**, `Could not locate script 'sm-objects.lua'` |
| `wp.core.access_module_required` | private core fragment with `module.access = false` | every client leg times out (hang) — assert the *absence* of a reply, not an rc |
| `wp.default.first_sink_wins` | create one null sink | `default.audio.sink = {name=<sink>}` within ≤0.1 s |
| `wp.default.priority_session` | A(100) then B(200) | default A → B |
| `wp.default.tie_keeps_incumbent` | equal `priority.session`, either creation order | default = first sink |
| `wp.default.driver_is_fallback` | incumbent `session=100`; challenger with **no** session, `driver=999` | default = challenger |
| `wp.default.explicit_beats_priority` | `set-default C(50)`, then create D(300) | default stays C |
| `wp.default.configured_survives_restart` | set-default P, restart the private WP, sinks alive | default = P; state file has `…sink=P` and `…sink.0=Q` |
| `wp.link.target_is_serial` | `--target <global id>` vs `--target <object.serial>` | id → default sink; serial → requested sink |
| `wp.link.target_name` | `--target <node.name>` | links to that sink |
| `wp.link.target_zero` | `--target 0` | 0 links |
| `wp.link.bogus_falls_back` | `--target 99999` | links to the default sink, rc 0, empty stderr |
| `wp.link.dont_fallback_destroys` | `--target 99999` + `node.dont-fallback=true` | 0 links, stderr `defined target not found`, stream node absent from the dump |
| `wp.wpexec.sandbox_no_G` | `print(type(_ENV) .. tostring(_G) .. _VERSION)` | `tablenilLua 5.5` |
| `wp.wpexec.runtime_error_opaque` | `error("x")` | rc 70, stderr exactly `Lua runtime error` |
| `wp.wpexec.compile_error_located` | syntax error | rc 70, stderr starts `Failed to compile: [string "…"]:1:` |
| `wp.wpexec.settings_unbound` | six `Settings.get_*` calls | `false/0.0/""` for all, unchanged after `wpctl settings` writes |
| `wp.settings.lattice_25` | `wpctl settings` | 25 `- Id:` entries, byte-stable order |

**Bimodal / envelope cells (do not arm as a single shape)**

- **Target addressing**: the *same* numeric argument means a serial in
  `pw-cat --target`, while the help text says "serial or name" and a global id
  is accepted without complaint. Arm both a serial and an id and assert the
  *sink*, never the rc.
- **Failure-mode envelope**: an unresolvable target can be (a) a silent
  fallback (rc 0), (b) a client error + node destruction (`dont-fallback`), or
  (c) a wait (`linger`). Assert link presence, not rc.
- **`wpexec` errors**: two different worlds — compile errors are located,
  runtime errors are opaque. Never assert a message for a runtime error.
- **Private-instance env**: `WIREPLUMBER_*_DIR` replace, `XDG_*` add. A row that
  mixes them (V5) is a *failure* row, not an isolation row.
- **`linking.follow-default-target`**: do not arm as a behavioural row until the
  path is identified (§9.2).
- **Default-node state**: assert the metadata row (`default.audio.sink`) for
  "who is default now" and the *state file* only for "what was configured" —
  the file lags the metadata by up to ~1 s (observed empty 1 s after
  `set-default`, populated later).

---

## 9. Remaining unknowns

1. `[?]` **Why a fragment-added `script/lua` component is never loaded** even
   when the fragment's `main` profile requires its `provides` (§2.3). The
   component is present in the merged array (`a_v6d.log:1008-1010`), the profile
   sections merge, the daemon starts (rc 124 = ran to the cap), and no error is
   printed. This blocks the cheap "inject a probe script into the private
   daemon" technique; the in-daemon `Settings` question was instead answered
   from the `settings-instance` anchor + the shipped call sites (§5.3).
2. `[?]` **Which code path moves a stream when the default changes** with
   `linking.follow-default-target=false` (§4.1). Candidates: `linking/rescan.lua`
   re-running `select-target` for a stream whose `node.target` is unset, or the
   setting being read only where role-based loopbacks are created.
3. `[?]` The **private-core wedge** (§2.5): process alive, sockets present, no
   reply. Reproduced twice; not isolated to a trigger.
4. `[?]` `default` metadata-object lifetime: created by `metadata.lua:18`
   (`creating metadata object: default`) and observed absent when the graph has
   no default/configured rows, present again afterwards. The exact
   create/destroy condition was not chased.
5. `[?]` **Device-profile policy** (`policy.device.profile`, 8 hooks) was *not*
   armed: it needs a real `WpDevice` with profiles, which needs ALSA/bluez
   hardware. On a shared host this seat refuses to point a second daemon at the
   host's PCMs. The hook graph and settings gates are anchored in §2 of
   `sources/ANCHORS.md`; the behaviour (voice-call/headset auto-switch, route
   priorities >15000) remains unmeasured.
6. `[?]` `filter.smart` / `node.filter-graph.rules` (r92 [?]8) was not armed
   either: it needs a filter node in a private graph plus the smart-filter
   policy — the private pair is now the arming shape that makes it cheap.
7. `[?]` `node.linger` (the third branch of the defined-target failure) was not
   armed.
8. `[?]` `pw-cli`'s `Error: "unsupported type PipeWire:Interface:SecurityContext"`
   on every connection — cosmetic, but it pollutes every stderr receipt.

---

## 10. Contention ledger + exit state

| window | contact | effect |
| --- | --- | --- |
| whole window | shared graph read-only via `pw-dump`/`pw-cli` at `/run/user/1000`: foreign `r79lb_*`, `r86ctl_*`, `r87b_ns`, `r78fol_*`, `…SPDIF__sink` | read-only; no foreign object touched, no shared default read or written |
| whole window | this seat: private core + private WirePlumber + ~90 bounded client legs (`pw-cli`, `pw-cat`, `pw-dump`, `wpctl`, `wpexec`) in the private runtime dir | own objects only; private state dir holds this seat's rows |
| 17:15Z | **foreign mutation observed**: `~/.local/state/wireplumber/default-nodes` grew 410 → 450 B, gaining `default.configured.audio.sink.0=r87b_ns` | not this seat: my rows were written to the private state dir, and the shared `stream-properties` contains **0** `r97s` rows |
| whole window | shared `~/.local/state/wireplumber/stream-properties` grew 661 KB → 681 KB | foreign lanes (r90/r95 class of residue); 0 `r97s` rows in it |
| exit | private pair stopped by pid file; `pw-dump` (shared) `r97s` count = 0; `ps` seat processes = 0; shared daemons 2060/2063/2694 untouched and up | clean |

---

## 11. Labrat fold (frozen `probeParent` — exactly one child, advisory)

One read-only `ufo-labrat` was dispatched with a single falsifiable hypothesis
(H1: the sandbox global set, the `Lua runtime error` substitution and the
`Settings` binding requirement are all evidenced in the *installed* artifacts).
It returned **PARTIAL SUPPORTS**, with an explicit toolset limitation (no exec ⇒
no `strings`; it could not open the `.so`). What it contributed, and what the
parent then verified itself:

- `[I]` `/usr/share/wireplumber/wireplumber.conf:282-297` — the
  `settings-instance` built-in is the explicit `WpSettings` binding step
  ("blocks and waits for the sm-settings metadata object"); `wpexec` runs no
  component graph. **This is the mechanism behind claim 10** and was folded into
  §5.3 and `sources/ANCHORS.md`.
- `[I]` 40 `Settings.get_*` call sites across 15+ shipped scripts (e.g.
  `node/state-stream.lua:112,404`, `device/autoswitch-bluetooth-profile.lua:577,590`)
  — no shipped script binds settings itself, and none guards the globals
  (`Plugin`, `Json`, `Conf`, `ImplMetadata`, `Script`, `LocalModule`), so the
  globals come from the engine, not from Lua.
- `[O]` The parent closed the child's one gap locally: the strings
  `Lua runtime error` (1317), `Failed to compile: %s` (1323) and
  `Could not locate script '%s'` (1058) are in
  `/usr/lib/wireplumber-0.5/libwireplumber-module-lua-scripting.so`; `/usr/bin/wpexec`
  has none of them.
- The child found **no contradiction** with any parent measurement, and created
  no artifacts.

---

## 12. Artifacts & provenance

`corpus/live/r97-scout/` (untracked, 87 hashed files):
`probes/{r97lib,up.sh,down.sh,a_arming,b_wpexec,c_default,c2_default2,c3_restart,d_linking,e_residuals,f_target_prop,build_manifest}`;
`receipts/{a_arming,b_wpexec,c_default_nodes,c2_default_controls,c3_restart,d_linking,e_residuals,f_target_property,summary}.json`;
`runs/` (stage logs incl. `a_v5_full.log`, `a_v6{,b,c,d}_*.log`, `core.log`,
`wp.log`, `pwcli_debug.log`); `conf/` (private core conf + fragments, the
working private WP fragment, the component-add probe, `wp-copy`, `wp-empty`,
`wpdata`, `xdg-data`); `scratch/` (Lua legs, `settings_list.txt`, pw-cli
sessions); `sources/ANCHORS.md`; `manifest.sha256`; `RECEIPTS.md`.

Key receipt shas (prefix): `a_arming 306b34abb272cfaa`,
`b_wpexec 3f48138e576a8aeb`, `c_default_nodes e4d1da77aa7c1179`,
`c2_default_controls e2c4876c646c414d`, `c3_restart 7173882463987f29`,
`d_linking 020bc042e1840a34`, `e_residuals d7103bb367815673`,
`f_target_property 3c75f8e59ad32279`, `summary 5376fcbd47552671`,
`RECEIPTS.md c122de6dd89bfff3`, `sources/ANCHORS.md 6e6e595c2802ce93`.

Version anchors (all installed, version-matched): `wireplumber` 0.5.17
(`libwireplumber 0.5.17`), `pipewire` 1.6.8, Lua 5.5 sandbox;
`/usr/share/wireplumber/wireplumber.conf` (1121 lines),
`/usr/share/wireplumber/scripts/lib/node-utils.lua`,
`…/default-nodes/find-best-default-node.lua`, `…/linking/find-defined-target.lua`,
`…/linking/find-default-target.lua`, `…/linking/find-media-role-sink-target.lua`,
`…/default-nodes/state-default-nodes.lua`,
`/usr/lib/wireplumber-0.5/libwireplumber-module-lua-scripting.so`.
