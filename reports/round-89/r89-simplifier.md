# r89 SIMPLIFIER — YAGNI/dead-code review of the `0d732989` r89 pwprof landing (read-only, patch NOT applied)

**Seat** simplifier (r89) · **host** plazir27 (devin substrate) ·
**scope** the r89 pwprof landing only: `git show 0d732989 --
corpus/fixtures/measure_audio.py` (**+1561/−3**, 6 hunks; family region
`:29255`–`:30783`, 1529 lines, 4 entry functions / 52 recorded leg keys
(27+12+4+9) / 30 r89 module-level names) plus its 5 wiring splices
(`add_argument` L30913, the mutex sum L30921, the 34-line dispatch block
L31351–31381, the `mode` head L32032, the `suffix` head L32052).
**Writes**: this report + `corpus/live/r89-simplifier/` only. **Zero
tracked writes, no commit, the patch is NOT applied.**

## Custody / tree state at report time

- Analysis base = the **commit-pinned blob**
  `git show 0d732989:corpus/fixtures/measure_audio.py`, sha256
  **`623c25cc55521472dc54a1ab2b4ccb4a9836fda3ca1a71dcca06092a4317cd22`**
  (32062 lines, 1 611 226 B), copied byte-identically to
  `proofs/base-measure_audio.py`; every line number in this report is a
  **0d732989-pinned** line number. The author report's own source sha is
  the same value — the pin is self-consistent.
- **The working tree MOVED under this seat**: HEAD advanced
  `0d732989` → `df0dd8bf` (r89 scribe) → `ec5228ff` (r89 critic) during
  the window. `corpus/fixtures/measure_audio.py` is **byte-identical**
  between the working tree, `HEAD` and the pin
  (`git diff --numstat 0d732989 HEAD -- corpus/fixtures/measure_audio.py`
  empty; sha256 `623c25cc…` on all three), so `git apply --check` of the
  fold patch is **clean against the moved tree** (S10b).
- The only dirty tracked path is the pre-existing
  `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`
  (mtime `04:46:12`, sha256 `a2edda5a…`) — **inside the author window**,
  **not touched by this seat**; every import here ran on scratch copies
  under `PYTHONDONTWRITEBYTECODE=1` (the one `py_compile` ran on the
  *folded copy* inside the receipts dir). The lane lock
  `corpus/live/measure_audio-pwprof-r89.lock` is untracked and carries
  run 2's pid (verified L0).
- **No `lsp` device answers this file on this substrate** (the only MCP
  server is `rea`, whose subject format has no Python source).
  **Recorded unavailable**; this seat performs no renames — all edits
  are exact-string folds — so the `lsp` fallback rule is not engaged.
  All reference proofs are literal AST/symtable/`grep` censuses over the
  pinned blob plus **module loads** (importlib) of the pinned and folded
  copies.
- **probeParent**: exactly **one** read-only `ufo-labrat` was dispatched
  (agent `d5b7e977`; verbatim report at `proofs/labrat-probe.txt`). It
  returned **CONFIRMED on all four hypotheses** (H1 never-bound params,
  H2 dict-domain dead guards, H3 fixed-path lock, H4 dead stats guard)
  with zero files created/modified. Its method was grep enumeration +
  full region reads (no shell in that seat); the residual "no AST pass"
  caveat it raises is independently closed by this seat's own AST
  call-site census and symtable deltas (S3/S5/S6/S8).
- **No fresh full-family replay.** The r89 family is live-host data
  (PipeWire 1.6.8 / WirePlumber 0.5.17 on a loaded host with sibling
  wave-B seats running); the **two pinned author runs are the replay
  oracle** and their verdict surfaces are re-verified here (receipt
  census; both receipt shas re-derive).
- Sibling wave-B seats committed during the window (scribe `df0dd8bf`,
  critic `ec5228ff`). Their findings are **not adopted on citation**;
  where my independently-derived results converge (scribe ADJ-1 on the
  52-vs-47 leg count, scribe/`lock-verify` on the fixed-path lock), the
  convergence is disclosed at the item.

**Proof classes** — `[S]` static reachability over the pinned blob
(AST/symtable/word-boundary census, call-site binding, dominance walk,
patch confinement), `[R]` receipt census across **both** pinned runs,
`[D]` executed differential base-vs-folded (module loads + stubs,
**75 checks**), `[L]` lock proof (static + two-process cross-TMPDIR
serialization + cross-tree race control + fail-open, **23 checks**),
`[P]` `patch -p1` round-trip byte-identity + `git apply --check` +
`py_compile`/`ast.parse`, plus composition with the pending r88 fold.

