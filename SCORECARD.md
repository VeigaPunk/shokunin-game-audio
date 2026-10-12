# audio scorecard — mint

Owned axes: depth, coverage, calibration. Scores remain unassigned without a
quality rubric; a row count is a measurement, not a score or verdict.

| axis | score | evidence / counting command | last change |
|---|---|---|---|
| depth | unmeasured | mint: no rounds yet | mint |
| coverage | unmeasured | mint: no rounds yet | mint |
| calibration | unmeasured | mint: no rounds yet | mint |

planned: round 1 declares the first falsifiable claim (see LOG.md).
retired: none.

## Round 1 verdict — 2026-10-12

| axis | verdict | evidence |
|---|---|---|
| depth | improved | source-generated SFX/stem plus format, RMS/peak, EBU gated loudness, FFT centroid/bandwidth and loop endpoint checks; `corpus/fixtures/` + `corpus/knowledge/2026-10-12-fixture-battery.md` |
| coverage | improved | four SFX and one stem with passing normal receipt and failing seam positive control; `.shokunin/reports/audio-r1-verifier.md` |
| calibration | improved | calibrated thresholds are labeled local; short-SFX gated LUFS is null, RMS remains available; seam/centroid proxies explicitly do not establish perceptual quality; verifier report |

Admission: at least one improved, none harmed. Score remains unassigned; no scalar rating is implied. SHONEN box 1 was checked by the named non-author verifier only. Other boxes remain open.

## Round 2 verdict — 2026-10-12

| axis | verdict | before → after evidence |
|---|---|---|
| depth | unchanged | Same generated-WAV duration/format, level, full-signal spectrum, ebur128 and endpoint battery applies to nine files; no new quality dimension claimed. `reports/round-2/r2-adjudicator.md` |
| coverage | improved | Four → eight SFX (one → two in each UI/impact/movement/ambience category), unchanged stem. Count: `python3 -c "from pathlib import Path; print(sorted(p.stem for p in Path('.shokunin/audio/corpus/artifacts').glob('*.wav')))"`; all nine measured and four variant distinctness rules pass in `corpus/live/runs/20261012T161825061249Z-normal/measurements.json`. Before `31d8e9e`; measured on round-2 delivered files, see `reports/round-2/r2-verifier.md`. |
| calibration | improved narrowly | Ambiguous nonzero-duration branch tightened before integration to >=.020 s; measured centroid OR branch remains >=.10, receipt includes both. All are fixture-local thresholds, not mastering/perceptual rules. `reports/round-2/r2-critic.md`, `r2-adjudicator.md`. |

Admission: coverage improved, calibration narrowly improved, depth unchanged, none harmed. No scalar score assigned. Named non-author `r2-verifier` checked SHONEN box 2; 3–4 open.

## Round 3 verdict — 2026-10-12

| axis | verdict | before → after evidence |
|---|---|---|
| depth | improved | Before `ef2dc58`: endpoint-amplitude test alone. After: decoded-PCM adjacent-slope join metric catches equal-endpoint probe (endpoint 0, slope .469970703125 > .001 FS/sample) as sole failure in `.shokunin/audio/corpus/live/runs/20261012T162835463500Z-slope/measurements.json`. Non-author replay `reports/round-3/r3-verifier.md` and `r3-adjudicator.md`. |
| coverage | unchanged | All nine canonical WAVs match before hashes, four variant comparisons continue to pass; count with `python3 -c "from pathlib import Path; print(sorted(p.stem for p in Path('.shokunin/audio/corpus/artifacts').glob('*.wav')))"` against before `ef2dc58`, receipts `20261012T162822089971Z-normal`/`162836475076Z-normal`. |
| calibration | unchanged | Local .001 FS/sample bound has 32.8× clean max of three loops, described as nonportable; prior checks and caveats preserved. `reports/round-3/r3-calibration.md`, `r3-adjudicator.md`. |

Admission: depth improved, coverage/calibration unchanged, none harmed. No scalar score. SHONEN box 3 narrowly checked by named non-author `r3-adjudicator`; box 4 open.

