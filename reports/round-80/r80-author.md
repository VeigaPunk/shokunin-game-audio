# R80 AUTHOR (audio) — the `pactl load-module` lattice + topology lifecycle, armed and run

Round 80. Repo `~/Projects/shokunin/audio-shokunin` @ HEAD
`ee6d6847cf27f9fd2c9dd784ada25468ef0a1426` (`r79 LOG: ADMIT-corr`). Host
`plazir27`. Toolchain: PipeWire **1.6.8** (pactl / pw-cli / pw-dump /
pw-link / pw-cat / pw-record all 1.6.8), libpulse **17.0** (pactl
17.0-98-gb096, protocol 35), WirePlumber **0.5.17**, Python **3.14.7**
(numpy 2.5.3), Linux **7.2.3-arch1-3**.

**Seat: AUTHOR. Tracked edits: exactly one file —
`corpus/fixtures/measure_audio.py` (+905 / −3, sha256
`3b69541f684c0cf4…`).** The three rewritten lines are the prepend-only
wiring every prior round used: the one-mode exclusivity sum, the `mode`
ternary, the `suffix` ternary — every earlier flag's value is unchanged.
Receipts: `corpus/live/runs/20261015T134301846760Z-module-r80/` and
`…T134359918834Z-module-r80/` (both `failures: {}`, exit 0, 10 r80 legs
across 2 entries), copied to `corpus/live/r80-author/` with sha256s.
**No commit — the tree is left dirty by design.**

---

## 0. Scope — a tight cut of the scout surface

The r80 scout measured a wide surface (the whole module family, the index
LIFO law, the unload argument matrix, the native/pulse namespace split,
hot-unload lifecycle, wpctl). This arm takes a **tight, measured scope**:
two entries, **10 legs**, covering the six sharpest candidates from the
scout's headline — all re-verified on this host during authoring.

- `module_args_lattice_r80_probe` (5 legs): which `pactl load-module
  module-null-sink` arguments reach `node.description`/derived props and
  which land only as literal passthrough props; the linger orphan
  lifecycle.
- `module_topology_r80_probe` (5 legs): the `@DEFAULT_SINK@` slave-list
  refusal, `pw-link` linger vs `-m` authority, and `pactl
  move-sink-input` sticky vs the `node.dont-move` silent no-op — the
  last two with **content witnesses** (monitor taps on the destination /
  retained sink).

