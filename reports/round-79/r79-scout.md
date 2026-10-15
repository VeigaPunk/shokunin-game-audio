# R79 scout — the pw-loopback / filter-chain DSP surface

Round 79 pre-measurement. Host `plazir27`, measured 2026-10-14 ~18:26–18:50 UTC−3.
Repo `~/Projects/shokunin/audio-shokunin` @ HEAD `731937c` (`r77 report-last`).
Toolchain: PipeWire **1.6.8** (pw-loopback/pw-cat/pw-record/pw-cli/pw-dump/pw-link
1.6.8), libpulse **17.0** (pactl 17.0-98-gb096, protocol 35), Python **3.14.7**
(numpy 2.5.3), Linux **7.2.3-arch1-3**.

**Seat: SCOUT (leaf). Zero tracked-file edits. Every write is under
`corpus/live/r79-scout/` plus this report.** `corpus/fixtures/measure_audio.py`
is **dirty at sha256 `2cb08911c0c0fee6…`** (+2124/−3, mtime 18:44:14) — the r78
author's concurrent edit; this seat never read, imported, or executed it, and no
import path to `corpus/fixtures` exists anywhere in this harness (own
classifiers, own tone, own analysis). `git status` shows exactly two new untracked
paths for this seat: `corpus/live/r79-scout/` and `reports/round-79/`.

Live host state at start: default sink `…HiFi__SPDIF__sink`, default source the
DualSense mic; one probe-owned null sink from a sibling seat (`r78b_ns`) and a
second sibling seat (`r78-baseline`) recording the SPDIF monitor mid-run.

**Concurrency.** Three seats were live during these measurements: r78-baseline
(`--probe-capture-r77` battery), r78-boundary (SPDIF/Speaker monitor records),
this scout. §9 is a mandatory contamination ledger: four of this seat's early
legs fed tone into the shared default sink before the fail-closed pin was
added, and §9 names every window.

---

## 0. Headline — the brief's questions

