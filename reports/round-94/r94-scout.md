# R94 scout — SoX_ng v14.8.0.1 effect/DSP lattice: the unscouted half of the province's own toolchain

Round 94 pre-measurement. Host `plazir27`, measured **2026-10-15 19:39:12Z →
19:47:29Z** (host local UTC−3): three battery passes — a first exploratory
pass, the full default+`-D` pass (receipts on disk, 19:44), then a second
`-D`-only pass as the cross-run reproducibility control (19:46–19:47). Repo
`~/Projects/shokunin/audio-shokunin`,
HEAD **`2333fac`** (`r82 baseline: 86/136 x2 frozen…`), tracked-dirty at entry
and exit = the sibling-owned `corpus/fixtures/measure_audio.py` +
`__pycache__` (never read, imported or executed here). Toolchain pinned:
`sox` = **SoX_ng v14.8.0.1** (`/usr/bin/sox` sha256 `646d899b53c1…`,
`libsox_ng.so.3` sha256 `8d7fee4875…`), Python 3.14.7, numpy 2.5.3, Linux
7.2.3-arch1-3.

**Seat: SCOUT (leaf). Zero tracked-file writes; the only file written outside
`corpus/live/r94-scout/` is this report. Not committed.** Every leg is
triple-bounded (element bound in argv + wall cap + output-byte cap checked in
the same loop that owns the process group; `start_new_session` + `os.killpg`,
`RLIMIT_CORE=0`). **File-only: no PipeWire object was created, no device was
opened; `sox` was never invoked with `-d`/`-p`/`play`/`rec`.** Own stimuli, own
RIFF reader (sox never sits in the measurement path of a sox output; control
leg: own reader vs `sox -t f32 -` = **max abs diff 0.0** over 96 000 floats).

**Label legend.** `[O]` = directly observed on this host in this window.
`[I]` = read from the **version-matched upstream source** fetched from Codeberg
tag **`sox_ng-14.8.0.1`** (shas in `sources/FETCHED-SOURCES.sha256`), or
inferred from measured laws. `[?]` = not resolved by this seat.

---

## 0. Why this surface (the pick, and what it displaces)

The r94 brief excludes gst↔PW (r81), ffmpeg↔PW (r82), filter-chain DSP (r92)
and r93's in-flight filter-graph internals; r95's brief claims JACK↔PW interop
and ALSA-direct hw negotiation. The province's declared toolchain is
*"ffmpeg, ffprobe, sox"* (`corpus/knowledge/seed.md`), and the seed assigns sox
the roles *"scriptable synthesis…, precise trimming, concatenation"*. Rounds
r62–r75 measured sox only as a **decoder/detector** (`sox --i`, `sox -V6 -n
stat`, transport forks). **Not one sox *effect* row exists anywhere in
`corpus/knowledge/`, `reports/` or the receipts** — no `gain`, `vol`, `norm`,
`rate`, `remix`, `trim`, `fade`, `repeat`, `pad`, `silence`, `dither` or
`stat`-field law. That is the province's own content-production half, unscouted.

The pick is also **zero-contention**: r93's filter-graph battery, the r82 fold
probe and g2d/g3d lanes were live throughout (loadavg 27.6 at entry), and every
r94 leg is a process-local file transform whose content is load-independent —
3–5 reps per leg were byte-compared, not time-compared.

**Headline: sox is bit-reproducible only when nothing changes the samples, or
when `-D`/`-R` is passed. Every default 16-bit effect that alters a sample
silently adds time-seeded TPDF dither — and the reason is a precision-tracking
rule in `effects.c`, not a dither option.**

---

## 1. Headline claims

