# Round 3 slope scout: measurement and join semantics

## Scope and method

I inspected `corpus/fixtures/measure_audio.py`, `corpus/fixtures/build_artifacts.py`, the round-2 critic/verifier reports, and decoded the three raw WAV fixtures named by the round-3 claim (`ambience`, `ambience_alt`, `stem`). No source, fixture, canonical artifact, or shared decision file was changed. I did not run a shell command and made no listening or perceptual-quality claim.

## Current measurement path

`measure_audio.py`'s `measure(name, spec)` gets the artifact path from `ARTIFACTS`, reads rate/channels/duration via `ffprobe`, and decodes its PCM through `sox ... -t f32 -e floating-point -`. It converts that mono sample sequence to float64. For loop specs (`spec[3]`), the only current join-specific observation is:

```python
seam_delta = float(abs(samples[0] - samples[-1]))
...
if spec[3] and seam_delta > .03:
    failures.append("loop seam: endpoint jump > .03 full scale")
```

The JSON receipt includes `seam_endpoint_delta_full_scale`; the threshold is also recorded as `loop_endpoint_delta_max: 0.03`. The three loop specs are `ambience`, `ambience_alt`, and `stem`. No slope/adjacent-difference field or condition currently exists. This is an endpoint-amplitude comparison only; it says nothing about the neighboring trajectory or playback behavior.

## Sample-index semantics for the proposed companion metric

For decoded sequence `x[0] ... x[N-1]`, incoming interior difference is `d_in = x[N-1] - x[N-2]`; outgoing interior difference is `d_out = x[1] - x[0]`. Comparing these signed, same-direction first differences (e.g. `abs(d_out - d_in)`) tests whether the local discrete change approaching the end resembles the local discrete change leaving the beginning. This is distinct from comparing `x[0]` and `x[N-1]`, and should be reported separately in full-scale sample units per sample. Do not reverse the sign of the incoming difference: both differences describe increasing sample index through the periodic join. If an implementation instead measures the single cross-boundary step, that is `x[0] - x[N-1]` and duplicates the existing endpoint comparison, not the proposed slope-comparison proxy.

I decoded PCM16 fixtures to normalized sample values (`int16 / 32768`) to verify these index interpretations. For the periodic sine fixtures, the signed incoming/outgoing differences have the same sign and are nearly equal. The proposal is a local proxy over one adjacent interval at each side; it is not a continuous derivative estimate, and its raw magnitude depends on sample rate and local waveform frequency/amplitude. Keep the endpoint check as its own guard.

## Independent direct decoded-fixture observations

These values come from the current clean raw PCM files, decoded as little-endian signed 16-bit mono and divided by 32768 (48 kHz, 96,000 samples each). `mismatch` is `abs(d_out - d_in)`:

| Fixture | Endpoint `abs(x[0]-x[-1])` | `d_in = x[-1]-x[-2]` | `d_out = x[1]-x[0]` | Mismatch |
|---|---:|---:|---:|---:|
| ambience | 0.000671387 | 0.000640869 | 0.000671387 | 0.000030518 |
| ambience_alt | 0.001892090 | 0.001892090 | 0.001892090 | 0 |
| stem | 0.011383057 | 0.011352539 | 0.011383057 | 0.000030518 |

All observed endpoint deltas are below the existing 0.03 bound. The clean mismatch maximum in this decode is `3.0518e-5` full-scale/sample. This is a three-fixture observation, not a recommended or universal threshold; whether to add quantization margin is for the metric/calibration lane. No control artifact was used in this measurement.

## Limit

A first-difference mismatch is one numerical local-join diagnostic. It does not establish audible seamlessness, phase continuity, decoded codec/runtime behavior, or mastering quality. No shell command was run; shell command/exit-code evidence is therefore not applicable.
