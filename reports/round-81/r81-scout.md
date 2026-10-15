# R81 scout — the GStreamer↔PipeWire surface, measured

Round 81 pre-measurement. Host `plazir27`, measured **2026-10-15 05:24:59Z →
05:37:29Z** (host local UTC−3, 02:24–02:37). Repo
`~/Projects/shokunin/audio-shokunin` @ HEAD `d9aa6f9`. Toolchain:
**GStreamer 1.28.6** (`gst-launch-1.0`/`gst-inspect-1.0`; gstreamer 1.28.6-3,
gst-plugins-base/good 1.28.6-3, **gst-plugin-pipewire 1:1.6.8-1** — no `-bad`,
no `-ugly`), PipeWire **1.6.8** (pipewire 1:1.6.8-1), libpulse
**17.0+r98+gb096704c0-1** (protocol 35), ffprobe **n9.0.1**, Python **3.14.7**
(numpy 2.5.3), Linux **7.2.3-arch1-3**.

**Seat: SCOUT (leaf). Zero tracked-file edits. Every write is under
`corpus/live/r81-scout/` plus this report.** `corpus/fixtures/measure_audio.py`
was dirty at entry and still dirty at exit (`532440 B`, sha256 prefix
`9cb045a26cca1fa3`, mtime 02:32:52 local) — **that is a sibling lane's
concurrent edit; this seat never read, imported or executed it.** Own harness
`r81_probe.py` (9 stages — baseline/inventory/pw_sink/pw_src/pulse/loss/loss2/
errors/final — one consolidated JSON receipt each), `analyze.py`, `rerun.py`.
Scratch **7.0 MB** at exit (the 11.5 MB tone anchor was deleted; per-leg
receipts + the consolidated JSONs are the durable evidence). Every leg is
bounded three ways: element bound (`num-buffers`) where it exists, a wall cap,
and a byte cap **checked in the same loop that owns the process group** — no
watchdog thread that can silently fail to arm (the r77 flood lesson).

**Isolation.** All routing legs target a **seat-owned null sink
`gst_r81_ns`** (module index verified against the name before *every* unload;
nothing was ever unloaded by name) or the host default sink, and every stream
node is named `gst_r81_*` or is the default `gst-launch-1.0`. Content anchor
is a seat-owned 1 kHz tone (`gst_r81_tone`, peak 8192) played **only** into
`gst_r81_ns`. §10 is the mandatory contention ledger — the host default sink
was moved by a foreign lane during this window and moved back.

---

## 0. Headline: seven frontier claims

