# Round 5 threshold inventory

Scope: source-level inventory of enforced decisions in `corpus/fixtures/measure_audio.py`. This is not a calibration verdict; source pointers use 1-based line numbers in that file.

## Enforced checks

| Check | Threshold / boundary polarity | Applicability | Source |
|---|---|---|---|
| Format | Sample rate **exactly 48,000 Hz** and channels **exactly 1**; reject if either differs. | Every measured fixture and added probe, via `measure`. | `measure_audio.py:61-62`; receipt states rate at `:134`. |
| Duration | Expected duration per fixture with absolute error **at most 0.001 s**; reject only when `abs(actual-expected) > .001` (inclusive boundary passes). | All names, expected durations listed below. | `:15-26` (`SPECS`), `:63-64`; tolerance in receipt `:134`. |
| Peak | Absolute sample peak must be **strictly below 0.95 FS**; `peak >= .95` fails. | Every measured fixture/probe. | `:48`, `:65-66`; receipt key `peak_max_exclusive` at `:135`. |
| RMS floor | RMS must be **at least 0.001 FS**; `rms < .001` fails (boundary passes). | Every measured fixture/probe. | `:49`, `:65-66`; receipt key `rms_min_exclusive` at `:135` (key name says exclusive, implementation is inclusive at equality). |
| Spectral centroid | Inclusive fixture-specific band `[low, high]` Hz; values outside fail. | Every named fixture/probe, using that measurement's spec. | Bands `:16-25`; centroid computation `:38-42`; gate `:67-68`; receipt map `:146`. |
| Loop endpoint jump | Absolute last-to-first decoded sample difference must be **<= 0.03 FS**; `> .03` fails. | Only specs whose final tuple element is `True`: ambience, ambience_alt, stem, stem_sections; and slope probe spec. | Loop flags `:22-25`, probe spec `:107`; metric `:50`, gate `:69-70`; receipt `:137`. |
| Loop slope mismatch | Absolute difference between the final and initial adjacent-sample differences must be **<= 0.001 FS/sample**; `> .001` fails. | Same loop specs as endpoint check. | Metric `:51`, gate `:71-72`; receipt `:138`. |
| SFX variant duration distinctness | For each `_alt`, absolute duration delta from its base must be **>= 0.020 s OR** centroid relative delta must be >= 0.10; fail only if both are below their limits. | `ui_alt`, `impact_alt`, `movement_alt`, `ambience_alt`. | Pairing and calculation `:115-120`; predicate/failure `:121-125`; receipt `:140-141`. |
| SFX variant centroid distinctness | Relative absolute centroid difference `abs(variant-base)/base` must be **>= 10% OR** duration condition above passes. | Same four `_alt` variants. | `:120-125`; receipt `:141`. |
| Section sample count | Exactly **192,000 decoded samples** (4 s at 48 kHz); otherwise section result invalid. | `stem_sections` always; `flat30_probe` only in `--probe-flat` mode. | `section_contrast`: `:85-89`; dispatch `:127-130`. |
| Section component amplitude floor | Both sections' measured 30 Hz amplitudes must each be **>= 0.01 FS**; otherwise invalid. | Same section-check cases. | FFT amplitude at `:87`; validity predicate `:88`; receipt `:142`. |
| Section RMS floor | Both sections' RMS must each be **>= 0.001 FS**; otherwise invalid. | Same section-check cases. | `:88`; receipt `:143`. |
| Section contrast | For a valid signal, signed `20*log10(A_second/A_first)` must be **>= 6.0 dB**; equality passes. A decrease is negative and fails; this is not absolute contrast. Invalid inputs also fail. | Same section-check cases. | `:89-92`; gate attaches failure `:130`; receipt `:139`. |

### Fixture-specific expected duration and centroid bands

All durations use the ±1 ms rule above. The band endpoints pass (`low <= centroid <= high`).

| Fixture | Expected seconds | Centroid band (Hz) | Loop checks? | Source |
|---|---:|---:|:---:|---|
| ui | 0.12 | 250–4,000 | no | `:16` |
| ui_alt | 0.16 | 250–4,000 | no | `:17` |
| impact | 0.32 | 50–15,000 | no | `:18` |
| impact_alt | 0.32 | 50–15,000 | no | `:19` |
| movement | 0.24 | 100–16,000 | no | `:20` |
| movement_alt | 0.36 | 100–16,000 | no | `:21` |
| ambience | 2.0 | 5–200 | yes | `:22` |
| ambience_alt | 2.0 | 5–200 | yes | `:23` |
| stem | 2.0 | 100–2,000 | yes | `:24` |
| stem_sections | 4.0 | 100–2,000 | yes | `:25` |

Probe modes: `--probe-failing` rebuilds the existing failing fixture; `--probe-slope` additionally measures the round-3 slope probe using spec `(1.0, 5, 24000, True)` (`:103-109`); `--probe-flat` additionally measures flat30 against `stem_sections` spec (`:105-110`, `:127-130`). At most one mode can be chosen (`:99-101`). Normal mode rebuilds and measures the ten named artifacts (`:102-106`, `:111-114`).

## Measured fields that are not acceptance thresholds

- `integrated_lufs` is reported if finite and above the ebur128 **-70 LUFS gated floor**; `<= -70` or non-finite values are converted to null (`:52-59`). This is a reporting filter, not a loudness pass/fail check. No LUFS window is enforced.
- `spectral_bandwidth_hz` is computed/reported (`:43-44`) but never gates acceptance.
- RMS is calculated in FS and emitted as `rms_dbfs` (`:49`, `:74-76`); the minimum gate is the linear 0.001 FS floor, not a dBFS interval.
- `section_contrast` checks only the fixed 30 Hz component, extracted from FFT bin 60 of each half (`:85-89`); no other section/frequency or general musicality test is enforced.
- The section output calls the quantity `section_energy_delta_db`; implementation derives it from amplitude ratio using `20 log10`, equivalently an energy ratio in dB. It is signed, not absolute.

## Coverage note

`SPECS` supplies the centroid band and loop flag per fixture; there is no independently enforced global centroid range. Distinctness and section checks are additional gates outside `measure`'s basic format/duration/level/centroid/loop checks. No shell commands were needed for this source inventory.
