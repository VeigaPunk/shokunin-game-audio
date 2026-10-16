# r88 VERIFIER — wave-B gate on committed `c19bec96` (frozen tree)

Seat: verifier (non-author). Host `plazir27` (`Linux 7.2.3-arch1-3`,
32 cores), lane `~/Projects/shokunin/audio-shokunin`, window
**2026-10-16 07:25Z–07:40Z**, loadavg **55–86** throughout (run-start
1-min loads from the receipts: v1 79.55 / v2 77.71 / v3 76.54 /
v4 75.65 / v5 75.67; author A1/A2 74.73/74.44; load preferred). Target:
commit **`c19bec96`** ("r88 author: 79 legs / 3 entries — bluetooth
VACUOUS-by-absence …, dump-vs-ls witness diff, pw-top -n traps; 2
green"), frozen via `git archive` — **not** the worktree (sibling
wave-B seats are live in the lane and in `corpus/live/r88-reviewer/tree`,
§8). Toolchain: PipeWire **1.6.8**, pactl/libpulse **17.0-98-gb096**,
WirePlumber **0.5.17-1**, bluez **5.87-2**, Python **3.14.7**, numpy
2.5.3; all scratch under `TMPDIR=~/Projects/shokunin/tmp`. **No tracked
writes by this seat, no commits, no pushes, no `set-default-*`; every
seat artifact under `corpus/live/r88-verifier/`.**

## 0. Verdict

**GATE FAIL as a reproducible green landing — PASS on every encoded
law.** Every claim the r88 author landed is independently re-derived and
holds (66 verifier laws **462/462** across 7 receipts; 6 live spots
against the host; the fixed-path lock executed 4/4). But the landing's own
**verdict arms are co-tenancy lotteries**: on the frozen bytes
(`ad9d59b1…`) this seat measured **7 of 9 red** under 3-way concurrent
probe runs, across **four distinct arm classes** (all diagnosed to
mechanism, §6.1), and the wave itself already contains a natural-rate
red — the **r88 reviewer's replay r88r2** (07:29:37Z, its own frozen
tree) failed `wd_dump_empty` while its r88r1/r88r3 passed. The laws are
intact in every red; the reds are the arms, exactly the r87-F1 shape in
new clothes. This seat's own five replays (07:26:20–07:28:01Z, solo
under load) and both author runs were green — the landing is green when
alone and **not reliably green when co-tenanted**, which is how the wave
actually runs.

| check | required | measured | verdict |
| --- | --- | --- | --- |
| frozen tree integrity | `git archive c19bec96` | tar sha256 `d13b4d34360c94d070a7aac914bac8abaaaf1bf7286c3abf70c2513d74477708`; 44 064 files / 11 701 dirs / 0 symlinks; file-set symdiff vs `git ls-tree -r` = **0** | PASS |
| fixture identity | committed blob | sha256 `ad9d59b1e0dc5e2be4274f4966e571dabefed94076c06093eed1bf4cd2aef4c4` — identical to the author's declared pin, the worktree tracked blob, the frozen-tree copy, and both scratch-tree copies | PASS |
| py_compile / ast | clean | rc=0 inside the frozen tree | PASS |
| `normal` receipt sha | canonical pin | `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b` — byte-identical to the r85/r86/r87 canonical normal pin | PASS |
| `--probe-btwit-r88` replays, solo | green | **r88v1–v5 all rc=0**, `failures {}` (79 legs / 3 entries each) | PASS |
| wave-level run census | green | 10 wave receipts on identical bytes: A1, A2, r88r1, r88r3, v1–v5 = **9 green**; **r88r2 RED** (`wd_dump_empty`) | **FAIL (1/10)** |
| co-tenancy stress (3 concurrent trees × 3 rounds) | green | **9 runs: 7 red**; classes `wd_dump_empty` ×6, `wd_enum_num2` ×3, `wd_cli_meta_extra`/`wd_silent_cli_meta` ×3+1, `bz_create_{midi,a2dpsource}` ×2 | **FAIL** |
| verdict-surface stability (solo) | deterministic | v1–v5 vs A1 **0 exact / 0 entry**; vs A2 **3 exact** (the declared-variable `wd_enum_fmt` recorded path, which A1-vs-A2 also shows); A1-vs-A2 calibration **3 exact / 1 named / 0 entry** | PASS (solo surface) |
| independent law re-derivation | armed law set | **66 laws × 7 receipts = 462; 462 PASS** | PASS |
| fixed-path family lock (r84 fold) | not TMPDIR-scoped | static: `path = ROOT / "live" / "measure_audio-btwit-r88.lock"`, no env/tempfile input; executed 4/4: lock lands in-tree, not under foreign TMPDIR; blocking + release proven; cross-materialization: two ROOTs → two locks held simultaneously; r85 control lands under the foreign TMPDIR | PASS with F5 |
| independent spots (own code, own namespace) | ≥5 shapes | absent-class 12/12, set rule 138/138 keys, Metadata split 9v4, serial law 14/14, pw-top traps 4/5 (the `-n abc` capture came back empty once — F4), four-witness state agreement idle+active | PASS with F4 |
| custody/teardown | zero residue | 7/7 receipts: `sinks_gone` all-true, `own_nodes_after: []`, `verified_index == captured`, `recycled: false`; post-state **0** `r88v_*` nodes of this seat; defaults unchanged | PASS |
| zero tracked writes | none | this seat wrote only under `corpus/live/r88-verifier/`; the only tracked dirty file is the pyc that was dirty **before** the window | PASS (for this seat) |

