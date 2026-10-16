# r96 scribe — custody audit of landing `7358f13b` (pulsecli family)

Seat: **scribe** (non-author, custody only — no judgment; the canonical Rust
runtime is the sole Pareto judge). Basis: `/home/vgpnk/Projects/shokunin/
audio-shokunin` (main, HEAD `a2c6e3b7` at audit time) + the author worktree
`audio-shokunin-wt-r96` (branch `wt-r96` @ `5755be5b`). Method: read-only —
`git show`, `sha256sum`, `sed` spans, receipt JSON re-derivation. **No leg was
re-run for this report** (no decorative re-execution); the only write is this
file. Nothing committed.

Audited surfaces: `7358f13b` (4 files, +3 179/−3), `reports/round-96/
r96-author.md` + `r96-integrate.md` (both in the commit), the worktree receipts
`audio-shokunin-wt-r96/corpus/live/r96-author/**` and the five run receipts
under `audio-shokunin-wt-r96/corpus/live/runs/*pulsecli-r96/`, plus the
verifier's frozen-tree receipts under `/home/vgpnk/r96v/tree/corpus/live/runs/`
(existence/counts spot-checked, not re-run).

## 1. Claims → receipts → committed bytes

| claim (source) | receipt evidence | status |
| --- | --- | --- |
| 5 entries / 178 legs, 41/27/68/20/22 (author §1, §5 census) | runs `…093539…` and `…093802…`: legs per entry exactly 41/27/68/20/22 = 178, in both | **match** |
| two green runs on frozen bytes, `failures: {}` (author §5) | `run{1,2}.stdout.json` = `{"receipt": …, "failures": {}}`; per-entry `failures: []`; **0 of 178 legs** carry a failure in either receipt; stderr logs 0 B | **match** |
| 143 s per run (author §5 table) | `battery.log` 09:33:16→09:35:39 and 09:35:39→09:38:02 = 143 s / 143 s | **match** |
| frozen sha `measure_audio.py` `b545283e…`, `pulse_r96_probe.c` `fe2c1683…` (author §5) | `frozen-shas.txt` + worktree files hash exactly; committed `pulse_r96_probe.c` = `fe2c1683…`; committed `measure_audio.py` = `97ed1b1c…` (**≠**) | **match for the worktree file; see §2** |
| instrument binary `c3fc4cef…` (author §5) | every cork receipt's `client_build`: `source_sha256 fe2c1683…`, `binary_sha256 c3fc4cef…` (worktree runs and verifier runs) | **match** |
| named coverage blocks = 2 per run, only non-green lines (author §5) | `coverage_blocked` length 2 in both green runs, both `e_native_corked`; no other non-green field | **match** |
| `e_cork` 71 677 nonzero frames, both runs | `tap.nonzero_frames` 71 677 in `e_cork__r1/r2`, both runs | **match** |
| `e_trigger` 0 nonzero / peak 0 (3 reps) | `e_trigger__r1..r3` `nonzero_frames 0`, `peak 0`, both runs | **match** |
| prebuf 2 752 vs 57 341 | `e_prebuf_zero_slow__r1..r3` = 2 752 each; `e_prebuf_default_slow__r1..r2` = 57 341 each | **match** |
| `e_record_cork` readable peak 196 608 / drained 262 144 | `readable_peak 196608`, `drained_bytes 262144` (both runs) | **match** |
| `e_latency_query` every call rc −16 | every `latency` event line `rc=-16 … err=No data` (11 lines/rep, both runs) | **match** |
| `e_subscribe` exactly 1 change at the uncork, 2 before, 1 new, 24–40 foreign | `changes_at_uncork 1`, `changes_before_uncork 2`, `new_events 1`; `foreign_sink_input_events` 40/40 (run 1), 24/38 (run 2) | **match** |
| `late_attr_census` 0/66 in both green runs; 25/66 in the dev window (author §2.2/§5) | green runs `{"legs":66,"first_snapshot_missing_attrs":0}`; `dev-attr.json` = 25 | **match** |
| `capture_miss_census` 3/3 refused / 0 hung | `{"measured":3,"refused":3,"hung":0}` in both green runs and the dev-target receipt | **match** |
| `b_host_bogus` live 7.998/8.04 s (author §4.1) | `dev-avail.json` r2/r1 = 7.998 / 8.04; green runs 7.66/8.00 and 7.81/8.00 | **match (dev window)** |
| 24/24 target legs needed 2 polls | 24 legs carry `polls: 2` (both green runs, and dev-target) | **match** |
| row→link gap 0.004–0.086 s (author §2.1) | dev-target `link_t − row_t` range **0.000–0.086**; green runs 0.000–0.001 | **lower bound not reproduced (minor)** |
| "8 rows carried `sink = 4294967295`" in the first dev run (author §2.1) | no retained receipt contains it (`dev-target.json` rows all carry a real sink index, e.g. 282 893) | **attestation-only (superseded run, not retained)** |
| superseded runs: `…092633…` entries 1–3 gated out, props 20/0, cork 22/4; `…092940…` green; `…093204…` cork 1 failure (author §5) | re-derived exactly: 3 `coverage_blocked` "pulse server unresponsive at entry", props 0 failures, cork 4 failures; 092940 `failures {}` + 2 blocks; 093204 1 failure + 1 block | **match** |
| exit census: `sinks_gone` true, `own_nodes_after []`, unloads verified, defaults unchanged, residue 24 `r96a_*` store rows (author §5) | receipts: `sinks_gone {'ns': True}`, `own_nodes_after []`, `unloads.captured == verified_index` rc 0, `foreign_r96a_nodes []`, `inventory`/`oracle_at_start` = USB `HiFi__SPDIF__sink` / `HiFi__Line__source`; live store now holds **43** `r96a` rows (later runs added rows after the 06:38 census) | **match; residue count is point-in-time** |
| "0 seat processes", `clock.*` unchanged (author §5) | **no receipt field exists** for either in the author's receipts (`grep clock.`/`force-quantum` = 0 hits) | **attestation-only for the author seat**; independently re-derived PASS by the verifier seat on the committed tree (`r96-verifier.md` §0) |
| §4.4 "`pulsecli_props_r96_probe` … (12 legs)", §4.5 "`pulsecli_cork_r96_probe` … (24 legs)" | receipts and the report's own §1/§5 census say **20** and **22** | **internal inconsistency — §4.4/§4.5 headers are stale** |
| commit message "+2358/−3" | `measure_audio.py` numstat is 2 358/3; the **full** commit is +3 179/−3 across 4 files (probe +383, author report +362, integrate +76) | house convention (r97 "+2156/−3", r92 "+2328/−3" likewise quote the fixture only) — scope-narrowing, not a defect |
| "Nothing committed." (author, Files changed) | the report itself is committed verbatim (sha `6d7b6880…`) in `7358f13b` | **stale at commit time** (true at authoring, 06:58 vs commit 06:59) |

