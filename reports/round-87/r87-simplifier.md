# r87 SIMPLIFIER — YAGNI/dead-code review of the `d1e687b9` r87 landing (read-only, patch NOT applied)

**Seat** simplifier (r87) · **host** plazir27 (devin substrate) ·
**scope** the r87 pwbind landing only: `git show d1e687b9 --
corpus/fixtures/measure_audio.py` (**+2083/−3**; family region
`:25452`–`:28054`, **2603 lines**, 4 entry functions / 105 recorded leg
keys / 34 r87 defs / 23 r87 constants) plus its 5 wiring hunks
(`add_argument`, the mutex sum, the 30-line dispatch block, the `mode`
and `suffix` ternary heads). **Writes**: this report +
`corpus/live/r87-simplifier/` only. **Zero tracked writes, no commit,
the patch is NOT applied.**

## Custody / tree state at report time

- Analysis base = the **commit-pinned blob**
  `git show d1e687b9:corpus/fixtures/measure_audio.py`, sha256
  **`be31da679be229074690dc5157edcc122612560594baa8ba62a9b5ce26dd9516`**
  (28735 lines), copied byte-identically to `proofs/base-measure_audio.py`
  (`proofs/sha256.txt`). Every line number in this report is a
  **d1e687b9-pinned** line number; the author report's own source sha is
  the same value — the pin is self-consistent.
- **The working tree MOVED under this seat**: HEAD advanced
  `d1e687b9` → `a924878f` (r87 critic) during the window.
  `corpus/fixtures/measure_audio.py` is **byte-identical** between the
  working tree, `HEAD` and the pin (`git diff --numstat HEAD --
  corpus/fixtures/measure_audio.py` empty; sha256 `be31da67…` on all
  three), so `git apply --check` of the fold patch is **clean against
  the moved tree** (re-checked at `a924878f`).
- The only dirty tracked path is the pre-existing
  `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` (mtime
  `03:55:12`, **before** this seat's first command; also flagged by the
  r84–r86 seats) — **not touched by this seat**; every
  compilation/import here happened on scratch copies under
  `corpus/live/r87-simplifier/proofs/`.
- **No `lsp` device answers this file on this substrate** (the only
  external device is the `rea` Ghidra/native-REA MCP server, whose
  subject format has no Python source). **Recorded unavailable**; this
  seat performs no renames — all edits are exact-string folds — so the
  `lsp` fallback rule is not engaged. All reference proofs are literal
  AST/symtable/`grep` censuses over the pinned blob plus **module loads**
  (importlib) of the pinned and folded copies.
- **probeParent**: exactly **one** read-only `ufo-labrat` was dispatched
  (agent `3b2aebe1`; verbatim report at `proofs/labrat-probe.txt`). It
  reported **NOT-FALSIFIED on all four hypotheses** (H1 dead constants,
  H2 fixed-path lock + r82/r84/r85 TMPDIR contrast, H3 `solo_hi` dead
  store, H4 `nid` dominance) with zero files created/modified.
- **No fresh full-family replay.** The r87 family is live-host data
  (PipeWire 1.6.8 / WirePlumber 0.5.17 on a loadavg ~85–88 host with
  sibling wave-B seats running, incl. live r87 family runs); a folded
  replay would need the host, the 105-leg wall time and the lane lock,
  and would perturb siblings. The **two pinned author runs are the
  replay oracle** and their verdict surfaces are re-verified here
  (`proofs/receipt-census.txt`, 13/13; 105 leg keys ×2, `failures: []`).
- Sibling wave-B seats committed during the window (r87 critic
  `a924878f`). Their findings are **not adopted on citation**; where my
  independently-derived results converge (critic F9 on the `p_coll`
  port arm, critic F10 on the tree-relative lock), the convergence is
  disclosed at the item.

**Proof classes used below** — `[S]` static reachability over the pinned
blob (AST/symtable/word-boundary census, dominance walk, call-site
census, patch confinement), `[R]` receipt census across **both** pinned
runs, `[D]` executed differential base-vs-folded (module loads + exact
source slices with stubbed I/O, 12 checks), `[L]` lock proof (static +
two-process cross-TMPDIR serialization + cross-tree race control, 13
checks), `[P]` `patch -p1` round-trip byte-identity + `git apply --check`
+ `py_compile`/`ast.parse`, `[X]` executed findings evidence.

