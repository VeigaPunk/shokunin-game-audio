# r92 author — the `libpipewire-module-filter-chain` DSP lattice, encoded

**Seat: AUTHOR (executor-class, leaf).** Tree
`~/Projects/shokunin/audio-shokunin-wt-r92` (branch `wt-r92` @ entry HEAD
**`5a632a4f`**). Host `plazir27`, window **2026-10-15 05:42–06:50 UTC−3**
(08:42–09:50Z). Toolchain: PipeWire **1.6.8**, WirePlumber **0.5.17-1**,
Python 3.14.7, numpy 2.5.3, Linux 7.2.3-arch1-3. **Zero commits.**

Implementation of the round-92 move: an insertion-only `filterchain` family
in `corpus/fixtures/measure_audio.py` (appended after the r89 block, before
`def main()`), wired as `--probe-filterchain-r92`. Four entries: **37
live-audio legs** (dsp 20, ir 17 + the `i_residual` block), **26
arming/grammar/load legs** (one of which holds the 64 label rows) and
**17 wpexec + read-only inventory legs**. Every armed law is a
**boundary-surviving** claim from `reports/round-92/r92-boundary.md`; the
boundary's falsified rows are dropped, one boundary row is **falsified by
this seat's own measurement** (§3.1), and the scout's un-armed rows are
either corrected (§4.3) or left un-armed.

**Headline: two full batteries on the final bytes are GREEN
(`failures: {}`, rc 0, 0 `coverage_blocked`, 0 surviving own nodes), run
while sibling lanes were live (`host_is_quiet: false`).**

## 1. Files changed

- `corpus/fixtures/measure_audio.py` — **+2328/−3** (one tracked file;
  insertion-only except the three shared-line splices the wiring requires:
  the mutex list, the mode select, the receipt suffix — identical
  convention to r86–r89). sha256
  `5b17ad3dad4381905228c0789f0ef8d14b9366bf2cdbad38986d97e80fecd20c`.
- `corpus/live/r92-author/RECEIPTS.md` — the live-receipt index (run shas,
  leg inventory, the pre-fix reconciliation run, the host incident, the
  orphan disclosure, the exit sweep).
- `corpus/live/r92-author/receipts/*.json` — byte copies of the three run
  receipts (A, B, and the pre-fix reconciliation run).
- `corpus/live/r92-author/scratch/run{1,2,3}/` — every stimulus, IR fixture
  and captured WAV of the three runs.
- `corpus/live/r92-author/dev-validation/{analyze_dev.py,analysis.json}` —
  the pre-insertion dev-rig evidence, re-derived from its captures with the
  **fixture's own** analyzers.
- `reports/round-92/r92-author.md` — this file.

The tracked `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` also
shows as modified — the byte churn of importing/compiling the fixture, the
same artifact every prior round leaves (no source semantics in it).

Nothing committed. No `pactl set-default-*` was ever issued (defaults read
unchanged at exit: `…HiFi__SPDIF__sink` / `…HiFi__Line__source`); every
child is its own session leader with `RLIMIT_CORE=0`; the family lock is
the fixed path `corpus/live/measure_audio-filterchain-r92.lock` (r84 F1
consensus); `TMPDIR=/home/vgpnk/Projects/shokunin/tmp`.

## 2. The family

| entry | legs | what it pins |
| --- | --- | --- |
| `filterchain_arm_r92_probe` | 26 (+64 label rows) | client-local lifetime + shape + grammar + label table + pw-cli stdin classes + the silent-at-load half |
| `filterchain_dsp_r92_probe` | 20 | transfer function vs an independent **analytic RBJ** reference, the clamp/guard lattice, the inert port surfaces |
| `filterchain_ir_r92_probe` | 17 + `i_residual` | convolver sample-exactness (LSB residual), rate/channel/clip limits, the delay map, the silent class at **activation** |
| `filterchain_wpx_r92_probe` | 17 | wpexec `LocalModule` path + the read-only absent-class inventory |

