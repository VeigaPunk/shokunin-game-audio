# R94 boundary — SoX_ng v14.8.0.1 lattice replayed under load: 66 confirmed, 1 falsified

Round 94 **boundary** (executor seat, leaf). Attacks every pinnable claim in
`reports/round-94/r94-scout.md` by replaying its armed cells **under load
(16 own concurrent hogs) and quiet-ish**, with fresh-process reps, and by
varying the named independent axes.

Host `plazir27`, measurement window **2026-10-15 21:05:17Z → 21:11:19Z**
(host local UTC−3). Repo `~/Projects/shokunin/audio-shokunin`, HEAD
**`51a98e54`** at entry and **`25d89bdb`** at exit — two sibling commits landed
mid-window (`28cc128f r99 scout`, `25d89bdb r95 boundary`), neither of them this
seat and neither touching r94. The scout measured `2333fac`, so its report has
since been committed by a sibling (`cdacdc43 r94 scout: SoX_ng DSP lattice`) and
three rounds landed on top. Toolchain re-pinned: `sox` = **SoX_ng v14.8.0.1**
(`/usr/bin/sox` sha256 `646d899b53c1…` — unchanged), Python 3.14.7, numpy 2.5.3.

**Seat discipline.** Zero tracked-file writes; nothing committed. The only file
written outside `corpus/live/r94-boundary/` is this report. Every child is
triple-bounded (element bound in argv + wall cap + output-byte cap checked in the
loop that owns the process group; `start_new_session` + `os.killpg`,
`RLIMIT_CORE=0`). **File-only**: no PipeWire object created (0 `r94b_*` nodes and
0 modules at exit), no device opened, `sox` never invoked with
`-d`/`-p`/`play`/`rec`. **No global mutation**: no `pactl set-default-*`, no
`wpctl set-*`, no metadata write, no config write. Hogs are own PIDs only
(argv-marked `r94b_hog`, kill path re-verifies marker **and** `/proc/<pid>/stat`
start-time; final kill log `final_alive: []`, zero skipped entries) — the r95
namespace-blind-`sweep()` incident is the explicit precedent.

---

## 0. What was replayed, and the three boundary questions

The scout's 18 proposed rows and 15 headline claims were re-implemented
independently (`probes/r94b_driver.py`, own RIFF reader/writer, own metrics) and
run as **397 cells / 1 342 process reps** in two passes:

| pass | own hogs | loadavg1 over the 525 laws+axes reps (per-rep) | conc cells (cell-level) | host loadavg in-receipt |
| --- | --- | --- | --- | --- |
| quiet-ish | 0 | min 72.81 · p50 75.63 · max 78.23 · mean 75.29 | 78.23 → 78.23 | `76.86 74.72 76.71` |
| load | 16, held across the whole pass | min 107.99 · p50 109.14 · max 110.14 · mean 108.92 | 110.14 → 110.14 | `109.37 87.68 81.20` |

The three questions a boundary seat exists to ask:

1. **Is the law load-invariant?** → yes, 124/124 deterministic cells byte-identical
   across passes, 0 mismatches; the 7 dither cells are nondeterministic in *both*
   passes (nondeterminism is a property of the effect, not of the host).
2. **Is the law seat/time-invariant?** → yes, **87 deterministic legs reproduce the
   scout's exact output bytes** (same stimulus bytes, different seat, ~1 h later,
   different filenames, different load); the only 6 differing legs are exactly the
   time-seeded default-dither legs.
3. **Does any *independent axis* change the content?** → no: flag placement,
   PipeWire client env, the sox buffer knob, a foreign-driven default-node change,
   and 16-way process concurrency all leave the bytes alone.

---

## 1. Verdict table

68 verdicts. **66 CONFIRMED, 2 FALSIFIED** (R5 and R5b are the same claim attacked
two ways). Machine-readable: `receipts/verdicts.json`; rendered:
`runs/analysis-verdicts.txt`.

