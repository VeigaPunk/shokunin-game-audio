# R77 SIMPLIFIER (audio) — YAGNI audit of `65790f1`

Round 77. Repo `~/Projects/shokunin/audio-shokunin` @ HEAD
**`65790f1`** ("r77 work: capture-source lattice + fallback law + reader
matrix"). Audited surface: `corpus/fixtures/measure_audio.py` (blob
`6299b33…`, the +1552/−2 of that commit) — the `--probe-capture-r77` family
only.

**Seat: SIMPLIFIER.** One new report (this file) and one evidence directory
(`corpus/live/r77-simpl/`, untracked). **No tracked file was edited**: the
shared tree's fixture is byte-identical to `65790f1`
(`git hash-object corpus/fixtures/measure_audio.py` = `6299b335ad925eea0b1da
6c4900bd4abc466fa76` = `HEAD:corpus/fixtures/measure_audio.py`; `git status
--short corpus/fixtures/` empty). All candidate edits live in a scratch copy
(`/tmp/r77-simpl-cand`, materialized from the r77-baseline seat's
`measure-env-post`, whose fixture blob is also `6299b33…`, so no canonical
write is possible from it).

---

## 0. Headline

| # | question asked | answer |
| --- | --- | --- |
| 1 | duplicated probe-leg scaffolding? | **yes, 3 irreducible-looking copies of one reap adapter → single-sourced** (§3 S4); the five *leaf builders* and the r77/r76 *file-leg pair* look like duplicates and are **not** — rejected with mechanism (§4 R1, R2) |
| 2 | dead constants (33 new)? | **33/33 read, 34/34 helpers read, 0 dead top-level symbols** (`dead-symbol-check.txt`). The dead weight is *inside* the symbols: 2 dead parameters, 2 dead branches/guards, 2 dead internal leaves |
| 3 | redundant checks inside entries? | 1 unreachable guard (§3 S5); 1 **vacuous** check that could never fire because of a stale name + wrong enumeration (§3 S6, §6 F1); 1 silently-skipping guard (§3 S9) |
| 4 | over-broad pinned values? | 3 duplicate numeric authorities (96000 / 0x80000000-div-4 / 19244 / 48000) derived instead (§3 S8); 1 leaf that reports `False` for *unknown* (§3 S10); the `sink_gone` leaf was not evidence at all (§6 F1); 2 pins whose honest form is a **declared** host fact, not a measured leaf (§4 R7, R8); 1 absolute host-load floor whose law is relational (§4 R9) |
| 5 | applied batch | **26 replacements, +56 / −58 lines**, receipt-neutral by construction, replay-proven: the pair (pristine vs batch, back-to-back in one quiet window) gives **A = 0 / B = 0 / C = 0, `failures: {}` on both sides**, and the batch receipt is likewise identical to each of the round's three canonical clean receipts (§5) |
| 6 | round-ledger findings | §6: the `sink_gone` vacuity, the falsified `±1 frame` drift declaration, the loss leg's missing silence guard (F4), the bound-kill finalize asymmetry |

Axes walked: **A1 weight** (paths/authorities), **A2 falsifiability** (reachable
failure clauses), **A3 receipt stability** (byte-identical modulo declared
drift), **A4 pre-r77 isolation**. The batch improves A1 and A2 and leaves A3/A4
untouched — the only Pareto-admissible shape available to this seat.

---

## 1. Method and freeze anchors

**Static pass.** AST census of every new top-level symbol with line-level read
sites (`dead-symbol-check.txt`); literal-authority census over the r77 block
(each repeated magic number with every occurrence); call-site census for every
parameter I propose to delete.

**Static dead-parameter pass.** `dead-params.txt` lists every r77 parameter
with its in-body use count. Both parameters the batch deletes are *masked by
their own dead branch*: `_capture_r77_file_leg(exact_bytes)` shows `uses=1`
(the unreachable disjunct) and `_capture_r77_lattice_cell(sink)` shows `uses=1`
(the `pass` statement). An unused-name linter cannot see them; a reachability
read can. Only one `pass` in the r77 block is dead (the `elif sink:`); the
other four are `except …: pass` fallbacks on real failure paths and are kept.

