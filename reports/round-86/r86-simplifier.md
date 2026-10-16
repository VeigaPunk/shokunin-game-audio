# r86 SIMPLIFIER — YAGNI/dead-code review of the `fa5994a0` r86 landing (read-only, patch NOT applied)

**Seat** simplifier (r86) · **host** devin · **scope** the r86 pwctl
landing only: `git show fa5994a0 -- corpus/fixtures/measure_audio.py`
(**+1761/−3**; family block `:23730`–`:25451`, **1722 lines**, 5 entry
functions / 149 legs / 25 module-level r86 defs + 19 r86 constants)
plus its wiring hunks (import, `add_argument`, mutex sum, dispatch
block, mode/suffix ternary heads). **Writes**: this report +
`corpus/live/r86-simplifier/` only. **Zero tracked writes, no commit,
the patch is NOT applied.**

## Custody / tree state at report time

- Analysis base = the **commit-pinned blob**
  `git show fa5994a0:corpus/fixtures/measure_audio.py`, sha256
  **`5ceba94019eaaa8f1db9ac18ea15023f7e4891e844defe86711f37873059b780`**
  (26655 lines), copied byte-identically to `proofs/base-measure_audio.py`
  (`proofs/sha256.txt`). Every line number in this report is a
  **fa5994a0-pinned** line number. The author report's own source sha is
  the same value — the pin is self-consistent.
- **The working tree MOVED under this seat** (HEAD advanced
  `fa5994a0` → r86 scribe/critic/verifier/reviewer, now `44c083cd`) and
  is *not* the analysis base; the deliverable is anchored to the pin.
  `corpus/fixtures/measure_audio.py` is **byte-identical** between the
  working tree, `HEAD` and the `fa5994a0` pin (`git diff --numstat HEAD
  -- corpus/fixtures/measure_audio.py` empty; sha256 `5ceba940…` on all
  three), so `git apply --check` of the patch against the live tree is
  clean and the fold is applicable as-is.
  The only dirty tracked path is the pre-existing
  `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` (also
  flagged by the r84/r85/r86 scribe seats) — **not touched by this
  seat**; every compilation/import here happened on scratch copies under
  `corpus/live/r86-simplifier/proofs/`.
- **No `lsp` device answers this file on this substrate** (the only
  external device is the `rea` Ghidra/native-REA MCP, whose subject
  format has no Python source). **Recorded unavailable**; no
  symbol-aware rename/edit was performed (this seat performs no renames
  — all edits are exact-string folds), so the `lsp` fallback rule is not
  engaged. All reference proofs are literal AST/symtable/`grep` censuses
  over the pinned blob plus **module loads** (importlib) of the pinned,
  folded and shipped copies.
- **probeParent**: exactly **one** read-only `ufo-labrat` was dispatched
  (agent `cb5ec686`; verbatim report at `proofs/labrat-probe.txt`). It
  reported **NOT-FALSIFIED on all three hypotheses** (H1 `self_serials`
  write-only, H2 fixed-path lock, H3 dead constants) with zero files
  created/modified and no exec capability on its substrate.
- **No fresh full-family replay.** The r86 family is live-host data
  (PipeWire 1.6.8 / WirePlumber 0.5.17 / pactl 17.0 on a loadavg ~85
  host with sibling wave-B seats running, incl. live r86 family runs);
  a folded replay would need the host, the 149-leg wall time and the
  lane lock, and would perturb siblings. The **two pinned author runs
  are the replay oracle** and their verdict surfaces are re-verified
  here (`proofs/receipt-census.txt`, 32/32; 149 legs ×2, `failures: {}`).
- Sibling wave-B seats committed during the window (r86 scribe
  `55ed1641`, critic `14b8ebdc`, verifier `caafa1c2`, reviewer
  `44c083cd`). Their findings are **not adopted on citation**; where my
  independently-derived results converge, the convergence is noted.

**Proof classes used below** — `[S]` static reachability over the pinned
blob (AST/symtable/word-boundary census, dominance walk, executed source
slices), `[R]` receipt census across **both** pinned runs, `[D]` executed
differential base-vs-folded on scratch imports with stubbed I/O
(20 checks), `[L]` lock proof (static + two-process cross-TMPDIR
serialization, 14 checks), `[SD]` symtable symbol-set diff (4 checks),
`[P]` `patch -p1` round-trip byte-identity + `git apply --check`.

## 0. Summary

