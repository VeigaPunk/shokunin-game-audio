# Round 8 layer candidate (executor)

- Candidate: `corpus/live/round-8/stem_layer_candidate.wav` (relative to `.shokunin/audio/`).
- Original analytic PCM: for sample index `n=0..191999`, `t=n/48000`, `x[n]=A(t)*sin(2*pi*120*t)`, where `A(t)=0.012` for `0 <= t < 2` and `A(t)=0.060` for `2 <= t < 4`. Quantization is `round(clip(x,-1,1)*32767)` to little-endian signed PCM16. One mono channel, 48000 Hz, 192000 frames (4.000 s); sections are 96000 frames each.
- SHA-256: `ca7825f4f93f67facc3c7d0ea5bf96bb3061f2354bf4d692dc03a9944fb075c9`.
- Independent section-local Hann-window FFT at 120 Hz measured 120.0 Hz and amplitudes 0.0119996 / 0.0599977 FS (~13.98 dB contrast); RMS 0.008485 / 0.042425 FS.
- No shell commands were run. Candidate generation, metadata inspection, hashing and measurements used Python in the REPL.
- Numeric fixture candidate only, not a production stem or claim of audible quality/adaptive game behavior. The boundary amplitude step at 2 s is intentional; no transition-smoothness claim.
