# R92 scout — `libpipewire-module-filter-chain`: the SPA filter-graph host, measured

Round 92 pre-measurement. Host `plazir27`, measured **2026-10-15 14:24–15:35 UTC−3**
(17:24–18:35Z). Repo `~/Projects/shokunin/audio-shokunin` @ HEAD **`a98c674`**
(HEAD moved during this seat; `git status` tracked-dirty at entry is the
sibling-owned `SHONEN.md` + `corpus/fixtures/measure_audio.py` — never read,
imported or executed here; own synth, own DFT, own biquad reference).
Toolchain: PipeWire **1.6.8** (`1:1.6.8-1`), WirePlumber **0.5.17-1**,
GStreamer 1.28.6, Python 3.14.7, numpy 2.5.3, Linux 7.2.3-arch1-3.

**Seat: SCOUT (leaf). Zero tracked-file writes; the only file written outside
`corpus/live/r92-scout/` is this report.** Every leg is triple-bounded (element
bound in argv + wall cap + byte cap; `start_new_session` + `os.killpg`, plus
`RLIMIT_CORE=0` because `pw-cli` aborts on EOF — §2.7). Seat-owned names only
(`r92s_*`); module unloads are index-verified against the seat name immediately
before the call; **no `pactl set-default-*` was ever issued**. Defaults read live
at every stage boundary: sink `…HiFi__SPDIF__sink`, source `…HiFi__Line__source`,
unchanged at exit. Final sweep: **0 `r92s` nodes, 0 `r92s` modules, 0 `r92s`
processes**, defaults unchanged.

**Label legend.** `[O]` = directly observed on this host in this window (probe
output or on-disk file read). `[I]` = read from installed version-matched source
(0.5.17 Lua / 1.6.8 man pages, both on-disk) or inferred from measured laws.
`[?]` = not resolved by this seat.

---

## 0. Why this surface (the pick, and what it displaces)

r90 left *policy/state* unknowns (settings file, restore debounce mechanism,
pw-v4l2 absent-class) and r91 left *gst capture-freeze internals*; r82/r85 are
static-file codec/format lanes. None of them yields a **live DSP primitive**.
r83 §0.2 explicitly **named this gap**: *"`pw-filter` is absent … the filter
surface is `libpipewire-module-filter-chain` (man7) + SPA `filter-graph` plugins
(builtin/ebur128/ladspa/lv2/sofa)"* — named, never measured.

The province's deliverables are SFX/soundtrack content measured headless by
duration/loudness/**spectral content**/loop-seam. `filter-chain` is the only
on-host surface that produces those properties **inside the live graph with a
measurable transfer function** (biquad response, convolver IR, delay in samples,
mixer/param_eq), and it is a *positive* surface: 26 builtin labels load, 6 of the
12 shipped in-province configs load, and the `ebur128` loudness meter and `sofa`
spatializer node types are present. Native LV2/LADSPA hosting is *structurally*
absent here (measured, §5.4) — so the pick also **pins an absent-class** instead
of depending on it. `wpexec` was measured as the script-side loader for the same
module (§6).

**Headline: the module is fully usable headless and self-cleaning, but it fails
in three distinct ways — loud, warning-only, and completely silent — and the
silent one is the shipped-config default.**

---

## 1. Headline claims

