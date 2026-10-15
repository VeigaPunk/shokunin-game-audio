# r83 SIMPLIFIER — YAGNI/dead-code review of the `a151a226` r83 landing (read-only, patch NOT applied)

**Seat** simplifier (r83) · **host** devin · **scope** the r83 pw-cat /
pw-record / pw-loopback landing only: `git show a151a226 --
corpus/fixtures/measure_audio.py` (**+2426/−3**; family block `:16315`–`:18702`,
**2395 inserted lines**, 7 entry functions / 128 legs / 40 helper defs) plus
its 5 CLI wiring surfaces. **Writes**: this report +
`corpus/live/r83-simplifier/` only. **Zero tracked writes, no commit, the
patch is NOT applied.**

## Custody / tree state at report time

- Analysis base = the **commit-pinned blob**
  `git show a151a226:corpus/fixtures/measure_audio.py`, sha256
  **`26431adf29ab122bbf1f55ef03c9aa47bf9825c61654562d9a421117434f5eea`**
  (19811 lines; git blob `27fe971077f64de3a6339fba10294fa2d61d666b`), copied
  byte-identically to `proofs/base-measure_audio.py`
  (`proofs/sha256.txt` §1). Every line number in this report is a
  **a151a226-pinned** line number.
- **The working tree MOVED under this seat** and is *not* the analysis base:
  HEAD advanced `a151a226` → `bc3f55ca` → `52c5d807` → `2b221233` during the
  window, and `corpus/fixtures/measure_audio.py` now carries a **sibling
  seat's uncommitted fold of the r82-simplifier patch + r82 tone-pair
  changes** (`git diff --numstat HEAD`: +198/−77 at report time). I verified
  by content that the drift is entirely **outside** the r83 block and that
  the r83 block is **byte-identical** between the working tree and the
  commit-pinned blob (2388 lines both, `proofs/sha256.txt` §2). The
  deliverable is anchored to the pin, not to the moving tree.
- **No `lsp` device answers this file on this substrate.** The only external
  device present is the `rea` Ghidra/native-REA MCP (binary/JS artifacts — its
  subject format has no Python source). **Recorded unavailable**; all
  reference proofs are literal AST/`grep` census over the pinned blob plus an
  executed differential on scratch copies. No symbol-aware rename/edit was
  performed, so the `lsp` fallback rule is not engaged.
- **probeParent**: exactly **one** read-only `ufo-labrat` was dispatched
  (agent `7efed093`; verdict verbatim at `proofs/labrat-probe.txt`). It
  reported **NOT-FALSIFIED on all six items I gave it** and independently
  surfaced a **seventh dead store** (`tapf = None` in two legs), which I
  re-derived from the pinned blob myself (AST dominance check, S8) and
  **folded into the patch as T7**. Its line numbers are against the *moving*
  working tree and are offset from the pin (its T1 = 17034, pinned 16939;
  offset varied +94…+118 while it ran) — content-level claims all match.
- **No fresh full-family replay.** The r83 family is live-host data; a
  folded replay would need a live PipeWire/WirePlumber host, would take the
  full 128-leg wall time, and sibling seats (`r83-reviewer`, `r83-scribe`,
  `r100-boundary`) were committing and probing concurrently during this
  window. The **two pinned author runs** are the replay oracle and their
  verdict surfaces are re-verified here (`proofs/receipt-census.txt`).

**Proof classes used below** — `[S]` static reachability over the pinned blob
(AST dominance / call-site census; no path to the deleted code), `[R]`
receipt census across **both** pinned runs (0-hit or realization counts),
`[D]` executed differential base-vs-folded on scratch copies (53 checks),
`[P]` `patch -p1` round-trip byte-identity.

## 0. Summary

