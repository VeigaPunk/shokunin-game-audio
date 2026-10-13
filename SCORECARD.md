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

## Round 19 verdict — 2026-10-12

| axis | verdict | before → after evidence |
|---|---|---|
| calibration | improved narrowly | Before `010f88b`, the +8-count 200Hz rejection existed but no integrated near-boundary pair. Opt-in +2/+3 one-frame controls measure 32/32768 = `.0009765625` pass and 33/32768 = `.001007080078125` sole internal-slope failure around the unchanged strict `> .001` FS/sample threshold on this SoX float32 decode path. Independent 16-mode replay and Sol adjudication: `reports/round-19/r19-verifier.md`, `r19-adjudicator.md`. |
| depth | unchanged | Same comparator and gate, no additional failure class or perceptual criterion. |
| coverage | unchanged | Thirteen canonical WAV hashes and five `_alt` checks preserved; scratch controls are not canonical content. |

Admitted with zero demonstrated scoped harm. This is local numerical resolution, not proof of audible quality or engine/production behavior; no equality test. Invalid mode is malformed-input scope only. Wave-1 scribe had no artifact and was cancelled. SHONEN box4 open. Operator paused after round 19; no round 20.

## Round 20 verdict — 2026-10-12

Operator dispatch `shk47-audio-r20` supersedes the round-19 pause line above. That line stays as history.

| axis | verdict | before → after evidence |
|---|---|---|
| coverage | improved narrowly | Before r19 report work commit `6648aae`: 16 verifier-table mode routes, no 200 Hz internal-gap route. After: 17th route `--probe-layer-third-join`. Non-author `reports/round-20/r20-verifier.md` exits `0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0`; receipt `corpus/live/runs/20261012T232009162006Z-layer-third-join/measurements.json` has sole `join200_probe` internal-gap failure `.030029296875` FS. Thirteen canonical hashes match `a905a26`. Scratch is not a 14th canonical. Sol `r20-adjudicator.md`. |
| depth | unchanged | Same `.03` FS gap predicate and existing runner; no new detector. First canonical-copy click (`20261012T231846536176Z`) failed centroid and gap and was not selected. |
| calibration | unchanged | `.03`, `.001`, and `6 dB` bounds unchanged. Target count 839 is geometry of this fixture, not a retuned threshold. |

Admission: coverage narrowly improved, depth and calibration unchanged, no demonstrated scoped harm. No scalar score. The selected scratch adds the original 220/330 Hz bed before the two-frame edit, so it is not a waveform-identical corruption of `stem_layer_third.wav`. No audible, engine, or production claim. SHONEN box 4 remains open.

## Round 21 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| calibration | improved narrowly | Before `b1af040`, selected round-20 984-count 200 Hz internal-gap rejection lacked a paired integrated 983-count positive. New opt-in 983/984 PCM16 gap controls straddle unchanged strict `> .03` gate: 0.029998779296875 FS passes and 0.030029296875 FS fails solely on gap. Named non-author `reports/round-21/r21-verifier.md` independently replayed 19 executions; Sol `r21-adjudicator.md`. Numeric decode-grid disclosure only, not perceptual threshold validation. |
| depth | unchanged | Same gap/section/outer gates and detector, no new gate. 19-run verifier preserves historical outcomes. |
| coverage | unchanged | No new canonical WAV, category or detector; 13 canonical hashes match `b1af040`, all five `_alt` checks pass. Scratch modes are controls, not content. |

Admitted narrowly: calibration improved; no demonstrated scoped harm. No scalar score. SHONEN box 4 remains open; no listening/engine/production/rights claim. Counting command: `python3 -c "from pathlib import Path; print(sorted(p.stem for p in Path('.shokunin/audio/corpus/artifacts').glob('*.wav')))"` → thirteen canonical names, unchanged from `b1af040`; report and receipts name exact SHA-256 comparisons. Work commit cited in final `.shokunin/reports/round-21/audio.md` after integration.

