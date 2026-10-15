# audio scorecard — mint

Owned axes: depth, coverage, calibration. Scores remain unassigned without a
quality rubric; a row count is a measurement, not a score or verdict.

| axis | score | evidence / counting command | last change |
|---|---|---|---|
| depth | unmeasured | mint: no rounds yet | mint |
| coverage | unmeasured | mint: no rounds yet | mint |
| calibration | unmeasured | mint: no rounds yet | mint |

planned: r64 (devin, ADMIT) — valid-bits step-map pinned as tracked boundary pairs (u8|s16le|s24le|s32le|NONE|s64le, seven boundaries, envelope-gated). Next: stdin-detection dead-combination surface (boundary-measured, undrained pending_buffer EPIPE + prefetch offset loss), preemptor-collision controls (gsrt@16/hcom@65+128 on RIFF files), non-USING_FFMPEG build UNKNOWN (source-only), f24le promotion family. Prior: r62 — SoX 3,839 frame gap resolved as ffmpeg packet-residue (act-autodetect byte-256 0x84 → ffmpeg bridge → valid17→pcm_s24le → 8192+3328 packets → mod-3 tails dropped); valid24/32 family landed; 84-ledger + verifier byte-exact. Next: fixture hardening vs byte-256 act-collision fragility, a third valid-bits family (e.g. mask/GUID variation), or a distinct axis move.
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

## Round 43 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| depth | unchanged | Existing combined `peak >= .95 or rms < .001` comparator and thresholds unchanged. |
| coverage | unchanged | Seventeen canonical WAVs remain; opt-in scratch crest modes do not establish broad coverage. |
| calibration | **improved locally** | Before `fc638d9`, R42 bracketed peak arm only, no RMS-side near-`.001 FS` straddle with peak false. Named non-author `reports/round-43/r43-verifier.md` fresh 46-run replay: crest46 decoded RMS **.0009918604133909925 FS** below .001 exit1 sole combined level failure, crest47 **.0010130695326051166 FS** above .001 exit0 no failures; peaks .00140380859375/.001434326171875 both far below .95, UI centroids1333.1671762128612/2221.1801421740442Hz within 250–4000. Sol `r43-adjudicator.md` admits only fixture-local RMS branch isolation. |

Non-author **46 distinct fresh** receipts: 19 exit0/27 expected exit1, prior44 subset18/26; old17 SHA/metrics, five generic `_alt`/four family groups, thresholds/sections, eight invalid statuses and normal restore held. SHA46 `869d1e5ada618a3c9daaa7be3100c9a01dc1342df63d732355a23a306130adfc`/47 `4c8c67a08558f14ad0642cac99563056407eeeecdc6b05e974f7b24cf74804b3`, independently SHA-identical executor/alt original generation. Centroids **not faithful 1kHz** from tiny-count PCM quantization. No final numeric failed fits; executor/alt/critic helper relative-path/API errors were setup, not gate. Crest counts adjacent, **RMS values not proven adjacent grid**; no exactly-.001 equality, audible silence/quality/production/rights/engine/publishing or promotion inference. Work hash in `.shokunin/reports/round-43/audio.md`.

## Round 44 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| depth | unchanged | Ordinary `abs(ffprobe_duration - spec[0]) > .001 s` comparator and thresholds unchanged. |
| coverage | unchanged | Seventeen canonical WAVs remain; two scratch UI duration points do not establish broad coverage. |
| calibration | **improved locally** | Before `8009269`, ordinary ±1ms UI duration had no source-generated near-tolerance pass/fail pair. Named non-author `reports/round-44/r44-verifier.md` fresh 48-run replay: 5807 ffprobe `.120979s`, parsed delta `.0009790000000000076` exit0; 5809 `.121021s`, delta `.001021000000000008` exit1 sole duration failure. Peaks `.27947998046875`, RMS `-16.431537076901346/-16.432818198672756dBFS`, centroids `1132.7351495568296/936.6642301482127Hz`; other UI gates pass. Sol `r44-adjudicator.md` admits only this local comparator calibration. |

Non-author **48 distinct fresh** receipts: 20 exit0/28 expected exit1, prior46 subset19/27; old17 SHA/metrics, five generic `_alt`/four family groups, thresholds/sections, eight invalid statuses, normal restore held. Source WAV SHA5807 `17890e483de91075569283a2bcfbada6a6402e1cd87ab52da53bdfbc605cf934`/5809 `c0552b983ecd9230b16d6ac3441eb8be7b43e80130bbd413fb62272752d7d510`, alternate independent different SHA same pass/fail. Critic disposable **5808** reports `.121000`, parsed delta `.0010000000000000009` and **fails**, so no equality pass or exact `.001s` claim. No final numeric failed fits; scout malformed shell exit127 and alt/guard helper relative-path exceptions were setup, not gate. No perceptual duration/quality/production/rights/engine/publishing or promotion inference. Work hash in `.shokunin/reports/round-44/audio.md`.

## Round 45 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| depth | unchanged | Ordinary `abs(ffprobe_duration - spec[0]) > .001s` unchanged. |
| coverage | unchanged | Seventeen canonical WAVs remain; two opt-in scratch UI points do not establish broad coverage. |
| calibration | **improved locally** | Before `4de93bf`, R44 bracketed only **positive** ±1ms side. Named non-author `reports/round-45/r45-verifier.md` fresh 50-run replay: 5713 ffprobe `.119021s`, actual signed `-.0009789999999999938`, abs `.0009789999999999938` exit0; 5711 `.118979s`, signed `-.0010209999999999941`, abs `.0010209999999999941` exit1 sole duration failure. Peaks `.27947998046875` each, RMS `-16.399347369151716/-16.3992750775437dBFS`, centroids `1663.1001045998237/1627.5978467387597Hz`; other UI gates pass. Sol `r45-adjudicator.md` admits fixture-local negative-side calibration only. |

Non-author **50 distinct fresh** receipts 21 exit0/29 expected exit1, prior48 subset20/28; old17 SHA/metrics, five generic `_alt`/four family groups, thresholds/sections, eight invalid statuses, normal restore held. Integrated SHA5713 `94f1ad9459fbfc06120668e3ebe5743a2d8690c66238d586f05006102811dd99`/5711 `2b4b0323f040a65b431a984e4fde5866f5c412754206c928e1fa21358adb9ab8`, independent alt different SHA same polarity. Critic disposable **5712** ffprobe `.119000`, parsed abs `.0010000000000000009` **fails** strict >.001; not integrated, no exact equality claim. Executor first report draft transcribed R44 positive-side float magnitudes for four negative-side cells; parent corrected report text from unchanged ffprobe durations before integration, **transcription** error not numeric failed fit or setup. Alt first helper relative-path exception was setup, not gate. No perceptual duration, quality, production, rights, engine, publishing or promotion inference. Work hash in `.shokunin/reports/round-45/audio.md`.

## Round 46 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| depth | unchanged | Existing whole-wave magnitude-FFT centroid and ordinary UI `250 <= centroid <= 4000` predicate unchanged. |
| coverage | unchanged | Seventeen canonical WAVs; two opt-in scratch controls do not establish broad coverage. |
| calibration | **improved locally** | Before `803c5fb`, ordinary **absolute lower 250Hz** band had no source-generated pass/fail bracket (R29 measured pairwise relative `.10` distinctness). Named non-author `reports/round-46/r46-verifier.md` fresh 52-run replay: measured project SoX-f32 centroid below **249.71389590882862Hz** exit1 sole spectrum failure, above **250.3250670185918Hz** exit0; both .12s/5760-frame 48k mono PCM16, peak `.279754638671875/.27984619140625`, RMS `-18.327838866709165/-18.32783946042307dBFS`; other ordinary gates pass. Sol `r46-adjudicator.md` admits only fixture-gate calibration. |

Non-author **52 distinct fresh** receipts 22 exit0/30 expected exit1, prior50 subset21/29; old17 SHA/metrics, five generic `_alt`/four family groups, thresholds/sections, eight invalid statuses, normal restore held. Integrated SHA below `fff9d981fe76c9163ba6a0db851e498b15fe193a1597427c8b73993b4666bfdf`/above `6e453ff6cdf02e3fb72e0ebb0734f39a566a823841da8949187ad73d74a90a2a`. Executor nominal225/226Hz **not measured centroids**; initial 230/270 decoded both in-band, failed numeric *bracket fit*; alt first decaying pairs likewise failed bracket fits, one helper relative-path setup exception; final independent alt broader centroid pair 202.48468234677034/302.47893043755806Hz same polarity. Reviewer below-peak draft `.279754150390625` corrected to `.279754638671875` as report transcription error. Waveforms differ in nominal frequency, quantized samples/full FFT: **gate-level isolation, not causal single-variable spectral isolation**, no exact250Hz equality, timbre/quality/perception, production/rights/engine/publishing/promotion inference. Work hash in `.shokunin/reports/round-46/audio.md`.

