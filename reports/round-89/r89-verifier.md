# r89 VERIFIER — wave-B gate on committed `0d732989` (frozen tree)

Seat: verifier (non-author). Host `plazir27` (`Linux 7.2.3-arch1-3`,
32 cores), lane `~/Projects/shokunin/audio-shokunin`, window
**2026-10-16 07:50Z–08:05Z**, loadavg **52–82** throughout (run-start
1-min loads from the receipts: v3 75.17 / v4 75.15 / v5 80.55 /
v6 78.67 / v7 78.67 / cot 76.92; author A1 56.86 / A2 53.90; load
preferred). Target: commit **`0d732989`** ("r89 author: 47 legs / 4
entries pwprof lattice — gate completions, SIGKILL-leaves-49152B
(boundary falsification folded), schema invariants, xw witnesses; 2
green"), frozen via `git archive` — **not** the worktree. Toolchain:
PipeWire **1.6.8** (`pw-profiler` compiled/linked), pactl
**17.0-98-gb096**, Python **3.14.7**, numpy 2.5.3; all scratch under
`TMPDIR=~/Projects/shokunin/tmp`. **No tracked writes by this seat, no
commits, no pushes, no `set-default-*`; every seat artifact under
`corpus/live/r89-verifier/`.** The single permitted `probeParent`
labrat was dispatched once (read-only; its substrate had no exec/write,
disclosed in §7).

## 0. Verdict

**GATE FAIL as a reproducible green landing — PASS on every encoded
law.** Every claim the r89 author landed re-derives green: **106
verifier laws × 14 receipts = 1484 cells, 1464 PASS / 20 FAIL / 0
BLOCKED**, where all 20 red cells are **11 distinct arm failures in
three arm classes** (the 20 = 11 arm laws + 9 entry-level
"failures-empty" cells for the same failures). The laws are intact in
every red; the reds are the *verdict arms*, and the wave itself already
contains natural-rate reds: the **r89 reviewer's replays r89r1/r89r2/
r89r3 are all red** (its own frozen tree, launched via `nohup`), and
this seat's deliberate 3-way co-tenancy round is **3/3 red**. On
identical fixture bytes the wave census is **6 green / 17 receipts**,
and the landing is **not reliably green even solo** (v3 red at
loadavg 75 with `fixture_runs=0`).

| check | required | measured | verdict |
| --- | --- | --- | --- |
| frozen tree integrity | `git archive 0d732989` | tar sha256 `f8497c365df5ce36ef05e48aa12d40343869091b4da9492d6a126e913ddc2eab`; 44 320 files / 11 738 dirs / 0 symlinks; file-set symdiff vs `git ls-tree -r` = **0** | PASS |
| fixture identity | committed blob | sha256 `623c25cc55521472dc54a1ab2b4ccb4a9836fda3ca1a71dcca06092a4317cd22` — identical to the author's declared pin, the worktree blob, and the frozen-tree copy | PASS |
| py_compile / ast | clean | rc=0 inside the frozen tree | PASS |
| `normal` receipt sha | canonical pin | `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b` — **byte-identical to the r85/r86/r87/r88 canonical normal pin** (the r89 insertion is receipt-invisible in normal mode) | PASS |
| replays (HUP-corrected launcher) | green | v3 (solo) **RED** x_top; v4 GREEN (co-tenanted); v5 GREEN (solo); v6 GREEN (co-tenanted); v7 **RED** x_foot (co-tenanted); lockpair-A GREEN (solo) | **FAIL (1/6)** |
| replays (as the wave launches, `nohup`) | green | v1/v2 + orphan: **all RED** `g_hup` rc −9; v1 also x_foot; the reviewer's r89r1–r89r3: **all RED** `g_hup` (r89r1 also x_top) | **FAIL (0/6)** |
| law re-derivation | armed law set | **106 laws × 14 receipts = 1484; 1464 PASS / 20 FAIL / 0 BLOCKED**; author A1/A2 = 106/106 each | PASS (laws) |
| wave-level census on committed bytes | green | **17 receipts: 6 green / 11 red** (greens A1, A2, v4, v5, v6, lockpair-A) | **FAIL** |
| co-tenancy stress (3 tree copies, 3 concurrent) | green | **3/3 red**: x_top ×3, x_foot ×2; gate/oart/schema green 3/3 | **FAIL** |
| verdict-arm classes diagnosed | none | **3 classes**: `g_hup` launcher disposition (×3 receipts), `x_foot` global census (×4), `x_top` own-row/band (×4) — mechanisms measured, §4 | **FAIL** |
| independent live spots (own code, own namespace) | ≥5 shapes | S1–S8 all measured as designed: HUP A/B, strtol extended lattice, `-o` incremental ladder, 4096 blocks, exact-N, Profiler refusal, SIGPIPE, suspension 21→0 (§5) | PASS |
| fixed-path family lock | not TMPDIR-scoped, excludes same-path holders | static path + executed: same-path exclusion, child-holder blocking, cross-TMPDIR land-in-tree; two-run serialization **B waited 33.9 s**; cross-materialization two locks held (inherited F1) | PASS with F5 |
| custody/teardown | zero residue | 14/14 receipts: `unloads` all rc 0, `sinks_gone` all-true, `own_nodes_after: []`; post-state 0 `r89v_*`/`r89a_*` objects, defaults unchanged | PASS |
| zero tracked writes | none | this seat wrote only under `corpus/live/r89-verifier/`; the only tracked dirty file is the pyc that was dirty **before** the window | PASS (for this seat) |
| declared leg count | receipts | declared **47** (commit msg + report), per-entry arithmetic 27+12+4+8=51, measured **52** (27/12/4/9) | **FAIL (doc, F4)** |

## 1. Frozen tree

- `git archive 0d732989` → 3 276 441 600 B tar, sha256 `f8497c36…`;
  extracted to `corpus/live/r89-verifier/tree/` (gitignored per
  `corpus/.gitignore` `live/**/*tree*/`). Census 44 320 files / 11 738
  dirs / 0 symlinks; file-set symdiff vs `git ls-tree -r 0d732989` =
  **0 lines** (`runs/r89v-symdiff.txt`).
- Fixture inside the tree: sha256 `623c25cc…`; `py_compile` + `ast`
  clean (`runs/pycompile.txt`).
- Commit shape `+1776/−3` (fixture +1561/−3; the 3 deletions are the
  shared-line splices — mutex list, mode select, receipt suffix — the
  same convention as r86–r88).
- The worktree moved **only** by the pre-existing pyc; the tracked
  fixture blob equals the frozen copy (both `623c25cc…`).

## 2. Battery — CWD = frozen tree root

Round 1 was launched under `nohup`; the fixture's own `SigIgn` was
`0x1000007` (HUP|INT|QUIT|XFSZ ignored — inherited), so its `g_hup`
legs measured rc −9 at the bound. That is a **launcher artifact, not a
landing change** (§4.3); round 1 receipts are kept as the class's
witness. Round 2 execs every fixture through `runs/runone.py`, which
restores SIGHUP/SIGINT/SIGQUIT to `SIG_DFL` before `execvp` — the
fixture's own `SigIgn` then reads `0x1001000` (only Python's
PIPE + XFSZ).