| # | claim | label | sharpest single fact | evidence |
| --- | --- | --- | --- | --- |
| 1 | **Auto-dither is a precision-tracking consequence, and it makes default s16 effect output nondeterministic.** Auto-dither is inserted iff (no user `dither` in the chain) ∧ ¬`-D` ∧ tracked precision > output precision ∧ output precision < 24. Effects bump tracked precision to 32 unless they set `SOX_EFF_MODIFY`, or *explicitly preserve* it for integer/unity operations, or return `SOX_EFF_NULL`. | `[O]`+`[I]` | `sox in.wav out.wav gain -6` → **3 distinct shas / 3 reps**; `sox -D … gain -6` → **1 sha, mismatch vs `rint(x·10⁻⁶ᐟ²⁰)` = 0**; `gain 0` (fixed_gain = 1.0, integer) → byte-identical to input; `trim`/`repeat`/`pad`/`silence`/`copy`/`remix 1`/`remix -m 1,2`/`rate 48000` → byte-stable in both passes | `receipts/dither.json`+`_D.json`, `receipts/gain_D.json`; `src/effects.c:143-145`, `src/sox_ng.c:1132-1134`, `src/gain.c:93-95`, `src/remix.c:164-166`, `src/rate.c:874-875` |
| 2 | **The default RNG is time-seeded; `-R` (not `-D`) is what makes an *explicit* `dither` reproducible.** | `[O]`+`[I]` | `… dither` ×5 reps → **5 shas**; `sox -R … dither` → **1 sha**; `-D` does **not** fix an explicit `dither` (still 5 shas) — it only suppresses the *automatic* one | `receipts/dither.json` L2–L5; `src/sox_ng.c:2578-2580` (`repeatable`), `:3288` (`ranqd1 = now.tv_sec − now.tv_usec`) |
| 3 | **`gain` is exact to ±0.5 LSB under `-D`; the `vol` *amplitude* form rounds differently (ceil) and is not interchangeable with `vol <dB> d`.** | `[O]` | `gain -6` → mismatch 0 vs `rint`; `vol 0.5` → mismatch **0 vs `ceil`**, 23 000 vs `rint`; `vol -6.0206 d` → mismatch 0 vs `rint`; `vol 0.5 p` → mismatch 0 vs `rint`; the two `vol` spellings differ by **1 LSB** (max abs diff 3.05e-05) | `receipts/gain_D.json` (vol rows), `receipts/chain_D.json` `vol_forms_equivalence` |
| 4 | **`rate` output length is ±1 frame around `in·out/in_rate` and no simple rounding rule fits all rates; same-rate is a true no-op; pitch is preserved.** | `[O]` | 12 000 → 11 025 @44 100 (exact), 12 001 → **11 026**, 12 000 → **5 512** @22 050 (exact 5512.5), 12 000 → **6 013** @24 050 (exact 6012.5), 12 000 → 2 756 @11 025; `rate 48000` output **byte-identical to input**; tone stays 996.8 Hz (estimator-biased, identical before/after) | `receipts/rate_D.json`; `src/rate.c:874-875` (`SOX_EFF_NULL` when in_rate == out_rate) |
| 5 | **The `-q` resampler is a content hazard: a 23 kHz tone folds to 21.1 kHz at −6.3 dB.** Default (`-h`) and `-v` reject it at −84/−130 dB; `-a` alone (default quality) leaves −86 dB; `-m -a` leaves −73 dB. At 20 kHz, `-q` rolls off −3.9 dB where `-h`/`-v` are flat (−0.001/−0.002 dB). | `[O]` | `rate -q 44100` on a 23 kHz 0.5 FS tone: band 21 100 Hz = **−6.289 dB**, output peak −6.17 dB (input peak −6.02) | `receipts/rate_D.json` (`23k*`, `20k*` rows) |
| 6 | **`remix` is select/sum/mix with a documented auto-gain — and the auto downmix rounds half-up, not to nearest-even.** | `[O]`+`[I]` | `remix 1` = **L only** (mismatch 0 vs L); `remix 1,2` = `floor((L+R+1)/2)` (mismatch **0**; nearest-even is off on 17 000/48 000); `-m 1,2` = exact `L+R`; `-p 1,2` = `rint((L+R)/√2)`; `channels 1` ≡ auto downmix | `receipts/remix_D.json`; `src/remix.c:102-105` (`mult = 1/(mix_power? √j : j)`) |
| 7 | **`trim`'s `s` suffix means *samples*, `1sec` is a hard refusal, and lengths round to nearest frame.** | `[O]` | `trim 0 1s` → **1 frame**; `trim 0 4800s` → 4 800; `trim 0 0.1s` → rc=1 `cannot parse position '(null)'`; `trim 0 1sec` → rc=1; `trim 0 0` → **0-frame valid WAV, rc 0**; `trim 0 1e-9` → rc=1; `trim 0 -0.1` → 7 200; `trim 0 =0.1` → 4 800; `trim 0.05+0.05` → 7 200 (0.1 s to EOF, not 0.05 s) | `receipts/trim_D.json` |
| 8 | **`fade` silently truncates the output at the stop-position and the log curve spans exactly 100 dB in both directions.** | `[O]`+`[I]` | `fade 0 0.15 0.1` on a 0.25 s file → **7 200 frames** (truncated at 0.15 s); `fade 0 0.25 0.1` → 12 000; `fade 0 0.2 0.05` → 9 600; log gain at x=0.5 = 0.003169 (−49.98 dB), at x=0.75 = 0.056235 (−25.00 dB), fade-out mirrored | `receipts/fade_D.json`; `src/fade.c:18-19,376-379` (`pow(0.1,(1-x)·5)` — *"5 means 100 db attenuation"*) |
| 9 | **`repeat` is sample-exact concatenation (the loop-seam primitive), `repeat 0` is identity, negative counts refuse.** | `[O]` | `repeat 2` → 36 000 frames, `out[n] == in[n mod 12000]` mismatch **0**; `repeat 1` → 24 000; `repeat 0` → 12 000 (identity); `repeat -1` → rc=1 `must be from 0 to 4.29497e+09` | `receipts/repeat_pad_silence_D.json` |
| 10 | **`silence`'s detectors are windowed-RMS; the below-periods trim lags the true silence start by `window_size − 1` samples, `-l` leaves one extra `duration`.** | `[O]`+`[I]` | window = `(rate/50)·channels` = 960 → trailing trim keeps **959** frames of silence; `-l` keeps 959 + 4 800 = **5 759**; leading trim cuts at frame 4 804 (tone starts 4 800); `silence 0 0.1 1%` → rc=1 `below-periods requires a duration and a threshold`; threshold units `1%`, `0.01`, `-60d` all accepted | `receipts/repeat_pad_silence_D.json`; `src/silence.c:264-265` |
| 11 | **`stat`'s "RMS amplitude" is the per-channel quadratic mean (total RMS/√channels), and its "delta" fields run over the interleaved stream — not per channel.** | `[O]` | stereo L 0.5 / R 0.25 sines: `RMS amplitude 0.279509` = `sqrt((0.35355²+0.17678²)/2)` (total RMS is 0.39528); `Maximum delta 0.728180` = max interleaved `abs(L−R)`, while each channel's own max sample-delta is ≤0.0655; `Rough frequency 10803` for a stereo file | `receipts/stat.json` `stat_plain_a`/`stat_j_a` |
| 12 | **sox `stat -e` yields EBU R128 momentary/short-term figures where the lane's canonical ffmpeg `ebur128` gates to the −70 LUFS floor on short SFX.** | `[O]` | same 0.25 s mono 0.5 FS file: ffmpeg `I = −70.0 LUFS` (gated floor, `LRA 0.0`); sox `EBUR128 Momentary −11.071128`, `Short term −19.821741`, `True Peak 0.500332`; on a 1 s stereo file sox adds `Integrated −7.752591` | `receipts/stat.json` `ffmpeg_ebur128_b`, `stat_e_b`, `stat_e_a` |
| 13 | **`-G` is not a limiter: it does not prevent clipping.** | `[O]` | `gain 12` on a 0.5 FS tone: **7 979 samples ≥ 32 766 with and without `-G`**; the apparent 4 022 vs 7 979 split at the `≥32767` threshold is dither quantization at the rail (`-D` pass: 7 979 / 7 979 for both) | `receipts/dither.json` + `_D.json` (`guard` rows) |
| 14 | **Effect order is semantics; `norm` and the global `--norm` are 1 LSB apart.** | `[O]` | `gain -6 norm -3` peak −3.0000; `norm -3 gain -6` peak −8.9996; `norm` (0) peak **0.0 dB** (32 767) vs `--norm` peak **−0.0003 dB** (32 666); `gain 6 -G norm -3` peak −3.0 (no clip) | `receipts/chain_D.json` |
| 15 | **`pad %50` is a silent no-op; `pad <len>@<pos>` inserts at a sample position.** | `[O]` | `pad 0.1 0.2` → 26 400 = 4 800+12 000+9 600, content at 4 800…16 799; `pad 0.05@0.05` → 14 400 with 2 400 zero frames at 2 400…4 799; `pad %50` → **12 000 frames, zero padding added, no warning, rc 0** | `receipts/repeat_pad_silence_D.json` |