## Round 47 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| depth | unchanged | Existing whole-wave magnitude-FFT centroid and ordinary UI `250 <= centroid <= 4000` predicate unchanged. |
| coverage | unchanged | Seventeen canonical WAVs; two opt-in scratch controls do not establish broad coverage. |
| calibration | **improved locally** | Before `90c4aea`, ordinary **absolute upper 4000Hz** band had no source-generated pass/fail bracket (R46 lower250 separately). Named non-author `reports/round-47/r47-verifier.md` fresh 54-run replay: measured project SoX-f32 centroid below **3999.922795974407Hz** exit0 no failures, above **4000.427101452783Hz** exit1 sole spectrum; both .12s/5760-frame 48k mono PCM16, peak `.279754638671875/.2789306640625`, RMS `-18.327854015660773/-18.32785200392649dBFS`; other ordinary gates pass. Sol `r47-adjudicator.md` admits fixture-gate calibration only. |

Non-author **54 distinct fresh** receipts 23 exit0/31 expected exit1, prior52 subset22/30; old17 SHA/metrics, five generic `_alt`/four family groups, thresholds/sections, eight invalid statuses, normal restore held. Integrated SHA below `b04d00164fc57a97a0cdd591a589a44792d0084ba66cdc2118989183ae22fc17`/above `8f6dd0411d240e46ea619c32e3c344b8c03491d860ebc6ab32b248cbd51e4383`; nominal3983/3984Hz **not** measured centroids. Executor 3950/4050 and3980/4020 were valid but broader brackets, NOT failed fits. Independent alt different SHA centroids3998.2575908677754/4000.5907358489767 same polarity. Wave1 relative-path helper errors were setup, executor redundant path correction report text; none are gate outcomes. Waveforms differ nominal frequency/quantized samples/full FFT: **gate-level, not causal single-variable spectral isolation**, no exact4000 equality, timbre/quality/perception, production/rights/engine/publishing/promotion inference. Work hash in `.shokunin/reports/round-47/audio.md`.

## Round 48 verdict — 2026-10-13

| axis | verdict | before → after evidence |
|---|---|---|
| depth | unchanged | Existing exact ffprobe integer `sample_rate == 48000`, mono `format_failures` predicate unchanged. |
| coverage | unchanged | Seventeen canonical WAVs; two opt-in scratch controls do not establish broad coverage. |
| calibration | **improved locally** | Before `2c05aa0`, R25 `mono441_probe` tested broad 44.1k mismatch, not adjacent 47999/48000 boundary. Named non-author `reports/round-48/r48-verifier.md` fresh 56-run replay: 47999 Hz 5760-frame mono PCM16 ffprobe `.120003s` exit1 sole `format: expected 48kHz mono`, 48000 `.120000s` exit0 clean. Both decoded same f32 bytes SHA `4497c82d9bd1fb000455081a5f477af7756e7c035bbe1e81ad295f0b32805c7f`, peak `.27996826171875`, RMS `-18.327858226717105dBFS`; centroids `1022.5148421151724/1022.536144951523Hz` pass UI band but differ via rate-dependent FFT grid. Sol `r48-adjudicator.md` admits metadata-rate fixture calibration only. |

Non-author **56 distinct fresh** receipts 24 exit0/32 expected exit1, prior54 subset23/31; old17 SHA/metrics, five generic `_alt`/four family groups, thresholds/sections, eight invalid statuses, normal restore held. Source WAV SHA47999 `71551e200633e62b1b9db4ee5a582f8d4d996cd693f2e4a040a96023b130a210`/48000 `387500a620fbfdfb38e044ebb1ec8e0a82be14be9dc71e2bd18e45ec9625ed8c`; same PCM payload, different header rate. Independent alt original same-sample pair different SHA same polarity. No numeric failed fits/transcription; alt helper relative-path errors, scout direct-SoX error, guard shell quoting error were setup, not gate. Same discrete samples **not identical physical-time signal**; no resampling/converter, audible quality/perception, production/rights/engine/publishing/promotion inference. Work hash in `.shokunin/reports/round-48/audio.md`.

## Round 49 verdict — 2026-10-13

| axis | Sol verdict | before → after evidence |
|---|---|---|
| depth | **improved locally** | R48 immediate lower neighbor 47999/48000 only; R49 adds reproducible same-discrete-PCM **upper** neighbor 48001/48000, with other UI gates measured passing. Exact format predicate unchanged. |
| coverage | **improved locally** | Prior56 mode suite retained plus two opt-in upper-neighbor modes; corrected independent replay actually executed 58 commands. Canonical WAVs remain 17; no broad rate coverage. |
| calibration | **improved locally** | 48001 exit1 solely `format: expected 48kHz mono`, 48000 exit0 clean. Source WAV SHA `92b22d8749c5f02d4f68d9a8daa32b935404f1d7cdbc31bca55af2f9adf4cb5a`/`387500a620fbfdfb38e044ebb1ec8e0a82be14be9dc71e2bd18e45ec9625ed8c`; same SoX-f32 bytes SHA `4497c82d9bd1fb000455081a5f477af7756e7c035bbe1e81ad295f0b32805c7f`, peak `.27996826171875`, RMS `-18.327858226717105dBFS`; metadata48001/48000 mono pcm_s16le/16, durations `.119998/.120000s`, centroids `1022.557447787877/1022.536144951523Hz` both UI pass. |

Named non-author `reports/round-49/r49-verifier.md`: corrected **58 unique fresh receipts** 25 exit0/33 expected fixture-validation exit1, prior56 subset24/32, old17 SHA/metrics, five generic/four family, thresholds/sections/eight invalid/normal restored. Two discarded verifier wrapper-construction attempts each ran 58 shell invocations exit127 with **zero receipts**, setup not gates; alt helper/SoX and critic CLI/path errors likewise setup. No selected numeric failed fits/transcription. Named Sol `r49-adjudicator.md` admits one declared above-side move, no scoped harm. Scope: identical discrete PCM, **not** identical physical-time signal; changing rate tag changes duration/frequency axis. No arbitrary-rate/converter/resampling, perceptual/audible, production/rights/engine/publishing/promotion inference. Work hash in `.shokunin/reports/round-49/audio.md`.

## Round 50 verdict — 2026-10-13

| axis | Sol verdict | before → after evidence |
|---|---|---|
| depth | **improved locally** | Historical `stereo48_probe` was a broad invalid 4s spec; new matched 5760-frame ordinary UI mono/stereo 48k PCM16 pair controls all other UI gates and isolates the channel-count format decision. |
| coverage | **improved locally** | Two opt-in mono/stereo modes add to prior58; fresh non-author 60-command replay retains prior58. Canonical17 unchanged; no general stereo/multichannel coverage. |
| calibration | **improved locally** | Stereo 2ch exit1 sole `format: expected 48kHz mono`, matched mono 1ch exit0 clean. WAV SHA stereo `59e508f1b30d17eef5f00951434915bc7974e02d6988faf07a557270611e950e` / mono `93223ee4df8c027d6efaa12d9eca47af3de4fba1eba90c27f29c49ab0086a54a`; ffprobe 48000 pcm_s16le/16 both `.120000s`, peak `.3160400390625`, RMS `-19.902100515581505dBFS`; SoX-f32 project flattened centroid **stereo** `2019.8445020922231Hz` from 11520 interleaved values vs **mono** `1928.2134621890698Hz` from 5760, both UI band. |

Named non-author `reports/round-50/r50-verifier.md`: corrected **60 unique fresh receipts** 26 exit0/34 expected fixture-validation exit1, prior58 subset25/33, old17 SHA/metrics, five generic/four family, thresholds/sections/eight invalid/normal restore held. Discarded verifier wrapper attempt x60 exit127 **zero receipts** was setup, not gate; executor/alt str/relative Path helper errors likewise setup. No selected failed numeric fits/transcription. Named Sol `r50-adjudicator.md` admits one declared channel move, no demonstrated scoped harm. Stereo duplicates mono per-channel PCM; project measures flattened interleaved whole-stream FFT, **not** per-channel centroid or general stereo/downmix behavior. No audibility/perception, production/rights/engine/publishing/promotion inference. Work hash in `.shokunin/reports/round-50/audio.md`.

## Round 51 verdict — 2026-10-13

| axis | Sol verdict | before → after evidence |
|---|---|---|
| depth | **improved locally** | Historical native24 invalid probe was broad; new matched ordinary UI PCM24/PCM16 pair keeps all non-format gates passing and isolates the unchanged PCM16 predicate. No full-precision PCM24 test. |
| coverage | **improved locally** | Two opt-in depth modes extend the retained prior60 to 62 fresh non-author commands; canonical corpus remains 17. Fixture-mode coverage only. |
| calibration | **improved locally** | 5760-frame mono 48k pair: PCM24 `pcm_s24le`/24 sole `format: expected PCM16` exit1; PCM16 `pcm_s16le`/16 clean exit0. Both project-decode to equal floats by PCM16×256 construction, peak `.315399169921875`, RMS `-14.628083420045229 dBFS`, centroid `1123.8154138173777 Hz`; all other UI gates pass. |

Named non-author `reports/round-51/r51-verifier.md`: **62 new unique receipts**, 27 exit0/35 expected validation exit1; prior60 subset26/34 exact preserved, canonical17 hash/metrics, five generic/four family, thresholds/sections/eight invalid and normal restoration. Earlier 62 stalled-verifier receipts `083353`–`083459` excluded; stall and wave1 helper/path/quoting errors are setup, not gates. No selected failed numeric fit or corrected transcription. Sol `r51-adjudicator.md` admits with no demonstrated scoped harm. No additional PCM24 precision, codec generality, fidelity, audibility/perception, production/rights/engine/publishing/promotion inference. Work hash in `.shokunin/reports/round-51/audio.md`.