| run | window (UTC) | launcher | fixture_runs at xw | rc | failures | receipt sha256 |
| --- | --- | --- | --- | --- | --- | --- |
| normal | 07:51:22→24 | runone | — | 0 | `{}` | **`8e8cdad6…`** (canonical pin) |
| r89v1 | 07:51:24→07:52:07 | nohup | 2 | 1 | g_hup(launcher), x_foot | `250f63ee0e0dc7f9d175e61a45846552eac945d4408be8bd6fc5f48a92b5b874` |
| r89v2 | 07:52:07→49 | nohup | 1 | 1 | g_hup(launcher) | `3588c9e8af71d67cd4215fefdebd1044d3286356f66bb5b4b5a43099b62e22ea` |
| v3-orphan | 07:52:49→07:53:35 | nohup (killed parent) | — | 1 | g_hup(launcher) | `e94059cf804a3305f8d92923c305faebf684d8eb1552e8699d169446570661d6` |
| r89v3 | 07:53:36→07:54:13 | runone | 0 (solo) | 1 | **x_top** (busy ratio 0.203) | `50ab4c263b3bd70870ef7cb5d73bf433678c529eb42d18ca5f6c6401a90d00cb` |
| r89v4 | 07:54:14→48 | runone | 1 | 0 | `{}` | `0392484028e4456effcd2b4445ac14e665b6f27bf52342b9130e7c4d6e739b7e` |
| r89v5 | 07:55:02→40 | runone | 0 (solo) | 0 | `{}` | `4b0ea1d1848d7a44176409f8ae9872af6905cc8e359e63fb33a416cc57a084fe` |
| r89v6 | 07:55:40→07:56:14 | runone | 1 | 0 | `{}` | `2405133cdbe5e75a9fe6f52249e19ecf4b248aa1ad210f9bd8fd13098bf27670` |
| r89v7 | 07:56:53→07:57:28 | runone | 1 | 1 | **x_foot** (before=1/during=1, nodes_delta −4) | `8732e5483ac09a01a530799acf61d7b873880b280f18102d00276332ec2bcc53` |
| lockpair-A | 08:02:55→08:03:31 | runone | 0 | 0 | `{}` | `999f4e8d73f1418a5d61d2b50a8d4b5a0f2eeb8e44254a88fb7ae894b7d46293` |
| cot1/cot2/cot3 | 08:01:13→47 | runone ×3 concurrent | 2 (each) | 1/1/1 | x_top ×3; x_foot ×2 | `c94c38e5…` / `209f1e0e…` / `30c597e9…` |

