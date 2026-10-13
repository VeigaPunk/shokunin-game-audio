# Round 36 reviewer: builder/SPECS review

## Scope and disposition

Review of the declared round-36 change only. No builder or measurement code was executed, no candidate was measured, and no candidate fit or setup failure is established by this review. I did not edit source, canonical artifacts, LOG, SCORECARD, or other reports. This is a minimal-design review, not an integration approval.

## Minimal implementation shape

- Add one deterministic original `ambience_third` synthesis in `corpus/fixtures/build_artifacts.py`, using the existing `time(2)` / `save(...)` pattern and 48 kHz rate. Keep it bounded below the existing peak limit and above the RMS floor. A 2-second integer-cycle periodic signal is a plausible starting point for loop endpoints; its measured endpoint jump and side-slope mismatch still need to be checked by the project helper. Do not treat this suggestion as a fit result.
- Add only `"ambience_third": (2.0, 5, 200, True)` to `SPECS`.
- Add a separate `ambience_family_comparisons` record for comparisons against each of `ambience` and `ambience_alt`, mirroring existing family-comparison code. Preserve the existing OR rule (`duration_delta >= .020 or centroid_relative_delta >= .10`); because all three are intended to be exactly 2 s, the duration arm should be zero and the centroid arm must pass for both records. Include both records in the receipt.
- Leave the generic `_alt` comparison loop and its thresholds unchanged. Do not change older canonical fixtures or existing UI, impact, movement, and stem family checks.

## Review limits / required validation

The receipt's centroid is a weighted whole-waveform numeric proxy, not a measure of perceptual novelty. Endpoint and slope checks are numeric seam proxies only. A passing helper receipt would not establish seamless perception, musical quality, rights, production readiness, engine suitability, publishing, or promotion. The declared 17-fixture count, prior-16 preservation, and replay remain for parent integration/verification.

No shell commands were run; there are no command exit codes or failed setup/fit attempts to report.
