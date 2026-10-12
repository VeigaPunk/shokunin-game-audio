# Round 11 scribe — decision table draft

## Declared claim and evidence boundary

LOG declares one **depth** move at the internal join of the original analytic `stem_layer`: compare the one-sample slope immediately before the join with the one-sample slope immediately after it. The proposed limit is `.001` full scale per sample, borrowed from the existing *outer* loop-slope bound as a fixture-local threshold. This is a discrete local PCM slope-mismatch proxy. It is not an acoustic/perceptual quality threshold.

For decoded samples `x` and the declared join at frame 96,000, the proposed quantity is

`abs((x[96001] - x[96000]) - (x[95999] - x[95998]))`.

Pass at `<= .001`; fail at `> .001`. This uses exactly one adjacent difference on either side; it does not measure curvature, a window, or continuity of derivatives in an analog signal. The proposed isolation condition is essential: an original scratch control should pass the `.03` internal adjacent-gap predicate and every generic, outer-edge, and section-contrast predicate, but fail only the new local slope-mismatch predicate.

## Decision table (draft; integration/replay pending)

| decision | measurement / rule | interpretation and required evidence |
|---|---|---|
| Input and generic validity | Existing decoded PCM format/duration, peak `< .95` FS, RMS `> .001` FS, and declared spectral-centroid band | Preserve existing checks. A candidate failing any of these is not an isolated slope control. |
| Outer loop seam | Existing endpoint difference `<= .03` FS and first-vs-last one-sample slope difference `<= .001` FS/sample | Keep distinct from the internal join. Existing outer-slope control must retain its prior behavior. |
| Section contrast | Existing 120 Hz section estimator; each half must be valid and section contrast `>= 6 dB` | Verify both halves and retain old behavior; this is not a join measure. |
| Existing internal join gap | `abs(x[96000]-x[95999]) <= .03` FS for `stem_layer` and its join probe | Retain round-10 predicate unchanged. The new control must pass this check. |
| **Proposed internal side-slope mismatch** | `abs((x[96001]-x[96000])-(x[95999]-x[95998]))`; pass `<= .001`, fail `> .001` FS/sample | Add one named internal metric and gate at the declared frame. This is the sole intended new predicate. |
| Isolated negative control | New control exceeds `.001` mismatch, while gap, sections, generic checks, and outer seam checks pass | Only then can the measurement support this narrow depth claim. If another check fails, label it failed-fit telemetry, not isolated evidence. |
| Regression preservation | Replay clean original, join probe and prior flat30/flat120/outer-slope/failing/invalid modes; compare eleven canonical hashes | Required non-author evidence before deciding whether depth improved and coverage/calibration stayed unchanged. This draft has no such replay. |

## Before → proposed after; history and caveats

| topic | before / historical context | proposed after / status |
|---|---|---|
| Internal join coverage | Round 10 added a decoded adjacent-sample gap check at frames 95,999→96,000 with strict failure above `.03` FS. The outer slope check compares the file's first and last edge slopes; it does not compare the slopes on the two sides of this internal join. | Add a single internal side-slope mismatch measurement/gate at the same fixed join. Retain the gap and all other rules. Pending parent integration and independent verification. |
| Clean original values | LOG records frames 95,998–96,001 as `[-.0003662109375, -.00018310546875, 0, .000946044921875]` FS. Thus left difference is `.00018310546875`, right difference `.000946044921875`, mismatch `.000762939453125` FS/sample, and the join gap is `.00018310546875` FS. | The recorded clean mismatch is below `.001`; this is historical declared fixture telemetry, not my independent replay. |
| Threshold | `.001` was already used for the outer loop-slope delta. | Reuse is a test-design choice, not threshold calibration. The record supplies no evidence of audibility or portability. |
| Probe and regression evidence | At draft time, no round-11 candidate or integrated receipt was examined here. Round-10 historical verification reports an isolated join-gap probe and preserved prior controls, but that does not verify this new metric. | `r11-slope` / `r11-alt` and later non-author replay must supply candidate recipe/hash and complete receipt; failed-fit alternatives remain telemetry only. Verify canonical hashes and old controls independently. |

The declared four samples give a specific reproducible discrete calculation, but no conclusion about click-free playback, perceived smoothness, audibility, engine/adaptive timing, production readiness, security, or behavior beyond this fixture follows. A pass is only a pass under the proposed sample-domain proxy. A threshold exceedance is only a measured mismatch. No borrowed audio or external reference is used or needed for this draft.

## Commands / provenance

No shell commands or audio CLI were run; therefore there are no shell command exits to report. I read the round-11 declaration in `.shokunin/audio/LOG.md`, the fixture measurement implementation, and the prior `r10-scribe.md` report in Python. The numerical clean-fixture values above are quoted from the round-11 LOG declaration, not recomputed. No source, LOG, SCORECARD, canonical artifact, or executor scratch was edited. This is a draft, not an integrated or independently verified result.