| # | brief item | verdict | the single sharpest measured fact |
| --- | --- | --- | --- |
| 1 | pw-loopback shape / props | **PINNED** | one client, two nodes: `input.<n>` (Stream/Input/Audio, ports `input_FL/FR` + `monitor_FL/FR`) and `output.<n>` (Stream/Output/Audio, ports `output_FL/FR` only). **There is no graph link between them** — the copy is in-client (both nodes carry the same `client.id`); `node.link-group` is a WirePlumber hint, not a link |
| 2 | `-C`/`-P` target resolution — same fallback lattice? | **NO — it is a two-sided mix of the r78 laws, plus a new ungated default-source arm** | `-C <sink>` **without** `stream.capture.sink=true` → **default SOURCE** (live mic), never the sink monitor, never unlinked; the same name on pw-record is *unlinked* (r78). With the prop, `-C <sink>` → that sink's monitor, and an unresolvable name → **default sink monitor** (r78 law). `-P` mirrors r78's write side exactly: ungated, everything unresolvable → current default sink |
| 3 | `-C`/`-P` matrix mixing | **MEASURED, 0.5/0.5** | `-c 1 -m '[ MONO ]'` downmixes: peak 7801, FFT amp 2047.6 at 1.5 kHz on **both** channels — the analytic `0.5·(L+R)`. `-c 1` alone is **inert** (the default `-m '[ FL, FR ]'` wins); `-m` alone is enough; port names stay `FL/FR` |
| 4 | filter-chain conf.d loading | **PARSE-SOFT, RUNTIME-FATAL — and the module is a CLIENT** | a fragment with a syntax error is a *warning*: `conf.c:427 conf_load() error in config '<fragment>'`, the loader stays up and **later fragments still load**; a syntactically-valid fragment with an unknown filter label and no `nofail` **kills the loader (rc=254)**. The module publishes its nodes into the *running session* (it is a client, not a server) |
| 5 | pw-cat `-P` node latencies | **PROP-ONLY WITNESS** | `--latency 10ms` → `node.latency='480/48000'`, `--latency 256` → `'256/48000'`, `-P node.latency=1024/48000` → `'1024/48000'` and **the prop beats the flag**; the reported `Latency` param and the playout wall time (1.05–1.07 s for 1 s of audio) are **identical in all 10 legs** — the request is intent, not a measured param |
| 6 | `stream.capture.sink` on PLAYBACK-side tools | **DECORATION** | `pw-cat -p -P stream.capture.sink=true` records the prop on the node and changes nothing: valid target still honored, garbage target still → default sink (no gate, no redirect) |
| 7 | pw-record vs a loopback-created capture port | **THREE DISTINCT ARMS** | `--target input.<lb>` → **default source** (mic); `--target output.<lb>` → links `output.<lb>:output_FL/FR`, tone carried; `--target input.<lb>` **+ `stream.capture.sink=true`** → links `input.<lb>:monitor_FL/FR`, tone carried. Adding the prop to `output.<lb>` *breaks* it → default sink monitor |
| 8 | hot-plug: load/unload a null sink under a live loopback | **FOLLOWS BOTH WAYS** | unload the playback target → silent re-link to the default sink in ≤0.5 s, client alive; **load** the named target → re-link to it in ≤0.5 s with the tone verified there; unload the *capture* target → capture side re-links to the **default sink monitor** (the prop's fallback), client alive |

Plus the crash-class-adjacent operational traps in §10 (the pw-cli reply/global-dump
id hazard, client-scoped modules, the AF_UNIX 108-byte runtime-dir limit, the
missing `core.daemon` in the shipped `filter-chain.conf`).

---

## 1. Shape: what `pw-loopback` actually creates (`probe-a-shape-r79.json`)

`pw-loopback -n <n> -C <src> -i stream.capture.sink=true -P <sink>` produces **one
client and two nodes**:

| node | class | in-ports | out-ports |
| --- | --- | --- | --- |
| `input.<n>` | `Stream/Input/Audio` | `input_FL`, `input_FR` | `monitor_FL`, `monitor_FR` |
| `output.<n>` | `Stream/Output/Audio` | *(none)* | `output_FL`, `output_FR` |

Both nodes share one `client.id` (measured 88). `output.<n>` has **no input
ports**, so the capture→playback copy cannot be a graph link: the loopback client
copies buffers in-process. Measured link inventory for the pair: the only links
are `<source>:monitor_*`/`capture_*` → `input.<n>:input_*` and
`output.<n>:output_*` → `<sink>:playback_*`. **Zero links have both endpoints
inside the pair.** `node.link-group = loopback-<pid>-<n>` is the WirePlumber
"the client links these itself" marker, not a link object.

Prop inventory (identical on both nodes unless noted): `node.group =
pw-loopback-<pid>`, `node.link-group = loopback-<pid>-<n>`, `node.virtual = true`,
`node.want-driver = true`, `resample.disable = true`, `resample.prefill = true`,
`stream.is-live = true`, `object.register = false`, `clock.quantum-limit = 8192`,
`node.autoconnect = true`, `audio.channels = 2`, `audio.position = '[ FL, FR ]'`,
`port.group = stream.0`; `node.trigger = true` on the playback node only;
`media.name = '<n> input'` / `'<n> output'`.

**`target.object` is stored verbatim** from the `-C`/`-P` argument — including a
`.monitor` suffix that never resolves (`target.object = 'r79_ns_a….monitor'` while
the node is fed by the mic). Every link is created by `client.id 33`
(WirePlumber), i.e. resolution is the session manager's, not the client's.

`-i`/`-o` property syntax: **both** space- and comma-separated key=value lists are
accepted (`'stream.capture.sink=true media.role=DSP'` and the same with a comma
both landed both props on the capture node). `-i` writes only the capture node,
`-o` only the playback node.

*Not run:* the no-argument `pw-loopback` leg. It routes the **live mic into the
shared default sink** while two sibling seats record that sink's monitor. The two
one-sided legs (A5: `-P` only; A6: `-C` only) establish both autoconnect defaults
with zero tone leakage instead.

---

## 2. Capture side (`-C`) — `probe-b-capture-r79.json`

Playback side pinned to a probe-owned null sink on every leg; tone only where the
destination is probe-owned (content = `tone1k`/`tone1.5k` on the sink monitor).

| leg | `-C` argument | resolved producers of `input.<n>` | content | verdict |
| --- | --- | --- | --- | --- |
| B01 | `<probe sink>` + `stream.capture.sink=true` | `<sink>:monitor_FL/FR` | **tone** | honored |
| B02 | `<probe sink>`, no prop | **DualSense mic `capture_FL/FR`** | mic noise | **default source** |
| B03 | `<probe sink>.monitor` | **DualSense mic** | mic noise | `.monitor` never resolves |
| B04 | real `Audio/Source` (`…HiFi__Line__source`) | that source's `capture_FL/FR` | silence (host) | honored |
| B05 | `no_such_node_xyz` | **DualSense mic** | mic noise | default source |
| B06 | `0` | **DualSense mic** | mic noise | `0` is not a don't-link idiom |
| B07 | `<probe sink>` + `stream.capture.sink=false` | **DualSense mic** | mic noise | false ≡ absent |
| B08 | real source name **+ `target.object=<probe sink>` prop** | `<sink>:monitor_FL/FR` | **tone** | **prop beats flag** |
| B09 | `target.object=no_such_node_xyz` + sink prop true | **SPDIF `monitor_FL/FR`** | silence | r78 fallback law |
| B10 | sink + prop + `node.autoconnect=false` | *(none)* | — | honored, never links |
| B11 | `node.autoconnect=false`, no target | *(none)* | — | honored |
| B12 | **real source** + `stream.capture.sink=true` | **SPDIF `monitor_FL/FR`** | silence | prop makes a source "a sink" → default sink monitor |

### 2.1 The law

`pw-loopback`'s capture side is **not** the pw-record lattice. Two independent
switches:

* **`stream.capture.sink`** (a *stream* prop, honored exactly as on pw-record):
  `true` + a sink-like target → that sink's **monitor**; `true` + anything
  unresolvable or inapplicable (garbage, a source name) → **default sink
  monitor**; absent/`false` → the prop does not exist.
* **`node.autoconnect`** (default `true`): with no usable target and no prop, the
  stream **autoconnects to the default source** (the live mic) — this is the new
  arm. pw-record with an unresolvable target and no prop is *unlinked* (r78 law);
  pw-loopback's capture stream instead lands on the mic, so "did my capture side
  resolve?" is invisible in rc and stderr and only visible in the link graph.

---

## 3. Playback side (`-P`) — `probe-c-playback-r79.json`

Capture side pinned to a probe sink with the prop; tone only where the playback
destination is probe-owned; fallback legs run on a digital-silent source and are
judged by topology (declared `content_witness=declined_shared_default`).

| leg | `-P` / prop | consumers of `output.<n>` | content | verdict |
| --- | --- | --- | --- | --- |
| C01 | `<probe sink>` | `<sink>:playback_FL/FR` | **tone** | honored |
| C02 | second probe sink | `<sink2>:playback_FL/FR` | **tone** | honored |
| C03 | `no_such_sink_xyz` | **SPDIF `playback_FL/FR`** | (silent) | default sink |
| C04 | real **source** name | **SPDIF** | (silent) | default sink |
| C05 | `0` | **SPDIF** | (silent) | `0` is not a don't-link idiom |
| C06 | *(absent)* | **SPDIF** | (silent) | default sink |
| C07 | `-P <sink>` **+ `-o target.object=<sink2>`** | `<sink2>:playback_FL/FR` | **tone at sink2**; control record of `sink` = **all-zero** | **prop beats flag, with content control** |
| C08 | `-P <sink>` + `-o node.autoconnect=false` | *(none)* | — | honored, never links |
| C09 | `-P <sink>` + `-o stream.capture.sink=true` | `<sink>:playback_FL/FR` | **tone** | **decoration on playback** |
| C10 | `-P <sink>` + `-o target.object=no_such_node_xyz` | **SPDIF** | (silent) | prop beats flag → fallback |

**Law.** The write side reproduces r78's pw-cat law exactly: **ungated**,
`target.object` > `--target`/`-P` > absent, everything unresolvable or
inapplicable → the **current default sink**, rc=0, stderr empty, no error class.
Only topology (and content when the destination is probe-owned) separates honored
from fallback. `stream.capture.sink` on a playback stream is decoration.

---

## 4. Channel-map / matrix mixing (`probe-b-capture-r79.json`, CM group)

Tone = L 1 kHz / R 1.5 kHz, amp 8192, 48 kHz s16, played into a probe sink whose
monitor the loopback captures; the loopback plays into a second probe sink whose
monitor is recorded and analysed per channel.

| leg | flags | `audio.channels` | `audio.position` | measured | verdict |
| --- | --- | --- | --- | --- | --- |
| CM1 | `-c 1 -m '[ MONO ]'` | 1 | `[ MONO ]` | peak 7801 both ch, amp **2047.6** @1.5 kHz both ch, rms 3919 | **0.5/0.5 downmix** |
| CM2 | `-c 1` | 1 | `[ FL, FR ]` | peak 8192, amp 4095.3 @1 kHz (FL) / 4095.4 @1.5 kHz (FR) | **inert** — stereo passthrough |
| CM3 | `-m '[ MONO ]'` | 2 | `[ MONO ]` | peak 7801 both ch, amp 2047.6 both ch | **downmix** |
| CM4 | `-m MONO` | 2 | `MONO` | peak 7801 both ch, amp 2047.6 both ch | same as bracketed |

The CM1/CM3/CM4 signature is the analytic `0.5·(L+R)` mono mix (an 8192-peak sine
has FFT amp ≈4095; half-gain each → 2047.6, and the sum's peak ≈7801). The
**position array** drives the matrix, not `-c`: `-c 1` with a 2-entry position is
a no-op, and a 1-entry position downmixes even when `audio.channels = 2`. Port
names stay `input_FL/input_FR`/`output_FL/output_FR` in every case
(`port.group = stream.0`), so **the channel count is not visible in the port
names** — only in props + content.

---

## 5. `pw-cat --playback` `-P` vector (`probe-d-pwcat-r79.json`)

All legs: `pw-cat -p -P node.name=<tag> … --target <probe sink> -n 48000
<tone>`, node sampled ~0.7 s in, process reaped bounded.

| leg | request | measured `node.latency` | other |
| --- | --- | --- | --- |
| D01 | *(default)* | `'4800/48000'` | 100 ms default |
| D02 | `--latency 10ms` | `'480/48000'` | |
| D03 | `--latency 256` | `'256/48000'` | samples at the source rate |
| D04 | `-P node.latency=480` | `480` (literal, unvalidated) | |
| D05 | `-P node.latency=1024/48000` | `'1024/48000'` | |
| D06 | `--latency 5ms -P node.latency=2048/48000` | `'2048/48000'` | **prop beats flag** |
| D07 | `--latency 0` | *(no prop)* | stderr `error: bad latency value 0 (is zero)`, **rc=1**, stream still created and played — non-fatal argv error |
| D08 | `-P node.latency=0` | `0` | no validation, rc=1 (file-end), no error text |
| D09 | `--latency 500ms` | `'24000/48000'` | |
| D10 | `--latency 10ms -P node.force-latency=true` | `'480/48000'` | `node.force-latency=true` stored; no change to `node.latency` |

**Invariance.** The `Latency` param read from `pw-dump` is byte-identical in all
ten legs — `[{'direction':'Input','minQuantum':1.0,'maxQuantum':1.0,'minRate':0,
'maxRate':0,'minNs':0,'maxNs':0}]` — and total wall-to-exit is 1.05–1.07 s for
1 s of audio on every leg. On this host/sink the latency request is **only**
visible as the `node.latency` prop; nothing downstream re-negotiates visibly.
(Confidence: high for the prop values, medium for "no downstream effect" — a null
sink with a fixed quantum may simply absorb any request.)

**`stream.capture.sink` on a PLAYBACK tool** (D11–D13): with a valid target the
prop is recorded on the node and the target is still honored with the tone
verified (`tone1k`/`tone1.5k`); with `--target no_such_sink_xyz` the stream still
lands on the **default sink** — the prop neither gates nor redirects the write
side; `-P node.autoconnect=false` → unlinked (r78 law reproduced).

---

## 6. `pw-record --target` against a loopback-created node (`probe-d2-…json`)

Loopback running: `-C <ns_a> -i stream.capture.sink=true -P <ns_b>`, tone into
`ns_a`; the record stream is sampled **while alive** (the first pass sampled after
exit and was vacuous — recorded as a harness defect, fixed).

| leg | `--target` | extra prop | record stream's producers | content |
| --- | --- | --- | --- | --- |
| D2a | `input.<lb>` | — | **DualSense mic `capture_FL/FR`** | mic noise |
| D2b | `output.<lb>` | — | **`output.<lb>:output_FL/FR`** | **tone** |
| D2c | `input.<lb>` | `stream.capture.sink=true` | **`input.<lb>:monitor_FL/FR`** | **tone** |
| D2d | `output.<lb>` | `stream.capture.sink=true` | **SPDIF `monitor_FL/FR`** | silence |

Manual pin (D17): `pw-record --target 0 -P node.name=<tag>` then
`pw-link input.<lb>:monitor_FL <tag>:input_FL` (+FR) → both pins rc=0, content
**tone**. So the `monitor_*` ports on the loopback's capture node are real data
ports; the name-based route to them needs `stream.capture.sink=true`, and the
playback node's output ports are capturable by name directly.

---

## 7. Hot-plug pseudo-surface (`probe-e-hotplug-r79.json`)

Tone stopped before every unload, so any silent re-link to the shared default sink
carries digital silence; content witnesses are only taken while the destination is
a live probe-owned sink.

| leg | event | before | after (≤0.5 s) | client |
| --- | --- | --- | --- | --- |
| E1 | `pactl unload-module` of the **playback target** | `output.<lb>` → `<hp>:playback_FL/FR`, monitor content **tone** (peak 8192) | `output.<lb>` → **SPDIF `playback_FL/FR`**, unchanged at +1.5 s and +3.0 s | **alive**, rc=−9 (probe SIGKILL), stderr empty |
| E2 | **load** the named target after the route is up | `output.<lb>` → **SPDIF** | `output.<lb>` → **`<hp2>:playback_FL/FR`** at +0.5 s, content **tone** (peak 8192) | alive |
| E3 | `pactl unload-module` of the **capture target** | `input.<lb>` ← `<ns_a>:monitor_FL/FR`, monitor content **tone** | `input.<lb>` ← **SPDIF `monitor_FL/FR`** (the sink-prop fallback), playback side untouched | **alive** |

**Law.** A pw-loopback route follows its named target *both* ways: target loss →
silent re-link to the default sink (write side) or to the default sink monitor
(capture side with the prop); target appearance → re-link to it. The client never
exits and never prints anything. This is the loopback twin of r78's pw-cat
mid-play target-loss row, extended with the *return* direction.

---

## 8. `libpipewire-module-filter-chain` (`probe-f-filterchain-r79.json`)

### 8.1 Mechanism (measured, corrects the brief's mental model)

The filter-chain module is a **client of a running session**: its init calls
`try_connect()` on `pipewire-0` in the runtime dir. A standalone instance pointed
at an empty private runtime dir fails at module load —

```
mod.filter-chain | [module-filter-ch: 2099 pipewire__module_init()] can't connect: Host is down
pw.conf | could not load mandatory module "libpipewire-module-filter-chain": Host is down
default | failed to create context: Host is down            (loader exits non-zero)
```

Two further traps in the same area:

* the shipped `/usr/share/pipewire/filter-chain.conf` (68 lines) does **not** set
  `core.daemon`; a `pipewire -c filter-chain.conf` instance therefore never
  listens on its own socket (measured: runtime dir stays empty, `pw-dump` →
  `can't connect: Host is down`, while the daemon is alive and its log ends at
  `start main loop`). Injecting `core.daemon = true` makes it listen — and then
  the socket path can exceed the AF_UNIX limit: `socket path "…/pipewire-…-manager"
  plus null terminator exceeds 108 bytes` → `could not load mandatory module
  "libpipewire-module-protocol-native": File name too long` → context creation
  fails (`rc=220`; the same class of private-instance failure also exits `rc=144`
  in the no-`core.daemon` shape). Keep private runtime dirs short.
* fragments are merged from `<config-dir>/filter-chain.conf.d/*.conf` and the
  nodes land in the **session the loader connects to**; killing the loader removes
  them (measured `nodes_after_kill = []`).

### 8.2 conf.d legs (documented recipe, scratch `PIPEWIRE_CONFIG_DIR`, live session)

| leg | fragment set | loader | node in session | stderr | verdict |
| --- | --- | --- | --- | --- | --- |
| F1 | good (builtin mixer graph) | alive | **yes** (`mix_input.r79_fc_good`), gone after kill | — | **fragment loads; nodes are client-scoped** |
| F2 | one syntax error | **alive** | no | `W … conf.c:427 conf_load() error in config '<fragment>'` | **parse error is fail-soft** |
| F3 | good(10) + bad(20) | alive | **yes** (good) | warning for the bad one | earlier fragments survive |
| F3b | bad(10) + good(20) | alive | **yes** (good) | warning for the bad one | **per-fragment**: a bad fragment does not poison later ones |
| F4 | bad label + `flags = [ nofail ]` | alive | no | *(empty)* | module failure tolerated, silent |
| F5 | bad label, **no** `nofail` | **exits rc=254** | no | *(empty)* | **runtime graph error is fatal to the loader** |
| F6 | base only (control) | alive | no | — | control |

### 8.3 Live-daemon module load (`pw-cli`, one line, client-scoped)

| leg | command | reply | graph effect |
| --- | --- | --- | --- |
| F7 | `load-module libpipewire-module-filter-chain <args>` | `1 = @module:22` | **both nodes published** (`mix_input.…`, `mix_output.…`); manual pins onto the chain's input ports (`playback_FL/FR`) rc=0; content = the mono mix below |
| F8a | `unload-module @module:22` | `Error: "unload-module: unknown module '@module:22'"` | nodes stay (refusal shape; teardown is client exit) |
| F9 | same load with `label = nosuchfilter` | `Error: "Could not load module"` | no node; **daemon alive** |
| F10 | malformed args (`{ args = { oops`) | `Error: "Could not load module"` | no node; daemon alive |
| F11 | `quit` the pw-cli client | — | **nodes gone** (`nodes_after_quit = []`) |

### 8.4 DSP content witness (the graph actually processes audio)

Graph: `builtin` `mixer` node, `"Gain 1" = 0.5`, `"Gain 2" = 0.5`, inputs
`mix:In 1/2` ← FL/FR, output `mix:Out` → mono playback stream with
`stream.dont-remix = true`. Tone injected with manual pins onto the chain's input
ports (`playback_FL/FR`).

Measured (identical for the conf.d path F1 and the pw-cli path F7):

```
recorded sink monitor: peak [7801, 0]  rms [3915.7, 0.0]
dom: FL 2047.6 @ 1500.0 Hz ; FR 0.0
edges: mix_output.<n>:output_FL -> <probe sink>:playback_FL
       <tone>:output_FL/FR     -> mix_input.<n>:playback_FL/FR
```

That is exactly `0.5·(L+R)` on FL and **digital silence on FR** — the mono stream
links to the sink's FL only because `stream.dont-remix = true` forbids the
upmix. Same signature as the §4 channel-map downmix, which is an independent
cross-check of both measurements.

---

## 9. Contamination ledger (mandatory read for the sibling seats)

Three seats shared the graph. This scout's tone (L 1 kHz / R 1.5 kHz, amp 8192)
and one mic leak reached the **shared default sink (SPDIF)** before the
fail-closed pin was added to the harness. Two sibling seats record that sink's
monitor (r78-baseline `--probe-capture-r77`; r78-boundary SPDIF/Speaker legs), so
these windows are named confounds, class `r79_scout_default_sink_leak`:

| window (local, UTC−3) | source leg | duration | content at SPDIF |
| --- | --- | --- | --- |
| 18:29:21.5 → 18:29:28.5 | recon `pw-loopback` with **no** `-C`/`-P` | ~7 s | **live mic noise** (peak ≈369/32768 ≈ −39 dBFS), not tone |
| 18:32:21.3 → 18:32:24.5 | `probe-b` B01-base, first pass (missing `-P` pin) | ~3.2 s | tone 1 kHz/1.5 kHz |
| 18:32:42.2 → 18:32:45.4 | `probe-b` B08-prop-beats-flag, first pass | ~3.2 s | tone |
| 18:33:51.9 → 18:33:55.2 | `probe-b` B01-base, second pass | ~3.3 s | tone |
| 18:34:12.7 → 18:34:15.9 | `probe-b` B08-prop-beats-flag, second pass | ~3.2 s | tone |
| 18:48:54.4 → 18:48:56.0 | `probe-f` F3 pin leg (chain output autoconnected to SPDIF via `node.passive`) | ~1.6 s | mono 0.5·(L+R) mix, peak 7801 |
| 18:48:59.4 → 18:49:01.0 | `probe-f` F3b pin leg, same mechanism | ~1.6 s | mono mix |

Total ≈14 s of tone plus ≈7 s of mic noise across six windows. Nothing else this
seat ran fed the shared sink: every other leg was pinned to a probe-owned null
sink, and every fallback leg (topology-only) ran on a digital-silent source.

**Two harness defects, both fixed and both worth carrying into the arm:**

1. `run_leg` initially omitted the `-P` pin, so two "capture-side" legs sent their
   tone to the default sink. Fix: a **fail-closed assert** in `run_leg` — a tone
   leg must carry an explicit `-P` naming a probe-owned sink, and an `-o
   target.object` that could escape is refused.
2. The filter-chain legs were outside that assert and leaked twice via
   `node.passive = true` (the chain's playback stream autoconnects to the default
   sink). Fix: **the assert must cover every tone-injection path**, including
   filter-chain fragments and legs whose destination is implicit. An arm that
   adds these cells should pin `playback.props.target.object` on *every*
   filter-chain fragment, and should treat "destination is implicit" as a refusal.

---

## 10. Operational hazards (measured)

| # | hazard | evidence |
| --- | --- | --- |
| 1 | **Never scrape an id out of a `pw-cli` reply and feed it to `destroy`.** Replies interleave the command result with the async global dump; a scraped `@module:22` named the daemon-owned `libpipewire-module-session-manager`. The `destroy` was refused and the graph stayed healthy, but this seat will not repeat it | §8.3 F8a; post-check: module 22 present, `pactl info` healthy, wireplumber alive |
| 2 | `pw-cli load-module` args must be on **one line**: pw-cli parses line-by-line, so a multi-line args string is truncated → `Error: "Could not load module"` | first F7 pass |
| 3 | `-C 0` / `-P 0` are **not** the pw-cat `--target 0` don't-link idiom; `target.object = 0` falls back to the default source/sink | B06, C05 |
| 4 | `.monitor` names never resolve as pw-loopback targets (stored verbatim, then fallback) | B03 |
| 5 | `--latency 0` is a **non-fatal** argv error: message on stderr, rc=1, stream still created without `node.latency` | D07 |
| 6 | Modules loaded through a client (`pw-cli`, the filter-chain loader) are **client-scoped**; they die with the client. `unload-module @module:<id>` is refused with `unknown module` | F1 `nodes_after_kill=[]`, F8a, F11 |
| 7 | A private runtime dir must be **short** (AF_UNIX 108 bytes) or protocol-native fails and the daemon dies rc=220 | §8.1 |
| 8 | The shipped `filter-chain.conf` lacks `core.daemon`, so a standalone instance never listens; the documented recipe works because the module is a *client* of the running session | §8.1 |

---

## 11. Artifacts, receipts, provenance

All under `corpus/live/r79-scout/` (untracked). Harness: `r79_probe.py` (own
classifiers; never imports `corpus/fixtures`), drivers `probe_a…probe_f`, raw
records in `raw/`, tones/silence in `scratch/`. See `RECEIPTS.md` for sha256 and
per-artifact content. Node naming: every probe node/sink carries `r79_<pid>` and
every stream `r79_<pid>_<leg>`; probe null sinks are loaded per driver and
unloaded in a `finally` (verified: no `r79*` node, process or null sink remains).

**Labrat dispatch (exactly one, read-only, depth-2).** Hypothesis H1 — conf.d
fragment merge-append + the parse/runtime failure split. Reported **NOT
EXECUTED**: its seat exposes read-only filesystem tools only (no exec, no
`pipewire`), the same constraint the r78 labrat hit. It returned static evidence
only (fragment path from the conf header; `sink-mix-FL-FR.conf` as the
plugin-free builtin graph) and the commands it would have run; zero writes, zero
processes. This seat answered H1 with §8 instead. Route provenance: advisory
prediction, no measured claim taken from it.

**What this report does not claim.** No perceived-quality claim; no claim that the
latency vector has no effect on a *real* ALSA sink (only this null sink was
measured); no claim about `-m` matrix syntax beyond the four forms tested; no
claim that every filter-chain plugin type behaves like `builtin` (only `builtin`
was exercised — LADSPA/FFmpeg node types were not available in the probe's
plugin-free fragment); `filter-chain.conf.d` merge order beyond "later fragments
still load after a bad one" was not exhaustively probed.

## 12. Confidence

* **High** (reproduced twice or with content + topology witnesses): §1 shape, §2/§3
  lattices, §4 matrix signature, §5 prop values + prop-beats-flag, §6 four record
  arms, §7 all three hot-plug legs, §8.2/§8.3 failure split, §8.4 DSP signature.
* **Medium**: §5 "no downstream effect" (single sink type, single host, no
  strace); §7 re-link latency bounds (0.5 s sampling resolution).
* **Unknown**: whether the ungated default-source fallback of §2 is WirePlumber's
  generic autoconnect for `Stream/Input/Audio` or a pw-loopback-specific path
  (both would look identical here); whether `-P 0`/`-C 0` resolution differs on a
  host with a session manager other than WirePlumber.
