# R79 SIMPLIFIER (audio) — YAGNI deletion on the r79 loopback arm

Round 79, repo `~/Projects/shokunin/audio-shokunin` @ HEAD **`a2616f7`**
("r78 LOG: adjudicator ADMIT-corr"). Audited surface: the **dirty tree's**
`corpus/fixtures/measure_audio.py` — the r79 prepend (+2737/−3; fixture
sha256 `4ee754b3fa7dab6c7be7c60930fc8c14854acf7f5439c9b150bb40aba0805095`,
git blob `d6263714…`), the `--probe-capture-r79` family only. Host
`plazir27`: PipeWire 1.6.8, pactl 17.0-98-gb096, Python 3.14.7.

**Seat: SIMPLIFIER.** Deliverables are untracked, under
`corpus/live/r79-simplifier/`: `census.py`/`census.txt`, `apply_fold.py` +
`fold.diff`, `unit_equiv.py` + `unit-equivalence.txt`, `pidpin.py`,
`faultrun.py` + `fault_seq.sh`, `healthy_seq.sh`, `compare.py`,
`diffset.py`, `verdict_check.py`, `host-window.txt`, `receipts/` (10
receipts + 6 comparison transcripts + the negative control), the verified
fold copy `cand/` and the byte-identical control `control/`. **No tracked
file was edited**: the shared tree's fixture is still
`4ee754b3…` and `git status --porcelain` carries exactly the two
modifications the author seat left (`SHONEN.md`,
`corpus/fixtures/measure_audio.py`).

---

## 0. Headline

