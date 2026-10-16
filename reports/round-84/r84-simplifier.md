# r84 SIMPLIFIER — YAGNI/dead-code review of the `fbe65713` r84 landing (read-only, patch NOT applied)

**Seat** simplifier (r84) · **host** devin · **scope** the r84
pactl/monitor-tap landing only: `git show fbe65713 --
corpus/fixtures/measure_audio.py` (**+2796/−3**; family block `:18821`–`:21578`,
**2758 lines**, 6 entry functions / 147 legs / 52 module-level defs) plus its
5 CLI wiring surfaces. **Writes**: this report +
`corpus/live/r84-simplifier/` only. **Zero tracked writes, no commit, the patch
is NOT applied.**

## Custody / tree state at report time

- Analysis base = the **commit-pinned blob**
  `git show fbe65713:corpus/fixtures/measure_audio.py`, sha256
  **`8ed09d19990480fd337cba99e45cb0588e0615fd90e34793ecc4841c21368e4e`**
  (22725 lines), copied byte-identically to `proofs/base-measure_audio.py`
  (`proofs/sha256.txt`). Every line number in this report is an
  **fbe65713-pinned** line number.
- **The working tree MOVED under this seat** and is *not* the analysis base:
  HEAD advanced `fbe65713` → **`2e4e879b`** (`r84 scribe: INTACT pin chain + both
  runs byte-verified …`) during the window, and a sibling wave-B seat executed
  the r84 fixture live (21:39–21:41Z) while this seat was reading. I verified by
  content that **`corpus/fixtures/measure_audio.py` is byte-identical between
  the working tree, `2e4e879b` and the `fbe65713` pin** (`git diff --numstat
  fbe65713 HEAD -- corpus/fixtures/measure_audio.py` is empty; sha256
  `8ed09d19…` on all three). The deliverable is anchored to the pin, not to the
  moving tree; `git apply --check` was re-run against the live tree after the
  scribe commit and is clean.
- **No `lsp` device answers this file on this substrate** (the only external
  device is the `rea` Ghidra/native-REA MCP, whose subject format has no Python
  source). **Recorded unavailable**; no symbol-aware rename/edit was performed,
  so the `lsp` fallback rule is not engaged. All reference proofs are literal
  AST/`grep` census over the pinned blob plus executed differentials on scratch
  imports.
- **probeParent**: exactly **one** read-only `ufo-labrat` was dispatched (agent
  `db0a1145`; verbatim verdict at `proofs/labrat-probe.txt`). It reported
  **NOT-FALSIFIED on all eight items given to it**, flagged **T5 as the only
  risky one** (dead binding over a live `pactl` read — adopted verbatim), and
  independently surfaced **two additional dead items**, which I re-derived
  myself (`S2c`, `S13`, `S14`, `D4`) and **folded as T9 and T10**. Its
  "flagged only" item (`_alsapw_r84_wait_moved.timeout_s` never supplied) is
  reported in §4.
- **No fresh full-family replay.** The r84 family is live-host data (PipeWire
  1.6.8 / pactl 17.0 / WirePlumber 0.5.17 on a loadavg >100 host); a folded
  replay would need that live host, the full 147-leg wall time, and the
  family lock, and would perturb sibling seats. The **two pinned author runs
  are the replay oracle** and their verdict surfaces are re-verified here
  (`proofs/receipt-census.txt`, 9/9).

**Proof classes used below** — `[S]` static reachability over the pinned blob
(AST dominance / call-site census / executed source slices), `[R]` receipt
census across **both** pinned runs, `[D]` executed differential base-vs-folded
on scratch imports with stubbed I/O (8 checks), `[P]` `patch -p1` round-trip
byte-identity + `git apply --check`.

## 0. Summary

**Verdict: PASS (gate green, no blocker).** The r84 landing is insertion-only,
structurally clean, correctly wired (five surfaces, mutex sum 128 terms with no
duplicates and every term parsed) and its dead-code surface is **small and
tight**: **10 provably dead items** delivered as **15 fold edits** (11 rewrites
+ 4 deletions), `git apply --numstat` **+12/−19 → net −7 lines**, all inside the
family block, as an **unapplied 13-hunk patch**. Every item carries a static
reachability proof, a receipt census where it has a receipt surface, and an
executed differential; **no item changes any verdict or any receipt value**,
and **no item changes any receipt key** — the fold is key-preserving everywhere
(unlike r83-T3, nothing is dropped from a receipt row). Nothing in the round's
falsification envelope was pruned.

