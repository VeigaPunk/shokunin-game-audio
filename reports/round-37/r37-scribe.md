# Round 37 scribe — before/after decision table

## Scope and evidence boundary

This note follows the Round 37 declaration in `.shokunin/audio/LOG.md`. The declared question is narrow: add one opt-in, scratch-only equal-duration ambience negative control where the measured centroid delta is nonzero but <10%, so the existing duration-OR-centroid distinctness rule rejects on distinctness alone while the individual numeric/loop checks pass. This is a numerical-control proposal, not an audition or asset-quality judgment.

At review time, `measure_audio.py` has no `--probe-ambience-centroid-below` option, and `.shokunin/audio/corpus/live/round-37/` contains no files. No Round 37 run/report artifacts were present in `reports/round-37/`. I ran no shell commands, generated no fits, and made no source or fixture changes. Thus there is no observed numeric fit result to report; this is not evidence that a fit failed.

## Before / after decision table

| Decision point | Before (clean checkpoint / existing evidence) | After (declared target / evidence currently available) | Decision |
|---|---|---|---|
| Control coverage | 17 canonical WAVs. The existing ambience positive comparisons have equal 2.0 s duration and pass via centroid delta. Existing UI controls include exact clone and below/above or joint controls, but do not supply the requested equal-duration ambience-family, nonduplicate negative. | Proposed pair is scratch-only: baseline plus nonidentical `_alt`, both 2.0 s, measured relative centroid delta `0 < delta < .10` (preferably `.05 < delta < .10`). | The missing case is specific and worth testing; proposal alone does not establish a passing fit. |
| Individual numeric checks | Existing loop and ordinary-fixture limits are recorded in the runner: 48 kHz mono PCM16; duration tolerance ±1 ms; peak `< .95`; RMS `> .001`; ambience centroid 5–200 Hz; loop endpoint delta `<= .03`; slope mismatch `<= .001`. | Required pair must satisfy those checks for both files; duration delta must be exactly `0.0`. Existing distinctness OR rule must then report false, with only the distinctness failure on the variant. | Do not call it a successful negative control until its receipt proves all conditions together. |
| Canonical/regression boundary | The declared clean checkpoint is `83395d1b4241582463d9d5fbdece619180610372`; baseline is 17 canonical files. | Required preservation is all 17 canonical hashes/metrics, thresholds, existing generic five `_alt` controls, explicit family records, and prior 34-mode outcomes. No Round 37 run has been observed here. | Preservation remains unverified; no inference of regression or success. |
| Numeric fit outcome | No equal-duration ambience negative of this form is declared in the baseline. | No scratch files, receipt, or fit attempt are available in the inspected Round 37 paths at review time. | **Fit status: not attempted / not evidenced**, not “failed fit.” If a future numerical candidate misses the centroid window or any limit, record it as a failed fit and do not admit it. |
| Setup outcome | No Round 37 execution attempt observed. | No command was run by this scribe; there is no exit code or setup failure to classify. | **Setup status: none observed**, not a numerical failure. If a future command cannot start/find dependencies/inputs, report exact command and exit as setup separately from fit results. |

## Conclusion

No before/after implementation or measured result can be attested from the evidence available to this scribe. The declaration defines a falsifiable target and preservation requirements; the new numerical control remains unverified here. A failed numeric fit would be a candidate that runs and measures but misses the stated numeric window/checks. A setup failure would prevent that measurement from occurring. Neither occurred in this scribe's work, so there are no commands or exit codes to quote.

Centroid, duration, and seam measurements are numerical proxies only. This report makes no audition, quality, production, rights, engine, publish, or promotion claim.