| # | claim | label | sharpest single fact | evidence |
| --- | --- | --- | --- | --- |
| 1 | **A pw-cli-loaded filter-chain is exported to the live graph and dies with the pw-cli process.** | `[O]` | 2 nodes live while `pw-cli` runs; **0** after it exits, 3/3 every stage; no daemon module, no `pactl` row, no residue | `receipts/f0_load.json` L1/L4; every `v2_*` receipt `live` field |
| 2 | **`node.autoconnect` is the WirePlumber linking gate, and omitting it is the host-safe arming.** | `[O]`+`[I]` | with the prop absent/false WP links **nothing** (0 links 3/3, `spdif_links=[]`); with `node.autoconnect=true` WP links the playback stream **to the operator's default sink** (`…SPDIF__sink:playback_FL/FR`) | `receipts/shape.json` `one-biquad` vs `autoconnect-true`; `…/linking/rescan.lua:145-149,174-178` |
| 3 | **The capture stream has NO ports unless `capture.props.media.class` is overridden.** | `[O]` | no props → `Stream/Input/Audio`, `ports=[]`, `suspended` (unfeedable); `media.class=Audio/Sink` → sink with `playback_MONO`+`monitor_MONO` | `receipts/shape.json` `one-biquad`/`stereo-2ch` vs `media-class-sink` |
| 4 | **The builtin filter table is 26 labels, and 6 strings in the .so are not labels.** | `[O]` | load 3/3: `bq_*`(9), `abs clamp convolver copy dcblock delay exp invert linear log max mixer mult noisegate param_eq recip sine`; fail 3/3: **`gain`, `nop`, `passthrough`, `sum`, `avg`, `min`** | `receipts/v2_labels.json` (96 legs) |
| 5 | **`copy` is bit-exact unity and the biquads reproduce RBJ to 0.01 dB** (3/3 byte-identical). | `[O]` | `copy` = **0.000 dB** at 200/1000/4000/12000 Hz; `bq_lowpass(1000,0.707)` = `-0.007 / -3.011 / -24.476 / -47.329`; `bq_peaking(1000,Q1,+6)` = **+6.000 dB** at fc | `receipts/v2_dsp.json` |
| 6 | **The convolver is a true sample-exact FIR engine.** | `[O]` | a 2-tap IR `[1.0, 0.5]` comes out as two impulses **exactly 64 samples apart with ratio 0.49997**; a 100-sample-delayed IR shifts the impulse by **exactly +100** against a route constant of 15460 samples | `receipts/v2_ir.json` |
| 7 | **Silent failure is the default failure mode for `convolver` and `sofa`.** | `[O]` | `convolver` with no `config`, or with `filename=/nonexistent/…`, **loads with zero `[E]`/`[W]` lines (8 log lines, all `[I]`) and emits pure silence** (nz=0 over 366636 B) | `receipts/v2_ir.json` `convolver-noconfig`/`convolver-missing` |
| 8 | **A typo'd control name is warning-only and leaves the audio silently wrong.** | `[O]` | `control={Gain1=0.5}` → `[W] parse_control() control 'Gain1' can not be set: No such file or directory`; the real port is **`Gain 1`** (with a space); the mixer leg then output **silence**, not unity | `receipts/v2_clamp.json` `mixer-1in-gain0.5` |
| 9 | **Clamping is per-control, not uniform.** | `[O]` | `Gain=100` → **+20.000 dB** (clamped to the advertised max 20) and `Gain=-200` → the fc bin is annihilated while skirts sit at −46 dB (clamped to −120); but `Freq=99999` → **flat 0.000 dB** (not clamped to the advertised max of 1.0) and `Freq=0`/negative → **silence** | `receipts/v2_clamp.json` |
| 10 | **`pw-cli` aborts on stdin EOF; only an explicit `quit` exits cleanly.** | `[O]` | `printf 'quit\n' \| pw-cli` → **rc 0**; `pw-cli </dev/null` → **rc 134 (SIGABRT)**, `'source->loop == &impl->loop' failed at …loop.c:189 remove_from_poll()`, core dumped | §2.7 (3/3 + 1/1) |
| 11 | **`links=[…]` needs quoted port names; unquoted `node:port` is rejected.** | `[O]` | `links=[{output="b1:Out",input="b2:In"}]` loads 3/3; `links=[{output=b1:Out,input=b2:In}]` fails 3/3 | `receipts/v2_links.json` |
| 12 | **`wpexec` can instantiate a live DSP graph from a Lua script, and it self-cleans.** | `[O]` | `LocalModule("libpipewire-module-filter-chain", args)` → `pcall ok=true`, `<WpImplModule:0x…>`; while the interpreter lives the graph contains `r92s_wpx_in`/`r92s_wpx_out`, **0 links, 0 SPDIF links**; after exit `[]`, 3/3 | `receipts/f6_wpx_module.json` |
| 13 | **The `type=ffmpeg` node type documented in the 1.6.8 man page does not exist on this host.** | `[O]` | `[E] plugin_load()] can't load plugin type 'ffmpeg': No such file or directory` + `Error: "Could not load module"`; no `libspa-filter-graph-plugin-ffmpeg.so` in `/usr/lib/spa-0.2/filter-graph/` | `receipts/f5_absent2.json`; `/usr/lib/spa-0.2/filter-graph/` listing |
| 14 | **LADSPA is structurally unavailable: the host exists, the search path has zero plugins.** | `[O]` | `[E] plugin_ladspa.c:352] failed to load plugin 'g2reverb' in '/usr/lib64/ladspa:/usr/lib/ladspa:/usr/lib': No such file or directory` — `/usr/lib64/ladspa` and `/usr/lib/ladspa` are **0 entries**, `/usr/lib` has 5370 files and no LADSPA plugin | `receipts/v2_absent.json`; directory listing |
| 15 | **LV2: the host is present and tries, the inventory is empty.** | `[O]` | `[W] plugin_lv2.c:661 impl_init()] can't load plugin http://lv2plug.in/ns/ext/atom` (host ran); `/usr/lib/lv2` holds **25 bundles, all LV2 spec/schema bundles, zero DSP plugins** | `receipts/f5_absent2.json`; `ls /usr/lib/lv2` |
| 16 | **A shipped config can load and still be a silent passthrough of nothing.** | `[O]` | `sink-virtual-surround-5.1-kemar.conf` publishes 2 nodes 3/3, but its convolvers reference `hrir_kemar/hrir-kemar.wav` and **neither `hrir_kemar/` nor `hrir_hesuvi/` exists anywhere under `/usr/share/pipewire`** → by claim 7 / §4 the convolvers are silent | `receipts/v2_configs.json`; `find /usr/share/pipewire -name '*kemar*'` |

---

## 2. The arming law (how to drive it headlessly)

### 2.1 Loader, lifetime, teardown
- `[O]` `pw-cli` → `load-module libpipewire-module-filter-chain <args>` prints
  **`1 = @module:22`** (var = `@module:<id>`). `unload-module` takes the **var**
  (`1`); passing the id → `Error: "unload-module: unknown module '1473199'"`.
- `[O]` The module lives in the **pw-cli client context**. Its nodes are exported
  to the graph (visible to `pw-dump`/`pw-link` from other processes) and are
  destroyed when pw-cli exits — measured at every stage (`live: {nodes: [],
  modules: [], procs: []}` after each leg). No daemon module, no `pactl` row.
- `[O]` Two args forms reach the parser: comma form
  (`k=v,filter.graph={…}`) and the shipped spaced form; both load (f0 L1/L5).

### 2.2 The args grammar is the properties parser, not full spa-json
Measured failure texts (each 3/3):

