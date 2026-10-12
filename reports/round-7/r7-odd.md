# Round 7 odd-length scratch probe

Created `corpus/live/round-7/odd_sections.wav` as a valid mono PCM16 WAV at 48,000 Hz with exactly 101 frames (202 data bytes). Samples are deterministic: for frame index `i` in `0..100`, PCM sample is `round(0.2 * 32767 * sin(2*pi*180*i/48000))`, encoded little-endian signed 16-bit.

- SHA-256: `81c7ba97bfc8f68a9ad48403a6b102bf4d5f573963f5d8f74a9697bd09aa72d8`
- Header verification: `wave.open` reports `(frames=101, channels=1, sample_width=2, rate=48000)`.
- Purpose: valid odd-length input for the dependent before-state `section_contrast()` probe; this report does not claim the old exception or new receipt outcome.
- Creation/verification used Python `wave`, `struct`, `math`, and `hashlib`; no shared fixture builder or canonical WAV was modified.