| # | question asked | answer |
| --- | --- | --- |
| 1 | dead constants? | **1** — `LOOPBACK_R79_TIMEOUT_S` is referenced nowhere (its only occurrence is the definition; the r79 taps reap on `PLAYBACK_R78_TIMEOUT_S`). The other 16 `LOOPBACK_R79_*` constants are live (`census.txt` §1). |
| 2 | dead helpers / dead params? | **0 dead helpers** (37 r79 functions, every one has a live call site) and **0 never-loaded parameters** (`census.txt` §2–3). |
| 3 | dead locals / dead stores? | **8** — `line` (r79 runner), `extra_tw` (playback lattice), `inv` ×2 (matrix + fc entries), `ctx` (fc entry, 7 lines), `want_node` (fc verdict loop), `ltag` (hotplug e1), `nm` (unload loop) — all store-only in the AST census (`census.txt` §4), each cross-checked by text (`grep` finds only the binding). |
| 4 | unreachable/vacuous branches? | **4** — the `tap_t = ns_b if kind != "none" else ns_b` ternary (identical arms); the `and s0 is None` conjunct (s0 is truthy after the entry's own early block, single assignment); `_loopback_r79_check_tap`'s `require` parameter (kw-only, default True, no call site passes it → `if require:` can never be False); the record verdict loop's re-declared 4-tuple table (byte-identical to `RECS`). **One arm is NOT dead** and was kept: `check_side`'s `want is None` fires on the two `autoconnect_off` legs (b10/b11). |
| 5 | duplicated shape inside r79? | **3 single-source folds** — the two inline watch unions in `_loopback_r79_leg` → `_loopback_r79_union`; the 15 named coverage-block sites → `_loopback_r79_block`; the record verdict table → `RECS`. |
| 6 | contradictory comments? | **2 prose sites** state "the reported Latency param is byte-identical on every leg — intent, not a negotiated param" while the same entry's code computes `latency_param_verdict` and its own comment records three distinct values that track the request (the author's repair-table item 7 fixed the code, not the prose). Doc-only, folded (F15). |
| 7 | applied batch | **F1–F16, 24 replacement patterns, +70 / −112 lines (net −42; 12 535 → 12 493)**. No leaf, no gate, no failure text, no class was dropped. |
| 8 | replay-proven? | **yes, five receipts pairs + a unit pass**: fault-injected pairs (monitor **0 diffs at every tier over 721 leaves**; authority **strict 0 over 2 718 leaves**), the adjacent healthy pair **strict 0+0 over 23 055 leaves**, the primary pristine-vs-folded pair **strict 0+0 over 23 057 leaves** (its host-tier deltas are the sibling r78 battery's footprint, named by the receipt itself), a pristine-vs-pristine host baseline, 33/33 unit checks, and a negative control that catches a single verdict flip. |
| 9 | candidates found but **not** applied | §4 R1–R9, each with its reason — two dead stores kept as diagnostics, four duplications that are not byte-preserving, one cross-family extraction that needs its own r78 vfold. |

Axes walked: **A1 weight** (dead constant/store/binding/branch/table),
**A2 falsifiability** (one vacuous guard made unconditional — the r77 S9
fail-closed form; every failure string byte-identical), **A3 receipt
stability** (strict tiers empty on four pairs, `failures` maps identical),
**A4 provenance** (nothing marked historical was touched; the r78 arm is
byte-untouched). The batch improves A1/A2 and leaves A3/A4 untouched.

---

## 1. Method and freeze anchors

**Reference census.** No `lsp` device is available in this seat's
environment, so the seat-card's semantic proof is replaced by the literal
fallback **plus a stronger instrument**: a full-parse Python `ast` pass
(`census.py`) that counts, per r79 function, every `Name` store vs load,
every parameter's body loads, and every constant's file-wide references.
That is a syntax-tree reference analysis, not a text grep; every claim it
makes about a deletion candidate is re-checked with a plain text scan of
the enclosing region (`grep` output quoted in §2). Recorded as required:
**no LSP server answered the file; the census is AST-based, and grep is
used only as a cross-check.**

**Unit equivalence** (`unit_equiv.py` → `unit-equivalence.txt`): control
and candidate modules imported side by side and driven on synthetic
inputs — `check_tap`'s six arms (no tap / empty tap / tap that never ran /
tap bound elsewhere / silent tap with `want_tone=True` / a `mine` window
with `want_tone=False`), the union helper against the control's inline
comprehension on 7 synthetic sample sets, the block helper against the
control's inline statements for all six messages × (with/without loads)
with a recording unload stub, and machine re-checks of every static
premise (dead-local proofs, the `s0` single assignment, the `RECS` table
identity, the ternary's identical arms, the stale-claim removal).
**VERDICT: PASS — 33 checks, 0 failures.**

**Replay.** Two scratch roots, each a tracked-only materialization of the
*current dirty tree* (`control/` = byte-identical copy, sha256 verified
against the shared tree at every step; `cand/` = the same file with
`apply_fold.py` applied). The control side is therefore the dirty tree's
own run in every respect that can reach a receipt — same fixture bytes,
same tools, same host — with only the scratch root path differing, which
the comparator normalizes. Runs are sequential (never concurrent: the r79
entries are host-state witnesses). One instrumentation detail is
mandatory and is part of the method: **`PLAYBACK_R78_TONE_L_HZ =
997.0 + (os.getpid() % 4) * 211.0` makes the tag tone's frequency a
function of the probe process's pid**, and with it every tone-derived leaf
(window `f_l`/`f_r`/`a_l`/`a_r`, `at_l`/`at_r`, the mix bands). `pidpin.py`
forks until a child lands on a requested residue and execs the probe from
that child, so **control and candidate run at the same residue**; without
it, two receipts are incomparable on those leaves by construction
(measured: the author's own run B vs run C differ on 2 790 leaves, most of
them tone-derived).

**Comparator** (`verdict_check.py`, built on `diffset.py`): three tiers.
Normalization is per-run identity only — pid-stamped `r79lb_*`/`r79fc_*`
names (including the `r79lb_fc_<pid>` form), the pw-loopback child pid
inside `node_group`/`node_link_group`, `TemporaryDirectory` paths,
pw-cli/pipewire log timestamps and pointers. **STRICT** = every leaf that
is neither a declared class nor a host-content witness; **HOST** = content
witnesses on the shared host (tap/two-tone magnitudes, live link content,
spawn-time authority snapshots, the named confound); **DECLARED** = daemon
ids, measured clocks, per-run negotiated stream params, the sibling-process
snapshot. STRICT must be empty in both the value-diff tier and the
key-set tier; HOST and DECLARED counts are printed by class so nothing is
hidden. `classes.txt` is the same declaration in the older comparator's
format.

**Host window** (`host-window.txt`): the fleet was live throughout
(verifier `vrun2`/forge runs, the boundary lane's `r79b*` experiments, one
r78 battery). Each run's window and its concurrent siblings are recorded;
the contamination that this caused is named in §3.4, not hidden.

---

## 2. The applied batch (F1–F16)

`fold.diff` is the batch (28 hunks, +70/−112); `apply_fold.py` asserts each
pattern's occurrence count before replacing and is deterministic (re-running
it on a fresh copy reproduces `cand/` byte for byte —
`receipts/apply-fold.log`).