## Round 22 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| depth | improved narrowly | Before `14cf986`, `measure()` allowed matched 48 kHz mono native PCM24 (`failures: []`) alongside PCM16 because it only checked rate/channels. After, shared ffprobe `codec_name == pcm_s16le` and `bits_per_sample == 16` checks reject matched native PCM24 solely as `format: expected PCM16`, admit native PCM16. Non-author `reports/round-22/r22-verifier.md` independently replayed 19 modes, Sol `r22-adjudicator.md` judged scope. |
| coverage | unchanged | 13 original canonical WAV SHA-256 hashes match `14cf986`; five `_alt` comparisons and 19 historical mode outcomes hold. Two malformed-input width controls are not playable asset expansion. |
| calibration | unchanged | All existing numerical thresholds and predicates unchanged; no hearing, perceptual or codec population calibration. |

Admission: depth improved narrowly, zero demonstrated scoped harm. New normal JSON fields and `expected_pass` invalid-record schema are untested with unknown external strict consumers; no compatibility claim. WAVE_FORMAT_EXTENSIBLE valid bits are outside this encoded-width test. Counting commands: `git ls-tree -r --name-only 14cf986 .shokunin/audio/corpus/artifacts/ | wc -l` → 13; `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` yields six named records (four old + two width controls), receipt and exact exit in `r22-verifier.md`. No scalar score or SHONEN promotion; box4 remains open. Work commit cited in report-last `.shokunin/reports/round-22/audio.md`.

## Round 23 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| calibration | improved narrowly (auditability only) | Before `64e6088`, historical threshold table describes ten files and omits current 13-file/7-loop/4-section/3-gated-join/five-variant distribution. Appended dated current decision table and explicit historical section-count correction in `corpus/knowledge/2026-10-12-threshold-calibration.md`. Non-author `reports/round-23/r23-verifier.md` first FAIL, then correction follow-up PASS with full arithmetic/polarity/control check and seven fresh mode receipts; Sol `r23-adjudicator.md`. |
| depth | unchanged | Same measurement code and gate predicates; no new detector or control category. `git diff 64e6088 -- .shokunin/audio/corpus/fixtures/` empty. |
| coverage | unchanged | Thirteen canonical SHA-256 hashes match `64e6088`, five variant records and seven-mode normal/control/restore outcomes pass; no new WAV asset. |

Admitted narrowly after correction with zero demonstrated scoped harm. No scalar score, threshold retuning, audibility inference or external JSON compatibility claim. SHONEN box4 open. Counting commands: `python3 -c "from pathlib import Path; print(len(list(Path('.shokunin/audio/corpus/artifacts').glob('*.wav'))))"` → 13; code/receipt counts in `r23-verifier.md`. Work commit cited in final `.shokunin/reports/round-23/audio.md`.

## Round 24 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| depth | improved narrowly | Before `2a19811`, PROVINCE refusals were terse and SHONEN box4 open. After, appended task/action-effect decision table distinguishes audio content/proxies, engine/game/lore/rights/publishing refusals, mixed uncertainty and exact report/write paths. Named non-author `reports/round-24/r24-verifier.md` checked box4 only after 13 held-out classifications and bounded 47-first-parent-commit audit; Sol `r24-adjudicator.md`. This is a bounded review, not universal no-bleed or promotion. |
| coverage | unchanged | No new WAV/content category. Thirteen canonical hashes match `2a19811`, five variants pass in existing normal receipt. |
| calibration | unchanged | No gate/code/threshold changes; no stronger quality or rights inference. |

Admitted narrowly, no demonstrated scoped harm, no scalar score. Count command `git rev-list --first-parent --count 0f60e7658a63030ed054fb83ec7b830bea7be08b..2a198118a527baf749dbd2e23b6667a79a1ccf31` → 47; verifier and Sol reports distinguish 765 endpoint paths from 869 cumulative per-commit path entries, and cite mint/report exceptions. SHONEN all four boxes now checked, **without** promotion or rank change. Work commit cited in final `.shokunin/reports/round-24/audio.md`.

