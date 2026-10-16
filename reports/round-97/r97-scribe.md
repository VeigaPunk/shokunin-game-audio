# r97 SCRIBE — custody audit of the `wppol` landing `b8ff4efc`

**Seat.** `scribe` (UFO-FSD scribe custody audit; not a judge). **Target repo**
`/home/vgpnk/Projects/shokunin/audio-shokunin`. **Landing under audit**
`b8ff4efce1c7b569875ee160decd16830925dbff` — *"r97 author: wppol WirePlumber
policy lattice (5 entries/69 legs, +2156/-3)"*, committer `ci <ci@local>`,
2026-10-16 07:01:30 -0300. **Host** `plazir27`. **Audit window** 2026-10-16
07:18Z–07:30Z (local, UTC−3).

**Method — read-only.** Every fact below is either (a) a hash/byte/count read
of an existing artifact, (b) a JSON field read out of the receipts, or (c) a
line-level inspection of the committed fixture. **No battery, probe, private
daemon, or fixture execution was performed by this seat**, and nothing was
committed, staged, or pushed. Where a live counterexample exists only in a
sibling seat's report, it is cited as *that seat's* observation and labelled as
such — never upgraded to my own measurement.

**State at audit time.** `git rev-parse HEAD` = `a2c6e3b7` (r90 adjudication on
top of `b8ff4efc`; the landing is unchanged). Registered worktrees include
`audio-shokunin/audio-shokunin-wt-r97` @ `5755be5b` (branch `wt-r97`) and
`/home/vgpnk/Projects/shokunin/critic-r97/wt` (detached at `b8ff4efc`).

**Dispatch-path note (verbatim).** The assignment named the receipts at
`../audio-shokunin-wt-r97/corpus/live/r97-author/`. No sibling
`/home/vgpnk/Projects/shokunin/audio-shokunin-wt-r97` exists; the receipts were
found at the **nested** worktree
`/home/vgpnk/Projects/shokunin/audio-shokunin/audio-shokunin-wt-r97/corpus/live/r97-author/`.
That nested directory is a registered `git worktree` of the same repository
(`.git` file, `git worktree list`), not a copy. All receipt paths below resolve
there.

---

## 1. Landing anatomy (committed diff)

| check | command | observed |
|---|---|---|
| diff stat | `git show --numstat --format=… b8ff4efc` | `2156 3 corpus/fixtures/measure_audio.py`; `367 0 reports/round-97/r97-author.md`; `80 0 reports/round-97/r97-integrate.md` |
| deletions | `git show b8ff4efc -- corpus/fixtures/measure_audio.py \| grep -nE '^-[^-]'` | exactly **3** lines: the probe-mutex `if sum([…]) > 1:` list, the `mode` ternary, the `suffix` ternary — matching the author's "the deletion set is exactly the mutex-list, mode-select and receipt-suffix lines" |
| family block byte-identity | `git show b8ff4efc:… \| sed -n '43788,45905p' \| sha256sum` vs `sed -n '31091,33208p'` on the worktree file | `f58f0290fff2f76c5c343db643585d3b9bb32912dee99aa7e129f262cc8243f5` **both sides** (2118 lines) |
| dispatch block byte-identity | same method, `46710,46743` vs `33808,33841` | `68de4d267dded2a4ad2c5ae5f5a7a59e823d63d594bdcd8a8a48317644dea3b9` **both sides** (34 lines) |
| wiring splices | `grep -n 'probe_wppol_r97\|probe-wppol-r97\|-wppol-r97'` on the committed blob | 5 sites: `46041` argparse row, `46051` mutex head, `46710` dispatch, `47394` mode ternary, `47414` suffix ternary — the author's five declared splices |
| commit identity | `git show --format='%H %an %ae %ad %s'` | `ci <ci@local>` — the author's "the orchestrator commits" is consistent with the metadata but **not verifiable from artifacts** (who invoked the commit is not recorded) |

## 2. Claim → artifact reconciliation

### 2.1 The fixture hash claim (the one real drift, and it is disclosed)

| artifact | sha256 | bytes | lines |
|---|---|---|---|
| author's frozen worktree file (claim of record) | `f0eb6c509ecc20bff8a4652ec09e2ddf6607153fc01fbe150e679aee54b7d50e` | 1 728 061 | 34 522 |
| **committed blob** `b8ff4efc:corpus/fixtures/measure_audio.py` | `7a070fa817c4de6f4ae5eb5be38e7cfc2cdbb18cad605ee52427afcf0a6ca2bc` | 2 347 038 | 47 424 |
| parent blob `5755be5b:…` (worktree base) | `d4b2e088bbfaa71f7cb19123c36b1646681009237f5d6049686789c157171e65` | 1 627 588 | 32 369 |
| main working tree at audit time (dirty, **not** r97) | `e2e5a002a701bf5165cc04ee2f20e473148723df379b0f72058716187df18923` | 2 371 546 | 47 889 |