---

## 2. The determinism law (why every hash-pinned fixture builder must care)

The province's whole discipline is "reproducibly synthesize" + sha-pinned
artifacts. SoX's default 16-bit path breaks that for *any* sample-changing
effect, and the mechanism is version-matched source `[I]`:

| step | anchor (tag `sox_ng-14.8.0.1`) | verbatim |
| --- | --- | --- |
| an effect without `SOX_EFF_PREC` sets its output precision | `src/effects.c:143-145` | `if (!(effp->handler.flags & SOX_EFF_PREC)) effp->out_signal.precision = (effp->handler.flags & SOX_EFF_MODIFY)? in->precision : SOX_SAMPLE_PRECISION;` |
| `gain` opts back down only for integer gain factors | `src/gain.c:93-95` | `else if (p->fixed_gain == floor(p->fixed_gain) && !p->do_scan) effp->out_signal.precision = effp->in_signal.precision;` |
| `remix` opts back down only when every multiplier is an integer | `src/remix.c:164-166` | `if (!non_integer) effp->out_signal.precision = effp->in_signal.precision; else effp->out_signal.precision = SOX_SAMPLE_PRECISION;` |
| same-rate `rate` is a true no-op | `src/rate.c:874-875` | `if (effp->in_signal.rate == out_rate) return SOX_EFF_NULL;` |
| auto-dither insertion | `src/sox_ng.c:1132-1134` | `if (i == nuser_effects[…] && !no_dither && signal.precision > ofile->ft->signal.precision && ofile->ft->signal.precision < 24) auto_effect(chain, "dither", 0, NULL, &signal, &guard);` |
| RNG seed | `src/sox_ng.c:3288`, `:2578-2580` | `sox_globals.ranqd1 = (int32_t)(now.tv_sec - now.tv_usec);` … `case 'R': sox_globals.repeatable = sox_true;` |