## 0. Summary

**Verdict: PASS (gate green, no blocker).** The r89 landing is
insertion-only apart from the 3 declared wiring splices, structurally
clean, correctly wired (one `add_argument`, one mutex term, one dispatch
block, two ternary heads; no duplicates) and its dead-code surface is
**small and tight**: **7 provably dead items** delivered as **13 fold
edits** covering **14 replacement sites**, `git apply --numstat`
**+17/−28 → net −11 lines** (32062 → 32051), all inside the family
region, as an **unapplied 7-hunk patch**. Every item carries a static
reachability/dominance proof, a receipt census where it has a receipt
surface, and an executed differential; **no item changes any verdict, no
receipt key and no receipt value**.

| # | item | class | base lines | Δ | proofs | tier |
|---|---|---|---|---|---|---|
| T1 | `_pwprof_r89_play` `role` never bound by 2/2 call sites | dead param + dead fallback | 29638, 29644 | ±0 | S,D | B |
| T2 | `_pwprof_r89_nleg` `wd` never bound by 7/7 call sites | dead param + dead pass-through | 29485–29486, 29493 | −1 | S,D | B |
| T3 | `_pwprof_r89_block` `players` never bound by 10/10 call sites | dead param + dead kill-loop | 29614–29626 | −8 | S,D | B |
| T4 | `_pwprof_r89_ensure_player` `wait_s` never bound by 4/4 call sites | dead default → inline 6.0 | 29652, 29664 | ±0 | S,D | C |
| T5 | `_pwprof_r89_teardown` `(loads or {})`×3 + `leaf or {}` + 2 `.get` fallbacks | dead guards (dict domain) | 29567–29573, 29592, 29607 | −1 | S,D,R | B |
| T6 | `_pwprof_r89_block` `leaf or {}` + 2 `.get` fallbacks (its `(loads or {})` is **LIVE**, retained) | dead guards | 29628, 29632–29633 | −1 | S,D,R | B |
| T7 | `pwprof_schema_r89_entry` `st = l.get("stats") or {}` | dead guard | 30343 | ±0 | S,D,R | C |

Totals: **+17/−28 across 7 hunks → net −11 lines** (32062 → 32051),
**14 replacement sites**, every hunk inside the region (base-side hunk
starts 29482, 29564, 29589, 29604, 29649, 29661, 30340 — all within
29255–30783). `git apply --numstat`: `17 28 corpus/fixtures/measure_audio.py`.

**Tier A** = never-firing statement with no receipt surface. **Tier B** =
logically subsumed guard/parameter with a **provably** zero behavioural
delta (including message text, call args and failure-list content).
**Tier C** = dead default/guard provably unreachable from the current
call graph — separable hunks the operator may retain as mirror
vocabulary.

## 1. Deliverable

- `corpus/live/r89-simplifier/proofs/fold.diff` — sha256
  **`a92789d6be28cc463b7313a44e811c88df4660eacfbb8aeede02acac3c5e2f38`**,
  7 hunks, `git apply --check` **clean** against the live working tree at
  `ec5228ff` *and* `patch -p1` clean against the commit-pinned blob; a
  fresh `patch -p1` over a scratch copy is **byte-identical** to the
  folded copy (S10, run-all.log). **Not applied.**
- `corpus/live/r89-simplifier/proofs/folded/measure_audio.py` — sha256
  **`417344c3e2d315cc2de10de9c367e3339411036de62c06e9fd32f41afa97b790`**,
  32051 lines; `python3 -m py_compile` + `ast.parse` clean.
- **Composition with the pending r88 fold**: `corpus/live/r88-simplifier/
  proofs/fold.diff` (still unapplied) then this patch applies in order
  with a −7-line offset (7/7 hunks), yielding **32044** lines whose r89
  region is byte-identical to `folded/measure_audio.py`'s region (S11).
  The two patches touch disjoint regions; application order does not
  matter (both verified).
- `corpus/live/r89-simplifier/proofs/` — the pinned base copy, the r89
  landing diff (`r89-diff.patch`), `fold-r89-simplifier.py` +
  `fold-apply.txt` (**13** exact-match edits, each asserted to match
  exactly once — or exactly twice for the shared teardown/block unload
  text — *inside the region*; the homographs shared with the kept block
  head are disambiguated by adjacent context), the static suite
  (`static-proofs.py`/`.txt`, **42 checks**), the census and call-site
  dumps (`census-r89-simplifier.py`, `callsite-dump.py`), the executed
  differential (`differential.py`/`.txt`, **75 checks**), the receipt
  census (`receipt-census.py`/`.txt`, **74 checks**), the lock proof
  (`lock-proof.py` + `lock-worker.py`/`.txt`, **23 checks**), the labrat
  report, `run-all.sh` + `run-all.log`, and `manifest-census.txt`.

