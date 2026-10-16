# r89 RE-VERIFY — wave-B gate re-run on committed `5755be5b` (foldfix)

Seat: **re-verifier** (non-author, non-judge). Host `plazir27` (Linux
7.2.3-arch1-3, 32 cores), lane `~/Projects/shokunin/audio-shokunin`,
window **2026-10-16 08:47Z–09:00Z**, loadavg **52–60** (verifier window
was 52–82; shared daemon with sibling seats r90/r91/r94/r95 running
`--probe-wpstate-r90`, `--probe-gstfrz-r91`, `--probe-sox-r94`,
`--probe-jack-r95` in the same lane root — real co-tenancy, named).
Toolchain: PipeWire **1.6.8**, pactl **17.0-98-gb096**, Python **3.14.7**,
numpy 2.5.3. All scratch under `TMPDIR=~/Projects/shokunin/tmp`. Target:
**`5755be5b`** ("r89 foldfix: g_hup/x_foot/x_top + 52-leg census
(+135/−26)"), frozen via `git archive` — never the worktree. **No tracked
writes by this seat, no commits, no pushes, no `set-default-*`; every
seat artifact under `corpus/live/r89-reverify/`.** No subagent was
dispatched (this seat is not a probeParent; the frozen probeParent of the
r89 wave was the prior verifier).

## 0. Verdict

**GATE PASS — re-derived green on the committed bytes.** All four
prior-fail classes re-derive green or land in a **named** coverage class;
**zero FAIL cells** on the committed bytes across the whole law set.

| prior-fail class (verifier baseline) | committed bytes `5755be5b` | verdict |
| --- | --- | --- |
| `g_hup` launcher inheritance (6/6 nohup reds, rc −9) | **8/8 committed receipts rc −1 @ 0.816–0.888 s**, all under the nohup launcher; revert-the-fix mutant reds again rc −9 @ 9.034 s (causal) | **GREEN** |
| `x_foot` global census (4 wave reds + 2/3 co-tenancy) | **2 green** (solo own `[80]`; co-tenanted own `[252]` where the global law false-FAILs) + **6 named `coverage_blocked`** (own client slower than the 0.35 s bracket) + **0 FAIL**; deterministic same-window replay: 12 windows where the pre-fold global law reds (11 named, 1 green) | **GREEN-or-NAMED** |
| `x_top` zero-row/band lottery (5 wave reds) | **4 green** (median-vs-median in band) + **4 named `coverage_blocked`** (transient-only rows: 3 transient / 0 real — the pre-fix single-row arm would have false-FAILed each at ratio 0) + **0 FAIL** | **GREEN-or-NAMED** |
| 52-leg count (doc said 47, arithmetic 51, receipts 52) | **8/8 receipts exactly 27/12/4/9 = 52**; header comment records the true census | **GREEN** |

Census (see §4): committed bytes, **111 laws × 8 receipts = 888 cells:
867 PASS / 0 FAIL / 21 BLOCKED**, every BLOCKED cell a *named* class
(`C03` entry coverage list ×7, `X03` x_foot ×6, `X06`/`R02` x_top ×4+4).
The 106-law baseline subset alone: 848 cells, **831 PASS / 0 FAIL /
17 BLOCKED**. Prior baseline for comparison: 106 laws × 14 receipts =
1484 cells, 1464 PASS / **20 FAIL** / 0 BLOCKED (all 20 reds in the three
arm classes). The fold converts every one of those reds into either a
green arm or a named unmeasured class.

## 1. Frozen tree + provenance (committed bytes only)

- `git archive 5755be5b` at 08:47Z → extracted to
  `corpus/live/r89-reverify/tree/` (gitignored per `corpus/.gitignore:15`
  `live/**/*tree*/`). File count 44 550 = `git ls-tree -r HEAD`
  at extraction time; 0 symlink surprises.
- Fixture inside the tree: sha256
  **`d4b2e088bbfaa71f7cb19123c36b1646681009237f5d6049686789c157171e65`**
  — byte-identical to `git show 5755be5b:corpus/fixtures/measure_audio.py`
  (provenance `runs/PROVENANCE.txt`); `py_compile` rc 0 + `ast` clean.
- Foldfix scope verified: `git diff 5a632a4f 5755be5b` hunks are confined
  to the header census comment, `_pwprof_r89_sigreset` + its wiring in
  `_pwprof_r89_stream`/`_pwprof_r89_play`, and the xw entry (x_foot
  census/spawns, x_top row selection + medians, the verdict block). **No
  gate/oart/schema arm hunk exists** — nothing outside the three named
  classes was weakened.
- **HEAD moved under this seat** (disclosed): the tree was at `5755be5b`
  when archived (08:47Z); during the battery window a sibling seat landed
  the r94 sox family on top (`f46dce00`) and committed a merge
  (`aaf56d30`, "Merge branch 'wt-r94'", 08:53:57Z), then started a second
  merge ("Merge branch 'wt-r95'", in progress at 08:58–09:00Z, `UU
  corpus/fixtures/measure_audio.py`). My grading target stays pinned to
  `5755be5b` by the fixture sha above; the current worktree fixture is a
  different artifact (`git show aaf56d30:…` = `4808c4cf…`) and was never
  graded.
- Canonical **signature gate**: the `normal` receipt (no probe) sha256 is
  **`8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b`**
  — byte-identical to the r85–r88 canonical pin and to the prior
  verifier's pin. The r89 insertion remains receipt-invisible in normal
  mode.

## 2. Battery (8 committed receipts, all `nohup`-launched)

Every probe run was launched under **`nohup`** on purpose — the wave's own
failing launcher context pre-fold.

| receipt | launcher / co-tenancy | census | result |
| --- | --- | --- | --- |
| `normal` | nohup (no probe) | — | rc 0, pin `8e8cdad6…` |
| `r89v1` | nohup, solo | 27/12/4/9 | `failures {}`; g_hup −1 @0.817; x_foot blocked (own client slower than bracket); x_top 3.1/3.7 vs 6.54/3.15 |
| `r89v2` | nohup, solo | 27/12/4/9 | `failures {}`; g_hup −1 @0.816; **x_foot GREEN own `[80]`**; x_top 3.1/2.7 vs 6.51/5.37 |
| `r89v3` | nohup, solo | 27/12/4/9 | `failures {}`; g_hup −1 @0.888; x_foot blocked (global `nodes_delta −1` — the old arm would false-FAIL); x_top 3.5/4.7 vs 10.19/7.57 |
| `cot-r1-t2` / `cot-r1-t3` | nohup ×2 concurrent (independent ROOTs) | 27/12/4/9 | `failures {}`; g_hup −1 @0.820/0.821; x_foot blocked (foreign `pactl`/`pw-cat`/`gst-launch-1.0`/`pw-link` churn in window); x_top blocked (transient-only) |
| `cot-r2-t2` / `cot-r2-t3` | nohup ×2 concurrent | 27/12/4/9 | `failures {}`; g_hup −1 @0.819/0.821; **cot-r2-t2 x_foot GREEN own `[252]` under `pwprof_before=1 / during=1`, foreign `r95jack`/`pactl`/`pw-cat` added, `nodes_delta 2`**; x_top blocked |
| `held-foreign` | nohup, held foreign pw-profiler client in-window | 27/12/4/9 | `failures {}`; g_hup −1 @0.821; x_foot blocked (own client slower than bracket, foreign profiler present); **x_top GREEN 6.4/6.7 vs 5.22/4.55** |

Round boundaries (`runs/battery-solo.log`, `runs/battery-cot.log`),
per-receipt shas in `runs/receipt-shas.txt` / `PROVENANCE.txt`.

## 3. The four classes, re-derived

### 3.1 `g_hup` — green, and causally attributable to the fold

- Committed bytes: **8/8 receipts rc −1**, wall 0.816–0.888 s, stream
  32 768–1 392 640 B — under `nohup`, the launcher that produced 6/6 reds
  (rc −9 at the 9 s bound) in the prior verifier's battery and in the
  reviewer's r89r1–r89r3.
- **Mutation (revert-the-fix)**: `mut-sigreset` = committed bytes with
  `_pwprof_r89_sigreset`'s body replaced by `return None` (single-anchor
  mutation, `runs/mut.py`; diff shown in `runs/`), launched under nohup →
  **g_hup rc −9, wall 9.034 s, 512 000 B** — the pre-fold failure
  signature reproduced exactly. The fixture's own failure list names it.
