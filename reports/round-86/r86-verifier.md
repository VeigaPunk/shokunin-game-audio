# r86 VERIFIER — wave-B gate on committed `fa5994a0` (frozen tree)

Seat: verifier (non-author). Host `plazir27` (`Linux 7.2.3-arch1-3`, 32
cores), lane `~/Projects/shokunin/audio-shokunin`, window
**2026-10-16 06:33:56Z–06:40Z**, loadavg **77–101** throughout (load
preferred; every run below ran under it). Target: commit **`fa5994a0`**
("r86 author: 5 entries pwctl lattice (addr/params/dsp/meta/tools) —
+1761 lines; r84 fold applied: fixed-path family lock; 2 green runs"),
frozen via `git archive` — **not** the worktree (sibling r86 seats are
live-writing their own seat dirs, §8). Toolchain: PipeWire **1.6.8**
(`pw-cli`/`pw-dump`/`pw-metadata`/`pw-top`), pactl/libpulse
**17.0-98-gb096**, aplay **1.2.16**, Python **3.14.7**; all scratch under
`TMPDIR=~/Projects/shokunin/tmp`. **No tracked writes by this seat, no
commits, no pushes, no `set-default-*`; every seat artifact under
`corpus/live/r86-verifier/`.**

## 0. Verdict

**VERIFIED — wave-B gate PASS.** On the frozen `fa5994a0` tree, two
green replays (r86v1, r86v2) reproduce the author's committed verdict
surface **exactly** — **0 exact / 0 named / 0 entry-level diffs** against
**both** author runs on all **149 legs × 5 entries** — and an independent
149-law checker passes on all four receipts (**596/596**). The r84 fold
is verified **executed, not just read**: the family lock resolves to a
fixed `<tree>/corpus/live/measure_audio-pwctl-r86.lock` under a foreign
TMPDIR and never under TMPDIR, while the r85 control lock lands under the
foreign TMPDIR (F1 records the one structural caveat: tree-relative, not
host-global). The three caveat rows behave as declared: `dump_color_eq`
and `d_route` are record-only (every realization passes, `armed: False`),
`n_format` is either-way on pod presence and rc-armed only. One replay
class (V2) initially failed 5 meta laws **in my own checker** (subject id
hardcoded); fixed to id-generic — no fixture defect (§9, iterations).

| check | required | measured | verdict |
| --- | --- | --- | --- |
| frozen tree integrity | `git archive fa5994a0` | tar sha256 `f8643b9a…`, 1 606 819 840 B; 43 778 files / 11 676 dirs / 0 symlinks; symdiff vs `git ls-tree -r fa5994a0` = **0** | PASS |
| fixture identity | committed blob | sha256 `5ceba94019eaaa8f1db9ac18ea15023f7e4891e844defe86711f37873059b780` — identical to the author's declared pin, in the tree before and after all runs | PASS |
| py_compile | clean | rc=0 (inside frozen tree) | PASS |
| `normal` receipt sha | canonical pin | `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b` — byte-identical to the r85 canonical normal pin | PASS |
| `--probe-pwctl-r86` ×2 under load | failures `{}` | r86v1 `06:34:30→06:34:59Z` rc=0 `{}`; r86v2 `06:34:59→06:35:29Z` rc=0 `{}` | PASS |
| 149 legs × 5 entries ×2 | all legs, no skips | 149/149 per run (34/43/16/22/34); no `blocked`/`coverage_blocked` | PASS |
| verdict-surface stability | deterministic | v1 vs A1 **0/0/0**, v1 vs A2 **0/0/0**, v2 vs A1 **0/0/0**, v2 vs A2 **0/0/0**, v1 vs v2 **0/0/0**; calibration A1 vs A2 **0/0/0** | PASS |
| independent law re-derivation | armed law set | **149 laws, 149/149 PASS** on A1, A2, r86v1, r86v2 (**596/596**) | PASS |
| fixed-path family lock (r84 fold) | not TMPDIR-scoped | static: path = `ROOT/live/…` (`ROOT = Path(__file__).resolve().parents[1]`), no TMPDIR/env input; executed 8/8: foreign TMPDIR → lock at frozen-tree `corpus/live/`, absent under TMPDIR; blocking + release proven; r85 control lands **under** the foreign TMPDIR | PASS |
| caveat rows | as declared | executed committed-slice probe 8/8: `dump_color_eq` record-only ×3 realizations, `d_route` record-only ×2, `n_format` rc-only either-way + hostile rc≠0 fails | PASS |
| custody/teardown | zero residue | all entries `sinks_gone` all-true, `own_nodes_after: []`, `meta_keys_gone: true`, unloads `verified_index == captured`, `recycled: False`; post-state **0** `r86a_*`/`r86v_*`/`r86b_*` modules/sinks/sources/nodes/meta keys; defaults unchanged | PASS |
| independent spots | ≥5 shapes | **29/29 green** — own code, own `r86v_*` namespace | PASS |
| zero tracked writes | none | this seat wrote only under `corpus/live/r86-verifier/`; the one tracked delta (` M …pyc`) was dirty **before** this seat (§8) | PASS (for this seat) |

## 1. Frozen tree

- `git archive fa5994a0 -o …/r86v-tree.tar` → sha256
  `f8643b9adc8dcef2135c42dfd1817890d8df3be3fb49edb187dedf44ec91470f`
  (1 606 819 840 B); extracted to `corpus/live/r86-verifier/tree/`
  (gitignored regenerable path per `corpus/.gitignore` `live/**/*tree*/`);
  the tar was deleted after extraction, sha pinned in
  `runs/tree-tar-sha.txt`.
- Census: **43 778 files / 11 676 dirs / 0 symlinks**; file-set symdiff
  vs `git ls-tree -r fa5994a0 --name-only` = **0 lines**
  (`runs/tree-symdiff.txt`).
- Fixture inside the tree: sha256 `5ceba940…` — unchanged after 1
  normal + 2 probe runs. Commit shape: `+1761 / −3` in
  `corpus/fixtures/measure_audio.py`; the 3 deletions are the declared
  wiring lines. Author receipts are byte-identical to canon:
  run1 == `20261016T063006268243Z` (`1097d9f1…`), run2 ==
  `20261016T063043717745Z` (`fe57c1cb…`) — no citation drift.

## 2. Battery — CWD = frozen tree root (`runs/commands.log`)

| run | window (UTC) | cmd | rc | failures | receipt sha256 |
| --- | --- | --- | --- | --- | --- |
| normal | 06:34:24→06:34:26 | `python3 corpus/fixtures/measure_audio.py` | 0 | `{}` | **`8e8cdad6…`** (canonical pin) |
| r86v1 | 06:34:30→06:34:59 | `… --probe-pwctl-r86` | 0 | `{}` | `67ea181da13626cfa5addb0a0804e27bae374e8c14722fea796453d5b10aaa20` |
| r86v2 | 06:34:59→06:35:29 | `… --probe-pwctl-r86` | 0 | `{}` | `fc66270100225639dc7e16f76fa313d3b301b667f15a51f1382ed862778a45b3` |

- Load at starts: 85.87 / 87.00 / 87.85 (1-min) — the replays are also
  load replays.
- Leg census per green run: **149 legs / 5 entries** — exact match to the
  committed count (entry split 34/43/16/22/34).
- r86v1 headline values: addr `ns_leaf` id 160 / serial 243537;
  self-client serials `243573→243574` (one fresh `pw-dump` client per
  invocation); `dump_color_eq` rc255 `Unknown color: =never` (recorded);
  params `d_route armed: False`, `n_format armed: "rc_only"` with
  `has_pod: True`; DSP regions `solo 8192 / cv25 2048 / cv50 4096 /
  mute 0 / reset 8192 / dead 8192 / pa25 128 / pa100 8192`; pactl
  readbacks `63 % / 79 % / 100 % / 25 % / 100 %`; meta census
  `store_ids == ls_ids == [31,34,35,36,37,38,39,41,42]` (9 stores),
  `dump_ids = [31,34,36,39]` (strict subset); tools `cli_devnull` rc−6
  SIGABRT, `cli_pipe` rc−9 killed-at-bound, `top_tui_term` rc−6
  `loop_assert: True`, `top_batch_term` rc0 `loop_assert: False`.
- All five entry heads record `fixture_runs: 0` (no same-family sibling
  in flight at my run times).

## 3. Fixed-path family lock (the r84 fold) — static + executed

**Static (committed blob).** `_pwctl_r86_family_lock` (line 24118):
`path = ROOT / "live" / "measure_audio-pwctl-r86.lock"` with
`ROOT = Path(__file__).resolve().parents[1]` (line 26). No `os.environ`,
`TMPDIR`, `tempfile`, or argument reaches the path. The acquisition site
(line 25964) is `_r86_family_lock = _pwctl_r86_family_lock()  # held to
exit` — one fd for the whole five-entry family. Contrast: the r85
helper (line 22324) is `Path(tempfile.gettempdir()) /
"measure_audio-pactlmon-r85.lock"` — TMPDIR-scoped; the r82/r84 helpers
(lines 14764/19846) likewise. The only `tempfile` use inside the r86
block is the DSP scratch dir (line 24781, `TemporaryDirectory`), unrelated
to the lock.

**Executed (`runs/lockprobe.py` + `lockprobe.txt`, 8/8 PASS).** Helpers
extracted verbatim by anchor from the frozen-tree fixture (sha
`5ceba940…`), executed with `TMPDIR` pointed at a fresh foreign scratch
dir:

- r86 lock appears at `<frozen tree>/corpus/live/measure_audio-pwctl-r86.lock`
  and **not** under the foreign TMPDIR;
- witness line written (`pid=424242 ns=… role=…`);
- a second exclusive attempt blocks while held (`LOCK_NB` →
  `BlockingIOError`), and succeeds after release — the "waits HERE"
  serialization is real;
- with a scratch ROOT the lock follows ROOT (it is ROOT-relative, not a
  hardcoded absolute path);
- **control**: the r85 helper's lock lands **under** the foreign TMPDIR
  — the TMPDIR-scoping contrast is proven, not assumed.

**Lane evidence.** The lane worktree's
`corpus/live/measure_audio-pwctl-r86.lock` carries a sibling seat's
witness (`pid=2808000 ns=r86a_ns_2808000`, 03:34) — runs from the
worktree resolve to the lane's fixed path. My frozen-tree runs used the
frozen tree's own lock file. See **F1** for the corollary.

## 4. Verdict-surface stability

Tiered comparator (`runs/surface.py`, r83/r84 convention, extended):
**exact** = rc/signal/killed_at_bound/signal_delivered/loop_assert/armed +
`error_class`/`error_hit` (normalized) + structural law fields
(`typed_rows`, `self_clients`, `destroy_census.surviving`,
`self_loop_census` count, `has_pod` for the params matrix, pw-jack `env`,
DSP `writes` rc); **named** = law-bearing magnitudes (DSP envelope
*bounds*, pactl percents, store counts, pod floats, silent-empty
booleans); **entry** = teardown projections (`sinks_gone`,
`own_nodes_after`, `meta_keys_gone`, unload verification, failures,
`coverage_blocked`); **analog** = everything else (timings, sizes,
ids/serials, argv, loadavg, host census, `tap_windows`, `subj0_keys`).
Normalization collapses pids, `r86a_`/`r86v_` namespaces, object ids
(including `object N`), serials, hex pointers.

- Calibration: **A1 vs A2 = 0 exact / 0 named / 0 entry** — the
  comparator pins exactly the surface the author's own two green runs
  agree on (242 analog-volatile fields; A1's window had a foreign
  default source `r85v_2658932_vsrc` and 7 monitors, A2 4 — the census
  counts are correctly analog).
- r86v1 vs A1 **0/0/0**; v1 vs A2 **0/0/0**; v2 vs A1 **0/0/0**; v2 vs
  A2 **0/0/0**; v1 vs v2 **0/0/0**.
- Two fields are deliberately **not** in the exact tier, with evidence:
  `tap_windows` (93/93/94/96 across the four receipts — a sampling
  count, the envelope medians are the law) and `subj0_keys` (subject-0
  metadata key list changes with host state). One leg is race-exempted:
  `cli_pipe`'s `error_class`/`error_hit` (author1 saw
  `pwcli_remote_enoent` from a foreign registry-event line; author2/V1/V2
  `None`) — **F2**; the arm is rc/SIGKILL/killed_at_bound, unaffected.