| # | item | class | base lines | Δ lines | proofs | tier |
|---|---|---|---|---|---|---|
| T1 | `ALSAPW_R84_LINK_WAIT_S` unused constant | dead constant | 18968 | −1 | S,R | A |
| T2 | `(leaf or {})` dead falsy guard ×2 (`teardown`, `block`) | dead guard | 19881, 19914 | ±0 | S,R,D | B |
| T3 | `_alsapw_r84_st_leg` `ctx` param supplied-but-unread (+2 call sites) | dead param | 19533, 20324–20330 | ±0 | S,R,D | C |
| T4 | `cls, hit =` dead `hit` store ×2 (`prop_leg`, `ctl_sigkill`) | dead store | 20559, 21546 | ±0 | S,R,D | C |
| T5 | `_alsapw_r84_wait_moved` pre-loop fetch | dead binding over live I/O | 19334 | −1 | S,D | C |
| T6 | `_alsapw_r84_prop_leg` `g = {}` pre-loop init | dead store | 20529 | −1 | S,D | C |
| T7 | `(si1 or {})` subsumed by `si1 is None` | redundant predicate | 21346 | ±0 | S,D | B |
| T8 | `hold_note` recomputes the loop's `flipped` | redundant expression | 20041–20044 | −2 | S,D | B |
| T9 | `_alsapw_r84_teardown` `(loads or {})` ×3 (required positional) | dead guard | 19879, 19888, 19901 | ±0 | S,R,D | B |
| T10 | ebusy pre-loop init pair `held_pcm`/`states_held` | dead store ×2 | 20019–20020 | −2 | S,D | C |

Totals: **+12/−19 lines across 13 hunks → net −7 lines** (22725 → 22718),
**15 fold edits / 19 changed lines**, every hunk inside the r84 family block.
`git apply --numstat`: `12 19 corpus/fixtures/measure_audio.py`.

**Tier A** = never-executed code with no receipt surface. **Tier B** =
verdict-superseded / logically subsumed predicate with a **provably** zero
behavioural delta (including message text). **Tier C** = dead guards, dead
payload params and dead stores, provably unreachable from the current call
graph — separable hunks the operator may retain as input-contract guards or
mirror-vocabulary.

## 1. Deliverable

- `corpus/live/r84-simplifier/r84-simplifier.patch` — sha256
  **`df424b848694d73472ff64e99f3ccfb0983477dfb6e446844669ea6a40e89c80`**,
  13 hunks, `git apply --check` **clean** against the live working tree *and*
  `patch -p1` clean against the commit-pinned blob (`proofs/patch-check.txt`).
  **Not applied.**
- `corpus/live/r84-simplifier/proofs/folded/measure_audio.py` — sha256
  **`65c21ab77b07a678e2ebb21271ec025b0031b48aff5f513c1295bfa5cf63bff9`**,
  22718 lines; `python3 -m py_compile` clean (`proofs/pycompile.txt`); a fresh
  `patch -p1` of the patch over a scratch base copy is **byte-identical** to it
  (D0/P).
- `corpus/live/r84-simplifier/proofs/` — the pinned base copy (== committed
  blob), `fold-r84-simplifier.py` + `fold-apply.txt` (**15** exact-match
  replacements/deletions, each asserted to match **exactly once**; the fold
  aborts on a 0- or multi-match, which is how the *file-wide homographs* were
  caught and context-anchored — the r83 `_pwcat_r83_teardown` twin shares
  `gone = {nm: nm not in sinks_now for nm in (loads or {})}` verbatim),
  `static-proofs.py`/`.txt` (S1–S14, **21/21 PASS**), `receipt-census.py`/`.txt`
  (R1–R9, **9/9 PASS**), `differential.py`/`.txt` (D0–D7, **8/8 PASS**),
  `census.py`/`.txt` (defs / params / call sites / constants / write-only
  locals), `labrat-probe.txt`, `sha256.txt`, `patch-check.txt`,
  `pycompile.txt`.
- `corpus/live/r84-simplifier/manifest.json` + `manifest.sha256` — sha256
  census of all seat files.

