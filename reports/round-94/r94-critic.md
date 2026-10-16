# r94 critic — attack on the committed SoX_ng effect/DSP landing

Seat: **critic** (leaf). Repo `/home/vgpnk/Projects/shokunin/audio-shokunin`,
target **HEAD `aaf56d30`** ("Merge branch 'wt-r94'"); r94 branch tip
**`f46dce00`**. Frozen verification tree
`corpus/live/r94-critic/tree/` = `git archive aaf56d30` (56 322 entries).
Host `plazir27`, my window **2026-10-16 08:55:57Z → 08:57:29Z** (host local
UTC−3). Toolchain unchanged and re-read in every receipt: `sox` SoX_ng
v14.8.0.1, `/usr/bin/sox` sha256 `646d899b53c1…`, Python 3.14.7, numpy 2.5.3.

**Seat discipline.** Zero tracked writes, zero commits. Everything I wrote is
under `corpus/live/r94-critic/` (untracked). `TMPDIR=/home/vgpnk/Projects/shokunin/tmp`.
No `pactl set-default-*` (my only `pactl` calls are read-only
`list short …`/`get-default-*`); no PipeWire object created — 0 `r94a_`/`r94c_`
sinks/sources/modules after the runs, defaults untouched
(`…HiFi__SPDIF__sink.29` / `…HiFi__Line__source.29`). The committed family
takes **no** `r94c_` name (see F5).

**Environment note (not mine).** The live worktree file is not trustworthy
right now: `git status` shows `UU corpus/fixtures/measure_audio.py` plus
staged `A corpus/fixtures/r95jack.c`, `A reports/round-95/r95-author.md` — an
in-progress sibling merge. Every r94 claim below is re-derived from the frozen
archive, never from that worktree. HEAD advanced during my window
(`aaf56d30` → `ffeb5155` r95 author, +1805/−3 on the same shared file →
`021bde86` r89 adjudicate); the live file now hashes `dca4dc9b…`. All claims
here are anchored to the frozen `aaf56d30` archive.

---

## 0. Verdict

**PASS-with-findings.** No blocker. On committed bytes the landing is
insertion-only, 8 entries / 150 legs, and green — twice by the author and
twice by me — with every boundary correction encoded at its corrected value
(the falsified −130 dB form is nowhere armed). Eight findings: six
report/one-line-code defects (F1–F4, F6, F8) and two tradeoffs for the
canonical judge (F5, F7). **F1 (a false statement about on-disk evidence),
F2 (the report's implementation sha is not the committed file's sha) and
F8 (the PipeWire census negative control is fail-open, and that path is
reachable on this host today) should be corrected before the round seals.**

---

## 1. Claims re-derived on committed bytes (all pass)

