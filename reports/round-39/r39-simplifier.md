# R39 simplifier — two-mode orientation control

## Scope and command record

I read the Round 39 declaration in `.shokunin/audio/LOG.md` and prior Round 38/30 reports. I made no source, LOG, scorecard, canonical asset, or other report edits; no commits or pushes. I did not run a generator, measurement helper, numerical fit, or project runner. Thus there is no new ambience strict-split measurement, failed numeric fit, or experiment setup failure from this report.

Inspection shell commands and exits:

- `pwd; find .shokunin/audio -maxdepth 4 -type f | sort | sed -n '1,140p'; git status --short` — exit 0.
- `find .shokunin/audio -maxdepth 3 -type f | grep -E 'py$|round-38|round-39' | sort | head -100; grep -R "_alt\|centroid\|strict" -n .shokunin/audio/*.py .shokunin/audio/corpus/fixtures 2>/dev/null` — exit 0.
- `find .shokunin/audio/reports/round-39 .shokunin/audio/corpus/live/round-39 -maxdepth 4 -type f 2>/dev/null | sort; git status --short --untracked-files=all` — exit 0.
- `find . -maxdepth 3 -type f | grep -E '(run|validate|score|SCORE)' | head -80; sed -n '1,180p' .shokunin/audio/reports/round-38/r38-executor.md` — exit 0.

The pre-existing `LOG.md` modification was present in initial `git status --short`; I did not touch it.

## Minimal recommendation

Implement only two opt-in orientation modes, each feeding the same two scratch WAV byte sequences through the existing local ambience measurement and generic `_alt` distinctness comparison. Forward assigns the lower-centroid WAV as baseline and the higher-centroid WAV as `_alt`; reverse swaps those roles. Keep this logic specific to the probe: no generic refactor, new comparator/threshold, canonical asset, or family rule. Scratch files stay under the declared round-39 executor area. Require two original deterministic 2.0s, 48kHz mono PCM16 loops, distinct hashes, ordinary and seam checks clear, and exactly zero measured duration delta in both orientations.

Choose a pair by measured helper floats, not nominal frequencies. For A < B, the strict split is `((B-A)/A) > .10` and `((B-A)/B) < .10`; equivalently the forward delta must fall strictly in `(.10, 1/9)` (about `(.10, .111111...)`). The forward mode must pass exit 0; reverse must fail only generic distinctness, exit 1. Check both JSON receipts for equal duration and the expected centroid deltas; do not turn the intentional reverse distinctness failure into a setup failure. Do not change `.020 s OR .10` or any other threshold.

The R30 UI result is precedent for the arithmetic, not an ambience result: its measured forward/reverse deltas were `0.09901901500217196` and `0.10990133715464667`, respectively. Do not reuse those UI files as the declared ambience fixture. R38's measured ambience pair (36.6164076785 / 41.2475246227 Hz) is also not a fit for this strict orientation split: forward delta `0.1264765508` passes, but reverse delta is about `0.11228`, also above .10, so it would pass in both directions. This is a numeric candidate mismatch, not setup failure, and is prior-report evidence only, not a new command or measurement.

No new fit or runner outcome is established here. Numerical denominator-orientation control only; no audition, perception/quality, production, rights, engine, publishing, or promotion claim.
