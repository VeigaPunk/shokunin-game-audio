# R100 boundary — the sofa/spatializer pins attacked: replay under load, axes, and the window-landing falsifier

Round 100 **boundary seat** (leaf; frozen `probeParent` — exactly one read-only
`ufo-labrat` child, advisory, folded §8). Host `plazir27`, window
**2026-10-15T21:29Z → 2026-10-16T01:45Z** (host local UTC−3). Repo
`~/Projects/shokunin/audio-shokunin` @ entry HEAD `de59a276`, exit HEAD
`a151a226` (sibling `r83 author` landed during the seat) — **zero tracked writes,
nothing committed**: the only tracked modification in the worktree at exit is
`corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`, a sibling author's
bytecode cache (this seat never imported or opened `corpus/fixtures/`). Object
namespace **`r100b_*` only**; own PIDs only; the r95 sweep
incident precedent is honoured — every sweep is filtered on the `r100b` token and
the process sweep additionally requires a PipeWire tool in `argv[0]`. Foreign
objects were **counted, never signalled** (§6). Exit census: **0 `r100b` nodes,
0 `r100b` modules, 0 seat processes, 0 own hogs** (`receipts/census-exit-*.json`,
`receipts/hog-kill-*.json`, plus an out-of-band `pw-dump`/`pgrep` re-check).

Target: `reports/round-100/r100-scout.md` — its 9 pinned cells (§3), its 12
author-ready rows (§4) and its 10 predeclared falsifications (§5), replayed with
**fresh processes** in two load conditions and then attacked along five axes.

Toolchain identical to the scout: PipeWire **1.6.8** (`1:1.6.8-1`),
WirePlumber **0.5.17-1**, libpulse 17.0-98-gb096, Python 3.14.7, 32 CPUs
(Ryzen 9 9950X).

---

## 0. Headline