## 1. Frozen tree

- `git archive c19bec96 -o $TMPDIR/r88v-tree.tar` → sha256
  `d13b4d34…`, 3 248 128 000 B (the tree carries the committed
  1.6 GB `r87-reviewer/runs/r87r-tree.tar`); extracted to
  `corpus/live/r88-verifier/tree/` (gitignored regenerable path per
  `corpus/.gitignore` `live/**/*tree*/`); extraction 5 s, 3.1 GB on disk.
- Census **44 064 files / 11 701 dirs / 0 symlinks**; file-set symdiff
  vs `git ls-tree -r c19bec96 --name-only` = **0 lines**
  (`runs/tree-symdiff.txt`).
- Fixture inside the tree: sha256 `ad9d59b1…` — unchanged after 1 normal
  + 5 probe runs; `py_compile` rc=0, `ast.parse` ok.
- **The worktree moved during this window**: at ~07:36Z a sibling seat
  (r89 author) began inserting an r89 block into the tracked
  `corpus/fixtures/measure_audio.py` (`+1483` lines, worktree sha now
  `707ab1e4…`; wave HEAD `7bfc8a5f`). Every verdict in this report comes
  from the frozen `c19bec96` archive, not the worktree; the two scratch
  trees used for the stress battery were copied from the frozen archive
  and carry the same `ad9d59b1…` fixture.
- Commit shape `+1775/−3` (net +1772) — the three deletions are the
  shared-line splices (mutex list, mode select, receipt suffix), same
  convention as r86/r87.

## 2. Battery — CWD = frozen tree root (`runs/commands.log`)

| run | window (UTC) | cmd | rc | failures | receipt sha256 |
| --- | --- | --- | --- | --- | --- |
| normal | 07:26:14→07:26:17 | `python3 corpus/fixtures/measure_audio.py` | 0 | `{}` | **`8e8cdad6…`** (canonical pin) |
| r88v1 | 07:26:20→07:26:38 | `… --probe-btwit-r88` | 0 | `{}` | `157dc1582ff1362c401834128556fc8f486c64c7011bdd38404266c63415812e` |
| r88v2 | 07:26:41→07:26:59 | `… --probe-btwit-r88` | 0 | `{}` | `74c488852c5ae00820f9f01f390e67e6b59be30218925213179734e449adeb3b` |
| r88v3 | 07:27:00→07:27:19 | `… --probe-btwit-r88` | 0 | `{}` | `bd3a721ce4d195d05fae4257cf111481a0bc0dbbbd800c9a9bfcb4596f9ddf00` |
| r88v4 | 07:27:25→07:27:43 | `… --probe-btwit-r88` | 0 | `{}` | `13eaf780e4d1bf0030830f72f480739a4ed56d7a5a16adfc373ccdfa23fc0df6` |
| r88v5 | 07:27:43→07:28:01 | `… --probe-btwit-r88` | 0 | `{}` | `fc1e918bc777af45fd4390a419117b0bd505f40e4574e242615fca11bc4544cc` |

- Leg census per run: **79 legs / 3 entries (28/41/10)** — exact match to
  the committed count; no `coverage_blocked` in any run.
- Wall time 18.3 / 17.8 / 18.5 / 18.3 / 18.5 s under loadavg ≈ 75–80 —
  the replays are also load replays. All runs serialized on the frozen
  tree's own family lock.
