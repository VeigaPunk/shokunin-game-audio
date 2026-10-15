# R91 boundary — the capture freeze is a `gst-launch-1.0` CLOCK_LOST pause, not a client stall

**Seat: BOUNDARY (executor-class, leaf, falsification).** Host `plazir27`, lane
`~/Projects/shokunin/audio-shokunin` @ HEAD **`58adad60`** (the r91 scout
measured `dbe3a7f`; `r97 scout` + `r82 verifier` landed in between). Window
**2026-10-15 20:34–20:5x UTC** (17:34–17:5x UTC−3). Toolchain re-verified:
PipeWire **1.6.8**, gst-plugin-pipewire **1.6.8**, GStreamer **1.28.6-3**,
gst-launch-1.0 **1.28.6**, libwireplumber **0.5.17-1**, Python 3.14.7. Host load
during the window **82–89 on 32 cores** (the scout ran at similar load).

**Zero tracked-file edits, no commits, no `set-default-*`, no `wpctl set-default`.**
Entry tracked-dirty set was sibling-owned (`corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`,
sha `0b0c61ae012f4cad…`); at exit the same file is the **only** tracked
modification and its hash is **unchanged**. Every write is under
`corpus/live/r91-boundary/` (5 probes, 88 files, 6.5 MB) plus this report. Every
audio object this seat created is named `r91b_*` / `gst_r91b_*`; every census
and sweep matched only those prefixes. Module unloads are **by id with a
namespace guard** (the id's args must contain the seat name, else the unload is
refused). **Exit state: `pactl list modules short | grep r91b` → 0 rows,
`pw-dump` → 0 `r91b_*` nodes, 0 seat processes.**

**Labrat: not dispatched.** The seat is the frozen `probeParent`, and the
assigned attack resolved entirely to on-host measurement plus two upstream
source fetches; there was no residual bounded unknown that a read-only probe
could settle better than the measurements already taken. Budget retained.

**The headline.** The r91 scout measured a real freeze and got the prop lattice
right, but attributed the freeze to the element/client. It is
`gst-launch-1.0`'s own `CLOCK_LOST` handler: it re-clocks by forcing
`PLAYING→PAUSED→PLAYING`, the capture element **fails** the PAUSED→PLAYING
transition (no link → negotiation error), and the source is left flushed. An
application that does not take that pause keeps the element alive: with the
identical target-loss and a fresh link, the file **resumes** — no `set_state`,
no keepalive, no special prop. The scout's "Gate B / client is sticky" is a
harness artifact.

---

## 0. Verdict table

