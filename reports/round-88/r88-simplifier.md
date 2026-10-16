# r88 SIMPLIFIER — YAGNI/dead-code review of the `c19bec96` r88 btwit landing (read-only, patch NOT applied)

**Seat** simplifier (r88) · **host** plazir27 (devin substrate) ·
**scope** the r88 btwit landing only: `git show c19bec96 --
corpus/fixtures/measure_audio.py` (**+1772/−3**, 6 hunks; family region
`:27507`–`:29252`, 1746 lines, 3 entry functions / 79 recorded leg keys
(28+41+10) / 43 r88 module-level names) plus its 5 wiring splices
(`add_argument`, the mutex sum, the 20-line dispatch block, the `mode`
and `suffix` ternary heads). **Writes**: this report +
`corpus/live/r88-simplifier/` only. **Zero tracked writes, no commit,
the patch is NOT applied.**

## Custody / tree state at report time

- Analysis base = the **commit-pinned blob**
  `git show c19bec96:corpus/fixtures/measure_audio.py`, sha256
  **`ad9d59b1e0dc5e2be4274f4966e571dabefed94076c06093eed1bf4cd2aef4c4`**
  (30504 lines), copied byte-identically to
  `proofs/base-measure_audio.py`; every line number in this report is a
  **c19bec96-pinned** line number. The author report's own source sha is
  the same value — the pin is self-consistent.
- **The working tree MOVED under this seat**: HEAD advanced
  `c19bec96` → `2226b92e` (r88 scribe) → `c4de692e` (r88 critic) during
  the window. `corpus/fixtures/measure_audio.py` is **byte-identical**
  between the working tree, `HEAD` and the pin
  (`git diff --numstat c19bec96 HEAD -- corpus/fixtures/measure_audio.py`
  empty; sha256 `ad9d59b1…` on all three), so `git apply --check` of the
  fold patch is **clean against the moved tree** (S11b).
- The only dirty tracked path is the pre-existing
  `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`
  (mtime `04:22:52`, 1 670 979 B, sha256 `d758dabd…`) — **inside the
  author window** (independently dated by r88-scribe ADJ-10), **not
  touched by this seat**; every import here ran on scratch copies under
  `PYTHONDONTWRITEBYTECODE=1` (O4).
- **No `lsp` device answers this file on this substrate** (the only
  external device is the `rea` Ghidra/native-REA MCP server, whose
  subject format has no Python source). **Recorded unavailable**; this
  seat performs no renames — all edits are exact-string folds — so the
  `lsp` fallback rule is not engaged. All reference proofs are literal
  AST/symtable/`grep` censuses over the pinned blob plus **module loads**
  (importlib) of the pinned and folded copies.
- **probeParent**: exactly **one** read-only `ufo-labrat` was dispatched
  (agent `8c774af2`; verbatim report at `proofs/labrat-probe.txt`). It
  returned **CONFIRMED on all four hypotheses** (H1 dead runner params,
  H2 dict-domain guards, H3 `_frames_cache` no-op pops, H4 fixed-path
  lock) with zero files created/modified and no commands spawned. Its
  citations were independently re-derived by this seat's own scripts
  before this report was written (S3/S4/S5/S7, L0/L1).
- **No fresh full-family replay.** The r88 family is live-host data
  (PipeWire 1.6.8 / WirePlumber 0.5.17 on a loadavg ~85–88 host with
  sibling wave-B seats running, incl. the r88 verifier's five live
  `--probe-btwit-r88` runs per r88-scribe ADJ-11); the **two pinned
  author runs are the replay oracle** and their verdict surfaces are
  re-verified here (R1–R8; both receipt shas re-derive).
- Sibling wave-B seats committed during the window (scribe `2226b92e`,
  critic `c4de692e`). Their findings are **not adopted on citation**;
  where my independently-derived results converge (scribe ADJ-1 on the
  uncited RED dev run, scribe ADJ-12 / critic F8 on the tree-relative
  lock residual, scribe ADJ-10 on the dirty `.pyc`), the convergence is
  disclosed at the item.

