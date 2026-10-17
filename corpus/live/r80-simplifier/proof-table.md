# r80 simplifier — fold proof table

Base: `corpus/fixtures/measure_audio.py` (13463 lines / 720228 B, author's r80 work unmodified).
Folded: `corpus/live/r80-simplifier/folded/measure_audio.py` (13434 lines / 718952 B).
Scope: r80 block only (base lines 11555–12440). All diffs confined to that range; pre-r80 code byte-identical.

## Receipt equivalence (normalized diff, `normalize.py`)

| run | receipt | mode | failures | legs a/t | vs base1 | vs base2 | vs base3 |
|---|---|---|---|---|---|---|---|
| base1 | `corpus/live/runs/20261015T155155955015Z-module-r80/` | probe-module-r80 | `{}` | 5/5 | — | 0 | 0 |
| base2 | `corpus/live/runs/20261015T155230037067Z-module-r80/` | probe-module-r80 | `{}` | 5/5 | 0 | — | 0 |
| base3 | `corpus/live/runs/20261015T160033687459Z-module-r80/` | probe-module-r80 | `{}` | 5/5 | 0 | 0 | — |
| foldA | `r80-simplifier/live/runs/20261015T155926389567Z-module-r80/` | probe-module-r80 | `{}` | 5/5 | 0 | 0 | 0 |
| foldB | `r80-simplifier/live/runs/20261015T155956273594Z-module-r80/` | probe-module-r80 | `{}` | 5/5 | 6* | 6* | 6* |
| foldOLD (pre-`with_node` gate) | `r80-simplifier/live/runs/20261015T155343438656Z-module-r80/` | probe-module-r80 | `{}` | 5/5 | 6* | 6* | 6* |

\* 6 changed lines = t4 tap tail-boundary window `mine: false→true`, `mine_spans` [0.6,5.1]→[0.6,5.2],
`mine_windows` 45→46. **Demonstrated inherent jitter**: identical source `foldA` vs `foldB` reproduces
it; it is the feed-kill landing ±50 ms across the 0.1 s analysis grid — not fold-attributable
(foldA matches all three base runs exactly).

Volatile set normalized (all verified to vary between *base* runs or pid-derived by construction):
`r80md_<pid>` tags (incl. `r80md_desc_<pid>_marker`), module/object/serial/client ids, `own_pid`,
`*_waited_s`, `stdout_tail` when it is the returned module index, tmpdir names, `module_count_*`
(foreign module load/unload observed: 47↔48 between base runs, `before==after` invariant holds in
every run), and per-window `f_l/f_r/a_l/a_r`/`peak_*` — the tag tone's frequency is pid-derived
(`PLAYBACK_R78_TONE_L_HZ = 997 + pid%4*211`; measured 1420/1920, 997/1500, 1208/1711 across runs).

Non-volatile surface proven identical across base×3 vs foldA (normalized diff = 0): leg names and
dicts, all `load`/`unload`/`re_unload`/`destroy`/`move` leaves incl. `error_class`
(`pa_io_error`/`pa_no_such_entity`), `description`/`expected`/`sent` strings, `enum_rates`/
`enum_formats`, `media_class`/port counts, edge sets (post tag-normalization), `sinks_gone`,
`own_nodes_after`, `oracle_at_start`, `contention` counts, `inventory`, `blocked`/`coverage_blocked`
absence, all `failures` lists, plus the full non-r80 receipt (SPECS measurements, distinctness,
sections, family comparisons — byte-identical).

## Folds (each inside the r80 block only)

| # | fold | base lines | delta | evidence |
|---|---|---|---|---|
| F1 | dead constant `MODULE_R80_STREAM_LEAD_S` (grep: 1 hit = definition; legs use `PLAYBACK_R78_TAP_LEAD_S` / `_module_r80_wait_edge` instead) | 11585 | −1L/−61B | def-only hit; all runs green |
| F2 | `_MODULE_R80_ERR_CLASSES` one-element tuple + bespoke loop → explicit `pa_io_error` check + delegate to `_playback_r78_errclass` (identical first-match order) | 11592–11604 | −6L/net −19B | `pa_io_error` still classified in t1 attempts (receipt identical) |
| F3 | `_module_r80_load`: `out.strip().isdigit()`/`int(out.strip())` → `out.isdigit()`/`int(out)` — `stdout_tail` is already `.strip()`-ed at construction | 11631–11632 | ±0L/−16B | module ids land: a5 stale-`pulse.module.id` check passes in every run |
| F4 | `_module_r80_wait_node(tag, timeout_s=…)` → `(tag)`; 5/5 call sites used the default | 11709,11714 | ±0L/+34B | a1–a5 `node_seen`/`node_waited_s` identical |
| F5 | `_module_r80_load_sink(name, *extra_args)` → `(name)`; sole caller never passed args; stale docstring clause trimmed | 11722–11728 | −3L/−174B | 6/6 topo sinks `sink_seen: true` every run |
| F6 | `_module_r80_wait_edge(…, timeout_s=…)` → `(out_port, in_port)`; both call sites used the default | 11747–11753 | −1L/−46B | t4/t5 `edge_a_linked: true` identical |
| F7 | t1's duplicated `pactl list modules short` try-blocks → `_module_r80_module_count()` | 12149–12176 + new helper | −7L net (18L removed, 11L added) | `module_count_before==after` in all 6 runs |
| F8 | t4/t5 shared move skeleton → `_module_r80_move_leg(...)`; `with_node` gate keeps t4's subprocess sequence byte-identical (t5's node snapshot preserved) | 12247–12337 + new helper | −13L net (84L removed, 71L added incl. shared helper) | t4/t5 leaves identical; leg dict key order preserved |
| F9 | `_module_r80_block(loads=None)` → required `loads`; sole caller always passes the dict; `if loads is not None` guard inlined | 11838–11841 | −1L/−37B | coverage path unchanged (never fired — no run blocked) |
| F10 | `ctx["tmp"]` dead dict slot (set, never read — `tmp` used directly) | 12132 | ±0L/−12B | `ctx["tone"]` path unchanged |

Net: −29 lines / −1249 B on the r80 block (135 lines removed, 106 added; +59 of the added lines are
the two extracted helpers F7/F8).

## Rejected / deferred candidates (no fold — would change semantics or receipt)

- `_module_r80_nodes` vs `_loopback_r79_nodes`: different leaf schema (`pulse_module_id`,
  `object_linger`, `enum_*`, port counts) — receipt-bearing, folding changes output.
- `_module_r80_unload` vs `_playback_r78_unload`: r80 needs the rich leaf
  (`error_class` checked by a5 `re_unload`); r78's returns a bare rc.
- `_module_r80_teardown` vs `_loopback_r79_teardown`: r80 adds the orphan `pw-cli destroy` pass —
  the linger law's cleanup.
- `_module_r80_feed` vs `_loopback_r79_feed`: `extra_props` is used (t5 `node.dont-move`);
  delegating only t4 would split one convention into two.
- `_module_r80_feed`'s unread `stderr=subprocess.PIPE`: latent wedge if pw-cat ever emitted >64 KiB;
  observation only — changing it is not a deletion and alters process wiring.
- Single-use constants (`MLINK_DEAD_S`, `TONE_S`, `TAP_S`, `MOVE_*`): live knobs, not dead weight;
  only the zero-use `STREAM_LEAD_S` was removed.
