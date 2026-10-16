# r84 REVIEWER — wave-B gate on committed `fbe65713`

**Seat: REVIEWER (executor-class, leaf, frozen `probeParent`).** Lane
`/home/vgpnk/Projects/shokunin/audio-shokunin`. Scope **only** the r84
landing — `git show fbe65713 -- corpus/fixtures/measure_audio.py`
(**+2796/−3**, committed blob `bc3e0d3381b8af4914f6978c87951d52931463c9`,
sha256 `8ed09d19990480fd337cba99e45cb0588e0615fd90e34793ecc4841c21368e4e`,
22 725 lines) plus the two committed receipts. Everything below was
measured against a **pinned copy of the committed blob**
(`corpus/live/r84-reviewer/measure_audio_fbe65713.py`, extracted with
`git show`, `git hash-object` == the committed blob, and the working-tree
file is byte-identical to it — `git status --porcelain
corpus/fixtures/measure_audio.py` is empty). **Zero tracked writes, no
commits, no `set-default-*`, no foreign object touched.** The frozen
`probeParent` seat dispatched **no** labrat: the review's arithmetic is
re-derived independently in `r84r_audit.py` (110 checks, see §3) and the
behavioural re-run is executed in-seat (§4) rather than delegated.

---

## 0. Verdict

**PASS with findings.** The r84 family is insertion-only, correctly
wired, and its 6 entries / **147 legs** reproduce **0 failures** in both
committed receipts; every pinned constant I re-derived independently from
the receipt data reproduces **exactly** (`x0.125`/`x3.375`/`x0.015625`,
the index-addressed `25%` pin, sticky `30% → 221 = 8192·0.3³`, the
refusal taxonomy, the 44-byte index refusals, the mid-run post-gain
`x0.125` tap visibility), the four author refinements are encoded where
they matter, teardown is name-verified and clean, and **my own run of the
pinned blob on this host reproduces the committed leaves with 0
non-volatile diffs across all 147 legs and `failures: {}`** (§4). The
findings do not change the verdict; the sharpest one is not in the
fixture's audio arithmetic but in its **co-tenancy guard**: the
same-family lock is **TMPDIR-scoped**, so it does not exclude a sibling
`--probe-alsapw-r84` that runs with its own TMPDIR — observed live at my
entry, with both sibling runs recording cross-credited failures (and the
same seats running green once they shared a TMPDIR).

---

## 1. Findings, ranked

### F1 (medium) — the family lock is TMPDIR-scoped: it does **not** exclude same-family runs, and the cross-credit it exists to prevent is observable

`_alsapw_r84_family_lock()` (`measure_audio.py:19840-19857`) takes an
`flock` on `Path(tempfile.gettempdir()) / "measure_audio-alsapw-r84.lock"`
(`:19845`) — i.e. **inside `$TMPDIR`**. Its own docstring/comment claims
"Same-family exclusion — two concurrent r84 runs would cross-credit the
monitor taps … and corrupt the /proc RUNNING witness, so a second
`--probe-alsapw-r84` waits HERE" (`:19841-19844`). Two seats with
different `TMPDIR` values therefore take **different lock files** and
never contend.

Observed live at my entry (`corpus/live/r84-reviewer/cotenancy-at-entry.txt`):

| seat | pid | TMPDIR | lock file | window |
|---|---|---|---|---|
| `r84-verifier` (r84v1) | 1682245 | `…/shokunin/tmp` | `…/tmp/measure_audio-alsapw-r84.lock` (`pid=1682245`) | 00:40:28 → 00:45:16 |
| `r84-critic` (replay-run1) | 1685102 | `…/shokunin/tmp/r84critic-tmp` | `…/r84critic-tmp/measure_audio-alsapw-r84.lock` (`pid=1685102`) | 00:40:38 → 00:45:17 |

Both ran concurrently for the whole window, each with its own
`r84a_ns_<pid>` null sink and `speaker-test -D pipewire:NODE=r84a_ns_<pid>`
node (`ps` capture in the receipt). **Both runs' own stdout shows the
predicted cross-credit:**

- critic: `a_front: rc=0 class=None nodes=['r84a_1682245_hold'] — neither
  adaptive arm`; `a_iec958_d0: rc=0 … nodes=['alsa_playback.aplay',
  'r84a_ns_1682245']` — the **verifier's** objects appearing in the
  critic's `nodes_mid` (the dev-lattice verdict classifies `new_node_names`
  as own-node evidence, so a foreign node flips the arm);