- Author receipts A1/A2 (lane, untracked working-tree evidence) were
  pinned into `runs/author-A{1,2}.receipt.json`
  (`a1c7746d…`, `cce9164f…`) and used as the comparison baseline; A1/A2
  carry 79 legs / 3 entries, `failures {}`, `blocked {}` too.
- **Wave-level census on identical bytes** (all fixture sha
  `ad9d59b1…`): author A1 + A2 green; **r88-reviewer** r88r1 green
  (07:28:15Z), **r88r2 RED** (07:29:37Z, `wd_dump_empty`), r88r3 green
  (07:29:52Z) — its receipts live under
  `corpus/live/r88-reviewer/tree/corpus/live/runs/` and its stdout
  markers under `corpus/live/r88-reviewer/runs/r88r{1,2,3}.stdout.json`
  (`4e43e313…` / `30fb2028…` / `69c9e960…`); this seat's v1–v5 green.
  **9 green / 1 red in the wave.**
- Headline values (v1, identical shape in all five): `bz_device`
  UUID16 `[1124, 1200]`, `audio_uuids []`; `bz_media1` A2DP 110a+110b;
  `bz_pactl_lines` exactly 1 `session.services` line; `bz_midi_bridge`
  one object, `Midi/Bridge`; `bz_spa_inventory` 14 files; fabrications
  `res:-2/-2/-22/-22` at rc 0 with zero residue; `wd_ls_metadata`
  ls=9 / dump=4 / extra `[35,37,38,41,42]`; `wd_serial_law` 6 matched,
  0 violations; `pt_n1` one all-`C` frame; `pt_n3` 3 frames
  `[C]→[I,S]→[I,S]` (attempt 1); `pt_nneg`/`pt_nabc` SIGKILL at the 4 s
  bound with **4096 B captured in both legs in all 7 receipts**;
  `pt_state_idle` `SUSPENDED/suspended/suspended/S`; `pt_state_active`
  `RUNNING/running/running/R` with a real own link.

## 3. Fixed-path family lock (the r84 fold) — static + executed

**Static (committed blob).** `_btwit_r88_family_lock` (line 27968):
`path = ROOT / "live" / "measure_audio-btwit-r88.lock"` with
`ROOT = Path(__file__).resolve().parents[1]` (line 26). The only
`TMPDIR` mention in the helper is docstring prose; no `tempfile`,
`os.environ`, or argument reaches the path. Acquisition site (29817):
`_r88_family_lock = _btwit_r88_family_lock()   # held to exit` — one fd
for the whole three-entry family.

**Executed (`runs/lockprobe.py`, helper extracted verbatim by anchor,
4/4; `runs/lockprobe.json`):**

1. With `TMPDIR` pointed at a fresh foreign dir, the r88 lock appears at
   `<frozen tree>/corpus/live/measure_audio-btwit-r88.lock` with the
   witness `pid=424242 ns=r88v_ns_424242 role=r88vrole424242`, and
   **not** under the foreign TMPDIR.
2. A second exclusive attempt **blocks** while held
   (`BlockingIOError` on the non-blocking probe; the helper's own
   blocking `flock` acquired only after release) — the "waits HERE"
   serialization is real; after release the same attempt proceeds.
3. **Cross-materialization (r86-F1 corollary, re-realized):** with two
   scratch ROOTs the two lock files are held **simultaneously**
   (`pid=424251`, `pid=424252`) — tree-relative locks do not serialize
   runs from different tree materializations. §8 shows this live.
4. **Control:** the r85 helper's lock lands **under** the foreign TMPDIR
   (`/tmp/r88v-ctl-tmp-…/measure_audio-pactlmon-r85.lock`) and not under
   the tree — the TMPDIR-scoping contrast is proven
   (`runs/lockprobe_r85ctl.json`).

**Lane evidence.** In-window lock witnesses: lane
`measure_audio-btwit-r88.lock` content `pid=1298372` (author A2, 07:23),
frozen-tree lock `pid=1450101` (my v5, 07:28), reviewer-tree lock
`pid=1483465` (07:29) — three distinct lock files concurrently.

## 4. Verdict-surface stability (solo runs)

Tiered comparator (`runs/surface.py`; **exact** = verdict-bearing keys —
exit codes/signals/killed-at-bound/state vocab/booleans/`has_pod`/
`error_class`/`got`/`predicted`/`violations`/counts/layouts/emptiness;
**named** = law-bearing magnitudes/witnesses; **entry** = teardown
projections + `failures`/`coverage_blocked` + foreign census; **analog** =
everything else). Normalization collapses pids, `r88a_/r88v_`
namespaces, ids, serials, remote counters, tmp paths, argv, timings,
census listings (replaced by type+length shape tokens).

