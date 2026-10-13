# Round 27 numeric decision table — scribe

## Decision rule and declared values

The LOG claim is calibration of the existing distinctness duration arm, `duration_delta >= .020`, with the centroid arm held below `.10`. A pair passes when either arm passes. No source-generated candidates or integrated round-27 receipts are present in the inspected workspace, so there are **no observed runtime measurements or exits to report**. The values below are declared/nominal frame arithmetic, not observed ffprobe outputs.

| Case | Base → variant frames (48 kHz) | Declared durations | Nominal delta | Expected duration arm | Expected centroid arm | Expected distinctness result |
|---|---:|---:|---:|---|---|---|
| Below | 5760 → 6719 | 0.120 s → 0.1399791666667 s | 959/48000 = 0.0199791666667 s | false (`< .020`) | false only if measured relative delta `< .10` | fail, duration branch isolated |
| At threshold | 5760 → 6720 | 0.120 s → 0.140 s | 960/48000 = 0.020 s | true (`>= .020`) | false only if measured relative delta `< .10` | pass via duration branch |

Both variants must first pass their own measurement specs: base duration 0.120 s, below variant 0.1399791666667 s, at variant 0.140 s; otherwise identical UI band, format, and level constraints. Measuring either longer variant against the existing 0.120 s UI duration spec would produce a duration-spec failure, not evidence about distinctness.

## Observed results / execution status

| Item | Observed |
|---|---|
| Candidate WAV metadata, ffprobe durations, measured deltas | Not available; no round-27 scratch candidates found |
| Centroid-relative deltas / per-file spec checks | Not available |
| Integrated below/at mode receipts and process exits | Not run / not available |
| Existing-mode/hash preservation | Not assessed by this scribe |
| Failed fit | None established. The declared candidates remain unverified, not successful fits. |

No shell command was run for this report; therefore it has no command exit code to attribute.

## Exact proposed invocations (not run here)

```sh
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-below
```
Expected process exit **1** only if the below candidate passes its own spec and fails distinctness solely because duration delta is below .020 while centroid-relative delta is below .10.

```sh
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-duration-at
```
Expected process exit **0** only if the at-threshold candidate passes its own spec and distinctness passes through the duration arm, with centroid-relative delta below .10.

These are the LOG’s proposed mode invocations; they are not evidence that either mode currently exists or has been run. A process exit alone is insufficient: inspect each JSON receipt and classify measurement failures separately from distinctness.

## Rounding, fit, and limits

**Binary-rounding risk (declared, not observed):** nominal `0.140 - 0.120` is exactly 0.020 in decimal arithmetic, but the implementation compares ffprobe-derived floating-point values. The observed subtraction may be slightly below the literal `.020`; if so, the at-threshold case does not pass the duration arm. Report that as a failed fit to the declared equality case, not as a pass, and do not change the `.020` threshold. Likewise verify the below case’s actual delta remains below `.020`.

**Possible failed fits (speculation, not observed):** waveform truncation may move centroid by `>= .10`; generated file duration may miss its per-file spec; format, level, or band checks may fail; or the at case may compare below `.020` due to float representation. Any such result confounds or defeats the intended isolation and must be reported as a failed fit, not relabeled as a duration-comparator result. Do not infer these failures without receipts.

This is limited to two source-generated analytical PCM16, 48 kHz mono duration cases and the duration arm of the existing OR predicate. Even successful results would not establish the `.10` centroid boundary, other durations, general floating-point behavior, auditory/perceptual similarity, audio quality, rights, engine behavior, publication, or promotion.
