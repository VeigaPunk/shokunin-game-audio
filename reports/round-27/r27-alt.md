# r27-alt — independent adjacent-count and float check

## Scope
I read the round-27 claim in `.shokunin/audio/LOG.md` and independently generated candidate PCM16 WAVs in `corpus/live/round-27/alt/`. No shared source, LOG, SCORECARD, canonical artifacts, or other reports were changed. No perceptual, rights, engine, publish, or promotion claim is made.

## Method and outcomes
At 48 kHz mono PCM16, I compared a 5,760-frame (0.120 s) reference to adjacent 6,719- and 6,720-frame files. First candidate repeated the source-generated analytic UI chirp/envelope equation (`.38*sin(2π*(700t+800t²))*exp(-30t)`); a second independent fit used a 700 Hz sine with exponential envelope (`.30*sin(2π*700t)*exp(-20t)`). Both are synthetic, analytically specified signals. `ffprobe` reports duration to six decimals, so the tested duration values are **0.139979**, **0.140000**, and **0.120000** seconds—not exact rational durations retained by the comparator.

| waveform | file | frames | ffprobe duration | `abs(variant-base)` | relative centroid delta | duration `>=.020` | centroid `>=.10` | OR result |
|---|---|---:|---:|---:|---:|---|---|---|
| chirp | base | 5760 | .120000 | — | — | — | — | — |
| chirp | 6719 | 6719 | .139979 | .019978999999999997 | .026103720992748162 | false | false | fail |
| chirp | 6720 | 6720 | .140000 | .020000000000000018 | .028427598871782873 | true | false | pass |
| tone/envelope | base | 5760 | .120000 | — | — | — | — | — |
| tone/envelope | 6719 | 6719 | .139979 | .019978999999999997 | .01250942368630596 | false | false | fail |
| tone/envelope | 6720 | 6720 | .140000 | .020000000000000018 | .002547362932441558 | true | false | pass |

Each generated WAV was also tested with the repository's `measure()` against its own exact duration spec and existing UI centroid band `[250,4000]` (same format/level checks). All six passed with no failures. Chosen files/metrics: chirp centroid base 966.8966593379727 Hz, 6719 941.657058713794 Hz, 6720 939.4101089558459 Hz; tone centroid base 971.86422306315 Hz, 6719 959.7067617312905 Hz, 6720 974.3399139603472 Hz. The second fit is less confounded by centroid movement (relative changes ≈1.25% and 0.255%) and both retain centroid branch false. It does **not** establish an exact decimal threshold test: comparator inputs are the six-decimal ffprobe float values, and subtraction yields .020000000000000018 due to binary float arithmetic. Thus this exercises an observed adjacent-count transition with the current float comparison, not mathematical equality independent of representation.

No production runner mode was changed or invoked; this is direct candidate/measure evidence, not independent integration/replay.

## Exact shell invocations / exits
- `python3 .shokuni/audio/corpus/live/round-27/alt/fit.py` — exit **0**; queried ffprobe metadata and SoX-decoded samples, computed FFT centroids and OR outcomes for chirp files.
- `python3 .shokuni/audio/corpus/live/round-27/alt/tone_fit.py` — exit **0**; same checks for the alternative waveform fit.
- `python3 .shokuni/audio/corpus/live/round-27/alt/measure_fit.py` — first attempt exit **1**, setup/path error (`ValueError` from relative_to because the path was relative); it emitted no measurements. Corrected script to resolve scratch paths:
- `python3 .shokuni/audio/corpus/live/round-27/alt/measure_fit.py` — exit **0**; all six direct `measure()` results had empty failures.

## Assessment / limits
The intended polarity is reproducible for both analytical fits: 6719 frames fall just below the comparator's duration bound and fail the existing OR check while centroid remains under its bound; 6720 frames cross the duration comparison and pass it while centroid remains under its bound. This is a candidate for the requested calibration probe, not evidence that any integrated runner implemented it. The reported `0.020000000000000018` is binary floating-point subtraction, not exact real-number equality. No threshold adjustment or failed fit was concealed. The initial path error was a setup failure; the run was corrected without changing shared code. No auditory similarity, general distinctness, or broader numeric-calibration conclusion follows.
