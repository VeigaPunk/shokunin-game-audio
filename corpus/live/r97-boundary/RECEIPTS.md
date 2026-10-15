# r97-boundary receipts index — WirePlumber 0.5.17 policy laws re-armed under load

Seat: BOUNDARY, host `plazir27`, 2026-10-15 20:50Z–21:5xZ, HEAD `51a98e54`.
All receipts are untracked and written by this seat's own bounded driver
(`probes/*.py`, own env, own process groups, own pid files). `manifest.sha256`
pins every file.

**Arms.** `*.ambient.json` = no seat-added load (the host still carried 48–96
foreign `yes` hogs — the "quiet" arm is ambient, not quiet). `*.hogs.json` = the
same stage with 12 of this seat's own `r97b_hog` processes (`run/hogs.pid`, killed
by that list only). `<name>.json` always holds the newest arm.

| receipt | stage | what it pins |
| --- | --- | --- |
| `a_arming.{arm}.json` | arming | V1 `WIREPLUMBER_CONFIG_DIR` without a conf ⇒ **rc 78** with `Could not locate configuration file 'wireplumber.conf'` (the scout's `no modules loaded` chain does **not** appear; the scout's own V1 leg has an empty matching-line list); V2 replacement (only the copy's fragment); V3 shipped + own fragment; V4 operator fragment; V5 rc 78 `sm-objects.lua` after both fragments open; V6 empty-conf variant |
| `a2_core_no_modules.{arm}.json` | attribution | L1 a core config without `context.modules` ⇒ `no modules loaded from context.modules` (warning, core runs on); L2 a real `wireplumber` client on that core ⇒ `Failed to connect to PipeWire`, **rc 69** — the home of the scout's chain, and not rc 78 |
| `b_access.{arm}.json` | core access | `module.access=false` ⇒ socket present, every client leg killed at the 8 s cap with 0 B; rt/profiler/portal-only and no-fragment cells answer in 0.007–0.017 s |
| `c_defaults.{arm}.json` | default-node cells | c1 first-sink-wins, c2 higher `priority.session` takes over, c3 lower does not, c4 explicit `set-default` (both metadata rows + state-file body + lag), c5 highest-priority newcomer does not steal, c6 `clear-default` → best, c7 removing the default → best remaining, c8a/c8b tie keeps incumbent in both creation orders, c9/c10 (invalid in the first pass: empty priority values are a spa-json parse error and the node is never created — see `c4_priority`) |
| `c4_priority.{arm}.json` | priority fallback | n1 a node with no priority keys does not displace a 100; n2 a `driver=999`-only node takes the default from `session=100`; n3 that driver-only node **keeps** the default against a `session=200` newcomer |
| `c3_restart_race.{arm}.json` | restart race | restart **immediately** (0.042–0.058 s) and at **0.5 s** after `set-default` ⇒ configured default **lost** (3/3); restart **after the state file row appears** (0.965–1.011 s) ⇒ survives (3/3); the lag is a repeatable ≈1.00 s |
| `d_linking.{arm}.json` | linking | `--target 0`; auto → default; global id → default (silent); serial → requested; name → requested; 99999 → default rc 0; `dont-fallback` → 0 links + `-2 defined target not found` + node destroyed; `linger` → 0 links, node stays, silent; 4 `--target` placements + equals form; `target.object` vs `node.target` id/serial matrix; 44100 stream; `follow-default-target=false` and `allow-moving-streams=false` both inert |
| `e_wpexec.{arm}.json` | wpexec | inventory byte-identical to the scout (39 present / 26 absent); `_G` nil / `_ENV` table / Lua 5.5; four runtime-error shapes rc 70 + bare `Lua runtime error`; syntax rc 70 + location; no `Core.quit()` → killed at the 6 s cap; no-arg and missing-file rc 70; `Settings.get_*` inert across a verified `wpctl settings` write; JSON-argument form (rc 64 on a non-JSON arg; the JSON arg is not exposed to the script); `--help` rc 0; the same legs with WirePlumber **down**, where `wpctl status` still exits 0 (not a WP gate) |
| `f_settings.{arm}.json` | settings lattice | `wpctl settings` ⇒ 25 keys, 4745 B, sha256 `56526540…`, identical across 3 fresh processes **and** to the operator's shared instance read read-only; metadata faces `settings` (8) / `schema-sm-settings` (25) / `sm-settings` (25) / `default` (1) |
| `g_sibling_exit.{arm}.json` | sibling + exit | a second private pair of this seat armed simultaneously: each pair sees only its own sink, neither reaches the shared graph, both pass the `sm-settings` gate; then the exit census (own pid files, own process count, shared-graph `r97b` count, shared daemon pids/start times, shared state-file fingerprints) |
| `h_clock.json` | clock/quantum axis | core re-armed at `rate=44100 quantum=64` (live `default.clock.*` read back), then first-sink-wins / takeover / explicit-survives / serial target / id fallback / dont-fallback / 44100 stream replayed |
| `w_wedge.json` | wedge trigger search | W1 dump storm, W2 sink churn, W3 set-default churn, W4 WP-restart churn (15 steps each) and W5 a 400-leg rapid connection storm: **no wedge**; every leg 0.016 s |
| `wedge_forensics.json` + `wedge_ledger.jsonl` | wedge forensics | the live wedged state (bounded `pw-dump`/`pw-cli`/`wpctl` all killed at their caps with 0 B; core threads R→S in `do_epoll_wait`, 0 CPU, 27 fds; WP threads all parked), the recovery procedure (re-arm only), and the shared session answering in 75 ms while the private core was wedged |
| `exit_census.json` | exit | private pair stopped by pid file, 0 pid files left, 0 own seat processes, shared graph 121 objects with **0 `r97b` hits**, shared daemons 2060/2063/2694 alive with boot-time start times, shared state-file fingerprints (0 `r97b` rows) |
| `*.ambient.json` | arm copies | every receipt is written twice: `<name>.json` (newest arm) and `<name>.<arm>.json` (per-arm pin) |

Raw runs: `runs/` (`c_ambient*.log`, `c_cells2.log`, `c3r.log`, `c4.log`, `d.log`,
`e.log`, `f*.log`, `g*.log`, `w_ambient*.log`, `*_hogs.log`, `core.log`,
`wp.log`).

Probes: `probes/r97blib.py` (bounded runner, private env, `PwCli(env=…)`,
wedge-aware `dump`/`health`/`health_or_rearm`, `wp_ready` gate on the
`sm-settings` metadata object, `stage_write` with per-arm copies), `up.sh`,
`down.sh` (cmdline **or** environ namespace guard), `hogs.sh`, the stage probes
listed above, `analyze.py`, `build_manifest.py`.

Configs under test: `conf/pw/r97b-pipewire.conf` (+ `.d/10-r97b.conf`,
`.d/20-r97b-clock.conf` during stage H), `conf/xdg-config/wireplumber/
wireplumber.conf.d/10-r97b.conf`, `conf/wp-empty/`, `conf/wp-copy/`,
`conf/wp-stub/`, `conf/wpdata/`, `conf/pw/r97b-cell-*/` (access cells),
`conf/pw-sibling/` (sibling pair).

**Harness defects found and fixed in-window** (disclosed in the report §2.4/§2.5):
`wpctl status` is not a WirePlumber readiness gate; the namespace guard must read
`/proc/<pid>/environ`; `PwCli` must take an explicit env (the first sibling test
was vacuous without it); `SHARED_ENV` must keep the operator's `XDG_RUNTIME_DIR`
(the first shared census read 0 objects).

**Collision disclosed**: two background chains of this seat ran concurrently for
~1 minute (21:31Z); the duplicate was killed, and its one `health_fail` ledger
entry (rc 255 in 9 ms) is a missing-socket artifact of that collision, **not** a
wedge. Ambient receipts were preserved as `*.ambient.json` before the hogs arm
overwrote `<name>.json`.
