# r94-scout receipts — SoX_ng v14.8.0.1 effect/DSP lattice

Seat: audio r94 forward scout (leaf). **No tracked-file writes, no commits.**
Host `plazir27`, measured **2026-10-15 19:39–19:47Z** (host local UTC−3;
three battery passes — the receipts on disk are the 19:44 full pass plus the
19:46–19:47 `-D` reproducibility re-run).
Toolchain pinned: `sox` = **SoX_ng v14.8.0.1** (`/usr/bin/sox` sha256
`646d899b53c1c3fb94d8f48032a1e5eee549df75b22b4819a6be896af0d36947`,
`libsox_ng.so.3` sha256 `8d7fee48754b6ef28581e82176a14cb9a8b7350f60bd135fda7a1fc4dd68f7b7`);
Python 3.14.7, numpy 2.5.3.

## Layout

| path | content |
| --- | --- |
| `probes/r94lib.py` | own bounded runner (wall cap + output-byte cap + `killpg` + `RLIMIT_CORE=0`), own RIFF writer/reader (PCM u8/s16/s24/s32 + IEEE f32/f64, plain + EXTENSIBLE), own metrics (peak/RMS dB, windowed DFT tone, band level) |
| `probes/r94driver.py` | staged battery; `R94_PREFIX`/`R94_SUFFIX` produce the `-D` (no-dither) pass into `receipts/*_D.json` |
| `probes/r94_analyze.py` | receipt → report tables (`python3 probes/r94_analyze.py [det\|gain\|rate\|remix\|trim\|fade\|rps\|dither\|stat\|chain]`) |
| `run_all.sh` | sequential battery: default pass then `-D` pass (24.8 s wall under host load ≈ 27) |
| `receipts/*.json` | one receipt per stage; every leg carries argv, per-rep rc/wall/out sha256/out bytes/stderr head + parsed metrics |
| `runs/<stage>/<leg>/rep<N>/` | per-leg `cmd`, `stdout`, `stderr`, `meta.json` (triple-bounded) |
| `runs/analysis-*.txt` | the report's tables, regenerated from receipts |
| `sources/` | version-matched upstream sources fetched from Codeberg tag **`sox_ng-14.8.0.1`** (sha256 list in `sources/FETCHED-SOURCES.sha256`); `sources/*.txt` (branch `main`) is a superseded first fetch, kept only for provenance |
| `scratch/r94s_stim_*.wav` | seat-built deterministic stimuli (shas in `receipts/prep.json`) |

## Receipt index (stage → what it pins)

| receipt | legs | pins |
| --- | --- | --- |
| `prep.json` | 1 | stimuli shas; own-reader vs `sox -t f32 -` decode **max abs diff 0.0** (96000 floats) |
| `gain.json` / `gain_D.json` | 14 | gain/vol/norm laws; `vol` amplitude form = **ceil**, dB/power forms = nearest; `-D` exact |
| `rate.json` / `rate_D.json` | 27 | output-length law (±1 frame), pitch preservation, `-q` alias law, band rolloff |
| `remix.json` / `remix_D.json` | 12 | `remix 1` = L-select; auto downmix = `floor((L+R+1)/2)`; `-m` = L+R; `-p` = (L+R)/√2; selections bit-exact |
| `trim.json` / `trim_D.json` | 22 | sample-suffix `s`, `=`/`-`/`+` forms, rounding boundary matrix, refusals |
| `fade.json` / `fade_D.json` | 10 | 100 dB log law (both directions), curve tables, **stop-position truncation** |
| `repeat_pad_silence.json` / `_D.json` | 19 | `repeat` sample-exact tiling, `repeat 0` = identity, pad insertion, silence window lag |
| `dither.json` / `dither_D.json` | 15 | determinism matrix, `-R`/`-D` laws, guard non-limiter, 24-bit no-dither |
| `stat.json` | 10 | `stat`/`stats -j`/`stat -e` field definitions + ffmpeg ebur128 cross-check |
| `chain.json` / `chain_D.json` | 9 | effect order law, `norm` vs `--norm` 1 LSB, `vol` spellings differ by 1 LSB |

## Repro

```
cd corpus/live/r94-scout && ./run_all.sh        # ~25 s, writes receipts/ + runs/
python3 probes/r94_analyze.py all               # prints the report tables
sha256sum -c manifest.sha256                    # 3429 files
```

`manifest.sha256` covers `probes/`, `receipts/`, `sources/`, `runs/`
(3429 files; manifest sha256 `e072454f9fb977201cc39b4fb6fbb664d3eb20c15bb15acf1253efa2a4f7a8cd`).

## Safety ledger

- **File-only**: no PipeWire object created, no device opened; sox was never
  invoked with `-d`, `-p`, `play` or `rec`. The live graph was untouched by
  this seat.
- Sibling lanes live during the window: r93-scout filter-graph battery
  (`runs/battery.log`), r82 fold probe (`measure_audio.py --probe-ffmpeg-r82`),
  g2d/g3d lanes (host loadavg 27.6 at entry). Contention affects only wall
  times; every content law is process-local and was re-run 3–5× per leg.
- No `pactl`, no `pw-*`, no `wpctl`, no config/state writes.