## 5. Independent law re-derivation (`runs/laws.py`, no fixture import)

**149 verifier-owned laws re-derived from raw receipt data**, run on all
four receipts: **596/596 PASS** (`runs/laws-all.txt`). Coverage:
addr (serial/id inversion, indistinguishable-empty, typed rows,
`<id>`≡`<serial>` byte-equality, silent-empty refusals, joined `-Cnever`
dump, self-client exactly-one + fresh serials, live Metadata
silent-empty, real nonzero bogus-remote, self-loop create/info/destroy),
params (exposure matrix pods, pod-absence, `n_format` rc-only, remote
ENOENT, not-implemented classes, numeric 3 ≡ EnumFormat, unknown-param,
`None` echo, empty pod, stripped keys, wrong-type slot, remote −95, port
Latency write dropped + local not-implemented, bad id, usage),
dsp (tap edges, player attach, all writes rc0, eight envelope bounds,
pactl cubic readback, 25 %/100 % round-trip, scalar-volume display-dead,
alive-at-end, peak), meta (9-store census + ls agreement + dump strict
subset, echo/overwrite/typed round-trip, absent read, delete-then-absent,
delete-absent, dead-subject echo-no-readback, subject wipe, monitor
filters, keys-gone), tools (pw-cli EOF SIGABRT, pipe killed-at-bound,
quit rc0, six pw-jack env rows + remote, pw-link rc lattice 255/255/255,
usage/modifier refusals, list/link/unlink/junk-props, pw-top batch/TUI
signal classes, jack bogus 127 / badopt usage), and per-entry custody
(`sinks_gone`, `own_nodes_gone`, name-verified unloads).