## Round 25 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| depth | improved narrowly | Before `30530e1`, the only rate/channel invalid WAV was 44100 Hz stereo PCM16, co-violating both equalities. New source-generated 48000Hz stereo PCM16 and 44100Hz mono PCM16 scratch each fail independently on `format` against 48000Hz mono PCM16 positive; non-author `reports/round-25/r25-verifier.md` confirmed direct `measure()` sole format failure under broad custom spec and 19 serial runner modes, Sol `r25-adjudicator.md`. |
| coverage | unchanged | No new asset/codec family, canonical WAV, or runner mode. 13 hashes, five variants, old 19 outcomes hold. |
| calibration | unchanged | `format_failures()` and all thresholds unchanged; stereo flattened SoX sample/FFT semantics are not mono-equivalent. |

Admission: depth improved, zero demonstrated scoped harm. Count command: read `corpus/live/runs/20261013T014025494866Z-invalid/measurements.json` `invalid_probes` → eight entries (six old + two new); exact command/exit in `r25-verifier.md`. Nineteen malformed setup shell exits127 produced no receipts, excluded. Four SHONEN boxes remain checked, no rank/promotion change, no scalar score. Work commit in final `.shokunin/reports/round-25/audio.md`.

## Round 26 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| depth | improved narrowly | Before `7c3241d`, five `_alt` pairs passed but no exact duplicate negative. Opt-in original `ui_clone`/`ui_clone_alt` WAVs have identical SHA-256 `57b3061d6a1b3ea7d94dcf4ea9c1bf6638d22e5284adaff37d3caf3d07b59ce1`; ordinary UI checks pass, duration and centroid delta both 0, sole existing distinctness failure. Non-author `reports/round-26/r26-verifier.md` 20-mode replay; Sol `r26-adjudicator.md`. |
| coverage | unchanged | Scratch control not canonical; thirteen WAV hashes, five existing variants and prior 19 outcomes preserved. |
| calibration | unchanged | Existing `.020 s OR .10` predicate and thresholds unchanged; neither boundary tested. |

Admitted narrowly with zero demonstrated scoped harm, no scalar score. Counting command: `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` → exit1 with sole `ui_clone_alt` distinctness failure in `corpus/live/runs/20261013T015341619139Z-ui-clone/measurements.json`; non-author exact command and exit in `r26-verifier.md`. No perceptual deduplication or promotion; four SHONEN boxes stay checked. Final work hash in `.shokunin/reports/round-26/audio.md`.

## Round 27 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| depth | unchanged | Exact duplicate zero/zero negative and five old positives remain; no new auditory validation. |
| coverage | unchanged | Two original opt-in scratch pairs, no new canonical WAV or supported category. |
| calibration | improved narrowly | Before `6666888`, no adjacent-frame distinctness duration polarity. After, independent 22-mode replay `reports/round-27/r27-verifier.md`: 5760→6719 frames, observed duration delta `0.019978999999999997` and centroid relative `.026103720992748162`, sole distinctness failure (exit1); 5760→6720, delta `0.020000000000000018`, centroid relative `.028427598871782873`, no failures (exit0). Sol `r27-adjudicator.md` admitted this bounded numeric transition. |

The latter binary float delta is **greater** than `.020`: no exact comparator-equality proof. Longer variants use their separately declared scratch duration spec, **not** the canonical `.120 s` UI duration spec; format/level/band checks remain. `.020 OR .10` thresholds, thirteen canonical hashes, previous twenty outcomes, five variants, eight invalid statuses and normal restoration held. No perceptual, production or promotion claim. Final work hash in `.shokunin/reports/round-27/audio.md`.

## Round 28 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| depth | unchanged | Exact-clone and duration branch controls remain; no auditory/semantic validation added. |
| coverage | unchanged | Original opt-in scratch centroid pair only, no new canonical WAV or category. |
| calibration | improved narrowly | Before `13a19e2`, no integrated near-`.10` centroid arm pair at duration delta zero. After, independent 24-mode replay `reports/round-28/r28-verifier.md`: baseline/variant both canonical UI .120s ordinary checks pass; k=1.11 relative centroid `0.09434076861679014`, duration delta0, sole distinctness failure (exit1); k=1.10 relative centroid `0.10454649711208937`, duration delta0, no failures (exit0). Sol `r28-adjudicator.md` admitted bounded two-point numeric polarity. |

