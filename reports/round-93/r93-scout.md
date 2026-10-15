# R93 scout — `ebur128`: the SPA filter-graph loudness node, measured

Round 93 pre-measurement. Host `plazir27`, measured **2026-10-15 18:58–20:20 UTC**
(15:58–17:20 UTC−3). Repo `~/Projects/shokunin/audio-shokunin` @ HEAD **`b7d80d0`**
(tracked-dirty at entry is the sibling-owned `corpus/fixtures/__pycache__/*.pyc`
only — never read, imported or executed here). Toolchain: PipeWire **1.6.8**
(`1:1.6.8-1`), WirePlumber **0.5.17-1**, libebur128 **1.2.6-2**, ffmpeg n9.0.1,
Python 3.14.7, gcc 16.2.1, Linux 7.2.3-arch1-3.

**Seat: SCOUT (leaf). Zero tracked-file writes; the only file written outside
`corpus/live/r93-scout/` is this report.** Every leg is triple-bounded (element
bound in argv + wall cap + byte cap; `start_new_session` + `os.killpg`, plus
`RLIMIT_CORE=0` because `pw-cli` aborts on stdin EOF — r92 §2.7). Seat-owned
names only (`r93s_*`); module unloads are index-verified (pw-cli module var from
the same session; the null sink by the exact `pactl` module id returned at load);
sweeps unload only modules whose short listing carries the seat name; **no
`pactl set-default-*` was ever issued**. Defaults read live at entry and exit:
sink `…HiFi__SPDIF__sink`, source `…HiFi__Line__source`, unchanged. Final sweep:
**0 `r93s` nodes, 0 `r93s` modules, 0 `r93s` processes**, `sha256sum -c
manifest.sha256` = 258/258 OK.

**Label legend.** `[O]` = directly observed on this host in this window (probe
output, receipt or on-disk file read). `[I]` = read from version-matched source
(fetched upstream 1.6.8 tag / installed headers) or inferred from measured laws.
`[?]` = not resolved by this seat.

---

## 0. Why this surface (the pick, and what it displaces)