## 6. Caveat rows — executed either-way pinning (`runs/armprobe.py`)

Committed verdict slices extracted verbatim by anchor and exec'd against
synthetic legs (8/8 cases, **SUSTAINED**):

- **`dump_color_eq` — record-only confirmed.** Slice = the committed
  `armed = False` line (the leg is referenced nowhere else). Observed
  rc255 `Unknown color: =never`; boundary-boot rc0 0 B; hypothetical rc0
  full dump — **all three append no failure and stay `armed: False`**.
- **`d_route` — record-only confirmed.** Silent-0B and pod-dump
  realizations both pass, `armed: False`.
- **`n_format` — rc-only either-way confirmed.** rc0 + pod present and
  rc0 + pod absent both pass (negotiation-tracked presence is recorded,
  not armed); hostile rc1 appends the failure; `armed: "rc_only"`.

## 7. Independent spots (`spot/spots.py`, own code, own `r86v_<pid>`)

Final battery **29/29 green**, `residue_after: 0`
(`spot/spots2.out.txt`):

| spot | shape | measured |
| --- | --- | --- |
| s0/s1 | own null sink; pw-cli namespace split | `ls <serial>` resolves the node (7 lines, `id 85,`); `ls <id>` 0 B rc0; `info <id>` rc0; `info <serial>` rc0 `unknown global` |
| s2 | pw-dump surface | `<id>` ≡ `<serial>` byte-identical (11 547 B); bad id 0 B rc0; `-C never` positional trap 0 B rc0 vs `-Cnever` 243 628 B |
| s3 | enum-params matrix on own node | Props/PropInfo/EnumFormat pods; Latency pod-absent; IO `res:-2` ENOENT; `Bogus` → unknown param type |
| s4 | metadata census | `pw-metadata -l` = 9 = `pw-cli ls Metadata`; `pw-dump` = {31,34,36,39} strict subset |
| s5 | pw-link lattice | create rc0; duplicate **rc255 File exists**; usage rc255; bogus port rc255; `-l -I` shows own link; `-d <link-id>` rc0 removes it |
| s6 | pw-jack shim | `-p 512` → `Q=512/48000`; `-v -v` → DEBUG 4 |
| s7 | pw-cli `</dev/null` | **SIGABRT rc−6**, `remove_from_poll()` assertion; RLIMIT_CORE=0, no core left |
| s8 | set-param volume dead key | write rc0, store reads `Float 0.250000`, pactl still 100 % |

