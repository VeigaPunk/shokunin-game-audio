# r20-simplifier — round 20 coverage move (leaf, read-only)

**Role:** r20-simplifier  
**Worktree:** `/home/vgpnk/Projects/prymeagnt/audio` (branch `craft/audio-r1`, HEAD a905a26)  
**Write path:** only this file. No commits, no MANIFEST/SCORECARD/LOG/PROVINCE/SHONEN, no edits to `measure_audio.py` / `build_artifacts.py` from this leaf.

## 1. What the parent must not do

Read of fixtures:

- Runner: `.shokunin/audio/corpus/fixtures/measure_audio.py` (276 lines)
- Builder: `.shokunin/audio/corpus/fixtures/build_artifacts.py` (206 lines)

**Forbidden this round (parent / executor integration):**

| Do not | Why |
|--------|-----|
| Change any threshold (`.03`, `.001`, `6.0` dB, centroid bands, distinctness, RMS/peak) | Calibration axis; round is coverage of a mode class, not retune |
| Rewrite canonical WAVs under `artifacts/` (esp. `stem_layer_third.wav`) | Canonical identity + SHA are fixed; scratch only |
| Add a new detector / new failure string family | Depth/calibration noise; reuse existing gap string |
| Refactor the exclusive-mode `sum([...])` / nested ternary into a table or dispatch map | Second structural change beyond the one flag; out of scope |
| Mint a new canonical artifact name in SPECS / `artifacts/` | Scratch lives under `live/round-20/` only |
| Edit MANIFEST.json, SCORECARD.md, LOG.md, PROVINCE.md, SHONEN.md | Parent integrates books |
| Change `measure()` loop-seam gates or invent a parallel gap constant | Same physical gate as internal join; constants already shared in receipt thresholds |

**Allowed one-move shape:** one new CLI flag `--probe-layer-third-join`, one scratch WAV path (e.g. `live/round-20/join200_probe.wav`), wire that path into measure + `section_contrast(..., 200)`, apply the **existing** internal-join adjacent gap predicate (`> .03`) and keep slope / contrast / outer seam as negative-control pass conditions.

## 2. Smallest coverage move; constants are required

**Uncovered class:** 200 Hz internal-gap-only. Existing gap-only routes are `--probe-layer-join` (120 Hz) and `--probe-layer-alt-join` (180 Hz). 200 Hz today only has slope modes (`--probe-layer-third-slope`, edge-pass, edge-fail). Mode count in runner exclusive sum today: 14 probe flags + invalid + normal path; **no** `probe_layer_third_join`.

**Minimal delta:**

1. **One flag:** `--probe-layer-third-join` on both builder and runner (argparse + exclusive `sum` + mode/suffix string + build forward + measure path hook).
2. **One scratch WAV:** copy canonical PCM16 `stem_layer_third.wav`; do not add SPECS entry; do not touch canonical bytes on disk beyond read.
3. **Same gap predicate:** `result["internal_join_adjacent_delta_full_scale"] > .03` → existing failure text `sections: internal join adjacent sample gap > .03 full scale`. Include the new probe name in the same name-sets that already gate 200 Hz layers for gap (and for slope only if the scratch must still be slope-checked—yes, negative control).

**Reusing `.03` and `.001` is required, not optional.** Receipt already publishes:

- `internal_join_adjacent_delta_max_full_scale`: `.03`
- `internal_join_side_slope_mismatch_max_full_scale_per_sample`: `.001`

A second numeric gap bar would be a threshold change dressed as coverage. Slope must stay the same constant so the scratch can prove gap-only isolation (gap fails, slope still ≤ `.001`).

## 3. Acceptable vs harmful duplication

**Acceptable this round (mirrors prior join routes):**

- Another branch in the exclusive-mode `sum([...])` and another arm in the nested mode/suffix ternary (same style as r10/r14 joins and r18/r19 third-slope).
- Another `if args.probe_layer_third_join: path = live/round-20/...` measurement slot.
- Another builder block that opens canonical third WAV, mutates two frames, writes scratch under `live/round-20/`.
- Listing the new probe name next to `stem_layer_third` / slope200 / edge* in the 200 Hz `section_contrast` Hz ternary and in the gap (and slope) name tuples.

**Harmful (drop if proposed):**

