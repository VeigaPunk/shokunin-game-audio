# R38 scout — Round 37 negative wiring and positive complement

## Scope and command record

I read the Round 38 declaration in `.shokunin/audio/LOG.md`, the Round 37 reports/receipt, and inspected the builder and runner wiring. This is a source/wiring survey only: I did not synthesize a wave, run the measurement helper/runner, or perform a numeric fit. The Round 37 measured numbers below come from the recorded independent replay, not a new fit here.

Shell reconnaissance commands and exits:
- `pwd && find .shokunin/audio -maxdepth 4 -type f | sort | tail -100` — exit 0.
- `find .shokunin/audio -maxdepth 3 -type f | sort | grep -E 'LOG|round-38'` — exit 0.
- `git status --short && grep -R -n --exclude-dir=.git -E 'probe-ambience-centroid|ambience_probe' .shokunin/audio corpus 2>/dev/null | head -100` — exit 0. It showed `.shokunin/audio/LOG.md` already modified; I did not edit it.

A Python source-inspection snippet ended with an `IndexError` because I requested lines beyond `measure_audio.py`'s length; that was inspection setup only, not a numeric fit or runner result. No experiment command was run, so there is no experiment exit code to report.

## Round 37 negative and current wiring

The Round 37 declaration records the equal-duration 2.0 s / 48 kHz mono PCM16 scratch pair: baseline 60 Hz and variant 64 Hz. Independent runner replay measured centroid values `67.37182625964924 Hz` and `71.80863982343814 Hz`, giving baseline-relative delta `0.06585562259644766`; duration delta was `0.0 s`. Both individual ordinary/loop failure lists were empty. Existing generic `_alt` distinctness failed only the variant with `distinctness: duration < .020 s and centroid delta < 10%`, and the negative-mode runner returned expected exit 1. These are one local numeric negative control, not a general cutoff finding.

Current source wiring is narrowly opt-in. `build_artifacts.py` has `build_ambience_centroid_below_probe()` writing `ambience_probe` and `_alt` into `live/round-37`, currently with 60/64 Hz loops; its CLI branch calls the canonical build then this scratch builder. `measure_audio.py` forwards the below flag to the builder, locally measures the two names at `(2.0, 5, 200, True)` using explicit scratch paths, and its existing generic `_alt` loop compares the variant against the same-name-stripped baseline. The unmodified predicate is `duration_delta >= .020 or centroid_relative_delta >= .10`; false appends the sole distinctness failure. This route avoids adding a family comparison or changing the generic threshold. Canonical measurements are still run as usual.

## Recommendation for the Round 38 positive complement

Add only the declared separate opt-in `--probe-ambience-centroid-above` branch and a distinct `live/round-38/` pair; leave the Round 37 negative intact. Reuse the current source-generated 2.0 s analytical-loop approach, 48 kHz mono PCM16 output, local `(2.0, 5, 200, True)` specs, explicit scratch paths, and generic `_alt` comparison. Keep equal sample counts and make the variant source different. Select/tune its wave only from **project-measured** results so the measured baseline-relative centroid delta is strictly `> 0.10` and `< 0.13` (the declared preferred narrow band); do not treat source frequency/coefficient as a substitute for measurement. Require exact `duration_delta_s == 0.0`, nonidentical file hashes, clean ordinary/loop checks, centroid in the declared measurement band, generic `_alt` pass with centroid arm true, and a normal positive-mode runner exit 0. If tuning fails, report fit attempts as unsuccessful numeric fits separately from setup failures; do not loosen the band or change the gate.

The complement tests a local positive polarity beside the Round 37 local negative. It does not establish an exact boundary, universal calibration, perceptual/spectral similarity, audition or quality, production suitability, rights, engine behavior, publishing, or promotion.