## 0. Summary

**Verdict: PASS (gate green, no blocker).** The r87 landing is
insertion-only apart from the 3 declared wiring lines, structurally
clean, correctly wired (one `add_argument`, one mutex term, four
dispatch lines, two ternary heads; no duplicates) and its dead-code
surface is **small and tight**: **9 provably dead items** delivered as
**11 fold edits** covering 12 replacement sites, `git apply --numstat`
**+17/−24 → net −7 lines** (28735 → 28728), all inside the family region,
as an **unapplied 10-hunk patch**. Every item carries a static
reachability/dominance proof, a receipt census where it has a receipt
surface, and an executed differential; **no item changes any verdict, no
receipt key and no receipt value**.

| # | item | class | base lines | Δ | proofs | tier |
|---|---|---|---|---|---|---|
| T1 | `PWBIND_R87_LINK_WAIT_S` unused constant | dead constant | 25572 | −1 | S,D,R | A |
| T2 | `PWBIND_R87_TAP_WAIT_S` unused constant | dead constant | 25573 | −1 | S,D,R | A |
| T3 | `_pwbind_r87_teardown` `(loads or {})`×3 + `leaf = leaf or {}` | dead guard | 25902, 25903, 25926, 25941 | −1 | S,D,R,SD | B |
| T4 | `_pwbind_r87_block` `leaf = leaf or {}` (its `loads` guard is **LIVE**, retained) | dead guard | 25953 | −1 | S,D | B |
| T5 | cli dsp `solo_hi` dead `None` init (overwritten before any read) | dead store | 26601 | ±0 | S,D,SD | C |
| T6 | cli `fmt_sink` `if nid is not None:` always-true (early block-return dominates) | dead guard | 26639–26651 | −1 | S,D | C |
| T7 | target `DEF = entry.get(…) or "<unreadable-default>"` dead fallback | dead fallback | 26430 | ±0 | S,D,R | C |
| T8 | cli `cold_nowarm` id-term subsumed by the generic term | subsumed predicate | 26956–26957 | −1 | S,D,R | B |
| T9 | target `p_coll` `coll_ports and` subsumed (`all([])` is True) | subsumed predicate | 26488–26489 | −1 | S,D,R | B |

Totals: **+17/−24 across 10 hunks → net −7 lines** (28735 → 28728),
**12 replacement sites**, every hunk inside the family region
(min base-side start 25569 ≥ 25452; max 26953 ≤ 28054).
`git apply --numstat`: `17 24 corpus/fixtures/measure_audio.py`.

**Tier A** = never-referenced code with no receipt surface. **Tier B** =
logically subsumed predicate/guard with a **provably** zero behavioural
delta (including message text and failure-list content). **Tier C** =
dead store/guard/fallback provably unreachable from the current call
graph — separable hunks the operator may retain as mirror vocabulary.

## 1. Deliverable

- `corpus/live/r87-simplifier/r87-simplifier.patch` — sha256
  **`fafb3d0b1b6a1d374c185ce454b62ddb83d1c4f9ab27ab86ac975d9e300448e4`**,
  10 hunks, `git apply --check` **clean** against the live working tree
  at `a924878f` *and* `patch -p1` clean against the commit-pinned blob; a
  fresh `patch -p1` over a scratch copy is **byte-identical** to the
  folded copy (`proofs/patch-check.txt`, `proofs/patch-check-rt.txt`).
  **Not applied.**
- `corpus/live/r87-simplifier/proofs/folded/measure_audio.py` — sha256
  **`aa15268dee8e48e705839cc5021e12137cde93826c2b1029d30d08457e2dedb9`**,
  28728 lines; `python3 -m py_compile` + `ast.parse` clean
  (`proofs/pycompile.txt`).