| input | result |
| --- | --- |
| `nodes=[type=builtin,…]` (bare `k=v` element in an array) | `[W] properties.c:264 error parsing more than 0 properties: Invalid array separator` → `[E] load_graph() missing filter.graph property` → **load fails** |
| `filter.graph=42` | `[E] filter.graph must be an object` → fails |
| `filter.graph={nodes=[]}` | `[E] load_graph() filter.graph has no nodes` → fails |
| `label=not_a_filter` | `[E] descriptor_load() cannot create label not_a_filter` → fails |
| `links=[{output=b1:Out,input=b2:In}]` | fails 3/3 (bare `:` in a value) |
| `links=[{output="b1:Out",input="b2:In"}]` | **loads 3/3** — the documented form (see the shipped `smart-equalizer.conf` example) |
| `links=[{output=b1,input=b2}]` | fails 3/3 |
| `plugin="http://example.org/r92s#none"` | `[W] … Mismatched bracket` at the `#` — **`#` starts a comment even inside quotes**, so a typical LV2 URI (with `#`) is *inexpressible in this grammar* |
| `type=r92s_bogus` | `[E] plugin_load() can't load plugin type 'r92s_bogus'` → fails |

**Author rule.** Build the graph with `{…}` array elements, quote every port
name, and never put `#` in a value.

### 2.3 Load shape
`[O]` (3/3, `receipts/shape.json`)

| props given | capture node | playback node |
| --- | --- | --- |
| none | `input.filter-chain-<pid>-<n>`, `Stream/Input/Audio`, **`ports=[]`**, suspended | `output.filter-chain-<pid>-<n>`, `Stream/Output/Audio`, `output_FL/FR`, running |
| `node.name` only | `r92s_fc_in`, `Stream/Input/Audio`, **`ports=[]`** | `r92s_fc_out`, `Stream/Output/Audio`, `output_FL/FR` |
| `node.name` + `media.class=Audio/Sink` | `r92s_fc_in`, **`Audio/Sink`**, `monitor_MONO`+`playback_MONO` | `r92s_fc_out`, `Stream/Output/Audio`, `output_MONO` |

Two consequences, both measured:
1. **Without a `media.class` override the capture side is unfeedable** (no ports
   to link into) — the shipped-configs' `media.class=Audio/Sink` is not decoration.