- Control: the same mutant launched from a HUP-default context → rc −1
  @0.816 (the mutation only bites when HUP is ignored at generation —
  i.e. the fold fixes precisely the launcher-inheritance defect it names,
  and nothing else).
- `SigIgn` reads captured live while the mutant ran: `pw-profiler`
  children with `0x7` (HUP|INT|QUIT ignored — nohup/asynchronous
  launcher) coexisted with children at `0x1000004` (QUIT|XFSZ only —
  HUP default); the two mutant receipts' rc split exactly along those
  two dispositions, re-measuring the inheritance mechanism on this host.

### 3.2 `x_foot` — own-scoped arm green or named; the global lottery is dead

- Committed arm (verified in the frozen bytes, :31002–31015): PASS iff
  exactly one Client carries `application.process.id == foot.pid` and
  that client owns no objects; unreadable census / foot rc ≠ 0 / own
  client not enumerated → **`coverage_blocked`** with a named reason.
- Live: **2 green**, including the decisive co-tenanted window
  `cot-r2-t2` (`before=1 / during=1`, foreign `r95jack` added mid-window,
  `nodes_delta 2`) — the *exact shape* the pre-fold global law reds
  (recorded pre-fix in `r89-verifier/runs/r89v1.receipt.json` and
  `cot2/cot3`). 6 receipts land in the named class (own client slower
  than the 0.35 s bracket), **0 FAIL**.
