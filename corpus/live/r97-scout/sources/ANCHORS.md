# r97-scout mechanism anchors — WirePlumber 0.5.17 / PipeWire 1.6.8 (installed artifacts)

Host plazir27, 2026-10-15. Every anchor below was read on this host; the
binaries are the running ones (`/usr/bin/wireplumber`, `/usr/bin/wpexec`,
`/usr/lib/wireplumber-0.5/libwireplumber-module-lua-scripting.so`,
`/usr/lib/libwireplumber-0.5.so.0.517.0`). No upstream git tree was fetched:
the installed artifacts *are* the version-matched source of truth here.
Labels: [O] observed at runtime by this seat, [I] inferred from a source file.

## 1. Configuration resolution (arming)

| anchor | claim |
| --- | --- |
| `man wireplumber` §ENVIRONMENT | documents `WIREPLUMBER_CONFIG_DIR` / `WIREPLUMBER_DATA_DIR` as "Overrides the directory that is searched first" |
| [O] V1/V5 (§3 of the report) | measured: they **replace** the search path — a dir without `wireplumber.conf` → `no modules loaded from context.modules` → `can't find protocol 'PipeWire:Protocol:Native'` → `Failed to connect to PipeWire`, **exit rc 78 (EX_CONFIG)**; a dir with `WIREPLUMBER_DATA_DIR` but no scripts → `failed to load required component 'metadata.sm-objects [script/lua: sm-objects.lua]': Could not locate script 'sm-objects.lua'` → rc 78 |
| [O] V3/V4 | `XDG_CONFIG_HOME` (and by the same measured pattern `XDG_DATA_HOME`) **add** a fragment/script dir while `/usr/share/wireplumber` stays in the search path |
| [O] `runs/a_v6b_indadaemon.log:54-55` | `section 'wireplumber.profiles' is merged from multiple locations` / `section 'wireplumber.components' is merged from multiple locations` → arrays are concatenated, not replaced |
| [O] `runs/a_v6b_indadaemon.log` (whole) | a fragment profile entry `hardware.audio = disabled` **does** disable `monitor.alsa` (no ALSA component enabled in the log, no udev/ALSA activity) |
| [O] `runs/a_v6d.log:1008-1010` | a component added by a fragment *is* present in the merged array (`pw_conf_find_match: 'provides' ... 'r97s.probe'`) but is never loaded, even when the fragment's profile lists `r97s.probe = required` — see §9 remaining unknowns |
| [O] `runs/core.log` (V-access bisect) | `module.access = false` in the private core leaves the socket listening but the core never answers a client handshake: `pw-cli`/`pw-dump`/`wpctl` hang with no error. Keep the access module |

## 2. Policy graph (the shipped policy, as loaded)

`/usr/share/wireplumber/wireplumber.conf` (1121 lines) is the policy program:

| line | content |
| --- | --- |
| 282–286 | `libwireplumber-module-settings` with `arguments = { metadata.name = sm-settings }`, `provides = metadata.sm-settings` |
| 288–297 | `settings-instance, type = built-in` — "Activates a global WpSettings instance, providing settings from the sm-settings metadata object. Note that this blocks and waits for the sm-settings metadata object to become available" |
| 306–310 | `libwireplumber-module-lua-scripting` = "the lua scripting engine", `provides = support.lua-scripting` |
| 620–656 | `policy.device.profile` virtual component: requires `hooks.device.profile.select`, `…autoswitch-bluetooth`, `…apply`; wants `…find-voice-call`, `…find-best`, `…find-preferred`, `…state` |
| 661–688 | `policy.device.routes`: requires `select`, `apply`; wants `find-best`, `state`, `automute-alsa` |
| 692–721 | `policy.default-nodes`: requires `hooks.default-nodes.rescan`, `…apply`; wants `…find-selected`, `…find-best`, `…state` |
| 759–828 | `policy.linking.standard`: requires `hooks.linking.rescan`, `hooks.linking.target.prepare-link`, `hooks.linking.target.link`; wants the eight target-finding hooks (`find-media-role`, `find-defined`, `find-audio-group`, `find-filter`, `find-default`, `find-best`, `get-filter-from`, `pause-playback`) |
| 854–865 | `policy.standard` = client.access + device.profile + device.routes + default-nodes + linking.standard + linking.role-based + node + support.standard-event-source |
| 900–945 | `wireplumber.components.rules`: every `type = "script/lua"` gets `requires = [ support.lua-scripting ]`; every `provides = "~hooks.*"` (non-monitor) is ordered `before = [ support.standard-event-source ]`; every `provides = "~monitor.*"` `after` it |
| 948–1121 | `wireplumber.settings.schema` — the declared 25-key lattice with `type`, `default`, `min`, `max` |

## 3. Default-node ranking (mechanism)

`/usr/share/wireplumber/scripts/lib/node-utils.lua`:

