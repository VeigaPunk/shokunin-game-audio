# R76 critic — capture arm, POST-COMMIT verify

Seat: critic (LEAF). Repo `~/Projects/shokunin/audio-shokunin` @ HEAD
`d566a317e6b849032c444155e933b33a102bbada`. Scope of this report:
adversarial review of the landed capture arm (`--probe-capture-r76`,
`corpus/fixtures/measure_audio.py` +1123/−3). Evidence index:
`corpus/live/r76-critic/RECEIPTS.md`; harnesses and reproductions live in
`corpus/live/r76-critic/`.

**Bottom line: I could not falsify any pinned class in the canonical
receipts.** The receipt reproduces byte-for-byte (one sha, five runs,
including two of mine), and the prior arm replays to a one-leaf difference.
Every defect I found is in the *checker/provenance* layer — places where the
arm keeps reporting `failures: {}` while the claim it carries has become
vacuous or mis-labelled. One of them is **not latent: D1 already fired in
the author's own run `…T181743427243Z` — the run the report presents as a
clean `failures: {}` run — where the sever entry's `parecord_term` cell
captured zero audio bytes and the class check still passed.** Ranked below;
D1–D3 are the ones I would fix before the next consumer arm is built on this
pattern.

## 1. Reproduction — the arm is deterministic and the receipts are honest

| run | who | sha256 (measurements.json) |
| --- | --- | --- |
| `…T182450100472Z-capture-r76` | author canonical | `ba36cd70f765826a9937fc78c62143c984790f1bdc26a4ad8aaf813cfc00f92f` |
| `…T182539237046Z-capture-r76` | author rerun | `ba36cd70…` |
| `…T183215518470Z-capture-r76` | **critic run 1** | `ba36cd70…` |
| `…T183309733895Z-capture-r76` | concurrent seat (not mine) | `ba36cd70…` |
| `…T183404004733Z-capture-r76` | **critic run 2** | `ba36cd70…` |

`timeout -s KILL 480 python3 corpus/fixtures/measure_audio.py
--probe-capture-r76`, `failures: {}`, `EXIT=0`, both critic runs. A
key-by-key walk of the two JSON trees (author run 1 vs critic run 1) emits
**no differences** — the byte-identity is not an artifact of the hash
comparison. Mode/suffix wiring is correct (`probe-capture-r76`,
`-capture-r76`); the flag is present in the 120-flag mutex sum; the diff's
only non-insertion lines are that sum and the two ternary chains, each
prepending the r76 clause ahead of the prior expression verbatim.

## 2. Prior rows untouched — replayed, not assumed

I re-ran the *previous* arm on the r76 fixture:

```
timeout -s KILL 480 python3 corpus/fixtures/measure_audio.py --probe-consumers2-r75
→ corpus/live/runs/20261014T183519581984Z-consumers2-r75   failures: {}
```

Structural diff against the r75 canonical (`…T172034398145Z`, sha
`9de8b8f8…`): **exactly one differing leaf** —
`consumer2_paplay_ops_r75_probe/daemon_gate_dead/wall_s` `0.001 → 0.002`.
All 29 entries, every prior row, byte-identical. "Insertion-only" is
confirmed at receipt level. (The residual leaf is a *pre-existing* r75 wart:
a raw wall-clock float on a sub-ms dead-daemon gate leg, unbucketed; the r75
arm itself produced three distinct shas across its own runs. The r76 arm's
`wall_lt_0.5s` class is the right pattern for that field.)

## 3. Defects (counterexample → evidence → axes → smallest safe correction)

### D1 — a zero-audio capture satisfies the parecord TERM-bound gate, and the landed classifier calls that same file `riff_wav`

**Counterexample.** A capture that produced *no audio* is admitted by the
bounded entry's parecord gate and classified as a correctly-named wav:

- `parecord nodev.wav` (no `-d`) → rc=1, `Stream error: No such entity`,
  **and a 44-byte finalized WAV** — `RIFF$...WAVE fmt 16 PCM 2ch 44100Hz
  data(0)`. Same for a dead server (`repro/nodev.wav`, `repro/dead.wav`).
  That shape is already in the arm's own gate receipt (`pwrecord_auto_target`,
  `pwrecord_monitor_alias`, `parecord_no_device`: `exists: true`,
  `riff_size_field: finalized`, `data_declared_field: finalized`,
  `duration_bucket_s: 0.0` ⇒ `data_actual == 0`).
