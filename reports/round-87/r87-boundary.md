# R87 boundary — falsification of the r87 scout under load and host-state variation

**Seat: BOUNDARY (executor-class, leaf; frozen probeParent).** Host `plazir27`,
lane `~/Projects/shokunin/audio-shokunin`. Window **2026-10-15 20:04–20:19 UTC**
(17:04–17:19 UTC−3). Tree @ HEAD **`1abd9549`** (the scout report cites
`a2616f73`; the tree moved between rounds — **no file this seat touched is
tracked**). Toolchain re-verified: PipeWire **1.6.8**, pactl 17.0-98-gb096,
kernel 7.2.3-arch1-3, Python 3.14.7.

**Discipline.** Zero tracked-file edits, no commits, no `git add`. Every audio
object this seat created is named **`r87b_*`** (sinks `r87b_ns`, `r87b_ns2`,
`r87b_kill`; streams `r87b*`; `pw-mididump` renamed to `r87b_mdump` via
`PIPEWIRE_PROPS`). Every module unload re-verifies its own `sink_name=` line at
that index immediately before the call; **only pids this seat started were ever
signalled** (`OWN_PROCS`/`HOGS` registries + a `/proc` scan restricted to
`r87b_` with the harness itself excluded — no pattern sweep). One host-global
mutation was made and reversed: a **~10 s `pactl set-default-sink r87b_ns`**
during the host-state battery (disclosed §4/§7; restored and verified
byte-for-byte by `pactl get-default-sink`). Exit state (20:18 UTC): **0 `r87b`
modules, 0 `r87b` nodes, 0 `r87b` pids, default sink = SPDIF, 0 hogs**
(`receipts/final-cleanup.json`; one unload needed a retry — see §7).

**Labrat.** The single permitted `probeParent` labrat was dispatched once for a
static binary-identity/option-surface hypothesis. Its substrate exposed **no
exec tooling**: it returned `UNSTABLE: no exec tooling available` with zero
evidence and zero side effects. Every measurement below is seat-owned.

**Harness.** `corpus/live/r87-boundary/r87b_lib.py` (primitives),
`r87b_probe.py` (stages quiet/load/host/cleanup), `r87b_supp.py`,
`r87b_supp2.py`, `r87b_supp3.py`, `r87b_supp5.py`, `r87b_reparse.py`.
≈120 bounded legs; receipts `receipts/*.json` + raw logs `runs/*.pwcli`
(+ raw pw-cli dumps `receipts/*.raw.txt`). Two receipt-hygiene artifacts are
disclosed: (a) `links_for` counts each link twice (once per port header) — all
verdicts use peer port names, not counts; (b) the `module_idx` fields in
`b0-inventory.json` are racy (both sinks showed one index at load time) — every
actual unload re-verified the line first, so no unload was ever misdirected.

---

## 0. Verdict table (scout claim → verdict → sharpest measured fact)

