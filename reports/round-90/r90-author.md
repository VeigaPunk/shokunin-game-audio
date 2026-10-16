# r90 author — the WirePlumber store / pulse-module / pw-link / format lattice

Implementation of the round-90 move: an insertion-only `wpstate` family in
`corpus/fixtures/measure_audio.py` (appended after the r89 `pwprof` block,
before `def main()`), wired as `--probe-wpstate-r90`. **Four entries, 60
legs.** Every armed law is an r90-boundary-surviving claim
(`reports/round-90/r90-boundary.md` §0); the scout's falsified claims are
re-armed at the boundary's corrected values and named where the correction
*is* the law.

## Files changed

- `corpus/fixtures/measure_audio.py` — +2182/−2 (the only deletions are the
  two shared-line splices the wiring requires: the `mode` select and the
  receipt `suffix`; the argparse row and the dispatch block are pure
  insertions — the r86–r89 convention).
- `corpus/live/r90-author/receipts/*.json` — one live receipt per entry per
  battery (untracked). Every exit-signature claim in this report (rc, error
  string, stderr class, sha, id) is readable there without walking the run
  dir.
- `corpus/live/measure_audio-wpstate-r90.lock` — fixed-path family lock
  created at runtime (untracked, the r84 F1 3-seat convention).
- `corpus/live/runs/20261016T085347601935Z-wpstate-r90/` — green receipt #1.
- `corpus/live/runs/20261016T085628919120Z-wpstate-r90/` — green receipt #2.
- `corpus/live/runs/20261016T085112273969Z-wpstate-r90/` — a **superseded
  revision's** battery (2 real failures: the vanished-target fallback and a
  `k_w_late` counting bug in the leg, not in the law). Kept as honest
  history; **not** one of the two green runs.
- `reports/round-90/r90-author.md` — this file.

**Editing provenance.** No `lsp` device was available for this tree (the
seat's tool surface exposes no language-server session, and the file is a
32k-line single-module script with no server answering it), so the
additions were made by hand: the family body was authored in a scratch file
and spliced before `def main():` with a fixed-anchor insertion script, and
the two shared lines (`mode` select, receipt `suffix`) plus the argparse row
and dispatch block were spliced at unique anchors. The result was verified
by `ast.parse` on the final bytes and by running the battery.

Nothing committed. **No `pactl set-default-sink` / `set-default-source` was
ever issued**; the live default sink stayed
`alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink.29` throughout.

## Conventions carried over

- Namespace `r90a_<role>_<pid>` (`r90a_ns_`, `r90a_ns2_`, `r90a_ns3_`,
  `r90a_ns4_`, `r90a_nso_`, `r90a_la_`/`lb_`/`lc_`, `r90a_late_`,
  `r90a_mc_`, `r90a_tun_`), private role key `r90arole<pid>` on every
  pw-play follower.
- Fixed-path lock `corpus/live/measure_audio-wpstate-r90.lock` (flock, never
  `$TMPDIR`); `TMPDIR=~/Projects/shokunin/tmp` for all runs.
- Name-verified teardown: re-read `pactl list modules` immediately before
  firing and unload only the index whose args carry our `sink_name=`; a
  surviving `r90a_*` node is destroyed by id via `pw-cli destroy`; final
  sink/node/module census armed (`sinks_gone`, `own_nodes_after`,
  `own_modules_after`).
- Every spawned process is its own session leader, bounded by
  SIGTERM→SIGKILL process-group escalation. Volatile ids/seqs scrubbed in
  recorded text; `stdout_token` keeps the RAW first token for id parsing.
- r90-local error classes checked before the inherited r89→r88→r87→r86
  chain: `wpstate_no_entity`, `wpstate_entity_exists`,
  `wpstate_invalid_arg`, `wpstate_conn_refused`, `wpstate_not_loaded`,
  `wpstate_io_error`, `wpstate_enum_failed`, `wpstate_setparam_failed`,
  `wpstate_unlink_failed`, `wpstate_link_failed`,
  `wpstate_missing_ports`, `wpstate_fetch_failed`.

