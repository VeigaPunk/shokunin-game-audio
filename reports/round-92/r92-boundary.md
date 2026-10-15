# R92 boundary — falsification of the r92 scout: filter-chain DSP replayed, IR varied, clamps hunted, load applied

**Seat: BOUNDARY (executor-class, leaf).** Host `plazir27`, lane
`~/Projects/shokunin/audio-shokunin` @ HEAD at entry **`58adad60`** (the scout
measured `a98c674`; another lane moved HEAD to `00d44595` mid-window — see the
deltas below). Window **2026-10-15 20:33–21:30 UTC**. Toolchain re-verified:
PipeWire **1.6.8**, WirePlumber **0.5.17-1**, pactl 17.0-98-gb096, Python 3.14.7,
numpy 2.5.3.

**Zero tracked-file edits, no commits, no `set-default-*`, no `pw-metadata`
writes.** Every write is under `corpus/live/r92-boundary/` (`probes/*.py`,
`receipts/*.json`, `runs/*.log`, `scratch/*.wav`) plus this report. **Every audio
object is named `r92b_*`**; every census/sweep matched only that prefix; module
unloads are index-verified against `r92b_` before the call. Exit state:
`pactl list short modules | grep r92b` → 0, `pw-dump` → 0 `r92b_*` nodes,
`ps` → 0 `r92b_*` audio children, **0 own CPU burners** (`pgrep -af
"110351524[5]"` → empty).