- Round-2 solo guard waited for a foreign-fixture-free window before
  each run (cap 240 s; v5 waited 14 s, v7 waited 38 s). The fixture's
  own `contention.fixture_runs` field is the second witness: v3/v5
  ran with `fixture_runs: 0` + `host_is_quiet: true`; v4/v6/v7 were
  co-tenanted.
- Every run serializes on its own tree's fixed-path family lock
  (§6); the three cotrees have three independent locks by
  construction (F5).

## 3. Law re-derivation (`runs/laws.py`, `runs/laws-matrix.txt`)

`laws.py` is verifier-owned and re-derives every armed r89 law from the
recorded receipt fields (the fixture pops `stdout_raw` for the gate
legs, so the receipt is the arm surface; the live spots independently
re-measure the same laws with verifier code). 106 laws per receipt:

- **Gate (33)**: exact-N completions (`g_own` rc0/term/8, `g_two`
  rc0/4/summed-hist/wall≤1.5, `g_extra`/`g_remote_empty` rc0/4),
  graceful flush (`g_term`/`g_int` rc0 + `{ } ]` terminator + ≥5
  infos), truncating class (`g_kill` −9, `g_hup` −1, `g_usr1` −10,
  invalid JSON), exact-4096 stream samples (+monotone), `-o` ignored
  under `-J`, refusals rc 255 with class, `g_version`, `g_lastwins`
  unbounded, and the **strtol lattice** (007/+3/" 3" bounded-exact;
  2.5/3abc/1e1/huge/−1/abc/0 unbounded; partition law — no "other").
- **Oart (16)**: `o_live` rc0/10 rows/aux superset/`Logging to`/
  `generate_timings`; `o_int` rc0 bytes>0; `o_kill` −9 bytes>0 rows>0
  (+ verifier-added size%4096==0); truncating open; eager creation;
  default `profiler.log`; literal `-` file; `/dev/null` aux-in-cwd;
  dir/empty/proc rc 255 `pwprof_cant_open`.
- **Schema (24)**: own-block order, count step +1, quantum relation
  exact, position step, transport `stopped`-while-cycling, diff 1.0,
  order chain + prev==last-signal, driver `finished`/latency `0/0`,
  id law vs own node, monotonic clock name + window, xrun 0, zero
  followerClock rows, follower-less sink 0 blocks, window-local count
  contiguity, count persistence (c2>c1), suspension (hook fired,
  pre>0, **after==0**), graceful TERM rc0.
