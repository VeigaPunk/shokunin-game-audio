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

## Round 7 verdict — 2026-10-12

| axis | verdict | before → after evidence |
|---|---|---|
| depth | improved narrowly | Before `cba2748`, only even 144000-sample short control existed, leaving the old odd-length split exception unexercised. Named 101-frame odd input raises `ValueError` in isolated `3b02c31` function (non-author `reports/round-7/r7-verifier.md`), while current `--probe-invalid` receipt `corpus/live/runs/20261012T171718939143Z-invalid/measurements.json` reports `section count` 101/192000 without traceback. Precheck code itself dates to round 6; new gain is direct regression control and structured fourth receipt, not old CLI crash/general fix. Sol `r7-adjudicator.md`. |
| coverage | unchanged | Ten canonical hashes match `cba2748`; four variant checks pass; first three invalid cases and normal/flat/slope/failing/restore outcomes preserved. Odd scratch is not a canonical category. |
| calibration | unchanged | No threshold changes or new LUFS window; local proxy limitations remain. |

Admission: depth narrowly improved, none harmed, no scalar score. Nine verifier misquoted shell attempts exit 127 and are excluded; corrected replay is cited above. SHONEN box 4 remains open.

## Round 8 verdict — 2026-10-12

| axis | verdict | before → after evidence |
|---|---|---|
| coverage | improved narrowly | Before `75c95d9`: ten canonical WAVs, no separate synchronized-grid companion. New `stem_layer.wav` is eleventh original 4s/192000-frame 120Hz two-section file; non-author `reports/round-8/r8-verifier.md` normal receipt `corpus/live/runs/20261012T172620813098Z-normal/measurements.json` measures 13.9793723 dB amplitude contrast; matched flat120 receipt `172637297691Z-layer-flat` gives 0 dB sole contrast failure. Ten old hashes, four variants preserved; Sol `r8-adjudicator.md`. Numeric alignment only, not adaptive behavior. |
| depth | unchanged | Same generic and section-check method parameterized 30/120 Hz; no broader detector established. Old probes pass their expected negative behavior. |
| calibration | unchanged | Old thresholds unchanged; `section_energy_delta_db` is an amplitude-ratio misnomer and top-level `thresholds.section_component_hz: 30` is legacy, while per-section layer `component_hz:120` is authoritative. Disclosed, not empirically tuned. |

Admission: coverage narrowly improved, none harmed within declared numeric fixture scope; seven verifier setup exits 127 excluded; no scalar score or audible/engine/production claim. SHONEN box 4 remains open.

## Round 9 verdict — 2026-10-12

| axis | verdict | before → after evidence |
|---|---|---|
| calibration | improved narrowly (disclosure/auditability only) | Before `aaf4801`, top-level `thresholds.section_component_hz:30` could misstate 120Hz layer and `section_energy_delta_db` labeled 20log10(component amplitude ratio) as energy. New receipts use per-section `component_hz` alone and `component_amplitude_contrast_db`; eight paired normal/flat30/flat120 records have zero numeric delta; non-author `reports/round-9/r9-verifier.md` and Sol `r9-adjudicator.md`. No threshold tuning. Breaking JSON schema for unknown external readers, disclosed. |
| depth | unchanged | Same builder, FFT, gates and outcomes; seven corrected replay exits 0/1/1/1/1/1/0. |
| coverage | unchanged | Eleven canonical WAV hashes match `aaf4801`, four variants remain passing; no new file/category. |

Admission: disclosure improved narrowly, none demonstrated harmed within deterministic fixture scope; no scalar score. One typo exit 2 excluded; historical JSON unchanged. No compatibility/perceptual/production claim. SHONEN box 4 remains open.

## Round 10 verdict — 2026-10-12

| axis | verdict | before → after evidence |
|---|---|---|
| depth | improved narrowly | Before `f32ab7f`, internal 2s layer boundary unmeasured. New decoded-PCM adjacent gap at frames 95999→96000 gates `stem_layer`/`join_probe` at strict `> .03` FS; non-author `reports/round-10/r10-verifier.md` receipt `corpus/live/runs/20261012T174637561631Z-layer-join/measurements.json` shows selected control `.030914306640625` sole failure; clean layer `.00018310546875` passes. Sol `r10-adjudicator.md`. Single-edge proxy only. |
| coverage | unchanged | Eleven canonical WAV hashes match `f32ab7f`, four variants pass; scratch probe not new category. Old controls unchanged. |
| calibration | unchanged | `.03` reused as fixture-local comparator, not empirically tuned to audibility; equality passes. All-section additive gap telemetry is not an expanded gate. |

Admission: depth narrowly improved, no demonstrated scoped harm, no scalar score. Earlier failed-fit candidates and unused alternate documented, not passes. No audible/engine/production claim. SHONEN box 4 open.