**Proof classes** — `[S]` static reachability over the pinned blob
(AST/symtable/word-boundary census, dominance walk, call-site census,
patch confinement), `[R]` receipt census across **both** pinned runs
(plus the stale dev run as a non-oracle), `[D]` executed differential
base-vs-folded (module loads + stubs, **51 checks**), `[L]` lock proof
(static + two-process cross-TMPDIR serialization + cross-tree race
control + fail-open, **16 checks**), `[P]` `patch -p1` round-trip
byte-identity + `git apply --check` + `py_compile`/`ast.parse`.

## 0. Summary

**Verdict: PASS (gate green, no blocker).** The r88 landing is
insertion-only apart from the 3 declared wiring splices, structurally
clean, correctly wired (one `add_argument`, one mutex term, one dispatch
block, two ternary heads; no duplicates) and its dead-code surface is
**small and tight**: **6 provably dead items** delivered as **11 fold
edits** covering **12 replacement sites**, `git apply --numstat`
**+12/−19 → net −7 lines** (30504 → 30497), all inside the family
region, as an **unapplied 8-hunk patch**. Every item carries a static
reachability/dominance proof, a receipt census where it has a receipt
surface, and an executed differential; **no item changes any verdict, no
receipt key and no receipt value**.

| # | item | class | base lines | Δ | proofs | tier |
|---|---|---|---|---|---|---|
| T1 | `_btwit_r88_run` `env`/`stdin_data` never bound by 19/19 call sites | dead params + dead branch | 27659–27660, 27666–27669, 27676 | −3 | S,D | B |
| T2 | `_btwit_r88_teardown` `(loads or {})`×3 + `leaf = leaf or {}` | dead guard (dict domain) | 28021, 28022, 28046, 28061 | −1 | S,D,R | B |
| T3 | `_btwit_r88_block` `leaf = leaf or {}` (its `(loads or {})` is **LIVE**, retained) | dead guard | 28073 | −1 | S,D | B |
| T4 | `r_top.pop("_frames_cache")` / `r_top2.pop("_frames_cache")` | no-op statement | 29070, 29132 | −2 | S,D,R | A |
| T5 | `leaf.get("field", "sink_name")` / `leaf.get("value", tag)` ×2 call sites | dead fallback | 28026–28027, 28077–28078 | ±0 | S,D,R | C |
| T6 | `for nid, n in …items()` unused loop variable → `.values()` | dead binding | 28263–28264 | ±0 | S,D | C |

Totals: **+12/−19 across 8 hunks → net −7 lines** (30504 → 30497),
**12 replacement sites**, every hunk inside the region (min base-side
start 27656 ≥ 27507; max 29129 ≤ 29252). `git apply --numstat`:
`12 19 corpus/fixtures/measure_audio.py`.

**Tier A** = never-firing statement with no receipt surface. **Tier B** =
logically subsumed guard/parameter with a **provably** zero behavioural
delta (including message text and failure-list content). **Tier C** =
dead fallback/binding provably unreachable from the current call graph —
separable hunks the operator may retain as mirror vocabulary.

## 1. Deliverable

- `corpus/live/r88-simplifier/proofs/fold.diff` — sha256
  **`de8032a77aebaa7d575afacff42daf0fdc534bbe5587c735292f4dd6e69401e3`**,
  8 hunks, `git apply --check` **clean** against the live working tree at
  `c4de692e` *and* `patch -p1` clean against the commit-pinned blob; a
  fresh `patch -p1` over a scratch copy is **byte-identical** to the
  folded copy (S11, run-all.log). **Not applied.**
- `corpus/live/r88-simplifier/proofs/folded/measure_audio.py` — sha256
  **`1beac939703a163093c2f634c3ec61e3e5d2bea6ac7a56966c3f398e55a045a6`**,
  30497 lines; `python3 -m py_compile` + `ast.parse` clean.
- `corpus/live/r88-simplifier/proofs/` — the pinned base copy, the r88
  landing diff (`r88-diff.patch`), `fold-r88-simplifier.py` +
  `fold-apply.txt` (**11** exact-match edits, each asserted to match
  exactly once — or exactly twice for the shared teardown/block unload
  text — *inside the region*; the homographs shared with the
  r83/r84/r85/r86/r87 families — 21 `(loads or {})` lines and 6
  `leaf = leaf or {}` lines outside the region — were left byte-identical
  by the region-scoped 0/multi-match abort), `fold.diff`,
  `static-census.py/.txt` (43-name defs/uses + 19-call-site census),
  `deadscan.py/.txt` (dead-store/param census), `static-proofs.py/.txt`
  (S1–S12, **36/36 PASS**), `differential.py/.txt` (D1–D6, **51/51
  PASS**), `receipt-census.py/.txt`, `receipt-proofs.py/.txt` (R1–R8,
  **36/36 PASS**), `lock-proof.py` + `lock-worker.py/.txt` (L0–L8,
  **16/16 PASS**), `observations.py/.txt` (O1–O5),
  `labrat-probe.txt`, `run-all.sh` + `run-all.log` (reproduces every
  artifact end-to-end, rc=0).
