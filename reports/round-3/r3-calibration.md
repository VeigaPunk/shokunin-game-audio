# Round 3 calibration critique (critic)

## Scope and independent clean-loop measurements

I challenge the slope-gap limit as a local numerical fixture rule, not as an audibility criterion. I independently decoded all three clean loop WAVs through SoX to float PCM and computed `abs((x[-1]-x[-2]) - (x[1]-x[0]))` without relying on a proposed threshold. The checked inputs were `ambience.wav`, `ambience_alt.wav`, and `stem.wav` under `corpus/artifacts/` (all 48 kHz, 96,000 decoded samples). Results:

| fixture | endpoint delta (FS) | first difference (FS/sample) | last difference (FS/sample) | absolute slope gap (FS/sample) | peak (FS) |
|---|---:|---:|---:|---:|---:|
| ambience | 0.000671387 | 0.000671387 | 0.000640869 | 0.000030518 | 0.174591 |
| ambience_alt | 0.001892090 | 0.001892090 | 0.001892090 | 0 | 0.199738 |
| stem | 0.011383057 | 0.011383057 | 0.011352539 | 0.000030518 | 0.323792 |

Exact shell command: `python3 -c 'import subprocess, numpy as np; from pathlib import Path; root=Path(".shokunin/audio/corpus/artifacts");
for n in ("ambience","ambience_alt","stem"):
 p=root/(n+".wav"); x=np.frombuffer(subprocess.run(["sox",str(p),"-t","f32","-e","floating-point","-"],check=True,capture_output=True).stdout,dtype="<f4").astype(float); a=x[1]-x[0]; b=x[-1]-x[-2]; print(n,"n",len(x),"first_slope",a,"last_slope",b,"abs_slope_gap",abs(a-b),"endpoint_delta",abs(x[-1]-x[0]),"max_abs_sample",max(abs(x)),"first_3",x[:3].tolist(),"last_3",x[-3:].tolist())'`; exit code **0**.

## Threshold challenge

The measured clean range is [0, 3.0518e-5] FS/sample. A strict zero threshold false-fails two clean fixtures. A limit equal to the observed maximum, or only infinitesimally above it, is brittle: PCM16 quantization and a small benign regeneration change can flip the decision. A defensible local bound needs explicit headroom over 3.0518e-5 and should be recorded as fixture-specific, not generalized to other sample rates, encodings, levels, or source material. If parent chooses a much larger bound (for example 0.01 FS/sample), it easily passes these clean fixtures, but allows a real slope mismatch up to that magnitude to pass; whether that is acceptable depends on the required positive control, not on hearing claims.

Amplitude and frequency matter. These are decoded PCM16 fixtures at 48 kHz; `measure_audio.py` bounds peak below 0.95 FS and requires RMS above 0.001, but the clean loop peaks here are only 0.175–0.324 FS. A fixed absolute slope limit is level-dependent: scaling a waveform down makes its mismatch easier to pass, while scaling it up makes the same relative shape mismatch more likely to fail. The loop centroid bands (ambience 5–200 Hz; stem 100–2000 Hz) are broad spectral-centroid checks, not hard frequency cutoffs or limits on every component. First difference is likewise frequency-dependent: for a sinusoid its magnitude scales with `2 sin(pi*f/48000)`, so the same amplitude discontinuity at higher frequency produces a larger per-sample difference. No one absolute bound therefore transfers across level/frequency/sample-rate domains.

## False decisions and recommendation

- **False fail:** a strict zero or near-maximum bound can reject the existing clean PCM16 loops due to endpoint quantization; any threshold near the measured ceiling lacks margin. A bound can also reject an otherwise valid higher-level/higher-frequency loop if treated as universal.
- **False pass:** any threshold greater than a constructed probe's slope gap will accept that discontinuity. A small threshold can still miss a high-frequency/low-level or attenuated mismatch. This metric checks only two local first differences, not a long join window, periodicity, waveform identity, playback behavior, or audibility.
- **Calibration prerequisite:** publish the exact numeric limit, compare the raw decoded values, and show that all three clean loops pass while an equal-endpoint probe with a gap strictly above the limit fails. Also retain the endpoint-amplitude check and existing normal/broken-amplitude controls. Do not call this a perceptual threshold.

This report has no probe measurement: the probe artifact was not present when I ran these checks. The independent clean distribution above is evidence for challenging the bound, not evidence that the probe works or that the integrated code passes.
