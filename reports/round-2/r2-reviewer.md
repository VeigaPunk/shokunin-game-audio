# Round 2 reviewer: before-state, test gaps, honest claim

## Scope and evidence

I read the round-2 declaration and wave spec in `.shokunin/audio/LOG.md`, plus the current `corpus/fixtures/build_artifacts.py` and `corpus/fixtures/measure_audio.py`. I did not run commands, synthesize audio, or edit shared fixtures, measurement code, scorecard, or log.

## Before-state

The log identifies before commit `31d8e9e`: five original mono PCM16, 48 kHz fixtures, exactly one each for UI, impact, movement, ambience, plus the stem. The current builder and measurement entrypoint agree with this: the builder writes those five names, and `SPECS` contains exactly those five. Thus the stated target (four added SFX variants, unchanged stem) is a clear coverage expansion, provided no existing artifact is replaced and all five baseline entries remain in the measured result.

## Reviewer assessment

The claim is falsifiable and appropriately narrow: distinctness is an explicit numeric criterion; existing format, level, duration, and applicable seam checks remain; coverage is credited only after independent replay. The scope explicitly excludes subjective sound quality and production readiness. The guard-axis language is useful: source generation and the original measurement battery must persist, while local fixture bounds and ebur128's gated floor must not be presented as mastering standards or valid short-SFX loudness readings.

The current instrumentation does **not** operationalize the claim yet. The fixed five-name `SPECS` mapping omits variants, so integration must make all nine artifacts measurable without dropping any baseline. The ordinary per-file checks alone also do not establish the new cross-file distinctness condition. The verifier should calculate each variant's duration and centroid from the decoded raw artifact, compare it with its category baseline, and record which branch of the OR criterion passed. For centroid, state the relative-difference calculation explicitly (absolute difference divided by baseline centroid, at least 0.10). For duration, record both values and the resolution/strict inequality used; the claim does not specify a minimum duration delta, so do not silently claim a stronger threshold.

## Test gaps / falsification checks

- Require a reproducible source-generation path for each new artifact and demonstrate repeatability (e.g. regenerate and compare hashes); merely finding WAVs in `live/round-2` is not evidence of deterministic generation.
- Replay all nine raw artifacts independently. Confirm exactly the four named additions, unchanged stem and baselines, expected 48 kHz mono PCM16 format, and no missing or extra files. Keep separate raw-artifact evidence from generator output.
- Check each variant against its own category's existing bounds and all applicable existing tests. In particular, ambience must satisfy the existing endpoint delta threshold; a passing endpoint proxy is not a general proof of seamless looping.
- Check the distinctness criterion against the matching baseline, not against another variant or rounded presentation values. Record measurements at sufficient precision and identify duration-versus-centroid pass for every variant.
- Ensure a negative/invalid control is rejected (for example, a duplicate of the baseline should fail distinctness, and a broken ambience endpoint should fail the seam proxy). Do not count unrun checks as passes.
- Preserve the calibration caveat: centroid is a whole-waveform magnitude-spectrum summary, not a timbre or perceptual-similarity test; peak/RMS bounds are local fixture checks; LUFS at/below the ebur128 gated floor is not a measured useful level.

## Verdict

The coverage move is well-posed but remains **unproven until integration and non-author replay**. Passing the proposed checks can support the bounded statement “four additional deterministic fixtures passed this local battery and met the declared measured-distinctness rule.” It cannot support perceived quality, general loop continuity, production suitability, or mastering claims.