- `r97-author.md` §Evidence calls `f0eb6c50…` the **"Final fixture sha256
  (34 522 lines; +2156/−3)"**. That is exactly the *worktree* file: it is the
  r89-fold base (`5755be5b`) plus the r97 block (net +2153 lines = +2156/−3).
  It is **not** the landed bytes.
- `reports/round-97/r97-integrate.md` discloses this in its own table
  (hashes truncated here; full 64-hex in that file):
  *"merged sha `7a070fa8…` (47424 lines) — **≠** the WT file's `f0eb6c50…`
  (expected: the merged file carries main's r90–r96 blocks on top)"*.
- `r97-verifier.md` §9 independently flags it: *"the author's full-file sha
  (`f0eb6c50…`) is not the committed sha (`7a070fa8…`), and the author's
  receipts were produced on a base that lacks r90–r96. Both verifier runs were
  produced on the committed base and are green, which is the transfer test."*
- **Consequence for custody:** the two author battery receipts were produced on
  bytes that were never committed. The transfer to the landed bytes is covered
  by two independent green runs on the committed blob (critic full battery
  `51d95b79dd89f708132742b1a5094bad19644cb8dc0969fdce145e6f78f709e9`;
  verifier's two runs, §2 of that report) — the *mechanism* evidence transfers,
  but the author's own receipts are **not** receipts of the landed file, and no
  receipt records a fixture hash at all (`grep -c fixture_sha256` on all four
  wppol receipts = 0). The fixture→receipt binding is the report plus
  `corpus/live/r97-author/fixture-sha256.txt`, not the receipt.

### 2.2 Claims I reproduced from the receipts (all four: 2 pre-freeze smoke + 2 final)

Commands: `sha256sum` over `receipts/*.json` vs `runs/*-wppol-r97/measurements.json`;
a Python recount over `measurements.json` using the disclosed context-key rule.

| claim | observed |
|---|---|
| receipt copies == canonical run receipts | **byte-identical, 4/4** (`2d257486…`, `6d9ffbac…`, `470116a2…`, `c795d24b…`) and equal to the shas in `RECEIPTS.txt` |
| `r97-author.md` sha `f912538c…` | ✓ both in main and in the worktree (367 lines) |
| 69 leg keys, 14/15/21/15/4 | ✓ **in all four receipts** (arming 14, defaults 15, linking 21, wpexec 15, settings 4) |
| `failures: {}`, no blocked classes | ✓ all five entries in all four receipts; `coverage_blocked` absent in the final two |
| 17 base entries, 14 legs each, green | ✓ 17 non-wppol entries present in all four, zero failures |
| battery exit 0, both final runs | ✓ `battery-final{1,2}.log` + `battery.log` (`BATTERY DONE 09:52:58`) |
| `own_procs_after: []`, `shared_census.own_hits: []` | ✓ 5 entries × 4 receipts |
| w1 inventory 39 present / 26 absent, `_G` nil, `_ENV` table, Lua 5.5, `debug.getregistry` present | ✓ counted from `w1_inventory.stdout`: 39 FOUND tokens, 26 MISSING tokens, `ENV=table G=nil VERSION=Lua 5.5`, `debug.getregistry=function` |
| s1/s4 lattice: 25 keys, listing sha `56526540bdc17f52…`, install-scoped | ✓ both receipts: `n_keys 25`, `sha256 56526540bdc17f5287f59d057edebf22d5de61653f622dc990a28e382db48a46`, s4 `same_key_set: true` |
| s3: private read-back flips, operator's value unchanged | ✓ `set_rc 0`, `private_readback "Value: false\n"`, `shared_before == shared_after == "Value: true\n"` (recorded — see F1 below for the *unarmed* half) |
| d9/d12/d13 as narrated | ✓ `d9` both metadata rows + `state_file_row_secs 1.003/1.002`; `d12` `state_file_at_set ""`, `t_set_to_restart_s 1.306/1.305`, `default_after` = the other sink, `configured_after null`; `d13` row at `1.003` and survives |
| a3/a4/a6 raw-log claims | ✓ re-read from the author's own roots: a3 log ends `Failed to load configuration: Could not locate configuration file 'wireplumber.conf'`; a4 opens the *copy's* conf + copy fragments and never `/usr/share/wireplumber/wireplumber.conf.d`; a6 opens the shim-HOME fragment `conf/home/.config/wireplumber/…/10-r97a-user.conf` + shipped `alsa-vm.conf` |
| "no operator config/state was read" | ✓ `grep -rl 'vgpnk/.config/wireplumber\|vgpnk/.local/state/wireplumber'` over the four battery root families returns **no files** |

### 2.3 Claim that does not reproduce

| claim | artifact | observed |
|---|---|---|
| `RECEIPTS.txt`: "private instance roots … **36 dirs / 13 MB**" | `du`/`os.walk` over the 36 roots whose pid is an author run pid (`3685894`, `3997488`, `218888`, `443725`, + 16 dev pids) | **36 dirs ✓** but **11 050 976 B = 11.1 MB**, not 13 MB. The critic measured the same 11.1 MB. Bookkeeping drift, no mechanism impact. |

## 3. Private-daemon lifecycle custody

- **Start custody.** Every root under `$TMPDIR` (`TMPDIR=/home/vgpnk/Projects/shokunin/tmp`)
  carries its own `conf/` with `xdg-config/wireplumber/wireplumber.conf.d/10-r97a.conf`
  disabling `hardware.audio/bluetooth/video-capture` (verified by grep) and a
  *copy* of the shipped `wireplumber.conf` (`conf/wp-copy/`) plus private
  `xdg-state`/`xdg-data`/`home` trees — the author's isolation claim is
  artifact-visible, not just narrated.
- **Stop custody (recorded).** Each entry's teardown stops the pair by pid file
  (`run/{wp,core}.pid`) with `_wppol_r97_kill(..., grace=8.0)`; the receipts
  record `stops` and `wp_restarts`, and every entry ends with
  `own_procs_after: []` + `shared_census.own_hits: []`.
- **Stop custody (measured now).** 21 pid files across the 36 author roots →
  **0 live (non-zombie)**; a `/proc` scan of `cmdline`+`environ` over all
  same-UID processes names **no** `wppol-r97-*` root (the only hit was this
  audit's own shell); **0** socket-ish entries under any root. So the retained
  36 roots are inert: no daemon, no socket, no zombie.
- **Retention.** The 36 roots (11.1 MB) are retained deliberately and disclosed
  in `r97-author.md`; the count matches the critic's independent 36.
- **Family lock.** `audio-shokunin-wt-r97/corpus/live/measure_audio-wppol-r97.lock`
  exists (27 B: `pid=443725 tag=r97a_443725`), its `flock` is **free** at audit
  time (`flock -n` acquired), and pid 443725 is **gone**. The lock path is
  `ROOT/live/…` (tree-relative) — the critic and the verifier both note this is
  the inherited r84 design, and the verifier's F3 records that it serializes
  same-tree runs only. Main's checkout carries **no** wppol lock
  (`ls corpus/live/ | grep wppol` → nothing), which matches the integrate
  note's "no lock, receipt or run dir written by any parse-only exit".
- **Latency caveat (carried from the critic, code-confirmed).** Every stop
  record is `grace + 0.305` (`4.303`/`8.305`; the `+0.305` is the trailing
  `time.sleep(0.3)`), because the death detector is `os.kill(pid, 0)` on an
  unreaped child. The recorded `sig: "KILL"` therefore cannot distinguish
  SIGTERM-death from SIGKILL-escalation. **I confirmed the code shape
  (`_wppol_r97_kill` lines 44226–44262) and the numbers in the receipts; I did
  not re-run the zombie experiment.**

## 4. Kill-guard honor

- **Code as landed** (committed lines 44208–44263): `_wppol_r97_own(root, pid)`
  returns `tag.encode() in cmd or tag.encode() in env` — a **substring** test
  over `/proc/<pid>/cmdline` **or** `/proc/<pid>/environ`; `_wppol_r97_kill`
  refuses with `{"killed": false, "reason": "REFUSED foreign pid"}` when the
  predicate is false, and otherwise signals the **process group**.
- **`pkill` absent.** `grep -c 'pkill'` on the committed file = **0** — the
  author's "`pkill` appears nowhere" reproduces.
- **Refusal direction works.** Verifier §5/§0 (that seat's probe): foreign pid
  **REFUSED and survived**, own pid killed, a live private core recognised and
  left alone; no receipt contains a `REFUSED foreign pid` string (my grep over
  all four = 0 matches), i.e. the refusal path did not fire during the r97 runs.
- **Over-match direction is a real defect (critic F4, that seat's live
  counterexample, quoted verbatim):** *"a foreign `tail -f
  <root>/logs/reader-target.log` (clean env, started by the critic) →
  `_wppol_r97_kill` returns `{"killed": true, "sig": "KILL"}`. The predicate
  (44208) is "cmdline **or** environ contains the root path", not "is a process
  this seat started"."* The author's absolute sentence — *"the kill **refuses**
  anything else"* — is therefore **not supported**: a foreign process that
  merely mentions the private root path is signalled. My code read confirms the
  predicate shape that makes F4 possible; **I did not re-run the surgical
  probe.**
- **No evidence of a foreign signal in r97's own runs:** the receipts record
  only own-pid stops, `foreign_r97a_nodes: []`, and the shared census
  (`objects: 100, own_hits: []`, `shared_daemons: {}`). The verifier separately
  records the shared daemons' pid+start time unchanged. The defect is a
  *capability* finding, not an observed foreign casualty in this round.

## 5. The "no pactl" claim vs receipts (critic F5) — **falsified as written**

Author (`r97-author.md`, Custody): *"No `pactl` call of any kind is made by
this family."* Critic F5: *"report claim falsified: "No `pactl` call of any kind
is made by this family" (r97-author.md, Custody)."*

Reproduced from the artifacts, three ways:

1. **The receipts carry pactl output.** Every wppol entry in all four receipts
   has `oracle_at_start.sink_pactl = "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink"`,
   `source_pactl = "alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source"`,
   `pactl_exit: 0` — fields that can only be filled by running `pactl`.
2. **The code path.** `_wppol_r97_entry_head()` (committed 44666 ff.) calls
   `_capture_inventory()` once and `_loopback_r79_oracle()` once. Those
   inherited helpers invoke `pactl list sources short`, `pactl info`
   (`_capture_inventory`, 3150 ff.) and `pactl info` again via
   `_loopback_r79_pactl_defaults` (8929 ff.) — 3 read-only calls × 5 entries ×
   every battery run.
3. **What *is* true.** The r97 block itself contains exactly **two** `pactl`
   string occurrences, both inside a single comment line (block-relative line
   65): *"paths where pactl is used at all, never pactl set-default-*, bounded"*.
   The only `pactl set-default-*` **invocation** in the committed file is at
   line 7107, inside `playback_default_follow_r78_entry()` (r78), which the r97
   block calls **0** times. So the intended narrower claim — *no `pactl`
   write, `pactl set-default-*` never called by this family* — holds, and the
   verifier's header states it that way (*"no `pactl set-default-*` anywhere"*).

**Net:** the sentence in `r97-author.md` is a provenance error in the report
(not in the fixture); the same file's `sinks_gone` rationale ("no pactl sinks
are used") remains defensible because no pactl *sink* is created.

## 6. Conflicts and sibling findings, recorded verbatim for the canonical judge

The canonical Rust runtime is the sole judge; nothing here adjudicates them.
Numbering **collides** between the two sibling reports (critic F1 = s3
fail-open; verifier F1 = s1 sha) — labels below carry their source.

| id | source | one-line substance |
|---|---|---|
| F1 | critic | `s3_write_scope` cross-witness recorded, **never asserted** (fail-open); live counterexample P3 (`shared_before='Value: true'` vs `shared_after='Value: false'` and still `failures: []`). My code read confirms: `shared_before`/`shared_after` are recorded at 45871–45872 with no comparison; `sha_matches_boundary` (45830) likewise never asserted |
| F2 | critic | `a3_conf_dir_missing.errclass` is a constant literal, not an observation; `a9` mirrors it as `[None, None]` |
| F3 | critic | stop/restart bookkeeping is zombie-blind: every latency `grace + 0.305`, `t_set_to_restart_s` is not a restart latency (`t_set_to_SIGNAL_s = 0.004` vs `1.305`); `own_procs_after: []` means "no **live** own process" |
| F4 | critic | kill guard over-matches (foreign reader killed); the report's absolute "refuses anything else" unsupported |
| F5 | critic | "no `pactl` call of any kind" falsified (this §5) |
| F6 | critic | `d9_lag_s` re-measures `state_file_row_secs` — 1 of the 15 defaults legs adds no observation (distinct observations 68, not 69) |
| F7 | critic | dead code: `WPPOL_R97_SINK_D` and three unused parameters |
| F1 | verifier | settings listing sha computed but not armed (same class as critic F1's second half) |
| F2 | verifier | `a9` `errclass` `[None, None]` recorded, not a defect (agrees with critic F2) |
| F3 | verifier | family lock is tree-relative — same-tree exclusion only |
| §7 | verifier | **disclosed self-inflicted incident**: `cp -al` hardlink copy + `cp` over the fixture wrote *through* the shared inode and mutated the frozen tree; detected by the sha check, the mutated run was killed mid-flight, fixture and tracked `.pyc` restored from the archive; `tar -df` clean (0 "Contents differ") |
| §9 | verifier | author base lineage `5755be5b` ≠ committed lineage; the full-file sha difference is stated as a transfer risk |

**No conflict found between the two siblings' measurements**: critic F3
(zombie artifacts) and verifier F5 (`d9`/`d13` = 1.002/1.003, `d12` =
1.304) are the same numbers under the same explanation; verifier's guard
three-arm probe and critic's F4 differ only in probe shape (a foreign process
that *names the root* vs one that does not).

## 7. Out-of-scope dirt observed (not this landing, recorded so it is not misread as r97)

- **Main working tree is dirty on the audited file, by a foreign lane.**
  `git diff --numstat HEAD -- corpus/fixtures/measure_audio.py` = `659 194`
  (`sha e2e5a002…`, 47 889 lines, mtime **07:19:11** — *after* this audit
  began). Every hunk header names `_wpstate_r90_*` / `wpformat_r90_*` /
  `def main()`, and `grep -cE '^[+-].*(wppol|r97a)'` over that diff = **0** —
  i.e. the r90 foldfix lane's in-progress edit, untouched by r97.
  `reports/round-90/r90-author.md` is likewise `M`.
- Other untracked residue in main's `corpus/live/`: fixed-path locks from
  r86–r96 (`pwctl`, `pwbind`, `btwit`, `pwprof`, `sox`, `jack`, `pulsecli`),
  and the r97 run dirs live **only** in the worktree (main has none).
- `critic-r97/wt` remains registered as a worktree detached at `b8ff4efc`
  (its own report says "prune it when the archive is no longer wanted");
  `git worktree list` also shows a prunable `/tmp/audio-prefold`.
- The critic §6 ledger records **two orphaned r99 private pairs from 06:16**
  alive 52 min later — explicitly *not* r97 residue. This seat did not touch
  them.

## 8. Known limits of this audit

1. **No execution.** No fixture run, no daemon, no probe. Every "live" claim
   above belongs to the critic or the verifier and is labelled with its source.
2. **`/proc` coverage.** My process scan reads `environ` only for same-UID
   processes (others return EACCES); a root-naming process owned by another
   user would be invisible. The verifier's `/proc` scan is the stronger one.
3. **Commit attribution.** The commit's author/committer is `ci <ci@local>`;
   which seat invoked it is not recorded in the repository.
4. **"pyc already `M` at seat entry"** (author disclosure) is not verifiable
   from artifacts; at audit time the worktree shows exactly two tracked
   modifications — the fixture and `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`
   — matching the author's "only tracked writes" statement.
5. **Not covered here:** the C-side flush timeout behind the `~1 s` deferred
   save (both siblings flag it as unverifiable from the installed Lua); the
   `l18` movement path; `wpctl status` against a half-initialised WirePlumber.
6. This report does not evaluate whether the round's changes are Pareto
   improvements or admissible; that is the canonical runtime's judgment.

## 9. Artifact paths touched by this audit

- **Written (this seat, not committed):**
  `reports/round-97/r97-scribe.md` (this file).
- **Read:** `b8ff4efc` blob + diff; `reports/round-97/{r97-author,r97-integrate,r97-critic,r97-verifier}.md`;
  `audio-shokunin-wt-r97/corpus/live/r97-author/{RECEIPTS.txt,fixture-sha256.txt,battery-r97.sh,battery*.log,receipts/*.json,dev/*}`;
  `audio-shokunin-wt-r97/corpus/live/runs/*-wppol-r97/measurements.json`;
  `audio-shokunin-wt-r97/corpus/live/measure_audio-wppol-r97.lock`;
  raw private roots under `/home/vgpnk/Projects/shokunin/tmp/wppol-r97-*`
  (logs, confs, pid files); `git worktree list`; main `git status`.
- **Not touched:** no tracked file, no run dir, no lock, no worktree, no
  commit/stage/push.

Seat stop. The canonical Rust runtime remains the sole judge.