## The two harness laws this round added

1. **The debounce measurement is fresh-key by construction.** The r90
   scout's headline "a pulse-protocol volume write lands in ≤0.01 s" was a
   *stale-row read* on a key reused across stages (boundary §1). Every write
   leg here uses `_wpstate_r90_key(tag)` = `r90a_<pid>n<wallclock-nonce>_<tag>`
   — a key no seat has ever written — and `w_create`/`w_pulse`/`w_target`
   each assert the key's PRE value is absent before the write (`key_pre`,
   armed as a `fresh-key guard` failure). A stale read can no longer
   masquerade as a fast write.
2. **A cold read is not absence — the settings read retries once.** The
   first battery measured `wpctl settings` returning **rc −11 (SIGSEGV)** with
   zero rows, followed by `Setting 'device.routes.default-sink-volume' not
   found`, in the same window; both reads were clean on the immediate
   re-read. An empty or crashed read is recorded as an *attempt*, retried
   once after a 0.8 s settle, and both attempts are stored
   (`w_settings.attempts`, `w_cross_volume.attempt`). This is load-bearing
   evidence, not a papered-over flake: **run 2 of the final bytes caught it
   live** — `attempt 1: exit_code −11, entries 0` → `attempt 2: rc 0, 25
   entries` — and the run stayed green on the retry with the crash preserved
   in the receipt.

## Entries and legs

### 1. `wpstate_store_r90_probe` — the settings + store lattice (15 legs)

- `w_settings`: `wpctl settings` → **25 rows**, every row carrying
  Id/Name/Desc/Type/Default/Value, type histogram
  `{Boolean: 17, Float: 5, Integer: 1, String: 2}`, and **all 25 at their
  built-in Default** (`Value == Default`, Float range suffix stripped) —
  the boundary's C1, and the direct evidence that no `settings` file is in
  play. `w_settings_flags`: `-d/--delete`, `-s/--save`, `-r/--reset` all
  present in the help text.
- `w_meta`: the pw-dump Metadata twins — exactly **one** 25-key scalar
  object (live `sm-settings`) and exactly **one** 25-key descriptor object
  (schema), each **key-for-key equal to the CLI's 25 ids**. This is the
  boundary's cross-witness; the ids are recorded (`live [36]`,
  `schema [34]`) but the *armed* claim is the set equality, never the id.
- `w_state_dir`: `~/.local/state/wireplumber/` holds **only**
  `default-nodes` + `stream-properties`; a `settings` file **must not**
  exist (armed).
- `w_cross_volume`: `device.routes.default-sink-volume` == `Value: 0.064`
  (armed). The default sink node's live `channelVolumes` are **recorded, not
  armed** — that is operator/sibling-mutable state; the measured delta was
  **3e-06** against the operator's SPDIF sink, reproducing the boundary's C2
  live.
- `w_create` / `w_props` / `w_pulse` / `w_target`: the four write paths, each
  on a fresh key, each armed into the **coalescing band [0.5 s, 3.0 s]**:

  | leg | path | run 1 | run 2 |
  | --- | --- | --- | --- |
  | `w_create` | stream creation → row | 1.852 s | 1.053 s |
  | `w_props` | `pw-cli set-param Props {volume:0.5}` | 1.058 s | 1.061 s |
  | `w_pulse` | `pactl set-sink-input-volume 50%` | **1.483 s** | **1.057 s** |
  | `w_target` | `pactl move-sink-input` → `target` | 2.588 s | 1.645 s |

  The pulse command itself returned in **4 ms** in both runs — and the row
  still landed ~1.0–1.5 s later. `w_pulse` arms the two halves of the
  boundary's correction explicitly: the command is fast, the *store write is
  not*, and a change **inside** the band is reported as the stale-row class
  the scout mistook for a ≤0.01 s write.