Existing `.020 OR .10` predicate/thresholds, thirteen canonical hashes, five variants, prior 22 outcomes, eight invalid statuses and normal restoration held. Analytic multiplier sweep is nonmonotonic; no exact `.10` equality, smooth transition, perceptual difference, engine/production/rights/publishing or promotion inference. Failed candidate fits and corrected setup errors in wave reports are not counted as gate evidence. Final work hash in `.shokunin/reports/round-28/audio.md`.

## Round 29 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| depth | improved narrowly | Before `99b6c0a`, only higher-centroid comparisons tested near .10. Independent corrected 26-mode replay `reports/round-29/r29-verifier.md`: lower-centroid variant k=.95 absolute relative delta `0.09901901500217196`, zero duration delta, sole distinctness failure (exit1); k=.94 relative delta `0.1084606104331939`, zero duration delta, passes (exit0). A signed delta would miss the latter. Sol `r29-adjudicator.md` admits the bounded numeric direction check. |
| coverage | unchanged | Two opt-in original scratch controls, no new canonical WAV or category. |
| calibration | unchanged | Existing `abs` and `.020 OR .10` thresholds unchanged; no exact boundary or smoothness result. |

Both variants pass unchanged canonical UI .12s ordinary checks, and have centroids below baseline. Prior 24 outcomes, eight invalid statuses, thirteen canonical hashes, five variants, threshold objects and normal restoration held. Verifier's first 26 command-wrapper exit127 attempts produced no receipts; they are setup errors **excluded** from the corrected 26-run evidence. No perception, production, rights, engine, publishing or promotion claim. Final work hash in `.shokunin/reports/round-29/audio.md`.

## Round 30 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| depth | unchanged | Existing numeric distinctness tests remain; no new audio/semantic validation. |
| coverage | unchanged | Two opt-in original scratch orientations, no canonical WAV or category added. |
| calibration | improved narrowly | Before `6a36968`, only k=1→.95 had baseline denominator ratio `.09901901500217196` and failed. Independent corrected 28-mode replay `reports/round-30/r30-verifier.md` shows *identical two whole WAV byte strings swapped*: forward exit1 sole distinctness at duration0/ratio `.09901901500217196`; reverse exit0 at duration0/ratio `.10990133715464667`. Sol `r30-adjudicator.md` admitted numerical orientation sensitivity. |

All four paths pass canonical UI ordinary checks, existing `.020 OR .10` and denominator unchanged; thirteen canonical hashes, five variants, prior26 outcomes, eight invalid statuses, thresholds and normal restoration preserved. Verifier's first 28 exit127 command-wrapper attempts produced no receipts and are excluded from corrected 28-run evidence. No normative symmetry, exact cutoff equality, auditory/perceptual/production/rights/engine/publish/promotion claim. Work hash in `.shokunin/reports/round-30/audio.md`.

## Round 31 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| depth | unchanged | Existing controls remain; this is no new audio/semantic validation. |
| coverage | unchanged | One opt-in original scratch joint pair; no new canonical WAV/category. |
| calibration | improved narrowly | Before `c1c6c96`, zero/zero and separate near-bound controls, not both nonzero below. Independent 29-mode replay `reports/round-31/r31-verifier.md`: 5760→6719 frame pair, measured duration delta `0.019978999999999997` (<.020), relative centroid delta `0.09964036511023265` (<.10); sole distinctness failure exit1. Sol `r31-adjudicator.md` admits bounded joint false-branch observation. |

Longer variant uses separately declared scratch expected duration `6719/48000`, **not** canonical UI `.120 s`; ordinary format/level/band checks retained. Both sample count and phase change: no causal isolation or universal OR/equality claim. Prior28 outcomes, eight invalid statuses, thirteen canonical hashes, five variants, threshold objects and normal restoration held. Failed k=1.0 centroid fit `.1353` and corrected relative-path setup errors excluded. No perception, production, rights, engine, publishing or promotion claim. Work hash in `.shokunin/reports/round-31/audio.md`.