Measured consequences (3–5 reps per leg, `receipts/dither*.json`):

- `gain -6`, `gain ±n`, `gain -e/-b`, `vol *`, `rate *` (except same-rate),
  `remix` auto/`-p`/`-v`, `fade *`, `channels 1` → **3 distinct shas / 3 reps**
  (default) vs **1 sha** with `-D`.
- `gain 0`, `copy`, `trim *`, `repeat *`, `pad *`, `silence *`, `remix 1`,
  `remix 2 1`, `remix 1 1`, `remix -m 1,2`, `rate 48000` → **stable in both
  passes** (precision preserved or `SOX_EFF_MODIFY`/`SOX_EFF_NULL`).
- `f32→s16` conversion → 5 shas/5 reps default, 1 sha with `-D`; `f32→s24`,
  `f32→s32`, `s16→s24+gain` → stable (the `< 24` clause).
- An **explicit** `dither` effect is *not* fixed by `-D`; only `-R` fixes it.

**Cross-run reproducibility control:** the whole `-D` pass was re-run a second
time (independent battery, same host): **125/127 legs byte-identical across
runs; the only two that changed are the explicit `dither` legs without `-R`**
(`f32_to_s16_dither`, `f32_to_s16_dither_s`) — exactly what the law predicts
(`-D` does not suppress an explicit dither; the RNG is time-seeded). Every
`_R` leg stayed identical.

**Author consequence:** a probe/battery that wants byte-pinned sox output must
pass `-D` (exact, no dither) for math rows, and must *expect* nondeterminism
(and assert it) for default rows; `-R` is the reproducibility flag for
deliberate dither.

---

## 3. Author-ready cells (each with the falsifier actually tried)

Format: **claim** · **evidence** · **falsifier attempted** · **residual risk**.
All receipts carry per-rep shas, argv and parsed metrics; tables regenerated by
`python3 probes/r94_analyze.py all` → `runs/analysis-*.txt`.

### 3.1 gain / vol / norm
- **G1 — dB→factor is exact to ±0.5 LSB with `-D`.** `gain -6` on a stereo
  s16 stimulus: mismatch 0/96 000 vs `rint(x·10^(−6/20))`, `maxdiff 0`, peak
  −12.0211/−18.0406 dB (formula −12.0206/−18.0412). *Falsifier tried:* two
  rounding candidates (rint vs floor/ceil) — only `rint` matches; default path
  mismatch 30 734 with maxdiff 1 (dither). *Residual:* only 3 reps and one
  stimulus family; rounding verified on 96 000 samples but not on all bit
  patterns.
- **G2 — `vol` amplitude form rounds **ceil**; power and dB forms round to
  nearest.** mismatch `ceil` = 0 vs `rint` = 23 000 for `vol 0.5`;
  `vol 0.5 p` → `rint` = 0; `vol -6.0206 d` → `rint` of the dB formula = 0.
  *Falsifier tried:* floor/trunc/rint/ceil candidate matrix on both channels.
  *Residual:* the exact integer path (`(int)` cast in the 32-bit domain) was
  not read line-by-line; the empirical rule holds for this build.
- **G3 — `norm` vs `--norm` differ by 1 LSB** (0.0 vs −0.0003 dB peak);
  `norm -3` after `gain -6` gives −3.0 dB (order-dependent, see §3.8).
- **G4 — `gain -n` normalizes the file peak to 0 dBFS (32 767, not 32 768);
  `-h` reserves headroom that a following `gain -r` reclaims (`-h -6` ≡ −6 dB,
  `-h -6` + `gain -r` ≡ 0 dB).** `gain -e`/`-b` lift both channels to the max
  channel (R ×2, measured −6.0206 dB both channels).

