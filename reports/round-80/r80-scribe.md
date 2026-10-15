# R80 SCRIBE — audit of the r80 landing (`reports/round-80/r80-author.md` vs receipts)

Seat: **SCRIBE** (audio-shokunin round 80). Lane `~/Projects/shokunin/audio-shokunin`.
Read-only on tracked files and other seats' dirs: this seat wrote **only** this
report and `corpus/live/r80-scribe/` (`claim-crosswalk.tsv`, `runs-inventory.txt`,
`leafdiff-run1-run2.txt`). **No commit, no push.** HEAD audited:
`ee6d6847cf27f9fd2c9dd784ada25468ef0a1426` (`r79 LOG: ADMIT-corr`) — unchanged
at seat start and seat end (reflog top identical; the audit added no commit).

Scope: every load-bearing claim of `r80-author.md` against the five canonical
receipts `corpus/live/runs/*module-r80*/measurements.json`, the copies in
`corpus/live/r80-author/`, the r80 scout's receipts (`corpus/live/r80-scout/`),
the fixture source, and the live filesystem (read-only). 35 claims crosswalked;
the full table is `corpus/live/r80-scribe/claim-crosswalk.tsv`.

---

## 0. Seat-window state (audited, not assumed)

| item | observed | evidence |
| --- | --- | --- |
| HEAD | `ee6d6847cf27f9fd2c9dd784ada25468ef0a1426` | `git log -1`, `git reflog -3` |
| tracked dirt | ` M SHONEN.md` (foreign, pre-existing per r80-baseline), ` M corpus/fixtures/measure_audio.py` (+905/−3, sha256 `3b69541f…`), ` M …/__pycache__/measure_audio.cpython-314.pyc` (**stat-dirty only** — worktree sha256 `6e271a2d…` == HEAD blob; `git diff` empty; mtime 12:32:41 local from post-report re-runs) | `git status --short`, `sha256sum`, `git show HEAD:…\|sha256sum` |
| `-module-r80` runs dirs | **five**: `T134206631212Z` (disclosed failure, pid 712083), `T134301846760Z` (pid 726605), `T134359918834Z` (pid 736128), `T152510343508Z` (pid 930381), `T153530291390Z` (pid 986178 — appeared *during* this audit) | `ls -d`, per-receipt `contention.own_pid` |
| `r80-author/` | **three** receipt copies + `receipt-shas.txt`; the third (`T152510343508Z`, mtime 12:32:02, sha `66d0532a…` == canonical) is **not in the manifest** | `sha256sum`, `stat` |
| author report mtime | 10:46:00 local (13:46Z) — predates both post-report runs (15:25Z, 15:35Z) | `stat` |

**Post-report activity (not the author's):** two further `--probe-module-r80`
executions (15:25:10Z, 15:35:30Z) wrote canonical receipts — both green
(`failures: []` both entries, `own_nodes_after: []`, `sinks_gone` all true,
no `blocked`/`coverage_blocked`) — and a copy of the first was dropped into
`r80-author/` at 12:32. Whichever lane ran them, their verdicts **agree** with
the author's two formal runs (see F3).

## 1. Verified-sound inventory (what checked out)

Receipt integrity and structure:

* Both formal receipts exist, are **byte-equal** to their canonical
  `measurements.json` (sha `8a3a37a4…` / `ba565dc7…`), and match
  `receipt-shas.txt` exactly — including the fixture sha line (`3b69541f…`).
* Each receipt carries exactly the two `*_r80_probe` entries, 5 legs each (10
  legs total), `failures: []` per entry, `own_nodes_after: []`, all
  `sinks_gone: true`, `oracle_at_start` and the `aplay: 1 /
  host_is_quiet: false / source_meta: null` contention+oracle shape the report
  describes. No `blocked`/`coverage_blocked` key anywhere.
* The disclosed failing run's receipt (`T134206631212Z`) records exactly what
  §3 says: a2 sent `r80md desc 712083 marker`, measured `node.description ==
  "r80md"`, single failure `"args a2: sink_properties description did NOT land
  — got 'r80md'"`; the topology entry in the same run is clean.
* Fixture diff is exactly as reported: `+905/−3` on one file, the three removed
  lines are the exclusivity `sum([…])`, the `mode` ternary and the `suffix`
  ternary (the prepend-only wiring); the new block is an append at line 11555.
* HEAD/toolchain claims all verify live (pactl 17.0-98-gb096 / libpulse 17.0.0,
  libpipewire 1.6.8, libwireplumber 0.5.17, Python 3.14.7, kernel
  7.2.3-arch1-3).

Leg-by-leg (all ten legs checked against both formal receipts — C07–C16):

* **a1** derived description + `pulse.module.id == module_id` — receipted.
* **a2** prop wins (`r80md_desc_<pid>_marker` as `node.description`) — receipted.
* **a3** `enum_rates: [99999]` verbatim — receipted.
* **a4** `Audio/Source`, 0/1 ports, `pactl_sink_listed false /
  pactl_source_listed true / pactl_monitor_listed false`, out port
  `<n>:capture_FR` — receipted (the port name is an author-side detail; the
  scout recorded 0/1 but not the name — consistent, not contradictory).
* **a5** linger orphan lifecycle (client.id absent → survives unload with stale
  pmid → still pactl sink+monitor → re-unload rc=1 `pa_no_such_entity` →
  `pw-cli destroy` removes) — receipted field-for-field in both runs.
* **t1** both `@DEFAULT_SINK@` spellings rc=1 `pa_io_error`, `node_created:
  false`, `branch_nodes: []`, module count unmoved — receipted (but see F1 for
  the printed number).
* **t2** linger link up immediately and at +2.0 s, `pw-link -d` rc=0 — receipted.
* **t3** `-m` link live while running, gone at the +1.0 s sample after SIGKILL
  (`m_exit_code: -9`, `linked_after_death: false`) — receipted; the 1.0 s bound
  is the code constant `MODULE_R80_MLINK_DEAD_S`, stated honestly.
* **t4** move sticky: edges `→mv_a` before, `→mv_b` at +1.2 s and +4.6 s; tap
  `ran`, `carries_tone: true`, `mine_windows` 45 — receipted.
* **t5** dont-move no-op: `node_dont_move_prop: true`, move rc=0, edges stay
  `→dm_a` at both samples, dm_a tap `mine_windows` 47 — receipted.

Author↔scout cross-check: **no contradiction found.** Every armed item is
corroborated by the scout's own receipts — p1 `desc` leg (plain `description=`
dropped even with spaces), p2 `null-props` (`r80desc` space-free, prop wins),
p2 combine legs 12–14 (`@DEFAULT_SINK@` → rc=1 `Input/Output error`, zero
nodes), p1/p3 linger orphan, p7 link authority (linger +2 s, `-m` dies, move
sticky, dont-move no-op). The author's §3 correction claims (whitespace-split
modargs, scout's space-free `r80desc`, scout's `--volume 0.05` concession) all
trace to scout artifacts.

