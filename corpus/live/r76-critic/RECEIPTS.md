# r76-critic evidence index

HEAD at review: `d566a317e6b849032c444155e933b33a102bbada` (matches author).
Fixture sha256 `691d730d4b4b2aa1475aa03bd4d9d7b5c9bdd3baf6a62d24923097f6fb9e9734`
(matches the author's report). Tracked tree clean before and after review
(the fixture `__pycache__/*.pyc` was re-dirtied by one of my importlib
experiments and restored to HEAD bytes; every later harness runs with
`sys.dont_write_bytecode = True`).

## Receipts — one sha, four runs

| run (corpus/live/runs/) | who | sha256 of measurements.json |
| --- | --- | --- |
| 20261014T182450100472Z-capture-r76 | author (canonical) | ba36cd70f765826a9937fc78c62143c984790f1bdc26a4ad8aaf813cfc00f92f |
| 20261014T182539237046Z-capture-r76 | author (rerun) | ba36cd70… (same) |
| 20261014T183215518470Z-capture-r76 | **critic run 1** | ba36cd70… (same) |
| 20261014T183309733895Z-capture-r76 | concurrent seat (not mine) | ba36cd70… (same) |
| 20261014T183404004733Z-capture-r76 | **critic run 2** | ba36cd70… (same) |

Commands (outer bound exactly as assigned):

```
timeout -s KILL 480 python3 corpus/fixtures/measure_audio.py --probe-capture-r76
```

Logs: `probe-run1.log`, `probe-run2.log`. Both printed
`"failures": {}` and `EXIT=0`. Structural diff of the two JSON trees
(key-by-key walk) between author run 1 and my run 1: **zero differences**
(not just equal sha — the walk emits nothing).

## Regression replay of the PREVIOUS arm (r75)

```
timeout -s KILL 480 python3 corpus/fixtures/measure_audio.py --probe-consumers2-r75
→ corpus/live/runs/20261014T183519581984Z-consumers2-r75   failures: {}
```
sha `6ffb0f819ea998cc75413b0e04d5f068d29cc8d52f52936ffaa5fc54beb4c410`
vs r75 canonical `9de8b8f8483cb77706663127e2b7a9cb083c5134742224d458b10d60cff2b897`.
Structural diff: **one leaf** —
`consumer2_paplay_ops_r75_probe/daemon_gate_dead/wall_s` `0.001 → 0.002`
(a pre-existing raw wall-clock float; r75 itself produced three distinct
shas across its own runs). Every prior row reproduces.

## D1 sweep — the degenerate `parecord_term` cell in the author's own runs

| receipt | sever `parecord_term` | sever entry `failures` |
| --- | --- | --- |
| …T181454123380Z | `data_actual_zero: true`, wave `honest_empty` | 2 (ffmpeg-KILL union, arecord riff field) |
| …T181743427243Z ("clean run") | `data_actual_zero: true`, wave `honest_empty` | **0** |
| …T182210846231Z … …T183404004733Z (7 receipts) | `data_actual_zero: false`, wave `honest` | 0 |

The bounded leg `parecord_term_bound` (`prd_bound.wav`, same argv, same 2.5 s
wait) is `data_actual_zero: false` in all nine receipts.

## Counterexample harnesses (run on the landed fixture)

- `exp_classifier.py` — calls the landed `_capture_wav_inspect`,
  `_capture_out_kind`, `_capture_parser_verdict` on synthetic files.
- `exp_gate_vacuity.py` — calls the landed `capture_gate_r76_entry()` with
  `_capture_inventory` monkeypatched to a degraded (empty) inventory.
- `repro/` — direct consumer reproductions:
  - `nodev.wav` — `parecord nodev.wav` (no `-d`) → rc=1, stderr
    `Stream error: No such entity`, and a **44-byte finalized WAV**
    (`RIFF$...WAVE fmt 16 PCM 2ch 44100Hz data(0)`).
  - `dead.wav` — `PULSE_SERVER=unix:/nonexistent-r76-gate parecord -d
    @DEFAULT_SOURCE@ dead.wav` → rc=1, `pa_context_connect() failed`, same
    44-byte finalized WAV.
  - `pwr_notarget.wav` — `pw-record -n 4800 pwr_notarget.wav` (no
    `--target`) → rc=1, `no target node available`, 44-byte finalized WAV
    (`data(0)`), i.e. the arm's own `pwrecord_auto_target` gate shape,
    reproduced byte-exactly.

## Runtime / host

Same host as the author (`plazir27`), PipeWire 1.6.8 / pacat 17.0-98 /
alsa-utils 1.2.16 / ffmpeg n9.0.1 / Python 3.14.7. No git mutation: no
commits, no index changes; the only tracked-file write was the pyc restore
to HEAD bytes described above.