### 3.2 rate
- **R1 — length law.** Measured matrix (in frames @48 k → out):

  | in | out rate | exact | measured |
  | --- | --- | --- | --- |
  | 12 000 | 44 100 | 11 025.00000 | **11 025** |
  | 12 001 | 44 100 | 11 025.91875 | **11 026** |
  | 12 000 | 22 050 | 5 512.50000 | **5 512** |
  | 12 001 | 22 050 | 5 512.95938 | **5 513** |
  | 12 000 | 22 054 | 5 513.50000 | **5 514** |
  | 12 000 | 24 050 | 6 012.50000 | **6 013** |
  | 12 000 | 11 025 | 2 756.25000 | **2 756** |
  | 12 000 | 44 101 | 11 025.25000 | **11 025** |
  | 12 001 | 96 000 | 24 002.00000 | **24 002** |
  | 12 001 | 32 000 | 8 000.66667 | **8 001** |

  No single rounding rule (floor/round/half-even/half-up) fits the .5 rows —
  the rate machinery approximates the ratio internally. *Falsifier tried:*
  floor/round/ceil columns per row (§runs/analysis-rate.txt). *Residual:* the
  internal ratio representation was not reconstructed; **arm the row as
  `|measured − exact| ≤ 1 frame`, not as an exact rounding law.**
- **R2 — pitch is preserved** (estimator-identical 996.8 Hz at every rate);
  duration = frames/out_rate within one output sample.
- **R3 — `-q` alias law** (§1 claim 5); `-a` is *not* a strong-alias switch on
  this build (default `-a` = −86 dB at 21.1 k).
- **R4 — `rate <same rate>` is byte-identical** (SOX_EFF_NULL) — useful as a
  cheap probe control.

### 3.3 remix / channels
- **M1 — `remix 1` selects L; it does not sum.** mismatch vs L = 0;
  vs `(L+R)/2` = 47 000. *Falsifier tried:* five formula candidates.
- **M2 — auto downmix = `floor((L+R+1)/2)`** (mismatch 0; nearest-even
  mismatches on 17 000 samples). `-m` = exact `L+R`; `-p` = `rint((L+R)/√2)`;
  `channels 1` ≡ auto.
- **M3 — channel selection/swap/upmix are bit-exact** (stable in both passes):
  `remix 2 1` swaps, `remix 1 0` keeps L, `remix 1 1` duplicates mono→stereo,
  `remix 1v0.5 2v0.5` applies the v multiplier, `remix 1p-6` applies −6 dB.

### 3.4 trim
- **T1 — `s` suffix = samples** (`1s` = 1 frame; `4800s` = 4 800; `1sec` and
  `0.1s` refuse with `cannot parse position '(null)'`).
- **T2 — rounding boundary matrix** (`trim 0 <sec>` → frames):
  0.09995→4 798, 0.09997917→4 799, 0.09998958→4 799, 0.1000104→4 800,
  0.1000208→4 801, 0.10003125→4 802, 0.10001→4 800, 0.09999→4 800.
  Sub-sample decimals follow float32 representation — **arm `round(len·rate)`,
  not a decimal-exact pin.**
- **T3 — forms:** `trim 0.1` = to EOF; `trim 0 -0.1` = drop the last 0.1 s;
  `trim 0 =0.1` = absolute end; `trim 0.05+0.05` = position 0.1 s to EOF;
  `trim 0 100`/`trim 0.2 0.2` take what exists + `WARN … not reached`;
  `trim 0 0` = valid 0-frame WAV rc 0; `trim 0 1e-9` rc 1.
- **T4 — content is sample-exact** (`trim 0 0.1` output == first 4 800 frames
  of the input, mismatch 0).

### 3.5 fade
- **F1 — output is truncated at the second positional (stop) argument**:
  `fade 0 0.15 0.1` on a 0.25 s file → 7 200 frames; `fade 0 0.2 0.05` →
  9 600; `fade 0 0.25 0.1` → 12 000. **This is a silent data-loss trap.**