2. **The playback stream defaults to stereo** (`output_FL/FR`) unless both
   `capture.props` and `playback.props` are present, in which case it honours
   `audio.channels=1`/`audio.position=[MONO]` → `output_MONO`. (This is what
   silently produced 44-byte captures in this seat's first instrument, §7.)

### 2.4 The host-safe arming shape (used by every measurement below)
```
pactl load-module module-null-sink sink_name=r92s_in channels=1     # the only driver
pw-cli: load-module libpipewire-module-filter-chain
        node.description=r92s_fc,
        filter.graph={nodes=[{type=builtin,name=f1,label=bq_lowpass,
                              control={Freq=1000.0,Q=0.707}}]},
        audio.channels=1,audio.position=[MONO],
        capture.props={node.name=r92s_fc_in,node.autoconnect=false,media.class=Audio/Sink},
        playback.props={node.name=r92s_fc_out,node.autoconnect=false}
pw-link r92s_in:monitor_MONO  r92s_fc_in:playback_MONO     # feed
pw-link r92s_in:monitor_MONO  r92s_ref:input_MONO          # PRE-chain tap
pw-link r92s_fc_out:output_MONO r92s_rec:input_MONO        # POST-chain tap
pw-play --target r92s_in tone.wav                          # stimulus
```
`[O]` every hop returned rc 0 on the first try (`tries: 1`) once the rig was
correct; `pw-play --target <filter-chain sink name>` resolves by name (the same
node also accepts a hand link). **Nothing in this shape can reach the operator's
devices** — `node.autoconnect=false` on both streams is the load-bearing prop.

### 2.5 Driver law (`receipts/f3_driver.json`)
| arm | result |
| --- | --- |
| **S1** one null sink (driver) → chain → record the FC output directly | **92204 B captured**, chain ran (`r92s_in running drv=True`), `node.passive` absent |
| S2 two null sinks (two drivers) in one chain | worked in f3 (73772 B, both drivers `running`) — but the same shape in f2 was **all-suspended with a 44 B capture**; the discriminator was **not** identified `[?]` |
| S3 S2 + `playback.props node.passive=true` | **identical bytes and identical gains to S2** — the prop lands (`pas=True` on the node) and is *inert in this topology* |
| S4 `playback.props media.class=Audio/Sink` | `[W] pw_stream_connect() media.class Audio/Sink does not expect Output stream direction` → `[E] node_port_info() can't add port …: -28, No space left on device` → **the pw-cli client dies** (BrokenPipe) |

### 2.6 Teardown
`[O]` `unload-module <var>` returns rc 0 and the nodes vanish immediately
(`nodes_after_unload` = seat sinks only); then `quit`. Every stage ends with
`SWEEP clean: True  final: {nodes: [], modules: [], procs: []}`.

### 2.7 `pw-cli` EOF abort (crash class `pwcli_eof_abort`)
```
printf 'quit\n' | pw-cli     -> rc 0
pw-cli < /dev/null           -> rc 134 (SIGABRT)
   >> 'source->loop == &impl->loop' failed at ../pipewire/spa/plugins/support/loop.c:189 remove_from_poll()
   timeout: the monitored command dumped core
```
Independent of the filter-chain (reproduced with no module loaded, 3/3 + 1/1).
Cores go to `systemd-coredump` (`core_pattern` is the systemd handler), so no
file lands in the tree; this seat additionally sets `RLIMIT_CORE=0` on every
child. **Always send `quit`.**

---

## 3. Transfer function (dual-tap, 3/3 byte-identical)

Instrument: PRE tap = `r92s_in:monitor_MONO`, POST tap = `r92s_fc_out:output_MONO`,
stimulus = own 4-tone sum (200/1000/4000/12000 Hz, 1.2 s, exact integer cycles in
the 24000-sample analysis window), analysis = own Goertzel DFT on the max-RMS
0.5 s window. Every row below is `ref=174124 B, out=172076 B` with identical
values in all 3 reps.

| graph (`filter.graph.nodes[0]`) | 200 Hz | 1 kHz | 4 kHz | 12 kHz |
| --- | --- | --- | --- | --- |
| `label=copy` (unity control) | **0.000** | **0.000** | **0.000** | **0.000** |
| `bq_lowpass Freq=1000 Q=0.707` | −0.007 | **−3.011** | −24.476 | −47.329 |
| `bq_highpass Freq=1000 Q=0.707` | −27.992 | **−3.011** | −0.016 | −0.000 |
| `bq_peaking Freq=1000 Q=1 Gain=+6` | +0.266 | **+6.000** | +0.405 | +0.028 |
| `bq_peaking Freq=1000 Q=1 Gain=−6` | −0.266 | **−6.000** | −0.405 | −0.028 |
| `bq_notch Freq=1000 Q=1` | −0.184 | **−93.977** | −0.285 | −0.019 |
| `bq_allpass Freq=1000 Q=1` | 0.000 | 0.000 | 0.000 | −0.000 |
| `bq_lowshelf Freq=200 Q=0.707 Gain=+6` | **+3.000** | +0.011 | −0.000 | 0.000 |
| `bq_highshelf Freq=4000 Q=0.707 Gain=−6` | −1.865 | −1.843 | **−3.000** | **−5.979** |
| `bq_bandpass Freq=1000 Q=1` | −15.555 | 0.000 | −13.832 | −25.506 |
| `param_eq config={filters=[{type=bq_peaking,freq=1000.0,gain=6.0,q=1.0}]}` | +0.266 | **+6.000** | +0.405 | +0.028 |
| `invert` | 0.000 | 0.000 | 0.000 | 0.000 |
| `delay config={max-delay=0.05} control={Delay=0.01}` | 0.000 | 0.000 | 0.000 | 0.000 |

`[O]` **`param_eq` with one peaking filter is byte-identical to the equivalent
`bq_peaking`** (same output file length and the same 4 gains) — the parametric EQ
is the same biquad cascade. `invert` and `delay` are magnitude-invisible here by
construction; their *polarity* and *delay* are measured in §4.

### 3.1 The biquad control lattice and the clamp law
`[O]` the node's own log prints the port table (`PIPEWIRE_DEBUG=3`):
```
using port 0 ('Out')  as output 0
using port 1 ('In')   as input  0
using port 2 ('Freq') as control 0  0.000000/0.000000/1.000000     <- min/def/max
using port 3 ('Q')    as control 1  0.000000/0.000000/10.000000
using port 4 ('Gain') as control 2  0.000000/-120.000000/20.000000
using port 5..10 ('b0','b1','b2','a0','a1','a2') as control 3..8, def 1,0,0,1,0,0, range [-10,10]
loaded n_input:1 n_output:1 n_control:9 n_notify:0
```
Measured against that advertised table (`receipts/v2_clamp.json`, 3/3 each):

| input | measured | law |
| --- | --- | --- |
| `Gain=100` | **+20.000 dB** at fc | clamped to the advertised max **20** |
| `Gain=-200` | fc bin = **−273.977 dB** (numerical zero), skirts −46.4/−48.3/−36.4 dB | clamped to the advertised min **−120** |
| `Freq=99999` | **0.000 dB at all four freqs** | **not** clamped to the advertised max of 1.0 |
| `Freq=0` | **silence** (all four bins −273.978 dB) | degenerate → NaN/zero, no guard |
| `Freq=-1000` | **silence** | same |
| `Q=0` | identical to `Q=0.707` (−3.010 dB at fc) | 0 = "use the implementation default" |
| `control={Bogus=3.0}` / `{Gain1=…}` | `[W] parse_control() control 'X' can not be set: No such file or directory`, node loads | typo = warning only |

**So the advertised `Freq` range is not a clamp**: 0 and negative are *unsafe*,
and a value above Nyquist is simply a no-op filter. An author who writes
`Freq=0` gets silence with no error; `Gain` is the one control that *is* clamped.

---

## 4. Impulse response, latency and the convolver (`receipts/v2_ir.json`)

Stimulus = own single-sample delta at sample 100 of a 4096-sample WAV. In every
leg the PRE tap shows the impulse at the **same absolute sample index 15460** —
the route latency is deterministic and identical across legs, so *differences*
between legs are chain-only.

| graph | first impulse | non-zeros | gap | ratio |
| --- | --- | --- | --- | --- |
| `copy` | 15460, 0.9999695 | 1 | — | — |
| `convolver config={filename=ir_d100.wav,…}` (IR = delta at 100) | **15560**, 0.9999390 | 1 | — | — |
| `convolver config={filename=ir_2tap.wav,…}` (IR = `[1.0@0, 0.5@64]`) | 15460, 0.9999390 | **2** | **64** | **0.49997** |
| `convolver … gain=0.5` (same IR) | 15460, 0.4999695 | 2 | 64 | 0.49997 |
| `delay config={max-delay=0.05} control={Delay=0.01}` | 15460, 0.9999695 | 1 | — | — |

`[O]` **the convolver reproduces the kernel exactly**: a 100-sample IR delay
shows up as **+100 samples**, and the 2-tap kernel's amplitudes are `1.0` and
`0.49997` (= 0.5 after the int16 round trip). `gain` in the convolver config
scales the IR by exactly 0.5. The captured impulse is a **single-sample spike**
(`window = [0,0,0,0.9999,0,0]`) — no dispersion, no ringing.

`[O]` **`delay` did NOT delay, and the reason is in the log**:
```
using port 2 ('Delay (s)') as control 0  0.000000/0.000000/100.000000
using port 3 ('latency')   as notify 0
using port 4 ('Feedback')  as control 1 0.000000/-10.000000/10.000000
using port 5 ('Feedforward') as control 2 0.000000/-10.000000/10.000000
[W] parse_control() control 'Delay' can not be set: No such file or directory
```
The control is named **`Delay (s)`** (seconds) — `Delay` is a typo that costs a
warning line and leaves the delay at 0. The same class produced the mixer's
silence (`Gain 1`, not `Gain1`).

`[O]` **The silent-failure class, verbatim**: `convolver` with no `config`, and
`convolver config={filename=/nonexistent/r92s_ir.wav}`, both **load**, publish
both stream nodes, stream 366636 B of audio, and emit **zero `[E]`/`[W]` lines**
(the whole captured client log is 8 lines, all `[I]`) — and the output is
**pure silence** (`nz=0`). A typo'd IR path is indistinguishable from a working
filter until you measure it. `sofa`/`spatializer` behaves the same way (§5.4).

---

## 5. Node-type inventory (`type=` and the shipped configs)

### 5.1 Builtin labels — measured, not inferred
`[O]` 32 candidate labels × 3 reps (`receipts/v2_labels.json`):

- **load 3/3 (26):** `abs bq_allpass bq_bandpass bq_highpass bq_highshelf
  bq_lowpass bq_lowshelf bq_notch bq_peaking bq_raw clamp convolver copy dcblock
  delay exp invert linear log max mixer mult noisegate param_eq recip sine`
- **fail 3/3 (6):** `avg gain min nop passthrough sum`

All six failures also appear as *strings inside* `libspa-filter-graph-plugin-builtin.so`
— the r88/r90 "advertisement ≠ objects" law, now measured for the label table.
`passthrough` is not a label; the official example uses `label = copy` for a
passthrough (`/usr/share/doc/wireplumber/examples/wireplumber.conf.d/filter-graph.conf`).

### 5.2 Types
| `type=` | verdict | evidence |
| --- | --- | --- |
| `builtin` | **present** | §3, §4 |
| `ebur128` | **present, label `ebur128`** | `{type=ebur128,name=e,label=ebur128}` loads 3/3; `label=loudness`/`x` → `cannot create label` 3/3 |
| `sofa` | **present, label `spatializer`** | `{type=sofa,name=s,label=spatializer}` loads 3/3 (with *and* without `config`) — see §5.4 for the silent-config trap; `libspa-filter-graph-plugin-sofa.so` links `libmysofa.so.1`, config keys `filename/blocksize/tailsize/gain/normalize/auto`, error text `spatializer: expected object in config` |
| `ladspa` | **absent-class (structural)** | host present (`libspa-filter-graph-plugin-ladspa.so`); search path printed verbatim `'/usr/lib64/ladspa:/usr/lib/ladspa:/usr/lib'` with `No such file or directory`; `/usr/lib64/ladspa` and `/usr/lib/ladspa` are **empty dirs**, `/usr/lib` has 5370 files and no LADSPA plugin |
| `lv2` | **absent-class (empty inventory)** | host present and running (`[W] plugin_lv2.c:661 impl_init()] can't load plugin http://lv2plug.in/ns/ext/atom`), `liblilv-0.so.0` linked; `/usr/lib/lv2` = 25 bundles, **all spec/schema**, zero DSP plugins; plus the grammar cannot express a URI containing `#` |
| `ffmpeg` | **absent-class (no SPA plugin)** | documented in the 1.6.8 man page; `[E] plugin_load() can't load plugin type 'ffmpeg': No such file or directory`; no `*ffmpeg*`/`*avfilter*` file anywhere under `/usr/lib/spa-0.2/`; `libpipewire-module-filter-chain.so` does not link libavfilter |

`[O]` plugin file inventory (`/usr/lib/spa-0.2/filter-graph/`): `libspa-filter-graph.so`,
`…-plugin-builtin.so` (448 KB), `…-plugin-ebur128.so`, `…-plugin-ladspa.so`,
`…-plugin-lv2.so`, `…-plugin-sofa.so` — **six files, no ffmpeg**.

### 5.3 The 12 shipped configs (`/usr/share/pipewire/filter-chain/`)
Fed to `pw-cli load-module` as one args token (transform in §7.4; the configs'
`#` comments stripped, whitespace folded, port names quoted). 3 reps each
(`receipts/v2_configs.json`):

| config | nodes (3 reps) | verdict |
| --- | --- | --- |
| `sink-eq6.conf` | 2/2/2 | **loads** — 6-band biquad EQ (`r92s_effect_input_eq6`/`…_output_eq6`) |
| `sink-make-LFE.conf` | 2/2/2 | **loads** — copy+mixer+`bq_lowpass` LFE extraction |
| `sink-mix-FL-FR.conf` | 2/2/2 | **loads** — mixer downmix |
| `sink-dolby-surround.conf` | 2/2/2 | **loads** (emits `[W] impl_activate() graph has unaligned latency m…`) |
| `sink-dolby-pro-logic-ii.conf` | 2/2/2 | **loads** |
| `sink-virtual-surround-5.1-kemar.conf` | 2/2/2 | **loads, but silent** — its convolvers point at `hrir_kemar/hrir-kemar.wav` and **the directory does not exist** (§5.3) |
| `sink-matrix-spatialiser.conf` | 0/0/0 | **fails at plugin level** — `[E] plugin_ladspa.c:352 failed to load plugin 'matrix_spatialiser_1422' in '/usr/lib64/ladspa:/usr/lib/ladspa:/usr/lib'` |
| `source-rnnoise.conf` | 0/0/0 | **transform-level parse error here**; its only node is `type=ladspa plugin="librnnoise_ladspa"`, which the measured empty LADSPA search path cannot satisfy → by the §5.2 LADSPA pin it is dead on this host `[I]` |
| `demonic.conf` | 0/0/0 | transform-level parse error here; all three of its nodes are `type=ladspa` (`revdelay_1605`, `am_pitchshift_1433`, `g2reverb`) → dead by the same pin `[I]` |
| `sink-upmix-5.1-filter.conf` | 0/0/0 | not authoritatively measured (transform — §7.4) |
| `sink-virtual-surround-7.1-hesuvi.conf` | 0/0/0 | not authoritatively measured (transform — §7.4); its IR dir `hrir_hesuvi/` is also missing |
| `source-duplicate-FL.conf` | 0/0/0 | not authoritatively measured (transform — §7.4) |

**Author rule.** The `builtin`-only configs are usable **if you copy the config
*and* its IR directory** — `hrir_kemar/`/`hrir_hesuvi/` are not shipped, so the
virtual-surround pair loads as a silent chain. Every LADSPA config is dead on
this host.

### 5.4 `sofa`/`spatializer` config trap
`[O]` `{type=sofa,name=s,label=spatializer}` loads 3/3 **without any config**, and
`config={filename="/nonexistent/r92s.sofa"}` also loads 3/3. The plugin's own
strings carry `spatializer:filename requires a string` / `Only the same sampling
rate supported`, i.e. the config is required for real HRTF work — but its absence
is **silent** (same class as `convolver`, §4). Whether the no-config node passes
audio through or emits silence was **not measured** `[?]`.

---

## 6. `wpexec` — the script-side loader (`receipts/f4_wpexec.json`, `f6_wpx_module.json`)

| leg | result (3/3 unless noted) |
| --- | --- |
| W1 `print(...)` + `Core.quit()` | **rc 0**, `r92s hello from wpexec`, 0.01 s |
| W4/W6 `LocalModule("libpipewire-module-filter-chain", args)` | **`pcall ok=true`, `mod=<WpImplModule:0x…>`, `mod.name=libpipewire-module-filter-chain`, rc 0** |
| **f6** same + `Core.timeout_add(2500, Core.quit)` | while alive the graph contains **`r92s_wpx_in`, `r92s_wpx_out`**; **0 links**, **0 SPDIF links**; after exit `[]` — 3/3 |
| W5 script without `Core.quit()` | **hangs to the wall cap** (rc −9 at 4 s, `timed_out=True`, 3/3) — the interpreter never exits on its own |
| W6 syntax error | rc 70 `Failed to compile: [string "w6_syntax.lua"]:1: syntax error near 'is'` |
| W7 missing script | rc 70 `Could not locate script '/nonexistent/r92s.lua'` |
| W8 no argv | rc 70 `Could not locate script '(null)'` (no usage output) |
| W2/W3 globals + `Settings.get_*` | rc **70**, stderr is the bare string **`Lua runtime error`** — **no line, no stack**; the legs are **inconclusive** (`[?]`, see §8) |
| residue | `wpexec` added nothing persistent; the only `r92s` node seen before/after was a *pre-existing* leftover from this seat's own aborted runs, removed by the sweep (`n_nodes 11 → 10 → 9`; final clean) |

`[O]` So the module can be instantiated **from a Lua script** as well as from
`pw-cli`, the resulting nodes are real graph citizens, and both loaders
self-clean on exit. `wpexec`'s terse `Lua runtime error` (no location) is a real
author-facing defect.

---

## 7. Falsification list (what was tried that could have killed each claim)

| claim | falsifier attempted | outcome |
| --- | --- | --- |
| the module is a daemon module | `pactl list modules short` after every leg | **falsified** — never appears; it is pw-cli-local |
| the nodes survive the loader | census after pw-cli exit, every leg | **falsified** — always 0 |
| the loader is dangerous to the host by default | `pw-link -l` SPDIF census on every leg | **falsified** — 0 host links unless `node.autoconnect=true` |
| `node.autoconnect` is only cosmetic | explicit `true` arm | **falsified** — WP links the playback stream to `…SPDIF__sink:playback_FL/FR` |
| strings in the .so = available labels | 32-label load census | **falsified** — 6 of the string-present labels do not exist |
| `Freq` is clamped to its advertised max (1.0) | `Freq=99999` | **falsified** — flat 0.000 dB |
| `Gain` is not clamped | `Gain=100` | **falsified** — exactly +20.000 dB (the advertised max) |
| an invalid control is an error | `Bogus=3.0`, `Gain1=…`, `Delay=…` | **falsified** — `[W]` only, node loads, audio silently wrong |
| an invalid `convolver` config is an error | no config / bad IR path | **falsified** — 8 log lines, all `[I]`, output silent |
| `pw-cli` exits cleanly on EOF | `pw-cli </dev/null` | **falsified** — SIGABRT rc 134, core dumped |
| the shipped virtual-surround config works | load + IR-path check | **falsified** — loads, but its IR directory is not shipped → silent |
| LV2 is merely uninstalled | host-level probe with a non-`#` URI | **refined** — the *host runs and tries*; the *inventory* is empty |
| LADSPA could be loaded from an absolute path | `plugin="/usr/lib/libmltladspa"` | **falsified** — the name is appended to the search dirs only |
| the route adds an unknown level offset | dual-tap calibration vs the stimulus file | **falsified** — `copy` = 0.000 dB; the first pass's "−1.83 dB" was a **window artifact** (§7.1) |
| the seat perturbs host state | census + defaults before/after every stage | only own modules/nodes; defaults unchanged; final sweep clean |

### 7.1 Harness defects found and fixed inside this seat (recorded, not hidden)
1. **Fixed analysis window** (`skip = 0.7 s`) sampled the prefill, not the tone →
   a phantom "−1.83 dB route loss" and one phantom "−273 dB silence" family.
   Fixed by selecting the max-RMS 0.5 s window; after the fix `copy` measures
   **0.000 dB** and the route is provably transparent.
2. **Missing `{…}` in `nodes=[…]`** → `Invalid array separator`; every graph in
   the first shape pass silently failed to load (the census then showed only the
   seat sinks). Fixed; the failure text became claim §2.2.
3. **No `--channels 1` on `pw-record`** (default is 2, `pw-record --help`) → the
   record node published `input_FL/FR` and the mono links failed.
4. **`node.autoconnect` omitted on the FC streams in the first driver** → the
   playback stream defaulted to stereo `output_FL/FR` while the rig linked
   `output_MONO` → 44-byte captures.
5. **No link retry**: a stream publishes its ports a moment after the client
   starts, so a single `pw-link` raced and failed. Fixed with a bounded retry
   (10 × 0.25 s) + a validity gate + one whole-leg retry; all links then
   succeeded on `tries: 1`.
6. **Killed mid-leg runs left residue** (5 duplicate `r92s_in` null sinks, 2
   orphan `pw-record`s) which made every `pw-link` name ambiguous and produced a
   whole stage of false failures. Fixed with a `preflight()` that unloads any
   `r92s` module and kills stray audio-tool children before arming; the final
   state is verified clean.
7. **`stray_procs` false-positived on this seat's own shell/python** (their
   command lines contain `r92s`); narrowed to processes whose argv starts with
   an audio-tool binary.

