# R52 scribe — independent replay ledger and evidence classification

## Scope / status

This report records wave-1 source reports and defines the exact 64-command non-author replay sequence: the declared two R52 probes, then the full R51 62-command sequence in its existing order. **This scribe did not run the 64-command replay.** Therefore every row below is a command specification, not an execution receipt; exits and receipt paths must be populated only by the non-author runner from its actual run. Do not count earlier R51 receipts or scratch/helper commands as replay rows. No verdict is offered.

## Pair evidence already reported (not replay evidence)

Executor's original pair is in `.shokunin/audio/corpus/live/round-52/executor/`; the independent alternate is `.shokunin/audio/corpus/live/round-52/alt/`. Both reports used 5,760-frame mono 48,000-Hz WAVs and the unchanged `measure(..., SPECS["ui"], path)`.

| Pair | PCM8 metadata / SHA-256 | PCM16 metadata / SHA-256 | Project measurements (PCM8 / PCM16) | UI result |
|---|---|---|---|---|
| Executor | `pcm_u8`, 8-bit, SHA `74dd0a3d7a5218e9ead995d14f118beb2118c0f163ce086d406415ce368efb37` | `pcm_s16le`, 16-bit, SHA `b09eb7e624813cd9734e6f4c3b373f7842fb44900737138d7c841c1ad2333344` | peak `.3125` / `.3125`; RMS `-14.699802598426999` / same dBFS; centroid `1581.8516662990894` / same Hz; duration `.12` / `.12`; 5,760 SoX-f32 values each, exact vector equality, max abs difference 0 | PCM8 sole `format: expected PCM16`; PCM16 no failures |
| Alternate | `pcm_u8`, 8-bit, SHA `0020bae326c373083f0e25be9b9362ef628b3ae0f2daf3942e5dee14d48c706c` | `pcm_s16le`, 16-bit, SHA `40ba4ae4a7231b9072a29b734005a4f64e87331d91b49c4cd93582daecbb6db2` | peak `.34375`; RMS `-14.981981404018596` dBFS; centroid `2897.653252566734` Hz; duration `.12`; 5,760 values each, decoded SHA both `dc30251b3580c197f2937ce9c48b716ee87d56470b9fd6bb78cd1be4d34a01b6`, exact equality, max difference 0 | PCM8 sole `format: expected PCM16`; PCM16 no failures |

These are two specifically grid-matched constructions: unsigned PCM8 centered by subtracting 128, and PCM16 formed by multiplying signed PCM8 values by 256. Both reports say all other UI bounds passed (duration ±.001 s, peak <.95, RMS >=.001, centroid 250–4000 Hz). Do not generalize equality or acceptance beyond these constructed files/current decode path.

### Commands actually reported by pair authors

Executor: `python3 .shokunin/audio/corpus/live/round-52/executor/generate.py` exit 0; `python3 .shokunin/audio/corpus/live/round-52/executor/measure.py .shokunin/audio/corpus/live/round-52/executor .shokunin/audio/corpus/fixtures/measure_audio.py` exit 0; two listed SoX decode commands each exit 0; ffprobe per-file command exit 0. Alternate: `python3 .shokunin/audio/corpus/live/round-52/alt/generate_pair.py` and `.../measure_pair.py` exit 0; two SoX decode commands and per-file ffprobe exit 0; vector comparison command exit 0. Full invocations and results are preserved in `r52-executor.md` and `r52-alt.md`.

## Setup, gate, and transcription classification

- **Setup only:** Executor's initial measurement attempt used scratch outside the `.shokunin/audio/corpus` root and exited 1 with `ValueError` from the measurer's `relative_to` path handling; it moved the scratch into the allowed corpus root and reran successfully. This is not an audio gate or numeric-fit failure.
- **Numeric fit:** Neither reported selected pair had a failed duration/level/centroid fit. The PCM8 `format: expected PCM16` result is the intended format-predicate failure, not a setup failure and not a numeric fit.
- **Transcription:** No speech-to-text/transcription was run or reported; status is **not tested**, not pass/fail. No report transcription correction is recorded.
- The separate scout identification WAV's ffprobe metadata is not a project UI measurement and not an added replay row. The reviewer report is a source/integration proposal only, not a CLI execution.

## Exact 64-row fresh replay ledger

Run serially from repository root with the exact commands shown. Rows 1–2 are PCM8 and PCM16; rows 3–64 are R51 verifier's original 62-command order shifted by two positions. Every command must produce a distinct newly created receipt; use actual stdout/receipt exit data to complete the final two columns. Expected failure exit 1 is fixture validation, not shell/setup failure. No row may be inferred from prior receipts.