| # | r87 scout claim | verdict | sharpest measured fact |
| --- | --- | --- | --- |
| 1 | `pw-play/pw-record/pw-midiplay/pw-midirecord` are symlinks to `pw-cat`, sha `1cd5f309…`; `pw-mididump`/`pw-cli` distinct | **CONFIRMED** | 4/4 symlinks → `/usr/bin/pw-cat`, all sha `1cd5f30904400ab2…`; mididump `0410b8c1…`, cli `d37463f8…` |
| 2 | playback lattice ≡ capture lattice; `target.object` > `node.target` > `--target`; serial resolves, `object.id` doesn't; unresolvable → current default sink | **CONFIRMED in substance / FALSIFIED as the stated precedence chain** | all 25 lattice legs reproduce, **but `--target` beats `node.target` in both directions** and a garbage `--target` never falls through to `node.target` (§2) |
| 3 | no duplex; mode flags last-wins; flags override argv0; bare `pw-cat` refused; `-m` orthogonal | **CONFIRMED + extended** | `-p -r -p`→Output, `-r -p -r`→Input; `-m -r`→`Stream/Input/Midi` + `input_1`; no leg ever carried both `input_*` and non-monitor `output_*` |
| 4 | pw-cli Props mutate mid-stream at exact ratio; Format sealed while running | **CONFIRMED (quiet + under load; streams *and* sinks)** | monitor RMS `8485.01 → 2121.28` = **0.2500×**, mute `0.0`, restore `1.0000×` — identical in 1 quiet + 2 hog reps; Format write silently discarded on a running stream (`S16LE/48000` unchanged) **and on the sink** (`F32P/48000` unchanged) |
| 5 | no FOREIGN gate on the default socket; refusal classes pinned | **CONFIRMED** | `enum-params` + identical-value `set-param Props {volume:1.0}` on WP-owned HDMI sink accepted, 0 errors, value unchanged; every unknown-id verb → `unknown global '99999999'` |
| 6 | midi `--target` is dead; manual port pin carries real events | **CONFIRMED** | 5 target forms + prop path + `autoconnect=false` → `no target node available`+`res:-2`; pin rc=0 → **45 B** SMF with C4/E4 on/off, quiet **and** under load |
| 7 | remote/RAOP surface absent; refusal classes uniform | **CONFIRMED** | 34 native modules, 9 network-capable, **0 raop/zeroconf**; `pactl load-module` ×4 names all `Failure: No such entity`; `pw-cli load-module` ×4 all `Could not load module`; `-R`/env all `Host is down` |
| 8 | cold-registry artifact (`unknown global` pre-sync) | **CONFIRMED** | zero-warmup `info <live id>` → `unknown global`; **1.4 s warmup still sufficient at loadavg 112** (state `idle`), 2.5 s likewise |
| 9 | `create-node` object is session-bound; `destroy` of a module-owned node unloads the module | **CONFIRMED + linger carve-out** | default: present in-session, **gone after quit**; `object.linger=true`: **survives quit** until destroyed; `destroy` of `r87b_kill` node → module gone |
| 10 | `send-command Suspend`/`Pause` → `state:"suspended"` | **CONFIRMED + resume direction closed** | `Suspend`→suspended, `Pause`→suspended; **`Resume` refused** (`unknown node command type: Resume`); `Start` accepted but state stays `suspended` (no-op on this sink) |
| 11 | bare `pw-mididump` live node + pin carries events | **CONFIRMED with intermittent-startup caveat** | 2/2 fresh reps: node `r87b_mdump`, stdout `Note On C4 vel 96 … Note Off E4` via pin; **one earlier rep exited rc=0 with no node/stdout** (scout's own s5 leg also recorded empty stdout; its claim came from s8) |
| 12 | *(not claimed)* `--volume` | **NEW LAW** | spawn-time `--volume` honored exactly and unclamped: 0 → RMS `0`, 0.5 → `0.500×`, 1.5 → **`1.500×`** (help says 0–1.0) |

§10 falsification-list items 1–13 were all attacked: 12 of 13 stand (with
sharpened scoping); the precedence chain in item 2's parent claim breaks (§2).

---

## 1. What survived verbatim (fresh processes, own sinks, own prefixes)

Arm table A1–A26 replayed one-to-one (map in `receipts/`):

- **A1/A2/A3** `p_own` → `r87b_ns`; `pw-cat --playback` identical; bare
  `pw-cat` rc=1 `error: one of the playback/record options must be provided`
  + usage, no node.
- **A4** `--capture`/`--duplex` rc=1, stderr `pw-cat: unrecognized option
  '--capture'` / `'--duplex'` + usage (full-stream capture; the scout's
  receipt only had the usage tail — same class).
- **A5/A6** `-p -r`→`Stream/Input/Audio`, `-r -p`→`Stream/Output/Audio`,
  `pw-play -r`→Input, `pw-record -p`→Output; extended: `-p -r -p`→Output,
  `-r -p -r`→Input.
- **A7** `--target r87b_no_such_target` → live default (`SPDIF`); **A8**
  prop-beats-flag both directions, plus a third leg where the prop wins to a
  *different valid sink* (`-P target.object=r87b_ns2 --target r87b_ns` → ns2).
- **A9** serial resolves (new serial `118652` → ns), `object.id` (own `125`,
  live HDMI `175`) → default. Extended: prop-path `target.object=<serial>` →
  resolves; `target.object=<id>` → default; scout's stale serial `41546` →
  default.
- **A10** `--target 0` → node published, links `{}`.
- **A11** `r87b_ns.monitor` and the Line **source name** → default; extended:
  source **serial** → default; `.monitor` + `stream.capture.sink=true` →
  default (the capture-side prop does not unlock playback `.monitor`).
- **A12** `PIPEWIRE_PROPS` braces → ns; extended: brace-less form accepted.
- **A13** live Props mutation — numbers in §0/§3.
- **A14** Format sealed — §0; plus sink and unlinked variants (§5).
- **A15** `send-command Suspend` → `state:"suspended"`.
- **A16** `destroy <own stream>` → node gone, `pw-play` exits rc=1
  `stream node N unconnected`.
- **A17/A18** foreign enum + identical-value write accepted; unknown-id verbs
  all `unknown global`.
- **A19** midi targets dead (name/serial/objid/garbage/prop) — identical
  `no target node available` + `res:-2`; `--target 0` / `autoconnect=false`
  publish unlinked.
- **A20** pin + `aplaymidi -p 14:0` → 45 B SMF, payload
  `90 3c 60 / 80 3c 00 / 90 40 60 / 80 40 00`; `pw-midirecord --target
  Midi-Bridge` (no pin) → 26 B skeleton on refusal.
- **A21/A22** `pw-mididump` live via pin → timestamped C4/E4; offline file
  parse rc=0.
- **A23/A24** `pactl load-module module-raop-discover` ×3 `Failure: No such
  entity`; `pw-cli load-module libpipewire-module-raop-discover` etc. ×4
  `Could not load module`.
- **A25** `-R`/`PIPEWIRE_REMOTE` ×3 `pw_context_connect() failed: Host is
  down`; `-R pipewire-0 --target 0` stalls (timeout at 10.0 s).
- **A26** zero-warmup `info <live id>` → `unknown global '<id>'`; warm info
  works.

Byte-stability: the refusal legs are byte-identical across reps after pid/id
scrub (pactl ×3, remote ×3, env ×3, capture/duplex ×1 each with full strings).
Routing legs are stable across quiet/load/host states (§3/§4).

---

## 2. The one falsified law — the §1.2 precedence chain

Scout §1.2 states precedence **`target.object` (prop or env) > `node.target` >
`--target` flag > absent**. The scout measured `target.object` vs flag (both
directions) and `node.target` alone — it never measured `node.target` vs
`--target`. This seat did:

| leg (`receipts/b1-lattice.json`, `b1y-supplement2.json`, `b1x-supplement.json`) | argv | links to |
| --- | --- | --- |
| `x_nt_vs_flag` | `-P node.target=r87b_ns2 --target r87b_ns` | **`r87b_ns`** (flag) |
| `y_nt_rev` | `-P node.target=r87b_ns --target r87b_ns2` | **`r87b_ns2`** (flag) |
| `y_garbage_flag_nt` | `-P node.target=r87b_ns2 --target r87b_no_such_target` | **SPDIF** (default — no fall-through to `node.target`) |
| `y_three` | `-P target.object=r87b_ns2 -P node.target=r87b_ns --target r87b_ns` | `r87b_ns2` (target.object wins) |
| `x_zero_prop` | `-P target.object=r87b_ns --target 0` | **unlinked** (`0` is a hard no-link, beats the prop) |
| `x_auto_false` | `-P node.autoconnect=false --target r87b_ns` | **unlinked** (autoconnect=false beats the flag) |
| `p_pb1/p_pb2/p_pb3/y_tobj_vs_flag` | prop vs flag both directions + different valid sink | prop wins 4/4 |
| `x_env_swap/x_env_garbage/x_env_vs_nodetarget` | env `target.object` vs `-P target.object` / `-P node.target` | **env wins 3/3**, including when env's value is garbage (→ default) |
| `x_prop_twice` | `-P target.object=ns -P target.object=ns2` | ns2 (last `-P` wins) |

**Measured precedence:** `--target 0` (hard no-link; also `autoconnect=false`)
> env `target.object` > `-P target.object` (last wins) > `--target` >
`node.target` (consulted only when `target.object` is absent; a garbage
`target.object` falls to the **default sink**, never through to
`node.target`) > absent. `--target` behaves like a pre-prop default for
`target.object` that later prop sources override.

Everything else in §1.2 stands: serial is first-class (new serial and prop
serial resolve; stale serial falls back), `object.id` never resolves (own id,
HDMI id, prop id all fall back), every unresolvable/wrong-class string lands
the **current** default sink (proven by moving the default — §4).

---

## 3. Load battery — 24 seat hogs on top of an already-loaded host

`receipts/l1-load.json`. External load was extreme: `loadavg` **103.2 before**
my hogs, **112.8 during** (24 `python3` busy loops, pids recorded, all killed
after), **148.9 after**. Foreign actors at the time included `r93-scout`
probe batteries, `r97-scout`'s **own PipeWire daemon** (separate socket,
`r97s-pipewire.conf`), `r94-boundary` (game-dev lane), `r89-simplifier`
battery, and foreign nodes `r89b_* r90b_* r93s_* r96s_* r98s_*` (§7).