- Landed classifier on that artifact: `_capture_out_kind` → **`riff_wav`**
  (both for the full inspect dict and for the reduced sever leaf, which
  carries `data_actual_zero: True`).
- Landed gate on that artifact: `rc == 0 and data_finalized and
  data_64k_aligned` — `0 == 0` is "finalized" and `0 % 65536 == 0` is
  "aligned", so the conjunction holds on an empty capture.

**Evidence — and it already fired, in the author's own receipts.**
`measure_audio.py:3090` (`"empty"` tests `bytes == 0` / `file_zero_bytes`,
never `data_actual_zero`); `:3076` (0 is 64k-aligned by construction);
`:3605-3606` and `:3720-3721` (the two checks);
`corpus/live/r76-critic/exp_classifier.py` (`EMPTY44 out_kind: riff_wav`,
`EMPTY44 sever-leaf out_kind: riff_wav`) and `corpus/live/r76-critic/repro/`
plus the new `repro/pwr_notarget.wav` (44 bytes, `data(0)`, rc=1).

Sweeping all nine `-capture-r76` receipts, the sever entry's `parecord_term`
cell carried **zero audio bytes** in two of them:

| receipt | sever `parecord_term` | sever entry `failures` |
| --- | --- | --- |
| `…T181454123380Z` | `data_actual_zero: true`, wave `honest_empty` | 2 (ffmpeg-KILL union, arecord riff field — *not* this cell) |
| `…T181743427243Z` (**the report's "clean run, `failures: {}`"**) | `data_actual_zero: true`, wave `honest_empty` | **0** |
| `…T182210…` onward (incl. the canonical pair and my runs) | `data_actual_zero: false`, wave `honest` | 0 |

So the gate that certifies "parecord TERM ⇒ rc=0, finalized, granule payload,
wave honest" **passed on a capture that carried no audio at all**, in a run
the report presents as clean. The pinned table is still correct (the
canonical pair shows `honest` with payload), and the receipt does record the
degenerate state (`data_actual_zero`, `honest_empty`) — but `failures: {}`
does not certify that row, which is what the ledger reads. Same family as
the wave-14 vacuous-invariance guard: one admissible degenerate input makes
the class claim vacuous.

**Axes.** name-axis (container class), bound-unit (parecord TERM bound),
sever-wound-class.

**Smallest safe correction.** (i) add `data_actual_zero` to
`_capture_file_leg`'s `file` leaf; (ii) in `_capture_out_kind`, extend the
`"empty"` test with `or insp.get("data_actual_zero")`; (iii) add
`fin.get("data_actual_zero") is False` to the parecord TERM-bound check and
to all four TERM cells (`:3720`).

### D2 — the gate drops a leg silently and still reports a clean pass

**Counterexample.** With `_capture_inventory` monkeypatched to a degraded
(empty) inventory, the landed `capture_gate_r76_entry()` runs **11 of 12**
named-failure legs, silently omits `pwrecord_monitor_alias`, and returns
`failures: []` — i.e. the report's "all 12 named gate legs landed exactly
the predicted (rc, class) pairs" becomes vacuously 11/12 with no signal in
the failure carrier.

**Evidence.** `measure_audio.py:3448` (`if leg is None: continue`);
`corpus/live/r76-critic/exp_gate_vacuity.py` output (`legs present: 11`,
`MONITOR-ALIAS LEG ABSENT: True`, `failures: []`). `viability.monitor=false`
is still recorded, so this is a completeness defect, not false provenance.
`pwrecord_monitor_alias` is the only leg that can be absent today, but the
`continue` pattern is what a future leg will inherit.

**Axes.** capture-gate.

**Smallest safe correction.** Replace the silent `continue` with a recorded
`{"blocked": "no monitor enumerated"}` leaf (same idiom the entries already
use elsewhere) so the leg count and the failure list both carry the
degradation.

### D3 — the sever entry voids a whole consumer's verification if *either* cell early-exits

**Counterexample.** `if tcell.early_exit_code is not None or
kcell.early_exit_code is not None: continue` skips all four class assertions
for that consumer. An `alsa_busy` early exit on the TERM cell (documented as
honest data under a foreign holder) also suppresses the KILL cell's
placeholder check — so under device contention the arm reports a clean pass
for a consumer whose KILL class was never verified.

**Evidence.** `measure_audio.py:3716-3718`. On this round the hole is not
exercised: all 8 cells in all nine `-capture-r76` receipts carry
`early_exit_code: null`, so
the four consumers were genuinely verified (I checked each cell).

**Axes.** sever-wound-class.

**Smallest safe correction.** Skip per cell, not per consumer: assert the
TERM class on `tcell` when `tcell.early_exit_code is None`, and the KILL
class on `kcell` when `kcell.early_exit_code is None`, independently.

### D4 — `wave_frames_class` returns `"inflated"` whenever the `fmt` leaf is missing

**Counterexample.** With `frame_bytes == 0` the honest frame count collapses
to 0, so *any* parseable wav with `n > 0` classifies as `inflated`. Calling
the landed `_capture_parser_verdict` on one honest 4096-byte wav twice — once
with its `fmt` leaf, once without — flips the class `honest → inflated`. The
arecord-KILL accept-and-lie assertion (`wave_frames_class == "inflated"`)
can therefore be satisfied for the wrong reason; today it is additionally
pinned by `data_declared_field == "placeholder_80000000"`, which is why no
claim breaks.

**Evidence.** `measure_audio.py:3108-3117`; `exp_classifier.py` output
(`REAL parser verdict (fmt ABSENT): {"wave_frames_class": "inflated"}`).
`_capture_wav_inspect` only sets `fmt` when the *first* chunk is `fmt ` with
declared ≥ 16, so the path is reachable by a leading LIST/JUNK chunk.

**Axes.** sever-wound-class (parser-tolerance evidence).

**Smallest safe correction.** Return `None`/"unknown" when `frame_bytes ==
0`, and require the arecord-KILL gate to see exactly `"inflated"`.

### D5 — provenance: the roundtrip writes into the author's seat directory and labels its evidence as the author's

**Counterexample.** `scratch = ROOT / "live" / "r76-author"` and the detect
label `"live/r76-author/<tmp>/roundtrip_capture.wav"` are hard-coded. Every
non-author run of the landed probe (a) writes into another seat's directory
and (b) files evidence labelled as the author's.

**Evidence.** `measure_audio.py:3935`, `:3990`;
`corpus/live/r76-author/` mtime advanced to `15:32:15.504` (critic run 1) and
`15:34:03.989` (critic run 2), while its `scratch/` subdir is the author's
from `14:55`; the label string appears in the `detect_legs.sox.captured.input`
leaf of every receipt, including mine.

**Axes.** provenance, write-scope (leaf seats may only write their own
`corpus/live/<round>-<seat>/`).

**Smallest safe correction.** Take the scratch dir from the run (e.g.
`tempfile.mkdtemp(dir=ROOT/"live")` or a run-scoped path) and derive the
label from `cap.relative_to(ROOT)` instead of a literal.

### D6 — provenance: the roundtrip's argv normalizes away the sink it used

**Counterexample.** `capture_roundtrip_r76_probe.capture_leg.argv` is the
hand-written `"pw-record -P stream.capture.sink=true --target
<default-sink> -n 240000"` — the sink node is not recorded, and the only
inventory snapshot in the receipt lives in a *different* entry (the gate,
its own enumeration). If the default sink moved between the gate's snapshot
and the roundtrip's, the pinned 960044 B would still be reported against a
sink nobody can name. The bounded entry gets this right
(`pwrecord_monitor_bound.argv` carries the resolved node verbatim).

**Evidence.** receipt leaves `…/capture_roundtrip_r76_probe/capture_leg/argv`
vs `…/capture_bounded_r76_probe/legs/pwrecord_monitor_bound/argv`;
`measure_audio.py:3957-3967`.

**Axes.** provenance, roundtrip-parity.

**Smallest safe correction.** Record the resolved `sink` in the
`capture_leg` leaf (and/or an inventory digest for the entry) rather than
normalizing it away.

### D7 — the stated PipeWire counter normalization never fires

**Counterexample.** `_capture_tail` scrubs `node \d+` and `id=\d+ seq=\d+`,
but the observed text is `remote error: id=2 seq:7 res:-2 (No such file or
directory): no target node available` — `seq:` not `seq=`, and "node" is
never followed by a digit. Both substitutions are no-ops; **zero** tails in
the receipt carry the `<n>` normalization.

**Evidence.** `measure_audio.py:2972-2973`; my regex replay over the
observed strings (`NO-OP`), and a full walk of the receipt's
`stderr_tail`/`error` leaves (`tails with <n> normalization applied: 0`,
two raw-counter leaves). Determinism holds today only because the counters
are reproducible on this path — the comment's stated guarantee is not
implemented.

**Axes.** receipt-determinism (latent).

**Smallest safe correction.** `r"id=\d+ seq[:=]\d+"` (and normalize
`res:-?\d+`), then re-pin the sha.

### D8 — sever cells carry no byte count, and `data_64k_aligned` is not a TERM/KILL discriminator

**Counterexample.** The author's own `parecord_kill` cell — a *wound* — is
also `data_64k_aligned: true`, and 0 is aligned by construction (D1). So
alignment witnesses "the written payload is an exact multiple of 64 KiB",
not "the buffered remainder was lost": the arm never compares delivered
against written bytes, and the sever `file` leaf records no `bytes` at all,
so a reader cannot distinguish 65536 from 393216 in the TERM cell.

**Evidence.** receipt `capture_sever_r76_probe/cells/parecord_kill/file`
(`data_64k_aligned: true`) and `…/parecord_term/file` (no `bytes` key);
`measure_audio.py:3324-3333` (the sever leaf) and `:3076`.

**Axes.** sever-wound-class, claim strength.

**Smallest safe correction.** Record `bytes`/`data_actual` in the sever leaf
and state the claim as "granule-quantized payload at TERM", or add the
delivered-vs-written comparison the "remainder is lost" wording needs.

### D9 — hygiene: ~29 GB of rotation artifacts under the author's scratch dir

**Evidence.** `du -sh corpus/live/r76-author/scratch` → **29G**, 60 files,
including **11 rotation files > 1.9 GB** — four of them exactly
2 147 483 692 B (= the `0x80000000` placeholder + 44-byte header), the rest
1.86–1.98 GB. These are the flood artifacts behind the "never run `-D null`
unbounded" claim (good corroboration, and they also pin the ~2 GiB rotation
size the report states), but the report lists the scratch dir among "new
files (all untracked, operator to commit)".