**Replay pass.** Two scratch envs, each a copy of
`corpus/live/r77-baseline/measure-env-post` (the baseline seat's 663-file
tracked-only materialization at this commit):
`/tmp/r77-simpl-control` (pristine) and `/tmp/r77-simpl-cand` (batch applied by
`apply_simplifications.py`, which asserts every pattern's occurrence count).
Both were driven by `pair_replay.py`, which gates on a **quiet host** (no
`measure_audio.py`/`pw-record`/`arecord`/`parecord`/`ffmpeg`/`sox` process for
20 consecutive seconds) because the lattice and target-loss cells are topology
witnesses: a concurrent seat's capture merges into the same `pw-link -l` port
names and would void the receipt (the author's §7.4 confound, reproduced live
in this wave: the concurrent seat's own run at 20:13:36Z carried exactly those
three failures).

**Comparator** (`compare_r77.py`), three levels:

* **A STRICT** — every leaf outside the declared host-drift *classes* must be
  equal.
* **B CONTRACT** — the pinned verdict classes must be equal (failures maps,
  error classes, finalize classes, reader verdicts, consumed nodes, tone
  booleans, split sizes, format `fmt` leaves, `eintr_cells`/`alsa_busy_cells`,
  sha256 of the bounded legs).
* **C SELF** — the receipt's own derived relations must hold in *both* receipts
  (`bytes == data_actual + 44`; `honest_frames == data_actual // frame_bytes`;
  each reader verdict recomputed from `(value, honest, declared)`; the lattice
  fallback law per cell; `rot-01.wav == total_limit`).

**Calibration.** On the author's three canonical clean receipts
(`…200120162289Z`, `…200431704613Z`, `…200645323501Z`) the comparator must
report A = 0 / B = 0 / C = 0 — it does, for all three self-pairs **and** all
three cross-pairs. A comparator that cannot pass the round's own reference
receipts proves nothing; this one does.

The drift classes are the author's §8 items, taken **as classes** (the
parenthetical envelope is falsified — §6 F2): D1 sever-wall-clock magnitudes,
D2 wall times and rate-window buckets, D3 host state (module-id counter,
contention counts, node-inventory cardinality, raw content peaks).

---

## 2. What "weight" means here

`65790f1` is a *measurement* commit: every leaf it adds is either a pinned
verdict or a witness, and deleting witnesses is not simplification — it is
falsifiability loss. So the audit targets only:

1. **unreachable adapters** — a parameter/branch/guard that no call site and no
   host state can reach;
2. **duplicate authorities** — two spellings of one number, two accumulators
   for one set, two computations of one device list, three copies of one
   escalation policy;
3. **stale names / wrong enumerations** — a helper whose name and body disagree
   with its only caller's test, making the test vacuous;
4. **pins that lie** — a leaf that reports a verdict for a state it never
   observed.

Nothing in §3 removes a witness, a pinned class, or a failure clause's
condition; two of the moves *arm* clauses that were previously unreachable.

---

## 3. APPLIED — the deletion batch (26 replacements, +56 / −58 lines)

Patch: `corpus/live/r77-simpl/apply_simplifications.py`; unified diff kept at
`/tmp/r77-simpl-cand/corpus/fixtures/measure_audio.py.diff`. Every item is
receipt-neutral: the receipts' leaf sets, key names and values are unchanged
(§5 proves it on a live replay, not by argument).

