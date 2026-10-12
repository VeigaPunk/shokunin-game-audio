# Round 8 scout — base grid and section-bin map

Scope: source/code and original canonical PCM inspection for the declared coverage claim. No files were changed except this report. I did not run shell commands, so there are no command exit codes to report. No perceptual, engine, security, or production claim is made.

## Base `stem_sections` grid

`corpus/fixtures/build_artifacts.py` synthesizes `stem_sections` from `t = np.arange(4*48000)/48000`, then `common + np.where(t < 2, .012, .060)*sin(2π·30t)`. The common components are 220 Hz at .08 FS and 330 Hz at .04 FS. The saved file `corpus/artifacts/stem_sections.wav` is mono PCM16, 48,000 Hz, 192,000 frames (4.000 s). The section boundary at 2 s is sample 96,000; each section has 96,000 samples. This is a same-grid four-second fixture, not a multi-track engine or perceptual demonstration.

For each 96,000-sample half, an unwindowed `rfft` has frequency spacing 48,000/96,000 = **0.5 Hz/bin**. Thus 30 Hz is bin 60 and 120 Hz is bin 240. The current `section_contrast()` extracts `2*abs(rfft(half)[60])/len(half)`: measured 30 Hz amplitudes are approximately **0.0120** then **0.0600 FS**, a 5x amplitude ratio / **13.98 dB**. In this canonical fixture, 120 Hz bin 240 is effectively zero (about 1e-8–5e-8 from PCM quantization), so the proposed 120 Hz component must use bin 240, not reuse bin 60.

## Existing checks and thresholds

`measure()` currently checks 48 kHz mono; duration within ±1 ms; peak < .95 FS and RMS ≥ .001 FS; centroid in the `stem_sections` 100–2000 Hz band; and, for looping specs, endpoint delta ≤ .03 FS and endpoint-slope delta ≤ .001 FS/sample. The section check currently requires 192,000 decoded samples, 96,000 per half, finite component amplitudes each ≥ .01 FS, section RMS each ≥ .001 FS, and section-2 / section-1 component amplitude contrast ≥ 6.0 dB. Those are fixture-local numerical rules, not evidence of audible quality or seamless looping. Existing flat30 probe has equal .036 FS at 30 Hz in both halves, so its section contrast is 0 dB and should fail the 6 dB predicate while remaining above the amplitude floor.

## 120 Hz interpretation / confounds

For a proposed 120 Hz test, the same aligned half-grid gives bin 240 exactly, avoiding leakage for a stationary, phase-coherent 120 Hz sinusoid. A matched flat120 control with .036 FS in each half should yield approximately equal bin-240 amplitudes and 0 dB contrast. Ensure the analyzer explicitly names 120 Hz/bin 240 (or derives the bin from the frequency and sample count); bin 60 is 30 Hz on this grid. A 120 Hz sinusoid is also the fourth harmonic of 30 Hz, so a broadband harmonic-rich source could produce 120 Hz energy without an independent 120 Hz layer. Here the parent claim is only a generated numeric companion-layer component contrast; the independent layer file and matched control help isolate that metric. The base fixture's 30 Hz and common 220/330 Hz components do not materially populate bin 240. The existing centroid and level gates do not establish component identity, synchronization in a runtime engine, or perceptual salience.