## Round 11 verdict — 2026-10-12

| axis | verdict | before → after evidence |
|---|---|---|
| depth | improved narrowly | Before `f15fe55`, 2s internal join only had a gap gate. New side-slope mismatch `abs((x[96001]-x[96000])-(x[95999]-x[95998]))` on decoded PCM, strict `> .001` FS/sample, detects selected probe's `.00115966796875` as sole failure while its gap `.00018310546875` passes .03. Clean layer `.000762939453125` passes; old join remains sole-gap failure. Non-author `reports/round-11/r11-verifier.md`, Sol `r11-adjudicator.md`. Exact-edge proxy only. |
| coverage | unchanged | Same eleven canonical WAV hashes, four variants and prior controls; slope probe is scratch, not content category. |
| calibration | unchanged | .001 borrowed from outer slope comparator without audibility study; equality passes by code but no equality-valued probe run. New telemetry can affect unknown strict JSON readers. |

Admit bounded depth, no demonstrated harm in deterministic fixture scope, no scalar score. Verifier's failed orchestration/receipt inspection attempts not credited as checks. No audible/engine/production claim. SHONEN box 4 open.

## Round 12 verdict — 2026-10-12

| axis | verdict | before → after evidence |
|---|---|---|
| coverage | improved narrowly | Before `f986933`, 11 canonical WAVs, four SFX variants, one measured 120Hz two-half layer. New original 4s 180Hz `stem_layer_alt.wav` has SHA `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9` matching selected scratch; 180Hz contrast 10.457250572050896dB, internal/outer gates pass, centroid relative delta .46179931396667484 (> .10), fifth `_alt` record passes. Non-author `reports/round-12/r12-verifier.md`, Sol `r12-adjudicator.md`. |
| depth | unchanged | Same detectors and old negative controls, no matched flat180 negative; explicit new section frequency applies old checks to new fixture. |
| calibration | unchanged | Existing 6dB, .03 FS, .001 FS/sample and .10 centroid rules reused; no listening or threshold tuning, unknown strict JSON readers. |

Admit bounded synthetic coverage, no demonstrated scoped harm, no scalar score. Quoted-command and typo exit127 setup failures and handwritten hash typo corrected, never passes. No audible/engine/production claim. SHONEN box 4 open.

## Round 13 verdict — 2026-10-12

| axis | verdict | before → after evidence |
|---|---|---|
| depth | improved narrowly | Before `db36a69`, passing 180Hz stepped layer had no matched flat180 negative. New original opt-in `.036*sin(2π180t)` PCM16 scratch with two valid equal 180Hz amplitudes `.03599800833461317` FS gives signed contrast 0dB and sole `<6dB` section failure; generic/outer/internal pass. Non-author `reports/round-13/r13-verifier.md`, Sol `r13-adjudicator.md`. |
| coverage | unchanged | Same 12 canonical WAVs/five `_alt` records; scratch control is not new content. |
| calibration | unchanged | Existing >=6dB, <=.03FS and <=.001FS/sample local bounds unchanged; no audibility study. Normal JSON exactly equal; strict external readers untested. |

Admit bounded depth, no demonstrated scoped harm, no scalar score. Verifier TypeError, ten setup exits 127 and flawed text hash discarded. Numeric polarity only; no audible/engine/production inference. SHONEN box 4 open.

## Round 14 verdict — 2026-10-12

| axis | verdict | before → after evidence |
|---|---|---|
| depth | improved narrowly | Before `ce3233a`, passing 180Hz layer had no gap-only 180Hz negative. New opt-in scratch with original 220/330Hz bed fails solely on decoded internal gap `.044403076171875` FS (> .03), side-slope 0 <= .001, valid 180Hz contrast 10.457775175842691dB and generic/outer pass. Non-author `reports/round-14/r14-verifier.md`, Sol `r14-adjudicator.md`. Gate-isolated, **not** waveform-identical canonical corruption. |
| coverage | unchanged | 12 canonical hashes/five variant records retained; scratch is not new content. |
| calibration | unchanged | Existing local `.03` FS, `.001` FS/sample and 6dB bounds not retuned; no audible/field study. |

Admit bounded depth, no demonstrated scoped harm, no scalar score. Runner decoded gap authoritative vs worker direct scaling decimal. No audible/engine/production inference, strict external JSON readers untested. SHONEN box4 open.

## Round 15 verdict — 2026-10-12

| axis | verdict | before → after evidence |
|---|---|---|
| depth | improved narrowly | Before `0928e9e`, clean 180Hz layer passed gap/slope checks but lacked a waveform-matched 180Hz slope-only negative. Original opt-in single-frame +13-count (39→52 at 96001) scratch fails solely on decoded internal side-slope `.001251220703125` FS/sample (> .001), while gap `.0003662109375` FS, valid 180Hz contrast 10.457250605879763dB, generic and outer gates pass. Non-author `reports/round-15/r15-verifier.md`; Sol `r15-adjudicator.md`. |
| coverage | unchanged | 12 canonical WAV hashes unchanged vs `0928e9e`; five `_alt` records pass. Scratch control is not new content. |
| calibration | unchanged | Existing `.001` FS/sample, `.03` FS and 6dB local bounds unaltered; no perceptual calibration. |

