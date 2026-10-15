# r100-scout receipts index

Seat: SCOUT (leaf, frozen `probeParent` — exactly one labrat child, advisory).
Round 100, audio lane, surface verdict: **capstone residue ranking + the
`sofa`/`spatializer` HRTF pin**.

Generated 2026-10-15. 25 files, 7.13 MB. Every path below is untracked scratch
under `corpus/live/r100-scout/`; nothing outside it was written except the
round report. No tracked writes, no commits.

## Receipts (JSON) — one consolidated file per stage

| file | stage | what it holds |
| --- | --- | --- |
| `runs/sofa_gate.json` | gate | 3 legs: no-config @48000 (silence + graph error −22), real SOFA @48000 (rate-mismatch), real SOFA @44100 az0 |
| `runs/sofa_azimuth.json` | azimuth | 9 legs: az 0/90/270 × 3 reps, matching rate 44100 |
| `runs/sofa_extra.json` | extra | 5 legs: az90 @48000 ×3 (rate-mismatch ILD), az180 @44100 ×2 (front/back) |
| `receipts/sofa_probe_{gate,azimuth,extra}.json` | — | per-stage summary (seat, surface, SOFA path/rate, stage rows) |

Each leg record carries: exact module-argv token, per-link rc/tries, plugin log
lines (`spatializer`/`sofa`/`using n_samples`), `pw-play`/`pw-record` results,
the capture analysis (per-channel rms/peak/440 Hz Goertzel), `links_after`,
`pre_sweep`/`post_sweep` (namespace cleanliness), and `wall_s`.

## Captures (stereo WAV, pw-record post-tap)

`scratch/cap_<leg>_r<rep>.wav` for every leg, plus the two stimuli
`scratch/tone_44100.wav` / `tone_48000.wav` (440 Hz, amplitude 0.5, 1.6 s).

## Harness

`probes/sofa_probe.py` — seat-owned driver; imports the r92-scout `pwlib`
read-only (proven helper: bounded children, own synth, own WAV read). Two
in-flight harness defects were found and fixed here (recorded in the report
§7): a null-sink post-tap that cannot be linked (`No such file or directory`
×12 tries) and an unguarded `pw-cli` unload that raised `BrokenPipeError`
after the module's graph-start error. Final bytes are the fixed harness.

## Provenance

- SOFA file: `/usr/share/libmysofa/MIT_KEMAR_normal_pinna.sofa`
  (`Data.SamplingRate = 44100`, `Data.IR` 710×2×512, read with
  `/usr/bin/mysofa2json`; `/usr/share/libmysofa/default.sofa` exists too).
- Plugin: `/usr/lib/spa-0.2/filter-graph/libspa-filter-graph-plugin-sofa.so`
  (links `libmysofa.so.1`; config keys `filename/blocksize/tailsize/gain/
  normalize`; control ports `Azimuth/Elevation/Radius`).
- Man page contract: `man 7 libpipewire-module-filter-chain` §SOFA FILTERS
  (input `In`, outputs `Out L`/`Out R`; azimuth 0 ahead, 90 left, 270 right;
  "The control can be changed at runtime").
- Every PipeWire object this seat created is `r100s*`; teardown verified
  (`final sweep: clean: True` at the end of each stage); no operator device
  was touched (`node.autoconnect=false` on every stream; no
  `set-default-sink`/`set-default-source`).
