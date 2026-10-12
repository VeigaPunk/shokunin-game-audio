# r20-scribe — round 20 decision-table draft (READ ONLY worker)

Worktree: `/home/vgpnk/Projects/prymeagnt/audio`  
Branch: `craft/audio-r1`  
HEAD at scribe time: `a905a265517828d2d10efc33b7dbcf36655e935f` (`a905a26 Audio round 19: final calibration report`)  
Role: `r20-scribe`. Write path only: this file. No LOG.md / MANIFEST / SCORECARD / measure edits. No measurements performed by this leaf.

**Every AFTER row is HYPOTHESIS until the parent (or verifier) measures it.** Setup errors are telemetry, not passes.

---

## 1. BEFORE (measured / cited)

| Field | Value | Evidence |
|---|---|---|
| Work commit (r19 final report) | `6648aae` (r19 report body); tree now at `a905a26` | `.shokunin/reports/round-19/audio.md` |
| Mode count | **16** serial routes in independent replay | `.shokunin/audio/reports/round-19/r19-verifier.md` table rows 1–16 |
| Canonical artifact hashes | **13** canonical byte hashes matched `7083a3f` blobs in r19 verifier | r19-verifier.md (“all 13 canonical byte hashes matched `7083a3f`”) |
| `--probe-layer-third-join` | **Absent** from `measure_audio.py` `add_argument` list | Scribe read of fixtures at HEAD `a905a26` |
| 200 Hz routes present | slope only: `--probe-layer-third-slope`, `--probe-layer-third-slope-edge-pass`, `--probe-layer-third-slope-edge-fail` | same |
| Existing gap-only routes | `--probe-layer-join` (120 Hz), `--probe-layer-alt-join` (180 Hz) | same; r19 table exits 10 and 7 |
| Canonical 200 Hz layer | `stem_layer_third.wav` SHA-256 `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445`; 192000 frames, 48 kHz mono PCM16 | parent task + r19 report |
| Decoded frames 95998–96001 (canonical) | signed counts `[-26, -13, 0, 43]` | parent task |
| Canonical internal gap | `abs(s[96000]-s[95999]) = 0/32768 = 0` FS (passes strict `> .03`) | parent task |
| Canonical side-slope | `abs((s[96001]-s[96000])-(s[95999]-s[95998])) = 30/32768 = .00091552734375` FS/sample (passes strict `> .001`) | parent task |
| 200 Hz contrast | about `+10.457` dB (passes `>= 6` dB); outer/generic pass | parent task / r19 edge receipts |

### r19 mode inventory (exact commands from r19-verifier; exits quoted)

| # | Exact command | Exit |
|---:|---|---:|
| 1 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 |
| 2 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 |
| 3 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 |
| 4 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | 1 |
| 5 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | 1 |
| 6 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | 1 |
| 7 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | 1 |
| 8 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | 1 |
| 9 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | 1 |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | 1 |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | 1 |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | 1 |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | 1 |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | 1 |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 |

Scribe confirmation at HEAD `a905a26`: `parser.add_argument` probe flags = 14 named probes + default normal path = the 16-mode serial table above (normal counted twice in replay). **No** `probe-layer-third-join` string in `measure_audio.py`.

---

## 2. AFTER (HYPOTHESIS — parent must measure)

| Field | Hypothesized value | Status |
|---|---|---|
| New mode class | **exactly one** previously uncovered route: `--probe-layer-third-join` | HYPOTHESIS |
| Mode count | **17** distinct runnable modes (16 prior + third-join); verifier serial table grows by one intentional negative | HYPOTHESIS |
| Scratch WAV | `corpus/live/round-20/join200_probe.wav` (path convention per task; not a new canonical) | HYPOTHESIS |
| Design edit (fit attempt) | Copy canonical PCM16; set frame `96000 = 0 + 1050` (`1050/32768 = .03204345703125` FS `> .03`); set frame `96001 = 43 + 1050` so two-frame step identical and side-slope stays `30/32768 = .00091552734375 <= .001` | HYPOTHESIS design; if second gate fails → **failed fit**, try smallest integer offset that isolates gap only — **do not relax thresholds** |
| Sole intended failure string | `sections: internal join adjacent sample gap > .03 full scale` (wording must match runner; align to existing join_* failure text style, e.g. r19 join rows) | HYPOTHESIS |
| Side-slope | still `<= .001` (does not trip strict `> .001`) | HYPOTHESIS |
| 200 Hz contrast | still `>= 6` dB (~10.457 unchanged in spirit) | HYPOTHESIS |
| Generic / outer gates | pass | HYPOTHESIS |
| Canonical WAVs | **unchanged**; 13 canonical hashes still match verifier baseline | HYPOTHESIS |
| Hash baseline for verifier | Prefer **worktree HEAD `a905a26`** blob set for “unchanged vs current tree”; r19 cited **`7083a3f`** for the 13 canonicals — parent/verifier should **state which** commit’s blobs are the hash oracle and confirm both agree if trees match | DECISION FOR PARENT |
| Thresholds / comparators | unchanged (strict `>` on gap `.03` and slope `.001`) | REQUIRED |
| Coverage claim | new **gap-only** class on 200 Hz layer (pair: live negative control isolating gap from slope/contrast/generic/outer) | HYPOTHESIS coverage axis only if isolation holds |

