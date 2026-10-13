# r29-scribe — candidate/observed decision table

## Scope and status

This report covers the declared round-29 lower-centroid calibration case. Candidate assets are scratch-generated 5760-frame, 48 kHz mono PCM16 signals; baseline is the UI-shaped `k=1.00` analytic chirp. The project measurement function reports the whole-waveform FFT spectral-centroid proxy. The proposal requires a lower centroid on each candidate, zero duration delta, and ordinary UI checks passing for both files, with one relative delta below `.10` and one at or above `.10`. The existing distinctness predicate is absolute relative centroid delta `>= .10` (OR the existing duration arm); no cutoff or constant was changed. There is no integrated round-29 runner receipt in the evidence available for this report, so the distinctness decisions below are predictions from measured inputs, not observed comparator outcomes.

## Decision table

| Candidate | Proposed decision (duration arm false) | Observed measurement | Ordinary UI checks | Classification |
|---|---|---|---|---|
| Baseline `k=1.00` | Reference | 0.120000 s; centroid 966.896659 Hz | pass; no measurement failures | Reference only |
| `k=0.95` | Below `.10`: expected to fail distinctness | 0.120000 s; centroid 871.155505 Hz; signed delta `(variant-base)/base = -0.0990190`; absolute relative delta **0.0990190**; duration delta 0 | pass; PCM16/48 kHz/mono, peak 0.3757324, RMS −19.991709 dBFS, centroid in UI band; empty failures | Candidate predicts existing distinctness failure; comparator not run |
| `k=0.90` | At/above `.10`: expected to pass distinctness | 0.120000 s; centroid 865.698025 Hz; signed delta `-0.1046633`; absolute relative delta **0.1046633**; duration delta 0 | pass; PCM16/48 kHz/mono, peak 0.3754883, RMS −19.991708 dBFS, centroid in UI band; empty failures | Candidate predicts existing distinctness pass; comparator not run |

Both candidates are below the baseline centroid; the `.90` candidate specifically illustrates why the rule must take an absolute value rather than compare signed `(variant-base)/base` to a positive threshold. The measured pair brackets the numeric predicate only at two points. It does not establish exact `.10` equality, behavior between points, monotonicity, or smoothness.

## Other fit points

The same successful scratch sweep measured `k=.99: .0259969`, `.98: .0494142`, `.85: .0575250`, `.80: .1255899`, `.70: .3077554`, `.60: .2617963`, and `.50: .4788067` absolute relative centroid delta. Every one had duration 0.12 s and an empty ordinary-measurement failure list. These results are nonmonotonic (for example, `.85` is closer to baseline than `.90`); they are not a continuous calibration curve. The selected bracket is `.95`/`.90`, not a claim that all candidates on either side behave similarly.

## Commands and exits

- `python3 .shokunin/audio/corpus/live/round-29/alt/fit.py` — exit **0**. Generates/uses the scratch WAVs and prints project `measure_audio.measure` results for baseline and all listed candidates. Baseline and both table candidates had empty `failures` lists. Duration was 0.12 s for all.

No separate runner mode, full validation suite, or independent replay was run by this scribe. No additional command/setup failure was encountered in the command above. Thus there are no failed setup attempts to report here; candidate fit points that do not bracket the cutoff are disclosed in the table of other fit points rather than mislabeled as setup errors.

## Limits

Evidence is scratch measurement only. The FFT centroid is a numeric proxy, not evidence of perceptual difference. No runner comparator result, independent replay, admission, smoothness, or exact-cutoff equality is claimed. Nothing here establishes rights, engine behavior, publishing readiness, or production/promotion status. No source, LOG, SCORECARD, canonical asset, threshold, or other report was edited.