- `corpus/live/r87-simplifier/proofs/` — the pinned base copy, the r87
  landing diff (`r87-diff.patch`), `fold-r87-simplifier.py` +
  `fold-apply.txt` (**11** exact-match edits, each asserted to match
  **exactly once** *inside the r87 region*; the homographs shared with
  the r83/r84/r86 families — `leaf = leaf or {}` ×4 and
  `for tag, leaf in (loads or {}).items():` ×1 outside the region — were
  caught by the region-scoped 0/multi-match abort and left
  byte-identical), `fold.diff`, `static-proofs.py/.txt` (S1–S16,
  **31/31 PASS**), `differential.py/.txt` (D1–D9, **12/12 PASS**),
  `receipt-census.py/.txt` (R1–R12, **13/13 PASS**),
  `lock-proof.py` + `lock-worker.py/.txt` (L1–L7, **13/13 PASS**),
  `findings-evidence.py/.txt` ([X]), `legcensus.txt`, `symscan.txt`,
  `deadscan.py/.txt`, `deadscan2.txt`, `receipt-structure.txt`,
  `sha256.txt`, `patch-check.txt`, `patch-check-rt.txt`, `pycompile.txt`,
  `cli-check.txt`, `labrat-probe.txt`, `lane-witness-restored.txt`.
- `corpus/live/r87-simplifier/manifest.json` + `manifest.sha256` —
  sha256 census of all seat files; `proofs/run-all.sh` reproduces every
  artifact end-to-end (rc=0, `proofs/run-all.log`).

## 2. Items — remove / proof / receipts

### T1/T2 — `PWBIND_R87_LINK_WAIT_S` / `PWBIND_R87_TAP_WAIT_S` are never referenced `[S][D][R]`

**(a) Change** delete `:25572` `PWBIND_R87_LINK_WAIT_S = 5.0` and
`:25573` `PWBIND_R87_TAP_WAIT_S = 6.0`.

**(b) Proof.** `[S]` region-scoped word-boundary census: each symbol
occurs **once** (its own definition, `uses=0`); the labrat independently
re-derived the same census (H1 NOT-FALSIFIED). The sibling the r87
family kept for exactly this purpose, `PWBIND_R87_STREAM_WAIT_S`
(`:25574`), has **2** occurrences (1 definition + 1 load at `:26570`,
`_alsapw_r84_wait_attached(tag, timeout_s=PWBIND_R87_STREAM_WAIT_S)`) —
the contrast proves these two are copy-paste leftovers, not knobs with
live defaults. `[D]` D8: the folded module's `PWBIND_R87*` attribute
delta is exactly `{LINK_WAIT_S, TAP_WAIT_S}` and nothing else.

**(c) Receipts.** `[R]` R2: **0 occurrences** of `LINK_WAIT`/`TAP_WAIT`
anywhere in either pinned receipt. No receipt surface at all.

### T3 — `_pwbind_r87_teardown`'s guards are dead (required positional, dict domain) `[S][D][R][SD]`

**(a) Change** `:25902` `for tag, leaf in (loads or {}).items():` →
`for tag, leaf in loads.items():`; delete `:25903` `leaf = leaf or {}`;
`:25926` `for nm in (loads or {})` → `for nm in loads`;
`:25941` `or n in (loads or {})` → `or n in loads`.

**(b) Proof.** `[S]` `_pwbind_r87_teardown(entry, failures, loads)` has
**no default** for `loads` (S4: 3 positional params, 0 defaults) and its
four call sites (`:26201`, `:26428`, `:26952`, `:27400`) all pass a local
`loads` **positionally** — S6 shows every `loads` local in the four
entries is either `{}` (modes `:26113`, midi `:27190` — never populated)
or filled with `_pwbind_r87_load_ns(...)` results (target `:26300`,
cli `:26518`). Every value ever stored into a `loads[...]` slot is a
**dict**: `_pwbind_r87_load_ns` returns
`_pwcat_r83_ns_load(name)` + `field`/`value`, and `_pwcat_r83_ns_load`
returns `leaf` on **2/2** paths (both dict literals, S5). So
`(loads or {})` ×3 and `leaf = leaf or {}` can never select their
fallback. `[D]` D1 runs the real teardown with stubbed readers/unload
for **5 `loads` shapes** (incl. a leaf without `field`/`value` and a
`module_id: None` leaf) × **5 reader cases** (both readers failing, both
empty, foreign-only, survivor, residue-destroy): **identical entry,
identical failure list, identical unload-call and pw-cli-call lists**
(25/25 comparisons). `[SD]` D9: the symtable symbol sets of all 34 r87
functions are identical base-vs-folded.

