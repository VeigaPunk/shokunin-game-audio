# Round 8 flat120 control — executor report

## Construction

Created the original scratch file `.shokunin/audio/corpus/live/round-8/flat120_candidate.wav`; it is not a production/canonical asset. It is 4.000 s of mono, uncompressed PCM16 at 48,000 Hz (192,000 frames), with a continuous 120 Hz sine at constant amplitude 0.036 full scale in both 2 s sections. The samples were generated analytically as `round(0.036 * sin(2*pi*120*n/48000) * 32767)` and stored little-endian signed 16-bit. No borrowed samples or perceptual/engine/security claims.

SHA-256: `bfc71f84f6d9bae0f5e9b1d786d10bc7becd2e766b406fe5583cfd5fcf0af1bd`

## Original PCM measurements

- WAV metadata: 1 channel; 2 bytes/sample; 48,000 Hz; 192,000 frames; 4.0 s; `NONE` compression.
- Quantized decoded peak: 0.0360107422 FS; RMS: 0.0254538726 FS (about -31.88 dBFS).
- Per-half 120 Hz component amplitude, measured as `2*abs(rfft(half)[240])/len(half)` on each 96,000-sample section: 0.0359972097 FS and 0.0359972097 FS.
- Section contrast `20*log10(second/first)`: 0.000 dB. This is the expected flat-control value, below the declared 6 dB section-contrast criterion.
- Whole-file positive-frequency weighted spectral centroid: 149.209 Hz.
- Endpoint absolute difference: 0.000579834 FS; endpoint slope mismatch: 0.000030518 FS/sample.

This documents the control's construction and numeric result only; it does not assert parent integration or a public probe result.

## Commands / exits

No shell commands were run; therefore there are no shell exit codes to report. File generation and measurements were performed with Python's `wave`, NumPy, and `hashlib` in the session REPL.
