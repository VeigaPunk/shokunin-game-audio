# r94-boundary receipts — SoX_ng v14.8.0.1 lattice replayed under load

Seat: **audio r94-boundary** (executor). **Zero tracked-file writes; nothing
committed.** The only files this seat wrote outside `corpus/live/r94-boundary/`
are `reports/round-94/r94-boundary.md`.

Host `plazir27`, measurement window **2026-10-15 21:05:17Z → 21:11:19Z**
(host local UTC−3). Repo `~/Projects/shokunin/audio-shokunin`, HEAD
**`51a98e54`** at entry and exit. Toolchain: `sox` = **SoX_ng v14.8.0.1**
(`/usr/bin/sox` sha256 `646d899b53c1…`), Python 3.14.7, numpy 2.5.3,
Linux 7.2.3-arch1-3, PipeWire 1.6.8 / wireplumber 0.5.17.

## Layout

| path | content |
| --- | --- |
| `probes/r94b_lib.py` | own bounded runner (wall cap + output-byte cap in the loop that owns the process group; `start_new_session` + `os.killpg`, `RLIMIT_CORE=0`), own RIFF writer/reader, own metrics (peak/RMS dB, windowed-DFT tone + band level), own host witnesses, own-PID hog manager |
| `probes/r94b_driver.py` | the replay battery: `prep`, `laws` (125 cells), `axes` (44 cells), `conc` (5×16 concurrent), `witness`, `census` |
| `probes/r94b_r5_probe.py` | focused high-precision probe of the one falsified claim (r94-scout §1.5 `-v`) |
| `probes/r94b_analyze.py` | receipts → `runs/analysis-lattice.txt`, `analysis-scout-cross.txt`, `analysis-verdicts.txt`, `receipts/verdicts.json` |
| `probes/r94b_manifest.py` | `manifest.sha256` over every file this seat wrote |
| `run_all.sh` | single repro path: prep → settle 120 s → quiet pass → r5 quiet → load pass (16 hogs, 90 s warmup) → r5 load → census |
| `receipts/*.json` | one receipt per stage per pass (12 receipts, 397 cells, 1 342 process reps) |
| `runs/<pass>/<family>/<cell>/rep<N>/` | per-rep `cmd`, `stdout`, `stderr`, `meta.json` (triple-bounded, with per-rep `loadavg1`) |
| `runs/load/hogs-all.json` | hog lifecycle: PIDs, argv-marker verification, start-times, loadavg trace, CPU accounting, kill log |
| `runs/analysis-*.txt` | the tables quoted by the report |
| `scratch/r94b_stim_*.wav` | stimuli rebuilt from the r94 scout's own definitions — **all 9 sha256 match** `r94-scout/receipts/prep.json` |

## What the receipts pin

| receipt | cells/reps | pins |
| --- | --- | --- |
| `prep-quiet.json` | 2 / 12 | 9/9 stimulus shas equal the scout's; 3/3 smoke legs reproduce the scout's exact output bytes |
| `laws-quiet.json`, `laws-load.json` | 125 / 385 each | the armed cells: determinism matrix, gain/vol/norm, rate length+alias, remix, trim, fade, repeat/pad/silence, stat, chain, guard |
| `axes-quiet.json`, `axes-load.json` | 44 / 140 each | `-D`/`-R`/`--no-dither` placement, PipeWire client-env axes, sox buffer axes |
| `conc-quiet.json`, `conc-load.json` | 5 / 80 each | 16 simultaneous `sox` processes per cell |
| `r5-quiet.json`, `r5-load.json` | 22 / 66 each | focused attack on the `-v` claim (11 rate options × 2 stimuli × 3 reps) |
| `witness-quiet.json`, `witness-load.json`, `census-final.json` | 1 each | default sink/source, `settings` metadata, process + PipeWire node census |
| `verdicts.json` | 68 | machine-readable verdict table |

## Repro

```
cd corpus/live/r94-boundary && ./run_all.sh   # ~6 min (incl. 120 s settle + 2×90 s hog warmup)
python3 probes/r94b_analyze.py                # prints the verdict table
sha256sum -c manifest.sha256
```

## Safety ledger

- **File-only**: no PipeWire object was created by this seat (`pw-cli ls Node`
  shows **0** `r94b_*` nodes, 0 modules at exit); no device opened; `sox` never
  invoked with `-d`/`-p`/`play`/`rec`.
- **No global mutation**: no `pactl set-default-*`, no `wpctl set-*`, no
  `pw-metadata -w`, no config write. The PipeWire "rates/quantum" axis was
  varied with **per-process environment variables only** (`PIPEWIRE_QUANTUM`,
  `PIPEWIRE_RATE`, `PIPEWIRE_LATENCY`, `PIPEWIRE_NODE`, `PULSE_SINK`,
  `PULSE_SOURCE`). A global `set-default-sink` toggle was deliberately **not**
  performed: sibling sink-inputs were live throughout (r92-boundary streams),
  and the province precedent is that r95 never issued one.
- **Own PIDs only**: the 16 hogs are argv-marked `r94b_hog`; the kill path
  re-verifies the marker *and* the recorded `/proc/<pid>/stat` start-time before
  signalling, and never matches by name (r95 incident precedent: a namespace-blind
  `sweep()` killed three foreign `r85-boundary` children). Final kill log:
  `final_alive: []`, zero skipped/mismatched entries.
- **Foreign work preserved**: every foreign process, node and file encountered
  was only *listed*; the sibling-owned tracked file
  `corpus/fixtures/measure_audio.py` was never read, imported or executed.
