# R91 scout — the capture-freeze law, mechanism-read and re-measured

Round 91 pre-measurement. Host `plazir27`, measured **2026-10-15 17:05:58Z →
17:07:50Z** (host local UTC−3, 14:05–14:07) plus bounded diagnostics
17:09–17:2xZ. Repo `~/Projects/shokunin/audio-shokunin` @ HEAD **`dbe3a7f`**
(HEAD moved during this seat from `15c6a35` — sibling `r81-boundary-readonly`
commit; that report is folded where it intersects). Toolchain: PipeWire
**1.6.8** (`1:1.6.8-1`), gst-plugin-pipewire **`1:1.6.8-1`** (so the GStreamer
plugin *is* the PipeWire 1.6.8 tree), GStreamer **1.28.6-3**, libwireplumber
**0.5.17-1**, Python 3.14.7.

**Seat: SCOUT (leaf). Zero tracked-file writes; the only file written outside
`corpus/live/r91-scout/` is this report.** Every leg is triple-bounded
(element bound in argv + wall cap + byte cap checked in the same loop that owns
the process group; `start_new_session` + `os.killpg`). Seat-owned names only
(`r91s_*`, `gst_r91_*`); module unloads are index-verified against the seat
name immediately before the call; **no `pactl set-default-*` was ever issued**.
Defaults read live at every stage boundary: sink `…HiFi__SPDIF__sink`, source
`…HiFi__Line__source`, unchanged at exit.

**Label legend.** `[O]` = directly observed on this host in this window (probe
output or on-disk file read). `[I]` = read from **version-matched upstream
source fetched over the network** (not present on disk; URL + sha recorded) or
inferred from measured laws. `[?]` = not resolved by this seat.

**Surface chosen: priority 1 — mechanism/prior-art read of the r81 freeze law.**
The host has readable sources: WirePlumber's *entire Lua policy tree*
(`/usr/share/wireplumber/scripts/**`, MIT, installed by libwireplumber 0.5.17)
is on-disk `[O]`, `/usr/include/pipewire-0.3` + `wireplumber-0.5` headers and
the full module man-page set are on-disk `[O]`, and the host has network
access — `curl -sI https://gitlab.freedesktop.org` → 302 `[O]` — so the
exact-version C sources were fetched from the `1.6.8` tag `[I]` and cross-
checked against the installed package versions and binary strings `[O]`.

---

## 0. Headline claims