Admit bounded gate depth, no demonstrated scoped harm, no scalar score. Non-author twelve-mode serial replay preserved prior failures and normal/restore equality. Executor's first count direction was corrected from actual PCM bytes. Threshold proxy is not audibility/engine/production evidence; strict external JSON readers untested. SHONEN box 4 open.

## Round 16 verdict — 2026-10-12

| axis | verdict | before → after evidence |
|---|---|---|
| depth | improved narrowly | Before `35d978c`, passing +10.457dB 180Hz canonical and failing flat 0dB negative lacked a **valid reversed-order** section negative. New original opt-in `.050→.015` 180Hz scratch has valid decoded amplitudes `.04999787162649197/.014999921578770435` FS, signed contrast `-10.457250572050894dB` (<+6dB) sole failure, internal gap `.001190185546875` FS and slope `.00079345703125` FS/sample plus generic/outer pass. Non-author `reports/round-16/r16-verifier.md`, Sol `r16-adjudicator.md`. |
| coverage | unchanged | 12 canonical WAV hashes match `35d978c`, five variants pass; scratch not new content. |
| calibration | unchanged | Same local >=6dB contrast, .01 component amplitude, .03 gap and .001 slope bounds; no perceptual study or retuning. |

Admit bounded numeric direction-depth move; no demonstrated scoped harm, no scalar score. Independent 13-mode serial replay preserved prior failures and normal/restore equality; verifier initially printed false `{}` failure sets and corrected table against receipts before adjudication. Alternate misquoted SoX exit127 and invalid fit are not passes. No audible/engine/production assertion, strict external JSON readers untested. SHONEN box4 open.

## Round 17 verdict — 2026-10-12

| axis | verdict | before → after evidence |
|---|---|---|
| coverage | improved narrowly | Before `6fb9e80`, twelve original measured canonical WAVs included stepped 120Hz/180Hz layers. New original separately measured `stem_layer_third.wav` at 200Hz makes thirteen; SHA `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445`. Decoded valid section amplitudes `.014999984892417233/.04999803906398615` FS, +10.457242997641432dB contrast; internal gap `.000396728515625` FS and slope `.00091552734375` FS/sample plus outer/generic pass. Non-author `reports/round-17/r17-verifier.md`, Sol `r17-adjudicator.md`. |
| depth | unchanged | Existing 200Hz bin in section helper and generic/join/outer gates reused; no new gate or rejection class. |
| calibration | unchanged | Numeric thresholds unchanged; `.00091552734375` slope is close to `.001` local bound, not a robustness or perceptual study. |

Admit bounded frequency-point coverage; no demonstrated scoped harm or scalar score. Independent 13-mode serial replay (invalid mode checks invalid files, not canonical) preserved twelve old hashes, prior failures, five variants and normal/restore equality. Rejected verifier spawn TypeError and alternate relative-path setup failure excluded. New canonical is not evidence of audible/musical distinctness, adaptive engine behavior, external JSON compatibility, security or production quality. SHONEN box4 open.

## Round 18 verdict — 2026-10-12

| axis | verdict | before → after evidence |
|---|---|---|
| depth | improved narrowly | Before `7083a3f`, passing canonical 200Hz layer lacked a matched slope-only negative. New opt-in canonical-copy scratch changes solely frame 96001 **43→51** (+8 counts), SHA `e7c98cc5af858d8dab2be01a4f76382e06008573a017909c2760e68a585b1881`; decoded internal slope `.00115966796875` FS/sample strictly >.001 as sole failure. Gap `.000396728515625` FS <=.03, valid 200Hz contrast +10.457243020771665dB and generic/outer gates pass. Non-author `reports/round-18/r18-verifier.md`; Sol `r18-adjudicator.md`. |
| coverage | unchanged | All 13 canonical WAVs match `7083a3f` Git blobs, five variants pass; scratch is not new playable content. |
| calibration | unchanged | Existing local .001 FS/sample, .03 FS and >=6dB bounds reused, not perceptually calibrated; +8 excess is target failure, not upper-bound overshoot. |

Admit bounded numeric gate depth with no demonstrated scoped harm or scalar score. Fourteen-mode non-author replay preserved prior failures and normal/restore equality; invalid mode tests invalid fixtures, not canonicals. Executor initial unusable/overshoot wording corrected; alternate +3/+2 and setup failures excluded from selected evidence. No audible/engine/production claim, strict external JSON readers untested. SHONEN box4 open.