**Host-state deltas during the window (not caused by this seat).** (a) The
operator's **USB audio device disappeared** mid-window: the entry snapshot
(20:33Z) had `…usb-Generic_USB_Audio…HiFi__SPDIF__sink` as default sink and
`…HiFi__Line__source` as default source; at exit `pactl list short cards` shows
only the two PCI cards and `pactl list short sinks | grep -c HiFi` = **0**, while
WirePlumber's runtime metadata moved to `default.audio.sink =
{"name":"alsa_output.pci-0000_01_00.1.hdmi-stereo.99"}` — **the *configured*
default (`default.configured.audio.sink`) still names the SPDIF sink**, i.e. a
runtime re-selection after a device vanished, not a `set-default-*` write by any
seat. (b) HEAD moved **`58adad60` → `00d44595`** and the tracked-dirty set grew
from `{…measure_audio.cpython-314.pyc}` to `{….pyc, corpus/fixtures/measure_audio.py}`
(+2264 lines, mtime 18:22 local) — **another lane's work**; this seat wrote
nothing outside its own two paths. (c) Foreign lanes were live throughout,
including `r83a_ns_a/b_1271909` and, at exit, a second filter-chain rig
(`r93b_in`, `r93b_fc_in`, `r93b_fc_out`).

**Instrument.** An *independent* rig (`probes/rig.py`): own WAV I/O (s16/s24/f32),
own numpy DFT, own **analytic** RBJ reference (complex response — not an impulse
simulation), single null-sink driver, PRE/POST dual tap, `node.autoconnect=false`
on every stream, every child `start_new_session` + wall cap + killpg +
`RLIMIT_CORE=0`. **No scout module, no sibling fixture was imported.** All 9
stages are triple-bounded and end with `SWEEP clean: True`.

**Labrat.** The single permitted `probeParent` labrat was dispatched once,
read-only, for: *"are the report's §4 convolver numbers and §3 contested rows
supported by the raw captures on disk?"* It returned **CONTRADICTED** (the two
§3 rows appear in no file under `corpus/live/r92-scout/`; the receipted values
are `-0.0/-0.023/-3.0/-5.967` and `-13.822/0.0/-11.979/-23.652`), plus two
nuances I re-verified myself: **no §3 capture WAV exists on disk at all**, and
`3/3 byte-identical` is verifiable for **no** leg (at most 2/2 where ≥2 captures
survive). Zero side effects; it could not read binary WAVs with its read-only
toolset, so every number below is this seat's own measurement.

---

## 0. Verdict table

| # | r92 scout claim | verdict | sharpest measured fact |
| --- | --- | --- | --- |
| 1 | C5 `copy` = bit-exact unity | **CONFIRMED** | 0.000 dB at 200/1000/4000/12000/**20000** Hz, 3/3 reps |
| 2 | C5 "biquads reproduce RBJ to 0.01 dB" | **CONFIRMED (11/13 rows) — report table FALSIFIED in 2 rows** | my live replay matches an independent analytic RBJ within **0.001–0.031 dB** on all 11 rows, and the *receipts* agree — but the **report's** `bq_highshelf`/`bq_bandpass` rows are off by **~1.85 dB** and match no artifact on disk |
| 3 | C5/§3 heading "3/3 **byte-identical**" | **NOT REPRODUCIBLE** | my raw captures differ in size and hash every rep (out sizes 172076 / 174124 / 178220 B; no two files share a sha); the *analysis* is stable to 0.000 dB, and the selected window is byte-identical in 2/3 reps (copy, lowpass) and 3/3 (highshelf) — the honest statement is "analysis-stable", not "byte-identical" |
| 4 | C6 convolver is a true **sample-exact FIR** engine | **CONFIRMED, strengthened** | full-convolution residual **≤ 0.5 LSB (s16) over 8256 samples**, incl. a **512-tap** IR, **3/3 under load** |
| 5 | C6 "route latency is deterministic … same absolute sample index 15460" | **FALSIFIED as stated** | the impulse index moves in **exactly ±1024-sample steps** (`blocksize`): 14436 / 15460 / 16484 / 17508 across reps and legs; only *differences* within a leg are stable |
| 6 | C6 "IR `[1.0@0,0.5@64]` → gap 64, ratio 0.49997" | **CONFIRMED** | gap 64; ratio 0.499970; first tap 0.999939, second 0.4999695 |
| 7 | C6 (implicit) the IR kernel is reproduced exactly | **REFINED — rate-dependent** | a **44.1 kHz** IR in a 48 kHz graph is **resampled**: 47-tap windowed-sinc kernel, peak at **+110** samples (100·48000/44100 = 108.8) |
| 8 | C7 silent failure is the default for `convolver` (no config / bad path), **zero `[E]`/`[W]` lines** | **CONFIRMED, level-independent** | graph *loads* (`loaded n_input:1 n_output:1 n_control:0 n_notify:1`) and **E=0, W=0 at `PIPEWIRE_DEBUG=3` *and* `=5`** (full logs on disk); output is **exact digital zeros** (f32 `0x00000000`, `nz_exact=0`) |
| 9 | C7 silent class extends to other malformed paths | **EXTENDED** | an **empty** file, a **text** file named `.wav`, and a **directory** path are all silent with E=0/W=0 — identical class |
| 10 | C8 typo'd control name is warning-only, audio silently wrong | **CONFIRMED for a *typo*** | `Delay=0.01` → `[W] parse_control() control 'Delay' can not be set`, node loads, delay stays 0 |
| 11 | C8 (implicit) the fix is just the real name | **FALSIFIED — a space in an unquoted key kills the whole graph** | `control={Delay (s)=0.01}` → `[W] properties.c:264 … Expected object key` (col 122) → `[E] load_graph() missing filter.graph property` → **no graph, 3/3**; the **quoted** form `control={"Delay (s)"=0.01}` loads **clean (no warning)** |
| 12 | C9 `Gain` is clamped to its advertised [-120, +20] | **CONFIRMED at both exact bounds** | `Gain=20.000` → RBJ(+20) exact; `20.5` → same; `Gain=-120.000` → skirts match RBJ(-120) to 0.01 dB; `-120.5` → same |
| 13 | C9 "`Freq` is **not** clamped (99999 → flat 0.000 dB)" | **CONFIRMED + sharpened: there is a >Nyquist guard, not a no-op shrug** | `Freq=49000` and `97000` **alias exactly onto 1 kHz**, yet measure **0.000 dB at all five probes** — an unguarded biquad would read −3.012 dB at 1 kHz; the filter is a **pass-through** above Nyquist |
| 14 | C9 "`Freq=0`/negative → silence … degenerate → **NaN**/zero, no guard" | **FALSIFIED (the NaN half)** | f32 capture of both legs is **exact zeros** (`nz_exact=0`, `nan=0`, `inf=0`) → the node emits digital silence, never NaN |
| 15 | C9 clamping is per-control, not uniform | **CONFIRMED + extended to Q** | `Q=10` → RBJ(10) exact (+20.000 dB at fc); `Q=10.5` and `Q=1e9` → **identical to Q=10** (clamped); `Q=-1` → **identical to Q=0.707** (default) |
| 16 | §4 "`delay` did **NOT** delay" | **FALSIFIED** | with the **quoted real name** `control={"Delay (s)"=0.01}` the impulse moves by **exactly 480 samples** (=0.01 s × 48 kHz), single clean sample, 3/3 (1504 = 480 + one block in the third rep) |
| 17 | §4 `delay-10ms` → no delay | **CONFIRMED as an artifact of the typo** | the scout's own args (`Delay=0.01`) → shift 0; the node is fine |
| 18 | C9 (implicit) the advertised `b0..a2` control ports are usable | **FALSIFIED — they are inert** | `bq_lowpass` with `control={b0=1,b1=0,b2=0,a0=1,a1=0,a2=0}` still measures the 1 kHz lowpass; `a0=0` does **not** divide by zero, no NaN |
| 19 | (implicit) the advertised `Gain` port is meaningful on every `bq_*` label | **FALSIFIED** | `bq_lowpass … Gain=6.0` measures the plain 1 kHz lowpass — the port is advertised on all 9 controls but honored only where the label uses it |
| 20 | (new) `bq_raw`'s direct-coefficient path | **FALSIFIED — unreachable from module args** | the label loads (`n_control:9`) but `control={b0..a2}`, `config={coefficients=[…]}` and no-config **all** emit exact digital silence (2/2 each) |
| 21 | C10 `pw-cli` aborts on stdin EOF; only `quit` exits cleanly | **REFINED — stdin-kind dependent** | `/dev/null` (file EOF) → **SIGABRT rc 134** 3/3 (`remove_from_poll()`); **pipe EOF → HANGS** (no exit; killed at the 6 s cap) **5/5** and 3/3 in-stage; `quit` → rc 0 3/3 |
| 22 | C12 `wpexec` `LocalModule` builds a live graph and self-cleans | **CONFIRMED, incl. the error path** | `pcall ok=true`, `<WpImplModule:0x…>`; `r92b_wpx_in/out` visible during, **0 links**, `[]` after, 3/3; a script that **errors 1.8 s after** a successful load also leaves `[]` |
| 23 | C12/§6 wpexec W2/W3 `[?]` bare `Lua runtime error` | **CLOSED — two named triggers** | `rawget` (W2) and `Core.require_api` (W3) are **nil in the sandbox**; calling either ⇒ rc 70, bare `Lua runtime error` (no location). `Settings` **is** a global table and `Settings.get_boolean(...)` works (returned `false`) |
| 24 | C12 `wpexec` self-cleaning + error classes | **EXTENDED** | `LocalModule` with a bad module name **or** a bad label → `pcall ok=true, mod=nil` (**silent**); an **empty** script **hangs** (rc −9 at the cap, 3/3) |
| 25 | §3 `bq_notch` = −93.977 dB | **REPRODUCED (my replay: −93.812) but the number is an instrument floor** | same filter, steady window: **−105.87 dB (s16 floor)**, f32 4-tone: −114.80, f32 steady window: **−127.01** — a 33 dB spread from window/stimulus alone |
| 26 | C13/C14/C15 absent classes (ffmpeg/LADSPA/LV2) | **CONFIRMED (read-only)** | the SPA filter-graph dir holds exactly **6 files, no `ffmpeg`**; **`/usr/lib64/ladspa` and `/usr/lib/ladspa` do not exist at all** (the report says "0 entries" — sharper: absent); `/usr/lib/lv2` = **25** bundles |
| 27 | C16 shipped `…-kemar.conf` loads but is silent (missing IR dirs) | **CONFIRMED (read-only)** | the only `*kemar*`/`*hesuvi*` hits under `/usr/share/pipewire` are the two **`.conf` files themselves** — no `hrir_kemar/`, no `hrir_hesuvi/` |
| 28 | C1 nodes die with `pw-cli`; C2 `node.autoconnect` gate | **CONFIRMED** | every one of 9 stages ends `{nodes:[],modules:[],procs:[]}`; 0 SPDIF links in every census; the gate's cited source lines re-read verbatim (`rescan.lua:145-149`, `174-178`) |
| 29 | C3 capture stream has no ports without `media.class` | **NOT re-armed by this seat** (out of scope; my rig always sets `media.class=Audio/Sink`) | — |
| 30 | C4 label table: the six non-labels | **CONFIRMED (load-only A/B, 2/2)** | `gain nop passthrough sum avg min` → **`Error: "Could not load module"`, no `@module:`**; `copy`/`bq_lowpass`/`convolver` → `@module:` |
| 31 | C11 `links=[…]` needs quoted port names; `#` is a comment even inside quotes | **CONFIRMED (load-only A/B, 2/2)** | quoted-colon loads; unquoted-colon and an LV2 URI containing `#` both fail with `Error: "Could not load module"` |
| 32 | new — `delay` clamp law | **MEASURED** | exact for every request ≤ `max-delay` (`0.001→48`, `0.01→480`, `0.02→960`, `0.049→2352`, `0.05→2400` samples); every request **above** it clamps to **2431 samples** (6/6: `0.051/0.06/0.1`) |