Deliberately NOT armed this round: the index-allocation LIFO law
(host-global, timing-sensitive — a fleet lane's own loads perturb it),
the by-name unload row (the scout's §10 incident — **dangerous on a
shared host**, banned by convention), the namespace split and
`module-pipe-sink` FIFO, and the §4.2 re-link transient (the scout
itself marks it unattributed; a dedicated-sink 10 ms re-measure is its
own round).

## 1. Declared move

`--probe-module-r80`: two entries, **10 legs**, over the surfaces above.
Conventions inherited live: pid-stamped names (`r80md_<pid>_*`), unload
by the captured module index **only** (never a name — the scout's own
incident is the reason), spawn-time metadata+pactl oracle, port-presence
and edge gates before any leg asserts, `coverage_blocked` naming,
teardown that verifies `sinks_gone` **and** sweeps any `r80md_` orphan
through `pw-cli destroy` by node id. **Two consecutive formal runs**
(13:43:01Z, 13:43:59Z) on byte-identical frozen code: `failures: {}`,
exit 0, empty stderr, `own_nodes_after: []` in both entries, every
verdict flag identical run-to-run.

## 2. Headline — the ten legs

| leg | arm | expected | measured (run 2 verbatim) |
| --- | --- | --- | --- |
| a1_desc_dropped | `sink_name=<n> description=<d>` | rc=0, `node.description` is the **derived** string; `d` lands only as a plain `description` prop | `r80md_…_a1 Audio/Sink sink`; `pulse.module.id` == returned index |
| a2_desc_prop_wins | `sink_properties=device.description=<d>` | rc=0, `node.description` == `d` | `r80md_desc_736128_marker` — the prop wins |
| a3_rate_no_check | `rate=99999` | rc=0, verbatim in `EnumFormat` | `enum_rates: [99999]` — **no range check** |
| a4_source_class | `media.class=Audio/Source` | class change, 0 in ports, source `<n>`, no sink / no `.monitor` | `Audio/Source`, n_in=0 / n_out=1, sinks: absent, sources: `<n>` listed, `.monitor` absent |
| a5_linger_orphan | `object.linger=true` → unload → orphan | survives unload, stale pmid, pactl-unreachable, `pw-cli destroy` only | `client.id` absent; unload rc=0 → node still found, still a pactl sink **and** `.monitor`, pmid stale `536870931`; re-unload **rc=1 `No such entity`**; `pw-cli destroy 227` → gone |
| t1_combine_default_refused | `module-combine-sink … slaves=@DEFAULT_SINK@` / `sinks=@DEFAULT_SINK@` | both rc=1 `Failure: Input/Output error`, no node, module count unmoved | both attempts rc=1 / `pa_io_error`; `node_created: false`, `branch_nodes: []`, count 49→49 |
| t2_pwlink_lingers | `pw-link <a>:monitor_FL <b>:playback_FL` | link persists after the (exited) creator | edge present immediately and still at **+2.0 s**; explicit `pw-link -d` teardown rc=0 |
| t3_pwlink_m_dies | `pw-link -m <a>:monitor_FR <b>:playback_FR` | link dies with the process | edge live while running, **gone 1.0 s after kill** (m exit −9) |
| t4_move_sticky | `pactl move-sink-input <idx> <mv_b>` on a live tone stream | moved at +1.2 s **and still at +4.6 s**, content follows | edges `→mv_a` before, `→mv_b` at both samples; mv_b monitor tap **45 `mine` windows** (peak 8189) |
| t5_move_dontmove_noop | same move on a `node.dont-move=true` stream | **silent no-op** — rc=0, links unchanged | prop `true` confirmed on the node; move rc=0; edges stay `→dm_a` at both samples; dm_a tap **47 `mine` windows** (the tone never left) |

All five scout headline items chosen for this arm are **confirmed as
laws** on this host — each with the graph witness, not just rc.

## 3. Measured corrections / additions during authoring

- **`sink_properties=` is whitespace-split modargs.** This seat's first
  formal run (receipt `20261015T134206631212Z-module-r80`, disclosed
  failing run) used `description=r80md desc <pid> marker` and measured
  `node.description == "r80md"` — the value truncates at the first
  space **inside** the prop vector. The scout's own a2 cell used a
  space-free `r80desc`; the arm now uses a space-free marker so a1/a2
  compare the *same* value on both paths. The truncation micro-fact is
  recorded here, not armed (it deserves its own leg lattice on quoting,
  another round).
- **`media.class=Audio/Source` output port name.** The node publishes
  exactly one output port and it is named `<n>:capture_FR` (not the
  `capture_FL/FR` pair a real source would have). Recorded verbatim in
  `out_ports`; asserted only on `n_input_ports == 0` + the pactl view.
- **Tap amplitude**: the feeds run at **full tag amplitude** into
  probe-owned sinks — the scout's `--volume 0.05` was a
  shared-default-sink concession; probe-owned destinations let the
  standard `mine` bands (≥3000 corrected peak) apply, and both move-leg
  taps carry the tone.

## 4. Guards, fail-closed rules, teardown

- **By-id unload only**: every `pactl unload-module` call in the arm
  uses the index captured at *our own* `load-module` return. No name is
  ever passed to unload — the scout's §10 foreign-module incident is the
  exact failure this prevents. Post-fold, teardown/block re-unloads go
  through the **ownership guard** (`_module_r80_unload_own`): indexes
  recycle LIFO within seconds, so a stale id whose slot now lists a
  foreign (or native — boundary B3) module is skipped as
  `foreign_risk`, an absent id as `already_unloaded`, and only an id
  still cited by a *live* (client-id-carrying) node of ours fires. The
  a5 re-unload row accepts the named skips as the same law client-side.
- **`pw-cli destroy` is scoped**: invoked only on a node id read from a
  `pw-dump` name match, and only ever on `r80md_`-tagged nodes (the a5
  orphan plus teardown's stray sweep). A scraped id is never fed to it.
- **Teardown witnesses**: `sinks_gone` per loaded name and
  `own_nodes_after: []` (no `r80md_` node survives) are asserted on both
  entries in both runs.
- **Coverage honesty**: `coverage_blocked`/`blocked` naming is wired;
  neither entry blocked in either formal run.
- **Oracle + contention census** recorded per entry (`source_meta:
  null` while pactl enumerates the Line source — the same authority
  split the r79 arm documented; `aplay: 1` — the known stale process;
  `host_is_quiet: false`).

## 5. Run-to-run stability

Two consecutive runs on identical bytes: leg sets identical, every
verdict flag identical, `failures: {}` twice, stderr 0 B both runs. The
420 normalized leaf diffs are the volatile classes only (pid-stamped
names/keys, module ids `536870942→536870931` — the host's LIFO free-list
visible in the receipt, object ids/serials, sink-input index, `waited_s`
≤0.001 s, tap peak 8137→8189, and the **per-run pid-derived tag
frequency** pair working as designed: 1210→1000 Hz). The 23 added/23
removed leaf paths are pid-stamped `sinks_gone`/`sink_loads` **keys** —
no structural delta.

## 6. What this arm does not claim

- No claim beyond this host / PipeWire 1.6.8 / pactl 17.0-98 /
  WirePlumber 0.5.17 — `@DEFAULT_SINK@` expansion could differ elsewhere.
- The linger-orphan leg asserts the lifecycle law, not a leak severity
  rating.
- `move-sink-input` stickiness was held to +4.6 s (scout measured +6 s);
  nothing claimed past the horizon.
- The scout's §4.2 re-link transient stays **unattributed** — no
  re-measure here.
- The a4 leg records `n_output_ports: 1` / port name verbatim but does
  not claim the single `capture_FR` port is general — it is this host's
  reading.

## 7. Write scope, replay, tree state

- **Tracked edits: one file** — `corpus/fixtures/measure_audio.py`
  (+905/−3, sha256 `3b69541f684c0cf414084c6f7e4cb313facff050783dde95c335308850d046c4`,
  `python3 -m py_compile` clean; the `__pycache__` .pyc was `git
  checkout`-ed back to HEAD so the tracked diff is exactly the source
  edit).
- **Untracked artifacts**: `corpus/live/r80-author/` (both receipt
  copies + `receipt-shas.txt`), the three canonical receipts the fixture
  itself wrote under `corpus/live/runs/` (`…T134206631212Z` = the
  disclosed spaced-description failure run; `…T134301846760Z` and
  `…T134359918834Z` = the two formal greens), and this report.
  `SHONEN.md` was already modified before this seat's first command —
  untouched. **No commit, no push.**
- **Replay**: `python3 corpus/fixtures/measure_audio.py
  --probe-module-r80` from the repo root (~55 s; writes its own
  `-module-r80` receipt and prints `{"receipt": …, "failures": {}}`;
  exit 0 on a clean run).
- **Authoring-window probes**: six direct `pactl`/`pw-link`/`pw-cli`
  sanity probes ran before coding to pin EnumFormat shape, link
  direction, the orphan destroy path and the move legs; all
  `r80md_<pid>` resources from those probes were unloaded/destroyed and
  a post-probe census shows zero `r80md` sinks/nodes on the host.
