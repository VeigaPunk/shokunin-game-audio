# r88 author — bluetooth absent-class + pw-dump/pw-cli/pw-top witness-diff lattice

Implementation of the round-88 move: an insertion-only `btwit` family in
`corpus/fixtures/measure_audio.py` (appended after the r87 block, before
`def main()`), wired as `--probe-btwit-r88`. Three entries, 79 legs total.
Bluetooth is **vacuous by absence** on this host — no device was fabricated,
paired, or connected; every fabrication path is probed and asserted-refused.

## Files changed

- `corpus/fixtures/measure_audio.py` — +1772/−3 (the only deletions are the
  three shared-line splices the wiring requires: mutex list, mode select,
  receipt suffix; identical convention to r86/r87).
- `corpus/live/measure_audio-btwit-r88.lock` — fixed-path family lock created
  at runtime (untracked, same convention as the r86/r87 locks).
- `corpus/live/runs/20261016T072313132218Z-btwit-r88/` — green receipt #1.
- `corpus/live/runs/20261016T072341162452Z-btwit-r88/` — green receipt #2.
- `reports/round-88/r88-author.md` — this file.

Nothing committed.

## Conventions carried over

- Namespace `r88a_<pid>` (`r88a_ns_`, `r88a_ns2_`, `r88a_*_pt`), private role
  key `r88arole<pid>`.
- Fixed-path lock `corpus/live/measure_audio-btwit-r88.lock` (flock, never
  `$TMPDIR`); `TMPDIR=~/Projects/shokunin/tmp` for all runs.
- Name-verified teardown: re-read module args, unload only when `sink_name`
  matches; residual `r88a_<pid>` nodes destroyed by id; final sink/node census
  armed (`sinks_gone`, `own_nodes_after`).
- Never `set-default-*`; process groups bounded SIGTERM→SIGKILL.
- r88-local error classes checked before the inherited r87/shared tables
  (unmodified): `pa_sendmsg_noent`, `pwtop_connect_down`,
  `pwdump_invalid_opt`, `cli_enum_notimpl`, `cli_unsupported_type`.
- Volatile ids/serials/seq counters scrubbed in recorded text; parse-bearing
  legs keep a `stdout_raw`/`stderr_raw` verbatim channel (recorded, never
  armed).

## Entries and legs

### 1. `btabs_bluez_r88_probe` — absent class, pinned honestly (28 legs)

Stack alive + device present + audio class absent + every fabrication path
refusing:

- `bz_tree`/`bz_adapter`/`bz_media1`: hci0 Powered=true; Media1 advertises
  A2DP source+sink UUIDs.
- `bz_device`: the one device `dev_BC_C7_46_34_C5_66` is the DualSense —
  paired, `Connected=false`, Class 1288, `input-gaming`, UUID16 `1124`
  (HID) + `1200` (PnP) only; `audio_uuids=[]` — measured, not assumed.
- `bz_cards`/`bz_pactl_lines`/`bz_sinks`: zero bluez cards/sinks; the single
  `bluez|a2dp|sco` match in `pactl list` is the `session.services` line
  carrying `bluetooth.audio` — advertisement, not an object.
