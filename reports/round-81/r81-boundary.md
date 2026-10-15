# R81 BOUNDARY — the honest edges of the r81 gst↔pipewire claims, measured

**Seat:** AUDIO lane r81 BOUNDARY (bounded empirical probe; respawn — the prior
seat had no exec capability). **Host** `plazir27`, measured **2026-10-15
17:03:47Z → 17:21:19Z** (host local UTC−3). Repo
`~/Projects/shokunin/audio-shokunin` @ HEAD `15c6a35`.

**Scope.** Work the r81 scout's §11 "remaining unknowns" and the edges of its
pinned claims with *real* `gst-launch-1.0` / `pactl` / `pw-dump` legs. Every
leg is bounded three ways — element bound (`num-buffers`) where it exists, a
wall cap, and a byte cap checked **in the same loop that owns the process
group** (no watchdog thread; the r77 flood lesson). Producer processes are
separate process groups owned and killed by that same loop.

**Isolation.** Seat-owned names only: nodes/streams `gst_r81_bnd_*`, seat-owned
null sink `gst_r81_bndns`. **No `pactl set-default-sink` / `set-default-source`
was ever issued** (the host default was read live in every stage; it never
moved during this window). Every `pactl unload-module` used an index re-read
from `pactl list short modules` and matched against the seat-owned name
immediately before the call, and — after the discipline bug in §6.1 was found —
every unload also records the live seat-node count before/after. **No tracked
file was written and nothing was committed**; all receipts are under
`corpus/live/r81-boundary/` (untracked). `corpus/fixtures/measure_audio.py`
belongs to a sibling lane and was never read, imported or executed here.

**Labels.** **[O]** = measured by this seat, receipt-backed. **[I]** = inferred
from this seat's measurements plus another seat's recorded receipt. **[?]** =
not measured, or mechanism unread.

**Headline:** the scout's *freeze* law survives at full strength (and is now
byte-reproducible), but three of its edges move: `on-disconnect` is inert
against a **true peer-stream death** too, the capture side **does** link
directly to a non-sink stream node, and `num-buffers` **is** an exact frame
bound on the pulse record path. Two new laws are added: the frozen artifact
lands exactly on a **quantum** boundary, and two same-name sinks can be handed
to two clients that land on **different** nodes.

---

## 0. Headline table