---

## 0b. Bottom line for an author

* **The DSP core is real and reproducible**: unity `copy`, RBJ-exact biquads
  (≤0.03 dB over five probes), a convolver that is sample-exact **to the s16 LSB
  over 8k samples including a 512-tap IR and under CPU+graph load**, and a delay
  that is exact to the sample once you arm it correctly.
* **Three ways to be silently wrong**: a typo'd control name (`Delay`) is a
  warning; a **spaced control name unquoted** (`Delay (s)`) kills the whole graph
  with a *parse* error; and a `convolver` with a bad/missing/empty/non-WAV IR is
  **silent with zero `[E]`/`[W]` at debug 3 *and* 5** — measure, never trust rc 0.
* **Trust no dB below ≈−90**: the s16 capture floor plus the max-RMS window rule
  make deep-attenuation rows (notch, clamped-negative Gain) read 30–60 dB high;
  the "silence" cells are exact zeros, and the notch is ≥127 dB down in f32.
* **Absolute latency is ±1 block**: the impulse index moves in 1024-sample steps
  between runs — quote the *difference* between two legs, never a route constant.
* **Two advertised surfaces are dead**: the `b0..a2` coefficient ports (inert for
  every `bq_*` label, `bq_raw` silent in all three arms) and `Gain` on labels that
  do not use it.