## 2. Items — remove / proof / receipts

### T1 — `ALSAPW_R84_LINK_WAIT_S` is never referenced `[S][R]`

**(a) Change** delete `:18968` `ALSAPW_R84_LINK_WAIT_S = 5.0` (the neighbouring
`ALSAPW_R84_STREAM_WAIT_S = 8.0` stays — it is the family's live wait bound).

**(b) Proof.** `[S]` whole-file word-boundary census: the symbol occurs **once**
(its own definition). The sibling it was copied from, `PWCAT_R83_LINK_WAIT_S`
(`:16511`), has **4** references (`:16884`, `:16996`, `:17244`) — the contrast
proves this is a copy-paste leftover, not a knob with a live default. The
family's waits use `ALSAPW_R84_STREAM_WAIT_S` (4 refs) and the hardcoded leg
bounds.

**(c) Receipts.** `[R]` neither pinned run contains any `link_wait`/`LINK_WAIT`
key or value (0 occurrences in both, R2). No receipt surface at all.

### T2 — `(leaf or {})` is an unreachable falsy guard, both sites `[S][R][D]`

**(a) Change** `:19881` and `:19914`
`_gst_r81_unload_own((leaf or {}).get("module_id"), …)` →
`_gst_r81_unload_own(leaf.get("module_id"), …)`.

**(b) Proof.** `[S]` `_pwcat_r83_ns_load` (`:16632`) returns `leaf` on **every**
return path (2/2, `S2a`) and both `leaf = …` bindings in it are **dict
literals** (2/2, incl. the `except OSError` body) — it cannot return `None`.
All five r84 `loads[...] =` assignments are `_pwcat_r83_ns_load(...)` (`S2b`),
and the four `_alsapw_r84_teardown` call sites pass such a dict positionally
(`S2c`), as do the four `_alsapw_r84_block` calls that supply `loads`. The
sibling `(loads or {})` in `_alsapw_r84_block` **is** live (7 of its 11 call
sites omit `loads`, `S2c`) and is retained.

**(c) Receipts.** `[R]` all 10 `unloads` entries across both runs are dicts
(R3); `sinks_gone` is all-true and `own_nodes_after` empty on every entry.
`[D]` D4 runs both copies' `_alsapw_r84_teardown` over a dict `loads` (incl. a
`module_id: None` leaf) with stubbed unload/readers: **identical entries,
identical failure lists, identical unload call lists**. No key or value changes.

### T3 — `_alsapw_r84_st_leg`'s `ctx` parameter is passed and never read `[S][R][D]`

**(a) Change** the signature at `:19533`
(`_alsapw_r84_st_leg(dev, ctx, tail, timeout_s=25.0)` → `(dev, tail, …)`) and
drop the `ctx` argument at the two call sites (`:20324` `st_pw_node`, `:20327`
`st_pw_c6`).

**(b) Proof.** `[S]` inside the function body there are **zero** `Name('ctx')`
nodes (`S3a`) — unlike every sibling leg, this one never applies the
`ctx["redact"]` pass (`_alsapw_r84_arecord_leg` `:19580–19582` does). Both call
sites pass `ctx` as positional argument #2 (`S3b`), so the value is computed and
discarded. The only r84-relevant key in those `ctx` dicts is
`redact=(str(tmp),)`; the recorded argv is
`speaker-test -D pipewire:NODE=<ns> …` and contains no `tmp` token, so even
applying redaction would be a no-op (`[R]` R4: all four st_ legs' argv across
both runs carry `r84a_ns_<pid>` and no `/tmp`).

**(c) Receipts.** `[R]` the four `st_*` records have an identical key set across
both runs and both copies (R4). `[D]` D1 runs the real function with stubbed
spawn/graph: **byte-identical `rec`** (argv, rc, signal, wall, stderr heads,
class/hit, nodes_mid) and identical spawn argv. No key or value changes.

### T4 — the `hit` half of two `cls, hit =` unpacks is a dead store `[S][R][D]`

**(a) Change** `:20559` (`_alsapw_r84_prop_leg`) and `:21546`
(`alsapw_negctl_r84_entry`, `ctl_sigkill`) from `cls, hit = _alsapw_r84_errclass(err)`
to `cls, _ = …`.