- The field split (boundary C5 second half, armed): the pulse path writes
  `channelVolumes: [0.125, 0.125]` and leaves `volume: 1.0`; the `pw-cli`
  path writes `volume: 0.5` and leaves `channelVolumes: [1.0, 1.0]`.
- `w_replay_fields` (C6): a replay of the pulse-written key shows live
  `channelVolumes [0.125, 0.125]` and `volume 1.0` — the stored field only.
- `w_replay_target` (C7): a replay with no `--target` links into the stored
  sink (2 edges, both channels) — and `w_explicit_target` (C7 new edge)
  shows an explicit `--target` winning: **2 edges into the explicit sink, 0
  into the stored one**.
- `w_optout_stream` / `w_optout_device` (C8): `state.restore-props=false`
  produces **no row** in 3.0 s / 2.5 s while the paired **control row lands
  in the same window** — the control is armed, so the opt-out legs cannot
  pass vacuously.
- `w_vanished_target` (C7/P7): **recorded, not armed — see §"Boundary
  correction that did not survive"**.

### 2. `wpstate_pmod_r90_probe` — the pulse module namespace (15 legs)

- `m_control`: a plain `module-null-sink` round trip (rc 0 + id → sink
  enumerated → name-verified unload rc 0 → sink gone).
- `m_phantom` (C12): `module-tunnel-sink server=127.0.0.1:1` returns **rc 0
  + an id** whose **module row is never held by my module** at any of 8
  args-aware probes (0/30/60/120/250/500/1000/2000 ms), with no node and no
  sink. `id_recycled_by_foreign` is recorded: in **both** green runs the
  phantom id was observed **held by a foreign module** during the probe
  window — the recycled-index hazard the boundary §3.2 named, witnessed
  live. This is why the leg witnesses liveness by the **module row**, never
  by the bare id.
- `m_unassignable`: `pactl unload-module 4000000001` (pre-checked absent from
  the module table) → **rc 1 `Failure: No such entity`**. This is the
  recycle-safe way to witness the error class — a raw unload of a *free*
  phantom id is refused by design.
- `m_unix`: `server=unix:/tmp/r90a_nope.sock` → **rc 1 `Connection
  refused`** (a unix socket fails synchronously; no phantom).
- `m_zeroconf_discover` → rc 1 `No such entity`; `m_zeroconf_publish` →
  rc 0, the module row carries my marker arg, unload rc 0 — the split the
  scout found, re-armed.
- `m_stub_stream_restore` / `m_stub_device_restore` / `m_stub_always_sink`
  → **rc 1 `Failure: Entity exists`**; `m_stub_unknown` → rc 1
  `No such entity`.
- The by-name vehicle (C13), on `module-loopback` **only after a
  zero-foreign pre-check** (`_wpstate_r90_loopback_arm`; a foreign row, or an
  arm that does not reach exactly two own rows, means **no fire** and a named
  `coverage_blocked`):
  - `m_byname_control`: two own loopbacks → **one** by-name unload → **0**
    remain, my null sinks alive;
  - `m_byname_prefix` (`module-loopb`), `m_byname_nodename` (a sink name),
    `m_byname_unknown` (an unknown module name): all **rc 0 with the error
    only on stderr** (`Failed to unload module: … not loaded`) and **nothing
    removed** (count still 2). Matching is exact, never a prefix, and rc is
    not a validity witness.
  - `m_byname_final` re-cleans the vehicle.

### 3. `wplink_r90_entry` — the `pw-link` grammar and unstated modes (24 legs)

Every counting leg rebuilds a **known** link set first (`k_reset`), so no
"first pair only" claim can pass on ordering luck.

