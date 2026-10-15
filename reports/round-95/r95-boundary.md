# R95 boundary — the scout's JACK↔PipeWire laws under load, no-own-hogs, and varied axes

Seat: **BOUNDARY (leaf)**. Host `plazir27`, window **2026-10-15 20:52–21:09Z**
(17:52–18:09 local, UTC−3). Repo `~/Projects/shokunin/audio-shokunin` @ entry/exit HEAD
**`51a98e54`** — **zero tracked writes, nothing committed**; the only tracked file this seat
touched is none. Object namespace `r95b_*`; own PIDs/modules only (r95 sweep incident
precedent honored: `procs_matching` requires the seat binary *and* `r95b` in the cmdline;
final sweep `killed=[] unloaded=[]`).

The surface under attack is the r95 scout report (`reports/round-95/r95-scout.md`, tracked)
and the laws it proposes. Everything here was re-measured with **fresh processes**, an own
JACK client (`probes/r95bjack.c`, a namespaced copy of the scout's probe plus a new
`rtprio_poison` mode), under **two load conditions**:

- **Q** — no own hogs; foreign load only. load1 62.9 → 80.8 (the host was *never quiet*:
  ~60 foreign `yes` processes + sibling seats ran the whole window).
- **H** — 14 own CPU hogs (`r95b_hog_00..13`); load1 74.8 → 108.8.

**Headline: 3 laws falsified outright, 4 falsified-in-part/refined, 8 confirmed with
extensions; two mechanisms found that the scout missed (Dummy-Driver self-drive of an
unlinked JACK client; the `sink_properties` comma-parse artifact that produced the scout's
"restore-props" and "description" conclusions).**

---

## 1. What was replayed

`probes/r95bdriver.py` (own bounded runner: per-child wall cap + killpg +
`start_new_session`, `RLIMIT_CORE=0`, own tone synth, own Goertzel) re-ran the scout's
armed cells: citizen shape, port/flag mapping, whole-graph census, addressing matrix,
both byte witnesses, per-client/env/wrapper/cross quantum, the global metadata arm,
xrun control+stall, latency, RT-priority, transport, metadata, name projection — each
in Q and H, 3 reps where the scout used 3, fresh process every rep. On top of the replay,
independent axes were varied: **PipeWire rates/quantum** (256/512/2048 @48000, plus
44100 and 96000), **CLI flag order** (pw-jack, pw-play/pw-record `-P`, pw-link, pactl),
**default-node state** (process-scoped `PULSE_SINK`, explicit `--target`, paplay vs
pw-play), **sibling-seat presence** (censuses before/during/after), and two new
discriminating stages (`driverid`, `corner`, `bufsize1`). One read-only `ufo-labrat`
(frozen probeParent, exactly one child) independently read the fetched upstream source
for four mechanisms (§8).

---

## 2. Verdict table

Verdicts: **CONFIRMED** = law held in every armed rep of both conditions; **REFINED** =
core holds, the stated form is wrong/conditional; **FALSIFIED** = the stated form did not
reproduce and the receipts show a different law. Receipts are under
`corpus/live/r95-boundary/receipts/` (`{q,h}_<stage>.json`).

