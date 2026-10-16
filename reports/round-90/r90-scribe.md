# r90 scribe — custody audit of the f50cf66a landing

**Seat.** UFO-FSD `scribe` (custody only). **No verdict is asserted here** — the
canonical Rust runtime is the sole Pareto judge; every line below is either a
receipt read or a file byte-compare.

**Audit target.** `audio-shokunin` landing
`f50cf66ab378f7be3823d1b4d659839fe21f4e4c` ("r90 author: wpstate/pw-link/wp-format
lattice (4 entries/60 legs, +2183/-3)", parent `a969ea73`, `main`, HEAD at audit
start) against the author worktree `../audio-shokunin-wt-r90` (branch `wt-r90`,
base `5a632a4f`).

**Window.** 2026-10-16 06:54–06:59 local (-0300) = 09:54–09:59Z, read-only.
No battery, probe, or fixture run was executed by this seat; nothing was
committed, staged, or edited outside this report.

**The audited tree moved during the window.** At audit start `main` was clean
at `f50cf66a` (working tree byte-equal to the commit). Two successors landed
while this audit ran — `d78f1cc9 r91 author: gst capture-freeze mechanism
lattice (5 entries/15 legs, +1501/-3)` (~06:58) and `ccbce758 r92 author:
filter-chain DSP lattice (4 entries/80 legs, +2328/-3)` (~06:58–59) — and the
working tree at audit end again carries an uncommitted
`M corpus/fixtures/measure_audio.py`
(`97ed1b1c586d2d5446f2ae85d1ab158e43b0f7d71edf430c2c5f045ed5299efc`, 45271
lines, another seat's in-flight round). Every merged-side byte claim below was
therefore re-derived from the immutable blob
`git show f50cf66a:corpus/fixtures/measure_audio.py` (`d3119c5d…`, 39093 lines),
not from the moving working tree.

---

## 1. Behavior the landing carries

`corpus/fixtures/measure_audio.py` gains the r90 family as an insertion-only
block plus four wiring edits, dispatched by `--probe-wpstate-r90`, with four
ledger entries (`wpstate_store_r90_probe` 15 legs, `wpstate_pmod_r90_probe` 15,
`wplink_r90_probe` 24, `wpformat_r90_probe` 6 = **60 legs**). The two green
runs recorded `failures: []` for all four entries.

| artifact | value |
| --- | --- |
| landed blob (`git show f50cf66a:corpus/fixtures/measure_audio.py`) | `d3119c5d88228349b54996e23978cf726d59bfc615739838177a5a5e14551154`, 39093 lines |
| worktree fixture (author bytes) | `d9a07b14af4e605353b2b07e6fccff41ff0eb083c1d430fb58e7192b1fb276eb`, 34440 lines |
| committed numstat | `2183 3 corpus/fixtures/measure_audio.py`; `370 0 reports/round-90/r90-author.md`; `59 0 reports/round-90/r90-integrate.md` |
| worktree numstat | `2182 2 corpus/fixtures/measure_audio.py` (only file modified) |
| committed `r90-author.md` vs worktree copy | byte-identical (`d51f63851e11942d419ea3089a28e4eef1940b2d29cde1a8c6234701260eec1f`) |
| commit contents | 3 paths, **no** `corpus/live/**` receipt, run dir, or lock |

---

## 2. Claims verified against receipts and bytes

### 2.1 Block-extraction byte-identity — **VERIFIED, exactly as declared**

`r90-integrate.md` line 16 declares: family block "merged lines 35553–37711
(2159 lines) sha256 `85f10b6619f9c45bb3b535a8f389dabfae0fcd750c3d67bf3115a156774d7eaa`;
WT lines 30982–33140 sha256 `85f10b66…` — **byte-identical** (same
marker-delimited span both sides)".

- `sed -n '35553,37711p'` of the landed blob and `sed -n '30982,33140p'` of the
  worktree file: both 2159 lines, both
  `sha256 = 85f10b6619f9c45bb3b535a8f389dabfae0fcd750c3d67bf3115a156774d7eaa`,
  `cmp` → **byte-identical**.
- Span boundaries confirmed on both sides: the span opens on the `# ----…` rule
  immediately above `# ROUND 90 — the WIREPLUMBER …` and closes on the blank
  line immediately above `def main():` (merged `def main()` at 37712, WT at
  33141). The WT diff hunk is exactly `@@ -30981,0 +30982,2159 @@`.
- Dispatch block: 20 lines, landed blob 38365–38384 and WT 33712–33731, both
  `sha256 = 797be5b6dbedcaaa54775b2a88158bffcd2f1d67a8d4a1303ef607d248792c80`,
  `cmp` → byte-identical, spliced immediately before `if args.probe_pwprof_r89:`
  (the author's anchor) in both files.
- Symbol census reproduced: the four entry functions defined 1× each in both
  files; `_r90_family_lock = _wpstate_r90_family_lock()   # held to exit` 1×;
  prefix counts landed/WT = `wpstate` 315/314, `wplink` 6/6, `wpformat` 7/7;
  conflict markers 0 hits; `compile()` of both files succeeds (no bytecode
  written); block's module-level name loads unresolved = **0** (368 names by
  this seat's scoping; the report's count of 372 differs only in counting
  convention, both zero unresolved).

### 2.2 Disclosed mutex wiring deviation — **VERIFIED, and it is the only wiring deviation**

`r90-integrate.md` lines 39–49 disclose that the author diff "deletes only 2
lines (`mode`, `suffix`) and never adds `args.probe_wpstate_r90` to the
`if sum([…]) > 1` guard", and that the merged landing carries it.

- Worktree diff (`git diff -U0`) = 5 hunks: block (2159), argparse row (1),
  dispatch (20), `mode` replacement (1), `suffix` replacement (1) →
  `+2182/−2`. The only two deleted lines are the `mode = "probe-pwprof-r89" …`
  and `suffix = "-pwprof-r89" …` ternaries; the guard line is untouched.
- Merged diff = 6 hunks, `+2183/−3`: the extra insertion is the mutex guard
  rewrite. Mutex list token count: parent `a969ea73` = **135**, merged = **136**
  (`args.probe_wpstate_r90` prepended) — matching the declared "136 tokens
  (was 135)". Worktree list = 133 (branch base predates r91–r95, expected).
- `args.probe_wpstate_r90` occurrences: merged **4** (guard, `mode`, `suffix`,
  dispatch), worktree **3** (no guard) — the deviation is real and exactly the
  one declared. Guard error text in the merged file: `parser.error("choose one
  probe mode")` (line 37853).

### 2.3 Receipt custody — **VERIFIED for the eight green receipts; chain is one-way**

`r90-author.md` lines 244–252 declare four receipts per green run by sha256
prefix. All eight match the files on disk under
`corpus/live/r90-author/receipts/`:

| entry (report label) | run 1 `20261016T085347601935Z` | run 2 `20261016T085628919120Z` |
| --- | --- | --- |
| `wpstate_store_r90_probe` | `0bd7081d162f6674` ✓ | `4ffa08082fe90716` ✓ |
| `wpstate_pmod_r90_probe` | `f3d83e00c84875e3` ✓ | `f77b4eaafe1e36b1` ✓ |
| `wplink_r90_entry` | `cb52c938048e4138` ✓ | `2173957959ba9c2c` ✓ |
| `wpformat_r90_probe` | `64e370f12cbbba2a` ✓ | `35cb424c5dfe59a2` ✓ |

Chain check (both green run bundles):
`measurements.json` → entry → `live_receipt` path → loose file exists → loose
file content **equals** the bundle entry object modulo the `live_receipt` key
(4/4 entries per run, 8/8 total). The loose files are written *before*
`entry["live_receipt"]` is set (`_wpstate_r90_receipt`, WT line 31521), so the
back-pointer exists only in the run bundle; the loose receipt carries no
self-reference (17/17 receipts have `live_receipt = None`).

Run bundles: `mode = "probe-wpstate-r90"`, r90 entries `legs` = 15/15/24/6,
`failures: []`, `coverage_blocked` key absent (not an empty list), 17 non-r90
ledger rows byte-identical across all three r90 runs.

### 2.4 Headline numbers spot-checked against the two green receipts — **match, with one exception (§3.1)**

- Debounce table (`r90-author.md` 116–121): `w_create` 1.852/1.053 s
  (`t_row_s`), `w_props` 1.058/1.061 s (`t_hit_s`), `w_pulse` 1.483/1.057 s
  (`t_change_s`), `w_target` 2.588/1.645 s (`t_target_s`) — **all eight exact**;
  `w_pulse` `cmd_ms` = 4/4 as claimed.
- `w_settings`: 25 rows, histogram `{Boolean: 17, Float: 5, Integer: 1, String: 2}`,
  and 25/25 rows at their built-in Default (range suffix stripped) — recomputed.
  Run 2 retry law caught live: attempt 1 `exit_code -11, entries 0` → attempt 2
  `rc 0, entries 25`, exactly as claimed.
- `w_meta`: 25-key scalar id **36**, 25-key schema id **34** (both runs) —
  the recorded ids match the report's `live [36]` / `schema [34]`.
- `w_state_dir` entries = `['default-nodes', 'stream-properties']`;
  `w_cross_volume` `Value: 0.064`, `delta 3e-06`, live `[0.063997, 0.063997]`.
- Field split, replay, opt-out, vanished target: pulse row `volume 1.0` +
  `channelVolumes [0.125, 0.125]`; props row `volume 0.5` +
  `channelVolumes [1.0, 1.0]`; replay live `[0.125, 0.125]`; `w_replay_target`
  edges 2 into stored / 0 into explicit; `w_explicit_target` 0 / 2;
  `w_optout_stream`/`w_optout_device` `row_present false` with
  `control_row_present true`; `w_vanished_target` `outcome:
  fallback_to_default`, 2 `edges_into_default` links into the operator SPDIF
  sink, `content_witness: declined_shared_default`.
- Module namespace: `m_phantom` rc 0 + id, `node_present/sink_present false`,
  8 probes, `id_recycled_by_foreign true` in both runs; `m_unassignable`
  `rc 1 Failure: No such entity`; `m_unix` `rc 1 Failure: Connection refused`;
  `m_zeroconf_discover` `No such entity`; `m_zeroconf_publish` rc 0 with the
  seat marker row; `m_stub_*` `Failure: Entity exists`; `m_stub_unknown`
  `No such entity`; `m_byname_control` 2 own loopbacks → by-name unload →
  after-count 0 with `own_sinks_alive [true, true]`; prefix/nodename/unknown
  rc 0 with stderr only and after-count 2.
- `pw-link`: `k_connect` 1 / `k_bulk` 2 (first pair only) / `k_dup` 255
  `File exists` / `k_two_ids` 255 / `k_single_id` 0 → 1 / `k_bulk_d` 2 → 1 /
  `k_reversed` 255 / `k_glob` 255 / `k_w_valid` 0.01 s / `k_w_missing` killed
  at 3.001 & 3.01 s / `k_p_foo` `foo_links 1` / `k_p_passive` link object
  without `link.passive` / `k_list_slot` 33 rows / `k_list_filtered` 2 /
  `k_o_pattern` 2 / `k_l_pattern` rows present / `k_t` 0 B with and without a
  live stream / `k_m` 255 with the exact message / `k_m_stream` killed at bound
  (5836 B run 1, 3279 B run 2) / `k_v` 34 rows run 1, **38 rows run 2**.
- Format: `f_rest` `1735b4739ef7`/1128 B, node `Format` 0 B, port `res:-5`;
  `f_mid48` `1735b4739ef7`/1128, `91f7342230f7`/863, `5a828addfad7`/456,
  `e718690a7ce2`/1247; `f_setparam_stream` rc 0 / 622 B / stderr 0;
  `f_44k` `684a7c8dad24`/1247 vs sink `91f7342230f7`/863; `f_post` sticky
  `91f7342230f7` + port `res:-5` + EnumFormat unmoved.
- Post-run census: every `unloads[*].exit_code == 0`, all `sinks_gone` true,
  `own_nodes_after: []`, `own_modules_after: []`, store `6868 → 6884` (run 1)
  and `6926 → 6941` (run 2) — **all exact**.
- Superseded run `20261016T085112273969Z`: exactly the two failures the report
  names — `w_vanished_target: a vanished stored target fell back to the default
  sink` and `k_w_late: -w returned 0 but the link is missing (links 2)` — plus
  five `coverage_blocked` rows on `wpstate_pmod_r90_probe` (by-name vehicle
  pre-checks), which are a separate category from `failures`.

---

## 3. Findings — report claims that do not match the receipts

Quoted verbatim; conflicts are reported, not resolved, for the canonical judge.

### 3.1 `k_w_late` run-1 wall time is the superseded run's number

> "- `-w` (C15, refined): `k_w_valid` rc 0 on an existing pair; `k_w_missing`
>   **blocks** (killed at the 3.0 s bound); `k_w_late` returns **rc 0 at
>   1.526 s / 1.527 s** — ~26 ms after the port appeared at 1.5 s, with the
>   link witnessed on the specific late→L3 edge."

Receipts: run 1 `legs.k_w_late.wall_s = 1.52`
(`wplink_r90_entry.20261016T085342655222Z.json`, equal to the run-1 bundle
entry); run 2 `= 1.527`; the printed **1.526 belongs to the superseded run**
`wplink_r90_entry.20261016T085107205642Z.json` (which has `late_edges: null`).
Direction is immaterial to the law (~20 ms vs ~26 ms after the 1.5 s port), but
the run-1 figure as printed is not the run-1 receipt.

### 3.2 `f_setparam_sink` stderr shape is run-1's, not the run-2 shape

> "- `f_setparam_sink` / `f_setparam_stream` (C21 + the boundary's new
>   node-class split): the **same** pod on the live sink node → **rc 0**,
>   stderr `res:-5 … set param id:4 … failed`, stdout echo **622 B**, link set
>   unchanged, stream alive."

