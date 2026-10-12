# Round 15 scout — decoded 180 Hz join and gates

## Scope and finding

The target is the existing `stem_layer_alt` synthetic 180 Hz, four-second fixture: the first two seconds use amplitude 0.015 and the second two seconds 0.050, with 48 kHz mono PCM16 output. Its 96,000-sample section boundary is the test join. The current runner's `section_contrast()` decodes samples through SoX to float32 and promotes them to float64; the boundary metrics are therefore computed from decoded PCM, not the pre-quantized NumPy generator values.

The clean decoded frames 95998..96001 are, respectively:

| Frame | Value (full scale) |
|---:|---:|
| 95998 | -0.000701904296875 |
| 95999 | -0.0003662109375 |
| 96000 | 0 |
| 96001 | 0.001190185546875 |

These values are also recorded in the round-15 source/LOG brief. The current clean receipt (`corpus/live/runs/20261012T183645508917Z-normal/measurements.json`) independently reports the related 180 Hz section results: contrast 10.457250572050896 dB, valid/pass true, adjacent join gap 0.0003662109375, and side-slope mismatch 0.0008544921875 FS/sample. Both join metrics pass their existing strict upper bounds: gap `<= .03`, side-slope mismatch `<= .001`.

## Gate mapping

For decoded samples `x`, the existing internal measures are:

- Gap: `abs(x[96000] - x[95999])`.
- Side-slope mismatch: `abs((x[96001]-x[96000]) - (x[95999]-x[95998]))`.
- Existing section validity/contrast: each half's 180 Hz FFT-bin amplitude must be at least 0.01 FS and its RMS at least 0.001 FS; then `20*log10(second_half_amplitude / first_half_amplitude)` must be at least 6 dB.

The clean left difference is 0.000335693359375 and right difference is 0.001190185546875 FS/sample, yielding mismatch 0.0008544921875. No runner or source change was made by this scout. The existing 120 Hz `layer_slope_probe` is a different fixture and does not establish a slope-only negative for this 180 Hz layer.

As a calculation only, adding 0.0004 FS to frame 96001 before PCM16 encoding corresponds to about 13 integer counts (13/32767 = 0.00039674 FS). If quantized that way, it would leave the join gap unchanged and raise the local side-slope mismatch to about 0.0012512 FS/sample, over the existing .001 bound. This is a candidate-construction hypothesis, **not** a measured artifact or a demonstrated sole-failure result; other gates, including the generic centroid band, must still be checked by the executor/runner.

## Commands and limits

No shell commands were run, so there are no shell exit codes or new receipts from this scout. I read the existing builder/measurement source and round-15 LOG, and inspected the existing normal receipt named above. These are deterministic original synthetic PCM fixtures and threshold checks only. They do not establish audible detectability, musical quality, engine behavior, security, external compatibility, or production suitability.
