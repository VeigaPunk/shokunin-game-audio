# Round 39 reviewer — minimal opt-in builder/runner design

## Recommendation

Add two opt-in runner flags, `--probe-ambience-orientation-forward` and `--probe-ambience-orientation-reverse`. Both modes must build and measure the same two source-generated, deterministic 2.0-second / 48 kHz mono PCM16 ambience WAVs in one scratch directory, e.g. `corpus/live/round-39/reviewer/`. Use stable names `ambience_orientation` and `ambience_orientation_alt`; each mode only swaps which measured WAV is the generic comparison baseline versus `_alt`. Feed both measured entries to the existing unchanged generic `_alt` comparison. Keep canonical `SPECS`, the 17 canonical assets, generic comparison formula and `.020 s OR .10` constants untouched; do not add a family comparison or edit canonical assets.

The required actual-helper relation for measured centroids `A < B` is strict:

- Forward: baseline `A`, alternate `B`; `abs(B-A)/A > .10`, so generic distinctness passes (expected runner exit 0).
- Reverse: baseline `B`, alternate `A`; `abs(A-B)/B < .10`, so the alternate has the sole distinctness failure (expected runner exit 1).

Both modes must reference the same exact WAV bytes (cross-mode hashes equal), with distinct hashes between A and B. Require both ordinary format, duration, level, centroid-band and loop-seam checks to pass, and measured duration delta exactly `0.0`. A possible initial fit to test is clean integer-bin single tones near 100 Hz and 111 Hz at modest equal amplitude. This is only a candidate: accept it only if the project measurement helper reports the strict inequalities with margin and all checks pass. Do not substitute nominal frequencies or coefficient ratios for measured centroid floats. Record the actual centroids, ratios, duration delta, hashes, checks and each mode’s receipt/exit before claiming the split is demonstrated.

## Fits and setup accounting

This review performed no waveform fit, builder/runner execution, or setup attempt. Therefore there are no measured strict-split results, failed numeric fits, or setup errors to report; the 100/111 Hz suggestion is untested, not evidence. In subsequent work, keep valid numeric candidates that miss either strict inequality separate from setup/tool failures (generation, decode, wrong format, ordinary/seam failure, missing receipt, etc.); neither category is a runner threshold outcome. Do not claim the expected exits above as observed results.

This is a local numeric baseline-denominator orientation check only. It supports no claim about perception, spectral distinctness, audible seamlessness, quality, production, rights, engine, publishing, or promotion.

## Commands and scope

No shell commands were run; no exits or receipts exist. I inspected the Round 39 LOG declaration, the existing fixture runner/builder wiring, and Round 30 reviewer precedent. This review makes no project source, LOG, scorecard, canonical asset, or other report edits; the only intended output is this report.