## Round 32 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| depth | improved narrowly | Before `ae9c941`, joint nonzero-below negative but no joint duration-below/centroid-above positive. Independent 30-mode replay `reports/round-32/r32-verifier.md`: 5760→6719 frames, duration delta `0.019978999999999997` (<.020) and centroid relative `0.1059638814557548` (>=.10), both nonzero; no failures, exit0 through centroid arm. Sol `r32-adjudicator.md` admits bounded numeric mixed-input outcome. |
| coverage | unchanged | One opt-in original scratch pair, no canonical WAV/category. |
| calibration | unchanged | Existing OR, `.020/.10` cutoffs and ordinary tolerance unchanged; no exact equality/calibration retune. |

Longer variant ordinary check uses separately declared scratch expected duration `6719/48000`, **not** canonical UI `.120 s`; both waveform length and phase change, so no causal independence. Prior29 outcomes, eight invalid statuses, thirteen canonical hashes, five variants, threshold objects and normal restore held. Verifier's initial 30 exit2 mistyped-path attempts produced no receipts and are excluded from corrected 30-run evidence. No perception, production/rights/engine/publishing/promotion claim. Work hash in `.shokunin/reports/round-32/audio.md`.

## Round 33 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| depth | unchanged | Same ordinary checks and OR rule on one more file; no auditory/semantic control. |
| coverage | improved narrowly | Before `b8e3e5c`, 13 canonical WAVs and two UI members. Independent 31-run replay `reports/round-33/r33-verifier.md` confirms 14 deterministic canonical WAVs incl original ui_third .20s/9600 frames 48k mono PCM16, SHA `734a0a47077f5b614b5d51d486b88a51940c7d61ecea0878642b60a0103513bc`, ordinary checks pass; ui→third comparison passes duration-only (.08000000000000002s/.00018103031409457665), ui_alt→third passes both (.04000000000000001s/.3207185389302337). Sol `r33-adjudicator.md` admits only measured analytical coverage. |
| calibration | unchanged | Existing `.020 OR .10` cutoffs, generic five `_alt` comparisons, and ordinary limits unchanged. |

Thirteen older canonical hashes/metrics held, prior30 outcomes, eight invalid statuses, thresholds and normal restoration held. Executor's two initial helper-path failures excluded. Duration-only distinction from `ui` is **not** spectral/perceptual novelty. No listening, asset quality, production, rights, engine, publishing or promotion inference. Work hash in `.shokunin/reports/round-33/audio.md`.

## Round 34 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| depth | unchanged | Existing format/level/duration/whole-wave centroid checks applied to one additional original WAV; no new measurement dimension or audition. |
| coverage | **improved narrowly** | Before `d6bfc6e`, 14 canonical WAVs, impact family two; non-author 32-run replay `reports/round-34/r34-verifier.md` verifies 15 deterministic canonical WAVs incl `impact_third` .40s/19200 frames 48k mono PCM16, SHA `d14376241f409f07edde30fbcef86b5f060ff36f731b7578fd9934d1dc1b39bf`, ordinary failures []; two explicit impact-family pairs pass both numeric duration and centroid arms. Named Sol `r34-adjudicator.md` admits only analytical fixture coverage. |
| calibration | unchanged | `.020 s OR .10` thresholds, five generic `_alt` comparisons and ordinary limits unchanged. |

Old fourteen canonical SHA/metrics, UI-family records, prior31 outcomes, eight invalid statuses and restored normals held; replay 11 exit0/21 expected exit1/no runner setup failures. Executor's two failed helper path/type setups excluded. Each `.08000000000000002 s` impact duration delta alone would pass OR; centroid scalar does not show spectral-distribution/perceptual novelty. No audition, quality, production, rights, engine, publishing or promotion inference. Work hash in `.shokunin/reports/round-34/audio.md`.

## Round 35 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| depth | unchanged | Existing format/level/duration/whole-wave centroid checks on one more original WAV; no new detector or audition. |
| coverage | **improved narrowly** | Before `56f2b0f`, 15 canonical WAVs and two movements; named non-author 33-run replay `reports/round-35/r35-verifier.md` verifies 16 canonical WAVs including `movement_third` .30s/14400 frames 48k mono PCM16, SHA `0e5f815e1987e13646170571e1f1e977b25e3566d90ebcca558c72ed07851d44`, ordinary failures []; explicit comparisons pass both duration and centroid arms. Sol `r35-adjudicator.md` admits analytical coverage only. |
| calibration | unchanged | `.020 s OR .10` cutoffs, ordinary limits and five generic `_alt` comparisons unchanged; new fixture inherits the movement band. |