| # | scout's law (r95) | verdict | exact receipt evidence |
| --- | --- | --- | --- |
| 1 | No JACK server; a JACK client is a native PW client node (`client.api=jack`, `node.always-process=true`, group/category/role) | **CONFIRMED** | `{q,h}_shape` 3/3 each: `client.api=jack`, `node.group=group.dsp.0`, `media.category=Duplex`, `media.role=DSP`, `node.always-process=true`; `jackd`/`jack_lsp` absent; pipewire-jack `1:1.6.8-1`; libjack sha `34bbb09a…`; version `"3.1.6.8 (using PipeWire 1.6.8)"` (`q_env`) |
| 2 | Ports become PW ports with an alias triple; Physical/Terminal survive, CanMonitor does not | **CONFIRMED** | `{q,h}_shape` 3/3: `port.name=out`, `port.alias=r95b_shape:out`, `object.path=r95b_shape:output_0`, `format.dsp="32 bit float mono audio"`; `outp→port.physical=true`, `outt→port.terminal=true`, `outm→no prop` (`port.extra` null); monitor API rc 0/`monitoring_input=1`/ensure 0 with **0 links** |
| 3 | Whole-graph census; links by the **rendered** name; native `node.name:port` never resolves | **CONFIRMED + corner FALSIFIED** | census lists foreign nodes/ports (Q all=48/51/50; H 35/40/44; scout's 71 was window-specific) — rendered rc 0 + link 3/3 both cond, native not found rc 22 3/3, fill-alias rc 0 3/3. **Corner**: a sink whose `node.description == node.name` (space-form props) makes `r95b_t4:playback_MONO` resolve and connect rc 0 (3/3 Q, 2/2 H, `{q,h}_corner`) — resolution is by *rendered* name; the two forms coincide when description==name |
| 4 | Audio path byte-exact both directions, "byte-identical 3/3" | **FALSIFIED as stated** | `{q,h}_bytepath`: JACK→PW peak 0.5 exact, but capture frames 174080/175104/174080 (Q) and 175104/174080/174080 (H) → **2 distinct shas in Q, 3 in H** (Q: `1c53e9fb…`×2 + `a68a79e9…`; H: `966aa89f…`, `1c53e9fb…`, `07f0c0e8…`), rms 0.292449–0.294556, mag² 897130681.379 / 912488472.013. PW→JACK: peak 0.499969482 exact; Q rep2 differs (`in_nonzero` 71677 vs 71997, mag² 321109139.205 vs 323955146.781), H 3/3 identical. **Sample values are exact; the capture window is not stable across fresh processes.** |
| 5 | Period size is per-client `node.force-quantum` by default, and moves the graph quantum for other clients | **CONFIRMED** | `{q,h}_quantum` 3/3 each: inactive set(2048) rc 0 but read-back 1024; activated 2048 + node prop `force-quantum=2048`; live set(512) → `bufsize_after_set_active=512`, `bufsize_cbs` 1→2, `last_bufsize_cb_after=512`; second client B `bufsize_active=2048` 3/3; `clock.force-quantum` stays `0` throughout |
| 6 | `jack.global-buffer-size=true` writes `settings clock.force-quantum`; `set_buffer_size(1)` resets | **CONFIRMED + REFINED** | `{q,h}_global` 2/2 each: during `'512'`, after exit `'512'`, reset → `'0'`, only that key moved, B reads 512. **Refined**: `nframes==1→"0"` is **metadata-path only** — without the opt-in, `{q,h}_bufsize1` shows node prop `force-quantum="1"` and effective bufsize 4 (2/2 each); labrat read the same branch (`pwjack.c:5380-5395`) |
| 7 | `PIPEWIRE_QUANTUM=q/rate` and `pw-jack -p q` land as node props and yield that bufsize | **CONFIRMED + EXTENDED** | `{q,h}_quantum`: `512/48000`, `256/48000`, `2048/48000` → props and bufsize exact 3/3; `pw-jack -p 512` ≡ `-p512` (3/3). **Extended (rate axis)**: `512/44100` and `512/96000` land `force-rate` and the client *runs* at 44100/96000 (`srate_live`) 3/3 each — despite `clock.allowed-rates=[48000]`; `clock.rate` back at 48000 after every rep |
| 8 | xrun callback ignores client stalls; a spurious callback fires on the control arm | **REFINED / control arm FALSIFIED** | `{q,h}_xrun`: stalls (8×150 ms, 23–29×60 ms) → `xrun_cbs=0` and callbacks drop — client stalls invisible, confirmed. **But control `xrun_cbs=0` in 6/6 arms** (scout saw 1) and delayed values 0.0 (scout 0.004). Labrat source read: callback gates on the *driver* counter with a `c->xrun_count != 0` first-divergence guard — a control-arm callback implies a genuine driver-side divergence, not a startup artifact |
| 9 | RT-priority accessors return uninitialized stack garbage | **CONFIRMED + mechanism** | `{q,h}_rtprio`: plain runs → 6 distinct garbage values (e.g. `-1335310918`, `-1917501494`, `-1716969382`); **stack-poison control 6/6**: after poisoning 0xAA the accessors return `aaaaaaa4`/`aaaaaaa9`, after 0xBB `bbbbbbb5`/`bbbbbbba` (Q and H, 3/3 each); baseline sometimes reads the scout's `77/82`. Labrat confirmed the source path and corrected that `jack_client_real_time_priority` = `jack_client_max_real_time_priority - 5` |
| 10 | `jack_set_property` writes the `default` metadata keyed by the object's **registry id**, and rows die with the writer | **CONFIRMED** | `{q,h}_metadata` 3/3 each: live row `id:164 key:'r95b/key1' value:'value1' type:'text/plain'` (ids 164/201 Q, 138 H) while `jack_uuid_to_index` reports the serial (150607…/154118…); round-trip rc 0; missing key −1; rows `{}` after exit; `get_after_remove` still `value1` at 250 ms |
| 11 | Transport is a read-only projection: start/stop gate, locate/reposition inert | **CONFIRMED** | `{q,h}_transport` 3/3 each: state 0→0 on activate; start → state 1, frame advancing (23552 Q; 22528/22016/21504 H); stop → 0 frozen; `locate(123456)` rc 0 and `reposition` rc 0 leave the frame unchanged; linked `out_connected=1` |
| 12 | Latency is a local store deferred to the data loop | **CONFIRMED** | `{q,h}_latency` 3/3 each identical: default `[0,0]/[0,0]`; sets invisible pre-activate; after activate `[100,200]`/`[10,20]`, total 150; `recompute_rc=0` |
| 13 | Client name is projected from `node.description`; an override breaks exact-name opens (status 4) | **CONFIRMED + EXTENDED** | `{q,h}_nameproj`: `node.description="r95b_forced"` → status 4 (rc 3) 3/3 each; **new arms**: `node.description="r95b_info"` (== requested) → status 0 3/3; `node.nick` override → 0; `node.name` override → 0; a duplicate live client → second gets status 4 3/3. It is an exact-name **mismatch** check under `JackUseExactName`, not a server uniqueness check (labrat) |
| 14 | Unlinked JACK client runs while a driver is active, but is **idle with no driver** | **FALSIFIED (second half)** | `{q,h}_liveness` no-driver arm: **cb=76/76/76** in both conditions (driver-present also 76); `{q,h}_driverid` (no seat sink at all): scheduling driver = **Dummy-Driver** (`node.driver=true`, prio 200000) in 9/9 Q samples and 4/4 non-empty H samples, frames advancing; one rep shows a driver restart (frame counter → 2048). The always-process JACK node pulls the fallback driver itself |
| 15 | 52 of 218 declared `jack_*` functions are not exported | **REFINED (numbers)** | `q_env`: strict header count **217 functions** (218 includes the *type* `jack_port_t`), **51 not exported** (same classes: netjack/slist/adapter + `jack_error`/`jack_info`/`jack_log`/`jack_client_activate`/`jack_uuid_to_string`); 168 exports confirmed |

### Envelope cells the scout said to arm (checked)

| cell | verdict | evidence |
| --- | --- | --- |
| buffer size is dynamic | **CONFIRMED** | `bufsize_live` 256/512/1024/2048 across stages; H xrun control reps ran at **256** (cb 378 over 2 s) vs 1024 (cb 94) — never arm a constant |
| `jack_get_buffer_size` inactive = latency default | **CONFIRMED** | 1024 in every inactive read-back (18 arms) regardless of env/set |
| xrun count "1" is a startup artifact | **REFINED/FALSIFIED** | control 0/6 in this window; source shows a first-divergence guard, so no artifact is guaranteed — treat any count as a driver-counter divergence |
| `jack_get_property` after remove is stale | **CONFIRMED** | `value1` read back 250 ms after `remove_client_rc=0` (6/6) |
| latency getters pre-activation are 0/0 | **CONFIRMED** | 6/6, regardless of sets |
| `node.description` overrides break exact-name opens | **REFINED** | only when it *mismatches* the requested name; description==requested → status 0 (6/6) |
| `state.restore-props=false` leaves no `stream-properties` rows | **FALSIFIED (comma form)** | §3-F4: `sink_properties=state.restore-props=false,device.description=X` parses as **one** property `state.restore-props="false,device.description=X"`; rows are written per unique node name. Space-separated form parses to boolean False and leaves **no** row (2 arms, plus a live prop dump) |
| the two-property description form "loses the description" | **REFINED (same artifact)** | comma form: description falls back to `<name> Audio/Sink sink`; space form: description exactly `X` (live props) |

### Axes

| axis | result |
| --- | --- |
| **PipeWire rates/quantum** | 256/512/2048 quantum exact; **44100/96000 force-rate land and the client runs at that rate** (6/6 arms), `allowed-rates=[48000]` notwithstanding; graph rate back at 48000 after each arm (`settings_after` in `{q,h}_quantum`) |
| **CLI flag order** | `-P` props before vs after positional args identical (pw-play node `r95b_f1/f2` + `target.object=r95b_ns` + 2 links; pw-record 2 links) 2/2 each condition; `pw-jack -p 512` ≡ `-p512`; `pw-jack PROBE -p 512` → probe mode `-p`, rc 2 (wrapper flags must precede the command); `pw-link A B` rc 0 vs reversed rc 255 `No such file or directory`; `pactl load-module` arg order identical nodes 2/2 (`{q,h}_flags`) |
| **default-node state** | process-scoped `PULSE_SINK=r95b_ns2`: **paplay** (Pulse ABI) links to the seat sink 4/4 arms; **pw-play** (native) ignores it and links to the then-current global default 4/4; explicit `--target` honored 3/4 (one census race). **Global defaults churned mid-window by sibling seats** (hdmi-stereo.6 → SPDIF.5; SPDIF.24 → hdmi-stereo.99 + a `HiFi_7_1__Line__source.12` source) — see §5 (`{q,h}_defaultnode`) |
| **sibling seat presence** | armed cells (shape + rendered xconnect) held with siblings present, 2/2 each condition; foreign census during the window: `yes` 60–62, game-dev 5–6, godot 3–5, r99 5–6, r97b 1, r92b 0–2, run_battery 1–2 (`{q,h}_sibling`) |

---

## 3. Falsified / refined claims in detail

**F1 — "idle with no driver" (claim 14) is not a law.** With no seat sink and no links,
the unlinked JACK client's process callback ran at the full rate (cb=76 in 6/6 arms,
i.e. 1.6 s at 48 k/1024) in both conditions. `{q,h}_driverid` shows why: the client node's
`node.driver-id` resolves to **Dummy-Driver** (`node.driver=true`, `priority.driver=200000`)
in 9/9 Q samples and 4/4 non-empty H samples (2 further H samples were taken after the
client exited), and `jack_last_frame_time` advances (one rep shows the
driver restart, frames reset to 2048). The correct law: an unlinked JACK client is
scheduled whenever *any* driver is available, and the always-process node itself keeps the
Dummy-Driver running — so it is effectively never idle. The scout's observation was
probably a moment when their probe had already exited (their `pw-top QUANT 0` view is not
a live witness; my own `pw-top` samples also show QUANT 0 while callbacks run — `pw-top -b
-n 1` snapshots are not reliable for this).