| id | removed | why it was dead / duplicated | A2 falsifiability |
| --- | --- | --- | --- |
| **S1** | `_capture_r77_file_leg`'s `exact_bytes=False` parameter and the `or insp["bytes"] == 0` disjunct it guarded | both call sites (`:5621`, `:5630`) pass `True`; with the parameter gone the condition reduces to `insp.get("bytes") is not None` — the *same* branch for every existing call | unchanged (the disjunct was unreachable) |
| **S2** | `_capture_r77_lattice_cell`'s `sink` parameter and `elif sink: pass` | the `elif` body is `pass`; `sink` had no other read (grep: 3 sites = param, the no-op branch, the one call arg) | unchanged |
| **S3** | the parallel `names` accumulator in `_capture_r77_link_producers` | `producers` and `per_port` were two accumulators for one table; `producers` is now derived from `per_port`, so the two views cannot disagree | unchanged (identical set) |
| **S4** | three inline `wait(timeout) → killpg(SIGKILL) → wait()` copies (lattice cell `:4648`, loss run `:5077`, sever cell `:4532`) | one escalation policy written three times; now `_capture_r77_reap(proc[, timeout])` | unchanged |
| **S5** | `capture_target_loss_r77_entry`'s `if not bounded: … return` guard | `bounded` is assigned unconditionally inside the `try` whose only companion is a `finally` — the guard is unreachable; `bounded` is now read directly | unchanged |
| **S6** | `_capture_r77_sink_names`' **wrong enumeration** (`pactl list sources short` for a *sink* test) | the caller tests `CAPTURE_R77_NULL_SINK not in …`; a `module-null-sink` creates the sink `X` and the **source** `X.monitor`, so the bare sink name can never appear in a source list ⇒ `sink_gone` was always `True` and its failure clause was unreachable (§6 F1) | **armed** (the clause can now fire) |
| **S7** | `_capture_r77_node_props`' `out["count"]` (never read) and `_capture_r77_run`'s `link_baseline` return field (never read by any of the 4 callers) | dead internal leaves; the `stderr` field is *retained* — it drains a bounded pipe and an undrained child can block before it exits | unchanged |
| **S8** | four duplicate numeric authorities: `LOSS_BYTES = 44 + 96000*4`, `SPLIT_{UNDER,OVER}_FRAMES = 536870912 ∓ 240000`, the `19244` baseline literal, the `3 * 48000` table, the `or 48000` rate fallback | the same bound was spelled as a literal in one place and as a constant in another *inside one file*: `12 * CAPTURE_R77_FRAMES_PER_SECOND` (`:5216`) vs `12 * 48000` (`:5373`) — a second convention by construction; now one `SPLIT_LIMIT_FRAMES`, one `SPLIT_MARGIN_FRAMES`, derivations everywhere | unchanged (identical values) |
| **S9** | the `and` guard in the split-undershoot rotation check (`if under.get("siblings") and …`) | an empty sibling map silently skipped the check; now `if list(under.get("siblings") or {}) != ["rot.wav"]` | **strengthened** (the skip is gone) |
| **S10** | `_capture_r77_loss_leaf`'s `data_actual_zero: insp.get("data_actual") == 0` | for a file with no data chunk this returned `False` — i.e. "payload is non-zero" for a state never observed; now `None` (unknown) | **strengthened** (a lying leaf becomes a three-valued honest one) |
| **S11** | the second `plug = "plughw:" + …` computation and the second `(hw0, plug, "sysdefault")` tuple in `capture_arecord_sever_r77_entry` | the sweep and the coverage check named the device axis twice; an edit to one would leave the other checking a different device set. Now one `devices` tuple feeds both | unchanged (same order/values) |

**Weight accounting, honestly.** +56 / −58 lines: the batch is net **−2**
lines, i.e. line-neutral. The deletions (−58) are mostly *control-flow* weight;
the additions (+56) are one shared adapter, four derivations, one three-valued
leaf and a few docstring lines that record *why* a parameter or enumeration was
wrong. The weight that actually falls is the decision surface: 4
dead/unreachable paths, 1 vacuous clause, 6 duplicate spellings of 5 pinned
numbers, 3 copies of 1 policy, 2 duplicated device computations.

---

## 4. Candidates examined and REJECTED (with the mechanism)

These are the "obvious" simplifications a grep would suggest. Each fails for a
reason that is *in the instrument*, so recording them is cheaper than
re-litigating them next round.

* **R1 — the five leaf builders** (`_capture_r77_file_leg` `fin`,
  `_capture_r77_sever_cell` `fin`, `_capture_r77_lattice_cell` `fin`,
  `_capture_r77_loss_leaf`, `_capture_r77_split_leg.siblings`). They look like
  one authority written five times. They are five **declared key sets** that
  differ on purpose (sever cells carry `data_64k_aligned`/`file_zero_bytes`;
  file legs carry `wall_lt_0.5s`; the loss leaf carries `sha256_16`/
  `unloaded`/`all_zero_payload`). A parameterized builder would relocate the
  differences into a key-list argument — same decisions, one more indirection,
  no weight removed (~52 lines → ~50). Rejected.
