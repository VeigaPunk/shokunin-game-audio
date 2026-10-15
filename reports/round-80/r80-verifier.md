# R80 VERIFIER (audio) — independent replay of `--probe-module-r80`

Seat: VERIFIER. Lane `~/Projects/shokunin/audio-shokunin`, HEAD
`ee6d6847cf27f9fd2c9dd784ada25468ef0a1426` (`r79 LOG: ADMIT-corr`). Host
`plazir27`. Toolchain verified live: PipeWire **1.6.8** (pw-cli linked
1.6.8), pactl **17.0-98-gb096** (libpulse 17.0), WirePlumber present
(wpctl on PATH). Frozen artifact under test:
`corpus/fixtures/measure_audio.py` sha256
`3b69541f684c0cf414084c6f7e4cb313facff050783dde95c335308850d046c4` —
byte-identical to the author's claimed sha. `+905/−3` confirmed by
`git diff --stat`; `python3 -m py_compile` clean.

**No LSP device exists in this session** (`lsp` is not an available
tool), so all checks are literal: exact diff hunks, code reading, and
first-hand runtime evidence. Nothing below is claimed as semantic (LSP)
proof.

**Write scope:** untracked `corpus/live/r80-verify/` (my receipt copy,
the captured stdout/stderr pair, the verbatim diff, the cross-run
projection) and this report. The tracked `__pycache__` `.pyc` dirtied by
py_compile + my run was restored via `git checkout` — tracked tree shows
only the pre-existing ` M SHONEN.md` and the author's
` M corpus/fixtures/measure_audio.py`. **No commit.**

---

## Verdict: **CONFIRM**

Every headline claim in `r80-author.md` reproduced on my own fresh run;
the diff is additive-only modulo the three prepend wiring lines, exactly
as claimed; host left clean by every run I observed, including a
concurrent sibling lane's.

## 1. Independent run

| run | receipt | sha256 | exit | failures | stderr |
| --- | --- | --- | --- | --- | --- |
| V1 `--probe-module-r80` | `corpus/live/runs/20261015T153530291390Z-module-r80/measurements.json` | `dd40b1246871283d…` | 0 | `{}` | 0 B |

Driver: direct `python3 corpus/fixtures/measure_audio.py
--probe-module-r80` from the repo root; stdout/stderr captured to
`corpus/live/r80-verify/verify-run.{stdout.json,stderr.log}`. stdout is
the single `{"receipt": …, "failures": {}}` line. Run pid 986178; run
occupied ~12:34:35→12:35:30 local (~55 s), consistent with the author's
replay estimate. Receipt copied to `corpus/live/r80-verify/`.

## 2. Verdict table — every leg re-measured, not just asserted

All cells below are read from **my** receipt (pid-stamped `r80md_986178_*`)
unless noted.