| id | verdict | claim |
| --- | --- | --- |
| D1 | CONFIRMED | default s16 effect output is nondeterministic (auto-dither) |
| D2 | CONFIRMED | `-D` makes gain -6 exact to ±0.5 LSB (mismatch vs rint = 0) and byte-stable |
| D3 | CONFIRMED | an explicit `dither` is nondeterministic (time-seeded RNG) |
| D4 | CONFIRMED | `-R` makes an explicit `dither` reproducible (1 sha) and cross-pass identical |
| D5 | CONFIRMED | `-D` does NOT fix an explicit `dither` (still >1 sha) |
| D6 | CONFIRMED | `-R -D` explicit dither output == `-R` explicit dither output (extension) |
| D7 | CONFIRMED | `dither -s` noise-shaping error envelope (max ~21-22 LSB, rms ~5.8) |
| D8 | CONFIRMED | f32→s16 conversion is nondeterministic by default |
| D9 | CONFIRMED | f32→s24 / f32→s32 are byte-stable (the `< 24` auto-dither clause) |
| D10 | CONFIRMED | `copy` is byte-identical to the input; `rate <same>` is SOX_EFF_NULL identity; `gain 0` is byte-identical (extension) |
| D11 | CONFIRMED | s16→s24 + gain is stable (output precision ≥ 24 suppresses auto-dither) |
| G1 | CONFIRMED | dB→factor is exact to ±0.5 LSB with `-D` (rint) |
| G2 | CONFIRMED | `vol` amplitude form rounds ceil; dB and power forms round to nearest |
| G3 | CONFIRMED | `vol 0.5` and `vol -6.0206 d` differ by exactly 1 LSB (not interchangeable) |
| G4 | CONFIRMED | `gain -n` normalizes the file peak to 0 dBFS; `-e`/`-b` lift both channels |
| G5 | CONFIRMED | `-h` reserves headroom that a following `gain -r` reclaims |
| R1 | CONFIRMED | rate output length reproduces the scout's matrix exactly and is within ±1 frame of in·out/in_rate |
| R2 | CONFIRMED | no single rounding rule fits the .5-boundary rows (rate approximates the ratio) |
| R3 | CONFIRMED | `-q` folds a 23 kHz tone to 21.1 kHz at ~-6.3 dB (content hazard) |
| R4 | CONFIRMED | at 20 kHz `-q` rolls off -3.9 dB where default/`-v` are flat |
| **R5** | **FALSIFIED** | report claim: 23 kHz `-v` rejects at -130 dB (scout §1.5 text) |
| **R5b** | **FALSIFIED** | same claim, dedicated 11-option × 2-stimulus × 3-rep probe, both passes |
| R6 | CONFIRMED | `-q -a` is refused ('override options only work at higher quality levels') |
| R7 | CONFIRMED | pitch is preserved at every resample rate (estimator-identical 996.8 Hz) |
| M1 | CONFIRMED | `remix 1` selects L (does not downmix) |
| M2 | CONFIRMED | auto downmix = floor((L+R+1)/2); `channels 1` ≡ auto |
| M3 | CONFIRMED | `-m 1,2` = exact L+R; `-p 1,2` = rint((L+R)/√2) |
| M4 | CONFIRMED | channel selection/swap/upmix are bit-exact |
| T1 | CONFIRMED | `s` suffix means samples (`1s` = 1 frame, `4800s` = 4800 frames) |
| T2 | CONFIRMED | `1sec` / `0.1s` / `1e-9` are refused (rc 1); `trim 0 0` is a valid 0-frame WAV |
| T3 | CONFIRMED | trim rounding boundary matrix (round(len·rate) follows float32) |
| T4 | CONFIRMED | trim forms: `-0.1` drops the tail, `=0.1` absolute end, `0.05+0.05` = 0.1 s to EOF |
| T5 | CONFIRMED | trim content is sample-exact (output == first 4800 frames of input) |
| F1 | CONFIRMED | `fade` truncates the output at the stop position (silent data loss) |
| F2 | CONFIRMED | log fade = exactly 100 dB across the span (gain 0.003169 @x=.5, 0.056235 @x=.75) |
| F3 | CONFIRMED | curve table matches (q/h/t/l/p/s at x=.25/.5/.75) and default type = l |
| F4 | CONFIRMED | first frame of a fade is 0 under `-D` |
| P1 | CONFIRMED | `repeat N` = N additional sample-exact copies; 0 = identity; negative refused |
| P2 | CONFIRMED | `pad %50` is a silent no-op — and the output is byte-identical to the input |
| P3 | CONFIRMED | `pad <len>@<pos>` inserts at a sample position; `pad len1 len2` = head+len1+len2 |
| P4 | CONFIRMED | silence below-periods keeps window_size-1 = 959 frames; `-l` keeps 959+duration |
| P5 | CONFIRMED | silence threshold units 1%/0.01/-60d all accepted; `silence 0 …` refused |
| S1 | CONFIRMED | `stat` RMS amplitude is the per-channel quadratic mean; delta fields are interleaved; Rough frequency 10803 |
| S2 | CONFIRMED | `stat -e` yields EBU R128 momentary/short-term; Integrated only on the 1 s file |
| S3 | CONFIRMED | lane-canonical ffmpeg ebur128 gates to -70 LUFS on the same 0.25 s file |
| S4 | CONFIRMED | stat text is byte-stable across reps and across load (extension) |
| C1 | CONFIRMED | effect order is semantics: `gain -6 norm -3` → -3.0 dB; `norm -3 gain -6` → -9.0 dB |
| C2 | CONFIRMED | `norm` (0 dBFS peak 32767) and global `--norm` (-0.0003 dB, 32666) differ by 1 LSB |
| X1 | CONFIRMED | `-G` is not a limiter: clipping counts are equal with and without it |
| AX-D_between_in_out | CONFIRMED | `-D` between infile and outfile yields byte-identical output |
| AX-D_after_out_before_effect | CONFIRMED | `-D` after the outfile, before the effect, yields byte-identical output |
| AX-no_dither_longform | CONFIRMED | `--no-dither` yields byte-identical output |
| AX-D_R_order | CONFIRMED | `-D -R` yields byte-identical output |
| AX-R_D_order | CONFIRMED | `-R -D` yields byte-identical output |
| AX-D-after-effect | CONFIRMED | `-D` after the effect name is NOT a global option (rc 1, `gain` usage) |
| AX-R-after-effect | CONFIRMED | `-R` after the effect name is NOT a global option (rc 1, `dither: invalid option`) |
| AX-R-after-infile | CONFIRMED | `-R` between infile and outfile is accepted and reproduces the canonical `-R` bytes |
| AX-PWENV | CONFIRMED | PipeWire client-config axes (QUANTUM/RATE/LATENCY/NODE, PULSE_SINK/SOURCE) do not change sox file output |
| AX-BUFFER | CONFIRMED | sox `--buffer`/`--input-buffer` do not change gain/rate/silence output |
| CONC-1 | CONFIRMED | 16 concurrent `-D` processes produce one identical output |
| CONC-2 | CONFIRMED | 16 concurrent `-R dither` processes produce one identical output |
| CONC-3 | CONFIRMED | 16 concurrent default `gain -6` processes are mutually nondeterministic (16/16 shas) |
| CONC-4 | CONFIRMED | 16 concurrent `rate 44100` processes produce one identical output |
| LOAD-1 | CONFIRMED | every deterministic content law is byte-identical under load (quiet sha set == load sha set) |
| LOAD-2 | CONFIRMED | nondeterminism is a property of the effect, not of the load |
| XSEAT-1 | CONFIRMED | 87 deterministic legs reproduce the scout's exact output bytes (different seat, ~1 h later) |
| XSEAT-2 | CONFIRMED | the `-R` dither stream is byte-identical across seats and passes |
| HOG-1 | CONFIRMED | load pass really held ≥12 own concurrent hogs, all argv-marked and all reaped |