## 2. Committed diff vs frozen (measured) bytes

- **Frozen/measured file** (worktree, `wt-r96` @ `5755be5b` base + r96 block):
  `b545283e6355d77346e11e0883d9d79792180f0732f2a5851623dbfb353786c8`,
  34 724 lines. **Committed file** (`7358f13b`):
  `97ed1b1c586d2d5446f2ae85d1ab158e43b0f7d71edf430c2c5f045ed5299efc`,
  45 271 lines. Parent `ccbce758` (r92) = 42 916 lines. The difference is base
  composition (main carries the r90–r94 blocks; the WT base predates them), not
  r96 drift.
- **Span identity (verified independently of the integrate report):**
  - family block: merged `41471–43787` = WT `31091–33407`
    = `be60f1bae6db9859839ebe2f3daf6938af3bc03f2d7595bdf5c97ac82968b97d`
    (2 317 lines) — byte-identical.
  - dispatch block: merged `44554–44590` = WT `34007–34043`
    = `75bc7fdd9f6b3d983db6816b6ea8a925c6cdd602e65e1645db0665639c467d65`
    (37 lines) — byte-identical. *The integrate report cites the WT range as
    `34007–34042` (one line short); the sha it prints matches the true 37-line
    span.*
  - wiring: `--probe-pulsecli-r96` inserted at merged line 43 922 after the r92
    row (verified in the diff); the mutex token appended at list end; `mode`/
    `suffix` ternaries carry r96 first — all three replaced lines are the
    commit's **only 3 deletions** (6 hunks total: 2 323 / 1 / 1 / 43 / 1 / 1),
    consistent with "insertion-only … plus the three shared-line splices".