**F2 — "byte-identical 3/3" (claim 4) is window-dependent.** The sample values are exact
(peak 0.5 JACK→PW; 0.499969482 PW→JACK), but the *capture window* is set by process start
and stop timing: 170/171 quanta captured in different reps, so whole-file sha256 and
whole-file Goertzel/rms differ (2 distinct shas in Q, 3 in H for JACK→PW; 1 differing rep
in Q for PW→JACK). The scout's 3/3 identity was a lucky alignment; arm the invariants
(peak, per-sample copy) and the window length, never the file hash.

**F3 — the control-arm xrun callback (claim 8) did not reproduce.** Control `xrun_cbs=0`
in 6/6 arms; delayed values 0.0 (scout: 1 and 0.004). The labrat's source read shows the
callback is gated on the *driver* activation's counter with a `c->xrun_count != 0`
first-divergence guard: a callback on a control arm means the driver really diverged once
in that window; it is not a startup artifact. The *client-stall invisibility* half of the
claim is solid (8×150 ms and 23–29×60 ms stalls → 0 callbacks, 6/6).

**F4 — the scout's `stream-properties` conclusion is a parse artifact.** The scout's
`pactl load-module ... sink_properties=state.restore-props=false,device.description=X`
argument is parsed by `pw_properties_new_string` with **no comma splitting**: the live node
carries `state.restore-props = "false,device.description=r95b_t1"` (string), so the
restore-props hook never sees `false` and writes a row per unique `node.name`. The scout's
battery left only one `r95s_ns` row because every leg reused that name; the 3 manual sinks
used unique names. The **space-separated** form
(`sink_properties=state.restore-props=false device.description=r95b_t3`) parses to boolean
`False` and leaves **no row**, and yields `node.description` exactly `r95b_t3`. This also
explains the scout's "two-property form loses the description" side finding — same artifact.
Consequence for this seat: 9 new `r95b_*` rows in
`~/.local/state/wireplumber/stream-properties` (8 null-sink names + one paplay app row),
disclosed in §5; they are the r90 class (no CLI deletes them).