Vacuity check: **no leg passes by structure.** Each leg's pass is gated on
measured fields — rc+error class, node/port enumeration, edge-list membership
at named sample times, `pulse.module.id` equality, `pactl` listing booleans,
tap `ran`+`carries_tone` (with the explicit "no windows → the content pin is
vacuous" failure branch, `measure_audio.py:12398-12405`).

Stability math (independently recounted, `leafdiff-run1-run2.txt`): raw
key symmetric difference between the two formal receipts is **exactly
23 added / 23 removed** — all `r80md_<pid>_*` keys under `sinks_gone` +
`sink_loads`, as reported. Shared-path normalized diffs: 431 under a
baseline-style normalizer (all leaves in named volatile/jitter classes;
zero structural or verdict-surface diffs) — see F5.

## 2. Findings

Severity: **HIGH** = would change a verdict or a law; **MEDIUM** = a claim is
not backed as stated; **LOW** = provenance/precision; **INFO** = record only.
Blocking = blocks accepting the report's claims as written.

### F1 — MEDIUM — the t1 row's "count 23→23" contradicts every receipt — BLOCKING for that cell's literal value (not for the law)

The §2 table's t1 row prints `count 23→23` in a column labeled "measured".
The leg's own receipt fields record `module_count_before/after =
49→49` in all three author-window runs (13:42Z, 13:43:01Z, 13:43:59Z) and
`47→47` / `48→48` in the two post-report runs. **No module-r80 receipt carries
the value 23** (grep across all five receipts + both r80-author copies;
`corpus/live/r80-scribe/runs-inventory.txt`). The scout's baseline module list
(`r80-scout/runs/00-baseline/pactl-modules.txt`) has 42 lines — also not 23.

What stands: the asserted *law* (count unmoved across two refused loads) is
receipted — the fixture asserts `after != before → failure`, and every receipt
shows equality. What fails is the printed absolute number, which appears to be
transcribed from nothing recorded. Note this field is host-global volatile
state (`pactl list modules short` line count, `measure_audio.py:12151-12174`);
quoting any absolute value as "measured" without the matching receipt is the
volatile-as-stable pattern — the receipt says 49.

### F2 — LOW — the "measured (run 2 verbatim)" column quotes the *first* formal run, not the second — ambiguous label, not fabrication

Every volatile value in the §2 table's measured column — stale pmid
`536870942`, `pw-cli destroy 151`, tap peak `8137`, marker
`r80md_desc_726605_marker` — verbatim-matches receipt `…T134301846760Z`
(own_pid 726605, 13:43:01Z), the **first** of the two formal green runs.
Receipt `…T134359918834Z` (13:43:59Z, pid 736128) carries pmid `536870931`,
destroyed_id `227`, peak `8189`, marker `…_736128_…`. §1 numbers the two formal
runs `(13:43:01Z, 13:43:59Z)`, under which "run 2" is the 13:43:59Z receipt and
the column is mislabeled; the column is only consistent if the disclosed
failing run (`T134206631212Z`, called "this seat's first formal run" in §3) is
counted as run 1. All quoted values are real receipt values — the citation is
ambiguous-to-wrong, the data is sound. (§5's own arrow direction
`536870942→536870931`, `8137→8189`, `1210→1000` confirms
T134301846760Z = "from" run.)

### F3 — LOW — receipt inventory is stale relative to the corpus (post-report activity) — NOT blocking

The report's write-scope list inventories three canonical `-module-r80`
receipts and two `r80-author/` copies — accurate at write time (report mtime
13:46Z). The corpus now holds **five** canonical runs (plus `T152510343508Z`
15:25:10Z and `T153530291390Z` 15:35:30Z — the latter appeared during this
audit, both green on the same fixture bytes) and `r80-author/` holds a third
copy (`receipt-…T152510343508Z.json`, added 12:32 local, sha `66d0532a…`,
byte-equal to its canonical source) that `receipt-shas.txt` does not list. The
manifest covers only what it claims to cover; the directory it describes has
since grown — and the `.pyc` the report says was restored to HEAD is
byte-identical to HEAD still (recompiled by the post-report runs, content
unchanged). Recorded for provenance: the extra runs corroborate rather than
contradict the report.

### F4 — LOW — asserted-but-unarchived claims — NOT blocking (conventional gaps)

No artifact backs: "exit 0, empty stderr" (runs dirs hold only
`measurements.json`, per the standing convention — no stdout/stderr capture was
archived for this arm); "byte-identical frozen code" between the two runs (the
receipt schema records no per-run fixture sha; support is the single sha line in
`receipt-shas.txt` plus the 58 s gap); the "six direct `pactl`/`pw-link`/
`pw-cli` sanity probes" and their "post-probe census shows zero `r80md`" (no
logs under `r80-author/`); `py_compile` clean; "~55 s" replay. None of these is
contradicted by anything; the teardown witnesses (`own_nodes_after: []`,
`sinks_gone` all true) independently cover the census claim's substance.

### F5 — LOW — "420 normalized leaf diffs" recounts to 431 under a minimal normalizer — NOT blocking

Independent normalized leaf-diff (run1 vs run2, baseline-style normalization —
`leafdiff-run1-run2.txt`): **431** shared-path diffs, **0** added/removed
(normalized), all in named volatile classes (`f_l/f_r/a_l/a_r` 378 — the
pid-derived tag-frequency shift, `module_id` 11, `object_id`/`object_serial`
14, `pulse_module_id` 6, `client_id` 5, `sink_waited_s` 5, `own_pid` 2,
`index`/`sink` 4, `peak_*` 2, `node_waited_s`/`edge_a_waited_s`/`destroyed_id`
3). 431 − 11 = 420 exactly if `own_pid`, `client_id`, and `sink_input`
`index`/`sink` are excluded as volatile-by-construction (the r80-baseline
taxonomy classes `own_pid`/`client_id` as volatile regardless). The number is
defensible; no diff artifact was archived to pin the counting convention. The
load-bearing half — "the volatile classes only" and "23 added/23 removed" —
verifies **exactly**.

### F6 — INFO — minor prose inconsistencies

§0 says the arm covers "the six sharpest candidates from the scout's headline"
while §2 says "All five scout headline items chosen for this arm"; the scout's
headline table has five numbered rows. `failures: {}` is the printed-envelope
shape; the receipts store per-entry `failures: []` (empty list) — semantically
equal. Neither affects any measurement.

## 3. Out of scope / not re-verified

* No legs re-executed; no scout receipts regenerated. Vacuity was audited from
  the fixture's assertion code plus the recorded fields, not by re-running.
* The two post-report runs' attribution (which lane re-ran `--probe-module-r80`
  and copied the receipt into `r80-author/`) is outside this audit; both are
  green and consistent with the author's bytes.
* `SHONEN.md` dirt is foreign and pre-existing (r80-baseline documents it
  before this seat's window); not re-attributed.
* The report's "~55 s" replay estimate and toolchain micro-versions beyond the
  top-level checks (e.g. numpy 2.5.3) were not independently re-measured.

## 4. Verdict-relevant summary for the judge

Every verdict-bearing claim in `r80-author.md` traces to a receipt: all ten
legs' measured fields are present and equal run-to-run, the disclosed failing
run is receipted verbatim, the author↔scout surface shows zero contradictions,
and no leg is vacuous or `coverage_blocked`-as-verified. Two factual defects
stand: **F1** — the t1 row's `23→23` module count appears in no receipt (the
receipted value is `49→49`; the underlying "unmoved" law holds); **F2** — the
"run 2 verbatim" column quotes the first formal run's volatile values. F3–F5
are provenance/precision items; F6 is cosmetic. Nothing found that would flip
a leg verdict.

---

*Seat output only. Read-only on tracked files and other lanes' artifacts, no
commits, no judgment passed on any other lane's work; the canonical Rust
runtime remains the sole judge.*
