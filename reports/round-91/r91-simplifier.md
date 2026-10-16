# r91 SIMPLIFIER — proven folds in the gstfrz block (d78f1cc9)

**Seat** simplifier (r91) · **host** plazir27 (devin substrate) ·
**scope** the r91 landing only — `git show d78f1cc9 -- corpus/fixtures/measure_audio.py`
(**+1501/−3**): the insertion-only `gstfrz` family block (the
`# r91: the Gst CAPTURE-FREEZE MECHANISM` banner → end of
`gstfrz_connect_r91_entry`, **1464 lines**, 5 entry functions, 15 legs + the
resume fixture process) plus its wiring (argparse row, mutex token,
`mode`/`suffix` ternary entries, the 5-row dispatch block in `main()`).
No other block was touched, and no line outside the r91 block changed.

**Writes**: this report + `corpus/live/r91-simplifier/` (census, fold,
battery and comparison tooling; 8 battery summaries; 9 comparison receipts)
+ the archive checkouts under
`/home/vgpnk/Projects/shokunin/r91s/{base,f1,f2,f3}`. **Zero tracked writes,
no commit, nothing landed.** The folds exist only inside the archive
checkouts.

## 0. Axes named for this gate

| axis | direction | what would harm it |
| --- | --- | --- |
| weight | fewer lines / symbols / dead paths in the fixture | — |
| evidence fidelity | the 15-leg receipt surface, the armed laws, the class-armed cells, and the round's provenance comments stay intact | deleting a law, a leg, a recorded claim, or a historical note; changing a receipt key |
| convention consistency | one authority per job; the family-local helper shape (`*_run` knob set, the leg-loop caps, the reader leaf fields, the teardown/block pair) | inventing a second form of an existing helper |
| proof cost | a fold must be provable by a fresh before/after battery on this host | a fold whose proof needs a new measurement, a mutant, or a new leg |

## 1. Custody / tree state

- **Analysis base** = `git archive d78f1cc9` (the landing itself) extracted to
  **`/home/vgpnk/Projects/shokunin/r91s/base`** — under `/home`, **never
  `/tmp`** (44 578 files, 3.2 GB). The folded trees `f1`, `f2`, `f3` are the
  same archive + the fold patches (`fold_apply.py`, exact-string with
  occurrence asserts).
- **Fixture identity** (base): `corpus/fixtures/measure_audio.py` sha256
  **`7f9ee31b3b7f9269333387868a036a54beb38d633abac0a69cf839c434943cb3`**
  (2 032 880 B, 40 591 lines); `corpus/fixtures/gstfreeze_r91_resume.py`
  sha256 **`066d6fff7ba74ef40d11b2f3a71ae336d4ee21c6d73d0975d6dc94fe714b1dc2`**
  = the author's declared value, byte-identical in all four trees.
- **Family block**: lines **37712–39175**, **1464 lines**, sha256
  **`6fe734a8ff7cd530b8790c4ada4cec6fae58216955ef3cbe7d5bc6fc0a52570d`** —
  identical in `d78f1cc9`, in `HEAD` (`a2c6e3b7`) and in the shared worktree,
  and equal to the value declared by `r91-integrate.md` and re-verified by
  `r91-verifier.md`. (The author report's "line 30982" is the block's
  position in the author's own worktree `audio-shokunin-wt-r91`, not in the
  landing; no code effect.)
- **The shared tree MOVED under this seat** (a sibling wave was landing while
  this gate ran): the tracked fixture carries a **pre-existing, actively
  rewritten `M`** — sha256 `e2e5a002a701bf…` when this seat started, and
  `4d0a1fe66eff45d3…` (50 272 lines, +659/−194 vs `HEAD`) by the end, i.e.
  a sibling lane's r90-foldfix/landing work in flight. **This seat touched no
  tracked file**; the r91 block inside the shared tree stayed byte-identical
  to the landing (`6fe734a8…`, 1464 lines, at line 38128) at every check, so
  the analysis base and the landability check are unaffected. The only files
  this seat added to the shared tree are this report and
  `corpus/live/r91-simplifier/` (both untracked).
