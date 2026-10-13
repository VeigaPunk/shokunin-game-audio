# R40 simplifier — smallest source diff recommendation

## Scope and claim

I read the R40 LOG declaration. Keep the existing `measure()` endpoint check and its strict `seam_delta > .03` comparator unchanged. Add only two fixture-local opt-in modes for a decoded PCM16 endpoint-jump pass/fail bracket; do not generalize the runner or change a threshold.

## Minimal source change

1. In `corpus/fixtures/build_artifacts.py`, add one R40-specific builder that writes two original, deterministic 2.0 s / 96,000-frame, 48 kHz mono PCM16 WAVs under `corpus/live/round-40/`. Construct endpoint samples as exact PCM integers whose decoded absolute difference is 983 counts for pass and 984 counts for fail (respect the decoder's normalized full-scale convention). Make the samples adjacent to the endpoints so the existing side-slope metric is <= .001 FS/sample; retain adequate nonzero level and 5–200 Hz centroid. Add only the two explicit CLI flags and dispatch them to this builder. Avoid changing existing builders or canonical artifacts.
2. In `corpus/fixtures/measure_audio.py`, add the two explicit mutually exclusive flags, map each to its corresponding R40 WAV and existing ambience `(2.0, 5, 200, True)` spec, and include them in the existing mode/receipt naming. Reuse `measure()` and its existing generic failure path. The 983 mode should exit 0 with no failures; the 984 mode should exit 1 with only `loop seam: endpoint jump > .03 full scale`. Do not special-case expected failure into a different threshold or alter the common result logic.

This confines the diff to the existing fixture builder and measurement CLI. No generic helper/refactor, shared fixture edits, scorecard changes, or canonical WAV/threshold changes are needed. Parent should verify decoded samples (not just source float values), WAV hashes, format/frame count, peak/RMS/centroid, seam endpoint and slope values, plus the expected runner receipts.

## Evidence and limitations

I ran no shell commands and made no candidate WAVs, so there are no command/exit receipts or decoded sample measurements from this leaf. The target bracket is the LOG-declared **decoded** delta: 983/32768 = 0.029998779296875 FS (pass) versus 984/32768 = 0.030029296875 FS (fail). These are target measurements, not observed results. Any attempted synthesis that misses the target or fails another numeric gate is a numeric failed fit; missing tools, bad paths, or command/decoder failures are setup errors and should be recorded separately. No audition or sound-quality, production, rights, engine, publish, or promotion claim is made.