- verifier: `a_plughw00: rc=0 … nodes=['alsa_playback.aplay']`,
  `st_hw00_c1: rc=1 class=None` (unattributable `alsa_playback.aplay`
  could be its own lingering node **or** the critic's), and
  `pw_server: rc=-9` (killed at the 8 s bound instead of the `Host is
  down` refusal — a load/co-tenancy artifact).

Impact: the author's own receipts are unaffected (run1/run2 were
serialized by the author: the two canon stamps are 5 min apart and each
run was single-tenant), but the **wave-B evidence chain is not safe under
co-tenancy** — verifier and critic ran simultaneously and both produced
false failures from foreign nodes.

The same session provides the **positive control** for the lock's
mechanism: when the next wave of seats *did* share `TMPDIR`, the lock
serialized them correctly and the results were green —
`r84-verifier` r84v2 (00:45:41→00:50:21, `rc=0`, single-tenant at its
window) and `r84-critic` replay-run2 (started 00:50:2x, `failures: {}`,
receipt stamp `20261016T005500150290Z`) both ran behind
`…/shokunin/tmp/measure_audio-alsapw-r84.lock`; this reviewer's own run
waited in `locks_lock_inode_wait` for 8 m 46 s behind them
(`ps -o stat,wchan` captured in `runs/r84r1.window.txt`) and then ran
green (§4). So the guard works exactly when every seat agrees on
`TMPDIR` — which is a convention, not a guarantee.
Note also that `_alsapw_r84_pcm_states` (`:19043`) feeds the ebusy arm
from `/proc/asound` **host-wide**, and the `-D null` census / default-sink
fallback legs are shared-surface: those are exactly the arms a concurrent
sibling perturbs.
Fix options: anchor the lock outside `$TMPDIR` (a fixed lane path, e.g.
`corpus/tmp/`), or make a foreign `r84a_*` object a **hard precondition**
(abort/block, never "record and continue").

### F2 (medium-low) — the sticky respawn pin is read over a mixed pre/post-repair window and passes on a one-sample margin

`_alsapw_r84_sticky_leg` writes the repair **2.0 s** after the respawn
(`:21372-21374`) and then computes the pin as
`respawn_tap_med = _alsapw_r84_amp_med(ser, 0.8, 3.2)` (`:21387`), i.e.
the median over a window that **contains both** the 221-level respawn and
the 8192-level repaired tail. Both committed receipts show the tail
flipping inside the window: `[[2.1, 221], [2.2, 8191], …]` (run1) /
`[[2.0, 221], [2.1, 8191], …]` (run2). The median is 221 only because
**14 of the 25** 0.1 s samples are pre-repair (13 would still be 221;
**12 flips the median to 8192 → the `150 ≤ med ≤ 340` gate reports a
failure of correct behaviour**). The margin is ~0.2 s of scheduling on a
host whose loadavg was 53–59 during the author's runs.
Fix: measure the pin on the pre-repair span only (`0.8 ≤ t ≤ 1.9`), and
keep the repaired tail as the separate `repaired_percent` check it
already is.

### F3 (low) — the gain-law envelopes are wider than the measured law (r83-F2 pattern)

`ALSAPW_R84_VOL_ENV` (`:18977-18980`) vs the exact measured ratios
(reproduced in both receipts, and re-derived by me from the raw `series`):

| law | gate | exact | slack (low/high) |
|---|---|---|---|
| `x0.125` | 0.105–0.150 | 0.125 | −16 % / +20 % |
| `x3.375` | 3.00–3.80 | 3.375 | −11 % / +12.6 % |
| `x0.015625` | 0.010–0.024 | 0.015625 | −36 % / +53.6 % |

The index-addressed pin is the loosest: a regression to 0.010 (a 25 % pin
that under-attenuates by 36 %) or to 0.024 would still pass. The measured
value is exactly `8192·0.25³ = 128` in both runs, so the gate is not
covering a measured jitter — it is just wide. This is much tighter than
r83's 2–4× envelopes, so it is recorded as low, not as a repeat.

### F4 (low) — report-vs-receipt claim hygiene (6 items, no verdict impact)

`reports/round-84/r84-author.md`:

1. "`failures: {}` across all six entries" — the receipt stores
   `failures: []` (an empty **list**), not a dict.
2. "`coverage_blocked: null`" — the key is **absent** from both receipts
   (it is only emitted when non-empty, `:19885`/`:19911`). "no coverage
   blocks" is the accurate form.
3. "Green receipts (identical final bytes, two runs)" — the two files are
   **not** byte-identical (sha256 `e8d463c2…` vs `283f69e8…`). They agree
   on every non-volatile leaf (my 110-check audit); the only differences
   are pids/indices/spa buffer geometry (`pulse.attr.*`,
   `node.driver-id`) and the sticky tail's 0.1 s timestamp shift.
