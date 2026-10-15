# R77 REVIEWER (audio) — post-commit review of `65790f1`

Target: `65790f1` ("r77 work: capture-source lattice + fallback law + reader
matrix"), 6 files: `corpus/fixtures/measure_audio.py` (+1552/−2) + 5 reports.
Method: my own two runs of `--probe-capture-r77` on HEAD, a mechanical
insertion/string-assert proof, and a leaf-level diff of the two receipts.
**My receipts** (this session, own_pid 2066910 / 2544442):
`corpus/live/runs/20261014T201336507976Z-capture-r77/measurements.json`
(contended host, 3 failures) and
`corpus/live/runs/20261014T201650898147Z-capture-r77/measurements.json`
(**`failures: {}`**).

## Verified clean (independent of the author's runs)

- **Insertion-only is exact, not just numstat.** Removing the 7 added-line
  ranges (`+6,1` hashlib · `+12,1` shutil · `+4148,1528` the r77 block ·
  `+5798,1` arg · `+6092,19` dispatch · `+6597,1` mode · `+6617,1` suffix)
  from the new file leaves **only the two rewritten ternaries** as residual
  (`difflib` over `503689c:`… vs stripped HEAD). 1+1+1528+1+19+1+1 = 1552;
  deletions 2. No shared helper touched.
- **The −2 are value-preserving (string-assert, stronger than sampling).**
  Both are *literally* `"<r77 literal>" if args.probe_capture_r77 else
  <OLD EXPRESSION BYTE-IDENTICAL>` (mode 8291→8342 B, suffix 7697→7743 B,
  prefix comparison exact). Every pre-existing invocation is unchanged.
- **No prior-row reclassification.** `_CAPTURE_R77_ERR_CLASSES` is r77-local
  and `_capture_r77_errclass` is called only at 4402/4540/4662/5500 (all
  r77); `hashlib`/`shutil` appear only at 6/12 and inside the block.
  `py_compile` clean.
- **`ambience.wav` untouched at HEAD.** The commit touches no
  `corpus/artifacts` path (`git log -- corpus/artifacts/ambience.wav` →
  only `57ef9c5`); worktree blob == HEAD blob (`57934d4d…`);
  `git diff HEAD -- corpus/artifacts/` empty.
- **No scratch-path cross-seat writes.** The block writes only to
  `tempfile.TemporaryDirectory(prefix="capture-r77-")` and
  `ROOT/live/capture-r77-split` (created + `rmtree` in `try/finally`, each
  leg `rmtree`s its own subdir, 5465/5504/5530). No seat-named path. After
  both runs: no scratch dir, `pactl list modules` has no `r77_loss_sink`,
  no stray probe processes.
- **Both scout falsifications are documented correctly in-code — and
  reproduced by my run.**
  (1) *Split clamp* (4192-4193, 5313-5315, 5517-5525): my crossing leg gave
  `rot-01.wav` = **2147483692 B** = `0x80000000+44`, `data_declared` =
  **2147483647** (`0x7FFFFFFF`), `data_actual` = 2147483648,
  `requested_path_exists: False`, rc=0 → `rename_is_silent: True`; the
  unbounded KILL still asserts `placeholder_80000000` (5392-5395). Asserted,
  not merely asserted-in-prose.
  (2) *`alsa_read_eintr`* (5421-5435): `eintr_cells: []` over exactly the
  **15** device-axis cells (3 devices × {4 TERM + 1 KILL}, 5415-5417),
  `scout_alsa_read_eintr_reproduced: False`, with the note naming it a
  contended-host event, not a per-route partition.
- **Law leaves are stable and reproduced.** Run 2 reproduces every pinned
  number: 12×5 reader matrix with the exact tally (`sndfile 12/12 honest`,
  `ffprobe 11/12`, `wave 6/3 rejects/3 declared_echo`, `soxi_s`/`soxi_D`
  `6/5/1` — `_answered: 12` for all five), split bytes above, 16/16 format
  legs (12 honored + 4 `usage_refusal`, baseline 19244 B), 26 arecord legs
  (11 bound + 15 device), 11/11 lattice cells. Comparing my two receipts,
  955 law-bearing leaves were compared and the differing 53 are 52 declared
  wall-clock-severed bytes/derived answers plus 1 declared raw wall time
  (`split_sentinel.undershoot.wall_s`).

## Findings, by severity

### F1 — HIGH: the new verdict surface mis-asserts three host confounds it can already detect; `failures: {}` is not reproducible on a shared host

My run 1 (host had 5-6 concurrent `measure_audio.py`; `host_is_quiet:
False`) emitted 3 failures. None is a law violation — in each case the
artifact matched the pinned law and the *witness* was unreadable:

- **F1a lattice `prop_auto`** (4800, 4803-4858): `stale_link_before_cell:
  True` (i.e. `_capture_r77_wait_clear()` returned `None`, 4383-4392) is
  **recorded and then ignored**; the cell's artifact was exactly the
  predicted `384044 B / finalized / carries_tone: True` yet it failed
  `"expected consumption of default_sink, got []"`. Cause: the differenced
  table (4339-4359) cancels the real link when the *same node's* producer is
  already in the pre-spawn baseline — the ghost of the previous cell, which
  also targets the default sink (the lattice puts 8 same-node cells back to
  back). **Same run, same host condition, opposite treatment**:
  `prop_garbage` had `stale_link_before_cell: True` plus a *new* foreign
  link and was correctly named a confound and skipped (4816-4832); 4833-4847
  already ignores the link table for the `noprop_*` cells for exactly this
  ghost reason (§7.3). Fix: treat `stale_link_before_cell`/`wait_clear is
  None` as a named confound (skip the node verdict) — the flag already
  exists.
- **F1b target loss, witness** (4972-4989): `nodes_before: ['r77_loss_sink']`
  → `nodes_after: []`, `contended: False` → hard failure. The loss entry has
  **no foreign/stale guard at all** (the lattice has one); the preceding
  `fallback_control` leg consumes the same fallback node, so its ghost is in
  the `after_loss` baseline and cancels the re-link. The re-link law itself
  held: rc=1, 384044 B, finalized, 98 % → 100 % of nominal.
- **F1c target loss, content** (4990-4993, `all_zero_payload` 5107-5121):
  `sha_match_control: False` fails whenever the fallback monitor carries
  *live* content. Across the r77 family, **all 6 runs whose sha check passed
  have `fallback_control.all_zero_payload: True`** (incl. the author's three),
  and the 2 whose sha check failed have `False` (195831 and my run 1: control
  `2bfd20c5a270498e` vs after_loss `a9056b0ae09b6dc4`). The guard leaf is
  already computed — gate the sha verdict on it (or name a confound).
- The author's claim is *true for their three runs* (I re-read those
  receipts: `failures: {}`, `alsa_busy_cells: []`, `confound_observed: None`)
  — but it is not reproducible under the fleet's normal concurrent load, and
  the failure text attributes a host confound to the capture.

### F2 — MEDIUM: the new flag escaped the "choose one probe mode" guard

`measure_audio.py:5801` sums 120 flags — `probe_capture_r76` is there,
**`probe_capture_r77` is not**; the diff added the registration (5798) as
the only change near that line (the guard line appears as unchanged context).
Guard eval over the file's own literal: `(r77,r76)` → no error,
`(r77,consumers2_r75)` → no error, `(r76,consumers2_r75)` → error. Both
dispatch blocks are independent `if`s (6092, 6111), so a mixed invocation
runs both and writes a receipt labelled `mode: probe-capture-r77` (6597) in
a `-capture-r77` dir (6617) that also contains the six `capture_*_r76_probe`
rows — a receipt that lies about its own payload. One-line fix: add the flag
to the sum. (Corroboration only, another seat's artifact:
`corpus/live/r77-baseline/exclusivity-check.txt` shows
`--probe-consumers2-r75 --probe-capture-r77` → rc=124, guard did not fire.)

### F3 — MEDIUM: the declared host-drift leaf set is honest for quiet hosts but under-covers the contended surface

My run1↔run2 diff: **307 differing leaves**. **211 fall inside the declared
categories** (145 wall-clock-severed bytes + derived reader answers; 51 more
of the same shape inside the reader-matrix wounds, which are also TERM/KILL
severed; 7 rate buckets/wall times; 8 host-state). The remaining
**96 are undeclared**, dominated by the **ALSA-busy carve-out cell flip
(65 leaves, 4 cells)**: when a device is busy the whole leg's leaf set
appears/disappears (`error_class`, `error`, `stderr_tail`, `file.*`,
`readers.*`) — my run 1 had 4 busy cells, run 2 none. Also undeclared: the
target-loss host-content leaves (7: `fallback_control`/`after_loss`
`sha256_16` + `all_zero_payload`, `sha_match_*`, `nodes_after`), the confound
flags (2), the failures map (2), and 20 lattice ghost-witness leaves
(`consumed_nodes`/`link_producers`/`link_after_exit`/`target_object_prop`
lengths, `stale_*`). Two wording notes: the drifting content leaf is
`content.nonzero_frac` (and `peak`), not only "raw content peaks"; and
`contention.own_pid` is the PID. §8's zero-difference claim was made on three
runs whose receipts have no busy cell and no confound — i.e. on a surface
where these classes cannot appear. Fix: declare them (or bucket the busy
cells out of the stable shape).

### F4 — MEDIUM-LOW: the reader matrix's stated precondition is recorded, never asserted

`entry["unit_calibration"]` (5164) is the **only** reference to it in the
file; the docstring (5150-5155) and §3 call the calibration the basis of the
frame-domain comparison ("an uncalibrated reader comparison is worthless").
My run's calibration is correct (all five readers = 96000 frames), so the
tally stands — but nothing fails if `soxi -s` semantics or the synthetic
writer drift, and the tally would then be emitted as a pinned result.
Fold: assert the five calibration values.

### F5 — LOW-MEDIUM: the split leg's header inspection costs ~2 GB RAM (declared disk bound only)

The crossing leg hands a 2,147,483,692-byte file to `_capture_wav_inspect`,
which does `data = path.read_bytes()` (3037). Isolated measurement on a file
of exactly that size: **peak RSS +2048 MB** (34.9 → 2082.8 MB), 0.27 s.
The round declares a hard *disk* bound (2.4 GB SIGKILL watchdog, 60 s wall
cap, 4193-4194) but not the RAM. Pre-existing helper, new 2 GiB call site.
Fold: bounded header read (first 64 KiB + `os.path.getsize`) for the split
sibling.

### F6 — LOW: receipt hygiene / remaining ungated leaves

- `entry["default_source_is_silent_on_this_host"] = True` (4762) is a
  hardcoded literal presented as a measurement, and the `noprop_source`
  verdict depends on it (expects `tone: False`). Label as a declaration.
- Lattice cells record `link_producers`/`consumed_nodes` but not the link
  probe's `exit`/`error` (4293-4327), so an empty witness cannot be
  attributed ("no producer" vs "table unreadable") — this is what forced a
  mechanism argument in F1a. Add `link_exit`/`link_error`.
- Totality holds where the tables are the coverage contract (lattice 11/11,
  arecord 26/26 presence-checked, format 16/16, split 2/2, readers 12 cells
  × 5 verdict slots all filled). Gap: the **12 device-axis TERM legs** are
  presence-checked and eintr/busy-scanned but have no finalize/class
  assertion (5396-5409 covers only the 5 `bound_*_term` labels) even though
  headline #5 claims all 15 TERM cells finalize with `aborted_by_signal`.
- Readers loop message "no readers ran on a non-empty file" (5231-5233)
  also fires for empty/missing files (double-report on early-exit cells).

## Residual risk

- A probe run rewrites **tracked** `corpus/artifacts/*.wav` (via
  `build_artifacts.py`): mtime moved 17:11 → 17:14:35 in my run 1 with bytes
  identical (`git diff` empty, blob `57934d4d…` unchanged). This is the
  mechanism behind the mid-round accidental regeneration; byte-determinism
  held for my two runs, but the write itself is a cross-seat hazard on
  tracked files (pre-existing harness behavior, not this diff).
- `corpus/live/capture-r77-split` is a fixed path: two concurrent r77 runs
  collide (one's `finally: rmtree` deletes the other's scratch). Same for the
  shared default sink/ALSA device — the probe is serialized by convention
  (4617-4618), not enforced.
- My review left no side effect: the one tracked file I touched
  (`corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`, from
  `py_compile`) was restored; `git status` shows no tracked modification.

## Verification gaps (not covered by this review)

- No independent re-run of the r76 regression (the author's 23/23-key claim
  and the baseline seat's re-check were not reproduced by me); my
  insertion-only proof covers the structural half of that claim.
- The `f32` "+44 bytes, recorded but not asserted" delta and the lattice's
  `target_object_is_request` leaf are witnesses, not verdicts (author
  declares this for the former).
- Host was not quiet during any of my runs (`host_is_quiet: False`), so I
  cannot demonstrate the contended-only nature of F1 by a quiet-host
  counter-run; the correlation (pass ⇔ `all_zero_payload` True; fail ⇔ False)
  across 9 family receipts is the evidence I have.

## Recommendation

**ACCEPT the diff** — insertion-only, value-preserving, prior rows intact,
both falsifications documented and reproduced, `ambience.wav` untouched at
HEAD, no cross-seat scratch writes; my run 2 reproduces every pinned law with
`failures: {}`. **Fold F1a/F1b/F1c and F2** before citing the r77 receipt
family as a gate on a shared host: three of the four are one-liners against
flags the probe already computes, and F2 is a one-line guard extension. F3-F6
are declared-vs-recorded cleanups.
