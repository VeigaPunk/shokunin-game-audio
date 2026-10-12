# Round 20 Sol adjudicator (r20-adjudicator)

Leaf judge. Worktree `/home/vgpnk/Projects/prymeagnt/audio`. No spawn. No edits to builder, runner, canonical WAVs, SCORECARD, LOG, PROVINCE, SHONEN, or MANIFEST. Only this report.

Owned axes: **depth**, **coverage**, **calibration**. One-axis move this round: **coverage**.

## Sources read
- `.shokunin/reports/round-19/audio.md` (r19: 16-mode table; coverage unchanged; third routes slope/edge only)
- `.shokunin/audio/reports/round-19/r19-verifier.md` (16 serial rows; **no** `--probe-layer-third-join`)
- `.shokunin/audio/reports/round-20/r20-verifier.md` (17 serial rows; exit vector `[0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0]`)
- `.shokunin/audio/reports/round-20/r20-critic.md` (pre-admit attack: 200 Hz gap cell missing; same `.03` predicate; reject multi-gate / hash drift / threshold edit)
- Selected receipt: `.shokunin/audio/corpus/live/runs/20261012T232009162006Z-layer-third-join/measurements.json`
- Builder branch `layer_third_join_probe` in `.shokunin/audio/corpus/fixtures/build_artifacts.py` (lines ~124–143)

## Claim under judgment
r19 verifier table had **16** mode routes; after, **17**, by adding `--probe-layer-third-join` (a **200 Hz** internal-gap route absent from that table) whose demonstrated **sole** failure is the paired negative control. **13** canonical WAV hashes and previous failure sets unchanged.

## Verification facts (not invented)

### Mode table growth
- r19: 16 rows; third-layer routes = slope, edge-pass, edge-fail only.
- r20: 17 rows; **new row 2** = `--probe-layer-third-join`, exit 1, receipt `20261012T232009162006Z-layer-third-join`, failure set sole `join200_probe`: `sections: internal join adjacent sample gap > .03 full scale`.
- Rows 3–16 map to r19 rows 2–15 with matching exit pattern and failure **kinds**; row 17 restores normal exit 0. First vs restored normal JSON equal after stripping path/time identity (**held** per verifier).

### Selected receipt (sole-gap profile)
- `measurements.join200_probe.failures` = only `["sections: internal join adjacent sample gap > .03 full scale"]`.
- Section `join200_probe`: `component_hz` 200; internal gap **0.030029296875** FS (**> .03**); side-slope **0.0**; contrast **~10.46 dB** (≥ 6); `valid` true; `passed` true (**contrast/validity only**, not full internal-join gate).
- Measurement centroid for the probe path stays inside the 100–2000 Hz stem band (verifier: ~1209.6 Hz). Outer endpoint/slope pass; no second measurement failure kind on the selected run.

### Builder construction (selected path)
- Not a pure two-frame bump on canonical `stem_layer_third.wav` alone.
- Pattern matches r14 **180 Hz join**: stepped 200 Hz layer **plus** original **220/330 Hz bed**, then `frames[96000]=839` and `frames[96001]=frames[96000]+frames[95999]-frames[95998]` (preserve left step → side-slope 0).
- Verifier PCM check: `pcm[95999]=-145`, `pcm[96000]=839` (delta 984 counts ≈ 0.03003 FS); whole-file FFT peaks **220, 330, 200 Hz**; differs on **191921** frames vs third stem.
- **Limit (state explicitly, as r14 did for 180 Hz join):** this is **NOT** a waveform-identical corruption of `stem_layer_third.wav`. Scratch only — SHA-256 `5194bd8e…`; **not** a 14th canonical.

### Rejected author telemetry (not a pass)
- Parent/first-builder receipt `20261012T231846536176Z-layer-third-join`: **both** centroid-band **and** gap failures (canonical-copy +984 on frames 96000 and 96001). Failed fit. **Not** selected. Does not support admission by itself.

### Canonical hashes
- Verifier: all **13** `corpus/artifacts/*.wav` SHA-256 match `git show a905a26` and `7083a3f`, including `stem_layer_third.wav` = `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445`.

### Prior failure sets
- Verifier: rows 4–15 (r20 numbering) hold same failure **kinds** as r19 rows 3–14; alt-join key label `join180_probe` vs r19 table `join_probe` is naming only — gap kind string matches.
- No second gate failure on the **selected** new mode; no hash drift; no changed previous failure sets in the independent replay.

### Unchanged machinery
- Gap predicate remains strict **`>` .03** FS (`internal_join_adjacent_delta_max_full_scale: 0.03` in receipt thresholds).
- Side-slope companion remains **`.001`** FS/sample; no threshold edit in the selected receipt’s threshold block vs established fixture contract.
- No new detector class — same internal-join gap string as `join_probe` / alt-join family.
- `--probe-invalid` remains malformed-input only (four kinds); does not measure canonical WAVs.
- SHONEN box 4 stays **open** (not checked here).

## Per-axis verdicts

| axis | verdict | rationale |
|---|---|---|
| **coverage** | **improved** (narrowly) | One new CLI/mode route binds the existing gap gate to the **200 Hz / third-layer** cell that r19 left slope/edge-only. Independent 17-row replay shows sole-gap negative on selected `join200_probe`, prior negatives’ kinds held, 13 canonical hashes held, normal restore held. Paired negative = failure of that single route (r14 alt-join accounting), not a second control flag. |
| **depth** | **unchanged** | Same `.03` internal-gap predicate and failure string family; no new detector or failure class. |
| **calibration** | **unchanged** | No threshold edit; receipt still records `.03` gap max and `.001` side-slope max. No local numeric bracket claim this round (unlike r19 slope edges). |

## Admission
**ADMIT** the coverage move under the narrowest true claim below. Zero demonstrated harm on owned axes from the independent verifier package. Do **not** treat the failed first-builder dual-gate receipt as success.

## Narrowest true claim
After r20, the fixture runner exposes **one** additional opt-in mode, `--probe-layer-third-join`, absent from the r19 16-row table. On the **selected** live scratch (`join200_probe.wav` under `corpus/live/round-20/`, with 200 Hz section component over a **220/330 Hz bed** and post-join sample **839**), independent replay records **exit 1** with **sole** failure `sections: internal join adjacent sample gap > .03 full scale` at internal gap ≈ 0.03003 FS and side-slope 0.0; centroid stays in-band. All **13** canonical WAV byte hashes and the prior negative failure **kinds** are unchanged. Scratch is not a 14th canonical; `section.passed` is contrast/validity only; this is not a waveform-identical edit of `stem_layer_third.wav`. No audible-click, musical-quality, engine, rights, security, perceptual-calibration, or production claim. SHONEN box 4 remains open.

## Explicit non-claims
- No pass credit for unrun checks or for author receipt `…T231846…`.
- No claim that coverage improved via a new mathematical gate.
- No claim that invalid-mode validates canonical WAVs.