- `corpus/live/r88-simplifier/manifest.json` + `manifest.sha256` —
  sha256 census of all **27** seat files; `sha256sum -c` verified.
- **139 checks total (36 S + 51 D + 36 R + 16 L), all PASS.**

## 2. Items — remove / proof / receipts

### T1 — `_btwit_r88_run`'s `env`/`stdin_data` are dead parameters `[S][D]`

**(a) Change** drop both parameters from the signature (`:27659–27660`),
collapse the `stdin=` conditional to `stdin=subprocess.DEVNULL` and drop
`env=env` (`:27666–27669`), and call `proc.communicate(timeout=timeout_s)`
(`:27676`).

**(b) Proof.** `[S]` S3: **19/19** call sites (all inside the region)
bind only `(argv, timeout_s)` positionally plus `keep_chars=`/
`keep_raw=` keywords — **zero** bind `env`/`stdin_data` or pass a third
positional; the two names occur nowhere else in the region (S3c), and
the sibling `_pwctl_r86_run`/`_pwbind_r87_run` uses at `:25247`/`:26541`
are different functions (labrat H1 independently re-derived both).
`[D]` D1: with a fake `Popen`/`communicate`, base vs folded are identical
for the normal, timeout-kill and `keep_raw` shapes; both pass
`stdin=subprocess.DEVNULL`, `env=None`, `start_new_session=True`, and the
normalized communicate kwargs are identical (`input=None` ≡ omitted).
The behaviour is fixed: stdin was **always** `DEVNULL` (the conditional's
`stdin_data is not None` branch was never selected) and `env` was always
`None` (Popen's default).

**(c) Receipts.** No receipt surface: the runner is the spawn primitive;
its recorded keys (`stdout`, `stderr`, `error_class`, …) are produced
identically (D1 rec equality).

### T2 — `_btwit_r88_teardown`'s guards are dead (required positional, dict domain) `[S][D][R]`

**(a) Change** `:28021` `for tag, leaf in (loads or {}).items():` →
`for tag, leaf in loads.items():`; delete `:28022` `leaf = leaf or {}`;
`:28046` `for nm in (loads or {})` → `for nm in loads`;
`:28061` `or n in (loads or {})` → `or n in loads`.

**(b) Proof.** `[S]` S4: `_btwit_r88_teardown(entry, failures, loads)` has
**no default** for `loads` (3 params, 0 defaults) and its three call
sites (`:28269`, `:28764`, `:29158`) all pass a local `loads`
**positionally**; S4d: every entry initializes `loads = {}`; S4c: all
four `loads[...]` stores are `_btwit_r88_load_ns(...)`, whose
`_pwcat_r83_ns_load` returns `leaf` on **2/2** return paths (both dict
literals, S5a/S5b) and then sets `field`/`value` unconditionally (S5c).
So `(loads or {})` ×3 and `leaf = leaf or {}` can never select their
fallback. `[D]` D2 runs the real teardown with stubbed readers/unload for
**6 loads/reader scenarios** (empty, one leaf, mid-`None` leaf +
residual-destroy, sinks-reader error, node-reader error, foreign+own):
**identical entry, identical failure list, identical unload-call and
pw-cli-call lists** (18/18 comparisons).

**(c) Receipts.** `[R]` R4: all **8** `unloads` records (2 runs × 4) are
either the name-verified fired shape (`verified_index == captured`,
`recycled: False`, `exit_code: 0`) or a designed skip; every record
carries `field: "sink_name"` and `value: "r88a_ns…"` — the reachable
domain only. R5: `sinks_gone` all `true`, `own_nodes_after` `[]`,
`residual_destroy` absent, `foreign_r88a_nodes` `[]` on all 6
entry-runs. No key or value changes.

### T3 — `_btwit_r88_block`'s `leaf = leaf or {}` is dead; its `loads` guard is LIVE `[S][D]`

**(a) Change** delete `:28073` `leaf = leaf or {}` only.

**(b) Proof.** `[S]` S6: `_btwit_r88_block(entry, failures, msg,
loads=None)` **has** a default and **3 of its 8 call sites omit `loads`**
(S6b: omit `[28114, 28440, 29024]`, pass `[28128, 28447, 28453, 28466,
29032]`; the omitters are exactly the missing-tools early blocks, S6c) —
so `(loads or {})` at `:28072` is a real path and is **retained**. The
`leaf` guard is dead for the same dict-domain reason as T2. `[D]` D3:
identical entry/failure/unload-call tuples for `loads=None`, `{}`, a real
leaf and a `module_id: None` leaf.

**(c) Receipts.** `[R]` No `blocked`/`coverage_blocked` surface is
realized in either green run (R2d), so the retained guard has no receipt
cost.

### T4 — the two `_frames_cache` pops are provable no-ops `[S][D][R]`

**(a) Change** delete `:29070` `r_top.pop("_frames_cache", None)` and
`:29132` `r_top2.pop("_frames_cache", None)`.

**(b) Proof.** `[S]` S7a: the literal `_frames_cache` occurs **4 times in
the whole file** — the write at `:29047`
(`legs["pt_n3"]["_frames_cache"] = …`, consumed at `:29175` by
`l.pop("_frames_cache", [])`), and the two pops under review. S7b/S7c:
`_btwit_r88_top_until` (`:27862`) builds its returned `rec` from
`_btwit_r88_run`'s rec + `attempt`/`frames`/`status_sets` (popping only
`stdout_raw`/`stderr_raw`) and **never writes `_frames_cache`** — the
only writer is the external `legs["pt_n3"]` store on a *different* dict.
So both pops can only ever pop an absent key. `[D]` D4: the real
`_btwit_r88_top_until` runs against a stubbed runner (one-shot and retry
shapes); the returned recs are identical base-vs-folded and contain no
`_frames_cache` key; applying the base's pop to the dict leaves it
byte-equal to the folded dict (the no-op is executed, not asserted).
Labrat H3 independently re-derived the same key-domain argument.

