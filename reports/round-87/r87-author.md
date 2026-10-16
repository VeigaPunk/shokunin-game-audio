# r87-author — the pw-cat/pw-midi*/pw-cli DEVICE-BINDING lattice

`--probe-pwbind-r87`, landed insertion-only in
`corpus/fixtures/measure_audio.py` (+2083/-3 lines; the 3 edited lines
are the flag mutex sum, the `mode` ternary and the `suffix` ternary —
append/prepend only, no prior family row touched). All claims are the
r87 scout's THIS-HOST measurements as CORRECTED by the r87 boundary;
falsified rows were dropped or re-armed at the boundary's values, never
the scout's. Host: plazir27, PipeWire 1.6.8, WirePlumber 0.5.17,
libpulse 17.0-98-gb096 protocol 35, Python 3.14.7, numpy 2.5.3.

## Guards (r76–r86 conventions inherited)

- **Namespace**: every owned object is `r87a_<pid>`-tagged
  (`PWBIND_R87_PREFIX`); sinks `r87a_ns_<pid>` / `r87a_ns2_<pid>`,
  taps `r87a_tap_/r87a_vrec_<pid>`, stream tags `r87a_<pid>_<leg>`,
  create-node objects `r87a_<pid>_adp/_ling`, mididump rename
  `r87a_<pid>_mdump` via `PIPEWIRE_PROPS`.
- **Role key**: `r87arole<pid>` — private per-run, never the shared
  `music` key.
- **Family lock**: `corpus/live/measure_audio-pwbind-r87.lock` — a
  FIXED lane path per the r84 F1 3-seat consensus (never `$TMPDIR`;
  cross-TMPDIR same-family runs must still exclude). Holder witness
  line `pid=<pid> ns=<ns> role=<role>`.
- **Name-verified teardown**: `_pactlmon_r85_unload_own` re-reads
  `pactl list modules short` immediately before unloading and fires
  only the index whose arg string carries OUR `sink_name=<name>` —
  captured module ids are never fired (recycling is measured). A
  residual census then destroys any surviving `r87a_<pid>` node by id
  via `pw-cli destroy` (a lingering create-node object is
  pactl-invisible) before the final sweep; `sinks_gone` and
  `own_nodes_after` are armed, and reader failures append to
  `coverage_blocked` instead of passing vacuously.
- Never `set-default-*`, never subject-0 writes, bounded process
  groups (SIGTERM then SIGKILL), monitor taps link-validated
  (`<sink>:monitor_* -> <tap>:input_*`) before the tone, foreign
  destructive verbs never exercised (deferred by scout AND boundary —
  recorded, unarmed).

## Entries and legs

### `pwbind_modes_r87_probe` — one binary + direction flags (loads nothing)

- `binaries` — pw-play/pw-record/pw-midiplay/pw-midirecord realpaths ==
  pw-cat (shared sha256 head); pw-mididump, pw-cli are distinct.
- Refusals to-exit: `m_bare`, `m_mflag_only`, `m_noflag_target` →
  `one of the playback/record options must be provided` (media mode is
  orthogonal to direction — `-m` alone still refuses);
  `m_capture`/`m_duplex` → `unrecognized option '--capture/--duplex'`
  (neither option exists — no duplex surface); `m_clip` →
  `midiclip: can't read midi file`; `m_dsd` → `dsdfile: can't read
  dsd file`.
- Last-wins direction (watch legs on `--target 0`, verdict =
  media.class + port shape): `m_p_r`/`m_r_p_r`/`m_play_r` →
  `Stream/Input/Audio` with `input_*` ports; `m_r_p`/`m_p_r_p`/
  `m_record_p` → `Stream/Output/Audio` with `output_*` ports — the
  flag pair overrides argv0 (pw-play -r captures, pw-record -p plays,
  extended triples keep last-wins). `m_midi_p`/`m_midi_r`/`m_ump`/
  `m_sysex` → `Stream/Output/Input/Midi` with `output_1`/`input_1`;
  `-s` stays running past EOF (armed).
- The never-duplex law is armed on every watch leg: no snap ever
  carries both `input_*` and non-monitor `output_*` ports.
- Recorded files of the record legs ({exists, bytes}) logged.

### `pwbind_target_r87_probe` — the routing precedence lattice (2 null sinks)

Each leg is a tagged `pw-play -P node.name=r87a_<pid>_<leg>` sampled
at (0.9 s, 1.7 s); the verdict is `consumers` = union of
`edges_out[].in_node` — link witnesses, never intent props.
`DEF` = `pactl get-default-sink` read at entry start; a mid-entry
default drift is itself a failure.

- Happy paths → `[NS]`: `p_own` (--target name), `p_cat`
  (`pw-cat --playback` — same lattice), `p_pb2` (prop overrides
  garbage flag), `p_nt` (node.target alone), `p_nt_vs_flag` (**flag
  beats node.target** — the boundary's correction of the scout's
  reversed claim), `p_serial` (--target object.serial),
  `p_prop_serial` (target.object=serial — serial resolves on both
  paths), `p_env`/`p_env_nobrace` (PIPEWIRE_PROPS braces and bare
  forms), `p_env_vs_prop` (env > -P).