---

## 2. The falsified claim — exact receipts

**Claim as written** (`reports/round-94/r94-scout.md` §1 claim 5):
*"The `-q` resampler is a content hazard: a 23 kHz tone folds to 21.1 kHz at
−6.3 dB. **Default (`-h`) and `-v` reject it at −84/−130 dB**; `-a` alone
(default quality) leaves −86 dB; `-m -a` leaves −73 dB."*

**Why it was already unpinnable:** the scout's own `receipts/rate_D.json` contains
**no 23 kHz `-v` leg** — the 23 kHz option loop is
`default, alias_a, q, q_alias_a, m_alias_a` only, and `runs/analysis-rate.txt`
has no `rate44100_23k_v` row. The −130 dB figure exists in the scout's own table
only as `band21.1k=-129.576` for the **20 kHz** stimulus default leg.

**Direct replay** (`runs/analysis-scout-cross.txt`, `laws-*`, and the dedicated
`r5-*` receipts, 3 fresh processes per option per pass, own 10 Hz-half-width DFT):

| cell | band @21.1 kHz | whole-output peak | sha256[:16] |
| --- | --- | --- | --- |
| `rate44100_23k_default` | **−104.385934 dB** | **−84.288399 dB** | `8f842d06847b13e5` |
| `rate44100_23k_h` | −104.385934 dB | −84.288399 dB | `8f842d06847b13e5` (≡ default) |
| `rate44100_23k_v` | **−104.385935 dB** | **−84.288399 dB** | `51aa41a12e1fd324` |
| `rate44100_23k_u` | −104.385935 dB | −84.288399 dB | `51aa41a12e1fd324` (≡ `-v`) |
| `rate44100_23k_q` | −6.289203 dB | −6.172481 dB | `adb5b6f393fb8d19` |
| `rate44100_23k_a` | −86.300366 dB | −80.766574 dB | `62e75ffb542b9ef0` |
| `rate44100_23k_m_a` | −73.494 dB | −78.267800 dB | `569e862115f69c56` |
| `rate44100_20k_default` | **−129.576210 dB** | −6.021130 dB | `7b9150613043908c` |