- **Xw (13)**: pactl-vs-native module mismatch, blank-line guarded
  parse, 1-Client footprint, concurrent captures clean, overlapping
  blocks dict-identical (BLOCKED when zero overlap), pw-top band,
  Profiler refusal, SIGPIPE −13, `/dev/full` silent.
- **Custody (10)**: entries present, leg census, failures-empty,
  coverage_blocked-empty, unloads rc0, sinks gone, own nodes gone,
  tools.

Result: **author A1/A2 = 106/106 PASS each**; over the 14 receipts the
20 red cells are exactly the three arm classes plus their entry-level
cells. No law regressed in any red receipt — the reds are arm
lotteries, not measurement failures.

## 4. The three arm classes (mechanisms measured)

### 4.1 `x_top` — own-row selection + ratio band (4 wave reds + 1 solo)
- **Solo false-FAIL**: v3 (07:53:36Z, `fixture_runs 0`, `host_is_quiet
  true`, loadavg 75) — `top 2.2/0.6us vs profiler 3.43/2.96us`; the
  busy ratio **0.203 < 0.25** fails while every profiler law holds
  (own blocks 40, all invariants green).
- **Transient-row false-FAIL**: cot1/cot2 and the **reviewer's r89r1**
  picked a real-state row with `0.0us/0.0us` (`status != "C"` and
  `wait_us is not None` both accept `0.0`) → forced ratio 0.
- **Band-edge wait ratio**: cot3 `top 3.9/5.1us vs profiler
  19.739/5.26us` → wait ratio 0.198.
- Rate: **5/17 wave receipts** where measurable (v3 solo; cot1/cot2/
  cot3; r89r1); 1/5 fully-solo receipts. The two timing windows are
  not the same quantity (pw-top's last real frame vs the profiler's
  whole-window median), and the busy cells are 0.1 µs-quantized
  values in the 1–6 µs band.
- Labrat (relayed, §7): non-C `0.0/0.0` rows occur in ~40/40 archived
  `pw-top -b` captures on this host (majority of frames), so the
  selection path is genuinely exposed, not a rare transient.

### 4.2 `x_foot` — global census arms (4 wave reds; 2/3 deliberate 3-way)
- The arm counts **all** `pw-profiler` clients (`application.name`) and
  **all** graph nodes in a 0.35 s window. Under co-tenancy a sibling
  run's foot profiler is inside the window: v1 `before=1/during=1`
  (foreign alive at c0, left before c1), v7 same + `nodes_delta −4`
  (foreign node churn), cot2 `during=4`, cot3 `during=3`.
- It passes **by luck** when the foreign client persists through the
  window (v4/v6 `before=1/during=2`), so the arm is a race, not a
  measurement. The intended claim (footprint = own 1 Client) is not
  measurable by a global census under the wave's actual conditions.

