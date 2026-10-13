# Round 23 controls — historical gate controls to raw receipts

## Scope and basis

This is a receipt map, not a rerun. Evidence is the committed round-22 non-author verifier's raw JSON receipts under `.shokunin/audio/corpus/live/runs/` and current `.shokunin/audio/corpus/fixtures/measure_audio.py` source. Round-22 verifier report: `.shokunin/audio/reports/round-22/r22-verifier.md`. It records serial replay order, exit codes, and outcomes. Raw receipt paths below are repository-relative. “Isolated” means the receipt's named synthetic control reports only the intended applicable failure in the runner failure set; it does not establish general validity of the gate or perceptual quality.

No shell commands were used. I read files and receipts directly in Python; no listening, engine, sample-rights, or publishing claim is made.

## Round-22 paired format control

| Control | Raw receipt / fields | Outcome and interpretation |
|---|---|---|
| Native PCM16 positive | `corpus/live/runs/20261013T010824568740Z-invalid/measurements.json`, `native16_probe` | 48 kHz mono, `pcm_s16le`, 16 bits; `expected_pass`, no observed failure. Positive for the implemented narrow PCM16 metadata/rate/channel predicate. |
| Native PCM24 negative | same receipt, `native24_probe` | Matched declared control: 48 kHz mono, `pcm_s24le`, 24 bits; `expected_failure`, observed `format`. Negative isolated to the format family by the receipt. |
| Earlier PCM-width direct probes | The same verifier report cites matched scratch `native_pcm16.wav` / `native_pcm24.wav` measurements, not runner receipts. The files are under `corpus/live/round-22/executor/`; verifier documents exact `measure()` invocations and exits. | PCM16 returned `failures: []`; PCM24 returned only `format: expected PCM16`. Supporting direct-function evidence, distinct from integrated invalid-probe receipt. Do not mistake earlier round-22 pre-change executor/scout/critic fits (which passed both widths) for after-state evidence. |

The runner's invalid receipt is a six-control bundle. Its four legacy controls map as follows:

| Control | Raw receipt / decisive evidence | Isolation / limitation |
|---|---|---|
| `short_sections` | `.../20261013T010824568740Z-invalid/measurements.json`; `section.failure_kind: section count` | Isolated count rejection in this probe. |
| `corrupt` | same; `observed_failure: decode`; ffprobe detail exit 1 | Decode rejection; not a measurement of a numeric audio gate. |
| `wrong_format` | same; 44,100 Hz, stereo, `pcm_s16le`, 16 bits; `observed_failure: format` | Format-family negative, but sample rate and channel count are changed together: their individual contributions are confounded. It is not a PCM-width negative. |
| `odd_sections` | same; `section.failure_kind: section count`, 101 actual samples vs 96,000 per section | Isolated count rejection in this probe. |

## Prior runner control receipts

These are the remaining non-author round-22 serial replay receipts. The verifier reports exit 0 for passes and exit 1 for intentional failures; no execution returned setup exit 2. Paths use the timestamped receipt directory, with `/measurements.json` appended.

