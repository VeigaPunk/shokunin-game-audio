# R40 reviewer — minimal two-mode design

## Scope and recommendation

Add exactly two opt-in runner switches, e.g. `--probe-ambience-loop-edge-pass` (983 PCM counts) and `--probe-ambience-loop-edge-fail` (984 counts). Each switch asks the builder for one independently named WAV under `corpus/live/round-40/`, then measures only that scratch file using the existing `measure(name, (2.0, 5, 200, True), path)` function. Do not add a comparison pair, alter canonical artifacts, add shared thresholds, or change the generic `_alt` / family calculations. Keep `SPECS`, generic distinctness, and all five `_alt` and four family comparisons unchanged; register the measured scratch result separately from those dictionaries or add it only after their generic calculations.

## Builder fit

Use one deterministic source generator parameterized by endpoint gap count (983 or 984), with 96,000 samples at 48 kHz, mono PCM16. A low-frequency bed (for example, a 60 Hz sine) provides nonzero level and centroid in the existing 5–200 Hz band. Convert to PCM16 using the existing `save` convention. Pin the first endpoint to an integer `a` and the last to `a + gap_counts`, within signed PCM16 range. Set neighboring samples to `first + k` and `last - k` for the same small integer `k`; then decoded outer side-slope mismatch is zero counts (subject only to SoX float conversion), while the endpoint difference remains exactly the requested count. Choose `a`/`k` so neither endpoint clips. Save distinct named files for the two modes; hash each emitted WAV in the receipt or report so the samples are auditable.

The strict existing endpoint comparison stays `seam_delta > .03`. Expected decoded differences are 983/32768 = 0.029998779296875 and 984/32768 = 0.030029296875 FS. With all ordinary checks satisfied, the pass mode has no failures and runner exit 0; fail mode has exactly `loop seam: endpoint jump > .03 full scale` and exit 1. The side-slope check remains the existing `<= .001 FS/sample`; no comparator or spec changes are needed.

## Runner and error accounting

Mirror the established one-probe pattern: argparse mutually-exclusive mode flags, a corresponding builder flag, a scratch-path selection, and the explicit spec above. Record mode, scratch path/hash, measurements, and failures in the normal JSON receipt. Do not classify an expected numeric fit failure as setup failure: a completed measurement with a receipt and the sole endpoint failure is a numeric miss (expected for 984). Builder/decoder/tool invocation failure before valid measurement is setup/tool failure; record exact command, process exit code, stderr, and absence of valid gate measurement separately. A missing receipt is not a numeric verdict. A runner-level exit 1 alone does not distinguish these cases.

## Execution evidence

No shell commands were run for this review; there are no command exit codes or new decoded sample measurements to report. Values above are the requested mathematical PCM16 targets, not observed results. Do not claim either fixture passed its format, duration, level, centroid, slope, or gate fit until its generated WAV has actually been decoded and the JSON receipt inspected.

This calibration is limited to numerical behavior of this fixture-local PCM16/SoX loop gate. It does not establish an exact real-number equality case at .03, an audible click/seam threshold, sound quality, production readiness, rights, engine behavior, or publish/promotion suitability.