**Verdict: PASS (gate green, no blocker).** The r86 landing is
insertion-only, structurally clean, correctly wired (five dispatch
lines, one add_argument, one mutex term, two ternary heads; no
duplicates) and its dead-code surface is **small and tight**: **9
provably dead items** delivered as **13 fold edits**, `git apply
--numstat` **+7/−18 → net −11 lines** (26655 → 26644), all inside the
family block, as an **unapplied 11-hunk patch**. Every item carries a
static reachability proof, a receipt census where it has a receipt
surface, and an executed differential; **no item changes any verdict, no
receipt key and no receipt value**.

| # | item | class | base lines | Δ | proofs | tier |
|---|---|---|---|---|---|---|
| T1 | `PWCTL_R86_LINK_WAIT_S` unused constant | dead constant | 23852 | −1 | S,D | A |
| T2 | `PWCTL_R86_TAP_WAIT_S` unused constant | dead constant | 23853 | −1 | S,D | A |
| T3 | `self_serials` dead accumulator (init + 2 appends) | dead store | 24327, 24343–24345, 24350 | −5 | S,D,R,SD | A |
| T4 | `_pwctl_r86_teardown` `(loads or {})`×3 + `leaf = leaf or {}` | dead guard | 24167, 24168, 24181, 24196 | −1 | S,D,R | B |
| T5 | `_pwctl_r86_block` `leaf = leaf or {}` (loads guard **retained**) | dead guard | 24229 | −1 | S,D | B |
| T6 | `_pwctl_r86_own_links` subsumed `(l["out"] or "")`/`(l["in"] or "")` | redundant guard | 24067–24068 | ±0 | S,D | B |
| T7 | dsp unreachable `tap_link` verdict (early return dominates) | unreachable code | 24922–24923 | −2 | S,D | B |
| T8 | dsp `solo_hi` dead `None` init (overwritten before any read) | dead store | 24837 | ±0 | S,D | C |
| T9 | addr `ser in (None, "None")` dead `None` member (`ser` is `str`) | dead guard | 24283 | ±0 | S,D | C |

Totals: **+7/−18 across 11 hunks → net −11 lines** (26655 → 26644),
**13 replacement sites**, every hunk inside the r86 family block
(min old-side start 23849 ≥ 23730; max old-side start 24919 < 25451).
`git apply --numstat`: `7 18 corpus/fixtures/measure_audio.py`.

**Tier A** = never-executed code with no receipt surface. **Tier B** =
verdict-superseded / logically subsumed predicate with a **provably**
zero behavioural delta (including message text). **Tier C** = dead
guards/stores, provably unreachable from the current call graph —
separable hunks the operator may retain as mirror vocabulary.

## 1. Deliverable

- `corpus/live/r86-simplifier/r86-simplifier.patch` — sha256
  **`5cc93d42cb77288c5877ad63db22e6c8011c86481df1f22ac42d5414306dccf7`**,
  11 hunks, `git apply --check` **clean** against the live working tree
  *and* `patch -p1` clean against the commit-pinned blob; a fresh
  `patch -p1` over a scratch copy is **byte-identical** to the folded
  copy (`proofs/patch-check.txt`). **Not applied.**
- `corpus/live/r86-simplifier/proofs/folded/measure_audio.py` — sha256
  **`e35b0c2636b28ce292a20a27960f1179a08ff6af309657fe404337a73dc50c1b`**,
  26644 lines; `python3 -m py_compile` + `ast.parse` clean
  (`proofs/pycompile.txt`).
- `corpus/live/r86-simplifier/proofs/` — the pinned base copy, the r86
  block extract, the r86 landing diff, `fold-r86-simplifier.py` +
  `fold-apply.txt` (**13** exact-match replacements, each asserted to
  match **exactly once**; the two *homographs* shared with the r83/r84
  families — `gone = {nm: …}` and `or n in (loads or {})` — were caught
  by the 0/multi-match abort and folded **inside their function region**
  so the r83/r84 copies stay byte-identical),
  `static-proofs.py/.txt` (S1–S13, **43/43 PASS**),
  `differential.py/.txt` (D1–D8, **20/20 PASS**),
  `receipt-census.py/.txt` (R1–R9, **32/32 PASS**),
  `lock-proof.py` + `lock-worker.py/.txt` (L1–L5, **14/14 PASS**),
  `symdiff.py/.txt` (**4/4 PASS**), `symscan.py/.txt`,
  `deadscan.py/.txt`, `legcensus.py/.txt`, `legcensus2.py/.txt`,
  `labrat-probe.txt`, `sha256.txt`, `patch-check.txt`,
  `pycompile.txt`, `cli-check.txt` (help + probe-mutex wiring).
