# R38 scribe — before/after numerical decision table

## Scope and status

This report summarizes the Round 38 declaration and settled wave-1 evidence available so far. It is a decision-table proposal, not an integrated runner result or admission verdict. I did not run shell commands or a waveform fit; no commands/exits from this scribe lane. I wrote only this report.

## Decision table

| Stage | Evidence / decision | Interpretation |
|---|---|---|
| Before (Round 37 local negative) | Equal-duration 2.0 s pair; project-measured baseline-relative centroid delta `0.06585562259644766`; duration delta `0.0 s`; ordinary and loop checks empty; generic `_alt` distinctness fails. | The centroid arm is below `.10`; with duration unchanged, the existing `.020 s OR .10` predicate rejects. This is a local negative, not general calibration. |
| Round 38 author proposal (LOG declaration) | Add a separate opt-in scratch pair, same 2.0 s duration and `(2.0, 5, 200, True)` checks; demonstrate measured relative centroid strictly `> .10` and `< .13`, with unchanged gate. | Proposal only. Source frequency/coefficient cannot stand in for project-measured centroid; no runner pass follows from the declaration. |
| Numeric fit attempts (executor) | Initial 60/64 Hz pure-tone pair reproduced the R37 negative (`0.0658556`); single-tone candidates from 60–75 Hz did not meet the target; exploratory multi-tone amplitude sweeps also did not reach it. | These are unsuccessful numeric fits, not setup errors. They are not threshold failures from an integrated runner. |
| Setup error (executor) | One helper invocation supplied relative scratch paths and raised `ValueError` while converting paths relative to the corpus root; retry with absolute paths worked. | Setup/path failure only; it is not a numeric fit result and must not be counted as one. |
| Viable executor fit | `base.wav` vs `var_0.050.wav`, both 2.0 s / 96,000 frames / 48 kHz mono PCM16; centroids `36.6164076785` and `41.2475246227 Hz`; relative delta `0.1264765508`; duration delta `0.0 s`; ordinary/seam failures empty; hashes differ. | Meets the strict numeric interval and has the centroid arm true while duration arm is false. A fit only; no integrated runner result. |
| Independent alternative fit (alt) | 65 Hz vs 75 Hz, both 2.0 s; centroids `91.03372963007341` and `81.62439856673954 Hz`; relative delta `0.10336093117979261`; duration delta `0.0 s`; ordinary/seam failures empty; hashes differ. | Also meets the strict numeric interval as an independent candidate. Its relative-path helper attempt raised `ValueError` at receipt-path conversion; absolute paths succeeded. This is setup, not a failed fit. |
| After / remaining gate | Neither candidate report is an integrated `--probe-ambience-centroid-above` runner receipt. The parent must select/integrate a candidate and a non-author replay must establish the mode outcome and preservation checks. | Pending. Do not call Round 38 admitted or say the integrated predicate passed based on fit-only evidence. |

## Command and exit record

I ran no shell commands. The reports record these executor command vectors and statuses; their helper-script bodies are abbreviated in the source report, so I do not reconstruct them here:

- `['python3', '.shokunin/audio/corpus/live/round-38/executor/generate.py', '60', '67']` — exit 0.
- `['python3', '-c', <measure helper script with relative scratch paths>]` — exit 1, setup/path error.
- `['python3', '-c', <same helper script with absolute scratch paths>]` — exit 0.
- `['python3', '.shokunin/audio/corpus/live/round-38/executor/generate.py', '61', '62', '63', '64', '65']` — exit 0; exploratory singles.
- `['python3', '.shokunin/audio/corpus/live/round-38/executor/generate.py', '60', '60.1', ..., '75']` — exit 0; 151 single-tone candidates, none in band.
- `['python3', '.shokunin/audio/corpus/live/round-38/executor/generate.py']` — exit 0 as transcribed in executor report (two-tone exploratory candidate; path spelling is preserved from that report).
- `['python3', '.shokunin/audio/corpus/live/round-38/executor/generate.py', '0.005', '0.010', ..., '0.100']` — exit 0 as transcribed in executor report; added-100Hz sweep did not reach band.
- `['python3', '.shokunin/audio/corpus/live/round-38/executor/generate.py', '0.01', '0.02', ..., '0.10']` — exit 0 as transcribed in executor report; harmonic sweep did not reach band.
- `['python3', '.shokunin/audio/corpus/live/round-38/executor/generate.py', '0.03', '0.05', '0.07', '0.09', '0.11', '0.13', '0.15', '0.18', '0.20']` — exit 0 as transcribed in executor report; selected `.050` fit.
- `['python3', '-c', <measure helper script for final pair>]` — exit 0.

The three `/ .shokhun` spellings above appear exactly as supplied in the executor report; because the documented `generate.py` path is `.shokunin`, treat any such invocation as a possible report transcription issue rather than silently normalizing it. Executor states its selected measurements succeeded, but these command strings alone do not establish an integrated runner outcome. Alt reports no shell commands; its first relative-path helper call failed with `ValueError` and its absolute-path retry succeeded.

## Scope limit

This is numerical control evidence only. The centroid is one scalar measurement; seam checks are limited boundary proxies. No audition, audio/perceptual quality, production, rights, engine, publish, or promotion claim is made. The `.10` rule is unchanged and this pair would test only one local positive polarity, not an exact boundary or universal cutoff.
