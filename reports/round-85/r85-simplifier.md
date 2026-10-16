# r85 SIMPLIFIER — YAGNI/dead-code review of the `2a49d540` r85 landing (read-only, patch NOT applied)

**Seat** simplifier (r85) · **host** devin · **scope** the r85
pactl/monstreams landing only: `git show 2a49d540 -- corpus/fixtures/measure_audio.py`
(**+2178/−3**; family block `:21579`–`:23728`, **2150 lines**, 5 entry
functions / 87 legs / 34 module-level r85 defs) plus its 5 CLI wiring
surfaces. **Writes**: this report + `corpus/live/r85-simplifier/` only.
**Zero tracked writes, no commit, the patch is NOT applied.**

## Custody / tree state at report time

- Analysis base = the **commit-pinned blob**
  `git show 2a49d540:corpus/fixtures/measure_audio.py`, sha256
  **`714564a32141f134f849401dd029e1e10c4aa19bb848a43fd50f70a251499ee2`**
  (24900 lines), copied byte-identically to `proofs/base-measure_audio.py`
  (`proofs/sha256.txt`). Every line number in this report is a
  **2a49d540-pinned** line number. The author report's own source sha is the
  same value — the pin is self-consistent.
- **The working tree MOVED under this seat** (HEAD advanced `2a49d540` →
  `8ae131e6` r85-critic → `972202bf` r85-scribe) and is *not* the analysis
  base; the deliverable is anchored to the pin. `corpus/fixtures/measure_audio.py`
  is **byte-identical** between the working tree, `HEAD` and the `2a49d540`
  pin (`git diff --numstat HEAD` is empty; sha256 `714564a3…` on all three),
  so `git apply --check` of the patch against the live tree is clean and the
  fold is applicable as-is. The only dirty tracked path is the pre-existing
  `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` (r84's, also
  flagged by the r84/r85 scribe seats) — **not touched by this seat**; every
  compilation here happened on scratch copies under `corpus/live/r85-simplifier/proofs/`.
- **No `lsp` device answers this file on this substrate** (the only external
  device is the `rea` Ghidra/native-REA MCP, whose subject format has no
  Python source). **Recorded unavailable**; no symbol-aware rename/edit was
  performed, so the `lsp` fallback rule is not engaged. All reference proofs
  are literal AST/`grep` census over the pinned blob plus executed
  differentials on scratch imports.