**F5 — claim 15's counts.** 218 "declared functions" includes the type `jack_port_t`
captured by the regex; strict: **217 declared, 51 absent, 168 exported** (`q_env`).

**F6 — "the native form never resolves" (claim 3) has a corner.** With a correctly-parsed
sink whose description equals its node name, the string `r95b_t4:playback_MONO` *is* the
rendered name and resolves + connects (3/3 Q, 2/2 H). The law is "resolution uses the
rendered name (`node.description:port`); the native form fails only when it differs".

**F7 — "`jack_set_buffer_size(1)` is the reset" (claim 6) is metadata-path only.**
Without `jack.global-buffer-size`, the node path writes the raw value:
`node.force-quantum="1"` and the effective bufsize is 4 (2/2 each condition); the reset
semantics (`→"0"`) belong to the metadata path the scout measured.

---

## 4. Confirmed with extensions (compact)

- Claims **1, 2, 5, 7, 10, 11, 12, 13** reproduced 3/3 in both conditions with the exact
  scout values (see table); claim **3** reproduced plus the corner; claim **9** reproduced
  *with mechanism* via the stack-poison control (0xAA/0xBB patterns come back verbatim,
  6/6); claim **6** reproduced plus the bufsize1 nuance.
- **Load did not break the laws**: every confirmed cell held at load1 ≈ 80 (Q) and ≈ 80–108
  (H); the two falsifications are structural (driver-id, parse artifact), not load-induced.