- `corpus/live/r86-simplifier/manifest.json` + `manifest.sha256` —
  sha256 census of all 37 seat files; `proofs/run-all.sh` reproduces
  every artifact end-to-end (rc=0, `proofs/run-all.log`).

## 2. Items — remove / proof / receipts

### T1/T2 — `PWCTL_R86_LINK_WAIT_S` and `PWCTL_R86_TAP_WAIT_S` are never referenced `[S][D]`

**(a) Change** delete `:23852` `PWCTL_R86_LINK_WAIT_S = 5.0` and
`:23853` `PWCTL_R86_TAP_WAIT_S = 6.0`.

**(b) Proof.** `[S]` whole-file word-boundary census: each symbol occurs
**once** (its own definition, `uses=0`); the labrat independently
re-derived the same census. The sibling the r86 family kept for exactly
this purpose, `PWCTL_R86_STREAM_WAIT_S` (`:23854`), has **2** occurrences
(1 definition + 1 load at `:24805` in the dsp player-attach wait) — the
contrast proves these two are copy-paste leftovers, not knobs with live
defaults. `[D]` D8: the folded module's `PWCTL_R86*` attribute delta is
exactly `{LINK_WAIT_S, TAP_WAIT_S}` and nothing else.

**(c) Receipts.** `[R]` R4: **0 occurrences** of `LINK_WAIT`/`TAP_WAIT`
(and of the full names) anywhere in either pinned receipt. No receipt
surface at all.

### T3 — the `self_serials` accumulator is write-only `[S][D][R][SD]`

**(a) Change** delete `:24327` `self_serials = []`, the 3-line
`:24343–24345` `self_serials.append({s for s in …})`, and `:24350`
`self_serials.append(set())` — **not** the recorded dict key
`"self_serials"` at `:24340` (that is `legs["dump_fullN"]["self_serials"]`,
built independently from `selfs`).

**(b) Proof.** `[S]` whole-file census: the name `self_serials` occurs 5×
(1 init, 2 appends, 2 continuation lines of the first append); its only
value-producing uses are the two `append` calls, and **no read of the
accumulated value exists** (this seat's own `legcensus.py`/`legcensus2.py`
arm census finds no consumer; the labrat re-derived the same
5-occurrence census and confirmed the receipt key is built from `selfs`,
never from the accumulator). `[D]` D5 executes the
extracted `dump_full` loop slice against a stubbed `pw-dump` JSON in both
copies: **identical `legs` dicts** (`dump_full1/2.self_serials ==
["243277"]`), base keeps a dead accumulator, folded has none. `[SD]` SD3:
symtable shows the removed symbol closure is exactly
`{self_serials, s, set}` in `pwctl_addr_r86_entry` and nothing anywhere
else; SD2: no new unread name is introduced.

**(c) Receipts.** `[R]` R3: both runs record
`dump_full1/2.self_serials` (`[['242898'],['242899']]` and
`[['243277'],['243278']]`) — values the fold does not touch; R3 also
shows `self_clients >= 1` on all 4 reps. **Disclosed**: the r86-critic's
F3 ("serial-freshness recorded but never compared") remains true after
this fold — the recorded key survives; only the unused copy is deleted.

### T4 — `_pwctl_r86_teardown`'s guards are dead (required positional) `[S][D][R]`

**(a) Change** `:24167` `for tag, leaf in (loads or {}).items():` →
`for tag, leaf in loads.items():`; delete `:24168` `leaf = leaf or {}`;
`:24181` `for nm in (loads or {})` → `for nm in loads`;
`:24196` `or n in (loads or {})` → `or n in loads`.

