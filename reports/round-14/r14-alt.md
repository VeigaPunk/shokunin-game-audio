# Round 14 alternative exploration: `join180_other.wav`

## Scope and method

Independent local exploration of the declared 180 Hz gap-only negative. I used the original synthetic mono PCM16 48 kHz source `.shokunin/audio/corpus/artifacts/stem_layer_alt.wav` (192,000 frames; SHA-256 `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9`). The source-generated signal is the 180 Hz layer with first-half amplitude 0.015 and second-half amplitude 0.050. I made a separate scratch WAV; no canonical artifact, fixture source, runner, LOG, SCORECARD, or commit was changed by this lane.

Scratch artifact: `.shokunin/audio/corpus/live/round-14/join180_other.wav`, 384,044 bytes, SHA-256 `a9e449b8270343d0c9339c600295ad669fde65d5b3a967649e6d7df7c5034528`. It starts from original `stem_layer_alt` PCM, adds a smooth 60 Hz, 0.03 FS sine over the 4 s waveform (a source-generated broad smooth bed), then adjusts frames 96000 and 96001 to preserve the preceding local increment while creating a gap. Final samples at frames 95998..96002 are `[-38, -20, 996, 1015, 92]` PCM counts. The central adjacent gap is 1016 counts = 0.0310068 FS, while side-slope mismatch is 0.0000305 FS/sample, under the existing .001 limit. This avoids the broad-spectrum impulse fit failure described below while retaining one targeted adjacent gap violation.

## Measured gates / fit telemetry

Measurements below are independent calculations on the scratch PCM with the same FFT/section definitions visible in `measure_audio.py`; they are not a runner receipt (the current runner has no `--probe-layer-alt-join` mode). A formal integrated-loudness reading was not run for this exploratory candidate; RMS dBFS is reported separately.

| Gate / observable | Result | Existing local bound | Result |
|---|---:|---:|---|
| WAV format | PCM16, mono, 48,000 Hz | mono / 48 kHz | pass |
| Duration | 4.000 s / 192,000 frames | 4.000 ± .001 s | pass |
| Peak | 0.0657369 FS | < .95 | pass |
| RMS | 0.0336341 FS (−29.4644 dBFS) | > .001 FS | pass |
| Whole-wave spectral centroid | 1863.739 Hz | 100–2000 Hz | pass |
| Loop endpoint delta | 0.00143437 FS | ≤ .03 | pass |
| Loop endpoint slope mismatch | 0.00076296 FS/sample | ≤ .001 | pass |
| 180 Hz first/second-half component amplitudes | 0.01500006 / 0.04999909 FS | each ≥ .01 | pass |
| Section RMS | 0.02371796 / 0.04123067 FS | each ≥ .001 | pass |
| Component contrast | 10.45725 dB | ≥ 6 dB | pass |
| Internal join adjacent delta | 0.03100681 FS | ≤ .03 | **fail** |
| Internal join side-slope mismatch | 0.00003052 FS/sample | ≤ .001 | pass |

The selected scratch therefore passes the broad 100–2000 Hz centroid band (1863.739 Hz), as well as format, duration, peak/RMS, loop seam, section validity/contrast, and join-side slope; the target adjacent-gap gate is the sole failed acceptance gate. The smooth added bed is deterministic synthetic signal, not an audible-quality claim. This is a gap-only failure according to those numerical gates, not evidence of a perceived click.

## Failed-fit telemetry / sensitivity

The exploratory target was a central sample just above 0.03 FS, not an arbitrary large spike. Around this source's frame 95999 = −12 PCM counts, the selected frame-96000 value is 996 counts, giving a 0.0310068 FS gap and passes the contrast and all listed companion gates. If frame 96001 is left unadjusted at the original 39 counts, side-slope mismatch becomes 0.0292367 FS/sample (fails the .001 bound) in addition to the gap: that fit is rejected as *not* gap-only. A naive one-sample gap injection into the unmodified layer is also a bad fit even after making its slope continuous: its impulsive broadband energy raises whole-wave centroid to 2180.954 Hz, above the 2000 Hz upper band. Leaving its next sample untouched produces an additional .029237 FS/sample slope failure. A large impulse is worse: central sample 1600 counts gives .049196 FS gap and .047975 FS/sample slope mismatch when the next original sample is retained. The selected smooth-bed candidate avoids those extra failures while preserving gap-only gate isolation. This records why a naive single-sample perturbation is a failed fit and documents the adjustment that isolates the requested gate.

## Commands / provenance

Shell commands used (from repository root) and exits:

- `find . -name 'join180_other.wav' -o -iname '*join180*' | head -30` — exit 0; found the executor's `join180_candidate.wav`; the first lookup had no `join180_other.wav`.
- `find . -name 'join180_other.wav' -o -iname '*join180*' | head -30` — exit 0 after creating this lane's scratch; found candidate and other scratch WAV.

The file was created directly via Python `wave` and NumPy operations in the persistent REPL; there was no shell command or runner invocation for creation/measurement. It is deterministic, from the original synthetic PCM, and has no listening, engine, security, or production-quality claim. Thresholds are the existing local fixture bounds only.
