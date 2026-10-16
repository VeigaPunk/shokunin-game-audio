# r97 AUTHOR — the WirePlumber policy lattice, encoded as `--probe-wppol-r97`

**Seat r97-author (executor).** Host `plazir27`, worktree
`audio-shokunin/audio-shokunin-wt-r97`, branch `wt-r97` @ **`5755be5b`**.
Window **2026-10-16 05:53Z–09:55Z** (4 h wall; ~40 min of it was
measurement, the rest dev iteration on the private-instance harness). Toolchain re-verified on this host: PipeWire
**1.6.8**, WirePlumber **0.5.17** (`libwireplumber 0.5.17`), Lua 5.5 sandbox,
Python 3.14.7.

**Zero commits.** The only tracked writes are the fixture and the pyc it
refreshes; everything else this seat wrote is untracked, under
`corpus/live/r97-author/` (plus this report).

**Scope discipline.** The r97 scout measured the WirePlumber 0.5.17
policy/scripting surface in a private instance; the r97 boundary re-armed it
under load and falsified two claims. This seat encodes **only the
boundary-surviving cells**, at the boundary's corrected values — nothing was
re-derived from the scout alone, and every cell the boundary marked "do not
assert" is dropped or carried as a recorded, unarmed observation.

---

## Files changed

| file | change |
|---|---|
| `corpus/fixtures/measure_audio.py` | **+2156/−3** (insertion-only): the r97 block inserted after `pwprof_xw_r89_entry()` / before `def main()` (lines 31091–33208) plus five wiring splices: the `--probe-wppol-r97` argument, the mutex list, the mode select, the receipt suffix, and the dispatch block. The three deleted lines are exactly those three shared-line rewrites (r86–r89 convention). |
| `reports/round-97/r97-author.md` | this report |
| `corpus/live/r97-author/` (untracked) | `battery-r97.sh`, `battery.log`, `battery-final{1,2}.log`, `fixture-sha256.txt`, `RECEIPTS.txt`, `receipts/` (copies of the canonical run receipts), `dev/` (the five per-entry dev receipts, the two micro-probes, `wppol_r97_block.py` — the block as authored before splicing) |
| `corpus/live/runs/<stamp>-wppol-r97/` (untracked) | the canonical battery receipts |
| `corpus/live/measure_audio-wppol-r97.lock` (untracked) | the fixed-path family lock, created at runtime |

`git diff --numstat corpus/fixtures/measure_audio.py` = `2156 3`; the
deletion set is exactly the mutex-list, mode-select and receipt-suffix lines.
`python3 -m py_compile` clean.

## Conventions carried over (r76–r89)

- **Namespace `r97a_<pid>`**: every node this seat creates is
  `r97a_{sa,sb,sc,…}_<pid>` / `r97a_str_<pid>`, matched by an explicit
  ownership predicate (`r97a_` prefix **and** this pid's suffix — the tag
  `r97a_<pid>` is *not* a substring of `r97a_sa_<pid>`, and a tag-substring
  filter silently matches nothing; that defect was caught in dev and fixed).
- **Private instance only.** Every daemon, client, stream and `wpctl` call
  runs with `PIPEWIRE_RUNTIME_DIR`/`XDG_RUNTIME_DIR` pointed at a private
  runtime dir under `$TMPDIR` (`TMPDIR=/home/vgpnk/Projects/shokunin/tmp`), a
  private `XDG_CONFIG_HOME`/`XDG_STATE_HOME`/`XDG_DATA_HOME`, and a private
  core conf that is a *copy* of the shipped `pipewire.conf` plus this seat's
  fragment. The private WirePlumber fragment disables every hardware monitor
  (`hardware.audio/bluetooth/video-capture = disabled`) so a second daemon
  never touches the operator's ALSA/bluez/v4l2 devices.
- **The forbidden surface is `pactl set-default-sink/source`** — never called,
  anywhere. `wpctl set-default`/`clear-default` *are* armed, but only ever
  with the private env, so they land in the private instance's metadata; the
  write-scope leg measures that directly (`s3`: the operator's value is
  unchanged while the private read-back flips).