- **probeParent**: exactly **one** read-only `ufo-labrat` was dispatched
  (agent `10900a89`; verbatim report at `proofs/labrat-probe.txt`). It
  reported **NOT-FALSIFIED on all 14 items** and **CONFIRMED C1/C2** (the
  either-way arming and the patch's block confinement) from its own census,
  with no artifact created.
- **No fresh full-family replay.** The r85 family is live-host data
  (PipeWire 1.6.8 / WirePlumber 0.5.17 / pactl 17.0 on a loadavg ~50 host);
  a folded replay would need that host, the 87-leg wall time and the family
  lock, and would perturb sibling seats. The **two pinned author runs are
  the replay oracle** and their verdict surfaces are re-verified here
  (`proofs/receipt-census.txt`, 8/8; 87 legs ×2, `failures: {}`).
- Sibling wave-B seats committed during the window (r85-critic `8ae131e6`,
  r85-scribe `972202bf`). Their F1–F3 / ADJ-3 arm-looseness findings are
  **independently re-derived and executed** in §3 here (B6/B7), not adopted
  on citation.

**Proof classes used below** — `[S]` static reachability over the pinned blob
(AST dominance / call-site census / executed source slices), `[R]` receipt
census across **both** pinned runs, `[D]` executed differential base-vs-folded
on scratch imports with stubbed I/O (13 checks), `[B]` executed either-way /
absorption replay of the committed arm slices (7 checks), `[P]` `patch -p1`
round-trip byte-identity + `git apply --check`.

## 0. Summary

**Verdict: PASS (gate green, no blocker).** The r85 landing is insertion-only,
structurally clean, correctly wired (five surfaces, mutex sum 129 terms, no
duplicates) and its dead-code surface is **small and tight**: **14 provably
dead items** delivered as **44 fold edits**, `git apply --numstat`
**+42/−64 → net −22 lines**, all inside the family block, as an **unapplied
21-hunk patch**. Every item carries a static reachability proof, a receipt
census where it has a receipt surface, and an executed differential; **no item
changes any verdict, no receipt key and no receipt value**.

| # | item | class | base lines | Δ | proofs | tier |
|---|---|---|---|---|---|---|
| T1 | `PACTLMON_R85_STREAM_WAIT_S` unused constant | dead constant | 21690 | −1 | S,D | A |
| T2 | `_pactlmon_r85_wait_node` zero-call helper | dead function | 22032–22040 | −11 | S,D | A |
| T3 | `_pactlmon_r85_sd_leg` `ctx` dead param (+2 call sites) | dead param | 22260, 23280, 23301 | ±0 | S,D | C |
| T4 | `_pactlmon_r85_wait_tap_link` `sink` dead param (+1 call site) | dead param | 22043, 22111 | ±0 | S,D | C |
| T5 | `cls, hit =` dead `hit` store ×2 (`cap_leg`, `sd_leg`) | dead store | 22218, 22304 | ±0 | S,R,D | C |
| T6 | `sers` dead store (`addr`) | dead store | 22738–22739 | −2 | S,R,D | B |
| T7 | `lp = link_ports("t_prop_srcname")` dead store | dead store | 23510 | −1 | S,D | C |
| T8 | `want_node` dead loop payload (`capture`) | dead payload | 23491–23496 | −5 | S,R,D | C |
| T9 | entry-local `gsv` `label` dead param (+20 call sites) | dead param | 22487 + 20 | ±0 | S,D | C |
| T10 | `_pactlmon_r85_teardown` dead guards ×7 (`loads`×4, `leaf`, `l`×2) | dead guard | 22353–22400 | −1 | S,R,D | B |
| T11 | `_pactlmon_r85_block` `leaf = leaf or {}` | dead guard | 22412 | −1 | S,R,D | B |
| T12 | subsumed `(a1 or {})`/`(a2 or {})`×2/`(a4 or {})` | redundant guard | 22682, 22688, 22693, 22703 | ±0 | S,D | B |
| T13 | `_pactlmon_r85_vol_pct` `(rec or {})` | dead guard | 22424 | ±0 | S,D | B |
| T14 | `feeder is not None and` dead conjunct (pre-ladder) | dead guard | 23272 | ±0 | S,D | C |

Totals: **+42/−64 across 21 hunks → net −22 lines** (24900 → 24878),
**44 replacement sites**, every hunk inside the r85 family block
(min old-side start 21687 ≥ 21579; max old-side start 23507 < 23728). `git apply --numstat`:
`42 64 corpus/fixtures/measure_audio.py`.

**Tier A** = never-executed code with no receipt surface. **Tier B** =
verdict-superseded / logically subsumed predicate with a **provably** zero
behavioural delta (including message text). **Tier C** = dead guards, dead
payload params and dead stores, provably unreachable from the current call
graph — separable hunks the operator may retain as input-contract guards or
mirror-vocabulary.

## 1. Deliverable

- `corpus/live/r85-simplifier/r85-simplifier.patch` — sha256
  **`8d349469e61ac612251dcf61d66730099f2d946fe381edc61444f02b6d6e330c`**,
  21 hunks, `git apply --check` **clean** against the live working tree *and*
  `patch -p1` clean against the commit-pinned blob; a fresh `patch -p1` over a
  scratch copy is **byte-identical** to the folded copy
  (`proofs/patch-check.txt`). **Not applied.**
- `corpus/live/r85-simplifier/proofs/folded/measure_audio.py` — sha256
  **`840f35be6d4930fc4783db909d509a5c93e5b7fc24baf372d8bdf813516a62c6`**,
  24878 lines; `python3 -m py_compile` clean (`proofs/pycompile.txt`).
- `corpus/live/r85-simplifier/proofs/` — the pinned base copy, the r85 block
  extract, `fold-r85-simplifier.py` + `fold-apply.txt` (**44** exact-match
  replacements, each asserted to match **exactly once**; the fold aborts on a
  0- or multi-match — this is how the two *homographs*
  `    cls, hit = _pactlmon_r85_errclass(err)` (×2) and the twin
  `for tag, leaf in (loads or {}).items(): leaf = leaf or {}` blocks
  (teardown vs block) were caught and context-anchored),
  `static-proofs.py/.txt` (S1–S19, **19/19 PASS**), `receipt-census.py/.txt`
  (R1–R8, **8/8 PASS**), `differential.py/.txt` (D0–D12, **13/13 PASS**),
  `bimodal-arms.py/.txt` (B1–B7, **7/7 PASS**), `census.py/.txt`,
  `deadscan.py/.txt`, `labrat-probe.txt`, `sha256.txt`, `patch-check.txt`,
  `pycompile.txt`.
- `corpus/live/r85-simplifier/manifest.json` + `manifest.sha256` — sha256
  census of all 27 seat files; `run-all.sh` reproduces every artifact.

## 2. Items — remove / proof / receipts

### T1 — `PACTLMON_R85_STREAM_WAIT_S` is never referenced `[S][D]`

**(a) Change** delete `:21690` `PACTLMON_R85_STREAM_WAIT_S = 8.0`.

**(b) Proof.** `[S]` whole-file word-boundary census: the symbol occurs **once**
(its own definition, `uses=0`). The sibling the r84 family kept for exactly
this purpose, `ALSAPW_R84_STREAM_WAIT_S` (`:18969`), has **5** occurrences (1 definition +
4 references: `:19270`, `:19281`, `:19301`, `:19314`) — the contrast proves this is a
copy-paste leftover, not a knob with a live default. `[D]` D12: the folded
module has no such attribute.

**(c) Receipts.** `[R]` R2: **0 occurrences** of any `STREAM_WAIT` key or
value in either pinned receipt. No receipt surface at all.

### T2 — `_pactlmon_r85_wait_node` has zero call sites `[S][D]`

**(a) Change** delete `:22032–22040` (the helper + its two trailing blank
lines).

**(b) Proof.** `[S]` AST call census over the whole file: **0** calls to
`_pactlmon_r85_wait_node`; the only other `wait_node` mentions belong to
other families (`_module_r80_wait_node` `:11760`+5 calls,
`_pwcat_r83_wait_node` `:16884`+1 call, the `wait_nodes=` kwargs of r79/r80).
The r85 family polls with `_pactlmon_r85_graph()` directly (10 call sites) and
`_pactlmon_r85_wait_tap_link`. `[D]` D12: absent from the folded namespace;
`[S]` S2/S16: r85 defs 34 → 33, exactly one removed. **Tier A, separable** —
the operator may keep it as mirror vocabulary; it is unreachable either way.

### T3 — `_pactlmon_r85_sd_leg`'s `ctx` is passed and never read `[S][D]`

**(a) Change** `:22260` signature
`_pactlmon_r85_sd_leg(name, ctx, sd, client_argv, dur_s=2.6)` →
`(name, sd, client_argv, dur_s=2.6)`, and drop the `ctx` argument at the two
call sites (`:23280` `sd_idle`, `:23301` connect legs).

**(b) Proof.** `[S]` inside the body there are **zero** `Name('ctx')` loads
(S3) — unlike every sibling leg, this one never applies a redaction pass
(`_pactlmon_r85_cap_leg` uses `_capture_tail(err, str(out))`; the r84 aplay
leg applies `ctx["redact"]`). Both call sites pass `ctx` positionally (S3),
so the value is computed and discarded. `[D]` D4 runs the real function with
stubbed spawn/graph: **byte-identical leg dict and identical spawn argv**.

**(c) Receipts.** `[R]` R4: the capture legs carry **no** `hit`/`ctx` key; the
`sd_*` records' key set is identical base/folded (D4). **Disclosed caveat**
(see F3): the sd legs are the only r85 legs whose recorded `argv` carries a
raw TMPDIR path, unredacted — `ctx` was the carrier that would have allowed a
redaction pass. T3 is a separable hunk if the operator prefers to keep `ctx`
and add the pass instead.

### T4 — `_pactlmon_r85_wait_tap_link`'s `sink` is passed and never read `[S][D]`

**(a) Change** `:22043` signature `(sink, tap_tag, timeout_s=…)` →
`(tap_tag, timeout_s=…)` and drop `ctx["mix"]` at the single call site
(`:22111`).

**(b) Proof.** `[S]` the body polls `_pactlmon_r85_edges_in(g, tap_tag)` and
only checks that every out-port name starts with `monitor_` (S4); `sink`
appears nowhere but the docstring. `[D]` D6: identical return value and
identical poll/sleep pattern with a stubbed graph.

**(c) Receipts.** `[R]` the tap legs' `tap_link`/`tap_link_wait_s` values are
unchanged by the fold (D6). **Disclosed caveat** (see F1): the validation
never verified *which* sink the monitor belongs to — the parameter was the
hook for that check.

### T5 — the `hit` half of two `cls, hit =` unpacks is a dead store `[S][R][D]`

**(a) Change** `:22218` (`_pactlmon_r85_cap_leg`) and `:22304`
(`_pactlmon_r85_sd_leg`) from `cls, hit = _pactlmon_r85_errclass(err)` to
`cls, _ = …`.

**(b) Proof.** `[S]` of the four `hit`-binding sites in the r85 block
(`:21757`, `:22218`, `:22304`, `:23663`), only these two never load `hit`
(S5). The live one is `_pactlmon_r85_run`
(`:21757` → `rec["error_hit"]`, 1 load); the negctl unit table
(`got, hit = …` `:23663`, load `:23665`) and `ctl_sigkill`'s `khit` are
separate bindings and are retained. `[D]` D3/D4: **byte-identical leg dicts**.

**(c) Receipts.** `[R]` R4: **no** capture-side leg record in either run
carries a `hit` or `error_hit` key (17 leg records × 2 runs); the live
`error_hit` records are `ctl_pactl_info`/`ctl_pwdump`/`ctl_pwcli_ser`/
`ctl_sigkill`, and the 13 unit-table legs carry `hit`. No key or value change.

### T6 — the `sers` binding in the addr entry is a dead store `[S][R][D]`

**(a) Change** delete `:22738–22739`
`sers = [s for s in entry["serial_cycles"]["serials"] if s is not None]`.

**(b) Proof.** `[S]` `sers` stores = {22738}, loads = {} (S6). The
monotonicity check immediately below reads the loop-local `serials`
(`:22740–22743`), not `sers`. `[D]` D8 replays the check slice from both
copies over six synthetic `(serials, serial_cycles)` cells: **identical
failure lists and identical exception behaviour** (incl. the `None`-in-list
`TypeError` cell).

**(c) Receipts.** `[R]` R6: no receipt key named `sers`; `entry["serial_cycles"]`
is the recorded surface and is untouched (both runs: `serials` strictly
increasing, module index recycled ×3).

### T7 — `lp = link_ports("t_prop_srcname")` is a dead store `[S][D]`

**(a) Change** delete `:23510`.

**(b) Proof.** `[S]` `lp` stores = {23497, 23504, 23510}, loads =
{23498, 23500, 23502, 23505, 23506, 23508} — the **last store has no load
after it** (S7); the next statement binds `pl` from the same leg and every
subsequent check reads `pl`. `link_ports` is a pure local closure over `legs`
(no I/O), so the fold removes one pure call. `[D]` D9: identical failure lists
in three leg-shape scenarios; **exactly one fewer `link_ports()` call**
(5 → 4) — disclosed.

**(c) Receipts.** `[R]` R6: no receipt key named `lp`.

### T8 — `want_node` is a dead loop payload `[S][R][D]`

**(a) Change** `:23491–23496` the 6-line header
`for nm, want_node in (("t_srcname", PACTLMON_R85_VSRC + "b"), …)` →
`for nm in ("t_srcname", "t_srcserial", "t_srcid"):`.

**(b) Proof.** `[S]` `want_node` stores = {23491}, loads = {} (S8); the body
loads only `nm` and `lp`. `[D]` D9 replays the whole slice (three legs + the
`t_prop_sinkname`/`t_prop_srcname` checks) with a counting `link_ports` stub:
identical failure lists in all three scenarios. **Disclosed + escalated as
F2/B7**: the dead values encoded an `out_node == VSRC+"b"` expectation that
the receipts **contradict** — the lattice legs measure bindings on the
*original* `r85a_vsrc_<pid>` (`r85a_vsrc_2546640:capture_*`), never on
`…vsrcb`; a revived check would fail both pinned runs.

### T9 — the entry-local `gsv` closure's `label` is never read `[S][D]`

**(a) Change** `:22487` `def gsv(arg, label):` → `def gsv(arg):` and drop the
label at all **20** call sites (`:22490–22512`).

**(b) Proof.** `[S]` the body is a single
`return _pactlmon_r85_pactl("get-sink-volume", arg)`; **zero** `label` loads
(S9), 20/20 call sites supply it. `[D]` D7 extracts the whole `gsv` slice
(def + 20 calls) from both copies and executes it against a recording stub:
**identical `legs` dict and identical 20-entry pactl argv list**. The
contrasting sibling `gsvo(arg)` (`:22514`) has no label at all — the labels
were decoration. **Tier C, separable** (the operator may prefer to keep the
labels as mirror vocabulary; 21 changed lines).

**(c) Receipts.** `[R]` R6: no receipt key named `label`; the recorded
`stdout`/`exit_code`/`error_class` of the 20 `g_*` legs are unchanged.

### T10 — `_pactlmon_r85_teardown`'s guards are dead (required positional) `[S][R][D]`

**(a) Change** `:22353` `(loads or {})` → `loads`; delete `:22354`
`leaf = leaf or {}`; `:22367`/`:22383` `(loads or {})` → `loads` and
`(l or {})` → `l` (`:22368`, `:22384`); `:22400` `or n in (loads or {})` →
`or n in loads`.

**(b) Proof.** `[S]` `_pactlmon_r85_teardown(entry, failures, loads)` has **no
defaults** (S10) and its five call sites (`:22746`, `23001`, `23143`, `23613`,
`23701`) all pass a local `loads` dict. Every value ever stored into a
`loads[...]` slot in the r85 block is a **dict**: `_pwcat_r83_ns_load` returns
`leaf` on **2/2** paths (both dict literals, `:16644`/`:16649`), and
`_pactlmon_r85_remap_load`/`_pactlmon_r85_sd_load`/`dict(dup, …)`/
`lb_leg["late_load"]` likewise (S11, 16 value assignments + 13 key mutations).
So `(loads or {})` ×4, `leaf = leaf or {}` and `(l or {})` ×2 can never select
their fallback. `[D]` D1 runs the real teardown with stubbed readers/unload for
four `loads` shapes (incl. a leaf without `field`/`value` and one with extra
keys): **identical entry, identical failure list, identical unload call list**.

**(c) Receipts.** `[R]` R3: all **13** `unloads` records per run are dicts
(26/26); every `sinks_gone`/`sources_gone` value is `true`; `own_nodes_after`
is `[]` on all 5 entries ×2 runs.

### T11 — `_pactlmon_r85_block`'s `leaf = leaf or {}` is dead; its `loads` guard is LIVE `[S][R][D]`

**(a) Change** delete `:22412` `leaf = leaf or {}` only.

**(b) Proof.** `[S]` `_pactlmon_r85_block(entry, failures, msg, loads=None)`
**has** a default and **5 of its 11 call sites omit `loads`** (`:22442`,
`22765`, `23018`, `23164`, `23631`) — so `(loads or {})` at `:22411` is a real
path and is **retained** (S10; the same asymmetry r84 folded on the teardown
side only). The `leaf` guard is dead for the same dict-domain reason as T10.
`[D]` D2: identical entry/failure/kill lists for a dict `loads`, `loads=None`
and `loads={}`.

**(c) Receipts.** `[R]` R1: no `blocked`/`coverage_blocked` surface is
realized in either run (both runs green), so the retained guard has no
receipt cost.

### T12 — four subsumed `(aN or {})` guards `[S][D]`

**(a) Change** `:22682` `(a1 or {}).get('sink')` → `a1.get('sink')`;
`:22688` and `:22693` `(a2 or {})` → `a2`; `:22703` `(a4 or {})` → `a4`.

**(b) Proof.** `[S]` each name is bound on the preceding line by
`… or {}` (`a1` `:22678`, `a2` `:22684`, `a4` `:22699`) — a strict
short-circuit subsumption on the dict domain, exactly the r84-T7 shape ×4
(S12). `[D]` D11 renders both forms over `{}`, `{'sink': None}`,
`{'sink': 0}`, `{'sink': 4294967295}`, `{'sink': 77}`, `{'index': 5}`:
**identical strings**, so even the failure-message text is unchanged.

**(c) Receipts.** `[R]` these strings only appear on the failure path, which
is not realized in either run (`failures: []`); no receipt surface.

### T13 — `_pactlmon_r85_vol_pct`'s `(rec or {})` is dead `[S][R][D]`

**(a) Change** `:22424` `(rec or {}).get("stdout")` → `rec.get("stdout")`.

**(b) Proof.** `[S]` all **7** call sites (`:22616`, `22617`, `22634` ×2,
`22638`, `22649`, `22650`) pass a leg dict produced by
`_pactlmon_r85_run`/`_pactlmon_r85_pactl` (always a dict) or a local bound to
one (S13). `[D]` D5: identical pct over the rec domain
(`{}`→None, `100`, `50`, `""`→None, no-percent→None).

**(c) Receipts.** `[R]` the `g_*`/`s_*` volume rows are compared across legs in
the entry's own arms; the folded copy's comparisons are identical (D5).
**Disclosed caveat**: `rec=None` would now raise instead of returning `None` —
unreachable from the call graph (7/7 dict arguments).

### T14 — the pre-ladder `feeder is not None` conjunct is dead `[S][D]`

**(a) Change** `:23272` `if feeder is not None and feeder.poll() is None:`
→ `if feeder.poll() is None:`.

**(b) Proof.** `[S]` `feeder = _pactlmon_r85_play(…)` at `:23190` is
unconditionally reached before the guard inside the same inner `try`; the only
way to skip it is an exception, which also skips the guard (it propagates to
the `finally`). The **`finally` site at `:23610` is LIVE** (an exception
before `:23190` leaves `feeder=None`) and is retained (S14). `[D]` D10:
identical kill decisions for an alive and an already-dead fake process.

**(c) Receipts.** `[R]` no receipt surface (a control-flow guard). **Disclosed
caveat**: the folded form would raise `AttributeError` on a `None` feeder —
unreachable, as argued.

## 3. The three host-bimodal realizations — either-way verification (the round's special ask)

The task asks to verify that `latebind`, `cdup_cap` and `sd_prop` are pinned
as **either-way**, not silently absorbing. `proofs/bimodal-arms.py` extracts
each committed classifier + failure predicate **verbatim** and executes it
over synthetic leg states for **both hosts' sides** and for the broken states
(`proofs/bimodal-arms.txt`, B1–B7, **7/7 PASS**).

| arm | side A (authoring host, realized) | side B (boundary host) | broken states that still FAIL | either-way? |
|---|---|---|---|---|
| `latebind` `:23589–23608` | `late_bound` (links → the late source's own `capture_*`) | `stalled` (never re-armed) / `refused` | `foreign_bind` (monitor or foreign node), `other` | **YES** |
| `cdup_cap` `:22706–22737` | `serial_monitor_bypass` (digits → the serial holder's monitor) | `name_shadow_bound` / `stalled` / `refused` | `foreign_monitor`, `other` | **YES for the two named sides** — with the ADJ-3 channel below |
| `sd_prop` `:23545–23575` | `bind_killed_then_default` | `clean_default_fallback` | non-monitor links, monitor links not on the default sink, vacuous (no links + module alive) | **YES** |

Receipts confirm the realized side in both runs (R5): `cdup_cap`
`serial_monitor_bypass`, `latebind` `late_bound`, `sd_prop`
`bind_killed_then_default`; the phase realizations *do* vary run-to-run
(`mixdup` `coherent_2x`↔`partial`, `mixdelay` `partial`↔`cancelled`,
`mixinv` `slipped`) — exactly the volatile surface the boundary warned about —
while every armed verdict is identical.

**Absorption channels that remain (B6) — reported, not folded.** The
either-way property holds for the two *named* sides, but the same predicates
also accept these third states (each confirmed by executing the committed
slices):

| channel | committed branch | executed result |
|---|---|---|
| `cdup_cap`: a **foreign** node's `capture_*` links | `elif cl_links:` → `name_shadow_bound` (`:22724–25`) has no `out_node` constraint | realization `name_shadow_bound`, **0 failures** |
| `t_srcname`/`t_srcserial`/`t_srcid`: a **foreign** node's `capture_*` links | the arm checks only the `capture_` port prefix | **0 failures** |
| sd connect-kill: the trap **never existed** (module "dead" at t≈0) | `module_dead_at_s` ≤ 1.5 passes | **0 failures** (the `None`/`2.5`/content-before-death states correctly fail) |
| `mixdup`/`mixdelay`/`mixinv`: a **single** stream (ratio 1.0) | only the ≤2.05 upper bound is armed | `partial`, **0 failures** |

These are the same channels the r85-critic (F1/F2/F3, committed `8ae131e6`)
and the r85-scribe (ADJ-3, committed `972202bf`) raised during this seat's
window; this seat's B6/B7 **independently re-derive and execute** them from
the pinned blob. They are arm-looseness findings for the operator, not dead
code, and are deliberately **not** folded (fixing them changes behaviour).

## 4. Checked and NOT dead (explicitly cleared)

- **`_pactlmon_r85_block`'s `(loads or {})`** (`:22411`) — live: 5 of 11 call
  sites omit `loads` (S10). Retained.
- **The live `hit` bindings** — `_pactlmon_r85_run` (`error_hit`), the negctl
  unit table (`hit`, 13 legs), `ctl_sigkill`'s `khit`. All recorded (R4).
- **`_pactlmon_r85_edges_out`** — 1 call site (the `sd_pwlink` leg). Live.
- **`PACTLMON_R85_LINK_WAIT_S`** (3 refs), **`TAP_WAIT_S`** (1), **`FEED_S`**
  (1), **`AMP`** (2), **`SOLO_ENV`/`BLEED_MAX`/`DUP_ENV`/`CLIP_AMP`/`RAIL_ENV`/
  `SPUR_MIN`/`FLUSH_BOUND`** (2–4 each) — every constant used by an armed arm.
- **`_pactlmon_r85_family_lock`** — held to exit; the mutex-sum guard is live.
- **The teardown `skipped: not_listed` path** (`_pactlmon_r85_unload_own`) —
  live and *realized*: the capture entry's `cap_loss_prop` leg unloads the tone
  sink mid-entry, so the teardown re-read correctly reports
  `verified_index: null / skipped: not_listed` for `r85a_tone_<pid>` in both
  runs while `sinks_gone` is `true`. Not dead code — the name-verified
  re-read is the guard that makes stale-index firing impossible.
- **The 0-hit falsification arms** — `g_lead0` (record-only, `armed: False`,
  rc1 `pa_get_info_noent` ×2), `mv_bogus` refuse-and-stay, `t_sinkname`
  refusal side, `latebind` stall side, `sd_prop` clean-fallback side,
  `cdup_cap` name-shadow side, the `mixdup`/`mixdelay`/`mixinv` phase
  realizations, the `cap_loss` flush shapes (`grew_content` 2048f ×1/×2,
  `froze` ×1), `env_bogus`/`env_none` silent-default fallbacks: all are the
  envelope the round deliberately armed (they realize on a different host
  state), not dead code.
- **Wiring** — `--probe-pactlmon-r85` is consumed by all five surfaces
  (parser `:23854`, mutex sum `:23862`, dispatch `:24220`, mode `:24870`,
  suffix `:24890`); the mutex sum has **129 terms, no duplicates**, and the
  new term is present (S15). No dead config key.
- **Namespacing** — all 34 module-level r85 defs match
  `_pactlmon_r85_*`/`pactlmon_*_r85_*` and are unique file-wide (S16); the
  entry-local closures (`gsv`, `gsvo`, `noent`, `to_sink`, `tap_ok`,
  `links_of`, `link_ports`) are function-scoped and intentional.
- **Classifier table** — all 13 unit cases present, both family-local classes
  (`pa_invalid_arg`, `pwcli_unknown_global`) covered, 4 must-classify-nothing
  cells (S18).
- **The r85 evidence leaves** (`contention`, `oracle_at_start`, `inventory`,
  `loadavg`, `tools`, `ns_props`, `sink_index`, `serial_cycles`, `vsrc`,
  `samples`, `size_at_loss`, `post`, `realization`, `sd_module_gone_after`,
  `grid`, `late_load`, `out`, `target_candidates`, …) — the family's
  honest-leaf convention (recorded, not gated). No deletion.
- **Consolidation candidates (considered, declined)** — the two load helpers
  (`remap_load`, `sd_load`) share a poll/gate shape, and `_pactlmon_r85_edges*`
  re-implement r84 shapes; merging them would touch live call graphs and is a
  refactor, not a YAGNI deletion with a zero-delta proof (r84 §3 precedent).

## 5. Below the bar (reported, retained)

- **Never-supplied knobs that are bounds and feed live expressions**:
  `_pactlmon_r85_pactl.timeout_s` (0/6), `_pactlmon_r85_run.env` (0/8),
  `_pactlmon_r85_amps.win_s`/`skip_s` (0/6), `_pactlmon_r85_med.lo`/`hi`
  (0/17), `_pactlmon_r85_play.role` (0/3 — the private-restore-key default is
  load-bearing), `_pactlmon_r85_cap_leg.out_name` (0/13 — a live path knob
  with a receipt surface, `leg["file"]`), `_pactlmon_r85_tone.amp` (3/7) /
  `invert_both` (1/7), `_pactlmon_r85_killpg.sig` (3/11). Retained: each is
  the family's documented bound and the r83/r84 §4 precedent.
- **`_pactlmon_r85_edges_in` vs `_pactlmon_r85_edges_out`** — the `_in`
  helper filters `in_node`, the `_out` helper filters `out_node`; both are
  used (4/1 call sites). No duplication to remove.

## 6. Findings for the operator (reported, NOT folded — deletions/fixes would change behaviour)

- **F1 — the tap validation never verifies *which* sink the monitor belongs
  to.** `_pactlmon_r85_wait_tap_link` (`:22043–22059`) and the mix entry's
  `tap_ok` (`:22830–22844`) accept any link set whose out-port name starts
  with `monitor_`; the `sink` parameter that could have constrained the
  `out_node` was never read (T4). A tap accidentally linked to a *foreign*
  sink's monitor would pass the §2.1 hazard gate. T4 is a separable hunk if
  the operator prefers to keep the parameter and add the constraint.
- **F2 — the source-bind arm checks the port *shape*, not the node** (the
  critic's F1 shape). The `t_srcname`/`t_srcserial`/`t_srcid` loop's
  `want_node` (T8) encoded `out_node == VSRC+"b"` but was never read; the
  executed receipts bind the **original** `r85a_vsrc_<pid>`
  (`r85a_vsrc_2546640:capture_*`), never `…vsrcb`. Reviving the check would
  therefore **fail both pinned runs** (B7) — the stale intent must be
  re-derived, not re-enabled. The arm currently also accepts a foreign node's
  `capture_*` links (B6).
- **F3 — the `sd_*` legs are the only r85 legs with no redaction pass.**
  Their recorded `argv` carries the raw TMPDIR path
  (`…/tmp/r85a-cap-XXXX/sdr.wav` in both runs), unlike every other leg which
  redacts via `_capture_tail(err, str(out))`/`ctx["redact"]` (r84-F3 shape).
  T3 removes the parameter that would carry a redaction; a future call site
  putting a path into `tail` would be recorded verbatim.
- **F4 — `cdup_cap`'s `name_shadow_bound` branch has no `out_node`
  constraint** (the scribe's ADJ-3, independently reproduced in B6): the block
  comment claims "the digits never resolve a foreign target", but any
  non-monitor link set is accepted, including a foreign node's `capture_*`.
  Both *named* host sides are still correctly either-way (§3).
- **F5 — the connect-kill arm accepts "the module never existed"** (the
  critic's F2, reproduced in B6): `module_dead_at_s` is initialized on the
  first grid sample, so an absent trap reads as "died at t≈0" and passes.
  Only the `None` (survived), `>1.5 s` (died late) and
  content-before-death states fail.
- **F6 — the mix phase arms bound only the upper side** (the critic's F3,
  reproduced in B6): a single stream (ratio 1.0) is classified `partial` and
  passes, so `mixdup` cannot distinguish "summed" from "one player never
  landed".

## 7. Blockers

- None for this seat. `/tmp` remains near quota → all scratch work used
  `TMPDIR=/home/vgpnk/Projects/shokunin/tmp`, and everything material lives
  under `corpus/live/r85-simplifier/` (the receipts are 6.6 MB; the two
  195 KB receipt copies were read in place, not duplicated).
- No fresh full-family replay (live-host + family-lock cost, sibling seats
  committing concurrently); the two pinned author runs are the oracle and
  were re-verified (8/8).
- The `lsp` device is unavailable on this substrate (recorded); no
  symbol-aware operation was needed for this patch (it renames nothing).
- The tracked `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`
  remains dirty from r84 (pre-existing, also flagged by the scribe seats);
  this seat left it exactly as found.

## 8. Verdict

**PASS** — the r85 landing is clean; **14 provably dead items**, net **−22
lines**, delivered unapplied with **19/19 static, 8/8 receipt, 13/13
differential and 7/7 either-way/absorption** proofs plus a byte-identical
patch round-trip and an independent labrat NOT-FALSIFIED sweep (14/14).
No verdict, no receipt key and no receipt value changes. The three
host-bimodal realizations are **pinned either-way** (both named host sides
pass; broken states still fail); the residual absorption channels (F1–F6,
matching the critic's F1–F3 and the scribe's ADJ-3) are **arm-looseness
findings for the operator**, not dead code, and are deliberately not folded.
The fold decision (and F1–F6) belongs to the operator.