**Axes.** write-scope/hygiene.

**Smallest safe correction.** Delete the flood artifacts (keep the small
`arc*.txt`/json/strace files); do not `git add -A` that directory.

### D10 — the "no author-created process remains (verified via pgrep)" claim is not attribution-safe

**Counterexample (mine, and it failed).** I observed two live `parecord`
processes at `15:33:3x` whose `/tmp/capture-r76-*` temp dirs no longer
existed and initially read them as a leak of the landed arm. They were not:
a *concurrent* probe run was live in this repo (`ps` shows
`bash -c … corpus/live/r76-reviewer/scratch/tree/corpus/fixtures/measure_audio.py
--probe-capture-r76` plus a second `timeout … corpus/fixtures/measure_audio.py`
whose CWD was this repo), and the two processes were its in-flight legs. After
both runs finished, `ps` showed no consumer processes at all — **no leak**.
The finding is the method: the arm's temp dirs share the fixed prefix
`capture-r76-`, so a `pgrep` check cannot attribute a process to a run on a
host with concurrent seats.

**Evidence.** `pgrep -af measure_audio.py` / `ps -eo pid,ppid,etime,cmd`
transcript; `/tmp/capture-r76-*` mtimes; final empty `ps`; my own receipt
pair (`…T183215518470Z`, `…T183404004733Z`) plus the unattributed
`…T183309733895Z` written at `15:33:09`. At the end of my window a third
seat was still running the same arm from a mirrored fixture
(`…/corpus/live/r76-simplifier/mirror/corpus/fixtures/measure_audio_simplified.py
--probe-capture-r76`), so up to three seats share this host's
`/tmp/capture-r76-*` namespace.