| # | r91 scout claim (report §) | verdict | sharpest fact from this seat |
| --- | --- | --- | --- |
| 1 | gst capture node carries `node.dont-reconnect=true`, unconditionally set on the capture element | **CONFIRMED** | 8 fresh gst legs, `pw-dump`: `node.dont-reconnect: True` every time (`B0`–`B12`, `C3`) |
| 2 | the override `node.dont-reconnect=false` lands and WP then re-links | **CONFIRMED** (prop) / **NOT RE-TESTED** (WP re-link) | scout's F4 numbers reproduced in kind; this seat did not re-run the override-loss arm |
| 3 | gst **sink** does not carry the flag | **CONFIRMED** | `S1`: `node.dont-reconnect` absent on a live `pipewiresink` node |
| 4 | the freeze is "Gate B (client)", element-specific, sticky under a valid link | **FALSIFIED** | `RESUME` hold=999 (never forces PLAYING): relink at t=1.677 → bytes resume 204844 → 348204; `B11` pw-record: relink at 2.217 → resumes to 745516 |
| 5 | the freeze mechanism: keepalive 0 → `pw_thread_loop_wait`, "no timeout, no error path" | **INCOMPLETE / mechanism misattributed** | real cause is upstream: `gst-launch.c:642-646` forces PAUSED→PLAYING; `pipewiresrc0` fails that transition (`error during negotiation`, `:1094`) → `FLUSHING` |
| 6 | `keepalive-time>0` is the element's designed resend path (scout §7.5) | **FALSIFIED as a fix** | `B1` keepalive=20 freezes flat (413740 / 204844); `DBG_keepalive20` log: **0** `timeout, send keepalive buffer` lines, **0** `popped buffer` lines |
| 7 | frozen file is `204844 B` | **FALSIFIED as a constant** | frozen size is non-deterministic: 65580, 135212, 139308, 204844, 229420, 413740 across 12 legs; `B0` (2/2) = 135212, not 204844 |
| 8 | frozen header `riff 0x7FFF0024` / `data 0x7FFF0000` | **CONFIRMED** | reproduced on **every** frozen leg (header is the invariant; file size is not) |
| 9 | no-prop capture × sink target never links (F1 law) | **CONFIRMED, cause sharper** | `C1` pw-record exits rc=1 at **44 B** with `no target node available`; `C2` gst exits **255** `stream error: target not found` — a hard *target resolution* failure, not merely a never-formed link |
| 10 | the no-prop law is a *direction* law (control) | **CONFIRMED** | `C4` pw-record no-prop × **source** target: links and records 536620 B |
| 11 | F1s pw-record source-loss **freezes** | **FALSIFIED** | `B12` (no relink, no props): grows 311340 → **966700 B** post-loss, stream stays `running`; the r85 shape reproduces |
| 12 | "Gate B" also applies to pw-record (manual link does not resume) | **FALSIFIED** | `B11`: pw-record frozen at 229420 (idle, 1.21–2.04 s) resumes to 745516 immediately after the hand-made link |
| 13 | force-quantum moves the freeze window (assigned probe) | **FALSIFIED** | `B5` fq=4096 → 229420 / 65580; `B6` fq=1024 → 135212 / 135212; no relation to quantum; scout's implied recipe (`PIPEWIRE_LATENCY`) would not even arm the leg (see §4) |
| 14 | `pw-dump` renders F3 as JSON `true`, F4 as string `"FALSE"` | **CONFIRMED** | `B0`-class props show `True`; gst passes `stream-properties` values through as written |

---

## 1. Root cause, mechanism-read and log-anchored

### 1.1 The three-log chain

Every link is on-disk in this seat's receipts and in the scout's own fetched
sources.

| step | anchor | verbatim |
| --- | --- | --- |
| the element posts CLOCK_LOST when the stream drops out of STREAMING | `[I]` `gstpipewiresrc.c:904-912` + scout's own report §1.1 | `case PW_STREAM_STATE_PAUSED: … gst_element_post_message (… gst_message_new_clock_lost …)` |
| **gst-launch-1.0 re-clocks on that message by forcing a state round-trip** | `[I]` `gst-launch.c:642-646` (fetched, sha `606dfaecceb1da93…`) | `case GST_MESSAGE_CLOCK_LOST: PRINT ("Clock lost, selecting a new one\n"); gst_element_set_state (pipeline, GST_STATE_PAUSED); gst_element_set_state (pipeline, GST_STATE_PLAYING); break;` |
| the element **fails** the PAUSED→PLAYING half because no link exists | `[O]` `DBG_keepalive20` + `WIN_nom` element log | `:1788 in-activating stream` → `:1449 setting flushing` → `:1774 activating stream` → `:1074 waiting for NEGOTIATED, now paused` → `:1094 error during negotiation`; then `gst_base_src_get_range: clock was unscheduled (2), returning FLUSHING` |
| pipeline aborts the transition and stays PAUSED | `[O]` `WIN_nom/window_1.15-1.60.log` | `gst_bin_change_state_func:<pipeline0> child 'pipewiresrc0' failed to go to state 4(PLAYING)` → `gst_element_abort_state:<pipeline0> aborting state from PAUSED to PLAYING` |
| once `flushing=TRUE` is set, every `create()` returns FLUSHING before it can dequeue | `[I]` `gstpipewiresrc.c:1568-1569` + `:1449-1451` | `if (pwsrc->flushing) goto streaming_stopped;` → `return GST_FLOW_FLUSHING` |

