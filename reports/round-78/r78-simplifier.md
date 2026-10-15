# R78 SIMPLIFIER (audio) — YAGNI deletion on the r78 arm

Round 78, wave `shokunin-train-20261101-w19`. Repo
`/home/vgpnk/Projects/shokunin/audio-shokunin` @ HEAD **`d9aa6f9`** ("r78
work: playback-direction lattice — 8 entries, 60+ legs"). Audited surface:
`corpus/fixtures/measure_audio.py` — the `+2401/−3` of that commit
(fixture blob `d21f5637…`, sha256
`af28eadef3008973863f1a4dedeb51ed6a38911f9b831f1bff5db53dd95cee9a`), the
`--probe-capture-r78` family only.

**Seat: SIMPLIFIER.** Deliverables are untracked: `fold.diff`, the applier
and the proof scripts, `receipts/`, and the verified fold copy
(`vfold/measure_audio.py` + its receipts and comparisons) under
`corpus/live/r78-simplifier/`, plus this report. **No tracked file was
edited**: the shared tree's fixture is byte-identical to `d9aa6f9` at every
stamp below (`git hash-object corpus/fixtures/measure_audio.py` =
`d21f5637…`; `git status --porcelain` carries no tracked modification). The
batch was applied only inside a `/tmp` env materialized from the pinned
commit.

---

## 0. Headline

| # | question asked | answer |
| --- | --- | --- |
| 1 | dead constants? | **4/37** — `PLAYBACK_R78_CAP_{TONE,FRAMES,UNLINK,RELINK}_S` are referenced **nowhere** (`census.txt` §1, `refs=1` = the definition). They are not merely dead: they are a **stale authority** (6.0 s / 4.8 s / 1.6 s / 3.2 s) against the zeros entry's measured literals (12 s tone, 7 s / 5 s captures, unlink at 1.6 s, relink at **3.9 s**). |
| 2 | dead helpers? | **0/26.** Every `_playback_r78_*` helper and both `*_r78_entry` builders have a live call site. The one *dead envelope* is `_playback_r78_link_map`'s `exit`/`error` fields — all 3 call sites read `links` only (`census.txt` §4). |
| 3 | dead params? | **2** — `_playback_r78_write_tone(rate=…)` (10/10 call sites take the default) and `_playback_r78_tone_windows(window_s=…)` (10/10, 4 uses in the body). Plus 4 dead `cls, _line = …` bindings. |
| 4 | unreachable branches / vacuous guards? | **2 vacuous guards** in `capture_unlinked_zeros_r78_entry` (`len(seq) >= 7`, `len(seq_b) >= 2`): the event tables fix **7** and **5** size samples and neither loop breaks (`census.txt` §6), so the false arm cannot run. Plus 1 dead filter (`isinstance(l, dict)`) and 1 duplicated branch selector (S9). |
| 5 | duplicated leg-table shape? | 3 single-source folds: the inline `pwlink` adapter → the declared batch helper (S5); the two `plugin_default`/`plugin_pipewire` blocks → one leg loop with byte-identical failure text (S6); the lattice table's **second** walk (the `default_sink_trace` rebuild) → derived from the legs it already carries (S8b). |
| 6 | applied batch | **25 replacements, +71 / −109 lines (net −38; 9 255 → 9 217)**; replay-proven (§3): the accepted pair (pristine vs folded, back-to-back in one window) is **A = 0 / B = 0 / C = 0 over 13 142 leaves with identical `failures` maps on both sides**, and the folded receipt is **A = 0 / B = 0 / C = 0 over 13 148 leaves with `failures: {}` on both sides** against the round's canonical clean receipt. |
| 7 | candidates found but **not** applied | §4 R1–R7, each with its exact receipt delta — every one of them moves a leaf the canonical receipt pins today (28-leaf `default_sink_trace`, 14-leaf `expected`, 14-leaf `expected_nodes`, …), which is not a fold this seat may make. The 28-leaf delta is *measured*, not asserted (§3.4). |
| 8 | round-ledger findings | §5: the `pactl` gate is a **tautology** of its own two pins; the `segv_audio` leg's crash pin is **falsified on the current host state** — 6/6 standalone and 5 of 7 in-battery runs return `rc=1 no target node available` while its three siblings are `rc=-11` 10/10, on the pristine arm too; the `err` bound is now single-sourced at 100 and is unobservable (the host's failure text is 50 chars). |