r92 named the highest-value leftovers in priority order. This seat took **(a)
`ebur128`** — the province's own loudness axis — because it is the only candidate
that yields a **numeric transfer function with an independent reference**: an own
BS.1770 implementation (libebur128-matched K-weighting + gating) plus an
`ffmpeg ebur128` cross-witness can *falsify* the node's every readout, not just
describe it. (b) the wpexec/Lua Settings cross-witness is an API-namespace
debugging exercise whose outcome is bounded by r90's already-pinned 25-key
lattice and r92's failure mode; (c) the pw-dump/pw-mon lattice is an observation
surface without a reference value. The pick also drains r92 §8.5 verbatim
("`ebur128`'s port/control inventory and its loudness output … the single most
valuable next cell") and re-checks r92 claim 4 (label inventory).

**Headline: the node is a working, sample-accurate BS.1770 *mono* loudness meter
whose per-port channel semantics are dead — every one of the 7 input ports reads
the same value — and whose notify outputs are only observable graph-internally
(the `debug` label is the readout). Three silent failure classes make a loaded
meter a liar: deferred activation failure, a NaN-only mode, and stale Peak/True
Peak values.**

---

## 1. Headline claims

| # | claim | label | sharpest single fact | evidence |
| --- | --- | --- | --- | --- |
| 1 | **Port topology is 7 audio in / 7 audio out / 7 notify, with exact names.** | `[O]` | `loaded n_input:7 n_output:7 n_control:0 n_notify:7`; notify = `Momentary LUFS Shortterm LUFS Global LUFS Window LUFS Range LU Peak True Peak` | `receipts/recon1.json` port table; §2 |
| 2 | **Notify values are not in any node param; the only external readout is a `debug` node logging them at INFO per quantum.** | `[O]` | `enum-params <fc node> Props` shows only audioconvert props (volume/mute/channelVolumes/params) — no LUFS key in any rep; linking `{output="e:Momentary LUFS",input="dbg:Control"}` yields `[I][…][plugin_builtin.c: 2627 debug_run()] control: -9.024196` every 42.7 ms | `receipts/recon1.json`, `recon4.json`, `recon5.json`, every stage receipt `log_sample` |
| 3 | **Momentary is an exact BS.1770 K-weighted 400 ms loudness** (single state, LEFT weight). | `[O]` | own reference matches **to ≤1e-5 dB** at 6 amplitudes (1.0→0.03125) and 5 frequencies (40 Hz–10 kHz), 3/3 reps; ffmpeg `ebur128` on the same stimulus reads `-9.0 LUFS` vs measured `-9.024196` | `receipts/amp.json`, `freq.json`, `refflat.json` |
| 4 | **The per-port channel map is dead: all 7 input ports read identical loudness.** | `[O]` | Momentary plateau `-9.024196` on FL, FR, FC, **UNUSED**, SL, SR and **DUAL MONO** — 21/21 legs; the intended DUAL-MONO ×2 (+3.01 dB), surround ×1.41 (+1.5 dB) and UNUSED exclusion never apply | `receipts/portmap.json` |
| 5 | **Momentary/Shortterm/Window are a *dB-domain mean* over connected states; Global is a *block-energy average* across states — no stereo summation.** | `[O]` | FL+FR (same tone): Momentary `-9.024196` (no +3 dB), Global `-9.39…-9.50` (no +3 dB); FL 0.5 + FR 0.05: Momentary `-19.024195` = mean of `-9.024196` and `-29.024196` (energy mean would be `-11.99`) | `receipts/stereo.json`, `mix.json` |
| 6 | **One silent channel poisons Momentary to `-inf`** (dB mean with `-inf`), while Global stays finite. | `[O]` | FL tone + FR silence → Momentary all `-inf` (3/3, 387 lines each), Global `-9.39…-9.50` | `receipts/stereo.json` |
| 7 | **The relative gate works and excludes a −40 dB section; the histogram arm agrees.** | `[O]` | loud/quiet(−40 dB)/loud: Global `-9.64` (an ungated mean would read ≈`-12.4`); Momentary tracks `-49.0242` = `-9.0242 − 40` exactly; `use-histogram=true` agrees within 0.04 dB | `receipts/gating.json` |
| 8 | **Linking only `Window LUFS` leaves the lib mode empty → the node is a pass-through whose meter is constant NaN.** | `[O]` | only-Window: **241/241 values `-nan`** (3/3) while the audio still flows (`post_nz=166911`, rms 0.261); only-Range and only-Peak read `0.0`; only-Global reads a real value | `receipts/modes.json`; C witness `receipts/ebur_witness.txt` (`init(mode=0) -> NULL`, `init(mode=I) -> OK`) |
| 9 | **Peak/True Peak are wrong for any input port other than `In FL`** (state index used as channel number). | `[O]` | FL → `0.5`/`0.5`; **DUAL MONO → `0.0`** (tail `4.29`/`4.37`); stereo FL=0.2/FR=0.8 → **`0.2`** (FR's 0.8 peak ignored) — 3/3 each | `receipts/peaks.json`; C witness `sample_peak(ch=6) rc=3 out unchanged` |
| 10 | **`max-window` is honored in milliseconds; absent → constant NaN.** | `[O]` | decay-length law: 0.05 s→50 ms, 0.4→400 ms, 1.0→1 s, 2.0→2 s, 5.0→5 s (30 dB-down at tone-end + window); absent (0) → `-nan` 241/241 | `receipts/window.json` |
| 11 | **`max-history` is a block-count cap, not a time window: silence never evicts.** | `[O]` | burst 1.5 s + 5 s silence: default (10 s) and `max-history=2.0` both hold `≈-9.83`; two bursts (2.5 s @0.5 + silence + 2.5 s @0.25): default `-11.49…-11.56`, 2.0 s `-15.54…-15.67` (first burst evicted) | `receipts/history.json`, `hist2.json` |
| 12 | **`lufs2gain`: `gain = 10^((target−LUFS)/20)`, exactly; `target` clamps to [−70, 0]; non-finite LUFS → `1.0`.** | `[O]` | default target −23 → `0.2086…0.2112` (audio-domain ratio 0.199–0.206); target 0 → `2.945159` (3/3); target −100 → clamped → **`0.000932`** (6/6 across two arms); digital silence → `1.0` (3/3) | `receipts/lufs2gain.json`, `l2gcheck.json`, `ctlgrammar.json` |
| 13 | **A control key containing a space must be quoted; the raw form is a load failure.** | `[O]` | `control={Target LUFS=-100}` → `[W] properties.c:264 update_string() error parsing more than 0 properties: Expected object key` + `Error: "Could not load module"`; `control={"Target LUFS"=-100}` loads | `receipts/ctlgrammar.json` (3/3 each) |
| 14 | **The builtin label table is 32 entries (source); 31 load, `null` does not.** | `[O]`+`[I]` | loads: the 26 of r92 + **`debug ramp zeroramp sqrt busy`**; `null` fails in 5 graph shapes with the terse `Error: "Could not load module"` (no `[E]` line reaches the client) | `receipts/labels.json`, `labels2.json`, `nullprobe*.json`; `sources/plugin_builtin.c.txt` `builtin_descriptor()` |
| 15 | **The audio path is bit-exact and the module's own error classes are loud, warning-only, or deferred.** | `[O]` | aligned dual tap: `max_abs_diff = 0.0` at lag 0/±1024 (3/3); `config={bogus=1}` = `[W]`-only and works; `config={max-history=abc}` = module load **rc 0** but `[E] … cannot create plugin instance … Invalid argument` at activation, meter dead | `receipts/passthrough.json`, `edge.json` |
| 16 | **`Global LUFS` sits ≈0.13 LU below an independent measurement of the same signal.** | `[O]` | `amp_500_Global_r0`: plugin `-9.382176` vs own reference on that leg's capture `-9.254570`; `ffmpeg ebur128` on the parallel capture reads `-9.3 LUFS`; offset is amplitude-independent (`-0.128` dB at 0.5/0.125, `-0.128…-0.149` at 0.03125) | `receipts/amp.json`, `refflat.json`; mechanism `[?]` §7 |

---

## 2. The readout path (the finding authors need first)

The notify ports are **output control ports internal to the graph**. Measured:

- `[O]` They do **not** appear in the node's `Props` param. `pw-cli enum-params
  <fc_in> Props` (interactive session; one-shot `printf | pw-cli` races and
  returns nothing) shows only audioconvert props: `volume`, `mute`,
  `channelVolumes`, `channelMap`, `softMute/softVolumes`, `params` — **no LUFS
  key**, mid-tone, 3 samples (recon1/recon4). `pw-dump <id>` mid-tone likewise.
- `[O]` They are not in `pw-mon`/`pw-dump -m` output either (the module emits
  `Props` only for *control* ports — `impl_get_props` loops `graph->n_control`).
- `[O]` **The working readout is the builtin `debug` label**: link any notify
  port to `dbg:Control` and the plugin logs
  `[I][HH:MM:SS.µs][plugin_builtin.c: 2627 debug_run()] control: <value>`
  at INFO level **every graph quantum** (2048 frames = 42.7 ms on this host).
  `control: -nan`, `control: -inf` and `control: -9.024196` are the three
  observed literals. Do not connect the debug node's audio `In` — it dumps raw
  float memory into the log.
- `[O]` The intended audio-domain consumer also works: `e:Global LUFS →
  l2g:LUFS`, `l2g:Gain → lin:Mult`, audio through `lin:In→lin:Out` — the gain
  is applied to the samples (measured ratio ≈ gain, §3.9).

**Readout shape (verbatim, 3/3):**

```
filter.graph = {
  nodes = [ {type=ebur128,name=e,label=ebur128},
            {type=builtin,name=dbg,label=debug} ]
  links = [ {output="e:Momentary LUFS",input="dbg:Control"} ]
  inputs = ["e:In DUAL MONO"]  outputs = ["e:Out DUAL MONO"]
}
audio.channels=1  audio.position=[MONO]
capture.props={node.name=r93s_fc_in,node.autoconnect=false,media.class=Audio/Sink}
playback.props={node.name=r93s_fc_out,node.autoconnect=false}
```

---

## 3. Cells measured

273 stage legs (plus ~30 recon/null-probe legs; ~100+ bounded legs required).
All numbers below are 3-rep plateaus (median of the longest near-equal run,
`stats` in `probes/r93driver.py`).

### 3.1 Port map (`portmap`, 42 legs)

| readout | FL | FR | FC | UNUSED | SL | SR | DUAL MONO |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Momentary LUFS | **-9.024196** ×3 | **-9.024196** ×3 | **-9.024196** ×3 | **-9.024196** ×3 | **-9.024196** ×3 | **-9.024196** ×3 | **-9.024196** ×3 |
| Global LUFS | -9.382176 ×2, -9.388371 ×1 | -9.382176 ×2, -9.387122 ×1 | -9.382176 ×2, -9.383840 ×1 | -9.388371 ×3 | -9.382176 ×3 | -9.382176 ×3 | -9.382176 ×3 |

`[O]` 21/21 identical Momentary values; the 0.006 dB spread on Global is
block-grid phase (see §4). Own reference computed on each leg's captured
pre-tap matches Momentary to **0.000000** in all 7 port checks.

`[I]` Cause: the plugin calls `ebur128_set_channel(st[i], i, channels[i])` on
**1-channel** states; only `i==0` is a legal channel number. The C witness shows
`set_channel(0,DUAL_MONO) rc=0`, `set_channel(6,DUAL_MONO) rc=3`,
`set_channel(1,SL) rc=3`, and the plugin ignores the return — every state keeps
the 1-channel default map `LEFT` (weight 1.0).

### 3.2 Amplitude ladder (`amp`, 27 legs)

| amp | Momentary (measured) | own reference | Δ |
| --- | --- | --- | --- |
| 1.0 | -3.003596 | -3.003596 | 0.000000 |
| 0.5 | -9.024196 | -9.024196 | 0.000000 |
| 0.25 | -15.044795 | -15.044795 | 0.000000 |
| 0.125 | -21.065395 | -21.065395 | 0.000000 |
| 0.0625 | -27.085995 | -27.085995 | 0.000000 |
| 0.03125 | -33.106594 | -33.106595 | 0.000001 |

6.0206 dB per doubling, exact; convergence from first finite value to within
0.1 LU = **0.384 s** (the 400 ms window). Global rows (0.5/0.125/0.03125):
plugin − reference = **−0.128 dB** (systematic, see claim 16).

### 3.3 K-weighting transfer (`freq`, 15 legs)

| f | Momentary | Δ vs 1 kHz | own K-weighting Δ |
| --- | --- | --- | --- |
| 40 Hz | -15.288830 | −6.2646 | −6.265 |
| 100 Hz | -10.855398 | −1.8312 | −1.831 |
| 1000 Hz | -9.024196 | 0 | 0 |
| 4000 Hz | -5.753903 | +3.2703 | +3.270 |
| 10000 Hz | -5.680018 | +3.3442 | +3.344 |

### 3.4 Stereo / mixing (`stereo` 24 legs, `mix` 6 legs)

| shape | Momentary | Global |
| --- | --- | --- |
| mono FL / mono FR | -9.024196 ×3 / ×3 | -9.388371 ×3 |
| stereo FL+FR same tone | -9.024196 ×3 | -9.390468…-9.495832 |
| stereo FL tone, FR silence | **-inf** ×3 (all 387 lines) | -9.390054…-9.495832 |
| stereo FL 0.5 + FR 0.05 | **-19.024195** ×3 | -9.382176/-9.383840 |

`[O]` dB-mean law pinned: `(−9.024196 + −29.024196)/2 = −19.024195`; the energy
mean would be −11.99. Global excludes the quiet channel by the relative gate
(equal to the FL-only value).

### 3.5 Notify-only coupling (`modes`, 15 legs)

| linked notify only | readout | audio post |
| --- | --- | --- |
| Momentary | -9.024196 ×3 | flows (`nz` 166911, rms 0.261) |
| Global | -9.388371 / -9.495832 ×2 | flows |
| Range | 0.0 ×3 (steady-tone LRA is 0.0; states exist) | flows |
| Peak | 0.0 ×3 (index bug; tail 4.29/4.37) | flows |
| Window | **-nan 241/241 ×3** | flows |

`[O]` The Window-only arm is a **NaN meter on a live pass-through**: the notify
set determines the libebur128 mode bits; `modes[3]` (Window) is `0`, so a
Window-only graph initializes with mode 0, `ebur128_init` returns NULL (C
witness), and the plugin writes `0/0` = NaN forever. The audio path is
unaffected.

### 3.6 Window matrix (`window`, 18 legs)

| `max-window` | plateau | 30 dB-down after tone end | law |
| --- | --- | --- | --- |
| absent (0) | **-nan 241/241** | — | 0-frame query |
| 0.05 | -9.024196 | +0.04 s | 50 ms window |
| 0.4 | -9.024196 | +0.38 s | 400 ms window |
| 1.0 | -9.024196 | +1.00 s | 1 s window |
| 2.0 | -9.024196 | +2.00 s | 2 s window |
| 5.0 | -9.383840 (frozen) | not reached | 5 s window |

`[?]` **Source-vs-binary divergence:** the upstream 1.6.8 tag source
(`sources/plugin_ebur128.c.txt`) contains a version-gated
`max_window = (max_window + 999) / 1000` compat hack for libebur128 1.2.5/1.2.6
that, on the installed lib (whose setter clamps `<400` to 400), would make
`max-window ≥ 1 s` a stale `0.0`. The installed binary does **not** exhibit it
(measured 1 s/2 s/5 s windows). Which revision the Arch 1.6.8-1 package was
built from is unresolved.

### 3.7 History (`history` 6 legs, `hist2` 6 legs)

`[O]` After one burst + 5 s of silence, default and `max-history=2.0` both hold
`≈-9.83` (silence blocks are below the absolute gate and are never inserted, so
nothing evicts). With a second, quieter burst the 2 s cap evicts the first:
default `-11.49…-11.56` vs 2.0 s `-15.54…-15.67` (3 reps each; own reference
`-11.45…-11.50` for the default).

### 3.8 Peaks (`peaks`, 18 legs)

| shape | Peak | True Peak |
| --- | --- | --- |
| mono `In FL` | **0.5** ×3 | **0.5** ×3 |
| mono `In DUAL MONO` | **0.0** ×3 (tail 4.29/4.37) | **0.0** ×3 |
| stereo FL 0.2 / FR 0.8 | **0.2** ×3 | **0.2** ×3 |

`[I]` `ebur128_sample_peak(st[i], i, …)` is called with the state index; for
1-channel states `i≥1` returns rc 3 and writes nothing (C witness), so `value`
is stale/uninitialized. On `In FL` the readout is correct.

### 3.9 lufs2gain (`lufs2gain` 15, `l2gcheck` 6, `ctlgrammar` 6 legs)

| arm | gain plateau | predicted |
| --- | --- | --- |
| default target (−23) | 0.208652–0.211248 | 0.208501 |
| target 0 | 2.945159 ×3 | 2.945159 |
| target −100 (clamped −70) | 0.000932 ×6 (l2gcheck + ctlgrammar) | 0.000931 |
| digital silence | 1.0 ×3 | 1.0 (`isfinite` guard) |
| unquoted key | load failure ×3 | — |

`[O]` Audio-domain application: default arm `audio_ratio` = 0.199215–0.206203
(mid-tone post/pre RMS) against a logged gain plateau of 0.2086–0.2112.
`[O]` **Anomaly recorded, not hidden:** the *first* `lufs2gain` run of the
`target_m100` arm (19:42, peak sibling contention) measured 0.007451/0.034498,
which would imply a Global of −27.4/−40.8. The dedicated `l2gcheck` leg (Global
and Gain in the same run) reads Global −9.38…−9.50 and gain 0.000932 — the
anomaly is a run-window transient under load, not a semantic; the clamp law is
pinned 6/6.

### 3.10 Grammar / errors / labels (`edge` 9, `ctlgrammar` 6, `labels` 36, `labels2` 9, `nullprobe` 10 legs)

- `[O]` `config={bogus=1}` → `[W] plugin_ebur128.c:127 ebur128_instantiate()] ebur128: unknown key bogus`, loads, momentary works.
- `[O]` `config={max-history=abc}` → module load **succeeds** (rc 0), then
  `[E] plugin_ebur128.c:106 … ebur128:max-history requires a number` +
  `[E] spa.filter-graph | [filter-graph.c:1644 impl_activate()] cannot create
  plugin instance 0 rate:48000: Invalid argument` — the meter never activates
  (no readout at all).
- `[O]` Stream/graph port-count mismatch (`inputs=["e:In FL","e:In DUAL MONO"]`
  on a 1-channel stream) → `[W] filter-graph.c:1888 setup_graph()] The input
  stream has 1 ports and the filter has 2 inputs … Some filter ports will be
  unconnected..`, loads, one state live.
- `[O]` Label loads: `debug ramp zeroramp sqrt busy` **load 3/3**; `avg gain min
  nop passthrough sum` fail 3/3 (r92's fail set reproduced); `null` fails in all
  5 shapes tried, with `Error: "Could not load module"` and **no `[E]` line in
  the client log** (unlike the bad-label class, which is loud).
- `[O]` Bit-exact audio: `max_abs_diff = 0.0` at quantum-aligned lag
  (0, +1024, −1024 across reps) on an 8192-sample in-tone window.

---

## 4. Rep stability

- **Exact (byte-stable across reps):** every Momentary plateau (21/21 portmap,
  18/18 amp, 15/15 freq, 3/3 mix, 3/3 gating), the `-nan` Window-default
  (241/241 ×3), Peak/TruePeak values, gain plateaus for target 0 and the clamped
  target (3/3 and 6/6), silence gain 1.0 (3/3), label load matrix (36+9 legs).
- **Stable to ±0.007 LU:** Global plateaus within a port/config (e.g. FL
  -9.382176 ×2 + -9.388371 ×1).
- **Stable to ±0.11 LU:** Global across *runs* of the same shape (stereo
  `both` -9.390…-9.496). Cause `[I]`: the gated value depends on how many
  partial-ramp 100 ms blocks land on the stream's block grid, i.e. tone-onset
  phase; the spread is amplitude-independent.
- **Cadence:** control lines arrive every **42.7 ms** → graph quantum 2048
  frames at 48 kHz (the null sink's quantum), not 1024.
- **Contention classes seen:** one Global rep of `hist2_max-history=2.0` drifted
  0.13 LU (tone-onset late under sibling load), the m100 l2g arm anomaly
  (§3.9), and 2/42 portmap Global reps at the outer spread. All are *timing*
  effects; no readout class changed sign or semantics.

---

## 5. Authorability directives

**Verbatim-ready cells** (≥3 reps, byte-stable, exact argv in the receipts):

1. **Arm + read** — §2 shape; feed `r93s_in:monitor_MONO → fc_in:playback_MONO`
   (first try, 3/3) and read the log for `control:` lines.
2. **Calibration row** — 1 kHz sine, f32, amp 0.5, mono: `Momentary = -9.024196`
   (any input port), `Global = -9.382…-9.388`. Own reference on the same
   captured signal: `-9.024196 / -9.2546`; `ffmpeg ebur128`: `I: -9.0 LUFS`.
3. **K-weighting deltas** — 40 Hz −6.265, 100 Hz −1.831, 4 kHz +3.270,
   10 kHz +3.344 (dB vs 1 kHz).
4. **Gain law** — `gain = 10^((target − Global)/20)`; target 0 → `2.945159`,
   default −23 → `0.2085`, clamped −70 → `0.000932`, silence → `1.0`.
5. **Window config** — `max-window` in **seconds** in the config (converted to
   ms internally): 0.4→400 ms, 1.0→1 s, 2.0→2 s; **omit it and Window LUFS is
   NaN**; do not link Window without also linking Momentary or Shortterm.
6. **Grammar pins** — quote control keys containing spaces
   (`control={"Target LUFS"=-100}`); quote link port names; `#` is a comment
   even inside quotes (r92).
