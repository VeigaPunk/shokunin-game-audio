# Round 12 scout — current section and distinctness semantics

## Scope and read sources
Read `.shokunin/audio/LOG.md` Round 12 declaration plus `corpus/fixtures/measure_audio.py` and `corpus/fixtures/build_artifacts.py`. No shell commands were run; no waveform was generated or measured. This is a source-semantics map, not a fit or validation claim.

## Current section measurement
- `section_contrast(path, component_hz=30)` decodes to float32 through SoX, converts to float64, and accepts exactly 192,000 samples (four seconds at 48 kHz); otherwise it returns invalid `section count` with no amplitudes.
- It splits into two 96,000-sample halves, each two seconds. For each half, the requested component uses bin `component_hz * 96000 // 48000`. Thus 120 Hz maps to bin 240; 180 Hz maps to **bin 360** (FFT spacing 0.5 Hz). Amplitude is `2 * abs(rfft(half)[bin]) / 96000`.
- Validity requires finite amplitudes, each component amplitude >= .01 FS, and each half RMS >= .001 FS. Contrast is `20*log10(second_amp/first_amp)` and `passed` means valid and contrast >= 6 dB. This is one-bin component amplitude, not a full spectrum or perceptual measure.
- At the internal boundary, adjacent gap is `abs(samples[96000]-samples[95999])`; side-slope mismatch compares the sample increments across frames 95998–96001. Both are returned by the helper. Current caller gates gap > .03 for `stem_layer`, `join_probe`, and `layer_slope_probe`; it gates slope mismatch > .001 only for `stem_layer` and `layer_slope_probe`. `stem_sections` and flat30/flat120 controls use the same helper but no internal gap/slope gate.
- Caller currently assigns 120 Hz only to `stem_layer`, `flat120_probe`, `join_probe`, `layer_slope_probe`; `stem_sections` and `flat30_probe` use 30 Hz. Other items are omitted from `sections`. A new alt needs deliberate membership in this map, with 180 Hz, and its own appropriate gap and slope gate; simply adding it to `SPECS` does not produce a section result or internal gate.

## Generic measurement and distinctness
`measure()` checks mono 48 kHz, duration within ±1 ms of its spec, peak < .95, RMS >= .001, centroid within its spec band, and for loopable specs outer endpoint delta <= .03 and outer slope mismatch <= .001. `stem_layer` is specified as 4 s, centroid 100–2000 Hz, loopable; an alt spec should preserve those generic constraints. These outer-seam checks are distinct from the internal section-boundary values.

Distinctness iterates measured entries whose names end in `_alt`, pairs each to `measurements[name[:-4]]`, then passes if duration delta >= .020 s **OR** relative centroid delta >= .10. For `stem_layer_alt`, the intended baseline key is `stem_layer`; exact expected pairing depends on both entries being present. This comparison uses whole-file spectral centroid, not the requested 180 Hz section component. Check that the new alternate appears in measurements under this exact suffix convention; section-only insertion will not create a distinctness result. No further distinctness threshold is warranted by the declaration.

## Round 12 declaration alignment
The LOG defines one coverage move: retain existing two-section 120 Hz `stem_layer`, add one original distinct 4 s 180 Hz stepped-amplitude `stem_layer_alt`, measure its own per-half contrast and generic/outer plus internal gap/slope checks, and compare it against the base using existing `_alt` distinctness logic. The hypothesized `.015/.050 * sin(2*pi*180*t)` recipe is not evidence until measured. Existing 6 dB, .03, .001 and 10% thresholds are fixture-local reused gates, not calibrated audibility thresholds. Any result supports synthetic fixture coverage only, not adaptive engine behavior, playback, music, audibility or production readiness.