| check | under load | quiet reference |
| --- | --- | --- |
| `l_own` / `l_garbage` / `l_pb2` / `l_serial` / `l_objid` / `l_zero` | ns / SPDIF / ns / ns / SPDIF / unlinked | identical |
| `l_mode_pr` / `l_mode_rp` | Input / Output | identical |
| `l_cold_nowarm` | `unknown global '125'` | identical |
| `l_warm_1.4` / `l_warm_2.5` | `state:"idle"` / `state:"idle"` | 1.4 s warmup holds |
| `l_mut1` | 8485.01 → **2121.28 (0.2500×)** → 8485.01 → **0.0** → 8485.01 | exact same numbers |
| `l_mut2` | 8485.01 → **2121.28 (0.2500×)** → 8485.01 → **0.0** → 8485.01 | exact same numbers |
| `l_fmt_sealed` | write echoed, `enum Format` = `S16LE/48000` unchanged | identical |
| `l_midi_notarget` | `no target node available` + `res:-2` | identical |
| `l_midi_pin` | pw-link rc=0, **45 B**, C4/E4 both present (offline parse sec 0/2/3/4) | identical payload |

The mutation witness is *exact* under load: the same RMS values to two
decimals across quiet and both hog reps (`post_format` differs at the 4th
significant digit: 8484.8 quiet vs 8485.17/8485.07 load — still 1.0000×).
No verdict-bearing claim weakened under load.

