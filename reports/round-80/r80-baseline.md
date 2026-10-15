# R80 baseline — clean post-r79 freeze at `ee6d684` + battery ×2 (per-case field stability, pid-normalized)

host: `plazir27` (`Linux 7.2.3-arch1-3`), seat: BASELINE. Lane
`~/Projects/shokunin/audio-shokunin`. Freeze target: the **r79 commit**,
which landed at **08:47Z** as two commits — `d170df9` ("r79: pw-loopback
-C/-P binding frontier — 66 legs, ADMIT-corr", the work commit: fixture
+2763/−3 and nine r79 reports) and `ee6d684` ("r79 LOG: ADMIT-corr",
HEAD). Everything below is attributable to HEAD
`ee6d6847cf27f9fd2c9dd784ada25468ef0a1426` and fixture sha256
`ec33beb108ef2026d8a269c7d784106bc7f9cbbe97a6f4bd0aa310aa4bb2d50e`
(674,556 B, git blob `f71fc82e8d933c20b0f78b9de1f94cfd205487e0`).
**No tracked edits by this seat; nothing committed.**

The battery is the file's default `normal` mode plus the r78 and r79 probe
entries, executed **twice** (`runs-a`, `runs-b`). Receipts, tooling and
comparison outputs live in `corpus/live/r80-baseline/`.

---

## 0. Headline

