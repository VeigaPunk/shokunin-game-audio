# Round 13 scout — 180 Hz section and gate map

## Scope
Read `.shokunin/audio/LOG.md` Round 13 declaration and current `corpus/fixtures/measure_audio.py` plus `corpus/fixtures/build_artifacts.py`. No shell commands were run; no files were generated or measured. This is a source map, not a validation result.

## Current 180 Hz measurement
- `SPECS["stem_layer_alt"]` is `(4.0, 100, 2000, True)`: expected duration 4 s, centroid band 100–2000 Hz, loopable. It is an entry in the 12-name canonical measurement set, not a probe.
- The `sections` comprehension explicitly includes `stem_layer_alt` and selects component 180 Hz for that key. `section_contrast` decodes via SoX to float32 then uses float64 samples; exactly 192,000 samples are required, split into two 96,000-sample (2 s) halves. At 48 kHz the FFT spacing is 0.5 Hz; 180 Hz is bin 360. Per-half amplitude is `2 * abs(rfft(half)[360]) / 96000`.
- A section is valid only when both amplitudes are finite and >= .01 full scale and both half RMS values are >= .001. Its contrast is `20*log10(second_half_amplitude / first_half_amplitude)`; `passed` requires valid and contrast >= 6 dB. The caller adds `sections: 180 Hz component amplitude contrast < 6 dB or invalid` when it does not pass.
- The helper also reports the internal midpoint adjacent-sample gap, `abs(samples[96000]-samples[95999])`, and side-slope mismatch across the boundary. For `stem_layer_alt`, caller gates gap > .03 full scale and slope mismatch > .001 full scale/sample. These are internal join checks, distinct from outer seam checks.

## Generic, outer, internal, and distinctness gates
- Generic `measure()` checks 48 kHz mono, duration within ±1 ms, peak < .95, RMS >= .001, centroid within the spec band, and—because `stem_layer_alt` is loopable—outer endpoint delta <= .03 and outer slope mismatch <= .001. Any failures are appended to that measurement’s failure list.
- The 180 Hz internal gap/slope checks are only applied to `stem_layer_alt` among current measured keys (along with existing `stem_layer` and applicable probes). Do not infer that merely calling `section_contrast` adds these caller-side gates.
- `_alt` distinctness iterates names ending in `_alt`, pairs each with `measurements[name[:-4]]`, and passes if duration delta >= .020 s OR relative whole-file centroid delta >= 10%. For `stem_layer_alt`, the baseline is `stem_layer`. A candidate probe named `flat180_probe` does not end in `_alt` and thus is not itself distinctness-tested; the clean canonical `stem_layer_alt` continues to be. This is whole-file centroid/duration distinctness, not a 180 Hz contrast test.
- Current probe modes are mutually exclusive. The declaration’s new flat-control branch is not present in either source yet. Source should route that control to a 180 Hz section measurement and the intended generic/outer checks, while preserving existing gates rather than adding duplicated or new bounds. The expected sole section-contrast failure is a hypothesis until its receipt is measured; all other candidate failure channels must be checked explicitly.

## Round 13 claim boundary
The declared move is depth: a same-format, same-length equal-per-half 180 Hz control should fail the existing 6 dB contrast branch while passing generic/outer/internal checks; clean alt should pass. Existing values (.01 component validity, .001 RMS, 6 dB, .03 gap, .001 slope, 10%/20 ms distinctness) are fixture-local checks, not calibrated quality or audibility thresholds. The flat control establishes only numeric check polarity for original synthetic PCM. It cannot establish audible flatness, adaptive engine behavior, music quality, or production readiness. No claim here about execution, fit, canonical hashes, or a successful probe.