---

## 4. Host-state variation

`receipts/h1-host.json`, `b1x-supplement.json`.

- **Default sink moved (disclosed global mutation, ~10 s):**
  `pactl set-default-sink r87b_ns` (rc=0; `get-default-sink` = `r87b_ns`,
  WirePlumber did **not** reassert during the window). Then:
  `h_garbage` (`--target r87b_no_such_target`) → **`r87b_ns`**;
  `h_mon` (`--target r87b_ns.monitor`) → **`r87b_ns`**;
  `h_own` → `r87b_ns`. Restore to SPDIF rc=0, verified;
  `h_garbage_restored` → **SPDIF**. The fallback target is the *current*
  default, not the hardware sink — confirmed by moving it.
- **Suspended sink:** `send-command Suspend` → `state:"suspended"`; a playback
  leg still links to the suspended sink (`h_own_suspended` → ns); after that
  leg the sink reads `state:"idle"` again — observed sequence is consistent
  with resume-on-connect (Resume itself is refused, §5), not with a
  command-driven resume.
- **Serial/id churn:** scout's serial `41546` and id `84` no longer exist;
  the stale serial falls back, and the *current* serial (`118652`) resolves —
  serials are per-object, not recycled (consistent with r85's monotonic-serial
  law).
- **Name collision:** with a stream node deliberately named `r87b_ns` next to
  the sink (`collision.objects_while_colliding` = Audio/Sink id 125 +
  Stream/Output/Audio id 116), a third process `--target r87b_ns` linked to
  **`r87b_ns:playback_FL`** — the sink wins name resolution.
