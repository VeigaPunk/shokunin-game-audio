# r28-scribe — proposed vs measured decision table

## Scope and status

The declared move is a two-point calibration check of the existing centroid-relative OR arm: same 5760-frame (0.12 s), 48 kHz mono PCM16 UI-shaped samples; duration delta must be zero; one analytic parameter is changed. Existing predicate is `duration_delta >= .020 or centroid_relative_delta >= .10`. The table below compares expected outcomes with scratch measurements; it does **not** claim the integrated runner exercised these cases. No round-28 runner modes or receipts were present when this report was written.

## Decision table

| Candidate / basis | Proposed decision | Measured duration / centroid relative delta | Ordinary UI gate | Classification |
|---|---|---|---|---|
| Baseline, alt sweep coefficient scale 1.00 | Reference; compare to itself | 0.120000 s; 966.896659 Hz | pass | Reference only; not a distinctness test |
| Alt sweep scale 1.10 | At/above .10 should pass distinctness (duration arm false) | 0.120000 s; centroid 1067.982318 Hz; relative delta **0.1045464971**; duration delta 0 | pass: PCM16/48k/mono; peak .3758545; RMS −19.991648 dBFS; centroid in 250–4000 Hz | Measured input predicts pass under current formula; comparator outcome not observed in runner |
| Alt sweep scale 1.11 | Below .10 should fail distinctness (duration arm false) | 0.120000 s; centroid 1058.114433 Hz; relative delta **0.0943407686**; duration delta 0 | pass: PCM16/48k/mono; peak .3760681; RMS −19.991623 dBFS; centroid in 250–4000 Hz | Measured input predicts distinctness failure under current formula; comparator outcome not observed in runner |
| Executor chirp-coefficient candidates 720, 760, 784, 816, 840, 880 (baseline 800) | Seek values on opposite sides | Relative centroid deltas respectively **.0595504, .0277033, .0706130, .0576052, .0316723, .0481650**; duration .12 s each | all reported no ordinary-measure failures | Failed fit for this candidate sweep: no above-.10 side; do not count as a two-sided calibration pair |

The closest adjacent successful opposite-side pair in the alt sweep is scale 1.10 / 1.11: measured difference is about 1.02 percentage points from the threshold on either side. The code comparator is `>= .10`; these values are not exact equality tests. Distinctness formula is a numeric comparison of weighted FFT magnitude spectral-centroid proxies, not a judgment of sound difference.

## Commands and exits

Commands were run from project root using the project’s available Python/tool environment:

- `python3 .shokunin/audio/corpus/live/round-28/executor/sweep.py` — exit **0**. Printed seven measured chirp candidates; all ordinary UI checks reported `[]`; no candidate exceeded .10 relative centroid change.
- `python3 .shokunin/audio/corpus/live/round-28/alt/sweep.py` — exit **0**. Printed baseline and nine scales 1.08–1.16; scale 1.10 and 1.11 provide the opposite-side measurements above. These are scratch sweep results, not a runner receipt.
- `python3 -c 'import sys; from pathlib import Path; sys.path.insert(0, str(Path(".shokunin/audio/corpus/fixtures").resolve())); from measure_audio import measure,SPECS; p=Path(".shokunin/audio/corpus/live/round-28/alt").resolve(); [print(n, measure(n,SPECS["ui"],p/(n+".wav"))) for n in ("baseline","scale_1.1","scale_1.11")]'` — exit **0**. Directly measured the baseline and selected pair with the project measurement function; all three `failures` lists were empty and values match the table.

## Failed setup / fit, kept separate

- An initial direct-measurement command used relative paths, and `measure()` raised `ValueError` because its report path was not relative to the corpus root; exit **1**. Correcting the path to `.resolve()` produced the successful command above. This was a reporting-path setup error, not an audio fit result.
- A second initial invocation selected nonexistent `scale_1.10.wav` (the sweep names files `scale_1.1.wav`); `ffprobe` returned exit **1**, propagated by `measure()`. Correct filename produced successful measurements. This is a filename setup error, not a failed media decode finding.
- The executor’s coefficient sweep did run successfully but did not find a passing-side candidate; that is the actual candidate-fit limitation, recorded separately in the table.

## Limits

Scratch measurements only. No integrated runner comparator outcome, independent replay, or adjudicator verdict is claimed. The proxy does not establish audibility or perception, rights clearance, engine behavior, publishing readiness, or promotion. No thresholds, canonical fixtures/specifications, source, LOG, SCORECARD, or other report were changed.