**Axes.** provenance, evidence method.

**Smallest safe correction.** Run-scope the temp prefix (include the run id)
and have the process check filter on the run's own tmp dirs.

## 4. Attacks that failed (the arm held)

- **The placeholder partition is not foolable in the wound→finalized
  direction.** Synthetic matrix through the landed inspector:
  `(riff=finalized, data=0xFFFFFFFF)` → `data_finalized False`;
  `(riff=8, data=0xFFFFFFFF)` → `placeholder_8` / `placeholder_ff`;
  `(riff=finalized, data=0x80000000)` → `placeholder_80000000`,
  `data_finalized False`. The two size fields are classified independently,
  no placeholder value maps to `finalized`, and no valid wav can carry
  `riff_sz ∈ {8, 0xFFFFFFFF, 0x80000000}` — so no healthy file is
  mis-classified as a wound either. `placeholder_80000000` on the *riff*
  field is a latent branch (measured `other` on arecord-KILL, as the entry
  comment honestly says).
- **No dead-daemon class aliasing found.** The three dead-daemon legs land
  three disjoint strings (`pw_context_connect() failed: Host is down`,
  `Connection failure: Connection refused`, `No such process`) against three
  disjoint patterns, and each is checked as an exact `(rc, class)` pair. Had
  an env override been ignored, the leg would have *succeeded* and the
  expectation would have failed loudly — the gate cannot silently pass a
  dead-daemon leg.
