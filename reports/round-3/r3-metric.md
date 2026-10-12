# Round 3 slope-metric report

Role: `r3-metric` (executor). Scope: derive and measure a fixture-local decoded-PCM loop-join slope proxy. I changed no shared script or fixture.

## Proposed metric and bound

For decoded mono samples `x[0..N-1]` in full-scale units, retain the existing endpoint check `abs(x[N-1] - x[0]) <= 0.03`. Add the absolute first-difference mismatch

`S = abs((x[N-1] - x[N-2]) - (x[1] - x[0]))`.

Proposed local pass bound: `S <= 0.001` full-scale per sample. This is an absolute difference, not a relative ratio: near-zero slopes do not make the metric unstable. It compares the two one-sample increments adjacent to the loop boundary; it does not establish derivative continuity between rendered playback blocks or perceptual seamlessness.

## Clean distribution

I decoded the three existing loop WAVs to float32 PCM using SoX, then promoted the decoded samples to float64 for arithmetic. The clean `S` distribution was: min `0`, max `3.0517578125e-05`, median `3.0517578125e-05` full-scale/sample. Per fixture:

| Fixture | First difference | Last difference | `S` | Endpoint delta | Proposed bound |
|---|---:|---:|---:|---:|---|
| ambience | 0.00067138671875 | 0.000640869140625 | 0.000030517578125 | 0.00067138671875 | pass |
| ambience_alt | 0.00189208984375 | 0.00189208984375 | 0 | 0.00189208984375 | pass |
| stem | 0.011383056640625 | 0.0113525390625 | 0.000030517578125 | 0.011383056640625 | pass |

The proposed bound is 32.8 times the maximum observed clean mismatch (about 30.1 dB of amplitude margin), while remaining far below the constructed control mismatch. This is a calibration choice for these PCM16 fixtures only, not a general audio threshold.

## Constructed control

The existing `corpus/live/round-3/slope_probe.wav` decodes to 48,000 mono samples. Its endpoint delta is `0`; first difference is `0.449981689453125`, last difference is `-0.019989013671875`, and `S = 0.469970703125`. Thus it passes the existing endpoint bound but exceeds the proposed slope bound by about 470 times. This confirms the metric distinguishes an equal-endpoint, slope-discontinuous control from the three clean fixtures. I did not run or modify the integrated measurement script; positive-control construction/verification and regression execution belong to their assigned lanes.

## Reproduction

From repository root, command:

```sh
python3 - <<'PY'
import subprocess, numpy as np
from pathlib import Path
root=Path('.shokunin/audio/corpus')
for n in ('ambience','ambience_alt','stem'):
 p=root/'artifacts'/f'{n}.wav'
 raw=subprocess.run(['sox',str(p),'-t','f32','-e','floating-point','-'],check=True,capture_output=True).stdout
 x=np.frombuffer(raw,dtype='<f4').astype(np.float64)
 first=x[1]-x[0]; last=x[-1]-x[-2]
 print(f'{n}: samples={len(x)} first_diff={first:.12g} last_diff={last:.12g} slope_delta={abs(last-first):.12g} endpoint_delta={abs(x[-1]-x[0]):.12g}')
PY
```

Exit **0**. Output:

```text
ambience: samples=96000 first_diff=0.00067138671875 last_diff=0.000640869140625 slope_delta=3.0517578125e-05 endpoint_delta=0.00067138671875
ambience_alt: samples=96000 first_diff=0.00189208984375 last_diff=0.00189208984375 slope_delta=0 endpoint_delta=0.00189208984375
stem: samples=96000 first_diff=0.0113830566406 last_diff=0.0113525390625 slope_delta=3.0517578125e-05 endpoint_delta=0.0113830566406
```

The analogous decode-and-measure command on `corpus/live/round-3/slope_probe.wav` exited **0** and printed `samples 48000 endpoint_delta 0.0 first_diff 0.449981689453125 last_diff -0.019989013671875 slope_delta 0.469970703125`.

**Recommendation:** use `S <= 0.001` as a second, fixture-local numerical guard while retaining the endpoint guard. Existing coverage, baseline hashes, and integrated regression behavior remain unverified by this report.