## Round 52 verdict — 2026-10-13

| axis | Sol verdict | before → after evidence |
|---|---|---|
| depth | **improved locally** | Matched ordinary UI unsigned PCM8/signed PCM16 pair exercises below-16-bit depth while holding decoded vectors equal and all other UI gates passing; no generic conversion claim. |
| coverage | **improved locally** | Two opt-in modes extend prior62 to fresh 64-command replay; canonical corpus remains 17, prior modes preserved. |
| calibration | **improved locally** | PCM8 `pcm_u8`/8 sole `format: expected PCM16` exit1; matched PCM16 `pcm_s16le`/16 clean exit0. Both mono48k/5760 frames/.120s, peak `.3125`, RMS `-14.699802598426999dBFS`, centroid `1581.8516662990894Hz`; project SoX f32 vectors equal by `(u8-128)*256` construction. |

Named non-author `reports/round-52/r52-verifier.md`: **64 fresh unique receipts**, 28 exit0/36 expected validation exit1, prior62 raw JSON exact subset27/35, canonical17 SHA/metrics, five generic/four family, thresholds/sections/eight invalid, initial/final normal restoration. Executor initial scratch-root error was setup; parent's first author-mode receipts had wrong `normal` suffix until corrected (report-label integration error), not gate outcomes. Verifier ledger's semicolon joins two ambience failures; raw list has both. Sol `r52-adjudicator.md` admits with no demonstrated scoped harm; no selected failed numeric fit or corrected transcription. No broad codec/fidelity/audibility/quality/production/rights/engine/publishing/promotion inference. Work hash in `.shokunin/reports/round-52/audio.md`.

## Round 53 verdict — 2026-10-13

| axis | Sol verdict | before → after evidence |
|---|---|---|
| depth | **improved locally** | Original matched ordinary UI IEEE-float32/PCM16 pair isolates existing PCM16 metadata predicate without tuning gates. Not a general float precision or header test. |
| coverage | **improved locally** | Two opt-in modes extend the prior64 to 66 fresh commands; canonical corpus remains 17 and prior64 raw JSON is preserved. |
| calibration | **improved locally** | Float `pcm_f32le`/32 sole `format: expected PCM16` exit1; PCM16 `pcm_s16le`/16 clean exit0. Both mono48k/5760 frames/.120s, peak `.315399169921875`, RMS `-14.628083420045229dBFS`, centroid `1123.8154138173777Hz`; SoX-f32 decoded vectors equal for constructed PCM16-grid samples. |

Named non-author `reports/round-53/r53-verifier.md`: **66 new unique receipts**, 29 exit0/37 expected validation exit1, prior64 exact JSON subset28/36, canonical17 SHA/metrics, five generic/four family, thresholds/sections/eight invalid and normal restoration. SoX warns `wave header missing extended part of fmt chunk` for simple float header but decodes exit0; no extensible-header/general-codec claim. Executor scratch path, simplifier quoting, scout malformed ffprobe are setup, not gates. Sol `r53-adjudicator.md` admits no demonstrated scoped harm, no selected numeric failed fit or corrected transcription. No general conversion/fidelity/audibility/quality/production/rights/engine/publishing/promotion inference. Work hash in `.shokunin/reports/round-53/audio.md`.

## Round 54 verdict — 2026-10-13

| axis | Sol verdict | before → after evidence |
|---|---|---|
| depth | **improved locally** | Ordinary matched signed PCM32/PCM16 UI pair tests integer width above 24 through unchanged metadata predicate, unlike historical `native24_probe` (`pcm_s24le`/24 even though `sample_fmt=s32`). No added PCM32 low-bit precision tested. |
| coverage | **improved locally** | Two opt-in modes extend prior66 to 68 fresh commands; canonical corpus remains 17, prior66 raw JSON preserved. |
| calibration | **improved locally** | PCM32 `pcm_s32le`/32 sole `format: expected PCM16` exit1; PCM16 `pcm_s16le`/16 clean exit0. Both mono48k/5760 frames/.120s, peak `.31536865234375`, RMS `-14.628519169868087dBFS`, centroid `1123.322704293326Hz`; SoX-f32 vectors equal by `s16*65536` construction. |

Named non-author `reports/round-54/r54-verifier.md`: **68 new unique receipts**, 30 exit0/38 expected validation exit1, prior66 exact raw JSON subset29/37, canonical17 SHA/metrics, five generic/four family, thresholds/sections/eight invalid and normal restoration. Sol `r54-adjudicator.md` admits no demonstrated scoped harm; wave1 pre-integration proposed flags/results are not replay evidence. No selected numeric failed fit or corrected transcription. No arbitrary PCM32, general codec/conversion/fidelity, audibility/quality, production/rights/engine/publishing/promotion inference. Work hash in `.shokunin/reports/round-54/audio.md`.

## Round 55 verdict — 2026-10-13

| axis | Sol verdict | before → after evidence |
|---|---|---|
| depth | **improved locally** | Same 5760 signed16 samples through conventional tag1/fmt16 and exact WAVE_FORMAT_EXTENSIBLE tag0xfffe/fmt40 valid16 front-center-mask0x4 PCM-subtype headers, equal SoX-f32 decoded vectors and UI measurements. No new valid-bit/fidelity claim. |
| coverage | **improved locally** | Two opt-in modes extend prior68 to 70 new commands; canonical17 and prior68 exact JSON preserved. One specified extensible header, not universal coverage. |
| calibration | **improved locally** | Both headers ffprobe `pcm_s16le`/16, mono48k/.120s, peak `.31536865234375`, RMS `-14.628519169868087dBFS`, centroid `1123.322704293326Hz`, no failures, exit0 through unchanged PCM16/UI gates. Positive representation control complements earlier negative width/codec controls. |

Named non-author `reports/round-55/r55-verifier.md`: **70 new unique receipts**, 32 exit0/38 expected validation exit1; prior68 exact JSON subset30/38, canonical17 SHA/metrics, five generic/four family, thresholds/sections/eight invalid and normal restoration. Sol `r55-adjudicator.md` admits no demonstrated scoped harm. Guard's extensible WAV SHA was a report transcription error; integrated SHA `bd7d95901935c0effe21fd64e44a47487372be9d0c80f86cc725380df0352f47` is confirmed independently, so guard transcription is not gate evidence. No selected numeric failed fit or receiptless verifier setup error. No universal extensible support, general codec/fidelity/audibility/quality/production/rights/engine/publishing/promotion inference. Work hash in `.shokunin/reports/round-55/audio.md`.

## Round 56 verdict — 2026-10-13

| axis | Sol verdict | before → after evidence |
|---|---|---|
| depth | **improved locally** | Same PCM16 payload in valid16 mono extensible PCM-subtype headers with mask0 (unspecified) versus mask0x4 (front-center); isolated mask representation, not other layouts. |
| coverage | **improved locally** | Two opt-in modes extend prior70 to 72 fresh commands; canonical17 and prior70 complete JSON preserved. |
| calibration | **improved locally** | Both ffprobe `pcm_s16le`/16 mono48k/.120s, peak `.31536865234375`, RMS `-14.628519169868087dBFS`, centroid `1123.322704293326Hz`, identical SoX-f32 decode, no failures, exit0 through unchanged gates. |

Named non-author `reports/round-56/r56-verifier.md`: **72 new unique receipts**, 34 exit0/38 expected validation exit1, prior70 exact raw JSON subset32/38, canonical17 SHA/metrics, generic five/four family, thresholds/sections/eight invalid, normal restoration. One malformed shell-quote attempt produced zero receipt (**setup**, not gate); critic malformed GUID scratch is a separate negative, not the selected pair. Sol `r56-adjudicator.md` admits no demonstrated scoped harm. No selected failed numeric fit or corrected transcription. Mask0 is unspecified positions, not front-center; no arbitrary masks, universal extensible/standards, general codec/fidelity/audibility/quality/production/rights/engine/publishing/promotion inference. Work hash in `.shokunin/reports/round-56/audio.md`.

## Round 57 verdict — 2026-10-13

| axis | Sol verdict | before → after evidence |
|---|---|---|
| depth | **improved locally** | Left-aligned identical signed PCM16 payload in extensible PCM-subtype mono headers differing only at valid bits 15 versus 16; container remains 16. The project does not parse the valid-bits field. |
| coverage | **improved locally** | Two opt-in modes extend prior72 to 74 fresh commands; canonical17 and prior72 complete JSON preserved. |
| calibration | **improved locally** | Both ffprobe `pcm_s16le`/16 mono48k/.120s, peak `.2098388671875`, RMS `-18.84202236105824dBFS`, centroid `2153.742616905067Hz`, identical SoX-f32 decoded vectors, no failures, exit0 through unchanged gates. |