All four gate on a **daemon health witness** (`pactl info`, bounded): a
wedged or saturated daemon is a *named block* **and a failure** — a battery
that measured nothing must never read as green (this fired for real in this
window, §6). Every audio leg is triple-bounded (argv bound + wall cap +
byte cap), every node name is `r92a_<pid>_<tag>` (unique per leg, so no
cross-leg collision), every unload is name-verified (`sink_name=`) and every
teardown ends with the absence witnesses (`sinks_gone` all-true,
`own_nodes_after: []`) plus a bounded-retry reader wrapper (a saturated
daemon answers `None` once — that is not absence).

## 3. Boundary-surviving laws encoded (and what was dropped)

Encoded (each an arm with a named failure text):

- **Client-local lifetime** — the loaded chain's two stream nodes are
  exported while the pw-cli session lives; `node.autoconnect=false` on both
  prop bags produces **0** own edges; `unload-module <var>` destroys the
  nodes, the **module id is refused** (`unknown module '22'`, nodes survive
  it), and the nodes die with the session.
- **The port law** — `media.class=Audio/Sink` yields a feedable
  `monitor_MONO`+`playback_MONO` pair (feed link rc 0); without it the
  capture side is a `Stream/Input/Audio` with no `playback_MONO` and the
  feed link refuses **rc 255 `failed to link ports: No such file or
  directory`** (see §4.3).
- **Args grammar** — quoted port names load, unquoted `node:port` does not;
  `#` is a comment even inside quotes (an LV2 URI is inexpressible);
  `filter.graph=42` / `{nodes=[]}` / a bad label / a bad type / `ffmpeg` /
  `ladspa` each refuse with their **specific** class; a control key
  containing a space is expressible **only quoted** (bare form = a
  properties parse error that kills the whole graph; quoted form loads with
  **no** warning); a typo'd control name is warning-only and the audio is
  silently wrong.
- **Label table** — the 26 load / 6 fail split (`avg gain min nop
  passthrough sum`), 2 reps each, 64/64 correct in both green runs.
- **pw-cli stdin classes** — `/dev/null` (file EOF) → SIGABRT (−6) +
  `remove_from_poll()`; **pipe EOF → hang** (killed at the bound); `quit` →
  rc 0.
- **DSP core vs analytic RBJ** — `copy` unity (all five probes |g| ≤ 0.05);
  lowpass/peaking rows within 0.06 dB of RBJ; `param_eq` ≡ the equivalent
  `bq_peaking`; notch ≥60 dB down at fc with passing skirts.
- **Clamp/guard lattice** — `Gain` clamped at the advertised bounds:
  `+20.5` ≡ `+20` (0.5 dB discriminator), `−120.5` ≡ `−120` (loosely, see
  §7) and the decisive new witness `Gain=−140` → **−46.566 dB** at 200 Hz =
  the −120 response (an unclamped −140 would read −66.4 dB: a 20 dB
  separation); `Q` clamped at 10 (`1e9` ≡ `10`); `Freq` above Nyquist is a
  **pass-through** (0.000 dB where an unguarded biquad would read
  −3.012 dB at 1 kHz); `Freq=0`/negative are **exact digital zeros**.
- **Inert surfaces** — the advertised `b0..a2` ports and `Gain` on labels
  that do not use it are inert; `bq_raw` has no reachable
  direct-coefficient path (exact silence).
- **Convolver** — the file's own quantised kernel is reproduced:
  full-convolution residual **0.5 / 0.5 / 0.0 LSB** over 12287 samples with
  **0 samples over 1 LSB**; IR tap gap 64 / ratio 0.500031; delta@100 →
  +100 samples; `gain=0.5` scales exactly; a 44.1 kHz IR in a 48 kHz graph
  is **resampled** (peak ≡ +110 mod 1024, 40 non-zeros); a 2-channel IR
  silently uses **channel 0** only; `gain=4.0` hard-clips at full scale;
  the silent class (no config / missing / empty / text / directory) is
  **exact digital zeros**.
- **Delay map** — exactly `round(s·rate)` samples up to `max-delay`
  (residues 48/480/2400) and **2431** for every over-max request
  (0.051/0.06/0.1 → residue 383), asserted modulo the 1024-sample block
  quantum (the taps are separate streams; only a *difference* is stable).