| leg | author claim | my measurement | verdict |
| --- | --- | --- | --- |
| a1_desc_dropped | plain `description=<d>` is an unknown key, silently dropped; `node.description` stays the derived `<name> <class> sink`; `pulse.module.id` == returned index | `node.description = "r80md_986178_a1 Audio/Sink sink"` (derived, `d` absent); `pulse_module_id 536870939 == load.module_id 536870939`; unload rc=0; `gone_after_unload` True | CONFIRMED |
| a2_desc_prop_wins | same value via `sink_properties=device.description=` lands and wins | `node.description == sent_description == "r80md_desc_986178_marker"` | CONFIRMED |
| a3_rate_no_check | `rate=99999` accepted verbatim into `EnumFormat` — no range check | `enum_rates: [99999]`; `enum_formats[0].rate: 99999` | CONFIRMED |
| a4_source_class | `media.class=Audio/Source` is a real class change: 0 input ports, pactl source `<n>`, no sink / no `<n>.monitor` | `media_class Audio/Source`, `n_input_ports 0`, `in_ports []`, `out_ports ["…:capture_FR"]` (single capture_FR, as author recorded), `pactl_sink_listed False`, `pactl_source_listed True`, `pactl_monitor_listed False` | CONFIRMED |
| a5_linger_orphan | `object.linger=true` node survives `unload-module`: stale pmid, still sink+monitor, re-unload rc=1 `No such entity`, only `pw-cli destroy` removes | live: `object_linger True`, `client_id None`; unload rc=0 → `node_after_unload.found True`, `pulse_module_id 536870939` (stale), `pactl_sink_after_unload True`, `pactl_monitor_after_unload True`; `re_unload exit_code 1 / pa_no_such_entity`; `destroy exit_code 0`, `gone_after_destroy True` | CONFIRMED |
| t1_combine_default_refused | `slaves=@DEFAULT_SINK@` and `sinks=@DEFAULT_SINK@` both rc=1 `Failure: Input/Output error`, no node, module count unmoved | both attempts `exit_code 1 / pa_io_error`; `node_created False`; `branch_nodes []`; `module_count 48 → 48` | CONFIRMED |
| t2_pwlink_lingers | `pw-link <o> <i>` edge outlives the exited creator at +2.0 s; `pw-link -d` rc=0 | `create rc 0`, `linked_immediately True`, `linked_later True` (+2.0 s), `teardown_d exit_code 0` | CONFIRMED |
| t3_pwlink_m_dies | `pw-link -m` edge dies with the client (~1 s after kill) | `linked_while_running True`, `m_exit_code −9`, `linked_after_death False`, `edges_after_death []` | CONFIRMED |
| t4_move_sticky | `move-sink-input` lands by +1.2 s, still moved at +4.6 s, content follows (destination monitor tap carries the tag tone) | move rc=0; edges `→mv_b` at both samples; mv_b tap `carries_tone True`, **45 `mine` windows**, peak 8137/7980 — the pid-derived tag (1420/1920 Hz for pid 986178, formula `997+pid%4·211`/`L+503`, measured 1420/1920 ±1 Hz) is *my* run's tone, not a replayed constant | CONFIRMED |
| t5_move_dontmove_noop | `node.dont-move=true` stream: move is a silent rc=0 no-op, edges stay on the original sink, its tap keeps the tone | `node_dont_move_prop True` on the stream node; move rc=0; edges stay `→dm_a` at +1.2 s and +4.6 s; zero `→dm_b` edges; dm_a tap `carries_tone True`, **47 `mine` windows** | CONFIRMED |

Both entries: `failures: []`, `own_nodes_after: []`, `sinks_gone` all
True, no `blocked`/`coverage_blocked`. Oracle and contention census
present (`source_meta: null`, `aplay: 1`, `host_is_quiet: false`) —
same shape the author reported.

## 3. Run-to-run stability — four receipts, zero verdict drift

`corpus/live/r80-verify/cross-run-verdict-diff.txt`: **266 leaf keys
compared** across author run 1 (`T134301`, pid 726605), author run 2
(`T134359`, pid 736128), a third green receipt present in
`corpus/live/r80-author/` (`T152510`, pid 930381 — see Finding I3), and
my V1 (`T153530`, pid 986178). **70 differing leaves, 0 non-volatile**:
every diff is a pid-stamped name/key, module-id recycling
(`536870942/536870931/536870943/536870939` — the LIFO free-list, visible
and consistent), object ids/serials, `waited_s` ≤0.106, tap amplitude
(8136–8189 band — same physical tone, pid-shifted estimator), and the
host-global `module_count` (49/49/47/48 — unmoved *within* each run,
which is what the leg asserts). Every verdict-bearing flag — all five
a-leg and five t-leg outcomes, `failures`, `own_nodes_after`,
`sinks_gone`, `carries_tone`, `mine` window counts (45/47 stable in all
four runs) — is identical across all four receipts.

## 4. Prior legs untouched — additive-only diff verified

`git diff corpus/fixtures/measure_audio.py` (archived verbatim at
`corpus/live/r80-verify/measure_audio-r80.diff`): five hunks —

- `@@ -11552,6 +11552,894 @@` — the r80 arm: new constants, seven
  ` _module_r80_*` helpers, `module_args_lattice_r80_entry`,
  `module_topology_r80_entry`. Pure insertion between
  `filterchain_module_r79_entry` and `main`.
- `@@ -11674,12 +12562,13 @@` — one added line:
  `parser.add_argument("--probe-module-r80", action="store_true")`.
- `@@ -11970,6 +12859,19 @@` — the `if args.probe_module_r80:` dispatch
  block (13 added lines, zero deletions).
- `@@ -12528… / @@ -12548…` — the three rewritten wiring lines,
  exactly as claimed: the exclusivity `sum([…])` (new flag **appended**
  at position 123 of 124 — verified programmatically: the list minus the
  new flag is ordered-identical to the old list), the `mode` ternary and
  the `suffix` ternary (both **prepended** — `"-module-r80" if
  args.probe_module_r80 else <old chain verbatim>`). For every prior flag
  the computed value is unchanged.