| # | deletion | mechanism | evidence |
| --- | --- | --- | --- |
| F1 | `LOOPBACK_R79_TIMEOUT_S = CONSUMER_R73_TIMEOUT_S` | referenced nowhere; r79 reaps taps on `PLAYBACK_R78_TIMEOUT_S` | `census.txt` §1 (`refs=0`); `grep` finds the definition only |
| F2 | `_loopback_r79_run`'s `cls, line = …` → `cls, _ = …` | the second value is never read (the r79 runner emits `error_class`, not r78's `error` leaf) | `census.txt` §4; grep: the binding is the only occurrence |
| F3 | `_loopback_r79_sinks_unload`'s `for nm, leaf in loads.items()` → `for leaf in loads.values()` | the key is never read | `census.txt` §4 |
| F4 | capture lattice's `tap_t = ns_b if kind != "none" else ns_b` | both arms are the same expression; the call site now names `ns_b` | grep: 1 hit, arms identical |
| F5 | capture lattice's dead `and s0 is None` conjunct | the entry returns when `not s0` a few lines above and `s0` is assigned once | `census.txt` §4; unit check "s0 assigned once" |
| F6 | playback lattice's `extra_tw` binding (3 lines) | 2 stores, 0 loads — the c07 control tap is built from `ctx_l`/`tapc`, not from it | `census.txt` §4; grep: the two stores only |
| F7 | matrix entry's `inv = _capture_inventory()` | 0 loads; the entry carries no `inventory` leaf and the call is a read-only enumeration | `census.txt` §4; `grep inv` in the entry: the binding only |
| F8 | fc entry's `inv = _capture_inventory()` | same | `census.txt` §4 |
| F9 | fc entry's `ctx = {…}` (7 lines) | 0 loads, nested defs included — `confd_leg` builds its own `env`, the cli path uses `tone` directly | `census.txt` §4; grep in the entry: the definition only |
| F10 | fc's `for name, want_node in ((…, True), (…, True))` → `for name in (…)` | the tuple's second element is never read | `census.txt` §4 |
| F11 | hotplug e1's `ltag, out_n = e1["ltag"], f"output.{…}"` → `out_n = …` | `ltag` never read | `census.txt` §4 |
| F12 | record verdict loop's re-declared 4-tuple table (4 lines) → `in RECS:` | the table is byte-identical to `RECS`, defined ~90 lines above in the same function scope | unit check "4 lines, twice"; the AST equality of the two tables |
| F13 | `_loopback_r79_check_tap`'s `require` parameter + `if require:` | kw-only, default True, **no call site passes it** → the false arm cannot run; the empty-tap failure is now unconditional (fail-closed) | grep: `require=` occurs at the definition only; unit: six arms identical |
| F14 | `_loopback_r79_leg`'s two inline watch unions (8 lines) → `_loopback_r79_union` | the helper is the same comprehension (`sorted({…} or [])`); the dict's key order is unchanged | unit: identical on 7 synthetic sample sets |
| F15 | the two stale "Latency param is byte-identical" prose sites (family header + entry docstring) | contradicted by the entry's own comment and by `latency_param_verdict` (`latency_param_tracks_request`); the new text states the measured law (r78 one value, r79 run 2 three values) and that the **prop** is the hard pin | doc-only; unit check that the stale strings are gone and the verdict machinery is present |
| F16 | the 15 named coverage-block sites → `_loopback_r79_block(entry, failures, msg, loads=None)` | the same 5–6 statement block (`blocked` / `coverage_blocked` / unload / `failures` / `return entry`) with six distinct messages and the unload only where a load happened | unit: entry, failures and unload calls identical for all six messages × (with/without loads); the fault pairs in §3 fire all 15 sites |

Net: **+70 / −112 lines** (24 replacements; 12 535 → 12 493). Nothing was
renamed, no message was edited, no leaf was moved.

---

## 3. Replay proof

All receipts live in `corpus/live/r79-simplifier/{control,cand}/corpus/live/runs/`
(sha256 table in `receipts/receipt-shas.txt`); every comparison transcript
is in `receipts/compare/`.

### 3.1 The fault pairs — the blocked paths, byte-level

The 15 folded block sites and F13's empty-tap arm cannot fire on a healthy
host, so they are proven with injected faults (`faultrun.py`):

