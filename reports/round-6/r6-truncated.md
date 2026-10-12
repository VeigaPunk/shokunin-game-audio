# Round 6 truncated-section probe (r6-truncated)

## Artifact

Created `corpus/live/round-6/short_sections.wav` from original generated samples; it is not copied from a fixture or another probe. The file is a valid RIFF/WAVE PCM file with mono, 16-bit little-endian samples at 48,000 Hz, uncompressed (`NONE`). It contains **144,000 frames (3.0 s)**, whereas the section checker expects 192,000 total samples (two 96,000-sample sections). This forces a section-count mismatch while retaining a valid header and decodable audio.

Recipe: for frame index `i = 0..143999`, generate `int(0.2 * 32767 * sin(2*pi*180*i/48000))`, pack each value as signed little-endian 16-bit PCM, and write using Python's standard-library `wave` module with one channel, 2-byte sample width, and 48 kHz frame rate.

SHA-256: `61786e40b1eeca4557bb5b02b9ba4ab65231b46f50ae76702f1b1bdb9a1f3795`.

## Relevance and limits

In the before-state `section_contrast()` path, `sox` decodes samples, `np.split(samples, 2)` and FFT bin indexing happen before the exact `len(samples) == 192000` validity predicate. This probe supplies an even but short sample count, so the split and bin indexing can run and the eventual count predicate should mark it invalid. It is a focused section-count mismatch probe, not evidence that the integrated runner already has a structured invalid-input receipt or that odd-length/corrupt WAVs are handled.

No shell commands were run; generation and header/frame verification used Python standard-library code. Therefore there are no shell command exit codes to report. No fixture, shared source, receipt, or other shared artifact was edited.