**(b) Proof.** `[S]` `_pwctl_r86_teardown(entry, failures, loads,
meta_subject=False)` has **no default** for `loads` (S3: 4 positional
params, 1 default, `loads` is the third) and its five call sites
(`:24370`, `:24621`, `:24920`, `:25093`, `:25311`) all pass a local
`loads` dict. Every value ever stored into a `loads[...]` slot in the r86
block is a **dict**: the only writer is `_pwctl_r86_load_ns()`
(5/5 entries), which returns `_pwcat_r83_ns_load(PWCTL_R86_NS)` with
`field`/`value` added, and `_pwcat_r83_ns_load` returns `leaf` on
**2/2** paths (both dict literals, S5). So `(loads or {})` ×3 and
`leaf = leaf or {}` can never select their fallback. `[D]` D1 runs the
real teardown with stubbed readers/unload for 4 `loads` shapes (incl. a
leaf without `field`/`value`) × 3 sink-reader values × 2 node-reader
values, plus the `meta_subject` clean and leftover paths: **identical
entry, identical failure list, identical unload call list** (11/11
comparisons).

**(c) Receipts.** `[R]` R2: all **10** `unloads` records (5 entries ×2
runs) are dicts with `verified_index == captured` and `recycled: False`;
every `sinks_gone` value is `true`; `own_nodes_after` is `[]` on all 5
entries ×2 runs. No key or value changes.

### T5 — `_pwctl_r86_block`'s `leaf = leaf or {}` is dead; its `loads` guard is LIVE `[S][D]`

**(a) Change** delete `:24229` `leaf = leaf or {}` only.

**(b) Proof.** `[S]` `_pwctl_r86_block(entry, failures, msg, loads=None)`
**has** a default and **5 of its 15 call sites omit `loads`**
(S4: `without=5 with=10`) — so `(loads or {})` at `:24228` is a real path
and is **retained** (the same asymmetry r85 folded on its teardown side
only). The `leaf` guard is dead for the same dict-domain reason as T4.
`[D]` D2: identical entry/failure/unload-call tuples for `loads=None`,
`loads={}`, and three dict leaves.

**(c) Receipts.** `[R]` R1: no `blocked`/`coverage_blocked` surface is
realized in either run (both runs green), so the retained guard has no
receipt cost.

### T6 — two subsumed `(l[...] or "")` guards `[S][D]`

**(a) Change** `:24067–24068` `(l["out"] or "").startswith(sink + ":")` →
`l["out"].startswith(sink + ":")` and likewise for `l["in"]`.

**(b) Proof.** `[S]` every leaf consumed by `_pwctl_r86_own_links` is
built by `_pwctl_r86_links` (`:24031–24057`) as
`f"{nodes.get(…)}:{ports.get(…)}"` — S6 asserts both keys are
`JoinedStr` in the AST, so the value is always a **non-empty `str`**
(it always contains `":"`), never `None` and never falsy. The guard is a
strict short-circuit subsumption, the r85-T12 shape ×2. `[D]` D3:
identical filtered lists on the reachable domain (incl. `"None:None"`
endpoints) and identical `None` propagation on reader failure.
**Disclosed**: for an out-of-domain leaf with `out=None` the folded form
raises `AttributeError` where the base filtered it — unreachable from
the call graph (D3 records this divergence explicitly).

**(c) Receipts.** `[R]` R6: the three recorded censuses
(`self_loop_census`, `lk_census`, `lk_junkprops_census`) carry the same
leaf lists; the fold changes no recorded value.

### T7 — the dsp `tap_link` verdict is unreachable `[S][D]`

**(a) Change** delete `:24922–24923` (`if not legs["tap_link"]["edges"]:
failures.append("tap_link: the monitor tap never validated")`).

**(b) Proof.** `[S]` dominance walk (S7): `:24792`
`legs["tap_link"] = {"edges": edges, …}` < `:24793` `if not edges:` <
`:24797–24800` `return _pwctl_r86_block(entry, failures, "monitor tap
never linked — dsp arms skipped", loads)` < `:24922` the verdict. The
`return` inside the `try` executes the `finally` and **exits the
function**, so any execution reaching the post-`finally` verdicts has
`edges` truthy and the verdict can never fire. `[D]` D4 extracts the
early-return slice from both copies (byte-identical) and executes it:
`edges=[]` → early return, `edges=[…]` → falls through; the base verdict
snippet adds **no failure** on the reachable domain and the folded copy
has no such branch. **Disclosed**: on the unreachable `edges=[]` domain
the base would append a (redundant) failure message; the `coverage_blocked`
record `"monitor tap never linked — dsp arms skipped"` is produced by the
early return either way, so no receipt value changes.

**(c) Receipts.** `[R]` R5: both runs have all eight `regions` with solo
`8192.0` in the x8192 envelope; no `failures`/`coverage_blocked` entry
depends on the deleted verdict.

### T8 — dsp `solo_hi` dead `None` init `[S][D]`