Non-author `reports/round-57/r57-verifier.md`: **74 new unique receipts**, 36 exit0/38 expected validation exit1, prior72 exact raw JSON subset34/38, canonical17 SHA/metrics and control suite preserved. Its preliminary malformed shell-quote exit127 yielded **no receipt** (setup, not gate). Critic found 2520 odd samples in executor's rejected valid15 draft; selected alt pair has 5760/5760 even samples, identical payload, and only WAV offset38 differs. Sol `r57-adjudicator.md` admits no demonstrated scoped harm. No selected failed numeric fit. No metadata-enforcement, universal valid-bit/codec/header, extra precision, fidelity, audibility/quality/production/rights/engine/publishing/promotion inference. Work hash in `.shokunin/reports/round-57/audio.md`.

## Round 58 verdict — 2026-10-13

| axis | Sol verdict | before → after evidence |
|---|---|---|
| depth | **improved locally** | Matched, all-divisible-by-four signed PCM16 payload in extensible PCM-subtype mono headers differing only valid-bits14 versus 16 at WAV byte38, advancing R57's all-even 15/16 pair. |
| coverage | **improved locally** | Two opt-in modes extend prior74 to 76 fresh commands; canonical17 and prior74 complete JSON preserved. |
| calibration | **improved locally** | Both ffprobe `pcm_s16le`/16 mono48k/.120s, peak `.3153076171875`, RMS `-14.629479252569332dBFS`, centroid `1129.9910331085607Hz`, equal SoX-f32 decode, no failures, exit0 through unchanged gates. |

Non-author `reports/round-58/r58-verifier.md`: **76 new unique receipts**, 38 exit0/38 expected validation exit1, prior74 exact raw JSON subset36/38, canonical17 SHA/metrics and controls preserved. No verifier receiptless setup/decode attempt or selected numeric failed fit. Executor relative-path direct-measure exits1 and alt malformed inspection were setup, not selected gates; scout's corrected R57 history error was report transcription. Sol `r58-adjudicator.md` admits no scoped harm. The predicate does not parse valid-bit metadata; no precision/fidelity, universal valid-bit/header/codec, perceptual/quality/production/rights/engine/publishing/promotion inference. Work hash in `.shokunin/reports/round-58/audio.md`.

## Round 59 verdict — 2026-10-13

| axis | Sol verdict | before → after evidence |
|---|---|---|
| depth | **improved locally** | Matched, all-divisible-by-eight signed PCM16 payload in extensible PCM-subtype mono headers differing only valid-bits13 versus 16 at WAV byte38, extending the left-aligned 15/16 and 14/16 controls. |
| coverage | **improved locally** | Two opt-in modes extend prior76 to 78 designated fresh commands; canonical17 and prior76 complete JSON preserved. |
| calibration | **improved locally** | Both ffprobe `pcm_s16le`/16 mono48k/.120s, peak `.659912109375`, RMS `-8.811743007017897dBFS`, centroid `2139.5871109211243Hz`, equal SoX-f32 decode, no failures, exit0 through unchanged gates. |

Non-author `reports/round-59/r59-verifier.md` designated **78 new unique receipts**, 40 exit0/38 expected validation exit1, prior76 exact raw JSON subset38/38, canonical17 SHA/metrics and controls preserved. Separately, an *earlier* unnecessary complete 78-receipt run `131110`–`131231` is also raw evidence, identical JSON but distinct paths; the verifier attributed its repeat to mistaken in-memory state tracking. Original chronology “after” was report transcription, corrected; Sol correctly treated the cause as unknown from evidence available to it. Preliminary malformed shell quote exit127 produced **zero receipt** (setup, not gate). No selected failed numeric fit. No valid-bit enforcement/precision/fidelity, universal header/codec, audible/quality/production/rights/engine/publishing/promotion inference. Work hash in `.shokunin/reports/round-59/audio.md`.

## Round 60 verdict — 2026-10-13

| axis | Sol verdict | before → after evidence |
|---|---|---|
| depth | **improved locally** | Matched PCM16 extensible headers differ only at WAV byte38: malformed/unspecified valid-bits0 versus valid16 control; identical payload and decoded samples. Not a conforming positive case. |
| coverage | **improved locally** | Two opt-in modes extend designated prior78 to 80 fresh commands; canonical17 and prior78 full JSON preserved. This is malformed-input coverage, not positive format conformance. |
| calibration | **improved locally** | This host's ffprobe/SoX and unchanged gate do not reject this one valid0 header: both `pcm_s16le`/16 mono48k/.120s, peak `.082489013671875`, RMS `-26.87354274685677dBFS`, centroid `2139.5871109211243Hz`, no failures/exit0. |

Non-author `reports/round-60/r60-verifier.md`: **80 new unique receipts**, 42 exit0/38 expected validation exit1, designated prior78 exact raw JSON subset40/38, canonical17 SHA/metrics and controls preserved. No verifier extra run or selected failed numeric fit. Critic's pre-integration unknown flag exit2 produced zero receipt (setup); simplifier's `inspect.py` shadowed stdlib in scratch generator exit1, corrected under isolated `python3 -I` (setup). Sol `r60-adjudicator.md` admits no scoped harm. No valid-bit enforcement/standards conformance, zero-bit audio, precision/fidelity, universal header/codec, audible quality/production/rights/engine/publishing/promotion inference. Work hash in `.shokunin/reports/round-60/audio.md`.

## Round 61 verdict — 2026-10-13 (retroactive record; the round closed ADMIT under Sol `r61-adjudicator.md` — this table was omitted at closeout and is supplied now)

| axis | Sol verdict | before → after evidence |
|---|---|---|
| depth | **improved locally** | First host rejection along the valid-bits dimension: valid17>16 reclassified by ffprobe to `pcm_s24le`/24b/`0.080s` and rejected by the unchanged gate (format/duration/level/spectrum), while valid16 stays `pcm_s16le`/0.120s clean. |
| coverage | **improved locally** | Two opt-in modes extend designated prior80 to 82 fresh commands; canonical17 and prior80 complete JSON preserved (80/80 pair-matched vs R60 ledger). |
| calibration | **improved locally** | Malformed above-range valid-bits is neither ignored (valid0) nor decoder-fatal — it is reclassified then gate-rejected, exit1 with receipt; directional asymmetry evidenced. |

Non-author `reports/round-61/r61-verifier.md`: **82 fresh unique receipts**, 43 exit0/39 expected exit1, prior80 complete-JSON subset42/38 exact. SoX 3,839-vs-3,840 one-frame gap retained UNKNOWN at this verdict — resolved at r62. Commit pins cited in r61 records resolve only in the pre-extraction origin repo; canonical equivalents noted in LOG's append-only correction. No valid-bit enforcement/standards conformance/precision/fidelity/audibility/production/rights/engine/publishing/promotion inference.

## Round 62 verdict — 2026-10-13

| axis | Sol verdict | before → after evidence |
|---|---|---|
| depth | **improved locally** | r61's SoX 3,839-vs-5,760 UNKNOWN resolved end-to-end: byte-256 `0x84` payload → `act` autodetect → ffmpeg bridge → valid17→pcm_s24le → packets 8192+3328 → per-packet mod-3 tail drop = 2730+1109. Five independent seat derivations converge; 28/28 predictions confirmed; two-directional falsifications (3839 without valid17, non-3839 with it). |
| coverage | **improved locally** | Second impossible-header family `corpus/live/round-62/pair_valid_{24,32}.wav` + two opt-in modes extend the designated ledger 82→84 fresh commands; prior 82 preserved verbatim. |
| calibration | **improved locally** | Gate behavior on above-range valid-bits now measured across three values: 17→4-failure reject, 24→4-failure reject, 32→2-failure reject — all exit1 with receipt under unchanged thresholds. |

Non-author `reports/round-62/r62-verifier.md`: **84 fresh unique receipts**, 43 exit0/41 exit1, **84/84 exits match and 84/84 receipts byte-identical** to committed counterparts; discernment spot-checks both directions (direct ffmpeg = 3,839 — SoX passthrough; byte-256 flip → native fatal refusal). Verifier disclosed and self-restored one `xxd` overwrite incident byte-exact — receipts unaffected. Sol `r62-adjudicator.md` admits no demonstrated scoped harm. Bounded to SoX_ng 14.8.0.1 + ffmpeg n9.0.1 on this host; the `act` detection is a payload byte-256 `0x84` collision (fixture fragility disclosed). No standards-conformance, decoder-correctness, universal valid-bit/header/codec, precision/fidelity, audibility/quality/production/rights/engine/publishing/promotion inference. Work commit `cbe763e`; report-last commit follows.

## Round 63 verdict — 2026-10-13

| axis | Sol verdict | before → after evidence |
|---|---|---|
| depth | **improved locally** | r62's disclosed fragility resolved to an exact source-cited predicate: `len≥257 ∧ file[0:4]=="RIFF" ∧ file[256]==0x84 ∧ ¬(earlier CHECK)`. Five independent derivations converge; 23,738+1,408+293+~30 probe rows; preemptor set {gsrt@16, hcom@65+128}; no-fallback ordering proven (`premature EOF` = au reader on empty pipe) — r62's retained UNKNOWN closed. |
| coverage | **improved locally** | Tracked pair `pair_route_{84,00}.wav` (sole byte-256 diff) + `--probe-ui-route-act-{84,00}-r63` modes; designated ledger 84→86 fresh commands; prior 84 preserved verbatim, receipts byte-identical. |
| calibration | **improved locally** | Routing now receipt-visible per probe (`sox_detected_format`/`sox_route` fields); native-reject (route-00→exit2) vs bridge-decode (route-84→exit1) calibrated on an unchanged gate. |