- **No `lsp` device answers this tree.** The substrate's MCP surface exposes
  exactly one server, `rea` — a Ghidra native-binary provider with no Python
  source semantics and no `references` verb. **Recorded unavailable.** Every
  "no callers" claim below is therefore the **literal fallback**: an AST
  load / call-site / parameter census over the whole 40 591-line module
  (`r91-census.py`, `reach_census.py`) plus `grep`, labelled as such and
  never presented as semantic proof. **No rename is proposed or performed** —
  renaming is exactly the class of change that would need the device.
- **Provenance preserved.** Neither fold deletes a comment line: the only
  hunks are code (the banner, the boundary-correction notes, the
  "recorded, never armed" notes and the r84 F1 fixed-path lock note are
  byte-identical in `f1`/`f2`/`f3`).

## 2. Fold 1 — delete the dead `hooks` timed-event mechanism (dead alternate path)

`_gstfrz_r91_leg` carries **two** timed-event mechanisms: the gated one
(`gates`, the r91 harness law the author report names as this round's own —
"a gated event fires only once the leg has *measured flow*") and the
inherited ungated one (`hooks` → `pending`). The ungated half is dead:

```python
def _gstfrz_r91_leg(name, argv, ctx, out_path=None, env_extra=None,
                    wall_cap=GSTFRZ_R91_WALL_S,
                    byte_cap=GSTFRZ_R91_BYTE_CAP, timeline=0.15,
                    hooks=(), gates=(), stdout_cap=262144,     # <- dead
                    ...
    pending = sorted(hooks, key=lambda h: h[0])                 # <- dead
    pgates = sorted(gates, key=lambda g: g[0])
    ...
        while pending and el >= pending[0][0]:                 # <- unreachable
            _, kind, payload = pending.pop(0)
            try:
                res = _gstfrz_r91_hook(kind, payload)
            except Exception as exc:            # a hook must not kill the loop
                res = {"exc": repr(exc)[:200]}
            rec["fired"].append({"at": round(el, 3), "kind": kind,
                                 "result": res})
```

**Deletion evidence (literal fallback — `lsp` unavailable, §1).**

| probe | result |
| --- | --- |
| call-site census over the whole module (`census-base.txt`) | `_gstfrz_r91_leg` **10 call sites**, every one passing exactly **3 positional** args (`name`, `argv`, `ctx`); kwargs ever used = `out_path` ×9, `wall_cap` ×10, `timeline` ×10, `gates` ×5, `env_extra` ×1, `stderr_cap` ×1, `counts` ×1 — **`hooks` never supplied** |
| writer census | `pending` has exactly one writer, `pending = sorted(hooks, …)`, and one reader, the `while pending …` loop — with `hooks == ()` the list is empty, so the loop body is **unreachable** |
| receipt-shape census (`fired_census.py`) | the ungated loop is the **only** producer of a `fired` entry without `"gated": true` |
| author/verifier receipts | the author's **5 pre-gate draft runs** (084957–085634) recorded 9 *ungated* events each; **every run from 085757 on — the final block's bytes — recorded gated-only**: 92 gated / **0 ungated** across 12 runs (15 author + 2 verifier receipts, `fired-census.txt`) |
| fresh base batteries (this seat) | 3/3 runs: **9 gated / 0 ungated** fired events, all five entries green |
| dynamic-name dispatch | no `globals()` / `eval` anywhere in the module, and the module's only `getattr` is a foreign-process `args` probe in the r8x region — nothing can reach `_gstfrz_r91_leg`'s `hooks` except a call site, and there is none |