Axes walked: **A1 weight** (dead authority/bindings/guards), **A2
falsifiability** (every gate kept, one guard made unconditional), **A3
receipt stability** (A = 0 outside declared drift, identical failures),
**A4 pre-r78 isolation** (the batch touches the r78 block only; the 3
rewritten `main()` lines are untouched). The batch improves A1/A2 and leaves
A3/A4 untouched — the only Pareto-admissible shape available to this seat.

---

## 1. Method and freeze anchors

**Static pass** (`census.py` → `census.txt`): per-constant file-wide
reference counts, per-function parameter use counts, call-site censuses for
every parameter the batch deletes, and an AST census of the two zeros legs'
event tables (the vacuous-guard proof). `static_pass.py` is the same pass
with per-local store/load counts.

**Unit equivalence** (`unit_equivalence.py` → `unit-equivalence.txt`): the
pure helpers the batch touches, control vs candidate, on synthetic inputs —
tone bytes (`sha256` equal), the tone classifier on the same wav and on a
mono (unsupported) tap, the hw-params parser on four device-text shapes, the
ratio-bucket helper on a grid, the consumer/producer witnesses on five edge
sets (empty / one-sided / ambiguous), the err-class tuple, and the `pw-link`
adapter on a guaranteed-failing pair. **VERDICT: PASS** — with one
deliberate, non-verdict difference recorded in §5.3.

**Replay pass.** Two scratch envs, each a tracked-only materialization of
`d9aa6f9` (663 files, `git show` blobs, `env-proofs-*.txt`; control =
pristine fixture, cand = folded fixture). Both were driven by
`pair_replay.py --probe-capture-r78`, which gates on a **quiet host** (no
`measure_audio.py` / `pw-record` / `pw-play` / `parec` / `aplay` / `ffmpeg`
/ `sox` process for 20 consecutive seconds) because the r78 entries are
topology *and host-state* witnesses: two concurrent batteries load null
sinks, move `default.audio.sink` and contend for the PCM (the wave's own
reviewer lane ran `--probe-capture-r78` at 20:02–20:06 and
`--probe-capture-r77` at 20:23–20:25 local; the gate waited both out). The
single exclusion is a 2 h 53 m old unpaced `aplay -D null` leftover from the
r75 lane — a stale process, not a battery (the round's canonical clean
receipt carries the same foreign `aplay`, and the fixture's own
`host_is_quiet` reads `false` on every run, so quiet is *reported*, never
required).

**Comparator** (`compare_r78.py`), three levels:

* **A STRICT** — every leaf outside the declared host-drift *classes* must
  be equal, **including the key set** (a removed leaf is a diff).
* **B CONTRACT** — the pinned verdict classes must be equal: failures maps,
  error classes, exit codes, `killed_at_bound`, consumer/producer unions,
  tone verdicts and their aggregates, the named `pactl` classes, sink-gone
  flags, header-mismatch leaves, `blocked` rows.
* **C SELF** — the receipt's own derived relations must hold in *both*
  receipts (nodes derived from the port sets; `consumers_union` from the
  samples; tone aggregates from the window lists; `carries_tone` from the
  8-window law *and* from the tap; the lattice fallback law; `bytes ==
  expected_bytes`; the parec header/payload law).

Declared drift classes (host variance, not the fold): D1 `wall_s`,
D2 fire/apply/release times, D3 the host module counter, D4 host
topology/census snapshots, D5 the `pactl` poll trace, D6 per-window tap
magnitudes, **D6b** the tap's boundary-window any-audio/zero split (one
~0.1 s window flips with the tap's alignment; the verdict leaves
`carries_tone`/`mine_windows`/`mine_spans`/`peak_*` stay strict), D7 growth
traces. Two per-run naming schemes are *normalized* rather than declared:
pid-stamped node names → `_<pid>` and the run's TemporaryDirectory path
(every `aplay` `argv`/`stderr` leaf echoes it) → `<tmp>/`.