---

## 1. Headline falsification — the report's §3 table contains two rows its own receipts contradict

The report's §3 table (`reports/round-92/r92-scout.md`) states, for
`bq_highshelf Freq=4000 Q=0.707 Gain=−6`:
`−1.865 / −1.843 / −3.000 / −5.979` and for `bq_bandpass Freq=1000 Q=1`:
`−15.555 / 0.000 / −13.832 / −25.506`.

Four independent lines disagree:

| source | bq_highshelf @200/1k/4k/12k | bq_bandpass @200/1k/4k/12k |
| --- | --- | --- |
| report table | −1.865 / −1.843 / −3.000 / −5.979 | −15.555 / 0.000 / −13.832 / −25.506 |
| `receipts/v2_dsp.json` (3/3 rows) | **−0.0 / −0.023 / −3.0 / −5.967** | **−13.822 / 0.0 / −11.979 / −23.652** |
| `runs/v2_all4.log:35-40` (3/3) | same as the receipt | same as the receipt |
| analytic RBJ (numpy, this seat) | **−0.000 / −0.023 / −3.000 / −5.967** | **−13.822 / −0.000 / −11.979 / −23.651** |
| this seat, live re-measure (3/3) | **−0.0 / −0.023 / −3.0 / −5.967** | **−13.821 / 0.0 / −11.979 / −23.652** |

The six report values appear in **no file** under `corpus/live/r92-scout/`
(labrat grep, confirmed by my own `grep -rn` over `*.json`/`*.log`/`*.md` in the
seat tree: zero hits). The deviation is ~1.85 dB on the *skirt* bins only — the
same magnitude as the seat's own disclosed "phantom −1.83 dB route loss"
(§7.1 defect 1, the fixed-window analysis) — so the most likely provenance is a
stale pre-fix run; the artifacts to prove that were not kept.

**Consequence.** Claim 5's headline ("reproduce RBJ to 0.01 dB") survives — on
the eleven rows whose numbers are faithful, my independent analytic reference
agrees to **0.001–0.031 dB** — but the table as printed is not trustworthy row
by row, and the two bad rows are exactly the ones a shelf/band-pass author would
copy.

## 2. The notch row is an instrument floor, not a filter response

The report's `bq_notch` row (−93.977 dB at fc) is **reproducible** — my replay
with the same 4-tone stimulus measures **−93.812 dB** — but it is not the notch's
depth. Measuring the *same* filter three ways:

| instrument | measured attenuation at 1 kHz |
| --- | --- |
| 4-tone stimulus, scout's max-RMS window, **s16** capture | −93.812 dB (scout: −93.977) |
| same, **f32** capture | −114.803 dB |
| single 1 kHz tone, **steady** window (abs 24000–48000), s16 | −105.872 dB (out max = exactly 1 LSB) |
| same, **f32** | **−127.013 dB** |

Two mechanisms, both measured: (a) the **s16 output floor** is 1 LSB of a
near-zero signal, and (b) the scout's **max-RMS window rule inverts** on
deep-attenuation legs — in a near-silent output the loudest 0.5 s window is the
**tone-onset transient** (my single-tone leg: out window offset 14400, containing
a 0.2735 spike at the tone start; the steady window contains only ±1 LSB dither).
The scout's §7.1 fixed the *opposite* failure (window in the prefill) with a rule
that fails here. **Any number in this surface below ≈−90 dB must be read as
"below floor", not as a filter response** — which also applies to every
"−273.9 dB" cell in the report (those are exact zeros).