- Second sink → `[NS2]`: `p_pb3`, `p_nt_rev`, `p_three` (prop > flag >
  node.target full chain), `p_prop_twice` (last -P wins).
- Default-landed → `[DEF]`: `p_garbage`, `p_pb1` (garbage prop beats
  VALID flag — prop wins then misses), `p_nt_garbage` (**garbage flag
  does NOT fall through to node.target** — the second half of the
  correction), `p_objid`/`p_prop_objid` (object.id NEVER resolves),
  `p_serial_stale`, `p_mon`/`p_mon_cs` (.monitor suffix is a name,
  not a source), `p_src_name`/`p_src_serial` (wrong-class Audio/Source
  name or serial), `p_env_garbage` (garbage env beats valid -P),
  `p_mediarole`/`p_capsink` (role/capture props are decoration),
  `p_empty`.
- Hard no-link switches (present node, `consumers == []`):
  `p_zero` (--target 0), `p_zero_prop` (0 beats target.object),
  `p_noauto` (node.autoconnect=false beats the flag).
- `p_coll` — a stream NAMED `r87a_ns_<pid>` collides with the sink:
  `--target` still lands `NS:playback_*` — the same-name stream does
  not shadow the Audio/Sink (`collision_objects` records both).

### `pwbind_cli_r87_probe` — pw-cli on live objects (1 null sink)

- `cold_nowarm` — `pw-cli` with `info <nid>` piped at t=0 fires the
  cold-registry artifact `unknown global '<nid>'`; `warm_control` —
  argv `info` on the same live id works (the contrast is armed).
- `unknowns` — info/enum-params/set-param/destroy/get-permissions on
  `99999999` all land `unknown global '99999999'`.
- `writes`+`regions` — the live-DSP mutation witness: monitor tap
  (link-validated) reads solo median **8192**, Props `{volume:0.25}`
  mid-stream → **2048.0** (ratio 0.25 exactly), `{volume:1.0}` → 8192,
  `{mute:true}` → **0.0**, `{mute:false}` → 8192. The scalar `volume`
  key IS live on a running STREAM (contrast r86's dead scalar on the
  null SINK — different subject node class). `props_unk` —
  `{no_such_prop:3}` parses to empty pod, rc 0, zero errors.
- `volume_legs` — spawn-time `--volume` through a shared tap:
  v100=8192, v050=**4096** (0.5), v000=**0**, v150=**12288** (1.5 —
  unclamped past the "0-1.0" help text).
- `fmt_stream` — enum-params Format on the RUNNING stream
  (S16LE/48000) → `set-param` with a valid pod (96000) AND `{}` →
  negotiated unchanged both times (silently discarded).
  `fmt_sink` — same seal on the sink (F32P/48000) while the player
  holds it running. `fmt_unlinked` — on a published-but-unlinked
  stream (held alive across the calls): `enum-params Format` → async
  `res:-2`; `enum-params Props` still reads.
- `sendcmd` — Suspend→suspended, Resume→`unknown node command type:
  Resume` (state stays suspended), Start→ACCEPTED no-op (still
  suspended), Pause→suspended, `0`/`bogus-cmd`→unknown-command class,
  no-args→usage refusal. `wake_after_suspend` — play-to-suspended-sink
  sequence recorded only (boundary marked resume-on-connect as an
  observed sequence, not a controlled experiment).
- `latency` — `set-param Latency {}` on the sink → async `res:-95
  (Operation not supported)`.
- `foreign` — WirePlumber-owned hdmi sink (candidates recorded):
  enum Props → volume 1.0; identical-value write `{volume:1.0}` →
  zero errors, post-enum 1.0 (no permission gate); `{no_such_prop:3}`
  silent drop; `BogusType {}` → `unknown param type`. Destructive
  foreign verbs unexercised by design.
- `destroy_stream` — `pw-cli destroy <stream id>` → node gone and
  pw-play exits rc=1 `stream node N unconnected`.
- `create_session`/`create_linger` — held-session `create-node
  adapter`: default factory lands session-bound (present in-session,
  GONE after `quit`); `object.linger=true` survives quit and dies on
  `pw-cli destroy`. `create_badfac` — `factory.name="no_such…"` →
  async `res:-2 can't create node`; `create_usage` — missing
  factory.name → `usage: factory.name=` (`res:-22`).
- `destroy_sink_module` — LAST leg: `pw-cli destroy <sink id>`
  unloads the WHOLE module (sink absent from pactl list, node gone).

### `pwbind_midi_r87_probe` — midi target-dead + pin + remote (loads nothing)

- `m_t_bridge`/`m_t_serial`/`m_t_objid`/`m_t_garbage`/`m_t_prop`/
  `m_t_nt` — EVERY target form on pw-midiplay is the same dead path:
  rc!=0 + `no target node available` + `res:-2` — midi does not bind,
  name/serial/id/prop all equivalent.
- `m_t_zero`/`m_noauto` — the only publishes: `--target 0` /
  autoconnect=false → `Stream/Output/Midi`, `output_1`, zero links.