* **R2 — `_capture_r77_file_leg` as a wrapper over the r76 `_capture_file_leg`.**
  Impossible without changing behaviour: the r76 leg classifies with the r76
  `_CAPTURE_ERR_CLASSES`, and the r77 format axis *needs* `usage_refusal` from
  the r77 tuple; the leg therefore has to classify itself. Making the class
  tuple a parameter of the r76 helper would touch pre-r77 code (A4), so it is a
  next-round candidate with an r76-regression proof, not this one.
* **R3 — the four `error_class == "alsa_busy"` carve-outs.** Already one
  convention (same literal, four checks); a predicate helper adds a symbol and
  removes no decision. Rejected.
* **R4 — the five "leg absent — the … is the coverage contract" clauses.**
  Three different wordings for one contract. Unifying them rewrites *failure
  prose* only (the receipt is empty in a passing run) and costs a branch to
  preserve two plain-wording sites. Prose, not weight. Rejected.
* **R5 — the `12` in `-d 12`** (10 occurrences: argv literals, comments, a
  failure message, and two arithmetic authorities — one of which S8 already
  unified). A named bound constant would edit 8 argv sites to remove a literal
  that the receipt *pins as a leg parameter*; the honest form is the S8
  derivation, already applied. Rejected beyond S8.
* **R6 — naming `44` (`CAPTURE_R77_WAV_HEADER_BYTES`).** Pre-r77 code spells
  the same header size as a literal in several places; an r77-local name would
  add a *third* convention (r76 literals, r77 name, shared law). Rejected.
* **R7 — `unit_calibration.expected_frames: 96000` is recorded but never
  asserted.** The calibration is the *premise* of the `declared_echo` class
  (soxi's `-s` is frames, not interleaved samples). If a future host's soxi
  answered in samples, the matrix would still pass and the class would silently
  change meaning. Arming it (`all five readers must equal expected_frames`)
  **adds** a clause — that is a falsifiability move with a weight cost, so it
  belongs to the round's falsifiability arm, not to this seat. Reported, not
  applied.
* **R8 — `"default_source_is_silent_on_this_host": True`** (`:4762`) is a
  hardcoded `True` inside a receipt that otherwise pins only measured leaves.
  It is *declared*, not measured, and the author's report leans on it (byte
  identity between two source captures is not evidence *because* the default
  source is silent). Dropping it orphans that reasoning; measuring it needs a
  new leg (weight). Reported as a **declared-not-measured** leaf for the
  ledger's own vocabulary — not deleted.