## 3. `delay` — the control works; a space in an unquoted key is a *load* failure

The scout's §4 concluded "`delay` did NOT delay … the control is named
`Delay (s)`". Measured now, with the delta stimulus (single-sample impulse):

| args | impulse shift | notes |
| --- | --- | --- |
| `control={Delay=0.01}` (the scout's args) | **0** | `[W] … control 'Delay' can not be set` — reproduced |
| `control={Delay (s)=0.01}` (bare, spaced key) | **no graph at all**, 3/3 | `[W] properties.c:264 update_string() error parsing more than 0 properties: Expected object key` @ col 122 → `[E] load_graph() missing filter.graph property` → `[E] impl_init() can't load graph: Invalid argument` |
| `control={"Delay (s)"=0.01}` (**quoted**) | **+480 samples**, 3/3 (one rep +1024 = one block) | single clean sample, no smear; **no `[W]` at all** |
| `control={"Delay (s)"=0.001}` | **+48** | |
| `control={"Delay (s)"=0.1}`, `max-delay=0.05` | **+2431** (2/2, ±1024 block) | the over-max request clamps to **2431 samples ≈ 0.0506 s**, *not* 2400 |

So the author-facing law is sharper than the report's: **a control name
containing a space is expressible only as a quoted key; the bare form destroys
the entire graph (not a warning), and the quoted form actually applies the
value.** The report's "delay did not delay" is an artifact of its own typo.

## 4. Control lattice: bounds, guards, inert ports

All rows below are 2–3 reps, byte-stable in analysis, and compared against the
analytic RBJ reference computed for the *same* parameters.

| control | measured | law |
| --- | --- | --- |
| `Gain=20.000` | 1.543 / **20.000** / 2.216 / 0.182 / 0.013 | = RBJ(+20) exactly |
| `Gain=20.5` | identical to `20.000` | **clamped to +20** |
| `Gain=-120.000` | −46.363 / (−104.4 s16 floor) / −48.305 / −36.369 / −24.908 | skirts = RBJ(−120) to 0.01 dB; fc bin is the **float32 floor** (−107.543 in f32), not −120 |
| `Gain=-120.5` | identical to `-120.000` | **clamped to −120** |
| `Q=10` | 0.352 / **+20.000** / −23.927 / −47.334 / −69.671 | = RBJ(Q=10) |
| `Q=10.5`, `Q=1e9` | identical to `Q=10` | **clamped to 10** (new) |
| `Q=-1` | identical to `Q=0.707` | negative Q → **implementation default** (new) |
| `Freq=49000`, `97000` | **0.000 at all five probes** | alias-exact discriminator: unguarded RBJ would read −3.012 dB @1 kHz; it does not → **guard above Nyquist ⇒ pass-through** |
| `Freq=24000`, `24001` | 0.000 at all five probes | consistent (RBJ at Nyquist is b≡a = identity) |
| `Freq=0`, `Freq=-1000` | **exact digital zeros**; f32: `nan=0, inf=0, nz_exact=0` | silence, **not NaN** — the report's "NaN/zero" is half wrong |
| `control={b0=1,b1=0,b2=0,a0=1,a1=0,a2=0}` on `bq_lowpass` | the 1 kHz lowpass (−0.007/−3.012/−24.477/−47.370) | advertised ports **inert** via the args path |
| `control={…,a0=0,…}` | identical lowpass; no NaN, no divide-by-zero | inert, not dangerous |
| `Gain=6.0` on **`bq_lowpass`** | identical to the plain lowpass | the `Gain` port is advertised on every `bq_*` label but **honored only by the labels that use it** |
| `bq_raw` + `control={b0=1,b1=0,b2=0,a0=1,a1=0,a2=0}` | **exact digital silence**, 2/2 | the raw label loads (`n_control:9`) but the port coefficients are not applied |
| `bq_raw`, no config | **exact digital silence**, 2/2 | default coefficients are zero |
| `bq_raw` + `config={coefficients=[1,0,0,1,0,0]}` | **exact digital silence**, 2/2 | the key I guessed is ignored — the per-rate raw path was not otherwise reached |
| `Freq=-24000` | **exact digital silence**, 2/2 | RBJ at −Nyquist is the **identity** (b ≡ a) → a formula-only implementation would pass audio; silence ⇒ **negative Freq is guarded**, not computed |

## 5. Convolver: sample-exactness at scale, under load, and its limits

The sharp instrument is the **full-convolution residual**: the captured POST tap
compared sample-by-sample against the *file's own quantised IR* × the quantised
delta, at the best alignment lag (the two `pw-record` taps are separate streams,
so the lag is searched over ±4096).

| leg | IR | residual | lag |
| --- | --- | --- | --- |
| `ir-2tap` | `[1.0@0, 0.5@64]` | **0.5 LSB** over 8256 samples, 0 samples >1 LSB | 0 / 1024 |
| `ir-2tap-g0.5` | same, `gain=0.5` | **0.25 LSB**; first tap 0.499969 | 0 / 1024 |
| `ir-d100` | delta@100 | **0.0 LSB** | 0 / 1024 |
| `ir-decay512` | 512-tap exp. decay (0.99) | **0.5 LSB** over 8256 samples | 0 / 1024 |
| `ir-dc64` | 64 × 1/64 | **0.016 LSB** | 0 / 1024 |
| `ir-s24` / `ir-f32file` | same 2-tap as 24-bit / float32 WAV | **0.5 LSB** | 0 / ±1024 |
| `load-ir-2tap` | 2-tap, **6 CPU burners + a second seat sink fed by a live stream** | **0.5 LSB, 3/3** | 0 |

New limits found by varying the IR:

* **Rate.** A delta@100 stored as 44100 Hz in a 48000 Hz graph comes out as a
  **47-nonzero-sample windowed-sinc kernel**, peak at **+110** (predicted
  100 × 48000/44100 = 108.8; side lobes 0.243 / −0.158 / 0.131 / −0.131). The
  kernel is **resampled to the graph rate**, so "sample-exact" is a
  same-rate property.
* **Channels.** A 2-channel IR into a mono chain yields **only channel 0's
  tap** (+10), silently dropping channel 1's (+20).
* **`tailsize` does not truncate.** A spike at offset 1500 of a 4096-tap IR is
  present with `tailsize=1024` *and* `tailsize=4096` (gap 1500, ratio 0.899988).
* **Clipping.** `gain=4.0` on a 1.0-amplitude tap yields **0.999969, 0.999969**
  — the output hard-clips at full scale; no wrap, no NaN.
* **Silent class.** `no config`, `/nonexistent/…`, an **empty file**, a **text
  file**, and a **directory** path all load, stream, and emit **exact digital
  zeros** (`nz_exact=0` in s16 *and* f32) with **E=0/W=0 at debug 3 *and* debug
  5** (`runs/b9_dbg5_missing.log`, 8715 lines, 3412 `[D]`, **0 `[E]`, 0 `[W]`**).
  The graph really does load: `loaded n_input:1 n_output:1 n_control:0 n_notify:1`.
* **Latency is block-quantised.** The impulse index is *not* a fixed route
  constant: across reps/legs I measured **14436 / 15460 / 16484 / 17508** —
  differences of exactly ±1024 = the configured `blocksize` — and the PRE/POST
  taps' relative lag is 0 or ±1024. The scout's per-leg *differences* remain
  valid (that is how it used them), but any absolute latency statement is ±1
  block.

## 6. `wpexec` — error classes and the closed `[?]`

| leg | result (3/3) |
| --- | --- |
| `print` + `Core.quit()` | rc 0, `Lua 5.5` |
| `Core`, `LocalModule`, `Settings` globals | `table` / `function` / **`table`** |
| `require_api` global | **`nil`** |
| `rawget(_G, 'Core')` | **rc 70, bare `Lua runtime error`** ← W2's trigger |
| `Core.require_api("support.settings")` | **rc 70, bare `Lua runtime error`** ← W3's trigger |
| `Settings.get_boolean('node.stream.restore-props')` | rc 0, **`false`** — the settings cross-witness *is* reachable |
| `local x = nil; print(x.y)` | rc 70, bare `Lua runtime error` (no location, no stack) |
| `LocalModule(bad module)` / `LocalModule(bad label)` | `pcall ok=true, mod=nil` — **silent failure**, no nodes during |
| `LocalModule(ok)` | nodes `r92b_wpx_in/out` visible during, **0 links**, `[]` after |
| load, then `error()` 1.8 s later | nodes visible during, **`[]` after** — self-cleans on the error path |
| no `Core.quit()` | hangs (alive at 1.4 s, killed at the cap) |
| **empty script file** | **hangs**, rc −9 at the cap 3/3 |
| syntax error / missing file / directory | rc 70 with a *precise* message (`Failed to compile…`, `Could not locate script …`) |
| no argv | rc 70 `Could not locate script '(null)'` |

## 7. `pw-cli` EOF — two classes in one window

| stdin | result |
| --- | --- |
| `quit` on a pipe | rc 0, 3/3 |
| `/dev/null` (file EOF) | **rc 134 SIGABRT** + `'source->loop == &impl->loop' failed at …loop.c:189 remove_from_poll()`, 3/3 |
| **pipe EOF** (Python `subprocess`, writer closed) | **no exit — hangs**, killed at the 6 s cap: **5/5** (and 3/3 in-stage) |

So "always send `quit`" is right, but the *stated mechanism* ("aborts on EOF") is
a property of a **file** EOF only; the natural scripted case (`cmd | pw-cli`)
**hangs** instead.

## 8. Cheap replays (labels, grammar, absent classes) — `receipts/b8_cheap.json`

Load-only A/B, 2/2 each, one `pw-cli` per variant (`quit` always sent; no sink,
no audio, no links):

| variant | result | verbatim |
| --- | --- | --- |
| `label=gain`, `nop`, `passthrough`, `sum`, `avg`, `min` | **no load, 2/2 each** | stderr `Error: "Could not load module"` (no `@module:` on stdout) |
| `label=copy`, `bq_lowpass`, `convolver` | load, 2/2 | `@module:` printed |
| `links=[{output="b1:Out",input="b2:In"}]` | load, 2/2 | — |
| `links=[{output=b1:Out,input=b2:In}]` | **no load, 2/2** | `Error: "Could not load module"` |
| `plugin=http://example.org/r92b#none` | **no load, 2/2** | `Error: "Could not load module"` (`#` starts a comment even inside quotes) |

Read-only inventory:

* `/usr/lib/spa-0.2/filter-graph/` = `libspa-filter-graph.so` + the five plugins
  `builtin, ebur128, ladspa, lv2, sofa` — **no ffmpeg** (C13 confirmed).
* `/usr/lib64/ladspa` and `/usr/lib/ladspa` — **`ls: cannot access … No such file
  or directory`** (C14 confirmed; sharper than "0 entries": the directories are
  absent, which is why the plugin's search path prints `No such file or directory`).
* `/usr/lib/lv2` = **25** entries (C15 confirmed: the inventory is spec/schema
  bundles, and a URI with `#` cannot even be expressed — see the grammar row above).
* `find /usr/share/pipewire -name '*kemar*'` → **only
  `…/filter-chain/sink-virtual-surround-5.1-kemar.conf`**; `*hesuvi*` → only the
  matching `.conf`. **No `hrir_kemar/` or `hrir_hesuvi/` IR directory exists**
  (C16 confirmed: the shipped virtual-surround config loads as a silent chain).

## 8b. The `delay` map (`receipts/b7_delay.json`, `max-delay=0.05`)

| request | expected samples | measured shift |
| --- | --- | --- |
| 0 s | 0 | **0, 0** |
| 0.001 | 48 | **48**, 1072 (= 48 + one block) |
| 0.01 | 480 | **480**, 1504 (= 480 + one block) |
| 0.02 | 960 | **960, 960** |
| 0.049 | 2352 | **2352**, 3376 (= 2352 + one block) |
| 0.05 (exactly `max-delay`) | 2400 | **2400, 2400** |
| 0.051 | 2448 | **2431, 2431** ← clamped |
| 0.06 | 2880 | **2431**, 3455 (= 2431 + one block) |
| 0.1 | 4800 | **2431**, 3455 |

So: **the delay is exactly `round(seconds × rate)` samples for every request up
to `max-delay`, and clamps to 2431 samples above it** (6/6 over-max reps). 2431 =
2432 − 1 = `ceil(2400/32)·32 − 1`, which is a plausible buffer-rounding artefact
but is *inference*, not measurement. Every impulse is a **single clean sample**
(no interpolation smear), including at the clamp.

---

## 9. Harness disclosure, contention, and own-process kills

* **Foreign lanes were live for the whole window**: `r91b_*` (r91-boundary,
  its own null sinks + pw-play/pw-record) and `r100s_*` (r100-scout) were
  measured running concurrently; `…SPDIF__sink` carried their rows. My censuses
  and sweeps matched only `r92b`; no foreign object was touched.
* **Rig defects found and fixed inside this seat**: (1) `Rig`'s first version
  hard-coded `PIPEWIRE_DEBUG=3`, so the debug-5 A/B legs failed to link (44-byte
  captures) — re-run as a dedicated log-only stage (`b9`) and reported as such;
  (2) my first `wav_write` had no channel parameter, so the stereo-IR fixture
  was written mono — fixed and re-armed; (3) `b5` crashed on a str/int key
  mismatch in the RBJ reference (in-process int keys vs JSON string keys) — the
  crash is in the log, the stage was re-run.
* **Two legs were re-tried** by the rig's own validity gate (`ir-bad-missing`
  rep 1, `ir-bad-*` attempts) — recorded per row as `attempt`.
* **Kills**: every child is `killpg`-ed by its own wall cap; the 6 CPU burners
  and the extra load sink/player were stopped and unloaded in a `finally` block;
  `R.live_r92b()` reports `{nodes:[],modules:[],procs:[]}` at the end of all 9
  stages.
* **Not armed by policy**: `node.autoconnect=true` (would link a stream to the
  operator's default sink — the scout measured that class once; this seat
  declines to repeat it), and `filter.smart`/daemon-config paths.

## 10. Remaining unknowns

1. The provenance of the report's two bad §3 rows (stale pre-fix run vs
   transcription) — unfalsifiable now, the pre-fix captures were not kept, and
   **no §3 capture exists on disk at all** (labrat finding, re-checked).
