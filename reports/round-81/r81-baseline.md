# R81 baseline — frozen-tree regression replay at `15c6a35b` + battery ×2 (4 modes × 2 runs)

host: `plazir27` (`Linux 7.2.3-arch1-3`), seat: BASELINE. Lane
`~/Projects/shokunin/audio-shokunin`. Freeze target: the **reconcile commit**
`15c6a35b066acfb9474d1b569bb8a76b42f4f06a` ("reconcile: late r77 wave-B
reports + fleet round-1 calibration audit … + forward scout reports r82-r90",
committed 2026-10-15 13:53:54 −0300 = **16:53:54Z**), fixture sha256
**`ac9c64a1b51f3c986b08644c8c0e6b59be8efce1d3a7baa6994f5b3a1a4ae717`**
(725,461 B, git blob `adab76ce7e491fb7551b687f4e3555079d792cb7`, clean vs
HEAD at entry). Everything below is attributable to those bytes.
**No tracked edits by this seat; nothing committed.**

The battery is the file's default `normal` mode plus the three newest probe
entries (r78, r79, r80 — the r80 family is new at this freeze), executed
**twice** (`runs-a`, `runs-b`) with the fixture run **inside the frozen tree**
(`corpus/live/r81-baseline/tree/`, CWD = tree root), so every receipt lands
under `tree/corpus/live/runs/` and the worktree is never written. Receipts,
tooling and comparison outputs live in `corpus/live/r81-baseline/`.

---

## 0. Headline

| # | question | answer |
| --- | --- | --- |
| 1 | Did the freeze hold? | **The frozen bytes held; HEAD did not.** 125-sample watcher (`head-watch.log`, 17:01:25 → 17:22:06Z, every 10 s): the **tree** fixture sha is `ac9c64a1…` in every sample and re-recorded before/after all 8 runs. HEAD moved **twice** mid-battery — `dbe3a7f` (17:06:15Z) and `c58ac36` (17:11:06Z) — both **report-only** commits (`reports/round-81/r81-boundary-readonly.md`, `reports/round-91/r91-scout.md`); `git diff` for the fixture across them is **empty**. From 17:14:26Z a sibling lane (r81-author) dirtied the worktree fixture (`c1a1c6fa…` → `3fad7c4c…` → `0dad37ee…`, now carrying a `--probe-gst-r81` probe my frozen copy does not have) — the tree copy stayed `ac9c64a1…`. |
| 2 | Is the replay green? | **6/8 runs green.** `normal` ×2, `capture-r78` (run-a), `capture-r79` (run-b), `module-r80` ×2: exit 0, `failures {}`, stderr 0 B. Two red: run-a `capture-r79` (2 legs, foreign node) and run-b `capture-r78` (3 cases, the known metadata/tap flap). Both reds are named row-by-row in §4. |
| 3 | Byte-identical vs landed receipts? | **Receipt-level: 2/8.** Both `normal` runs are byte-identical to `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b` — the same bytes as **371 landed `normal` receipts (352 of them tracked)**. The six probe receipts have **no prior byte match** (pid-stamped node names + numeric jitter make cross-session byte identity impossible for probe modes; the same was true in r80). |
| 4 | Leaf-level byte-identity vs the nearest landed reference per family? | `normal` **373/373 exact (100 %)**; `capture-r78` 8 276/12 426; `capture-r79` 18 194/23 680; `module-r80` 1 253/1 789. Full class tables in §3. |
| 5 | Same-bytes noise floor (runs-a vs runs-b)? | `normal` **373/373 exact, 0 of any other class**; `module-r80` 1 semantic leaf of 1 785; `capture-r79` 182 semantic of 23 680; `capture-r78` 234 semantic of 12 386. The semantic mass is concentrated in the red legs of §4 and the window-content / `host_is_quiet` classes (§4.4). Prior reference pairs for scale: r79 pair **0** semantic, r80 pair 5, r78 pair 140. |
| 6 | Verdict surface (legs/classes/outcomes/failures) vs prior? | **Identical in 6 of 8 runs.** The two exceptions are exactly the two red runs: run-a r79 `capture_lattice` (`named_outcomes` 12 → 8, `FAILURES []` → 2 rows) and run-b r78 (3 entries, `FAILURES []` → rows; legs/classes/outcomes unchanged). `module-r80` **both runs IDENTICAL**, `capture-r79` run-b **IDENTICAL**. |

