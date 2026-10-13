# Round 30 simplifier review

## Recommendation

Keep this as two narrowly scoped opt-in probes that feed the existing `_alt` distinctness comparator. Do not add symmetric normalization, a new comparison helper/framework, or refactor the measurement path. The proposed move is calibration of the existing baseline-denominator rule, not correction of it.

The current comparator is already explicit: `abs(variant_centroid - base_centroid) / base_centroid`, followed by the existing `duration_delta >= .020 or centroid_relative_delta >= .10` test. For the declared measured pair, forwarding baseline `966.8966593379727 Hz` and variant `871.155504521436 Hz` gives relative delta `0.09901901500217196` and fails distinctness; swapping the same pair gives denominator `871.155504521436 Hz`, relative delta `0.10990133715464667`, and passes. This is a numeric orientation effect of the baseline denominator. It does not imply symmetric similarity is expected or preferred.

## Minimal wiring constraints

- Preserve the original sample bytes in both roles: forward `(base, alt)` and reverse `(alt, base)`. Prefer constructing or copying one pair once, then assigning the same paths/bytes to opposite measurement names; avoid duplicate synthesis logic.
- Route both probe modes through the current measurement and `_alt` comparison path. Keep existing `SPECS["ui"]`, thresholds, absolute difference, denominator, and ordinary checks unchanged.
- Keep probe labels and receipt names explicit. A small pair of CLI flags and a small role-selection branch is sufficient; no generic pair registry, normalization abstraction, comparator refactor, or new threshold mode is warranted.
- Validate byte identity across swapped roles (forward base SHA equals reverse alt SHA, and forward alt SHA equals reverse base SHA), then inspect both individual ordinary-check results and the distinctness result. If the measured values fail to straddle `.10`, treat the move as falsified; do not tune the checker to force a pass.

## Evidence boundaries

The declared pre-integration record cites round-29 measured centroids and zero duration delta. It predicts forward rejection and reverse acceptance under the existing formula. No round-30 implementation, shell command, or independent replay was run for this review; therefore there are no round-30 command exit codes or receipts to report. Failed fits/setup attempts are not evidence and must remain separately identified if encountered by other lanes.

This proposal establishes only baseline-denominator orientation for these numeric measurements. It does not establish perceptual similarity, audio quality, symmetry as a normative goal, exact-threshold behavior, or any rights, engine, publishing, or promotion conclusion.