- The graph's **dynamic quantum** was observed live (256 in H xrun reps 1–2, 1024/2048
  elsewhere), and callback rates track it (cb 378 vs 94) — consistent with the scout's
  "arm a current value plus the callback" envelope note.

---

## 5. Contention ledger + disclosed perturbations

| window | contact | effect |
| --- | --- | --- |
| whole window | **foreign load**: ~60 `yes` processes (PIDs 2316xxx/3268xxx/3288xxx, PPID 1537, 36–50 min old) — **not this seat's**; sibling seats `r92-boundary` (`b2_clamp.py`, ended ~21:02Z), `r99-scout` probes, `r90-author` godot battery, an `r97b` process, game-dev-3d battery (waiting for load<30, never fired), a namespace-blind `grep` sweep | read-only contact; my loadavg receipts carry it; no foreign process/object was killed or modified |
| whole window | foreign nodes/streams in the graph: r92b/r93b/r96b/r98b null sinks & filter chains, `pacat`→`r96b_ns`, `pw-play`/`pw-record` streams | my census receipts carry their rows; nothing foreign was linked to or unloaded |
| ~21:05Z and ~21:08Z | **foreign default-node churn**: global Default Sink/Source changed `hdmi-stereo.6 → SPDIF.5` (Q) and `SPDIF.24 → hdmi-stereo.99` + a `HiFi_7_1__Line__source.12` source (H), with WirePlumber `.N` re-registration suffixes | my defaultnode arms are measured against a *moving* default; each arm records its actual links; I never issued `pactl set-default-*` or `wpctl set-default` |
| 21:04:23Z + 21:04:27Z (Q), 21:07:20Z + 21:07:25Z (H) | **own disclosed host mutation**: `settings clock.force-quantum='512'` for ~2.4 s per rep (global arm) | restored to `'0'` and verified each rep; no other metadata key moved (`moved: ['0:clock.force-quantum']` only) |
| quantum env arms | **own disclosed excursion**: per-client `node.force-rate` 44100/96000 for ≤1 s per arm (6 arms) | client-local; `clock.rate`/`allowed-rates` unchanged after each arm; graph returned to 48000 |
| defaultnode arms | **own disclosed contact**: silent (all-zero) streams linked to the then-current host default sink for ~1.2 s in the pw-play control/env arms | no audible content (silence); no tone ever reached a host sink |
| whole window | **own load**: 14 `r95b_hog_*` CPU hogs during H (started/stopped by the driver, `killed=[]` at exit) | disclosed by design; H loadavg receipts carry the counts |
| exit | `~/.local/state/wireplumber/stream-properties` | **9 new `r95b_*` rows** (r95b_probe_ns, r95b_ns, r95b_ord1, r95b_ord2, r95b_ns2, r95b_dbg_ns2, r95b_t1, r95b_t2, r95b_dn_client) from the F4 artifact; 4 scout rows pre-existing; the space-form sink `r95b_t3` left none. Not deletable by CLI (r90 class); left in place and disclosed |