Non-author `reports/round-63/r63-verifier.md`: **86 fresh unique receipts**, 43 exit0/43 exit1, **86/86 exits match and 86/86 receipts byte-identical** to committed counterparts; discernment both directions (0x42@256→wav, 0x84@257→wav). Verifier caveat: `00` receipt embeds absolute repo path in `sox_stderr` — same-host byte-identity property. Sol `r63-adjudicator.md` admits no demonstrated scoped harm. Bounded to SoX_ng 14.8.0.1 USING_FFMPEG + ffmpeg n9.0.1 on this host; the act row is `#if USING_FFMPEG`-only. No standards-conformance, decoder-correctness, fidelity, audibility, production, rights, or promotion inference. Work commit `1a97b0e`; report-last commit follows.

## Round 64 verdict — 2026-10-14

| axis | Sol verdict | before → after evidence |
|---|---|---|
| depth | **improved locally** | valid-bits→codec reclassification resolved to an exact, source-attributed step map: `w=(V+7)>>3` → {1:u8, 2:s16le, 3:s24le, 4:s32le, 5–7:NONE, 8:s64le, >64:NONE} under the act-forced ffmpeg bridge; seven boundaries pinned (0|1, 8|9, 16|17, 24|25, 32|33, 56|57, 64|65); three independent sweeps converge (74+85+17+39 variants); envelope-gate precondition (`0xFFFE∧cbSize≥22∧PCM-GUID`) measured and carried; f24le promotion + named-undecodable 0-sample class + nb_channels factor disclosed; residue re-explained as alignment×width (lossless-3,840 counterexample). |
| coverage | **improved locally** | tracked `pair_valid_{8,9,24,25,56,57}.wav` boundary pairs (sole byte-38 diffs, all byte-256=0x84 act-forced) + six `--probe-ui-extensible-valid-*-r64` modes; ledger 86→92 (44 exit0/48 exit1); prior-86 receipts byte-identical across three generations. |
| calibration | **unchanged** | thresholds, format_failures, gate bounds all untouched; designed exit-1 failure shape preserved; verifier methodology caveat (relative-path compare artifact) recorded. |

Non-author `reports/round-64/r64-verifier.md`: **AGREE on all four claims** — 92-cmd replay 44/48 exact, 86/86 + 6/6 receipts byte-identical, pair discriminators live, envelope-gate spot-checks, commits resolve. Sol `r64-adjudicator.md`: own reproduction of all six pair members (u8/11,520; s16le/5,760; s32le; NONE/exit-2; s64le/1,440). Bounded: this host's SoX_ng 14.8.0.1 + ffmpeg n9.0.1 only; non-extensible/float-GUID shapes unexercised; stdin+ffmpeg-bridge dead combination disclosed. No standards/fidelity/production inference. Work commit `4c12342`; report-last commit follows.

## Round 65 verdict — 2026-10-14

| axis | Sol verdict | before → after evidence |
|---|---|---|
| coverage | **improved locally** | Autodetect surface grew from one pinned predicate to a measured order — `gsrt ≺ hcom ≺ act ≺ wav` on the RIFF family (wve sits at table row 80 but is byte-0-incompatible with RIFF — unreachable there, r66 measured it live only on non-RIFF carriers); tracked collision family `corpus/live/round-65/pair_preempt_{act,gsrt,hcom,both}.wav` (sole signature-span diffs; `act` member byte-identical to r63 pair_route_84); `--probe-ui-preempt-*-r65` modes; designated ledger 86→96 (44 exit0/52 exit1); prior 92 receipts byte-identical. |
| depth | **improved locally** | Detection ≠ accept decoupled: hcom-shaped RIFF decodes 9 samples natively (critic falsification of "preemptor ⇒ reader-fail"); `premature EOF` non-attributing (3 emitters); fd seekability is an invisible conjunct — gsrt decodes 11,076 on pipe where ffmpeg bridge dies (boundary); no-fallthrough proven on failed opens. |
| calibration | **unchanged** | No thresholds or gate structure touched; ordering measured purely by detection lines + strace/execve counts. |

Non-author `reports/round-65/r65-verifier.md`: **AGREE all five claims** — committed-state replay of all four tracked members, equivalent ledger re-run 96 commands (44/52) with 92/92 prior receipts byte-identical, sole-span `cmp -l` diffs exact, hcom-decode counterexample reproduced, zero tracked mutation observed. Sol `r65-adjudicator.md` admits no demonstrated scoped harm. Bounded to SoX_ng 14.8.0.1 USING_FFMPEG + ffmpeg n9.0.1 on this host; ordering is empirical detection-order on RIFF-family files. No standards-conformance, decoder-correctness, fidelity, audibility, production, rights, or promotion inference. Work commit `1b0d276`; report-last commit follows.

## Round 66 verdict — 2026-10-14