- **F2 — log law = exactly 100 dB per fade span**: gain = `10^(−5(1−x))`;
  measured 0.003169 @x=.5, 0.056235 @x=.75, 0.316210 @x=.9, 0.997634 @x=.9998;
  fade-out mirrored (0.056184 @x=.25 of the out-span). *Falsifier tried:*
  source constant read (`pow(0.1,(1−x)·5)`, comment *"5 means 100 db
  attenuation"*) — measured and source agree.
- **F3 — curve table** (gain at x = .25/.5/.75): `q` 0.382630/0.707129/0.923866;
  `h` 0.146410/0.499962/0.853541; `t` 0.249933/0.499962/0.749969;
  `p` 0.437483/0.749981/0.937523 (= 1−(1−x)²); `s` 0.062517/0.250019/0.562477
  (= x²); **default type = `l`** (default and `l` envelopes are identical).
- **F4 — first frame of the fade is 0 under `-D`** (the −1 seen in the default
  pass is dither on a zero sample).

### 3.6 repeat / pad / silence
- **P1 — `repeat N` = N *additional* copies, sample-exact tiling**
  (`repeat 2` → 36 000 frames, `out[n] == in[n mod 12000]` mismatch 0);
  `repeat 0` = identity; `repeat -1` rc 1.
- **P2 — `pad` insertion law** (§1 claim 15) and the `%` form is a silent
  no-op on this build.
- **P3 — silence window law** (§1 claim 10): below-periods keeps
  `window_size − 1 = rate/50 − 1` samples (959 @48 k mono) of the silent
  period; `-l` keeps that plus `duration` (5 759); leading trim cuts at the
  windowed-RMS crossing (4 804 for a 4 800-frame leading silence; 4 801 when
  the duration argument is 0.05 s). Threshold units `1%`, `0.01`, `-60d` all
  accepted; `silence 0 …` refuses.

### 3.7 dither / guard
- **D1 — determinism matrix** (§2). **D2 — `-G` is not a limiter** (§1 claim
  13): arm `clip_count(|x| ≥ 32766)`.
- **D3 — noise-shaped `dither -s`**: max sample error 21–22 LSB, error RMS
  5.8 LSB, deterministic only with `-R`; `dither -p 12` max error 23.

### 3.8 chain / stat
- **C1 — order law**: `gain -6 norm -3` → peak −3.0000 (norm last wins);
  `norm -3 gain -6` → −8.9996.
- **C2 — `vol 0.5` ≠ `vol -6.0206 d`** (1 LSB; rms −15.0515 vs −15.0517).
- **S1 — `stat` field definitions** (§1 claim 11): `RMS amplitude` =
  per-channel quadratic mean; `Volume adjustment` = normalization factor to
  0 dBFS (2.000 for a 0.5 FS file — matches `gain -n`); `stat -v` prints only
  that number; `stats -j` gives per-channel `rms_level_db`/`crest_factor`/
  `peak_count`/`window 0.05`; `stat -freq` prints a 4 096-point spectrum.
- **S2 — `stat -e` vs ffmpeg `ebur128`** (§1 claim 12) — the only row that
  touches r93's loudness theme; see §5.

---

## 4. Falsification list — claims an arm must not make

1. "sox effect output is deterministic." False for every sample-changing
   effect at 16-bit output unless `-D`/`-R`; measured 3–5 distinct shas.
2. "`-D` makes dither reproducible." False: `-D` suppresses the automatic
   dither; an explicit `dither` still needs `-R`.
3. "`vol 0.5` equals `gain -6.0206`." False: different rounding (ceil vs
   nearest) → 1 LSB difference.
4. "`remix 1` downmixes to mono." False: it selects channel 1; use `remix 1,2`
   (auto) or `-m 1,2` (raw sum).
5. "`rate` output length = round(in·ratio)." False at .5 boundaries (5 512 vs
   6 013 for the same .5 fraction). Arm ±1 frame.
6. "`-q` is just lower quality." False: it folds 23 kHz to 21.1 kHz at −6.3 dB.
7. "`fade` only applies a curve." False: the stop-position truncates the file.
8. "`trim 1s` means one second." False: one *sample*.
9. "`-G` prevents clipping." False: 7 979 railed samples either way.
10. "`sox stat` RMS matches a full-scale RMS." False: it is the per-channel
    quadratic mean (÷√channels for stereo); its delta fields are interleaved.
11. "`silence` trims at the exact silence boundary." False: window lag
    (`rate/50 − 1` samples) applies to the below-periods side.
12. "`pad %50` pads by 50%." False: silent no-op on this build.

---

## 5. Bimodal / envelope cells (do not arm as a single shape)

- **Default-path determinism**: a leg that is byte-stable in one run may carry
  dither in another if the effect's precision tracking changes (e.g. `gain 0`
  stable, `gain -6` not). Arm the *stability predicate*, never one sha.
- **Sub-sample `trim`/`fade`/`rate` decimals**: float32 representation decides
  the ±1 frame; arm a tolerance.