- **wpexec** — `LocalModule` builds a live, link-free, self-cleaning graph;
  a bad module/label is the silent `pcall ok=true mod=nil` class; `rawget` /
  `require_api` die with the bare `Lua runtime error` (rc 70, no location);
  `Settings` is reachable; an empty script (or a script without
  `Core.quit()`) hangs; syntax/missing/no-argv refuse rc 70 with precise
  text.
- **Absent classes (read-only)** — the SPA filter-graph directory is exactly
  six plugins with no `ffmpeg`; both LADSPA search dirs are **absent** (and
  the live LADSPA refusal carries its own `failed to load plugin` class);
  the LV2 tree is 25 bundles with **zero** `.so`; the shipped
  `sink-virtual-surround-5.1-kemar.conf` references
  `hrir_kemar/hrir-kemar.wav` and that path exists nowhere under
  `/usr/share/pipewire`.

### 3.1 A boundary row this seat's measurement falsifies

`r92-boundary.md` §4 row 15: "`Q=-1` → identical to `Q=0.707` (the
implementation default)". Measured twice on the final bytes:
`bq_peaking(Freq=1000, Q=-1, Gain=20)` gives a **broadband gain**
(19.015/18.979/19.289/18.729/19.289 in run A; 19.004/18.939/19.253/18.731/
19.254 in run B) — not the 0.707 peaking curve (2.671/20.0/3.66/0.357/
0.026) and not the analytic RBJ curve with `q=-1`
(1.543/20.0/2.216/0.182/0.013). The arm now pins the falsification
(|Δ at 200 Hz| ≥ 3 dB) plus the measured *shape* (flat within 2 dB across
five probes); the mechanism is **recorded, not explained**.

Dropped / not armed (with reasons):

- The scout's §3 table rows for `bq_highshelf`/`bq_bandpass` (boundary
  falsified: they match no artifact; the round's RBJ arms are computed
  in-process instead of copied).
- "`delay` did NOT delay" (a typo artifact — encoded as the delay map).
- The NaN half of the `Freq=0` claim (measured: exact zeros).
- "3/3 byte-identical" (the boundary's raw captures differ; the receipt
  records `sha16` + bytes, never byte-identity).
- The scout's absolute latency constant 15460 (replaced by the
  modulo-1024 shift law).
- `node.autoconnect=true` — **not armed by policy** (it links a seat stream
  to the operator's default sink; recorded in the entry as
  `not_armed_by_policy`), and the `pipewire -c filter-chain.conf` route
  (starts a second daemon on a shared host).
- The scout's no-props shape (§4.3).

## 4. Author findings that sharpen the boundary

### 4.1 The silent class is silent at LOAD and loud at ACTIVATION
The boundary's `E=0/W=0 at debug 3 and 5` is a **load-time** property (its
b9 stage was log-only). With audio flowing, the same legs emit at graph
start:

```
[E] convolver_instantiate()] convolver: requires a config section
[E] impl_activate()] cannot create plugin instance 0 rate:48000: Invalid argument
[E] stream_set_state()] ... error (-22) can't start graph: Invalid argument
```
(no config) and `read_closest()] Can't open any sample file` +
`failed file <path>` + `can't start graph` (missing/empty/text/directory).
The output is still **exact digital zeros**, rc is 0 and the module var is
real — so `rc 0` + "nodes present" + "load log clean" are all
non-witnesses. Both halves are armed: the load-only legs (`E=0/W=0`, debug
3 and 5 — measured 1792/1836/15468 log lines) and the activation classes.

### 4.2 The POST tap needs a driver (rig law)
A stream-to-stream link (`fc_out:output_MONO → pw-record:input_MONO`) leaves
**both ends suspended** and the capture is **exact zeros** — measured 4/4
legs in dev (identical args, healthy ref tap). The working shape (all nodes
`running`) drives the POST side with a second null sink:
`fc_out:output_MONO → ns2:playback_MONO`, tap `ns2:monitor_MONO →
pw-record:input_MONO`. This is a *rig* law, not a module claim — but it is
why a naive copy of the scout's §2.4 shape measures silence.