**(c) Receipts.** `[R]` R6a: `_frames_cache` appears in neither receipt
(the key never leaks); R6b: `pt_n3.attempt == 1` and 3 frames on both
runs — the recorded surfaces are untouched.

### T5 — `leaf.get("field", …)`/`leaf.get("value", …)` fallbacks are dead `[S][D][R]`

**(a) Change** at both unload call sites (`:28026–28027` teardown,
`:28077–28078` block): `leaf.get("field", "sink_name")` → `leaf["field"]`,
`leaf.get("value", tag)` → `leaf["value"]`.

**(b) Proof.** `[S]` S5c: `_btwit_r88_load_ns` (`:28008–28014`) sets
`leaf["field"] = "sink_name"` and `leaf["value"] = name`
**unconditionally** on its only path (its input `_pwcat_r83_ns_load`
returns a dict on 2/2 returns; a non-dict would raise before the keys are
read); all four `loads[...]` stores are `_btwit_r88_load_ns(...)` (S4c).
So the defaults are unreachable from this call graph. `[D]` D2/D3 run
the real unload paths with a real-shaped leaf: the recorded unload calls
are `(4242, "sink_name", NS)` in both copies. **Disclosed**: at the
out-of-domain leaf `{module_id: 1}` (no `field`/`value` — never produced
by `load_ns`), base falls back to `"sink_name"`/`tag` while the folded
copy raises `KeyError`; D2/D3 record this divergence explicitly as
unreachable.

**(c) Receipts.** `[R]` R4c: all 8 records carry exactly
`field: "sink_name"` and `value: <own name>` — the defaults never fire.

### T6 — the `bz_own_residue` comprehension's `nid` is never read `[S][D]`

**(a) Change** `:28263–28264`
```python
            n.get("name") for nid, n in
            (g2.get("nodes") or {}).items()
```
→
```python
            n.get("name") for n in
            (g2.get("nodes") or {}).values()
```