**(c) Receipts.** `[R]` R3: all **6** `unloads` records (2 runs ×
target/cli) are either the name-verified fired shape
(`verified_index == captured`, `recycled: False`, `exit_code: 0`) or the
designed `skipped: "not_listed"` shape; R4: every `sinks_gone` value is
`true`, `own_nodes_after` is `[]` and `foreign_r87a_nodes` is `[]` on
all 4 entries ×2 runs. No key or value changes.

### T4 — `_pwbind_r87_block`'s `leaf = leaf or {}` is dead; its `loads` guard is LIVE `[S][D]`

**(a) Change** delete `:25953` `leaf = leaf or {}` only.

**(b) Proof.** `[S]` `_pwbind_r87_block(entry, failures, msg,
loads=None)` **has** a default and **4 of its 9 call sites omit `loads`**
(S15: `without=[26110, 26294, 26513, 27187] with=[26302, 26309, 26315,
26520, 26532]`) — so `(loads or {})` at `:25952` is a real path and is
**retained** (the same asymmetry r86 folded on its teardown side only).
The `leaf` guard is dead for the same dict-domain reason as T3. `[D]`
D2: identical entry/failure/unload-call tuples for `loads=None`,
`loads={}`, and two dict-leaf shapes.

**(c) Receipts.** `[R]` R5: no `blocked`/`coverage_blocked` surface is
realized in either run (both runs green), so the retained guard has no
receipt cost.

### T5 — cli dsp `solo_hi` dead `None` init `[S][D][SD]`

**(a) Change** `:26601` `solo_lo, solo_hi = mark(), None` →
`solo_lo = mark()` (the real assignment `solo_hi = mark()` at `:26603`
is kept).

**(b) Proof.** `[S]` between the two lines there is only
`sleep_to(solo_lo + 0.6)` (`:26602`), which reads `solo_lo`, not
`solo_hi`; the first read of `solo_hi` is at `:26678`
`regs = {"solo": (solo_lo, solo_hi)}` — after the real assignment, so the
`None` is a dead store. The labrat re-derived the same adjacency
(H3 NOT-FALSIFIED). `[D]` D7 executes both forms with fake
`mark`/`sleep_to`: **identical `(solo_lo, solo_hi)`**.

**(c) Receipts.** `[R]` R7/R8: both runs' `regions.solo` window
(`t` + `median_peak 8192.0`) is computed from `mark()` values only and is
unchanged; all five dsp ratios/writes are unchanged (R7).

### T6 — cli `fmt_sink`'s `if nid is not None:` is always true (dedent) `[S][D]`

**(a) Change** `:26639–26651`: delete `:26640` `if nid is not None:` and
dedent its 10-line body (the `fs[...]` three-verb block) to the `fs = {}`
level.

**(b) Proof.** `[S]` S7 dominance walk: `:26525` `nid =
na.get("node_id")` < `:26531` `if nid is None:` < `:26532–26533`
`return _pwbind_r87_block(entry, failures, "probe node id never
resolved", loads)` < `:26640` the guard. The `return` inside the `try`
executes the `finally` and **exits the function**, so any execution
reaching `:26640` has a non-None `nid`; there is no rebinding of `nid`
between (`grep` census + labrat H4 NOT-FALSIFIED). `[D]` D3 extracts the
exact base/folded slices and executes them against a stubbed `pwcli` for
the reachable `nid` domain (12345/0/−1/99999999): **identical `fs` dict
and identical `legs` dict**. **Disclosed**: at the unreachable
`nid=None` domain the base leaves `fs` empty while the folded copy calls
the three verbs — unreachable because the `nid is None` block-return
fires first (D3 records this divergence explicitly).