1. **Every pinned number reproduced — but the scout's *stability bound* does not
   hold across processes, and the cause is its own metric.** The scout says
   "per-channel rms and 440 Hz Goertzel magnitudes are identical to **≤2e-5
   relative** across reps". Replayed with fresh processes the *same recipe*
   scatters **1.3e-5 … 3.1e-5** (three cells), and the rate-mismatch cell differs
   from the scout's single rep by **1.0–1.3e-4**. The underlying waveform is
   **identical to ≤1 LSB everywhere** (max |Δ| = 3.052e-05 = 1/32768; the only
   samples above 1 LSB sit in **exactly one contiguous block** of 1 569–2 667
   samples at the stimulus's terminal region, `scratch/align.json`), and a
   **stride-1** window metric reproduces to **6e-8 … 1e-7** with the ILD
   **4.6084 dB in 10 of 12** captures — the scatter is the scout's coarse
   `best_window` stride (`win//10` = 1920 samples) landing differently on the
   stimulus fade-in. §3.1.
2. **The ILD law is the robust pin** (the scout's headline): azimuth
   0/45/90/135/180/225/270/315 → 0.000 / **+3.465** / +4.612 / **+4.195** /
   0.000 / **−4.195** / −4.612 / **−3.465** dB at 44100 (3 reps each for the
   cardinal points), **±0.0035 dB** across arms in the scout's coarse recipe, and
   **4.6084 dB in 10 of 12 captures** with a stride-1 window (outliers: one fg
   capture 4.6100, the 96 kHz private core 4.6176; az270 = **−4.6084 ×3**). The
   channel-swap falsifier (never run by the scout or its labrat) returns
   **−4.612 dB**: the asymmetry follows the physical `output_FL`/`output_FR`
   routing, not the analysis. §4.2.
3. **The node is clock-invariant.** A private core + private session manager
   (custom profile with **no hardware monitors** — zero `alsa` lines in the WP
   log) reproduces the shared graph to ~1e-5 at server quantum **512/1024/2048**
   and server rate **44100/48000/96000**. The scout's numbers are not an artifact
   of the shared graph's ambient clock. §4.7.
4. **The control plane is real and the scout left it unmeasured**: the Props
   param exposes `s0:Azimuth` / `s0:Elevation` / `s0:Radius` **on the capture-side
   node only**, and `pw-cli set-param <id> Props '{ params = [ "s0:Azimuth" 90.0 ] }'`
   moves a *running* spatializer (read-back 0.0 → 90.0; the capture's ILD steps
   0.000 → +4.612 dB in the same take). The man page's "can be changed at
   runtime" is now measured. §4.3.
5. **Three claims are falsified outright** (§3): the ≤2e-5 stability bound as a
   cross-process statement; the scout's proposed `Radius` ladder ("spectrum
   changes") — Radius 0.5/1.0/3.0 give *identical* output; and the implicit
   "`default.sofa` is a second file" — it is a **symlink** to
   `MIT_KEMAR_normal_pinna.sofa` (identical sha256, identical output).
6. **A new silent parameter-drop**: the quoted token form
   `config={"filename"="…"},control={"Azimuth"="90.0"}` loads the graph and plays
   audio but **silently ignores the control object** (read-back `s0:Azimuth = 0.0`,
   output = the az0 signature). Token *order* is inert; token *quoting* is not.

---

## 1. Method

| arm | load | legs | what it is |
| --- | --- | --- | --- |
| **quiet** | 0 self hogs (foreign load1 100–117) | 23 | the scout's armed cells, fresh process per leg |
| **load** | **+16 own `r100b_hog` processes** (pids + `/proc` starttime recorded; all 16 killed, `refused=[]`) | 30 | same cells, load1 98–131 |
| **axes** | ambient | 47 | token order, azimuth curve, rate ladder, config keys, rig falsifiers, sibling presence |
| **axes2** | ambient | 22 | corrected channel-swap falsifier + token-form rerun |
| **mismatch** | ambient | 7 | the scout's n=1 rate-mismatch cell, 5×48000 + 2×96000, with retry |
| **timing** | ambient | 7 | source loss, relink timing, driver drop, FC unload, runtime control change |
| **sandbox** | private core + private WirePlumber (no hardware monitors) | 10 | server quantum/rate axis, private-core-vs-shared |

**Clients.** `probes/r100b_sofa.py` is the workhorse: the scout's arming shape
(null-sink driver → `pw-cli`-loaded filter chain → `pw-record` post-tap) with
axis knobs. It imports the r92-scout `pwlib` **read-only**, exactly as the scout
did. Per-leg fields: `utc`, `loadavg_start/end`, pre/post sweep, node ids and
states, ports, per-link rc/tries, the plugin's log lines, a **live clock witness**
(`pw-cli info 0` + driver-node `clock.*`), both analysis recipes, and an optional
per-100 ms rms/ILD time series.

**Rig deviations from the scout's rig (all disclosed, all recorded per leg).**
(i) The stimulus is played **backgrounded with `node.autoconnect=false` + an
explicit `pw-link`** (`play_link_origin="manual"`, 124 legs) instead of relying on
session-manager autolink (`"policy"`, 12 legs — the scout's exact foreground shape,
run as `fgprobe`). Reason: one exploratory leg of the scout's fg shape **hung for
the full 5.6 s wall** (silent `paused`, no link — the r98 §3.5 class); the fgprobe
stage itself was then clean 12/12, so the hang is transient, but the manual link
makes every leg deterministic. (ii) `PIPEWIRE_DEBUG=3` is set on the `pw-cli`
client so the **plugin's own log lines** (`plugin_sofa.c:60/222/268`) are captured
— without it the scout's `n_samples` pin is unverifiable. (iii) The post-tap
record window is longer than the scout's (frames 96 380–147 456 vs 101 376–105 472);
comparisons therefore use **the scout's own recipe** (`win = 0.4 × fc_rate`) as well
as the file-rate recipe, and §3.1 shows the recipe itself is the variable.
(iv) A zero-frame capture (a client died before producing data) is retried once
from the `mismatch` arm onward; the retry is recorded in the row.

**Hog lifecycle.** `probes/r100b_hog.py` × 16, spawned by the runner with pid +
`/proc/<pid>/stat` starttime + comm; killed only after re-verifying both;
`receipts/hog-kill-*.json` shows `attempted=16, refused=[], remaining=[]` (the
first run's `remaining` was a zombie artifact — the reap was fixed and the
receipts distinguish the two). A 2 s `loadavg` sampler ran for every arm
(`receipts/loadavg-*.jsonl`).

**Contention disclosure (first-order).** The host was **never quiet**: 84
foreign `yes` processes, 12 `r93b_hog` (a sibling boundary seat), 64–96 orphaned
hogs earlier, and sibling seats in the shared graph. Ambient load1 was 100–117;
the load arm reached 131. A zero-contention baseline is unavailable on this host
(r98 B1 stands). "quiet-ish" below means **no self-induced load**.

---

## 2. Verdict table

Verdicts: **CONF** = confirmed in fresh reps of both arms; **CONF-L** = confirmed
under load; **EXT** = extended/pinned further; **REFINED** = the observation
holds, the stated form is wrong; **FALS** = falsified. Receipts:
`corpus/live/r100-boundary/receipts/`.

| # | scout claim (abridged) | verdict | key numbers from this seat |
| --- | --- | --- | --- |
| 1 | ports/shape: capture mono `playback_MONO`, playback stereo `output_FL`/`output_FR`; module loads, both nodes publish; 12 legs | **CONF** | **136/136** shared-graph legs publish exactly those ports; **136/136** have every link `rc 0` on `tries: 1`; nodes `r100b_sofa_in`/`r100b_sofa_out` present in 136/136 (`receipts/*-{gate,azimuth,extra,fgprobe,mismatch}.json`) |
| 2 | no-config spatializer: load OK → activation `error (−22)` (`spatializer: no config was given`) → pure silence | **CONF-L** | quiet: `[E] plugin_sofa.c:60 … no config was given` → `[E] stream.c:429 error (-22) can't start graph: Invalid argument` → `module-filter-ch:1579 … error: can't start graph`; load: the same `module-filter-ch:1579 … error: can't start graph` line (the plugin line was pushed out of the 40-line log tail by pw-cli noise). Capture rms 0.0/0.0 with frames > 0 (147 456 / 148 480) — silence, not a failed take (`quiet-gate.json`, `load-gate.json`) |
| 3 | real SOFA @44100: `using n_samples:512 256:4096` + `making spatializer with <az> <el> <radius>` | **CONF** | `n_samples:512` in every 44100 leg that logged it (≥12); `making spatializer with 0.000000 0.000000 1.000000` (az0) and `90.000000` (az90) |
| 4 | rate mismatch @48000 is **not** refused: `n_samples:558`, output non-silent, the `Only the same sampling rate supported` string is not reached | **CONF + EXT** | `n_samples:558` ×5 (48 k) and `n_samples:1115` (=512·96000/44100) ×3 (96 k); rms 0.121 474 56…0.121 477 38 non-silent; **the string is absent from all 146 legs' logs** (the only plugin error emitted is the no-config one) |
| 5 | azimuth law @44100: az0 0.000 / az90 +4.611…4.612 / az270 −4.612 (exact mirror) / az180 0.000 | **CONF-L (+ EXT curve)** | quiet az90 **4.612/4.609/4.612**, az270 **−4.609/−4.612/−4.612**; load az90 **4.609/4.612/4.612**, az270 **−4.612 ×3**; az0 and az180 ILD 0.0 in every leg of both arms. New curve points: 45→+3.465, 135→+4.195, 225→−4.195, 315→−3.465 dB (§4.1) |
| 6 | front/back is spectral, not ILD: az180 vs az0 at 440 Hz = −1.4517 dB, L = R | **CONF + EXT (sign flip)** | az180 rms 0.098 566 43…0.098 569 93 (ILD 0.000) vs az0 0.116 45; with a **997 Hz** stimulus the same comparison is **+2.34 dB** (0.186 898 62 vs 0.142 764 16) — the offset is frequency-dependent in *sign*, i.e. genuinely spectral (§4.4) |
| 7 | azimuth survives the rate mismatch: az90 @48000 → +4.616 dB ×3 | **CONF-L** | quiet 4.614/4.616/4.616, load **4.616 ×3**; L = 0.169 796 96 in **6/6** legs (identical to 8 dp) |
| 8 | not a pass-through: az0 output −9.642 dB vs the stimulus | **CONF + EXT (direct witness)** | reference tap on the sink monitor (the FC's real input): rms **0.353 528 99**, tone 0.499 965 49; az0 output 0.116 451 55 → **−9.6421 dB**; az90 per-channel L −6.73 dB / R −11.35 dB (`axes-rigart.json` `reftap_*`) |
| 9 | teardown: every stage ends `final sweep: clean: True` | **CONF** | **136/136** shared-graph legs + 10/10 sandbox legs have `post_sweep.clean = true`; entry/exit censuses list 0 `r100b` objects |
| 10 | analysis-level stability: rms + Goertzel identical to ≤2e-5 relative across reps | **REFINED / FALS as a cross-process claim** | coarse-recipe spread **3.08e-5** (az0), **2.66e-5** (az90), **1.32e-5** (az180); 48 k cell off by **1.0–1.3e-4**; stride-1 recipe spread **8.6e-8 / 6.1e-8 / 1.0e-7**; ILD coarse 4.609–4.616 vs **fine 4.6084 dB in 10/12**. §3.1 |
| 11 | WAV bytes are not identical (pw-record start offset differs) | **CONF + RE-ATTR** | bytes differ mainly in **length** (mine 123 904–146 432 vs scout 101 376–105 472, 1024-frame-quantized); after an integer lag the samples agree to **exactly 1 LSB (3.052e-05)** outside **one contiguous block** of 1 569–2 667 samples at the stimulus's terminal region; az270 has **zero** samples above 1 LSB and 99.93 % exact. §3.2 |
| 12 | §5 caveats: ILD is rate-insensitive; no perceptual claim; bounded to this host/plugin/file | **CONF + EXT** | az90 ILD across **FC** rate 44100 / 48000 / 88200 = 4.612 / 4.616 / 4.614 dB; **identical 4.612** across **server** rate 44100/48000/96000 and quantum 512/1024/2048 in the private core (§4.7). No perceptual claim is made here either |
| 13 | proposed row 8 (IR/latency) and row 12 (crash class on unload) | **NOT REPRODUCED / UNRES** | no `pw-cli` `BrokenPipeError` in 146 legs (all unloads guarded); the IR/latency row is not armed — see §7 |

---

## 3. Falsified and re-attributed claims (exact receipts)

### 3.1 "identical to ≤2e-5 relative across reps" — FALSIFIED as a cross-process statement, and the cause is the metric

Three independent measurements point the same way:

**(a) Coarse vs fine window (`r100bwindow.py`, `scratch/window-landing.json`).**
The scout's `best_window()` scans with `step = win // 10` (1 920 samples at
48 000). Recomputing both recipes on the scout's own captures and mine:

| cell | scout coarse | r100b coarse | coarse spread | scout fine | r100b fine | **fine spread** |
| --- | --- | --- | --- | --- | --- | --- |
| az0 @44100 | 0.116 503 63 (r0,r1) | 0.116 506 01 / 0.116 502 42 | **3.08e-5** | 0.116 509 92 | 0.116 509 93 / 0.116 509 92 | **8.6e-8** |
| az90 @44100 | 0.162 776 55 | 0.162 780 88 | **2.66e-5** | 0.162 781 02 | 0.162 781 01 | **6.1e-8** |
| az180 @44100 | 0.098 569 98 | 0.098 568 68 | **1.32e-5** | 0.098 578 26 | 0.098 578 25 | **1.0e-7** |

The coarse recipe — *the scout's own* — exceeds its stated bound (3.08e-5 > 2e-5)
as soon as the process is fresh. The fine recipe is ~300× tighter. The stimulus
has a short fade-in (first 100 ms rms 0.120 787 vs steady 0.121 475), so where the
coarse stride lands changes the answer; **the pin is a property of the window
search, not of the signal**.

**(b) The ILD inherits the same artifact.** Coarse ILD across 6 quiet + 6 load
reps: 4.609…4.616 (az90) and −4.609…−4.612 (az270) — a ±0.0035 dB band. With a
stride-1 search the ILD is **4.6084 dB in 10 of 12** captures (scout r0/r1/r2,
r100b fg r1/r2, sandbox q512, r100b r1; `scratch/fine-ild.json`) and
**−4.6084 ×3** for az270 — an exact mirror. The two fine outliers are informative:
one fg capture reads 4.6100 dB, and the private core running at a 96 kHz *server*
rate reads 4.6176 dB (a genuinely different clock, not noise).

**(c) The scout's own receipts already contained the crack**: az90 r0
(L = 0.162 776 55) is *not* the mirror of az270 r0 (R = 0.162 780 89), while
r1/r2 are; the scout's "exact mirror" is a two-of-three statement. The labrat
(§8) sharpened this: inside the scout's **own** three az90 reps the coarse search
landed at three *different* offsets (59976 / 12348 / 42336) and produced three
different rms values — the instability is not a cross-seat effect, it is already
inside the scout's "3/3 identical" claim.

**Consequence for author rows:** pin **fine-window** values (or the ILD), never the
coarse `best_window` rms; and never assert a ≤2e-5 bound on the coarse recipe.

### 3.2 "the WAV bytes are not identical" — CONFIRMED, but the difference is length + 1 LSB, not the signal

`r100balign.py` (`scratch/align.json`), direct (not FFT-global) alignment, because
the captures carry different amounts of leading silence. Every mismatching sample
is localized: `gt1lsb_samples` counts samples above 1 LSB, `mismatch_blocks`
localizes them, and `residual_outside_blocks` re-measures what is left.

| pair | frames (mine vs scout) | lag | max abs Δ | exact | >1 LSB samples | block | **residual outside the block** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| az270 r0 ch0 | 139 264 vs 102 400 | −28 672 | **3.052e-05** | 0.9993 | **0** | — | max **3.052e-05**, 99.93 % exact |
| az270 r0 ch1 | ″ | −28 672 | **3.052e-05** | 0.9973 | **0** | — | max **3.052e-05**, 99.73 % exact |
| az0 r0 (both ch) | 144 384 vs 102 400 | −30 720 | 3.087e-01 | 0.9733 | 2 666 | **80896 : 2666** | max **3.052e-05**, 99.93 % exact |
| az0 r1 (both ch) | 146 432 vs 102 400 | −29 696 | 3.087e-01 | 0.9833 | 1 643 | **80896 : 1643** | max **3.052e-05**, 99.94 % exact |
| az90 r1 ch0/ch1 | 143 360 vs 102 400 | −32 768 | 4.326e-01 / 2.537e-01 | 0.9715 / 0.9732 | 2 666 / 2 667 | **80896 : 2666** | max **3.052e-05**, 99.74 % / 99.92 % exact |
| 48 k az90 r0 ch0/ch1 | 123 904 vs 102 400 | −15 360 | 4.981e-01 / 2.363e-01 | 0.9846 | 1 569 | **80898/80903 : 1569** | max **3.052e-05**, 99.999 % / 99.996 % exact |

So: **the waveform is identical to exactly 1 LSB everywhere except one contiguous
block** whose start (80 896–80 903, in the scout's coordinate frame) sits on the
end of the stimulus (the scout's tone spans 6 212–82 538 in those captures) — i.e.
the two rigs stop the tone at slightly different points. The scout's
"analysis-level stability only" is therefore **too weak**: the *signal* is
reproducible; only the window (and the stimulus's last ~1.6–2.7 k samples) is not.

> **Labrat-driven correction (§8):** the first version of this claim ("one
> contiguous 2 663-sample block") was **not receipted** — the child read
> `align.json`, correctly found no positional field, and returned *CONTRADICTS*.
> The script was upgraded to localize the mismatches and to re-measure the
> residual; the table above is the post-correction receipt. The child's sample
> counts (2 734 / 1 704 / 2 924 / 1 577) match the block lengths to within the
> 1 LSB threshold difference.

### 3.3 Proposed `Radius` ladder "expect ILD symmetry preserved, spectrum changes" — FALSIFIED

`Radius` 0.5 / 1.0 / 3.0 at az90 @44100 give **0.162 704 81 / 0.095 677 1**,
**0.162 704 81 / 0.095 677 09**, **0.162 704 81 / 0.095 677 09** — identical to
1e-7 (ILD 4.612 in all three). At this file/plugin the control is inert
(`axes-cfgkeys.json` `radius05/radius30` vs `order_base`). The man-page contract
("value between 0 and 100, default 1.0") is accepted but has **no measurable
effect on the binaural output** here. (Elevation *is* effective: el 90 →
0.103 201 48/0.103 201 48, ILD 0.000.)

### 3.4 "`/usr/share/libmysofa/default.sofa` exists too" (proposed row 11) — RE-ATTRIBUTED

It is a **symlink**: `default.sofa -> MIT_KEMAR_normal_pinna.sofa`, both
`sha256 2768ac84…57e28`. Feeding it as `filename` gives output identical to the
canonical file (0.162 704 83/0.095 686 16, ILD 4.611). There is **no second
corpus** on this host; the labrat's untested item (ii) is closed.

### 3.5 The quoted token form silently drops `control` — NEW falsifier class

`config={"filename"="…"},control={"Azimuth"="90.0","Elevation"="0.0","Radius"="1.0"}`
loads, plays audio, and reports **`s0:Azimuth = 0.000000`** on read-back with the
**az0 signature** (0.116 451 56/0.116 451 56, ILD 0.0) — the `control` object is
parsed into nothing, silently. The unquoted form (`config={filename=…}`,
`control={Azimuth=90.0}`) is correct in every order tested
(`base`/`reversed`/`graph_last`/`props_first`/`rates_first`/`control_first`/no
`node.description`), all 90.000000 on read-back. **Order is inert; quoting is not.**

### 3.6 The scout's rate-mismatch cell is n=1 and its value does not reproduce

The scout armed `sofa_48k` **once** (0.121 490 02). Replayed 5× (quiet, with
retry): **0.121 477 38 ×4, 0.121 474 56 ×1** (spread 2.3e-5); under load:
0.121 474 56 (the other three load reps died as zero-frame captures, §7-2). The
scout's value sits **1.0–1.3e-4** above every rep this seat measured. A single
rep cannot support a pin; the cell needs `n ≥ 3` in any author row.

---

## 4. Extensions and new pins (beyond confirm/falsify)

1. **Azimuth curve** (44100, 1 rep each): 0 → 0.000, 45 → **+3.465**,
   90 → +4.612, 135 → **+4.195**, 180 → 0.000, 225 → **−4.195**,
   270 → −4.612, 315 → **−3.465** dB. Exact mirror pairs 45↔315 and 135↔225
   (0.149 196 12/0.100 114 2 vs 0.100 114 2/0.149 196 11).
2. **Channel-swap falsifier** (the labrat's untested item (i)): crossing the FC
   outputs into the recorder's ports (`output_FL→input_FR`, `output_FR→input_FL`)
   gives **ILD −4.612** (L 0.095 677 1, R 0.162 704 81) vs +4.612 unswapped —
   the asymmetry is physical, not an analysis artifact (`axes2-rigart.json`).
3. **Runtime control change** (scout row 9, man-page claim): the Props param
   exposes `s0:Azimuth` / `s0:Elevation` / `s0:Radius` **on `r100b_sofa_in`
   only** (`has_azimuth` true; the `_out` node exposes none).
   `pw-cli set-param <id> Props '{ params = [ "s0:Azimuth" 90.0 ] }'` → rc 0,
   read-back **0.0 → 90.0**, and the capture's ILD series steps
   **0.000 → +4.612 dB** inside the same take (`timing-runtime.json`
   `rt_az0_to_90`, 100 ms windows).
4. **Front/back spectral sign flip**: 997 Hz az180 vs az0 = **+2.34 dB** where
   440 Hz gave −1.45 dB — a frequency-dependent sign, i.e. a real HRTF spectral
   feature rather than a level offset (`axes-rigart.json` `multi_*`).
5. **`gain` is exactly linear**: 0.5 → 0.081 352 52 (½ of 0.162 704 82),
   2.0 → 0.325 409 88 (2×). `normalize=true`, `blocksize=128`, `tailsize=2048`,
   `latency=256` are **indistinguishable** from the default at the rms level.
   **Filter-chain rate ladder** (IR resampled): az90 ILD **4.612** @44100,
   **4.616** @48000, **4.614** @88200, and `n_samples` 512 / 558 / 1115 at
   44100 / 48000 / 96000. (The 22050 and 96000 *az90* ladder legs were lost to
   zero-frame captures in the axes arm, which predates the retry policy — see §7.)
6. **Reference-tap transfer** (closes the "not a pass-through" argument with a
   direct witness): input 0.353 528 99 → az0 out 0.116 451 55 (**−9.6421 dB**),
   az90 out −6.73 dB (L) / −11.35 dB (R). The scout's −9.642 dB comparison against
   the *file* rms was numerically valid because the null sink passes unity.
7. **Private core / clock invariance**: private `pipewire` + private
   `wireplumber -p r100b` (a drop-in profile with **no** hardware monitors; the WP
   log contains **0** `alsa` lines, so no operator device is enumerated) gives,
   for az90 @44100: q512 **4.612**, q1024 4.612, q2048 4.612, server rate 44100
   4.612, 96000 4.612; az0: 0.116 451 55 / 0.116 451 8. The shared graph
   reproduces to ~1e-5. **The sofa pins are not a shared-graph artifact.**
   *Negative result recorded:* a **bare** private core (no session manager) creates
   the nodes but **never creates their ports** (`pw-link` lists nothing; every
   link attempt `rc 255 "No such file or directory"`) — the private-core axis
   requires a session manager (or manual port creation).
8. **Sibling presence**: with a second filter chain (`r100b_sib_in/_out`) live,
   az90 = 4.611 and az0 = 0.116 466 44 — no material change (the 1.3e-4 delta is
   the same window-landing wobble).
9. **Source-loss / relink / driver-drop timing** (`timing-*.json`, 100 ms series):
   - killing the `pw-play` source mid-tone → the FC output goes to **exact
     silence with no error and no state change** (the chain does not error);
   - `unlink`+`relink` of `output_FL→input_FL` (`rc 0` both) leaves the **L
     channel silent for the rest of the take** — re-creating a link does **not**
     resume the flow; the untouched R channel continues;
   - `unlink`+`relink` of the *input* link (`sink monitor → FC`) → output
     continues (`rc 0` both);
   - unloading the driver (null sink) mid-stream → the chain runs ~1 s then goes
     silent (`nodes_after` shows the FC nodes alive, no driver);
   - unloading the FC mid-stream → the post-tap stream ends (capture truncated).

---

## 5. Receipt index (this seat)

`corpus/live/r100-boundary/` (~140 files, `MANIFEST.sha256` at the root):

- `probes/r100b_sofa.py` — leg rig (axis knobs, both analysis recipes, series,
  namespace-scoped sweep, own-PID discipline); `probes/r100b_hog.py` — own-load hog.
- `r100b_run.py` — arms, hog lifecycle (pid + starttime verified, reaped), retry,
  incremental receipts; `r100bsb.py` — private-core sandbox;
  `r100banalyze.py` — replay-cell comparison; `r100balign.py` — waveform alignment;
  `r100bwindow.py` — coarse-vs-fine window witness; `mkmanifest.py`.
- `receipts/` — `{quiet,load}-{gate,azimuth,extra,fgprobe}.json`,
  `load-mismatch.json`, `mismatch-mismatch.json`, `axes-*.json`, `axes2-*.json`,
  `timing-*.json`, `sandbox-{smoke,clock}.json`, `census-{entry,exit}-*.json`,
  `hogs-*.json`, `hog-kill-*.json`, `loadavg-*.jsonl`.
- `runs/*.log` (verbatim arm logs), `raw/enum_*.txt` (Props dumps, incl. the
  `s0:Azimuth` block), `scratch/*.wav` (every capture + stimuli),
  `scratch/{compare,align,window-landing,fine-ild}.json`, `sandbox/` (private-core
  runtime dir, logs, conf, the `r100b` WP profile drop-in).

**Custody disclosure.** The `scratch/*.wav` captures are keyed by leg tag, and
several tags are reused across arms (`sofa_44k_az90_r0` appears in the quiet, load
and fgprobe stages), so the file on disk is the **last** write of that tag; the
per-leg analysis in `receipts/` is the authoritative record for each arm. The
alignment/window witnesses above use tags that are unique (`cap_fg_*`,
`cap_clock_*`, `cap_sofa_48k_rep*`) or the scout's own files.

---

## 6. Contention ledger (foreign — observed, never touched)

| window | contact | effect |
| --- | --- | --- |
| whole seat | **84 foreign `yes`** + **12 `r93b_hog`** (sibling r93-boundary), 64–96 orphaned hogs earlier; sibling nodes `r93b_in/_fc_*`/`r93b_rec/_ref` in the shared graph | load1 100–117 ambient, 131 at the load-arm peak; the dominant contention; nothing foreign was signalled (every kill is filtered on `r100b` + identity) |
| whole seat | sibling seats live on the host (r93-boundary hogs, other lanes' probes) | the 44100/53500-class excursions r98 saw were not observed here; the live clock witness (`graph_witness_mid.clock`) recorded the graph rate/quantum per leg |
| axes arm | **6 zero-frame captures** (client died before producing data, `play_stop rc=1`, rec links gone) in ~40 s windows | rig flake, r98 §3.5 class; retried from the mismatch arm on (0 further failures in 32 legs) |
| residue | `~/.local/state/wireplumber/stream-properties` gains rows for `r100b_in` (the r90/r95 class) | disclosed, not hidden; no CLI deletes them |

---

## 7. Remaining `[?]`, risks, blockers

1. **B1 — no quiet arm exists on this host** (load1 never below ~100). The load
   arm (+16 hogs, load1 98→131) changed **no** verdict field: ILD, ports, links,
   n_samples, the no-config error, teardown and the capture pins are identical in
   both arms. The laws are load-robust as far as this host can tell.
2. **Rig flake is real and quantified**: **10/136** legs produced a zero-frame
   capture (3 consecutive load-mismatch reps + 7 scattered axes reps). The retry
   policy (one fresh process) recovered every one; author rows built on this rig
   should retry on `frames == 0`, never on `rms == 0` (the no-config cell is
   legitimately silent with frames > 0).
3. **The 1.0–1.3e-4 offset of the scout's 48 k rep is not fully explained.** The
   private-core clock axis rules out the graph rate/quantum; the coarse-vs-fine
   witness explains 2.3e-5 of it; the residual is a window/stimulus-edge effect
   (my captures are longer than the scout's). An author row for the mismatch cell
   must fix the capture length, not just the rate.
4. **`[?]` Link re-creation does not resume flow** (relink_out) — reproduced once;
   the mechanism (link lifetime vs stream activation) is not resolved and a second
   shape (relink both channels, or relink after a delay) was not run.
5. **`[?]` The runtime control change was measured once** (`rt_az0_to_90`). The
   second leg (`rt_az90_to_270`, read-back 270.0 confirmed) was truncated by the
   rig: the post-action's own latency (3 `pw-cli` calls + 2 Props dumps) exceeded
   the tone, so the play was stopped before the change took effect. Post actions
   must run with a longer tone or be issued from a separate process.
6. **`[?]` The `pw-play` hang** seen once in the exploratory smoke (fg shape,
   no link, `timed_out`) did not reproduce in the 12 fgprobe legs. Not resolved.
7. **Not measured (bounded scope)**: the IR/latency row (single-sample delta
   through the spatializer — the scout's row 8), `latency=` semantics at the
   sample level, and the exact dereference behind the no-config −22 (the class is
   pinned; the frame is not).

## 8. Labrat fold (frozen `probeParent` — exactly one read-only child, advisory)

One read-only `ufo-labrat` was dispatched against this seat's own artifacts with
five predeclared attacks. **Toolset limit disclosed: read/grep/glob only — no
exec**, so it could not re-run a leg; it attacked the receipts and the JSON.

| attack | verdict | what it read |
| --- | --- | --- |
| **H1** window-landing premise | **SUPPORTS** | recomputed the seat's coarse values against the scout's own published `rms`/`win_offset` in `r100-scout/runs/sofa_azimuth.json`: az0 0.11650363 @ 8820 **exact match**, az90 0.16277655 @ 59976 **exact match**. It also found something the seat had not highlighted: the scout's **own** az90 reps landed at *different* coarse offsets (12348 / 42336) with *different* rms (0.16278089 / 0.162781) — i.e. the coarse-stride instability is visible inside the scout's own three reps. Folded into §3.1(c) territory; strengthens the verdict. |
| **H2** ≤1 LSB / block localization | **CONTRADICTS (as first written)** | correctly found that `scratch/align.json` carried **no positional field**, so the "one contiguous 2 663-sample block" sentence was unreceipted; also computed mismatch counts (2 734 / 1 704 / 2 924 / 1 577) from `exact_frac` that did not match the quoted 2 663. **Acted on:** `r100balign.py` was upgraded to emit `gt1lsb_samples`, `mismatch_blocks` and `residual_outside_blocks`, the witness was re-run, and §3.2 now carries the post-correction table (block starts 80 896–80 903, lengths 1 569–2 667, residual max **exactly 1 LSB**). The child's counts agree with the block lengths within the 1 LSB threshold difference. |
| **H5** quoted-token control drop | **SUPPORTS** | `axes2-argvorder.json`: the `quoted` leg logs `making spatializer with 0.000000 …` while every unquoted leg logs `90.000000 …`; it also ruled out the failure alternative from the receipts (`play rc=0`, `rec rc=1` = the normal SIGTERM exit, `nonzero 76325`, node states `running`, links established) → the drop is **parsing**, not transport. |
| **H3** channel-swap sign flip | **SUPPORTS** | read the crossed link argv (`output_FL→input_FR`, `output_FR→input_FL`) in `axes2-rigart.json` and the `ild_db = −4.612` vs `+4.612` flip. |
| **(e)** namespace / tracked-write discipline | **SUPPORTS (partial)** | every `killed` array in the receipts is empty; every created object name is `r100b*`; foreign objects (`alsa_*`, `Midi-Bridge`, `r83a_*`, foreign module ids) appear only in **census** fields, never in creation records. "Zero tracked writes" is **UNVERIFIABLE from artifacts** (needs `git status`) — the parent confirms it separately in the header. |
| **not checked** | — | the sandbox clock axis (H4) and the WP `alsa`-free log claim were not read (lower priority once H2 fell); the child also could not verify anything requiring execution. |

Net: **three hypotheses supported, one contradicted and then repaired into a
receipted claim, one partially supported.** The child created no artifacts and
touched no PipeWire object.

*Boundary leaf — attacked, measured, not judged.*