4. "classifier unit table (22 named classes + 6 must-classify-nothing
   inputs)" — the receipt has **23** positive unit cases (18 distinct
   classes) and **5** negative cases (28 unit legs + 5 live legs = the 33
   legs of `alsapw_negctl_r84_probe`).
5. "family lock file removed after runs" — `_alsapw_r84_family_lock`
   never unlinks the file (no `os.unlink` anywhere in the r84 block), and
   the file is present on the host now (rewritten by a later sibling run).
   A manual removal is possible but is not receipt-backed; a stale lock
   file is harmless (advisory `flock` on a re-used path).
6. "sinks_gone all true" — true for the 4 entries that load a null sink;
   `alsapw_dev_lattice_r84_probe` and `alsapw_negctl_r84_probe` emit **no**
   `sinks_gone`/`own_nodes_after` key at all (they load none), so "all
   true" describes 4 of 6 entries.

### F5 (low) — the tap legs' recorded `stream_input` leaf is a pre-route read

Author refinement #2 says "reads must wait for routing … gates all percent
reads/writes". The **verdicts** are gated (the monstream/sticky entries
use `_alsapw_r84_wait_attached`, and the si-write arms assert
`pre_percent == 100` before scoring). But `_alsapw_r84_tap_leg`
(`:19686-19692`) records the leaf from `_alsapw_r84_wait_stream`
(appearance, **not** attachment), so the **six** volume tap legs of
`alsapw_pactl_write_r84_probe` (`vol_50_0`, `vol_50_1`, `vol_150`,
`vol_25_idx`, `src_vol50_0`, `src_vol50_1` — in both committed receipts
*and* in my fresh run) carry `stream_input.sink = 4294967295`,
`volume = 0%`, `corked = true`. It is record-only (nothing scores it),
but a reader can mistake it for the leg's pre-state, which is precisely
the trap the refinement documents.

### F6 (low) — refinement #1's counterexample is prose-only (no receipt leg)

The sticky leg's note asserts the name-scoping law ("same-tag respawn 30 %,
different-tag respawn 100 % measured"), but the leg only ever respawns
under the **same** tag (`:21335-21396`). The different-tag half — the part
that makes the law *name-scoped* rather than role-scoped — has no leg in
either receipt, so it is an author assertion, not a re-checkable datum.
A two-line counterexample leg (same role key, different `node.name`)
would close it.

### F7 (informational) — host state at entry, and the disclosed foreign sink

- Foreign `r84a_probe_548706` null sink (module `536870923`, index 220907,
  SUSPENDED) is present at my entry and still present after the sibling
  runs; it is **not** the author's (their names are `r84a_ns_*` /
  `r84a_ns2_*` / `r84a_<pid>_*`), and the author disclosed it. It is the
  only `r84a_`-prefixed object the family's `own_nodes_after` filter
  (`ALSAPW_R84_PREFIX in n`, `:19901`) cannot attribute.
- The author's `TMPDIR` scratch dirs are gone (`r84a-dev-*`,
  `r84a-pactl-*`, `r84a-props-*` all absent); the surviving `r84a-mon-*`
  dir belongs to the live sibling runs.
- Default sink/source were `…SPDIF__sink`/`…Line__source` before and
  after every seat's activity; no seat changed them.

---

## 2. Static review of the landing

- **Insertion-only, prior families untouched.** `git show --numstat`:
  `+2796/−3` for `corpus/fixtures/measure_audio.py`; the diff has exactly
  six hunks — the r84 block, one `add_argument("--probe-alsapw-r84")`
  (`:21703`), the mutex-sum append (`:21711`), the `main()` dispatch
  branch (`:22035-22068`), the mode ternary (`:22695`) and the suffix
  ternary (`:22715`) — i.e. the author's "3 modified wiring lines"
  convention (plus the one added argument line) holds exactly, and the
  r82/r83 families' code is byte-unchanged.
- **Family-local classifier.** `_ALSAPW_R84_ERR_CLASSES` (`:18982-19018`)
  is checked by `_alsapw_r84_errclass` **before** the shared table
  (`:19020-19027`) and is never prepended to `_CAPTURE_ERR_CLASSES`; the
  single capture-refusal class is encoded as one regex with both markers
  (`Unable to install hw params|TICK_TIME: \[0 0\]`), and the negctl unit
  table proves both slices map to that one class — the boundary's
  falsification is folded, not re-litigated.