**(a) Change** `:24837` `solo_lo, solo_hi = mark(), None` →
`solo_lo = mark()` (the real assignment `solo_hi = mark()` at `:24839`
is kept).

**(b) Proof.** `[S]` between the two lines there is only
`sleep_to(solo_lo + 0.6)`; `solo_hi` is first read at `:24904`
`regs = {"solo": (solo_lo, solo_hi)}` — after the real assignment, so the
`None` is a dead store. `[D]` D6 executes both forms with fake
`mark`/`sleep_to`: **identical `(solo_lo, solo_hi)`**.

**(c) Receipts.** `[R]` R5: `regions.solo.t` / `median_peak` are
computed from `mark()` values only; both runs' solo windows
(`[1.11,1.71]`, `[1.1,1.7]`) and `median_peak 8192.0` are unchanged.

### T9 — `ser in (None, "None")` has a dead `None` member `[S][D]`

**(a) Change** `:24283` `if nid is None or ser in (None, "None"):` →
`if nid is None or ser == "None":`.

**(b) Proof.** `[S]` S9: `ser = str(na.get("object_serial"))` on the
preceding line — `str(...)` never returns `None`, so the tuple's `None`
member is dead; `str(None) == "None"` keeps the original missing-serial
behaviour. `[D]` D7 evaluates both predicates over the reachable str
domain `{str(None), "0", "1", "None", "abc", "99999"}`: **identical
branch decisions**.

**(c) Receipts.** `[R]` R8: both runs' `ns_leaf.object_serial` is a real
number (`242862`, `243241`), i.e. the branch taken is unchanged.

## 3. The round's special ask — the fixed-path family lock is NOT TMPDIR-scoped `[S][L]`

**Verdict: CONFIRMED — fixed lane path, cross-TMPDIR serialization, no
TMPDIR dependence.**

- `[S]` L1: `_pwctl_r86_family_lock` (`:24118–24136`) builds
  `path = ROOT / "live" / "measure_audio-pwctl-r86.lock"` with
  `ROOT = Path(__file__).resolve().parents[1]` (`:26`); the function
  **body** (docstring excluded) contains no `tempfile`, no
  `gettempdir`, no `TMPDIR` reference. Contrast (same check): the r82
  (`:14757`), r84 (`:19841`) and r85 (`:22314`) lock functions all use
  `Path(tempfile.gettempdir()) / …` — **r86 is the first fixed-path
  lock**, exactly the r84 F1 3-seat consensus fold.
- `[L]` L2/L3 (executed, real shipped module loaded from
  `corpus/fixtures/measure_audio.py`): two workers with **different
  TMPDIRs** (`…/tmp/r86-simplifier-lockA` vs `…/tmp/r86-simplifier-lockB`)
  both resolved `os.readlink("/proc/self/fd/<fd>")` to the identical
  `/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/measure_audio-pwctl-r86.lock`
  while `tempfile.gettempdir()` differed; the second acquirer **blocked
  1.879 s** until the first exited (and 1.5 s in the reversed order) —
  cross-TMPDIR exclusion is real, not nominal.
- **Caveats recorded** (independent of TMPDIR): the path is fixed *per
  checkout* — it is derived from the fixture's own location, so a copy of
  the module in another tree resolves to that tree's `corpus/live/`
  (converges with the r86 verifier/reviewer F1 "cross-tree co-tenancy"
  residual); and `os.open` failure silently skips exclusion (`:24126–24128`,
  fail-open). Neither is a TMPDIR dependence.
- **Side-effect disclosure**: the L2/L3 workers rewrite the lock witness
  (`pid=… ns=… role=…`, last-writer-wins) and the proof restores the
  prior bytes on exit (L4); the sibling r86 scribe's ADJ-13 observed one
  such rewrite from a sibling lock test. The file is untracked lane
  scratch and is never unlinked.

## 4. The declared caveats are honored, not folded

`[R]` R7 re-verifies in **both** receipts: `dump_color_eq.armed == False`
and `d_route.armed == False` (record-only), `n_format.armed ==
"rc_only"`. None of the 13 edits touches those arms, their legs, or
their recorded `armed` markers; the fold is byte-confined to the lines
listed in §0 (S12/S13: all changed lines inside `23730–25451`).

## 5. Findings (recorded-only / unarmed surfaces — NOT deleted)