- **Environ-aware teardown guard** (the boundary's §2.5 defect): a private
  `wireplumber -c wireplumber.conf -p main` carries **no seat path in its
  cmdline** — its identity lives in the environment. `_wppol_r97_own()` checks
  `/proc/<pid>/cmdline` **or** `/proc/<pid>/environ` for the private root and
  the kill **refuses** anything else; there is no namespace-blind sweep
  (`pkill` appears nowhere).
- **Bounded everything**: every external process runs in its own session with
  a wall cap and is killed by process group; the private pair is stopped by
  pid file with an 8 s graceful window before SIGKILL escalation.
- **Fixed-path family lock** `corpus/live/measure_audio-wppol-r97.lock` (the
  r84 F1 3-seat consensus — never `$TMPDIR`).
- **Volatile text is recorded, never armed**: ids, serials, nsec counters,
  wall times, byte counts, loadavg, foreign names, log text.
- **Named blocked classes, never silent greens**: an unreadable operator graph
  or a private pair that will not publish `sm-settings` becomes a
  `coverage_blocked` entry, never a pass; the two vacuity guards
  (`d12` flush-window, `l8` wait-face) are named the same way.

---

## Entries and legs

**Leg census: 69 top-level observation keys across 5 entries — arming 14 /
defaults 15 / linking 21 / wpexec 15 / settings 4.** The rule (so the receipt
can be recounted): the named context keys (`probe`, `contention`,
`oracle_at_start`, `foreign_r97a_nodes`, `inventory`, `loadavg`,
`private_root`, `conf_paths`, `starts`, `pair`, `wp_restarts`, `stops`,
`purge_before`, `own_procs_after`, `shared_census`, `coverage_blocked`,
`failures`, `blocked`, `unloads`, `residual_destroy`) are not counted; the
custody sub-records that carry an observation each (`a1_core`, `a2_stop_wp`,
`d9_lag_s`, `l7_node_gone`, `w14_wp_stop`, `own_nodes_before_teardown`,
`setup`) are. The first draft's "63 legs" headline was arithmetic drift; the
receipt keys are the record (r89-fold convention) and the family header now
carries the corrected census.

### 1. `wppol_arming_r97_probe` — how a private WirePlumber gets its config (14 legs)

- `a1_pair_up`: private core answers, private WirePlumber publishes the
  `sm-settings` metadata object (the readiness gate; the pair is re-armed per
  entry and gated on it).
- `a2_status_wp_down`: **`wpctl status` is not a WirePlumber readiness gate** —
  with the private WirePlumber killed (guarded) and `sm-settings` verified
  gone, `wpctl status` still exits **0** and prints a well-formed but empty
  listing. Armed: rc 0, `sm-settings` absent, no own rows.
- `a3_conf_dir_missing` (**the boundary's correction**): `WIREPLUMBER_CONFIG_DIR`
  at a dir with no `wireplumber.conf` ⇒ **rc 78**, log carries
  `Failed to load configuration: Could not locate configuration file
  'wireplumber.conf'`, **no fragments opened**, and the scout's chain
  (`no modules loaded from context.modules`, `can't find protocol
  'PipeWire:Protocol:Native'`) is asserted **absent** from this shape.
- `a4_conf_dir_replaces`: with a dir holding a copy of the conf + its own
  fragment dir, the log opens `<copy>/wireplumber.conf` and the copy's
  fragments, and the shipped `/usr/share/wireplumber/wireplumber.conf.d` is
  never read — the override **replaces** the search path.
- `a5_xdg_config_adds`: the working shape opens the shipped `alsa-vm.conf`
  **and** this seat's `XDG_CONFIG_HOME` fragment.
- `a6_home_config_read`: with `XDG_CONFIG_HOME` unset, the user config dir
  resolves from `$HOME/.config` (armed through a **shim HOME** carrying a
  hardware-disabling fragment, so the operator's real
  `~/.config/wireplumber` is never read — the boundary's V4 leak law, re-armed
  safely; the leg asserts both the shim fragment being opened and the absence
  of the operator's path).
- `a7_data_dir_replaces`: `WIREPLUMBER_DATA_DIR` replaces the **script** search
  path too — rc 78, `Could not locate script 'sm-objects.lua'`, both fragments
  already opened.
- `a8_core_no_modules` / `a9_wp_on_modules_less_core` (**the home of the scout's
  text**): a core whose conf has no `context.modules` warns
  `no modules loaded from context.modules` and **keeps running** (no socket —
  there is no protocol module); a real `wireplumber -c wireplumber.conf -p
  main` on that core exits **69** with `Failed to connect to PipeWire`, and the
  middle chain mark is asserted absent.
- `a10_access_off` / `a11_access_on`: a private core with `module.access=false`
  listens (socket present) and **never answers** — `pw-dump` and `pw-cli ls
  Client` are both killed at the cap with 0 bytes; with access untouched the
  same `pw-cli` answers rc 0 with a `PipeWire:Interface:Client` object.
- `a12_shared_untouched`: read-only census of the operator's graph — zero
  `r97a` objects, with the shared daemons recorded as context (an unreadable
  graph is a named blocked class).

### 2. `wppol_defaults_r97_probe` — default-node policy (15 legs)

- `d1` first sink wins; `d2` strictly higher `priority.session` takes over;
  `d3` lower does not.
- `d4`/`d5` a **tie keeps the incumbent**, both creation orders (equal
  `priority.session`, different `priority.driver`).
- `d6` a node with no priority keys does not displace.
- `d7`/`d8` **`priority.driver` is the fallback rank compared across nodes**:
  a driver-only `999` takes the default from a `session=100` incumbent **and
  keeps it** against a `session=200` newcomer.
- `d9` an explicit `wpctl set-default` outranks every later priority, writes
  **both** `default.audio.sink` and `default.configured.audio.sink`, and the
  state file gains `[default-nodes]\ndefault.configured.audio.sink=<sink>`
  (armed with an explicit wait; the lag is recorded, `d9_lag_s`).
- `d10` `clear-default` hands the default to the best available; `d11`
  destroying the default falls back to the best remaining.
- `d12`/`d13` **the boundary's ~1 s restart race**: a restart before the state
  file flushes loses the configured choice and leaves **no** configured row
  (`d12`, SIGKILL restart, armed only when the pre-restart state file is
  verified unflushed — a flushed window is a named vacuous class, never a
  false red); after the row appears the choice survives (`d13`).
- `own_nodes_before_teardown`: the custody census (own sinks only).

### 3. `wppol_linking_r97_probe` — target addressing and the failure envelope (21 legs)

Two seat sinks, A (`priority.session=100`) and B (`500`, so B is the default);
every stream is `pw-cat -p --raw --rate 48000 --channels 1 --format s16
-P node.name=r97a_str_<pid> -` with stdin held open and killed by group.

- `l1` no target → default B; `l2` `--target 0` → **0 links**.
- `l3` `--target <A object.serial>` → A; `l4` `--target <A global id>` →
  **default B, rc 0, empty stderr** (the silent fallback); `l5`
  `--target <node.name>` → A; `l6` `--target 99999` → default B, rc 0, empty
  stderr. The bogus number is guarded against collision with any live id/serial
  before the leg runs.
- `l7` `node.dont-fallback=true` + bogus target → 0 links, stderr carries
  `defined target not found` and `res:-2 (No such file or directory)`, and the
  stream node is **gone** (`l7_node_gone` polls the dump).
- `l8` `+ node.linger=true` → 0 links, empty stderr, **node present** and the
  process still waiting at the cap (the third face of the envelope).
- `l9`–`l12` the two property namespaces: `target.object=<serial>` → A,
  `target.object=<id>` → B, `node.target=<id>` → A, `node.target=<serial>` → B.
- `l13`–`l16` the flag-order matrix (`--target` early, `--target=`, after the
  input argument, between the props) — all → A: argv order is not the
  variable, the **namespace of the number** is.
- `l17` `media.role=Communication` with no target → default B (no role target
  for a plain stream).
- `l18` **recorded, deliberately unarmed** (boundary §8): with
  `linking.follow-default-target` written `false` and verified by read-back
  **and** by the `sm-settings` metadata row, a live stream still moves to the
  new default (`links_before` → B, `links_after` → A). The armed cells are the
  read-back and the metadata row only; the movement is recorded for the next
  round, exactly as the boundary directed.

### 4. `wppol_wpexec_r97_probe` — the sandbox, closed from both sides (15 legs)

Lua legs are generated into the private scratch dir; the private env for this
entry strips the daemon log levels so stderr stays a byte-armed observable.

- `w1_inventory`: the FOUND / MISSING / ENV lines are armed **byte-equal** to
  the scout's receipt (39 present / 26 absent, same order; `_G` nil, `_ENV`
  table, Lua 5.5, `debug.getregistry` present) — the boundary's byte-for-byte
  cross-witness.
- `w2_compile_error_located`: rc 70 and
  `Failed to compile: [string "w_syntax.lua"]:1: …`.
- `w3`–`w6` four runtime-error shapes (`error()`, nested `error(…,2)`, nil
  index, `pairs(_G)`) → rc 70 with stderr **exactly** `Lua runtime error`.
- `w7_no_quit`: no `Core.quit()` → killed at the 6 s cap, rc −9, its `print`
  flushed.
- `w8_no_argument` → rc 70 `Could not locate script '(null)'`; `w9_missing_file`
  → rc 70 naming the path.
- `w10_positional_argument` → rc 64 `script argument must be a JSON object`;
  `w11_json_argument` → rc 0 and the JSON argument is **invisible** to the
  script (`arg=nil n=1`); `w12_help` → rc 0.
- `w13_settings_unbound`: six keys read `false/0.0/""` before and after a
  write verified by read-back, byte-identical across the two runs.
- `w14_sandbox_without_daemon`: with the private WirePlumber stopped
  (`sm-settings` verified absent) the inventory is byte-identical and
  `Settings` is still inert — the sandbox and the binding failure are both
  independent of a policy daemon.

### 5. `wppol_settings_r97_probe` — the 25-key lattice (4 legs)

- `s1_lattice`: `wpctl settings` rc 0, exactly 25 keys, and the key **set**
  equal to the boundary's 25-name lattice; the listing sha256 is recorded and
  is **`56526540bdc17f52…`** — byte-identical to the boundary's receipt.
- `s2_metadata_faces`: the private graph publishes `sm-settings` (25 rows) and
  `schema-sm-settings` (25 rows) — the WirePlumber-up witness — with the core's
  own `settings` face (8 rows) recorded as context.
- `s3_write_scope`: the private write reads back in the private instance while
  the operator's value for the same key is unchanged (read-only cross-check).
- `s4_shared_lattice`: the operator's instance lists the **same 25-name key
  set** and the same listing sha256 — the lattice is install-scoped, not
  instance-scoped. An unreadable operator instance is a named blocked class.

---

## Boundary corrections actually encoded (and the claims dropped)

| scout claim | what this family arms instead |
|---|---|
| V1's three-message chain (`no modules loaded` → `can't find protocol` → `Failed to connect`) | rc **78** + `Could not locate configuration file 'wireplumber.conf'`, chain asserted **absent**; the chain's real home (a modules-less core, rc **69**) is armed separately as `a8`/`a9` |
| "`WIREPLUMBER_*_DIR` searched first" (man page) | **replacement** semantics for both CONFIG_DIR (`a4`) and DATA_DIR (`a7`) |
| "the configured default survives a restart" (unconditional) | armed **only** with the flush state: unflushed ⇒ lost + no configured row (`d12`, vacuity-guarded), flushed ⇒ survives (`d13`) |
| "`priority.driver` is a tie-breaker" | it is the **fallback rank compared across nodes** (`d7`, `d8`) |
| "a numeric `--target` is a global id" | it is an `object.serial`; a global id **misses silently** into the default (`l3`, `l4`) |
| "a bogus target is an error" | silent fallback rc 0 (`l6`); the error face needs `dont-fallback` (`l7`), and `linger` is the third face (`l8`) |
| "`media.role` picks a role sink" | falsified for plain streams (`l17` — no role target) |
| "`wpctl status` proves WirePlumber is up" | it is **not** a gate (`a2`); the `sm-settings` object is (`a1`, `s2`) |
| "the private instance is isolated" | armed as a shape, not a claim: private `XDG_CONFIG_HOME` adds, `$HOME/.config` leaks when unset (`a6`), `WIREPLUMBER_*_DIR` replaces |
| "`wpexec`'s API namespace is unknown / `Settings` is broken" | the surface is a closed list (`w1`) and `Settings` is **unbound in `wpexec`** (`w13`, `w14`) — daemon-independent |

**Deliberately NOT armed** (boundary §8): `linking.follow-default-target` and
`linking.allow-moving-streams` as behavioural gates (both inert 3/3 in the
plain-`pw-cat` shape — recorded only, `l18`); any latency claim below one
`pw-dump` round trip; the `wpexec` JSON argument as reachable from the script
(armed as *invisible*, which is what was measured); the WP-side
`waiting for defined target` log line from client stderr.

---

## Evidence

- **Final fixture sha256**
  `f0eb6c509ecc20bff8a4652ec09e2ddf6607153fc01fbe150e679aee54b7d50e`
  (34 522 lines; `+2156/−3`).
- **Final battery (twice, on the frozen bytes)** — `battery-final1` /
  `battery-final2`, launched under `nohup` with
  `TMPDIR=/home/vgpnk/Projects/shokunin/tmp` and `PYTHONDONTWRITEBYTECODE=1`:
  - `corpus/live/runs/20261016T094737705611Z-wppol-r97/measurements.json`
    (run 1, exit 0, loadavg 13.07 → 8.63) — `failures: {}`, **no blocked
    classes**, 69 leg keys (14/15/21/15/4);
  - `corpus/live/runs/20261016T095258906395Z-wppol-r97/measurements.json`
    (run 2, exit 0) — `failures: {}`, no blocked classes, same 69 leg keys.
  - Copies of both under `corpus/live/r97-author/receipts/`; shas in
    `corpus/live/r97-author/RECEIPTS.txt`. Each receipt also carries the
    fixture's 17 pre-existing base entries (14 legs each, `failures: {}` in
    both runs) — the r97 family adds 5 entries on top of them, and the base
    rows are untouched by this seat.
- **Pre-freeze smoke battery** (same code, before the comment-only census
  header correction; disclosed, not the evidence of record):
  `…T093309501241Z-wppol-r97` and `…T093830854971Z-wppol-r97` — both
  `failures: {}` with no blocked classes, kept so the difference between the
  pre- and post-correction bytes is auditable.
- **Custody, every entry, both runs**: `own_procs_after: []`,
  `shared_census.own_hits: []`, `sinks_gone` n/a (no pactl sinks are used — the
  private graph's nodes are destroyed by id via `pw-cli destroy` and the
  residual census is armed), and the operator's graph carries **0** `r97a`
  objects. No `pactl` call of any kind is made by this family.
- **Safety witnesses measured live**: `s3` (private write, operator's value
  unchanged), `a6` (the operator's real config dir is never read), `a12` +
  teardown (0 own objects in the operator's graph).

### Labrat fold (frozen `probeParent` — exactly one child, read-only, advisory)

One `ufo-labrat` was dispatched with a single falsifiable hypothesis: the
mechanisms behind four armed cells are present verbatim in the **installed**
0.5.17 scripts. It returned **CONFIRMED** on all four, with line numbers, and
**no contradiction** with any measured cell:

- `linking/find-defined-target.lua:45-53` — `target.object` → `object.serial`,
  `node.target` → `node.id` (the two namespaces); `:116-127` — `dont_fallback`
  ⇒ `sendClientError(…, -2, "defined target not found")` then
  `node:request_destroy()`, else the `node.linger` "waiting for defined target"
  branch.
- `lib/node-utils.lua:12-17` — rank = `priority.session`, else
  `priority.driver`, else 0; `compare_nodes:88-98` — serial tie-break.
- `default-nodes/find-best-default-node.lua:30-35` — the incumbent gets
  `group_serial`/`serial = math.mininteger` (a superset of the hypothesis).
- `default-nodes/state-default-nodes.lua:67-81,143-177` — a
  `metadata-changed` hook on `default.configured.audio.sink` writes the state
  file via **`state:save_after_timeout(state_table)`**, with the `.0`/`.1`
  history stack — i.e. a *deferred* save, consistent with the ~1 s lag, but
  **the timeout value itself is C-side and could not be verified from the
  installed Lua** (recorded as a partial, not as a confirmation).

The child created no artifacts and ran no daemon.

---

## Contention ledger and host conditions

| window | contact | effect |
|---|---|---|
| whole window | foreign load 4–60 (1-min avg) on 32 cores; foreign seats live (r90/r91/r93/r94/r95/r96/r98/r99 class of lanes, read-only `ps` census) | the host was never uniformly quiet; the final battery ran at loadavg ≈ 12–16 |
| whole window | this seat: private core + private WirePlumber + bounded clients per entry, each entry re-armed and torn down; scratch under `$TMPDIR/wppol-r97-<pid>-*` | own objects only; every kill by own pid + cmdline/environ guard |
| ~06:24Z | **the operator's shared PipeWire/WirePlumber were restarted by a foreign actor** (`/usr/bin/pipewire` start time `06:24:34`, the earlier census showed the boot-time pids 2060/2063/2694) | **not this seat**: no lane of this seat signals, restarts or reconfigures the shared daemons, and the kill guard refuses any pid that does not name this seat's private root; the only shared-env commands are read-only (`pw-dump`, `wpctl settings <key>`, `ps`) |
| intermittent | the operator's graph was unreadable (`pw-dump` > 25 s) in three dev windows and readable (10–30 ms, 137–155 objects) in others | the shared census is a best-effort cross-witness with a **named blocked class** when unreadable; the final battery's two runs both read it |
| whole window | the operator's `~/.local/state/wireplumber/*` was never written by this seat (no `settings` file exists for WirePlumber 0.5; the private instance writes its own `stream-properties`/`default-nodes` under its private `XDG_STATE_HOME`) | verified by the private state dir contents and by `s3` |

**Disclosures.** The tracked
`corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` was already `M` at
seat entry (the round's other seats left it dirty); the `py_compile` checks
this seat ran refreshed it again — it stays dirty with different bytes and no
other tracked file was touched. The two pre-freeze smoke receipts and the five
per-entry dev receipts are kept rather than deleted, so the difference between
"measured in dev" and "measured on the frozen bytes" is auditable. The private
instance roots (`$TMPDIR/wppol-r97-<pid>-*`, 36 dirs / 13 MB across the whole
window) are kept in place: they hold the per-entry core/WirePlumber/pw-cli logs
behind the receipts, they contain no live process (`own_procs_after: []` in
every entry) and nothing in them is armed. The `shared_daemons` list inside the
custody census is best-effort `ps` context — it came back empty in the final
runs while the shared graph itself read fine (100–155 objects), and it is not an
armed cell.

## Remaining risks / blockers

1. **None blocking.** Both final battery runs are `failures: {}` with no
   blocked classes, and every armed cell is a boundary-surviving claim.
2. **The ~1 s flush window is a *state*, not a constant.** `d12` arms the
   unflushed case and refuses to red when the window was missed (observed
   restart latencies 1.3 s with the file still empty, and the flush itself at
   1.003 s in `d13`) — a later host could flush faster and turn `d12` into a
   named vacuous class. That is the honest shape, not a weakening.
3. **`l18`'s inertness is recorded, not armed** — the path that moves a stream
   on a default change is still unidentified in 0.5.17 (the scout's `[?]`2,
   unchanged).
4. **The `wpctl status` non-gate** is measured with WirePlumber *down* on a
   private pair; whether the same empty-listing shape appears for a
   half-initialised daemon was not tested.
5. **The shared instance's own behaviour** (settings writes, default changes)
   was never exercised — only read (`s3`, `s4`, `a12`); the two cross-witnesses
   are the operator's lattice read and the private write-scope check.
6. **A wedged private core** (the scout/boundary `[?]`) did not occur in this
   seat's window; the entries gate on `sm-settings` and would block rather than
   mis-red, but the wedge itself remains unexplained.
7. No resume mutation attempted; no commit, no push — the orchestrator commits.

Seat stop. Files changed by THIS seat: `corpus/fixtures/measure_audio.py`
(+2156/−3), `reports/round-97/r97-author.md`, and the untracked live evidence
under `corpus/live/r97-author/` + `corpus/live/runs/*-wppol-r97/`. The canonical
Rust runtime remains the sole judge.