7. **Label pins** — usable: the 26 of r92 **plus `debug ramp zeroramp sqrt
   busy`** (31); do not use `null` (in the source table, fails every shape).

**Envelopes for bimodal cells** (never arm as a single shape):

- **Meter-dead envelope**: `rc 0` + "module loaded" + "nodes present" is *not*
  validity. A loaded chain can be (a) a working meter, (b) a **deferred
  activation failure** (`max-history=abc`: no readout ever), (c) a **NaN meter**
  (Window-only: `-nan` forever), (d) a **stale-value meter** (Peak/True Peak on
  any port but `In FL`; Range/Peak-only `0.0`). Arm a *readout*, not a load.
- **Silence envelope**: `-inf` (energy 0 / digital silence, or a silent channel
  in the dB mean) vs `-nan` (mode-0 init, 0-frame window) vs `0.0` (Peak/Range
  loops that never ran, Window never written). Three distinct literals, three
  distinct causes.
- **Channel envelope**: any single-port routing except `In FL` is an *alias of
  FL*; DUAL MONO is **not** +3.01 dB; UNUSED is **not** excluded; SL/SR are
  **not** 1.41. A stereo pair does **not** sum: Momentary is the dB mean,
  Global the block-energy average.
- **Global is not ffmpeg's I**: expect ≈0.13 LU lower than an independent
  BS.1770 measurement of the same signal on this host.