---

## 1. Frozen state and archive

- **Entry state** (`env.txt`, 17:01:22Z): HEAD `15c6a35b`, fixture
  `ac9c64a1…`, `fixture_dirty_vs_HEAD: ''`, git blob `adab76ce…`. Host quiet:
  no foreign null sinks/sources at entry, no leaked probe processes (the r80
  window's ~10 h stale `aplay` is gone), `load 0.64`, session defaults
  `…HiFi__SPDIF__sink` / `…HiFi__Line__source`.
- **Archive** (`tree-archive.txt`, `archive-tree.sh`): `git archive HEAD`
  → tar sha256 `b4c7efc0e1d69d0f85bb7b91ac13574132ce9729f5d32735323f243e194d7ab5`,
  459,755,520 B, 30,765 members; extracted **23,803 files + 6,963 dirs**;
  file-set symmetric difference against `git ls-tree -r HEAD` = **0**; the
  fixture inside the tree is byte-equal to the worktree (`ac9c64a1…` both
  sides). The tree carries the committed receipt corpus (5,302 tracked
  `corpus/live/runs/` files) plus 476 MB of tracked fixture WAVs; gitignored
  by `corpus/.gitignore: live/*/*tree*`.
- **Watcher** (`head-watch.log`, 125 samples): HEAD `15c6a35` → `dbe3a7f`
  (17:06:15Z) → `c58ac36` (17:11:06Z); worktree fixture clean until
  17:14:16Z, dirty from 17:14:26Z; **tree fixture `ac9c64a1…` in every
  sample**. HEAD at exit `c58ac36`.
- **Pre-existing / foreign dirt at exit**: ` M SHONEN.md` (13:53:31 local,
  the reconcile commit's preserved patch) and the sibling r81-author's
  ` M corpus/fixtures/measure_audio.py` + ` M …/__pycache__/measure_audio.cpython-314.pyc`
  (mtime 14:15:56 local = 17:15:56Z). **Neither is this seat's**: the
  worktree fixture now contains `--probe-gst-r81` (3 hits) which the frozen
  tree copy has 0 of, and all 8 receipts of this battery landed under the
  tree, none under the worktree's `corpus/live/runs/`.

## 2. The battery — commands, windows, receipts

All eight runs: `python3 corpus/fixtures/measure_audio.py [--probe-…]` with
CWD `corpus/live/r81-baseline/tree`. Driver `battery.sh`; every run bracketed
by a tree-fixture sha256 check (`SHA before=… after=… rc=…` in
`runs-{a,b}/commands.log`); receipts copied inline and re-validated by
`collect-receipts.py`.

| run | mode | window (UTC) | dur | rc | failures | canonical receipt (in tree) | sha256 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| a | `normal` | 17:01:56 → 17:01:57 | 1 s | 0 | `{}` | `20261015T170157285159Z-normal` | `8e8cdad6cc3c356d…` |
| a | `--probe-capture-r78` | 17:01:57 → 17:05:28 | 3 m 31 s | 0 | `{}` | `20261015T170528427362Z-capture-r78` | `7528f037f7768ccf…` |
| a | `--probe-capture-r79` | 17:05:28 → 17:11:00 | 5 m 32 s | **1** | `capture_lattice` b05/b06 | `20261015T171100080047Z-capture-r79` | `7edaaf011f263fb1…` |
| a | `--probe-module-r80` | 17:11:00 → 17:11:26 | 26 s | 0 | `{}` | `20261015T171126223367Z-module-r80` | `0f7ac37dfa4410de…` |
| b | `normal` | 17:11:26 → 17:11:27 | 1 s | 0 | `{}` | `20261015T171127316692Z-normal` | `8e8cdad6cc3c356d…` |
| b | `--probe-capture-r78` | 17:11:27 → 17:14:54 | 3 m 27 s | **1** | 3 cases (§4.2) | `20261015T171453987764Z-capture-r78` | `4b040b56d921524d…` |
| b | `--probe-capture-r79` | 17:14:54 → 17:20:31 | 5 m 37 s | 0 | `{}` | `20261015T172031094682Z-capture-r79` | `d8270046e5781893…` |
| b | `--probe-module-r80` | 17:20:31 → 17:20:57 | 26 s | 0 | `{}` | `20261015T172057193402Z-module-r80` | `4c40c15cb8c3ea29…` |

**Rows replayed** (`rows.txt`): per run **86 receipt entries** (17 base + 8
r78 + 8 r79 + 2 r80), **136 legs** (0 + 59 + 67 + 10) and **38 179 / 38 154
leaf cells** (run-a / run-b, `normal` 373 each). Two runs = **172 entries,
272 legs, 76 333 leaf cells**; the four cross-run comparisons in §3 cover
**38 268 distinct leaf paths**.

**Battery scope, stated plainly.** `normal` + the three newest probe
families, per the r80 convention (that baseline ran `normal` + its two newest
entries, r78/r79); the r80 family is included here because it is new at this
freeze and its 10 legs are the only r80-era code under test. Rows for r70–r77
are **not** re-run (they are anchored by the r78 baseline's 127-command
harness and the r79/r80-verify receipts).

## 3. Per-case field stability (pid-normalized, `percase.py`)

Normalization is the r80 one, verbatim (digit runs ≥ 5 → `<N>`, `/tmp/<scratch>`,
wall-clock → `<t>`, `0x…` → `<ptr>`, `own_pid`/`client_id`-keyed leaves
volatile). Numeric leaves are **not** normalized — they are reported as
jitter with spread, so a real value change cannot hide in a digit rewrite.

| comparison | receipts | exact | volat | jit | sem | added | removed | total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `normal` runs-a vs runs-b | 2 | **373** | 0 | 0 | **0** | 0 | 0 | 373 |
| `normal` vs tracked canonical | 3 | **373** | 0 | 0 | **0** | 0 | 0 | 373 |
| r78 runs-a vs runs-b | 2 | 8 828 | 218 | 3 084 | 234 | 13 | 9 | 12 386 |
| r78 vs nearest prior pair | 4 | 8 276 | 214 | 3 501 | 430 | 0 | 5 | 12 426 |
| r79 runs-a vs runs-b | 2 | 18 238 | 2 143 | 3 024 | 182 | 32 | 61 | 23 680 |
| r79 vs nearest prior pair | 4 | 18 194 | 2 143 | 3 064 | 279 | 0 | 0 | 23 680 |
| r80 runs-a vs runs-b | 2 | 1 289 | 62 | 433 | **1** | 0 | 0 | 1 785 |
| r80 vs nearest prior pair | 4 | 1 253 | 58 | 431 | 47 | 0 | 0 | 1 789 |
| *prior pair alone* r78 (`081421351571Z` vs `055701745739Z`) | 2 | 11 686 | 224 | 319 | 140 | 35 | 3 | 12 407 |
| *prior pair alone* r79 (r80-baseline runs-a/b) | 2 | 19 364 | 2 145 | 2 110 | **0** | 0 | 0 | 23 619 |
| *prior pair alone* r80 (fold runs `160033687459Z` vs `161018039047Z`) | 2 | 1 261 | 58 | 425 | 5 | 36 | 4 | 1 789 |

Reference groups: `normal` = tracked canonical
`corpus/live/runs/20261014T142151899785Z-normal/measurements.json`;
r78 = r79-verify R78 `081421351571Z` + newest tracked `055701745739Z`;
r79 = r80-baseline runs-a/runs-b `085638725489Z` / `090549097852Z`
(pre-r80-fold bytes); r80 = r80 fold runs `160033687459Z` / `161018039047Z`
(the fold's final revision, 90 s pre-commit).

Reading:

- **`normal` is byte-reproducible across the r81 freeze** — 373/373 exact in
  every direction, three sessions/trees deep (§5).
- **`module-r80` is the tightest probe family** (1 semantic leaf of 1 785 in
  the fresh pair; 47 of 1 789 vs the prior pair), and that single leaf is the
  same `tap/windows[51]/mine` content flag the family's own prior pair
  carries.
- **The r78/r79 fresh pairs are noisier than their reference pairs** — and
  §4 shows why: the semantic mass is concentrated in exactly the legs that
  went red, plus the window-content and `host_is_quiet` classes.
- Jitter (3 024 / 3 084 leaves) is the known estimator class: `a_l`/`a_r`
  amplitudes, bimodal `f_l`/`f_r`, `peak_*`, `waited_s`, `module_id` bases —
  the r80 taxonomy reproduces unchanged.

## 4. Drift rows, named individually

### 4.1 run-a `capture-r79` — two legs, foreign node `r91s_src1` (contention, named in-receipt)

`loopback_capture_lattice_r79_probe` legs **`b05_garbage`** (`-C no_such_node_r79`)
and **`b06_zero`** (`-C 0`) — the two fallback legs whose expected kind is
`dsource` — resolved their input producer to **`r91s_src1:capture_FL/FR`**
instead of the session default source:

```
capture b05_garbage: expected producers
  [alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source], got ['r91s_src1']
capture b06_zero:    expected producers
  [alsa_input.usb-Generic_USB_Audio-00.HiFi__Line__source], got ['r91s_src1']
```

Attribution (by name and by clock, not by inference): `r91s_src1` is created
by the **r91-scout lane's own harness** — `corpus/live/r91-scout/probes/driver.py:449`
`load_remap_source("r91s_src1", NS1)` ("pw-play tone -> NS1, remap-source
r91s_src1"), with per-leg receipts at
`corpus/live/r91-scout/runs/loss/F1s_pwrec_srcloss_r{0,1,2}/` stamped
**17:06:34 → 17:07:27Z** — inside this leg's window (17:05:28 → 17:11:00Z).
The r91-scout commit `c58ac36` landed at 17:10:56Z.

Verdict-surface delta (`fold-delta-r79.txt`, run-a vs refs): **only**
`loopback_capture_lattice_r79_probe` differs — `named_outcomes 12 → 8` (the
four removed are exactly those legs' `capture_default_source_unnegotiated` +
`content_pin_unmeasured`) and `FAILURES [] → [the two rows above]`. Legs
13 → 13, classes unchanged, all seven other r79 entries **IDENTICAL**.
This is a foreign-node interference row, **not** a code delta: run-b's r79
(same bytes, no foreign source live) is `failures {}` and **verdict-identical
to the reference pair**.

### 4.2 run-b `capture-r78` — three cases, the documented metadata/tap flap

| case | failure rows |
| --- | --- |
| `playback_target_lattice_r78_probe` | `lattice absent_sink: the monitor tap on alsa_output…HiFi__SPDIF__sink carried no tag-tone windows — consumption without content is not a playout verdict` |
| `playback_default_follow_r78_probe` | `follow moved: last live consumers ['alsa_output…HiFi__SPDIF__sink'] — the stream never settled on the live default at ITS spawn (r78_def_sink_1252822)`; `follow moved: the monitor tap on r78_def_sink_1252822 carried no tag tone`; `follow restored: the monitor tap on …SPDIF__sink carried no tag tone` |
| `playback_props_r78_probe` | `props prop_garbage: monitor tap on ['…SPDIF__sink'] carried no tag tone`; `props node_target_garbage: monitor tap on ['…SPDIF__sink'] carried no tag tone` |

The fixture's **own confound attribution** for the `default_follow` entry:
`confound_observed: true`, `coverage_blocked: ["pactl: metadata was
alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink at write time, not
r78_def_sink_1252822 — the stale/delayed class is unattributable this run"]`,
classes `["live_default_follow", "pactl_delayed_default", "pactl_stale_default",
"active_stream_pinned"]`. That is the **session-metadata write race** the r79
baseline's anchor and the r80 baseline's §6 already named for this arm
(anchor: failed + `coverage_blocked`; R78: coverage-blocked only; r80
battery: clean). Verdict-surface delta vs refs (`fold-delta-r78-runb.txt`):
legs/classes/outcomes **unchanged**; only `FAILURES [] → rows` on those three
entries. Run-a's r78 (same bytes) is `failures {}` and **verdict-IDENTICAL**
to refs. Note the fixture's own process census said `host_is_quiet: true` in
all 8 r78 entries in **both** runs, so this row is not attributable to a
foreign probe process visible to that census; it is the family's documented
content/tap flap. The family never reproduces byte-identically at all: **16
distinct receipt bytes across 16 landed r78 receipts**, and its own prior
pair carries 140 semantic leaves (128 of them in `playback_default_follow`).

### 4.3 census rows (not failures)

- run-b `capture-r79`: `host_is_quiet: false` in **5/8** entries (run-a: 8/8
  true). The non-zero signal is **`fixture_runs: 1`** in exactly those five
  entries (`loopback_capture_lattice`, `loopback_playback_lattice`,
  `loopback_matrix`, `loopback_record_target`, `loopback_hotplug`) — the
  fixture's own census detected **one other `measure_audio.py` process live**
  during the 17:14:54 → 17:20:31Z window. Despite that, run-b's r79 verdict
  surface is **IDENTICAL** to refs (so a concurrent sibling fixture run did
  not move any r79 verdict; the r91 foreign *node* in §4.1 did).
- All other 31 census entries: `host_is_quiet: true`, `fixture_runs: 0`, and
  every probe counter (`pw_play`, `pw_record`, `pw_cat`, `pw_loopback`,
  `paplay`, `parec`, `pacat`, `aplay`, `arecord`, `ffmpeg`) **0**.
- `module_args_lattice_r80_probe/contention/host_is_quiet`:
  `False/False` (both fold reference runs) vs `True/True` (both r81 runs) —
  a CODE-DELTA-class leaf whose delta is on the **reference** side (the r80
  fold's runs shared the host with a foreign probe; this battery's did not).
- `module_args_lattice_r80_probe` `a5_linger_orphan/re_unload/*` and
  `unload_own/*` shape rows: reference[0] (`160033687459Z`) carries the raw
  `pa_no_such_entity` failure (`error_class`/`exit_code`/`stderr_tail`),
  reference[1] and **both** r81 runs carry the F2 guard's `skipped:
  already_unloaded` — i.e. the fold's own documented shape change, stable in
  the fresh pair (`fold-delta-r80.txt`: both r80 entries verdict-IDENTICAL).

### 4.4 where the semantic mass sits (exact per-case counts)

`percase.py` classifies, per case (exact counts; the fresh pair is
runs-a vs runs-b, the prior pairs are §3's reference groups):

| case | r78 fresh | r79 fresh | r80 fresh | r78 prior pair | r80 prior pair |
| --- | --- | --- | --- | --- | --- |
| default_follow / capture_lattice | 82 | 76 | — | 128 | — |
| target_lattice / playback_lattice | 63 | 67 | — | 11 | — |
| props / hotplug | 56 | 37 | — | — | — |
| target_loss / matrix / record_target | 33 | 1 + 1 | — | — | — |
| topology (r80) | — | — | 1 | — | 5 |
| **total semantic** | **234** | **182** | **1** | **140** | **5** |

The r79 prior pair is **0**. Sampling the printed rows (`percase.py` prints
≤ 25 per case): **85 of 100** printed r78-fresh-pair rows, **61 of 77**
printed r79-fresh-pair rows and the single r80 row are
`tap/windows[i]/audio|mine` content flags — the same marginal class the
r78/r79/r80 baselines named, and the reason no probe family is
byte-reproducible. The rest of the r78/r79 mass is the failure-shape
(`confound_observed`/`coverage_blocked`/`failures` keys replacing the
correlate keys) of the red legs in §4.1–4.2 plus `host_is_quiet` in §4.3.
Cross-reference counts (`vs prior`): r78 430 (default_follow 251,
target_lattice 72, props 68, target_loss 34, 5 singletons), r79 279
(capture_lattice 153, playback_lattice 81, hotplug 37, 8 singletons), r80 47
(topology 30, args_lattice 17).

## 5. Byte identity (§`byte-identity.txt`)

- **`normal`: 2/2 receipts byte-identical** to
  `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b`, which is
  the byte value of **371 of the 519 landed `normal` receipts** (352 tracked;
  the other 148 are older generations with 24 other distinct byte values).
  Both runs, plus a pre-battery smoke run at 17:01:51Z (`smoke-normal.receipt.json`),
  produced that exact file — three independent runs in the frozen tree.
- **`capture-r78` / `capture-r79` / `module-r80`: 0/6 byte-identical** to any
  landed receipt of the same mode (16 / 14 / 10 distinct prior byte values
  respectively). Expected: those receipts embed pid-stamped node names
  (`r79lb_<pid>_…`, `r78_def_sink_<pid>`, `r80md_<pid>_…`) and measured
  quantities. Their equality surface is the per-case table in §3, not bytes.
- The tree's own `corpus/live/runs/` copy of the tracked canonical `normal`
  receipt is byte-equal to the worktree's, so the comparison is against
  committed bytes, not a working copy.

## 6. Contention ledger

- **Foreign actors observed live inside the battery window** (all read-only
  observations; this seat created only its own `r79lb_*`/`r78*`/`r80md_*`
  probe objects via the fixture, and never touched the default sink/source):
  the r91-scout's `r91s_src1` remap-source (17:06:34 → 17:07:27Z, **named in
  run-a's failure rows**); the r81-author seat's `python3 -m py_compile` +
  `--probe-gst-r81` legs (17:15:56Z onward; `gst-launch-1.0 pipewiresrc
  target-object=gst_r81_auth_1291125 … stream.capture.sink=true` observed at
  17:18–17:19Z), whose worktree fixture edits begin 17:14:26Z; a sibling
  `--probe-capture-r78` run started 17:21:33Z (`r78_play_sink_1426648` +
  `r78lat_source_name_tap` still resident at post-state). Foreign
  `normal`/`gst-r81` receipts appeared in the worktree runs dir during the
  window (`20261015T171719214164Z-gst-r81`, `…171856751772Z-gst-r81`,
  `…172134153125Z-normal`) — none of them mine.
- **Entry vs exit host state**: default sink/source unchanged
  (`…HiFi__SPDIF__sink` / `…HiFi__Line__source`); no foreign null sinks at
  entry, three foreign `r78*`/`r79lb_*` nodes at exit (sibling runs, listed
  above); `corpus/live/runs/` in the worktree grew 5 704 → 5 707 (sibling
  receipts only — **this battery wrote zero receipts there**).
- **This seat's own contention footprint**: 8 fixture runs, all on
  probe-owned sinks/nodes; the r79 arm's legs route tones only to probe-owned
  sinks (its fail-closed guard) and the r78/r80 families pin every leg to
  probe-owned objects; no `pactl set-default-sink` was ever issued. The
  fixture's own census (36 entries across the 8 receipts) shows every probe
  counter at **0**; the only foreign signals it saw are the `fixture_runs: 1`
  rows and `host_is_quiet: false` of §4.3 (a concurrent sibling
  `measure_audio.py`, run-b r79 window).

## 7. Write-scope accounting

Wrote only: this report (new file, untracked) and `corpus/live/r81-baseline/`
— `tree/` (gitignored `git archive` materialization, 480 MB), `runs-a/` +
`runs-b/` (8 receipts + stdout/stderr/commands.log/receipt-shas.txt),
`attempt-1-failed/` (the failed first attempt's logs, see §8),
`env.txt`, `pre-state.txt`, `post-state.txt`, `head-watch.log`,
`tree-archive.txt`, `smoke-normal.receipt.json`, the tooling (`archive-tree.sh`,
`battery.sh`, `env.sh`, `watch.sh`, `percase.py`, `fold-delta.py`,
`verdicts.py`, `rows.py`, `byteid.py`, `collect-receipts.py`, `compare-all.sh`)
and the comparison outputs (`stability-*.txt` × 11, `fold-delta-*.txt` × 6,
`byte-identity.txt`, `rows.txt`, `receipt-shas.txt`). Scratch 483 MB total
(480 MB tree + 3.5 MB of tooling/evidence, 67 files outside the tree), no
`.wav` of this seat's own outside the tracked fixtures inside `tree/`; the
tar receipt (438 MiB) lives outside the repo in `/tmp/r81-baseline-work/`.
**Zero tracked-file edits, zero commits, zero pushes, no `git checkout`.**
`collect-receipts.py` reports `collector_faults=0` (all 8 inline copies
byte-equal to their canonical tree receipts, stamps and `mode` fields
matching).

## 8. Disclosed tooling faults

1. **`battery.sh` attempt 1 (fixed, recorded)**: the first version redirected
   stderr to a repo-relative path inside the `cd "$TREE"` subshell, so bash
   refused the redirection and **all 8 legs died with rc=1 before python
   ran** (`attempt-1-failed/runs-{a,b}-commands.log`, `battery.out`). All
   paths are absolute in the working version; the failed attempt wrote no
   receipt and its logs are kept. The battery restarted at 17:01:56Z.
2. **`verdicts.py` (r80 copy) crashed** on the r78 family's boolean
   `sinks_gone` (`AttributeError: 'bool' object has no attribute 'values'`);
   patched in the seat copy (bool branch added) and re-run.
3. `percase.py`'s `pairkind` CODE-DELTA label needs **4** receipts; the
   `normal` and reference-pair comparisons (3 and 2 receipts) are reported
   without it, which is why their detail sections carry no pair annotation.

## 9. Remaining unknowns

1. **What moved the session default-sink metadata in run-b's r78 window**
   (17:11:27 → 17:14:54Z). The fixture marks it `pactl_delayed_default` /
   `pactl_stale_default` + `confound_observed`; no foreign probe process was
   visible to its census (`host_is_quiet: true` 8/8), and no foreign actor was
   observed live by this seat inside that window. The sibling r81-author was
   editing the fixture from 17:14:26Z but ran no probe before 17:17:19Z.
2. **Which lane owns the resident `r78_play_sink_1426648` /
   `r78lat_source_name_tap`** at exit (a sibling `--probe-capture-r78` run
   started 17:21:33Z, i.e. after this battery's last leg at 17:20:57Z).
3. The r91-scout's `r91s_src1` window (17:06:34 → 17:07:27Z) is established
   from its own per-leg receipt mtimes; the exact instant it became a visible
   producer to this lane's legs is not instrumented on either side.
4. r70–r77 families were not replayed in this window (§2).

---

*Seat output only. Read-only on tracked files, no commits, no judgment passed
on any other lane's work; the canonical Rust runtime remains the sole judge.*