| claim | how re-derived | result |
| --- | --- | --- |
| 8 entries / 150 legs | my runs B/F receipts, per-entry counts | 45+15+22+12+20+11+12+13 = **150** ✓ |
| green ×2 | author receipts (wt-r94) + my own runs | `failures {}`, `coverage_blocked []` in all 8 ✓ |
| +2231/−3 insertion-only | `git diff 5a632a4f f46dce00` | 2231/3; the 3 deletions are exactly the mutex / `mode` / `suffix` splice lines; 6 hunks; **0 top-level name collisions** with the pre-r94 file (777 pre / 50 added, ∩ = ∅) ✓ |
| HEAD's r94 block == branch block | the two add-line sets (`5a632a4f→f46dce00` and `5755be5b→aaf56d30`) | both hash `3bf6b259…`, 2231 lines, 0 diff — the merge is a clean union of r94 + r89 foldfix ✓ |
| 59 sha witnesses / 9 stimuli / 29 metrics | my run B receipt | 59/59 `sha_match true`, 9/9 stimulus shas equal the scout's `prep.json`, 29/29 metric comparisons ✓ (F6 for the "7") |
| witness absent ⇒ coverage_blocked, never a pass | run C (scout dir hidden) | green, `failures {}`, **146** cb rows (72 stimulus + 59 sha + 15 metric) ✓ |
| arms are live, not vacuous | run D (witness tampered: 1 sha + 1 metric), run E (2 laws mutated in a copy) | D rc 1 with 3 failures (2 sha, 1 metric); E rc 1 with exactly the two mutated laws ✓ |
| 102 arm sites / ~140 evaluations | instrumented copy (run F) logging every `_sox_r94_arm` | 102 sites ✓, **144** evaluations ✓, 0 non-ok ✓, 120/150 legs carry ≥1 arm |
| boundary corrections at corrected values | my run B vs `r94-boundary.md` §2 | 23k default/`-h`/`-v`/`-u` band@21.1k **−104.385795**, peak −84.288399, shas `8f842d06`/`51aa41a1` (≡ boundary ≤1.4e-4 dB); 20k default **−129.587952** (< −120 arm); `-q` **−6.289062**; `-a` 20k **+0.000645**, 21.1k **−142.046731**; `-l` 20k **−23.020257**; `-q -a` rc 1 + exact message ✓ |
| anti-re-arm guard is the *min* over the five 23 kHz legs | code read + receipt | `worst23 = min(band23) > −110` — "every 23 kHz leg" is literally what is armed (not just the max) ✓ |
| reproducibility | run B vs run F (same committed bytes) | exactly **1** diff outside the volatile set — the disclosed dither-sensitive `railed_G_gain12_default` ✓ |
| author's own drift claim | author green #1 vs #2, masked walk | exactly **1** residual field outside the 7 volatile legs: that guard count (14987→15097) — exactly as disclosed ✓ |
| hygiene | family grep + live census | 0 `load-module`/`unload-module`/`set-default`/`pw-cli`/`-d`/`-p`/`play`/`rec`; 0 `r94a_`/`r94c_` PW objects in my window; defaults untouched; triple-bounded spawn + `start_new_session`/`killpg`/`RLIMIT_CORE=0` ✓ (but the census negative control is fail-open — F8) |
| no duplicate authority | pre-r94 file (5a632a4f) | sox appears only as `-V6 … -n stat` decoder/detector; no effect row existed ✓ |
| author evidence | `sha256sum -c manifest.sha256` (r94-author) | **217/217 OK**; both named receipts present, 351545 / 351541 B — the claimed 4-byte delta ✓ |

My runs (all from `corpus/live/r94-critic/tree/`, receipts in its
`corpus/live/runs/`):

| run | what | rc | result |
| --- | --- | --- | --- |
| B `…085557637310Z` | committed bytes, witness present | 0 | `failures {}`, cb 0, 150 legs — **green on committed bytes** |
| C `…085633708378Z` | witness hidden | 0 | `failures {}`, cb 146 — degradation is a record, not a pass |
| D `…085647046931Z` | witness tampered | 1 | 3 failures (2 sha + 1 metric) — witnesses fail closed |
| E `…085654710454Z` | 2 laws mutated | 1 | exactly the 2 mutated laws fail |
| F `…085729269017Z` | instrumented arms | 0 | green, 144 arm evaluations |

---

## 2. Findings

### F1 — false statement about on-disk evidence (fix the report)
`r94-author.md` §Remaining risks: *"Five dev/iteration receipts remain under
`corpus/live/runs/` (pre-final bytes, **all with real `failures`** …)"*.
Counterexample, from the author's own worktree: `20261016T085137302309Z` and
`20261016T085151245387Z` both have `failures: {}` (green, 150 legs, cb 0).
A union-masked walk of `…085151…` vs the named green `…085212…` finds **3**
diffs, all in `sox_dither_stat_r94_probe`: the `ffmpeg_ebur128_short_mono`
recording shape (`integrated_line` / `text_tail`) and the dither-sensitive
guard count — i.e. those two greens ran on **content-identical** bytes with a
pre-final recording shape. The true green count is **4**, not 2.

- Impacted: evidence provenance (a verifier counting greens gets 4).
- Smallest safe correction: "three of the five dev passes carry real failures
  (32/20/13); `…085137…` and `…085151…` are green pre-final-shape passes on
  content-identical bytes".

### F2 — the report's implementation sha is not the committed file's sha (fix the report)
`r94-author.md` §Evidence: *"Implementation sha256 … `84298dcc…`"*. That is the
**branch** file (`f46dce00:corpus/fixtures/measure_audio.py`, identical to
`r94-author/measure_audio.py.final`). **HEAD `aaf56d30` carries `4808c4cf…`**
= branch file + r89 foldfix (+135/−26, clean union; the r94 block itself is
byte-identical, §1). Hashing the committed artifact does not yield the sha the
report prints.