Old fifteen canonical SHA/metrics, UI/impact family records, prior32 outcomes, eight invalid statuses and normal restores held; replay 12 exit0/21 expected exit1/no runner setup failures. Wave-one command/path failures excluded. Each `.06 s` movement duration gap alone passes OR; centroid scalar does not show spectral-distribution/perceptual novelty. No audition, quality, production, rights, engine, publishing or promotion inference. Work hash in `.shokunin/reports/round-35/audio.md`.

## Round 36 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| depth | unchanged | Existing format/level/loop-seam/whole-wave centroid checks on one more original WAV; no new detector or audition. |
| coverage | **improved narrowly** | Before `1fdccc4`, 16 canonical WAVs/two ambience members; named non-author 34-run corrected replay `reports/round-36/r36-verifier.md` confirms 17 canonical WAVs incl `ambience_third` exactly 2s/96000 frames 48k mono PCM16, SHA `c2c8e0bb2385bc93b39c70b719d0f56553c771969986ef1f732d24af5677d404`, ordinary/loop checks pass; both explicit ambience pair comparisons pass centroid-only at duration delta zero. Sol `r36-adjudicator.md` admits analytical coverage only. |
| calibration | unchanged | `.020 s OR .10` cutoffs, ordinary/loop limits and five generic `_alt` comparisons unchanged; new fixture inherits ambience band. |

Old sixteen canonical SHA/metrics, UI/impact/movement family records, prior33 outcomes, eight invalid statuses and restored normals held; corrected replay 13 exit0/21 expected exit1. Verifier disclosed 34 initial wrapper attempts exit127 without receipts, excluded setup errors; executor relative-path error excluded. Centroid scalar cannot establish spectral-distribution/perceptual novelty and seam metrics do not prove audible seamlessness. No audition, quality, production, rights, engine, publishing or promotion inference. Work hash in `.shokunin/reports/round-36/audio.md`.

## Round 37 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| depth | unchanged | No deeper audio/perceptual or full-spectrum check. |
| coverage | unchanged | Seventeen canonical WAVs remain; one opt-in scratch pair is not a canonical family expansion. |
| calibration | **improved locally** | Before `83395d1`, no integrated equal-duration ambience nonduplicate negative. Named non-author `reports/round-37/r37-verifier.md` 35-run replay verifies `--probe-ambience-centroid-below` exit1: 2s/96000 frames 48k mono PCM16 loops, ordinary/seam checks pass; duration delta **0.0**, centroid-relative **0.06585562259644766** (`0 < delta < .10`), generic `_alt` `passed:false`, sole variant distinctness failure. Sol `r37-adjudicator.md` admits this one local numeric negative, not universal cutoff calibration. |

Seventeen old canonical SHA/metrics, five generic `_alt`, four family groups, thresholds, sections, prior34 outcomes, eight invalid statuses and restored normal held (35 receipts: 13 exit0/22 expected exit1/no replay setup). Scratch SHA baseline `281e9a25191825bd062f854de6f9b85f6a5902200e0cd1027e36a225422a901c`, variant `cd48ad3f1e4020c10225d65904358a1ea1e7f18d28050e858dec9a9b7feed8a9`. Wave-one SciPy/path setup errors excluded; no failed numeric fits. No perceptual/spectral similarity, audible seamlessness, quality, production, rights, engine, publishing or promotion inference. Work hash in `.shokunin/reports/round-37/audio.md`.