**(b) Proof.** `[S]` of the **8** `X, hit = _alsapw_r84_errclass(...)` sites in
the block, exactly two have **no load of `hit` after the assignment**: `20559`
(0 loads in the whole function, `S4a`) and `21546` (the function's only `hit`
load is `21512`, reading the *unit-table* binding created at `21509`, `S4b`).
The other six (`19179`, `19517`, `19560`, `19608`, `19815`, `21509`) record
`hit` into their receipt row (`error_hit` / `"hit"`) and are retained (`S4c`).

**(c) Receipts.** `[R]` **no prop_leg record in either run carries a `hit`
key** (14 records × 2 runs), and `ctl_sigkill` carries exactly
`{argv, error_class, exit_code, signal, stderr_tail}` in both runs (R5). `[D]`
D2 runs the real `_alsapw_r84_prop_leg` under a stubbed spawn/graph: **identical
`rec`** with `error_class` present and `has_hit=False`. No key or value changes.

### T5 — the pre-loop fetch in `_alsapw_r84_wait_moved` is a dead binding over a live read `[S][D]`

**(a) Change** delete `:19334` `leaf = _alsapw_r84_stream_leaf(tag)` (the
loop at `:19335` re-reads into `leaf` before any use; the post-loop
`return leaf` at `:19340` sees only loop-bound values).

**(b) Proof.** `[S]` `leaf` stores = `{19334, 19336}`, loads = `{19337×2,
19340}` (`S5`); `timeout_s` defaults to `2.0` and its single call site passes
no keywords, so `time.monotonic() - t0 < timeout_s` is true on the first check
and the body rebinds `leaf` before any read — the pre-loop value is only
reachable on a zero-iteration loop, which the call graph cannot produce.

**(c) Disclosed caveat (adopted from the probe verbatim).** The deleted RHS is
**not** a pure expression: `_alsapw_r84_stream_leaf` spawns
`pactl -f json list sink-inputs`. The fold therefore **removes one live reader
call** before the poll loop starts; the returned leaf and the sleep pattern are
unchanged. `[D]` D3 models the *host* (the stream's sink flips at a fixed point
on the simulated clock) and shows: identical returned leaf `{'sink': 9}`,
identical sleep list `[0.12]`, **exactly one fewer reader call** (3 → 2). An
operator who wants the extra read kept should drop this hunk alone.

### T6 — `_alsapw_r84_prop_leg`'s `g = {}` is a pure dead store `[S][D]`

**(a) Change** delete `:20529` `g = {}` (the `while` at `:20530` assigns `g`
first thing).

**(b) Proof.** `[S]` `g` stores = `{20529, 20531}`, loads = `{20532, 20533}`
(`S6`) — both loads are inside the loop **after** the loop-body store, and `g`
is never read after the loop (the code that follows reads `node`, not `g`). A
zero-iteration loop (impossible: bound 2.2) would still never read `g`.

**(c) Receipts.** `[D]` D2 covers the whole function: **byte-identical `rec`**.
No key or value changes.

### T7 — `(si1 or {})` in the sticky guard is subsumed by `si1 is None` `[S][D]`

**(a) Change** `:21346` `if si1 is None or (si1 or {}).get("sink") in (None,
4294967295):` → `if si1 is None or si1.get("sink") in (None, 4294967295):`.

**(b) Proof.** `[S]` in a disjunction the second operand is evaluated only when
`si1 is None` is False, i.e. when `si1` is not None — so `(si1 or {})` is
always exactly `si1`. Strict short-circuit subsumption, not a coincidence. The
first disjunct stays (it is load-bearing: `wait_attached` returns a leaf **or**
`None` — `S7` pins the producer: `_alsapw_r84_stream_leaf` returns a dict
literal or `None`, and `wait_attached`'s `leaf` is bound only to `None` or that
call's result). `[D]`/`[S]` the two source slices are replayed over
`{None, {}, {"sink": None}, {"sink": 0xFFFFFFFF}, {"sink": 77}, {"index": 5}}`:
**identical booleans on all six**.

**(c) Disclosed caveat.** On the producer's contract domain (`None` or a leaf
dict) the two forms are equivalent; a *falsy non-dict* `si1` (impossible from
the call graph) would make the folded form raise `AttributeError` instead of
silently reading `None`. Same "loud failure instead of silent default" trade
the r83 seat disclosed for its T7.