| # | question | answer |
| --- | --- | --- |
| 1 | Did the freeze hold? | **Yes.** 124-sample watcher (`head-watch.log`, 08:47:18 → 09:07:51Z, every 10 s) shows **one** distinct `(HEAD, fixture sha)` pair across all six probe runs; the fixture sha is re-recorded before **and** after every run (`runs-*/commands.log`). |
| 2 | Is the post-commit tree green? | **Yes, 6/6 runs.** `normal`, `capture-r78`, `capture-r79` × 2 runs: exit 0, `failures {}`, stderr 0 B. The r79 family measures **67 legs** (66 pre-fold + the fold's new `b13_nullsource_law`), 8/8 entries, `own_nodes_after: []`, every probe sink `sinks_gone: True`, 15 named outcomes. |
| 3 | Per-case stability vs the r79-author receipts (B/C)? | **Base fixture: 100 % exact.** All 17 base cases (`ui*`, `impact*`, `movement*`, `ambience*`, `stem*`, `thresholds`, `distinctness`, `sections`, `*_family_comparisons`) are **byte-identical** across B, C, runs-a, runs-b — 0 differences of any class across their 373 leaves. The r79 entries carry 564 **added** paths (the fold's own new leg/outcomes), **0 removed**, and only **5** flagged paths, all explained in §4. |
| 4 | Battery noise floor (runs-a vs runs-b, same bytes)? | **0 semantic paths** in the r79 family; 2 110 numeric-jitter and 2 145 volatile leaves out of 23 619. The r78 family: 7 semantic leaves, all `tap/windows[N]/audio|mine` content flags at the leading window. The verdict surface (legs/classes/outcomes/failures) is **identical** run-to-run in both families. |
| 5 | Prior rows untouched? | **Yes.** `normal` is **byte-identical** to the tracked canonical receipt (`8e8cdad6…`) in both runs; the r78 family shows only its known flap/environmental classes (§6). |
| 6 | What does the fold change? | +1 capture leg (`b13_nullsource_law`, fold C7), +6 `content_pin_unmeasured` named outcomes (fold A2) and their reordering — a purely **additive** verdict-surface delta (§5). |

---

## 1. Frozen state and archive

- **Poll → commit.** Entry at 08:42:36Z: HEAD `a2616f7` (r78), fixture
  dirty (`ec33beb1…`, mtime 08:40:24Z — the fold's last write). The
  poll (`/tmp/r80-baseline-work/poll.log`) sampled every 60 s; the r79
  commit appeared at **08:47:38Z** (attempt 6), and the fixture became
  clean in the same sample.
- **The committed blob is byte-identical to the fold's working revision:**
  the dirty file at entry already had sha256 `ec33beb1…` / git blob
  `f71fc82e…`, and `git rev-parse HEAD:corpus/fixtures/measure_audio.py`
  is the same `f71fc82e…`. So the r79-verify V1/V2/R78 receipts and the
  fold-verify run D were produced from bytes that either precede
  (`4ee754b3…`) or exactly equal the commit (`ec33beb1…`) — §5 uses that.
- **Diff surface vs the r78 HEAD:** `+2763/−3` on
  `corpus/fixtures/measure_audio.py` (the three rewrites are the
  prepend-only wiring lines every round uses); 9 reports added.
- **Archive** (`tree-archive.txt`, `archive-tree.sh`): `git archive HEAD`
  materialized into `corpus/live/r80-baseline/tree/` (gitignored by
  `corpus/.gitignore: live/*/*tree*`).
  tar sha256 `5dec4366b1ed4519c993f327e1f9fc320edef39afb6032254b9e8026713ff96d`,
  459,171,840 B, 30,726 members; extracted **23,774 files + 6,953 dirs**;
  file-set symmetric difference against `git ls-tree -r HEAD` = **0**;
  the fixture inside the tree is byte-equal to the worktree
  (`ec33beb1…` both sides).
- **Pre-existing tracked dirt:** ` M SHONEN.md` only (present before this
  seat's first command; not the r79 fold's, not mine). The fixture and its
  tracked `.pyc` are clean.

## 2. The battery — commands, windows, receipts

| run | mode | window (UTC) | dur | rc | failures | receipt (canonical → copy) | sha256 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | `normal` | 08:47:28 → 08:47:29 | 1 s | 0 | `{}` | `runs/20261015T084729176329Z-normal` → `runs-a/normal.receipt.json` | `8e8cdad6cc3c356d…` |
| A | `--probe-capture-r78` | 08:47:29 → 08:51:01 | 3 m 32 s | 0 | `{}` | `runs/20261015T085101000260Z-capture-r78` → `runs-a/capture-r78.receipt.json` | `f0e3d50586be29d1…` |
| A | `--probe-capture-r79` | 08:51:01 → 08:56:38 | 5 m 37 s | 0 | `{}` | `runs/20261015T085638725489Z-capture-r79` → `runs-a/capture-r79.receipt.json` | `63110300dad351f1…` |
| B | `normal` | 08:56:38 → 08:56:39 | 1 s | 0 | `{}` | `runs/20261015T085639809777Z-normal` → `runs-b/normal.receipt.json` | `8e8cdad6cc3c356d…` |
| B | `--probe-capture-r78` | 08:56:39 → 09:00:11 | 3 m 32 s | 0 | `{}` | `runs/20261015T090011572551Z-capture-r78` → `runs-b/capture-r78.receipt.json` | `8e25e8722d4c10d4…` |
| B | `--probe-capture-r79` | 09:00:11 → 09:05:49 | 5 m 38 s | 0 | `{}` | `runs/20261015T090549097852Z-capture-r79` → `runs-b/capture-r79.receipt.json` | `9f15d1dde641d12f…` |

All six receipts were written to the canonical `corpus/live/runs/` by the
fixture itself and copied beside the logs by `collect-receipts.py`
(`receipt-shas.txt` records both). Driver: `battery.sh`; every run is
bracketed by a fixture-sha256 check (`SHA before=… after=… rc=…`).

**Battery scope, stated plainly.** This battery is `normal` + the two
newest probe entries, per the r78/r79 receipt conventions — it is *not*
the 127-command historical replay the r78 baseline built (`rerun.py` +
`measure-env/`). Rows for r70–r77 families are covered by that harness and
by the r79-verify V1/V2/R78 receipts, not re-run here.

## 3. Per-case field stability vs the r79-author receipts (primary)

Comparator: `percase.py`, four receipts — `B`, `C`
(`corpus/live/r79-author/receipt-run{B,C}-…-capture-r79.json`, pre-fold
bytes `4ee754b3…`) as the reference group, `runs-a`/`runs-b` (post-commit
bytes `ec33beb1…`) as the fresh group. Output:
`stability-r79-vs-author-BC.txt` (23 619 leaf paths, 0 normalized-key
collisions).

**Normalization (pid-normalized, applied to every key and string leaf):**
digit runs ≥ 5 → `<N>` (covers `r79lb_…_<pid>`, `r79fc_<pid>`,
`r79lb_<pid>_…`, `loopback-<pid>-<n>`, `pw-loopback-<pid>`); any
`/tmp/<scratch-dir>/…` path → `/tmp/<scratch>/…`; wall-clock
`[hh:mm:ss.µs]` → `<t>`; `0x…` pointers →
`<ptr>`. Leaves whose key is `own_pid`/`client_id` are classed volatile
regardless of value. Numeric leaves are **not** normalized — they are
reported as jitter with their spread, so a real value change cannot hide
inside a digit-run rewrite.

| case | exact | volat | jit | sem | added | removed | total |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ui / ui_alt / ui_third | 13 / 13 / 13 | 0 | 0 | 0 | 0 | 0 | 13 each |
| impact / impact_alt / impact_third | 13 / 13 / 13 | 0 | 0 | 0 | 0 | 0 | 13 each |
| movement / movement_alt / movement_third | 13 / 13 / 13 | 0 | 0 | 0 | 0 | 0 | 13 each |
| ambience / ambience_alt / ambience_third | 13 / 13 / 13 | 0 | 0 | 0 | 0 | 0 | 13 each |
| stem / stem_sections / stem_layer(_alt/_third) | 13 each | 0 | 0 | 0 | 0 | 0 | 13 each |
| TOP thresholds / distinctness / sections / family_comparisons | 47 / 20 / 44 / 40 | 0 | 0 | 0 | 0 | 0 | 151 |
| `loopback_shape_r79_probe` | 1 586 | 193 | 171 | 0 | 1 | 0 | 1 951 |
| `loopback_capture_lattice_r79_probe` | 6 046 | 560 | 343 | 4 | 563 | 0 | 7 516 |
| `loopback_playback_lattice_r79_probe` | 5 195 | 519 | 662 | 0 | 0 | 0 | 6 376 |
| `loopback_matrix_r79_probe` | 1 334 | 153 | 666 | 0 | 0 | 0 | 2 153 |
| `loopback_record_target_r79_probe` | 635 | 138 | 188 | 0 | 0 | 0 | 961 |
| `loopback_hotplug_r79_probe` | 2 425 | 358 | 300 | 0 | 0 | 0 | 3 083 |
| `pwcat_latency_r79_probe` | 709 | 142 | 11 | 0 | 0 | 0 | 862 |
| `filterchain_module_r79_probe` | 240 | 46 | 57 | 1 | 0 | 0 | 344 |
| **TOTAL** | **18 543** | **2 109** | **2 398** | **5** | **564** | **0** | **23 619** |

Reading:

- **Every base-fixture case is exactly stable** (0 volatile, 0 jitter,
  0 semantic) — the 17 base cases carry no per-run variation at all
  between the pre-fold reference and the post-commit battery.
- **564 added / 0 removed** — the fold's delta is additive only (§5).
- **5 semantic paths**, each explained and each internally consistent in
  *both* pairs (reference pair stable, fresh pair stable, pairs differ):

  | path | B / C (pre-fold) | runs-a / runs-b |
  | --- | --- | --- |
  | `filterchain…legs.f1_good.tap.windows[0].audio` | `True` / `True` | `False` / `False` |
  | `capture_lattice…named_outcomes[1..4]` | the pre-fold 5-outcome list | the fold's 12-outcome list (insertion shifts indices) |

  The first is the **leading-window content flag** — the same marginal
  class that flips 1-in-4 runs elsewhere (§5: run D says `True` on the
  committed bytes). The four `named_outcomes[i]` rows are an **ordering
  artifact** of comparing an ordered list index-by-index after the fold
  inserted six entries; §5 compares those collections as sets/multisets
  and shows the delta is exactly the fold's additions.
- **Volatile (2 109)** — pid-stamped names, `/tmp` scratch dirs, `client_id`
  and `own_pid`. **Jitter (2 398)** — measured quantities; see §7 for the
  taxonomy.

Wider reference set (`stability-r79-6way.txt`, refs B/C + verifier V1/V2,
4+2 split): 18 483 exact / 2 109 volatile / 2 456 jitter / **7** semantic /
564 added. The two extra semantic paths are `filterchain…f9_bad_label.reply[2]`
and `…f10_bad_args.reply[2]`: the trailing `pipewire-0>> ` prompt line is
present in B, C, D, runs-a and runs-b but **absent in V1/V2** — a run-local
pw-cli teardown capture artifact (the reply vector is 2 lines vs 3), not a
code delta.

## 4. Noise floor — runs-a vs runs-b (same bytes, same session)

`stability-r79-runsAB.txt`: **0 semantic paths**; 19 364 exact / 2 145
volatile / 2 110 jitter. The verdict surface is identical for all eight r79
entries and all eight r78 entries (`fold-delta.py`: "verdict surface
IDENTICAL" for every case, legs included). This is the floor the r80
comparisons should be judged against: **on identical bytes this battery
reproduces every structural and verdict leaf.**

The r78 battery pair (`stability-r78-runsAB.txt`) is equally tight: 7
semantic leaves out of 12 400, all of them `playback_target_lattice…
tap/windows[4|30]/audio|mine` — content flags at the leading/trailing
window.

## 5. What the fold changed (verdict surface)

`fold-delta-prefold-vs-commit.txt` compares the verdict-bearing
*collections* (legs, `classes_extra`, `named_outcomes`, failures) — sets,
not index-wise lists — for refs B/C/V1/V2 vs runs-a/runs-b:

- `loopback_capture_lattice_r79_probe`: legs **12 → 13**, `+ b13_nullsource_law`;
  named outcomes **5 → 12** (five `content_pin_unmeasured` on b02/b03/b05/b06/b07,
  one on b13, and b13's `unnegotiated branch measured — no default source at
  this leg`). All six probe-owned sinks `sinks_gone: True`.
- `loopback_shape_r79_probe`: `+ shape a5: content_pin_unmeasured`.
- **Every other entry: verdict surface IDENTICAL** (legs, classes, outcomes,
  failures).

This is exactly the fold report's own delta (`reports/round-79/r79-fold.md`:
critic C7's `b13_nullsource_law` positive leg, verifier A2's
`content_pin_unmeasured` named outcome), measured independently here from
receipts. In runs-a/runs-b the b13 leg resolves the **unnegotiated branch**
with the authority split live (`oracle_at_start.source_meta: null` while
`source_pactl: alsa_input…Line__source`), `expected_kind: "unneg"`,
`exit_code: -9` at the leg bound, `consumers_union: [r79lb_ns_b_<pid>]`.

**Same-bytes control** (`stability-r79-vs-runD.txt`): the fold-verify run D
(`corpus/live/runs/20261015T084630169601Z-capture-r79`, receipt `a3e97211…`)
ran the *identical* committed blob. Against runs-a/runs-b: **0 added,
0 removed, 2 semantic** — `filterchain…f1_good.tap.windows[0].audio`
(D `True`, battery `False`) and `loopback_record_target…d17_manual_pin.
content.windows[0].mine` (D `False`, battery `True`). Both are
window-content flags on the first window; both are the marginal class named
in §4. So even the fold's own verification run differs from the battery
only in that class.

## 6. Prior rows — r78 family and `normal`

**`normal` (tracked canonical comparison).** `stability-normal.txt`:
**373/373 exact, 0 volatile, 0 jitter, 0 semantic** — runs-a, runs-b and the
tracked receipt `corpus/live/runs/20261014T142151899785Z-normal` are all
sha256 `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b`.
The base fixture battery is byte-reproducible across the r79 commit
(three byte-equal receipts from three sessions/trees).

**r78 family, post-commit.** Both runs are **green** — `failures {}`, exit
0, 25 cases, 17/17 fixture probes clean.

- vs the **pre-r79 anchor** (`r79-baseline/anchor-…json`, clean `a2616f7`
  bytes, 06:05Z; `stability-r78-vs-anchor.txt`): 8 500 exact / 218 volatile
  / 3 386 jitter / **252 semantic** / 44 added / 14 removed. The semantic
  set is confined to the r78 family's **named flap classes**:
  `playback_target_loss` (18 `audio`, 4 `mine` window flags),
  `playback_target_lattice` (15 `mine`, 6 `audio`, 2 `carries_tone`),
  `playback_default_follow` (10 `mine`, 3 `audio`, `bound_to_target`,
  `consumer_ports`, `nodes`, `producers` — the tap-binding flap the r79
  baseline named), and 1 `playback_aplay_axis.params_cap.stderr` (the
  anchor's `hw:0,0` `Device or resource busy` vs the parsed envelope —
  the environment-conditional leaf set the r79 verifier documented).
  The added/removed paths are the same story: the anchor's failing
  `default_follow` leg carries `failures`/`confound_observed`/
  `pactl_unmeasured` keys that the green leg replaces with
  `metadata`/`pactl`/`at_s` correlates, plus the `params_cap` envelope
  leaves. **No new or renamed key, no threshold change, no new failure
  class.**
- vs the **pre-fold r79 tree** (r79-verify R78, 08:14Z;
  `stability-r78-vs-prefold.txt`): 8 797 exact / 224 volatile / 3 207 jitter
  / **138 semantic** / 34 added / 6 removed — same classes; the removed set
  is R78's `coverage_blocked`/`confound_observed` keys on the
  `default_follow` arm (R78 was coverage-blocked there, my runs are not).
- Coverage blocks are **stable**, not drift: both capture arms
  (`capture_unlinked_zeros_r78_probe`, `capture_parec_fix_r78_probe`) are
  `coverage_blocked` with the identical string in the anchor, in R78 and in
  both battery runs ("… monitor source never enumerated", waited ≈ 4.01 s),
  and neither is a failure. `playback_default_follow` is the only arm whose
  verdict moved: anchor **failed** (+ `coverage_blocked`), R78
  coverage-blocked only, battery **clean** — the documented
  multi-seat/metadata flap, not a code delta.

## 7. Noise-class taxonomy (what this baseline pins)

From the primary 4-receipt comparison, jitter by leaf key (n, max rel.
spread across B/C/runs-a/runs-b):

| class | leaves | spread | note |
| --- | --- | --- | --- |
| `a_l` / `a_r` (window amplitude) | 577 / 553 | ≤ 0.97 / ≤ 0.07, median 0.057 | the tag-tone amplitude estimator; the *leading* window (`a_l` max 0.97) is the marginal one |
| `f_l` / `f_r` (window frequency) | 577 / 553 | median 0.387 / 0.296 | **bimodal** estimator (e.g. 1420 vs 1000 Hz on the same physical tone) — present in the author's own B/C pair, so not a battery artifact |
| `peak_l` / `peak_r` (tap peak) | 18 / 17 | ≤ 0.057 | consistent with the per-run pid-derived tag frequency (997 + pid%4·211 Hz) documented by the r79 verifier |
| `waited_s` / `monitor_waited_s` | 58 / 4 | ≤ 0.95 / 0.20 | node/monitor readiness polls; median ≈ 0.9 % |
| `zero_windows` | 1 | 0→1 | `filterchain f1_good` only |
| `audio_windows`, `wall_s`, `at_s`, `when_s`, `at_l/at_r`, `peak` | ≤ 8 each | ≤ 0.05 | pacing/window bookkeeping |
| `module_id` | 19 | absolute only | session allocation counter: `536870919/21/23` pre-fold vs `536870930/31/36` post-commit (stable *within* each pair) |

Volatile classes (normalized away, listed for the record): pid-stamped
probe/node names (≈ 2 000 leaves), `/tmp/<scratch>` module-config dirs,
`client_id`/`own_pid`, `node_link_group`/`pw-loopback-<pid>` counters.

**Semantic classes observed anywhere in this baseline** (all named, none
unexplained): leading/late-window content flags (`audio`, `mine`,
`zero_windows`), `filterchain` pw-cli trailing-prompt line count (2 vs 3),
`named_outcomes` index shifts under additive insertion, and the r78
family's default-follow/target-lattice tap-binding flap. Nothing else.

## 8. Contention ledger

- **Foreign state at battery start** (`env.txt`): default sink
  `…HiFi__SPDIF__sink`, default source `…HiFi__Line__source`; two foreign
  null sinks from a sibling lane — `r79lb_ns_a_4041488` /
  `r79lb_ns_b_4041488` (+ their `.monitor` sources), SUSPENDED — still
  present at exit (`post-state.txt`). Session `default.audio.source`
  metadata is **absent** (`source_meta: null`) while `pactl` enumerates the
  Line source; this is the authority split the r79 arm's fallback class
  measures, and it is reproduced in every battery run.
- **Contention census in the receipts**: every r79 entry reports
  `aplay: 1` and `host_is_quiet: false` — the ~10 h stale `aplay -D null`
  process another seat leaked (already named by the r78/r79 baselines).
  No other probe process was live inside the battery window.
- The battery itself adds **no** foreign sink to the shared default: the
  r79 arm's own legs route tones to probe-owned sinks (the arm's guard),
  and the two r78 capture arms are coverage-blocked rather than fed. One
  leg (`pwcat d12`) targets the shared default sink with digital silence by
  design.
- Canonical `corpus/live/runs/` grew 5 688 → 5 694 during the battery —
  exactly this battery's six receipts.

## 9. Write-scope accounting

Wrote only: this report; `corpus/live/r80-baseline/` — `tree/`
(gitignored archive materialization) + `tree-archive.txt`, `env.txt`,
`pre-state.txt`, `post-state.txt`, `head-watch.log`, `runs-a/` and
`runs-b/` (6 receipts + stdout/stderr/commands.log/receipt-shas.txt),
`receipt-shas.txt`, the tooling (`percase.py`, `fold-delta.py`,
`verdicts.py`, `battery.sh`, `archive-tree.sh`, `collect-receipts.py`,
`compare-all.sh`, `env.sh`, `watch.sh`, `BC-percase-check.txt`) and the
comparison outputs (`stability-*.txt`, `fold-delta-prefold-vs-commit.txt`);
plus the six canonical receipts the fixture itself wrote under
`corpus/live/runs/`. **Zero tracked-file edits, zero commits, zero pushes,
no `git checkout`.** The seat's own scratch is 47 files / 3.2 MB (largest
1.0 MB), with **0 `.wav`** — the 3 758 `.wav` files under the seat
directory are all the tracked fixtures inside `tree/` (the 476 MB archive
materialization). The archive tar (438 MiB) is kept outside the repo in
`/tmp/r80-baseline-work/` as a receipt only.

**Disclosed tooling faults (both fixed, both recorded):** (1) `battery.sh`'s
inline receipt copy appended `EXIT=` before parsing stdout, so the inline
copies were skipped — `collect-receipts.py` is the authoritative mapping
from canonical receipt to `runs-*/`; (2) that collector's first version
compared ISO command timestamps against receipt-dir stamps and selected
stale (Oct-12/14) receipts — corrected by normalizing the timestamp, the
wrong copies deleted, and the re-run's `receipt-shas.txt` cross-checked
against `commands.log` windows. No receipt in `runs-*/` predates
08:47:29Z.

## 10. Remaining unknowns

1. **`f_l`/`f_r` bimodality** (1420 vs 1000 Hz on one physical tone) is
   measured but not explained; it exists in the author's own B/C pair, so
   it is a property of the window classifier, not of any run.
2. **Which lane owns `r79lb_ns_a/b_4041488`** — attribution is by name
   prefix only; the nodes survived the whole window.
3. **`module_id` bases** (`536870919/21/23` vs `536870930/31/36`) track the
   server's allocation counter across sessions; the absolute base is not
   reproducible run-to-run, only within a session.
4. **The `b13_nullsource_law` linked branch** (a live source answering) was
   not measured in any battery run — the host's session default source is
   absent, so only the `unnegotiated` branch is observable here.
5. The battery covers `normal` + r78/r79 entries only; the r70–r77 families
   were not re-run in this window (they are anchored by the r78 baseline's
   127-command harness and by the r79-verify receipts).

---

*Seat output only. Read-only on tracked files, no commits, no judgment
passed on any other lane's work; the canonical Rust runtime remains the
sole judge.*