These are **data-only legs** (recorded in the receipts, so deleting them
would change receipt content — outside this seat's contract). They are
listed for the arm-strength review; none is created by the fold:

| # | surface | observation | class |
|---|---|---|---|
| F1 | `pwctl_params_r86_probe.legs.re_vol` (`:24611`) | the wrong-type re-enum is recorded but **never read** by any verdict — the `sp_voltype` arm judges only the write echo (`"None" in stdout`). Converges with the r84-critic "vol_neg unread" class. | unarmed evidence |
| F2 | dsp `pactl_after_cv50`, `player_alive_at_end`, `player_exit`, `tap_exit`, `tap_peak_all`, `tap_stderr_tail`, `tap_windows` | recorded, never armed (the cv50 law is armed on the tap median, not the echo). | recorded-only |
| F3 | meta `m_over`, `m_typed`, `subj0_keys` | the write legs' echoes and the subject-0 key list are recorded; the laws are armed via the subsequent reads (`m_read2`, `m_read3`, `subj0_read`). | recorded-only |
| F4 | tools `lk_junkprops_unlink` (`:25308`) | the unlink of the junk-props link is recorded but never read. | recorded-only |
| F5 | tools `lk_after_unlink.links` (`:25297`) | `_pwctl_r86_own_links()` may return `None` on reader failure; the arm treats `None` as falsy → would pass vacuously. (Same reader-failure shape is handled with `or []`/`coverage_blocked` elsewhere.) | fail-open arm |
| F6 | params `mk_self_loop` (`:24555`), addr `self_loop_census` (read), `core_setparam` (read via the not-implemented loop) | `mk_self_loop`'s echo is recorded only; the link's existence is judged through the census. | recorded-only |

**Considered but NOT folded** (kept for consistency with the r85 fold
convention and to preserve defensive surface): `leaf.get("field",
"sink_name")` / `leaf.get("value", tag)` defaults in T4/T5's unload call
(the r85 fold kept the same `.get` defaults), the `(o.get("info") or
{})` reader guards, `(_pwctl_r86_own_links() or [])` reader-failure
guards, `(x or "")` guards on possibly-absent `stdout`/`stderr` keys,
and the `_r86_family_lock = …  # held to exit` binding convention (the
same shape exists for r82/r84/r85 and is documented as the fd hold).

## 6. Verification summary

| suite | checks | result | artifact |
|---|---|---|---|
| static reachability/dominance/wiring/patch confinement | 43 | **43/43 PASS** | `proofs/static-proofs.txt` |
| executed differentials (teardown/block/own_links/dsp loop/solo/ser) | 20 | **20/20 PASS** | `proofs/differential.txt` |
| receipt census (both pinned green runs) | 32 | **32/32 PASS** | `proofs/receipt-census.txt` |
| fixed-path lock (static + two-process cross-TMPDIR) | 14 | **14/14 PASS** | `proofs/lock-proof.txt` |
| symtable symbol diff | 4 | **4/4 PASS** | `proofs/symdiff.txt` |
| patch round-trip + `git apply --check` | 1 | byte-identical, clean | `proofs/patch-check.txt` |
| compile/parse | 2 | clean | `proofs/pycompile.txt` |
| CLI wiring (help flag, probe mutex) | 2 | flag present; mutex output byte-identical | `proofs/cli-check.txt` |

Both pinned runs: 5/5 entries `failures: []`, `coverage_blocked: []`,
`unloads` verified (`verified_index == captured`, `recycled: False`),
`sinks_gone` all true, `own_nodes_after: []`, `meta_keys_gone: true` —
the fold changes none of these (all diffs are in never-executed code or
provably subsumed predicates).

## 7. Blockers

- **None blocking.** `git apply --check` is clean against the live tree
  (the tracked file is still byte-identical to the pin); the patch is
  deliberately **unapplied** — applying/committing it is the operator's
  call. If applied after further r86 folds land, re-run
  `proofs/run-all.sh` (it re-pins the base and aborts on any 0/multi-match).
- Residual risks: (i) T6/T7/T8/T9 carry out-of-domain disclosures (§2)
  that are unreachable from the current call graph but would matter if a
  future caller feeds `out=None` or reaches the dsp verdict with
  `edges=[]`; (ii) F5's fail-open `None` arm is an arm-strength issue
  for the reviewer, not a fold item; (iii) the lock path is fixed
  per-checkout (cross-tree co-tenancy residual, §3), unchanged by this
  fold.