| pair | exact | named | entry | analog |
| --- | --- | --- | --- | --- |
| A1 vs A2 (calibration) | 3 | 1 | 0 | 4 |
| v1..v5 vs A1 | 0 | 4 | 0 | 3 |
| v1..v5 vs A2 | 3 | 5 | 0 | 4–5 |

- The A1-vs-A2 calibration is not 0: the author's own two green runs
  differ on **`wd_enum_fmt.error_class`/`error_hit`/`outcome`**
  (`pwcli_remote_eio`/`res:-5` vs `silent`) — the fixture declares this
  path variable ("the refusal path varies run to run … recorded as
  `outcome`, armed only on the no-pod signature"). The arm for that leg
  is `has_pod` only; the comparator's *exact* bucket is a superset of
  the armed fields. All five replays matched A1 on this field and
  differed from A2 by exactly these three recorded values.
- The 4 named diffs in every v-vs-A1 pair are volatile object ids inside
  the recorded `wd_types` typed-pair table plus the foreign census count
  in `wd_info_all.dump_count` (91 vs 92) — recorded, never armed.
- **v1 vs v5 = 0 exact / 0 named / 0 entry** — five solo replays of the
  same bytes produce the same verdict surface. The surface is stable
  **solo**; §6.1 shows it is not stable **co-tenanted**.

## 5. Independent law re-derivation (`runs/laws.py`, no fixture import)

**66 verifier-owned laws × 7 receipts = 462/462 PASS**
(`runs/laws-all.txt`). The laws re-derive, from raw receipt JSON:

- **btabs (19):** positive control; no bluez card/sink; exactly one
  `session.services` advertisement; bluez objects are all `Midi/Bridge`;
  adapter Powered + Media1 110a/110b; every device `audio_uuids == []`
  and carries the HID `1124`; no MediaTransport; 5/5 module/set-card
  refusals `rc 1 + pa_module_noent`; send-message `pa_sendmsg_noent`;
  **the V3 confound** (identical refusal text on a real card + bogus
  profile, normalized-equal stderr); the valid-control `rc 0`; module
  census unchanged and bluez-free; SPA 14 files with ≥8 codec plugins;
  `bluez5.codecs` substring pair + 0 standalone lines; `find` empty;
  **4/4 create-node fabrications** `rc 0` + `can't create node` +
  `res:-2/-2/-22/-22` + class `pwcli_remote_enoent/einval`; zero residue.
- **witdiff (26):** set-rule `got == predicted` on own id/serial and
  foreign id/serial; no nested expansion; mode invariance (`-R`, `-i 0`);
  SPA form carries `id`/`object.serial`; `info` id-keyed singleton
  (serial/dead → `unknown global`, rc 0, empty stdout); `ls` exposes the
  serial; the two prop-block layouts (`ls` flat vs `info` starred);
  key sets equal on Node and Device; JSON types stringified; param names
  equal with `dump_empty ⊆ cli`; four silent-absence classes
  (`pw-dump` dead/abc/huge, `pw-cli info` on ls-only Metadata);
  `pw-dump ''` = full dump; two-arg form honors id1 only;
  `--color=always` ANSI breaks JSON; `pw-dump -1` loud
  `pwdump_invalid_opt`; **`ls Metadata` 9 ⊋ `pw-dump` 4** with the extra
  ids silent on `info`; `info all` omits every Metadata (and describes
  fewer objects than the dump); write-only params return no pod; numeric
  ≡ name on a readable param; `unknown param type`; client
  `not implemented`; dead-serial silent; **pactl index == serial**
  (violations empty, own index follows); four-witness state agreement.
- **pwtop (7):** `-n 1` one all-`C` frame; `-n 0` one frame; `-n 3`
  last frame real with first all-`C`; `-n -1`/`abc` bound-killed with
  frames; `-r bogus` `rc 255 pwtop_connect_down`; idle and active
  four-witness vocab agreement.
- **custody (12):** per entry `sinks_gone` all-true, `own_nodes_after`
  `[]`, unloads name-verified (`verified_index == captured`,
  `recycled false`, `exit_code 0`), `failures`/`coverage_blocked` empty.

The three laws that initially "failed" were bugs in *my* law code
(empty-list falsiness; reading the in-run-only `_frames_cache`; reading
`frames` on legs that never set it) — fixed against the recorded shape
before the 462/462 run; no fixture-side failure surfaced in the receipts
the laws read (the reds in §6.1 are arm failures, and my law set
re-derives the *laws* from the same receipts without tripping).

## 6. Mechanism probes (falsification attempts)

### 6.1 The four flaky arm classes (co-tenancy stress, measured)

`runs/co_tenancy_runs.py`: **3 concurrent `--probe-btwit-r88` runs from 3
distinct tree materializations × 3 rounds = 9 runs** (identical fixture
sha `ad9d59b1…`), all under the ambient load. Result **7/9 red** with
four distinct classes (`raw/co-tenancy-runs.json`):

| arm class | mechanism (from the red receipts) | reds |
| --- | --- | --- |
| `wd_dump_empty` | **bracket race.** The arm requires the `pw-dump ''` id set to equal census c1 **or** c2; every `pw-dump`/`pw-cli` invocation is itself a transient Client, so the set drifts by ±1 object between the three invocations. Measured shape: c1 104 → mid 103/104 (different id set) → c2 104/103; e.g. r88-reviewer's r88r2: census 97, mid 98, both `equals_*` false | **6/9** (and the wave-level r88r2) |
| `wd_cli_meta_extra`, `wd_silent_cli_meta` | **foreign registry-death lines on stderr.** A one-shot `pw-cli info <id>` can carry `remote 0: error id:108 seq:<n> res:-2 …: no global 98` + `unknown resource 108 op:7` from a *foreign* object dying mid-command; the arms require both channels empty (stdout is empty — the stderr line flips them) | **3+1/9** |
| `wd_enum_num2` | **same pollution breaks the `≡` byte-comparison.** `enum-params <id> Props` stderr carried `… res:-116 (Stale file handle): no global 249 any more` while `enum-params <id> 2` was clean; the arm compares `norm(stdout+stderr)` of the two calls. The stdout prefixes are byte-identical — the **law is intact**, the arm is not | **3/9** |
| `bz_create_midi`, `bz_create_a2dpsource` | **`error_class` precedence vs foreign churn (r87-F4 realized).** The create-node refusal itself is correct (`can't create node: Invalid argument`), but a preceding foreign `res:-2 … no global <id>` line makes the inherited class table report `pwcli_remote_enoent` before `pwcli_remote_einval` → the arm's fixed class mapping fires. Same for `a2dp-sink` in the mirror direction | **2/9** |

Aggregate: **7/9 red under 3-way concurrency**; the wave's own
natural-rate red (r88-reviewer r88r2, 07:29:37Z) coincided with this
seat's spot battery (null-sink load/unload + own `pw-play` stream +
hundreds of `pw-dump` clients) as the co-tenant — i.e. the wave runs
*exactly* this way (the r87 report already recorded cross-tree
co-tenancy "3rd round running"). Solo runs (A1, A2, v1–v5, r88r1,
r88r3) are green.