One tracked file edited, `+905/−3`, sha256 match — author §7 accurate.

## 5. Host hygiene

- Pre-run census (12:33Z): zero `r80md` in `pw-dump`, zero `r80md`
  sinks/sources/modules in pactl, 42 modules loaded.
- Post-run census after my V1: `pw-dump | grep r80md` → 0, `pactl list
  modules short | grep r80md` → 0, `pw-link -l | grep r80md` → 0, no
  `pw-cat`/`pw-link -m`/`measure_audio` strays, no
  `/tmp/module-r80-topo-*` leftovers. My run loaded 11 null-sinks and an
  a5 linger orphan; all destroyed/unloaded (`own_nodes_after: []`,
  `sinks_gone` all True).
- A **concurrent sibling run** (pid 1034748, started 12:38:32 local,
  *after* my run ended) loaded its own `r80md_1034748_*` set while I
  watched — pid-namespacing worked, and its teardown also left zero
  residue at the 12:44Z census. I unloaded nothing of it — it cleaned
  itself.
- The pre-existing stale `aplay` noted by prior rounds' contention
  census (`aplay: 1` in every receipt incl. mine) persists — foreign,
  not r80's.

## 6. Findings by severity

**L1 — Low (latent defect in the new arm): `_module_r80_teardown`
re-unloads already-freed module indexes, silently.**
`module_args_lattice_r80_entry` unloads each leg's module *inside* the
leg, yet `loads` still holds every captured `module_id`; teardown
(measure_audio.py:11813-11814) then issues `pactl unload-module <id>`
for all of them again — for a5, a *third* unload of an index the leg's
own `re_unload` proved freed (`rc=1 No such entity`). Module index
recycling is demonstrated within a single run: all five a-legs reused
`536870939` in mine (and `536870942/931` per-run across authors'). If a
foreign `load-module` lands the recycled index in the gap — and this
host demonstrably runs concurrent probe lanes (pid 1034748 during my
session) — teardown silently unloads a **foreign** module: the same
hazard class as the scout's §10 by-name incident the arm exists to
prevent, and the result is discarded (not recorded in the receipt).
Window is sub-second to ~2 s and did not fire in 4/4 observed runs.
Fix direction for a future round: mark leg-unloaded ids, or record the
teardown unload leaves.

**I1 — Info: the report's "measured (run 2 verbatim)" column quotes run
1's values.** `r80md_desc_726605_marker`, pmid `536870942`, `pw-cli
destroy 151`, tap peak `8137` are all run-1 numbers; run 2's are
`736128`/`536870931`/`227`/`8189` (author §5 itself lists
`536870942→536870931`, `8137→8189`). Labeling slip only — the laws are
identical across runs.

**I2 — Info: t1's "module count unmoved … 23→23" matches no receipt.**
Receipts show `module_count 49→49` (author ×2), `47→47` (lane run),
`48→48` (mine). The asserted property — equal before/after — holds in
all four; the literal `23` appears nowhere.

**I3 — Info: a third green receipt sits in the author's artifact dir.**
`corpus/live/r80-author/receipt-20261015T152510343508Z-module-r80.json`
(sha256 `66d0532a…`, pid 930381, `failures []`) is absent from
`receipt-shas.txt`, which names only the two author runs. It is a valid,
verdict-consistent receipt — apparently a parallel lane's copy placed
under `r80-author/` — but the dir's manifest no longer enumerates its
contents.

**I4 — Info: tracked `__pycache__` side effect.** Running/compiling the
fixture dirties `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`;
restored to HEAD here (`git checkout`), matching the author's handling.

## 7. Residual risk and verification gaps

- No forge-mutant runs this seat (r79's verifier killed two). The r80
  assertions were read and are fail-closed on falsification (each leg
  names the falsifying observation in `failures`), but no mutant
  empirically proved the gates kill a forged expectation this round.
- L1's stale-index hazard is reasoned from code + observed LIFO index
  recycling, not triggered experimentally — deliberately arming a
  foreign-module collision would itself violate the shared-host
  convention.
- All claims are this-host bounded (PipeWire 1.6.8, pactl 17.0-98,
  WirePlumber 0.5.17-era session, USB Audio device set) — matching the
  author's own scope hedge in §6.
- The sibling run's receipt (pid 1034748) is not mine to adjudicate;
  its zero-residue teardown is noted as corroborating hygiene only.
