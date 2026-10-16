# r90 VERIFIER — frozen-tree gate on committed `f50cf66a` (the wpstate / pw-link / wp-format lattice)

Seat: **verifier** (non-author). Host `plazir27`, lane
`~/Projects/shokunin/audio-shokunin`, basis **`git archive HEAD`**
(`f50cf66ab378f7be3823d1b4d659839fe21f4e4c`) extracted to
`corpus/live/r90-verifier/tree/` under **/home** — the committed bytes, **not**
the worktree and **not** `/tmp`. Window **2026-10-16 09:53Z–10:05Z** (local
UTC−3), loadavg **2.5–5.6** (quiet), 32 cores, `TMPDIR=~/Projects/shokunin/tmp`.
Toolchain re-verified: PipeWire **1.6.8** (server `PulseAudio (on PipeWire
1.6.8)`), pactl **17.0-98-gb096**, Python **3.14.7**.
**Zero tracked writes by this seat, zero commits, zero pushes, no
`set-default-*`**; every artifact under `corpus/live/r90-verifier/`. The single
permitted `probeParent` labrat was dispatched **once**, read-only (§7).

## 0. Verdict

**PASS on committed bytes.** The r90 family re-derives green on a fresh
archive, the law set re-derives the author's declared greens and the
superseded revision's reds, three fixture mutations red exactly where the
fixture's own arms say they should, every fabricated receipt is caught (33/33,
plus the two required no-op controls and one documented limit), and the seat's
exit census carries **zero live `r90a_*` objects**.

| check | required | measured | verdict |
| --- | --- | --- | --- |
| frozen tree integrity | `git archive HEAD` | tar sha256 `a5f0b96ca046c7bbd942cb739920dcd3c6b0deafd58253a796feaaa1ef7e8be6` (3 318 097 920 B); **44 571 files / 11 772 dirs / 0 symlinks**; file-set symdiff vs `git ls-tree -r HEAD` = **0** | PASS |
| fixture identity | committed blob | `corpus/fixtures/measure_audio.py` sha256 `d3119c5d88228349b54996e23978cf726d59bfc615739838177a5a5e14551154` = `HEAD:` blob = the worktree file at archive time = the merge's declared sha (`r90-integrate.md`) | PASS |
| author bytes | declared implementation sha | author worktree fixture sha256 `d9a07b14af4e605353b2b07e6fccff41ff0eb083c1d430fb58e7192b1fb276eb` — **exactly the sha the author's report pins** | PASS |
| block byte-identity | merged family body == author-measured body | merged lines **35553–37711** sha256 `85f10b6619f9c45bb3b535a8f389dabfae0fcd750c3d67bf3115a156774d7eaa` **==** WT lines **30982–33140** sha256 `85f10b66…` (2159 lines, same marker span) | PASS |
| `py_compile` in the frozen tree | clean | rc 0 | PASS |
| integrate wiring | flag + mutex | `--help` lists `[--probe-wpstate-r90]` (rc 0); `--probe-wpstate-r90 --probe-sox-r94` → **rc 2 `choose one probe mode`**; neither wrote a run dir, receipt, or lock | PASS |
| daemon gate | bounded `pactl info` first | **rc 0** (bounded, 12 s cap) before any battery; default sink `…HiFi__SPDIF__sink` | PASS |
| fresh runs on committed bytes | green | **v1** 09:55:34→09:56:18Z (44 s) rc 0 `failures {}`; **v2** 09:56:23→09:57:08Z (45 s) rc 0 `failures {}`; **60 legs each**, `coverage_blocked` empty in all 4 entries | PASS |
| law re-derivation | 203 verifier laws | **v1 203/203, v2 203/203**, author green #1 **203/203**, author green #2 **203/203** | PASS |
| author receipt custody | declared shas | the 8 declared live-receipt sha256 prefixes (run 1 `0bd7081d…/f3d83e00…/cb52c938…/64e370f1…`; run 2 `4ffa0808…/f77b4eaafe1e36b1/21739579…/35cb424c…`) all match the files byte-for-byte | PASS |
| superseded-revision sensitivity | law set must red a non-green revision | author `…T085112273969Z` (kept as honest history): **181 PASS / 5 FAIL / 17 BLOCKED** — the field FAIL is exactly `k_w_late: late_edges=0`; the un-fired by-name vehicle reads BLOCKED | PASS (as designed) |
| mutation battery | mutated bytes must red | `mutecho` 1 failure (echo 622≠999); `mutband` 4 failures (all four write legs at ~1.04 s); `mutsha` 4 failures (EnumFormat sha) — §5 | PASS |
| forgery / negative controls | forgeries caught | **36 rows: 33 CAUGHT, 2 required no-op controls, 1 documented limit, 0 unexpected** — §6 | PASS |
| exit census (this seat) | clean | per-pid (652285/665878/695410/714050/722054): **0 modules, 0 sinks, 0 sources, 0 pw-dump objects, 0 links, 0 processes**; lock content `pid=722054`, **LOCK_FREE**; defaults unchanged; no `settings` file | PASS |
| residue class | named, not hidden | store rows are **permanent by design** (labrat CONFIRMED, §7); this seat added 70 `r90a_`-tagged rows across its 5 runs | PASS with named class |
| global census | — | **not clean by construction in this window**: a concurrent sibling lane cycles the same family (pids 652161 / 672209 / 710014 / 732785 / 745426 observed live) — foreign, not killed, disclosed (§8) | disclosed |