- A second gap threshold or renamed failure string (“join200 gap” vs existing internal join string).
- A table refactor of modes “while we’re here.”
- New detector for gap independent of `section_contrast` join fields.
- Editing canonical synthesis of `stem_layer_third` so the clean fixture itself fails gap.
- Parallel constant like `JOIN200_GAP = 0.03` that can drift from receipt thresholds.

## 4. N selection (hypothesis → prefer smallest isolating N)

Canonical decoded join neighborhood (task + design): frames 95998–96001 signed counts `[-26, -13, 0, 43]`.

- Internal gap: `abs(s[96000]-s[95999]) = 0/32768 = 0` (pass strict `> .03`).
- Side-slope: `abs((s[96001]-s[96000])-(s[95999]-s[95998])) = 30/32768 ≈ .00091552734375` (pass strict `> .001`).
- Contrast ~ +10.457 dB (≥ 6 dB).

**Design hypothesis N=1050:** set `frames[96000] = 0 + 1050`, `frames[96001] = 43 + 1050` so the two-frame step is unchanged → side-slope stays 30 counts; gap becomes `1050/32768 ≈ .03204345703125 > .03`.

**Nearest gap crossing in integer counts:** threshold is exclusive `> .03`, so minimum failing adjacent delta is `ceil(.03 * 32768) = ceil(983.04) = 984` counts (`984/32768 = .030029296875`). With base gap 0, **N_min = 984** (not 983: `983/32768 = .029998779296875 ≤ .03` still passes).

**Recommendation:** if executor verifies N=1050 **and** N=984 (or the smallest N ≥ 984 that still leaves slope ≤ `.001`, contrast ≥ 6 dB, outer seam/generic pass, and **only** the gap failure string on the probe), **prefer the smallest isolating N (likely 984)**. That choice is nearest-crossing probe geometry; **it does not retune the threshold**—the bar stays `.03` / `.001`. If 984 collides with another gate, record failed fit and walk upward by 1 count until isolation; do not relax thresholds.

**Negative control contract:** probe measurement must show gap failure present; slope mismatch still ≤ `.001`; section contrast still valid and ≥ 6 dB; outer loop seam still pass; no new failure kinds. Canonical `stem_layer_third` in the same run must remain clean.

## Keep / drop list

### KEEP

- One flag `--probe-layer-third-join` only (coverage class: 200 Hz gap-only).
- Scratch under `live/round-20/` (name e.g. `join200_probe.wav`); copy-mutate canonical PCM16.
- Existing strings and constants: gap `> .03`, slope `> .001`, contrast `>= 6`, failure text unchanged.
- Parallel wiring style of `--probe-layer-join` / `--probe-layer-alt-join`.
- Prefer **smallest isolating integer N** (start 984; 1050 only if smaller fails isolation).
- Parent-only book/manifest integration after measured receipts.

### DROP

- Threshold edits or dual constants.
- Canonical WAV rewrite or new SPECS canonical.
- New detector / new failure taxonomy.
- Mode-table refactor or broad cleanup.
- MANIFEST / SCORECARD / LOG / PROVINCE / SHONEN / measure&build edits from this leaf (N/A — leaf did not touch them).
- Treating setup/tool errors as passes (telemetry only).

## Commands this leaf ran

```text
# Python Path.exists / read_text on measure_audio.py and build_artifacts.py only.
# No measure_audio.py / build_artifacts.py execution from this leaf.
# No WAV mutation from this leaf.
```

Exits: N/A (read-only inspection). Setup errors: none for file presence; both fixtures present.

## 5-line finding (for parent)

1. Smallest coverage move = one flag `--probe-layer-third-join` + one scratch 200 Hz PCM copy + existing internal gap predicate; no new detector.  
2. Reuse `.03` and `.001` is mandatory; a second bar would be retune, not coverage.  
3. Acceptable dup = exclusive-sum / ternary / live path branch; harmful dup = new threshold, new failure string, mode-table refactor.  
4. Prefer smallest isolating N (984 counts ≈ .03003 FS) over 1050 if isolation holds; choice is geometry, not threshold change.  
5. Parent must not touch canonical WAVs, MANIFEST/sibling books, or relax gates; this leaf wrote only `reports/round-20/r20-simplifier.md`.
