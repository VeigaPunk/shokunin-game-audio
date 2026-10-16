# r89 FOLDFIX — the boundary-surviving gate-fail fixes folded into `--probe-pwprof-r89`

**Seat** r89-foldfix (executor) · **host** devin/plazir27 · **repo**
`/home/vgpnk/Projects/shokunin/audio-shokunin` · **base** HEAD `5a632a4f`
("r87+r88 fold: land pwbind/btwit defect fixes (+310/-112)") — the tree was
**clean** at seat entry: the task card's "uncommitted r89 semantic fix" did
not exist; the r87+r88 fold was already committed and its diff touches no
r89 line (grep-verified). Every r89 fix below was authored by this seat
from the r89 author/critic/reviewer/verifier reports. **Scope**:
`corpus/fixtures/measure_audio.py` only (+ this report + receipts under
`corpus/live/r89-foldfix/`). **Zero commits, zero pushes.**

Fixture sha: `d2784585…` (committed `5a632a4f`) →
**`d4b2e088bbfaa71f7cb19123c36b1646681009237f5d6049686789c157171e65`**
(post-fold, 32 369 lines; `git diff` **+135/−26**). `python3 -m py_compile`
clean. All evidence shas in `corpus/live/r89-foldfix/RECEIPTS.txt`; the diff
itself at `corpus/live/r89-foldfix/foldfix.diff`.

## Items applied

| # | finding (sources) | change (post-fold lines) | live evidence |
|---|---|---|---|
| 1 | **`g_hup` launcher-disposition inheritance** (verifier §4.3 + F3, reviewer F1, critic F2 — 3-seat, 6/6 nohup reds rc −9 at bound): `restore_signals` covers only PIPE/XFSZ; `SIG_IGN` survives `exec` | new `_pwprof_r89_sigreset` `preexec_fn` (:29531) resets HUP/INT/QUIT/TERM/USR1 to `SIG_DFL` in every arm child — wired into `_pwprof_r89_stream`'s Popen (:29571, covers all streamed legs + pactl/pw-cli/pw-top/pw-dump spawns), `_pwprof_r89_play` (:29870), and the 6 direct pw-profiler spawns in xw (:30789 foot, :30828/:30833 x_conc, :30872 x_top prof, :30962 x_sigpipe, :30976 x_devfull). The arm now sees the host default, never the launcher | `g_hup` **rc −1** at 0.816/0.817/0.821/0.823 s in **4/4 nohup-launched** receipts — the exact context that was 6/6 red pre-fix (receipts: `…T084201`, `…T084804`, tree2 `…T084609`, tree3 `…T084624`) |
| 2 | **`x_foot` global-census race** (verifier F2, critic F3 17.6%/window, reviewer F8e): exact global `pw-profiler` client count + global `nodes_delta` fails on foreign churn, passes by luck | arm is now **own-scoped**: Client objects carrying `application.process.id == foot.pid` must be exactly 1; objects with props `client.id` owned by that client must be 0 (:30753–30817). Global `pwprof_before/during/clients_added/nodes_delta` kept as unarmed context. Named coverage classes (:31002–31015): census unreadable → `coverage_blocked`; foot run rc≠0 → `coverage_blocked`; own client never enumerated (connect slower than the 0.35 s bracket) → `coverage_blocked` | measured green **3×**: own `[210]` (solo), `[131]` while a foreign run's profiler client sat in-window (`pwprof_during: 2`, `fixture_runs: 1`), `[223]` while foreign `blender`+`pw-profiler` clients were added mid-window. 1× honest `coverage_blocked` (own client slower than the bracket — the OLD arm would have false-failed `0 != 0+1` on that receipt) |
| 3 | **`x_top` zero-row + band lottery** (reviewer F2, verifier F1+F4, critic F9): non-C `quant 0 / 0.0us` refresh rows (~40/40 captures on this host) accepted → forced ratio 0; single instantaneous frame cell vs whole-window profiler median is a band-edge lottery (~15 % co-tenancy, realized live this fold: tree3 cot1 RED `7.1us vs 1.47us` on a REAL row) | two-part honest fix, **band 0.25–4.0 unchanged**: (a) row selection requires `quant > 0` AND nonzero µs cells, scanning all frames newest→oldest; all-transient → `coverage_blocked` (:30883–30911); (b) the armed cells are the **pw-top median over the real-cycle rows of the capture** — median-vs-median, the verifier's "band derived from same-window samples" — not one noisy frame (:30912–30922). Leg records `real_own_rows`, `top_wait_med`, `top_busy_med`, `transient_own_rows` (:30928–30938); verdict arms the medians (:31038–31060) | transient guard fired live: tree2 cot2 `transient_own_rows: 3`, 0 real → **`coverage_blocked`** (no false-FAIL, no false-PASS); final lane run 2 transient skipped + 1 real → green. Median arm: tree3 cot2 `top-med 7.2/7.2 vs prof 7.12/6.87` green on the same elevated-load class that redded cot1 under the single-row arm. The pre-fix cot1 red receipt is kept as the mechanism witness |
| 4 | **52-leg count correction** (verifier F4, reviewer F3, critic F7, scribe ADJ-1): commit/report say 47, receipts carry 52 (27/12/4/9 — `x_link` uncounted) | the family header comment now records the true census (:29475–29478); every post-fold receipt confirms **52 leg keys** — the receipts are the record | all 4 post-fold receipts: 27/12/4/9 = 52 |