### T8 — `hold_note` recomputes the loop's `flipped` `[S][D]`

**(a) Change** `:20041–20044`
`if held_pcm in [k for k in running if "RUNNING" not in states0.get(k, "")]`
→ `if held_pcm in flipped` (the `flipped` binding created at `:20026–20027`).

**(b) Proof.** `[S]` the comprehension is **token-identical** to the `flipped`
expression (`S12` replays both source slices over three synthetic
`(running, states0, held_pcm)` cells: identical strings). `running` is bound
immediately before `flipped` in the same iteration and `states0` is fixed
before the loop, so at the point the dict literal is evaluated the two inputs
are exactly the ones that produced `flipped`; the loop can only exit via
`break` after both bindings or by timeout after the last iteration's bindings.

**(c) Receipts.** `[R]` the realized branch is exercised in both runs
(`held_pcm = card0/pcm1c`, `hold_note = "own pin flipped a pcm"`, R7); `[D]` D6
replays the *whole* ebusy slice (loop + recorded dict) from both copies in two
scenarios (nothing running → the "held pcm set" branch; a RUNNING pcm under the
pin → the "own pin flipped a pcm" branch): **identical `legs["ebusy_hold"]`
dicts and identical `held_pcm`**. No key or value changes.

### T9 — `_alsapw_r84_teardown`'s `(loads or {})` is dead (required positional) `[S][R][D]`

**(a) Change** `:19879`, `:19888`, `:19901` `(loads or {})` → `loads` (the
`_alsapw_r84_block` copy at `:19912` **stays** — its `loads=None` default is a
real path).

**(b) Proof.** `[S]` `_alsapw_r84_teardown(entry, failures, loads)` has **no
defaults** (`S13`), and its four call sites (`:20494`, `:20728`, `:21031`,
`:21324`) all pass a local `loads` dict built from `_pwcat_r83_ns_load`
(`S2b`/`S2c`). The `or {}` fallback therefore can never be selected in this
function; the folded copy's teardown contains **zero** such guards while the
block keeps its single one (`S2d`/`S13`). (This is the *mirror* of r83-T2,
where the r83 family's `loads` could be `None`; here the probe surfaced the
asymmetry and it is folded only on the teardown side.)

**(c) Receipts.** `[R]` the teardown receipts (`unloads`, `sinks_gone`,
`own_nodes_after`) are realized on all four teardown-running entries in both
runs and all `unloads` values are dicts (R3). `[D]` D4 compares entries,
failure lists and unload call lists for a normal dict and a `module_id: None`
leaf: **identical**. No key or value changes.

### T10 — the ebusy pre-loop init pair is never read `[S][D]`

**(a) Change** delete `:20019` `held_pcm = None` and `:20020`
`states_held = {}` (the `while` bound at `:20022` is the **hardcoded literal
`5.0`**, so the loop always runs and its first statements reassign both).

**(b) Proof.** `[S]` stores of the pair = `{20019, 20020, 20023, 20029, 20032}`,
loads = `{20024, 20039, 20040, 20042, 20047, …}` — the smallest load line is
**20024**, after the loop-body reassignment at 20023 (`S14`); the folded copy's
stores start at 20019 (loop-body only) with the first load at 20020. Because
the bound is a literal (not a parameter), the zero-iteration path cannot occur
on any host.

**(c) Receipts.** `[R]` the `ebusy_hold` record exists in both runs with
`held_pcm`/`pcm_states_at_hold`/`hold_note`/`hold_alive` (R7). `[D]` D6 replays
the slice: **identical `legs["ebusy_hold"]` and `held_pcm`** in both scenarios.
No key or value changes.

**(d) Disclosed caveat.** After the fold the pair is bound only by the loop; a
future editor who replaced the literal bound with a parameter that could be
`<= 0` would get a loud `NameError` at `:20047`/`:20089` instead of a silent
`None`/`{}`. This is the only item that removes an unconditional binding whose
value would be consumed by a guard on an unreachable path — the operator may
drop this hunk alone (it is the only one the probe did not certify as a *pure*
dead store for both halves; I re-derived the symmetric half myself).

## 3. Checked and NOT dead (explicitly cleared)