* **R9 — `if after < 95`** (post-loss delivery floor, `:4998`) pins an absolute
  host-load-dependent rate where the law is relational ("delivery does not
  collapse after the target dies"). The honest weaker form is relational
  (`after ≥ before − 5`, from the same run's pre-loss segment), but it is
  *weaker* in the starved-host corner (before = 50, after = 50 would pass).
  Keep the absolute floor, or add the relational clause — either way it is not
  a deletion, and the choice trades one falsifiability corner for another.
  Reported with the tradeoff; **not** applied.
* **R10 — the write-only receipt leaves** (`topology_witness`,
  `link_after_exit`, `foreign_links_ignored`, `sha_match_dead_sink`,
  `before_loss_pct`, `default_sink_is_stable`, `eintr_cells`,
  `alsa_busy_cells`, `requested_path`, `peak_dir_bytes`,
  `frames_worth_of_data`, `wall_lt_0.5s`, `reader_honesty`, `contention`, the
  per-cell `content` block). They are *witnesses*: several are exactly the
  evidence for the round's headline classes (the ghost link, the confound
  cancelling, the re-link). Retained wholesale. The single exception that is
  genuinely dead — `declared_bound_frames` written on the **unbounded** kill
  cell (`:5218`) and read only for the bounded one (`:5253`) — is left in place
  because removing a receipt key is a *declared diff* against the round's
  reference receipts, not a receipt-neutral simplification (§7 stop condition).

---

## 5. Replay proof

**Host-free unit equivalence first** (`unit_equivalence.py`,
`unit-equivalence.txt`): both fixture copies are imported under distinct module
names and the changed helpers are driven on synthetic inputs, so every §3 claim
that does not need a live audio graph is proven directly rather than argued:

* `_capture_r77_link_producers` on four synthetic `pw-link -l` tables (empty,
  one-sided, both-channels + a one-sided ghost, foreign node) — identical
  `producers` / `per_port` / `nodes` / `ambiguous` (the ghost case reproduces
  `ambiguous=True` and the two-node consumed set in both);
* `_capture_r77_link_delta` on synthetic per-port maps, the whole
  `_capture_r77_frame_class` verdict matrix (8 cases), `_capture_r77_readers`
  with and without an `fmt.rate` leaf (S8e), `_capture_r77_rate_buckets`,
  `_capture_r77_reader_honesty` — identical;
* `_capture_r77_reap` against a real child that exits at once and one that
  ignores `SIGTERM`: identical wall classes (0.0 s / 1.0 s timeout → killpg);
* `_capture_r77_loss_leaf` — **the one deliberate difference**: for a file with
  no data chunk the pristine leaf says `data_actual_zero=False`, the batch says
  `None`; the harness asserts that `data_actual_zero` is the *only* differing
  key, and that on a real wav (the state the round measures) the two leaves are
  equal.

**Design.** Control and candidate run back-to-back inside the same quiet
window (same host state), so the comparison is a *pair* comparison, not a
comparison against a receipt from another hour. `--probe-capture-r77` is the
whole family — all six entries plus the 17 ordinary measurement rows.

**Result — the pair (attempt 2, 17:30:33 → 17:35:21 local; both receipts
`failures: {}`, both with `contention.host_is_quiet: true`, `pw_record: 0`,
`fixture_runs: 0`, and all three loss sha256 = `e3a90286b3b54201`, the author's
own value):**

```
leaves compared          : 2708
A strict diffs           : 0
B contract-leaf diffs    : 0
  (declared drift diffs  : 178)
C self-consistency viols : 0
control   failures       : {}
candidate failures       : {}
VERDICT: PASS
```

**Result — candidate vs the round's three canonical clean receipts** (a
cross-window check, because the comparator was calibrated on them):

| reference | A | B | C | candidate failures |
| --- | --- | --- | --- | --- |
| `…200120162289Z` | **0** | 0 | 0 | `{}` |
| `…200431704613Z` | **0** | 0 | 0 | `{}` |
| `…200645323501Z` | **0** | 0 | 0 | `{}` |

So the batch's receipt is identical, leaf for leaf outside the declared drift
classes, to (a) the pristine implementation measured back-to-back in the same
quiet window and (b) the round's own reference receipts — with `failures: {}`
in all four comparisons. Every pinned class named in §7 is in that identity:
it is not a spot check.