Explicitly **not** weakened: the 0.25–4.0 ratio band, the rc arms
(`rc == −1` still required for `g_hup`), the one-Client footprint claim,
every schema/oart/gate arm. Confounds are named `coverage_blocked`
classes, never silent passes or re-aimed thresholds.

## Legs re-run (all on the affected legs, bounded)

Five full `--probe-pwprof-r89` batteries were run (each exercises all 52
legs including `g_hup`, `x_foot`, `x_top`), all launched **under `nohup`**
— the wave's own failing launcher context — with
`TMPDIR=/home/vgpnk/Projects/shokunin/tmp`, `PYTHONDONTWRITEBYTECODE=1`:

| receipt | bytes | launcher / co-tenancy | result |
|---|---|---|---|
| `20261016T084201819411Z` (lane root) | pre-median | nohup, solo | **green** — `g_hup` rc −1 @0.816; `x_foot` own `[210]`; `x_top` real row green |
| `tree2/…T084235560485Z` | pre-median | nohup, tail-overlap | **green** |
| `tree2/…T084333362366Z` + `tree3/…T084349220052Z` | pre-median | nohup ×2 concurrent | tree2 **green** (`x_foot` own `[131]` under `fixture_runs: 1`); tree3 **red** `x_top` band-edge on a real row — the single-frame estimator's live falsification, motive for the median arm |
| `tree2/…T084609262240Z` + `tree3/…T084624699320Z` | **final** | nohup ×2 concurrent | **both green** — `g_hup` rc −1 @0.817/0.823; `x_foot` own `[131]`/`[223]` under foreign churn incl. a foreign `blender` client added mid-window; `x_top` med-green (tree3 7.2/7.2 vs 7.12/6.87) + honest `coverage_blocked` (tree2, 3 transient rows) |
| `20261016T084804070899Z` (lane root) | **final** | nohup, solo | **green** — 52 legs, `g_hup` rc −1 @0.821/126 976 B; `x_top` med green (2 transient skipped, 1 real); `x_foot` `coverage_blocked` (own Client registered after the 0.35 s bracket — `pwprof_during: 0`, the old global arm would have false-failed) |

Census on final bytes: **3/3 runs `failures: {}`, 52 legs each**
(27/12/4/9); 2 `coverage_blocked` cells total, both named classes above;
zero failures in every entry. Custody: all `unloads` rc 0 with
`sink_name`-verified indices, `sinks_gone` all-true, `own_nodes_after: []`;
post-battery pw-dump shows **0 `r89a_*`, 0 `r89f_*` objects, 0 pw-profiler
clients**; no owned processes; defaults never touched (no `set-default-*`
call exists in the family).

## Constraints honored

- Seat-owned PipeWire names: probe-internal `r89a_<pid>` only (the `r89f_`
  prefix reservation went unused — no manual objects needed).
- Module unloads: all through the fixture's `sink_name=`-verified index
  path (`verified_index`/`captured` match in every receipt).
- No `pactl set-default-sink/source` anywhere.
- `TMPDIR=/home/vgpnk/Projects/shokunin/tmp` on every run.
- Lock honored: the lane run serialized on
  `corpus/live/measure_audio-pwprof-r89.lock`; co-tenancy runs used
  independent ROOTs under `corpus/live/r89-foldfix/tree{2,3}/` — the
  tree-relative residual (r86→r89 F-class) is what makes the co-tenancy
  evidence real, disclosed as inherited.

## Disclosures / hygiene

- The tracked `__pycache__/measure_audio.cpython-314.pyc` was already `M`
  at seat entry (pre-existing dirt, noted by all four r89 seats); one
  `py_compile` refreshed it — still dirty, different bytes. No other
  tracked file touched.
- Scratch trees `corpus/live/r89-foldfix/tree{2,3}/` contain only the two
  fixture files + their own `live/runs/` receipts — gitignored live area.
- One bounded read-only `pw-profiler -J -n 30` was spawned by hand to
  verify `application.process.id` on Client objects; it hit the family's
  documented idle-graph hang and was `pkill`'d — no graph objects created
  (the dump it produced is `/tmp/r89f_dump.json`, outside the repo).
- `nohup` redirection for two background launches failed twice inside this
  seat's shell wrapper (`No such file or directory` on the second `&`
  command); relaunched singly — disclosed, no probe impact.

## Remaining risks / blockers

1. **None blocking.** All three named arm classes measured green under the
   wave's own failing contexts (nohup launcher; concurrent same-family
   co-tenancy).
2. `x_top` can still legitimately red on a real sustained disagreement —
   that is the arm working, not the lottery; the estimator fix removes the
   single-sample noise, not the law.
3. `x_foot`'s `coverage_blocked` path fires when the own Client registers
   slower than the 0.35 s bracket (observed 1/5 runs at loadavg ~55) —
   honest unmeasured, never a pass; a later seat may widen the bracket or
   retry once.
4. The tree-relative family lock residual (r86→r89) is unchanged — runs
   from different ROOTs do not serialize; that is the inherited queue,
   not this fold's scope.
5. No resume mutation attempted; no commit, no push — the orchestrator
   commits.

Seat stop — files changed by THIS seat:
`corpus/fixtures/measure_audio.py` (+135/−26),
`reports/round-89/r89-foldfix.md`, evidence under
`corpus/live/r89-foldfix/` (receipt copies, `foldfix.diff`,
`fixture-sha256.txt`, `RECEIPTS.txt`, scratch trees + run logs).
The canonical Rust runtime remains the sole judge.
