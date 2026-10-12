# Round 12 simplifier review

## Scope and evidence

Static review of `.shokunin/audio/corpus/fixtures/build_artifacts.py` and `measure_audio.py`, against the Round 12 declaration in `.shokunin/audio/LOG.md`. No shell commands were run; no candidate was generated or measured. No edits outside this report.

## Duplicate-source and gate risks

- `SPECS` is the measurement inventory, so adding `stem_layer_alt` there makes it part of the normal measurement receipt. The current `_alt` distinctness loop already derives the base by removing `_alt`; `stem_layer_alt` therefore compares against `stem_layer` without a new pair-specific comparator. It reuses the existing `duration_delta >= .020 or centroid_relative_delta >= .10` rule.
- The section instrumentation is separately hard-coded by name in the `sections` comprehension, component-Hz choice, and internal-gap/slope name conditions. Merely adding the new `SPECS` entry does **not** give the alternate its section result or checks. Duplicating more special-case lists creates drift risk; make the smallest integration explicit and ensure the alternate uses 180 Hz and both existing internal-join checks.
- No new numeric gate is warranted. Reuse current section validity/6 dB contrast and generic seam checks, existing `.03` internal gap and `.001` internal slope conditions, and existing distinctness comparator. The declared candidate is only a hypothesis until its own receipt passes all of these.
- Source fixture generation has one canonical `stem_layer` expression. Add the alternate as a separate generated signal; don't overwrite or mutate the existing layer. The measurement receipt should retain old entries and report the added fixture, not revise historical receipts.

## Minimal integration suggestion

Add `stem_layer_alt: (4.0, 100, 2000, True)` to `SPECS`; generate a distinct 4-second 180 Hz stepped-amplitude waveform in `build_artifacts.py`; include it in section measurement at 180 Hz and apply the same layer internal gap and slope checks. Keep this as a small explicit extension of the current layer-specific logic (or centralize the section component mapping if doing so removes, rather than adds, duplicated name lists). Let the existing generic `_alt` logic perform comparison. Do not add a second comparator, threshold, or special waiver.

Static review only: no claims about fit, audible behavior, playback, rights beyond original synthetic generation, or production suitability.
