# R93 boundary — the `ebur128` armed cells replayed under load, and the axes the scout did not vary

**Seat: EXECUTOR (boundary) — the frozen `probeParent` for this round. Round 93,
measured 2026-10-15 20:51–22:0x UTC on host `plazir27`.**
Repo `~/Projects/shokunin/audio-shokunin` @ HEAD **`51a98e54`** (the scout measured
at `b7d80d0`; the tree moved under sibling commits, not this seat). Toolchain:
PipeWire **1.6.8** (`1:1.6.8-1`), libebur128 **1.2.6-2**, ffmpeg n9.0.1,
Python 3.14.7, gcc 16.2.1, 32 cores, `clock.quantum=1024`,
`clock.max-quantum=2048`, `clock.allowed-rates=[ 48000 ]`.

**Zero tracked writes; nothing committed.** All artifacts are under
`corpus/live/r93-boundary/` (untracked) plus this report. Namespace `r93b_*`;
sweeps use an exact-token selector, never a substring (the sibling lanes are
`r95b_*`/`r96b_*`/`r98b_*`, and a foreign tool uses an `/tmp` path containing
`r93b` — the r82 F4 / r95 precedent). Hog PIDs are recorded per stage and killed
by exact PID; session metadata is restored and verified in-receipt.

Label legend: `[O]` = directly observed on this host in this window; `[I]` =
inferred; `[?]` = not resolved by this seat.

---

## 0. Scope

This seat replayed the scout's armed cells and attacked every pinnable claim with
**fresh-process reps in two load regimes** (quiet-ish: no own hogs; load: 12 own
CPU hogs + 2 audio hogs, loadavg 87→130 on top of foreign load), then varied four
independent axes (PipeWire quantum/rate, CLI argv shape, default-node state,
sibling-seat presence). It also ran a **receipt-fidelity audit** of the scout's
own receipts against its report, and one **L2 `labrat` probe** (advisory; see §4.3).

It does **not** judge, rank, or ship. It reports what it measured.

### 0.1 The arm (replayed verbatim)

Per leg, fresh: `pactl load-module module-null-sink sink_name=r93b_in` → `pw-cli`
(`PIPEWIRE_DEBUG=3`) `load-module libpipewire-module-filter-chain <scout args,
r93b names>` → `pw-link` feeds (`r93b_in:monitor_MONO → r93b_fc_in:playback_MONO`)
→ optional taps → `pw-play --target r93b_in <stim>` → read the notify value from
`[I][…][plugin_builtin.c: 2627 debug_run()] control: <v>` → index-verified unload
→ sink unload. Plateau convention = the scout's `stats()` reused verbatim
(median of the longest run of consecutive near-equal finite values, 0.05 dB
grouping) so numbers are directly comparable.

### 0.2 Two measurement hazards this seat had to handle (and did)

1. **The arm itself fails silently.** `pw-play` exited **rc 1 with empty
   stderr** in 4/25 legs of the first quiet core rep, producing a *silent* meter
   (0 control lines, empty capture, or all `-inf`) that is indistinguishable from
   a dead meter. The scout's 273 legs contain **no** such failure (`play.rc`
   scanned across all scout receipts: only 2 silence-arm SIGKILLs). The driver
   therefore retries a leg up to 3× when `play.rc ∉ {0, None}` and records
   `attempt` + `arm_failed` per leg. Over this seat's 208 legs: **6 retried
   (2 recovered clean), 4 ended `arm_failed`** — `label_debug` and the 96 kHz
   stimulus leg in *both* conditions, i.e. partly deterministic, not purely load.
2. **The plateau statistic can pick a transient.** When a series is noisy
   (`l2g_t0` quiet r2: plateau `2.826221` vs tail `2.9286`), the "longest
   near-equal run" is not the converged value. Every Global/gain verdict below
   therefore uses the **same-leg** cross-checks (§5) and the per-leg tail, not
   the plateau alone.

---

## 1. Verdict table

