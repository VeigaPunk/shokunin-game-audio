# Round 41 scout — outer side-slope map

## Scope

Read the Round 41 declaration in `.shokunin/audio/LOG.md`. This is a read-only source/evidence map; I did not generate or audition audio, run the measurement runner, or edit shared sources, fixtures, LOG, SCORECARD, canonical assets, or any other report. I wrote only this report. No shell commands were run, so there are no command exits or newly decoded counts/receipts from this scout.

## R3 outer loop metric and branch

R3’s `measure(name, spec, path)` decodes the WAV with `sox <path> -t f32 -e floating-point -`, converts samples to float64, and for loop specs computes the two *outer* one-sample increments and their absolute mismatch:

`S_outer = abs((samples[-1] - samples[-2]) - (samples[1] - samples[0]))`.

The runner adds `loop seam: slope mismatch > .001 full scale per sample` only for strict `S_outer > .001`. The companion outer endpoint check is separate: `abs(samples[0] - samples[-1]) > .03`. The Round 41 requirement is an outer-neighbor side-slope bracket, with endpoint and all ordinary checks still passing.

In PCM16 full-scale units, the declared targets are 32 counts / 32768 = `0.0009765625` (not greater than `.001`) and 33 / 32768 = `0.001007080078125` (greater than `.001`). The threshold is 32.768 counts; neither target tests equality at `.001`. This arithmetic predicts comparator polarity only if the decoded outer-neighbor differences are actually those counts; it is not a generated fixture or runner result.

## Distinction from R21 and R40

- **R21 internal join:** `section_contrast()` samples around the midpoint of a 4-second section-bearing WAV, with its slope comparison based on indices 95998–96001: `abs((samples[96001]-samples[96000]) - (samples[95999]-samples[95998]))`. It is gated separately as `sections: internal join side slope mismatch > .001 full scale per sample`. R19’s scout documented a specific baseline window `[-26,-13,0,43]` PCM counts (30-count mismatch); changing the last value to 45/46 yields 32/33 counts. R21 adds section controls on this *internal* predicate, not the outer samples `[-2:]`/`[:2]`. The two predicates share the numeric bound but differ in location, measurement record, and failure path. R21 verifier’s 983/984 **gap** pair is likewise an internal adjacent-sample-gap bracket, not an outer slope test.
- **R40 endpoint:** `measure()` computes `abs(samples[0]-samples[-1])` and compares strictly to `.03`; R40’s verified 983/984 counts were endpoint deltas 0.029998779296875 / 0.030029296875. R40 retained its separate outer slope metric, which was 0 for those fixtures. Its endpoint bracket is not evidence for the R41 side-slope bracket.

## Existing R3 values (historical reports, not this run)

`r3-metric.md` reports SoX-decoded clean outer slopes for the three original loops: ambience start/end increments `0.00067138671875` / `0.000640869140625`, mismatch `0.000030517578125`; ambience_alt `0.00189208984375` / `0.00189208984375`, mismatch `0`; stem `0.011383056640625` / `0.0113525390625`, mismatch `0.000030517578125` FS/sample. These are normal-fixture reference values, not evidence about the new 2-second scratch pair. The R3 constructed `slope_probe.wav` had equal endpoints and decoded outer mismatch `0.469970703125`, an isolated slope failure in the R3 adjudicator replay; it is a far-above control, not adjacent-count evidence.

R19’s internal window arithmetic explicitly gives 32/32768 and 33/32768. It must not be reported as measured R41 outer side-slope output. A qualifying R41 result needs fresh SoX-decoded outer values plus independent runner receipts showing 32 mode exit 0/no failures and 33 mode exit 1 with the sole outer slope-mismatch failure, while endpoint, 5–200 Hz centroid, level, duration, format, and other ordinary checks pass. Report failed numeric fits separately from command/helper/decoder setup errors.

## Scope limits

This mapping concerns numerical behavior of the local decoded-PCM fixture check only. The integer pair does not test exact `.001`, audible smoothness, click/seam perception, sound quality, production readiness, rights, engine, publish, or promotion.