- **Load-state variation:** covered by §3 (the "quiet" battery itself ran at
  loadavg 40–60).

---

## 5. Unstated-mode hunting (scout-untested surface)

All receipts as cited; every claim here is measured, not inferred.

1. **`--volume` (spawn-time) is real and exact** (`b2-modes.json`
   `volume_legs`): monitor RMS 1.0→8485.01, 0.5→4242.43 (`0.500×`),
   0→0, **1.5→12727.60 (`1.500×`, no clamp despite "0-1.0" in help)**.
2. **`pw-cat -m -r`** → `Stream/Input/Midi`, port `input_1` (`b1x` ports).
   `-m -p` → `output_1`; `-M ump -m -p` → same shape; `-M ump` offline parse
   of an SMF is textually identical to the default parse.
3. **`-s` (sysex)** with an SMF: publishes `Stream/Output/Midi` + `output_1`
   and keeps running (>10 s, no error) — it accepts the SMF as a sysex stream.
4. **`-c` (midi-clip)** with a plain SMF: **new refusal class**
   `midiclip: can't read midi file '…': Invalid argument` +
   `error: open failed: Invalid argument` + usage, rc=1 (parallel to the
   scout's `dsdfile:` class, which reproduces exactly).
5. **`object.linger=true` on `create-node`** survives client disconnect
   (`present_after_quit=true`, then destroyed by id → gone), whereas the
   default create-node dies with the session — closes the scout's unknown #4
   for the create path.
6. **`send-command` resume direction closed:** `Resume` → `unknown node
   command type: Resume`; `Start` accepted (no error) but the sink stays
   `suspended`; `Pause` ≡ `Suspend`.
7. **Format on an unlinked/pre-negotiation stream:** the write is echoed
   client-side, but there is **no enum witness** — `enum-params <id> Format`
   fails server-side `res:-2 (No such file or directory): enum params id:4
   (Format) failed` while `enum-params <id> Props` succeeds (3 fresh
   sessions, `b3y`, `b3z`). Scout unknown #2 stays **unresolved by this
   method** (not contradicted).
8. **Format on a sink (running driver node):** sealed like a stream —
   negotiated `F32P`(518)/48000 before and after a valid 44100/S16LE write
   (`b3-fmt-sink.pwcli`).
9. **`set-param Latency { }`** on a sink → async refusal
   `res:-95 (Operation not supported): set param id:15 … failed`.
10. **`PIPEWIRE_PROPS` renames the `pw-mididump` node** (`r87b_mdump`) —
    useful for namespace discipline; bare name is `midi-dump` (tool-fixed).
11. **Interleaving hazard confirmed:** under heavy registry churn, a single
    long pw-cli session can swallow `info`/`enum` responses (only 1 of 4
    `state:` witnesses landed in one session); fresh sessions per command fix
    it (this is why §0 #10 and §5.7 use fresh sessions).

---

## 6. Refusal/class lattice — exact strings re-verified

| class | exact string (stderr unless noted) | where |
| --- | --- | --- |
| `pwcat_mode_required` | `error: one of the playback/record options must be provided` + usage, rc=1 | bare, `-m` only |
| `pwcat_unknown_longopt` | `pw-cat: unrecognized option '--capture'` / `'--duplex'` + usage | §1 A4 |
| `dsd_read_fail` | `dsdfile: can't read dsd file '<wav>': Invalid argument` + `error: open failed: Invalid argument` | `-d -p` on wav |
| `midiclip_read_fail` | `midiclip: can't read midi file '<smf>': Invalid argument` + `error: open failed: Invalid argument` | **new**, `-c -p` on SMF |
| `no_target_node_midi` | `stream node N error: no target node available` + `remote error: id=2 seq:9 res:-2 (No such file or directory): no target node available` | all midi target forms |
| `remote_host_down` | `error: pw_context_connect() failed: Host is down` | `-R`, env |
| `pactl_module_no_such_entity` | `Failure: No such entity` | 4 names, 3 reps |
| `pwcli_module_load_fail` | `Could not load module` | 4 native names |
| `pwcli_unknown_global` | `"<verb>: unknown global '<id>'"` | all verbs, both live-cold and bogus ids |
| `pwcli_cold_registry` | `unknown global '<live id>'` at zero warmup | A26, also under load |
| `pwcli_unknown_factory` | `@proxy:3` then async `res:-2 … unknown factory name nonexistent_factory_r87b` | §5 |
| `pwcli_factory_usage` | `res:-22 (Invalid argument): usage: factory.name=<factory-name> …` | §5 |
| `sendcommand_unknown` | `send-command: unknown node command type: <x>` (`Resume`, `0`, `bogus-cmd`) | §5 |
| `latency_unsupported` | `res:-95 (Operation not supported): set param id:15 (Spa:Enum:ParamId:Latency) … failed` | **new** |
| `format_enum_unlinked_enone` | `res:-2 … enum params id:4 (Spa:Enum:ParamId:Format) failed` | **new** |

---

## 7. Contention ledger + side effects

| time (UTC) | foreign actor | observation |
| --- | --- | --- |
| 20:04–20:08 | `r79lb_*` (round-79 loopback) 3 pid generations | present at recon, gone by first battery; `r80md_2389450_*` objects appear |
| 20:08 | `r82ff_2422178_*` (r82 fold seat) | `pw-record … --target SPDIF` leg live during inventory |
| 20:08–20:14 | `r86b_ns`; `paplay` on SPDIF; `Lavf63.1.101` (ffmpeg), `blender`, `pw-profiler`, `pactl` client churn | hundreds of async pw-cli events interleaved in my session logs (see §5.11); loadavg 40–60 |
| 20:14–20:17 | `r93-scout` batteries, **`r97-scout` own PipeWire daemon**, `r94-boundary` matrix (game-dev lane), `r89-simplifier` battery (game-dev lane) | loadavg 103 → 112 (with my 24 hogs) → 149; foreign nodes `r89b_* r90b_* r93s_* r96s_* r98s_*` |
| 20:17–20:19 | 44 foreign procs snapshot | host battery + supplements |

**My side effects:** the disclosed ~10 s default-sink swap (restored,
verified); one identical-value `Props {volume:1.0}` write on WP-owned
`alsa_output.pci-0000_01_00.1.hdmi-stereo`; reader-pins on `Midi-Bridge`
capture ports (reader only, die with my processes); `Suspend` on my own sink;
all `r87b_*` objects unloaded; 24 hogs killed by recorded pid. **Cleanup
nuance:** the first `pactl unload-module 536870928` returned rc=0 but the
module was still listed ~0.6 s later (loadavg ~145); a retry with the
index+`sink_name=` line re-verified succeeded. `r87b_ns2`'s module was already
absent at cleanup time (cause unobserved, not this seat's unload). Final
state: 0 `r87b` modules/nodes/pids; default sink SPDIF
(`receipts/final-cleanup.json` `post_retry`).

---

## 8. Classes added / refined by this seat

- **Falsified law:** `node.target > --target` → actually `--target >
  node.target`; garbage `target.object` never falls through to `node.target`.
- `--target 0` and `node.autoconnect=false` are **hard no-link switches** that
  beat `target.object`/`--target` props.
- env `PIPEWIRE_PROPS` **overrides** `-P` for the same key (3/3 legs);
  repeated `-P` keys: last wins.
- `pwcat_volume_spawn` — spawn-time `--volume` honored exactly, unclamped.
- `midiclip_read_fail` — new refusal class.
- `midi_record_node` — `-m -r` → `Stream/Input/Midi` + `input_1`.
- `sysex_mode_stream` — `-s -p` accepts SMF, publishes `Stream/Output/Midi`,
  runs indefinitely.
- `pwcli_linger_survives_session` — `object.linger=true` created node outlives
  `pw-cli`; default does not.
- `sendcommand_start_noop` / `sendcommand_resume_unknown`.
- `latency_unsupported` (`res:-95`).
- `format_enum_unlinked_enone` (`res:-2`; Props enum still works).
- `default_fallback_follows_current` — proven by moving the default sink.
- `name_collision_sink_wins` — sink beats same-named stream in `--target`
  resolution.

---

## 9. Remaining risks / unknowns / blockers

- **`set-param Format` on an unlinked stream** remains unwitnessed (no enum
  readback; server `res:-2`). The scout's running-state seal is intact; the
  pre-negotiation branch is **not measured**.
- **`pw-mididump` bare startup is intermittent under churn**: 1 of 3 seat
  attempts exited rc=0 with no node/stdout (scout's s5 leg shows the same);
  2/2 later reps + scout s8 succeeded. A single-shot mdump leg is not
  trustworthy under contention.
- **Suspend-cleared-by-connect** is an observed sequence (sink read `idle`
  after a stream linked), not a controlled experiment.
- **Foreign destructive verbs** (`destroy`/`send-command` on foreign nodes,
  `move-sink-input`) remain deliberately unexercised, as in the scout —
  `no_foreign_gate` predicts them allowed.
- **Host load is extreme** (sibling seats ran loadavg 40–149 through the whole
  window); all timings here are load-robust but the *exact* first-event delta
  in the pinned SMF varies (0x50–0x54 ticks across reps) — payload is stable.
- No blockers: cleanup verified, default restored, zero leftovers.

---

## 10. Evidence index

- `corpus/live/r87-boundary/r87b_lib.py`, `r87b_probe.py`, `r87b_supp.py`,
  `r87b_supp2.py`, `r87b_supp3.py`, `r87b_supp5.py`, `r87b_reparse.py`
- receipts: `b0-inventory.json`, `b1-lattice.json`, `b1x-supplement.json`,
  `b1y-supplement2.json`, `b2-modes.json`, `b3-cli.json`,
  `b3y-unlinked-fmt.json`, `b3z-fresh-sessions.json`, `b4-midi.json`,
  `b5-remote.json` (+`.raw.txt`), `b5x-supplement5.json`, `b6-foreign.json`
  (+`.raw.txt`, `-samevalue.raw.txt`), `l1-load.json`, `h1-host.json`,
  `reparse.json`, `final-cleanup.json`
- raw pw-cli sessions + monitor wavs + SMF captures under
  `corpus/live/r87-boundary/runs/` (e.g. `b3-mut-quiet.pwcli`,
  `l-mut-1.pwcli`, `mr_pin.mid`, `l_mr_pin.mid`, `b3-sendcmd.pwcli`)

*boundary leaf — measured, not judged; canonical runtime is the judge.*