### 6.2 `pt_nneg`/`pt_nabc` frame arm — a flush-timing lottery (minor)

The `frames ≥ 1` conjunct reads the first 200 bytes of a SIGKILLed,
block-buffered stream (`keep_raw` not set on those legs). Own runner
replicating the fixture's discipline (`runs/infinite_flush.py`, 5 reps
per cell): at the shipped **4.0 s** bound **0/10 empty captures**
(4096–8192 B, frames 10/10); at a shorter **3.0 s** bound **1/10
empty**. One live realization: spot E's `-n abc` returned 0 captured
lines (killed-at-bound still true). The law is intact; the secondary
frame arm is the fragile part.

### 6.3 `wd_dump_empty` bracket race — independent replay

`runs/dumpempty_race.py` (40 solo + 40 churned reps of the fixture's
bracket shape c1 → ~20 transient clients → `pw-dump ''` → c2):
**0/80 false-FAILs solo** (with extra churn the mid dump matched c2
40/40 and c1 only 13/40) — i.e. the race needs *concurrent* churn in the
mid→c2 window, which is why solo runs pass and the 3-way stress fails
6/9. The arm is fail-closed but not churn-immune.

### 6.4 The corpus contains one RED dev receipt

Untracked `corpus/live/runs/20261016T071710822152Z-btwit-r88/`
(07:17:10Z, pid 900201) is a **pre-fix iteration**: 75 legs (28/39/8,
`pt_n2`), 14 failures — the r88-local error classes were not yet in the
table (`cli_cant_create` on all four fabrications), `bz_pactl_lines` 0
matches, `wd_mode_spa`/`wd_ls_serial`/`wd_propblock`/`wd_ls_metadata`
not yet fixed, state legs' top witness absent. Every one of those
classes is fixed in the committed block. It is *not* the landing and its
custody fields are clean (`sinks_gone {r88a_ns_900201: True}`,
`own_nodes_after []`). Disclosed so a later reader does not misread it
as a committed red.