| # | frontier item | verdict | the single sharpest measured fact |
| --- | --- | --- | --- |
| 1 | element availability lattice | **PINNED** | all five named elements exist and are stable over 3 reps: `pipewiresink`/`pipewiresrc` (`Sink\|Source/Audio/Video`, plugin **version 1.6.8** = PipeWire's), `pulsesink`/`pulsesrc` (`Sink\|Source/Audio`, 1.28.6), `autoaudiosink`/`autoaudiosrc` (`libgstautodetect.so`); `openalsink` is **absent** (rc=255) |
| 2 | `pipewiresink`/`pipewiresrc` naming + media.class | **MEASURED** | default node is `gst-launch-1.0` / `Stream/Output\|Input/Audio`; **`client-name=` renames the *node*** (name+description+media.name) while **`client-properties=props,application.name=` renames the *Client*** — the two names cross over |
| 3 | is `-P`-equivalent targeting settable via gst props? | **YES, BOTH VECTORS** | gst `target-object=` writes **both** `node.target` *and* `target.object`; `stream-properties=props,node.target=` / `target.object=` each route alone; `PIPEWIRE_PROPS` **and** `PIPEWIRE_NODE` env vectors are honored; **the gst element property wins** over `stream-properties` (reverse of r78's `-P`-beats-flag law) |
| 4 | `pulsesink device=` vs the session default | **NAME HANDED TO THE SERVER — no client-side binding** | a bogus `device=` is **rc=0 with a silent fallback to the current default sink** (`target.object=no_such_sink_r81` is left on the node); the *record* direction refuses the same input (rc=1 `No such entity`); `pactl move-sink-input` is sticky (no snap-back ≥2.5 s) |
| 5 | stream behaviour under target loss | **SPLIT BY DIRECTION — new law** | **playback** (`pipewiresink target-object=`, `pulsesink device=`) re-links to the default sink within one 0.2 s sample and never exits; **capture** (`pipewiresrc`) does **not** re-link — the file **freezes at the last buffer (204 844 B), no error, no EOS, process alive** — where a same-session `pw-record` control re-links within one sample |
| 6 | gst-launch exit/error classes | **TYPED (rc split 1 / 255 / −9)** | parse-time refusals are **rc=1 + no artifact** (`WARNING: erroneous pipeline: …`); runtime state-change failures are **rc=255 + a 0-byte artifact** (`ERROR: from element …` + `Failed to set pipeline to PAUSED`); `pulsesrc` is the outlier at **rc=1 with a 0-byte artifact** |
| 7 | `autoaudiosink` / `autoaudiosrc` backend | **PULSE PATH BOTH** | `autoaudiosink` → `pulsesink` (a pw `Stream/Output/Audio` node appears, linked to the default sink); `autoaudiosrc` → `pulsesrc` → **fails rc=1** `Failed to connect stream: No such entity` then `not-negotiated (-4)` — r77's "pulsesrc has no working default" law survives the autodetect wrapper |

---

## 1. FRONTIER 1 — the `gst-inspect-1.0` availability lattice
(`receipts/s1-inventory.json`, 3 reps per element, all rows byte-stable)

| element | rc | Klass | plugin | version |
| --- | --- | --- | --- | --- |
| `pipewiresink` | 0 | `Sink/Audio/Video` | `libgstpipewire.so` | **1.6.8** |
| `pipewiresrc` | 0 | `Source/Audio/Video` | `libgstpipewire.so` | **1.6.8** |
| `pulsesink` | 0 | `Sink/Audio` | `libgstpulseaudio.so` | 1.28.6 |
| `pulsesrc` | 0 | `Source/Audio` | `libgstpulseaudio.so` | 1.28.6 |
| `autoaudiosink` | 0 | `Sink/Audio` | `libgstautodetect.so` | 1.28.6 |
| `autoaudiosrc` | 0 | `Source/Audio` | `libgstautodetect.so` | 1.28.6 |
| `alsasink` / `alsasrc` | 0 | `Sink\|Source/Audio` | `libgstalsa.so` | 1.28.6 |
| `audiotestsrc` | 0 | `Source/Audio` | `libgstaudiotestsrc.so` | 1.28.6 |
| `wavenc` / `wavparse` | 0 | `Codec/Muxer\|Demuxer/Audio` | `libgstwavenc.so` / `-parse` | 1.28.6 |
| `filesink`, `fakesink` | 0 | `Sink/File`, `Sink` | `libgstcoreelements.so` | 1.28.6 |
| `audioconvert`, `audioresample`, `volume`, `level`, `spectrum` | 0 | — | base/good | 1.28.6 |
| `jackaudiosink` / `jackaudiosrc` | 0 | `Sink\|Source/Audio` | `libgstjack.so` | 1.28.6 |
| `osssink`, `oss4sink`, `playbin` | 0 | `Sink/Audio`, `Sink/Audio`, `Generic/Bin/Player` | good/playback | 1.28.6 |
| `openalsink` | **255** | — | — | — |
| `nosuchelement_xyz` (control) | **255** | — | — | — |

- The `pipewire` **plugin** itself inspects (rc=0) at version **1.6.8** — the
  gst plugin tracks the PipeWire version, not the GStreamer one.
- `gst-inspect-1.0 -b` → **0 blacklisted files** (the 1295-feature / 196-plugin
  census is r77's; not re-measured here).
- The `Sink|Source/Audio/Video` klass of the pipewire pair is not cosmetic — it
  is the mechanism behind r77 §3.4 (the sink-side target resolution is
  audio-path-only).
- **rc asymmetry on the same absence**: the *identical* missing element is
  **rc=255** through `gst-inspect-1.0` and **rc=1** through `gst-launch-1.0`'s
  parser (§5). Never read a `gst-inspect` rc as a `gst-launch` rc.

---

## 2. FRONTIER 2 — `pipewiresink`/`pipewiresrc`: naming, media.class, prop vectors
(`receipts/s2-pw-sink.json`, `receipts/s3-pw-src.json`; 3 reps/leg)

### 2.1 Node identity (the default shape)

| client | node.name | node.description | media.class | media.name | other node props |
| --- | --- | --- | --- | --- | --- |
| `pipewiresink` (bare) | `gst-launch-1.0` | `gst-launch-1.0` | `Stream/Output/Audio` | `gst-launch-1.0` | `node.rate=1/48000`, `node.loop.name=pipewire-main-l`, `node.async=true`, `node.want-driver=true`, `object.register=false`; **no `application.name`** |
| `pipewiresrc` (+prop) | `gst-launch-1.0` | `gst-launch-1.0` | `Stream/Input/Audio` | `gst-launch-1.0` | same shape + `stream.capture.sink="TRUE"` |
| `pulsesink` | `gst-launch-1.0` | `gst-launch-1.0` | `Stream/Output/Audio` | **`audiotest wave`** | `application.name=gst-launch-1.0` |
| `pw-record` (control) | `gst_r81_pwrec` (`-P node.name=`) | `gst_r81_pwrec` | `Stream/Input/Audio` | **the file path** | `application.name=pw-record`, `media.category=Capture`, `media.role=Music`, `media.filename=<path>`, `node.latency=4800/48000`, `node.loop.name=main-loop` |

The pulse element fills `media.name` from the pipeline (audiotest), the
pipewire element leaves it as the client name, and `pw-cat` fills it from the
file — three different `media.name` conventions on one host.

### 2.2 The target lattice — every row 3/3, `rc=0` unless noted (`s2-pw-sink`)

| leg (`audiotestsrc wave=silence num-buffers=96 ! audio/x-raw,… ! <sink>`) | node props written | where it linked |
| --- | --- | --- |
| `pipewiresink` | — | default sink (`…SPDIF__sink:playback_*`) |
| `target-object=gst_r81_ns` | **`node.target=NS` AND `target.object=NS`** | `gst_r81_ns:playback_*` |
| `stream-properties=props,node.target=NS` | `node.target=NS` only | `gst_r81_ns` |
| `stream-properties=props,target.object=NS` | `target.object=NS` only | `gst_r81_ns` |
| `target-object=no_such_sink_r81` | both = `no_such_sink_r81` | **default sink — silent fallback** |
| `target-object=NS` + `stream-properties=props,target.object=no_such_r81` | **both = `NS`** | `gst_r81_ns` — **the gst property wins** |
| `PIPEWIRE_PROPS={ node.name=gst_r81_env node.target=NS }` (env) | `node.name=gst_r81_env`, `node.target=NS` | `gst_r81_ns` |
| `PIPEWIRE_NODE=NS` (env) | `target.object=NS` | `gst_r81_ns` |
| `stream-properties=props,node.name=gst_r81_snk_name` | `node.name` renamed; description/media.name stay `gst-launch-1.0` | default sink |
| `client-name=gst_r81_client` | node.name **and** description **and** media.name = `gst_r81_client`; **pw Client object name stays `gst-launch-1.0`** | default sink |
| `client-properties=props,application.name=gst_r81_app` | **pw Client object name = `gst_r81_app`**; node untouched | default sink |
| `stream-properties=props,media.class=Audio/Sink` | class overridden | **no link — pipeline stalls (wall-cap kill)** |
| `stream-properties=props,node.autoconnect=false` | `node.autoconnect="FALSE"` (a **string**) | **no link — pipeline stalls** |

**Laws.**

- **`target-object=` is a two-key write.** The gst property emits *both*
  `node.target` and `target.object`; the pw prop vector can emit either alone
  and both route. (r78 measured the same two keys on `pw-record` — where
  `--target` writes **only** `target.object`, §2.4.)
- **Precedence is client-specific and inverted vs r78.** For `pw-record`, the
  `-P target.object=` prop beat the `--target` flag. For `gst-launch`, the
  element's own `target-object=` **overwrites** the `stream-properties`
  `target.object` (measured on the node props *and* on the link).
- **Env prop vectors are honored by gst too** — `PIPEWIRE_PROPS` (a structure
  literal) and `PIPEWIRE_NODE` (a bare node name, which lands as
  `target.object`), same as `pw-record`/`pw-play` in r78.
- **A sink-side target miss is silent** (`rc=0`, fallback to the default sink).
  Contrast `pipewiresrc` **without** the capture prop: `rc=255`, 0-byte file,
  `stream error: target not found`. The r78 one-sided-fallback asymmetry
  reproduces across the gst boundary: the sink direction always has somewhere
  to go, the source direction does not.
- **`media.class` override and `node.autoconnect=false` produce the same
  shape**: unlinked, and the *pipeline stalls* (killed at the wall cap, `rc=−9`)
  — a sink with no consumer never drains.
- **`node.autoconnect` is a string** (`"FALSE"`) while the gst-side default is
  a boolean `true` — a probe that type-checks props will misread this row.

### 2.3 Capture identity, tone-anchored (`s3-pw-src`, tone = 1 kHz peak 8192 into `gst_r81_ns`)

| leg | rc | class | link (witness) | file | peak |
| --- | --- | --- | --- | --- | --- |
| `c0` `target-object=NS`, **no prop** | 255 | `target not found` | none | **0 B** | — |
| `c1` + `stream.capture.sink=true` | 0 | — | `gst_r81_ns:monitor_* → gst-launch-1.0:input_*` | 819244 B finalized, 204800 frames | **8192** |
| `c2` c1 + `node.name=gst_r81_src_name` | 0 | — | links to `gst_r81_src_name:input_*` | 819244 B | 8192 |
| `c3` c1 + `client-name=gst_r81_src_client` | 0 | — | links to `gst_r81_src_client` | 819244 B | 8192 |
| `c4` `target-object=NS.monitor` **+ prop** | 0 | — | **`…SPDIF__sink:monitor_*`** (the default sink!) | 409644 B | 0 |
| `c5` env `PIPEWIRE_PROPS={stream.capture.sink=true node.name=gst_r81_src_env}` | 0 | — | `gst_r81_ns:monitor_* → gst_r81_src_env` | 819244 B | 8192 |
| `c6` c1 + `node.autoconnect=false` | **−9 (wall cap)** | — | **none** | **0 B (no header at all)** | — |
| `c7` `stream-properties=props,stream.capture.sink=true,node.target=NS` (no gst prop) | 0 | — | `gst_r81_ns:monitor_*` | 819244 B | **8192** |
| `c8` `target-object=no_such_r81` + prop | 0 | — | **`…SPDIF__sink:monitor_*`** | 409644 B | 0 |
| `c9` `pw-record` control on the same sink | 1 (normal finalize) | — | `gst_r81_ns:monitor_* → gst_r81_pwrec` | 192044 B | 8192 |

- **r77 residual resolved — the `.monitor` suffix does not resolve for
  `pipewiresrc`, even with the prop.** The proof needs a *non-default* sink:
  `target-object=gst_r81_ns.monitor` + prop lands on **the default sink's
  monitor** (`…SPDIF__sink:monitor_*`), not on `gst_r81_ns`. In r77 the
  fallback and the honoured target were the same node, so the two could not be
  separated. **They are separate here.**
- The gst element writes `stream.capture.sink` as the **string `"TRUE"`**;
  `pw-record` writes the **boolean `true`**. Both work — but a probe that
  asserts a boolean will read the gst row as "prop absent".
- An **unlinked gst capture stalls with a 0-byte artifact** (no wav header at
  all), where `pw-record --target 0` stalls with a 44-byte placeholder (r78).
  Same PipeWire state, three consumer shapes: `pw-record` 44 B, `gst` 0 B,
  `ffmpeg -f jack` zero-fill.

---

## 3. FRONTIER 3 — `pulsesink device=` targeting vs the session default
(`receipts/s4-pulse.json`, 3 reps/leg; default sink at stage entry = SPDIF)

| leg | rc | node prop | where it linked |
| --- | --- | --- | --- |
| `pulsesink` (bare) | 0 | — | default sink (SPDIF) |
| `device=gst_r81_ns` | 0 | `target.object=gst_r81_ns` | `gst_r81_ns:playback_*` |
| `device=no_such_sink_r81` | **0** | `target.object=no_such_sink_r81` | **default sink — silent fallback** |
| `device=gst_r81_ns.monitor` | 0 | `target.object=gst_r81_ns.monitor` | **default sink** |
| `device=…SPDIF__sink` | 0 | `target.object=…SPDIF__sink` | SPDIF (honored) |
| `device=…HiFi__Line__source` (a *source*) | 0 | `target.object=…Line__source` | **default sink** |
| env `PULSE_SINK=gst_r81_ns`, bare element | 0 | `target.object=gst_r81_ns` | `gst_r81_ns` — **the env default is honored** |
| env `PULSE_SINK=gst_r81_ns` + `device=…SPDIF` | 0 | `target.object=…SPDIF` | SPDIF — **`device=` beats `PULSE_SINK`** |
| `server=unix:/nonexistent-r81` | **255** | — | none; `Failed to connect: Connection refused` + `ERROR: pipeline doesn't want to preroll.` + `Failed to set pipeline to PAUSED.` |
| `device=gst_r81_ns` + `stream-properties=props,node.name=gst_r81_pulse_name` | 0 | node renamed; `target.object=NS` | `gst_r81_ns` |
| `device=gst_r81_ns`, then `pactl move-sink-input <idx> SPDIF` at t=1.5 | move rc=0 | — | **moved and stays moved** (SPDIF at +1 s, +2 s, +2.5 s) — **no snap-back** |

**Laws.**

- **`device=` is a *name handed to the server*, not a node bind.** The client
  writes it verbatim into `target.object` and the link is created by policy:
  a miss is not an error (playback), the link follows
  `pactl move-sink-input` without being re-asserted, and on target loss the
  link is re-created to the *current* default (§4). There is **no client-side
  resolution** of the device string.
- **The direction asymmetry is real and same-session proven**: `pulsesink
  device=<garbage>` → **rc=0 + fallback**; `pulsesrc device=<garbage>` →
  **rc=1** `Failed to connect stream: No such entity` + 0-byte file (§5, e11).
  The pulse protocol's playback path is lenient, the record path is strict.
- **`PULSE_SINK` (a client-local default) is honored by gst**, and `device=`
  outranks it.
- **The `.monitor` suffix is not a sink name**: as a `device=` it silently
  falls back (same row as a source name and as garbage).

---

## 4. FRONTIER 4 — target loss: the sink side re-links, the source side freezes
(`receipts/s5-loss.json` incl. `body.followup`; `pactl unload-module <index>`
at t≈1.20 s, index verified against `gst_r81_ns` first; 3 reps/leg; 0.2 s
timeline sampling)

### 4.1 Playback re-links, silently and immediately

| leg | before | at the unload sample | after | process | stderr |
| --- | --- | --- | --- | --- | --- |
| `t1` `pipewiresink target-object=gst_r81_ns` | `gst-launch-1.0:output_* → gst_r81_ns:playback_*` | links `{}` | **`…SPDIF__sink:playback_*` at +0.2 s, held to the 4.5 s wall cap** | alive (wall-cap kill) | empty |
| `t2` `pulsesink device=gst_r81_ns` | same | `{}` | **same** | alive | empty |

This is r80's L1 law reproduced **through the GStreamer clients**: unload of a
live target is *target loss*, the consumer never dies and never errors, and
WirePlumber re-links it to the current default within one 110–200 ms sample.

### 4.2 Capture does **not** re-link — it freezes (new law)

| leg | links after unload | artifact | process | stderr |
| --- | --- | --- | --- | --- |
| `t3` `pipewiresrc target-object=NS` + prop | **`{}` for the rest of the window** | **frozen at 204 844 B** (= 44 + 51 200 frames × 4 B, the last buffer before the unload), header `wavenc_streaming` (`data` field `0x7FFFF000`), **unfinalized** | **alive** (wall-cap kill) | **empty** |
| `t4` same + `on-disconnect=error` | identical | identical | alive | empty |
| `t5` same + `on-disconnect=eos` | identical | identical | alive | empty |
| `t6` prop-only `target.object=NS` (no gst `target-object`, so **no `node.target` prop**) | identical | identical | alive | empty |
| `t7` **`pw-record` control**, same host event | **`…SPDIF__sink:monitor_*` at +0.2 s** | grows ≈187 KB/s (nominal 48 k×2ch×s16 = 192 KB/s) | alive | only the file path (normal) |

- **The capture-side fallback law is client-specific.** r80's L4 ("the capture
  side follows the same fallback") holds for `pw-record` — re-measured here in
  the same session on the same host event — and **does not hold for
  `pipewiresrc`**, which stalls at the buffer boundary with a *frozen,
  unfinalized* artifact and no error.
- **t6 kills the obvious explanation**: the stall is not caused by the stale
  `node.target` prop (a prop-only `target.object` capture stalls identically).
  It is the client, not the prop vector.
- **`on-disconnect` is inert under target-node loss**: `none`, `error` and
  `eos` are byte-identical in outcome (frozen file, no stderr, alive).
- The frozen artifact is *silent in rc and in stderr* — only the **byte count
  stopping** (and the `wavenc_streaming` placeholder header) reveals it. A
  probe that asserts "the pipeline is still running" or "rc is clean" will
  call this a healthy capture.

---

## 5. FRONTIER 5 — `gst-launch` exit/error classes vs pw's
(`receipts/s6-errors.json`, 3 reps/leg, every row byte-stable)

| leg | rc | first stderr line (verbatim) | artifact |
| --- | --- | --- | --- |
| `e1` missing element (source) | **1** | `WARNING: erroneous pipeline: no element "nosuchelementsrc_xyz"` | **not created** |
| `e2` missing element (sink) | **1** | `WARNING: erroneous pipeline: no element "nosuchelementsink_xyz"` | — |
| `e3` **bogus property** | **1** | `WARNING: erroneous pipeline: no property "bogus-prop" in element "audiotestsrc"` | — |
| `e4` bogus property on a pw element | **1** | `WARNING: erroneous pipeline: no property "bogus-prop" in element "pipewiresink"` | — |
| `e5` bogus enum value | **1** | `WARNING: erroneous pipeline: could not set property "mode" in element "pipewiresink" to "bogus"` | — |
| `e6` bogus caps value | **1** | `WARNING: erroneous pipeline: could not link audiotestsrc0 to fakesink0, audiotestsrc0 can't handle caps audio/x-raw, format=(string)BOGUSFMT` | — |
| `e7` caps mismatch (video caps) | **1** | same `can't handle caps` family | — |
| `e8` **negotiation failure at a real sink** (`F64LE ! pulsesink`) | **1** | `could not link audiotestsrc0 to pulsesink0, pulsesink0 can't handle caps audio/x-raw, format=(string)F64LE, rate=(int)48000, channels=(int)2` | — |
| `e9` incomplete pipeline | **1** | `ERROR: pipeline could not be constructed: syntax error.` | — |
| `e13` bad capsfilter | **1** | `WARNING: erroneous pipeline: could not link audiotestsrc0 to capsfilter0` | — |
| `e14` runtime, no downstream peer (`! wavenc` and stop) | **1** | `ERROR: … GstAudioTestSrc:audiotestsrc0: Internal data stream error.` + `streaming stopped, reason **not-linked (-1)**` | — |
| `e10` `pipewiresrc` garbage target, **no prop** | **255** | `ERROR: … GstPipeWireSrc:pipewiresrc0: stream error: target not found` | **0-byte file created** |
| `e11` `pulsesrc device=no_such` | **1** | `ERROR: … GstPulseSrc:pulsesrc0: Failed to connect stream: No such entity` | **0-byte file created** |
| `p8` `pulsesink server=unix:/nonexistent` | **255** | `Failed to connect: Connection refused` + `Failed to set pipeline to PAUSED.` | — |
| `e12` `gst-inspect-1.0 nosuchelement` | **255** | `No such element or plugin 'nosuchelement_xyz'` | — |

**Named classes.**

- **`gst_parse_refusal`** — rc=**1**, `WARNING: erroneous pipeline: …`, **no
  artifact created**. Covers missing element, unknown property, bad enum,
  caps mismatch, bad link. *Everything gst-launch can see at construction
  time lands here*, including caps negotiation, because gst-launch checks caps
  at link time — a "negotiation failure" in `gst-launch` terms is a **parse**
  refusal, not a runtime one.
- **`gst_state_change_refusal`** — rc=**255**, `ERROR: from element …` (+
  `Failed to set pipeline to PAUSED.`), **0-byte artifact already created**.
  This is the class of every *runtime* failure on this host (pipewire target
  miss, pulse server refused).
- **`gst_pulsesrc_refusal`** — rc=**1** with a **0-byte artifact** — a runtime
  failure wearing the parse rc. Same shape r77 measured; reproduced 3/3.
- **`gst_runtime_not_negotiated`** — rc=**1**, `Internal data stream error.` +
  `streaming stopped, reason **not-negotiated (-4)**`; reached in practice
  through `autoaudiosrc` (§6), not through a capsfilter (which fails earlier).

**vs the pw client classes (r78/r79/r80, cited not re-measured):** pw's
refusals are rc=1 + **44-byte** empty wav (`pw-record` bad target, `no_target_node`)
or rc=255 (`pwlink_enoent`); gst's are rc=1/**no file** (parse), rc=255/**0-byte
file** (state change) and rc=1/**0-byte file** (`pulsesrc`). **The rc and the
artifact shape both differ per client and per phase** — an arm must assert the
pair (rc, artifact shape), never rc alone.

---

## 6. Autodetect (`receipts/s7-auto.json`, 3 reps/leg)

| leg | rc | what appeared | note |
| --- | --- | --- | --- |
| `audiotestsrc ! audio/x-raw,… ! autoaudiosink` | 0 | pw node `gst-launch-1.0` `Stream/Output/Audio` linked to the default sink | autodetect picked the **pulse** backend |
| `autoaudiosrc ! audio/x-raw,… ! wavenc ! filesink` | **1** | no pw node; 0-byte file | stderr names the chosen element: `…GstAutoAudioSrc:autoaudiosrc0/GstPulseSrc:autoaudiosrc0-actual-src-puls: Failed to connect stream: No such entity`, then `Internal data stream error.` / `streaming stopped, reason not-negotiated (-4)` |
| `audiotestsrc ! … ! alsasink device=null` (control) | 0 | **no pw node** | the "no pw node" signature really does mean an ALSA path |

**`autoaudiosrc` is not a workaround for r77's "pulsesrc has no working
default on this host"** — autodetect selects `pulsesrc` and inherits its
refusal (rc=1 + 0-byte artifact). `autoaudiosink` works because the *sink*
direction has a default.

---

## 7. Named classes added this round

| class | signature | where |
| --- | --- | --- |
| `gst_target_two_key_write` | gst `target-object=` writes **both** `node.target` and `target.object` | pipewiresink/pipewiresrc node props |
| `gst_prop_beats_stream_props` | element property overwrites `stream-properties` (reverse of r78's `-P` law) | s11 |
| `client_name_renames_node` | `client-name=` renames the **node** (name/description/media.name), not the Client object | s5 / c3 |
| `client_properties_rename_client` | `client-properties=props,application.name=` renames the **Client** object only | s12 |
| `capture_stall_frozen` | target loss on a gst capture: file frozen at the last buffer, `wavenc_streaming` header, no error, process alive | t3/t4/t5/t6 |
| `on_disconnect_inert` | `on-disconnect=none\|error\|eos` identical under target-node loss | t4/t5 |
| `silent_device_fallback` | bogus/foreign `device=`/`target-object=` → **rc=0** + link to the *current default* (playback only) | s10, p2/p3/p5 |
| `device_direction_asymmetry` | same bogus name: sink rc=0+fallback, source rc=1 `No such entity` | p2 vs e11 |
| `gst_parse_refusal` / `gst_state_change_refusal` / `gst_pulsesrc_refusal` | rc=1/no file · rc=255/0 B · rc=1/0 B | §5 |
| `gst_unlinked_stall` | unlinked pw sink (stall) and unlinked gst capture (**0-byte** file) | s9/s6, c6 |
| `gst_autodetect_is_pulse` | `autoaudiosink`/`autoaudiosrc` resolve to the pulse elements; `autoaudiosrc` inherits the missing default | §6 |

---

## 8. Arm table (verbatim-armable rows + expected signature)

All rows measured ≥3× on this host. `NS` = a seat-owned `module-null-sink`
name; `DEF` = `pactl get-default-sink` **read live** (never hard-code it —
the host default moved twice during this session).

| # | arm | expected rc / stderr | expected topology | expected artifact signature |
| --- | --- | --- | --- | --- |
| A1 | `gst-inspect-1.0 pipewiresink \| grep -E 'Klass|Version'` | 0 | — | `Klass Sink/Audio/Video`, `Version 1.6.8` |
| A2 | `gst-inspect-1.0 openalsink` | **255** / `No such element or plugin` | — | — |
| A3 | `gst-launch-1.0 -q audiotestsrc wave=silence num-buffers=96 ! audio/x-raw,format=S16LE,rate=48000,channels=2 ! pipewiresink` | 0 | node `gst-launch-1.0` `Stream/Output/Audio` → **`<DEF>:playback_*`** | — |
| A4 | … `pipewiresink target-object=NS` | 0 | node props **`node.target=NS` and `target.object=NS`**; link → `NS:playback_*` | — |
| A5 | … `pipewiresink target-object=no_such` | **0** | props = `no_such`; link → **`<DEF>:playback_*`** | — (silent fallback row) |
| A6 | … `pipewiresink target-object=NS stream-properties=props,target.object=no_such` | 0 | both props **`NS`**; link → `NS` | — (precedence row) |
| A7 | `PIPEWIRE_NODE=NS gst-launch-1.0 -q … ! pipewiresink` | 0 | prop `target.object=NS`; link → `NS` | — |
| A8 | … `pipewiresink stream-properties=props,node.name=gst_x` | 0 | node.name `gst_x`, **description/media.name still `gst-launch-1.0`** | — |
| A9 | … `pipewiresink client-name=gst_x` | 0 | node.name **and** description **and** media.name `gst_x`; pw Client still `gst-launch-1.0` | — |
| A10 | … `pipewiresink client-properties=props,application.name=gst_app` | 0 | pw **Client** name `gst_app`; node.name unchanged | — |
| A11 | … `pipewiresink stream-properties=props,node.autoconnect=false` | **−9 (stalled; kill at wall cap)** | node prop `node.autoconnect="FALSE"` (string), **no links** | — |
| A12 | `gst-launch-1.0 -q pipewiresrc target-object=NS num-buffers=100 ! audio/x-raw,… ! wavenc ! filesink location=F` (no prop) | **255** / `stream error: target not found` | — | **F exists, 0 B** |
| A13 | A12 + `stream-properties=props,stream.capture.sink=true` | 0 | link `NS:monitor_* → gst-launch-1.0:input_*`; prop `stream.capture.sink="TRUE"` (string) | finalized wav, tone peak present |
| A14 | A13 with `target-object=NS.monitor` | 0 | link → **`<DEF>:monitor_*`** (fallback), **not** `NS` | — |
| A15 | A13 with `stream-properties=props,stream.capture.sink=true,node.target=NS` (no gst prop) | 0 | link → `NS:monitor_*` | tone captured |
| A16 | `gst-launch-1.0 -q audiotestsrc wave=silence num-buffers=96 ! audio/x-raw,… ! pulsesink device=NS` | 0 | prop `target.object=NS`; link → `NS:playback_*` | — |
| A17 | … `pulsesink device=no_such` | **0** | prop `target.object=no_such`; link → **`<DEF>:playback_*`** | — |
| A18 | `gst-launch-1.0 -q pulsesrc device=no_such num-buffers=4 ! audio/x-raw,… ! wavenc ! filesink location=F` | **1** / `Failed to connect stream: No such entity` | — | **F exists, 0 B** |
| A19 | `PULSE_SINK=NS gst-launch-1.0 -q … ! pulsesink` | 0 | prop `target.object=NS`; link → `NS` | — |
| A20 | A19 + `device=<DEF>` | 0 | link → `<DEF>` (**device wins**) | — |
| A21 | `gst-launch-1.0 -q … ! pulsesink server=unix:/nonexistent` | **255** / `Connection refused` + `Failed to set pipeline to PAUSED` | — | — |
| A22 | play into `NS` via `pipewiresink target-object=NS`, then `pactl unload-module <NS module>` | 0 (unload) | **re-link to `<DEF>:playback_*` within ≤0.2 s**, process alive, stderr empty | — |
| A23 | same with `pulsesink device=NS` | 0 | identical | — |
| A24 | capture from `NS` (A13), then unload the `NS` module | pipeline alive, **stderr empty** | links `{}` — **no re-link** | **file frozen** at the last buffer, header `wavenc_streaming` (`data` `0x7FFFF000`), unfinalized |
| A25 | `pw-record -P stream.capture.sink=true --target NS -n 1000000 F`, then unload the `NS` module | alive | **re-link to `<DEF>:monitor_*` within ≤0.2 s** | file keeps growing (≈187 KB/s measured; 192 nominal) |
| A26 | A24 with `on-disconnect=error` (or `=eos`) | identical to A24 | identical | identical |
| A27 | `gst-launch-1.0 -q nosuchelementsrc ! wavenc ! filesink location=F` | **1** / `WARNING: erroneous pipeline: no element …` | — | **F not created** |
| A28 | `gst-launch-1.0 -q audiotestsrc bogus-prop=42 num-buffers=4 ! fakesink` | **1** / `no property "bogus-prop" in element "audiotestsrc"` | — | — |
| A29 | `gst-launch-1.0 -q audiotestsrc num-buffers=4 ! audio/x-raw,format=F64LE,… ! pulsesink` | **1** / `pulsesink0 can't handle caps …F64LE` | — | — |
| A30 | `gst-launch-1.0 -q autoaudiosrc ! audio/x-raw,… ! wavenc ! filesink location=F` | **1** / `…GstPulseSrc…: Failed to connect stream: No such entity` + `not-negotiated (-4)` | — | F exists, 0 B |
| A31 | `gst-launch-1.0 -q audiotestsrc wave=silence num-buffers=48 ! audio/x-raw,… ! autoaudiosink` | 0 | pw node appears → **pulse backend** | — |
| A32 | `gst-launch-1.0 -q audiotestsrc wave=silence num-buffers=48 ! audio/x-raw,… ! alsasink device=null` | 0 | **no pw node** (ALSA path signature) | — |

---

## 9. Falsification list (what would prove each claim wrong)

1. **"`target-object=` writes both `node.target` and `target.object`"** — a
   `pw-dump` on a pipewiresink leg with `target-object=X` showing only one of
   the two keys (or a different key). *(§2.2; 3/3 here.)*
2. **"the gst property beats `stream-properties`"** — an s11-shaped leg that
   lands on `no_such` or whose props keep `target.object=no_such`.
3. **"`client-name=` renames the node, not the client"** — a `pw-dump` Client
   object whose name equals `client-name=` (or a node that keeps
   `gst-launch-1.0`).
4. **"a bogus playback device falls back silently"** — any `pulsesink
   device=<bogus>` or `pipewiresink target-object=<bogus>` leg with rc≠0, an
   empty stderr *and* no link (i.e. no fallback), or a link to a node other
   than the current default.
5. **"the sink/source asymmetry"** — a `pulsesrc device=<bogus>` that returns
   rc=0 + fallback, or a `pulsesink device=<bogus>` that returns rc=1
   `No such entity`.
6. **"gst capture does not re-link on target loss"** — a t3/t6 leg in which the
   `gst-launch-1.0:input_*` ports acquire any producer after the unload, or in
   which the file keeps growing. *(This is the round's most load-bearing new
   law; the t7 control proves the same host event re-links a `pw-record`.)*
7. **"`on-disconnect` is inert"** — a t4/t5 leg whose rc/stderr/artifact
   differs from t3. *(Also: a leg where the *peer* stream is closed rather than
   the target node destroyed may exercise the property — not tested.)*
8. **"the frozen artifact is silent"** — a t3 leg with non-empty stderr, or a
   file whose size still equals the byte cap.
9. **"parse refusals create no artifact"** — an e1/e3/e9 leg that leaves a file
   behind (even 0 bytes).
10. **"state-change refusals leave a 0-byte artifact"** — an e10 leg with no
    file, or with a non-zero file.
11. **"`autoaudiosink` picks the pulse path"** — an a0 leg with no pw node
    (that would mean it picked `alsasink`), or with a pw node *and* rc≠0.
12. **"the element lattice is stable"** — any of the 26 elements changing rc,
    klass, plugin or version across 3 reps (all stable in this window).
13. **"the host default sink is SPDIF"** — it is *not* a constant: a foreign
    lane moved it to `r78_def_sink_3071748` mid-session and back (§10). Any arm
    that hard-codes the fallback node name is unsound.

---

## 10. Contention ledger (mandatory)

**Foreign state at entry** (`receipts/s0-baseline.json`, 05:24:59Z): 13 nodes —
4 ALSA sinks/sources, `Dummy-Driver`, `Freewheel-Driver`, `Midi-Bridge`,
`bluez_midi.server`, plus sibling-owned null sinks `r78_prop_a_3048419` /
`r78_prop_b_3048419`. Default sink `…HiFi__SPDIF__sink`, default source
`…HiFi__Line__source`. Clients: WirePlumber (33, 45), xdg-desktop-portal (34),
pipewire (32), waybar (36), plus the sibling's `pw-cat` streams.

**A sibling lane was live for the entire window**:
`python3 corpus/fixtures/measure_audio.py --probe-capture-r78` (pid **3048419**
at entry, restarted as **3071748** at 02:32:56 local). Its stream/sink names
observed in this seat's receipts: `r78_prop_a/b_*`, `r78_fix_sink_*`,
`r78_def_sink_*`, `r78_loss_sink_*`, `r78_cap_sink_*`, `r78segv_control`,
`r78fix_feed`, `r78zeros_*`, `r78lat_*` (latency battery), `parec`, `r78loss_ul_*`.

### Interference events

1. **Not caused by this seat — the host default sink moved during the window.**
   At ≈05:35Z (`p10_move_mid_leg` rep 0, t=3.51 s) a stream that this seat had
   moved to `…SPDIF__sink` was observed re-linked to **`r78_def_sink_3071748`**
   — a sibling-owned null sink that was also the host default at that moment
   (`pactl get-default-sink` → `r78_def_sink_3071748` at 05:36Z). By the exit
   snapshot (05:37:29Z) the default was `…SPDIF__sink` again. **This is not
   attributable to any leg of this seat** (no `set-default-*` was ever issued
   here) and it is recorded rather than repaired. Consequence: every fallback
   claim in this report is pinned to *"the default sink at that moment"*, and
   §8's arms must read the default live.
2. **Caused by this seat (disclosed, content-free):** the target-loss legs
   (t1, t2, t7 — 9 of 15 legs) deliberately route a **`audiotestsrc
   wave=silence`** stream into the shared default sink for ~3 s after each
   unload, and the autoconnecting identity legs (A3-shaped) do the same. The
   payload is **digital silence**, so no tone is injected into any concurrent
   recording — but the *stream nodes* are visible in other lanes' `pw-link -l`
   witnesses.
3. **Content anchor was seat-local:** the 1 kHz/8192 tone played only into
   `gst_r81_ns`; it was killed before stage 5 (target loss), so no tone could
   reach the shared default sink when the null sink died.
4. **No by-name unload, ever.** Every `pactl unload-module` used an index that
   was re-read from `pactl list short modules` and matched against
   `gst_r81_ns` immediately before the call (indices are recycled — LIFO per
   r80 §3.1 — and the same index later belonged to the sibling's
   `r78_fix_sink_3071748`). No foreign module, node or link was touched.
5. **No `--probe-*` of `measure_audio.py` was ever run**; the file was never
   imported or executed by this seat.

**Exit state** (`receipts/s0-final.json`, 05:37:29Z): no `gst_r81_*` node, no
`gst_r81_*` module, no `gst-launch` process; pulse module list back to the four
static modules plus the sibling's `module-null-sink sink_name=r78_fix_sink_*`;
links = the sibling's three. Scratch 7.0 MB (tone deleted; receipts kept).

---

## 11. Receipts index + remaining unknowns

**Receipts** (all under `corpus/live/r81-scout/`; per-leg dirs under
`runs/<stage>/<leg>_r<rep>/` with `cmd.txt`, `stderr.txt`, `receipt.json`):

| artifact | sha256 |
| --- | --- |
| `receipts/s0-baseline.json` | `c651fd28d987b100aa5d98d3c2af69b0a8c00e23f4bec6ca8bee8e0ea0c47d6d` |
| `receipts/s0-final.json` | `6cb09bb4cf636a6d0e1d026792d947c65cb15b2910b2347b99b1c7fee9b34f15` |
| `receipts/s1-inventory.json` | `fd1549cc207c7ab95a6d664e9f4fa9ae1c942de896e502e762ab3702196bb667` |
| `receipts/s2-pw-sink.json` | `052adaceab95781f7ed4d149f53e3de468d8ba500e49f1a21ad418579e6e23cf` |
| `receipts/s3-pw-src.json` | `b79040dac009ee82105cd1eeae26984957398af452572ca51a04b81eae6fa89a` |
| `receipts/s4-pulse.json` | `6356ff320720a9bb3b3b615b00b37a3035c55f62e53edef05509e70334b2edb0` |
| `receipts/s5-loss.json` | `3985821d151d85f6e676fe9856c19fa42dee10255260af469b496791aa5d401a` |
| `receipts/s6-errors.json` | `eb05e4f394c9e197c9a5cd441568885e1c1b88ac2edddb420f7d5b50d7092995` |
| `receipts/s7-auto.json` | `dea4465b765111cdf0780eb906422d511aa399e049e276a2c6cfbfc78b9e078b` |
| `r81_probe.py` (harness) | `1a9c055393d8acbcb6f53ca6eac4e75b7fb334301c914743318675ee5a45c7ff` |

**Harness notes (disclosed).** Three leg-shape bugs were found and fixed
before the reported runs: a trailing `!` in the s0_bare pipeline, capture
properties placed after `filesink` (stage 3 and stage 5), and
`pactl list short sink-inputs` matching on a *sink name* when the column is a
**sink serial** (stage 4's `p10`). The affected stages were re-run in full
(`rm -rf runs/<stage>` first) or, where only the content witness was lost
(c7/c8/c9 ran after the 60 s tone had ended), re-run by `rerun.py` with a fresh
tone; the receipts referenced above are the valid executions. `analyze.py`
crashed once on a `pw-dump` that returned no `links` key under load — the
sample is present in the raw receipt and the analyzer was made tolerant.

**Remaining unknowns (honest edges).**

- **The mechanism is not read.** Everything here is measured through
  `gst-launch`, `pw-dump`, `pactl` and `pw-link`; `gstpipewiresrc.c`,
  `gstpipewiresink.c` and `pw_stream_connect` were not consulted. In
  particular *why* `pipewiresrc` stalls while `pw-record` re-links on the same
  host event is characterised, not explained (the t6 leg rules out the stale
  `node.target` prop as the cause).
- **`on-disconnect` was only tested against target-node destruction**, not
  against a peer stream that closes itself (e.g. the producer exiting while
  the sink node lives). The property may be live on that path.
- **The "`device=` target alive + host default moves" cell was never
  deliberately exercised** — it would require `pactl set-default-sink`, which
  would perturb every concurrent lane (r78 declined the same test). One
  accidental observation exists (§10 item 1) and is unattributed.
- **`PULSE_SINK`/`PIPEWIRE_NODE` were tested only as the client-local default
  /target**; the `PIPEWIRE_REMOTE`-style knobs are untouched.
- **`num-buffers` is still not a frame bound** for the pipe/pulse sources (r77
  §2); the 100-buffer capture legs came back as 204 800 frames here (2 048
  frames/buffer) and 102 400 in c4/c7/c8 (1 024) — the r77 variance reproduces
  and is why every capture leg is wall+byte capped.
- **The element lattice is a this-host pin** (no `-bad`, no `-ugly`); a host
  with `gst-plugins-bad` may add `pipewire`-adjacent or `openal` elements.
- **The default sink moved under this seat once** (§10). Nothing in this
  report depends on it *not* moving — but any future arm must read it live.
