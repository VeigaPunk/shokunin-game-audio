# Round 4 motif-energy proxy scout

## Proposed observable

Use a **decoded-PCM 440 Hz component amplitude** as the named component (the fundamental is a convenient fixture label, not a claim about musical role). Decode the generated mono PCM16 WAV to floating-point samples at 48 kHz, then analyze the half-open sections `[0, 96000)` and `[96000, 192000)` (exactly 0–2 s and 2–4 s). For each section of length N=96,000, compute `X = rfft(x)` and the normalized sinusoidal peak amplitude `A = 2*abs(X[880])/N`. Bin 880 is exactly 440 Hz because bin spacing is 0.5 Hz. This is a coherent, rectangular-window projection: 440 Hz completes 880 cycles in each section, so no windowing or leakage correction is needed if the generated component is exactly 440 Hz and section lengths/rate remain as specified. Report each A and `20*log10(A_larger/A_smaller)`; equivalently this is 10 log10 of the component power ratio. Require contrast >=6.0 dB. State which section is higher.

This measures one component's relative section energy from decoded PCM, not a generic spectral centroid, full-section RMS, correlation, or perceived motif. Since a fixed-frequency sinusoid's projected power is proportional to A²/2, the amplitude-ratio dB calculation is the component-energy contrast. The exact bin/frequency and section indexing make the result independently reproducible.

## Avoiding silence / invalid ratios

Before taking the ratio, require both projected amplitudes finite and above an explicitly reported floor. A conservative fixture-local floor such as `A >= 0.01 full scale` (about -40 dBFS peak amplitude) avoids an effectively silent denominator; report the two values and floor. Also require both section-wide RMS values above the existing 0.001 full-scale near-silence guard. Reject the metric as invalid if either section fails either floor; do not clamp the denominator, substitute epsilon, or count silence-versus-signal as a valid >=6 dB pass. The 0.01 floor is a proposed operational floor, not a calibrated hearing threshold. Parent/verifier should confirm it is below both authored section amplitudes and state this in the receipt.

## Negative control and interpretation

A useful flattened-section control preserves the candidate's other components and exact duration but replaces the 440 Hz component amplitude in both sections with one common amplitude (e.g. the arithmetic mean of the candidate's two section amplitudes), retaining phase continuity. It should have valid above-floor projections but <6 dB contrast and therefore fail only the section-contrast criterion. Verify it from the decoded control WAV, not merely from its synthesis parameters. Keep it separate from the canonical fixture. A control that zeros the component is weaker: it could be rejected by the silence floor rather than demonstrate the contrast threshold.

For a positive candidate, check the two measured amplitudes, >=6 dB contrast, per-section non-silence/finiteness, plus the already specified overall format, level, spectrum, duration and loop endpoint/slope guards. If the loop check is applied to the new four-second WAV, measure its decoded sample endpoints and adjacent differences just as for existing loops. Do not infer that a two-section energy change creates an audible, recognizable, or musically successful motif; it only establishes the declared numerical section variation.

## Caveats

The exact-bin method is intentionally narrow: a detuned or time-varying component spreads energy across bins and can be undercounted. Do not silently broaden to a band or choose a bin post hoc; if the fixture needs detuning, predeclare a fixed sinusoidal least-squares projection or fixed band and document it. A 6 dB threshold is the round's local analytic target, not a general musicality or perceptual threshold. The section cut is at an exact two seconds; report that boundary explicitly.