- Impacted: provenance naming. I closed the substance by re-running the
  committed bytes (run B green), but the report as written points at the wrong
  bytes.
- Smallest safe correction: state both — "block/branch file `84298dcc…`; HEAD
  file `4808c4cf…` (r89 foldfix union, r94 block byte-identical)".

### F3 — one measured row is recorded-only and undisclosed
`alias_20k_v` (20 kHz stimulus, `rate -v 44100`) is in the receipt (band@20 kHz
**−0.0007 dB**, band@21.1 kHz −118.273, sha `7e11b7c9…`) but no arm references
it (instrumented run F: it never enters the arm log). The report's
§Remaining risks presents the `-h`/`-r` headroom pair as "the one scout row
left out".

- Impacted: coverage claim (the scout's "`-v` flat at 20 kHz" row is measured,
  correct, and silently unarmed).
- Smallest safe correction: arm `abs(band_20000hz_db) < 1.5` (passes today), or
  list it with the recorded-only rows.

### F4 — one recorded field leaks the run-tree path (one-line fix)
`_sox_r94_spawn` computes `error_class, error_hit = _sox_r94_errclass(errt)`
from the **un-normalized** stderr, while `stderr`/`stderr_text` pass through
`_sox_r94_norm` (which replaces `str(ROOT)`). So
`det_copy_token_not_an_effect.reps[0].error_hit` embeds the absolute scratch
path, and a re-run from another tree/clone produces a spurious receipt diff
(run B vs author green #1: exactly this field plus the disclosed guard count).

- Impacted: "cross-run diff is a clean signal" holds only within one tree root.
- Smallest safe correction: `cls, hit = _sox_r94_errclass(_sox_r94_norm(errt))`.

### F5 — the committed family is not seat-parameterized (tradeoff)
`SOX_R94_TAG = f"r94a_{os.getpid()}"` and
`_sox_r94_scratch() = ROOT/live/r94-author/scratch` are hardcoded to the
**author's** namespace. Any other seat running the committed probe takes the
author's names (my run's census recorded `own_prefix: r94a_3129948`) and writes
its 211 products into the author's scratch path. The fixed-path lock is
per-tree, so same-tree runs serialize and different trees cannot collide on
files — the hazard is identity labeling plus clobbering the author's scratch
*if* both run in the same tree.

- Smallest safe correction: read the prefix from an env var with `r94a_` as
  default, or document "author-seat-bound, run from a private tree" in the
  block header.

