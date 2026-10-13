# Round 33 simplifier

## Recommendation
Keep the move to one new canonical `ui_third.wav` and exactly two explicit UI-family contrasts; do not introduce a generic variant/comparison framework or refactor existing fixture handling. Add only the `.20 s` source-generated UI spec and its builder entry, plus records comparing `ui_third` against `ui` and against `ui_alt`. Leave the existing `_alt` comparison path, predicates, thresholds, and all unrelated fixture behavior unchanged.

The declared OR rule makes the duration fit straightforward: nominal `.20 s` differs from `.12 s` by `.08 s` and from `.16 s` by `.04 s`, both greater than `.020 s`. Generate at 48 kHz, mono PCM16 and check the actual ffprobe duration and both existing per-file checks (format/level/centroid) before recording either contrast. Do not claim a centroid fit is needed to satisfy these two comparisons; duration is sufficient if measured values confirm it. If any per-file check or measured comparison fails, report the failure and do not admit the fixture.

## Interpretation / guardrails
This adds one measured duration point to the UI fixture family, not a generalized coverage system. Two duration-based OR passes are weak evidence of additional *duration coverage*, not evidence of spectral or perceptual distinctness; note that limitation plainly. Preserve the existing 13 canonical WAV hashes. Do not audition or make quality, production-readiness, rights, engine, publishing, or promotion claims. Do not change any other canonical bytes or existing variant count.

## Commands and failures
No project shell commands were run. There are no command exit codes, fit attempts, or setup failures to report. Treat any future failed invocation/setup separately from a valid measured-fit failure; do not present setup failure as a fixture gate result.