* **monitor fault** (the null-sink monitor gate reports "not ready", so
  every entry blocks *after* a real module load → the helper's unload path
  runs for real):
  `leaves A=721 B=721 value-diffs=0 key-only 0` — **VERDICT: PASS
  (strict=0 host=0 declared=0)**. The two raw JSON files differ **only** in
  the pid-stamped sink names and `own_pid` (the normalizer's domain); the
  eight `blocked` messages, their `coverage_blocked` rows and the
  `sink_loads` leaves are identical.
* **authority fault** (no default sink/source readable; the shipped
  filter-chain.conf reported absent): all 6 authority blocks + the fc
  base-missing block fire, and the matrix entry runs its full 4-leg
  battery with real sinks: `leaves A=2718 B=2718 value-diffs=25` →
  **VERDICT: PASS (strict=0+0 host=10 declared=15)**; the 10 host diffs are
  tap magnitudes (content) and the 15 declared are module ids/wait clocks.

Together the two faults exercise **all 15 block sites** (monitor ×8,
authority ×6, fc base ×1).

### 3.2 The adjacent healthy pair — the cleanest full-probe receipt

Control **C2** (`20261015T082232715628Z`, 08:17:05→08:22:32Z) and folded
**D2** (`20261015T082857514558Z`, 08:23:57→08:28:57Z), back-to-back in the
same fleet window (verifier forge run + boundary lane):

```
leaves compared         : 23055 (A=23039 B=23055)
value diffs             : 289
  STRICT                : 0
  HOST                  : 2  (tap windows of one record leg)
  DECLARED              : 287 (ids/clocks/negotiated params)
key-set diffs           : 16
  STRICT                : 0
  HOST                  : 2  (pw-cli transcript tail: one extra `pipewire-0>>` line)
  DECLARED              : 14 (the a6 node's second `latency_param` block)
VERDICT: PASS (strict=0+0)
```

Both sides carry `failures: {}` for all eight r79 entries and all 17
artifact measurements, and every verdict leaf — unions, expected sets,
`carries_tone`/`mine_windows`/`mine_spans`, exit codes, classes, `blocked`
rows, loader verdicts — is equal.

### 3.3 The primary pair — pristine control vs folded candidate

Control **C1** (`20261015T081137379814Z`, 08:06:09→08:11:37Z) vs folded
**D1** (`20261015T081705030963Z`, 08:11:37→08:17:05Z):

```
leaves compared         : 23057 (A=23053 B=23057)
value diffs             : 638
  STRICT                : 0
  HOST                  : 376
  DECLARED              : 262
key-set diffs           : 4 (all in loopback_shape/legs/a6_playback_default)
VERDICT: PASS (strict=0+0)
```

`failures` maps are `{}` on both sides, for every entry and every artifact
measurement.

### 3.4 The one contamination, and why it is not the fold

D1's window overlaps the **sibling r78 battery** (pid 190539, live
08:10:55→08:14:21Z, receipt
`corpus/live/runs/20261015T081421351571Z-capture-r78/measurements.json`).
That run's default-sink fallback legs play the *r78* tag tone into the
shared SPDIF sink, and its `default` leg also links its own probe sink onto
the same stream. The receipts say so themselves:

* D1's a6 leg carries
  `confound = "foreign node(s) ['r78_def_sink_190539'] ALSO consumers …"`
  and the four key-set diffs are exactly `consumers_union[1]`,
  `output_consumers_union[1]`, `tap.bound_producers[1]` and that confound;
* the a6/c04/c05 taps record `f_l/f_r = 1630/2130 Hz` and peaks
  8189/7725. `190539 % 4 = 3` ⇒ the r78 tone is `997 + 3·211 = 1630 Hz`
  (+503 = 2133 Hz), i.e. the observed frequency to the FFT bin;
* the peaks sit **below** the arm's own `8192·1.05 = 8602` ceiling, so the
  `foreign_tone_witness` class did not fire and `mine_windows` stayed 0 —
  the verdict is untouched on both sides.

So D1's HOST tier (376) is the sibling battery's footprint plus ordinary
content noise; the baseline C1-vs-C2 (same fixture) has the same *kinds*
of diffs (host=3, declared=280+14) with no sibling battery overlapping.

### 3.5 The comparator is not vacuous

`receipts/compare/negative-control.txt`: flipping **one** verdict leaf in
the folded receipt (`a1_shape.carries_tone` True→False, with
`tap.mine_windows` 40→0) yields `strict=2, host=0, declared=0` over the
same 23 055 leaves. Deleting a leg's `tap` subtree (402 keys) is likewise
caught (strict=2 + 67 key-set).

---

## 4. Candidates found and **deliberately not applied**