- **Guardrails inherited.** Seat-owned `r84a_<pid>`/`r84arole<pid>` names
  only; every module unload goes through `_gst_r81_unload_own`
  (name-verified index, `recycled` recorded); no `set-default-*` anywhere
  in the receipt text (grep over the whole 367 KB JSON); the restore key
  is the private `r84arole<pid>`, reset+verified at entry
  (`role_reset.reset_ok == true` in both write entries) and repaired at
  exit (`reset_sink_end == [0,0,0,0]`, sticky `repaired_percent == 100`,
  `repaired_mute == false`).
- **No vacuous legs.** I mapped every receipt leg name back into its
  entry's verdict region: all 147 legs are either named directly or
  covered by the `f"{name}"` loops (`susp_live_{rep}`, `monA_sivol_{rep}`,
  `r_pw_node_src_{rep}`, `pw_node_pin_{rep}`); the only non-armed legs are
  the three **witnesses** the report already labels as such
  (`ebusy_hold`, `hold_exit`, `ebusy_postkill` — "recorded here, never
  armed").
- **The four author refinements, checked one by one.**
  1. *name-scoped restore* — the sticky leg respawns under the **same**
     `node.name`/`application.name` tag (`:21335-21396`), and the role key
     is private; the different-tag counterexample is prose-only (F6);
  2. *routed-leaf gating* — `_alsapw_r84_wait_attached` (`:19280-19312`)
     is used by the sticky and parec legs, and the si-write arms assert
     `pre_percent == 100` before scoring (`:21269-21273`); the tap legs'
     *recorded* leaf is the pre-route read (F5);
  3. *parec-only donor* — `need_so` spawns a second `parec -d
     <ns>.monitor …--file-format=wav` and waits for the source-output by
     child pid (`:19746-19761`), with the pw-record refusal recorded in
     the comment;
  4. *per-leg pre-reset* — `_alsapw_r84_tap_leg` resets sink volume/mute
     and source volume/mute **before** every stream spawn
     (`:19671-19685`), and the entry additionally resets at head/tail
     (`:20762-20768`, `:21024-21029`; `reset_sink_end == [0,0,0,0]`).
- **Adaptive arms are explicit.** The dev-lattice free/held arms
  (`:20178-20197`) accept exactly two shapes and fail otherwise; the
  ebusy witness pairs rc/class with the `/proc` RUNNING state; the
  negctl live controls plus the mid-run SIGKILL discriminator pin
  killed-vs-refused (`ctl_sigkill`: `signal == SIGKILL`, `error_class ==
  null`).

## 3. Independent re-derivation (`corpus/live/r84-reviewer/r84r_audit.py`, 110 checks, 0 failed)

- receipt provenance: run1/run2 are byte-identical to their canon run-dir
  copies (`e8d463c2…`, `283f69e8…`);
- census: 6 entries / 147 legs in both runs, `failures == []` in all six,
  no `coverage_blocked` emitted, `sinks_gone` all true and
  `own_nodes_after == []` for the 4 sink-loading entries, unloads
  name-verified (`verified_index == captured`, rc 0, not recycled);
- every leg tag is `r84a_<one pid>_*`;
- **gain laws re-derived from the raw `series` with my own median** (not
  the fixture's): `vol_50_0/1`, `src_vol50_0/1` → 0.125; `vol_150` →
  3.375; `vol_25_idx` → 0.015625; `monA_sivol_0/1` → 0.125 with
  `pre_percent == 100`; `monA_simute` 8192/0/8192; `vol_0_100`
  8192/0/8192; `vol_frac` 33095 (`= 65536·0.505`), `vol_raw` 75020
  (`= 65536·1.5^⅓`);
- sticky: `8192·0.3³ = 221.184 → 221`, respawn 30 %, repair 100 %,
  unmuted;
- refusals: 10 pactl classes rc=1 with the expected class and **no
  signal**; `mon_bad0`/`mon_deadidx` rc=1 `pa_stream_noent` + 44-byte
  header-only WAV; `mon_soidx` rc=0 44-byte empty-accept;
- run1 vs run2 agree on **every** non-volatile, pid-normalized leaf
  (0 diffs) once the enumerated non-gated witnesses are excluded
  (sticky tail timestamps, sig-window amplitudes at a routing
  transition, spa buffer geometry, `node.driver-id`, one 0.1 s series
  sample);
- classifier coverage: **every** error class observed live in either
  receipt is one of the 18 classes the negctl unit table asserts
  (nothing in the run is unclassified), and only `alsa_open_enodev`
  appears in the table without a live producer in this round (it is the
  boundary's `No such device` tail class).

## 4. Behavioural re-run of the pinned blob (this host, this session)

One full `--probe-alsapw-r84` run of the **pinned committed blob**, from a
mirrored tree (`tree/corpus/fixtures/`, with the committed
`build_artifacts.py` — `main()` invokes it unconditionally at `:21723`, so
a tree without it aborts with `CalledProcessError` before any leg runs;
that is how the reviewer's first attempt failed, and it is worth knowing
for future seat copies). `TMPDIR=~/Projects/shokunin/tmp` (the lane's, so
the family lock applies). Window: lock wait from `00:46:14`, legs
`~00:55:00 → 00:59:40`, `loadavg` 50.4 → 85.3 (loaded host, the task's
"load preferred"), single-tenant for the whole leg window.

```
rc=0
{"receipt": "…/r84-reviewer/tree/corpus/live/runs/20261016T005939937850Z-alsapw-r84/measurements.json",
 "failures": {}}
```

- **6 entries / 147 legs, `failures: []` in all six**, `sinks_gone` all
  true, `own_nodes_after == []`, unloads name-verified
  (`verified_index == captured`, rc 0) — identical structure to the
  committed receipts.
- **`r84r_compare.py` vs committed run1: 0 non-volatile leaf diffs across
  all 147 legs** (same volatile normalization as the audit). The pinned
  constants reproduce: `vol_50_{0,1}`/`src_vol50_{0,1}` 8192→1024
  (0.125), `vol_150` 8192→27648 (3.375), `vol_25_idx` 8192→128
  (0.015625, sink-index addressed), `vol_0_100`/`mute_cycle` 0 → 8192,
  `monA_sivol_{0,1}` pre=100 % → 1024 (0.125, mid-run post-gain),
  `monA_simute` 0 → 8192, `monA_nowrite` 8192 → 8192, sticky respawn
  30 % / tap median **221** / repair 100 % unmuted, `r_null` 668 nz
  rows + 25 bursts + peak 32643 (boundary's 668/32508), `ctl_sigkill`
  `SIGKILL` with `error_class: null`, `role_reset.reset_ok: true`.
- **The sticky window is mixed in this run too**: tail
  `[[2.1, 221], [2.2, 8192], …]` — the same pre/post-repair split that
  makes F2's median a one-sample margin (here 14/25 again).
- Exit witness (`corpus/live/r84-reviewer/exit-witness.txt`): no
  `r84a_1743076` process/sink/module survives, no `r84a-*` scratch dir
  remains, default sink/source unchanged
  (`…SPDIF__sink`/`…Line__source`), `git status` shows only the
  **pre-existing** ` M corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`
  (mtime 21:26 local, before this seat's entry) — zero tracked writes by
  this seat. The foreign `r84a_probe_548706` null sink is still present,
  untouched.

---

## 5. Receipts index (`corpus/live/r84-reviewer/`)

- `measure_audio_fbe65713.py` — pinned copy of the committed blob
  (`git hash-object` == `bc3e0d33…`); `tree/corpus/fixtures/` — the
  mirrored tree used for the re-run (with the committed
  `build_artifacts.py`, which `main()` invokes unconditionally at
  `:21723`).
- `r84r_audit.py` / `r84r_audit.out` / `r84r_audit.json` — the 110-check
  receipt-data audit (0 failed).
- `r84r_compare.py` — leaf-by-leaf comparator (fresh run vs committed).
- `run-r84r1.sh`, `runs/r84r1.{window.txt,stdout.json,stderr.log}` —
  the behavioural re-run.
- `cotenancy-at-entry.txt` — `ps`, both lock files, `pactl` census and the
  two sibling runs' own failure lines (F1 evidence).
- `exit-witness.txt` — post-run host/namespace/git census for this seat.
- `tree/corpus/live/runs/20261016T005939937850Z-alsapw-r84/measurements.json`
  — the fresh run's own receipt (147 legs, `failures: {}`).

## 6. Remaining risks / blockers

- **Co-tenancy is the standing risk**: with 3–4 seats of the same lane
  active, any r84 run's dev-lattice and negctl arms are cross-creditable
  (F1). This reviewer's own run was queued behind the shared-`TMPDIR`
  lock, so it is single-tenant — but the verifier/critic pair was not.
- F2's one-sample margin means a *future* run of this fixture can report a
  sticky failure that is a scheduling artifact, not a regression.
- The different-tag half of refinement #1 (F6) is unverified by any
  receipt in the tree.
- `main()` shells out to `build_artifacts.py` unconditionally (`:21723`),
  so any seat that runs the fixture from a *partial* tree copy aborts
  before the first leg (observed here); the whole-tree copy the verifier
  used (1.5 GB tar) is the alternative.