**Verdict: FALSIFIED.** `-v` does not reject the 23 kHz alias at −130 dB; it sits
at **−104.386 dB (21.1 kHz band) / −84.288 dB (peak)**, indistinguishable from
default and `-h` to ≤1e-6 dB. `-v` and `-u` *are* byte-distinct from default
(`51aa41a1…` vs `8f842d06…`), so they are a different filter — just not a
different rejection level. The −129.576 dB figure belongs to the **20 kHz**
stimulus default leg, and −84.288 dB is the *peak*, not the alias band, of the
same 23 kHz leg; the claim text conflates three metrics/stimuli.

**Armable corrected form** (what an author should write):

- `rate44100_23k_default` → `peak_db = −84.2884`, `band_21100hz_db = −104.386`
  — identical for `-h` (same bytes) and for `-v`/`-u` (different bytes).
- The content hazard is `-q` only: `band_21100hz_db = −6.289` (folded to 21.1 kHz),
  with `-a` at −86.3 dB and `-m -a` at −73.494 dB.
- Do **not** arm "−130 dB" for any 23 kHz leg; the only ≈−129.6 dB row in the
  lattice is the 20 kHz stimulus default leg at the 21.1 kHz band.

Both passes agree to 1e-6 dB and the `-v`/`-u`/`-h`/default shas are identical
across the quiet and load passes (`r5: 20 identical across load, 0 differing`).

---

## 3. Load vs quiet-ish: how the condition was built and evidenced

- **16 own hogs**, one per process, argv-marked `r94b_hog`, held across the whole
  load pass (`witness → laws → axes → conc`), warm-up 90 s before the first leg so
  the 1-min loadavg reflects them.
- Lifecycle receipt `runs/load/hogs-all.json`: 16 PIDs, `marker_ok` on all,
  `final_alive: []`, no skipped/mismatched kill entries.
- **CPU accounting** (new in this seat): 16 hogs consumed **542.78 CPU-seconds**
  over the 133 s pass (33.9 CPU-s each) ⇒ ≈ **4.1 CPU-equivalents** of added
  demand. On a host already carrying ~75 runnable tasks on 32 CPUs, each hog got
  only ~25 % of a core.
- Loadavg trace: 78.23 before → 107.99 after warm-up → 110.14 at stop. **The
  quiet→load delta is therefore not attributable to this seat alone**: the host's
  foreign load also rose inside the window (see §7). The honest statement is
  "16 own CPU-bound processes were concurrently resident for the entire load pass,
  adding ~4 CPU-equivalents; the content result is invariant".
- **"Quiet-ish" is honest**: there is no quiet window on this host during the
  window — the quiet pass carried 0 own hogs but ~72–78 foreign runnable tasks.

---

## 4. Independent axes