- `bz_midi_bridge`: `bluez_midi.server` (`factory api.bluez5.midi.node`,
  `Midi/Bridge`) — the live bluez5 object; arm asserts no Audio/* media class.
- `bz_loadmod_*`/`bz_sendmsg`: `module-bluez5-discover` and
  `module-bluez5-device` refuse `rc=1 Failure: No such entity`
  (`pa_module_noent`), both bare and with args; `send-message` refuses
  `pa_sendmsg_noent`. Module census before/after unchanged.
- `bz_setcard`: profile-set on a fabricated `bluez_card.*` name refuses
  `pa_module_noent`; `bz_setcard_bogusctl` proves the same text fires on a
  bogus profile against a real card (refusal text is non-diagnostic —
  the V3 confound as a first-class leg); `bz_setcard_validctl` is the
  positive control.
- `bz_create_*`: `pw-cli create-node` fabrications all return process rc 0
  yet create nothing — `.a2dp-sink`/`.sink` → remote `res:-2`
  (`pwcli_remote_enoent`), `.a2dp.source`/`.midi.node` → `res:-22`
  (`pwcli_remote_einval`); `bz_own_residue` asserts zero `r88a_`-tagged graph
  objects survived.
- `bz_spa_inventory`: 14 bluez SPA files (the boundary's correction of the
  scout's 15), `libspa-bluez5.so` + 8 `libspa-codec-bluez5-*`.
- `bz_spa_codecs_str`: boundary-surviving claim encoded — `strings` finds
  `spa.bluez5.codecs` and `"property bluez5.codecs '%s' is not an array"`
  (126 `bluez5.` strings, 0 standalone `bluez5.codecs` lines). The scout's
  absent-claim was *not* encoded; runtime device-specific semantics are
  vacuous without an audio device.
- `bz_find_module`: no `module-bluez5*.so` under `/usr/lib*`.

### 2. `witdiff_dump_r88_probe` — the witness-diff lattice (41 legs)

- `wd_setrule_*`: `pw-dump <K>` is the `{id==K} ∪ {serial==K}` set query —
  armed on own id, own serial, foreign id, foreign serial, with mid-leg
  churn re-census.
- `wd_no_nested`/`wd_mode_*`: membership is mode-invariant (default, `-R`,
  `-i 0`, `-s`); `-s` SPA form carries unquoted `id = N` /
  `object.serial = N`.
- `wd_cli_id`/`wd_cli_serial`/`wd_cli_dead`/`wd_silent_cli_enum`: `pw-cli
  info` is strictly id-keyed — serial-only and dead keys produce the
  `unknown global` message at rc 0; never a silent lookup, never an exit
  status.
- `wd_ls_serial`/`wd_ls_metadata`: `ls` exposes `object.serial` per object
  (serial resolution through `ls` works); `ls Metadata` returns **9 ids** vs
  `pw-dump`'s 4 (`extra=[35,37,38,41,42]`) and `info` on an ls-only id is
  silent rc-0 — the visibility split is armed, not asserted.
- `wd_propblock`: `ls` renders the flat `key = "v"` continuation layout;
  `info` renders the `* properties:` starred layout — two honest layouts.
- `wd_keyset_own`/`wd_keyset_dev`/`wd_types`/`wd_params_*`: dump and `info`
  publish identical prop *key sets* on Node and Device; dump keeps JSON
  types while `info` stringifies; param *names* agree while dump's `[]`
  marks unreadable values — key presence ≠ value availability.
- `wd_silent_*`/`wd_dead_serial`: `pw-dump <dead-id>`, `<abc>`, `<huge>`,
  dead-serial, and `pw-cli info <dump-visible-metadata>` are all silent
  rc-0 absences (recorded verbatim).
- `wd_dump_empty`/`wd_dump_two`/`wd_dump_color`/`wd_dump_neg`: `pw-dump ''`
  is the full census (id-set equals a bracketing census); multi-id returns
  the first match only; `--color=always` emits ANSI that breaks JSON;
  `-1` is the family's one loud `invalid option` refusal.
- `wd_info_all`: `info all` described 85 of 92 objects — the silent-omission
  class is measured (Metadata objects among the omitted).
- `wd_enum_*`: the numeric≡name law is armed on a *readable* param —
  `enum-params <id> Props` ≡ `enum-params <id> 2` byte-identical. The
  boundary's write-only asymmetry is encoded honestly: on the suspended own
  sink `Format` and `4` never return a pod (measured `silent`/`silent` in
  run 2; `remote res:-5`/`silent` in the dev run — the refusal path varies,
  the no-pod signature does not). `BogusXYZ` → `unknown param type`;
  `enum-params <client> Props` → `enum-params not implemented on object`.
- `wd_serial_law`: pactl's sink index **is** the native `object.serial` —
  6/6 sinks matched, 0 violations, own index follows.
- `wd_state3`: pactl/dump/cli vocabularies agree on the own sink's
  suspended state inside the tight window.

### 3. `pwtop_r88_probe` — the frame lattice (10 legs)

- `pt_n1`: exactly 1 frame, all rows `C` — the `-n 1` first-frame trap
  armed (12/12 rows).
- `pt_n3`: `-n 3` with bounded retry (frame count is advisory — a dev
  capture emitted 1 frame, boundary emitted 4); 3 frames
  `[C] → [I,S] → [I,S]` — first frame all-CREATING, last frame real
  states (9 S + 3 I), own sink row non-`C`.
- `pt_n0`: exactly 1 frame.
- `pt_nneg`/`pt_nabc`: run indefinitely, killed at the 4 s bound (infinite
  class, rc via harness kill, not a refusal).
- `pt_rbogus`: `-r` bogus remote → `pwtop_connect_down`
  (`Can't connect ... Host is down`) — the family's one loud failure.
- `pt_state_idle`: pactl `SUSPENDED` / dump `suspended` / cli `suspended` /
  top `S` — four-witness agreement, idle side.
- `pt_state_active`: a `pw-play` stream (`r88a_*_pt`, role key) drives the
  sink — pactl `RUNNING` / dump `running` / cli `running` / top `R` —
  agreement under load.

## Evidence

- Implementation sha256 (both runs identical bytes):
  `ad9d59b1e0dc5e2be4274f4966e571dabefed94076c06093eed1bf4cd2aef4c4`
- Run 1: `corpus/live/runs/20261016T072313132218Z-btwit-r88/measurements.json`
  — `failures: {}`, coverage_blocked empty in all three entries.
- Run 2: `corpus/live/runs/20261016T072341162452Z-btwit-r88/measurements.json`
  — `failures: {}`, coverage_blocked empty.
- Post-run census after run 2: zero `r88a` graph nodes, zero `r88a` sinks,
  zero owned modules, no `pw-play`/`pw-top`/`pw-cli`/`pw-dump`/`r88a`
  processes. (`r87t_ns` and `r84a_probe_548706` null sinks are pre-existing
  foreign residue — untouched.)

## Boundary corrections actually encoded

Dropped/weakened scout claims: `bluez5.codecs`-absent (refuted by strings),
15→14 SPA files, pactl-refusal-text-as-diagnostic (confounded — now a
first-class confound leg), the broad pulse/native state-disagreement law
(replaced by measured four-witness agreement), and the pulse-only ghost
(0/70 — not encoded). Newly discovered in dev and handled honestly: the
`Format`/`4` name-vs-number asymmetry on write-only params (EIO vs silent —
armed as "no pod" rather than ≡).

## Blockers

None. Non-blocking notes:

- `pt_n3`'s `-n` frame count is advisory by upstream design; the retry
  helper records `attempt` (1 in both green runs) so a real flake would
  surface as evidence, not hide.
- `wd_enum_fmt`/`wd_enum_num4`'s refusal path (silent vs remote `res:-5`)
  varies run to run on a suspended node — recorded as `outcome`, armed only
  on the no-pod signature.
- Two pre-existing foreign null sinks (`r87t_ns`, `r84a_probe_548706`) are
  another round's residue; left untouched per preserve-unrelated-work.