- **Deterministic same-window replay** (`runs/replay-global.py`,
  `runs/replay-global.txt`): over 31 receipts (my 8 + the verifier's 14 +
  the foldfix's 7 + 2 mutants) the pre-fold global law FAILs 12 windows
  where the committed arm is green (1) or names the class (11); 9 windows
  agree PASS. The fold changed the **verdict function**, not the windows.
- Mutation M2 (global-arm revert, single-anchor) run with a held foreign
  client **passed by luck** (`before=1 / during=2`, `nodes_delta 0`) —
  the verifier's documented lottery path, reproduced; the replay above
  supplies the deterministic falsification instead.
- Arm teeth (`runs/forgery/arm-teeth.txt`): forged `own_clients=[1,2]` →
  FAIL; forged `own_objects=[7]` → FAIL; so the committed arm cannot
  silently accept a two-client or object-owning footprint.

### 3.3 `x_top` — median arm green or named; no forced-ratio reds

- Committed arm (:30883–30938, :31038–31060): real-cycle rows only
  (`quant > 0`, non-zero µs cells, status ≠ `C`, newest→oldest); armed
  cells are the **pw-top median over the real-cycle rows** vs the
  profiler medians, band **0.25–4.0 unchanged**; no real row → named
  `coverage_blocked`.
- Live: **4 green** (medians 3.1/3.7, 3.1/2.7, 3.5/4.7, 6.4/6.7 vs
  profiler 6.54/3.15, 6.51/5.37, 10.19/7.57, 5.22/4.55 — all inside
  band), **4 named blocked** (3 transient rows, 0 real, under
  co-tenancy). The pre-fix arm would have red-flagged all 4 blocked
  windows at ratio 0 (transient `0.0us/0.0us` accepted), and red-flagged
  the band-edge class (verifier §4.1) — **0 FAIL now**.
- Arm teeth: forged median 30.0/3.0 vs profiler 6.51/5.37 → FAIL
  (10× > 4.0 band); forged provenance with zero real rows → `R02` FAIL.

### 3.4 52-leg census

- 8/8 committed receipts carry exactly **gate 27 / oart 12 / schema 4 /
  xw 9 = 52**; `C01b` and `R01` PASS everywhere. The header comment
  (:29475–29478) records the true census. Dropping one leg key → FAIL
  (teeth check).

## 4. Law census (`runs/laws2.py`, `runs/laws-matrix.txt`)

The 106-law set of the prior verifier re-run **with `X03`/`X06`
re-encoded to the committed arm semantics** (the old X03 encoded the
global lottery and therefore FAILs the committed receipts by
construction; that re-encoding is the only law-set change, disclosed),
plus 5 re-verifier additions: `R01` armed census, `R02` x_top real-row
provenance, `R03` g_hup bounded-at-sig-point (rc −1 ∧ wall ≤ 1.5 ∧
bytes > 0), `R04` x_foot globals recorded-but-unarmed, `R05` no
undeclared xw leg keys.

| set | cells | PASS | FAIL | BLOCKED |
| --- | --- | --- | --- | --- |
| committed bytes, all 111 laws | 888 | **867** | **0** | 21 (all named) |
| committed bytes, base 106 | 848 | **831** | **0** | 17 |
| committed bytes, R-additions | 40 | 36 | 0 | 4 |
| revert-the-fix mutants | 222 | 216 | **3** | 3 |
| **prior baseline** (106 × 14) | 1484 | 1464 | **20** | 0 |

The 3 mutant FAILs are the intended mutation reds (C02/G04/R03 on
`g_hup` rc −9). No committed-bytes cell FAILs.

## 5. Forgery spot-check on the signature gate

`runs/forge.py` → `runs/forgery.log` — every prediction held:

| case | base | forged to | outcome |
| --- | --- | --- | --- |
| canonical pin | `normal` receipt | `rate_hz` 48000→48001 | **CAUGHT** (sha `2587ff60…` ≠ pin `8e8cdad6…`) |
| `g_hup` rc | pre-fix nohup red (rc −9, wall 9.032) | rc −1, wall kept | **CAUGHT** by `R03` (bounded-at-sig-point) + `C02`; `G04` alone is forgeable → closed by `R03` |
| `x_foot` | committed `coverage_blocked` | own client forged, coverage list kept | **BLOCKED via C03 — never silent green** |
| `x_foot` full | same | coverage list popped too | **MISSED at receipt level — disclosed** (a fully self-consistent rewrite is not detectable from fields; compensated by mutation M2 + live co-tenancy + arm teeth) |
| `x_top` | pre-fix 0.0/0.0 false-FAIL | real row + medians forged, failures kept | **CAUGHT** via `C02` (fixture's own failure list) |
| `x_top` full | same | failures list cleared too | **MISSED at receipt level — disclosed** (same caveat) |
| census | committed | one leg key dropped | **CAUGHT** (`C01b` + `R01`) |

Honest statement: the receipt-level law re-derivation catches partial
forgeries and never lets one turn into a silent green; it cannot
distinguish a *fully* self-consistent rewrite. The ground truth is the
live battery produced by the committed bytes plus the sha-pinned normal
receipt — both re-run here.

## 6. Custody, unload-index verification, post-state

- **Module index verified before unload** in every receipt: all
  `unloads[*]` have `verified_index == captured`, `field == sink_name`,
  `value == <the name>`, `exit_code == 0`, `recycled false` — 10 receipts
  × 4 entries, **0 violations** (`runs/census-summary.txt`).
- `sinks_gone` all-true; `own_nodes_after: []` in every entry; `tools`
  resolved (`pw-profiler`/`pw-top`/`pw-cli`/`pw-dump`/`pactl`/`pw-play`).
- Post-state at 08:58:42Z: **0 `r89v_*` objects, 0 `r89a_*`/`r89f_*`
  objects, 0 `r89` modules, 0 owned processes**. Default sink unchanged
  (`alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink.29` — matches
  the verifier's pre-state). **Confound named**: the default *source* is
  now `r91a_src_3169589`, a sibling r91 seat's null source on the shared
  daemon — not created by this seat and not touched by it.
- Seat-owned names: probe-internal `r89a_<pid>` (fixture) and
  `r89v_*` (this seat's scratch/foreign-holder disclosure); no manual
  modules were loaded by this seat.

## 7. Hygiene, disclosures, blockers

- **Zero tracked writes by this seat**: every artifact lives under
  `corpus/live/r89-reverify/` (`runs/`, `tree/`, `tree2/`, `tree3/`,
  `mut-*/`) or is this report (new, untracked). The pre-existing
  `__pycache__` pyc was dirty at entry (per all four r89 seats; mtime
  08:50:24Z, *before* this seat's first run 08:51:19Z — every run used
  `PYTHONDONTWRITEBYTECODE=1`) and a **sibling** merge commit
  (`aaf56d30`, 08:53:57Z, during my battery window) absorbed that dirt
  along with its r94/r95 work; the lane root is left mid-merge by that
  sibling (§1), not by this seat. No commits, no pushes, no
  `set-default-*`.
- Disclosed: three launch attempts of `battery-mut.sh` (a foreground
  `bash -x` probe, a `setsid` launch, a plain `nohup` launch) left two
  racing `mut-sigreset` runs; the lock serialized them and both receipts
  are kept (`085638` = HUP-default control, `085718` = nohup red). No
  probe impact.
- **Remaining risks** (none blocking a green landing):
  1. `x_foot` lands in the named `coverage_blocked` class in **6/8**
     committed receipts — the own Client registers slower than the
     0.35 s bracket under this load. Honest unmeasured, but it means the
     class is *armed* in only 2/8 windows; a retry or a wider bracket is
     a later-seat improvement (the foldfix already names this).
  2. `x_top` is named-blocked in 4/4 co-tenanted receipts (transient-only
     rows for the seat id under foreign driver churn); same shape of
     residual, same named class.
  3. A fully self-consistent receipt rewrite is undetectable by
     field-level laws (§5) — trust rests on the live battery + pin.
  4. The tree-relative family lock (r86→r89 inherited F-class) is
     unchanged: independent ROOTs do not serialize, which is what made
     the deliberate co-tenancy real and is not this fold's scope.
  5. The lane root is mid-merge (sibling r94/r95); any later seat
     grading "HEAD" must pin the commit — `5755be5b` is this report's
     target, proven by fixture sha.
- The canonical Rust runtime remains the sole judge; this seat reports
  evidence and stops.

## 8. Evidence index (`corpus/live/r89-reverify/`)

- `tree/` (frozen `5755be5b`), `tree2/`, `tree3/` (co-tenancy ROOTs),
  `mut-sigreset/`, `mut-footglobal/` (single-anchor mutants).
- `runs/PROVENANCE.txt` (fixture + receipt shas), `runs/receipt-shas.txt`,
  `runs/battery-solo.log`, `runs/battery-cot.log`, `runs/battery-mut.log`,
  `runs/foreign-holder.log`.
- `runs/laws2.py` (law set), `runs/laws-matrix.txt` (1110 LAW lines),
  `runs/census-summary.py` + `runs/census-summary.txt` (class matrix +
  custody check), `runs/replay-global.py` + `runs/replay-global.txt`
  (global-vs-committed same-window replay).
- `runs/forge.py` + `runs/forgery.log` + `runs/forgery/arm-teeth.txt`
  (forgery spot-check + arm teeth).
- `runs/mut.py` (mutant construction), `runs/battery-mut.sh`.
- Receipts: `runs/{normal,r89v1,r89v2,r89v3,cot-r1-t2,cot-r1-t3,
  cot-r2-t2,cot-r2-t3,held-foreign,mut-sigreset-nohup,
  mut-footglobal-held}.receipt.json`.

Seat stop — files changed by THIS seat: `reports/round-89/r89-reverify.md`
(this report) and untracked evidence under `corpus/live/r89-reverify/`.
Zero commits, zero tracked-file modifications.