---

## 6. Exit state (both conditions)

`{q,h}_verify`: `clock.force-quantum=0`, `clock.rate=48000`, **0 `r95b` modules, 0 `r95b`
processes, 0 `r95b` nodes/ports**; final sweep `killed=[] unloaded=[]`; no `pactl
set-default-*` ever issued; tracked tree untouched (`git status` clean for all tracked
paths; only untracked files created: this report + `corpus/live/r95-boundary/**`).

Note on the one tracked-dirty path an auditor will see: `corpus/fixtures/measure_audio.py`
(+ `.pyc`) was **already dirty at entry** (the scout recorded the same) and is being
actively rewritten by a *sibling* seat during this window (its diff is the sibling's r83
pw-cat PROPS-PARSER ledger; mtime moved at 21:09:10Z). This seat never read, imported,
executed, or wrote that file — its own synth/Goertzel are inside `r95bdriver.py`.


Artifacts: `corpus/live/r95-boundary/` (59 files; `manifest.sha256` 59/59 verified OK;
`RECEIPTS.md` index; `probes/{r95bjack.c,r95bjack,r95bdriver.py,r95banalyze.py}`;
`runs/{q,h}_battery.log`, `runs/{q,h}_axes.log`, `runs/{q,h}_summary_extract.json`).

---

## 7. Remaining unknowns / blockers

1. **Blocker (condition)**: a genuinely quiet host was unavailable — foreign load stayed
   60–80 for the whole window, so "quiet-ish" here means only *no own hogs*. All Q receipts
   carry the foreign load; absolute quiet-host values for the falsified cells (especially
   F1) could not be produced on this host.
2. **Blocker (baseline)**: sibling seats changed the *global default node* mid-window; a
   stable default-node baseline is impossible while they run. My defaultnode arms record
   the actual links per arm instead.
3. `valgrind` is absent, so no independent uninitialized-read detector; the stack-poison
   control is the substitute (and is stronger for this purpose: it returns the pattern).
4. Whether the scout's original `xrun_cbs=1` control observation was a real driver xrun or
   a different graph state cannot be reconstructed (their window is gone). The mechanism is
   source-confirmed; the count is window-dependent.
5. Why the Dummy-Driver self-drive sometimes lags (first driverid rep cb=38, one frame-counter
   reset) needs driver-side instrumentation; the *fact* of self-drive is 12/12 samples.
6. True unit/scale of `xrun_delay` (inherited unknown; my readings were 0.0).
7. `stream-properties` rows remain (r90 class); the correct restore-props syntax is now
   known but the scout's 4 rows + my 9 cannot be deleted by CLI.

---

## 8. Labrat fold (frozen probeParent — exactly one child, advisory, read-only)

One `ufo-labrat` was dispatched with four source-mechanism hypotheses against the scout's
fetched 1.6.8 sources (`corpus/live/r95-scout/sources/`). All four **CONFIRMED**, with three
corrections now folded in:

- **H1 xrun**: callback gates on the driver counter; the `c->xrun_count != 0` guard
  *suppresses* the first divergence → the scout's "spurious startup callback" framing is
  wrong (folded into F3); client-side stalls only bump `activation->xrun_count`/`xrun_delay=0`
  and cannot reach the callback (`pipewire-jack.c:2031-2036, 2070-2073`).
- **H2 rtprio**: `min/max` are never written on the `-ENOTSUP` path (thread_utils_impl has
  no `get_rt_range`); accessor = `max-5`, not `SPA_MIN-1` directly (`:7572-7580`, `:3454-3460`,
  `thread.h:89-95`). My poison control is the dynamic proof.
- **H3 buffer size**: two branches confirmed; `nframes==1→"0"` is metadata-only
  (`:5380-5395, :4491`) — folded into F7.
- **H4 name projection**: status 4 is set by a projected-vs-requested **mismatch** under
  `JackUseExactName`; prefix (`app/str`), `filter_name`, and dedup `-%d` all feed `c->name`
  (`:3837-3871, :4536-4541`) — folded into claim 13 and the duplicate-name arm.

*Leaf seat — measured, replayed, and read; not judged.*