| # | edge probed | verdict | the single sharpest measured fact |
| --- | --- | --- | --- |
| 1 | `on-disconnect` vs a *peer stream that closes itself* (scout §11, falsifier #7) | **CLOSED — inert** | capture linked **directly** to a producer stream node: producer SIGKILLed at 1.5 s → file frozen at **274 476 B**, `on-disconnect=none\|error\|eos` byte-identical, **stderr empty**, process alive (9/9 clean reps) |
| 2 | producer exits while the **sink node lives** | **NO DISCONNECT AT ALL** | producer EOS at 1.28 s and producer SIGKILL at 1.5 s both leave the capture **growing for the whole window** (901 164 B, 6/6) — the sink monitor keeps feeding silence |
| 3 | `PIPEWIRE_REMOTE` / `PIPEWIRE_NODE` / `PIPEWIRE_PROPS` | **HONORED, DECISIVE** | `PIPEWIRE_REMOTE=bogus` → **rc=255** on playback *and* capture (`Failed to connect`, `gstpipewirestream.c(136)`), and a valid `PIPEWIRE_NODE` does **not** rescue it (9/9) — no fallback to the default socket |
| 4 | env-vector precedence | **NEW LAW** | `PIPEWIRE_PROPS={node.target=NS}` + `PIPEWIRE_NODE=no_such` → node carries both keys and links to the **default sink**: `target.object` outranks `node.target` (3/3) |
| 5 | element prop vs `stream-properties` on the **capture** side | **SAME LAW + A SPLIT** | precedence is the playback law (element prop overwrites both keys, 9/9) **but** the element prop alone is *not* enough on capture: `target-object=NS` without `stream.capture.sink` → **rc=255 target not found, 0-byte artifact** (3/3) |
| 6 | `pulsesrc device=` variants the scout did not try | **STRICT SET, MEASURED** | `device=<NS>.monitor` (a real source name) → rc=0 3 840 frames; `device=<sink name>`, `device=no_such`, **`device=` (empty)** → rc=1 `No such entity`; `PULSE_SOURCE` is honored and **loses to `device=`** |
| 7 | `num-buffers` on the pulse record path | **SCOUT §11 PHRASING FALSIFIED** | `pulsesrc`: 8 → **3 840** = 8·480, 20 → **9 600** = 20·480, 200 → **96 000** = 200·480 frames, and with `blocksize=4096` → **8 192** = 8·1 024 (9/9) — an *exact* frame bound |
| 8 | frozen file at buffer granularity | **NEW LAW: quantum grid** | every 48 kHz freeze is `44 + k·4096` B = `k·1024` frames (204 844 = 50 quanta; 274 476 = 67; 483 372 = 118), and `PIPEWIRE_QUANTUM=256/2048` moves the grid with it (198 700 = 194·256 frames; 213 036 = 26·2048) |
| 9 | freeze before the first write batch | **0-BYTE EDGE** | unload at 0.2 s (first batch lands ≈0.35 s) → **0-byte artifact, no header at all**, process alive, rc=−9 (3/3) |
| 10 | duplicate `sink_name` | **NEW HAZARD, RECEIPTED** | two live `gst_r81_bndns` modules: the capture and the producer resolved the *same name* to **different nodes**; unloading the first index froze the capture in 2/3 rounds and not in the 3rd |
| 11 | scout's frozen-header claim | **CORRECTED** | raw bytes: RIFF size `0x7FFF0024`, data size `0x7FFF0000` — **not** `0x7FFFF000`; three independent runs produced a **byte-identical** 204 844-byte artifact (sha256 `6f2fe9c2…`) |

---

## 1. `on-disconnect` vs a peer stream that closes itself

The scout tested the enum only against *target-node destruction*. Three
different peer-death shapes were measured here, all with the seat's own null
sink `gst_r81_bndns` verified live at the instant of the event
(`nodes_before=1 → nodes_after=0` recorded in the receipt).

### 1.1 Producer exits, **sink node lives** — the capture never notices **[O]**

`a_prod_eos` — producer = `audiotestsrc wave=sine freq=1000 num-buffers=60
blocksize=4096 ! pipewiresink target-object=NS`, ends **by itself** (EOS) at
t≈1.28 s (`rc=0`). Capture = `pipewiresrc target-object=NS
stream-properties=props,stream.capture.sink=true num-buffers=1000
on-disconnect=error ! … ! wavenc ! filesink`.

| leg | producer end | capture file at wall cap | links after the producer died |
| --- | --- | --- | --- |
| `a_prod_eos` ×3 | rc=0 at 1.275/1.300/1.275 s | **901 164 B**, still growing | `gst_r81_bndns:monitor_* → gst_r81_bnd_cap:input_*` **unchanged** |
| `b_prod_kill` ×3 | SIGKILL at 1.50–1.51 s | **901 164 B**, still growing | same, unchanged |

901 164 B = 44 + 220·4096 = 225 280 frames ≈ 4.69 s of content in a 5.0 s
window — i.e. the capture ran at the nominal 48 kHz rate the whole time. The
tone is present in the file (`peak=26213`) up to the producer's death and
digital silence after it.

**Law [O]:** *a producer stream exiting — cleanly or by SIGKILL — is invisible
to a `pipewiresrc` capturing that sink's monitor. The monitor port keeps
producing silence; there is no disconnect event, no EOS, no error, and the file
does not stop growing.* The scout's freeze law is therefore **specific to
target-node destruction**, not to "the other end went away".

### 1.2 The true disconnect: capture linked **directly to a stream node** **[O]**

`stream.capture.sink=false` (or the prop absent) makes `pipewiresrc` resolve the
target as a **stream/source with output ports**, not as a sink:

```
gst_r81_bnd_prod:output_FL -> gst_r81_bnd_cap:input_FL      (r0/r1/r2, 3/3)
gst_r81_bnd_prod:output_FR -> gst_r81_bnd_cap:input_FR
```

Producer SIGKILLed at 1.5 s → the link's **peer node is destroyed**. Result:

| leg | enum | rc | artifact | stderr | process |
| --- | --- | --- | --- | --- | --- |
| `e_direct_false` ×3 | `error` | −9 (wall cap) | **274 476 B** frozen, `wavenc_streaming` | **empty** | alive |
| `e_direct_none` (2 clean reps) | `none` | −9 | 274 476 B frozen | empty | alive |
| `e_direct_eos` ×3 | `eos` | −9 | 274 476 B frozen | empty | alive |
| `e_direct_noprop` (2 clean reps) | `error` | −9 | 274 476 B frozen | empty | alive |

Freeze instant: the last size change is at **t=1.450–1.455 s** in every rep —
i.e. at the producer's death, not at the wall cap. The artifact carries the
producer's tone (`peak=26213`) and then nothing.

**Law [O]:** `on-disconnect` is inert on a **true peer destruction** as well as
on target-node destruction. **15 clean freeze reps** (3+3+3+3+3 across
`error`/`none`/`eos` and prop/no-prop shapes) are byte-identical in outcome.
The scout's falsifier #7 ("a leg where the *peer* stream is closed rather than
the target node destroyed may exercise the property") is **answered: no**.

### 1.3 The frozen capture does not resume when the target **name** returns **[O]**

`h1_freeze_then_reload` (×3): unload NS at 1.2 s → freeze; at **2.6 s** a *new*
`module-null-sink` with the **same `sink_name`** is loaded (verified:
`nodes_after_load=1`, new node serial). Result: the file stays at **204 844 B**
for the rest of the window in all 3 reps, and the capture node remains
**linkless** (`NO-SEAT-LINKS`) while the reloaded sink exists.

`e_direct_return` (1 clean rep of 3): producer killed at 1.2 s → freeze at
204 844 B; a new producer with the **same `client-name`** starts at 2.4 s →
capture still frozen, no re-link.

**Law [O]:** *a frozen gst capture never re-links — not when the same-name
target node returns, not when a same-name producer stream returns.* Recovery
requires a new client process. (3 + 1 clean reps; the other 2 reps of
`e_direct_return` lost the connect-time race of §3.4.)

---

## 2. `PIPEWIRE_REMOTE` / `PIPEWIRE_NODE` / `PIPEWIRE_PROPS`

The scout tested `PIPEWIRE_NODE`/`PIPEWIRE_PROPS` on playback only and left the
`PIPEWIRE_REMOTE`-style knobs untouched (§11). All rows 3/3.

| leg | env | direction | rc | stderr (verbatim head) | artifact | where it linked |
| --- | --- | --- | --- | --- | --- | --- |
| `p1_remote_ok` | `PIPEWIRE_REMOTE=pipewire-0` | playback | 0 | — | — | default sink |
| `p2_remote_bogus` | `PIPEWIRE_REMOTE=bogus_r81_bnd` | playback | **255** | `Failed to connect` + `…/pipewire/src/gst/gstpipewirestream.c(136): gst_pipewire_stream_open ()` + `pipeline doesn't want to preroll` | — | none |
| `c3_remote_bogus` | `PIPEWIRE_REMOTE=bogus` | capture | **255** | same, `GstPipeWireSrc` | **0-byte file created** | none |
| `p3_remote_bogus_node` | `PIPEWIRE_REMOTE=bogus` + `PIPEWIRE_NODE=NS` | playback | **255** | same | — | none — **the remote knob is decisive** |
| `c1_envnode` | `PIPEWIRE_NODE=NS` + capture prop | capture | −9 | empty | grows (silence) | **`gst_r81_bndns:monitor_* → cap`** |
| `c2_envnode_mon` | `PIPEWIRE_NODE=NS.monitor` + prop | capture | −9 | empty | grows | **default sink monitor** (fallback) |
| `p5_envnode` | `PIPEWIRE_NODE=NS` | playback | 0 | — | — | `gst_r81_bndns` |
| `p4_props_vs_node` | `PIPEWIRE_PROPS={node.target=NS}` + `PIPEWIRE_NODE=no_such_r81_bnd` | playback | 0 | — | — | **default sink** |

**Laws [O].**

- **`PIPEWIRE_REMOTE` is honored by the gst pipewire elements** — the connection
  is opened against the named socket, and a miss is a hard **rc=255**
  (`state_change_refusal` class), not a silent fallback to `pipewire-0`. It is
  symmetric across playback and capture, and it is **not** rescued by a valid
  `PIPEWIRE_NODE` (the remote is chosen before the target is resolved).
- **`PIPEWIRE_NODE` works on the capture side too** (new — the scout only had
  playback), and it lands as **`target.object`** exactly like the playback row.
- **The `.monitor` suffix fails in the env vector as well** — `PIPEWIRE_NODE=NS.monitor`
  resolves to the *default* sink's monitor, the same row the element property
  produces (§3, `f6`).
- **NEW LAW — `target.object` outranks `node.target` when both are present.**
  `PIPEWIRE_PROPS={node.target=NS}` + `PIPEWIRE_NODE=no_such` leaves **both**
  keys on the node (`node.target=gst_r81_bndns`, `target.object=no_such_r81_bnd`)
  and the stream links to the **default sink** — the missing `target.object`
  wins and falls back. This is the piece that explains the whole lattice:
  `node.target` alone routes (f4), but `target.object` decides whenever it is
  present, and the *element property* writes both keys at once — which is why
  the element property beats everything.

---

## 3. Capture-side prop precedence: same law, plus a real split

All rows 3/3 (`target-object=NS` + `stream.capture.sink=true` unless noted).

| leg | element prop | `stream-properties` | node props (pw-dump) | link |
| --- | --- | --- | --- | --- |
| `f1_prop_beats_sp` | `target-object=NS` | `target.object=no_such` | **both = NS** | **`NS:monitor_* → cap`** |
| `f2_sp_vs_bogus_prop` | `target-object=no_such` | `target.object=NS` | **both = no_such** | **default sink monitor** (silent fallback, keeps growing) |
| `f3_prop_vs_sp_nodetarget` | `target-object=NS` | `node.target=no_such` | **both = NS** | `NS:monitor_* → cap` |
| `f4_sp_nodetarget_only` | — | `node.target=NS` | `node.target=NS` | `NS:monitor_* → cap` |
| `f5_prop_no_capsink` | `target-object=NS` | — | — | **rc=255 `stream error: target not found`, 0-byte artifact** |
| `f6_monitor_suffix` | `target-object=NS.monitor` | — | `target.object=NS.monitor` | **default sink monitor** |

**Laws [O].**

- **Precedence is the playback law, not a split**: the element property
  overwrites the `stream-properties` key(s) — both `target.object` and
  `node.target` — and therefore wins (9/9 across f1/f2/f3). The scout's
  `gst_prop_beats_stream_props` class extends to the capture side.
- **The split is elsewhere — sufficiency.** On playback the element property
  alone is enough; on capture it is **not**: `target-object=NS` without
  `stream.capture.sink=true` is **rc=255 `target not found` + 0-byte artifact**
  (3/3, scout's `c0` reproduced on the seat's own sink). The capture prop is
  what selects *"resolve the target as a sink and use its monitor"*.
- **The prop's value selects the resolution family [O]**:
  `stream.capture.sink=false` (or absent) → the target is resolved as a
  **stream/source** and linked **directly to its output ports** (§1.2, 6 clean
  reps); `stream.capture.sink=true` against a *stream* target → the target is
  not a sink, so the client **silently falls back to the default sink's
  monitor** and keeps growing (`e_direct_true` 3/3, `peak=0`, link
  `…SPDIF__sink:monitor_* → cap`).
- **A missing/bogus target with `capture.sink=true` falls back silently and
  permanently** (`f2`, `f6`, and the deliberate `h2b_missing_target_fallback`
  cell 3/3: 708 652 / 708 652 / 716 844 B over a 4 s window). In the `h2b`
  cell the *producer* also fell back (playback law) to the same default sink,
  so the capture recorded the producer's tone through the default sink's
  monitor (`peak=32768`) — a clean demonstration that **two target-miss
  fallbacks can rendezvous on the default sink**.

### 3.4 Target resolution is a one-shot lookup at stream open — the race **[O]**

When the capture and its target stream start in the same instant, the capture
sometimes loses:

| leg | reps clean | reps rc=255 `target not found` |
| --- | --- | --- |
| `e_direct_false` | 3 | 0 |
| `e_direct_eos` | 3 | 0 |
| `e_direct_noprop` | 2 | 1 |
| `e_direct_none` | 2 | 1 |
| `e_direct_return` | 1 | 2 |

**4 of 12** "capture targets a *stream* created by a peer process" legs failed
with rc=255 + a 0-byte artifact because the peer's node did not exist yet at
`gst_pipewire_stream_open` time. The sink-target legs (a module-created sink,
9/9) never lost the race. **A fixture arm that links a gst capture to a
peer-created stream must sequence the producer first (or pre-create the target);
`pipewiresrc` does not wait for a target that appears later.** This is a
practical trap for any "capture from a live stream" arm.

---

## 4. `pulsesrc device=` — the record-side strictness lattice

All rows 3/3 unless noted; artifact shape read from the file *after* the process
exited (fast failures finish in 12–19 ms, before any size sample).

| leg | device / env | rc | stderr class | artifact |
| --- | --- | --- | --- | --- |
| `g1_sinkname` | `device=NS` (a **sink**) | **1** | `No such entity` (`pulsesrc.c(1622) gst_pulsesrc_prepare`) | **0 B** |
| `g3_bogus` | `device=no_such_r81_bnd` | **1** | same | **0 B** (scout's row reproduced) |
| `g4_empty_device` | **`device=`** + `PULSE_SOURCE=NS.monitor` | **1** | same | **0 B** |
| `g6_device_vs_env` | `device=no_such` + `PULSE_SOURCE=NS.monitor` | **1** | same | 0 B ×2, **44 B placeholder ×1** |
| `g2_monitor_name` | `device=NS.monitor` (a **real source**) | **0** | — | 15 404 B, finalized, **3 840 frames**, peak 0 |
| `g5_env_only` | bare + `PULSE_SOURCE=NS.monitor` | **0** | — | 15 404 B, 3 840 frames |
| `g7_monitor_sourceprop` | `device=NS.monitor` + `PULSE_SOURCE=no_such` | **0** | — | 15 404 B, 3 840 frames |
| `g8_bad_server` | `device=NS.monitor` + `server=unix:/nonexistent` | **255** | `Failed to connect: Connection refused` (`pulsesrc.c(1016) gst_pulsesrc_open`) | **0 B** |

**Laws [O].**

- **The record path is strict about *existence*, not about direction**: a real
  source name is accepted (`NS.monitor` — a null-sink monitor — works and
  yields silence), while a sink name, a garbage name and the **empty string**
  are all refused with rc=1 `No such entity`.
- **`device=` (empty) is a literal name, not "use the default"** — with a valid
  `PULSE_SOURCE` in the environment it still refuses (3/3). Pulse's "empty means
  default" idiom does not survive the gst element.
- **`PULSE_SOURCE` is honored on the record side** (new — the scout left it
  untested) and **`device=` beats it** (mirror of the playback
  `device=`-beats-`PULSE_SINK` law).
- **Two rc classes with the same 0-byte artifact**: entity resolution → **rc=1**
  (`gst_pulsesrc_refusal`, the scout's class), server connect → **rc=255**
  (`state_change_refusal`). The scout's class list gains a member.
- **Artifact-shape caveat [O]:** the rc=1 artifact is *usually* 0 bytes, but
  **one of nine** refusal reps (`g6` r1) produced a **44-byte streaming
  placeholder** (`riff=wavenc_streaming`, data size `0x7FFF0000`) instead. The
  artifact shape is a race between `wavenc`'s header write and the failure — an
  arm must accept {0 B, 44 B} for this class, not pin 0 B.

### 4.1 `num-buffers` **is** an exact frame bound on the pulse record path **[O]**

| leg | num-buffers | knob | artifact frames | per buffer |
| --- | --- | --- | --- | --- |
| `g2/g5/g7` | 8 | default | **3 840** | **480** |
| `g9_numbuf_20` | 20 | default | **9 600** | **480** |
| `g9_numbuf_200` | 200 | default | **96 000** | **480** |
| `g10_blocksize_4096` | 8 | `blocksize=4096` | **8 192** | **1 024** |

All 9/9, byte-exact (`bytes = 44 + frames·4`), rc=0, `finalized`, and
reproducible to the byte across reps. The 480-frame default fragment is exactly
what r77 §2 measured for the same element (24 000 frames / 50 buffers). **The
r81 scout's §11 line — "`num-buffers` is still not a frame bound for the
pipe/pulse sources" — is falsified for the pulse record path as written**: with
default knobs the bound is exact and stable; `blocksize` moves the *per-buffer*
size (r77's law) rather than destroying the bound. The honest formulation is:
`frames = num-buffers × (blocksize / frame_bytes)`, with the pipewire **source**
being the element where the per-buffer size is session-dependent (§5.1).

---

## 5. The frozen artifact at buffer granularity

### 5.1 Exact freeze sizes and the quantum grid **[O]**

`PIPEWIRE_QUANTUM` is a **client-local** env knob (it does not touch the shared
graph), so it was usable as a probe. Freeze sizes below are from clean reps
(`nodes_before=1 → nodes_after=0` at the unload, 3/3 each unless noted):

| leg | caps | quantum | frozen bytes | = 44 + | frames | in quanta |
| --- | --- | --- | --- | --- | --- | --- |
| `h2/h7/h1`, `c`, `d` | 48 k stereo s16 | default | **204 844** | 50·4096 | 51 200 | **50 × 1024** |
| `e_direct_*` | 48 k stereo s16 | default | **274 476** | 67·4096 | 68 608 | **67 × 1024** |
| `p6 r1` | 48 k stereo s16 | default | **483 372** | 118·4096 | 120 832 | **118 × 1024** |
| `h6_quantum_256` | 48 k stereo s16 | `256/48000` | **198 700** | 194·1024 | 49 664 | **194 × 256** |
| `h6_quantum_2048` | 48 k stereo s16 | `2048/48000` | **213 036** | 26·8192 | 53 248 | **26 × 2048** |
| `h5_44k_mono` | 44.1 k mono s16 | default | **65 844** | 65 800 | 32 900 | **35 × 940** (graph-domain) |
| `h4` (unload at 0.2 s) | 48 k stereo s16 | default | **0** | — | — | **before the first batch** |

**Laws [O].**

- **The freeze lands exactly on a whole number of graph quanta.** With the
  default quantum (1024 frames) every 48 kHz freeze is `44 + k·4096` bytes;
  `PIPEWIRE_QUANTUM=256` moves the grid to `44 + k·1024` bytes (194 quanta) and
  `=2048` to `44 + k·8192` (26 quanta). The partially-filled quantum in flight
  is **never written**: the artifact always ends on the grid.
- **The 44.1 kHz mono client is aligned in the *graph* domain, not the client
  domain**: 32 900 mono frames = 35 × 940 (the 44.1 kHz image of a 1024-frame
  48 kHz quantum). Resampling moves the client-side count off a power of two
  but not off the quantum grid. [?] the exact resampler rounding (940 vs the
  ideal 940.8) was not investigated.
- **The file grows in batches, not per quantum**: the stat-visible steps are
  `44+16·4096`, then `17·4096` (occasionally `18·4096`) at the default quantum,
  `65·1024` at quantum 256 and `9·8192` at quantum 2048 — i.e. **16–18 quanta
  (≈0.35–0.38 s of audio) per write batch**. Consequence: the artifact's
  *content* lags wall time by up to one batch, and a freeze inside the first
  batch writes nothing at all.
- **`num-buffers` on the pipewire source is exact once the per-buffer size is
  known**: `h3` (num-buffers=20, no unload) → rc=0, `finalized`,
  **81 964 B = 44 + 20·4096 = 20 480 frames = 20 × 1024** (3/3, byte-identical).
  The per-buffer size in *this* session is 1024 frames; the scout's session saw
  2 048 and r77 saw both — so the *frame* count is `num-buffers × quantum`
  (quantum 1024 or 2048 here), and the honest bound is
  `num-buffers × quantum`, not a raw frame count.
- **The 0-byte edge [O]:** `h4` (num-buffers=20, target unloaded at 0.205 s —
  *before* the first write batch) yields a **0-byte artifact with no header at
  all**, rc=−9, process alive, 3/3. Same freeze law, different artifact shape:
  the file's *shape* is decided by whether the first batch ever landed.

### 5.2 The raw frozen header, and a correction to the scout **[O]**

Three independent `h7` runs produced a **byte-identical** artifact:
`artifacts/h7_frozen_r0/r1/r2.wav`, 204 844 B each, sha256
`6f2fe9c21f27db170a8e22d8712c292c3eabf892f2e4b256249b9b6b3d917fbb`.

First 44 bytes (hex):
`52494646 2400ff7f 57415645 666d7420 10000000 01000200 80bb0000 00ee0200 00040010 64617461 0000ff7f`

| field | bytes | value |
| --- | --- | --- |
| RIFF size | `2400ff7f` | **0x7FFF0024** = 2 147 418 148 |
| data size | `0000ff7f` | **0x7FFF0000** = 2 147 418 112 |

The scout's §4.2/§8 reported the header as `data` field **`0x7FFFF000`** — that
is a digit transposition. The measured pair is mutually consistent
(`riff = data + 36`, the 36 bytes of `WAVE`+`fmt `+`data` header), and the
placeholder implies a bogus frame count (536 854 528) — **the real frame count
is always `(bytes − 44) / frame_bytes`**.

---

## 6. Duplicate `sink_name` — and the two contaminated passes, disclosed

### 6.1 The discipline bug (found, fixed, superseded) **[O]**

The first two `p5` passes **loaded a new `module-null-sink sink_name=NS` once
per leg *group* while each *rep* unloaded it**, so reps after the first ran
against **zero** targets (the "no freeze" rows: file growing at 190 KB/s with a
live tone) and some runs carried **two live same-name modules** (the "no freeze
with the link still present" rows). Both passes were deleted and the stage was
re-run with `ensure_single_ns()` executed **inside every rep**, with
`nodes_before/nodes_after` recorded on every unload. All numbers in §5 come
from the corrected pass (3/3, byte-identical). **Any probe that unloads a
module inside a rep loop must re-create the target inside that loop and must
count live nodes, not modules, before and after** — the module index alone is
not evidence of what the client is linked to.

### 6.2 The duplicate-name law **[O]** (`receipts/s6-dupname.json`)

Two live modules with the identical `sink_name=gst_r81_bndns`, two live nodes
with the identical `node.name` (r0: id 121 serial 17138, id 132 serial 17128),
then the **first** index is unloaded at 1.2 s and the survivor at 2.8 s:

| round | first_idx → second_idx | after unload #1 | capture behaviour | who was on which node |
| --- | --- | --- | --- | --- |
| r0 | 536870920 → 536870921 | nodes 2→1 | **froze at 204 844 B** | producer on **serial 17138** (survivor); capture on the **destroyed** node |
| r1 | 536870919 → 536870921 | nodes 2→1 | **kept growing** (froze only after unload #2, 483 372 B) | producer **and** capture both on **serial 17249** (survivor) |
| r2 | 536870919 → 536870920 | nodes 2→1 | **froze at 204 844 B** | producer on **serial 17389** (survivor); capture on the **destroyed** node |

**Laws [O].**

- **Same-name null sinks coexist** (two modules, two nodes, identical
  `node.name`), and the r80 B2 hazard class is real *across the pw client
  boundary*: unloading "the module whose name matches" is **not** the same as
  unloading the node the client is using.
- **Name resolution for a duplicated target is nondeterministic** — across three
  rounds the capture landed on the first-index node twice and on the
  second-index node once. In r0 the producer and the capture resolved the
  **same name to different nodes**.
- **`pw-dump` node counting (not the `pactl` module list) is the only safe
  liveness check** for a name-targeted teardown; the module index is recycled
  (here: `536870916` was reused three times within one stage).

---

## 7. Named classes added this round

| class | signature | where |
| --- | --- | --- |
| `on_disconnect_inert_true_peer` | peer **stream** destroyed (not just the target node): frozen artifact, empty stderr, `none\|error\|eos` identical | §1.2, 9 clean reps |
| `peer_exit_invisible_on_monitor` | producer EOS/SIGKILL while the sink node lives: capture keeps growing, no event at all | §1.1, 6/6 |
| `frozen_capture_no_resume` | a frozen capture never re-links — not to a same-name sink, not to a same-name producer | §1.3 |
| `pipewire_remote_is_decisive` | `PIPEWIRE_REMOTE=<bogus>` → rc=255 on both directions; a valid `PIPEWIRE_NODE` does not rescue it | §2 |
| `target_object_beats_node_target` | both keys present and disagreeing → `target.object` decides (missing → fallback) | §2, §3 |
| `capture_sink_selects_resolution_family` | `=false`/absent → link to a **stream's output ports**; `=true` → resolve as a **sink** (miss → default monitor) | §1.2, §3 |
| `capture_prop_required` | element `target-object=` alone on capture → rc=255 `target not found` (playback: sufficient) | §3, 3/3 |
| `target_resolution_race` | a peer-created stream target that appears later → rc=255, 0 B (4/12 reps) | §3.4 |
| `pulsesrc_device_strict_set` | real source name → rc=0; sink name / garbage / **empty** → rc=1 `No such entity` | §4 |
| `pulse_refusal_artifact_race` | the rc=1 artifact is 0 B *or* a 44-byte streaming placeholder (1/9) | §4 |
| `freeze_on_quantum_grid` | frozen bytes = `44 + k·quantum_bytes`, moved by client-local `PIPEWIRE_QUANTUM` | §5.1 |
| `write_batch_granularity` | file grows in 16–18-quantum batches (≈0.35 s); freeze inside batch #1 → **0-byte** artifact | §5.1 |
| `same_name_client_split` | two same-name sinks: clients may resolve to *different* nodes; unload-by-index is not unload-the-linked-node | §6.2 |

---

## 8. Arm table (verbatim-armable rows, all measured ≥3× on this host)

`NS` = a seat-owned `module-null-sink` name; **read `pactl get-default-sink`
live** — never hard-code the fallback node.

| # | arm | expected rc / stderr | expected topology | artifact signature |
| --- | --- | --- | --- | --- |
| B1 | `pipewiresrc target-object=NS stream-properties=props,stream.capture.sink=true num-buffers=1000 ! … ! wavenc ! filesink` + a producer into `NS`, then **kill the producer** | alive, **stderr empty** | monitor link unchanged | file **keeps growing** (901 164 B at a 5 s cap) |
| B2 | same, but `target-object=<producer stream node>` + `stream.capture.sink=false`, producer SIGKILLed at 1.5 s | alive, **stderr empty** | direct `prod:output_* → cap:input_*` | frozen **274 476 B**, `wavenc_streaming` |
| B3 | B2 with `on-disconnect=none` / `=eos` | identical to B2 | identical | identical (byte-identical) |
| B4 | capture from `NS`, `pactl unload-module <verified index>` at 1.2 s, then reload a same-name null sink at 2.6 s | alive, stderr empty | **no link ever returns** | frozen 204 844 B for the rest of the window |
| B5 | `PIPEWIRE_REMOTE=bogus gst-launch-1.0 -q audiotestsrc wave=silence num-buffers=96 ! <caps> ! pipewiresink` | **255** / `Failed to connect` + `gstpipewirestream.c(136)` | — | — |
| B6 | `PIPEWIRE_REMOTE=bogus` on a `pipewiresrc` capture leg | **255** / same | — | **0-byte file** |
| B7 | `PIPEWIRE_PROPS={ node.target=NS } PIPEWIRE_NODE=no_such … ! pipewiresink` | 0 | node props **both** keys; link → **`<DEF>`** | — |
| B8 | `pipewiresrc target-object=NS` (no `stream.capture.sink`) | **255** / `stream error: target not found` | — | **0-byte file** |
| B9 | `pipewiresrc target-object=NS.monitor stream-properties=props,stream.capture.sink=true` | 0 | link → **`<DEF>:monitor_*`**, never `NS` | grows |
| B10 | `pipewiresrc target-object=<peer-created stream>` started in the *same instant* as the producer | **255 target_not_found in ~⅓ of reps** | — | 0-byte file |
| B11 | `pulsesrc device=NS.monitor num-buffers=20 ! …` | 0 | — | **9 600 frames**, finalized |
| B12 | `pulsesrc device=NS.monitor blocksize=4096 num-buffers=8 ! …` | 0 | — | **8 192 frames** |
| B13 | `pulsesrc device=` (empty) + `PULSE_SOURCE=NS.monitor` | **1** / `No such entity` (`pulsesrc.c(1622)`) | — | 0 B **or** 44 B |
| B14 | `pulsesrc device=NS.monitor server=unix:/nonexistent` | **255** / `Connection refused` (`pulsesrc.c(1016)`) | — | 0-byte file |
| B15 | capture from `NS`, unload at 1.2 s, `PIPEWIRE_QUANTUM=256/48000` on the client | alive | no link | frozen **198 700 B** = 44 + 194·1024 |
| B16 | capture from `NS`, unload at 1.2 s, `PIPEWIRE_QUANTUM=2048/48000` | alive | no link | frozen **213 036 B** = 44 + 26·8192 |
| B17 | capture from `NS`, unload at **0.2 s** (before the first batch) | alive (rc=−9) | no link | **0 bytes, no header** |
| B18 | two modules with the *same* `sink_name`, unload the first index | 0 | one node survives | capture freezes **or not**, nondeterministically |

---

## 9. Falsification list (what would prove each claim wrong)

1. **"`on-disconnect` is inert against a true peer death"** — any B2/B3 leg
   whose rc, stderr or artifact differs across `none`/`error`/`eos`, or whose
   file keeps growing after the peer's death.
2. **"a producer's exit is invisible to a monitor capture"** — a B1 leg whose
   file stops growing or whose stderr is non-empty.
3. **"a frozen capture never resumes"** — a B4 leg that re-links or grows after
   the same-name target returns.
4. **"`PIPEWIRE_REMOTE` is decisive"** — a bogus-remote leg with rc=0, or one
   that links to the default sink.
5. **"`target.object` outranks `node.target`"** — a B7 leg that links to `NS`.
6. **"the element property wins on capture"** — an f1-shaped leg whose node
   props keep the `stream-properties` value or that links elsewhere.
7. **"`target-object=` alone is insufficient on capture"** — a B8 leg with
   rc=0.
8. **"capture.sink selects the resolution family"** — a `=false` leg that lands
   on a *sink* monitor, or a `=true` leg that links to a stream's output ports.
9. **"the freeze lands on the quantum grid"** — a 48 kHz freeze whose
   `(bytes−44) % quantum_bytes ≠ 0`, or a quantum leg whose freeze ignores the
   requested quantum.
10. **"`pulsesrc` num-buffers is an exact frame bound"** — a default-knob
    `pulsesrc` leg with `frames ≠ num-buffers·480`.
11. **"the record path refuses the empty device"** — a `device=` leg with rc=0.
12. **"the frozen header is `riff=0x7FFF0024 / data=0x7FFF0000`"** — a kept
    artifact whose first 44 bytes differ (the three kept here are identical).
13. **"same-name clients can split"** — a duplicate-name round where both
    clients provably resolve to the same node in every rep.
14. **"the host default sink is SPDIF"** — it was stable for this whole window,
    but a sibling lane moved it twice in the scout's window (§10); any arm that
    hard-codes the fallback node is unsound.

---

## 10. Contention ledger + instrumentation honesty

**Foreign state at entry** (`receipts/s0-baseline.json`, 17:03:47Z): default
sink `…HiFi__SPDIF__sink`, default source `…HiFi__Line__source`, 41 pulse
modules, 10 pw nodes — including sibling-owned null sinks `r78_prop_a_1109356`
/ `r78_prop_b_1109356`.

**A sibling lane was live for the entire window** (`measure_audio.py
--probe-capture-r79`, pid 1141702 → 1252822 → 1287380, plus a second audio lane
`r80md_1243214` and a **different r81 seat** using the `gst_r81_*` prefix:
nodes `gst_r81_1288879_*`, `gst_r81_auth_1288879`, `gst_r81_1291125_*`,
`gst_r81_smoke_ns`, `gst_r81_src_override`, `gst_r91_src_default`, plus a
game-dev Godot battery `r92-baseline`). The seat's own `gst_r81_bnd_*` prefix
kept every node separable in every `pw-dump` witness.

**Interference events (all recorded, none repaired by this seat):**

1. **A foreign link into a seat node [O]:** in the first `p1` pass, one sample
   showed `r91s_diag_src:capture_FL/FR -> gst_r81_bnd_cap:input_FL/FR` — a
   sibling lane's node linked into this seat's capture ports for ≲0.35 s. It
   vanished before the producer's death, so it does not affect the freeze
   result, but it is recorded.
2. **Load-driven wall-cap overshoot [O]:** the cap is checked in the loop that
   owns the process group, but a `pw-dump` sample *inside* that loop can block
   for >1 s under load, which delays the check by that much — measured: a leg
   capped at 4.0 s ran to **5.47 s** and exited by itself before the delayed
   check could kill it, and an earlier pass killed at 5.4 s on the same cap.
   The byte cap is delayed by the same sampler. This is a real property of any
   in-loop sampler; the receipts carry `elapsed_s` next to `killed` so the
   overshoot is visible. [I] the scout's harness has the same structure.
3. **The seat's own content was seat-local:** the 1 kHz tone played only into
   `gst_r81_bndns`. After an unload, the *producer* re-linked to the **shared
   default sink** (playback fallback law) and played digital-level tone there
   for up to ~3 s per freeze leg — disclosed, and the reason `h2b` shows a tone
   peak while `h7` shows silence. No tone was ever injected while another lane's
   recording was active on a seat-owned sink.
4. **No `set-default-sink`/`set-default-source` was ever issued**; the default
   read live at entry and exit is the same (`SPDIF` / `Line`). No foreign
   module, node or link was touched; every unload index was re-read and matched
   immediately before the call.
5. **Exit state** (`receipts/s0-final.json`, 17:21:19Z): **0** modules and **0**
   nodes matching `gst_r81_bnd`, no `gst-launch-1.0` process left, 41 modules
   (unchanged), scratch 10.06 MB (receipts + three kept artifacts).

**Harness bugs found and disclosed (both superseded by re-runs):**

- **Group-level `ensure_single_ns`** (§6.1) — two `p5` passes invalidated; the
  reported pass runs the target assertion inside every rep.
- **Size-sample blindness for fast exits** — legs that finish in 12–19 ms have
  no size samples at all (`sizes=[(0.0, None)]`); artifact truth is taken from
  the post-run `wav_shape`, never from the timeline. The `pulsesrc` refusal
  class would have been misread as "no file" from the timeline alone.

---

## 11. Remaining unknowns (honest edges)

- **The mechanism is unread.** Everything here is measured through
  `gst-launch`, `pw-dump` and `pactl`; `gstpipewiresrc.c`,
  `gstpipewiresink.c` and the WirePlumber policy were not consulted. *Why*
  `on-disconnect` never fires, *why* the write batching is 16–18 quanta, and
  *how* WirePlumber picks between two same-name sinks are characterised, not
  explained. **[?]**
- **The quantum observed here was not read from the graph** — it is inferred
  from the freeze grid and the `PIPEWIRE_QUANTUM` response. `node.latency` /
  the driver's quantum were not sampled. **[?]**
- **The 44.1 kHz resampler alignment** (940 vs the ideal 940.8 frames per
  quantum) is measured but not modelled. **[?]**
- **`PIPEWIRE_REMOTE` was probed with one bogus name and one valid name only**
  — not with a valid *alternate* socket, a relative path, or a socket owned by
  another user. **[?]**
- **The duplicate-name resolution rule** (age? serial? insertion order?) is
  measured as nondeterministic over 3 rounds; a larger sample (≥20) would be
  needed to state a distribution. **[?]**
- **`on-disconnect` was never observed to fire in any shape measured** — the
  property may be reachable through a state not probed here (e.g. a server
  restart, or a `fd=`-supplied stream). **[?]**
- **The default-sink-move cell** (target alive, host default moves) still
  requires `pactl set-default-sink` and was **not** exercised (shared host). **[?]**

---

## 12. Receipts index

All under `corpus/live/r81-boundary/`; per-leg dirs
`runs/<stage>/<leg>_r<rep>/` carry `cmd.txt`, `env.txt` (where set),
`stderr.txt`, `receipt.json`. Harness
`r81_bnd_probe.py` (stages `baseline p1 p2 p3 p4 p5 p6 final`), readers
`r81_bnd_analyze.py` / `r81_bnd_digest.py`.

| artifact | sha256 |
| --- | --- |
| `receipts/s0-baseline.json` | `39e79ac57d75a57c35ea0909802bb47953d03692ac1f622227924960734e25be` |
| `receipts/s0-final.json` | `decf67169382db843e6ceca63c293929de8898f56dbdcc71a76e1cecfbb1c33f` |
| `receipts/s1-disconnect.json` | `35e92c0a1dacb054220343715b1c6c730b979ca6664c82c0075aedb863fed1e7` |
| `receipts/s2-env.json` | `42f1acb28fca55d68012691450b86d3cdc432855a60e64179fbfb13b606e3401` |
| `receipts/s3-capture-prec.json` | `febd082e347518dd783c11b1c0eb67f7145ba4378293092415dda919559133eb` |
| `receipts/s4-pulsesrc.json` | `c0f25a9d4528734d76c2ce107158b09f4ac072ada7c9881930dbaf7200fd584c` |
| `receipts/s5-freeze.json` | `d3a47e38a99a820917142bbb287a93002bc76ba7108efcaa3c3fc1e316d62647` |
| `receipts/s6-dupname.json` | `3fb6c1f296d55c3400e1724da3899630a8a410b7a2f5d71e4bfff79f28a9dfa2` |
| `artifacts/h7_frozen_r0..r2.wav` (3×, byte-identical) | `6f2fe9c21f27db170a8e22d8712c292c3eabf892f2e4b256249b9b6b3d917fbb` |
| `r81_bnd_probe.py` (harness) | `8fd3141b854770f17dca37f093e11f83892eca335798889d4c71393df0c986cc` |

**Report status:** `reports/round-81/r81-boundary.md` is the assigned output
path; it is **untracked** in the worktree (no commit was made, no existing
tracked file was modified).

**Sibling artifact disclosure.** `corpus/fixtures/measure_audio.py` (and its
`.pyc`) is **dirty in the worktree and was dirty before this seat started** —
it is the concurrent sibling lane's file (`measure_audio.py
--probe-capture-r79`, live for the whole window; 532 440 B at the scout's entry
→ **808 688 B**, sha256 prefix `0dad37ee6500ca3d`, mtime 14:15:56 local, i.e.
written *during* this window by that lane). **This seat never read, imported or
executed it**, and its diff contains nothing of this seat's. The only paths this
seat created are `corpus/live/r81-boundary/` and this report.

**Prior pass closed.** `reports/round-81/r81-boundary-readonly.md` (the
capability-blocked predecessor, receipt re-analysis only) handed five leg
families to the exec-capable seat; **all five were run here** — (1)
`on-disconnect` vs peer-stream exit → §1.1/§1.2, (2) capture-side precedence →
§3, (3) `PIPEWIRE_REMOTE`/`PIPEWIRE_NODE` → §2, (4) `pulsesrc device=` variants
→ §4, (5) freeze sweep incl. the `num-buffers=20` control → §5.1. Its
frozen-header correction (`riff 0x7FFF0024` / `data 0x7FFF0000`, derived from
the scout's receipts) is **independently reproduced here from raw artifact
bytes** (§5.2) — two derivations, same constants.