- Single-pair grammar (C14): `k_connect` 1 link; `k_bulk` (`A B A2 B2`)
  → **first pair only**, 2 links, rc 0; `k_dup` → **rc 255 `File exists`**
  and the count unchanged; `k_two_ids` (`-d id1 id2`) → **rc 255 and nothing
  unlinked**; `k_single_id` → rc 0, exactly one link gone; `k_bulk_d`
  (`-d A B A2 B2`) → first pair only, 2 → 1; `k_reversed` → rc 255;
  `k_glob` → rc 255. `k_ids` parses `pw-link -I -l` and arms that the LINK
  id is the first token of the `|->` row.
- `-w` (C15, refined): `k_w_valid` rc 0 on an existing pair; `k_w_missing`
  **blocks** (killed at the 3.0 s bound); `k_w_late` returns **rc 0 at
  1.526 s / 1.527 s** — ~26 ms after the port appeared at 1.5 s, with the
  link witnessed on the specific late→L3 edge. `-w` is a
  wait-for-creation primitive, not a hang.
- `-p` (C17): `k_p_foo` lands `foo=bar` **on the Link object** (armed);
  `k_p_passive` returns rc 0, the link forms, and **no `link.passive` prop
  is visible** (armed as the negative, with the vacuity guard that the link
  must exist).