Teardown: own module unloaded by name-verified index, residue scan 0.

## 8. Custody, contention, host state

- **Custody**: every green receipt carries `sinks_gone` all-true,
  `own_nodes_after: []`, `meta_keys_gone: true` (meta entry), unloads
  `verified_index == captured` / `recycled: False` / rc0 in all five
  entries. Post-state (06:38:38Z): **0** `r86a_*`/`r86v_*`/`r86b_*`
  modules, sinks, sources, nodes or default-store keys; default sink
  `…HiFi__SPDIF__sink.29` / default source `…HiFi__Line__source.29`
  unchanged from pre-state.
- **Contention ledger** (foreign work observed read-only, never touched):
  - r86 sibling seats live in-window: **r86-reviewer** ran the probe
    from the lane worktree (lane lock witness `pid=2808000`, 03:34;
    `audit-live-run.json`, `surface-diff.json` in its seat dir);
    **r86-critic** (`live-readonly.json`, co-tenancy witness);
    **r86-simplifier** (proofs). No fixture process was in flight at my
    run times (`fixture_runs: 0` in all entry heads).
  - Ambient loadavg 77–101 on 32 cores; a foreign `pactl subscribe`
    (pid 446929, since Oct15) and foreign default-store values
    (`default.configured.audio.sink` value `{"name": "r93…"}`) are host
    state, recorded and never armed.
