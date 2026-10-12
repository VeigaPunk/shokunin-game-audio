# Round 13 simplifier review

## Scope and evidence

Static review of the Round 13 declaration in `.shokunin/audio/LOG.md`, plus the current `corpus/fixtures/build_artifacts.py` and `measure_audio.py`. No shell commands were run; no scratch WAV was generated or measured. No source, declaration, scorecard, or canonical asset was edited.

## Single-source-of-truth review

- `section_contrast(path, component_hz)` already calculates the 180 Hz amplitudes in two halves, validity, contrast, and internal-join metrics. Reuse this helper for the matched control; do not add a parallel flat-control analyzer or reproduce the 6 dB comparison.
- The current source has round-12 handling for `stem_layer_alt` but no round-13 flat-180 probe mode yet. The existing per-name instrumentation is distributed across the sections comprehension, component-frequency selection, and internal-join gap/slope name conditions. A new control needs to be included consistently in those existing paths (180 Hz measurement and the existing internal gap and side-slope checks), not given bespoke limits.
- The existing generic `measure()` already supplies format, duration, level, centroid-band, outer endpoint, and outer slope checks. Keep those checks unchanged and use them for the scratch control. The existing `_alt` distinctness loop applies to `stem_layer_alt`; the control is not an alternate canonical fixture and should not be added to `SPECS` or treated as a new `_alt` pair.
- Preserve the existing sole section-failure text and 6 dB threshold. A valid equal-amplitude 180 Hz control should be invalid only by the existing contrast test; its validity, generic checks, and internal-join metrics should otherwise pass. Do not add a numeric threshold or redefine “flat.”

## Minimal integration guidance

Add only the requested probe mode and scratch generation in the established probe flow, writing under `corpus/live/round-13/`. Let the current section helper and existing checks produce the expected section failure; avoid special-case failure suppression or a second comparator. Ensure control section accounting applies the existing internal gap and slope checks while leaving canonical `stem_layer_alt`, its `_alt` distinctness comparison, all old probe branches, and the 12 canonical assets unchanged. Keep the scratch outside `SPECS` so it cannot become a canonical or normal-measurement asset.

Static review only. No claims about acoustic flatness, audibility, adaptive-engine behavior, music, rights beyond original synthetic generation, security, or production suitability.