**Negative control (the comparator is not a rubber stamp).** Attempt 1 of the
pair ran while a foreign client was feeding the default sink; the *pristine*
control then failed the loss leg (`sha_match_control: false`, failure text
present) and differed from both the candidate and the canonical receipts in
exactly **10 leaves — all of them the loss entry's content leaves**
(`sha256_16`, `all_zero_payload`, `sha_match_*`, the failure string, the
wall-clock file's `bytes`/`sha`), with C = 0 throughout
(`attempt1/`, `replay-proof.txt`). The same comparator that reports A = 0 on
the clean pair reports A = 10 on the contaminated one, and names the mechanism
(§6 F4). Attempt 1 is retained as the sensitivity evidence.

---

## 6. Findings for the round ledger (not simplifier moves)

### F1 — the `sink_gone` check could not fire (stale name + wrong enumeration)

`capture_target_loss_r77_entry` computes
`entry["sink_gone"] = CAPTURE_R77_NULL_SINK not in _capture_r77_sink_names()`
and fails the leg if the probe-owned null sink survived the unload ("the leg
measured nothing"). `_capture_r77_sink_names()` ran
`pactl list sources short` — a **source** list. A `module-null-sink` creates
the sink `X` and the monitor source `X.monitor`, so the bare name `X` is never
in a source list:

```
sinks   : ['alsa_output.pci-0000_01_00.1.hdmi-stereo',
           'alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink', …]
sources : ['alsa_output.pci-0000_01_00.1.hdmi-stereo.monitor',
           'alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink.monitor', …]
  'alsa_output.usb-…SPDIF__sink' in sources -> False
      (monitor present as '…SPDIF__sink.monitor': True)          # ×4/4
```

The membership test is therefore `True` for every sink name, on every host, at
every moment: `sink_gone` was a constant, and the failure clause behind it was
unreachable — while the receipt presented it as a measured verdict. **S6** arms
it by enumerating sinks (receipt-neutral in a passing run: the module really is
unloaded by then, and the check is evaluated ~3 s later, after the wall-clock
leg). Evidence: `sink-gone-vacuity.txt`.

### F2 — the declared drift envelope is falsified by the receipts it describes

The author's §8 declares the sever-wall-clock leaves as "±1 frame". Across the
three canonical clean receipts the *same* leaves differ by up to **8192
frames** (170 ms) — `kill_sysdefault_w2_5.file.data_actual` = 475136 / 466944 /
475136; 301 sever leaves differ at all; the median is single digits. The
*class* declaration is right; the numeric envelope is three orders of magnitude
too tight. My comparator therefore excludes the class, not a tolerance band
(`drift-envelope.txt`). Any seat that wants to claim "±1 frame" must instead
claim "wall-clock-severed magnitudes are host-drift leaves", which is what the
class already says.

### F3 — bound-kill finalize asymmetry (observation, not a defect claim)

In `capture_arecord_sever_r77_entry` the five bound-kill legs
(`bound_{d3,d5,d12}_kill_early`, `bound_d12_kill_late`, `bound_s300k_kill`) are
asserted for their **declaration** (`data_declared // 4 == want`) but not for
their **finalize class**; the finalize law for the same shapes is asserted in
the sibling readers entry (`arecord_bounded_kill`, `arecord_unbounded_kill`).
The leaf is recorded in both, so this is a coverage asymmetry between two
entries, not a missing witness. No action taken (out of this seat's scope).

### F4 — the loss leg's byte-identity law has no silence guard (and reports a false failure)

`capture_target_loss_r77_entry` fails the leg when the post-loss artifact is not
byte-identical to the fallback node's own same-bound control. That identity
holds only while the fallback node is carrying **silence**: the two captures
are compared byte-for-byte, so any third party playing into the default sink
between the two legs changes the payload. The entry's `contended` flag does
*not* cover this — it is derived from `ambiguous` (link-table) samples only.

Observed live in this wave (my control run, `…202759903773Z`, a run whose
`contention` block honestly says `host_is_quiet: False`, `fixture_runs: 1`):

```
baseline        sha e3a90286b3b54201  all_zero_payload True    # = the author's value
fallback_control sha b1c1e2be76b291bc  all_zero_payload False
after_loss      sha 413b4778e1ac77d8  all_zero_payload False
nodes_before ['r77_loss_sink'] -> nodes_after ['…SPDIF__sink']   contended False
failures: ["target loss: the post-loss artifact is NOT byte-identical to the
            FALLBACK node's own same-bound control — the re-link is not total"]
```

The topology law held (the re-link happened, `nodes_after` is the fallback
node) and the *content* law held in the author's three quiet runs; here a
foreign client fed the fallback node, so the entry reports "the re-link is not
total" — a **false failure** for a contention condition it never names. The
lattice entry already solves the same class of problem (differencing + a named
`confound`); the loss entry's sha comparison has no equivalent guard. Not a
simplifier move (arming it *adds* a clause) — but it is why a candidate batch
needs a quiet window, and it is why this seat's *first* pair attempt had to be
discarded as a reference (the second, quiet one is the proof in §5).

---

## 7. Preserved contract, tradeoffs, stop condition

**Preserved (A3/A4, no axis regressed):**

* `failures: {}` for all six capture entries in the candidate run, and the
  complete contract class set (B = 0) equal to the control;
* every pinned class the round rests on: the 11 lattice cells (consumed node,
  tone, bytes, class, `target_object_is_request`), the three loss sha256s and
  the `nodes_before → nodes_after` re-link, every reader verdict and the
  honesty tally, every bound declaration, the device-axis finalize classes,
  `eintr_cells`/`alsa_busy_cells`, the exact split sizes (2147483692 / 960044)
  and all 16 format `fmt` leaves;
* **no pre-r77 code path touched**: the diff is confined to the r77 block
  (`CAPTURE_R77_*`, `_capture_r77_*`, the six `*_r77_entry` functions);
  `_capture_run`, `_capture_wav_inspect`, `_capture_inventory`,
  `_capture_leg_targets`, `_capture_file_leg`, `_capture_sever_cell`,
  `_CAPTURE_ERR_CLASSES` and every prior flag's dispatch are untouched — the
  candidate still *calls* them, exactly as the author did. Proven by region
  isolation (`region-isolation.txt`): the pre-r77 region (lines 1–4199) is
  **byte-identical** (sha `a12292df257549fb`) and the post-r77 region
  (`main()` + the whole CLI dispatch, 954 lines) is **byte-identical** (sha
  `986691e67aa7b572`); 21 of the 68 r77 symbols changed, 50 are untouched, and
  the r77 block itself shrank 1474 → 1472 lines.

**Tradeoffs.**

* The batch is line-neutral (+56/−58, net −2): the gain is in authorities and
  reachability, not bytes. A reviewer who measures simplification in lines
  should score this batch as a wash and read §3 as the real output.
* S6 changes a leaf's *derivation* (source list → sink list) while keeping its
  value; the risk is PipeWire's async module removal. Measured here: the check
  is evaluated after the bounded unload **and** after the 3 s wall-clock leg,
  and the candidate run's `sink_gone` is still `true` — but a host that removed
  modules lazily would see a new (correct, and loud) failure. That is the
  intended semantics: a target that never died means the leg measured nothing.
* S9/S10 strengthen two clauses. Strengthening is not free: S10 turns a
  previously-False leaf into `None` for a missing data chunk, so any *future*
  consumer of that leaf must handle three values. No current consumer does.

**Stop condition.** The next deletion would have to remove a receipt leaf
(`declared_bound_frames` on the unbounded kill, or one of the witness leaves in
R10) — that is a *declared diff* against the round's reference receipts, so it
is a ledger decision, not a simplification. Likewise the two remaining
"honesty" pins (R7, R8) and the relational-rate question (R9) cost weight or
trade falsifiability corners to fix. The seat stops here.

---

## 8. Evidence index

| artifact | path |
| --- | --- |
| applied batch (asserting patcher) | `corpus/live/r77-simpl/apply_simplifications.py` |
| unified diff of the batch | `/tmp/r77-simpl-cand/corpus/fixtures/measure_audio.py.diff` (copy: `corpus/live/r77-simpl/batch.diff`) |
| comparator (A/B/C levels) | `corpus/live/r77-simpl/compare_r77.py` |
| host-free unit equivalence | `corpus/live/r77-simpl/unit_equivalence.py`, `unit-equivalence.txt` |
| parameter-use census | `corpus/live/r77-simpl/dead-params.txt` |
| region isolation (A4 proof) | `corpus/live/r77-simpl/region-isolation.txt` |
| paired replay driver (quiet-host gate) | `corpus/live/r77-simpl/pair_replay.py` |
| symbol census / dead-symbol proof | `corpus/live/r77-simpl/dead-symbol-check.txt` |
| drift-envelope computation | `corpus/live/r77-simpl/drift-envelope.txt` |
| `sink_gone` vacuity proof | `corpus/live/r77-simpl/sink-gone-vacuity.txt` |
| control / candidate receipts | `corpus/live/r77-simpl/attempt2/{control,cand}.json` (clean pair) and `attempt1/` (negative control) |
| replay logs | `corpus/live/r77-simpl/{replay-proof.txt,pair_replay.log,pair.run.json}` |
| env receipts as written | `/tmp/r77-simpl-control/corpus/live/runs/*-capture-r77/measurements.json`, `/tmp/r77-simpl-cand/corpus/live/runs/*-capture-r77/measurements.json` |