**Crash classes** — no new ones: the r92 `pw-cli` EOF abort (rc 134) stands and
was avoided by always sending `quit`; `RLIMIT_CORE=0` on every child; every leg
tears down through the same session and the stage sweep asserts zero seat
objects. No core files were produced.

---

## 6. Falsifications of prior claims

| claim (source) | falsifier | outcome |
| --- | --- | --- |
| r92 claim 4: "the builtin filter table is **26 labels**" | source table + 12-label load matrix | **falsified** — the table is 32 entries; 31 load (26 + `debug ramp zeroramp sqrt busy`), `null` is unusable. r92's candidate set simply omitted 6 labels |
| r92 §8.5: "`ebur128`'s port/control inventory … not captured" | §1–§3 | **answered** (ports, notify names, readout path, semantics) |
| man page: "7 input ports … corresponding to the different input channels" | portmap 21/21 | **falsified** — every port reads the same; the channel map is never applied |
| man page: "Global LUFS … over the max-history window" | history + hist2 | **falsified as a time window** — it is a block-count cap over *above-gate* blocks; silence never evicts |
| man page: Momentary "400ms window and 75% overlap" | cadence + convergence | refined — the *value* is a 400 ms window recomputed **every quantum** (42.7 ms), not every 100 ms |
| blog claim: `Shortterm` must be written `Shorttem` (typo) | measured port table + source | **not present on 1.6.8** — `Shortterm LUFS` is the name |
| my own inference from the 1.2.6 GitHub source: `init(mode=I)` fails → Global-only would be `-inf` | C witness + `modes` stage | **falsified** — installed lib: `init(mode=I) -> OK`; Global-only works. The host lib differs from the fetched tag |
| my own inference: DUAL MONO would read +3.01 dB | portmap | **falsified** — identical to FL |
| my own inference: stereo Global would sum channels (+3 dB) | stereo | **falsified** — block-energy average, no summation |
| my own inference: `max-window=2.0` would be a stale `0.0` (source hack) | window matrix | **falsified for the installed binary** — a real 2 s window; source/binary divergence flagged `[?]` |

