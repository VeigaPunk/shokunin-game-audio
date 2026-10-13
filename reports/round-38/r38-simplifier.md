# R38 simplifier — one positive scratch control

## Scope and command record

I read the Round 38 declaration in `.shokunin/audio/LOG.md`, the Round 37 negative-control wiring, and the executor’s scratch generator. I made no source, fixture, LOG, scorecard, canonical asset, or other report edits. I did not run a shell experiment, build, measurement helper, runner, or numerical fit.

Shell command and exit: `git status --short` — exit 0. It showed pre-existing `LOG.md` modification and untracked Round 38 scratch/report paths; I did not modify those. No failed numeric fit occurred. No setup failure occurred because no experiment was attempted.

## Minimal recommendation

Keep this to one opt-in positive control in the declared `--probe-ambience-centroid-above` mode and its own `live/round-38/` scratch pair. Reuse the existing measurement and `_alt` distinctness path, same-name baseline matching, and local `(2.0, 5, 200, True)` specs. Do not add a generic abstraction, another source of threshold truth, family rule, or canonical asset. Leave `.020 s OR .10` unchanged.

The pair must be source-generated, equal-duration 2.0 s / 48 kHz mono PCM16 loops with distinct WAV hashes. Choose the variant only after the project measurement helper reports centroid-relative delta strictly `> 0.10` and `< 0.13`; do not infer it from nominal frequencies or generator parameters. The positive runner result should show `duration_delta_s == 0.0`, centroid arm true, no ordinary or loop failures, `_alt` passed, and exit 0. If an attempt misses the band, record it as an unsuccessful numeric fit; distinguish that from a setup failure (for example, a command/helper that could not run). Do not adjust the threshold to rescue a miss.

No numeric fit or positive runner outcome is established by this report. This is a proposed single local positive polarity control alongside Round 37’s local negative, not exact-boundary or universal calibration, an audition, perceptual/spectral similarity, quality, production, rights, engine, publishing, or promotion evidence.