## Round 4 verdict — 2026-10-12

| axis | verdict | before → after evidence |
|---|---|---|
| coverage | improved narrowly | Before `68a3c3c`: one soundtrack stem; after two (`stem.wav`, `stem_sections.wav`), the new 4s loop has measured 13.979508 dB 30Hz section contrast and matched flat30 0dB sole-failure control. Counting command `python3 -c "from pathlib import Path; print(sorted(p.stem for p in Path('.shokunin/audio/corpus/artifacts').glob('*.wav')))"`; non-author `reports/round-4/r4-verifier-replay.md`, raw `corpus/live/runs/20261012T164320494590Z-normal/measurements.json`; nine original hashes preserved. |
| depth | unchanged | Existing nine-file measurement dimensions, slope/endpoint controls and variant comparisons remain; section contrast is specific to new fixture, not evidence of general sonic quality. `reports/round-4/r4-adjudicator.md`. |
| calibration | unchanged | >=6dB 30Hz component contrast and amplitude/RMS floors are named local analytic choices; flat control tests rejection but not universal perceptual threshold. `reports/round-4/r4-critic.md`, `r4-adjudicator.md`. |

Admission: coverage improved narrowly, depth/calibration unchanged, none harmed. First verifier lane failed without report, replacement named non-author replay passed; 440Hz scratch probe failed-fit, not evidence for 30Hz rule. No scalar score. SHONEN box 4 open.

## Round 5 verdict — 2026-10-12

| axis | verdict | before → after evidence |
|---|---|---|
| calibration | improved narrowly (disclosure only) | Before `358f625`, threshold rationale scattered, RMS prose `>.001` vs code `>=.001`, no consolidated control map. After, `corpus/knowledge/2026-10-12-threshold-calibration.md` states exact polarity, ten authored-file clean ranges/nearest arithmetic margins, control isolation/not exercised, and no LUFS acceptance window. Non-author `reports/round-5/r5-verifier.md` replayed 0/1/1/1/0 and checked values; Sol `r5-adjudicator.md` confines verdict to auditability, not tuned thresholds. |
| depth | unchanged | Same measurement code and gates; no new detector. `git diff 358f625 -- .shokunin/audio/corpus/fixtures/`; non-author `r5-adjudicator.md`. |
| coverage | unchanged | Ten canonical WAV hashes match `358f625`, same four SFX distinctness checks and three negative modes. Counting command `python3 -c "from pathlib import Path; print(sorted(p.stem for p in Path('.shokunin/audio/corpus/artifacts').glob('*.wav')))"`; `r5-verifier.md`. |

Admission: calibration disclosure improved narrowly, depth/coverage unchanged, none harmed. Numeric thresholds not tuned; malformed section-count receipt behavior untested and documented. No scalar score. SHONEN box 4 remains open pending whole-lane independent review.

## Round 6 verdict — 2026-10-12

| axis | verdict | before → after evidence |
|---|---|---|
| depth | improved narrowly | Before `3b02c31`, section count checked after split/FFT, and corrupt ffprobe failure left no JSON. New `--probe-invalid` creates three named scratch WAVs and persists expected `section count` / `decode` / `format` failures with exit 1; pre-FFT count guard corrects source ordering, but the even-length 144000-frame probe would not have triggered the old exception, so no direct exception-path regression is claimed. Non-author `reports/round-6/r6-verifier.md`, receipt `corpus/live/runs/20261012T170607093097Z-invalid/measurements.json`, Sol `r6-adjudicator.md`. Only named inputs and installed toolchain supported. |
| coverage | unchanged | Ten canonical hashes match `3b02c31`; four variants pass, normal/control/restore exits 0/1/1/1/0. Three invalid scratch controls are not new canonical categories; verifier report. |
| calibration | unchanged | Existing thresholds and control gates intact, no threshold tuning, round-5 LUFS caveat preserved; source diff and non-author reports. |

Admission: depth improved narrowly, none harmed; no scalar score or perceptual/security/production claim. SHONEN box 4 remains open pending whole-lane independent review.