### 7.4 Residual on the shipped-config matrix `[?]`
**6 of 12 configs load 3/3** (`sink-eq6`, `sink-make-LFE`, `sink-mix-FL-FR`,
`sink-dolby-surround`, `sink-dolby-pro-logic-ii`, `sink-virtual-surround-5.1-kemar`)
and **one fails at plugin level** (`sink-matrix-spatialiser`, verbatim LADSPA
error). The remaining **five report 0 nodes with a properties-parse error**
(`Expected object key` / `Expected array close` / `Invalid array separator`) —
that text comes from **this seat's `norm_args` transform**, not from the configs:
folding whitespace to `,` interacts with the configs' inline `#` comments and
their `param_eq` `filters = [ … ]` lists. Those five are therefore recorded as
**not authoritatively measured**; two of them (`demonic`, `source-rnnoise`) are
*also* dead by the independent LADSPA pin (all their nodes are `type=ladspa`).
The intended route (`pipewire -c filter-chain.conf`, cwd = the config dir) was
**not** run — it starts a second PipeWire process, which this seat refuses on a
shared host. A verbatim-preserving transform (or that route) is the next cell.

---

## 8. Remaining unknowns

1. `[?]` **Why the f2 topology was all-suspended** while the same S2 topology
   worked in f3 (two null-sink drivers, identical hops). One reproducible
   difference was not found; the working shapes are S1/f3 and the v2 rig.