### Hypothesized commands (not run by scribe)

```text
# HYPOTHESIS — parent/builder/executor only
python3 .shokunin/audio/corpus/fixtures/build_artifacts.py   # with whatever flag wires join200 — not invented here
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join
# expect exit 1; sole failure internal gap > .03 FS; side-slope/contrast/outer/generic pass
```

Scribe **did not** execute these; exits and receipts are empty until measured.

### Fit-failure rule (must appear in LOG)

If measured run shows any second gate failure (slope, contrast, outer, generic, format), record **failed fit**, not an improvement. Retry smallest integer PCM offset that isolates the gap gate. Do not relax any threshold. Do not change canonical WAVs.

---

## 3. SHONEN lines the final report must carry

Copied verbatim from `.shokunin/audio/SHONEN.md` at HEAD `a905a26`. **Do not check a new box. Box 4 stays open.**

```markdown
- [x] Real decision tables/error patterns/checklists with cited sources. Verified by named non-author `audio-r1-verifier`; evidence: `.shokunin/reports/audio-r1-verifier.md` (decision table citations and error-pattern review).
- [x] End-to-end domain task executed and logged. Verified by named non-author `r2-verifier`; evidence: `.shokunin/audio/reports/round-2/r2-verifier.md` (nine-file source-generation replay, positive control, deterministic restore).
- [x] Fixture-battery instructions executable without oral context. Verified by named non-author `r3-adjudicator` with `r3-verifier` replay; evidence: `.shokunin/audio/reports/round-3/r3-adjudicator.md` and `r3-verifier.md`. Scope is the checked-in fixture workflow, not all future audio tasks.
- [ ] No cross-domain bleed; PROVINCE remains accurate.
```

Boxes 1–3 stay `[x]` with their named verifiers; box 4 stays `[ ]`.

---

## 4. Limits that must appear in the round report

1. **Scratch is not canonical content** — `join200_probe.wav` (or successor scratch name) is live/round-20 control only; does not enlarge the 13-canonical set.
2. **`section.passed` / sections `passed` denotes contrast (and section validity), not complete measurement status** — gap/slope/outer can still fail while contrast passes.
3. **No audible / engine / production / perceptual / rights / security claim** — admit only scoped fixture-runner behavior.
4. **`--probe-invalid` does not measure canonical WAVs** — malformed-input path only.
5. **A second-gate failure is a failed fit, not an improvement** — isolation of the internal-gap gate is the coverage claim; multi-gate trips reject the scratch design.
6. **Setup errors are telemetry, not passes.**
7. **Do not relax thresholds; do not modify canonical WAVs** including `stem_layer_third.wav` hash `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445`.

---

## 5. Draft axis table for parent LOG adaptation (all AFTER = hypothesis)

| axis | BEFORE (r19 Sol) | AFTER claim (HYPOTHESIS) | harm check |
|---|---|---|---|
| coverage | unchanged (scratch not canonical; no new class beyond slope bracket) | **improved narrowly** iff `--probe-layer-third-join` is the 17th route and sole failure is internal gap on 200 Hz scratch | zero scoped harm only if canonical hashes hold and no threshold relax |
| calibration | improved narrowly (slope edge bracket) | unchanged unless numbers re-disclose bound (not the r20 intent) | — |
| depth | unchanged | unchanged — reuse existing gap detector text/class on new layer frequency, not a new detector | — |

Parent adapts wording into LOG.md; scribe does not edit LOG.md.

---

## 6. Scribe method / non-claims

| Action | Result |
|---|---|
| Read `.shokunin/reports/round-19/audio.md` | mode-count 16 narrative; work commit `6648aae`; paused note historical |
| Read `.shokunin/audio/reports/round-19/r19-verifier.md` | exact 16-command table and exits quoted above |
| Read `.shokunin/audio/SHONEN.md` | boxes 1–3 `[x]`, box 4 `[ ]` copied |
| Read `measure_audio.py` at `a905a26` | 14 `--probe-*` flags; **no** `third-join` |
| `git rev-parse HEAD` | `a905a265517828d2d10efc33b7dbcf36655e935f` |
| Run measure / build / edit fixtures | **not done** (read-only role) |

---

## 7. Five-line finding (for parent message)

1. BEFORE: r19 = 16 modes at work `6648aae` / tree `a905a26`; 13 canonicals vs `7083a3f` in verifier; no `--probe-layer-third-join`.  
2. AFTER (HYPOTHESIS): 17th route `--probe-layer-third-join` + scratch `live/round-20/join200_probe.wav`; sole fail internal gap `> .03`; slope `<= .001`; contrast `>= 6` dB.  
3. SHONEN: boxes 1–3 remain `[x]`; box 4 remains `[ ]` — no new box.  
4. Limits: scratch ≠ canonical; `passed` = contrast only; no production/audible claim; invalid ≠ canonical; multi-gate = failed fit.  
5. Report path: `.shokunin/audio/reports/round-20/r20-scribe.md` — parent measures before promoting any AFTER cell.

---

*End r20-scribe draft. Parent integrates LOG / SCORECARD / final audio.md after measurement.*
