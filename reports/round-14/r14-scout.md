# Round 14 scout: decoded 180 Hz join and guard rules

## Scope and method

Read-only inspection of `corpus/fixtures/build_artifacts.py`, `corpus/fixtures/measure_audio.py`, and the original generated synthetic `corpus/artifacts/stem_layer_alt.wav`. Decoded the WAV's mono PCM16 frames directly as signed little-endian 16-bit integers and divided by 32767, matching the builder's PCM conversion convention. No shell commands were run; no runner was invoked and no files other than this report were written. This is a digital fixture inspection, not listening or an engine/production assessment.

## Original 180 Hz layer around the section boundary

The file is 48 kHz mono with 192,000 samples, and the section boundary is sample 96,000 (2 seconds). The four decoded source samples are:

| index | signed PCM16 | decoded full scale |
|---:|---:|---:|
| 95998 | -23 | -0.0007019257 |
| 95999 | -12 | -0.0003662221 |
| 96000 | 0 | 0.0000000000 |
| 96001 | 39 | 0.0011902219 |

Thus the original adjacent boundary gap, `abs(x[96000]-x[95999])`, is 0.0003662221 FS. Left and right one-sample slopes are respectively 0.0003357036 and 0.0011902219 FS/sample; their absolute mismatch, `abs((x[96001]-x[96000])-(x[95999]-x[95998]))`, is 0.0008545183 FS/sample. Both gap and mismatch are below the respective thresholds. The right slope itself is not what the slope-mismatch check bounds.

## Relevant acceptance logic and threshold semantics

The section analyzer splits each 192,000-sample signal into two 96,000-sample halves and measures the exact-frequency FFT-bin component (180 Hz for `stem_layer_alt` and its flat180 probe). Section validity requires both component amplitudes finite and at least 0.01 FS, and each half RMS at least 0.001 FS. It computes signed amplitude contrast `20*log10(second_half/first_half)`; acceptance requires valid sections and contrast **at least 6.0 dB**. This is not an absolute-value contrast: the latter section must be at least 6 dB above the former.

For the internal layer join, the adjacent-sample failure is added only when the measured gap is **strictly greater than 0.03 FS**; the side-slope mismatch failure is strictly **greater than 0.001 FS/sample**. Equality passes those checks. These layer thresholds supplement rather than replace the section-contrast gate. `stem_layer_alt` is included in both join checks. In the round-14 `probe-layer-join` path, the gate list includes the gap check but explicitly excludes the slope-mismatch check for `join_probe`; therefore the intended controlled negative must isolate the gap gate while the separately reported slope mismatch remains within the declared local value. Other layer modes (`stem_layer`, `stem_layer_alt`, flat180, layer-slope) use both internal checks.

The generic fixture gates also retain exact stated semantics: 48 kHz mono; duration within ±1 ms; peak must be below 0.95 and RMS above 0.001; centroid lies within inclusive fixture bands. These are deterministic fixture rules only. No new threshold is proposed.

## Caveat

These values and guards describe decoded synthetic PCM and local proxy checks. They establish neither audible discontinuity nor musical suitability, engine behavior, security, or production quality.