This is why **keepalive cannot help**: the element never reaches the wait loop
again. `DBG_keepalive20` (GST_DEBUG `*:5`, 3.9 MB raw log) records **zero**
`popped buffer` and **zero** `timeout, send keepalive buffer` lines across the
whole post-loss window — the loop is exited, not timing out.

### 1.2 The positive control that closes the case

`RESUME` arm (GStreamer python bindings, **no** CLOCK_LOST handling, so the
pipeline is never paused):

| event | t | observation |
| --- | --- | --- |
| target module unloaded | 1.20 | — |
| `clock-lost` on the bus | 1.374 | pipeline state-changed log stops at `paused -> playing` (0.142); **no pause ever happens** |
| manual `pw-link r91b_ns_res2:monitor_* → gst_r91b_resume:input_*` | 1.677 | link rc=0 |
| file grows again | 2.72 | 204844 → 274476 (+69632) |
| file grows again | 4.33 | → 348204 (+73728) |

`forced` is **null** in that receipt: nothing ever set the pipeline back to
PLAYING, because it was never taken out of PLAYING. The element dequeues and
the file resumes. **The "client" is not sticky.** The scout measured the same
relink on the same element and saw no growth because its harness had already
paused and flushed the pipeline.

### 1.3 Why the scout's own §4 landed where it did

The scout's `recover-inloop` used `gst-launch-1.0`. That binary installs
`bus_handler` unconditionally (`gst-launch.c:1294`), and `bus_handler` contains
the CLOCK_LOST state round-trip above. The scout recorded the element as `idle`
and the file flat — both true — and read them as element properties. They are
harness properties. The scout's `[?]` #1 ("whether this is a pw_stream
state-machine issue or a gst-side queue/negotiation stall") is now answered:
it is neither; it is the app-level clock re-selection, and it is the *element's
PAUSED→PLAYING path* that refuses, because `wait_negotiated` sees no link.

---

## 2. The freeze window is not a constant

`B0` (canonical F3 argv, target unload at 1.2 s) froze at **135212 B, 2/2** — not
the scout's 204844. Across this seat's 12 frozen gst legs:

| leg | frozen bytes | × 4096 |
| --- | --- | --- |
| `B0` r0, r1 | 135212, 135212 | 33.0 |
| `B1` (keepalive 20) r0, r1 | 413740, 204844 | 101.0, 50.0 |
| `B5` (force-quantum 4096) r0, r1 | 229420, 65580 | 56.0, 16.0 |
| `B6` (force-quantum 1024) r0, r1 | 135212, 135212 | 33.0, 33.0 |
| `B7` (manual relink) r0, r1 | 204844, 204844 | 50.0 |
| `DBG_keepalive20` | 135212 | 33.0 |
| `WIN_nom` / `GL_m_keepalive0` | 204844 / 204844 | 50.0 |

The values are 4096-aligned but **not determined by argv, quantum, or
keepalive**: the freeze lands wherever the last `wavenc` flush left the file at
the moment the pipeline aborted. **204844 is one sample of a distribution, not a
law.** What *is* invariant is the header (`§3`) and the flat-post-loss shape.

**Force-quantum** was armed correctly and independently checked: with
`PIPEWIRE_QUANTUM=4096/48000` the live node carries `node.force-quantum=4096`,
`node.force-rate=48000` (`B5`), and with `1024/48000` it carries `1024/48000`
(`B6`) — read from `pw-dump` on the running node, 2 reps each. The freeze window
moved to 229420/65580 and 135212/135212 respectively, i.e. **it tracked the
run, not the quantum**. The assigned probe's premise is falsified.

---

## 3. The frozen header is the real invariant