**(c) Receipts.** `[R]` R7: `fmt_sink.post_valid`'s negotiated
`{rate, format_id}` is compared against `pre` and is unchanged on both
runs; no `failures`/`coverage_blocked` entry depends on the guard.

### T7 — target `DEF`'s `"<unreadable-default>"` fallback is dead `[S][D][R]`

**(a) Change** `:26430` `DEF = entry.get("default_sink_at_start") or
"<unreadable-default>"` → `DEF = entry["default_sink_at_start"]`.

**(b) Proof.** `[S]` S8 dominance: `:26313` `DEF0 =
_pwbind_r87_default_sink()` < `:26314` `if not DEF0:` < `:26315–26317`
`return _pwbind_r87_block(…, "pactl get-default-sink unreadable",
loads)` < `:26318` `entry["default_sink_at_start"] = DEF0` < `:26430` the
verdict. A falsy/unreadable default **block-returns before any verdict**,
so at `:26430` the key is present and truthy and neither the `or`
fallback nor `.get`'s missing-key path can ever apply. `[D]` D4:
identical values for the reachable domain; the out-of-domain disclosure
(falsy value → base `"<unreadable-default>"` vs folded `None`; absent key
→ folded `KeyError`) is recorded and unreachable.

**(c) Receipts.** `[R]` R8: `default_sink_at_start` is recorded, is
truthy, and equals `default_sink_at_end` on both runs — the fold changes
neither the recorded value nor the drift verdict.

### T8 — cli `cold_nowarm`'s id-term is subsumed by the generic term `[S][D][R]`

**(a) Change** `:26956–26957`
```python
    if f"unknown global '{nid}'" not in blob and \
            "unknown global" not in blob:
```
→ `    if "unknown global" not in blob:`.

**(b) Proof.** `[S]` the id form `A = f"unknown global '{nid}'"`
**contains** the generic form `B = "unknown global"` as a substring, so
`B ∉ blob ⟹ A ∉ blob`; hence `A ∉ blob and B ∉ blob ≡ B ∉ blob` (the
first conjunct is implied by the second — a strict subsumption, the r86
T6 shape). `[D]` D5 evaluates both predicates over a 7-text domain
(exact-id form, generic-only, id-with-extra-text, different id, empty,
unrelated): **identical decisions**. The failure message still prints
`blob[-160:]`, so the recorded failure text is unchanged too.

**(c) Receipts.** `[R]` R8: both runs' `cold_nowarm` blob carries
`unknown global '<id>'` — the branch taken (no failure) is unchanged.

### T9 — target `p_coll`'s `coll_ports and` term is subsumed `[S][D][R]`

**(a) Change** `:26488–26489`
```python
    if coll_ports and not all(str(p).startswith("playback_")
                              for p in coll_ports):
```
→ `    if not all(str(p).startswith("playback_") for p in coll_ports):`.

**(b) Proof.** `[S]` `all([])` is `True`, so on an empty list the
unguarded predicate is `not True = False` — identical to the guarded
form; on a non-empty list the guard is `True` and drops out. So the
`coll_ports and` term is provably redundant. `[D]` D6 evaluates both
predicates over 7 port lists (`[]`, `["playback_1"]`, `["input_1"]`,
mixed, `["monitor_1"]`, `[None]`, `["playback_"]`): **identical
decisions** — including the `[None]` (`str(None) = "None"`) case, so the
arm still catches stripped port names. **Convergence disclosed**: the
r87 critic's F9 records this same line as "armed, not a gap" — that
assessment is **correct and preserved**: this fold removes only the
*redundant guard term*, not the arm (the r86/r87 arm-strength question is
untouched). The failure message still prints `coll_ports`.

**(c) Receipts.** `[R]` R8: `p_coll.consumers` is exactly one element
(the probe sink id) on both runs — the branch taken is unchanged.

## 3. The round's special ask — the fixed-path family lock is NOT TMPDIR-scoped `[S][L]`

**Verdict: CONFIRMED — fixed lane path, cross-TMPDIR serialization, no
TMPDIR dependence; tree-relative residual inherited and reproduced.**

