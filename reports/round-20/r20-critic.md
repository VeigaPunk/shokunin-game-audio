# Round 20 critic — attack coverage claim `--probe-layer-third-join`

Role: r20-critic (read-only except this file). Worktree `/home/vgpnk/Projects/prymeagnt/audio`, branch `craft/audio-r1`, HEAD `a905a26`. No builder/runner/canonical edits by this lane. No measure/build invocations claimed as passes.

## 1. New mode class vs duplicate frequency label

### What exists today (HEAD, no third-join flag)

Builder CLI (`build_artifacts.py` argparse): join routes are only `--probe-layer-join` and `--probe-layer-alt-join`. Third-layer routes are slope-only: `--probe-layer-third-slope`, `--probe-layer-third-slope-edge-pass`, `--probe-layer-third-slope-edge-fail`. **No** `--probe-layer-third-join`.

| Flag | Source construction (builder) | Live scratch | Runner measure key / SPEC / Hz |
|---|---|---|---|
| `--probe-layer-join` | Read canonical `stem_layer.wav` float, add `.03*sin(2π·60·t)`, force `frames[96000]=round(.0305*32767)` only (no paired +offset on 96001) | `live/round-10/join_probe.wav` | `join_probe` / `SPECS["stem_layer"]` / section bin **120 Hz** |
| `--probe-layer-alt-join` | Synthesize 180 Hz two-level sine + 220/330 carriers; `frames[96000]=round(.040*32767)`; `frames[96001]=frames[96000]+frames[95999]-frames[95998]` (preserve left step into right) | `live/round-14/join180_probe.wav` | `join180_probe` / `SPECS["stem_layer_alt"]` / **180 Hz** |
| proposed `--probe-layer-third-join` | **Absent.** Hypothesis: copy canonical `stem_layer_third` PCM16; add same integer offset to frames 96000 and 96001 so gap exceeds `.03` while side-slope stays at canonical 30/32768 | would be live/round-20 scratch | would need `SPECS["stem_layer_third"]` / **200 Hz** lists in `section_contrast` name sets |

### Same vs not the same

**Not new (do not over-claim):**

- Same runner module and same internal-gap predicate: after `section_contrast`, any listed name with `internal_join_adjacent_delta_full_scale > .03` appends `"sections: internal join adjacent sample gap > .03 full scale"` (`measure_audio.py` ~244–245). Thresholds receipt still records `internal_join_adjacent_delta_max_full_scale: .03` (strict `>`).
- Same side-slope companion gate `.001` FS/sample where the name is on the slope list (~246–247).
- Same outer seam gates on looped SPECS (`.03` endpoint, `.001` outer slope).
- Same contrast gate `delta_db >= 6.0` inside `section_contrast` (`passed` field).
- Pattern family already proven at 120 Hz (r10) and 180 Hz (r14): gap-only scratch negative, not a new detector algorithm.

**New (coverage claim that can be true if implemented and isolated):**

- A **200 Hz canonical-copy** join route is **absent** from the r19 verifier table and from current argparse/mode ternary (~248, ~265).
- r19 200 Hz coverage is **slope-class only** (third-slope, edge-pass, edge-fail). Gap-class on third is the missing cell of the (layer × {flat, join, slope, …}) grid.
- Distinct from alt-join construction: alt-join **resynthesizes** a richer base and sets an absolute level at 96000; third-join hypothesis is a **minimal two-frame integer bump on the existing 200 Hz canonical**, preserving side-slope by identical offsets — closer in spirit to third-slope’s “read canonical PCM16, edit frames, write live scratch” than to alt-join’s full rewrite.
- Distinct from layer-join: layer-join mutates 120 Hz stem_layer with an added 60 Hz tone and only forces frame 96000 (side-slope may also move; not the third-layer SPEC).

**Verdict on novelty:** Not a duplicate flag with a relabeled frequency. It is a **new CLI/mode route** binding the **existing** gap predicate to **stem_layer_third / 200 Hz**, which r19 does not route. Novelty is **coverage of an uncovered (layer, gate-class) pair**, not a new mathematical gate.