- **Interference by this seat**: 3 runs from the frozen tree, 1 lock
  probe, 1 arm probe, 2 spot batteries on probe-owned `r86v_*` null
  sinks (all unloaded name-verified); no default-sink audio, no
  `set-default-*`, no foreign object touched.

## 9. Findings (ranked)

- **F1 (minor, structural carry) — the fixed path is ROOT-relative, so
  the lock is TMPDIR-independent (the r84 fold requirement — verified)
  but also *tree-relative*.** Seats that materialize their own tree
  (frozen archive, as this seat and the r85 reviewer did) lock their own
  `<tree>/corpus/live/measure_audio-pwctl-r86.lock` and do **not**
  serialize against a lane-worktree run — both lock files existed
  concurrently in-window (lane witness `pid=2808000` vs my frozen-tree
  file). Practical impact is low: the family's `r86a_<pid>` namespacing
  is the real cross-run isolation, my four receipts show no
  interference, and the "identical for every seat regardless of TMPDIR"
  reading holds **within** a shared tree root. Carry to the fold: if
  host-global serialization across materializations is wanted, resolve
  the lock from an explicit lane root rather than `__file__`; otherwise
  record the tree-relative semantics as intended.
- **F2 (minor, race) — `cli_pipe`'s `error_class`/`error_hit` is
  volatile.** Author1 captured `pwcli_remote_enoent` from a foreign
  registry-event line (`no global N`) inside the killed-at-bound
  process; author2 and both replays captured `None`. The arm
  (rc/SIGKILL/killed_at_bound) is unaffected — no verdict effect, and
  the comparator exempts the field — but any future arm on that
  `error_class` would be flaky.
- **F3 (observation, host state) — subject-0 store varies across
  windows.** `subj0_keys` shows `default.audio.source` present in
  author1's window and absent in the other three; the `default` store's
  configured-sink value is a foreign name (`{"name": "r93…"}`). Both
  are recorded, never armed; the family writes no subject-0 key
  (`meta_keys_gone: true`). The caveat rows realized multiple ways
  across the four receipts (`dump_color_eq` rc255 here vs 0 B on the
  boundary boot; `d_route` silent here) — exactly the declared
  record-only semantics.