- `[S]` L1: `_pwbind_r87_family_lock` (`:25844–25861`) builds
  `path = ROOT / "live" / "measure_audio-pwbind-r87.lock"` with
  `ROOT = Path(__file__).resolve().parents[1]` (`:26`); the function
  **code** (docstring excluded) contains no `tempfile`, no `gettempdir`,
  no `TMPDIR`. Contrast (same check): the r82 (`:14764`), r84 (`:19846`)
  and r85 (`:22318`) lock functions all use
  `Path(tempfile.gettempdir()) / …` — **r86 and r87 are the fixed-path
  locks**, exactly the r84 F1 3-seat consensus fold. The labrat
  independently re-derived all four line citations (H2 NOT-FALSIFIED).
- `[L]` L2/L3 (executed, real shipped module loaded from
  `corpus/fixtures/measure_audio.py`): two workers with **different
  TMPDIRs** (`…/tmp/r87simp-lock/lockA` vs `…/lockB`) both resolved
  `os.readlink("/proc/self/fd/<fd>")` to the identical
  `/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/measure_audio-pwbind-r87.lock`
  while `tempfile.gettempdir()` differed; the second acquirer **blocked
  2.603 s** until the first exited — cross-TMPDIR exclusion is real, not
  nominal.
- `[L]` L6/L7 — **either-way control**: a holder in the original tree
  and a contender in a copied tree (fixture copy under `$TMPDIR`) resolve
  **different** lock files and **RACE** (contender waited 0.368 s while
  the holder held 2.6 s). So the lock is *per-checkout*, not global —
  the inherited r86 F1/F6 **cross-tree co-tenancy residual** (live-
  witnessed by the r87 critic, F10). This is **not** a TMPDIR dependence:
  within one checkout the exclusion holds across TMPDIRs; the residual is
  tree-relative by construction (`ROOT` derives from the fixture's own
  location) and is unchanged by this fold.
- **Caveats recorded** (independent of TMPDIR): `os.open` failure
  silently skips exclusion (`:25852–25853`, fail-open, as in r86), and
  the returned fd is never read (the intentional fd-hold — critic F11).
- **Side-effect disclosure**: the L2/L3/L6 workers rewrite the lane
  witness (`pid=… ns=… role=…`, last-writer-wins); the proof restores
  the bytes it found at start (L4), and this seat then re-restored the
  **pre-seat** witness `pid=3585207 ns=r87a_ns_3585207
  role=r87arole3585207` (52 B, sha256
  `432b79787a7ac1fc252903f172281f807798682b372e2599a1e9616cd31c2141`,
  `proofs/lane-witness-restored.txt`). The file is untracked lane
  scratch and is never unlinked.

## 4. The declared caveats are honored, not folded

`[R]` R5/R9/R10 re-verify in **both** receipts: no `coverage_blocked` or
`blocked` key is realized on any entry; `mdump_live` published + pinned +
printed Note lines; the `--volume` ladder is in envelope
(v050 ≈ 0.5, v150 ≈ 1.5, v000 = 0.0). None of the 11 edits touches those
arms, their legs, or their recorded markers; the fold is byte-confined to
the lines listed in §0 (S12: all changed lines inside `25452–28054`).

## 5. Findings (recorded-only / unarmed surfaces — NOT deleted)