The history is visible in the receipts: the mechanism was **replaced by
`gates`** during the round (harness law #1, "gated loss events") and the old
path stayed in the signature. The retained mechanism is exercised 9×/battery
(prop 1, clock 3, resume 2, srcloss 3) with **identical counts and shapes**
in base and folded trees (§5).

**Fold shape** (`r91s/f1`, fixture sha256
`e264961732437a768c7e958dccefee8bb25b0a4db9802ea981fa5c772ea86894`,
40 582 lines / 2 032 415 B; block sha256
`bc9bc5a3d98592929a4f1d0549f7f6c219e8324c778270bb34cd9598da9eb4bd`,
1455 lines):

```diff
@@ block-line 315 @@
-                    hooks=(), gates=(), stdout_cap=262144,
+                    gates=(), stdout_cap=262144,
@@ block-line 346 @@
-    pending = sorted(hooks, key=lambda h: h[0])
     pgates = sorted(gates, key=lambda g: g[0])
@@ the 8-line ungated loop (base block-lines 378-385) @@
-        while pending and el >= pending[0][0]:
-            _, kind, payload = pending.pop(0)
-            try:
-                res = _gstfrz_r91_hook(kind, payload)
-            except Exception as exc:            # a hook must not kill the loop
-                res = {"exc": repr(exc)[:200]}
-            rec["fired"].append({"at": round(el, 3), "kind": kind,
-                                 "result": res})
```

(The minimal diff aligns that third hunk one line earlier — block-lines
377–384 — because the loop's last line, `"result": res})`, is textually
identical to the *gates* append's own tail line; either alignment produces
the same bytes, and the gates append keeps all four of its lines.)

9 lines removed, one parameter removed, no replacement, no new name.
Side effect: `_gstfrz_r91_hook` drops from 2 call sites to 1 — the dispatcher
now has exactly one authority.

## 3. Fold 2 — drop the dead knobs `want_state_drop` / `want_header`

`_gstfrz_r91_frozen_checks` takes three `want_*` knobs; only `want_silent`
is ever supplied:

```python
def _gstfrz_r91_frozen_checks(failures, tag, leg, unl_at,
                              want_silent=True, want_state_drop=True,
                              want_header=True, margin=0.2):
...
    if want_state_drop and states and states[-1] == "running":
    ...
    if want_header and (out.get("riff_size") != GSTFRZ_R91_RIFF_SIZE or
                        out.get("data_declared") != GSTFRZ_R91_DATA_SIZE):
```

**Deletion evidence (literal fallback — `lsp` unavailable, §1).**

| probe | result |
| --- | --- |
| call-site census | `_gstfrz_r91_frozen_checks` has **1 call site** (the clock entry loop): 4 positional args + `want_silent=(tag == "c_quiet")`; `want_state_drop` / `want_header` **never supplied** (nor is `margin`) |
| body census | both knobs default `True` and are the **sole** gates of the state-drop and header assertions → the `False` halves are unreachable |
| receipt surface | the helper's returned cell dict (recorded as `entry["frozen"][tag]`) is built from `sizes_tail` / `states_tail` / `fed_by` / `bytes` / `align_ok` — **no key depends on the two knobs**; both armed checks keep the same condition and the same failure message |
| twin census | no other helper in the 40 591-line module carries a `want_*` knob (`grep want_silent\|want_state\|want_header` → this block only), so no family shape is broken; the *live* knob `want_silent` stays |

**Fold shape** (`r91s/f2`, fixture sha256
`eaa83ced4c145a56caac70897334bb8d1e3cfd7e746e947b54f9062a20f0ea3e`,
40 590 lines / 2 032 762 B; block sha256
`995e86253eb7dabfb31b4682fcbf39d9d0fe8b0871885fc93a6c3d04fac20ae3`,
1463 lines):

```diff
@@ block-line 443 @@
-                              want_silent=True, want_state_drop=True,
-                              want_header=True, margin=0.2):
+                              want_silent=True, margin=0.2):
@@ block-line 474 @@
-    if want_state_drop and states and states[-1] == "running":
+    if states and states[-1] == "running":
@@ block-lines 477-478 @@
-    if want_header and (out.get("riff_size") != GSTFRZ_R91_RIFF_SIZE or
-                        out.get("data_declared") != GSTFRZ_R91_DATA_SIZE):
+    if (out.get("riff_size") != GSTFRZ_R91_RIFF_SIZE or
+            out.get("data_declared") != GSTFRZ_R91_DATA_SIZE):
```

1 line removed, two parameters removed, no new name. `margin` stays: it is a
pass-through of `_gstfrz_r91_post`'s own live default, and deleting it would
only make the *post* helper's knob dead in turn.

**Fold 3 tree** (`r91s/f3` = fold 1 + fold 2, fixture sha256
`b3c310693ebbe393af50cb2d926e5e9a6730ba452d632900d084300c65b77af5`,
40 581 lines / 2 032 297 B, block sha256 `83bdf41f71b8211d…`, 1454 lines) is
the landable union; both patches apply **exactly once** to `HEAD`'s committed
blob and to the shared worktree's blob (`landcheck.txt`), and the union
battery is green (§5).

## 4. Preserved contract

| item | base | f1 (fold 1) | f2 (fold 2) | f3 (union) |
| --- | --- | --- | --- | --- |
| fixture sha256 | `7f9ee31b3b7f…` | `e26496173243…` | `eaa83ced4c14…` | `b3c310693ebb…` |
| fixture bytes / lines | 2 032 880 / 40 591 | −465 B / 40 582 | −118 B / 40 590 | −583 B / 40 581 |
| family block lines | 1464 | 1455 (−9) | 1463 (−1) | 1454 (−10) |
| `python3 -m py_compile` | rc 0 | rc 0 | rc 0 | rc 0 |
| entry functions (5) / dispatch rows (5) / receipt names | present | present | present | present |
| leg census (4/4/1/2/4 = **15**) | 15 | 15 | 15 | 15 |
| lines **outside** the r91 block (banner, wiring, all other blocks) | — | byte-identical | byte-identical | byte-identical |
| wiring splices (argparse row 1×, mutex token 1×, `mode`/`suffix` clauses) | — | untouched | untouched | untouched |
| comment / provenance lines inside the block | — | byte-identical | byte-identical | byte-identical |
| resume fixture sha | `066d6fff…` | `066d6fff…` | `066d6fff…` | `066d6fff…` |
| never-supplied parameter surface (census) | 13 names | 12 | 11 | 10 |

## 5. Fresh before/after batteries (live, archive checkouts under /home)

Eight batteries, one tree each, each with the pinned sha256 of the bytes it
ran (`run_battery.sh` / `run-log.txt`). Serialized against other **gstfrz**
batteries (the family lock is a tree-relative fixed path, so it excludes
nothing across trees); the census on both sides of every run is in the log.
Host contention was real and recorded: **10–15 foreign fixture batteries** in
flight, loadavg 1.5–4.7.

| tag | tree | fixture sha256 (12) | start (UTC) | rc | entry failures | fired (gated/ungated) |
| --- | --- | --- | --- | --- | --- | --- |
| base.before1 | base | `7f9ee31b3b7f` | 10:28:14 | 0 | `{}` ×5 | 9 / 0 |
| base.before2 | base | `7f9ee31b3b7f` | 10:29:11 | 0 | `{}` ×5 | 9 / 0 |
| f1.after1 | f1 | `e26496173243` | 10:30:04 | 0 | `{}` ×5 | 9 / 0 |
| f1.after2 | f1 | `e26496173243` | 10:30:57 | 0 | `{}` ×5 | 9 / 0 |
| f2.after1 | f2 | `eaa83ced4c14` | 10:31:49 | 0 | `{}` ×5 | 9 / 0 |
| f2.after2 | f2 | `eaa83ced4c14` | 10:32:42 | 0 | `{}` ×5 | 9 / 0 |
| base.before3 | base | `7f9ee31b3b7f` | 10:33:34 | 0 | `{}` ×5 | 9 / 0 |
| f3.after1 | f3 | `b3c310693ebb` | 10:35:41 | 0 | `{}` ×5 | 9 / 0 |

Every battery: `failures: {}` and empty `coverage_blocked` in all five
entries, 15 legs, the frozen cells at the pinned wavenc header with
`fed_by == []`, keepalive 0/0, resume `forced: null`, the class-armed shapes
as realized (`p_sink survived_running`, `freeze_idle` + `grows_running`,
`remapfed linked_live`), connect rc 1 / rc 255, teardown census clean.

### 5.1 The pairs, and what differs

`compare_runs_r91.py` projects both receipts onto their **law surface** —
the five entries' `failures` / `coverage_blocked` / `blocked`, the leg-key
census, the fired-event census, the prop lattice, the frozen cells, the
keepalive counts, the resume app status, the class-armed shapes, the connect
rcs/classes, the unload rc/field/value, the teardown census — with every
pid / module index / node id / wall time / sample / distribution-valued size
normalized or dropped (those differ by construction between two live runs).
**484 projected leaves per run.**

| pair | kind | changed leaves |
| --- | --- | --- |
| base.before2 → **f1.after1** | **FOLD-1 primary** | **0 / 484** |
| base.before2 → **f1.after2** | **FOLD-1 second** | **0 / 484** |
| base.before2 → **f2.after1** | **FOLD-2 primary** | **0 / 484** |
| base.before2 → **f2.after2** | **FOLD-2 second** | **0 / 484** |
| base.before2 → **f3.after1** | **UNION (folds 1+2)** | **0 / 484** |
| base.before1 → base.before2 | CONTROL pristine vs pristine | 0 / 484 |
| base.before2 → base.before3 | CONTROL pristine vs pristine | 0 / 484 |
| f1.after1 → f1.after2 | CONTROL folded vs folded | 0 / 484 |
| f2.after1 → f2.after2 | CONTROL folded vs folded | 0 / 484 |

**Reading.** Every pair is green on both sides and the fold pairs are
leaf-identical to their identical-bytes controls. Two observations make this
stronger than a single green pair:

- before the projection normalized the *tree*, the cross-tree fold pairs
  differed in exactly **one** leaf: `entry["app"]`, the recorded path of the
  resume fixture — a tree property, not a fold property;
- the only leaves that differed between two **pristine** runs in this window
  were the family's own *recorded, never armed* distribution-valued fields:
  the frozen `bytes` (135 212–413 740 across the author's window, 204 844 /
  413 740 here), the GST_DEBUG `stderr_bytes` (6 955 / 6 958) and the gate
  fire times (`at`, 1.803 / 1.805 s) — all dropped by the projection, and the
  same classes the r90 window's controls carried.

The union receipt (`f3.after1`) re-derives every declared cell: frozen
`idle` + `fed_by == []` + `align_ok`, headers `0x7FFF0024`/`0x7FFF0000`,
keepalive `resend 0 / popped 0`, prop lattice `true` / `"FALSE"` / absent /
absent with `p_sink survived_running`, resume `clock_lost: true`,
`forced: null`, `errors: []`, `exit: "wall"`, state changes exactly
`null→ready→paused→playing`, shapes `freeze_idle` + `grows_running`,
connect rc 1 / rc 255 / `remapfed linked_live` / control, teardown
`sinks_gone` all true and `own_nodes_after: []` in all five entries.

This window produced **no** class-armed flake in 8/8 runs (the verifier saw
2 reds in 6 full-family runs), so the pairs are read against green controls
*and* against the r90/verifier flake census — not against a lucky run.

## 6. Deletion candidates found but NOT landed

Each is proven dead by the same literal fallback census; none is landed,
because the next deletion would harm an axis.

| candidate | proof of deadness | why not landed |
| --- | --- | --- |
| `_gstfrz_r91_run`'s `keep_raw` (a dead `if keep_raw:` branch) | 4/4 call sites pass 2 positional + `keep_chars`; `keep_raw` never supplied | deletes a capability **and** diverges the helper from the family `*_run` knob set — `_btwit_r88_run`, `_wpstate_r90_run` and `_jack_r95_run` all carry `keep_raw` **live**; the r90 seat declined exactly this class |
| `_gstfrz_r91_run`'s `env` / `wd` | same 4/4 census; the Popen always inherits env/cwd | same: the r84–r87 `*_run` helpers carry `env=`, and the r90 report kept its twin's `env`/`wd` for this reason |
| `_gstfrz_r91_leg`'s `byte_cap` / `stdout_cap` / `keep_chars` | 10/10 call sites pass 3 positional; none of the three ever supplied | the caps are **live guards** (bytecap / stdoutcap / stderrcap) whose values are the family constants; the r81 parent `_gst_r81_leg` carries `byte_cap=GST_R81_BYTE_CAP` in the same shape |
| `_gstfrz_r91_frozen_checks`'s `margin` | 1/1 call site supplies only `want_silent` | pass-through of `_gstfrz_r91_post`'s own live default; folding it cascades a dead knob into the post helper for 1 token |
| `_gstfrz_r91_json`'s `cap` | 1/1 call site passes 1 positional | a capability (the oversize guard), 1 parameter |
| `_gstfrz_r91_src_ensure`'s `name` | 3/3 call sites pass 2 positional | mirrors `_gstfrz_r91_ns_ensure(loads, name=…)`, whose `name` **is** supplied 2× — folding one side creates two shapes for one job |
| `_gstfrz_r91_unload_at`'s `kinds` | 4/4 call sites pass 1 positional | 1 parameter whose default *is* the two unload kinds |
| 4 dead bindings (`_res` ×2, `_sz`, `t_min`) | assigned-but-never-loaded census per function | **weight-neutral** (renames to `_`); `_res`/`_sz` are already underscore-marked by the author, and `t_min` is a 6-tuple element — no axis gain |
| `gstfrz_prop_r91_entry`'s `"pw-play"` tool requirement | AST call-graph reachability: the prop entry reaches 44 module functions and **none of them invokes `pw-play`** — the only invoker, `_gstfrz_r91_play`, is reached only by resume/srcloss/connect; the other mention is `_playback_r78_foreign_clients`'s comm-name **map** (a classification, not a spawn) | deleting it changes the recorded `tools` receipt key (5 → 4) — the receipt surface is the artifact a reviewer diffs (the r90 `"pre": None` precedent) |
| `_gstfrz_r91_teardown` / `_gstfrz_r91_block`'s duplicated kill+unload preamble (~14 lines) | verbatim duplication inside the block | the r89/r90 twins (`_pwprof_r89_teardown`/`_block`, `_wpstate_r90_teardown`/`_block`) carry the same duplication — folding r91 alone creates a second convention for the family |
| `_gstfrz_r91_ns_ensure` vs `_gstfrz_r91_src_ensure` (near-duplicate bodies) | same shape, ~20 lines each | a refactor (kind switch + a new abstraction), not a deletion; the leaf key sets differ per kind |
| the clock entry's loop flag named `hooks` | after fold 1 the name denotes a mechanism the leg helper no longer has (`gates` is what it arms) | a **rename** — the class of change that needs the `lsp` device, which no server answers |
| `_gstfrz_r91_hook`'s `unknown_hook` fallback | the gate kinds in the five entries are exactly {`unload_sink`, `unload_source`, `relink`}, all handled | a 1-line defensive fallback in a dispatcher; deleting it makes an unknown kind return `None` |
| `_gstfrz_r91_dump`'s `clients[*].name` / `links[*].state` | unread by the r91 block | the r81/r82 graph readers build the same `clients` leaf (`name` + application fields) and the r85 reader the same `links` leaf — the reader shape, not dead weight |

## 7. Stop condition

The next deletion would harm an axis. The parameter surface that remains
(§6 rows 1–7) buys a handful of tokens at the price of a capability or a
divergence from a live family helper; the `pw-play` requirement is a *stale
requirement* whose removal changes a recorded receipt key; the teardown
duplication and the reader leaf fields are the family convention; the
`hooks` loop flag is a rename this seat may not prove without the `lsp`
device; and the dead bindings are weight-neutral. Fold 1 and fold 2 are the
two deletions whose weight gain is real, whose proof is a fresh before/after
pair on archive checkouts under `/home`, and whose retained behavior is the
identical 484-leaf law projection with all 15 legs green in 8/8 batteries.
**I stop here.** Nothing is landed and nothing is committed: the adjudicator
owns the landing decision.

## 8. Evidence index (`corpus/live/r91-simplifier/`)

| file | what it is |
| --- | --- |
| `fold_apply.py` | the two folds, exact-string with occurrence asserts (refuses a drifted tree) |
| `r91-census.py` + `census-{base,head,f1,f2,f3}.txt` | AST load / call-site / never-supplied-parameter / dead-binding census per tree (fold 1 + fold 2 proof; the never-supplied surface before/after) |
| `reach_census.py` + `reach-census.txt` | call-graph reachability from each entry (the `pw-play` candidate's proof) |
| `fired_census.py` + `fired-census.txt` | fired-event shape census: 17 prior receipts (92 gated / 45 ungated — the 45 are the 5 pre-gate draft runs) + this seat's 8 batteries (72 gated / 0 ungated) |
| `landcheck.py` + `landcheck.txt` | both folds apply exactly once on `HEAD`'s blob and the shared worktree's blob; folded shas |
| `run_battery.sh`, `summary_run.py`, `run-log.txt`, `*.out` | the 8 batteries: tree, fixture sha, start/end, load, foreign-battery census, rc, per-entry verdict surface |
| `compare_runs_r91.py`, `compare_all.sh`, `cmp-*.txt` | the law projection + the 9 pairs (4 fold, 1 union, 4 identical-bytes controls), 0 changed leaves / 484 |

Archive checkouts: `/home/vgpnk/Projects/shokunin/r91s/{base,f1,f2,f3}`
(each `git archive d78f1cc9` + its fold patch; the family lock file each
battery creates lives at `<tree>/corpus/live/measure_audio-gstfrz-r91.lock`).
The shared tree carries **no** r91 lock and no r91 run receipts; its tracked
fixture is being rewritten by sibling lanes but was never written by this
seat (the r91 block inside it stayed `6fe734a8…`), and the only files this
seat added to it are this report and the evidence directory.