## 2. Items and proofs

### T1 — `_pwprof_r89_play` dead `role` parameter (Tier B)

`def _pwprof_r89_play(tag, target, tone, role=None)` (29638) is called
exactly twice, both times with 3 positionals: 29659
(`_pwprof_r89_play(tag, ctx["ns"], ctx["tone"])`) and 29839
(`_pwprof_r89_play(tag2, PWPROF_R89_NS2, ctx["tone"])`). `role` is
bound **0/2**; the only read is the fallback at 29644
(`f"media.role={role or PWPROF_R89_ROLE}"`), which therefore always
yields `PWPROF_R89_ROLE`. Both names appear only as direct-call callees
(no `getattr`/alias path can bind it — S3e). Fold: drop the parameter,
use the constant directly. **[D1]** proves the spawned argv is identical
base-vs-folded (`pw-play -P node.name=… -P media.role=r89arole<pid>
--target … tone.wav`) and **[D7]** re-proves it through the whole gate
entry (the two `pw-play` Popen argvs are byte-identical). No receipt
surface (pw-play argv is never recorded; the link legs record only
`{"player": true}`).

### T2 — `_pwprof_r89_nleg` dead `wd` parameter (Tier B)

`def _pwprof_r89_nleg(n_arg, bound_s=PWPROF_R89_SIG_S, extra=(),
wd=None)` (29485–29486) has 7 call sites (29842, 29850, 29893, 29896,
29899, 29929, 29934), none of which binds `wd` (0/7); the parameter is
only forwarded at 29493 as `wd=wd` — i.e. always `None`, which is the
callee's own default. Fold: drop the parameter and the pass-through.
**[D2]** shows both modules call `_pwprof_r89_stream` with identical
argv/timeout/sig_at/sig and the **same effective `wd` (None)** — base
passes `wd` explicitly, folded omits it, and the returned `rec` is
identical; **[D7]** re-proves the whole 26-call stream surface is
identical once the (intended) `wd`-presence difference is excluded.
No receipt surface (`wd` never reaches a recorded rec).

### T3 — `_pwprof_r89_block` dead `players` parameter + kill loop (Tier B)

`def _pwprof_r89_block(entry, failures, msg, loads=None, players=())`
(29614) has 10 call sites: **4×3-arg** (the missing-tools early blocks
29815, 30057, 30237, 30467 — each omits `loads` too) and **6×4-arg**
(the never-enumerated early blocks 29822, 29828, 30065, 30245, 30251,
30477 — 4th positional is `loads`). `players` is bound **0/10**, so the
`for proc in players or ():` kill loop (29617–29624, the copy of the
teardown loop) iterates the empty default and can never run; the
`_alsapw_r84_killpg`/`subprocess`/`signal` symbols leave the function's
symtable with it (S8). Fold: drop the parameter, the loop and the now
untrue "kill players" docstring phrase. **[D3]** covers all four call
shapes (3-arg/empty/leaf/mid-none) with a `killpg` spy: entries,
failures and unload calls identical, **killpg never fires on either
side**; **[D7] load-failure** drives the real block path end-to-end
through `pwprof_gate_r89_entry` (unload called twice — block + finally
teardown — identically, no killpg); **[D6c]** discloses the unreachable
divergence (base with an explicit `players=[proc]` kills; folded raises
`TypeError`) — **0/10 call sites can reach it**.

### T4 — `_pwprof_r89_ensure_player` dead `wait_s` default (Tier C)

`def _pwprof_r89_ensure_player(ctx, tag, wait_s=6.0)` (29652) has 4 call
sites (29837, 30073, 30259, 30524), all `(ctx, tag)`; `wait_s` is bound
**0/4**, so the 6.0 default is the only value ever used at 29664. Fold:
inline `6.0`. **[D4]** runs three scenarios under a fake clock —
`linked` (early return), `never` (24 graph polls then return False,
fake-clock end state `tn = 10¹²+6·10⁹` **on both sides**, proving the
inlined constant is the consumed default), `dead-play` (respawn then
link) — with identical returns, ctx state, call counts and clock end
state; **[D8]** re-proves it inside the whole schema entry. No receipt
surface (the link legs record the boolean only).