These are **data-only legs / arm-strength surfaces** (recorded in the
receipts, so deleting them would change receipt content — outside this
seat's contract). They are listed for the arm-strength review; none is
created by the fold:

| # | surface | observation | class |
|---|---|---|---|
| F1 | modes `m_sysex` arm (`:26270`) | `if name == "m_sysex" and leg.get("exit_code") == 0` fires **only** on a clean early exit. Both runs record `exit_code=1` for every watch leg (harness SIGTERM exit), so an early *crash* (rc≠0) is indistinguishable from the harness kill and passes silently; the recorded `exited_before_observe` marker is never armed. `[X]` `findings-evidence.txt`. | fail-open arm |
| F2 | target `p_zero`/`p_zero_prop`/`p_noauto` verdict (`:26459`) | subscripts `legs[name]["snaps"]` directly; `_pwbind_r87_watch` returns a rec **without** `snaps` on a spawn error → `KeyError` instead of a recorded failure. `[X]` executed: spawn-error rec keys `['argv','spawn_error','tag']`, `rec["snaps"]` raises `KeyError`. Same line as the critic's F4 (presence-at-any-snap) — different failure mode, independently derived. | crash-instead-of-verdict |
| F3 | recorded-only fields | `binaries.pw_cat_sha`, `last` (`:26080`), `port_dirs` (`:26256`), `recorded_file` (`:26197`), `collision_objects` (`:26415`), `tap_windows` (`:26672`), `player_alive_at_end`/`player_exit`/`tap_exit`, `stream_leaf`, `fmt_unlinked_watch`, `foreign_candidates`, `wake_after_suspend`, `refs`, `inventory`, `oracle_at_start`, `contention`, `pin.bridge`/`pin.seq_port` — recorded, read by no verdict. | recorded-only |
| F4 | cli `unloads` record | after the `destroy_sink_module` leg (destroy by id → whole module unloaded), the teardown's name-verified unload finds nothing to fire and records `skipped: "not_listed"` — an honest record of a module already gone, not a missed unload. | recorded-only (honest skip) |
| F5 | `_pwbind_r87_run` spawn-error shape | the early-return rec carries only `argv`/`spawn_error`; every verdict consuming it fails closed via missing-key reads (`exit_code`/`error_class`/text `None`), except the arms gated behind another failure first (`props_unk` behind `attached`, `writes` behind the solo envelope). | fail-closed by omission |

## 6. Verification summary

| suite | checks | result | artifact |
|---|---|---|---|
| static reachability/dominance/wiring/patch confinement | 31 | **31/31 PASS** | `proofs/static-proofs.txt` |
| executed differentials (teardown/block/fmt_sink/DEF/cold/coll/solo/attr/symtable) | 12 | **12/12 PASS** | `proofs/differential.txt` |
| receipt census (both pinned green runs) | 13 | **13/13 PASS** | `proofs/receipt-census.txt` |
| fixed-path lock (static + cross-TMPDIR + cross-tree control) | 13 | **13/13 PASS** | `proofs/lock-proof.txt` |
| patch round-trip + `git apply --check` (at `a924878f`) | 1 | byte-identical, clean | `proofs/patch-check*.txt` |
| compile/parse | 2 | clean | `proofs/pycompile.txt` |
| CLI wiring (help flag, probe mutex rc=2) | 2 | flag present; mutex byte-compatible | `proofs/cli-check.txt` |
| leg census | 105 leg keys ×2 runs | identical | `proofs/legcensus.txt` |
| labrat probe (probeParent, 1 dispatch) | 4 hypotheses | NOT-FALSIFIED ×4 | `proofs/labrat-probe.txt` |

Both pinned runs: 4/4 entries `failures: []`, no `coverage_blocked`,
`unloads` verified or honestly skipped, `sinks_gone` all true,
`own_nodes_after: []`, `foreign_r87a_nodes: []`, `default_sink` stable —
the fold changes none of these (all diffs are in never-executed code or
provably subsumed predicates).

## 7. Blockers

- **None blocking.** `git apply --check` is clean against the live tree
  (the tracked file is still byte-identical to the pin at `a924878f`);
  the patch is deliberately **unapplied** — applying/committing it is the
  operator's call. If applied after further r87 folds land, re-run
  `proofs/run-all.sh` (it re-pins the base and aborts on any 0/multi-match
  or on a fixture sha drift).
- Residual risks: (i) T6/T7 carry out-of-domain disclosures (§2) that are
  unreachable from the current call graph but would matter if a future
  caller feeds `nid=None` or reaches the verdicts with a falsy/absent
  `default_sink_at_start`; (ii) F1/F2/F5 are arm-strength issues for the
  reviewer, not fold items; (iii) the lock path is fixed
  *per-checkout* — the cross-tree co-tenancy residual (§3, inherited r86
  F1/F6, live-witnessed by the r87 critic F10) is unchanged by this fold.
- No fresh full-family live replay was run (loadavg ~85–88, sibling
  wave-B seats, lane lock); the two pinned author runs are the replay
  oracle and every surface the fold touches was re-verified against their
  bytes.
