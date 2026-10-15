# R80 SIMPLIFIER — YAGNI folds inside the `pactl load-module` block

Seat: **SIMPLIFIER** (audio-shokunin round 80). Lane
`~/Projects/shokunin/audio-shokunin`, host `plazir27`, PipeWire live.
**No commit, no tracked-file edit** — `corpus/fixtures/measure_audio.py`
still diffs `+905/−3` (the author's r80 state, sha unchanged). All output
under `corpus/live/r80-simplifier/` + this report. LSP: no server answers
this file on this substrate (only the `rea` Ghidra MCP exists) — caller
proof used the documented text-grep fallback, then live-receipt replay as
the binding check.

## Deliverable

`corpus/live/r80-simplifier/folded/measure_audio.py` — the r80 block folded
to **13434 lines / 718952 B** (−29 lines / −1249 B net vs the 905-line
addition: 135 removed, 106 added, of which 59 are the two extracted
helpers). Pre-r80 code is byte-identical; argparse/mutex/dispatch/mode/
suffix wiring untouched.

## Method and kill criterion

Per the brief: candidates identified by census, each folded into the copy,
then `python3 measure_audio.py --probe-module-r80` run live on both files.
Receipts embed per-run data (pid-stamped `r80md_*` names, module/object
ids, wait times, tmpdirs) plus one subtlety: **the tag tone's frequency is
pid-derived** (`PLAYBACK_R78_TONE_L_HZ = 997 + pid%4*211` — L/R measured at
1420/1920, 997/1500, 1208/1711 across the six runs). `normalize.py` masks
exactly that volatile set; the non-volatile body — leg structure, every
`error_class`/`unload`/`move`/edge/`sinks_gone`/`failures` field, and the
whole pre-r80 receipt — is compared literally. **Any residual diff = fold
rejected.**

Runs (all exit 0, `failures: {}`, 10/10 legs, `sinks_gone` all true,
`own_nodes_after []`, `module_count` before==after):

| pair | normalized diff |
|---|---|
| base1↔base2, base1↔base3, base2↔base3 | 0 lines (all three identical) |
| **foldA↔base1, foldA↔base2, foldA↔base3** | **0 lines** |
| foldB↔any | 6 lines — t4 tail-window `mine` flip (5.1→5.2 span tail) |

The foldB diff is **demonstrated inherent jitter**, not a fold defect:
identical source `foldA` vs `foldB` produces the same 6-line flip — the
feed-kill lands ±50 ms across the 0.1 s analysis grid on this live daemon.
Earlier draft evidence proves the harness catches real perturbations: the
first helper revision added a pw-dump to t4's path and produced exactly
this signature; gating it behind `with_node` (t4's subprocess sequence now
byte-identical to base) returned foldA to 0 diffs against all three base
runs.

## Folds proven (see `proof-table.md` for byte counts per hunk)

- **F1** `MODULE_R80_STREAM_LEAD_S` — dead constant (definition-only hit;
  legs actually pace on `PLAYBACK_R78_TAP_LEAD_S` + `wait_edge`). −1 L.
- **F2** `_MODULE_R80_ERR_CLASSES` — a tuple of ONE class wrapped around
  r78's. Now an explicit `pa_io_error` check delegating to
  `_playback_r78_errclass`; first-match order identical. −6 L.
- **F3** `_module_r80_load` — `stdout_tail` is stripped at construction;
  removed the redundant `.strip()` pair on it. ±0 L.
- **F4/F6** `timeout_s` params on `_module_r80_wait_node`/`_wait_edge` —
  7/7 call sites use the default; dead alternate path inlined to
  `MODULE_R80_NODE_WAIT_S`. −1 L net.
- **F5** `_module_r80_load_sink(*extra_args)` — never passed; param and
  stale docstring clause gone. −3 L.
- **F7** t1's copy-pasted `pactl list modules short` blocks →
  `_module_r80_module_count()`. −7 L net.
- **F8** t4/t5 shared move skeleton (tap→feed→edge-gate→move→first/late
  edge samples→kill→reap) → `_module_r80_move_leg`; leg dicts assembled
  per-leg to preserve receipt key order; `with_node` keeps t5's node
  snapshot only where it was recorded. −13 L net.
- **F9** `_module_r80_block(loads=None)` → required `loads`; the only
  caller always passes the dict. −1 L.
- **F10** `ctx["tmp"]` dead dict slot. ±0 L.

## Tradeoffs / stops

- The `with_node` gate is a kept branch (one `if`) because it preserves
  t4's subprocess sequence exactly — buying 0-diff receipts is worth
  1 line; folding it away would reintroduce the boundary flip.
- `foldB`'s residual 6-line diff is the same jitter class demonstrated on
  identical code; the check-bearing fields (`carries_tone`, `failures`,
  `mine_windows` threshold margin 45/46 ≫ 8) never moved.
- Next folds stopped: `_module_r80_nodes` vs r79's reader (different
  receipt schema), `_module_r80_unload`/`-teardown`/`-feed` vs their r78/
  r79 twins (richer semantics used by verdicts) — all receipt-bearing or
  semantics-bearing; deleting them would harm the falsifiability axis.