### 4.3 `g_hup` — launcher signal-disposition inheritance (6 wave reds)
- `subprocess.Popen` does **not** reset inherited `SIG_IGN` dispositions
  (CPython's `restore_signals` covers only PIPE/XFSZ), and `exec`
  preserves `SIG_IGN`; `nohup`/bash-async launch trees therefore give
  every `pw-profiler` child `SIGHUP=SIG_IGN`, so the 0.8 s HUP is
  discarded and the leg runs to the harness bound → rc −9.
- Evidence: `/proc/<pid>/status` `SigIgn` bitmaps (`runs/
  sigign-evidence.txt`): nohup battery `0x1000007` (HUP|INT|QUIT|XFSZ);
  reviewer's `run_replay.sh` python `0x1001007`; runone-corrected
  fixture `0x1001000` (HUP clear). Receipts: v1/v2/orphan rc −9 with
  `alive_at_sig true` and 376 832–524 288 B streamed; **the reviewer's
  r89r1–r89r3 all rc −9** (its own harness is nohup-based); the
  author's A1/A2 and all runone runs rc −1 at 0.81–0.82 s with 28 672 B.
- Controlled A/B (spot S1, 3 reps each): `HUP=SIG_DFL` → rc −1 ×3
  (0.81 s); `HUP=SIG_IGN` → rc −9 ×3 (4.01 s bound). The underlying
  pw-profiler law is unchanged; the arm measures the launcher.
- The wave's own replay convention (nohup + background) trips this
  class 6/6 times — the fix belongs in the harness (`preexec_fn`
  resetting HUP/INT/QUIT to SIG_DFL), as `runone.py` demonstrates.

## 5. Independent live spots (`spot/spot.py`, own namespace `r89v_<pid>`)

All shapes measured with verifier-owned code on a private null sink +
tagged `pw-play` follower (`r89vrole<pid>`), unloaded by verified
`fname=` index, no `set-default-*`. Final run: `linked true`,
`unload_rc 0`, `own_nodes_after []`, `failures []`.

- **S1 HUP A/B** (above): rc −1 ×3 vs rc −9 ×3 — the g_hup mechanism.
- **S2 strtol lattice, new discriminators**: `" 10"`→**10 bounded**,
  `"10 "`→**unbounded**, `"+10"`→**10 bounded**, `"0x10"`→**unbounded**,
  `"007"`→**7 bounded**, `"2.5"`→unbounded. `atoi` would have parsed
  `"10 "`→10, `"0x10"`→0, `"2.5"`→2 — the full-string strtol model is
  confirmed and sharpened.
- **S3 `-o` incremental ladder** (own driver 2048/48k, 23.4 Hz):
  SIGKILL at 1/2/3 s → **24 576 / 49 152 / 73 728 B, rows 23/46/69,
  all size%4096==0**; graceful TERM at 1.5 s → rc 0, 38 828 B (the
  flush writes the remainder — not a 4096 multiple). Linear
  24 576 B/s = 6 blocks/s = 23 rows/s. The scout's "0-byte husk"
  claim is dead; the boundary's falsification reproduces exactly, and
  the fixture's armed 2.0 s value **49 152 B/46 rows is 14/14 fixture
  receipts (incl. the 3-way co-tenanted cot runs) + 1/1 spot run** —
  it is the one-own-driver graph rate, not a lucky sample. (The
  growth rate is graph-rate-dependent in general: the first spot run,
  whose follower had not linked, grew at a foreign-driver-only rate —
  see F6.)
- **S4 exact-4096 blocks**: cumulative samples 4096 / 8192 / 16 384 at
  0.3/0.6/0.9 s, TERM rc 0 + terminator.
- **S5 exact-N**: `-J -n 8` → rc 0, exactly 8 infos, terminator, 0.31 s.
- **S6 Profiler introspection**: `pw-cli info 5` / `enum-params 5 Props`
  → rc 0 + `unsupported type PipeWire:Interface:Profiler` ×2.
- **S7 closed reader** → rc −13.
- **S8 suspension**: follower SIGKILLed at 0.9 s inside `-n 0` →
  own blocks **21 before, 0 after** (600 ms margin), run survives to
  TERM rc 0 — the author's `s_suspend` 21→0 independently reproduced
  by a different code path (author's receipts: 21/21/0 too).

## 6. Fixed-path family lock

- Static: `path = ROOT / "live" / "measure_audio-pwprof-r89.lock"`,
  no env/tempfile input (committed fixture, line 29509).
- Executed (`runs/lockprobe.py`): same-path exclusion (second
  nonblocking acquire fails while held; reacquires after release);
  child-holder blocks the parent; **cross-TMPDIR independence** — with
  `TMPDIR=/tmp/…` the lock still lands at `ROOT/live/…` and nothing
  lands under the foreign TMPDIR.
- Executed serialization pair in the frozen tree: fixture A (runone)
  held the lock; `lockprobe.py hold 2` launched 3 s later **waited
  33.9 s** (wall 35.866 s) and acquired only after A exited — lock
  content flipped `pid=2058126` → `pid=2059983` (`runs/lockpair.txt`).
- Cross-materialization (inherited F5): two ROOTs each with their own
  `live/measure_audio-pwprof-r89.lock` can hold simultaneously, and
  the three cotrees ran genuinely concurrently — the lock is
  tree-relative, the same r84–r88 F1 residual (not a new regression;
  it is what makes the co-tenancy stress real).

## 7. Labrat (single permitted probe; advisory)

Dispatched once, read-only, one falsifiable hypothesis: *non-C
`0.0us/0.0us` rows occur in ≥1 of 20 `pw-top -b -n 3` invocations on
this host*. Substrate limitation (disclosed): the labrat environment
had read/search tools only — **no exec, no writes** — so it ran the
parse over archived `pw-top -b` captures in `corpus/live/` (same host,
PipeWire 1.6.8) rather than fresh invocations. Verdict **CONFIRMED**:
non-C 0.0/0.0 rows appear in ~40/40 archived captures (majority of
frames; `I`-state and `R`-state quant=0 rows, e.g. `R 142 0 0 0.0us
0.0us … r89b_ns`), far above 1-in-20. Relayed verbatim to
`corpus/live/r89-verifier/labrat/labrat-report.md` (no artifacts were
created by the labrat). This is the mechanism behind the reviewer's
r89r1 and cot1/cot2 `x_top` reds; the verifier's own receipts are the
live witnesses.

## 8. Custody, post-state, seat hygiene

- 14/14 receipts: `unloads[*].exit_code == 0`, `sinks_gone` all-true,
  `own_nodes_after: []`, `foreign_r89a_nodes` recorded (sibling sinks
  seen, never trusted).
- Post-state (`runs/post-state.txt`): zero `r89v_*`/`r89a_*` nodes,
  zero own modules/sinks, no owned processes, defaults unchanged
  (`…SPDIF__sink.29` / `…Line__source.29` — identical to pre-state).
- Seat hygiene (disclosed): the first spot run had a missing `cwd` on
  its `-o` legs and wrote two scratch artifacts into the lane root
  (`k` 53 248 B/50 rows, `g` 22 665 B/21 rows); both were measured,
  moved to `spot/stray-*.bin`, and the lane root is clean. The first
  spot run also failed to unload its sink (index-parser bug, fixed);
  the leftover module was unloaded by verified `sink_name=` index
  (`spot/stray-artifacts.txt`). Zero tracked files were touched.
- Tracked dirty set before and after this seat's window: only
  `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`
  (pre-existing at entry).

## 9. Findings ledger

1. **F1 — `x_top` arm lottery (gate-blocking).** Fails solo (v3) and
   co-tenanted (cot1/cot2/cot3, reviewer r89r1); mechanisms: accepted
   `0.0/0.0` real-state rows (labrat-confirmed host rate), band edge
   (0.203 / 0.198). Two independently timed quantities compared across
   different windows; the arm needs a real-value guard (`quant > 0`,
   cells > 0) and a band derived from same-window samples, or should
   degrade to `coverage_blocked` on transient rows.
2. **F2 — `x_foot` global census (gate-blocking under co-tenancy).**
   Counts all pw-profiler clients + all nodes; a sibling run in the
   window breaks it (4/17 wave reds; 2/3 in the deliberate 3-way
   round; passes by luck when the foreign client persists). Measure
   the own footprint instead (own client id/pid, or bracket own
   `application.name` counts around the foot process).
3. **F3 — `g_hup` launcher-disposition inheritance (wave-blocking).**
   The wave's own replay convention (nohup/background) yields
   `SIG_IGN` HUP → rc −9; 6/6 such receipts red; A/B proven. Reset
   HUP/INT/QUIT to `SIG_DFL` in the child (`preexec_fn`) or launch
   replays through a reset wrapper.
4. **F4 — declared leg count (doc).** Commit/report say 47; the
   report's own arithmetic is 51 (27+12+4+8); receipts carry **52**
   (27/12/4/9). Counts are the receipts'.
5. **F5 — lock tree-relative (inherited residual, not new).**
   Cross-materialization → two locks held; cotrees ran concurrently
   (the r84–r88 F1). No regression; the fold (fixed path, not TMPDIR)
   holds.
6. **F6 — `o_kill` 49 152 B is the own-driver graph rate (record).**
   14/14 fixture receipts (incl. 3-way co-tenanted) + 1/1 spot run at
   2.0 s = 49 152 B/46 rows; the spot ladder shows the mechanism
   (24 576 B/s = 6 blocks/s = 23 rows/s at 2048/48k). Growth is
   graph-rate-dependent in general (the first spot run, follower not
   linked, grew at a foreign-only rate: 53 248 B/50 rows at 3 s), so
   the armed law (>0 bytes, >0 rows, 4096-multiple) is the portable
   claim and the encoded 49 152 B is this host's own-driver value.
7. **F7 — `x_conc` byte-identity is not stable (recorded, unarmed).**
   v7 6506 vs 6510 B (author's runs happened to be byte-equal); the
   armed dict-identity of overlapping blocks held 7/7 receipts (and
   3/3 co-tenanted) — the author's boundary-driven handling is correct.
8. **F8 — exact-N is summed across foreign seats' drivers too
   (record).** v2/orphan `g_own`/`g_two` driver lists include sibling
   fixture sinks (`r89a_ns_1760907`, `r89a_ns_1759418`); the exact-N
   arm held in every receipt (8/8, 4/4), and the per-driver split
   (2+2) only appears solo.

## 10. Evidence inventory

All under `corpus/live/r89-verifier/`; `manifest.json`
(sha256 `093b9af354f638b9f40efd41d467b1ae5935bee6fef45fe87d5e069601e1d7b8`)
lists **76 files / 14 954 380 B** and `manifest.sha256` (sha256
`64bbab70e53a501b4928ccebc5e09dea6a39ee56800628b4941c7414ce218aae`)
covers every one of them plus manifest.json's own final sha —
`sha256sum -c manifest.sha256` → **77/77 OK**. The regenerable
snapshot trees `tree/` and `runs/cotree{1,2,3}/` are excluded by
convention (`corpus/.gitignore` `live/**/*tree*/`).

- `runs/`: 14 pinned receipts (`author-A1/A2`, `r89v1..v7`,
  `r89v3-orphan`, `lockpair-A`, `cot1..3`) + `normal.receipt.json`,
  `receipt-shas.txt`, `laws.py`, `laws-all.txt` (1484 cells),
  `laws-matrix.txt`, `matrix.py`, `runone.py`, `battery-v5.sh`,
  `battery-v5b.sh`, `cotenancy.sh`, `lockprobe.py`, `lockprobe.json`,
  `lockpair.txt`, `lockpair-B.time`, `lockpair-A.stdout.json`,
  `battery.log`, `battery{,2}.out.log`, `cotenancy.out.log`,
  `pre-state.txt`, `pre-census.txt`, `post-state.txt`,
  `sigign-evidence.txt`, `wave-census.txt`, `tree-tar.sha256`,
  `fixture-sha.txt`, `pycompile.txt`, `r89v-symdiff.txt`,
  `r89v-ls-tree.txt`, `make_manifest.py`, `laws-author-v12.txt`,
  `cot*.stdout.json`, `*.stderr.log`.
- `spot/`: `spot.py`, `spot-results.json` (final clean run),
  `spot2.out.log`, `spot.out.log` (first run), `spot-log.txt`,
  `stray-artifacts.txt`, `stray-k-3s.bin`, `stray-g-term.bin`.
- `labrat/labrat-report.md` (relayed advisory).
- Wave witnesses (other seats, referenced not copied): reviewer
  receipts `corpus/live/r89-reviewer/tree/corpus/live/runs/
  20261016T0752{18,58}…` and `20261016T075501656013Z-pwprof-r89/`
  (sha `51d57097…`, `493cde4a…`, `9f4a1026…`); author receipts
  `corpus/live/runs/20261016T0747{33,48}…-pwprof-r89/`.

## 11. Blockers

None for this seat. The landing is not a reproducible green gate until
F1–F3 are hardened; F4 is a report fix. Every law the round encodes is
independently re-derived green — the failures are confined to the
verdict arms under the wave's actual (co-tenanted, nohup-launched)
conditions.
