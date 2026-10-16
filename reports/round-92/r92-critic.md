# r92 critic — attack on the committed filter-chain DSP lattice (`ccbce758`)

Seat: **critic** (leaf). Repo `/home/vgpnk/Projects/shokunin/audio-shokunin`.
Target: the r92 landing **`ccbce758`** — *"r92 author: filter-chain DSP lattice
(4 entries/80 legs, +2328/−3)"* — file `corpus/fixtures/measure_audio.py`
(`--probe-filterchain-r92`, four entries). Frozen source =
`git show ccbce758:corpus/fixtures/measure_audio.py` sha256
`4e5fe3e673d8cb586523f3d5462e915c3db255ce4ba0013c5f7157756096ca90`; family block
(lines 39176–41470, 2295 lines) sha256
`a1b418be71203602eb012084a4e9b12080265cbedd0264babfd6f41b0f992291`.
Receipts re-read from the author worktree
`~/Projects/shokunin/audio-shokunin-wt-r92` (`…094024556467Z` run A,
`…094602455160Z` run B, `…093301592620Z` pre-fix) — all three sha256 **match**
the author's `RECEIPTS.md` claims (`d167cdc5…`, `01465b5a…`, `13eff464…`).
Host `plazir27`; PipeWire **1.6.8** and the SPA/LV2/LADSPA inventories re-read
**read-only** live (they still match the boundary's this-host pins).

**Seat discipline.** No tracked write except this report (untracked, **not
committed**); no `pactl set-default-*`; **no live probe battery was run** — the
evidence below is *re-derivation* (committed arms × committed receipts), a
mutation battery, numerical re-simulation **from the author's own captured
bytes** using the fixture's own analyzers, and bounded read-only host checks.
Rationale: sibling lanes were live for the whole window (HEAD advanced
`7358f13b` → `b8ff4efc`; `wt-r96…r100` present), the family lock is
*tree-relative*, and a new filter-chain probe would add nodes to the shared
daemon for a mechanism that is decidable from the captured bytes. Archive:
**`/home/vgpnk/r92-critic/`** (`evidence/*.json`, `scratch/*.py`,
`MANIFEST.shas.txt`).

**Verdict: PASS-with-findings on the encoding — the family's green is
reproducible from its own receipts (8/8 arm replays clean, no pid binding, no
reconstructed inputs) — and FAIL on two mechanism claims the report states as
fact (F1a, F1b), plus two small fail-open/arm defects (F3, F4) and one
documentation drift (F5).** No law in the family is falsified by this gate;
the falsified-cell *values* are right, their *explanations* are not.

---

## 0. Method (what was actually executed)

| check | artifact |
|---|---|
| custody + splice + symbol census + guard census (static, committed bytes) | `scratch/static_checks.py` → `evidence/static.json` |
| **arm replay** — the four committed entry functions, verbatim, with only their *measurement layer* stubbed from each receipt's own recorded legs | `scratch/replay.py` → `evidence/arm-replay.json` |
| **mutation battery** — 191 mutations, each declaring its designed outcome | `scratch/mutate.py` → `evidence/mutations.json` |
| **whole-leg vacuity sweep** — every recorded top-level leg key deleted, one at a time (81 keys) | `scratch/sweep_probe.py` → `evidence/sweep-and-probes.json` |
| **falsified-cell re-checks** — `d_qneg`, `d_lp@20k`, the convolver silent class, re-derived with the fixture's own `_fc92_dft`/`_fc92_best_window`/`_fc92_rbj` | `scratch/falsified_cells.py`, `scratch/lowpass_cell.py` → `evidence/falsified-cells.json`, `evidence/lowpass-cell.json`, `evidence/dqneg-scale.json` |
| residual-law probes (IR shifted ±1/+2, IR ×0.9, degenerate captures) | `scratch/sweep_probe.py` |
| bounded **read-only** host corroboration (`ls`, `strings`, `pactl info`, `pw-cli info 0`) | `evidence/final-verify.json` §host |

No object was created, loaded, linked or destroyed by this seat.

---

## 1. Custody, splice and wiring — verified, no finding

- committed sha == the integrate note's claim; worktree sha == the author's
  claim; `+2328/−3` in **6 hunks** (2295-line block + 2-line argparse row +
  28-line dispatch + 3 replaced wiring lines).
- **the 3 deleted lines are exactly** the mutex sum (137 → 138 tokens), the
  `mode` ternary and the `suffix` ternary; each **adds**
  `args.probe_filterchain_r92` and **removes nothing** (token multisets
  diffed programmatically) → no family token was lost by the splice.
- **78 block symbols, 0 collisions** with the rest of the committed file;
  each of the four entry names is defined **1×** in the block and referenced
  **2×** outside (dispatch + `measurements[...]` key).
- guards: 4 `subprocess.Popen`, all with `start_new_session=True` **and**
  `preexec_fn=_pwctl_r86_no_core`; 5 `_alsapw_r84_killpg` sites; the lock is
  the **fixed** `corpus/live/measure_audio-filterchain-r92.lock` (0 uses of
  `$TMPDIR`), taken **before** the first entry and held; the r92 dispatch sits
  before `--probe-pactlmon-r85`; the r79 filter-chain entry is dispatched under
  a **different** flag (`--probe-capture-r79`) → no routing collision.
- the only `set-default` occurrence inside the block is the comment saying it
  is never called; the block's unload path is name-verified (`sink_name=`).

## 2. Arm replay — 8/8 clean

The four entry functions were exec'd from the committed bytes with
`_fc92_entry_head`/`_fc92_ctx`/`_fc92_teardown`/the leg producers replaced by
the receipt's own recorded legs (and the read-only inventory re-derived from a
fixture tree built out of the receipt's recorded values). The verdict code is
untouched committed code.

| run | arm | dsp | ir | wpx |
|---|---|---|---|---|
| A `…094024556467Z` | 0 failures | 0 | 0 | 0 |
| B `…094602455160Z` | 0 failures | 0 | 0 | 0 |
| pre `…093301592620Z` | **1 RED** (`a_ladspa` class) | **CRASH** | GREEN | GREEN |

**No pid binding, no reconstructed arm input**: every leg the arms read is in
the receipt. The pre-fix receipt cannot masquerade as green under the final
arms — the dsp entry **aborts loudly** on the added `d_gneg140` leg (the fix's
new witness is load-bearing), and the arm entry still catches the one pre-fix
*data* signature (`a_ladspa` recorded as `fc92_type_missing`). The pre-fix
`i_441` red is *accepted* by the final arm by design (modulo-1024 law, see T1).

## 3. Mutation battery — 191 mutations

| designed → got | n | meaning |
|---|---|---|
| RED → RED | 140 | the arm fires on the perturbed evidence |
| CRASH → CRASH | 8 | loud (`KeyError`/`ValueError`), never a silent pass |
| GREEN → GREEN | 20 | volatile controls + declared weakness witnesses |
| CB → CB | 8 | the contention class is reachable and named |
| RED → GREEN | 8 | **by-design tolerance/dead cell** (listed below) |
| RED → CRASH | 1 | `d_qneg.gain_db` deleted → `ValueError: max() empty` (loud, acceptable) |
| CRASH → RED | 1 | `a_lifetime.live_shape` deleted → RED (better than loud) |

The eight RED→GREEN rows are the *disclosed* tolerance map, not holes:
`d_gnegx` at 12 kHz off by 0.3 dB (band = 1.0 dB); `i_d100` shift 99 and
`i_441` peak_delta 111 (`tol=2`); the five delay legs off by 1 sample
(`tol=2`). **Whole-leg sweep: 77/77 data-channel legs are load-bearing — a
deleted leg CRASHes the entry, never a silent pass.** (The four inventory legs
`v_spa`/`v_ladspa`/`v_lv2`/`v_kemar` are computed *inline* from the filesystem,
so my leg-channel mutation cannot reach them; that GREEN is a harness artifact
and is disclosed as such. Their arms are fail-closed by code read.)

Residual-law probes (with the fixture's own `_fc92_residual`): baseline
0.5 LSB / 0 samples > 1 LSB; IR shifted **±1 sample** → 16383.5 LSB; IR ×0.9 →
3277.9 LSB; 64-sample capture → `alignment_error`; quarter-length capture →
16383.5 LSB (no fake 0.0 from a degenerate edge overlap — the guard the author
added in dev holds).

---

## 4. Falsified-cell re-checks

### 4.1 `Q=-1` — the recorded "broadband ~+19 dB gain" is a **clip ceiling** (F1a)

Evidence chain (all from the author's own bytes, re-derived with the fixture's
own analyzers):

1. receipt, run A **and** run B: `d_qneg.analysis.out_stats.max_abs == 1.0`
   (`nz_exact` 68018 / 64093) — the leg's output is **saturated**; the
   stimulus peaks at 0.1596. My own read of
   `scratch/run2/d_qneg_0_out.wav`: **3844 samples at ±1.0**.
2. re-simulation: `clip(10·x)` followed by the capture's own s16 conversion
   (`round(x·32768)`) reproduces the recorded vector **exactly** —
   19.015 / 18.979 / 19.289 / **18.729** / 19.289 (receipt: … 18.729 …);
   `clip(30·x)` moves it by ≤ 3 dB; `3·x` (unclipped) reads exactly
   **+9.542 dB = 20·log10(3)**, i.e. the analyzer is honest below the clip.
3. therefore the recorded numbers are the **clip transfer function**, not a
   filter response. The arm's "flat within 2 dB" shape check is satisfied by
   *any* flat response above the clip threshold: **the leg cannot see the
   magnitude** (a flat +20 dB and a flat +40 dB are indistinguishable — both
   read ≈ +19 dB). A *frequency-shaped* wrong response is still caught
   (sims: 12 kHz ×30 → 11.95 dB spread; 200 Hz ×0.5 → 26.9 dB; the analytic
   `q=-1` RBJ curve → 19.99 dB spread ⇒ RED).
4. **the falsification itself stands** — the boundary's "`Q=-1` ≡ `Q=0.707`" is
   false on this host (a flat ≥ +16 dB response is not the 0.707 curve, and
   the shape arm would fire on the 0.707 curve).
5. **mechanism (this seat's contribution, hypothesis + numeric witness).** RBJ
   peaking with `q → 0+` degenerates to a **constant `A² = +20 dB`** gain: the
   analytic family is flat to 0.001 dB for `q ≤ 1e-4` and to 0.137 dB at
   `q = 1e-3` (`evidence/falsified-cells.json` §exp3). That is the only simple
   mechanism consistent with *both* the measured flatness and the ≥ +16 dB
   floor, and it is testable in **one leg**: `Q=+1e-6` should read the same
   flat +20 dB as `Q=-1`. The report's *"the mechanism is recorded, not
   explained"* should be replaced by this hypothesis plus that one leg.

### 4.2 the lowpass at 20 kHz — the stated **float32 mechanism is falsified** (F1b)

The report (§4.4) states: *"the lowpass numerator cancels catastrophically in
float32"*. Direct tests on the author's own captured stimulus:

| model | 20 kHz |
|---|---|
| analytic RBJ, float64 | **−70.217 dB** (the reference value) |
| **float32 coefficients + float32 state** (the module's presumed arithmetic) | **−70.217 dB** (identical to 6 decimals) |
| float64 filter + s16 capture `round(x·32767)` | −70.868 dB |
| float64 filter + s16 capture `round(x·32768)` | **−71.437 dB — the recorded value, exactly** |
| s16 truncate/floor variants | −68.889 … −69.057 dB |
| receipt, run A **and** run B | **−71.437 dB** |

The cancellation factor at 20 kHz is ~4× (not catastrophic) and float32's
6e-8 relative precision bounds the error at ~1e-6 dB — **the stated mechanism
is quantitatively impossible and empirically absent**. The real mechanism is
the **s16 capture floor**: the output's 20 kHz component is
**0.35–0.40 LSB** (ref magnitude 0.03999786 → analytic 1.2336e-5 = 0.404 LSB;
recorded out magnitude 1.072e-5 = 0.351 LSB), so the reading is a
*deterministic* property of the capture conversion — which is why it is
identical to 3 decimals in both green runs, and why my `round(x·32768)` model
reproduces it exactly. The s16 scale is the model's last degree of freedom —
the fixture's own writer multiplies by **32767** while the capture path
multiplies by **32768** — and only the ×32768 variant lands on the receipt
(×32767 reads −70.868 dB here, 0.57 dB off; in the clip leg of §4.1 the same
choice is worth 0.001 dB).

**The decision (record, never arm, the 20 kHz cell) is right; the reason is
wrong, and a wrong reason is load-bearing**: *"float32 artifact"* would excuse
a genuine HF regression as arithmetic noise. The fix is already in the file:
`_fc92_audio_leg(..., fmt=…)` / `_fc92_audio_attempt(fmt=…)` implement an
**f32 capture path that no leg ever uses** (`fmt="f32"` occurs **0 times** in
the family) — with an f32 capture the 0.4-LSB floor disappears and the cell
becomes armable at the same 0.06 dB tolerance.

### 4.3 convolver silent-at-load / loud-at-activation — armed, but confounded (F4)

Both halves *are* armed: `a_load_noconfig`/`a_load_missing`/`a_load_dbg5`
require `loaded` **and** `E=0`/`W=0` (recorded 0/0 at 1324/1059/12497 lines);
the five `i_*` silent legs require `out_nz_exact == 0` **and** their activation
class (`fc92_convolver_cfg` / `fc92_convolver_file`), with `err_lines` coming
from `convolver_instantiate` / `read_closest` / `impl_activate` /
`stream_set_state` only. Two defects:

- **confound**: the load half is measured on a *driverless* load (no sink, no
  feed link) and the activation half on a *driven* one. The two leg sets differ
  in more than time — the `[E]` lines come from `impl_activate`, which
  *requires* a driver. The report's *"the same legs emit at graph start"* is not
  what the evidence shows.
- **unarmed claim half**: on the five `i_*` silent legs the *load reply*
  (`load.load_text`) is recorded but **no arm reads it**. Mutation confirms it:
  strip it, or put an `[E]`/`failed file` line in it → the entry stays GREEN.
  The "silent at LOAD … diagnosable only at ACTIVATION" split is therefore
  armed on two *different configurations*, not within one leg.

## 5. Dead-entry shapes and fail-open fields

- **F3 — `d_fhi` is fail-open.** The "`Freq` above Nyquist is a pass-through"
  law reads `any(abs(v) > 0.05 for v in gains("d_fhi").values())`. If the leg's
  `gain_db` is absent, `gains()` is `{}` and `any(())` is `False` → **GREEN**.
  Verified by mutation: delete `gain_db` (or set `{}`) → GREEN; set one probe →
  RED. `d_copy` is protected by its `len != 5` clause; every other dsp row
  checks `is None` explicitly. This is the r89-F4 class in a new place.
- **F4b — `a_ports_none.feed_link` is fail-open** (`rc == 0 → fail`; absent
  passes) while `a_ports_sink.feed_link` is fail-closed (`rc != 0 → fail`).
  Verified by mutation: stripping the witness from `a_ports_none` leaves the
  entry GREEN; stripping it from `a_ports_sink` REDs. The *unfeedable* class is
  exactly the one whose witness is optional.
- `fc92_load_refused` is **unexercised in all three receipts** (recursive
  census over every `error_class` field): the generic refusal is always
  shadowed by a specific class. A fallback row, not a defect — but note the
  r92 table resolves by **table order** while the inherited r88 chain resolves
  by **latest match position**; the author's fix #2 (specific LADSPA line
  first) is consistent inside r92 and disclosed in the code comment.
- the four inventory legs are computed inline (not leg-channel data), so their
  arms cannot be reached by a receipt mutation — a shape worth knowing when
  reading the "81 legs" claim.

## 6. Tradeoffs the judge must weigh (not defects)

- **T1 — the delay/tap alias window.** `_fc92_shift_ok(delta, want)` accepts
  `want + k·1024 ± 2` for `|k| ≤ 4`: a ±2-sample tolerance **and** a ±4096-
  sample alias window. Justified by measured block-quantised PRE/POST jitter
  (author §4.5-6) and the recorded residues *are* exact (48/480/2400/2431),
  but a 1–2 sample or ±1024-sample delay regression is invisible — and the
  pre-fix `i_441` reading (1134 = 1024+110) is *accepted* by the final arm.
  This is host accommodation, not a law relaxation; the report's word
  *"exactly `round(s·rate)`"* overstates the arm.
- **T2 — min-side clamp bands.** `d_gnegx` at 1.0 dB (deep-attenuation
  instrument spread, disclosed) and `d_gneg140` at 1.5 dB around −46.362 with a
  5 dB exclusion around −66.4. Both deliberate; the −140 leg's 20 dB
  separation remains the decisive witness.
- **T3 — host-pinned inventories.** `v_spa`'s exact count 6, LADSPA dirs
  absent, LV2 zero `.so`, the unshipped `hrir_kemar` path — this-host boundary
  survivals armed as laws. Correct per the round's convention; a package
  update turns the family red for a non-module reason (today they still hold:
  re-read live, 6 plugins, 0 `.so`, both LADSPA dirs absent, PW 1.6.8).

## 7. Documentation drift (F5)

- **legs**: the commit and the report say **80**; both green receipts record
  **81** top-level keys (26 + 20 + **18** + 17 — `i_residual` is a leg key, not
  only a sub-block). Same class as r89's 47-vs-52.
- the report's headline writes `failures: {}`; the receipts carry `[]` in all
  four entries.
- "exactly `round(s·rate)` samples" vs the ±2 arm (T1).

## 8. Impacted axes and the smallest safe corrections

**Impacted axes** (externally visible, stable for this round):
**(1) arm fidelity** — does each arm measure the claim it names (F1a, F1b, F3,
F4b); **(2) evidence integrity of the falsified cells** — is the recorded
number the response or the instrument (F1a, F1b); **(3) fail-open surface** —
absent-is-fine fields (F3, F4b); **(4) provenance accuracy of mechanism
claims** (F1a, F1b, F5); **(5) host-pin exposure** (T3).

Smallest safe corrections, none of which changes a law and none of which needs
a re-measure to be *stated*:

1. **F1a** — replace §3.1's *"a broadband gain … the mechanism is recorded,
   not explained"* with: *the recorded vector is the clip ceiling of a flat
   ≥ +16 dB response; the numbers are not the transfer function; the flat
   `A² = +20 dB` limit of RBJ-peaking as `q → 0+` is the hypothesis*, and add
   the one-leg test (`Q=+1e-6` vs `Q=-1`, or a −26 dB stimulus).
2. **F1b** — replace §4.4's float32 sentence with the s16 capture-floor
   mechanism (reproducer above), or demote it to a hypothesis; keep the cell
   recorded-not-armed.
3. **F3** — one line: `if len(gains("d_fhi")) != 5 or any(abs(v) > 0.05 …)`.
4. **F4b** — make the unfeedable witness explicit:
   `(l.get("feed_link") or {}).get("rc") is None → fail`.
5. **F4a** — arm `load.load_text` on the five `i_*` silent legs (no `[E]`, no
   `failed file`), and/or require every `err_lines` entry to match an
   activation pattern — both derivable from *existing* receipt fields.
6. **F5** — 81 legs / `[]` in the report and the commit message.
7. *Optional, author move*: pass the already-implemented `fmt="f32"` for the
   deep-attenuation legs, then arm the 20 kHz cell at 0.06 dB (this also
   exercises the currently dead f32 branch).

**Nothing here is a shipping decision, and nothing here requires rejecting the
landing.** What must not be admitted as-is: the two *mechanism sentences*
(F1a/F1b) as explanations, and any reading of the F3/F4 arms as covering the
claims they name.

*Leaf seat — attacked the approach and the bytes; did not judge, admit, edit,
integrate or ship.*