2. `[?]` `wpexec`'s global/API namespace: W2/W3 die with a bare `Lua runtime
   error` (rc 70) and **no location**; `_G`/`require_api` usage could not be
   narrowed further. The `Settings` cross-witness of r90's 25-key lattice is
   therefore **not** delivered.
3. `[?]` Whether the no-config `sofa`/`spatializer` node passes audio through or
   emits silence (load-only measured, §5.4).
4. `[?]` The `mixer`'s silence with one connected input (`Gain1` typo *and* 7
   unconnected inputs are both candidate causes; the warning is measured, the
   cause is not).
5. `[?]` `ebur128`'s **port/control inventory and its loudness output** — the
   type loads with `label=ebur128` (3/3) but its ports were not captured
   (`PIPEWIRE_DEBUG` was off in that one-shot leg). This is the province's own
   loudness axis and is the single most valuable next cell.
6. `[?]` `bq_raw` (loads 3/3) — its per-rate `coefficients` config was not fed.
7. `[?]` `capture.volumes`/`playback.volumes` (control-port-driven volume, man
   page §Volumes) — not exercised.
8. `[?]` The `filter.smart=true` / `node.filter-graph.rules`
   `create-filter-graph` policy path: `[O]` the implementation is on disk
   (`/usr/share/wireplumber/scripts/node/filter-graph.lua:116,126`) and the
   official example is shipped, but it needs a config file + daemon reload
   (operator decision), so it was **not** armed.
9. `[?]` `pw-cli create-node` / `pw-cli set-param <node> Props` against a live
   filter-chain node (runtime control changes mid-stream) — r90 C21 pinned the
   *sink-node* rejection; the filter-chain's own control ports were not driven
   live.

---

## 9. Author directives

**Verbatim-ready cells** (≥3 reps, byte-stable, exact argv in the receipts):

1. **Arm a headless DSP chain without touching the host** — §2.4 verbatim; the
   load-bearing props are `node.autoconnect=false` on both stream prop bags and
   `capture.props.media.class=Audio/Sink`. Expect 4/4 links on the first try and
   0 SPDIF links.
2. **Unity check** — `label=copy` → `0.000 dB` at 200/1000/4000/12000 Hz with
   `ref=174124 B, out=172076 B`. Use it as the calibration row for any filter
   measurement.
3. **Biquad reference table** — §3 table; `bq_peaking Gain=+6` measures
   `+6.000 dB`, `bq_lowpass(1000,0.707)` measures `−3.011 dB` at fc,
   `bq_lowshelf(200,+6)` measures `+3.000 dB` at fc.
4. **Convolver fidelity** — IR `[1.0@0, 0.5@64]` → two impulses, **gap 64**,
   **ratio 0.49997**; IR delta@100 → **+100 samples** against a route constant
   of 15460; `gain=0.5` scales the first tap to `0.4999695`.
5. **Crash/abort classes** — `pw-cli` EOF → rc 134 + core (always `quit`);
   `playback.props media.class=Audio/Sink` → port-add failure + client death.
6. **Label inventory** — the 26/6 split in §5.1, with `gain`, `passthrough`,
   `nop`, `sum`, `avg`, `min` explicitly *not* labels.
7. **Type inventory** — `builtin` / `ebur128(label=ebur128)` /
   `sofa(label=spatializer)` present; `ladspa` (empty search path),
   `lv2` (empty inventory), `ffmpeg` (no SPA plugin) absent, each with its
   verbatim error line.
8. **Grammar rules** — `{…}` array elements; quoted port names; `#` is a comment
   even inside quotes.