- **F4 (corpus hygiene) — the runs dir also holds the pre-fix dev
  receipt** `20261016T062922907396Z-pwctl-r86` (149 legs; fails exactly
  on the old `n_format` pod-presence arm, `rc=0 pod=True`). It is not
  cited by the committed report; the committed blob arms `n_format`
  rc-only (verified by the executed slice probe). Noted so a later
  reader does not mistake it for a committed-source receipt.
- **F5 (observation) — `n_format` realized `has_pod: True` again** in
  both replays (the row is negotiation-tracked); recorded, rc-only as
  declared. No action.

## 10. Risks / blockers

- **None blocking.** The landing verifies on the frozen tree; both green
  replays are surface-identical to both author runs; 149/149 laws pass
  on all four receipts; the lock fold is verified executed; the three
  caveat rows behave as declared.
- Carries for the wave-B fold: **F1** (lock tree-relative — state the
  intended scope explicitly), **F2** (don't arm on `cli_pipe`
  error_class), **F4** (uncited pre-fix receipt retained).
- Residual uncertainty: the author receipts' provenance (source bytes at
  their run time) is inferred from the identical fixture sha and the
  reproduced surface, not observed directly — the commit timestamp
  (06:31:47Z) is ~1 min after the receipts (06:30:06/06:30:43Z), so the
  committed blob is the file that produced them only if it was unchanged
  in that minute; all four receipts agree, which is the strongest
  available check.
- Disclosed leftovers by this seat: the 1.6 GB frozen tree is left as
  regenerable receipt material (gitignored `live/**/*tree*/`) for the
  orchestrator to keep or prune.

## 11. Evidence map (`corpus/live/r86-verifier/`, 44 files / 5 671 065 B
excluding the gitignored tree; `manifest.json` + `manifest.sha256`)

`runs/`: `window-start.txt`, `toolchain.txt`, `pre-state.txt`,
`post-state.txt`, `commands.log`, `tracked-status-before.txt`,
`tracked-status-after.txt`, `tree-tar-sha.txt`, `tree-census.txt`,
`ls-tree-fa5994a0.txt`, `tree-files.txt`, `tree-symdiff.txt`,
`fixture-sha.txt`, `tree-fixture-sha.txt`, `worktree-fixture-blob.txt`,
`normal.stdout.json`/`.stderr.log`/`.receipt.json`/`.receipt-sha.txt`,
`r86v1.stdout.json`/`.stderr.log`/`.receipt.json`,
`r86v2.stdout.json`/`.stderr.log`/`.receipt.json`, `receipt-shas.txt`,
`surface.py` + `surface-{A1-vs-A2,V1-vs-A1,V1-vs-A2,V1-vs-V2,V2-vs-A1,V2-vs-A2}.txt`,
`laws.py` + `laws-all.txt`, `lockprobe.py` + `lockprobe.txt`,
`armprobe.py` + `armprobe.txt`;
`spot/spots.py`, `spot/spots{,2}.out.txt`, `spot/spots{,2}.err.txt`;
`labrat/` (empty — see §12); `tree/` (gitignored `git archive`
materialization holding the receipts as written by the fixture).

## 12. Labrat disclosure

The single permitted `probeParent` labrat was dispatched once, read-only,
for the bounded hypothesis "the r86 family lock is TMPDIR-independent
(fixed `<corpus>/live/` path) while the r85 lock is TMPDIR-scoped". Its
substrate exposed **no shell/exec/write tooling**, so the executed half
returned **UNTESTED** with zero artifacts (`labrat/` is empty) and zero
side effects; its **static** half returned **SUSTAINED** with the exact
quoted lines, an adversarial scan of the whole r86 block (all
`tempfile.gettempdir()` call sites are r82/r84/r85; the only r86
`tempfile` use is the DSP scratch dir), and "no code path lets a foreign
TMPDIR change the lock location". This seat then ran the executed half
itself (`runs/lockprobe.py`, §3) — the executed result confirms the
static trace and adds the blocking/release and ROOT-relative checks. No
other descendant was spawned.