Receipts: run 1 `cmd.stderr_bytes = 123` with the single quoted line; run 2
`cmd.stderr_bytes = 295` carrying **two preceding `res:-2 (No such file or
directory)` lines** (`no global 161`, `unknown resource 133 op:7`) before the
terminal `res:-5 … set param id:4 … failed`. The armed class is unchanged in
both (`error_class: wpstate_io_error`, `error_hit: res:-5 (Input/output
error)`), so the class-level law holds; the report's single-string
characterization understates the run-2 stderr. Same section's stream-node half
(rc 0 / 622 B / stderr 0) matches both runs exactly.

### 3.3 "Every write leg … a key no seat has ever written" — `w_props` reuses the create key

> "1. **The debounce measurement is fresh-key by construction.** … Every write
>    leg here uses `_wpstate_r90_key(tag)` = `r90a_<pid>n<wallclock-nonce>_<tag>`
>    — a key no seat has ever written — and `w_create`/`w_pulse`/`w_target`
>    each assert the key's PRE value is absent before the write (`key_pre`,
>    armed as a `fresh-key guard` failure)."

Receipts/code: `keys = {"create": k_c, "props": k_c, "pulse": k_v, "target":
k_t, …}` (WT lines 31860–31863) — `keys.props == keys.create`, so the props leg
writes a key the create leg wrote moments earlier in the same battery; its
stale-read protection is the other mechanism the code implements (`pre_value`
= the create row recorded before the fire, poll `want='"volume":0.5'` against
a `"volume":1.000000` pre-value). `key_pre` (entry level, all `false` in both
green runs) covers the six distinct keys at battery entry. The sentence's own
scope — create/pulse/target for the absence assertion — is exact; only the
"every write leg" lead-in overstates.

