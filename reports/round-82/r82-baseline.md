# R82 baseline — frozen-tree replay at `b7d80d0` + battery ×2 (4 modes × 2 runs)

host: `plazir27` (`Linux 7.2.3-arch1-3`), seat: BASELINE. Lane
`~/Projects/shokunin/audio-shokunin`. Freeze target: HEAD **`b7d80d0`**
("r81 report-last: adjudicator ADMIT-corr, LOG + SCORECARD — gst-pipewire
lattice round closed"), fixture sha256
**`5eaba74b532eb9c62d529fe3d94534c36cb3b3954365cb61b8552ade9ed49d82`**
(807,112 B, git blob `38c67960d1d0622184b1e8262c7b401ee4dcfc3e`, clean vs
HEAD at entry). **No tracked edits by this seat; nothing committed.**

The battery is the file's default `normal` mode plus the three newest probe
entries (r78, r79, r80), executed **twice** (`runs-a`, `runs-b`) with the
fixture run **inside the frozen tree** (`corpus/live/r82-baseline/tree/`,
CWD = tree root), so every receipt lands under `tree/corpus/live/runs/` and
the worktree is never written. Receipts, tooling and comparison outputs live
in `corpus/live/r82-baseline/`. **HEAD moved mid-battery** to `9725e53` (the
sibling r82-boundary lane's commit, 18:59:39Z) — the frozen tree was
unaffected: the fixture sha is `5eaba74b…` in **all 124** watcher samples,
before and after every run.

---

## 0. Headline

| # | question | answer |
| --- | --- | --- |
| 1 | Did the freeze hold? | **Yes.** 124-sample watcher (`head-watch.log`, 18:48:52 → 19:09:2xZ, every 10 s): tree fixture sha `5eaba74b…` in every sample; HEAD `b7d80d0` → `9725e53` at 18:59:35–18:59:45Z, a **sibling commit that does not touch the fixture** (worktree fixture stayed `5eaba74b…` too; `git show --stat 9725e53` has no `corpus/fixtures/` entry). Tar sha `2cecf391…`, file-set symmetric difference vs `git ls-tree -r HEAD` = **0**. |
| 2 | Is the replay green? | **6/8 runs green** on rc; **5/8 with `failures {}`**. `normal` ×2, `capture-r79` ×2, `module-r80` run-b: rc 0, `{}`, stderr 0 B. Three red runs: run-a `capture-r78` (1 case: props tap), run-a `module-r80` (1 case: host-global module count 47→48), run-b `capture-r78` (1 case: the documented metadata flap). All reds are named row-by-row in §4 with a contention class. |
| 3 | Rep counts as expected? | **86 entries / 136 legs per pass, exact.** Each pass: `normal` 17/0, `capture-r78` 25/59, `capture-r79` 25/67, `module-r80` 19/10. Leaves: 373 / 12 368 / 23 618(a)–23 617(b) / 1 786(a)–1 785(b). |
| 4 | Pinned `normal` receipt sha? | **`8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b` both runs** — byte-identical to the pinned value and to **375 landed `normal` receipts** (523 landed, 25 distinct byte values). Three sessions deep now (r81, r81-fold/verifier2, r82). |
| 5 | Did the r79 foreign-node red reproduce? | **No.** `capture-r79` is `failures {}` in **both** passes — unlike r81 run-a, no foreign remap-source (`r91s_src1`-class) was live. The b05/b06 fallback legs took the probe's green `capture_default_source_unnegotiated` + `content_pin_unmeasured` path (`source_meta=None`, no producers). |
| 6 | Sibling-lane contention? | **Two sibling lanes were live**, both named in §7: **r82-boundary** (`r82bnd_*` ffmpeg legs 18:50:22→18:57:55Z, extension stage + module custody churn at 18:58:12–25Z, commit `9725e53` at 18:59:39Z) and **r93-scout** (`r93s_in`/`r93s_fc_in` null sinks + `pw-play` legs from 18:59:07Z). **No `gst-launch`/gst_r81_v2 verifier was observed (0 sightings).** |

---

## 1. Frozen state and archive

- **Entry state** (`env.txt`/`pre-state.txt`, 18:48:32Z): HEAD `b7d80d0`,
  fixture `5eaba74b…`, `fixture_dirty_vs_HEAD: ''`; host quiet — no foreign
  null sinks/sources, no foreign modules, no probe processes; node count 10
  (4 hw sinks incl. HDMI, 2 hw sources, 4 drivers); default sink/source
  `…HiFi__SPDIF__sink` / `…HiFi__Line__source`; load 6.15.
- **Archive** (`tree-archive.txt`, `archive-tree.sh`): `git archive HEAD`
  → tar sha256 **`2cecf391a000fe28f6b6f0bbd7eeeb072be743a9355a6f794d9707a4a1e13b14`**,
  483,727,360 B, 30,981 members; extracted **23,997 files + 6,985 dirs, 0
  symlinks**; file-set symmetric difference against `git ls-tree -r HEAD` =
  **0**; the fixture inside the tree is byte-equal to the worktree
  (`5eaba74b…` both sides). The tree carries the committed receipt corpus
  (5,302 tracked `corpus/live/runs/` files) plus the tracked fixture WAVs.
- **Watcher** (`head-watch.log`, 124 samples): tree fixture `5eaba74b…` in
  every sample; HEAD transition `b7d80d0` → `9725e53` between 18:59:35Z and
  18:59:45Z; worktree fixture unchanged throughout. Sibling process census
  every sample (see §7).
- **Exit state** (`post-state.txt`, 19:11:15Z): HEAD `9725e53`; worktree and
  tree fixture both `5eaba74b…`; default sink/source unchanged; **no
  `r78*`/`r79*`/`r80*` module, node or process left by this battery**
  (foreign `r93s_in`/`r93s_fc_in` + `module-null-sink sink_name=r93s_in
  channels=1` were the r93-scout lane's, gone by 19:13Z). Tracked dirty at
  exit: only the pre-existing ` M …/__pycache__/measure_audio.cpython-314.pyc`
  (present before this seat ran anything).
- **The fixture at HEAD differs from r81's frozen bytes** (`5eaba74b` vs r81's
  `ac9c64a1`, +1,661 lines): the only diff hunks are the r81-fold's
  `--probe-gst-r81` family insertion and 4 `main()` hunks (argparse/mode/
  suffix). The r78/r79/r80 family code is byte-identical between the two
  freezes — so §6's cross-freeze comparisons are code-comparable.

## 2. The battery — commands, windows, receipts

All eight runs: `python3 corpus/fixtures/measure_audio.py [--probe-…]` with
CWD `corpus/live/r82-baseline/tree`. This is the **documented invocation
verbatim** (r81-fold: "there is no `--runs` flag"; r81-verifier2: "the
baseline's four modes verbatim"). Driver `battery.sh`; every run bracketed
by a tree-fixture sha256 check (`SHA before=… after=… rc=…` in
`runs-{a,b}/commands.log`, all 8 show `5eaba74b` before/after); receipts
copied inline and re-validated by `collect-receipts.py`
(**`collector_faults=0`**).

| run | mode | window (UTC) | dur | rc | failures | canonical receipt (in tree) | sha256 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| a | `normal` | 18:48:58 → 18:48:59 | 1.2 s | 0 | `{}` | `20261015T184859199349Z-normal` | `8e8cdad6cc3c356d…` |
| a | `--probe-capture-r78` | 18:48:59 → 18:52:25 | 3 m 26 s | **1** | props tap (1) | `20261015T185225182022Z-capture-r78` | `cc71d132741d5ff1…` |
| a | `--probe-capture-r79` | 18:52:25 → 18:58:03 | 5 m 39 s | 0 | `{}` | `20261015T185803826885Z-capture-r79` | `bdeeda54503fd782…` |
| a | `--probe-module-r80` | 18:58:03 → 18:58:30 | 27 s | **1** | topo t1 module count (1) | `20261015T185830064975Z-module-r80` | `919ce1115062e518…` |
| b | `normal` | 18:58:30 → 18:58:31 | 1.3 s | 0 | `{}` | `20261015T185831252955Z-normal` | `8e8cdad6cc3c356d…` |
| b | `--probe-capture-r78` | 18:58:31 → 19:01:58 | 3 m 28 s | **1** | default-follow metadata (1) | `20261015T190158516697Z-capture-r78` | `d9bfa84511c2a806…` |
| b | `--probe-capture-r79` | 19:01:58 → 19:07:40 | 5 m 42 s | 0 | `{}` | `20261015T190740035768Z-capture-r79` | `f60025dfbae87519…` |
| b | `--probe-module-r80` | 19:07:40 → 19:08:07 | 28 s | 0 | `{}` | `20261015T190807923331Z-module-r80` | `82ee18ccc61398e4…` |

Receipt sha table: `corpus/live/r82-baseline/receipt-shas.txt` (reference +
fresh) and `runs-{a,b}/receipt-shas.txt` (canonical tree paths).

## 3. Per-mode results and rep counts

`rows.txt` (fixture entries + legs inside every entry's `legs` map):

| mode | entries | legs | leaves a / b | cases with failures a / b |
| --- | --- | --- | --- | --- |
| `normal` | 17 | 0 | 373 / 373 | 0 / 0 |
| `capture-r78` | 25 | 59 | 12 368 / 12 368 | **1** / **1** |
| `capture-r79` | 25 | 67 | 23 618 / 23 617 | 0 / 0 |
| `module-r80` | 19 | 10 | 1 786 / 1 785 | **1** / 0 |
| **per pass** | **86** | **136** | 38 145 / 38 143 | 2 / 1 |

- **86 entries / 136 legs per pass — exact match to the expectation** (and to
  the r81-fold/verifier2 shape 17/0 + 25/59 + 25/67 + 19/10).
- Custody: every r78/r80 entry reports `sinks_gone: true` and
  `own_nodes_after: []`; the r79 family's own teardown removes its
  `r79lb_*`/`r79fc_*` nodes; post-state has **no** battery-owned object left.
  The fixture's own probe objects (`r78*`, `r79lb_*`, `r80md_*`) are the
  seat-owned names of the run; this seat created **no** additional PipeWire
  objects, and issued no `set-default-*` (the fixture itself never does).
- `per-mode-results.txt` carries the per-case failure rows and the census
  non-quiet rows quoted in §4/§7.

## 4. Reds, named individually with contention class

### 4.1 run-a `capture-r78` — one case, `playback_props_r78_probe` (tap-content flap; foreign ffmpeg in the same case)

```
props prop_garbage: monitor tap on
  ['alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink'] carried no tag tone
```

Class: **the r78 family's documented tap-content flap** — the same row text
r81 run-b carried for the same case (`props prop_garbage` + `node_target_garbage`).
The case's own census adds a second, named signal: `host_is_quiet: false`
with **`ffmpeg: 2`** foreign processes live — the r82-boundary lane's ffmpeg
legs were running in exactly this window (watcher: 18:50:52 → 18:51:22Z,
case legs 18:50:52–18:51:22Z). Causality is **not** asserted: the family's
own prior pair carries this class with a quiet census; the honest statement
is "documented flap, contemporaneous with a named foreign ffmpeg". The
verdict-surface delta vs the r81 reference pair (`fold-delta-r78.txt`):
all six r78 cases IDENTICAL except this case's `FAILURES [] → [row]`;
legs 14→14.

### 4.2 run-a `module-r80` — one case, `module_topology_r80_probe` (host-global module-table churn)

```
topo t1: module count moved 47 -> 48 on refused loads
```

Class: **host-global module-table race with a foreign lane's module custody
— not a fixture side effect.** Evidence:

- The fixture's two refused loads are clean: `slaves=@DEFAULT_SINK@` and
  `sinks=@DEFAULT_SINK@` both `rc=1 / pa_io_error / "Failure: Input/Output
  error"`, `module_id: null`, `node_created: false`, `branch_nodes: []` —
  i.e. **nothing was created by the probe**.
- The counted quantity is `pactl list modules short` **line count**, a
  host-global table. The r82-boundary lane was churning its
  `module-null-sink sink_name=r82bnd_ns` in-window: its extension legs
  (`runs/c2x`, `runs/c3x`) ran 18:58:12–18:58:18Z, its `.state.json` was
  rewritten 18:58:24Z and its teardown unloaded a **stale index**
  (`536870921`) at 18:58:25Z while its per-stage receipts show load-index
  churn (c1 536870921, c2 536870917, c3/c5/c6 536870924) — a unload/reload
  cycle straddling the count window is the consistent reading.
- **run-b reproduced the same leg `48 → 48` green** with `host_is_quiet:
  true` and `ffmpeg: 0` — the steady-state count there is host 42 + the
  probe's own 6 sink modules = 48; run-a's `47` start was one short.
- The exact identity of the +1 is **not instrumented** on either side (no
  module-table snapshot at t1); the red is recorded as sibling module
  churn, not a code delta. `fold-delta-r80.txt`: `args_lattice` verdict
  surface IDENTICAL, topology legs 5→5, only this `FAILURES [] → [row]`.

### 4.3 run-b `capture-r78` — one case, `playback_default_follow_r78_probe` (documented stale/delayed default-metadata race)

```
follow moved: last live consumers ['alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink']
  — the stream never settled on the live default at ITS spawn (r78_def_sink_699104)
```

Class: **the `pactl_delayed_default` / `pactl_stale_default` metadata race**
the r79 anchor, the r80 baseline §6 and r81 run-b already named for this arm.
The fixture's own attribution is in-receipt: `confound_observed: true`,
`coverage_blocked: ["pactl: metadata was …HiFi__SPDIF__sink at write time,
not r78_def_sink_699104 — the stale/delayed class is unattributable this
run"]`. Its census says `host_is_quiet: true` (8/8 r78 entries) — no foreign
process was visible, matching r81's run-b shape. Verdict-surface delta vs
refs: legs/classes/outcomes unchanged, only this case's `FAILURES [] → [row]`.

### 4.4 green where r81 was red

`capture-r79` is `{}` **both** passes. `fold-delta-r79.txt` shows the
`loopback_capture_lattice_r79_probe` delta is on the **reference** side: r81
run-a carried the two foreign-`r91s_src1` rows; the r82 fresh pair carries
none and instead adds the four `capture_default_source_unnegotiated` +
`content_pin_unmeasured` named outcomes for b05/b06 (`source_meta=None` —
the same host condition r81's own oracle recorded; with no foreign producer
present the legs take the probe's green no-mine path).

## 5. Byte identity (`byte-identity.txt`)

- **`normal`: 2/2 receipts byte-identical** to
  `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b` — the
  pinned value, and the byte value of **375 of 523 landed `normal` receipts**
  (25 distinct byte values across the corpus; the other 24 cover the
  remaining 148). The pinned sha now survives
  **three sessions on two fixture revisions** (r81 `ac9c64a1`, r82
  `5eaba74b`), the r81-fold verifier's 7-way identity extended by this
  battery's 2 runs.
- `capture-r78` / `capture-r79` / `module-r80`: **0/6 byte-identical** to any
  landed receipt of the same mode (23 / 20 / 15 distinct prior byte values
  respectively). Expected: those receipts embed pid-stamped node names and
  measured quantities; their equality surface is §6, not bytes.

## 6. Per-case field stability (pid-normalized, `percase.py`)

| comparison | receipts | exact | volat | jit | sem | added | removed | total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `normal` runs-a vs runs-b | 2 | **373** | 0 | 0 | **0** | 0 | 0 | 373 |
| `normal` vs tracked canonical | 3 | **373** | 0 | 0 | **0** | 0 | 0 | 373 |
| r78 runs-a vs runs-b | 2 | 8 993 | 217 | 3 040 | 109 | 9 | 9 | 12 377 |
| r78 vs r81 pair | 4 | 8 420 | 216 | 3 397 | 359 | 0 | 0 | 12 392 |
| r79 runs-a vs runs-b *(pid-normalized)* | 2 | 19 725 | 553 | 3 154 | 185 | 0 | 1 | 23 618 |
| r79 vs r81 pair *(pid-normalized)* | 4 | 19 100 | 553 | 3 622 | 405 | 0 | 0 | 23 680 |
| r80 runs-a vs runs-b | 2 | 1 289 | 62 | 434 | **0** | 0 | 1 | 1 786 |
| r80 vs r81 pair | 4 | 1 281 | 62 | 441 | **2** | 0 | 0 | 1 786 |

Reading, with the classes named:

- **`normal` is byte-reproducible again** — 373/373 exact in every direction,
  zero non-exact leaves of any class.
- **The semantic mass is the known content/census classes, not verdict
  movement.** r78 fresh pair 109: `target_loss` 47, `default_follow` 32,
  `props` 21, `aplay_axis` 6 (`arecord_constrain` `alsa_busy` vs
  `alsa_sample_format`, `arecord_honored` busy vs success,
  `contention/host_is_quiet` False vs True), `target_lattice` 2,
  `class_segv` 1 — i.e. the tap-window `audio|mine` flags plus the red
  cases' shape rows. r79 fresh pair 185: `playback_lattice` 141, `hotplug`
  40 (`host_is_quiet` False→True + `e1_unload_playback` window flags),
  singletons elsewhere. r80 fresh pair: **0 semantic** — the only leaf
  difference is the 1 removed = run-a's failure row.
- r80 vs r81 pair: 2 semantic = the t1 failure row (fresh-pair noise) and
  `t4_move_sticky/tap/windows[51]/mine` (ref-pair noise — the r81 pair
  itself disagreed on it; the family's own prior pair carries the same
  class).
- The small add/remove counts are **shape rows of the red/confound cases**,
  not new measurements: r78's 9/9 = `default_follow/failures[0]` and
  `moved|restored/tap/mine_spans[1][*]`, `props/failures[0]` plus
  `flag_a_prop_b/samples[*]/node/{error ↔ found,state,target_object,…}`,
  and `aplay_axis/confound_observed` + `arecord_constrain/confound` — all
  present on exactly the side that took the flap/contention path. r80's 1
  removed is run-a's t1 failure row. r79's 1 removed is the
  `f9_bad_label/reply` third line (the only list whose length differed
  between passes).
- **Disclosed tooling note — pid-normalization boundary:** run-a's r79
  fixture pid was **4-digit** (`7655`; run-b `2057825`), and `percase.py`'s
  key normalization only rewrites digit runs ≥ 5. The raw comparison
  therefore reports a phantom **6 161 added / 6 162 removed** (every leaf
  under `r79lb_7655_*`/`r79fc_7655_*` is a different key than
  `r79lb_<N>_*`). After targeted pid substitution
  (`pidnorm/*.pidnorm.json`, pid → `9999999`) the honest numbers are the
  table's 0/1 and 0/0 — same order as r81's own fresh pair (182 semantic).
  No other receipt pair is affected (all other pids ≥ 5 digits).

## 7. Contention ledger

- **r82-boundary lane (sibling, live)**: `corpus/live/r82-boundary/r82bnd_probe.py`
  + ffmpeg witness legs; first sighting 18:50:22Z, last ffmpeg sighting
  18:57:55Z (45 samples), extension legs (`runs/c2x`, `c3x`) 18:58:12–18:58:18Z,
  `module-null-sink sink_name=r82bnd_ns` custody churn + teardown unload
  18:58:25Z, commit **`9725e53`** at 18:59:39Z. Its ffmpeg clients are what
  the fixture census counts as `ffmpeg: 1–2` in §4.1/§4.2 windows. Its
  playback legs play `corpus/live/r82-boundary/tmp/tone{2,6,7}.wav` through
  `-f pulse -name r82bnd_*`; its capture legs read `r82bnd_ns.monitor` and
  the SPDIF monitor. None of its objects were touched by this seat.
- **r93-scout lane (sibling, live)**: `corpus/live/r93-scout/` (dir created
  18:59:07Z), `pw-play --target r93s_in` legs from 18:59:55Z (22 samples),
  resident `r93s_in` / `r93s_fc_in` sinks + `module-null-sink
  sink_name=r93s_in channels=1` visible at post-state (19:11Z), gone by
  19:13Z. It was live across run-b's r79/r80 windows; run-b r79's census is
  0/25 non-quiet and r80 is quiet, so no r93 signal reached this battery's
  verdicts.
- **No gst lane**: `grep -c gst-launch head-watch.log` = **0** — no
  `gst_r81_v2` verifier (or any gst process) was live in this window.
- **Other**: a `game-dev-2d-shokunin` battery driver (`run_battery.py
  --runs …`, other repo, no PipeWire clients observed) ran at 18:58Z; a
  sibling lane's own process census (`bash -c pgrep -af 'ffmpeg|ffplay|…'
  | grep -v r82bnd`) was observed — mutual census, recorded.
- **This seat's own footprint**: 8 fixture runs, all on probe-owned
  sinks/nodes; no manual PipeWire object created (no `r82b_*` names were
  needed); no `pactl set-default-*`; **zero receipts written to the
  worktree's `corpus/live/runs/`** (dir count 5 734 → 5 734); all 8 receipts
  under the frozen tree's `runs/` (5 302 → 5 310 files). No unload was
  issued by this seat; the fixture's own teardown was index-verified by
  construction and `sinks_gone`/`own_nodes_after` confirm it.
- **Entry vs exit host state**: default sink/source unchanged; node count 10
  → 10; battery-owned objects at exit **none**.

## 8. Write-scope accounting

Wrote only: this report (new file, untracked) and `corpus/live/r82-baseline/`
— `tree/` (gitignored `git archive` materialization, 461 MiB), `runs-a/` +
`runs-b/` (8 receipts + stdout/stderr/commands.log/receipt-shas.txt),
`pidnorm/` (4 pid-substituted comparison copies), the tooling
(`env.sh`, `archive-tree.sh`, `battery.sh`, `watch.sh`, `post-state.sh`,
`compare-all.sh`, `collect-receipts.py`, `rows.py`, `percase.py`,
`fold-delta.py`, `byteid.py`) and the comparison outputs (`rows.txt`,
`per-mode-results.txt`, `receipt-shas.txt`, `byte-identity.txt`,
`stability-*.txt` × 12, `fold-delta-*.txt` × 3, `env.txt`, `pre-state.txt`,
`post-state.txt`, `head-watch.log`, `tree-archive.txt`). Scratch total
≈ 465 MiB (tree + ~4 MiB tooling/evidence); the tar receipt (461 MiB) lives
outside the repo in `/tmp/r82-baseline-work/`. **Zero tracked-file edits,
zero commits, zero pushes, no `git checkout`.** `collect-receipts.py`
reports `collector_faults=0` (all 8 inline copies byte-equal to their
canonical tree receipts, stamps and `mode` fields matching).

## 9. Remaining unknowns and disclosed tooling notes

1. **Identity of the +1 module** in run-a `module-r80` t1 (§4.2): the count
   window has no module-table snapshot on either side; the r82-boundary
   lane's custody churn is the named candidate, not a proof.
2. **Causality of the run-a r78 props tap red** (§4.1): the row is the
   family's documented flap class; a foreign ffmpeg was live in the same
   case per the fixture's own census, but the family also produces this row
   on a quiet host (r81 run-b).
3. **pid-normalization boundary** (§6): `percase.py`'s ≥5-digit key
   normalization silently inflates add/remove when a probe pid is 4-digit;
   the pid-substituted copies are the honest reading and are kept in
   `pidnorm/`.
4. r70–r77 families were not replayed in this window (same scope as the r81
   baseline: `normal` + the three newest probe entries).

---

*Seat output only. Read-only on tracked files, no commits, no judgment passed
on any other lane's work; the canonical Rust runtime remains the sole judge.*