- Listing (C16): `k_list_slot` arms the slot-bound leak (the one-argument
  `-i <pat>` prints the other side's inputs); `k_list_filtered` arms the
  two-argument `-i '' <pat>` form filtering them out; `k_o_pattern` arms
  `-o <pat>` filtering; `k_l_pattern` arms that `-l <no-match pattern>`
  still prints rows.
- `k_t` / `k_t_live`: `pw-link -t` prints **nothing** — with and without a
  live stream attached (the scout's named unknown, closed negative; the
  live half also arms that the seat stream was alive at the probe).
- `k_m`: bare `-m` → rc 255 `missing output and input port names to
  connect`; `k_m_stream` (`-m -l`) streams (3279 B) and blocks to the bound.
  `k_v`: `-v -l` prints port properties (armed `>= 2` rows; 38 in run 2).

### 4. `wpformat_r90_entry` — the EnumFormat/Format lattice (6 legs)

- `f_rest`: on a **never-negotiated** sink the node `EnumFormat` sha is
  `1735b4739ef7` (1128 B); the node `Format` is **not enumerable** (0 B) and
  the **port** `Format` refuses with `res:-5 (Input/output error)` (armed via
  the error class, not the text).
- `f_mid48`: mid-stream the node `EnumFormat` is **byte-identical**
  (`1735b4739ef7`), the node `Format` is `91f7342230f7` (863 B), the port
  `Format` is `5a828addfad7` (456 B), and the **stream node** `Format` is
  `e718690a7ce2` (1247 B) — all four armed.
- `f_setparam_sink` / `f_setparam_stream` (C21 + the boundary's new
  node-class split): the **same** pod on the live sink node → **rc 0**,
  stderr `res:-5 … set param id:4 … failed`, stdout echo **622 B**, link set
  unchanged, stream alive. On the live **stream** node → **rc 0, 622 B
  stdout echo, stderr 0 bytes**. The seal is node-class dependent and rc is
  not a validity witness in either direction.
- `f_44k`: the stream node's `Format` is `684a7c8dad24` while the sink
  node's stays `91f7342230f7` — file rate vs graph rate.
- `f_post`: after the stream ends the node `Format` is **sticky**
  (`91f7342230f7`), the port `Format` is unreadable again with `res:-5`, and
  `EnumFormat` has not moved.

## Evidence

- Implementation sha256 (both green runs are byte-identical to this file):
  `d9a07b14af4e605353b2b07e6fccff41ff0eb083c1d430fb58e7192b1fb276eb`
- Run 1: `corpus/live/runs/20261016T085347601935Z-wpstate-r90/measurements.json`
  — `failures: {}`; all four entries `coverage_blocked` empty; 60 legs.
- Run 2: `corpus/live/runs/20261016T085628919120Z-wpstate-r90/measurements.json`
  — `failures: {}`; all four entries `coverage_blocked` empty; 60 legs.
- Live receipts (run 1 / run 2 sha256 prefixes), under
  `corpus/live/r90-author/receipts/`:

  | entry | run 1 | run 2 |
  | --- | --- | --- |
  | `wpstate_store_r90_probe` | `0bd7081d162f6674` | `4ffa08082fe90716` |
  | `wpstate_pmod_r90_probe` | `f3d83e00c84875e3` | `f77b4eaafe1e36b1` |
  | `wplink_r90_entry` | `cb52c938048e4138` | `2173957959ba9c2c` |
  | `wpformat_r90_probe` | `64e370f12cbbba2a` | `35cb424c5dfe59a2` |

- Post-run census (after run 2, re-verified): **0 `r90a_*` modules**, **0
  `r90a_*` nodes**, **0 `r90a_*` sinks**, **0 `module-loopback` rows**, no
  owned `pw-play` processes; every `unloads[*].exit_code == 0`;
  `sinks_gone` all-true; `own_nodes_after: []` and `own_modules_after: []`
  in all four entries. The live default sink is unchanged.

## Boundary corrections actually encoded

- **One coalescing debounce ≈1.0 s after the LAST change**, shared by
  creation / pw-cli Props / pulse volume / target — the scout's "≤0.01 s
  pulse write" is dead, and the harness makes a stale read structurally
  impossible (fresh key + pre-value guard).
- **`unload-module <name>` is all-matching and rc-0-with-stderr** — armed
  on a zero-foreign vehicle, with prefix / node-name / unknown all armed as
  no-ops.
- **Phantom ids and immediate index recycling** — liveness is witnessed by
  the module row; the recycled-id-foreign-holder event is recorded live.
- **`pw-link` single-pair grammar, `-w` wait-for-creation, `-l` ignoring its
  pattern** — armed, each with a vacuity guard.
- **The mid-stream set-param seal is node-class dependent** (explicit `res:-5`
  on the sink node at rc 0 with a 622 B echo; silent discard on the stream
  node) — armed on the class, with the byte counts recorded.
- Volatile-but-recorded, never verdict inputs: ids, seqs, wall times, byte
  counts, loadavg, foreign driver names, the store row census.

## Boundary correction that did NOT survive (named, not armed)

`w_vanished_target`: the boundary measured "no link forms (3/3 quiet + 3/3
load) — no fallback to the default sink materialised within the 2.2 s
window" after a stored target's sink was unloaded. **Both author runs
measured the opposite**: the replay linked into the default sink (SPDIF).
The outcome is recorded as a named class (`outcome:
fallback_to_default`, with `edges_into_default` carrying the link objects)
and the leg arms only that the replay stream node actually existed — so a
"no link" reading can never be an artifact of a dead process. The store
write half of the leg (`target` reaches the store at 1.0–1.9 s) **is**
armed. Two seats, two outcomes: the restore hook's vanished-target path is
host/session-manager-state dependent, and the boundary's negative is not a
law. A replay-fallback lattice (repeat reps, target reappearance, a
non-default stored target) is the carry-forward.

## Remaining risks / blockers

- **Host-level blocker observed after the two green runs.** While preparing
  a third battery the shared PipeWire session went **unresponsive**: both
  `/run/user/1000/pipewire-0` and `/run/user/1000/pulse/native` **accept a
  connection but never send the server greeting**, `pw-cli`/`pw-dump`/
  `wpctl`/`pactl` all time out (60 s), while the daemon threads sit idle in
  `do_epoll_wait` with 0 queued connections and the host loadavg swung
  51 → 3.7. `pactl load-module` timed out at 15 s, which is exactly the
  `probe null sink … never enumerated` block one aborted battery recorded.
  This is **not** attributable to this seat: the daemon wedge outlived the
  killed batteries, no `r90a_*` object was left behind, and the wedge is
  visible to every client. **A restart of the shared daemon is an operator
  action and was not taken.**
