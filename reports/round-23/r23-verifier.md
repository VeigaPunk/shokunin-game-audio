# Round 23 independent verifier (r23-verifier)

## Result

**FAIL — do not accept the appended 13-file table unchanged.** The table's current 13-file numeric observations, comparator polarities, eligible counts and cited control classifications independently check out against the raw receipts and source, and the required replay passed. However, the same knowledge document contains a concrete source-description error in the immediately preceding historical section (called out below). Correct it in a later authorized edit; I did not edit it. The SHONEN box 4 remains open. This is a document/code/fixture audit, not an assessment of sound quality.

## Scope and evidence

Read the round-23 claim and eight wave-1 reports, `measure_audio.py`, `build_artifacts.py`, the current decision table, the round-22 raw receipts and `r22-verifier.md`. Recomputed each table's numerical family from the 13 canonical raw measurement records in the non-author round-22 normal receipt `20261013T010810788169Z-normal/measurements.json`, the four section records and five distinctness records. Checked named control receipt complete failure sets, including all six invalid-probe outcomes, plus the prior negative/edge receipts against the verifier's ledger. No authored threshold or code/fixture/WAV was changed.

## Independent recalculation of all current-table rows

- **Format:** 13/13 canonical entries are 48,000 Hz mono `pcm_s16le` / 16 bits; categorical equality, no numeric margin. This is encoded PCM width, not valid-bit precision.
- **Duration:** 13/13 receipt durations equal their per-name spec at receipt precision; tolerance is `abs(duration-target) <= .001 s` (fails only `>`), hence nearest margin `.001 s` for each. Targets include `.12, .16, .24, .32, .36, 2, 4 s`.
- **Peak/RMS:** maximum peak `.808776855` (`impact`), so strict `<.95` headroom is `.141223145 FS`. Minimum reconstructed linear RMS `10**(rms_dbfs/20) = .026099737` (`stem_layer_alt`), so inclusive `>=.001` margin is `.025099737 FS`. The legacy `rms_min_exclusive` label is misleading; source accepts equality.
- **Centroid:** recomputed each of 13 distances to its own inclusive band; all table distances match, minimum `31.616408 Hz` (`ambience`). Receipt `spectral_bandwidth_hz` is not a gate.
- **Outer loop seam:** exactly 7 eligible loop fixtures (the other 6 are null/not applicable). Endpoint range `.000671387–.011383057`; maximum `.011383057`, margin `.018616943` below inclusive `.03`. Slope range `0–.000915527344`; maximum `.000915527344`, margin `.000084472656` below inclusive `.001`.
- **Section component validity/contrast:** exactly 4 section records (30/120/180/200 Hz). Recomputed all 8 amplitudes `.011999465109–.059998071188` (nearest inclusive `.01` floor margin `.001999465109`); all 8 RMS `.008484994006–.076155261259` (nearest `.001` floor margin `.007484994006`); signed `20log10(A2/A1)` contrast `10.457242998–13.979508034 dB` (nearest inclusive 6 dB margin `4.457242998`). This is component-bin amplitude contrast, not total section energy.
- **Internal join adjacent gap and side-slope:** exactly 3 gated layered-stem section records; `stem_sections` telemetry is not gated here. Gap `.000183105469–.000396728516`, margin `.029603271484` below inclusive `.03`. Side-slope `.000762939453–.000915527344`, margin `.000084472656` below inclusive `.001`.
- **Distinctness:** exactly five `_alt` records. Recomputed duration/relative-centroid pairs are `ui_alt (.04,.471877310)`, `impact_alt (0,.956304899)`, `movement_alt (.12,.007518619)`, `ambience_alt (0,.584513632)`, `stem_layer_alt (0,.461799314)`. Rule is duration `>=.020 s OR` centroid relative delta `>=.10`; each passing branch and listed margin are correct. This is not perceptual distinctness.
- **LUFS:** seven finite values `-30.7, -24.7, -15.8, -24.7, -29.3, -32.7, -32.6`; six are null. There is no LUFS acceptance window. Null after the `<= -70` ebur128 handling does not mean silence.

## Control receipt audit

The newly replayed invalid bundle's complete set is `short_sections: section count`, `corrupt: decode`, `wrong_format: format`, `odd_sections: section count`, `native16_probe: no failure / expected_pass`, `native24_probe: format / expected_failure`. The corrupt probe's ffprobe exit 1 is intentional and recorded; runner mode exit 1 is expected. `wrong_format` changes both rate and channels (44.1 kHz stereo), so their individual effects are confounded. PCM16/PCM24 controls are matched at 48 kHz mono and establish only those tested native encodings.

The historical raw receipt/report failure sets support the table's classifications: `probe-failing` ambience fails both centroid and outer endpoint (confounded); `probe-slope` fails only outer slope; 30/120/180 Hz flat and reverse-180 controls fail contrast; the 200 Hz internal join and side-slope edge pairs have pass receipts and fail receipts whose only failure is respectively internal gap / internal side-slope. No receipt establishes isolated peak, RMS, duration edge, centroid edge, section component/RMS floor, or general format compatibility. Edge pairs are tested decoded values, not continuous calibration.

## Serial replay, exact commands and receipts

Ran from repository root, in this order; intentional failing controls return 1. There were **no runner/setup errors**. (Four early attempts made with a malformed shell quoting wrapper returned shell 127 before invoking Python; discarded and immediately rerun correctly below. They created no receipts and are not runner results.)