## 1. Frozen tree

- `git archive -o corpus/live/r90-verifier/r90v-head.tar HEAD` → 3 318 097 920 B,
  sha256 `a5f0b96c…` (kept under the lane, `/home`, **not** `/tmp`); extracted
  to `corpus/live/r90-verifier/tree/` (2.5 s).
- Census: 44 571 files / 11 772 dirs / 0 symlinks; file-set symdiff vs
  `git ls-tree -r HEAD --name-only` = **0 lines** (`runs/symdiff.txt`).
- Fixture in the tree: `d3119c5d…` (= `HEAD:` blob = lane worktree at archive
  time) — the worktree moved **only** by nothing: `git status` tracked-dirty set
  was **empty** at entry and at exit.
- `py_compile` clean inside the tree.
- The tree carries the **tracked** r90 scout/boundary/integrate reports
  (`reports/round-90/`), so the committed evidence chain is in scope.

**The author's two greens transfer to committed bytes** by construction:
the family body is byte-identical to the author's measured revision
(`85f10b66…` both sides, §0), and the only differences in the merged file are
the three declared shared-line splices (`mutex` / `mode` / `suffix`) plus the
r91–r95 blocks elsewhere — which is why the whole-file sha differs
(`d3119c5d…` merged vs `d9a07b14…` WT), exactly as `r90-integrate.md` declares.

## 2. Daemon gate and fresh runs on committed bytes

Gate first, bounded: `timeout 12 pactl info` → **rc 0** (Server Name
`PulseAudio (on PipeWire 1.6.8)`, Client Index 36792) at 09:53Z; loadavg
5.61 → 2.53 through the window. No wedge, no retry loop needed.

Both batteries ran the **frozen-tree fixture** through a verifier-owned
launcher (`runs/run_fixture.py`) that resets HUP/INT/QUIT to `SIG_DFL` before
`execvp` (the r89 `g_hup` class; harmless here, but the r90 family inherits the
r89 stream helper).

| run | window (UTC) | wall | rc | failures | receipt |
| --- | --- | --- | --- | --- | --- |
| v1 | 09:55:34→09:56:18 | 44 s | 0 | `{}` | `tree/corpus/live/runs/20261016T095618128262Z-wpstate-r90/measurements.json` |
| v2 | 09:56:23→09:57:08 | 45 s | 0 | `{}` | `tree/corpus/live/runs/20261016T095708701406Z-wpstate-r90/measurements.json` |