**Calibration.** On the canonical clean receipt against itself: **A = 0 /
B = 0 / C = 0** over 13 148 leaves. Against the round's earlier
(contaminated) r78 receipts it reports **A = 350 / B = 148** — the
comparator is not vacuous. §3.4 perturbs one verdict leaf and one table and
is caught.

---

## 2. The applied batch (S1–S9)

`fold.diff` is the batch; `apply_fold.py` asserts each pattern's occurrence
count and prints the diff (applied to the scratch env's fixture only).

| # | deletion | mechanism | evidence |
| --- | --- | --- | --- |
| S1 | `PLAYBACK_R78_CAP_TONE_S` / `_FRAMES_S` / `_UNLINK_S` / `_RELINK_S` | referenced nowhere; the zeros entry carries its own literals | `census.txt` §1 (`refs=1` each) |
| S2a | `_playback_r78_write_tone`'s `rate` parameter | 10/10 call sites pass 2 args; the body now names `PLAYBACK_R78_TONE_RATE` (the only value ever supplied) | call-site census; unit tone `sha256` equal |
| S2b | `_playback_r78_tone_windows`'s `window_s` parameter | 10/10 call sites pass 1 arg; the body names `PLAYBACK_R78_TONE_WINDOW_S` (4 uses) | call-site census; unit classifier dict-identical |
| S3a | `if len(seq) >= 7:` (zeros leg A) | the 12-event table emits exactly 7 size samples and the loop cannot break — the false arm is unreachable; the three checks become unconditional (fail-closed, the r77 S9 form) | `census.txt` §6 |
| S3b | `len(seq_b) >= 2 and` (zeros leg B) | 5 size samples, no break; and on an empty list `not all([])` is `False`, so both forms are no-ops | `census.txt` §6 |
| S4 | `if isinstance(l, dict)` (lattice aggregate) | both `legs` write sites store dicts; the filter can never drop one | `census.txt` §5 |
| S5 | the inline `pwlink`/`pwlink_d` loop in `_playback_r78_run` (15 lines) | it is the same adapter as `_playback_r78_pwlink_batch` (declared 300 lines later); the helper's `err` bound is unified at **100** (the inline path's) so the one adapter is also the wider echo | unit `pwlink_*` checks; §5.3 |
| S6 | the `plugin_default` / `plugin_pipewire` blocks (2×11 lines) | one leg table over `("default", "pipewire")`; the failure text is f-stringed with the device name so **both texts are byte-identical**; the per-leg tap tag/filename are not receipt leaves | unit tone classifier; pair A = 0 |
| S7 | `_playback_r78_link_map`'s `{"links","exit","error"}` envelope | `exit`/`error` are read by nobody (all 3 call sites take `.get("links", [])`); the helper returns the edge list and an unreadable table is the empty set | `census.txt` §4 |
| S8a | 4 × `cls, _line = _playback_r78_errclass(…)` | the second value is never read at those sites (only `_playback_r78_run` needs the matched line, for the `error` leaf) | `census.txt` §2 |
| S8b | the lattice table's second walk (`for n, _r, _e in PLAYBACK_R78_LATTICE`) | `default_sink_trace` restates a leaf every leg already carries (`default_sink_at_leg`); it is now derived from `legs` — same order, same set, same values | pair A = 0 |
| S9 | the resolver guard re-testing `resolver is not None and not str(resolver).startswith("literal:")` | that is exactly the complement of the two branches above it; folded into the `else` branch (and the `str()` on a `str` is gone). The blocked message is byte-identical | pair A = 0 |

Net: **+71 / −109 lines** (25 replacements; 9 255 → 9 217). No gate, no leaf,
no witness, no class and no failure message was dropped.

---

## 3. Replay proof

### 3.1 The accepted pair (pristine control vs folded candidate, one window)

`receipts/pair-accepted/` — control `20261014T234006352387Z` (283.3 s) and
candidate `20261014T234449570961Z` (283.2 s), back-to-back, both landed
`pactl_stale_default`, both `host_is_quiet: false` (the stale r75 `aplay`):