| Command | Exit | Fresh receipt / observed result |
|---|---:|---|
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `corpus/live/runs/20261013T011828304599Z-normal/measurements.json`; 13/13 pass, five variants pass |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-invalid` | 1 expected | `corpus/live/runs/20261013T011828577717Z-invalid/measurements.json`; six expected statuses as listed above |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-pass` | 0 | `corpus/live/runs/20261013T011839878741Z-layer-third-join-edge-pass/measurements.json`; no failures |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-join-edge-fail` | 1 expected | `corpus/live/runs/20261013T011840772732Z-layer-third-join-edge-fail/measurements.json`; sole failure internal join adjacent gap `> .03` |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-pass` | 0 | `corpus/live/runs/20261013T011841645918Z-layer-third-slope-edge-pass/measurements.json`; no failures |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-third-slope-edge-fail` | 1 expected | `corpus/live/runs/20261013T011842494877Z-layer-third-slope-edge-fail/measurements.json`; sole failure internal side-slope `> .001` |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` (restored normal) | 0 | `corpus/live/runs/20261013T011843291086Z-normal/measurements.json`; 13/13 pass, five variants pass |

Initial and restored normal JSON are equal after recursively excluding `path` identity. All five normal/edge receipts have the same threshold object. Values remain 48,000 Hz, duration `.001`, peak `.95`, RMS `.001`, outer and internal gap `.03`, outer and internal slope `.001`, contrast 6 dB, component floor `.01`, section RMS `.001`, distinctness `.02 s` / `.10`, and the same centroid bands. Invalid receipt has no threshold object by schema design.

## Baseline integrity

Compared SHA-256 of every canonical `corpus/artifacts/*.wav` against `git show 64e6088794371769e31e0a6fc9ae0f2f2e0c91dd:.shokunin/audio/corpus/artifacts/<name>`: **13/13 byte-identical**. `measure_audio.py` SHA-256 is `4134727a85970d64ffee8ef206ae6ab0a00c857eb01f547a626457cee86bf178` and `build_artifacts.py` SHA-256 is `52f5f47b7f9c9560e70cf74b32bbb72d844cbf6c1fb5951ec7f06d32f4b0f02c`; both match the same baseline commit. No numerical threshold changed.

## Explicit document error and assessment

The knowledge file's pre-existing historical “Decision boundary and untested cases” says `section_contrast()` “splits samples and indexes FFT bin 60 **before** checking the 192000-sample predicate,” implying malformed short/odd arrays may raise before a count receipt. That claim is **wrong**: current source checks `if len(samples) != 192000: return ... failure_kind: "section count"` before `np.split`, FFT, or bin indexing. The newly replayed invalid receipt independently shows 144000-sample and 101-sample controls returned section-count outcomes. This is one explicit table-documentation error; the current appended table itself's section count rule/polarity is correct. Do not repeat or rely on the erroneous preceding statement.

The appended table improves auditability of fixture-local present bounds and exposes polarity/margins. It does **not** tune or validate the thresholds as perceptual criteria. No auditory quality, perceived seamlessness/distinctness, external JSON consumer compatibility, arbitrary valid-bits handling, engine behavior, rights, or production suitability is established. SHONEN box 4 stays open.


## Addendum — 2026-10-13: historical count correction recheck

I re-read the appended correction at the end of `.shokunin/audio/corpus/knowledge/2026-10-12-threshold-calibration.md` against current `measure_audio.py:section_contrast()` and my fresh invalid receipt `corpus/live/runs/20261013T011828577717Z-invalid/measurements.json`. The correction is accurate: for every decoded sample count other than 192000, the function returns the structured `failure_kind: "section count"` before splitting or FFT indexing. The receipt confirms `short_sections` at 144000 and `odd_sections` at 101 both report `observed_failure: "section count"` and `status: "expected_failure"`. It accurately limits the evidence to these two lengths, rather than claiming universal malformed-input handling.

**Disposition: the corrected whole knowledge artifact resolves the specific documentation defect behind my initial FAIL.** Retaining the initial FAIL above as the original point-in-time verdict, my follow-up verdict is **PASS for the declared document-only calibration auditability move**, with the complete current 13-file table evidence retained: all 13 canonical format/duration/level/centroid observations, seven eligible outer-loop observations, four section records and their component/RMS/contrast values, three eligible internal-gap/slope observations, five distinctness pairs, all threshold comparator polarities and nearest-margin arithmetic; cited isolated vs confounded control status and the full invalid-control failure set; 13/13 canonical WAV baseline hashes; unchanged source and builder hashes and unchanged thresholds; and fresh serial normal, invalid, join/slope edge pass/fail, restored-normal receipts with expected exits and path-excluded normal equivalence. The specific correction is now source- and receipt-consistent.

This pass is only for auditability/disclosure and unchanged implementation behavior, not threshold tuning or validation of thresholds as perceptual standards. Still unproven: perceptual quality/seamlessness/distinctness; boundary behavior beyond the named decoded points; arbitrary malformed-file handling; external JSON consumer compatibility; general codec/container or WAVE_FORMAT_EXTENSIBLE valid-bit behavior; engine/runtime suitability; security, rights, and publishing claims. SHONEN box 4 remains open.