Reproduced on **every** frozen leg, with no exceptions:

```
52494646 2400ff7f 57415645 666d7420 10000000 01000200 80bb0000 00ee0200
04001000 64617461 0000ff7f ...
```

- `riff-size = 0x7FFF0024`, `data-size = 0x7FFF0000`, file size = header + last
  flushed buffer. Matches the scout's §0.6 correction (and the r81-boundary
  correction), **not** r81's `0x7FFFF000`. This is the scout claim this seat
  most firmly re-confirms.

---

## 4. Connect law — the no-prop × sink target is a hard failure, not a silent no-link

The scout's §0.5 read is right about the *direction* filter but understates the
outcome. With the target's existence verified in `pw-dump` immediately before
each leg:

| leg | client | argv shape | result |
| --- | --- | --- | --- |
| `C1` | pw-record | no props, `--target r91b_ns_connect` (sink) | **rc=1**, 44 B, stderr `stream node 121 error: no target node available` / `remote error: … -2 (No such file or directory): no target node available` |
| `C2` | pipewiresrc | no props, `target-object=r91b_ns_connect` (sink) | **rc=255**, 0 B, `stream error: target not found` at `gstpipewiresrc.c(929)` |
| `C3` | pipewiresrc | `stream.capture.sink=true`, sink target | links, 483372 B |
| `C4` | pw-record | no props, `--target r91b_src_connect` (**source**) | links, 536620 B — **the control that isolates direction** |

So: the client does **not** stay alive in a "suspended, never linked" state; it
errors out at connect. The scout's F1 table row ("node state `suspended`") is a
per-sample artifact of the same class it flagged for F2 — in this seat's `C1`
the node was never observed at all, and the process had already exited.

**Quantum recipe note for the author.** `PIPEWIRE_LATENCY` sets only
`node.latency` (`stream.c:2159-2160`); the force-quantum lever is
`PIPEWIRE_QUANTUM=<q>/<rate>` (`stream.c:2149-2157`). An arm built on
`PIPEWIRE_LATENCY` would silently not move the quantum.

---

## 5. Cross-receipt resolution: the scout's own `[?]` #2 is answered

The scout flagged a conflict between its F1s freeze and r85's
`s3e-vsrc-loss.json` (growing). This seat resolves it **in favour of r85**, and
the reproduction is exact:

- r85 `wsrc0` timeline: loss at t=1.61 (`vsrc False, mod False`), size
  **311340 → 860204**, stepping in 16384/24576 B increments, final 876588,
  rc=1.
- this seat's `B12` (pw-record, remap-source target loss, no props, **no
  relink**): loss at t=1.206, size **311340 → 966700**, stream state `running`
  throughout, stepping in 24576/32768 B increments.
- **13 of B12's 31 sampled byte values are exactly r85's `sz` values**
  (24620, 65580, 221228, 311340, 376876, 417836, 483372, 548908, 589868,
  614444, 704556, 745516, 811052), including the shared pre-loss point 311340.

Both legs grow at ≈192 kB/s (≈ the stereo-48k-16bit rate), i.e. **real
content**, and both stay `running`. The residual difference between the two is
sampling phase and the record-rate stepping, not shape. **The universal
source-loss shape is "grows", not "freezes".**

The scout's `B11` (same shape **plus** a manual relink) also freezes only
*because the relink is the only link it ever gets*: it goes 229420 → idle from
1.21 to 2.04, then resumes to 745516 the moment the hand-made link lands. The
freeze is a "no link" state, not a "client refuses data" state.

---

## 6. The non-capture path

`S1`: `fakesrc is-live=true → pipewiresink target-object=r91b_ns_sink`, sink
module unloaded at 1.2 s.

- props on the live sink node: `node.dont-reconnect` **absent** (scout headline
  3 confirmed on a fresh node).
- after the unload the element's **stream state stays `running`** for the whole
  remaining window (2/2 reps of node-state sampling at 0.2 s), unlike the
  capture element which drops to `paused`/`idle`.