```
leaves compared          : 13142
A strict diffs           : 0
B contract-leaf diffs    : 0
  (declared drift diffs  : 28  [D1 wall clock, D3 host module counter,
                                D4 host topology/census, D6 per-window tap
                                magnitudes, D6b boundary-window split])
C self-consistency viols : 0
control   failures       : {"playback_class_segv_r78_probe": ["segv
                            segv_audio: expected rc=-11 (SIGSEGV), got 1",
                            "… no target node available"]}
candidate failures       : {"playback_class_segv_r78_probe": [ … identical
                            two strings … ]}
failures identical       : True (empty: False)
VERDICT: PASS (A=0 B=0 C=0 failures ctl=1 cand=1 identical=True r78=1)
```

**The folded fixture reproduces the pristine fixture's receipt leaf for leaf**
(A = 0 over 13 142 leaves, including the key set), with **identical
`failures` maps on both sides** — and the one failure that both sides carry
is the host-state refusal of §5.2, present on the *pristine* arm too. That
is the brief's standard met in its strongest available form on this host:
`failures` identical, pinned leaves unchanged, every gate intact.

### 3.2 Cross-window: the folded receipt vs the round's canonical clean receipt

`vfold/compare-canonical.txt` — the folded env's first run
(`20261014T231622914248Z`) against the round's canonical clean receipt
(`corpus/live/runs/20261014T221945369366Z-capture-r78/measurements.json`,
the author's declared `failures: {}` pass):

```
leaves compared          : 13148
A strict diffs           : 0
B contract-leaf diffs    : 0
  (declared drift diffs  : 41)
C self-consistency viols : 0
control   failures       : {}
candidate failures       : {}
VERDICT: PASS (A=0 B=0 C=0 failures ctl=0 cand=0 r78=0)
```

Every leaf the canonical receipt carries is reproduced by the folded fixture
outside the declared host classes, with `failures: {}` on both sides. The
same comparison for the **pristine control** of that window
(`vfold/compare-within-arm.txt`) yields **A = 27 / B = 15**, and **all 27 are
inside `playback_default_follow_r78_probe`**: the control landed
`pactl_delayed_default` (the `pactl set-default-sink` write landed *after*
the 5.6 s poll — a class the entry admits) while the canonical is
`pactl_stale_default`, so its `nofollow` leg spawned on a different default
and its `restored` tap missed the tone. Every other r78 entry and every
pre-r78 cell is leaf-equal. That is a *host-class* difference on the
pristine arm, not a fold difference — and it is why the pair driver requires
both sides to land the same class before a pair is accepted.

### 3.3 Within-arm reproducibility, and the host flake the pair carries

| comparison (two windows each) | A strict | B contract | where |
| --- | --- | --- | --- |
| pristine control vs pristine control | 37 | 20 | the `pactl` class flip + the `segv_audio` refusal |
| folded candidate vs folded candidate | 10 | 5 | the `segv_audio` refusal only |

The pristine arm's own cross-window difference is *larger* than the folded
arm's — the fold adds no instability; the host does. The four pairs
attempted today (`receipts/attempt1/`, `receipts/pair-accepted/`):

| attempt | window (local) | pristine control | folded candidate | disposition |
| --- | --- | --- | --- | --- |
| 1 | 20:06:56→20:16:22 | follow `restored` tap flake, class **delayed** | clean, class **stale** | rejected: classes differ |
| 2 | 20:19:35→20:24:16 | `segv_audio` + `aplay baseline` EBUSY (reviewer lane's r77 battery live) | aborted | rejected: contended window |
| 3 | 20:25:35→20:35:03 | `segv_audio` | `loss unlink` stall + `segv_audio`, class **delayed** | rejected: classes differ |
| 4 | **20:35:23→20:44:49** | `segv_audio` | `segv_audio` (identical) | **accepted** (§3.1) |

### 3.4 Unit equivalence and the negative control

* `unit-equivalence.txt`: **UNIT VERDICT: PASS** (tone bytes, classifier,
  hw-params parser, ratio buckets, consumer/producer witnesses, err classes,
  the `pw-link` adapter).
* `negative-control.txt` (against the canonical receipt, mutations applied to
  the *candidate* receipt): flipping one `carries_tone` → **A = 1 / B = 1 /
  C = 1** (the C level fires because the pin must equal both the tap's and
  the 8-window law); deleting `default_sink_trace` → **A = 28 / B = 14**,
  which is exactly the receipt delta claimed for candidate **R1** in §4.

---

## 4. Candidates found and **deliberately not applied**

Every item below is real weight, and every one of them moves a leaf the
canonical receipt pins today. Under the wave's own standard (the comparator
counts a removed key as an A-strict diff; the r77 batch's A = 0 over 2 708
leaves) they are **not** admissible as a simplifier fold — they are
proposals for a round that is allowed to move the receipt.

| # | candidate | weight | exact receipt delta |
| --- | --- | --- | --- |
| R1 | `entry["default_sink_trace"]` (lattice) | 3 lines | **28 leaves** (measured by the §3.4 mutation) — it is a second walk of `PLAYBACK_R78_LATTICE` re-emitting `legs[*].default_sink_at_leg`, which every leg already carries. The S8b fold removes the *duplicate walk*; removing the leaf is a contract decision. |
| R2 | `legs[*]["expected"]` (lattice, 14 legs) | 1 line | **14 leaves**, never read: the verdict loop re-reads `expect` from the table, not from the leg. A dead pin restating the gate's own conjunct. |
| R3 | `legs[*]["expected_nodes"]` (props, 14 legs) | 1 line | **14 leaves**, never read: the verdict loop recomputes `want = [default_sink_at_leg] if exp == "default" else exp` from the same rule. Same class as R2. |
| R4 | `legs[*]["early_consumers"]` / `late_consumers` / `landed_peer` / `peer_unresolved` | 4 lines | **3 leaves on this host** (only the `monitor_name` leg carries them; `landed_peer` was `None` this run). Evidence for the racy `.monitor` class, unread by the gate. |
| R5 | `entry["warmup"]`, `legs["pipewire_hold"]["consumers"]`, `entry["default_sink_final"]` | 4 lines | **2 + 3 + 1 leaves.** The warmup/hold *runs* are the mechanism (they must stay); only their extra pins are weight. |
| R6 | the zeros legs A/B scaffolding (event loops, teardown, leaf assembly) | ~25 lines | **Not admissible as-is**: a single-source helper must either add `relink_rc` to leg B (**+1 leaf**) or take 7 parameters (moving weight, not deleting it). The two legs share a shape but not a leaf contract — leg A reaps at `TIMEOUT_S * 2`, relinks, and records `relink_rc`; leg B does neither. |
| R7 | the two stall-verdict blocks (lattice `target_0` vs props stall legs) | ~12 lines | 3 checks each, same conjuncts, **different failure text** ("--target 0 must STALL" vs "expected a stall"). Unifying changes a *diagnostic* string (unobservable while `failures: {}`), which is a behavior change this seat will not make silently. |

---

## 5. Findings for the round ledger

### 5.1 The `pactl` gate is a tautology of its own pins

`playback_default_follow_r78_entry` writes

```
"pactl_stale_default":   (pactl_rc == 0 and moved_at is None),
"pactl_delayed_default": (pactl_rc == 0 and moved_at is not None)
```

and then gates `if not (stale or delayed): failures.append(…)`. The
disjunction of the two pins is **exactly `pactl_rc == 0`**, so the gate can
only ever fire on a non-zero `rc`; the named-class distinction the round
reports (`pactl_stale_default` on the canonical run, `pactl_delayed_default`
on my attempt-1 control and attempt-3 candidate) is **recorded but never
gated**. Both classes were observed live within the hour, and they move
leaves (the `nofollow` leg's spawn default, its tap, the pin/follow pins) —
so the class is a *measured host fact* the harness admits, but the gate
cannot distinguish it.

### 5.2 `segv_audio`'s crash pin is falsified on the current host state

The entry pins `-P media.class=Stream/Input/Audio --target <probe sink>` as
`class_override_segv`: `rc=-11`, empty stderr, no consumers. Measured today
(`vfold/segv-mechanism.txt`, a bounded probe: 6 fresh processes on the
**pristine** fixture, 3 with a fresh sink name and 3 with the props entry's
just-destroyed name pre-used):

| leg | `media.class` | rc | stderr |
| --- | --- | --- | --- |
| `segv_sink` | `Audio/Sink` | **−11** 6/6 | empty |
| `segv_audio` | `Stream/Input/Audio` | **1** 6/6 | `remote error: … res:-2 (No such file or directory): no target node available` |
| `segv_duplex` | `Audio/Duplex` | **−11** 6/6 | empty |
| `segv_bogus` | `Audio/Bogus` | **−11** 6/6 | empty |

The three sibling crash legs are stable (10/10 across the standalone probe
and the battery runs); `segv_audio` is **not** a crash on this host state —
it is a *server refusal* (`rc=1`, wall still 2.01 s), and it fired in **5 of
the 7 in-battery runs** taken today (pristine *and* folded arms) plus 6/6
standalone runs. It is not fold-related; the
author's canonical run recorded `rc=-11`, so the class is host-state
dependent. A name-reuse hypothesis (the segv entry reloading
`PLAYBACK_R78_PROP_SINK_A`, the name the props entry just destroyed) was
**falsified by the probe's fresh-name arm**, which fails identically. The
one correlate this seat can name: the session default **source** changed
between the author's session (`DualSense … Direct__source`) and this one
(`HiFi__Line__source`), and `segv_audio` is the only one of the four legs
whose stream class is an *input* — the only one that must resolve a
source-side target. The mechanism is **not** resolved by the receipt; the
round should name the refusal (`class_override_target_refused`) instead of
pinning the crash for that leg.

### 5.3 One deliberate non-verdict difference: the `err` bound

S5 removes the inline adapter, whose `err` echo was bounded at 100 chars,
and single-sources the declared helper, whose bound was 80. The unified
bound is **100** (the wider echo). This is the batch's only leaf-level
difference on any path, it is confined to *failed* `pw-link` operations, and
no gate reads `err` (every `pwlink` gate reads `exit`). Measured: the host's
failure text for a nonexistent pair is 50 chars
(`"failed to unlink ports: No such file or directory\n"`), so **both bounds
are unobservable** on this host — the unit check and every pair confirm it
(every observed `err` is `null` or 50 chars).

### 5.4 Dead constants are stale authority, not decoration

`PLAYBACK_R78_CAP_TONE_S = 6.0`, `_FRAMES_S = 4.8`, `_UNLINK_S = 1.6`,
`_RELINK_S = 3.2` vs the code they were meant to bound: a 12 s tone, a 7 s
(leg A) / 5 s (leg B) capture, an unlink at 1.6 s and a **relink at 3.9 s**.
A future reader who trusts the names would bound the wrong window. S1
deletes them; the literals are what the receipt was measured with.

---

## 6. Risks, limits, and what this fold does **not** claim

- **Host-state witness.** The r78 entries measure the live graph: null
  sinks, `default.audio.sink`, the PCM lock. Every run reports its own
  contention census (`host_is_quiet: false` on this host because of the r75
  lane's stale unpaced `aplay -D null`); the pair driver gated on 20
  consecutive quiet seconds and waited out the wave's reviewer lane twice.
- **The accepted pair's `failures` are identical but not empty** (§3.1):
  both sides carry the same `segv_audio` host-state refusal of §5.2, which
  is present on the pristine arm. The empty-`failures` form of the claim is
  supplied by §3.2 (folded receipt vs the canonical clean receipt, `A = 0`,
  `failures: {}` on both sides, 13 148 leaves).
- **No leaf was deleted.** R1–R7 are the round's decision, not this seat's.
- **The fold does not touch** `main()`'s three rewritten lines, any pre-r78
  cell, the shared `_capture_*` helpers, or any assertion/witness. The
  applier asserts every pattern's occurrence count, so a drifted fixture
  fails the batch rather than silently mis-applying it.
- **Not measured:** whether the folded fixture's *failure* paths render the
  same text (the S6 failure text is byte-identical by construction, the S5
  bound is argued in §5.3); whether `segv_audio` crashes on a host state
  where the default source is the DualSense (§5.2 names the correlate but
  this seat did not switch the host's default source to test it).