## Round 38 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| depth | unchanged | Existing measurements and OR rule, no new audio behavior or audition. |
| coverage | unchanged | Seventeen canonical WAVs remain; one opt-in scratch positive does not enlarge canonical family coverage. |
| calibration | **improved locally** | Before `c713fb6`, local equal-duration ambience negative R37 `.06585562259644766` alone. Named non-author `reports/round-38/r38-verifier.md` 36-run replay verifies `--probe-ambience-centroid-above` exit0: 2s/96000 frames 48k mono PCM16 loops ordinary/seam pass, duration delta **0.0**, baseline-relative centroid **0.10336093117966988** (`>.10`, `<.13`), generic `_alt` passed:true solely centroid. R37 negative remains exit1 sole distinctness. Sol `r38-adjudicator.md` admits only two-point local polarity, not exact/universal cutoff validation. |

Seventeen old canonical SHA/metrics, five generic `_alt`, four family groups, thresholds/sections, prior35 outcomes, eight invalid statuses/restores held; 36 receipts 14 exit0/22 expected exit1. Scratch SHA baseline `04d8d334553ecb0c155a4be37397edda8f01cfbe992df4bd2e9b3e474d1189e0`, variant `7bd6ae805a6a5ff2c15ba14470ba1d312c40768c97c1704629382ed76292bd77`. One wrapper exit127 before replay excluded; alt path setup excluded; executor exploratory .0658556 and other out-of-band numeric attempts, including .070 amplitude .14123783252085534, are failed fits, not gate results. No perceptual/spectral novelty or similarity, audible seamlessness, quality, production, rights, engine, publishing or promotion inference. Work hash in `.shokunin/reports/round-38/audio.md`.

## Round 39 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| depth | unchanged | Existing generic `_alt` denominator and OR rule, no new measurement dimension. |
| coverage | unchanged | Seventeen canonical WAVs remain; opt-in scratch modes do not enlarge the canonical corpus. |
| calibration | **improved locally** | Before `03fc02d`, ambience controls did not reverse baseline roles for the **same** looped pair. Named non-author `reports/round-39/r39-verifier.md` confirms equal-duration 108/114 Hz .22-amplitude pair low-baseline forward relative **.10535223771748284** passes exit0 and high-baseline reverse relative **.09531100957920152** fails exit1 solely generic distinctness. Same exact WAV hashes and zero duration delta; individual ordinary/seam checks pass. Sol `r39-adjudicator.md` admits only local denominator orientation, not exact/universal cutoff proof. |

Non-author 38-run replay: 15 exit0/23 expected exit1, prior36 subset 14/22 held; old17 SHA/metrics, five generic `_alt`, four family groups, thresholds/sections, eight invalid statuses and normal restore held. Scratch low/high SHA `7f4cdfefa6e52a8ff44268396b5c09ea459a648a5ac4cad0f42722fe5fc29938`/`24203978fe84384db6686e8cf065e1f06f2eb966e88e92578f5da1bb9c5b9482`. The critic's transient overwritten executor candidate and other exploratory misses were **numeric failed fits**; wrapper exit127 and helper-path exit1 were **setup errors**, neither counted in gate results. No perceptual/spectral similarity, audible seamlessness, quality, production, rights, engine, publishing or promotion inference. Work hash in `.shokunin/reports/round-39/audio.md`.

## Round 40 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| depth | unchanged | Existing outer-loop endpoint `> .03 FS` rule and slope rule unchanged; no new detector. |
| coverage | unchanged | Seventeen canonical WAVs remain; opt-in scratch bracket is not canonical corpus expansion. |
| calibration | **improved locally** | Before `9b21235`, R21 bracketing was at an **internal** section join, not the outer first/last loop endpoint. Named non-author `reports/round-40/r40-verifier.md` 40-run replay confirms 983/32768=**.029998779296875** FS pass exit0, 984/32768=**.030029296875** FS sole outer endpoint failure exit1; both 2s/96000-frame 48k mono PCM16, slope0, centroid 170.56815710368392/170.73676058919554 within band. Sol `r40-adjudicator.md` admits fixture-local adjacent-PCM16-count bracket only; no exactly-.03 or universal threshold claim. |