Leg census (both runs, all four entries): `wpstate_store_r90_probe` **15**,
`wpstate_pmod_r90_probe` **15**, `wplink_r90_probe` **24**,
`wpformat_r90_probe` **6** — **60 legs**, matching the author's declared
"4 entries / 60 legs". All four entries `coverage_blocked: []`,
`unloads[*].exit_code == 0`, `sinks_gone` all-true, `own_nodes_after: []`,
`own_modules_after: []`.

Live receipts were written into the frozen tree
(`tree/corpus/live/r90-author/receipts/`, 8 files = 4 entries × 2 runs).

## 3. Law re-derivation — `runs/r90v_laws.py` (203 laws)

The law set reads **recorded fields only**; the receipt's own
`failures`/`coverage_blocked` lists are cross-checked (`x:*` laws), never
trusted. Status semantics: `PASS` (claim holds), `FAIL` (field present, claim
fails), `BLOCKED` (witness absent — never green).

| prefix | laws | covers |
| --- | --- | --- |
| `store` | 63 | settings lattice + flags, metadata twins vs CLI ids, state dir, C2 cross-witness, fresh-key guard, the four write paths (band + field split), replay fields/target, explicit-vs-stored, vanished target (named class + consistency), both opt-outs, store census, entry hygiene |
| `pmod` | 45 | control round trip, phantom id (8-probe lattice + no node/sink + recycle witness), unassignable id, unix socket, zeroconf split, four stubs, by-name vehicle (arm status + all-matching + rc-0-with-stderr no-ops) |
| `wplink` | 52 | single-pair grammar, id legs, `-w` (valid/missing/late), `-p` (prop visible / `link.passive` invisible), listing slot-bound/leak/filter, `-t`, `-m`, `-v` |
| `wpformat` | 29 | EnumFormat/Format shas at rest / 48 k / 44.1 k / post, set-param seal by node class, echo bytes, link-set survival |
| `x` | 14 | per-entry verdict consistency (no silenced red, no fabricated red, no silenced block) + the 60-leg census |

**Result on four independent green receipts — 203/203 PASS each:**

- v1 (this seat, committed bytes), v2 (this seat, committed bytes),
- author green #1 (`…T085347601935Z`), author green #2 (`…T085628919120Z`).

The armed values re-derive identically on committed bytes (v1 / v2 / author1 /
author2):

| cell | v1 | v2 | a1 | a2 |
| --- | --- | --- | --- | --- |
| `w_settings` rows / types | 25 / `{B:17,F:5,I:1,S:2}` | same | same | same (attempt 1 **rc −11**, attempt 2 rc 0/25 — the retry law holds) |
| `w_cross_volume` | `Value: 0.064`, live `[0.063997, 0.063997]`, δ 3e-06 | same | same | same |
| `w_create` (creation → row) | 1.091 s | 1.043 s | 1.852 s | 1.053 s |
| `w_props` (`pw-cli` Props) | 1.041 s | 1.041 s | 1.058 s | 1.061 s |
| `w_pulse` (`pactl` volume) | 1.041 s, cmd **3 ms** | 1.042 s, 3 ms | 1.483 s, 4 ms | 1.057 s, 4 ms |
| `w_target` (`move-sink-input`) | 1.042 s | 1.407 s | 2.588 s | 1.645 s |
| pulse row / props row | `channelVolumes [0.125,0.125]`, `volume 1.0` / `volume 0.5`, `channelVolumes [1,1]` | same | same | same |
| vanished target | `fallback_to_default`, 2 edges into SPDIF, replay node alive | same | same | same |
| phantom tunnel | `mine=False` ×8, no node/sink, **id recycled by foreign** | same | same | same |
| `k_w_late` | rc 0 at **1.524 s**, 1 late edge | 1.524 s | 1.520 s | 1.527 s |
| `f_rest` / `f_mid48` / `f_44k` / `f_post` | `1735b4739ef7` (1128 B) / `1735b4739ef7`,`91f7342230f7`,`5a828addfad7`,`e718690a7ce2` / `684a7c8dad24` / sticky `91f7342230f7` | identical | identical | identical |
| `f_setparam_sink` / `_stream` | rc 0, `res:-5`, echo **622 B** / rc 0, stderr **0 B** | same | same | same |