| axis | how varied | result |
| --- | --- | --- |
| **CLI flag order** | `-D` before infile / between infile and outfile / after outfile before the effect / `--no-dither` / `-D -R` / `-R -D` | all **byte-identical** (`d011774f2a3f0466…`) |
| **CLI flag position, out of grammar** | `-D` after `gain -6`; `-R` after `dither` | both **refused, rc 1** (`gain` usage / `dither: invalid option '-R'`) — gopts stop at the first effect |
| **PipeWire rates/quantum** | per-process `PIPEWIRE_QUANTUM` 32/64/2048/8192, `PIPEWIRE_RATE` 44100/96000, `PIPEWIRE_LATENCY` 64/48000, `PIPEWIRE_NODE`, `PULSE_SINK`, `PULSE_SOURCE`, and an all-at-once combination | 10 variants × {gain, rate}: **byte-identical** to the no-env control, in both passes |
| **Global PipeWire settings (read-only witness)** | `clock.rate 48000`, `clock.allowed-rates [48000]`, `clock.quantum 1024`, `force-quantum 0`, `force-rate 0` | unchanged at every receipt; never written |
| **Default-node state** | **varied by foreign seats, witnessed read-only** — 5 distinct default sinks/sources during the window: `…hdmi-stereo.6` → `…hdmi-stereo.89` → **`r96b_ns`** → `…SPDIF__sink.24` → `…hdmi-stereo.99`; source flipped to `@DEFAULT_SOURCE@` and back | no effect on any file leg: 124/124 deterministic cells identical across the window, 87/87 cross-seat shas identical. **This seat issued no `set-default-*`** |
| **Sibling seat presence** | 30–35 foreign seat processes + 60–64 foreign `yes` processes + 11–14 foreign `r9Xb_*` PipeWire nodes live throughout; a second PipeWire instance runs with the r97-boundary seat's own config | no content effect; wall time only (laws `wall_s` p50 0.0268 s quiet vs 0.0288 s load, mean 0.0294 vs 0.0331, max 0.245 vs 0.197) |
| **sox internal buffers** (extension; the sox analogue of a quantum knob) | `--buffer` 1024/4096/16384, `--input-buffer 4096` on gain / rate / silence | **byte-identical** for gain and rate; silence trailing-zero law unchanged (959) |
| **Process concurrency** (extension) | 16 simultaneous fresh `sox` processes per cell | `-D` gain: **1 distinct sha/16**; `-R dither`: **1/16**; `rate 44100 -D`: **1/16**; default `gain -6`: **16/16**; default `dither`: **16/16** |

---

## 5. Extensions the scout did not pin

1. **Cross-seat byte identity.** All 9 stimuli rebuilt from the scout's definitions
   hash-match its `prep.json` (9/9), and **87 deterministic legs reproduce its
   exact output bytes** across seats/time/filenames/load. The only 6 differing
   legs are precisely the time-seeded default-dither legs
   (`gain_m6_default`, `f32_to_s16_plain`, `dither_explicit_default`,
   `dither_explicit_D`, `gain_p12_default`, `gain_p12_G_default`) — i.e. the
   determinism law predicts its own mismatches.
2. **`-R` is a *stream*, not just a length.** `dither -s -R` reproduces the scout's
   output byte-for-byte and its error RMS to the last digit
   (`5.740680853928971` on both sides), and is identical in both passes.
3. **`-R -D` ≡ `-R`** for an explicit dither (`3b6c7ea83ff31da0…`): `-D` only
   suppresses the *automatic* dither.
4. **`gain 0` and `pad %50` are byte-identical to the input**, not merely
   "stable" / "no padding added" — `80241968ffe7e28e…` and `6a2a6b0cad8058ad…`
   equal the stimulus shas exactly.
5. **`stat` text is byte-stable** across reps and across load (stream sha 1/1 in
   both passes).
6. **`-q -a` is a hard refusal** (`override options only work at higher quality
   levels`, rc 1), so `-a` alone is the only `-a` form that runs on the 23 kHz
   stimulus — worth arming, since the scout's §5 note treats `-a` as "unvalidated".
7. **`-l` (low quality) is the real 20 kHz hole**: `band_20000hz_db = −23.021`
   (the tone is attenuated 23 dB) while `-a` is flat there (−0.0006 dB) with the
   best alias rejection of the set (−142.180 dB at 21.1 kHz). Neither row is in
   the scout's curve table.

---

## 6. Imprecisions that are *not* falsifications (arm them differently)

- **D3 "error RMS 5.8 LSB"** — the scout's own `dither_D.json` shows `5.7407` for
  `f32_to_s16_dither_s_R` (exactly my value) and `5.8287/5.8555` for the
  non-`-R` legs. The "5.8" is the *nondeterministic* leg; arm 5.7407 with `-R`.
- **X1 "4 022 vs 7 979 at the ≥32767 threshold"** — dither-dependent, as the scout
  says; my default-path replay gives **7 979 vs 3 989**. Only the `-D` equality
  (7 979 / 7 979 at ≥32 766) is reproducible. Arm the `-D` row.
- **§1.5 mixes three metrics and two stimuli** for the same leg (peak −84.29,
  band-21.1 k −104.39, band-20 k −129.56) — the root cause of the R5 falsification.
  Name the metric in every rate row.
- **R1's "no single rounding rule"** survives an independent check: for the three
  `.5` rows (5512.5→5512, 5513.5→5514, 6012.5→6013) none of floor / half-up /
  half-even / ceil fits all three (`rules_that_fit_all: []`). Arm ±1 frame.