### 6.5 Labrat (frozen probeParent duty, exactly one)

`ufo-labrat` agent `0789feda`, read-only, bounded: static arm-table scan
of the r88 block against the r87-F1 class. Verdict **CONFIRMED for the
r87-F1 class** (no `[-N:]` session-log window anywhere; `error_class` is
computed pre-truncation at line 27686) with two residual flip paths
(`pt_nneg`/`pt_nabc`; `wd_cli_id` — measured margin ≈2.2 KB) and one
coverage-narrowing (false-PASS-direction) class (`bz_tree` enumeration
on truncated `busctl tree`). Verbatim in `labrat/labrat-report.md`. The
labrat's static reading did **not** surface the §6.1 classes — they are
only visible when the probe runs co-tenanted; this seat's stress battery
is what exposed them.

## 7. Independent spots (own code, own `r88v_<pid>` namespace)

`spot/spots_r88v.py` + `spot/spotF2.py`; raw receipts in `spot/raw/`,
consolidated in `spot/spots-r88v.json` / `spot/spotF2.json`. Every
object created was `r88v_`-tagged and destroyed by name/id; never
`set-default-*`.

| spot | result |
| --- | --- |
| A — bluetooth absent-class | 1 adapter, 1 device `dev_BC_C7_46_34_C5_66`, UUID16 `[1124,1200]`, `audio_uuids []`, `Connected b false`; `pactl list` 1 match = `session.services`; cards/sinks bluez-free; graph's only bluez object `bluez_midi.server` `Midi/Bridge`; SPA 14; codecs strings both, 0 standalone; `find` empty; refusals 4/4 `rc 1 Failure: No such entity`; send-message `rc 1`; set-card absent `rc 1`, bogus-profile-on-real-card **identical text** `rc 1`, valid control `rc 0`; **fabrications 4/4 `rc 0` res:-2/-2/-22/-22 with zero residue/new ids**; module set unchanged |
| B — `{id ∪ serial}` set rule | **138/138 live keys match** the predictor (own code, two censuses, re-census on mismatch), 0 churn, 1 silent-absence key (dead mid-sweep: `pw-dump <K>` rc 0, both channels empty) |
| C — Metadata split | `pw-cli ls Metadata` **9** ids vs `pw-dump` **4**, extra exactly `[35,37,38,41,42]`; `info` on an ls-only id rc 0 **silent both channels**; `info all` described 86 of 92 with **0** Metadata |
| D — pactl index == serial | **14/14** (6 sinks + 2 real sources + 6 monitor pseudo-sources, each resolving to its parent sink's serial), 0 violations |
| E — pw-top traps | `-n 1` one all-`C` frame; `-n 0` one frame; `-n 3` 3 frames, last real `[I,R,S]`; `-n -1` SIGKILL at bound with 41 lines / 4 frames; `-n abc` SIGKILL at bound but **0 captured lines in that instance** (the §6.2 realization); `-r bogus` rc 255 `Can't connect: Host is down` |
| F — four-witness state agreement | own null sink: idle `SUSPENDED/suspended/suspended/S`; driven by own `pw-play` stream with a real link (`r88v_pt → r88v_ns`): `RUNNING/running/running/R`; name-verified unload (`sink_name_ok`), sink gone, zero residue |

## 8. Custody, contention, host state

- **Custody (this seat):** post-state 07:34:53Z — **0** `r88v_` nodes,
  **0** owned modules, no `pw-play`/`pw-top`/`pw-cli` processes of mine;
  the two tone fixtures live under `spot/raw/`; the only created state is
  the frozen tree's btwit lock + receipts under the gitignored tree dir.
- **Custody (landing):** 7/7 receipts carry `sinks_gone` all-true,
  `own_nodes_after: []`, `verified_index == captured`,
  `recycled: false`, `exit_code 0` unloads; no `residual_destroy` path
  fired in any run. Default sink/source unchanged
  (`…HiFi__SPDIF__sink.29` / `…HiFi__Line__source.29`).
- **Co-tenancy ledger (read-only observation; this seat touched no
  foreign object):**
  - the **r88 reviewer** ran the *same probe* three times from its own
    frozen tree (`corpus/live/r88-reviewer/tree`, pids 1458207/1481496/
    1483465, 07:28:15–07:30:10Z) — its own `r88a_ns_*` sinks and
    `r88a_*_pt` streams were visible in my censuses; its r88r2 is the
    wave's natural-rate red;
  - a lane run (pid 1492742, lane worktree) and `r89a_dev*` namespaces
    appeared later in the window (sibling rounds);
  - three distinct `measure_audio-btwit-r88.lock` files existed
    concurrently (lane, reviewer tree, my frozen tree) — §3.3's
    executed cross-materialization proof, live;
  - ambient foreign residue (untouched): `r87t_ns`, `r84a_probe_548706`
    null sinks, `r89a_dev2_ns`/`r89a_dev2_pl` (sibling mid-work at
    post-state).
- **Interference by this seat:** 1 normal + 5 probe runs (frozen tree),
  3 stress rounds × 3 trees (9 probe runs), three spot batteries (two
  aborted at the final spot; the instrumented re-run is `spotF2`), two
  `spotF2` runs, 80 dump-empty race reps, 20 bound-killed `pw-top` reps,
  ~10 lock-probe children. No `set-default-*`, no foreign writes.

## 9. Findings (ranked)

**Cross-reference (independent seats, same round).** The r88 reviewer
(`reports/round-88/r88-reviewer.md`, committed as `7bfc8a5f`) replayed
the same bytes three times from its own frozen tree and found the same
`wd_dump_empty` false-FAIL (its F1; r88r2) with a deterministic churn
reproduction — independent corroboration of this seat's F1, reached
without seeing this seat's stress battery. Its fail-open findings
(F2 `bz_device` negative-only arm, F3 unrecorded missing-leg skips,
F4 latent `IndexError` in `wd_no_nested`, F5 silent lock-open failure,
F6 dev-run disclosure) stand as filed and are complementary to the
below; this seat's F5 is the same lock-scope class as its F7. The
novelty here is F2/F3: the reviewer's audit covers the *green* receipts'
laws (106 checks) and its F1 covers the one red it saw — the
**foreign-stderr pollution class (F2/F3) only appears under the 3-way
stress** and was not surfaced by any other seat's method.

- **F1 (blocking for a "green gate" reading) — `wd_dump_empty` is a
  bracket race.** The arm requires the `pw-dump ''` id set to equal c1
  or c2; transient clients (its own and every co-tenant's) drift the set
  by ±1 between invocations. Observed: the wave's own r88r2 red (census
  97 / mid 98 / both brackets false) and 6/9 of the stress runs; solo
  probe 0/80. The law (`''` is the full dump) is intact. Minimal
  repair: compare the mid set against a *union/tolerance* rule (e.g.
  require c1 ⊆ mid ∪ {transient clients}), or take c1 and c2 with
  `pw-dump` in the same process/socket and compare against a
  re-census taken immediately around the mid dump.
- **F2 (blocking for a "green gate" reading) — "both channels empty"
  arms are polluted by foreign registry-death lines on stderr.**
  `wd_silent_cli_meta`, `wd_cli_meta_extra`: a one-shot `pw-cli info
  <id>` prints `remote 0: error … no global <id>` when a *foreign*
  object dies during the ~10 ms invocation. Measured 3+1/9. The
  `wd_silent_dump_*` legs carry the same emptiness assumption (not
  observed red in the stress). Minimal repair: ignore
  `remote 0: error .*: (no global|unknown resource|Stale file handle)`
  lines when judging the silent classes (the fixture already records the
  pattern class in its own evidence).
- **F3 (blocking for a "green gate" reading) — `error_class` precedence
  is churn-sensitive (r87-F4 realized).** `bz_create_midi` /
  `bz_create_a2dpsource` flipped to `pwcli_remote_enoent` because a
  preceding foreign `res:-2 … no global <id>` line is scanned before the
  real `res:-22` refusal line. Measured 2/9. Minimal repair: derive the
  class from the `can't create node: <text>` line (or from the last
  matching line), not the first table match over the whole stderr.
- **F4 (minor) — `pt_nneg`/`pt_nabc` frame arm** reads a 200-byte
  truncated capture of a SIGKILLed buffered stream; 0/10 empty at the
  shipped 4 s bound, 1/10 at 3 s, 1 live realization (§6.2). Minimal
  repair: arm `killed_at_bound` alone or read `stdout_raw`.
- **F5 (structural, carried) — cross-materialization lock scope.** The
  fixed path is ROOT-relative (`Path(__file__)`), so every frozen-tree
  seat locks its own file; executed proof (two ROOTs hold two locks
  simultaneously) and live in-window (lane + reviewer tree + verifier
  tree locks concurrently). Same class as r87-F2 — the fold closed
  `$TMPDIR` but not materialization; and per F1–F3 the co-tenancy it
  permits is exactly what makes the arms flaky.
- **F6 (observation, declared variance) — `wd_enum_fmt` refusal path.**
  A1 `pwcli_remote_eio`/`res:-5` vs A2 `silent`; the arm is `has_pod`
  only and the author report declares the variability. No action.
- **F7 (observation, corpus hygiene) — one RED dev receipt is in the
  untracked corpus** (`20261016T071710822152Z-btwit-r88`, 75 legs, 14
  failures, pre-fix). Not the landing; every class it failed is fixed.
- **F8 (observation, false-PASS direction) — `bz_tree` device
  enumeration runs on 2400-truncated `busctl tree` output** (labrat
  §Fragile-3) — tail devices can be dropped → subset judging. Cannot
  produce a false-FAIL; ~90 B on this host.
- **F9 (observation, weak arm) — `wd_enum_num2` compares 2400-byte
  prefixes** of two 2497-byte outputs (self-masking truncation), on top
  of the F2 stderr exposure. The `≡` law was independently re-derived on
  the same prefix.

## 10. Risks / blockers

- **Blocker for a "green gate" reading: F1–F3.** On the frozen bytes
  the landing's verdict is not reproducible under co-tenancy (7/9 stress
  reds; 1/10 wave runs red; both author runs and all five of this seat's
  solo replays green). The reds are the arms, never a falsified law —
  every encoded claim re-derives clean, and the reviewer's own red run
  is green on the same receipt for all other legs.