| # | candidate | weight | why not |
| --- | --- | --- | --- |
| R1 | `_loopback_r79_metadata_default`'s `raw`/`exit` keys | 2 keys | only `.get("name")` is read by the r79 oracle, but the helper's docstring declares the verbatim-raw contract with the r78 reader; it is the reader's provenance capability, not a vestige |
| R2 | `_loopback_r79_pactl_defaults`'s `out["error"]` | 1 line | a genuine dead store (the dict is local, nobody reads `error`) — kept as the only pactl-failure diagnostic; deleting it trades one line for A2 (diagnosability) |
| R3 | the re-oracle triple repeated in capture/playback/pwcat | ~3 lines net | the shape entry's two re-oracles are deliberately *partial* (one field each); a helper would have to set both fields there and could move `default_*_at_leg` leaves if the authority flaps. Not dead weight — skipped |
| R4 | the fc `confd_leg` feed/pin/tap block vs the f7 cli block (~15 lines twice) | 15 lines | **not byte-preserving**: the f7 leg's receipt has `two_tone` but no `tap`/`chain_input_ports`-shaped leaf set; unifying adds leaves |
| R5 | cross-family: r78's `_playback_r78_run` sample block and r79's `_loopback_r79_watch_sample` share a **byte-identical 7-line tap-witness block** | 7 lines | extracting a shared helper edits the frozen r78 arm and needs its own r78 vfold (13 k leaves); flagged for a round allowed to touch r78, not for this one |
| R6 | `_playback_r78_node_state(tag)` vs `_loopback_r79_nodes(names)` | — | same reader shape, different leaf contract (r79 adds 12 keys) → not byte-preserving |
| R7 | `_loopback_r79_check_side`'s `want is None` arm | — | **LIVE**: the `autoconnect_off` legs (b10/b11) expect zero producers. Explicitly not a candidate |
| R8 | `_loopback_r79_check_tap`'s `if not tap:` arm | 4 lines | defensive fail-closed guard; every current call site passes `tap_target`, but the guard is the contract for a tap-less leg — kept |
| R9 | `_loopback_r79_run`'s feed/`loaded` scaffolding, `_loopback_r79_two_tone`'s DTFT | — | live on every entry; the DTFT is *not* a duplicate of `_playback_r78_domfreq` (exact-frequency evaluation vs dominant-bin FFT — the docstring says why) |

---

## 5. Findings for the round ledger

1. **The stale prose was real** (folded F15). The author's repair table
   item 7 changed the code to a named verdict but left two prose sites
   asserting the opposite ("byte-identical on every leg — intent, not a
   negotiated param"), including the family header every reader sees first.
2. **The tag tone frequency is pid-derived.** Any future control/candidate
   receipt pair on r78/r79 must pin the pid residue (or normalize the
   tone-derived leaves) — otherwise ~2 800 leaves differ between two runs
   of *the same* fixture (measured on the author's run B vs run C).
3. **The shared-default-sink fallback legs (a6, c04, c05, c10, b09, d2d)
   are the fleet's contention surface**, and the arm names the contention
   correctly (foreign consumer + foreign-tone class with a ceiling). The
   one battery that overlapped a proof run is fully identified by its own
   receipt (`own_pid 190539`, `r78_def_sink_190539`).
4. **The pw-cli transcript tail is read-chunk-dependent**: the number of
   `reply[n]` lines varies run to run (2 key-set diffs in the adjacent
   pair). Nothing gates on the tail; the common prefix is strict.
5. **The a6 node's `latency_param` array length varies** (1 vs 2 blocks
   across runs) — the pwcat entry's within-run `latency_param_verdict`
   already treats the param as data, so this is consistent.
6. **`mix_half_gain_ratio` measured 0.500 in one run and 0.527 in
   another** (matrix mix legs) — content noise inside the gated
   0.35–0.65 band; the band is the contract, the ratio is data.
7. The batch touches **no gate, no leaf, no failure string, no class, and
   no r76/r77/r78 code**; the three `main()` wiring lines the author wrote
   are untouched.

---

## 6. Tradeoff, and the stop

The batch removes dead weight only: one dead constant, eight dead
stores/bindings, four vacuous branches, three duplicated shapes, two stale
prose claims. It gives up nothing observable — the strongest available
receipts say so (fault pairs at 0/0/0 and 0/0 over 2 718 leaves; the
adjacent full-probe pair at strict 0+0 over 23 055 leaves; the primary
pair at strict 0+0 over 23 057 leaves, its host deltas traced to a named
sibling battery). The seat stops here: the next deletions on the shelf
(R1/R2 diagnostics, R4/R6 leaf moves, R5 the frozen r78 arm) each harm an
axis — provenance, receipt stability, or the r78 contract — rather than
removing weight.