**Sensitivity witness (not a green):** on the author's **superseded** revision
(`…T085112273969Z`, the run the author kept as honest history) the law set
derives **181 PASS / 5 FAIL / 17 BLOCKED**: the one field red is
`wplink.k_w_late.link-into-l3` (`late_edges=0`) — the counting bug the author
names — and the un-fired by-name vehicle (arm `arm_failed` / `foreign_present`)
is BLOCKED, not green. The law set is therefore not a rubber stamp: it derives
reds from fields on bytes that were red.

## 4. Determinism (v1 vs v2)

Full recursive diff of the two receipts (`runs/v1-v2-diff.txt`): the only
differing paths are **pid-derived object names** (`r90a_<pid>_*`), **volatile
ids/seqs** (link/object/port ids), **sample counts** in the poll traces, and
**per-run timings** — every timing inside the armed band. Specifically:

- `failures`, `coverage_blocked`, `own_nodes_after`, `own_modules_after`:
  **0 differing paths** in all four entries.
- `key_pre`: differs only by the pid+nonce key names; every value `False` in
  both runs (fresh-key guard holds by construction).
- `k_ids`: seat links (`mine`) = 2 in both; total link population differs
  (9 vs 12) because **sibling lanes' objects were live in the graph during the
  window** (v1 receipt records foreign `r90a_652161_*`; v2's `k_ids.head` shows
  foreign `r90a_672209_*`) — the legs filter to seat ports, so this is churn,
  not a disagreement.

## 5. Mutation battery (mutated frozen bytes)

Three hardlink copies of the frozen tree with exactly one armed constant
changed each (`runs/mut-sha.txt` records all four fixture shas; the frozen tree
sha is unchanged — the shared inode was unlinked before the edit):