### T5 — `_pwprof_r89_teardown` dead dict-domain guards (Tier B)

`loads` is a **required** parameter (29554) and all 4 call sites (29936,
30149, 30336, 30693) pass the entry-local dict, whose only leaf producer
is `_pwprof_r89_load_ns` (5 subscript stores at 29820, 29826, 30243,
30249, 30475 + the oart literal 30063); `_pwprof_r89_load_ns`
(29545–29551) always sets `leaf["field"] = "sink_name"` and
`leaf["value"] = name`, and `_pwcat_r83_ns_load` (16633–16664) returns a
dict on **every** path (2 returns, both `leaf`; 2 dict literals; S5).
Therefore the three `(loads or {})` sites (29567, 29592, 29607), the
`leaf = leaf or {}` (29568) and the two `.get` fallbacks (29572–29573)
are dead in-domain. Fold: `loads.items()` / `loads` ×3, drop the leaf
guard, `leaf["field"]` / `leaf["value"]`. **[D5]** covers six scenarios
(empty, one-leaf, residual-destroy, reader-error-sinks, reader-error-
nodes, foreign+own): entries, failures and unload/pw-cli/killpg calls
identical; **[D6a/D6b]** disclose the two unreachable divergences
(`loads=None` → base graceful / folded `AttributeError`; a leaf missing
`field` → base falls back / folded `KeyError`); **[R]** proves the
receipt-visible values are unchanged: every recorded unload carries
`field == "sink_name"` and `value == <its own tag>`, exactly what
`leaf["field"]`/`leaf["value"]` pass, and `sinks_gone` keys == loads
keys in both runs.

### T6 — `_pwprof_r89_block` dead leaf guard + `.get` fallbacks (Tier B)

Same dict-domain proof as T5, restricted to block: `leaf = leaf or {}`
(29628) and the two `.get` fallbacks (29632–29633) are dead when the
loop is reached (all leaves are `load_ns` products). The block's own
`(loads or {})` (29627) is **LIVE** — the four missing-tools call sites
leave `loads=None` — and is **retained**, mirroring the accepted r88 T3
convention. Fold: drop the leaf guard, index the keys. **[D3]/[D6b]/
[D7 load-failure]** as above; **[R]** the same unload-surface proof.

### T7 — `pwprof_schema_r89_entry` dead stats guard (Tier C)

`legs["s_window"]["stats"] = stats` is assigned unconditionally at 30281
inside the entry's `try`; the only handler is `try/finally` (30242 →
30335), so any exception propagates past the verdicts — no path reaches
`st = l.get("stats") or {}` (30343) with the key absent, `None`, or a
falsy dict (`_pwprof_r89_schema_stats` returns a 33-key literal that is
always truthy). Fold: `st = l.get("stats")`. **[D8]** re-proves the
whole schema entry byte-identical; **[R]** confirms `s_window.stats` is
a dict in both runs. This is **not** one of the critic's F4 fail-open
claim inputs: the guard removed is on a key the recorder always writes,
not on a claim-bearing measurement.

## 3. Proof inventory (all green)

| suite | checks | result |
|---|---|---|
| `static-proofs.py` (S1–S13) | 42 | **ALL PASS** |
| `differential.py` (D1–D8) | 75 | **ALL PASS** |
| `receipt-census.py` (both pinned runs) | 74 | **ALL PASS** |
| `lock-proof.py` (L0–L9) | 23 | **ALL PASS** |
| `fold-r89-simplifier.py` (13 edits) | 13 | all asserted 1×/2× |
| labrat probe (H1–H4) | 4 | CONFIRMED ×4 |
| `run-all.sh` end-to-end | 9 steps | **ALL SUITES PASS** |

