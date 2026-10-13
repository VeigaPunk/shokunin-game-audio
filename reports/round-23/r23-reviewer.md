# Round 23 reviewer — comparator/receipt mapping

Independent source/receipt read for the declared calibration-disclosure move. No shell commands were run; therefore there are no shell exit codes. No code, thresholds, fixtures, or receipts were changed. This is a field-name and predicate audit, not a listening, engine, rights, or perceptual-validity claim.

## Evidence read

- Current `.shokunin/audio/corpus/fixtures/measure_audio.py` (source only; `measure`, `section_contrast`, receipt construction and invalid probe path).
- Round-22 non-author normal receipt `.shokunin/audio/corpus/live/runs/20261013T010825350561Z-normal/measurements.json` (`mode=normal`).
- Round-22 non-author negative receipt `.shokunin/audio/corpus/live/runs/20261013T010824568740Z-invalid/measurements.json` (`mode=probe-invalid`). Its corrupt case records ffprobe exit 1; the runner's overall probe-invalid exit is documented in the round-22 LOG as expected exit 1.
- The round-23 declaration in `.shokunin/audio/LOG.md`.

## Numeric predicates and receipt names

The normal receipt has root keys `mode`, `thresholds`, `measurements`, `distinctness`, and `sections`. The `thresholds` object is a summary; some values are parameters to per-record checks, and there are no separate “observed pass/fail threshold” fields. `measurements[*].failures` is the outcome list (empty means that record has no listed failures); `sections[*].passed` and `distinctness[*].passed` are their own outcomes. These details matter when drafting a table: use measurement keys below, not guessed aliases.

| Check in source | Acceptance comparator / polarity | Receipt threshold and observation fields | Disclosure caveat |
|---|---|---|---|
| Stream format | rate exactly 48000 and channels exactly 1; codec exactly `pcm_s16le` and `bits_per_sample` exactly 16. Any mismatch adds format failure. | Threshold `rate_hz`; per-record `sample_rate_hz`, `channels`, `codec_name`, `bits_per_sample`, `failures`. | ffprobe's reported encoded-width fields only; no `sample_fmt`/valid-bits check. |
| Duration | reject when `abs(duration - spec_duration) > .001`; equality at tolerance is accepted. | `duration_tolerance_s`; `duration_s`; `failures`. | The target is per-name `SPECS` duration (not a common duration). |
| Peak | reject `peak >= .95`; accepted peak is strictly `< .95`. | `peak_max_exclusive`; `peak_full_scale`; `failures`. | Peak is absolute sample maximum. |
| RMS | reject `rms < .001`; equality accepted. | `rms_min_exclusive` (name is potentially misleading: code uses `<`, so equality passes); `rms_dbfs`; `failures`. | Source compares linear RMS; receipt reports dBFS. A table must not compare `rms_dbfs` directly to `.001`. |
| Spectral centroid | reject if centroid `< low` or `> high`; both edges accepted. | `centroid_bands_hz` per fixture; `spectral_centroid_hz`; `failures`. | Bounds vary by `SPECS` name; bandwidth is reported but not an acceptance gate. |
| Loop endpoints | for loop specs, reject `seam_delta > .03`; equality accepted. | `loop_endpoint_delta_max`; `seam_endpoint_delta_full_scale`; `failures`. | Non-loop specs report null; not applicable, not a pass-margin measurement. |
| Loop side slopes | for loop specs, reject `slope_delta > .001`; equality accepted. | `loop_slope_delta_max_full_scale_per_sample`; `seam_slope_delta_full_scale_per_sample`; `failures`. | Non-loop specs report null. |
| Section input validity | must have exactly 192000 samples (two 96000-sample sections); amplitudes all finite and each `>= .01`; section RMS each `>= .001`. Otherwise `valid=false`, contrast null if invalid. | `sections[*].section_samples`, `actual_samples`, `component_amplitudes_full_scale`, `section_rms_full_scale`, `valid`; summary thresholds `section_component_amplitude_min_full_scale`, `section_rms_min_full_scale`. | The invalid-probe short/odd controls specifically demonstrate section-count rejection; they do not isolate every validity predicate. |
| Section contrast | valid pair passes when `delta_db >= 6.0`; fails below 6. | `section_contrast_min_db`; `component_amplitude_contrast_db`, `passed`. | Component frequency is in `component_hz` and selected per fixture/probe; amplitude is a bin amplitude, not RMS. |
| Internal join adjacent sample | for selected section-bearing names, reject when `join_delta > .03`; equality accepted. | `internal_join_adjacent_delta_max_full_scale`; `internal_join_adjacent_delta_full_scale`; `failures`. | Applied only to the explicit name set in source; not every section-bearing record (e.g. `stem_sections` omitted). |
| Internal join side slope | for selected names, reject when `join_slope > .001`; equality accepted. | `internal_join_side_slope_mismatch_max_full_scale_per_sample`; `internal_join_side_slope_mismatch_full_scale_per_sample`; `failures`. | The source name set differs subtly from adjacent-gap set: `join180_probe` is in gap set but not slope set. Do not say universally applied to all section-bearing records. |
| Variant distinctness | pass if duration delta `>= .020` **OR** relative centroid delta `>= .10`; fail only if both are below. | `distinctness_duration_delta_min_s`, `distinctness_centroid_relative_delta_min`; `distinctness[*].duration_delta_s`, `centroid_relative_delta`, `passed`. | Relative centroid denominator is base centroid. Five `_alt` records are the round-23 declaration's inventory; this comparator is an alternate-specific distinctness guard, not a measurement acceptance in `failures` until failure is appended to that alternate. |
| Integrated loudness | Not used for acceptance. | `integrated_lufs` (null if no usable finite result or at/below -70). | Do not describe LUFS as an acceptance threshold. |

## Negative receipt field-name cross-check

`invalid_probes` records use `probe`, `path`, `expected_failure`, `observed_failure`, `status`, with optional `sample_rate_hz`, `channels`, `codec_name`, `bits_per_sample`, `section`, or `detail`. `status` is `expected_pass`, `expected_failure`, or `unexpected_result`; it is not the normal receipt's `failures` list. In the round-22 raw receipt, `native16_probe` is `expected_pass`, `observed_failure=null`, 48000 Hz mono `pcm_s16le`/16; `native24_probe` is `expected_failure`, `observed_failure=format`, 48000 Hz mono `pcm_s24le`/24. The prior wrong-format negative is 44100 Hz stereo and PCM16, so it is confounded for format dimensions; short/odd controls target section count and corrupt targets ffprobe decode. These controls do not show every numeric bound in isolation.

No mismatch found between the named round-22 receipt keys and the current comparator source for PCM16/PCM24. Potential disclosure traps are comparator polarity/equality, linear-RMS-vs-dBFS, absent fields as null/not-applicable, and the distinct internal-join name sets. The round-22 normal receipt gives actual clean-file observations but is one fixture observation, not a general clean distribution; computing minima/margins is **not measured in this review**. No source-generated table or broad validity claim is verified here.