**Verdict: PASS (gate green, no blocker).** The r83 landing is
insertion-only, structurally clean and correctly wired; the r83 block's
dead-code surface is **small and tight** — 7 provably dead items, 24 lines
touched, net **−8 lines**, all inside the family block, delivered as an
**unapplied** 12-hunk patch. Every item carries a static reachability proof,
a 0-hit/realization census over both pinned runs, and an executed
differential; **no item changes any verdict**, and only T3 changes a receipt
leaf (one always-`[]` key, disclosed). Nothing in the round's falsification
envelope was pruned.

| # | item | class | base lines | Δ | proofs | tier |
|---|---|---|---|---|---|---|
| T1 | `_pwcat_r83_lb_leg` `ftag` write-only loop var | dead store | 16939 | ±0 | S,R,D | A |
| T2 | `(leaf or {})` dead falsy guard ×2 (`teardown`, `block`) | dead guard | 16563, 16599 | ±0 | S,R,D | C |
| T3 | `_pwcat_r83_rec_leg` `extra` param + `*extra` argv slot + `extra_argv` leaf | dead param / dead expression | 17046–17047, 17049, 17058, 17066 | ±0 | S,D | C |
| T4 | `cons[0] == nsb` / `cons[0] != nsb` subsumed by `own_names` ×2 | redundant predicate | 18640, 18668 | −2 | S,D | B |
| T5 | `if c.get("min") is None: continue` never true | dead guard | 18437–18438 | −2 | S,D | C |
| T6 | `move_rc is None and not move_skipped` failure arm unreachable | dead conditional | 18259–18262 | −4 | S,R,D | B |
| T7 | `tapf` component of `tap = tapf = None` ×2 | dead store | 16853, 16982 | ±0 | S,D | C |

Totals: **+10/−18 lines across 12 hunks → net −8 lines** (19811 → 19803),
**13 replacement sites**, every hunk inside the r83 family block.
`git apply --numstat`: `10 18 corpus/fixtures/measure_audio.py`.

**Tier A** = never-executed code with no receipt surface. **Tier B** =
verdict-superseded / logically subsumed predicate with a **provably** zero
behavioural delta (including the message text). **Tier C** = dead guards,
dead payload params and dead stores, provably unreachable from the current
call graph — separable hunks the operator may retain as input-contract
guards or mirror-vocabulary.

## 1. Deliverable

- `corpus/live/r83-simplifier/r83-simplifier.patch` — sha256
  **`b969518cfc67f7eb643588d61bc125b0e988828843c5a115c5cf3e7863a1ef65`**,
  12 hunks, `git apply --check` **clean** against the live working tree *and*
  `patch -p1` clean against the commit-pinned blob
  (`proofs/patch-check.txt`, `proofs/differential.txt` D0). **Not applied.**
- `corpus/live/r83-simplifier/folded/measure_audio.py` — sha256
  **`6e394434940797b25a275697a2b58b0e230a391c583ddc0502c35d8e503883e4`**,
  19803 lines; `python3 -m py_compile` clean (`proofs/pycompile.txt`); a fresh
  `patch -p1` of the patch over a scratch base copy is **byte-identical** to
  it (D0).
- `corpus/live/r83-simplifier/proofs/` — the pinned base copy (== committed
  blob), `fold-r83-simplifier.py` + `fold-apply.txt` (13 exact-match
  replacements, each asserted to match **exactly once**; the fold aborts on a
  0- or multi-match, which is how the *file-wide homographs* were caught and
  context-anchored — `proofs/homographs.txt`), `static-proofs.py`/`.txt`
  (S1–S8, 29/29 PASS), `receipt-census.py`/`.txt` (20/20 PASS), `census.py`/`.txt` (defs /
  constants / call sites / param use / write-only locals),
  `params.py`/`.txt` (rigorous per-parameter supply census),
  `differential.py`/`.txt` (D0–D8, 53/53 PASS), `labrat-probe.txt`,
  `homographs.txt` (the file-wide homograph census that forced every fold
  anchor to be context-anchored), `sha256.txt`, `patch-check.txt`,
  `pycompile.txt`.