### F6 — two counting conventions, one un-sourced number (minor)
"7 cross-seat metric witnesses" is the **call-site** count; the receipt carries
**15** metric-witness legs / 29 comparisons (the report's "29/29" is exact).
The block comment's "18 proposed rows" is not re-derivable from the scout
report's own numbering (28 named cells G1…S1, 15 headline claims).

- Smallest safe correction: "15 metric-witness legs (7 call sites)"; drop "18"
  or cite its source.

### F7 — arms looser than the headline numbers (tradeoff)
`det_gain_m6_default` is armed `n_distinct_shas >= 2` (recorded 5/5) and
`det_concurrency_default` `>= 2` (recorded 16/16). A future regression to 2–3
distinct shas stays green while the report's headline says 5/5 and 16/16. The
choice is defensible (the law *is* nondeterminism), but the report should say
which number is armed.

- Smallest safe correction: tighten to `>= 4` / `>= 8` (green today), or record
  the observed count as a soft witness beside the envelope.

### F8 — the PipeWire census negative control is fail-open (strongest counterexample)
`_sox_r94_pw_census()` records `unreadable` when a `pactl` call fails
(`OSError`/`TimeoutExpired`, 12 s cap) and then `continue`s: `own_objects` and
`own_modules` stay `[]` and the totals stay `None`. The entry/exit leak check is
`if own_objects or own_modules: fail` — so with the daemon unreadable the
census **passes vacuously**, having measured nothing, and `unreadable` is
recorded but never armed or routed to `coverage_blocked`. This is the one place
the author's own fail-closed convention ("a witness that cannot be read
degrades to `coverage_blocked`, never to a pass") is not applied.

Live counterexample on this host, from the frozen module (2026-10-16 ~09:02Z,
after my runs — the shared daemon is currently starved and `pactl` times out):

```
import 0.39s  census 60.07s
census: own_prefix r94a_3212094, own_objects [], own_modules [],
        sink_total None, source_total None, module_total None,
        default_sink None, default_source None
unreadable: ['list short sinks', 'list short sources', 'list short modules']
leak check would fail: False
```

Reachability and cost: none of the 7 author receipts nor my 5 runs ever recorded
`unreadable` (0 receipts), so the path was never exercised — but it is reachable
right now. Aggregate exposure: 8 entries × 2 censuses × 5 `pactl` calls =
80 calls; under starvation that is up to ~16 min of timeouts inside a run whose
legs are all triple-bounded (my green runs took ~25 s while the daemon answered).

- Impacted: the family's only leak witness (negative control) — a green
  receipt can carry `own_objects: []` without having looked.
- Smallest safe correction (author's own idiom, keeps the run green while
  making the vacuous pass visible): in `_sox_r94_entry`/`_sox_r94_exit`, route
  `cen.get("unreadable")` to `coverage_blocked` (e.g. `_sox_r94_block(entry,
  f"pw census unreadable: {cen['unreadable']} -> negative control
  unmeasured")`), or arm `not cen.get("unreadable")` if the judge wants
  starvation to be red.

### Checked and clean (not findings)
- 30 of 150 legs carry no direct arm; 29 are inputs to armed aggregates
  (`det_flag_order` / `det_buffer_invariant` / `det_env_invariant` recompute
  `stable` from their variant shas; `guard_not_limiter` from the two `-D` guard
  legs; `fade_curve_table`, `trim_rounding_matrix`, `remix_vol_control`
  likewise) or the disclosed `-G` recorded rows. Only F3's row is genuinely
  unarmed.
- The `-G` guard row is recorded-not-armed exactly as disclosed
  (`guard_default_path_row` arms only `c1 > 0`; the `-D` equality lives in
  `guard_not_limiter`, threshold 32766, 30000/30000, `same_sha: False`).
- Failure text embeds `np.float64(...)` in own-vs-scout messages — cosmetic.
- The block redefines nothing and mutates no global env (it copies
  `os.environ`); the tracked `__pycache__` byte-code was not rewritten by my
  runs (`PYTHONDONTWRITEBYTECODE=1`).

---

## 3. Blocker

**None.** F1/F2/F3/F4/F6/F8 are report or one-line fixes; F5/F7 are tradeoffs
for the canonical judge to accept or reject. The landing itself is green on
committed bytes.

**Co-tenancy note for L0.** After my runs the shared daemon stopped answering
`pactl` (every read-only call I made at 09:00–09:02Z hit the 12 s cap; the
census reproduction above shows it). My runs' own censuses completed normally
~5 minutes earlier. A verifier re-running `--probe-sox-r94` under this
condition will spend up to ~16 min in census timeouts and will get the
fail-open census path (F8) rather than a leak check.

---

## 4. Artifacts (all untracked, under `corpus/live/r94-critic/`)

- `tree/` — frozen `git archive aaf56d30` (3.2 GB, 56 322 entries); its
  `corpus/live/runs/20261016T0855*Z-…0857*Z-sox-r94/` are my five receipts.
- `runB…runF.stdout` — rc + `failures` summary of each run.
- `probes/r94c_family.py` (r94 block from committed bytes + 34 lines of r89
  context), `probes/r94c_mutated.py`, `probes/r94c_instrumented.py`.
- `addlines-branch.txt` / `addlines-merge.txt` (sha `3bf6b259…` both),
  `armsites.txt` (all 102 arm predicates), `armlog.jsonl` (144 evaluations),
  `analyze.py`, `diff2.py`.
- F8's reproduction is one import + one call against the frozen module
  (`PYTHONDONTWRITEBYTECODE=1 python3 -c` → `_sox_r94_pw_census()`), runnable
  again while the daemon stays starved; it wrote no file.

*critic leaf — attacked the committed landing, re-derived its claims on frozen
bytes, mutated and tampered to prove the arms fail closed; not judged, not
committed.*