| # | Exact command | Receipt (fill with actual new path) | Exit / failures (fill from actual run) |
|---:|---|---|---|
| 01 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm8` | pending | pending — not run by scribe |
| 02 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16` | pending | pending — not run by scribe |
| 03 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | pending | pending — not run by scribe |
| 04 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm24` | pending | pending — not run by scribe |
| 05 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-pcm16` | pending | pending — not run by scribe |
| 06 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-channel-stereo` | pending | pending — not run by scribe |
| 07 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-channel-mono` | pending | pending — not run by scribe |
| 08 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-48001` | pending | pending — not run by scribe |
| 09 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-48000-r49` | pending | pending — not run by scribe |
| 10 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-47999` | pending | pending — not run by scribe |
| 11 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-48000` | pending | pending — not run by scribe |
| 12 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-upper-centroid-below` | pending | pending — not run by scribe |
| 13 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-upper-centroid-above` | pending | pending — not run by scribe |
| 14 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-absolute-centroid-below` | pending | pending — not run by scribe |
| 15 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-absolute-centroid-above` | pending | pending — not run by scribe |
| 16 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-tolerance-5713` | pending | pending — not run by scribe |
| 17 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-tolerance-5711` | pending | pending — not run by scribe |
| 18 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-tolerance-5807` | pending | pending — not run by scribe |
| 19 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-tolerance-5809` | pending | pending — not run by scribe |
| 20 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-crest-46` | pending | pending — not run by scribe |
| 21 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-crest-47` | pending | pending — not run by scribe |
| 22 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-peak-31129` | pending | pending — not run by scribe |
| 23 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-peak-31130` | pending | pending — not run by scribe |
| 24 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-32` | pending | pending — not run by scribe |
| 25 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-slope-33` | pending | pending — not run by scribe |
| 26 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-endpoint-983` | pending | pending — not run by scribe |
| 27 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-outer-endpoint-984` | pending | pending — not run by scribe |
| 28 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-forward` | pending | pending — not run by scribe |
| 29 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-orientation-reverse` | pending | pending — not run by scribe |
| 30 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-above` | pending | pending — not run by scribe |
| 31 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ambience-centroid-below` | pending | pending — not run by scribe |
| 32 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-mixed-pass` | pending | pending — not run by scribe |
| 33 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-joint-below` | pending | pending — not run by scribe |
| 34 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-forward` | pending | pending — not run by scribe |
| 35 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-orientation-reverse` | pending | pending — not run by scribe |
| 36 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-below` | pending | pending — not run by scribe |
| 37 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-lower-centroid-above` | pending | pending — not run by scribe |
| 38 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-below` | pending | pending — not run by scribe |
| 39 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-centroid-above` | pending | pending — not run by scribe |
| 40 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below` | pending | pending — not run by scribe |
| 41 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at` | pending | pending — not run by scribe |
| 42 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-clone` | pending | pending — not run by scribe |
| 43 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | pending | pending — not run by scribe |
| 44 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | pending | pending — not run by scribe |
| 45 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join` | pending | pending — not run by scribe |
| 46 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | pending | pending — not run by scribe |
| 47 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | pending | pending — not run by scribe |
| 48 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope` | pending | pending — not run by scribe |
| 49 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-reverse` | pending | pending — not run by scribe |
| 50 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-slope` | pending | pending — not run by scribe |
| 51 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` | pending | pending — not run by scribe |
| 52 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-flat` | pending | pending — not run by scribe |
| 53 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-slope` | pending | pending — not run by scribe |
| 54 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-join` | pending | pending — not run by scribe |
| 55 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat` | pending | pending — not run by scribe |
| 56 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-flat` | pending | pending — not run by scribe |
| 57 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope` | pending | pending — not run by scribe |
| 58 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing` | pending | pending — not run by scribe |
| 59 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | pending | pending — not run by scribe |
| 60 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | pending | pending — not run by scribe |
| 61 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | pending | pending — not run by scribe |
| 62 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | pending | pending — not run by scribe |
| 63 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | pending | pending — not run by scribe |
| 64 | `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | pending | pending — not run by scribe |

## Required replay checks / limits

After all 64 runs, verifier should establish 64 distinct fresh receipt paths; 27 exit 0 / 37 expected validation exit 1 if the declared two new fixture results reproduce and all 62 prior outcomes remain identical. Verify rows 1/2 are PCM8 sole format failure / PCM16 clean; compare the prior62 subsequence (rows 1 and 4–64) exactly to R51 by command, exit, and normalized failure map. Compare first/final normal canonical17 receipts and canonical hashes; confirm prior controls, generic/family comparisons, sections, invalid classifications and normal restoration. This is a replay checklist, **not evidence these conditions have occurred**. Parent's R52 log declares preservation targets; scribe makes no claim they were rerun.

This report is limited to fixture metadata, measurements, and runner-validation bookkeeping. It makes no broad codec, fidelity, audibility, quality, production, rights, engine, publishing, or promotion claim. No shared source, LOG, SCORECARD, canonical artifact, or other report was edited; no commit or push was made.