| axis | Sol verdict | before → after evidence |
|---|---|---|
| coverage | **improved locally** | Preemptor map complete: wve predicate pinned (`len>=15 ∧ "ALawSoundFile**"@0`, 15-B floor exact, all bytes load-bearing) and measured **unreachable on RIFF** (geometric byte-0 exclusion — declared claim's else-branch hit); reachable pre-act set on RIFF+0x84@256 proven exactly {gsrt, hcom}; exact gates gsrt 24|25, hcom 131|132; six tracked members `corpus/live/round-66/` with probe modes; ledger 96→102 (44 exit0/58 exit1); prior receipts byte-identical. |
| depth | **improved locally** | Detector-vs-reader contract table landed (wve detector looser than its 18-B reader ID; gsrt detector stricter at byte 24; hcom chain-gated post-detection); stdin+ffmpeg-bridge dead combination pinned (prefetch replay + fifo open-block); transport forks: `pair_dec_act` bridge decode is regular-file-only, txw/smp refuse pipes, seekability conjunct re-confirmed. |
| calibration | **unchanged** | No threshold/gate edits; ordering and gates measured purely by detection lines + decode counts. |

Non-author `reports/round-66/r66-verifier.md`: **AGREE on all five claims** — independent constructions confirm the {gsrt,hcom} set + geometric exclusion both directions; six tracked members re-detected exactly; full 102-command ledger replay 102/102 exits + receipts byte-identical; prior-96 byte-identical on independent runs. Sol `r66-adjudicator.md` reproduced all six tracked members + own wve construction. Bounded: SoX_ng 14.8.0.1 USING_FFMPEG + ffmpeg n9.0.1, this host; ordering empirical on the RIFF family; wve reach claim scoped to non-RIFF carriers. No conformance/fidelity/production inference. Work commit `014b532`; report-last commit follows.

## Round 67 verdict — 2026-10-14

| axis | Sol verdict | before → after evidence |
|---|---|---|
| coverage | **improved locally** | Transport added as a first-class measured axis: single parameterized `transport_leg`/`transport_matrix` over {file, stdin_pipe, redirected_fd, fifo_path}; complete 10-member × 4-transport matrix → 112-row ledger (49 exit0/63 exit1, 0 UNPARSED); prior-102 receipts byte-identical. |
| depth | **improved locally** | Detection proven transport-invariant (`sox_detected_format` identical ×40 cells); decode-stage fork set measured exactly = {preempt_act, preempt_gsrt, preempt_both, dec_act, lengate_gsrt_25}; fork locus attributed — native gsrt reader on the seekable bit, act/ffmpeg bridge on child-side name resolvability (boundary refinement over the named×seekable proxy); fifo determinism under pinned 1.0s writer-linger. |
| calibration | **unchanged** | No threshold/predicate edits; additive axis. |

Non-author `reports/round-67/r67-verifier.md`: **AGREE on all five claims** — 10 replayed receipts byte-identical to author's, fork/invariant partition verbatim incl. distinct non-seekable gsrt error strings, fifo linger pin re-verified across 3 runs, 112-row ledger + prior-102 byte-identical, 0 UNPARSED. Sol `r67-adjudicator.md` reproduced the dec-act 3-group fork, preempt-gsrt 2-group fork, and dec-hcom invariance on the committed tree. Bounded: SoX_ng 14.8.0.1 USING_FFMPEG + ffmpeg n9.0.1, this host; receipt byte-stability claimed for serial ledger execution only (non-atomic `build_artifacts.py` rebuild race disclosed); fifo legs deterministic under the pinned linger, residual extreme-load race disclosed. No conformance/fidelity/production inference. Work commit `366fcc1`; report-last commit follows.

## Round 68 verdict — 2026-10-14

| axis | Sol verdict | before → after evidence |
|---|---|---|
| coverage | **improved locally** | Post-table fallback path now tracked: `posttable_nomatch` (no CHECK row → name-resolved extension dispatch) + `txw_piperefuse` (reader-level `!seekable` gate) members; ledger 112→114 (49 exit0/65 exit1); 5 post-table verdict classes enumerated incl. `|cmd` assume-sox + `--magic` off-ledger classes. |
| depth | **improved locally** | Declared seekability-fork claim **falsified-as-stated** (four-seat convergence): post-table resolves on NAMED-resolvability (`{file,fifo_path}` vs `{stdin_pipe,redirected_fd}` — `ft->seekable` never read on this path; prefetch bytes pending-buffer-replayed not consumed); genuine seekable fork pinned inside the txw reader (`{file,redirected_fd}` decode-64 vs pipes refuse). `.snd` ext-gated CHECK row = first detection-fork counterexample to r67 invariance. |
| calibration | **unchanged** | no predicate/threshold edits; additive members + two probe flags; prior-112 rows byte-identical (verifier-confirmed). |

Non-author `reports/round-68/r68-verifier.md`: **AGREE 5/5** on `6c91040` — independent 114-cmd replay byte-identical across all rows, members identical to verbatim rebuild, 112 prior receipts byte-identical, probes deterministic ×5. Sol `r68-adjudicator.md`: falsification adopted as the finding; corrected named-axis mechanism is what the ledger encodes. Bounded: SoX_ng 14.8.0.1 USING_FFMPEG + ffmpeg n9.0.1, this host; serial-execution receipt stability; starved-fifo protocol artifact disclosed. No conformance/fidelity/production inference. Work commit `6c91040`; report-last commit follows.

## Round 69 verdict — 2026-10-14

| axis | Sol verdict | before → after evidence |
|---|---|---|
| coverage | **improved locally** | Extension-suffix sub-axis tracked: 5 byte-identical members × 4 transports → ≥6 distinct named-arm verdicts (wav-verdict / bin-no-handler / txw 3-way / f32-decode / sndr-detect); dead-CHECK-row census: 5/130 rows ever first-match in ledger receipts (16+4 in all committed evidence); ledger 114→119 (49/70). |
| depth | **improved locally** | `.snd` = first member where DETECTION itself forks on transport (ext-gated CHECK row formats.c:247-248 + b[0]=b[1]=b[7]=0 content contract; sole detection-fork across 4,929 receipts); `.txw` intersects reader-gate axis (3-group split); rate@2–3 selects decode vs verdict pin; census corrected to coverage-bookkeeping (wma sole dead-by-construction row). |
| calibration | **unchanged** | additive members + flags; prior-114 receipts byte-identical (verifier); no predicate edits. |

Non-author `reports/round-69/r69-verifier.md`: **AGREE 6/6** on `30bb86d` — independent 119-cmd replay position-identical, members byte-identical to rebuild, probes deterministic ×6, census reproduced. Sol `r69-adjudicator.md`: declared ≥3 claim confirmed at ≥6 groups; .snd detection-fork verified at byte level by 4 seats. Bounded: SoX_ng 14.8.0.1 USING_FFMPEG + ffmpeg n9.0.1, this host; `.mp3`/`.aptx`/`.dts` fifo hazards disclosed; census = coverage bookkeeping not deadness. No conformance/fidelity/production inference. Work commit `30bb86d`; report-last commit follows.

## Round 70 verdict — 2026-10-14

| axis | Sol verdict | before → after evidence |
|---|---|---|
| depth | **improved locally** | `fifo_writer_hold_s` demoted from point constant to MEASURED transition band: oneshot {0 blocked → >=50ms stable} on this host; chunked feed lands 10/10 at h*=0 (binary-arm control) — strict binary-on-attach refuted; outcome space = attach x close-before-deadline. |
| coverage | **improved locally** | `--probe-fifo-hold-ladder-r70` (6 holds x 2 feeds x 10 reps, per-cell verdict distributions); `fifo_feed` chunked variant; `reap_fifo_orphans` backstop on both fifo legs. |
| calibration | **unchanged** | default 1.0s preserved (~20x margin over the zone); prior-119 rows byte-stable (probe replay identical on dec_act); additive flag only. |

Non-author: verifier seat lost to free-model rate limits; operator adjudicator probe on `59a7440` + baseline's independent 10-rep ladder agree verbatim (blocked 10/10 @ h=0; exit-2 10/10 >=50ms; chunked all-stable). Sol `r70-adjudicator.md`: measured band + third-outcome refutation adopted. Bounded: SoX_ng 14.8.0.1 USING_FFMPEG + ffmpeg n9.0.1, this host; zone load-dependent; no conformance/fidelity/production inference. Work commit `59a7440`; report-last commit follows.

## Round 71 verdict — 2026-10-14

| axis | Sol verdict | evidence |
|---|---|---|
| coverage | **improved locally** | second decoder runtime under measurement: ffmpeg/ffprobe n9.0.1 on the 9-member transport corpus — new parallel receipt family (`ffprobe_*_r71_probe`), claim CONFIRMED content-vs-suffix |
| depth | **improved locally** | named/suffix partition shown SoX-specific: no ffmpeg analogue; per-process fifo writer protocol discovered (consumer chains need fresh writers); fresh-fd-per-leg rule recorded |
| calibration | **unchanged** | insertion-only flag; prior 120-mode ledger untouched; byte-identity check armed for the report-last receipts |

Sol (provisional): ADMIT — claim confirmed; operator-authored post-massacre; verifier pending post-reset. Bounded ffmpeg n9.0.1, this host.

## Round 72 verdict — 2026-10-14

| axis | verdict | evidence |
|---|---|---|
| coverage | **improved** | THIRD decoder runtime (libsndfile 1.2.2) on the canonical 9×4 matrix — 3-decoder verdict lattice established; .snd named/anonymous fork pinned; txw refuse-tier unique |
| depth | **improved** | claim corrected by measurement before landing: sndfile-only class empty (joint with sox); ffmpeg strictest (not superset); hold-band shown SoX-bridge-specific; 12B tier onset + sniff-consumption measured |
| calibration | **unchanged** | insertion-only; prior 121-mode rows untouched; r72 receipts byte-identical ×2 |

Sol `r72-adjudicator.md`: ADMIT-with-correction — 3-decoder lattice verified with corrected class claims; verifier AGREE on committed tree; critic+reviewer corrections folded. Bounded libsndfile 1.2.2 + this host.

## Round 73 verdict — 2026-11-01

| axis | verdict | evidence |
|---|---|---|
| coverage | **improved** | first non-decoder runtime class: pw-cat (PipeWire realtime) + mpv (lavf) on 9x4 matrix + operational surface entry (daemon gate, writer-attach, pacing) — consumer verdict shape now contrasted with the decoder axis |
| depth | **improved** | two member-local forks pinned with driver attribution: mpv inverted seekability (lavf-synthetic EPERM, no syscall) vs pw-cat name-axis (inherited libsndfile fallback); pwcat_name_axis 2x2 isolates name-vs-transport; corpus-wide "consumer polarity" claim falsified honestly |
| calibration | **unchanged** | insertion-only (+466/-3); prior rows byte-stable; wall_s leaves = realtime jitter, pins on signatures |

Sol `r73-adjudicator.md`: ADMIT-with-correction — member-local forks confirmed, class-polarity claim falsified as worded and restated. Bounded PipeWire 1.6.8 live daemon, mpv 0.41.0/lavf 63.1.101, this host. Work commit `febf34b`; report-last commit follows.

## Round 74 verdict — 2026-11-01

| axis | verdict | evidence |
|---|---|---|
| coverage | **improved** | lavf demuxer inventory measured past hcom: 4 new generated members (iss/apc/acm/adx hand-built + muxed) + 3 controls; the no-seek fork's real gate (NOGENSEARCH) now falsifiably pinned; --start=N position fork; pw-cat ops-2 hang taxonomy + raw-bypass |
| depth | **improved** | three wound shapes distinguished: output_rc (probe drains all), truncation (2-packet constant), wound-only (NOGENSEARCH survives) — the seekable-bit axis is a 3-valued partition, not boolean |
| calibration | **unchanged** | insertion-only (+544/-3 + folds); prior 120/121 modes byte-stable; byte-deterministic member generation; fork_kind honesty fold |

Sol `r74-adjudicator.md`: ADMIT-corr — NOGENSEARCH gate measured, acm briefed-prediction falsified honestly. Verifier AGREE 12/12 on `168b165`. Bounded: mpv 0.41.0/lavf 63.1.101, libpipewire 1.6.8, this host.

## Round 75 verdict — 2026-10-14

| axis | verdict | evidence |
|---|---|---|
| coverage | **improved** | three playback consumers on the canonical matrix: paplay (pacat/libpulse daemon-gated), aplay (in-process ALSA), ffplay (lavf pull-model) — 27/27 verdict groups + per-consumer ops rows (daemon ordering, SDL axis, kill classes, -ss) |
| depth | **improved** | four cross-consumer non-transfers pinned: pw-cat .snd axis absent on paplay, mpv seek fork absent on ffplay, aplay raw-accept invariant; input-open-before-connect ordering witness; per-consumer kill-class partition {-15 | -9 | 123} |
| calibration | **improved** | four critic/reviewer falsifications folded same-round (label honesty, vacuity guard, predicted-vs-measured -ss, dead regex anchor); verifier AGREE byte-identical ×5; post-fold integrator re-run clean |

Sol `r75-adjudicator.md`: ADMIT-corr — consumer breadth landed with falsifications folded. Bounded: pacat/libpulse 17.0, aplay -D null, ffplay lavf + SDL dummy, this host. Work `db46fba`; folds `5f60747`.
## Round 76 verdict — 2026-10-14

| axis | verdict | evidence |
|---|---|---|
| coverage | **improved** | the RECORD direction armed: 6 entries over 4 capture consumers — gate/named-failure lattice, bounded ops, TERM/KILL sever wound classes, name axis, device axis, monitor roundtrip |
| depth | **improved** | per-consumer wound partition measured at byte level (riff=8/data=0 reject vs 0x80000000 accept-and-lie vs 0xFFFFFFFF inflate); unpaced null oracle + parecord dead-start + 64KiB/256KiB flush granules; cross-decoder disagreement surface (alsa-utils predeclares requested duration) |
| calibration | **improved** | zero-audio vacuity closed (D1 — the defect was live in landed receipts); 4 unchecked legs armed; coverage totality on sever/gate; canonical sha rescoped quiescent-host after verifier measured the teardown-contention mechanism |

Sol `r76-adjudicator.md`: ADMIT-corr — capture lattice landed; the real defect (zero-audio TERM vacuity) and all unchecked-leg surfaces folded. Verifier AGREE on byte claims, N1-N3 folded/noted. Bounded: PipeWire 1.6.8 / pacat 17.0-98 / alsa-utils 1.2.16 / ffmpeg n9.0.1, this host. Work `d566a31` + folds `18deef6`.

## r77 — capture-source lattice + fallback law (wave-17)

| axis | move | evidence |
|---|---|---|
| coverage | **improved** | 6 new probe entries: target-loss sustain, 12-row source lattice (incl. discriminating probe-owned sink), 5-reader severed-WAV matrix, arecord bound-derived headers, 2 GiB split sentinel, format conversion/refusal axis |
| depth | **improved** | `stream.capture.sink` fallback law pinned (identity not silence); real target-loss transition measured (98→104→102 % + sink→fallback topology); 32×/5.05× reader inflation; usage_refusal vs bounded-capture rc=1 partition |
| calibration | **improved** | 4-seat exclusivity-guard defect closed; N2 wall-leg vacuity armed (was rc-0 no-op on a dead sink); F5 +2048 MB RSS streaming fix; sink_gone source/sink enumeration vacuity armed; 18.6 % contention false-alarm class named |

Sol `r77-adjudicator.md`: ADMIT-corr — fallback law + reader matrix + split sentinel armed; every consensus vacuity folded; r76 drift classified host-state (pre-fold HEAD repro + named contention class). Bounded: PipeWire 1.6.8, DualSense-default-source topology, this host. Work `65790f1` + fold `1a84ca7`.

## r80 — module-null-sink arg lattice + topology ops (wave-19)

| axis | move | evidence |
|---|---|---|
| coverage | **improved** | 10 legs over `pactl load-module`: arg lattice (passthrough props, rate=99999 no range check, media.class flip, linger orphan) + topology ops (`@DEFAULT_SINK@` refusal, `pw-link` linger/`-m` split, move-sink-input sticky vs `node.dont-move`) |
| depth | **improved** | linger-orphan lifecycle end-to-end (survives unload, stale pmid, pactl-invisible, `pw-cli destroy` only); falsified "dropped" model replaced by measured passthrough; stale-id foreign-kill window closed with live-citation guard |
| calibration | **improved** | F1–F8 + B2/B3 + scribe prose defects all folded same-round; strict readers end the absence-witness fail-open; verbatim column pinned to its named receipt |

Parent `r80-adjudicator.md`: ADMIT-corr — 4 green runs on final bytes; every wave-B finding folded or named. Bounded: PipeWire 1.6.8 / libpulse 17.0 / WirePlumber 0.5.17, shared host (by-name unload banned, disposable-daemon probes parked).

## Round 77 verdict — 2026-10-15

| axis | verdict | before → after evidence |
|---|---|---|
| coverage | **improved** | Six new `--probe-capture-r77` entries over the record-side frontier — target-loss sustain, 12-row source lattice (incl. the discriminating `prop_probe_sink` row), five-reader severed-WAV matrix, arecord bound-derived headers, 2 GiB split sentinel (`<name>-01.wav`), format conversion vs `usage_refusal`. Adjudicator: "Reader matrix CONFIRMED + armed" (all five readers honestly report 96,000 frames; fold asserted this fail-closed), "Split sentinel CONFIRMED". Work `65790f1` + fold `1a84ca7`. |
| depth | **improved** | Adjudicator: "Fallback law CONFIRMED" — the sink is never captured without the prop; unresolvable/`default`/source-name targets all land the current default sink's monitor (identity, not silence); `sustained_after_target_loss` reproduced byte-exact. Folded wall leg measures the real transition (98→104→102 % rate buckets, probe sink → SPDIF fallback, `probe_sink_gone: true`); 32×/5.05× reader inflation; `usage_refusal` vs bounded-capture rc=1 partition. Work `65790f1`; folded receipt `20261014T210316456683Z`. |
| calibration | **improved** | Adjudicator: "N2 wall-leg vacuity FIXED in fold" — the wall leg had run `pactl unload-module ""` (rc-0 no-op on a dead sink); fold adds a fresh per-run `r77_loss_sink_<pid>` + fail-closed unload-fired / pre-loss-consume checks. Also "4-seat exclusivity-guard defect closed", `sink_gone` source/sink-enumeration vacuity armed, F5 streaming fix (was +2048 MB RSS), "Contention classes NAMED" (18.6 % roundtrip false-alarm rate; `host_is_quiet` counts `/proc` comm+cmdline), "Seed-mutation surface DISCLOSED" (`ambience.wav` in-place rewrite caught at commit and restored to HEAD bytes). |

Non-author `reports/round-77/r77-verifier.md`: AGREE on all 8 headline claims in its own harness; baseline 125/125 prior rows stable in BOTH phases; verifier 1172 leaves 0 diffs on r76 rows; every consensus defect folded. Provenance caveat: `r77-adjudicator.md` states no per-axis verdict table — the three axis verdicts above are transcribed from the committed wave-17 record (`731937c`, section "## r77 — capture-source lattice + fallback law (wave-17)") and its claim-level calls (CONFIRMED / FIXED / NAMED); no verdict is asserted beyond those. Known limit: the pre-fold A/B leg ("reproduce identically on pre-fold HEAD") had no in-repo artifact until `corpus/live/r77-fold-prefold-ab/` was preserved (`reports/round-78/r78-scribe.md` §5.1). Sol `r77-adjudicator.md`: ADMIT-corr — every four-seat vacuity closed, host-state drift named rather than asserted; no demonstrated scoped harm. Bounded: PipeWire 1.6.8 / pacat 17.0-98 / alsa-utils 1.2.16 / ffmpeg n9.0.1, this host, DualSense-default-source topology; no conformance/fidelity/audibility/production inference. Work `65790f1` + fold `1a84ca7`; report-last `731937c` (round closed 2026-10-14).

## Round 78 verdict — 2026-10-15

| axis | verdict | before → after evidence |
|---|---|---|
| coverage | **ADMIT-corr (no per-axis call)** | Adjudicator claim-level: "Target lattice CONFIRMED" — `--target` flag, `target.object` prop, `node.target` and `PIPEWIRE_PROPS` env resolution armed with content-verified taps (fold requires a *bound* witness tap; `monitor_name` got a second peer tap). "Host-confound accounting ARMED" — zeros legs snapshot the producer edge before unlink; foreign/mis-routed binds record `setup misroute — class never armed` (named confound, blocked coverage) instead of a false class failure. 8 new `--probe-capture-r78` entries / 60+ legs (verifier: 25 rows = 17 ordinary + 8 probes, 70 legs + 1 warmup). Work `d9aa6f9`; fold `a005e1e`. |
| depth | **ADMIT-corr (no per-axis call)** | Adjudicator claim-level: "Default-follow law CONFIRMED + oracle corrected" — the stream follows `default.audio.sink` *metadata* at spawn, not pactl's stored default; a live session-manager re-assertion was caught and classified `default_reasserted` (pactl-vs-metadata divergence named `pactl_unmeasured` coverage). "Stall class ENVELOPE-VERIFIED" — `class_source_stall`/`autoconnect_false` bimodal: never-scheduled (suspended → killed at bound) or scheduled `running` → consume file → rc=0; `stall_realization` recorded, only `other` fails. Work `d9aa6f9`. |
| calibration | **ADMIT-corr (no per-axis call)** | Adjudicator claim-level: "Readiness races FIXED fail-closed" — fresh null sinks must enumerate in `pactl` AND publish `pw-link -i` playback ports (monitor sources: `pw-link -o` output ports) before target legs spawn; `boundary_source` must publish capture ports (probe #6's four `prop_b` fallbacks were enumerated-but-unlinkable ports). Probe arc: #4/#5 invalidated by disclosed sibling contention; #7 stall realization; #8 zero failures (receipt `20261015T055701745739Z`). Work `d9aa6f9`; fold `a005e1e`. |

Non-author `reports/round-78/r78-verifier.md` (receipt-level verdict on `d9aa6f9`; canonical receipt `corpus/live/runs/20261014T221945369366Z-capture-r78/measurements.json`, sha256 `45135e3fd524c7c22fa5e3327ec4945c6456f3ff6bf0d2c8666b3226ee45befe`, 25 rows / 70 legs + 1 warmup): leaf-level prior-row stability vs the r77 folded and r76 receipts; findings F1–F7 informational, none touching a verdict. Provenance caveat: `r78-adjudicator.md` gives no per-axis verdicts — the `ADMIT-corr` cells are transcribed as-is and the axis rows group its claim-level calls; no axis verdict is asserted here. Known limit: the two capture arms (`capture_unlinked_zeros_r78`, `capture_parec_fix_r78`) were `coverage_blocked` from 05:50:13Z — durable, and not disclosed by r78's own landing; probe #8's `failures: {}` is true but silent on the blocked coverage (`reports/round-79/r79-scribe.md` F4). Sol `r78-adjudicator.md`: ADMIT-corr — the playback/capture lattice is pinned fail-closed with content-verified taps, spawn-time metadata oracles, readiness gates, and honest confound/coverage classes. Bounded: PipeWire 1.6.8 / pacat-pactl 17.0-98-gb096 / alsa-utils 1.2.16, this host (`plazir27`, DualSense default source); the bimodal stall realization is scheduler-load dependent; #4/#5 receipts retained under `corpus/live/runs/` as the contention-evidence trail. Work `d9aa6f9`; fold/report-last `a005e1e`.

## Round 79 verdict — 2026-10-15

| axis | verdict | before → after evidence |
|---|---|---|
| coverage | **ADMIT-corr (no per-axis call)** | Adjudicator: the pw-loopback `-C`/`-P` binding frontier "lands 66 legs over eight entries" — loopback two-node shape + prop lattice; capture-side default-source fallback (conditional); playback lattice; channel matrix; `pw-record --target` three arms + D17; hot-plug re-links both directions; `node.latency` prop vector + prop-beats-flag; filter-chain module surface. Work `d170df9`; formal runs B/C + run D on folded bytes (`20261015T084630169601Z`). |
| depth | **ADMIT-corr (no per-axis call)** | Adjudicator: b13's unnegotiated branch "measured formally (first positive instance of the fallback law)" — `source_meta` absent while `pactl` enumerated a Line source (the two authorities split live in run D). Playback lattice honors r78's law verbatim with `-o` beating `-P`; channel-matrix mix is position-driven (`mix_half_gain_ratio = 0.500`); `latency_param_tracks_request` vector with 3-entry `latency_param_set`. Work `d170df9`. |
| calibration | **ADMIT-corr (no per-axis call)** | Adjudicator findings disposition: critic C1–C7 FIXED and live-verified (conjunct constant-source gate; tap precedence `B & (O \| I)`; origin-gated excuse; positive law leg); verifier A2 vacuity FIXED (`content_pin_unmeasured` named 6× on vacuous taps); simplifier 16 folds APPLIED (strict 0+0 leaf proof); scribe F1–F11 applied; verifier A1 DISCLOSED pre-existing (r78 `wait_source`, owner r80); boundary 7 classes recorded host-bounded. Work `d170df9`. |

Non-author `reports/round-79/r79-verifier.md`: independent V1/V2 replays green; 681 verdict-bearing keys byte-stable across B/C/V1/V2 modulo pid tags; two receipted forge-kills (F-union, F-tap) fail closed; recommendation ADMIT-with-notes (A1 handed up pre-existing, A2 softness on never-fed legs). Provenance caveat: `r79-adjudicator.md` gives no per-axis verdicts (overall `ADMIT-corr` only) — cells transcribed as-is, axis rows group its claim-level calls; no axis verdict is asserted here. Recorded limits: `foreign_tone_on_shared_monitor` is unexecuted in every r79 receipt (`reports/round-79/r79-scribe.md` F1); the labrat H1 "absent from man pages" sub-claim is falsified — the string ships in `libpipewire-module-protocol-simple(7)` (F2). Bounded: PipeWire 1.6.8 / pactl 17.0-98-gb096 / Python 3.14.7 (numpy 2.5.3), this host; boundary classes host-bounded; `source_meta` (metadata/wpctl) and `source_pactl` (pactl enumeration) are different authorities. Work `d170df9`.

## Round 80 verdict — 2026-10-15

| axis | verdict | before → after evidence |
|---|---|---|
| coverage | **improved** | pactl module-lattice surface armed: 10 legs over the `load-module` arg lattice (derived-vs-passthrough `description`, no range check on `rate` (99999), `media.class` flip, linger orphan) + topology ops (`@DEFAULT_SINK@` refusal, `pw-link` linger vs `-m`, move-sink-input sticky vs `dont-move` no-op). Author `+905/−3`; receipts `134206` (disclosed failing), `134359`, parent `152510` all `failures: {}`. Work `ed799e5`. |
| depth | **improved** | The linger-orphan lifecycle measured end-to-end (survives unload, stale pmid, pactl-invisible, `pw-cli destroy` only); passthrough-prop mechanism corrected against the falsified "dropped" model (`description=` lands as a literal prop; `node.description` stays derived); stale-id hazard closed with a live-citation discriminator. Work `ed799e5`. |
| calibration | **improved** | F1 model correction; F2 safety guard — `_module_r80_unload_own` skips LIFO-recycled stale ids (`already_unloaded`/`foreign_risk`) instead of blind-firing into a possible foreign module, with `client_id` as the only live-vs-stale discriminator; F3 vacuity armed (strict readers + `coverage_blocked`, absence witnesses no longer fail open); verbatim column pinned to its named receipt; two bimodal-adjacent hazards (recycle window, reader fail-open) converted to named classes. Work `ed799e5`. |

Non-author `reports/round-80/r80-verifier.md`: CONFIRM — 4th green run, 266 leaf keys ×4 runs, 0 non-volatile diffs; hygiene held under real concurrency (sibling pid observed mid-flight, zero residue); run D `20261015T161018039047Z` green on folded+corrected bytes. Parent `r80-adjudicator.md`: ADMIT-corr — four green runs on the final bytes; every wave-B finding folded or named (F1–F8 + boundary B2/B3 + scribe prose defects). Note: a wave-19 summary section (`## r80 — module-null-sink arg lattice + topology ops`) was already committed at `ed799e5` and is preserved verbatim above; this section is its canonical-format restatement carrying the adjudicator's own per-axis table. Bounded: PipeWire 1.6.8 / libpulse 17.0 / WirePlumber 0.5.17, this host; shared-host constraints recorded (by-name unload banned, disposable-daemon probes parked). Work `ed799e5`.

## Round 81 verdict — 2026-10-15

| axis | verdict | before → after evidence |
|---|---|---|
| coverage | **improved** | `--probe-gst-r81` arms the GStreamer↔PipeWire binding lattice: post-fold 54 legs over 7 entries — prop grammar + two-key `target-object=` write, element-prop precedence (inverse of r78's law), `device=` silent fallback vs strict refusal, direction-split target loss, `PIPEWIRE_REMOTE` decisiveness, env-vector precedence, exit-class lattice, autodetect→pulse path. Fixture `+1686/−3` then fold `+50/−75`; family receipts green on folded bytes (verifier2 `09a0b6f8…`). Work `6aa03e6` + fold `07c0671`. |
| depth | **improved** | Capture-freeze law promoted from observation to mechanism: `gstpipewiresrc.c:1207` unconditional `DONT_RECONNECT` → WirePlumber `prepare-link.lua:73` drops re-links; freeze lands on the PipeWire quantum grid; `on-disconnect` inert after true peer death. Author corrections: `client.name` is null (name rides `application.name`), STRING `"TRUE"/"FALSE"` prop landing, `pipewiresrc target-object=<ns>.monitor` lands default-sink monitor. Work `6aa03e6`. |
| calibration | **improved** | Two scout falsifications folded: hex constant `0x7FFFF000`→`0x7FFF0024`/`0x7FFF0000` (freeze predicate now PINS the corrected constants — reviewer F1 dead-acceptance criterion closed); `num-buffers` exact on pulse record path. Claim corrections on record (exit-count 6/8; truncated wavenc klass). Simplifier S1–S9+L1 proven-folded; dead leg p8 removed; vacuous assertions made substantive (e3/e8/e9 real out_paths). Work `07c0671`. |

`r81-adjudicator.md` (orchestrator): ADMIT-corr — eleven seat reports on record; all gate findings folded or named. Non-author verification: `r81-verifier.md` VERIFIED-WITH-RESERVATIONS on `6aa03e6` (transient reds = sibling-lane contention, `normal` byte-identity exonerated); `r81-verifier2.md` VERIFIED on folded `07c0671` (54 legs, corrected constants pinned, `normal` sha 7-way identical). Deferred: reviewer F2 dont-reconnect fixture framing (mechanism scout covers); comm-keyed quiet-check blind spot; 5/12 shipped configs unmeasured (second-PipeWire refusal, shared host). Bounded: PipeWire 1.6.8 / GStreamer 1.28.6 / WirePlumber 0.5.17 / Python 3.14.7, this host; capture-r78 follow leg contention-sensitive by construction. Work `6aa03e6` + fold `07c0671`; record `f91c7d0` + this commit.
