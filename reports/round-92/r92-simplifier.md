# r92 simplifier — proven folds on the filter-chain block (`ccbce758`, queued, not landed)

**Seat** simplifier (leaf) · **host** plazir27 · **audited revision**
`git show ccbce758:corpus/fixtures/measure_audio.py` sha256
**`4e5fe3e673d8cb586523f3d5462e915c3db255ce4ba0013c5f7157756096ca90`** (the
critic's frozen source). The r92 block (lines **39176–41470**, sha256
`a1b418be71203602eb012084a4e9b12080265cbedd0264babfd6f41b0f992291`) is
**byte-identical in every revision examined** — the landing `ccbce758`, HEAD
at entry (`a2c6e3b7`), the post-move HEAD (`d41cfa68`) and the
sibling-modified working tree — so every fold below applies to the landing
and to the current HEAD with the same bytes.

**Verdict: PASS — 7 proven folds queued (F1–F7).** Primary set F1–F5
(`+42/−77`, net **−35** lines); full set F1–F7 (`+63/−106`, net **−43**). Each
fold is proved by a differential driven by the author's own recorded receipts,
by mutation of the fail-open surfaces, and — for the primary set and the full
set — by fresh live before/after batteries on archive checkouts under
`/home/vgpnk/Projects/shokunin/r92s/`. **Nothing landed, no commit, zero
tracked writes.** Ten further candidates are held with named tradeoffs, and
three negative audits (no unreferenced helper, no unread law key, no
tautology) are reported with their method.

## 0. Axes named for this gate

| axis | direction | what would harm it |
| --- | --- | --- |
| weight | fewer lines / dead paths / duplicate authorities in the fixture | — |
| arm fidelity | every arm keeps measuring the claim it names; the three critic-flagged fail-open surfaces become fail-closed | a fold that weakens or removes an arm, or that lets an absent witness pass |
| evidence fidelity | the 81-leg receipt surface, the armed values, and the round's provenance comments stay intact | deleting a law, a leg, a recorded claim, or a historical note |
| convention consistency | one authority per job; the block's own idioms (`len(gains(...)) != 5`, `in (0, None)`, family-local `_fc92_*` helpers) | inventing a second form of an existing clause or helper |
| proof cost | each fold provable by a differential on existing evidence (replay, mutation, domain table) or one battery pair | a fold whose proof needs a new measurement rig |

## 1. Custody, scratch, and the reference-proof record

- **Analysis base** = the commit-pinned blob above; the block was extracted to
  `corpus/live/r92-simplifier/r92-block.py` (sha256 `a1b418be…`, 2295 lines).
