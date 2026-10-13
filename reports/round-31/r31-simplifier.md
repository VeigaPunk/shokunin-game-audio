# Round 31 simplifier report

## Scope

I read the declared Round 31 entry in `.shokunin/audio/LOG.md` and inspected the existing fixture builder and measurement runner. No source, LOG, SCORECARD, canonical artifact, or other report was changed. No shell commands were run, so there are no command exit statuses or fit results to report. The declared Round 31 probe is not present in this checkout; I cannot report an empirical fit or runner outcome.

## Simplification recommendation

Keep this as one narrowly named, opt-in probe mode using the existing builder and `_alt` comparison path. Do not add a generic search/fitting framework, refactor the OR comparison, change thresholds or canonical specs, or create a canonical WAV. A single measured coefficient selected by a bounded, manual preflight is enough; report unsuccessful candidate fits separately rather than hiding them or inferring measured centroid from the coefficient.

The probe's base is the ordinary 48 kHz mono PCM16 UI fixture at 5760 frames (`.120000 s`). Its 6719-frame variant is `.139979 s` by frame count; its intended per-file scratch duration expectation must be `6719/48000`, not canonical UI `.120 s`. The requested duration delta is nonzero and below `.020 s`. The intended centroid delta must also be nonzero and below `.10` under the existing comparison calculation. Both files should independently pass their applicable ordinary format/level/spectrum checks, then the existing OR should reject the pair as not distinct with both measured branches false. These are target conditions from the round declaration, not results I verified.

Keep the report limited to this jointly-below-threshold comparator control. Do not describe it as proof of a universal OR law or exact cutoff equality, and make no perceptual, rights, engine, publishing, promotion, or canonical UI `.12 s` claim for the longer variant.