- `corpus/live/r83-simplifier/manifest.json` + `manifest.sha256` — sha256
  census of all **21** seat files (1 032 371 B folded + 1 032 825 B base +
  91 620 B of proofs/patch; 2 157 816 B total).

## 2. Items — remove / proof / receipts

### T1 — `ftag` is a write-only loop variable `[S][R][D]`

**(a) Change** `:16939` `for ftag, f in feeds.items():` →
`for f in feeds.values():` (the body only uses `f`; the `cell["feeds"]`
comprehension two lines below rebinds its own `k`).

**(b) Proof.** `[S]` AST: inside `_pwcat_r83_lb_leg`, `ftag` has exactly
**1 `Store` / 0 `Load`** (S1); the whole-block census finds `ftag` to be the
**only** write-only local in the r83 block (S7). The identical spelling at
`:9179` **is** live (`fired.append({"kind": "feed_reap", "tag": ftag, …})`)
— so the naive first-line anchor aborted the fold with `2 matches` and was
re-anchored on the following `cell["feeds"]` line (`proofs/homographs.txt`).

**(c) Receipts.** `[R]` `feeds` is a receipt leaf on **51 lb-legs per run**
(102 across the two pinned runs); the folded copy produces the identical leaf
`[D]` D3 (`{'r83a_<pid>_t1_feed': {'exit_code': 0}}`) with the identical
killpg sequence and an identical cell on the verdict surface. No leaf
changes.

### T2 — `(leaf or {})` is an unreachable falsy guard, both sites `[S][R][D]`

**(a) Change** `:16563` and `:16599`
`_pwcat_r83_unload_own((leaf or {}).get("module_id"), tag)` →
`_pwcat_r83_unload_own(leaf.get("module_id"), tag)`.

**(b) Proof.** `[S]` `_pwcat_r83_ns_load` returns `leaf` on **every** return
path (2/2) and every `leaf = …` binding in it is a **dict literal** (2/2) —
it cannot return `None` (S2). All 7 sink loads in the family are built as
`loads[nm] = _pwcat_r83_ns_load(nm[, extra])` (S2), and every `loads`
argument to `_pwcat_r83_teardown` (7 sites) / `_pwcat_r83_block` (14 sites)
is such a dict, so the `or {}` fallback can never be selected. The sibling
`(loads or {})` **is** live (6 call sites pass `loads=None` — the
`sinks/monitor did not enumerate` block path) and is retained.

**(c) Receipts.** `[R]` both runs' `unloads` maps carry **14 entries** (2
sinks × 7 entries), every one derived from a `module_id`, and `sinks_gone` is
all-true with `own_nodes_after` empty on every entry (census H). `[D]` the
folded copy executes the same unload path (D3's cell comparison covers the
teardown input shape; `_pwcat_r83_unload_own` delegates to
`_gst_r81_unload_own` unchanged). No leaf changes.

### T3 — `_pwcat_r83_rec_leg`'s `extra` is never supplied `[S][D]`

**(a) Change** the keyword-only parameter at `:17046–17047`, the docstring's
`[extra]` token at `:17049`, the `*extra` argv slot at `:17058`, and the
`"extra_argv": list(extra)` leaf at `:17066` (the argv splice becomes
`argv += ["-P", f"node.name={tag}", "--target", sink, …]`).

**(b) Proof.** `[S]` `_pwcat_r83_rec_leg` has exactly **one** call site
(`:17339`, `legs["pr_land"]`), which passes `props`/`sink`/`frames`/
`sample_at` and **no** `extra` (S3) — so the slot is always `[]` and the leaf
is always `[]`. The parallel `_pwcat_r83_play_leg.extra` **is** live
(`:18362` `extra=("--rate", "48000")`, S3 contrast) and is retained.