## 2. Mode count: one route vs illegal 18th

### r19 baseline

`r19-verifier.md` opens: “Ran the requested **sixteen modes** serially” and tables **16 command rows**. Unique CLI identities in that table:

1. normal (row 1 and row 16 restore — same mode, two invocations)
2. `--probe-layer-third-slope-edge-pass`
3. `--probe-layer-third-slope-edge-fail`
4. `--probe-layer-third-slope`
5. `--probe-layer-alt-reverse`
6. `--probe-layer-alt-slope`
7. `--probe-layer-alt-join`
8. `--probe-layer-alt-flat`
9. `--probe-layer-slope`
10. `--probe-layer-join`
11. `--probe-flat`
12. `--probe-layer-flat`
13. `--probe-slope`
14. `--probe-failing`
15. `--probe-invalid`

So “mode-count 16” is **16 table invocations** (normal doubled for restore), not 16 distinct flags. Distinct measure modes including one normal ≈ **15** unique mode strings; argparse probe flags at HEAD = **14** + normal.

Parent sentence to attack: after r20, “**17 modes**” and “exactly one previously-uncovered mode class … plus its paired negative control.”

### r14 precedent (alt-join)

`--probe-layer-alt-join` is **one** table row / one flag. The **paired negative is the measured failure of that same route** (gap > .03 on the scratch), not a second CLI. r19 still lists alt-join once (row 7), exit 1, failure kind internal gap.

Edge pair in r19 is different: **two** CLIs (edge-pass / edge-fail) because both are first-class routes bracketing a threshold — each counts as its own mode row.

### Correct reading for r20 join

**Confirm parent intent:** one new flag `--probe-layer-third-join` whose **demonstrated isolated gap failure IS the paired negative**. That matches r14 alt-join accounting, **not** r19’s two-flag edge bracket.

- Legal after: **one** new mode string → verifier table grows by **one primary negative row** (plus optional normal restore policy). If they keep the r19 style of 16 rows with normal twice, “17 modes” means **17 rows** with one new join row, or **16 unique + 1** depending on whether normal-double still inflates the count. The honest unique-mode claim is: **unique CLI modes = prior unique set + 1**.
- **Illegal:** adding both `--probe-layer-third-join` **and** a separate “join-fail control” flag, or counting scratch WAV as a mode, or counting the gap failure as a second mode class → that would be an 18th (or worse) under a “one class + separate control mode” misread.
- **Also illegal:** claiming “17” while only documenting the builder without a runner flag/mode ternary/receipt suffix wire-up.

## 3. Falsifiers (reject the round if any hold)