- `:11-18 get_session_priority` — `priority.session`; **if unset, falls back to `priority.driver`**; `math.tointeger(priority) or 0`.
- `:28-33` (comment) — ranking key = `priority` (session, else driver), `group_serial`, `route_priority` (device route priority), `serial`.
- `:76-95 compare_nodes` — `a.priority ~= b.priority → a.priority > b.priority`; then `route_priority`; then serial.

`/usr/share/wireplumber/scripts/default-nodes/find-best-default-node.lua`:

- `:29-35` — "a node selected by an earlier hook carries no ranking of its own; the serials are set so that it keeps the selection whenever a candidate merely ties with it on the priority" (`group_serial = math.mininteger`, `serial = math.mininteger`) → the **tie keeps the incumbent** measured in §5.
- `:37-39` — skip if `selected.route_priority > 15000`.
- `:41-47` — `available-nodes` is the candidate set; `nutils.get_node_ranking` per node.

`/usr/share/wireplumber/scripts/default-nodes/state-default-nodes.lua` — the
persistence hook that writes `default.configured.audio.sink` (and the numbered
history keys) into `$XDG_STATE_HOME/wireplumber/default-nodes`.

`/usr/share/wireplumber/scripts/linking/find-media-role-sink-target.lua`:

- `:38-42` — bypasses unless `media_class == "Stream/Output/Audio"`, `node.virtual` is truthy **and** `node.link-group` is set (i.e. role-based *loopback* streams), and the target is not already set.
- `:52-60` — reads `policy.role-based.preferred-target` from the *input* node of the link group.
  → explains the measured null for `media.role=Communication` on a plain `pw-cat` stream (§6).

`/usr/share/wireplumber/scripts/linking/find-defined-target.lua`:

- `:9-10` — the two defined-target sources: `node.target`/`target.object` in the node properties, then `target.node`/`target.object` in the `default` metadata.
- `:38` — `local dont_fallback = cutils.parseBool (si_props ["node.dont-fallback"])`.
- `:45-51` — **`target.object` is looked up by `object.serial`; `node.target` by `node.id`** — this is why a numeric `pw-cat --target` behaves like a *serial* (measured in §6).
- `:120-133` — when a defined target is not found **and** `dont-fallback` is set: `lutils.sendClientError (event, node, -2, "defined target not found")` and, unless `node.linger` is set, `node:request_destroy ()` ("destroyed node as defined target was not found"); with `linger`, WP waits instead.
  → this is exactly the measured leg: stderr `stream node 49 error: defined target not found`, no link, stream node gone.

`/usr/share/wireplumber/scripts/linking/prepare-link.lua` and
`linking/find-default-target.lua` (`:31-56`) are the hooks that turn the picked
target into a link and that fall back to the default node when no target was
picked (`lutils.findDefaultLinkable`).

## 4. wpexec / Lua sandbox

| anchor | claim |
| --- | --- |
| [O] `strings -a /usr/lib/wireplumber-0.5/libwireplumber-module-lua-scripting.so` lines 1058, 1317, 1323 | `Could not locate script '%s'`, **`Lua runtime error`**, **`Failed to compile: %s`** all live in the scripting module |
| [O] `strings -a /usr/bin/wpexec` | `script/lua`, `libwireplumber-module-lua-scripting`, `script argument must be a JSON object`, `- WirePlumber script interpreter` → `wpexec` is a thin loader for that module |
| [O] `wp_conf_open` / `opening fragment file` in every run log | the private instance's fragment list is exactly the shipped `alsa-vm.conf` plus this seat's fragment |
| labrat fold (read-only child, §12) | `/usr/share/wireplumber/wireplumber.conf:282-297` is the explicit `WpSettings` binding step ("blocks and waits for the sm-settings metadata object"); 40 `Settings.get_*` call sites in 15+ shipped scripts show Settings *is* bound in the daemon; no shipped script binds it itself |
| [I] shipped scripts | globals injected host-side and used unguarded: `Plugin` (`lib/common-utils.lua:50,58,69`), `Json` (`sm-objects.lua:69`), `Conf` (`node/state-stream.lua:15`), `ImplMetadata` (`metadata.lua:20`), `Script` (`metadata.lua:9,23,26`), `LocalModule` (`sm-objects.lua:41`) |

## 5. pw-cli / spa-json grammar (measured the hard way)

| anchor | claim |
| --- | --- |
| [O] `scratch/pwcli_session.log:3` | `create-node adapter '{ factory.name=… }'` (shell-style outer quotes inside argv) → `syntax error in properties, line:1 col:16: Expected object key` |
| [O] same file | `audio.position=FL,FR` unquoted → `syntax error in properties, line:1 col:175: Expected object value`; omit the key or use `[ FL FR ]` |
| [O] `probes/r97lib.py:nullsink` | the working form is a bare `{ key=value … }` group with no outer quotes |
| [O] every pw-cli leg | `Error: "unsupported type PipeWire:Interface:SecurityContext"` — pw-cli noise on this host, unrelated to the command |