**Bimodal / envelope cells** (do not arm as a single shape):

- **Failure-mode envelope**: the same "invalid" input can be (a) a loud module
  load failure with a precise `[E]` (bad label, bad type, missing
  `filter.graph`), (b) a `[W]`-only no-op (bad control name), or (c) **silence
  with zero diagnostics** (convolver without config / bad IR path; `sofa`
  without config). Arm a measurement, not an exit code — `rc 0` and "nodes
  present" are not validity witnesses.
- **`Freq` control**: not clamped; `0`/negative → silence, `>Nyquist` → no-op.
  Treat any `Freq` outside the audio band as unvalidated.
- **The shipped-config matrix**: verbatim for the 8 configs whose verdict is a
  plugin-level result; **do not quote the other four** until the transform in
  §7.4 is fixed and re-run.
- **Two-driver topologies**: f3's S2 worked, f2's identical shape did not; arm
  one null sink (S1/§2.4) rather than two.

---

## 10. Contention ledger + exit state

| window | contact | effect |
| --- | --- | --- |
| whole window | foreign lanes: `r79lb_1951294_*` (null sinks, taps, loopback pairs), `r78fol_*`; `…SPDIF__sink` carries foreign playback links throughout | read-only contact; my link listings carry their rows; no foreign object touched |
| 17:24–18:35Z | this seat: ~200 bounded legs, one null sink + one pw-cli-loaded filter-chain per audio leg, all index-verified unloads | own residue zero at exit |
| ~1 s per rep × 3 | `node.autoconnect=true` shape test | **this seat's FC playback stream was linked to the operator's default SPDIF sink and streamed silence for ≈1 s per rep** (recorded; §1 claim 2). No tone ever reached a host sink; every other leg was `node.autoconnect=false`. |
| 17:2x–18:3xZ | `~/.local/state/wireplumber/stream-properties` | this seat's stream rows (same class of residue every round leaves; no CLI can delete) |
| exit | `pactl list modules short \| grep r92s` = 0; `pw-dump` r92s nodes = 0; `ps` r92s audio children = 0; defaults SPDIF/Line unchanged | clean |

