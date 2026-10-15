# r92-scout receipts index

Seat: SCOUT (leaf), round 92. Surface: **`libpipewire-module-filter-chain`**
(PipeWire 1.6.8 SPA filter-graph host) + `wpexec` as the script-side loader.

Generated 2026-10-15T18:30:50Z. 74 files, 10.84 MB. Every path below is untracked scratch; nothing outside `corpus/live/r92-scout/` was written except the round report.

## Receipts (JSON) — one per stage, each leg triple-bounded

| file | stage | what it holds |
| --- | --- | --- |
| `runs/f0/receipt.json` | f0 | loader feasibility, load shape, lifecycle (nodes die with pw-cli) |
| `receipts/f1_ports.json` | f1 | exact port names of every object; link-shape matrix |
| `receipts/f2_e2e.json` | f2 | end-to-end hop matrix + the suspended negative control |
| `receipts/f3_driver.json` | f3 | driver law S1-S4 (`node.passive`, class mismatch) |
| `receipts/v2_links.json` | links | `links=[...]` grammar, quoted vs unquoted port names |
| `receipts/v2_labels.json` | labels | **measured** builtin-label inventory (not strings) |
| `receipts/v2_dsp.json` | dsp | transfer function, 17 graphs x 3 reps, pre/post dual tap (v1 1-rep copy kept as `receipts/dsp.json`) |
| `receipts/v2_ir.json` | ir | impulse response: convolver / delay, delta stimulus |
| `receipts/v2_clamp.json` | clamp | control-value clamp law |
| `receipts/v2_absent.json` | absent | ladspa / lv2 / sofa / ffmpeg / ebur128 classes |
| `receipts/v2_configs.json` | configs | the 12 shipped `filter-chain/*.conf`, load matrix |
| `receipts/shape.json` | shape | v1 load-shape census (superseded by v2) |
| `receipts/f4_wpexec.json` | wpexec | interpreter legs W1-W8 + residue law |

## Probes

| file | role |
| --- | --- |
| `probes/pwlib.py` | own bounded runner (killpg + wall cap + byte cap), own synth, own DFT/biquad reference |
| `probes/driver.py` | v1 driver (superseded) |
| `probes/driver2.py` | v2 rig: single-driver topology + pre/post dual tap |
| `probes/f0_load.py` | loader feasibility |
| `probes/f1_ports.py` | port/link census |
| `probes/f2_e2e.py` | hop matrix |
| `probes/f3_driver.py` | driver-law arms S1-S4 |
| `probes/f4_wpexec.py` | wpexec legs |
| `probes/audit.py` | teardown audit |

## Sources read (not written by this seat)

`sources/READ-SOURCES.sha256` — sha256 of the 19 on-disk files this seat read
as sources (1.6.8 filter-chain man page, `wpexec` man page, the 12 shipped
`filter-chain/*.conf`, `filter-chain.conf`, the two official WirePlumber
examples, and the two Lua scripts `linking/rescan.lua`,
`node/filter-graph.lua`).

## Notes

- `scratch/` holds the stimuli (own synth) and the captured WAVs referenced by the
  receipts. `runs/v2_all.log` is the full stage log.
- No sibling fixture (`corpus/fixtures/measure_audio.py`) was read, imported or executed.
- Teardown: every mutating leg unloads its own module by index verified against the
  seat name; the final sweep in `driver2.py` asserts zero r92s nodes, modules and processes.