- the probe did **not** isolate a re-link to the default sink (foreign lanes own
  that port), so "the sink re-links" is **not claimed** here; the prop
  asymmetry and the state asymmetry are what this seat measured.

---

## 7. Falsification list (what was tried that could have killed each claim)

| claim attacked | falsifier attempted | outcome |
| --- | --- | --- |
| the element/client is the reason the file freezes | python app with the CLOCK_LOST handler absent; relink only, never `set_state` | **falsified** — resumes 204844 → 348204 |
| `keepalive-time>0` resends the last buffer (scout §7.5 arm) | `keepalive-time=20`, 2 reps + a GST_DEBUG run | **falsified** — flat; 0 resend lines, 0 popped-buffer lines |
| the freeze is a client stall "with a valid link" | pw-record + manual link (`B11`) | **falsified** — resumes on the link |
| pw-record source-loss freezes (F1s) | `B12`, no relink, 2 reps | **falsified** — grows to 966700; matches r85 |
| the frozen size is 204844 | 12 frozen legs | **falsified** — 6 distinct sizes, 4096-aligned |
| force-quantum moves the freeze window | `PIPEWIRE_QUANTUM` 4096 and 1024, prop-verified | **falsified** — no relation |
| no-prop × sink target "never links" (silently) | `C1`/`C2` with target verified present | **falsified as stated** — both error out at connect (rc=1 / rc=255) |
| the no-prop law is about direction | `C4` no-prop × source target | **control passed** — links, 536620 B |
| gst sink carries the flag too | `S1` census | **falsified** — absent |
| `node.dont-reconnect=true` on the capture node | 8 legs, `pw-dump` | **confirmed** |
| frozen header `0x7FFF0024` / `0x7FFF0000` | hex read on every frozen leg | **confirmed** |
| the seat perturbs host state | census before/after every stage, module guard, defaults | see §9 |

---

## 8. Author directives

**Verbatim-ready cells** (≥2 reps each here, byte/state-stable; exact argv in
the receipts):

1. **Root cause, four lines.** `gst-launch.c:642-646` forces
   `set_state(PAUSED); set_state(PLAYING)` on CLOCK_LOST;
   `gstpipewiresrc.c:1094` `error during negotiation` (no link);
   `gst_bin_change_state_func: child 'pipewiresrc0' failed to go to state
   4(PLAYING)`; `gst_base_src_get_range: … returning FLUSHING`. (Receipts
   `WIN_nom/window_1.15-1.60.log`, `DBG_keepalive20`, `GL_m_keepalive20`.)
2. **Client-is-not-sticky.** Manual link after target loss, **no** `set_state`:
   bytes 204844 → 348204 (`RESUME_relink`). Same on pw-record: 229420 → 745516
   (`B11`).
3. **Keepalive does not rescue.** `keepalive-time=20` → flat; 0 `timeout, send
   keepalive buffer` lines in 3.9 MB of `*:5` debug.
4. **Frozen header.** `riff 0x7FFF0024`, `data 0x7FFF0000` — every frozen leg.
5. **Prop witness.** `node.dont-reconnect=True` on capture (`B0`–`B12`, `C3`),
   absent on sink (`S1`).
6. **Connect law.** `C1` rc=1 / 44 B / `no target node available`; `C2` rc=255 /
   `target not found`; `C4` source target links (control).

**Bimodal / envelope cells** (do not arm as a single shape):

- **Frozen file size**: arm with bytes *and* the header; treat the size as
  distribution-valued (this seat saw 65580…413740). Only the header is a
  constant.
- **Source-loss shape (pw-record)**: arm both bytes and node state; the
  no-relink shape is "grows" (`B12`, r85) and the relink shape is
  "freeze-then-resume" (`B11`). The scout's "freeze" arm (`F1s`) was not
  reproduced in 2 reps here.
