# Round 3 slope probe — author recipe and raw metrics

## Artifact

- Path: `.shokunin/audio/corpus/live/round-3/slope_probe.wav` (scratch positive control; no canonical WAV modified).
- Format: mono, signed PCM16, 48,000 Hz, 48,000 frames (1.000 s), little-endian WAV; 96,044 bytes.
- SHA-256: `91b4a324124ef8a54b0dc25eea584f3e08f1451090e1413b15d7325ec8bde99f`.

## Reproducible recipe

Generated from scratch in Python with NumPy and the standard-library `wave` module. Set `fs=48000`, `n=fs`; for integer indices `i=0..47999`, form `x[i] = 0.30*sin(2*pi*220*i/fs)` in float64. Override `x[0]=0.0`, `x[1]=0.45`, `x[-2]=0.02`, `x[-1]=0.0`. Clip to [-1,1], multiply by 32767, round with `numpy.rint`, cast to little-endian signed int16, and write one channel at 48 kHz. This deliberately sets equal endpoint samples while forcing a large mismatch between the two boundary-adjacent first differences. No input audio or borrowed samples were used.

## Raw decoded metrics

Decoded the written PCM16 samples as little-endian int16 and divided by 32768. Values below are normalized sample units, computed from the decoded file, not the pre-quantized array:

- First sample `x[0]`: 0.000000000
- Second sample `x[1]`: 0.449981689
- Penultimate sample `x[-2]`: 0.019989014
- Last sample `x[-1]`: 0.000000000
- Absolute endpoint delta `abs(x[-1]-x[0])`: 0.000000000 (within the stated 0.03 amplitude limit)
- Start-side difference `x[1]-x[0]`: +0.449981689
- End-side difference `x[-1]-x[-2]`: -0.019989014
- Absolute slope-difference proxy: `abs((x[-1]-x[-2])-(x[1]-x[0]))` = 0.469970703

This is a constructed numerical positive control for equal endpoints with mismatched neighboring slopes. It does not establish an audible threshold or perceptual loop quality. No shell commands were run.