Non-author 40-run replay: 16 exit0/24 expected exit1, prior38 subset 15/23 held; old17 SHA/metrics, generic five `_alt`, four family groups, thresholds/sections, eight invalid statuses and normal restore held. Scratch SHA 983 `2f7dd5517ff2cfe380cc6710e6ac99d0939d95dece81d0cdedaddcee95b20286` / 984 `c5ca108680557a584cca19dead3a900a382ed8dfa1252ab994196624c0eb94c6`. First alt and executor scratch candidates met endpoint counts but failed centroid band; executor's low-frequency/amplitude/headroom sweeps also failed numeric fit. Helper/path errors were setup errors, not gate outcomes. Executor initially misstated first/last counts, corrected against SHA-pinned WAVs before replay. Synthetic .7 DC offset is **not** production sound design. No audible seam, quality, production, rights, engine, publishing or promotion inference. Work hash in `.shokunin/reports/round-40/audio.md`.

## Round 41 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| depth | unchanged | Existing outer loop slope comparator `>.001 FS/sample` and endpoint `>.03 FS` unchanged. |
| coverage | unchanged | Seventeen canonical WAVs remain; scratch opt-in boundary modes are not canonical corpus expansion. |
| calibration | **improved locally** | Before `d1a1a4d`, R3 outer side-slope only had a far-above failure, no adjacent decoded PCM16-count pass/fail. Named non-author `reports/round-41/r41-verifier.md` 42-run replay verifies 32/32768=**.0009765625** pass exit0 and 33/32768=**.001007080078125** sole slope failure exit1. Both endpoints fixed **39/32768=.001190185546875** (<.03), centroid150.16139474032187/152.54369633957694Hz within 5–200. Sol `r41-adjudicator.md` admits only fixture-local outer slope numerical bracket. |

Non-author 42 serial receipts: 17 exit0/25 expected exit1, prior40 subset16/24; old17 SHA/metrics, generic five `_alt`, four family groups, thresholds/sections, eight invalid statuses and normal restore held. Scratch SHA32 `0bc9c6f07b53b13336b253db069cc57702e9520634106eabf85fc27e329b4547` / SHA33 `b86a34d343a57e943ab4289cb67b992b8597d93002f3b4a7ef9981e6b30952fb`. Executor transient counts 0/1, alt initial centroid ~2801Hz and parent first builder centroid296Hz/slope .002166748046875 were **numeric failed fits**, not successful gate receipts; helper relative-path/str errors were **setup errors**. `.001*32768=32.768`: no exactly-.001 equality claim, audible smoothness/quality/production/rights/engine/publishing or promotion inference. Work hash in `.shokunin/reports/round-41/audio.md`.

## Round 42 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| depth | unchanged | Existing combined `peak >= .95 or rms < .001` comparator unchanged. |
| coverage | unchanged | Seventeen canonical WAVs remain; opt-in scratch peak modes do not establish broad coverage. |
| calibration | **improved locally** | Before `3b4f10b`, no adjacent decoded PCM16 peak-count bracket at `.95` for the combined level check. Named non-author corrected `reports/round-42/r42-verifier.md` fresh 44-run replay: peak31129/32768=**.949981689453125** pass exit0, peak31130/32768=**.95001220703125** sole combined level failure exit1, RMS -3.4559832611867107/-3.455749141202171dBFS far above `.001`, UI centroids1002.249073839976/1000.2482261395106Hz within 250–4000. Sol `r42-adjudicator.md` admits only local numerical peak branch isolation. |

Corrected non-author 44 distinct fresh receipts: 18 exit0/26 expected exit1, prior42 subset17/25; old17 SHA/metrics, five generic `_alt`/four family groups, thresholds/sections, eight invalid statuses and normal restore held. **First verifier draft falsely cited historical R41 and author receipts as fresh and was rejected**; corrected receipt ledger 20261013T053345–053440 independently checked. SHA31129 `7e6c11325d27c1e0d2acaa11975fae1180a8186d2449816fa38f2eabbab93e14`/31130 `8e7cf36d2a78ee78446b12076361d69284928019ae2bc0072bd63a1fe3c57b3d`. Final candidates had no numeric fit failures; critic relative-path, alt Python TypeError, verifier await TypeError after completed runner #1 are setup/orchestration errors, not runner gate failures. `.95*32768=31129.6`, so no exactly-.95 equality, audible clipping/quality/production/rights/engine/publishing or promotion inference. Work hash in `.shokunin/reports/round-42/audio.md`.