**(b) Proof.** `[S]` S8: the comprehension's target tuple is
`(nid, n)` and `nid` has **zero Load occurrences** in the comprehension
(elt + conditions) — it is a pure dead binding; `dict.values()` yields
the same objects as `dict.items()`' second element, in the same order.
`[D]` D6: the exact comprehension slice (base and folded) is executed
against a stubbed graph containing foreign, own-prefixed and
foreign-prefixed `r88a_` names: **identical result** (`['r88a_<pid>_bz_create_a2dpsource']`-shaped, foreign excluded).

**(c) Receipts.** `[R]` R3: `bz_own_residue` is a recorded leg key on
both runs and its value is `[]` (no residue) — the fold cannot change it
(D6 shows the same selection rule).

## 3. The round's special ask — the fixed-path family lock `[S][L]`

**Verdict: CONFIRMED — fixed lane path, cross-TMPDIR serialization, no
TMPDIR dependence; tree-relative residual and fail-open caveat inherited
and reproduced (both already live-witnessed by sibling seats).**

- `[S]` L1a: `_btwit_r88_family_lock` (`:27968–27984`) **code**
  (docstring/comments excluded) contains no `tempfile`, no `gettempdir`,
  no `TMPDIR`; L1b: `path = ROOT / "live" / "measure_audio-btwit-r88.lock"`;
  L1c: `ROOT = Path(__file__).resolve().parents[1]` (`:26`). Contrast
  (same check): the r82 (`:14764`), r84 (`:19846`) and r85 (`:22318`)
  locks use `Path(tempfile.gettempdir()) / …` — **r86, r87 and r88 are
  the fixed-path locks** (the r84 F1 3-seat consensus). The labrat
  independently re-derived all citations (H4).
- `[L]` L0: the committed resolution (`ROOT` = `corpus/` for the tracked
  fixture) is exactly the on-disk lane lock
  `corpus/live/measure_audio-btwit-r88.lock`; its witness is
  `pid=1298372 ns=r88a_ns_1298372 role=r88arole1298372` (mtime 07:23:25Z
  = run 2's acquisition; run 2's receipt stamp is 07:23:41Z), i.e. the
  last author run held it.
- `[L]` L2/L3 (executed, scratch trees only): two workers with
  **different TMPDIRs** (`…/r88simp-lock/tmpA` vs `…/tmpB`) loading the
  **same** fixture copy both resolve the identical
  `…/treeA/corpus/live/measure_audio-btwit-r88.lock` while
  `tempfile.gettempdir()` differs; the second acquirer **blocked 1.975 s**
  of the holder's 2.5 s hold — cross-TMPDIR exclusion is real, not
  nominal.
