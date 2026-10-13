# Round 34 scribe — impact-family decision table

## Before / proposed-after comparison

The declared coverage move proposes a third source-generated impact fixture at nominal `.40 s`, with explicit comparisons against the existing `.32 s` `impact.wav` and `impact_alt.wav`. Existing distinctness is the OR rule: duration delta `>= .020 s` **or** relative centroid delta `>= .10`. “Pass” below means only this numeric pair predicate; individual measurements are scratch-proxy evidence, not admission or a quality judgment.

| State / pair (baseline vs candidate) | Expected duration delta | Measured duration delta | Expected centroid-relative delta | Measured centroid-relative delta | OR result |
|---|---:|---:|---:|---:|---|
| Before: `impact` (.32 s) vs `impact_alt` (.32 s) | 0 s | 0 s | Not specified | 21.907… (`abs(10843.127202979935 - 473.79153568100764) / 473.79153568100764`) | Duration false; centroid true; pass |
| Proposed: `impact` (.32 s) vs scratch candidate (.40 s) | .08 s | 0.08000000000000002 s | Preferably >= .10 per declaration | 0.36935690461299725 | Duration true; centroid true; pass |
| Proposed: `impact_alt` (.32 s) vs scratch candidate (.40 s) | .08 s | 0.08000000000000002 s | Preferably >= .10 per declaration | 13.432810187572105 | Duration true; centroid true; pass |

The proposed scratch candidate measured duration `.4 s`, 48 kHz mono PCM16, peak `0.45611572265625`, RMS `-20.84958464133168 dBFS`, centroid `6838.143302962279 Hz`, and no ordinary individual-measurement failures. Existing baseline measurements came from the prior normal receipt; its impact centroids are `10843.127202979935 Hz` and `473.79153568100764 Hz`. Relative centroid calculations use the baseline centroid as denominator. The third candidate exists only in `corpus/live/round-34/alt/`; no canonical fixture or comparison receipt has been integrated here.

## Fit, setup, and evidence boundary

Exact shell command run:

```sh
cd /home/vgpnk/Projects/prymeagnt/audio && python3 .shokunin/audio/corpus/live/round-34/alt/fit.py
```

Shell exit code: **0**. The project's measurement function reported the scratch candidate values above and `failures: []`; both proposed pairs satisfy the numeric OR predicate. No coefficient or measurement-fit failure occurred. A subsequent Python orchestration attempt to `await` the already-returned `BashResult` raised `TypeError: object BashResult can't be used in 'await' expression`; this was a harness-result handling/setup mistake, not a shell command or fit failure. The shell process itself had completed successfully with exit 0.

This report documents only a proposed numeric scratch fit. It does not establish canonical builder/spec changes, 15-file inventory, preservation of the existing fourteen hashes/metrics, historical replay, independent verification, or an admission verdict. Candidate is not canonical until parent integration and verification. No audition, sound-quality, production-readiness, rights, engine, publishing, or promotion claim.

Only this report was written by me. No shared source, LOG, SCORECARD, canonical artifact, or other report was edited; no commits or pushes.