- **Disclosure status:** the hash difference is disclosed in `r96-integrate.md`
  ("merged sha `97ed1b1c…` — **≠** the WT file's `b545283e…` (expected: the
  merged file differs from the worktree file)"), in the same commit. The
  author report does **not** carry that disclosure, and its §5 frozen sha names
  the same relative path (`corpus/fixtures/measure_audio.py`) as the committed
  file — path-ambiguous to a reader of the commit alone.
- **Post-splice execution evidence (other seats, spot-checked):** the verifier's
  frozen-tree gate (`git archive HEAD` @ `7358f13b`) produced two receipts
  (`/home/vgpnk/r96v/tree/corpus/live/runs/20261016T100323631707Z-pulsecli-r96/
  measurements.json`, `…T100600813942Z…`) — I verified 178 legs, 2 blocks,
  `failures {}` and the identical instrument source/binary shas in both; and a
  concurrent main-worktree run `corpus/live/runs/20261016T100425297878Z-
  pulsecli-r96/measurements.json` (178 legs, `failures {}`, 2 blocks). I did
  not re-run anything.

## 3. Foreign-sandbox `pkill` disclosure

Verbatim (author §6, `r96-author.md:312–322`):

> **Discipline breach (disclosed).** While cleaning up the private-sandbox dev
> processes this seat ran a *pattern* kill (`pkill -f "^pipewire -c
> pipewire.conf"`) after checking only ONE matching PID's environment. The
> checked PID turned out to belong to a **foreign** seat's private sandbox
> (`PIPEWIRE_RUNTIME_DIR=…/tmp/r98a-sbx-yg9x_4_3/sbx/q1024/rt`) and the pattern
> kill terminated it. The system daemons (PIDs 2060/2063/2694) and the other
> foreign private instances (r99asmoke) were untouched, and no `r96a` process
> survived; but the r98 lane's private core was killed by a namespace-blind
> sweep — exactly the r95-incident class the corpus forbids.

Evidence status — **attestation-only**:

- No artifact under `corpus/live/r96-author/` records the kill, the environ
  check, or the victim PID (no `pkill`/`r98a-sbx`/`PIPEWIRE_RUNTIME_DIR` hit in
  `battery.log`, `waiter.log`, `frozen-shas.txt`, or the probe receipts). The
  two private-sandbox probe scripts kill by process group only
  (`os.killpg`), not by pattern.
- The named directory `tmp/r98a-sbx-yg9x_4_3` does not exist now and appears in
  no receipt I could search; r98's own receipts show sibling sandboxes of the
  same shape (`tmp/r98a-sbx-45xbmhgk/sbx/q1024/rt`), so the *shape* is
  corroborated, the *instance* is not.
- Temporal context (not a witness): `waiter.log` 09:19:07→09:24:44Z (the
  daemon-wedge wait; private-sandbox receipts mtime 09:19Z); r98's
  `tmp/r98a_battery2.log` starts 09:27:53Z and ends with no result, the next
  r98 battery starts 09:43:10Z. Nothing in the receipts contradicts the
  disclosure; nothing corroborates it either.
- Corpus-level conflict to hand to the judge, verbatim: `r97-boundary.md:403`
  — "No foreign seat uses a broad `pkill` (checked read-only: every sibling
  sweep is seat-path-scoped)" — alongside its own unexplained SIGKILL record
  (`r97-boundary.md:398–405`, a private WirePlumber leg `rc -9` at 14.3 s,
  `timed_out=False`). The r96 author's disclosure is the only broad-pattern
  kill named anywhere in `reports/round-9[567]/` of this repo. (The audio
  `r96-boundary.md:23–25` "no namespace-blind sweep (r95 incident precedent
  honored)" is seat-scoped to the boundary lane and does not reference the
  author's kill.)

## 4. `e_native_corked` named blocks (verified verbatim)

- Both green runs: `coverage_blocked` = exactly the two entries, verbatim:
  "e_native_corked rep 1: the pulse reply reports Corked=True while the live
  node state is 'running'->'running' — the server's cached dev_info state is
  not the live state, so the projection's VALUE is recorded, not armed (the
  no-pulse.corked class claim below still is)" and the rep 2 twin.