| # | claim | label | sharpest single fact | evidence |
| --- | --- | --- | --- | --- |
| 1 | **The r81 freeze is a two-gate law, now mechanism-read.** Gate A (policy): `gstpipewiresrc.c` sets `PW_STREAM_FLAG_DONT_RECONNECT` **unconditionally on the capture element** → the stream node carries `node.dont-reconnect=true` → WirePlumber's `prepare-link` drops any new target for a dont-reconnect item that was already handled (`"dont-reconnect, not moving"` / `target=nil`) → the link is never re-created. | `[I]`-source + `[O]` prop witness | live `pw-dump` of a gst capture node: `node.dont-reconnect = true`; same-session `pw-record`: key absent | `sources/gstpipewiresrc.c:1207-1211`, `stream.c:2091-2093`, `/usr/share/wireplumber/scripts/linking/prepare-link.lua:27,65,73`; `receipts/props.json` F3 |
| 2 | **Gate B (client) is the freeze itself and is sticky.** With the policy gate removed (`node.dont-reconnect=false`) WP *does* re-create the link to the default sink monitor — and the file **still freezes at 204844 B**. A hand-made link to a live seat-owned tone monitor also does not resume it (state stays `idle`). | `[O]` | F4 post-loss link `alsa_output…SPDIF__sink:monitor_FL → gst_r91_src_override:input_FL` present 3/3, bytes flat at 204844 3/3; recover: manual `r91s_ns2:monitor_FL → gst_r91_src_default:input_FL` present, bytes flat 3/3 | `receipts/loss.json` F4; `receipts/recover-inloop.json` |
| 3 | The gst *sink* does **not** set the flag (`gstpipewiresink.c` flags = ASYNC+EARLY_PROCESS), and the live sink node has no `node.dont-reconnect` — r81's playback re-link law stands with its mechanism now visible. | `[I]`-source + `[O]` | `pipewiresink` node props: `node.dont-reconnect` absent | `sources/gstpipewiresink.c:908-916`; `receipts/props.json` F5 |
| 4 | **The policy gate is controllable from the client CLI**: `stream-properties=props,node.dont-reconnect=false` lands the literal string `"FALSE"` (WP `parseBool` lowercases) and flips WP from "never re-link" to "re-link". | `[O]` | F3 post-loss links `[]` vs F4 post-loss link to SPDIF monitor, 3/3 each | `receipts/props.json` F3/F4; `receipts/loss.json` F3/F4 |
| 5 | **New connect law (no-prop capture × sink target)**: `pw-record --target <null-sink name>` with no `stream.capture.sink` **never links** — 44 B, node `suspended`, 3/3. Mechanism `[I]`: `getTargetDirection` returns `"output"` for a no-prop capture and `find-defined-target` requires the target's direction to match, so a sink-name target is filtered out. | `[O]` + `[I]` | file 44 B at every sample for 2.4 s, `links_relevant` empty | `receipts/props.json` F1; `lib/common-utils.lua:37-48`, `linking/find-defined-target.lua:45-79` |
| 6 | **Frozen header independently re-pinned**: `riff-size = 0x7FFF0024`, `data-size = 0x7FFF0000`, file 204844 B — reproduces the r81-boundary correction (not r81's `0x7FFFF000`). | `[O]` | hex head `524946462400ff7f…646174610000ff7f` | `runs/header/H1_r0/receipt.json` |
| 7 | `pw-record` + `stream.capture.sink=true` re-links to the **default sink monitor** ≤0.2 s after target loss and keeps growing with real content — r80 L4 / r81 t7 re-confirmed 3/3 (final 925740/925740/929836 B). | `[O]` | post-loss link `…SPDIF__sink:monitor_FL → r91s_pwrec_capsink:input_FL`, bytes monotonic | `receipts/loss.json` F2 |
| 8 | **Cross-receipt conflict, named not papered over**: r85's receipt shows the remap-source-death shape *growing with zeros* after loss; this harness (3 argv variants + 3 stage reps) freezes at the last buffer with the record node transitioning `running→idle` at the loss sample. | `[?]` | r85 `s3e-vsrc-loss.json` wsrc0: 311340 → 860204 B after `mod=False`; this seat: flat at 237612/229420/385068, state `idle` | `corpus/live/r85-scout/receipts/s3e-vsrc-loss.json`; `receipts/loss.json` F1s; `probes/diag_src3.py` output |
| 9 | The WP decision trace exists but is off by default: the user journal carries `s-linking` **warnings** (19 lines in a 20-minute window, all foreign loopback warnings) but no info-level decision lines. | `[O]` | `journalctl --user -u wireplumber` | §7 |

---

## 1. The mechanism, anchored

### 1.1 Gate A — client flag → node prop → session-manager branch

| step | anchor | verbatim (abridged) |
| --- | --- | --- |
| capture element sets the flag **unconditionally** | `[I]` `sources/gstpipewiresrc.c:1207-1211` | `flags = PW_STREAM_FLAG_DONT_RECONNECT \| PW_STREAM_FLAG_ASYNC; if (pwsrc->autoconnect) flags \|= PW_STREAM_FLAG_AUTOCONNECT; pw_stream_connect(…, PW_DIRECTION_INPUT, …)` |
| sink element does **not** | `[I]` `sources/gstpipewiresink.c:908-916` | `flags = PW_STREAM_FLAG_ASYNC; flags \|= PW_STREAM_FLAG_EARLY_PROCESS; …` |
| `pw-cat` does **not** | `[I]` `sources/pw-cat.c:2141-2151` | `flags = 0; … flags \|= PW_STREAM_FLAG_AUTOCONNECT;` |
| flag becomes the prop **only if absent** | `[I]` `sources/stream.c:2091-2093` | `if (flags & PW_STREAM_FLAG_DONT_RECONNECT) if (pw_properties_get(stream->properties, PW_KEY_NODE_DONT_RECONNECT) == NULL) pw_properties_set(…, "true");` |
| WP reads it and refuses to move the stream | `[O]` `…/linking/prepare-link.lua:27,71-76` | `local reconnect = not cutils.parseBool (si_props ["node.dont-reconnect"]) … if not reconnect and si_flags.was_handled then target = nil; goto done end` (log line `"... dont-reconnect, not moving"`, :65) |
| target-loss fallback chain | `[O]` `…/linking/find-defined-target.lua:38-79,116` + `lib/common-utils.lua:37-48` | `target.object` looked up as `object.serial` then by `node.name`/`object.path` **with a direction filter**; `getTargetDirection` = `"input"` iff playback or (`input` and `stream.capture.sink`), else `"output"`; fallback default node comes from `get-default-node("<media.type>/Sink|Source")` |
| monitor targets are linkable for a capture | `[O]` `lib/linking-utils.lua:257-267` | `isMonitor(props) = direction=="input" and item.features.monitor and …`; same-direction links allowed only if the target is a monitor |
| the client-side freeze | `[I]` `sources/gstpipewiresrc.c:48,1633-1642` | `#define DEFAULT_KEEPALIVE_TIME 0`; with keepalive 0 the create loop does `pw_thread_loop_wait (pwsrc->stream->core->loop)` — **no timeout, no error path** for "no buffer ever arrives again" |

The on-host Lua files' shas are in `sources/WP-LUA.sha256`; upstream C files'
shas in `sources/SOURCES.sha256` (URLs in `sources/SOURCES.md`).

### 1.2 Gate B — why "re-linked" ≠ "resumed" (measured, not read)

`[O]` F4 (override) gets a WP-created link to the SPDIF monitor after the loss
and the file still freezes; the recover stage builds the link **by hand** to a
live seat-owned source (`r91s_ns2` monitor, fed by a running `pw-play` tone,
`tone_state.state = "running"` 3/3) and the gst node's state stays `idle`,
bytes flat at 204844 for 2.5 s. So the element does not dequeue a buffer even
when a valid link exists; `[?]` whether this is a pw_stream state-machine
issue or a gst-side queue/negotiation stall is **not read** (the create loop's
wait is the only readable part; the pw_stream internals would need a
state witness or `GST_DEBUG` run).

---

## 2. Prop lattice (`receipts/props.json`, 5 families × 3 reps, byte-stable)

Instrument: each client captures from seat null-sink `r91s_ns1`; `pw-dump` at
+0.5 s; `wpctl inspect` captured too. All rows stable across reps (`stable=True`
for every family).

| family (argv shape) | node state | `node.dont-reconnect` | `stream.capture.sink` | `target.object` / `node.target` | file |
| --- | --- | --- | --- | --- | --- |
| F1 `pw-record --target r91s_ns1` (no prop) | suspended | — | — | `r91s_ns1` / — | **44 B** (never linked) |
| F2 `pw-record -P stream.capture.sink=true --target r91s_ns1` | suspended* | — | `true` | `r91s_ns1` / — | 462892 B (linked) |
| F3 `pipewiresrc target-object=r91s_ns1 stream-properties=props,stream.capture.sink=true` | running | **`true`** | `"TRUE"` | `r91s_ns1` / `r91s_ns1` | 413740 B |
| F4 F3 + `,node.dont-reconnect=false` | running | **`"FALSE"`** | `"TRUE"` | `r91s_ns1` / `r91s_ns1` | 413740 B |
| F5 `audiotestsrc wave=silence ! pipewiresink target-object=r91s_ns1` | running | — | — | `r91s_ns1` / `r91s_ns1` | n/a |

`pw-dump` renders F3's value as JSON `true` and F4's as the string `"FALSE"`
(gst passes structure values through as written). \*F2's node reports
`suspended` at the 0.5 s sample while the file grows — a per-sample artifact,
recorded as-is.

## 3. Target-loss ladder (`receipts/loss.json`, 4 families × 3 reps)

Event: `pactl unload-module <index verified against r91s_ns1>` at t≈1.20 s;
0.15 s sampling of file bytes + `pw-cli info` state + `pw-link -l` blocks.
Every unload returned rc=0 with the index gone.

| family | bytes at loss | after | node state | post-loss links | 3/3 |
| --- | --- | --- | --- | --- | --- |
| F1s `pw-record --target r91s_src1` (remap-source, no prop) | 237612 / 229420 / 385068 | **flat** (r0 flat from t≈2.0) | `running` → `idle` | none to any source | frozen 3/3 |
| F2 `pw-record -P stream.capture.sink=true --target r91s_ns1` | ~278572 | **grows** to 925740/925740/929836 | stays `running` | `…SPDIF__sink:monitor_* → …:input_*` | re-link 3/3 |
| F3 `pipewiresrc` + capture.sink prop | 204844 | **flat 204844** | `running` → `idle` | `[]` — never | frozen 3/3 |
| F4 F3 + `node.dont-reconnect=false` | 204844 | **flat 204844** | `running` → `idle` | `…SPDIF__sink:monitor_* → gst_r91_src_override:input_*` | re-link, still frozen 3/3 |

F3 reproduces the r81 curve exactly (0 → 65580 → 135212 → 204844 → flat), and
the header leg pins the corrected constant (`§0.6`).

## 4. Client-recovery discriminator (`receipts/recover-inloop.json`, 3 reps)

Per rep: seat sinks `r91s_ns1`+`r91s_ns2`; `pw-play` 997 Hz tone → NS2
(`tone_state.state="running"`); F3-shaped gst capture from NS1; unload NS1 at
1.2 s; at t≈2.21 s `pw-link r91s_ns2:monitor_F* gst_r91_src_default:input_F*`.

- frozen before the manual link: **yes** 3/3 (bytes 204844 flat from 1.27 s).
- manual link present after: **yes** 3/3 (blocks `r91s_ns2:monitor_FL |-> gst_r91_src_default:input_FL` + FR).
- resumed after: **no** 3/3 (bytes 204844 → 204844 through 4.9 s; state stays `idle`).
- link-state capture in the receipt is empty (the `pw-dump` inside the sample
  failed under load) — link **presence** is witnessed by the `pw-link -l`
  blocks, link **state** remains unmeasured `[?]`.

## 5. Falsification list (what was tried that could have killed each claim)

| claim | falsifier attempted | outcome |
| --- | --- | --- |
| gst capture node carries `node.dont-reconnect` | 3 fresh reps, `pw-dump` + `wpctl inspect` | **confirmed** (F3, stable) |
| gst sink carries it too | F5 census | **falsified** — absent; sink source has no flag |
| the override prop lands | F4 census | **confirmed** — literal `"FALSE"` on the node |
| WP ignores a `false` value | F4 loss | **falsified** — WP re-links (link present post-loss) |
| the re-link resumes the client | F4 + manual-link recover | **falsified** — no data either way |
| no-prop capture links to a sink name | F1 3 reps | **falsified** — 44 B, no link |
| r85's zeros shape is the universal source-loss shape | 3 stage reps + 3 argv variants (no name / rate flags / `-n`) | **not reproduced** — freezes with `running→idle`; conflict named `[?]` |
| the frozen header is `0x7FFFF000` | direct hex read | **falsified** — `0x7FFF0024`/`0x7FFF0000` |
| a gst tone into a null-sink feeds it | `diag_src.py` | **falsified** — node stays `suspended` (pw-play tone runs); side finding, recorded |
| the seat perturbs host state | census before/after every stage | only own modules/nodes; defaults unchanged; no `r91` residue at exit |

## 6. Author directives

**Verbatim-ready cells** (each ≥3 reps, byte-stable, exact argv in the receipts):

1. Prop witness: `pw-dump` a live capture node and read
   `node.dont-reconnect` — expect `true` for `pipewiresrc`, absent for
   `pw-record`, absent for `pipewiresink`. (`receipts/props.json` F3/F1/F5.)
2. Freeze repro with the corrected constant: F3 argv, unload the target's
   module at t≈1.2 s → file flat at `204844`, `riff-size 0x7FFF0024`,
   `data-size 0x7FFF0000`, stderr empty, process alive. (`runs/header/H1_r0`.)
3. Policy-gate discriminator: F3 vs F4 argv; F3 post-loss links `[]`; F4
   post-loss link to the default sink monitor, **file still flat**.
4. Re-link control: F2 argv → grows through the loss (925740 B class).
5. Client-stickiness: recover arm — manual `pw-link` to a live seat monitor
   after freeze; expect link present + no byte growth.
6. Connect law: F1 argv → 44 B / suspended / no link (do not confuse with the
   r85 source-target zeros shape).

**Bimodal / envelope cells** (do not arm as a single shape):

- F1s source-loss shape: freeze here vs zeros in r85's receipt. Arm it with
  *both* bytes and node state recorded and treat the shape as leg-conditional
  until the r91 author settles §7.2.
- "Why re-link ≠ resume": the *observable* (link present, no data) is
  verbatim-ready; the *cause* is an envelope — do not assert a pw_stream
  internal without the state witness.
- `stream-properties` precedence: F4 shows the prop lands and wins over the
  flag, but a post-connect `pw_stream_update_properties` variant was not
  tested.

## 7. Remaining unknowns

1. `[?]` Why the gst capture element never resumes even with an active link
   (Gate B internals). Needs a pw_stream-state witness or a `GST_DEBUG` run.
2. `[?]` The F1s zeros-vs-freeze conflict with r85 (`s3e-vsrc-loss.json`).
   Argv variants tested here all freeze; the discriminating variable is not
   argv (node.name, rate flags, `-n` all freeze 3/3 total). Candidate
   variables named: unload path in that harness, session epoch, or a re-link
   to the still-alive master.
3. `[?]` Link state (and negotiated format) of the WP-created post-loss link —
   presence is measured, state is not (pw-dump inside the sample failed).
4. `[?]` WP info-level decision trace (`"handling item"`, `"dont-reconnect,
   not moving"`) is not emitted at the default log level; enabling it needs a
   daemon log-level change (operator decision, out of scout budget).
5. `[?]` `keepalive-time>0` on the gst src would resend the last buffer instead
   of freezing (source-read prediction) — untested designed arm.
6. `[?]` Whether a re-appearing target *by name* (reload `r91s_ns1`) re-arms
   the stalled gst node — untested.

## 8. Contention ledger + exit state

| window | contact | effect |
| --- | --- | --- |
| whole window | foreign lanes: `r79lb_*` (null sinks `…_1141702`, taps `b05_garbage_tap`, `b06_zero_tap`, `b07_prop_false_tap`, `b12_source_sinkprop`, `c02_second_sink[_tap]`, `cm4_m_bare_tap`, pw-record `/tmp/capture-r79-*`), `gst_r81_bnd_cap` (r81-boundary lane), `r78fol_*` (SPDIF-monitor tap) | read-only contact; my link listings carry their rows; no foreign object touched |
| 17:06–17:08 | this seat: ~30 bounded legs, 4 `module-null-sink` + 2 `module-remap-source` load/unload cycles, all index-verified | own residue zero; two ~0.5 s tone emissions into seat-owned sinks only; **no tone ever reached a host sink** |
| whole window | `~/.local/state/wireplumber/stream-properties` | this seat added its stream-property rows (same class of residue every round leaves; no CLI can delete) |
| exit | `pactl list modules short \| grep r91` = 0; `pw-dump` r91 nodes = 0; no r91 processes; defaults SPDIF/Line unchanged; the only module delta vs entry is a sibling's `r79lb_ns_b2_1141702` | clean |

## 9. Artifacts & provenance

`corpus/live/r91-scout/` (untracked, 5.8 MB): `probes/driver.py` (stages
census/props/loss/recover-inloop), `probes/diag_src.py`/`diag_src2.py`/
`diag_src3.py` (bounded diagnostics), `probes/hdr_check.py`, `probes/audit.py`;
`receipts/{props,loss,recover-inloop,summary}.json` + 8 census files;
`runs/<stage>/<leg>/{receipt.json,combined.log}`; `sources/` with
`SOURCES.md`, the four fetched `.c` files, `SOURCES.sha256`, `WP-LUA.sha256`;
`manifest.sha256` (94 files) and `RECEIPTS.md`.

Key receipt shas (prefix): `receipts/props.json 82112a37c8204975`,
`receipts/loss.json 4b0cac03ece14a79`,
`receipts/recover-inloop.json 6bf2410406d6b6ca`,
`receipts/summary.json eb7778e9f6581206`; header leg
`runs/header/H1_r0/receipt.json`. Upstream sources: `gstpipewiresrc.c
0e2248a9051b46cf…`, `gstpipewiresink.c 8659aa72b5e265e7…`, `pw-cat.c
0b8d05ce84149e8f…`, `stream.c 3699792e732ec7a2…`.

*scout leaf — measured and read, not judged.*