- **`stat -e` loudness**: momentary/short-term exist on 0.25 s files, but
  `Integrated` only appears once the file is long enough (1 s stereo measured;
  0.25 s mono did not print it); ffmpeg `ebur128` gates to −70 LUFS on the
  same short file. **r93 adjacency:** r93 measures the SPA `filter-graph`
  `ebur128` node (libebur128 path); this row is SoX's *own* implementation
  (no libebur128 linkage — `ldd` shows none) plus the lane's canonical ffmpeg
  filter. Disclosed, bounded to one row, not re-measured from r93's side.
- **`-a` override semantics**: `-a` alone is weak (−86 dB alias rejection);
  the strong alias appears only with `-q`. Treat `-a` as unvalidated outside
  the measured pairs.
- **Sibling contention**: wall times in the receipts are host-load artifacts
  (loadavg 27.6). Content fields were identical across reps; do not read the
  `wall_s` column as a performance claim.

---

## 6. Author directives — proposed `--probe-sox-r94` rows

Every row below is verbatim-ready (receipt + falsifier + expected field).
Stimuli: reuse the probe's own generated WAVs (or the lane's fixtures,
read-only); pass **`-D`** for math rows and **no flag** for determinism rows;
3 reps minimum, 5 for dither rows.

| # | row name | argv (seat-owned scratch in/out) | expected JSON fields | the law | falsifier that was tried |
| --- | --- | --- | --- | --- | --- |
| 1 | `sox_gain_exact` | `sox -D <stereo>.wav out.wav gain -6` | `max_abs_diff_vs_rint`, `peak_db[]` | 0 mismatch; peak −12.021/−18.041 | floor/ceil candidates |
| 2 | `sox_vol_amp_ceil` | `sox -D <stereo>.wav out.wav vol 0.5` | `mismatch_ceil`, `mismatch_rint` | ceil 0, rint 23 000 | four rounding candidates |
| 3 | `sox_vol_spelling_delta` | `vol 0.5` vs `vol -6.0206 d` | `max_abs_diff` | 3.05e-05 (1 LSB), `same_sha` false | byte compare |
| 4 | `sox_default_dither_nondet` | `sox <a>.wav out gain -6` ×3 | `n_distinct_shas` | 3 (assert ≠1) | `-D` control = 1 |
| 5 | `sox_dither_R_reproducible` | `sox -R <f32>.wav -b 16 out dither` ×3 | `n_distinct_shas` | 1 | no `-R` = 5 |
| 6 | `sox_rate_length_tol` | `sox -D <12001f>.wav out rate 44100` | `frames` | 11 026 (±1 of 11 025.91875) | 5-rate matrix |
| 7 | `sox_rate_same_rate_identity` | `sox <b>.wav out rate 48000` | `byte_identical_to_input` | true | sha compare |
| 8 | `sox_rate_q_alias` | `sox -D <23k>.wav out rate -q 44100` | `band_21100hz_db` | ≥ −7 dB (measured −6.289) | default `-h` = −104 dB |
| 9 | `sox_remix_select_vs_sum` | `remix 1` / `remix 1,2` / `-m 1,2` | `mismatch_L_only`, `mismatch_half_up_floor`, `mismatch_L_plus_R` | 0 / 0 / 0 respectively | five formula candidates |
| 10 | `sox_trim_sample_suffix` | `trim 0 1s` / `trim 0 4800s` / `trim 0 1e-9` | `frames`, `rc` | 1 / 4 800 / rc 1 | `1sec` refusal |
| 11 | `sox_fade_truncates_at_stop` | `fade 0 0.15 0.1` on 0.25 s | `frames` | 7 200 | stop=0.25 → 12 000 |
| 12 | `sox_fade_log_100db` | `fade l 0.1` | `envelope.frame2400.gain` | 0.003169 ±1 LSB | 6-type curve table |
| 13 | `sox_repeat_seam_exact` | `repeat 2` | `mismatch_vs_tiling` | 0 | `repeat 0` = identity |
| 14 | `sox_silence_window_lag` | `silence 1 0.1 1%` on c2 | `trailing_zero_frames` | 959 (= rate/50 − 1) | `-l` = 5 759 |
| 15 | `sox_guard_not_limiter` | `gain 12` vs `-G gain 12` | `clipped_ge32766` | equal (7 979) | `≥32767` is dither-sensitive |
| 16 | `sox_stat_rms_definition` | `sox <stereo> -n stat` | `rms_amplitude`, `maximum_delta` | 0.279509 / 0.728180 | numpy cross-computation |
| 17 | `sox_stat_e_vs_ffmpeg` | `sox <mono> -n stat -e` + ffmpeg `ebur128` | `EBUR128 Momentary`, ffmpeg `I` | −11.071 / −70.0 (gated) | r93 adjacency disclosed |
| 18 | `sox_chain_order` | `gain -6 norm -3` vs `norm -3 gain -6` | `peak_db[]` | −3.0000 vs −8.9996 | `norm` vs `--norm` 1 LSB |

