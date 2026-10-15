# r97-scout receipts index — WirePlumber 0.5.17 policy/scripting surface

Host plazir27, 2026-10-15 17:06–17:26Z. HEAD `1abd954`. All receipts are untracked,
written by this seat's own bounded driver (`probes/*.py`, own env, own process
groups; no import of `corpus/fixtures/measure_audio.py`). `manifest.sha256` pins
every file; `summary.json` is a compact extraction of all of them.

The measurements ran against a **private PipeWire core + private WirePlumber**
(`PIPEWIRE_RUNTIME_DIR`/`XDG_RUNTIME_DIR`/`XDG_CONFIG_HOME`/`XDG_STATE_HOME` all
inside this seat dir). The shared WirePlumber (pid 2063) was never signalled,
restarted or reconfigured; no seat object ever appeared in the shared graph.

| receipt | stage | legs / reps | what it pins |
| --- | --- | --- | --- |
| `a_arming.json` | arming | 5 variants × 3 reps | `WIREPLUMBER_CONFIG_DIR` and `WIREPLUMBER_DATA_DIR` **replace** the search path (rc 78 EX_CONFIG, two different failure texts); private `XDG_CONFIG_HOME` adds a fragment dir while the shipped one stays; the operator's user fragment is only loaded when XDG_CONFIG_HOME is not overridden |
| `b_wpexec.json` | wpexec | 11 legs × 3 reps | the sandbox global inventory (37 present / 30 absent), `_G` = nil with `_ENV` present, `io`/`load`/`dofile`/`require_api`/`rawget`/`unpack` absent, `debug` present; every runtime error → rc 70 + bare `Lua runtime error`; compile error carries a location; no `Core.quit()` → hangs to the cap; `Settings.get_*` returns false/0.0/"" regardless of the live value (wpctl toggle verified) |
| `c_default_nodes.json` | default-nodes | 10 steps × 3 reps | first sink becomes default; strictly higher `priority.session` takes over; lower does not; explicit `set-default` survives a higher-priority newcomer; `clear-default` picks the best; removing the default falls back; equal session priority keeps the incumbent |
| `c2_default_controls.json` | default-nodes | 4 steps × 3 reps | driver-priority control with reversed creation order (incumbent keeps); a sink with **no** `priority.session` loses to one with 100; `set-default` writes both `default.audio.sink` and `default.configured.audio.sink`; the configured row survives with no sinks; the state file content |
| `c3_restart.json` | default-nodes | 6 steps × 3 reps | configured default (low priority) beats the highest-priority sink **across a private WirePlumber restart**; the state file gains `default.configured.audio.sink.0=<previous>` |
| `d_linking.json` | linking | 10 legs × 3 reps | `--target 0` = no link; auto → default sink; **global id silently falls back to the default**; `object.serial` and `node.name` resolve; bogus target falls back; bogus target + `node.dont-fallback` → no link + client error + node destroyed; `media.role` has no effect on a plain stream; `follow-default-target` behaviour |
| `e_residuals.json` | residuals | 2 cells × 3 reps | `priority.driver` **is** the fallback when `priority.session` is absent (999 beats an incumbent's 100); `follow-default-target=false` verified set, stream still moved |
| `f_target_property.json` | target property | 2 legs × 3 reps | the property `pw-cat --target <n>` writes is **`target.object = <n>`** (plus `node.autoconnect = true`), for both a serial and a global id — the *resolution* difference is pinned by `d_linking.json` (two sinks) |
| `summary.json` | — | extraction | compact machine-readable roll-up of all of the above |

Raw runs: `runs/core.log`, `runs/wp.log`, `runs/a_arming.out`,
`runs/a_v5_full.log`, `runs/a_v6{,b,c,d}_*.log` (fragment/profile/component
probes), `runs/b_wpexec.out`, `runs/c_default.out`, `runs/c2.out`, `runs/c3.out`,
`runs/d_linking.out`, `runs/e_residuals.out`, `runs/f_target_prop.out`,
`runs/pwcli_debug.log`,
`runs/api_probe.txt`.

Probes: `probes/r97lib.py` (bounded runner, private env, `PwCli` session,
pw-dump helpers, `ensure_up`), `probes/up.sh` / `probes/down.sh` (target-aware
private pair), `probes/a_arming.py`, `probes/b_wpexec.py`, `probes/c_default.py`,
`probes/c2_default2.py`, `probes/c3_restart.py`, `probes/d_linking.py`,
`probes/e_residuals.py`, `probes/f_target_prop.py`, `probes/build_manifest.py`.

Configs under test: `conf/pw/r97s-pipewire.conf` (+ `.d/10-r97s.conf`),
`conf/xdg-config/wireplumber/wireplumber.conf.d/10-r97s.conf` (the working
private fragment), `conf/xdg-config-probe/...` (the component-add probe),
`conf/wp-copy/`, `conf/wp-empty/`, `conf/wpdata/`, `conf/xdg-data/`.

Scratch: `scratch/t.lua`, `scratch/api.lua`, `scratch/globals.lua`,
`scratch/set_probe.lua`, `scratch/b_*.lua`, `scratch/settings_list.txt`,
`scratch/pwcli_*.log`.

Sources: `sources/ANCHORS.md` (every mechanism anchor with file:line or
`strings` offset, [O]/[I] labelled).

Exit state (17:26Z): private core + private WirePlumber stopped, 0 seat
processes, 0 `r97s` objects in the shared graph (`pw-dump`), 0 `r97s` rows in
the shared `~/.local/state/wireplumber/stream-properties`; shared daemons
(2060/2063/2694) untouched and still up. The private state dir holds this
seat's own 48 `stream-properties` rows and a 0-byte `default-nodes` (last
instance had no configured default).
