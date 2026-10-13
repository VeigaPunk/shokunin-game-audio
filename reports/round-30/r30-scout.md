# R30 scout — baseline-denominator orientation map

## Scope and source

Read the declared Round 30 section in `.shokunin/audio/LOG.md` and inspected `corpus/fixtures/measure_audio.py`. This is a source/formula map, not a new fit or execution. The R30 declaration says the comparator uses a baseline denominator, and specifies an exact-byte role swap using the existing `_alt` comparator. No R30 implementation is present in the inspected runner yet.

## Existing formula and suffix mapping

In `measure_audio.py`, for each measurement name ending in `_alt`, the runner sets `base = measurements[name[:-4]]` (removing exactly the `_alt` suffix). It computes:

```python
duration_delta = abs(variant["duration_s"] - base["duration_s"])
centroid_relative_delta = abs(variant["spectral_centroid_hz"] - base["spectral_centroid_hz"]) / base["spectral_centroid_hz"]
passed = duration_delta >= .020 or centroid_relative_delta >= .10
```

Thus `ui_lower_centroid_below_alt` maps to baseline measurement `ui_lower_centroid_below`; denominator is the baseline centroid, not the variant centroid and not a symmetric denominator. A variant is distinct if **either** absolute duration delta is at least 0.020 s or relative centroid delta is at least 0.10. If neither is true, the alt gets `distinctness: duration < .020 s and centroid delta < 10%` added to its failures. Runner overall return is nonzero when any measurement has failures; ordinary fixture checks also apply. The R29 lower-centroid pair was measured with the same `SPECS["ui"]` for both roles (0.120 s, 250–4000 Hz band; format check requires 48 kHz mono PCM16).

## Expected role-swapped ratios

Using the R30-declared R29 measured centroids (baseline 966.8966593379727 Hz; variant 871.155504521436 Hz; both same-duration), the absolute gap is 95.7411548165367 Hz:

| Roles | Calculation | Expected distinctness result (duration delta 0) |
|---|---:|---|
| Forward: higher centroid baseline, lower centroid `_alt` | `95.7411548165367 / 966.8966593379727 = 0.0990190150` | Below `.10`; fails the centroid arm, so not distinct |
| Swapped: lower centroid baseline, higher centroid `_alt` | `95.7411548165367 / 871.155504521436 = 0.1099013372` | Above `.10`; passes the centroid arm |

The exact same waveforms in reversed roles should therefore yield the declared below/above cutoff outcomes solely because the denominator follows the baseline role. Byte-identity checks should be `SHA(forward-base) == SHA(reverse-alt)` and `SHA(forward-alt) == SHA(reverse-base)`. Both files must independently pass their ordinary canonical UI checks for this comparison to isolate the relative-centroid result.

## Caveats / evidence boundary

This predicts the orientation result from the declared measured pair; it does not establish a new R30 replay, receipt, SHA match, or ordinary-check result. Round 30 explicitly requires preflight measurement and falsification if empirical waveform/float results do not cross the cutoff. The ratios are rounded here; do not treat them as exact-threshold evidence. This is only a numeric property of this baseline-denominator comparator and this pair—not an audio-quality or perceptual-similarity conclusion, nor a normative claim that the comparison should be symmetric. No new normalization or threshold change is implied. Failed fits and setup errors are not evidence; none were run for this report.

## Commands and exits

Inspection command run: `pwd; ls -la; find .shokunin -maxdepth 4 -type f 2>/dev/null | sort | head -100` — exit 0. No fixture, build, measurement, fit, or test command was run; there are no command exits or receipts to report for evidence.
