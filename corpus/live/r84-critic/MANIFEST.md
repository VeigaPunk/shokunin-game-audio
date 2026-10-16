# r84-critic receipts — MANIFEST

Seat: CRITIC (wave-B gate, r84). Lane `/home/vgpnk/Projects/shokunin/audio-shokunin`.
Scope: committed landing `fbe65713` (`corpus/fixtures/measure_audio.py`,
md5 `1e27992f3e3ab3cfa6ae71841827199a`, sha256
`8ed09d19990480fd337cba99e45cb0588e0615fd90e34793ecc4841c21368e4e`),
pinned export at `~/Projects/shokunin/tmp/r84critic-src` (fixture md5 ==
committed blob). Zero tracked writes; no commits; no `set-default-*`; no
foreign object touched. Report: `reports/round-84/r84-critic.md`.

## Files

| file | what it is |
| --- | --- |
| `pre-state.txt` | entry census: loadavg, `pactl info` defaults, running audio processes |
| `replay-run1.measurements.json` | 147-leg replay on the pinned export, own `TMPDIR` (concurrent sibling run): 2 dev_lattice reds = sibling nodes in `new_node_names` |
| `replay-run1.stdout.json` | the script's stdout for run1 (`failures` map) |
| `replay-run1.stderr.txt` | empty |
| `replay-run2.measurements.json` | 147-leg replay, shared `TMPDIR` (serialized behind the family flock): **`failures: {}`** |
| `replay-run2.stdout.json` | the script's stdout for run2 |
| `replay-run2.stderr.txt` | empty |
| `probeA-unload-anchor.py` / `.json` | live re-proof of the anchored `_gst_r81_sink_module_index` / `_gst_r81_unload_own` on the r84 teardown path (nested `r84c_a`/`r84c_a2`) |
| `probeA2-prefix-nesting.py` / `.json` | pid-prefix nesting re-proof (`r84c_ns_1` query vs `r84c_ns_12` module) |
| `probeB-env-hermeticity.py` / `.json` | ambient `PIPEWIRE_LATENCY` / `PIPEWIRE_PROPS` override of the r84 plugin pins |
| `probeC-ungated-pins.py` / `.json` | committed `alsapw_pactl_write_r84_entry` with the `-10%` call intercepted and a synthetic 64-amp series: `vol_neg` green on an absolute-10 % write; `vol_150`/`vol_25_idx` green with no base floor |
| `probeD-lock-scope.txt` | lock-path/co-tenancy evidence log (two concurrent runs, three serialized runs, the node-delta and bound-kill mechanisms) |
| `SHA256SUMS` | sha256 of every file above |

## Provenance notes

- All replays/probes ran against the **pinned export**, never the worktree
  (the worktree moved during the window: HEAD `fbe65713` → `2e4e879b` →
  `38cf715b`; the fixture file stayed byte-identical to the pinned blob).
- `TMPDIR` for run1/probes: `~/Projects/shokunin/tmp/r84critic-tmp`;
  run2: `~/Projects/shokunin/tmp` (`/tmp` is quota-bound on this host).
- Seat objects: `r84c_*` (probes) plus the family's own `r84a_ns_<own pid>`
  in the replays. All unloaded and verified; zero residue; defaults unchanged
  (`…SPDIF__sink.29` / `…Line__source.29`).
- Read-only citations outside this dir: the verifier's concurrent run
  (`corpus/live/r84-verifier/runs/r84v1.*`) and the committed receipts under
  `corpus/live/r84-author/runs/` (md5 `6bf2ce12…` / `31e47301…`, each equal
  to its canon copy under `corpus/live/runs/`).