### 3.4 `r90-integrate.md` "in 4 hunks" — the landed diff has 6 hunks

> "| diff stat | `corpus/fixtures/measure_audio.py | 2183 +…, 3 -…` in 4 hunks
> (2159-line block, 20-line dispatch, 1-line argparse row, 3 replaced wiring
> lines) |"

`git show f50cf66a -- corpus/fixtures/measure_audio.py | grep -c '^@@'` = **6**
hunks (the three wiring replacements are three separate hunks). The four edit
classes and the numstat are correct; the hunk count is not.

### 3.5 Implementation-sha claim is seat-attested, not artifact-witnessed

> "- Implementation sha256 (both green runs are byte-identical to this file):
>   `d9a07b14af4e605353b2b07e6fccff41ff0eb083c1d430fb58e7192b1fb276eb`"

No run dir and no receipt records any fixture hash (`grep -l d9a07b14` over the
two green bundles and all 17 receipts → 0 hits). The worktree file's mtime is
`2026-10-16 06:23:28`, i.e. **after** both green runs (05:53:47, 05:56:28) and
15 s before the report was written (06:23:43) — consistent with the report's
own narrative (the staged counter fix reverted before the report), but the
"both green runs ran these bytes" half is not independently recoverable from
artifacts. The "shipped bytes = `d9a07b14…`" half **is** verifiable and holds
(re-hashed at 06:57: still `d9a07b14…`, unchanged through the audit).