2. `sofa`/`spatializer` silent-config behaviour and its port inventory — not
   re-armed (out of this assignment's scope; the scout's `[?]` stands).
3. `ebur128` port/control inventory (the scout's "most valuable next cell") —
   not re-armed here.
4. Why the `delay` clamp lands on **2431** samples rather than 2400 (measured
   6/6, unexplained; `2432 − 1 = ceil(2400/32)·32 − 1` is only a candidate).
5. Whether the ±1024 lag jumps are the driver's or the filter-chain's block
   phase (both taps move, and in some reps they move *independently* — so at
   least one jump is on the capture side and one on the graph side) — I can
   state the quantisation, not the owner.
6. `bq_raw`'s direct-coefficient path: **CLOSED (negative)** — the label loads with
   `n_control:9`, but `control={b0..a2}` and `config={coefficients=[…]}` both
   yield **exact digital silence** (2/2 each), and the no-config arm is silent
   too; the direct-coefficient surface is unreachable from module args on this
   host. (The man page's own key name for the raw config was not otherwise
   reached, so a differently-named key is not excluded.)
7. Whether the `bq_notch` residual at fc is input quantisation noise, float32
   arithmetic noise, or onset-transient leakage — my three instruments bracket
   it (≤−127 dB in the best case) but do not name it.

## 11. Artifacts & provenance

`corpus/live/r92-boundary/` (untracked): `probes/rig.py` (own bounded runner +
WAV I/O + numpy DFT + analytic RBJ), `probes/b1_replay.py`, `b2_clamp.py`,
`b3_ir.py`, `b4_wpexec.py`, `b5_extras.py`, `b6_diag.py`, `b7_delay.py`,
`b8_cheap.py`, `b9_dbg.py`, `analyze_ir.py`, `align.py`; `receipts/*.json`:

| receipt | stage | what it holds |
| --- | --- | --- |
| `b1_replay.json` | B1 | 11 §3 rows replayed × 3 reps + independent RBJ per row, the two contested rows, `param_eq`, 3 `delay` name forms, notch floor in s16 vs f32 |
| `b2_clamp.json` | B2 | Gain/Q/Freq edges, alias/Nyquist discriminators, coefficient-control inertness, 6 f32 legs, `pw-cli` EOF classes |
| `b3_ir.json` | B3 | 21 IR legs × 2–3 reps: pins, content/rate/length/format variation, malformed paths, tail/tailsize, clipping, the under-load pin |
| `b3_posthoc.json` | B3 | alignment-searched residual in LSB, 44.1 kHz kernel shape, stereo channel choice, delay shifts, clip values |
| `b4_wpexec.json` | B4 | 20 wpexec legs × 3 reps incl. the error ladder and live-graph censuses |
| `b6_diag.json`, `b9_dbg.json` | B6/B9 | debug-level A/B; `runs/b9_dbg{3,5}_{missing,noconfig}.log` are the **complete** pw-cli client logs |
| `b5_extras.json` | B5 | `Freq=-24000` guard discriminator, `bq_raw`'s three coefficient arms, `Gain` inert on `bq_lowpass` |
| `b7_delay.json` | B7 | the delay map (9 requests × 2 reps) |
| `b8_cheap.json` | B8 | label/grammar load-only A/B + read-only inventory |

`runs/*.log` hold the full stage logs; `scratch/` holds every own stimulus, IR
fixture and captured WAV (each receipt records `out_sha16`/`ref_sha16` so any
number above can be re-derived from the bytes).

On-disk sources re-read (read-only): `/usr/share/wireplumber/scripts/linking/rescan.lua`
(lines 145-149, 174-178 — the `node.autoconnect` gate), the SPA plugin inventory
`/usr/lib/spa-0.2/filter-graph/`, `/usr/lib64/ladspa`, `/usr/lib/ladspa`,
`/usr/lib/lv2`, and the `hrir_*` search under `/usr/share/pipewire`.

*boundary leaf — measured, falsified, not judged.*