- Because of that blocker the two green runs are on
  `d9a07b14af4e60…`, the revision immediately preceding one
  **recorded-only** counter fix: `store_at_*[own_keys]` matched keys on a
  bare `r90a_<pid>` prefix and therefore missed the seat's device-node rows
  (`Audio/Sink:node.name:r90a_ns_<pid>`). That counter is **never armed**;
  the accurate residue is measured directly from the store file instead
  (below). The fix is staged but unverified, so it is **not** in the shipped
  bytes — the twice-verified revision is.
- **Store residue** (the permanent class every round leaves; no CLI deletes
  stream-store rows): run 1 grew the store 6868 → 6884 rows and run 2
  6926 → 6941; the store file held **57 `r90a_`-tagged rows** at the final
  census (every object this seat created across the whole session, including
  the pre-battery recon legs — 5 stream keys plus device-node keys per
  battery, the rest from recon). `wpctl settings -d` covers
  settings keys, not the stream store.
- **The `wpctl settings` rc −11 SIGSEGV is unexplained.** It was caught by
  the retry discipline in run 2 of the final bytes (attempt 1 crashed,
  attempt 2 returned all 25 rows) and in one earlier battery; it never
  reproduced on a standalone invocation. Whether it is a `wpctl` defect, a
  settings-metadata race, or host-load induced is **not read**.
- **The vanishing-target fallback** (above) is characterised, not explained.
- **The `127.0.0.1:9` bimodality** the boundary named is not re-measured
  here (the port-1 phantom class is armed instead) — deliberately left as a
  named unknown rather than armed on one branch.
- **`-p '{"link.passive":true}'` invisibility** is armed, but whether `-P`
  / `link.passive` changes scheduling is still unmeasured (the scout's and
  boundary's shared open edge).
- **zeroconf-publish's actual registration** remains unconfirmed (the
  boundary's empty `avahi-browse` baseline was not re-taken here; the leg
  arms only load/unload and the marker arg).

## Contention disclosure (shared host)

- The batteries ran at host loadavg **54–58** with **3–5 sibling
  `fixture_runs`** live (`contention.fixture_runs` recorded per entry;
  `host_is_quiet: false` in every entry). Quiet/loaded is therefore a
  *relative* distinction, exactly as the boundary's ledger states; no arm in
  this family depends on the host being idle.
- Foreign objects observed live and never touched: sibling null sinks
  (`r91a_ns_3169589`, `r92a_dev_*`, `r93a_in`, `r93b_in`), a sibling
  `pipewire -c …/r99asmoke/conf/minimal.conf` and an `r100a-sbx` private
  instance with their own runtime sockets. Every census and sweep matched
  **only** this seat's `r90a_`-plus-pid names.
- One aborted battery (before the two green ones, on an earlier revision)
  loaded a `module-loopback` pair and was killed before its teardown: a
  name-verified sweep of the module table and the node graph was run
  afterwards and left **0 `r90a_*` modules, 0 `r90a_*` nodes, 0
  `module-loopback` rows**.
- The `w_vanished_target` replay has no seat target and *did* land on the
  operator's default sink in both green runs; the leg was switched to
  **digital silence** (`_loopback_r79_write_silence`, the r79 fail-closed
  rule) and records `content_witness: declined_shared_default`, so the leg
  stays topology-complete with zero shared-sink content. An earlier
  revision of the leg played the tag tone into SPDIF for ~2.2 s once —
  disclosed here as an unintended emission of this seat.
- `module-zeroconf-publish` was loaded for ~0.2 s per run with a seat
  marker arg and unloaded by id (rc 0); `module-tunnel-sink` was loaded
  against a dead port and self-destructed. Both are LAN-facing classes and
  are named as accepted risk.

**Verdicts here are seat-side; the canonical Rust runtime remains the only
judge.**