- Carries for the wave-B fold: **F1** (bracket tolerance/re-census),
  **F2** (filter foreign remote-error lines in the silent-class arms),
  **F3** (class from the refusal line, not the first table match),
  **F4** (drop the frame conjunct), **F5** (state the intended lock
  scope), **F7** (note/prune the dev receipt), **F8** (full-capture
  enumeration or record the truncation as coverage).
- No custody, integrity, or identity risk: fixture bytes, lock fold,
  teardown, and the canonical normal pin all verify.

## 11. Evidence index

- Frozen tree: `corpus/live/r88-verifier/tree/` (regenerable, gitignored);
  `runs/tree-files.txt`, `runs/ls-tree-c19bec96.txt`,
  `runs/tree-symdiff.txt` (0 lines), `runs/fixture-sha.txt`,
  `runs/pycompile.txt`.
- Battery: `runs/commands.log`, `runs/normal.receipt.json` (+stdout/stderr),
  `runs/r88v{1..5}.receipt.json` (+stdout/stderr), `runs/receipt-shas.txt`,
  `runs/author-A{1,2}.receipt.json`.
- Surface: `runs/surface.py`, `runs/surface-*.txt` (11 pairs).
- Laws: `runs/laws.py`, `runs/laws-all.txt` (462/462).
- Lock: `runs/lockprobe.py`, `runs/lockprobe.json`,
  `runs/lockprobe_r85ctl.py`, `runs/lockprobe-r85ctl.json`,
  `runs/hold-*.json`, `runs/try-*.json`.
- Co-tenancy stress: `runs/co_tenancy_runs.py`,
  `raw/co-tenancy-runs.json` (9 runs, 7 red; scratch trees under
  `runs/cotree/`, regenerable).
- Mechanism: `runs/infinite_flush.py`, `raw/infinite-flush.json`,
  `runs/dumpempty_race.py`, `raw/dumpempty-race.json`.
- Spots: `spot/spots_r88v.py`, `spot/spots-r88v.json`,
  `spot/spotF2.py`, `spot/spotF2.json`, `spot/raw/spot{A..F}.json`.
- Labrat: `labrat/labrat-report.md`.
- Wave-level red (external, read-only): the r88 reviewer's
  `corpus/live/r88-reviewer/tree/corpus/live/runs/20261016T072937176820Z-btwit-r88/`
  and `corpus/live/r88-reviewer/runs/r88r{1,2,3}.stdout.json`.
- Custody/state: `runs/pre-state.txt`, `runs/post-state.txt`,
  `runs/worktree-tracked.txt` (only the pre-existing pyc is dirty).
- Manifest: `manifest.json`, `manifest.sha256` (seat files; `tree/`,
  `runs/cotree/`, scratch roots excluded).