- **The shared tree MOVED under this seat — by sibling lanes, not by this
  seat.** Entry state: HEAD `a2c6e3b7`, working fixture `e2e5a002…` (an
  in-flight sibling foldfix, +768/−210 vs HEAD), `reports/round-90/r90-author.md`
  modified. Exit state: HEAD **`d41cfa68`** ("r98 author: pw-stream …", a
  sibling landing that added +2386/−3 to the fixture), working fixture
  **`4d0a1fe6…`** (a sibling lane's continued edit, +659/−194 vs HEAD). The
  **r92 block is byte-identical (`a1b418be…`) in all four revisions** — the
  ccbce758 blob, both HEADs and the working tree (lines 39592–41887 there) —
  and both patches apply + `py_compile` clean on the new HEAD's bytes
  (re-verified on `d41cfa68`). This seat's only shared-tree writes are this
  report and `corpus/live/r92-simplifier/` (both untracked);
  `git status --porcelain` lists exactly those plus the pre-existing sibling
  modifications. Entry/exit hashes: `shared-tree-entry.txt` /
  `shared-tree-exit.txt` (§8).
- **Archive checkouts under `/home`** (`git archive ccbce758 | tar -x`):
  `r92s/base` (pristine), `r92s/f1` (F1–F5), `r92s/f2` (F1–F7), plus
  `r92s/head` (HEAD) for the landability check. The folded trees carry only
  the fixture diff; their `corpus/live/runs/` additions are this seat's own
  battery receipts (untracked scratch, never in the shared tree).
- **No `lsp` device exists in this seat's toolset, and no language server
  answers `corpus/fixtures/measure_audio.py`.** The only configured MCP server
  is `rea` (a Ghidra-family native-binary annotator: one tool,
  `annotate_native_function`, keyed by procedure address / executable bytes —
  no Python source semantics, no `references` verb). **Recorded unavailable.**
  Deletion candidates were therefore screened by **AST analysis over the whole
  43 k-line module** (definition census, module-wide `Name`/`Attribute` load
  accounting, per-function "assigned but never loaded" census, call-signature
  census) plus a **literal grep fallback**. Neither is semantic proof and
  neither is presented as such; no rename is proposed or performed (a rename
  is exactly the class of change that would need the device). The one
  candidate class decided *semantically enough to be decisive* is the
  call-site census of block-local helpers (every call is a literal `Name`
  call in an enumerable set; the module has no `globals()`/`eval`/`exec`
  code path and no string-built name dispatch — the single `getattr` in the
  file reads a subprocess object's `args` attribute in another family).

## 2. The fold set (queued; nothing landed)

Applier: `fold_apply.py` (every anchor asserted to occur exactly once/twice/four
times, `py_compile` on the result, AST-locality diff in `prove.py`).
Patches: `folds-r92s.patch` (F1–F5, `+42/−77` → net **−35**) and
`folds-r92s-all.patch` (F1–F7, `+63/−106` → net **−43**). All hunks sit inside
the r92 block; **no other family's identifier appears in either diff** (checked
programmatically), and no comment line is deleted except the three duplicate
copies of the daemon-gate comment, which move verbatim into the new helper's
docstring.

| # | fold | site | what it removes | proof | tradeoff |
| --- | --- | --- | --- | --- | --- |
| `F1` | dead second return + 5 dead bindings | `_fc92_shift_ok` (40157) + 5 call sites (41091/41105/41113/41120/41167) | `return bool(ks), ks` → `bool`-returning `any(...)`; `ok, ks =`/`ok, _ks =` → `ok =` (the `ks` list is read **nowhere**; the pre-fix file's only use was `bool(ks)`) | domain table over the reachable input domain (18 deltas × 4 wants = 72 rows, `all_equal: true`, folded returns a `bool`) + the receipt replay | none observed; the arm outcome is the same boolean |
| `F2` | fail-open arm → fail-closed (critic **F3**) | `d_fhi` arm (40905) | `any(abs(v) > 0.05 …)` passes when `gain_db` is absent/empty → adds `or len(gains("d_fhi")) != 5`, **the exact two-clause form `d_copy` already uses** | mutation: delete `gain_db` / set `{}` → base GREEN (0 failures), folded RED (1 failure, `d_fhi`); real receipts (5 probes ≈ 0.0 dB) stay GREEN | pins the probe count at 5 — a legitimate future probe-set change must update the count (same as `d_copy`) |
| `F3` | fail-open witness → fail-closed (critic **F4b**) | `a_ports_none` (40608) | `.get("rc") == 0` passes when `feed_link` is absent → `.get("rc") in (0, None)` (module idiom: `… not in (0, None)` at 13864/15876; the sink-side mirror already fails on absence via `!= 0`) | mutation: delete `feed_link` → base GREEN, folded RED; `rc=0` → RED in **both** (the existing fail-closed case is preserved); real receipts (`rc 255`) stay GREEN | a spawn-error `rc=None` now reads as a failure — which is the intent (unmeasured ≠ refusal) |
| `F4` | unarmed recorded field → armed load half (critic **F4a**) | `i_*` silent loop (41146) | the five `i_*` legs recorded `load.load_text` but **no arm read it** (strip it, or inject `[E]`/`failed file` → base stays GREEN) → the loop now fails when the recorded load reply carries `[E]` or `failed file` | mutation: inject an `[E]` line into the five legs' `load_text` → base GREEN (0), folded RED (5); control on a non-silent leg (`i_2tap`) → GREEN in both (the arm is scoped to the silent class); real receipts (clean 500-char replies) stay GREEN | **the only fold that adds weight (+5 lines)**; it reads the *recorded/truncated* (500-char) reply — a failure line beyond the truncation is invisible, i.e. the arm is bounded by the recorded artifact |
| `F5` | duplicate authority → one helper | four **byte-identical 16-line** daemon gates (40434/40748/41001/41270; all four copies sha16 `f5e0f5c61d43b881`) | 4 × (comment + 16-line gate) → `_fc92_daemon_gate(entry, failures)` + 3-line call site ×4 | gate differential on synthetic heads (`daemon_bad`, `daemon_bad_killed`, `daemon_ok`, `tools_missing`): the blocked entry, the failure text, the key set and the tool dict are **identical** base vs folded; the emitted strings are byte-equal by construction (`why` + `" — the entry is unmeasurable"`) | −38 lines; the gate text now lives in one place — a future per-entry gate difference must become a parameter (the four copies were byte-identical today) |
| `F6` | duplicate authority → one helper | the two audio entries' **byte-identical 10-line validity-gate bodies** (dsp 40857 / ir 41066; dedented sha16 `4cce8885e84d231b`) | two loop bodies → `_fc92_valid_gate(entry, failures, tags, legs)` + one call line each | receipt replay: identical entries; static: changed defs exactly the intended set; the bodies differ only in the loop header (`legs_spec + CLAMP_EXTRA` vs `specs`) | −2 lines only (the helper's 3-line provenance docstring eats the gain); a low-weight dedup whose value is the single authority, not the lines |
| `F7` | unreachable branch (optional) | `_fc92_block` (39932) | the `ctx` parameter and its `if ctx is not None:` cleanup branch (6 lines) — **8/8 call sites pass 3 args**, and every call site runs *before* `ctx = _fc92_ctx()` exists, so the branch is unreachable, not merely unsupplied | call-site census (8/8 3-arg, no kwargs) + control-flow placement + gate differential (the `_fc92_block` output on the gate paths is identical with the branch gone) | −6 lines, but it diverges the family-local `_*_block` signature from the sibling blocks (`_gstfrz_r91_block(…, loads=None, players=())` etc.) whose cleanup params **are** supplied by their call sites. Queued last; land it only if the integrator accepts the shape divergence |

Weight accounting (measured, file line counts): base 42916 → F1–F5 42881
(−35) → F1–F7 42873 (−43); per fold: F1 −3, F2 +1, F3 0, F4 +5, F5 −38,
F6 −2, F7 −6.

## 3. Proofs (no live probe needed)

Harness `prove.py`; results `prove-base-f1.json`, `prove-base-f2.json`,
`prove-base-f1f6.json`.

**A — replay differential on the author's own receipts.** The four committed
entry functions of base and folded trees were executed verbatim with only
their *measurement layer* stubbed from each receipt's own recorded legs
(run A `…094024556467Z`, run B `…094602455160Z`). **All four entries are
byte-identical between base and folded in both runs (`entries_identical:
true`, 8/8), with `failures: []` on both sides** — the folds change no
recorded value, no receipt key and no law outcome on real bytes.

**A2 — mutation of the fail-open surfaces** (the critic's F3/F4b/F4a
verified closed):

| mutation | base | folded |
| --- | --- | --- |
| `d_fhi.gain_db` deleted / set `{}` | GREEN (0 failures) | **RED** (`d_fhi`, 1 failure) |
| `a_ports_none.feed_link` deleted | GREEN | **RED** |
| `a_ports_none.feed_link.rc = 0` | RED | RED (preserved) |
| `[E]` injected into the five `i_*` `load_text` | GREEN (0) | **RED (5)** |
| `[E]` injected into a non-silent leg (`i_2tap`) | GREEN | GREEN (control: the arm is scoped) |

**B — gate differential.** Synthetic entry heads exercised the base inline
gates and the folded helper: `daemon_bad`, `daemon_bad_killed`, `daemon_ok`,
`tools_missing` — **identical** blocked entry, failure list, key set and tools
dict in all four cases (the emitted `daemon unreachable…` text and its
`— the entry is unmeasurable` suffix are byte-equal).

**C — `_fc92_shift_ok` domain table** (F1): 72 rows over `delta ∈ {None, ±,
0, 48, 110, 480, 1024±2, 1024+110, 2431±4096, 10000, ±0.0, bools}` ×
`want ∈ {0, 48, 110, 2431}` — `all_equal: true`.

**D — static.** `_fc92_block` call sites: base **8/8 three-argument, no
kwargs**; folded 5 direct + 4 through the gate helper. Changed top-level defs
(full set): `_fc92_shift_ok`, `_fc92_daemon_gate` (new), `_fc92_valid_gate`
(new), `_fc92_block`, and the four entries — exactly the intended set; no
module-level name removed. Post-fold dead-local census of the block: clean
except the deliberate `_`-prefixed discards (`_br`/`_ba` in the struct unpack,
`_` loop targets, `_spa_*`/`_lv2_*`/`_dn`) and the held-to-exit family-lock
locals in `main()`.

**Negative audits.** (1) **No unreferenced helper**: all 78 module-level names
defined by the block have ≥1 load/call site. (2) **No law reading a
never-emitted key**: the replay drives the real verdict code from the
receipts' own legs, so every key an arm reads must resolve — a never-emitted
key would surface as `None` and a failure (or a crash); all four entries
replay green on both runs. (3) **No tautology found**: the disclosed shape
witnesses (`a_load_dbg5`'s line floor, the modulo-1024 alias window, the
1.0/1.5 dB min-side bands) are the author's own; no new one was introduced.
The error-class census over all three receipts shows every class exercised
except `fc92_load_refused` (0 hits — the generic refusal is always shadowed by
a specific class; a fallback row, held, §6).

## 4. Live before/after batteries (archive checkouts under `/home`)

Batteries run with the family's own narrow check
(`python3 corpus/fixtures/measure_audio.py --probe-filterchain-r92`), each from
the tree named, `TMPDIR=/home/vgpnk/Projects/shokunin/tmp`, its own
`UFO_FC92_SCRATCH`, and the family lock at the tree-relative fixed path.

| tag | tree | fixture sha256 (16) | receipt | rc | failures | legs |
| --- | --- | --- | --- | --- | --- | --- |
| before | `r92s/base` | `4e5fe3e673d8cb58` | `20261016T102647520611Z-filterchain-r92` | 0 | `{}` | 26+20+18+17 = 81 |
| after | `r92s/f1` | `93df3b2963d7da65` | `20261016T103730209431Z-filterchain-r92` | 0 | `{}` | 26+20+18+17 = 81 |
| after-all | `r92s/f2` | `2801313dff792d93` | `20261016T104342264444Z-filterchain-r92` | 0 | `{}` | 26+20+18+17 = 81 |

All three batteries are **green on all four entries** with `own_nodes_after: []`
everywhere and the author's law values reproduced on this host: `d_fhi` 5
probes ≈ 0.0 dB, `d_gneg140` @200 Hz **−46.566 dB** (both author runs:
−46.566), `a_ports_none` feed `rc 255`, `a_ports_sink` feed `rc 0`, the five
`i_*` legs `out_nz_exact 0` with clean load replies and their activation
classes, residuals **0.5 / 0.5 / 0.0 LSB** with 0 samples > 1 LSB. All three
ran under contention (before: 3, after: 4, after-all: 2 foreign fixture runs
live; `host_is_quiet: false`).

**Narrow checks on the folded trees** (the round's own wiring check):
`python3 corpus/fixtures/measure_audio.py --help` → rc 0 in both `f1` and
`f2`, and `--probe-filterchain-r92 --probe-gstfrz-r91` → rc 2
`measure_audio.py: error: choose one probe mode` — the r92 flag still
participates in the probe mutex, and neither check wrote a run dir, receipt or
lock.

**The pair comparison is decisive: base vs f1 differ on 0 of the 1838
projected law-surface leaves, and base vs f2 (the full F1–F7 set) also differ
on 0 of 1838** (`cmp-base-vs-f1.json`, `cmp-base-vs-f2.json`; the projection
keeps every leaf the arms read plus the stable recorded census — classes,
shape witnesses, host pins — and normalizes ids, pids, module indices, wall
times, byte counts, raw logs and scratch paths). **The pairs are read against
a control**: the author's own two runs (identical bytes, different windows)
differ on exactly **12 projected leaves in two named classes** under the same
projection — `d_qneg.gain_db` (the clip-ceiling instrument spread, ±0.05 dB)
and `i_clip`'s block-quantised capture-start indices (`delta_samples`/
`peak_delta`/`out_first[0]`/`out_top[i][0]`/`ref_first[0]`/`ref_top[0][0]`,
all arm-irrelevant for that leg). The fold pairs' 0 changed leaves is
therefore *tighter than the instrument's own noise floor*: the folds are
behaviour-identical on the law surface, not merely within tolerance.

## 5. Preserved contract (what a landing must not lose)

1. All 4 entries and all **81** legs stay wired in `main()`
   (`--probe-filterchain-r92`); the argparse row, the mutex token, the
   `mode`/`suffix` ternaries and the 28-line dispatch block are **untouched**
   (all diff hunks are inside the block).
2. Every armed law and armed value is unchanged; the folds close three
   fail-open surfaces (F2/F3/F4), remove one dead return (F1) and two
   duplicate authorities (F5/F6), and delete one unreachable branch (F7,
   optional). No law name, no band and no expected value changes.
3. The receipt surface is preserved: no key added or removed (projection:
   1838 leaves on both sides), no recorded claim deleted, no leg dropped.
4. Provenance is preserved: every comment of the block survives except the
   three duplicate copies of the daemon-gate comment, whose text moves
   verbatim into `_fc92_daemon_gate`'s docstring; the `ROUND 92` banner, the
   "recorded, never armed" notes and the r84 F1 lock note are byte-identical.
5. Nothing in this report edits another seat's artifacts; the patches are the
   only landable diff. The `__pycache__` churn of the checks happened in the
   archive trees, never in the shared tree.

## 6. Deletion candidates found but NOT queued (with the tradeoff that holds them)

| # | candidate | proof of deadness | why held |
| --- | --- | --- | --- |
| `H1` | the never-supplied parameter group: `_fc92_f(nd=6)`, `_fc92_run(env=)`, `_fc92_spawn(env=)`, `_fc92_reap(term_s=)`, `_fc92_session_load(env=, quiet_s=)`, `_fc92_session_cmd(quiet_s=)`, `_fc92_load_leg(props=)`, `_fc92_audio_leg(fmt=, media_class=)`, `_fc92_audio_attempt(fmt=)` | call-signature census: each default is never overridden in the block (e.g. `_fc92_f` 11/11 calls pass `nd`; `props` 0/20; the `fmt` chain is `"s16"` at every site) | deletes *capabilities* (the no-props load shape the scout used, the f32 capture path the critic's optional #7 wants for armability) for 1–2 tokens each; r90's §6 precedent holds this class |
| `H2` | inline `_fc92_text` (one caller: `_fc92_cli_close`) | AST load census: 1 call site | 3-line named step; r89/r90/r95 keep 1-caller helpers (`_jack_r95_json`, `_wpstate_r90_lock_text`); inlining is weight-neutral at best |
| `H3` | `_fc92_dir_scan` returns `(files, dirs, sos)`; the SPA call site uses only `files`, the LV2 call site only `sos` | AST: 2 call sites, 1 used element each | splitting the return into two functions is a second convention; the `_spa_dirs`/`_lv2_files` bindings are `_`-prefixed deliberate discards |
| `H4` | `("fc92_load_refused", …)` table row | recursive `error_class` census over all three receipts: **0 hits** (every refusal carries a specific class first) | it is the table's weakest fallback row: an unclassified refusal would otherwise fall through to the inherited r88 chain under a different name; deleting it removes a fallback, not a dead path |
| `H5` | `d_qneg`'s recorded clip-ceiling vector / `i_clip`'s recorded capture indices | arm read: neither is armed (F1a is pinned by the falsification + shape arm) | deleting recorded-not-armed values costs the receipt surface the critic diffed against; the author's own two runs differ on them (§4) |
| `H6` | the four inline tools blocks (3 identical + 1 variant) | byte-identity: 3 copies identical; the wpx tuple differs | hoisting them would move `entry["not_armed_by_policy"]` (interleaved at the arm site) relative to the gate, changing the *blocked-path* receipt key order; F5 covers the byte-identical daemon gate only |
| `H7` | `_fc92_wav_read`'s `_br`/`_ba` discards | dead-local census | idiomatic struct-unpack discard; removing them needs a second unpack form (two `unpack_from` calls) |
| `H8` | `a_load_dbg5`'s `log_stats.lines < 500` | author-disclosed shape witness, not a law | a *shape* witness is the point of the leg; deleting it weakens the load-half evidence |
| `H9` | `_fc92_valid_gate`'s call-site tag extraction (a list comprehension at each site) | n/a | the alternative (passing the spec lists + arity) is a second convention; the current call sites are the minimal form |
| `H10` | the critic's other half of **F4a**: require every `err_lines` entry to match an activation pattern | the activation class is already armed via `error_class` (from the class table) | that is an arm *strengthening* (a new pattern list), not a weight fold; it is the author/verifier's move, and the `err_lines` field itself is already recorded |

## 7. Stop condition

The next deletion would harm an axis. What remains is (a) *recorded-not-armed
receipt evidence* (`H5`, and the recorded fields generally), whose removal
costs the receipt axis the critic and verifier diff against; (b) *capabilities
whose only fault is being unused* (`H1`, `H2`, `H3`), whose removal costs the
convention/armability axis (the f32 path is the critic's own recommended
armability move); (c) *fallback rows and shape witnesses* (`H4`, `H8`), whose
removal trades a named class for silence; and (d) the *optional shape
divergence* (`F7`). Beyond F1–F7 the block has no dead path, no unreferenced
helper, no duplicate authority and no unread law key left that can be removed
without paying one of those axes.

## 8. Evidence index (scratch, untracked) and exit state

`corpus/live/r92-simplifier/`: `fold_apply.py`; `census.py` +
`census-base.txt` / `census-f1.txt`; `prove.py` + `prove-base-f1.json` /
`prove-base-f2.json` / `prove-base-f1f6.json` (+ logs); `compare_runs.py` +
`cmp-authorA-vs-authorB.json` / `cmp-base-vs-authorA.json` /
`cmp-base-vs-f1.json` / `cmp-base-vs-f2.json`; `r92-block.py`,
`base-full.py`; the patches `folds-r92s.patch`, `folds-r92s-all.patch`,
`folds-r92s-optional-ctx.patch`; `shared-tree-entry.txt` /
`shared-tree-exit.txt`.
Archives: `/home/vgpnk/Projects/shokunin/r92s/{base,f1,f2,head}` (+
`scratch-base/`, `scratch-f1/`, `scratch-f2/`).

Patch checks: all three patches apply cleanly (`patch -p1`) to the pristine
base and to a HEAD checkout, produce the recorded folded hashes, and
`py_compile` clean — primary (F1–F5) on base → `93df3b29…`, all (F1–F7) →
`2801313d…`, optional-ctx (F7 alone) → `4297745d…`; the all-patch on the
pre-move HEAD (`a2c6e3b7`) → `64e559e8…`, and on the post-move HEAD
(`d41cfa68`, the r98 sibling landing) it applies and `py_compile`s rc 0. The
patches are independent (each lands on the pristine base/HEAD); they are not
composable by `patch` (the combined tree is the all-patch).

**Exit state**: the shared tree's tracked modifications are exactly the two
pre-existing sibling edits (`corpus/fixtures/measure_audio.py` — the sibling
lane's continued work — and `reports/round-90/r90-author.md`); this seat's
additions are untracked only. No `r92a_` node, module or process from this
seat's batteries survives (`pw-cli ls Node`/`ls Module` grep: 0/0); the
archive trees' `measure_audio-filterchain-r92.lock` files are the family's
per-tree lock files, held by no process.

*Leaf seat — queued folds, landed nothing, did not judge, admit, integrate or
ship.*