---

## 7. Contention ledger (foreign, disclosed)

| window | contact | effect |
| --- | --- | --- |
| whole window | **60–64 foreign `yes` processes** (r89-verify load generator, gated on `procs_running`) | loadavg 72–78 baseline; wall times inflated; no content effect |
| whole window | foreign seats live: r90-author (`hunt_greens.sh`, godot), r89-verify (godot crash arms), r92-boundary (`r92b_in`, `r92b_fc_in/out`, `r92b_rec`, `r92b_ref`), r93-boundary (`r93b_*`), r95-boundary (`r95b_*`), r96-boundary (`r96b_ns`, `r96b_pulse_trigger`), r97-boundary (**a second PipeWire instance** with its own config), r98-boundary (`r98b_*`), r99-scout | live graph not ours; read-only witnesses only |
| whole window | **foreign default-node mutations**: 5 distinct default sinks incl. the virtual `r96b_ns`; source flipped to `@DEFAULT_SOURCE@` | **used as the default-node-state axis** (varied without this seat mutating anything) |
| whole window | sibling sink-inputs/source-outputs 1–4 / 0–2 (r92-boundary streams) | why the global `set-default-sink` toggle was **not** performed |
| 21:09:10Z | foreign tracked write: `corpus/fixtures/measure_audio.py` +2 263 lines (sibling-owned) | tracked-dirty at exit is **not** this seat; the file was never read, imported or executed here (the only mention of its name in this seat is a read-only `ps` census regex) |
| own | 16 `r94b_hog` processes, 133 s, 542.78 CPU-s | 0 PipeWire objects, 0 modules, all reaped |

Exit state: HEAD moved by siblings (`51a98e54` → `25d89bdb`, neither commit this
seat), tracked-dirty set = the sibling's `measure_audio.py` only,
`corpus/live/r94-boundary/` + this report untracked, 0 `r94b_*` nodes and
0 `r94b_*` processes.

---

## 8. Limits, residual risk, blockers

1. **No truly quiet window exists on this host** (60–64 foreign `yes` processes
   plus ≥8 sibling batteries). "Quiet-ish" = *0 own hogs*; it is not a quiet
   machine, and the load arm added only ~4 CPU-equivalents because the host was
   already ~2.3× oversubscribed. A load claim stronger than "16 concurrent
   CPU-bound processes were resident" is not supportable from this window.
2. **The loadavg delta is not cleanly attributable to this seat** (foreign load
   rose inside the window: 78 → 110). CPU accounting is the honest evidence.
3. **Global default-node toggle was deliberately not exercised** (sibling streams
   live; province precedent from r95). The axis is covered only by (a) witnessing
   five foreign mutations and (b) per-process env overrides.
4. **Reps are 3–5 per cell**, and the rounding laws are verified on one stimulus
   family — not on all bit patterns. `vol`'s exact integer path was not read
   line-by-line (as the scout also noted).
5. **The scout's exploratory (undisked) pass** may have produced the −130 dB
   figure; only its on-disk pass is falsifiable, and only that pass was replayed.
6. **`-R` stream identity is a measurement, not a derivation**: it shows the PRNG
   stream is fixed for this build, not *why*.
7. **Not judged here**: nothing in this report is a shipping decision; the
   canonical Rust runtime remains the only judge, and no `--probe-sox-r94` row was
   added or modified by this seat.

## 9. Artifacts & repro

`corpus/live/r94-boundary/` (untracked): `probes/` (6 files), `receipts/` (13 JSON,
incl. `verdicts.json`), `runs/` (per-rep `cmd`/`stdout`/`stderr`/`meta.json` +
`analysis-lattice.txt` / `analysis-scout-cross.txt` / `analysis-verdicts.txt` +
`run-all.log` + `hogs-all.json`), `scratch/` (stimuli + outputs), `RECEIPTS.md`,
`manifest.sha256` — **6 518 files / 93.4 MB, `sha256sum -c` verified 6 518/6 518 OK,
manifest sha256 `09e76b0d10c492b5b1bdd89bcff53c249cda4544f8471db0b4c98957b06ad838`**.

```
cd corpus/live/r94-boundary && ./run_all.sh      # ~6 min, single repro path
python3 probes/r94b_analyze.py                   # verdict table
python3 probes/r94b_manifest.py && sha256sum -c manifest.sha256
```

*boundary leaf — replayed, varied, falsified where the receipts demanded it; not judged.*