1. **Second gate failure on the scratch** — side-slope > .001, contrast < 6 dB / invalid section, outer seam endpoint/slope, format/duration/level/centroid, or generic failures on the probe name. Hypothesis offset +1050 on both 96000 and 96001 aims to keep side-slope at 30/32768; if fit fails, smallest integer isolation is required. Multi-failure = not an isolated gap negative.
2. **Canonical hash drift** — `stem_layer_third.wav` SHA-256 must remain `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445`; any rewrite of artifacts/*.wav fails the round. Scratch must live under `corpus/live/…`, not replace canonical.
3. **Threshold edit** — changing `.03`, `.001`, `6.0`, SPECS bands, or switching `>` to `>=` (or the reverse) to force a pass/fail.
4. **Calling scratch a 14th canonical WAV** — inventory stays 13 artifacts; live probes are not canonicals.
5. **Counting `--probe-invalid` as measuring canonicals** — invalid mode only checks malformed probes; r19 already limits this.
6. **Treating `sections.*.passed` as the complete gate result** — that field is only `valid and delta_db >= 6.0` inside `section_contrast`. Internal gap and side-slope are **separate** appendages on `measurements[name].failures`. A gap-only fail can still show `sections.*.passed: true` (r19 edge notes the same trap).
7. **Runner list omission** — new probe name must be included in the 200 Hz branch of `section_contrast` selection **and** in the internal-gap name tuple; missing from gap list ⇒ silent non-measurement of the claimed gate. Note: `join_probe` is on the gap list but **omitted** from the side-slope name list (~246); third-join isolation claims must state which lists include the new name.
8. **Setup errors as passes** — missing WAV, SoX failure, argparse reject, or multi-flag `sum(...) > 1` are telemetry, not coverage.

## 4. Must not claim

- Audible click, discontinuity “heard,” musical quality, mix aesthetics.
- Engine/runtime/production player behavior.
- Perceptual calibration or that `.03` FS is an audibility threshold.
- Universal PCM grid law beyond this waveform + SoX float32 decode path + these comparators.
- That gap-class is newly invented (it is not; only 200 Hz routing is).

## Narrowest true claim (if executor later lands clean evidence)

> Added one runner/builder mode `--probe-layer-third-join` that builds a live PCM16 scratch from canonical `stem_layer_third` without changing its SHA-256, measures it under `SPECS["stem_layer_third"]` / 200 Hz section bins, and yields exit 1 with **sole** probe failure `sections: internal join adjacent sample gap > .03 full scale` under unchanged thresholds; side-slope, contrast, outer seam, and generic checks pass on that probe. This fills the r19 hole where 200 Hz had slope routes but no gap-only route. Mode accounting: **one** new mode; the isolated gap failure is the paired negative (r14-style), not a second mode.

Until receipts exist with exact commands/exits and single-failure JSON, the claim is **hypothesis only**.

## Admit / reject recommendation

| Question | Answer |
|---|---|
| Is the **design target** a legitimate uncovered cell? | **Yes** — 200 Hz gap-only route missing; slope-only third coverage at r19. |
| Is it a new detector? | **No** — same `.03` gap predicate and runner family as join / alt-join. |
| Mode count reading | **Confirm** one new CLI; failure of that CLI = paired negative; do not add a second control mode. “17 modes” must not mean two new flags. |
| Admit coverage **now** (pre-implementation / pre-receipt)? | **Reject admission of measured coverage.** Critic admits only the **plan’s logical slot**, not a pass. |
| Admit after clean isolated receipt + unchanged canonical hash + no threshold edits? | **Conditionally admit** under the narrowest true claim above; else reject. |

**Overall: REJECT admitting the round-20 coverage claim as established fact at critic time.** **ACCEPT** the parent’s problem framing (one new 200 Hz join mode, r14-style single-route negative) as the correct success criterion for later lanes. Any scribe/adjudicator language that equates “we intended +1050” with “gate isolated,” or that treats `section.passed` as full internal-join status, must be refused.

## Evidence anchors (static read; not pass telemetry)

```text
# flags present at critic read (no third-join):
grep -n 'probe-layer' .shokunin/audio/corpus/fixtures/build_artifacts.py \
  .shokunin/audio/corpus/fixtures/measure_audio.py
# join branches: build ~138–162 (alt-join, join); third branches ~100–123 (slope/edge only)
# gap predicate: measure_audio.py ~244–247; section.passed definition ~107
# r19 table: reports/round-19/r19-verifier.md (16 rows; third join absent)
```

Canonical third cited by parent/r19: SHA-256 `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445`; frames 95998–96001 counts `[-26,-13,0,43]`; internal gap 0; side-slope 30/32768; contrast ~+10.457 dB.

## 5-line finding

1. `--probe-layer-third-join` would be a **new 200 Hz route**, not a renamed `--probe-layer-join`/`--alt-join`; gate math is the **same** `.03` gap check.  
2. r19 has **no** third-join; 200 Hz is slope/edge only — the coverage hole is real.  
3. Paired negative = **failure of that one mode** (r14 alt-join style); a second control CLI would illegally inflate mode count.  
4. Falsifiers: multi-gate fail, canonical drift, threshold edits, scratch-as-canonical, invalid-as-canonical, `section.passed` misread.  
5. **Reject admit-now**; allow only the narrow isolated-gap claim after receipts — no click/perceptual/engine claims.