- **`(loads or {})` in `_alsapw_r84_block`** (`:19912`) — live: 7 of 11 call
  sites omit `loads` (the missing-tools / not-enumerated / no-default-source
  blocks), so the default `None` is exercised.
- **The other six `X, hit = _alsapw_r84_errclass(...)` sites** (`:19179`,
  `:19517`, `:19560`, `:19608`, `:19815`, `:21509`) — all record `hit`
  (`error_hit` / `"hit"`) into their receipt row (`S4c`).
- **`leaf = None` pre-loop inits in `_alsapw_r84_wait_attached` (`:19290`) and
  `_alsapw_r84_wait_attached_fresh` (`:19319`)** — retained as the sentinel
  value consumed by the `is not None` guards / the post-loop `return leaf`; they
  cost nothing and are the zero-iteration fallback. (Contrast T5, whose
  pre-loop statement is an *I/O call*, not a binding.)
- **`_alsapw_r84_run`'s `killed_at_bound` / `signal` / `unknown_pcm_name`
  surfaces** — live: read by the `-D ''`/argv-eaten verdicts and the refusal
  taxonomy.
- **`_alsapw_r84_aplay_leg`'s `unknown_pcm_name`** — recorded-not-gated for the
  direct-ALSA legs (honest-leaf convention; shared shape with `_run`).
- **The 0-hit falsification arms** — the segv/kill discriminator, the
  capture-refusal unit cases, the "no target node" and "nodes published" arms,
  the adaptive free-vs-held ebusy arms: all are the envelope the round
  deliberately armed (they realize on a different host state), not dead code.
- **The classifier table is complete**: all **18** family-local stderr classes
  have at least one positive unit-table case, and the 5 must-classify-nothing
  inputs are pinned (`S8`).
- **Error-class isolation** — the r84 classes are family-local and checked
  before the shared `_playback_r78_errclass` fallback; never prepended into
  `_CAPTURE_ERR_CLASSES`.
- **Wiring** — `--probe-alsapw-r84` is consumed by all five surfaces (parser
  `:21703`, mutex sum `:21711`, dispatch `:22035`, mode `:22695`, suffix
  `:22715`); the mutex sum has **128 terms, no duplicates, and every term has a
  parser arg** (`S9`). No dead config key.
- **Namespacing** — all 52 module-level r84 defs match
  `_alsapw_r84_*`/`alsapw_*_r84_*` and are unique file-wide (`S10`); the four
  entry-local closures (`props_of`, `si_props`, `ratio_of`, `sigset`) are
  function-scoped and intentional.
- **The r84 evidence leaves** — `pre_reset`, `role_reset`, `reset_sink[_end]`,
  `tap_exit`, `tap_stderr_tail`, `tap_file`, `dur_s`, `stream_wait_s`,
  `parec_argv_tail`, `out_bytes_at_kill`, `parec_sigkill`, `a_killed_at_s`,
  `ebusy_postkill`, `hold_note`, `pcm_key`, `pcm_state_before`, `respawn`,
  `respawn_tap_series_tail`, `repaired_mute`, `note`, … — the family's
  honest-leaf convention (recorded, not gated). No deletion.
- **Consolidation candidates (considered, declined)** — the four poll helpers
  (`wait_stream`, `wait_attached`, `wait_stream_pid`, `wait_attached_fresh`)
  and the duplicated unload loop in `teardown`/`block` could be merged into
  shared helpers, and several r84 helpers re-implement shapes that exist in
  r77–r83 families. Declined: the ledger's convention is that each family is
  self-contained and prior rows stay untouched, and a merge would be a
  refactor (touching live call graphs), not a YAGNI deletion with a
  zero-delta proof.

## 4. Below the bar (reported, retained)