- **rc is never the verdict — reproduced.** `pw-record -n 48000` completes an
  exact 192044-byte finalized capture at rc=1 (bounded entry, every
  receipt including the degenerate runs); ffmpeg TERM lands rc=255 with a usable file; arecord TERM lands
  rc=1 + `aborted_by_signal` with a finalized file.
- **The monitor roundtrip witness does separate signal from silence.** A
  silent capture fails `nonzero_fraction_gt_half` (0 > 0.5) *and*
  `peak_within_3db_of_member`, because the level term uses
  `max(cap_peak, 1)` so a zero peak lands at −90.3 dB against the member
  (outside 3 dB). I did not force silence (no monitor mute was attempted),
  so this is analysis of the landed predicate plus the receipt's
  `960044 B / finalized / both predicates true`; it is not an empirical
  silence trial.
- **Inventory change mid-run.** Every entry re-enumerates, and
  target-dependent legs are loud (stale target ⇒ the exact `(rc, class)`
  expectation or the byte-count check fails; the hw device is recorded in
  the cell's `device`/argv). The single silent case is D2.

## 5. Claims that exceed local evidence (bounded, low severity)

- `set_params:1462` / `set_params:1404` (arecord `-D default|pipewire`
  capture block, `-c 1` rejection): the receipt carries only `Unable to
  install hw params` / `Channels count non available`, and no artifact under
  `corpus/live/r76-author/scratch/` contains either line number. The *class*
  is witnessed; the line citation is not.
- "`-t` … overshoots ~0.6 % on paced sources": the leg records
  `duration_bucket_s` at 0.25 s granularity on a 1.0 s capture (25 %), so the
  receipt cannot witness 0.6 %.
- "the buffered remainder is lost" (parecord TERM): see D8.

## 6. Fixable defect vs tradeoff

All of D1–D10 are fixable checker/provenance defects — none is a claim
tradeoff, and none requires weakening a pinned number. Nothing here forces
the canonical judge to reject the round: the six claim families reproduce to
the byte, prior rows replay to one pre-existing leaf, and no pinned class in
the canonical receipts is false.

What D1 changes is the *weight of `failures: {}`* for this family: it is
already known to pass on a zero-audio capture (author run
`…T181743427243Z`), so the canonical pair's `parecord_term` row is certified
by the receipt's `data_actual_zero: false` + `wave honest` leaves, not by the
empty failure list. That is a checker repair (D1's three-line fix), not a
claim retraction — but until it lands, every future `parecord`-family pass
should be read off the leaves rather than off `failures`. D2/D3 are the same
defect class one level up (silent skips), and they are the ones that would
let a later arm silently drift.

## 7. Honest edges of this review

- Five-run byte-identity is evidence of determinism *on this host, this
  toolchain, this session*; it is not a portability claim, and it does not
  survive a different PipeWire/alsa-utils/ffmpeg version.
- The D1 sweep covers the nine `-capture-r76` receipts that exist in the
  tree; the two degenerate ones are the author's earliest runs. I did not
  re-run the arm under artificial source-resume latency to force the
  degenerate case in the bounded leg (it has never been observed there).
- I did not force a foreign device holder (`alsa_busy`), a silent monitor, a
  mid-run inventory change, or a concurrent-run collision; those paths are
  analysed from code and receipts, not measured, and are labelled as such.
- `…T183309733895Z-capture-r76` is not mine (my runs are
  `…T183215518470Z` and `…T183404004733Z`); a concurrent seat's invocation of
  the same arm was live in this repo during my window, which is what I
  attribute it to. I did not read that seat's report or scratch tree.
- LEAF discipline: no subagents, no git mutation (no commit/push/index
  change). One tracked file was touched and restored: the fixture
  `__pycache__/measure_audio.cpython-314.pyc` was re-dirtied by my first
  importlib harness and restored to exact HEAD bytes; every later harness
  ran with `sys.dont_write_bytecode = True`. `git status` tracked-clean at
  the end of the review.