---

## 7. Remaining unknowns

1. `[?]` **Installed-plugin revision vs the fetched 1.6.8 tag** — the max-window
   unit hack (§3.6). Candidate explanations: package built from a different
   commit, or an upstream fix not in the tag I fetched.
2. `[?]` **Why `label=null` fails** with a terse client error and no `[E]` line
   (5 shapes, 3 reps on two of them).
3. `[?]` **Mechanism of the −0.128 dB Global offset** vs own reference/ffmpeg
   (block-grid phase or an extra ramp block in the plugin's list; the offset is
   amplitude-independent).
4. `[?]` **Range LU on a dynamic program** (only the steady-tone `0.0` was
   measured; `ffmpeg` reads LRA 7.9 LU on the captured leg).
5. `[?]` **True Peak oversampling semantics** (no intersample-peak stimulus was
   used; only the index bug was measured).
6. `[?]` `capture.volumes`/`playback.volumes` mapping a notify port to stream
   volume (not exercised; the r92 control-port gap remains for volumes).
7. `[?]` r92 leftovers not addressed by this seat: wpexec `Settings`
   cross-witness; f2 all-suspended topology; 5/12 shipped configs; no-config
   `sofa`; mixer-silence cause; `bq_raw` coefficients.
8. `[?]` The m100 first-run anomaly class (transient under contention) was
   attributed, not deliberately reproduced.

