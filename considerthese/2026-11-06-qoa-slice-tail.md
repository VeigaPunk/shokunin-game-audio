# Encoded padding is not additional audio

[QOA's reference specification](https://github.com/phoboslab/qoa/blob/master/qoa.h), inspected November2026 with exact file identity retained, describes lossy sixteen-bit audio. The current WAV-import note leaves codec-induced measurement changes unresolved; reading this format does not close that gap.

Each slice encodes twenty samples. The final slice remains eight bytes even when fewer samples are used; unused positions are zeroed. Frame headers declare sample counts. Therefore storage length alone is not a decoded-duration contract, and padding should not silently become part of a measured seam.

The format also distinguishes known-length files from streaming headers. Streaming can change sample rate and channel count between frames, whereas static files cannot. The inspected reference implementation explicitly handles only known-total files. Format expressiveness is not implementation support.

This refines an existing QOA lead rather than proposing a superior codec. The README warns that the implementation has not been fuzzed and should not receive untrusted input. MIT terms require copyright and permission notices for substantial reuse. Original commentary only; no encoder, decoder, sample or benchmark was run or redistributed.