- **Sink re-link**: prop/state asymmetry is verbatim-ready; a re-link to the
  *default* sink is not claimed.
- **`on-disconnect=eos|error`** and **`resend-last`**: read in source
  (`gstpipewiresrc.c:613-689`, `:1593-1605`) and *predicted* to be unreachable
  once the pipeline pauses, but **not measured** here — do not assert.

---

## 9. Contention ledger + exit state

| window | contact | effect |
| --- | --- | --- |
| whole window | foreign lanes: `r79lb_*`, `r85`/`r86`/`r87`/`r90`/`r92`/`r100` seats, `r90-author/hunt_greens.sh`, `run_battery.py`, game-dev-2d lanes | read-only contact; link listings carry their rows; no foreign object touched |
| whole window | `~/.local/state/wireplumber/stream-properties` (mtime 17:41) | this seat added its stream-property rows (same class of residue every round leaves; no CLI can delete) |
| 20:34–20:5x | this seat: ~45 bounded legs across 5 probes, all with `start_new_session` + `os.killpg` + wall/byte caps | own residue zero at exit |
| **default source** | at entry census `pactl get-default-source` = **`r91b_src1`** — a *sibling* lane's dead `module-remap-source`, already residue before this seat's first leg (`default-nodes` mtime 17:15; the scout's window had `…HiFi__Line__source`) | after this seat unloaded its own modules the default **self-restored** to `alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source`, which is exactly `default.configured.audio.source` in `~/.local/state/wireplumber/default-nodes`. **No `set-default-*` was ever issued by this seat**; net default-source delta = 0 |
| exit | `pactl list modules short \| grep r91b` = 0; `pw-dump` r91b nodes = 0; seat processes = 0; `git status --porcelain -uno` = the single pre-existing sibling `.pyc`, hash unchanged | clean |

---

## 10. Artifacts & provenance

`corpus/live/r91-boundary/` (untracked, 88 files, 6.5 MB):
`probes/r91b_probe.py` (main lattice + loss/recover legs),
`probes/bus_probe.py` (python-bindings bus/CLOCK_LOST arms),
`probes/dbg_keepalive.py` (GST_DEBUG mechanism capture),
`probes/window_probe.py` (state-transition window),
`probes/connect_law.py` (no-prop connect law + control),
`probes/sink_probe.py` (non-capture path); `runs/<leg>/{receipt.json,*.log}`;
`receipts/{census-entry,census-exit}.json`; `sources/gst-launch.c`,
`sources/gstpipeline.c`.

Key receipt shas (prefix): `census-entry 764c6cfb622a9f6b`,
`census-exit ec4c25a1a066587d`, `B0 f0b9418e147f6dff`,
`B1 ec94a9562e49c8fd`, `B5 c595219447251f06`, `B6 4e28ab420d569d76`,
`B7 3e7069a182c8aa12`, `B11 15079f0f252ed3a9`, `B12 4c1d4fe10efd4e6f`,
`OBSERVE 501d895ec3aa3607`, `RESUME 20bcdb1b2bc7ea23`,
`WIN_nom 48cac7ce085d3fee`, `DBG_keepalive20 f6beec2f53876c1c`,
`S1 ca5047280801c79b`, `C1 cf6d66d8b0262366`, `C2 bdfc23a98c668cce`,
`C3 25c6fa1d4c6d5942`, `C4 bb1fc6f07ce3c1a4`.

Upstream sources fetched over the network (version-matched to installed
gst-launch-1.0 1.28.6): `gst-launch.c`
`606dfaecceb1da939f12103f30533f8c3c4810fa42d7e19d9ff7190b1ee8b7ce`,
`gstpipeline.c` `670eff0bb6773944809b962e35f536b758bc0b6fed875b7dbf9282f7ed5c410a`.
Element/policy sources are the scout's own `corpus/live/r91-scout/sources/`
(read here, not re-fetched).

*boundary leaf — attacked with fresh processes, measured, not judged.*