- **Never-supplied knobs that are bounds and feed live expressions**:
  `_alsapw_r84_run.env` (0/15), `_alsapw_r84_pactl.timeout_s` (0/44),
  `_alsapw_r84_aplay_leg.sample_s`/`timeout_s` (0/10),
  `_alsapw_r84_arecord_leg.timeout_s`/`env` (0/12),
  `_alsapw_r84_sig.ws`/`skip` (0/1),
  `_alsapw_r84_wait_moved.timeout_s` (0/1 — the probe's "flagged only" item),
  `_alsapw_r84_parec_leg.dur_s` (8/13), `_alsapw_r84_killpg.sig` (5/23).
  Retained: each is the family's documented bound and the r83 §4 precedent.
- **Never-supplied *selectors* with no receipt surface**:
  `_alsapw_r84_sink_leaf.what` (0/3), `_alsapw_r84_default.what` (0/2 varied),
  `_alsapw_r84_aplay_leg.tone_key` (0/10),
  `_alsapw_r84_arecord_leg.witness_subs` (0/12). Their deletion would change
  only signatures (no call site passes them), but unlike r83-T3 they carry **no
  always-empty receipt leaf**, so they are mirror-vocabulary seams rather than
  dead payload. Named here so the operator can take them separately if wanted.
- **`_alsapw_r84_sig`'s single call site** supplies 4 of its 6 parameters
  (defaults `ws=0.25`, `skip=0.3` are the only values ever bound) — same class,
  retained.
- **`leg["note"]`** in the sticky leg — a literal documentation string recorded
  into the receipt; retained (data, not code). Its *claim* ("different-tag
  respawn 100% measured") has no witness leg in either receipt and is already
  handed to adjudication as the r84-scribe's ADJ-4 — a citation matter for the
  judge, not a simplifier deletion (the string itself is a recorded leaf).
- **`corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`** is dirty in
  the worktree (pre-existing; the r84-compiled bytecode, also flagged by the
  r84-scribe as ADJ-7). This seat did not touch it (all compilation happened on
  scratch copies under `corpus/live/r84-simplifier/proofs/`); it is a tracked
  file, so it is left exactly as found.

## 5. Findings for the operator (reported, NOT folded — deletions would change behaviour)

- **F1 — the `pw-link` tool gate is over-broad in two entries.**
  `alsapw_dev_lattice_r84_entry` (`:19927`) and `alsapw_pw_args_r84_entry`
  (`:20259`) require `shutil.which("pw-link")` before running, but the r84
  family never invokes `pw-link`: the file's `["pw-link", …]` spawns are all
  outside the r84 block (`:3182`, `:4337`, `:6050`, `:6101`, `:6115`, `:8245`,
  `:12324`–`:12360`). On a host without `pw-link` the two entries block as
  "missing tools" even though nothing in them needs it. Deleting the token
  would *change* behaviour in that case (block → run), so it is reported rather
  than folded.
- **F2 — the `dev_lattice` entry calls `pactl` without gating on it.**
  `_alsapw_r84_aplay_leg` → `_alsapw_r84_default("sink")` shells out to
  `pactl get-default-sink`, but `dev_lattice`'s tool tuple does not include
  `pactl` (the other five entries do). A host without `pactl` would fail the
  `a_null`/`a_sysdefault`/direct arms as verdict failures rather than a named
  coverage block. The inverse of F1; no deletion implied.
- **F3 — `_alsapw_r84_st_leg` is the only leg with no `ctx["redact"]` pass**
  (`:19537` vs `:19579–19582` / `:19485–19488`). It is harmless today (its argv
  carries no redactable token — R4), but after T3 the parameter that would let
  it redact is gone; if a future call site puts a tmp path into `tail`, the
  argv would be recorded verbatim. T3 is a separable hunk if the operator
  prefers to keep `ctx` and add the pass instead.
- **F4 — the two `st_*` legs are `_alsapw_r84_run`-class legs for argv
  purposes** but use the leg helper; noted only because T3 touches their call
  sites.

## 6. Blockers

- None for this seat. `/tmp` remains near quota → all scratch work used
  `TMPDIR=/home/vgpnk/Projects/shokunin/tmp` (and everything material lives
  under `corpus/live/r84-simplifier/`), as instructed.
- No fresh full-family replay was run (live-host + family-lock cost, sibling
  seats active); the two pinned author runs are the oracle and were re-verified
  (9/9).
- The `lsp` device is unavailable on this substrate (recorded); no symbol-aware
  operation was needed for this patch (it renames nothing).

## 7. Verdict

**PASS** — the r84 landing is clean; 10 provably dead items, net −7 lines,
delivered unapplied with 21/21 static, 9/9 receipt and 8/8 differential proofs
plus a byte-identical patch round-trip. No verdict, no receipt key and no
receipt value changes. The gate is green; the fold decision (and F1–F3) belongs
to the operator.