## 11. Artifacts & provenance

`corpus/live/r92-scout/` (untracked): `probes/pwlib.py` (own bounded runner +
own synth + own DFT/RBJ reference), `probes/driver.py` (v1, superseded),
`probes/driver2.py` (v2 rig: single-driver topology, pre/post dual tap, link
retry, validity gate, `preflight()`/`sweep()`), `probes/f0_load.py`,
`probes/f1_ports.py`, `probes/f2_e2e.py`, `probes/f3_driver.py`,
`probes/f4_wpexec.py`, `probes/f5_absent2.py`, `probes/f6_wpx_module.py`,
`probes/build_manifest.py`; `receipts/*.json` (one per stage, per-leg
triple-bounded); `scratch/` stimuli + captured WAVs; `runs/*.log` full stage
logs; `manifest.sha256`; `RECEIPTS.md`.

Key receipts: `v2_dsp.json`, `v2_ir.json`, `v2_clamp.json`, `v2_labels.json`,
`v2_links.json`, `v2_configs.json`, `v2_absent.json`, `f4_wpexec.json`,
`f6_wpx_module.json`, `f5_absent2.json`, `f3_driver.json`, `shape.json`,
`f1_ports.json`, `f2_e2e.json` (plus `runs/f0/receipt.json`).

On-disk sources read (shas in `sources/READ-SOURCES.sha256`):
`/usr/share/man/man7/libpipewire-module-filter-chain.7.gz` (1.6.8),
`/usr/share/pipewire/filter-chain/*.conf` (12),
`/usr/share/pipewire/filter-chain.conf`,
`/usr/share/doc/wireplumber/examples/wireplumber.conf.d/{filter-graph,smart-equalizer}.conf`,
`/usr/share/wireplumber/scripts/linking/rescan.lua`,
`/usr/share/wireplumber/scripts/node/filter-graph.lua`,
`/usr/share/man/man1/wpexec.1.gz`.

*scout leaf — measured and read, not judged.*