- `[L]` L6/L7 — **either-way control**: a holder in tree A and a
  contender in tree B (a different fixture copy) resolve **different**
  lock files and **RACE** (contender waited 0.0 s while the holder held
  2.5 s). So the lock is *per-checkout*, not global — the inherited
  **cross-tree co-tenancy residual** (r86 F1/F6; r88-scribe ADJ-12;
  r88-critic F8, live-witnessed for the 4th round). This is **not** a
  TMPDIR dependence: within one checkout the exclusion holds across
  TMPDIRs; the residual is tree-relative by construction (`ROOT` derives
  from the fixture's own location) and is unchanged by this fold.
- `[L]` L8 — fail-open caveat reproduced: with `corpus/live/` missing,
  `os.open` fails, `_btwit_r88_family_lock` returns `None` and exclusion
  is silently skipped (inherited from r86/r87; unchanged by this fold).
- **`_r88_family_lock = _btwit_r88_family_lock()   # held to exit`**
  (`:29817`) looks like a dead binding and is **NOT**: it is the only
  reference that keeps the returned fd alive for the process lifetime;
  dropping the assignment would release the flock and let two same-tree
  runs interleave (labrat H4(iv); r87 critic F11 class). Explicitly
  **not folded** (O1).

## 4. Receipt oracle — the two green runs, and the stale RED dev run `[R]`

- R1/R2: exactly **3** `*btwit-r88` runs on disk; the two cited green
  runs (`20261016T072313132218Z`, sha256
  `a1c7746d8a7c18ab647f868816d128cf46c90d5bc6fccb32c0085130c08e83d4`;
  `20261016T072341162452Z`, sha256
  `cce9164f5a537f349e449be4576623fce44cfd4d3e2f6364383f515e0d9b640d`)
  each carry `mode: "probe-btwit-r88"`, the 3 expected entries,
  **28/41/10 = 79 legs**, `failures: []` in all 3 entries and no
  `coverage_blocked`/`blocked`. The author report's "2 green" and
  "79 legs / 3 entries" re-derive.
- R3: leg-key sets are identical between the two green runs per entry
  (28/41/10) and the recorded union is exactly the static literal keys
  (69) plus the 10 loop-generated keys
  (`bz_loadmod_{discover,device,device_path,discover_arg}`,
  `bz_create_{a2dpsink,sink,a2dpsource,midi}`,
  `wd_mode_{raw,indent0}`) — the fold touches no key.
- R4/R5/R6: the fold-relevant surfaces (unloads, `sinks_gone`,
  `own_nodes_after`, `pt_n3.attempt`, no `_frames_cache`) are in the
  reachable domain on all 6 entry-runs.
- R7: **all 5** r88-local error-class rows fire across the green runs
  (`pa_sendmsg_noent`, `pwtop_connect_down`, `pwdump_invalid_opt`,
  `cli_enum_notimpl`, `cli_unsupported_type`) — the local table is not
  dead code (a fact worth recording: without it, `wd_info_all` would
  record `error_class: None`).
- R8: the third run `20261016T071710822152Z` (sha256
  `8ea27480de11cda6267188ae9be9c9c5c3910ec378aa2a3d1482c6a2e5ca2976`) is
  **RED — 14 failures (6+5+3), 1 `coverage_blocked`, 75 legs (28/39/8)**
  and is from a **pre-final revision**: it carries the class
  `cli_cant_create` (absent from the committed table) and the leg `pt_n2`
  (absent from the committed code). It is therefore **not an oracle**;
  this seat records it as the same uncited-RED-dev-run class r88-scribe
  independently raised as ADJ-1 (convergence disclosed, not adopted).

## 5. Observed but NOT folded

- **O1** the intentional lock-fd hold (§3) — live, not dead.
- **O2** two cosmetic unused bindings left in place: `rec` at `:28501`
  (`rec, own_dump = _btwit_r88_dump_objs(own_id)`) and `pk` at `:28587`
  (`pk, _pl = _btwit_r88_cli_props(...)`) — the calls have the side
  effects; a rename to `_rec`/`_pk` is style, not a deletion.
- **O3** duplicate spawns: `wd_dump_color` spawns
  `pw-dump --color=always <id>` **3×** (record + json-parse probe +
  ANSI probe) and `_btwit_r88_dump_objs` spawns `pw-dump <args>` **2×**
  (bounded recorded witness + full JSON parse). Both are intentional
  (the recorded `rec` truncates at `keep_chars=300`; the parse needs the
  full stream) — not folded.
- **O4** the tracked dirty `.pyc` (§Custody) — pre-existing, untouched.
- **O5** tree state at report time: HEAD `c4de692e`, fixture clean.

## 6. Residuals / risks / blockers

- **The patch is unapplied** (operator decision). If it is applied, the
  strongest follow-up is a **fresh live replay of the family** to re-earn
  the two green receipts on the folded code; this seat did not replay
  (live-host family, sibling wave-B seats on the lane) and instead
  proves base≡folded on the reachable domain by the executed
  differential (D1–D6, 51 checks) and the receipt oracle (R1–R8).
- **Disclosed unreachable-domain divergences** (T5): a leaf dict not
  produced by `_btwit_r88_load_ns` (no `field`/`value`) would raise
  `KeyError` in the folded copy where base falls back to
  `"sink_name"`/`tag`. No current call path can produce such a leaf
  (S4c/S5c); recorded, not hidden.
- **Inherited, unchanged by this fold**: the lock is fixed **per
  checkout** (L6/L7; r86 F1/F6, r88-scribe ADJ-12, r88-critic F8 — fourth
  round live-witnessed) and **fail-open** when `corpus/live/` is missing
  (L8). Both are design/operator items, not simplifier folds.
- **Receipts are host-only and unpinned** (r88-scribe ADJ-2 class); the
  two green runs are the only replay oracle available in-tree.
- **Blockers: none.**