| Control class / flag | Raw receipt | Runner result; gate isolation |
|---|---|---|
| Baseline positive, no flag | `.../20261013T010810788169Z-normal/measurements.json` | Exit 0; 13 measurements pass, all four section records pass, five `_alt` distinctness records pass. Positive baseline, not a boundary control. |
| Third-section join edge pass | `.../20261013T010811648246Z-layer-third-join-edge-pass/measurements.json` | Exit 0; `join200_edgepass_probe` adjacent delta `0.029998779296875`, side slope `0`; below the strict `> .03` join rejection. Positive edge control. |
| Third-section join edge fail | `.../20261013T010812495732Z-layer-third-join-edge-fail/measurements.json` | Exit 1; only `join200_edgefail_probe` fails internal adjacent gap; delta `0.030029296875`, side slope `0`. Isolated just over-boundary join negative. |
| Third-section join negative | `.../20261013T010813339890Z-layer-third-join/measurements.json` | Exit 1; only `join200_probe` fails internal adjacent gap; `0.030029296875`, side slope `0`. Isolated join-family negative. |
| Third-section slope edge pass | `.../20261013T010814182622Z-layer-third-slope-edge-pass/measurements.json` | Exit 0; `edgepass_probe` side-slope mismatch `0.0009765625`, below strict `> .001`. Positive edge control. |
| Third-section slope edge fail | `.../20261013T010815030001Z-layer-third-slope-edge-fail/measurements.json` | Exit 1; only `edgefail_probe` fails internal side-slope; mismatch `0.001007080078125`. Isolated just over-boundary slope negative. |
| Third-section slope negative | `.../20261013T010815882922Z-layer-third-slope/measurements.json` | Exit 1; only `slope200_probe` fails internal side-slope; mismatch `0.00115966796875`. Isolated slope-family negative. |
| Alternate-section reverse | `.../20261013T010816730147Z-layer-alt-reverse/measurements.json` | Exit 1; only `reverse180_probe` fails 180 Hz section contrast. Isolated contrast negative (measured contrast `-10.457250572050894` dB). |
| Alternate-section slope | `.../20261013T010817574796Z-layer-alt-slope/measurements.json` | Exit 1; only `slope180_probe` fails internal side-slope; `0.001251220703125`. Isolated slope negative. |
| Alternate-section join | `.../20261013T010818423685Z-layer-alt-join/measurements.json` | Exit 1; only `join180_probe` fails internal adjacent gap; `0.044403076171875`. Isolated join negative. |
| Alternate-section flat | `.../20261013T010819277396Z-layer-alt-flat/measurements.json` | Exit 1; only `flat180_probe` fails 180 Hz section contrast. Isolated contrast negative (0 dB). |
| 120 Hz section slope | `.../20261013T010820134370Z-layer-slope/measurements.json` | Exit 1; only `layer_slope_probe` fails internal side-slope; `0.00115966796875`. Isolated slope negative. |
| 120 Hz section join | `.../20261013T010821007188Z-layer-join/measurements.json` | Exit 1; only `join_probe` fails internal adjacent gap; `0.030914306640625`. Isolated join negative under the code's applied gate (this probe is not in the internal slope gate's name set). |
| 30 Hz section flat | `.../20261013T010821850654Z-flat/measurements.json` | Exit 1; only `flat30_probe` fails section contrast. Isolated contrast negative (0 dB). |
| 120 Hz section flat | `.../20261013T010822692960Z-layer-flat/measurements.json` | Exit 1; only `flat120_probe` fails section contrast. Isolated contrast negative (0 dB). |
| Whole-file loop slope | `.../20261013T010823514996Z-slope/measurements.json` | Exit 1; only `slope_probe` fails loop seam slope. Isolated loop-slope negative. |
| Generic failing fixture | `.../20261013T010824294787Z-failing/measurements.json` | Exit 1; `ambience` fails both centroid band and loop endpoint delta. Confounded two-gate negative; it cannot independently attribute rejection to either gate. |
| Restored baseline positive, no flag | `.../20261013T010825350561Z-normal/measurements.json` | Exit 0; canonical normal restored after probes. Verifier reports parsed initial/restored receipts equal apart from path identity. |

The raw normal receipt includes per-measurement fields (`integrated_lufs: null` for all entries in the inspected normal JSON); source reports LUFS but does not apply it as an acceptance condition. Do not treat a LUFS number or null as a tested gate.

## Missing controls / what is not measured

- **No isolated numeric level controls** are present for peak clipping/headroom or minimum RMS. No isolated duration-boundary or centroid-band-edge controls are present. `probe-failing` is confounded between centroid and loop endpoint; it cannot stand in for either isolated control.
- **Section threshold coverage is partial.** There are isolated flat/contrast negatives at 30, 120, and 180 Hz, but no corresponding explicit near-6 dB pass/fail edge pair, no explicit 200 Hz contrast negative, and no amplitude-floor or section-RMS-floor isolated controls. The section edge receipts target internal join gap and side slope, not contrast.
- **Internal join/slope coverage is selective.** Boundary edge pass/fail pairs exist for 200 Hz join and slope only. No matching boundary pairs across all section frequencies, nor near-boundary control for whole-file seam endpoint delta, are evidenced here.
- **Format control gaps:** `wrong_format` changes rate and channels together, so neither has a separate isolated negative. PCM16/PCM24 paired controls cover only those tested ordinary native WAV encodings. No receipt here tests float PCM rejection in the integrated runner, compressed/other encodings, multiple streams, other containers, or a separately observable extensible-WAV valid-bits predicate. Round-22 alternate's `native24_valid20.wav` metadata challenge is a scratch ffprobe observation, not an integrated runner positive/negative control; queried `bits_per_sample` does not establish valid bits.
- **No claim of complete gate truth table.** Passing canonical records and deliberate failures show only those recorded fixtures/modes. No listening, perceptual acceptability, engine behavior, rights, or publishing property is measured.

## Current-source cross-check

Current `measure_audio.py` defines `format_failures()` as 48 kHz mono plus `codec_name == "pcm_s16le"` and `bits_per_sample == 16`; `measure()` applies this alongside duration, peak/RMS, centroid and seam checks. Section controls use section contrast plus named internal-join gap/slope checks. The invalid-probe path labels controls by expected failure family. This matches the classifications above; it does not turn missing controls into measured evidence.
