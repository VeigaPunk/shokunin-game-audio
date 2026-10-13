# Round 33 scout: UI family and comparison map

## Scope and provenance

I read the round-33 declaration in `.shokunin/audio/LOG.md` and inspected the fixture builder, measurement entry point, current normal receipt, canonical artifact names, and existing audio notes. I did **not** run shell commands, build or audition audio, edit shared sources, or change canonical artifacts. Thus there are no shell command exit codes to report; this is a source/receipt inspection only.

The current artifact directory contains 13 WAVs: five original fixture families plus the UI/impact/movement/ambience alternates and stem section/layer fixtures. The declared round-33 baseline says all 13 canonical hashes are protected. For reference, current `ui.wav` SHA-256 is `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9`; `ui_alt.wav` is `166275cdee0fcd8ca16d95fe75355159aeb25c7271c106906ad2555282b6517f`. These are inspection-time values, not a freshly verified before/after preservation test.

`build_artifacts.py` produces PCM16 mono WAVs at 48,000 Hz through `save()` and quantizes clipped samples. The declared UI assets are generated fixtures, not licensed source recordings. A proposed `ui_third.wav` should remain a source-generated *analytic fixture*, add no external sample or rights assertion, and must not alter the existing 13 bytes. It is not an audition, sound-quality finding, production-ready asset, or permission for engine, game, publishing, rights, or promotion use.

## Existing UI family and rules

`measure_audio.py` declares:

- `ui`: `(.12, 250, 4000, False)` — 120 ms nominal, centroid acceptance band 250–4000 Hz.
- `ui_alt`: `(.16, 250, 4000, False)` — 160 ms nominal, same band.

The common per-file checks require 48 kHz mono PCM16, measured duration within ±1 ms of that fixture's own spec, peak strictly below .95, RMS strictly above .001, and weighted whole-waveform FFT centroid within the declared band. The existing comparison loop processes names ending `_alt`, looks up the stem-matched baseline, and passes if **either** absolute duration delta is at least .020 s **or** absolute centroid delta divided by the baseline centroid is at least .10. This is a numeric fixture comparison, not a perceptual test.

The current normal receipt `corpus/live/runs/20261013T030036576341Z-normal/measurements.json` records `ui`: 0.12 s, centroid 966.8966593379727 Hz, no failures; `ui_alt`: 0.16 s, centroid 1423.1532540422852 Hz, no failures. Its `ui_alt` pair record is duration delta 0.04000000000000001 s, relative centroid delta 0.47187731004956435, passed. This is existing evidence only, not evidence for `ui_third`.

## Candidate comparison design

A proposed `ui_third` spec at `(.20, 250, 4000, False)` is consistent with the declared family band and gives a separate nominal duration check. At nominal lengths it is 0.08 s from `ui` and 0.04 s from `ui_alt`; both exceed the unchanged .020 s duration arm. Actual encoded/ffprobe durations and each file's individual checks still need measurement. The 20 ms margin for the closer pair is 20 ms beyond the threshold, but only actual measured values establish the result.

Important integration detail: merely adding `ui_third` to `SPECS` measures its ordinary properties, but the current generic pair loop will **not** compare it to `ui` or `ui_alt`: it only pairs `_alt` names with a same-stem baseline. Renaming an existing canonical asset or changing that generic loop risks unrelated behavior and is unnecessary. The minimal comparison is two explicit UI-family pair records, one `ui` ↔ `ui_third`, one `ui_alt` ↔ `ui_third`, leaving the five existing `_alt` comparisons and their generic path untouched. Record measured durations, absolute duration delta, centroid values and relative centroid delta, and apply the existing OR thresholds. For consistent interpretation, state the baseline denominator explicitly for each centroid-relative result; duration is symmetric. The `.20` candidate satisfies the duration branch if both actual deltas remain >=.020, so centroid difference is not needed to claim numeric distinctness. Keep wording strictly to that measured rule.

Do not call a new pair a canonical `_alt` comparison unless it uses the actual comparator semantics. Prefer a clearly identified UI family-pair section in the receipt/report rather than broadening the comparator into a generic all-pairs framework. No threshold changes are warranted by this fixture proposal.

## Failure handling and caveats

If either measured duration delta is below .020, the OR may still pass only if that pair's measured centroid-relative difference is >=.10; otherwise record that pair as failed. Any ordinary format, level, duration, or centroid-band failure excludes the fixture as proposed. Do not lower limits or modify the existing files to force passage. The round declaration calls for a candidate analytic chirp/envelope fit, but its exact signal recipe and measurements are executor work; source inspection alone cannot establish fit.

Duration-only distinctness is a coverage bookkeeping rule. It does not isolate spectral/timbre change, establish perceived difference, quality, utility, or whether it is an appropriate UI sound. In particular, 200 ms is simply a declared fixture duration, not a recommendation for a production UI cue.
