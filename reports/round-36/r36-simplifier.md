# Round 36 simplifier review

## Recommendation
Keep the move to one deterministic `ambience_third.wav` fixture and two explicit numeric pair records. No generic family framework, configurable thresholds, shared comparison helper, or new CLI mode is needed for this single case.

## Minimal source-change concept (proposal only)
- In `corpus/fixtures/build_artifacts.py`, add one fixed, deterministic original 2-second waveform and save it as `ambience_third`; place it with the existing ambience builders. Preserve the existing 48 kHz mono PCM16 save path. Ensure the source waveform itself loops at the boundary; do not copy or relabel either existing fixture.
- In `corpus/fixtures/measure_audio.py`, add only `"ambience_third": (2.0, 5, 200, True)` to `SPECS`, then a narrowly named `ambience_family_comparisons` block for `ambience` and `ambience_alt`. Keep the generic `_alt` loop, all existing thresholds, and other family blocks unchanged.
- Report duration delta and centroid-relative delta for each pair. Here both baseline and candidate are 2.0 s, so the duration delta target is exactly zero; under the existing `.020 s OR .10` comparison, duration cannot pass and the centroid arm alone must pass for each pair. Preserve that simple rule, and make failures explicit if either centroid delta is below `.10` (or candidate duration is not the declared 2.0 s). No generic AND/OR machinery is warranted.
- Keep the existing per-fixture endpoint and slope seam checks. They are numeric boundary proxies, not evidence that a loop sounds seamless.

## Scope and limitations
This is a proposal only. I generated/measured no candidate, verified no hashes, and edited no source, canonical artifact, LOG, SCORECARD, or other report. A candidate remains scratch until parent integration and verification. Centroid and seam measurements are numeric proxies only; no audition, perceived distinction/seamlessness, quality, production, rights, engine, publishing, or promotion claim is made.

## Commands and exits
No shell commands were run; there are no shell exit codes. I inspected the declared round-36 LOG and existing source using Python REPL file reads only.
