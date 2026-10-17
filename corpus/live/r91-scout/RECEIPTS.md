# r91-scout RECEIPTS

Scratch root: `corpus/live/r91-scout/` (untracked). Host `plazir27`, 2026-10-15 (UTC window ~17:0x-17:2x).

## Consolidated receipts

| artifact | content |
| --- | --- |
| `receipts/props.json` | live prop lattice, 5 client families x 3 reps |
| `receipts/loss.json` | target-loss timeline, 4 families x 3 reps |
| `receipts/recover-inloop.json` | manual-relink discriminator x 3 reps |
| `receipts/summary.json` | audit roll-up (this file's source) |
| `receipts/census-*.json` | entry/exit censuses (modules, defaults, dump size, residue) |
| `sources/*.c`, `sources/SOURCES.sha256`, `sources/WP-LUA.sha256` | version-matched upstream sources + on-host Lua shas |
| `probes/driver.py`, `probes/diag_src*.py` | harnesses (all legs triple-bounded) |
| `runs/<stage>/<leg>/receipt.json` | per-leg raw receipt (argv, rc, timeline) |

## Key numbers

- `F1_pwrec_plain`: stable=True x3; state=suspended; node.dont-reconnect=None; stream.capture.sink=None
- `F2_pwrec_capsink`: stable=True x3; state=suspended; node.dont-reconnect=None; stream.capture.sink=True
- `F3_gst_src_default`: stable=True x3; state=running; node.dont-reconnect=True; stream.capture.sink='TRUE'
- `F4_gst_src_override`: stable=True x3; state=running; node.dont-reconnect='FALSE'; stream.capture.sink='TRUE'
- `F5_gst_sink_silence`: stable=True x3; state=running; node.dont-reconnect=None; stream.capture.sink=None
- loss `F1s_pwrec_srcloss`: frozen=[False, True, True]; final=[385068, 237612, 229420]; states=[[[0.0, 'running'], [2.054, 'idle']]]
- loss `F2_pwrec_capsink`: frozen=[False, False, False]; final=[929836, 925740, 925740]; states=[[[0.0, 'running']]]
- loss `F3_gst_src_default`: frozen=[True, True, True]; final=[204844, 204844, 204844]; states=[[[0.164, 'running'], [1.278, 'idle']]]
- loss `F4_gst_src_override`: frozen=[True, True, True]; final=[204844, 204844, 204844]; states=[[[0.163, 'running'], [1.275, 'idle']]]
- recover r0: frozen_before=True resumed_after=False manual_links=['  |-> r79lb_ns_b_1141702:playback_FR', 'r91s_ns2:playback_FL', 'r91s_ns2:playback_FR']
- recover r1: frozen_before=True resumed_after=False manual_links=['r91s_ns2:playback_FL', 'r91s_ns2:playback_FR', 'r91s_tone_ns2:output_FL']
- recover r2: frozen_before=True resumed_after=False manual_links=['  |<- output.r79lb_1141702_c02_second_sink:output_FR', 'r91s_ns2:playback_FL', 'r91s_ns2:playback_FR']

## Manifest

`manifest.sha256` covers 94 files (probes, receipts, sources, per-leg receipts/logs). Report at `reports/round-91/r91-scout.md` is outside the scratch tree and is not in this manifest.

