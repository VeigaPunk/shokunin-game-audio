# Round 35 simplifier review

## Recommendation
Keep this to one deterministic `movement_third.wav` fixture and two explicit numeric comparisons. Do not add a generic family/variant abstraction, configurable threshold system, fixture registry, or shared comparison helper for this single case. The declared scope is small enough that one narrowly named block is easier to audit than framework machinery.

## Minimal source-change concept (proposal only)
- In `corpus/fixtures/build_artifacts.py`, add one deterministic, source-generated `movement_third` waveform in the canonical builder near the existing `movement` fixtures. Keep its generation parameters fixed and documented by the code; do not reuse/copy either existing waveform as a renamed fixture. Avoid introducing a new CLI switch for this always-built canonical fixture.
- In `corpus/fixtures/measure_audio.py`, add exactly `"movement_third": (.30, 100, 16000, False)` to `SPECS` and a separate, explicitly named `movement_family_comparisons` block for `movement` and `movement_alt`. Keep the existing generic `_alt` loop, all its thresholds, and other family comparison blocks unchanged.
- The declared fixture-selection target is measured duration .30 s (thus .06 s from each .24/.36 s baseline) and centroid-relative delta >= .10 against **each** baseline. Important implementation guard: the existing comparison pass rule is duration OR centroid. If the new block merely copies that rule, the .06 s deltas will pass even when either centroid criterion misses. Represent/report the duration and centroid arms separately and make admission/fixture `passed` require the declared centroid criterion for both comparisons (and the duration target), rather than silently treating the existing OR as satisfying the extra selection requirement. The numbers remain lossy proxies, not evidence of perceived novelty.

## Guard / scope
This is a proposal only: no source, canonical artifact, LOG, SCORECARD, or other report was edited; no candidate was generated or measured, and no source commands were run. I did not verify the candidate fit or any hashes. Parent integration and verification are required before anything is canonical/admitted. No claim about audition, sound quality, production, rights, engine integration, publishing, or promotion.

## Commands and exits
No shell commands were run, so there are no shell exit codes to report. Source/log inspection used Python REPL file reads only.