| tree | mutation | expected | measured (fixture's own failures) |
| --- | --- | --- | --- |
| `tree-mutecho` | `WPSTATE_R90_SETPARAM_ECHO_B 622 → 999` | `f_setparam_sink` echo red | **1 failure**: `f_setparam_sink: the stdout echo is 622 B, not the boundary's 999 B` (rc 1) |
| `tree-mutband` | `WPSTATE_R90_DEB_MIN_S 0.5 → 2.5` | the four write legs red | **4 failures**: `w_create` 1.039 s, `w_props` 1.039 s, `w_pulse` 1.040 s ("INSIDE the coalescing debounce… the stale-row read the r90 scout reported"), `w_target` 1.042 s (rc 1) |
| `tree-mutsha` | `WPSTATE_R90_ENUMFORMAT_SHA 1735b4739ef7 → deadbeef0000` | the four EnumFormat cells red | **4 failures**: `f_rest`, `f_mid48`, `f_44k`, `f_post` (rc 1) |

All three mutation runs finished in 43–44 s with the same teardown hygiene
(`own_nodes_after: []`, `own_modules_after: []`, unloads rc 0) — a mutation
reds the *claims*, not the custody.

Law set on the mutated receipts: **201 PASS / 2 FAIL** each — the verdict law
plus `x.<entry>.no-fabricated-red` ("receipt failures with no derived FAIL").
That is the honest reading of a **mutated fixture constant**: the recorded
fields are the real host values (622 B, ~1.04 s, `1735b4739ef7`), so no
field-only law can see the changed *comparison target*; the cross-check flags
the red as not field-reproducible, so it can never read green.

## 6. Forgery / negative-control suite — `runs/r90v_forge.py`

36 rows against the v1 green receipt (red base for the silencing controls):
**33 CAUGHT, 2 required no-op controls, 1 documented limit, 0 unexpected**
(`runs/forge.json`, `runs/forge.txt`).

- **Required no-ops:** `none` (203 PASS) and `blank-verdicts` — blanking both
  verdict lists on a green receipt changes nothing (the fields are the
  detector).
- **Silencing control (field red):** a field-visible red
  (`w_create.t_row_s → 0.01`) with **both verdict lists blanked** is still
  **CAUGHT** (`store.w_create.band` + `x.store.no-silenced-red`) — a silenced
  list cannot launder a field red.
- **Documented limit:** the same silencing applied to a *mutated-constant* red
  (`mutband`) is a no-op at the receipt level: that red lives **only** in the
  verdict list because the recorded fields equal the shipped law set's
  expectations. The mutation gate (§5) is the witness for that class; this is a
  property of receipt-level law sets, not a defect of this one.
- **33 caught fabrications**, each by a named law, e.g.: settings histogram /
  at-default / last-attempt-clean; metadata key drop; `settings` file in the
  state dir; cross-volume value; create band + row default; props field split;
  pulse cmd-ms / band / field split; target band; replay fields; explicit-swap
  (3 laws); vanish outcome-consistency; opt-out row; phantom `mine`; unassignable
  rc; by-name count; `k_ids.mine` count; `k_dup` rc; `k_w_late` wall;
  `link.passive` visibility; `-t` out-len; 48 k sha; echo bytes; sticky sha;
  unload rc; `sinks_gone`; `pop-leg` (BLOCKED + census); `pop-hygiene`
  (BLOCKED).

## 7. Labrat (single permitted probe; advisory, read-only)

Dispatched **once** (frozen `probeParent` slot) for one falsifiable hypothesis:
*the WirePlumber `stream-properties` store has no deletion path reachable from
the r90 toolset — every `r90a_*` row is permanent residue.* Verdict
**CONFIRMED with one refinement**, with citations:

- `/usr/share/wireplumber/scripts/node/state-stream.lua` is the only owner of
  `stream-properties`: writes at `saveStreamProps` (451–458), call sites
  255/321/389 — **no `state_table[key] = nil`, no `state:clear()` anywhere in
  the file**;
- the C API *does* expose `wp_state_clear` (`/usr/include/wireplumber-0.5/wp/state.h:37`)
  and the nil idiom exists — but only for the **`default-nodes`** store
  (`state-default-nodes.lua:172`, driven by `wpctl clear-default`); a grep of
  all 73 installed lua scripts finds zero `state:clear` callers;
- the r90 fixture's toolset (`pactl`, `pw-cli`, `pw-dump`, `pw-link`, `pw-play`,
  `wpctl settings`) exposes no stream-properties deletion verb; the fixture's
  teardown only *censuses* the store (`store_at_exit`).
- Counterexample command that deletes a stream-properties row: **none found**.

Substrate limitation disclosed by the labrat: no exec surface — it worked from
the live store file plus installed lua/headers with read/grep/glob only, and
reported zero writes. Relayed verbatim into
`corpus/live/r90-verifier/labrat/labrat-report.md` (no artifacts were created
by the labrat).

## 8. Exit census and residue class

Per-pid census at 10:01:42Z, after all five of this seat's batteries
(`runs/post-state2.txt`; pids 652285=v1, 665878=v2, 695410=mutecho,
714050=mutband, 722054=mutsha):

| surface | this seat's pids | any `r90a_` (foreign) |
| --- | --- | --- |
| `pactl list short modules` | **0** | 2 (sibling lane, live) |
| `pactl list short sinks` / `sources` | **0** / **0** | 2 / 2 |
| `pw-dump` objects | **0** | 103 |
| `pw-link -l` rows | **0** | 28 |
| processes | **0** | 4 (sibling lane) |