### 4.3 The scout's "no ports without media.class" is not reproduced
In the author's host-safe arming shape minus `media.class`, the capture node
is `Stream/Input/Audio` with ports `input_MONO` + `monitor_MONO` — **not**
`ports=[]` — but with **no `playback_MONO`**, so the feed link cannot bind
(armed: class + no-playback_MONO + `feed_link.rc == 255`). The *unfeedable*
conclusion survives; the mechanism is "the sink-side port does not exist",
not "there are no ports". The scout's exact no-props shape was **not
re-armed** (a stream with default autoconnect could reach the operator's
default sink; the boundary's row 29 also left it un-armed).

### 4.4 The lowpass at 20 kHz is a float32 artifact
`bq_lowpass(1000, 0.707)` measures **−71.437 dB** at 20 kHz against the
analytic RBJ **−70.217 dB** (1.22 dB) while the *peaking* rows match RBJ
**exactly** at the same probe — the lowpass numerator cancels
catastrophically in float32. The RBJ arm is therefore pinned on
200/1000/4000/12000 (≤0.06 dB; measured deltas 0.000–0.031) and the 20 kHz
cell is **recorded, not armed**.

### 4.5 Harness defects found and fixed inside this seat
The first run on the wired family (receipt
`20261016T093301592620Z`, rc 1, 19 arm failures) measured every leg and
exposed six arm defects — all reconciled in the final bytes, with the
pre-fix receipt kept as the record:

1. **`vs_rbj` compared `str` keys against `int` keys** — every RBJ cell read
   `rbj: None`, i.e. an arm that never compared anything. Fixed: int-key
   lookup.
2. **Class order** — the LADSPA host also prints `can't load plugin type
   'ladspa'`, so the generic type class shadowed the LADSPA line; the
   specific classes are now matched first (the generic refusal is last).
3. **Non-label refusal class** — the six non-labels refuse with
   `cannot create label <name>` (`fc92_label_missing`), not the generic
   `Could not load module`.
4. **`d_qneg`** — re-armed as the falsification in §3.1.
5. **`d_gnegx`** — one 0.57 dB cell under contention (deep-attenuation
   instrument spread; the same run's other cells matched exactly). Armed
   loosely (1.0 dB) and the decisive min-side witness `d_gneg140` was added.
6. **`i_441`** — the resampled-kernel peak is a PRE/POST difference and is
   therefore block-quantised like every other tap shift (measured
   1134 = 1024+110). Fixed with the modulo arm.

Earlier dev-phase defects (also measured, also fixed): a buffered `read(n)`
on a pw-cli pipe hides every reply until EOF (the r87 helper's latent
pattern — the r92 driver drains with `os.read(fd, …)`); a ±4096 lag search
found a degenerate edge overlap reading a fake 0.0 LSB (the residual is now
searched coarse-to-fine over near-full overlaps); `math` is not imported by
the fixture (the block is numpy-only); a fixed-name dev leg collided with
its own previous leg's nodes (unique per-leg names now).

## 5. Evidence

- **Two green batteries on the final bytes** (same sha256), rc 0,
  `failures: {}`, no `coverage_blocked`, `own_nodes_after: []` in all four
  entries:
  - `corpus/live/runs/20261016T094024556467Z-filterchain-r92/measurements.json`
    (sha256 `d167cdc5…f28aea`) — 5 foreign fixture runs live,
    `host_is_quiet: false`.
  - `corpus/live/runs/20261016T094602455160Z-filterchain-r92/measurements.json`
    (sha256 `01465b5a…492ca4`) — 3–4 foreign fixture runs live.
- **Cross-run stability of the pinned cells**: `copy` 0.000 dB; `d_gneg140`
  @200 Hz **−46.566 dB in both runs**; `d_qneg` stable to 0.04 dB;
  `i_2tap` gap 64 / ratio 0.500031; residuals 0.5/0.5/0.0 LSB; delay
  residues 48/480/352/383/383; all silent legs `nz_exact = 0` with their
  activation classes; labels 64/64; `ports_none` feed rc 255;
  `after_session_exit` clean with 0 SPDIF links.
- **Pre-fix reconciliation run**: `…T093301592620Z-filterchain-r92` (rc 1,
  19 arm failures — §4.5).
- **Pre-insertion dev-rig validation**: `dev-validation/analysis.json`
  (own rig, own synth, own DFT, own analytic RBJ), from which the arms were
  written: `copy` 0.000; `lp` −0.007/−3.012/−24.477/−47.370; `pk6` +6.000;
  `peq` ≡ `pk6`; notch −93.812; `Gain=20` +20.000 with `20.5` identical;
  `Freq=49000` 0.000; `Freq=0`/`bq_raw` exact zeros; IR gap 64 / ratio
  0.500031 / delta@100 +100 / residual 0.5 LSB / 44.1 kHz peak +110 /
  stereo channel-0-only / clip 0.999969; delay 48/480/2400/2431.
- **Exit sweep**: 0 `r92a_` nodes, 0 `r92a_` modules, 0 `r92a_` sinks, 0
  own audio children; defaults unchanged; each entry's `live_after` =
  `{spdif_links: 0, procs: []}`.

## 6. Host incident in this window (recorded, not hidden)

The shared PipeWire daemon **wedged at 05:58:33Z** and stayed wedged for
~26 minutes:

- `journalctl --user -u pipewire` — last line 05:58:33
  (`mod.client-node … can't start graph: Invalid argument`), then silence.
- `pactl info`, `pw-cli info 0`, `pw-dump` — all timed out at 12 s, 20 s and
  45 s bounds with 0 bytes.
- `ss -x` — the daemon socket carried ESTAB connections with **unread
  request bytes queued** (Recv-Q 27816 / 7800 / 2736) while the daemon sat
  in `epoll_wait` at 0.3 % CPU with 3 threads — wedged, not overloaded.
- Context: a foreign lane's runaway `pw-cli` (cwd `audio-shokunin-wt-r93`,
  `PIPEWIRE_DEBUG=3`) spinning at **94 % CPU**, a **second WirePlumber**
  (`-p main`) at **99.6 % CPU**, a second `pipewire -c pipewire.conf`, a
  foreign private daemon, and ~20 `yes` burners (load 53–57). The load fell
  back to 2.0 by 06:18Z and the daemon stayed wedged, so this is not a load
  artifact.
- Recovery at **06:24:36Z**; both green runs are after it. A daemon restart
  is an operator-level action — this seat did not attempt it and touched no
  foreign process. The health gate (§2) made the outage *red and named*
  rather than a silent green.

**Orphan disclosure (measured).** One orphaned `wpexec …/w_empty.lua` (the
hanging empty-script class) survived 22 minutes after its parent python was
SIGKILLed by an external `timeout` during the wedged window — the probe's
teardown cannot run on SIGKILL. It was idle (no nodes, no CPU, no sinks)
and this seat killed it. Recommended fold fix: wrap the hang-class and
long-lived children in a `timeout -s KILL <backstop>` argv prefix so the
backstop outlives the parent.

## 7. Remaining risks

- The orphan exposure in §6 (only reachable when the parent python is
  SIGKILLed; the normal path's teardown is proven clean by both runs).
- The `−120.5` min-side cell carries a ±0.6 dB deep-attenuation instrument
  spread under contention; the clamp is pinned decisively by `d_gneg140`
  instead.
- The `Q=−1` mechanism is unresolved (the falsification and the measured
  shape are pinned; the cause is recorded as unknown).
- The `sofa`/`ebur128` type rows and the label table are **load-only**
  (scout-observed, not boundary-re-armed): encoded as load rows with their
  precise classes; no DSP claim rides on them.
- The 20 kHz lowpass cell is recorded, never armed (§4.4).
- `a_load_dbg5`'s line-count floor (500) is a *shape* witness, not a law
  (measured 1792–15468 lines across the runs).

*author leaf — implemented, measured twice green on the final bytes, every
falsification named.*