Highlights: **S3** (the four never-bound params with arity-correct
call-site binding and no-aliasing check), **S5** (leaf-domain proof),
**S6** (block's live `(loads or {})` vs the dead guards), **S8**
(symtable deltas are exactly the removed params/locals: `{role}`,
`{wd}`, `{wait_s}`, `{players, proc, _alsapw_r84_killpg, subprocess,
signal}` — and nothing else in any r89 function), **S9** (leg-key and
entry-key literals identical base-vs-folded: 42 literal + 10 loop-bound
= 52 leg keys; entry keys `blocked/coverage_blocked/failures/legs/
own_nodes_after/refs/residual_destroy/sinks_gone/tools/unloads`), **S10**
(patch confinement and numstat), **S11** (r88-fold composition), **S12**
(tracked fixture unmodified, sha == pin).

## 4. Receipt census (the two pinned runs are the oracle)

Both runs — `20261016T074733533774Z-pwprof-r89` (sha256
`1d7a24afd20d5ad8f02441288426bbfd940d5667c8bf36dc5980d4718b1310ee`,
pid 1723178) and `20261016T074816877001Z-pwprof-r89` (sha256
`3e756403ecca86d9d9c982812733c57aecdc8fd421428daadeef3aff097d4274`,
pid 1728427) — are **green**: all four entries `failures: []`,
`coverage_blocked` empty, `blocked` absent, `own_nodes_after: []`,
`residual_destroy` absent, all unloads `exit_code: 0`, and **52 leg
keys (27/12/4/9)** in both. Realized error classes: `pwprof_connect_down`
×2 (`g_remote_bogus`, `g_env_bogus`), `pwprof_opt` ×1 (`g_opt_bogus`),
`pwprof_cant_open` ×3 (`o_dir`, `o_empty`, `o_proc`) — the same
r89-local class set the fold leaves untouched. The census asserts, per
run and per entry, that the folded code cannot change any recorded value
(unload `field`/`value` pairs, `sinks_gone` key set, stats dict
presence).

## 5. Observations (not blockers)

- **Leg-count discrepancy (converges with r89-scribe ADJ-1).** The
  commit headline and the task card say "47 legs"; the receipts contain
  **52** leg keys (27/12/4/9) in both runs, and the author report's own
  section headers sum to 51 (xw says 8, the receipt has 9). The receipt
  is the oracle; my census (S9a) independently re-derives 42 literal +
  10 loop-bound = 52. Not a verdict-bearing defect, but the headline
  should be corrected when the landing is next touched.
- **The r89 landing re-introduces the r88 dead-guard patterns** (the r88
  fold `de8032a7…` is still unapplied), so the operator now holds two
  disjoint pending patches; their composition is verified (S11) and
  either order applies. If the operator prefers a single consolidated
  fold, the r89 patch is region-scoped and can be merged with r88's
  without overlap.
- **Orthogonality with the critic's gate-fail items.** The critic's F2
  one-line fix lands in `_pwprof_r89_stream`'s spawn path — a function
  this fold does not touch (no overlap). F3 (`x_foot` bracket race) and
  F4 (fail-open claim inputs elsewhere) are untouched by all 13 edits;
  T7's removed guard is on an always-present recorded key, not on a
  claim input.
- **Lock.** The fixed-path lock is confirmed again here (L0–L9): static
  fixed path `ROOT/"live"/measure_audio-pwprof-r89.lock`, no
  `tempfile/TMPDIR` in the function code, acquired exactly once in the
  dispatch and **held to exit** (no `LOCK_UN`/close anywhere), on-disk
  witness `pid=1728427 ns=r89a_ns_1728427 role=r89arole1728427`; two
  cross-TMPDIR workers on the same tree serialized causally (contender
  acquired only after the holder's release window); cross-tree copies
  race (inherited residual, unchanged by this fold); fail-open on a
  missing `corpus/live/` (inherited caveat).
- **`.pyc`.** The tracked-dirty `measure_audio.cpython-314.pyc`
  (mtime 04:46:12, sha `a2edda5a…`) pre-exists this seat and was not
  touched; the receipts-dir `py_compile` bytecode stays inside
  `corpus/live/r89-simplifier/`.

## 6. Remaining risks / blockers

- **None blocking this seat's gate.** Honest exposures, not hidden:
  - The patch is **unapplied** and the shipping decision is the
    operator's. The three out-of-domain divergences disclosed in D6
    (`loads=None`, a non-`load_ns` leaf missing `field`, an explicit
    `players=` list) are unreachable from the committed call graph but
    would now raise instead of silently degrading if a future edit
    introduces such a call.
  - The dead-param removals (T1–T4) are signature changes for
    out-of-graph callers; there are none in the repository (S3e), and
    the differential re-proves every in-graph call.
  - No fresh full-family replay was run by this seat (live-host family;
    the two pinned author runs are the oracle). The sibling live runs
    (critic/scribe receipts) are cited as convergence only.
  - The critic's F2/F3 gate-fail items are landing-level and orthogonal;
    they are not addressed (and not claimed) here.

**Gate green for the simplifier duty.** Patch not applied; nothing
committed; tracked tree untouched.