- Lock: `tree/corpus/live/measure_audio-wpstate-r90.lock` content
  `pid=722054 ns=r90a_ns_722054 role=r90arole722054 nonce=722054n144743`
  (this seat's last run) and **`flock -n` succeeds → LOCK_FREE**. The lane's own
  `corpus/live/` never got an r90 lock (all runs were in the frozen/mutation
  trees); the frozen-tree lock file is the fixed-path convention, untracked.
- State dir = `default-nodes` + `stream-properties` — **no `settings` file**;
  default sink unchanged (`…HiFi__SPDIF__sink`); no `set-default-*` issued by
  this seat.
- **Store residue (the permanent class):** `stream-properties` held **7 708 rows
  / 61 `r90a_` rows** at entry and **7 875 rows / 206 `r90a_` rows** at
  10:01:42Z, of which **70 rows carry this seat's five pids** (5 stream keys +
  device-node keys per run). The labrat's source trace (§7) shows this is
  **structural**: no reachable CLI deletes a stream-properties row, so the
  census must report the row class, not hide it. The author's 57-row figure is
  consistent (their window had fewer runs).
- **Co-tenancy disclosure:** a concurrent sibling lane (paths
  `/home/vgpnk/Projects/shokunin/r90c`, `r90c-tree`, `r90c-mut1`, `r90c-mut2`,
  `r91c-tree`) cycled the **same family** through this window (live pids
  652161, 672209, 710014, 732785, 745426 observed; my v1 and mutband receipts
  record their nodes as `foreign_r90a_nodes`). Their objects are the foreign
  census rows above; none was touched, killed, or unloaded by this seat. A
  globally-empty `r90a_` census is therefore not attainable in this window —
  the seat's answer is the per-pid census.

## 9. Findings, limits, blockers

1. **F1 — residue is structural, not a cleanup failure (named class).** No
   deletion path for `stream-properties` is reachable from the fixture's
   toolset (labrat, §7); the fixture censuses it and the report names it. The
   r90 landing is custody-clean on live objects; only the store rows persist.
2. **F2 — mutated-constant reds are list-only at the receipt level (limit).**
   The fixture's own failure string is the only carrier for a changed armed
   constant (§5, §6); a field-based law set flags the inconsistency but cannot
   name the constant. Keep the battery's failure text as the witness.
3. **F3 — co-tenancy: the family is being run by sibling lanes on the shared
   daemon.** The fixed-path family lock is tree-relative (inherited r84–r89
   residual), so two lanes in different trees can run concurrently; both
   survived (all legs green, `mine` filtering correct), but foreign objects
   appear in listing legs (`k_l_pattern`, `k_ids`) and in the global census.
4. **F4 — the author's `wpctl settings` rc −11 SIGSEGV did not reproduce** in
   either of this seat's runs (attempt 1 clean, 25 rows) and is *preserved* in
   author run #2 (attempt 1 rc −11 / 0 rows → attempt 2 rc 0 / 25 rows), where
   the retry law holds. The crash class remains unexplained but is
   harness-handled; no green depends on it.
5. **F5 — the vanished-target outcome is host/session-manager-state dependent**
   and is armed only as a named class (`fallback_to_default` 4/4 in this
   window: author ×2 + this seat ×2, 2 edges into the operator's SPDIF sink).
   The boundary's `no_link` 3/3 is the other branch; the leg is correctly not
   armed to either.
6. **Blockers:** none for the landing. The only blocker-class event is the
   sibling lane's co-tenancy (F3), which is disclosed, not repaired — the
   verifier never kills foreign objects.

## 10. Seat hygiene and artifacts

- `git status --porcelain -uno` **empty** at entry and exit: **no tracked file
  was written** by this seat; no commits, no pushes, no `set-default-*`, no
  foreign object unloaded or killed.
- Everything this seat produced lives under `corpus/live/r90-verifier/`
  (untracked): `r90v-head.tar` (3.1 GiB, the archive — regenerable; operator may
  delete), `tree/` + `tree-mut{echo,band,sha}/` (gitignored by the
  `live/**/*tree*` rules), `runs/` (launcher, law set, forge suite, receipts
  summary, census logs, diff tables, `forge.json`, `laws-*.json`),
  `labrat/labrat-report.md`.
- No receipt, run dir, or lock was added to the lane's `corpus/live/runs/` or
  `corpus/live/r90-author/`; the frozen tree's own copies were used.
- Report: this file. **Nothing committed** — the landing decision is the
  operator's.