**Arming note for the author:** rows 4/5/15 are *negative controls* — they must
assert nondeterminism/clipping, not the absence of it. Rows 1–3, 6–14, 16–18
must be run with `-D` where the law is exact; without `-D` they are dither-noisy.

---

## 7. Mechanism anchors (version-matched, tag `sox_ng-14.8.0.1`)

| file:line | what it pins |
| --- | --- |
| `src/effects.c:143-145` | precision bump for non-`MODIFY` effects → auto-dither trigger |
| `src/sox_ng.c:1132-1134` | the auto-dither insertion predicate (`!no_dither`, precision > out, out < 24) |
| `src/sox_ng.c:2712` / `:2578-2580` / `:3288` | `-D` = `no_dither`; `-R` = `repeatable`; time-derived RNG seed |
| `src/gain.c:93-95` | integer gain factors preserve precision (why `gain 0` is bit-exact) |
| `src/remix.c:102-105`, `:164-166` | auto multiplier `1/j` (or `1/√j` with `-p`); integer multipliers preserve precision |
| `src/rate.c:874-875`, `:891-893` | same-rate → `SOX_EFF_NULL`; "rates too close, skipping resampling" → `SOX_EFF_NULL` |
| `src/fade.c:18-19`, `:376-379` | `FADE_LOG` = `pow(0.1,(1−x)·5)`, *"5 means 100 db attenuation"* |
| `src/silence.c:264-265` | window size = `(rate/50)·channels` → the 959-sample lag |
| `src/trim.c:190` | `SOX_EFF_MCHAN` + `SOX_EFF_LENGTH` + `SOX_EFF_MODIFY` → precision preserved, byte-stable |
| `src/repeat.c` | count semantics (0 = identity; `-1` refused) |

`sources/FETCHED-SOURCES.sha256` records the sha256 of every file fetched from
tag `sox_ng-14.8.0.1`; `sources/rate.c.txt` etc. are an earlier branch-`main`
fetch kept only as provenance (superseded by `sources/v14.8.0.1/`).

---

## 8. Contention ledger + exit state

| window | contact | effect |
| --- | --- | --- |
| whole window | r93-scout filter-graph battery (`runs/battery.log`, stages amp…refflat), r82 fold probe (`measure_audio.py --probe-ffmpeg-r82`), g2d/g3d lanes; loadavg 27.6 → 30.2 | wall times inflated (0.02–0.03 s per sox leg); no content effect — every law is process-local and rep-stable |
| whole window | no PipeWire object created, no device opened, no `pactl`/`pw-*`/`wpctl`/config write | live graph untouched by this seat |
| exit | `git status` tracked-dirty set identical to entry (`corpus/fixtures/measure_audio.py` + its `__pycache__`, sibling-owned); zero tracked writes by this seat; `reports/round-94/` + `corpus/live/r94-scout/` untracked | clean |

Host state read at entry and exit: default sink
`alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink`, default source
`…HiFi__Line__source`, `settings` metadata `clock.rate 48000 /
clock.allowed-rates [ 48000 ] / clock.quantum 1024` — **read-only witnesses;
nothing was written.**

---

## 9. Artifacts & provenance

`corpus/live/r94-scout/` (untracked, 61 MB, 4 219 files): `probes/r94lib.py`,
`probes/r94driver.py`, `probes/r94_analyze.py`; `receipts/` 19 JSON receipts
(10 default + 8 `_D` + prep); `runs/` 3 429 hashed files (per-leg
cmd/stdout/stderr/meta) + `runs/analysis-*.txt`; `sources/` (10 files at tag
`sox_ng-14.8.0.1` + provenance); `scratch/` stimuli + outputs;
`manifest.sha256` (3 429 entries, sha256 `62c5354e…`); `RECEIPTS.md`.

Key receipts: `dither.json`/`dither_D.json` (determinism + guard),
`gain_D.json` (exact gain/vol), `rate_D.json` (length + alias),
`remix_D.json` (formulas), `trim_D.json`, `fade_D.json`, `repeat_pad_silence_D.json`,
`stat.json` (cross-witness), `chain_D.json` (order).

*scout leaf — measured and read, not judged.*