### 3.6 Block byte-identity ≠ context identity: one helper the block calls differs

`r90-integrate.md` proves the block's names all *resolve* in the merged file
("372 names loaded by the spliced block, 0 unresolved"). Resolution is not
definition identity. Diffing every module-level function the block references
(49 of them) between the landed blob and the worktree file: **48
byte-identical, 1 different** — `_pwprof_r89_stream`. The landed version adds
`preexec_fn=_pwprof_r89_sigreset` to its `subprocess.Popen` (the r89 SIGHUP
inheritance fix landed in main after the worktree's branch base); the worktree
version has no `preexec_fn`. The block calls it at landed line 35706 inside
`_wpstate_r90_stream`, i.e. on the spawn path of the `pw-link -w` / `-m`
blocking legs — so the landed bytes execute those legs under a different
child-signal setup than the bytes the two green runs were measured on. This is
inherited-fix direction, not a regression, and it is a carry-forward the
integrate note does not disclose. (An independent in-flight seat computed the
same delta; see §5.)

---

## 4. Additional custody observations

- **Receipt inventory is wider than the report's file list.** The receipts dir
  holds **17 files across 5 batteries**: `084910/084915` (first battery,
  `wpctl settings` rc −11 SIGSEGV — referenced in prose), `085052/085058/085107/085112`
  (superseded run), `085325/085333/085342/085347` (green 1),
  `085607/085615/085624/085628` (green 2), `090159/090329/090600` (aborted
  third battery — referenced in prose as "one aborted battery recorded" the
  `probe null sink … never enumerated` block). The report's "Files changed"
  enumerates only the three run dirs; the prose covers the rest without naming
  paths. The 06:06 file is named `wplink_r90_probe.…json` — **not** producible
  by the entry's normal path (`"wplink_r90_entry"`, WT 32915) but exactly what
  its blocked path writes (WT 32607/32617), so it is attributable to the
  shipped bytes.
- **Lock file holds the third (aborted) battery's identity.** `corpus/live/measure_audio-wpstate-r90.lock`
  (73 B, mtime 05:58:38): `pid=3178246 ns=r90a_ns_3178246 role=r90arole3178246
  nonce=3178246n141117` — the fixed-path lock is overwritten per battery, so the
  green runs' identities are not in it.
- **"57 `r90a_`-tagged rows at the final census" is not re-derivable.** The
  store (`~/.local/state/wireplumber/stream-properties`) is live and grew during
  the audit: 6941 rows at run-2 exit → 7741 nonblank / 89 `r90a_` at 06:57 →
  7782 / 130 at 06:58, with a concurrent r90 battery writing (see §5). The
  residue *class* is confirmed; the count is a past observation.
- **Bundle key vs receipt name.** The run bundle key is `wplink_r90_probe`
  (`measurements["wplink_r90_probe"] = wplink_r90_entry()`, landed line 38383)
  while the on-disk receipt is `wplink_r90_entry.<stamp>.json`; the author
  report's table labels the row `wplink_r90_entry` (the file). Both spellings
  are correct for their artifact — recorded here so the judge is not surprised
  by the mismatch.
- **`coverage_blocked` in the green runs is an absent key**, not an empty list;
  the report's "all four entries `coverage_blocked` empty" is semantically
  right but not a literal field value.
- **"No owned `pw-play` processes" is seat-asserted.** The entry preamble
  records the contention census at *entry* only; no exit process census exists
  in the receipts (`own_nodes_after` / `own_modules_after` are the exit
  witnesses). Not disproved — just unwitnessed by artifact.
- **The report's own named blockers reproduce in the artifacts**: the aborted
  third battery's receipts carry `blocked: "probe null sink r90a_la_3178246
  never enumerated"` (wplink) and the store receipt carries 5 failures + 5
  coverage blocks with the wedge signature. The default-sink claim is supported
  at entry in both green runs (`inventory.default_sink` = `oracle_at_start` =
  `alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink.29`); note
  `default_source` differed between the two runs (`r91a_src_3038085` then the
  ALSA line source) — not a claimed invariant.

## 5. Concurrent activity seen during the audit (not this seat's evidence)

At 06:57 a live battery `python3 corpus/fixtures/measure_audio.py
--probe-wpstate-r90` (pid 672209) was running with cwd
`/home/vgpnk/Projects/shokunin/r90c-tree`, whose
`corpus/fixtures/measure_audio.py` is `d3119c5d…` — **the landed revision** —
with output in `/home/vgpnk/Projects/shokunin/r90c/`. Files read there:
`run1.out` (06:56:15) records a run of the landed bytes at
`r90c-tree/corpus/live/runs/20261016T095615156878Z-wpstate-r90/measurements.json`
with `failures: {"wpstate_pmod_r90_probe": ["m_phantom: the unreachable tunnel
did not return 0 (rc 1)", "m_phantom: the tunnel load returned no module id"]}`;
`mut1.out` (06:57:15) records a mutant tree (`r90c-mut1`) whose armed legs fail
as expected; `helper_delta.json` (06:55:44) reports the same single changed
helper as §3.6. These are another seat's in-flight artifacts, observed but
**not relied on** here, and they do not touch the audited worktree (their lock
is `r90c-tree/corpus/live/measure_audio-wpstate-r90.lock`). The shared store
growth in §4 is partly theirs.

**The target repo itself advanced mid-audit.** Within the window `main` moved
`f50cf66a` → `d78f1cc9` (r91) → `ccbce758` (r92), and the working tree carries a
new in-flight `M corpus/fixtures/measure_audio.py` (`97ed1b1c…`, 45271 lines) —
other seats' rounds, not this audit. Consequence for this audit: working-tree
line numbers taken at 06:54–06:57 (while the tree was still clean at
`f50cf66a`) are valid only for the blob; all merged-side citations in §2–§4
were re-derived from `git show f50cf66a:…` after the moves and reproduce
identically.

## 6. Gates

| check | status |
| --- | --- |
| block byte-identity (2159 lines, declared sha) | PASS (byte-compare) |
| dispatch block byte-identity (20 lines, declared sha) | PASS |
| wiring-deviation disclosure (mutex token 135→136, WT 3×/merged 4×) | PASS (exactly as disclosed) |
| receipt sha table (8/8) | PASS |
| bundle↔loose custody (8/8, modulo `live_receipt`) | PASS |
| green-run `failures: []`, 60 legs, census, store deltas | PASS |
| claimed wall-time tables / histograms / shas in legs | PASS except §3.1 |
| landed-bytes execution evidence | **UNWITNESSED by this landing's own artifacts** (§3.5); an independent seat is running the landed sha now (§5) |
| helper-context identity of the extracted block | **NOT CLAIMED by the integrate note; differs in 1 of 49 helpers** (§3.6) |
| host-wedge attribution | not re-probed by this seat; receipts show the wedge signature only |

No Pareto/admissibility verdict is offered by this seat.

## 7. Out of scope (deliberately not done)

No battery, probe, fixture, daemon, or lock interaction; no re-run of any leg
("do not rerun work to decorate the report"); no mutation testing; no edit of
product code, receipts, run dirs, or the worktree; no commit, stage, push, or
publish; no verification of `r90-boundary.md`/`r90-scout.md` internal claims
beyond what the author report ties to r90 receipts; no judgement of the
landing.

## 8. Touched surfaces / artifact paths

- Written (untracked, **not committed**): `reports/round-90/r90-scribe.md` (this file).
- Read: `audio-shokunin/reports/round-90/{r90-author.md,r90-integrate.md}`;
  `audio-shokunin/corpus/fixtures/measure_audio.py`;
  `audio-shokunin-wt-r90/corpus/fixtures/measure_audio.py`,
  `…/corpus/live/r90-author/receipts/*.json` (17),
  `…/corpus/live/runs/20261016T085112273969Z-wpstate-r90/measurements.json`,
  `…/corpus/live/runs/20261016T085347601935Z-wpstate-r90/measurements.json`,
  `…/corpus/live/runs/20261016T085628919120Z-wpstate-r90/measurements.json`,
  `…/corpus/live/measure_audio-wpstate-r90.lock`;
  `~/.local/state/wireplumber/stream-properties` (read-only count);
  `r90c/{run1.out,mut1.out,helper_delta.json}` (read-only).
- Working artifacts of this audit: `/tmp/landed-blob.py`,
  `/tmp/merged-block.txt`, `/tmp/wt-block.txt`, `/tmp/merged-dispatch.txt`,
  `/tmp/wt-dispatch.txt`, `/tmp/r90.diff`.
- Git state left untouched by this seat: `audio-shokunin` `main` advanced
  during the window from `f50cf66a` to `d78f1cc9` to `ccbce758` (other seats),
  with an in-flight `M corpus/fixtures/measure_audio.py` (`97ed1b1c…`) present
  at audit end; `audio-shokunin-wt-r90` `wt-r90` at `5a632a4f` with the
  pre-existing `M corpus/fixtures/measure_audio.py` and untracked r90
  artifacts. This report is untracked and uncommitted.