**(c) Receipts.** `[R]` `extra_argv` is carried by only **3** legs in
`props_parse` (`pc_drop`, `pr_land`, `pc_multi` — the 2 play legs and the 1
rec leg) and the `pr_land` row's value is `[]` in both pinned runs. `[D]` D2 runs the real function with a stubbed
spawn: **every** cell key is identical base-vs-folded and the redacted `argv`
is byte-identical; the **only** delta is the removed `extra_argv` key.
**Disclosed surface delta**: the `pr_land` receipt row loses the always-empty
`extra_argv` key. `[D]` also documents the removed surface — base accepts
`extra=("--rate","44100")` and changes its argv (proving the knob was real,
merely never exercised); folded raises `TypeError`. Drop this hunk if the
ledger wants to keep the (always-`[]`) key.

### T4 — `cons[0] == nsb` / `cons[0] != nsb` are subsumed `[S][D]`

**(a) Change** `:18640` (drop the disjunct `cons[0] == nsb or \`) and
`:18668` (drop the conjunct `cons[0] != nsb and`).

**(b) Proof.** `[S]` `own_names = {nsa, nsb}` is defined once, at `:18605`
(S4), before both tests. In `p_empty` the disjunction is
`len(cons) != 1 or cons[0] in own_names or cons[0] == nsb or cls != Audio/Sink`
— `cons[0] == nsb` implies the preceding `cons[0] in own_names`, so the
disjunct is dead. In `n_empty` the conjunction is
`len(cons) == 1 and cons[0] not in own_names and cons[0] != nsb and cls == Audio/Sink`
— `cons[0] not in own_names` implies `cons[0] != nsb`, so the conjunct is
dead. Both are strict set-membership subsumptions, not coincidences.

**(c) Receipts.** `[R]` the arm is realized (`n_empty.outcome =
failopen_foreign_sink` in both runs). `[D]` D5 replays the **exact source
slice** of each condition from both copies over 18 synthetic
`(consumers, class)` cells: **identical boolean for all 18** in both tests,
and both surviving conditions are non-degenerate (each arm realized:
17/18 fire for `p_empty`, 1/18 ok for `n_empty`). The failure **messages**
do not mention the removed terms, so even the text is unchanged.

### T5 — `if c.get("min") is None: continue` can never execute `[S][D]`

**(a) Change** delete `:18437–18438` (the guard) inside the `s4_peaks` loop,
pinning the helper's output contract to a channel leaf that always carries
`min`.

**(b) Proof.** `[S]` `chans` is read from `leg["tap_stats"]["channels"]`
(4 sites); `tap_stats` has exactly **one** producer — `_pwcat_r83_channel_stats`
at `:17039` (S5) — and `out["channels"] = chans` exactly once (`:16701`),
where each per-channel `leaf` is a dict literal carrying `min` (S5). If
`"channels"` exists at all, every element has `min`, so the `continue` is
unreachable. The **line immediately after** the deleted guard is
`if c["min"] < -64 or …` — the guard was protecting a `KeyError` that the
producer cannot cause.

**(c) Receipts.** `[R]` `s4_peaks_*` legs carry `tap_stats.channels` with
`min`/`max`/`mean`/`neg_frac` in both runs (3 legs × 2 runs), and
`s4_peaks`' `artifact_outcome` is `full_wave_abs_octave` in all of them. `[D]`
D6 runs `_pwcat_r83_channel_stats` on a real tone and on a missing path:
byte-identical dicts, every channel leaf carries `min`. No leaf changes.

### T6 — the `dm_move` "move never fired" arm is unreachable `[S][R][D]`

**(a) Change** `:18259–18262` collapse to a single positive guard:
`if leg.get("move_rc") is not None:` … (dropping the `if move_rc is None: if
not move_skipped: failures.append(…)` arm and its `else:`).

**(b) Proof.** `[S]` `move_rc` is assigned **only** inside
`if si.get("entry_found"):` (`:18123–18127`) and `move_skipped` **only** in
the matching `else:` (`:18132–18134`), with a non-empty literal string (S6).
The two branches are exhaustive over `si.get("entry_found")`, so
`move_rc is None` ⟹ `move_skipped` truthy ⟹ the inner `not …` is always
False. The arm cannot fire on any host, with any pw-cat version.

**(c) Receipts.** `[R]` the arm has 0 hits in both runs (F9: `move skipped`
count 0/2 runs) and can have none. `[D]` D4 replays the exact verdict slice
from both copies over 4 synthetic legs (`moved_ok`, `moved_bad`, `moved_rc`,
`skipped`): **identical failure lists**; the removed arm is silent in **both**
copies (0 failures for `skipped`), while the surviving rc/consumer arms still
fire (1 failure each) and the clean case stays silent. `move_skipped` remains
a receipt leaf (unread by any verdict — recorded, not gated).

### T7 — the `tapf` half of `tap = tapf = None` is a dead store ×2 `[S][D]`

**(a) Change** `:16853` (`_pwcat_r83_lb_leg`) and `:16982`
(`_pwcat_r83_play_leg`) from `tap = tapf = None` to `tap = None` (the `tap`
half **stays** — it is read by the `if tap is not None:` blocks).

**(b) Proof.** `[S]` in both legs `tapf` has exactly 2 `Store`s (the chained
init and the assignment inside the tap branch) and no `Load` before the init;
every post-init `Load` sits under the `if tap is not None:` guard, and
`_playback_r78_tap` has exactly **one** return — `subprocess.Popen(...)` —
so it can never return `None`, i.e. `tap is not None` ⟹ the tap branch ran ⟹
`tapf` was assigned (S8). The file contains the same `tap = tapf = None`
spelling in two **other** families (`:6568`, `:9213`); the r83 fold is
anchored on the following `f"r83a_…"` filename literal so only the r83 sites
move.

**(c) Receipts.** `[R]` the tapped legs are realized in both runs (13
`bound_producers` leaves in `channel_matrix`; `tap` on 18/18 remix legs and
15/15 resample legs). `[D]` D8 runs both legs with a tap installed
(stubbed spawn) — cell keys and verdict surface identical, the `tap` leaf
produced by both copies — and the untapped path produces no `tap` leaf in
either copy (`tapf` never read). No leaf changes.
**Disclosed caveat**: after the fold `tapf` is bound only on the tap path.
That is provably safe today (the only reader is guarded by `tap is not None`),
and a future editor who broke the invariant would get a loud `NameError`
rather than a silent `None` — but an operator who prefers an unconditional
binding should drop this hunk.

## 3. Checked and NOT dead (explicitly cleared)

- **`_pwcat_r83_ns_load`'s partial-enumeration path** (`:16532`, `:16541`) —
  live: `module_id is None` on a load failure and on a sink/monitor that
  never enumerated (which then name-verifies an unload).
- **`(loads or {})`** at `:16561/16570/16583/16597` — live: 6 `_pwcat_r83_block`
  call sites pass `loads=None` (the tool-absent / sink-not-enumerated blocks).
- **`_pwcat_r83_find`'s `"nodes" not in g` guard** — live: `_pwcat_r83_graph`
  returns `{"error": …}` on timeout/OSError/JSON failure (a real path on a
  busy host).
- **`_pwcat_r83_check_props`'s `want=None` / `absent=()` defaults** — both
  arms live (2 of 14 sites pass only `absent`).
- **`_pwcat_r83_check_rc`'s `cls` / `hit_part`** — all 4 sites pass both;
  retained as the shared assertion signature.
- **`_pwcat_r83_play_leg.extra` / `_pwcat_r83_onset_leg.extra`** — live
  (`:18362` `--rate 48000`; 3 onset call sites pass `-d`/`-l`).
- **`_pwcat_r83_lb_leg`'s `n_value` / `probe_absent` / `probe_default` /
  `node_names` / `wait_mode` / `feed_sink` / `tap_target`** — all supplied by
  at least one call site (S7 counts: 1/1/3/2/4/7/7).
- **`PWCAT_R83_PROP_DROP`'s `object.id`, `object.serial`,
  `window.x11.display`** — subsumed by `PWCAT_R83_PROP_KEEP`'s prefix set
  (redundant set members). Retained as documented drop vocabulary (the r82
  precedent for `window.x11.display`).
- **`_pwcat_r83_check_segv`'s `or leg.get("signal") != "SIGSEGV"`** — a
  two-surface assertion of one fact: `signal` is derived in-fixture as
  `signal.Signals(-rc).name`, so `rc == -11` ⟺ `signal == "SIGSEGV"`.
  Retained: the diagnostic prints both surfaces and the disjunct is
  honest redundancy, not dead flow.
- **Never-fired but real falsification arms** (0 hits in both runs): the
  segv "nodes published" arm (F3 0/0), the onset "unmeasured"/"unlinked"
  arms (F4/F5 0/0), the silent-control and deviating-`c1` arms (F6/F7 0/0),
  the remix `move_skipped` arm (F9 0/0), the resample `deviates` /
  `artifact_or_deviation` arms (F10/F11 0/0), the fail-open `nodes_not_seen`
  arm (F12 0/0), the `unsupported tap_stats` arm (F13 0/0). All are the
  envelope the round deliberately armed; pruning them would delete the
  falsification surface, not dead code. (`m_alone` `unmeasured` **did**
  realize once — F8 run1 = 1 — which is the honest-arm design working.)
- **Error-class tuple** — both r83-local classes realized in both runs
  (`props_syntax_error` 8, `pwcat_props_syntax_error` 5; the `pw_usage`
  class is the documented fallback). Retained (r81-T3 / r82 precedent).
- **Wiring** — `--probe-pwcat-r83` is consumed by all five surfaces (arg
  `:18826`, mutex sum `:18834`, dispatch `:19125`, mode `:19781`, suffix
  `:19801`). The mutex sum has **127 terms, no duplicates, and every term has
  a parser arg**. No dead config key.
- **The r83 block's evidence leaves** — `wait_mode`, `content_witness`,
  `failopen_target_is_default`, `default_sink_now`, `serials`,
  `producer_classes`, `consumer_classes`, `feed_node`, `feed_consumers`,
  `window_amps`, `mono_mix_dev_ratio`, `stereo_pass_dev_ratio`,
  `artifact_outcome`, `out_port_names`, `tap_exit`, `feed_lead_s`,
  `node_waits`/`port_waits`, `control_outcome`, `named_outcomes`, … — the
  family's honest-leaf convention (recorded, not gated). No deletion.

## 4. Below the bar (reported, retained)

- **Seven defaulted-but-never-supplied knobs**: `_pwcat_r83_channel_stats.skip_s`,
  `_pwcat_r83_windows.ws`, `_pwcat_r83_first_nonsilent.thresh`,
  `_pwcat_r83_wait_node.timeout_s`, `_pwcat_r83_lb_leg.feed_at`,
  `_pwcat_r83_play_leg.sample_at`, `_pwcat_r83_rec_leg.timeout_s` (S7). Each
  is a **bound**, and each feeds a *live* expression (`int(rate*ws)`,
  `> thresh`, `< timeout_s`, the events list, the sample loop). Only
  `rec_leg.extra` (T3) was a dead **expression**, which is why T3 is in the
  patch and these are not — the r82 §4 convention.
- **`_pwcat_r83_lb_leg.bound_s`** — the default `PWCAT_R83_LEG_S` is never
  used (all 20 sites pass `bound_s=`), same class as the knobs above.
- **`w0_ctl` (`:18081`)** — a stereo control leg for the widen/method arms
  that **no verdict reads**; and **`warmup` (`:17800`)** — the
  cold-negotiation absorber, deliberately "pinned to nothing" (its own
  comment). Both are *measured rows*, not dead code: deleting them would
  shrink the ledger, not the code. Operator's call; not folded.
- **Duplicated read idioms**: the `ch_amp` closure is defined identically
  twice (`:18147`, `:18372`) and
  `(leg.get("tap_stats") or {}).get("channels") or []` /
  `((leg.get("sample") or {}).get("node") or {}).get("props") or {}` appear
  4× each. Hoisting them into module-level helpers is a *refactor*, not a
  deletion, and would change no behaviour — out of scope for this seat.
- **`PWCAT_R83_ONSET_FEED_GAP_S` / `ONSET_TAP_S` / `LINK_WAIT_S` / `GRP` /
  `MONO_RATIO` / `TRANSPORT_MAX_S` / `D10_DELTA_S` / `D025_DELTA_S`** — every
  module-level constant in the block is loaded (census.txt); none is
  definition-only.

## 5. Limits / residual risk

- **No fresh folded full-family replay.** Per item the proof is static
  reachability `[S]` + receipt census `[R]` + the executed differential `[D]`
  (53 checks) + the patch round-trip `[P]`. A live folded replay is the
  operator's strongest end-to-end confirmation and can be run from
  `folded/` with the same `--probe-pwcat-r83` flag (the folded copy is a
  complete, `py_compile`-clean fixture; its `ROOT` resolves to
  `corpus/live/r83-simplifier/`, so its receipt would land under
  `corpus/live/r83-simplifier/live/runs/<stamp>-pwcat-r83/measurements.json`). It was **not** run here: it
  needs a live PipeWire/WirePlumber host, takes the 128-leg wall time, and
  three sibling seats were probing/committing concurrently during this
  window.
- **T3's receipt delta** (`pr_land.extra_argv` disappears) and **T7's
  conditional binding** are disclosed above; both are verdict-invariant
  today and both hunks are separable.
- The r83 family is live-host data: raw receipts are **not** byte-identical
  across replays (pids, `wall_s`, `link_waited_s`, `at_s`, foreign-node
  enumerations, transport onsets), so "identical replay" is only meaningful
  on the **verdict surface** — which is what the differential compares
  (timing keys excluded) and what `receipt-census.txt` re-verifies for both
  pinned runs. The deleted code produces no verdict-surface leaf in any of
  them.
- **The tree is moving.** A sibling seat has an uncommitted fold of the r82
  simplifier patch in `corpus/fixtures/measure_audio.py`, and HEAD advanced
  three times during this window. The r83 block is byte-identical between the
  working tree and the pin *at report time*, but the operator should apply
  this patch against `a151a226`'s blob (or re-verify the block identity
  first) — `proofs/sha256.txt` records both shas.
- No semantic LSP proof (device unavailable, recorded); the reference proofs
  are AST/`grep` census over the pinned blob plus the executed differential.

## 6. Reproduction

```
cd ~/Projects/shokunin/audio-shokunin
python3 corpus/live/r83-simplifier/proofs/static-proofs.py \
        corpus/live/r83-simplifier/proofs/base-measure_audio.py   # S1-S8, 29 PASS
python3 corpus/live/r83-simplifier/proofs/receipt-census.py        # 20 PASS
python3 corpus/live/r83-simplifier/proofs/census.py \
        corpus/live/r83-simplifier/proofs/base-measure_audio.py
python3 corpus/live/r83-simplifier/proofs/params.py \
        corpus/live/r83-simplifier/proofs/base-measure_audio.py
PYTHONDONTWRITEBYTECODE=1 python3 -B \
        corpus/live/r83-simplifier/proofs/differential.py          # D0-D8, 53 PASS
python3 corpus/live/r83-simplifier/proofs/fold-r83-simplifier.py \
        corpus/live/r83-simplifier/proofs/base-measure_audio.py \
        /tmp/r83-folded-check.py                                   # 13/13 "1 match"
git apply --check corpus/live/r83-simplifier/r83-simplifier.patch  # clean, NOT applied
python3 corpus/live/r83-simplifier/proofs/manifest.py              # 21 files
```

All six scripts exit 0; `patch-check` is a check only — the tracked fixture
is untouched by this seat (the `M` on `corpus/fixtures/measure_audio.py` in
`git status` is the **sibling's** r82 fold, present before this seat started
and confined to lines outside the r83 block).