| # | scout claim (r93-scout.md) | scout pin | this seat, quiet-ish | this seat, load (12 own CPU hogs) | verdict |
| --- | --- | --- | --- | --- | --- |
| 1 | port topology 7/7/7 + exact names | `n_input:7 n_output:7 n_notify:7` | `ports` stage re-derived it from the module's own load log: `loaded n_input:7 n_output:7 n_control:0 n_notify:7`; the 6 notify names were re-used as link targets | same | **CONFIRMED** (re-derived, not just re-read) |
| 2 | notify values not in any param; `debug` label is the readout | no LUFS key in `Props` | `enum-params Props` has **no** LUFS/Peak key; `debug:Control` is the only readout | same | **CONFIRMED** |
| 3 | Momentary = exact BS.1770 K-weighted 400 ms | 6 amplitudes, 5 frequencies, ≤1e-5 dB | amp: `-3.003596 … -33.106594` **all 6 exact**; freq 40/100/1k/4k/10k: `-15.288830 / -10.855398 / -9.024196 / -5.753903 / -5.680018` **all 5 exact**; own reference delta ≤1e-6; **libebur128 `ebur128_loudness_global` on the same captures equals the own reference to 1e-6 dB** | amp all 6 exact, freq all 5 exact | **CONFIRMED, independently witnessed** |
| 4 | the per-port channel map is dead (7 ports identical) | `-9.024196` ×21 | FL/UNUSED/SR/DUAL MONO all `-9.024196`; no +3.01, no ×1.41, no exclusion | same | **CONFIRMED** |
| 5 | Momentary/Shortterm/Window = dB mean; Global = block-energy average; no summation | FL+FR no +3 dB; mix = `-19.024195` | mix FL0.5+FR0.05 = `-19.024195` (r3) / `-19.021439` (r2) — dB mean, not `-11.99` | `-19.024195` | **CONFIRMED** (with a 0.0028 dB rep spread, see §2.6) |
| 6 | one silent channel poisons Momentary to `-inf`; Global stays finite | `-inf` ×3; Global finite | all `-inf` (316/317 lines), Global `-9.388371` | all `-inf` (316 lines), Global `-9.388371` | **CONFIRMED** |
| 7 | relative gate works; histogram arm agrees | Global `-9.64`; histogram within 0.04 dB | Global `-9.460499` (r3); histogram **not re-run** | Global `-9.757127` (r1) / `-9.665124` (r2) | **QUALIFIED / partially falsified** — the *law* holds, the *constant* does not (§2.2); the "within 0.04 dB" claim is 0.0449 dB in the scout's own receipts (§3) |
| 8 | Window-only ⇒ lib mode empty ⇒ constant NaN pass-through | `-nan` 241/241 ×3 | `n_nan = n = 241/242`, `n_finite = 0`, audio flows | same | **CONFIRMED** |
| 9 | Peak/True Peak wrong for any port but `In FL` | FL `0.5`; DUAL MONO `0.0`; stereo `0.2` | `peak_mono_fl 0.5`, `peak_mono_dm 0.0`, `truepeak_mono_fl 0.5`, `truepeak_mono_dm 0.0` | same | **CONFIRMED** |
| 10 | `max-window` honoured in ms; absent ⇒ NaN | 0.4→400 ms, 2.0→2 s; absent ⇒ NaN | absent ⇒ NaN only (334 lines); decay = **0.085 / 0.426 / 1.024 / 2.025 s** for 0.05/0.4/1.0/2.0 s; 5.0 s ⇒ frozen `-9.388371` | NaN only (363 lines); decay = **0.085 / 0.418 / 1.024 / 1.856 s**; 5.0 s ⇒ frozen `-9.495832`; all plateaus `-9.024196` | **CONFIRMED** |
| 11 | `max-history` is a block-count cap; silence never evicts | default ≈`-9.83`; cap 2.0 evicts | burst+5 s silence: **both** configs hold `-10.050837` (no eviction); two-burst program: default `-11.498295` vs cap `-15.684121`; **libebur128 on the same capture reads `-11.452473` in both arms** — the cap is witnessed from outside | default `-11.570074` vs cap `-15.650414`; burst+silence both `-10.050837` (identical to quiet) | **CONFIRMED, independently witnessed** |
| 12 | `lufs2gain`: `10^((target−LUFS)/20)`, target clamps to [−70,0], non-finite ⇒ 1.0 | target 0 ⇒ `2.945159`; clamp ⇒ `0.000932`; silence ⇒ `1.0` | target 0 ⇒ `2.826221` / `2.836325` / `2.945724` (leg-dependent, tracking that leg's Global); clamp ⇒ `0.000924` / `0.000932`; silence ⇒ `1.0`; **same-leg check: gain `2.916522`, Global `-9.297304`, residual `1e-6 dB`** | target 0 ⇒ `2.945724`; clamp ⇒ `0.000932`; silence ⇒ `1.0`; same-leg residual `1e-6 dB` | **LAW CONFIRMED, CONSTANT FALSIFIED** (§2.3) |
| 13 | a control key with a space must be quoted | raw ⇒ parse error, quoted ⇒ loads | raw ⇒ `[W] properties.c:264 update_string() error parsing more than 0 properties: Expected object key` + no module; quoted ⇒ `0.000931/0.000932` | raw ⇒ same failure; quoted ⇒ `0.000932` | **CONFIRMED** |
| 14 | builtin table 32 entries; 31 load, `null` does not | 26 + `debug ramp zeroramp sqrt busy`; `null` fails | loads: `debug busy sqrt ramp zeroramp`; fails: `null` (`[W] filter-graph.c:1380 load_node() error parsing label: Success`), `avg sum gain nop` | identical matrix (`debug busy sqrt ramp zeroramp` load; `null avg sum gain nop` fail) | **CONFIRMED** (one refinement: a `[W]` line *does* reach the client for `null`) |
| 15 | audio path bit-exact; error classes loud/warning/deferred | `max_abs_diff = 0.0` at lag 0/±1024 (3/3) | `max_abs_diff = 0.0` at lag 0 (2 reps); 307 200 vs 309 248 frames | `max_abs_diff = 0.0` at lag 0 **and at lag +1024** | **CONFIRMED for lag 0 and +1024; the scout's "±1024, 3/3" wording is not supported by its own receipt** (§3) |
| 16 | `Global LUFS` sits ≈0.13 LU below an independent measurement; offset amplitude-independent | −0.128 dB at 0.5/0.125, −0.128…−0.149 at 0.03125 | plugin − **libebur128 on the same capture**: `-0.256020` (amp 0.5), `-0.132096` (amp 0.125), `-0.148561` (amp 0.03125) in **one** run; gated program `+0.105596` (the plugin reads **above** the independent value); burst+silence `-0.528582` | amp 0.5 `-0.256020`, 0.125 `-0.148560`, 0.03125 `-0.256021`; gated program `-0.209206` (r1) / `-0.099029` (r2) | **FALSIFIED as a constant / as amplitude-independent** (§2.1) |

---

## 2. Falsified and corrected claims

### 2.1 Claim 16 is not a constant — and not amplitude-independent `[O]`

Measured with the **installed libebur128 itself** (`ebur_witness2`,
`ebur128_loudness_global`, `EBUR128_MODE_I`) on the very capture the plugin
measured (pre-tap of the null-sink monitor), so the comparison has no
reference-implementation slack: the scout's own Python reference equals
libebur128 on those files **to 1e-6 dB** (§4.1).

| leg (condition) | plugin Global | independent measurement, same capture | witness | plugin − ref |
| --- | --- | --- | --- | --- |
| amp_500_Global (quiet) | −9.495832 | −9.239812 | libebur128 | **−0.256020** |
| amp_125_Global (quiet) | −21.429571 | −21.297475 | libebur128 | **−0.132096** |
| amp_31_Global (quiet) | −33.470772 | −33.322211 | libebur128 | **−0.148561** |
| amp_500_Global (load) | −9.495832 | −9.239812 | libebur128 | **−0.256020** |
| amp_125_Global (load) | −21.429571 | −21.281011 | libebur128 | **−0.148560** |
| amp_31_Global (load) | −33.578232 | −33.322211 | libebur128 | **−0.256021** |
| cal_glob (load r1) | −9.388371 | −9.239812 | libebur128 | −0.148559 |
| cal_glob (load r2) | −9.495832 | −9.233017 | libebur128 | −0.262815 |
| port_SR_glob (load r1) | −9.388371 | −9.256275 | libebur128 | −0.132096 |
| port_SR_glob (load r2) | −9.495832 | −9.239812 | libebur128 | −0.256020 |
| gate_global (load r1) | −9.757127 | −9.547921 | libebur128 | −0.209206 |
| gate_global (load r2) | −9.665124 | −9.566095 | libebur128 | −0.099029 |
| gate_global (quiet r3) | −9.460499 | −9.566095 | own ref (≡ lib, §4.1) | **+0.105596** |
| port_SR_glob (quiet r2) | −9.051471 | −9.256275 | own ref (≡ lib, §4.1) | **+0.204804** |
| hist_default (quiet) | −10.050837 | −9.522255 | libebur128 | −0.528582 |
| hist2_default (quiet) | −11.498295 | −11.452473 | libebur128 | −0.045822 |
| hist2_max-history=2.0 (quiet) | −15.684121 | −11.452473 | libebur128 | −4.231648 *(expected: the cap evicts)* |

Three amplitudes, **one quiet run, three different offsets** (−0.256/−0.132/−0.149):
the "amplitude-independent −0.128" is a property of the scout's run, not of the
node. Excluding the `max-history` eviction leg (a *documented semantic*, not an
error), the deviation across my 16 comparable legs spans **−0.529 … +0.205 LU and
changes sign**, and it takes a small set of recurring values
(−0.099/−0.132/−0.149/−0.209/−0.256/−0.263), i.e. it is **quantised by the leg's
block phase**, not a fixed gain error. The plugin's *own* spread for one shape is
equally large: `port_SR_glob` read `-9.051471` (quiet r2) and `-9.495832`
(quiet r3) — 0.44 LU apart with no config change.

Consequence for authors: never pin a `Global LUFS` constant. Pin the **law**
(`Global` = gated block mean; the value depends on which partial 400 ms blocks
the graph accumulated since it started) and use the **same-leg** relation when a
number matters.

### 2.2 Claim 7's constants and the histogram tolerance `[O]`

The gate *law* reproduces (loud/quiet/loud reads ≈ −9.5…−9.76, an ungated mean
would be ≈ −12.4), but the pinned `-9.64` is a phase sample: my legs read
`-9.460499` (quiet r3) and `-9.757127` (load r1) for the same program.
The "`use-histogram=true` agrees within 0.04 dB" claim fails in the scout's own
receipts: max |histogram − default| = **0.0449 dB** (§3).

### 2.3 Claim 12's constants are leg-dependent; the law is exact `[O]`

Same-leg check (`l2g_check`, target 0, Global and Gain logged in one leg):
gain `2.916522` (quiet) / `2.947261` (load) against Global `-9.297304` /
`-9.388371` → residual `20·log10(gain) + Global = 1e-6 dB` in both. So
`gain = 10^((target−Global)/20)` **exactly**, and `2.945159` is just that leg's
Global. My target-0 legs read `2.826221`, `2.836325`, `2.945724` — all exactly
`10^((0−Global_leg)/20)`, none equal to the scout's constant.

### 2.4 The scout's §4 cadence/quantum claim is falsified as a general statement `[O]`

Scout §4: "control lines arrive every 42.7 ms → graph quantum 2048 frames at
48 kHz (the null sink's quantum), not 1024."

Measured, same armed cell:

- **one leg is bimodal**: pre-tone/tone cadence `0.043 s` (2048 frames) and the
  post-tone tail `0.021 s` (1024 frames) — recon leg: 76 diffs at 0.021 s and
  63 at 0.043 s;
- across legs the tone-phase cadence is **either** 2048 **or** 1024 with no
  config change (core quiet r2/r3, core load r1/r2: `plcad ∈ {1022.4, 2049.6}`
  in the same stage);
- `clock.force-quantum` pins it deterministically: **1024 → 1022.4, 2048 →
  2049.6, ambient → 2049.6 tone / 1027.2 whole-leg** — and the **Momentary value
  is `-9.024196` in all three** (the 400 ms window is quantum-invariant).

So "the null sink's quantum" is not 2048; the quantum is negotiated per leg and
per phase. `[?]` the mechanism (driver election vs client latency requests) is
not resolved by this seat.

### 2.5 The arm's own failure class `[O]`

4/25 legs of quiet core r2 had `pw-play` exit **rc 1, empty stderr**, with a
silent meter (`port_FL_mom`, `truepeak_mono_fl`, `l2g_default`, `gate_global`).
The scout's dataset has none, so its pins are not confounded — but any future
cell must record `play.rc`, or a silent arm will be read as a semantic. With the
bounded retry in place the load core reps recorded **0 arm failures in 50 legs**;
across all 208 legs of this seat, 4 ended `arm_failed` (§0.2) — two of them
(`label_debug`, the 96 kHz stimulus) fail in *both* conditions, so part of the
class is deterministic rather than load-induced.

### 2.6 Momentary is exact *except* in the two-channel dB-mean case `[O]`

Single-channel Momentary plateaus are byte-stable across all my reps
(`-9.024196` ×≥6 fresh processes, quiet and load). The stereo dB-mean case is
not: `mix_mom` = `-19.024195` (r3) vs `-19.021439` (r2) — a 0.0028 dB spread
(the two states' 400 ms windows are not phase-aligned). The scout's "exact
(byte-stable) … 3/3 mix" is therefore a 3-rep coincidence, not a law.

---

## 3. Receipt-fidelity audit of the scout's own receipts

`probes/audit_scout.py` recomputed 25 pinnable numbers from
`corpus/live/r93-scout/receipts/*.json` (read-only) and compared them with the
report. Result: **21/25 match**; the four that do not:

| id | report says | receipts say | note |
| --- | --- | --- | --- |
| C7.gate_histogram | histogram agrees "within 0.04 dB" | max \|hist − default\| = **0.0449 dB** | over-claim by 0.005 dB |
| C12.gain_clamp | clamp ⇒ `0.000932` "(6/6 across two arms)" | the `lufs2gain` **m100 arm itself is 0/3**: `0.007451, 0.007451, 0.034498` (implied Global −27.4/−40.8); the 6 clean legs are `l2gcheck` (3) + `ctlgrammar` (3) | §3.9 calls it "the *first* `lufs2gain` run"; the receipt shows all three reps of that arm |
| C15.bit_exact | "`max_abs_diff = 0.0` at lag 0/±1024 (3/3)" | rep r1 has `lag=-1024`, `best_lag=null`, `max_abs_diff=null` — the code skips negative lags, so the −1024 case was **never evaluated**; only 2/3 legs carry a diff | the +1024 and 0 cases are exact `0.0` |
| C16b.offset_amplitude | "offset is amplitude-independent" | scout's own data: amp family −0.1276…−0.1486 vs gating program −0.0959…−0.1209 (span 0.021) | program-dependent even in the scout's run |

Also verified as accurate: leg count (273 stage legs across the 19 stage
receipts), port table, amp/freq exactness, portmap 21/21, mix −19.024195,
window NaN matrix, window 2 s, history/hist2 ranges, peaks, silence gain,
ctlgrammar, label matrix (incl. `null`), `null` shapes.

---

## 4. Independent witnesses

### 4.1 Installed libebur128 on the scout's frozen captures `[O]`

`probes/ebur_witness2` (links `-lebur128`) on the scout's `*_ref.wav`:

| capture | libebur128 full | scout Python `ref_global` | Δ |
| --- | --- | --- | --- |
| amp_500_Global_r0 | −9.254570 | −9.254570 | **0.000000** |
| amp_500_Global_r2 | −9.256275 | −9.256275 | **0.000000** |
| amp_125_Global_r0 | −21.295769 | −21.295769 | **0.000000** |
| amp_31_Global_r0 | −33.320937 | −33.320937 | **0.000000** |
| gate_global_default_r0 | −9.524736 | −9.524736 | **0.000000** |

And for **Momentary** legs the plugin equals libebur128's integrated loudness of
the silence-trimmed capture to **8e-6 dB** (`amp_31_Momentary`: plugin
−33.106594, lib trim −33.106603). The scout's reference implementation is
therefore validated against the library it models, and the plugin's *Momentary*
is exact while its *Global* is not.

### 4.2 ffmpeg `ebur128` cross-witness `[O]`

`ref_quiet_r1`: plugin Global `-9.388371`; own reference `-9.256275`;
libebur128 full `-9.256275`; libebur128 trim `-9.024204`; ffmpeg on the capture
`I: -9.3 LUFS`; ffmpeg on the clean stimulus `I: -9.0 LUFS`. Three independent
implementations agree on the signal; only the plugin's Global differs.

### 4.3 L2 `labrat` probe (advisory, exec-limited) `[O]`

The one dispatched `ufo-labrat` (depth-2, read-only) returned **PARTIAL**: it
could not execute code, so it re-extracted the receipt numbers (confirming the
offset is −0.1276…−0.1486 in the scout's amp legs, and that the plugin's Global
is still *decreasing* through the post-tone tail — i.e. late partial blocks are
entering the gated mean). Its decisive clause — "plugin ==
`ebur128_loudness_global` within 0.02 LU" — was **not** testable for it, and this
seat's §4.1 measures it directly: the clause is **false** (deviation
0.05–0.53 LU). Its leaning ("the offset is a reference artifact") is therefore
**falsified**: the scout's reference *is* the library; the plugin is the deviant.

---

## 5. Axes

| axis | manipulation | result |
| --- | --- | --- |
| **PipeWire quantum** | `clock.force-quantum` 1024 / 2048 (ambient 0), restored to 0 and verified | cadence pinned (1022.4 / 2049.6 frames); **Momentary `-9.024196` in all three**, quiet and load. Ambient leg bimodal 2049.6 (tone) / 1027.2 (whole leg) |
| **PipeWire rate** | `pactl … rate=44100/96000` on the null sink; 44.1 k / 96 k stimulus files; `clock.force-rate` (+`allowed-rates`) | sink `rate=` arg is **inert** for the graph (capture stays 48 000, Momentary stays `-9.024196`); a **stimulus-rate mismatch moves the level**: 44.1 k stimulus reads `-8.813641` (+0.21 dB), 96 k reads `-9.679438` (−0.65 dB), and the plugin tracks libebur128 on each (Δ ≤ 4.3e-5 dB). `clock.force-rate` 44100 / 96000 (+`allowed-rates`, both restored and verified): the graph **does** move — see §5.1 |
| **CLI argv shape** | module arg order; `pw-play` `--target` before/after the file; `pw-record` flags-before-path vs path-before-flags; `pw-link` operands reversed | all five working shapes give the identical `-9.024196`; **reversed `pw-link` fails to link** (`ok=false`) and the meter then reads nothing — the link direction is load-bearing |
| **default-node state** | ambient default vs `pactl set-default-sink r93b_in` for one leg, restored and verified (`get-default-sink` equal before/after) | identical `-9.024196` both ways: the arm is default-node-independent (autoconnect=false + explicit links) |
| **sibling presence** | recorded per leg (`foreign_seat_nodes`, loadavg) | see §6 |

### 5.1 Graph-rate leg — the rate lever that *does* work `[O]`

`clock.allowed-rates` was widened to `[ 44100 48000 96000 ]` and
`clock.force-rate` set to 44100 / 96000 for three legs (window ≈ 65 s), then
**both keys restored and verified** (`restored = True`; `allowed-rates
[ 48000 ]`, `force-rate 0` afterwards). The 1 kHz stimulus file is a 48 kHz file.

| forced graph rate | plugin Momentary | own reference computed **at that rate** (offline synth) | own reference at 48 kHz |
| --- | --- | --- | --- |
| 44 100 | **−9.021439** | −9.021438 (Δ 1e-6) | −9.024195 |
| 44 100 (40 Hz stimulus) | **−15.285007** | −15.285002 (Δ 5e-6) | −15.288824 |
| 96 000 | **−9.041499** | −9.041499 (Δ 0) | −9.024196 |

So the graph really runs at the forced rate and the plugin's K-weighting follows
it (the 40 Hz point fingerprints it: Δ40 = −6.2636 dB at 44.1 kHz vs −6.2646 at
48 kHz vs −6.2690 at 96 kHz). The capture tap stayed at 48 kHz (pw-record's own
negotiation), which is why the tap's reference reads the 48 kHz-law value
(−9.024195) while the plugin reads the 44.1 kHz-law value (−9.021439): the
0.0028 dB gap is the resampled tap, not a meter error. `[O]` **The scout's
calibration row is therefore rate-qualified: `-9.024196` is the 48 kHz value;
the same stimulus reads `-9.021439` at 44.1 kHz and `-9.041499` at 96 kHz.**

---

## 6. Contention ledger and hygiene

**Load regime (the assignment's `>=12 concurrent hogs`).** Per load stage the
driver spawns **12 CPU hogs** (`r93b_hog.py`: `PR_SET_NAME r93b_hog`, a bounded
500k-iteration spin loop, wall-capped) **+ 2 audio hogs** (`pw-record` retry-loop
on `r93b_in`, its own session so `killpg` reaches the child). Every PID is
recorded (`hogs_start.pids`) and killed by **exact PID** (`hogs_stop.still_present
= []`); `hogs_state.cpu_alive = 12, audio_alive = 2` is asserted per stage. The
first load stage (core r1) ran with the audio hogs exiting immediately because
the sink did not exist yet (12 CPU only, still ≥12); the wrapper was fixed and
verified from `quantum-load` onward. Loadavg observed: **65 at entry, 72–90
during the quiet arms, 87–130 during the load arms** (32 cores).

| window | contact | effect |
| --- | --- | --- |
| whole window | foreign seats live: `r92b_*` (fc_in/fc_out/in/play/rec/ref), `r95b_ns`, `r96b_ns`, `r98b_ns`/`r98b_ns2`/`r98b_run`/`r98b_flags`/`r98bstream`, `r99_probe`, `r100b_in`/`r100b_sofa_in` (96 kHz, RUNNING), `r83a_*` (at exit) | read-only contact; every listing carried their rows; **no foreign object was created, modified or removed by this seat** |
| whole window | foreign hog batteries outside this repo: `/tmp/flake-impl/before-battery.sh` (+`hogs.pid`), `/tmp/flakeB/run-battery.sh`, `/tmp/mori-r9-receipts/battery.sh`, `/tmp/det-r9/battery.sh`, mori-shokunin self-test batteries | the dominant contention source. **This seat's "quiet-ish" arm is quiet with respect to its *own* hogs only** — foreign load was never below loadavg 72 |
| 20:54 → 21:24 UTC | a **foreign actor** moved the ambient default sink from `alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink` (read at 20:51 and again in `pw-metadata -n default` at 20:54) to `alsa_output.pci-0000_01_00.1.hdmi-stereo.99` | disclosed, not caused; the `defaults` axis leg read and restored whatever value it found |
| 21:24 & 21:53 | this seat's `defaults` axis: `pactl set-default-sink r93b_in` for one leg, then restored to the pre-leg value and verified in-receipt (`default_after_restore` = the pre-leg value in both conditions) | residual footprint: WirePlumber's `~/.local/state/wireplumber/default-nodes` retains `default.configured.audio.sink.0=r93b_in` as a **fallback slot** (that file already carries `r87b_ns` and `r86ctl_src` from other seats). The *configured* default is not an r93b name; the *effective* default moves with WirePlumber's own election during legs, so my transient sinks appear in `pactl get-default-sink` while they exist |
| 21:55 UTC | another seat modified the tracked files `corpus/fixtures/measure_audio.py` and its `__pycache__/*.pyc` (mtime in-window) | not this seat: nothing under `corpus/fixtures/` was read, imported, executed or written here |
| whole window | this seat: **208 legs** (107 quiet + 101 load) across 32 receipts, one null sink + one `pw-cli` chain per leg | own residue zero at every stage sweep |

**Exit state (measured 22:0x UTC).** `pw-dump` r93b nodes **0**; `pactl list
modules short` r93b **0**; `ps` r93b **0**. Defaults `…SPDIF__sink.29` /
`…Line__source.29` (not this namespace). Session metadata back to the entry
values: `clock.allowed-rates [ 48000 ]`, `clock.force-quantum 0`,
`clock.force-rate 0`. Tracked writes: `git status --short reports/round-93/` =
`?? reports/round-93/r93-boundary.md` only — **zero tracked-file writes by this
seat**. Receipts: `sha256sum -c manifest.sha256` = **119/119 OK** (119 files,
89.39 MB).

---

## 7. Remaining unknowns

1. `[?]` What selects 1024 vs 2048 for a given leg (driver election vs client
   latency requests) — measured, not explained.
2. `[?]` The plugin's exact block-accumulation rule that produces the quantised
   Global deviation set {−0.099, −0.132, −0.149, −0.209, −0.256, −0.263, −0.529}.
3. `[?]` The scout's §3.6 source-vs-binary `max-window` divergence (not re-attacked
   here; my window matrix reproduces the binary behaviour only).
4. `[?]` `Shortterm LUFS` (the 7th notify name) was not read by this seat.
5. `[?]` Range LU on a dynamic program (only steady-tone `0.0` reproduced).

---

## 8. Artifacts

`corpus/live/r93-boundary/` (untracked): `probes/` (`r93blib.py`,
`r93bdriver.py` 15 stages, `r93b_hog.py`, `ebur_witness2.c`+binary,
`witness_scan.py`, `audit_scout.py`, `analyze.py`, `build_manifest.py`),
`receipts/` (one JSON per stage × condition × rep, plus `scout_audit.json`,
`witness_amp.json`, `witness_gating.json`, `analysis.json`), `scratch/`,
`runs/` (stage logs), `battery.sh`, `manifest.sha256`, `RECEIPTS.md`.

*executor (boundary) seat — measured, audited and reported; judgment is the
orchestrator's.*
