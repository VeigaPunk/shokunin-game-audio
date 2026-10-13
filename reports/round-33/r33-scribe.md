# Round 33 scribe — UI-family decision table

## Before / after decision table

The declared change is coverage: add one original-source analytic UI-family fixture at `.20 s` and record its pairwise outcomes against both existing UI fixtures. The current rule is the existing distinctness OR: duration delta `>= .020 s` **or** relative centroid delta `>= .10`. “Accept” below means only that this numeric pairwise distinctness predicate passes; it is not a quality or perceptual judgment.

| Family state / pair (baseline vs candidate) | Expected duration delta | Measured duration delta | Expected centroid-relative delta | Measured centroid-relative delta | Existing OR arms / result |
|---|---:|---:|---:|---:|---|
| Before: `ui` (.12 s) vs `ui_alt` (.16 s) | .04 s | .04000000000000001 s | Not specified in the round-33 declaration | 0.472393… (from the existing measured centroids) | Duration true; centroid true; pass |
| After candidate: `ui` (.12 s) vs `ui_third` (.20 s) | .08 s | 0.08000000000000002 s | Not prescribed; intended only to satisfy ordinary UI centroid band | 0.00018103031409457665 | Duration true; centroid false; pass via duration |
| After candidate: `ui_alt` (.16 s) vs `ui_third` (.20 s) | .04 s | 0.04000000000000001 s | Not prescribed; intended only to satisfy ordinary UI centroid band | 0.3207185389302337 | Duration true; centroid true; pass via duration (and centroid) |

The before-pair relative centroid is `abs(1423.1532540422852 - 966.8966593379727) / 966.8966593379727 = 0.472393…`. All three files measured as 48 kHz mono PCM16 and each passed its applicable individual duration, level, and 250–4000 Hz centroid checks. The analytic third fixture measured 0.20 s, peak `0.375946044921875`, RMS `-22.20695387316763 dBFS`, centroid `966.7216217320357 Hz`; its measured pair deltas, not nominal duration alone, decide the table.

## Fit/setup record and evidence boundary

I ran this exact project command:

```sh
cd /home/vgpnk/Projects/prymeagnt/audio && python3 .shokunin/audio/corpus/live/round-33/alt/fit.py
```

Exit code: **0**. It uses the project `measure_audio.py` measurement implementation on the existing canonical `ui.wav`/`ui_alt.wav` and a newly source-generated scratch `ui_third.wav` under `corpus/live/round-33/alt/`. The fit script printed no ordinary-check failures and both proposed comparisons pass the existing OR predicate. No measured coefficient/fit failure occurred. An initial malformed shell-wrapper invocation failed before running the project script (setup only); the exact command above was the corrected successful run. No threshold or canonical file was changed by this scribe.

This is **analytic fixture evidence only**. The round declaration targets a canonical third fixture and an increase from 13 to 14 canonical WAVs, but the observed third candidate remains under `corpus/live/round-33/alt/`; it is not integrated into the canonical builder/spec or generic `_alt` comparator. No 13-hash preservation check, historical replay, independent runner verification, or admission verdict is established by this report. The duration arm alone is enough for both new comparisons; this says nothing about perceptual distinctness. No audition, quality, production-readiness, rights, engine, publishing, or promotion claim.

Only this report is written by me. No shared source, LOG, SCORECARD, canonical artifact, or other report was edited; no commits or pushes.