---

## 8. Contention ledger + exit state

| window | contact | effect |
| --- | --- | --- |
| whole window | sibling lanes: `r78_play_sink_699104`, `r78lat_*`/`r78prop_*` taps, `r84b_*` (hogrec/hogvol), `r85b_*` (sdrec), `r82ff_*` (pwrec), `r90b_ns_a/b`, `r96s_ns` (present at exit), desktop `blender` client, foreign playback on `…SPDIF__sink` | read-only contact; my listings carried their rows; no foreign object touched |
| 19:41–19:53Z (lufs2gain/labels) | heaviest sibling load observed | one l2g arm transient (§3.9), one hist2 Global rep drift 0.13 LU; all attributed |
| whole window | this seat: 273 stage legs + ~30 recon/probe legs, one null sink + one pw-cli-loaded chain per audio leg, all unloads verified | own residue zero at every stage sweep |
| exit | `pactl list modules short` r93s = 0; `pw-dump` r93s nodes = 0; `ps` r93s audio children = 0; defaults SPDIF/Line unchanged; `sha256sum -c manifest.sha256` 258/258 | clean |

---

## 9. Artifacts & provenance

`corpus/live/r93-scout/` (untracked, 258 files, 216.9 MB, `manifest.sha256`
verified): `probes/pwlib93.py` (bounded runner + f32 WAV I/O + own synth + own
libebur128-matched K-weighting/gating reference), `probes/r93driver.py` (19
stages), `probes/recon1..5.py`, `probes/ebur_witness.c` (+ compiled
`ebur_witness`), `probes/nullprobe.py`, `probes/analyze.py`,
`probes/build_manifest.py`, `run_all*.sh`; `receipts/*.json` (one per stage,
per-leg triple-bounded) + `receipts/ebur_witness.txt`; `sources/` (fetched
1.6.8/1.2.6 sources with `FETCHED-SOURCES.sha256`); `runs/` (stage logs +
`SUMMARY.txt`); `RECEIPTS.md`.

Key receipts: `portmap.json`, `amp.json`, `freq.json`, `stereo.json`,
`mix.json`, `modes.json`, `window.json`, `history.json`, `hist2.json`,
`peaks.json`, `lufs2gain.json`, `l2gcheck.json`, `ctlgrammar.json`,
`edge.json`, `labels.json`, `labels2.json`, `nullprobe*.json`,
`passthrough.json`, `gating.json`, `recon*.json`, `ebur_witness.txt`.

On-disk sources read: `/usr/share/man/man7/libpipewire-module-filter-chain.7.gz`
(1.6.8), `/usr/include/ebur128.h` (1.2.6), the installed
`/usr/lib/spa-0.2/filter-graph/libspa-filter-graph-plugin-ebur128.so`
(strings + `objdump -d`), `/usr/lib/libebur128.so.1.2.6` (linked C witness).

*scout leaf — measured and read, not judged.*
