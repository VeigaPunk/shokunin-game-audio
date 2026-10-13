# Round 31 scribe — expected versus measured

## Scope and evidence status

This report records the Round 31 declared joint-below-threshold probe. I read the declared Round 31 LOG entry and the other available round-31 role reports; at this point no round-31 executor/alternate fit output or runner receipt was available to me. I ran no shell commands, tests, or fits. Thus there are no shell command exit codes or observed fit/setup failures from my work. I make no claim that the proposed probe has been measured or integrated.

## Expected vs measured

| Quantity / check | Declared expectation | Measurement available to this scribe |
|---|---|---|
| Base | 48 kHz mono PCM16, 5760 frames, 0.120000 s; canonical UI spec | Not independently measured here |
| Variant | 48 kHz mono PCM16, 6719 frames; scratch expected duration `6719/48000` = 0.1399791667… s | LOG reports ffprobe `.139979` s; no independent receipt inspected |
| Duration delta | Nonzero and strictly `< .020` s; LOG target `0.019978999999999997` s | LOG-declared measured target only; no independent observation here |
| Centroid relative delta | Nonzero and strictly `< .10`, using existing baseline-denominator absolute relative difference | No coefficient/FFT fit result or measured centroid delta available |
| Per-file checks | Both ordinary checks pass using base `SPECS["ui"]` and a separate scratch variant duration of `6719/48000` | No individual measurement results available |
| Existing `_alt` distinctness | Both branches false (`duration < .020`, `centroid relative < .10`), so pair is rejected for distinctness only | No integrated runner result/receipt available |
| Canonical UI duration status | Variant is longer than .120 s and is not a canonical-duration UI fixture | No canonical-duration conformance claim is made |

The duration arithmetic from frame counts is `6719/48000 - 5760/48000 = 959/48000 = 0.0199791666…` s. This arithmetic is not a substitute for a runner/ffprobe measurement. In particular, no centroid value should be inferred from a phase multiplier; the measured fit must be reported. Failed coefficient fits and setup errors should be listed separately from any successful fit and must not be mistaken for runner evidence.

## Interpretation limits

If later measured evidence confirms the target, it supports only the observed joint nonzero-below-threshold comparator case with both per-file ordinary checks passing. It does not establish a universal OR law, exact cutoff equality, calibration of the ordinary duration tolerance, or perceptual similarity. No claims are made about engine behavior, rights, publishing, promotion, or audio quality.
