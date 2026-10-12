# Round 6 corrupt-header probe (r6-corrupt)

Created `.shokunin/audio/corpus/live/round-6/corrupt.wav` from scratch as a 16-byte invalid RIFF/WAVE prefix; no borrowed sample or existing WAV bytes. Exact file bytes (hex): `524946460000000057415645666d7420` (`RIFF`, zero RIFF size, `WAVE`, then incomplete `fmt ` chunk). SHA-256: `564867d8781dc7f4f43e66543e9db6631f464c90087e3cf87a04040f2e83217c`.

Commands and outcomes (run from repository root):

- `ffprobe -v error -show_format -show_streams .shokunin/audio/corpus/live/round-6/corrupt.wav` — exit **1**; stderr: `.shokunin/audio/corpus/live/round-6/corrupt.wav: Invalid data found when processing input`
- `sox .shokunin/audio/corpus/live/round-6/corrupt.wav -n stat` — exit **2**; stderr: `sox FAIL formats: can't open input file '.shokunin/audio/corpus/live/round-6/corrupt.wav': fmt chunk not found`

This establishes only that these installed command-line parsers reject this particular malformed header. It does not test the integrated measurement runner or establish general malformed-WAV handling/security; that is for integration and independent verification.