- `pin` — `pw-link Midi-Bridge:capture_* -> r87a_<pid>_mr:input_1` +
  `aplaymidi -p 14:0` carries REAL events: `pw-midirecord` writes a
  **45 B** SMF containing both injected `0x90` note-ons and both
  `0x80` note-offs (armed on the raw bytes).
- `skeleton` — a target-refused midirecord still writes the **26 B**
  `MThd+MTrk+EOT` skeleton, no note payloads.
- `mdump_off` — `pw-mididump <smf>` rc 0 with `Note On` lines.
  `mdump_live` — armed only when a node publishes (boundary's startup
  flake); on both green runs the first attempt published
  `r87a_<pid>_mdump`, pinned, and printed Note lines — if it hadn't,
  the leg records `coverage_blocked`, never a single-shot pass.
- `pactl_raop`/`pactl_zc`/`pactl_bogus` → rc!=0 `Failure: No such
  entity` — one class for raop/zeroconf/bogus. `pwcli_raop`/
  `pwcli_zc`/`pwcli_null`/`pwcli_panull` → `Could not load module`
  (native pw-cli module loads never work, existing modules included —
  recorded). `remote_flag`/`remote_env`/`remote_cli` → rc!=0
  `Host is down` / `failed to connect: Host is down`. `remote_stall`
  — `-R pipewire-0 --target 0` connects then stalls unlinked (r78's
  law; recorded only).
- `remote_census` — zero remote/raop/zeroconf/airplay-named nodes in
  the graph; zero raop/zeroconf/airplay `.so` in
  `/usr/lib/pipewire-0.3` (avahi runs but nothing consumes it).

## Runs — green twice on identical file bytes

`measure_audio.py` sha256 (both runs):
`be31da679be229074690dc5157edcc122612560594baa8ba62a9b5ce26dd9516`

| run | receipt | receipt sha256 | verdict |
|---|---|---|---|
| A | `corpus/live/runs/20261016T070036115509Z-pwbind-r87/measurements.json` | `01f04d354f2186dbcf4bc984e2d62a49f378ea8ca2f810d79c7586797d1f1667` | `failures: {}`, `coverage_blocked: []` on all 4 entries |
| B | `corpus/live/runs/20261016T070305393338Z-pwbind-r87/measurements.json` | `2970c944375f2e3b8b6f3ab16bdd5a343521222844d9a3a044a0a7d9a974a655` | `failures: {}`, `coverage_blocked: []` on all 4 entries |

(Receipt bytes differ only in volatile fields — pids, node ids,
serials, wall times — per design; the arms are identical.)

Post-run host census after run B: `pw-dump` shows ZERO `r87a_*` node
names; `pactl list sinks/modules short` shows ZERO `r87a_*`; no
`r87a_*` processes; `sinks_gone` all True; `own_nodes_after` `[]`;
default sink `alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink.29`
and default source
`alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source.29` —
unchanged (the lattice reads the default, never writes it).

## Files changed (nothing committed)

- `corpus/fixtures/measure_audio.py` — +2083/-3:
  - `25452–25557`: family header — the corrected-claim inventory.
  - `25559–25582`: `PWBIND_R87_*` constants (namespace, NS/NS2/TAP/
    VREC names, private `r87arole<pid>` key, envelopes).
  - `25585–25617`: `_PWBIND_R87_ERR_CLASSES` — family-local classes,
    consulted before the r86→r84 chain, never prepended.
  - `25619–26082`: helpers — run/errclass/norm, pw-cli argv one-shots
    + held-session, watch legs + consumers verdict, fixed-path family
    lock, entry head, load_ns, name-verified teardown + residual
    destroy, SMF write/witness, pod parsers, state reader, bridge/seq
    probes.
  - `26095–27595`: the four entry functions.
  - `27634`, mutex sum, `28005–28028` dispatch (lock held to exit +
    4 measurement keys), `mode`/`suffix` ternaries.
- `corpus/live/measure_audio-pwbind-r87.lock` — the fixed-path family
  lock (untracked; remains after release by design, as prior locks).
- `corpus/live/runs/{3 dev, 2 green}-pwbind-r87/` — run receipts.
- `reports/round-87/r87-author.md` — this report.
- `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` — was
  already dirty before r87 (bytecode churn, not authored content).

## Blockers

None blocking. Non-blocking caveats carried (recorded, unarmed):

- Unlinked/pre-negotiation `Format` writes are unstable per boundary —
  only the res:-2 enum-refusal + Props-read is armed; no write arm.
- Foreign-node destructive verbs stay unexercised (scout+boundary
  both deferred) — only read/identical-value/unknown-key writes are
  armed on foreign objects.
- `pw-mididump` live startup is contention-flaky (boundary §9) — the
  live arm fires only on a published node and degrades to
  `coverage_blocked` instead of a single-shot pass.
- `wake_after_suspend` records the resume-on-connect sequence only —
  the boundary flagged it as an observed sequence, not a controlled
  experiment.
- `-R pipewire-0 --target 0` records the unlinked stall (r78's law),
  never armed as a refusal.
