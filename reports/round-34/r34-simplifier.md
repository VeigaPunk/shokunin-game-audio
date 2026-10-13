# Round 34 — simplifier

## Recommendation

Keep this to one third original impact WAV plus one explicitly named impact-family comparison receipt against `impact` and `impact_alt`. Do **not** generalize the existing `_alt` loop or add a variant abstraction. The existing local distinctness rule (duration difference ≥0.020 s **or** relative centroid difference ≥0.10) already covers both comparisons; keep its thresholds unchanged. The third fixture's preflight passes the requested numeric gates.

## Scratch candidate and fit

Scratch only: `corpus/live/round-34/simplifier/impact_third.wav` (not canonical). Generated 19,200 samples at 48 kHz from `t = arange(19200)/48000` using the original analytic recipe

`0.42*sin(2π*2600*t)*exp(-18*t) + 0.16*default_rng(20261013).standard_normal(19200)*exp(-85*t)`

then clipped to [-1,1], rounded to signed PCM16 counts with `round(sample*32767)`, mono 48 kHz. SHA-256: `76082a17f1252e451c763112d7efcf7f76155cf548bd7520069a67bdda4baabe`.

Direct project `measure()` result for the proposed (.40 s, 50–15000 Hz, non-loop) spec: duration .400 s; PCM16/48 kHz/mono; peak .680267333984375 FS; RMS −21.870164296015894 dBFS; centroid 9732.507888417593 Hz; failures `[]`. Baseline measurements: `impact` .320 s / 10843.127202979938 Hz; `impact_alt` .320 s / 473.7915356810072 Hz. Against `impact`, duration delta is .080 s and relative centroid delta .10242610768756102; against `impact_alt`, duration delta is .080 s and relative centroid delta 19.541751288208456. Both clear the existing OR rule. This is numeric fixture fit only, not evidence of audible or perceptual difference.

## Setup/commands and limits

No shell command was run, so there are no shell exit codes to report. Initial measurement-module setup attempt failed with `AttributeError: module 'measure_audio' has no attribute 'save'`; that was a helper-lookup/setup failure, not a candidate fit failure. The scratch WAV was then written using the builder's PCM16 conversion rule and measured successfully through the project measurement function.

Recommendation for parent integration: add exactly one canonical `impact_third.wav`, its deterministic builder source, `SPECS["impact_third"]=(.40,50,15000,False)`, and the separate two-comparison receipt field described in the declared round spec. Candidate remains scratch until parent integration and independent verification. No generic threshold/framework edit is proposed. No listening, quality, production, rights, engine, publish, or promotion claim is made.