- Recorded leg values in the green runs: `has_pulse_corked False`,
  `corked_field True`, `node_state_before/after running/running`,
  `live_state_stable True`, `projection_agrees False`, `exit_code -9` — i.e.
  the block is a recorded value with the armed half (no `pulse.corked` prop)
  still green, as the report's §5/§7 describe. The main-worktree run of 07:04
  has rep 2 `suspended→running`, `live_state_stable False` (block text
  differs accordingly); the superseded 09:29 run's blocks read "the starved
  native stream's node state moved across the pulse snapshot ('suspended' ->…)".
- No other leg/entry in either green receipt is non-green (0 of 178 legs carry
  failures).

## 5. Out of scope / not done

- No re-execution of any leg, probe, or battery; no mutation testing; no
  re-derivation of the critic's C1/C2 counterexamples (`r96-critic.md`) or of
  the verifier's law set.
- No admissibility/Pareto statement — that is the canonical judge's.
- No writes outside this file; no `git add`/commit/push; no edits to fixtures,
  receipts, or other seats' reports; `corpus/live/**` untouched.
- The r97+ bytes on main (the `wppol` block) are outside this audit; only the
  r96 commit's own bytes were examined.

## 6. Findings (for the judge)

1. **Custody break (disclosed, not block-level):** the measured file
   (`b545283e…`) is not the landed file (`97ed1b1c…`); the r96 family and
   dispatch spans are byte-identical (verified), the difference is the
   surrounding base, and the integrate note in the same commit discloses it.
   The author report alone does not.
2. **Stale section headers:** `r96-author.md` §4.4 says 12 props legs, §4.5
   says 24 cork legs; receipts and the report's own census say 20 / 22.
3. **"re-verified after the runs"** (author §5) is not logged: `frozen-shas.txt`
   mtime 06:33:16 precedes run 1 (06:35:39), and `battery.log` prints shas only
   at battery start. Byte-stability across the runs is *inferable* (current
   worktree hash = frozen sha; file mtime predates run 1) but not witnessed.
4. **`pkill` disclosure is attestation-only** (§3): no receipt, no artifact;
   the named foreign sandbox dir is gone; r97-boundary's "no foreign seat uses
   a broad `pkill`" coexists verbatim with it.
5. **"Nothing committed."** in the committed report was true at authoring and
   stale at commit (report committed verbatim, `6d7b6880…`).
6. **Exit-census items without receipt fields** for the author seat: "0 seat
   processes" and the `clock.*` values; only the verifier seat's independent
   gate covers them on the committed tree.
7. **Unretained evidence:** the §2.1 "vacuous green, 8 rows `sink =
   4294967295`" first-dev-run receipt is not in `corpus/live/r96-author/`
   (superseded runs were kept only as the three listed run dirs).
8. **Residue grew:** 24 `r96a_*` store rows disclosed at exit census; the live
   store now shows 43 (later r96 runs — 07:04 main run, verifier runs — added
   rows).
9. **Minor numeric:** the §2.1 gap range lower bound (0.004 s) is not
   reproduced in the retained dev receipt (min 0.000 s; green runs 0.000–0.001).
10. **Commit-message scope:** "+2358/−3" quotes the fixture only (house
    convention); the full commit is +3 179/−3 across 4 files.

## 7. Artifact paths

- Landing: `/home/vgpnk/Projects/shokunin/audio-shokunin` @ `7358f13b`
  (`97ed1b1c…` fixture, `fe2c1683…` probe, `6d7b6880…` author report,
  `reports/round-96/r96-integrate.md`).
- Frozen bytes / receipts (worktree, untracked):
  `audio-shokunin-wt-r96/corpus/fixtures/{measure_audio.py, pulse_r96_probe.c}`,
  `audio-shokunin-wt-r96/corpus/live/r96-author/**`,
  `audio-shokunin-wt-r96/corpus/live/runs/20261016T092633752834Z-pulsecli-r96/`,
  `…T092940854796Z…`, `…T093204463094Z…`, `…T093539457589Z…`, `…T093802929935Z…`.
- Post-commit execution evidence (other seats, spot-checked):
  `corpus/live/runs/20261016T100425297878Z-pulsecli-r96/measurements.json`;
  `/home/vgpnk/r96v/tree/corpus/live/runs/20261016T100323631707Z-pulsecli-r96/`
  and `…T100600813942Z…`; `corpus/live/r96-verifier/{runs,receipts}/`.
- This report: `reports/round-96/r96-scribe.md` (untracked, not committed).
