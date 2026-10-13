# Round 30 scribe — denominator-orientation decision table

## Decision
The existing checker uses `abs(variant_centroid - baseline_centroid) / baseline_centroid`. For the declared two-waveform pair, the same absolute Hz difference is below the `.10` cutoff when the higher-centroid waveform is baseline, but above it when the lower-centroid waveform is baseline. This is a numerical baseline-denominator orientation effect only; it does not establish that normalization should be symmetric or that either orientation is perceptually preferable.

## Before/after orientation table
Declared pair: forward baseline `k=1.00` centroid `966.8966593379727 Hz`; forward variant `k=.95` centroid `871.155504521436 Hz`. Same bytes are intended to exchange baseline/variant roles in reverse. Duration delta is expected to remain zero; each file must pass the unchanged canonical UI ordinary checks.

| Orientation | Baseline → variant | Absolute centroid difference | Existing relative calculation | Expected distinctness decision |
|---|---|---:|---:|---|
| Before (forward) | 966.8966593379727 → 871.155504521436 Hz | 95.7411548165367 Hz | `95.7411548165367 / 966.8966593379727 = 0.09901901500217196` (< `.10`) | Reject on existing distinctness rule alone; ordinary checks pass |
| After (reversed roles) | 871.155504521436 → 966.8966593379727 Hz | 95.7411548165367 Hz | `95.7411548165367 / 871.155504521436 = 0.109901337` (> `.10`) | Pass distinctness; ordinary checks pass |

This is the declared fit and expected decision table, not a report of independently executed runner receipts. The source proposal requires verifying byte identity across swapped roles (forward baseline SHA = reverse variant SHA; forward variant SHA = reverse baseline SHA), measured centroids/durations, and both files' ordinary checks before treating the pair as evidence. Keep the existing `.020 OR .10` predicate, absolute difference, and baseline denominator unchanged.

## Failures and evidence exclusions
No shell command or runner was executed for this scribe task, so there are no command exit codes or observed runner failures to report. Any failed parameter fits or setup/command failures from other work are not evidence for the denominator decision and must remain excluded; only successful measured receipts after setup, with the specified byte swaps and ordinary checks, can support it.

## Scope limits
Numeric baseline-denominator orientation only. No claim of perceptual similarity, symmetric normalization as a norm, exact cutoff equality, general codec behavior, or audio quality. No rights, engine, publishing, or promotion conclusion.
