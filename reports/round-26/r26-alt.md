# r26-alt — independent duplicate-pair challenge

## Result

The existing pair signal does catch an exact duplicate under `alt/`: I wrote two original, same-content 0.12 s, 48 kHz mono PCM16 WAVs, `ui_clone.wav` and `ui_clone_alt.wav`. Both individually pass the existing `ui` numeric/format checks. Their SHA-256 hashes are identical (`225a6f6c5d3921cf0d1fe5b60227a1c0e3d6a34dfb95ead5a74e9d4f613aed43`). Direct `measure()` contrast gives duration delta 0.0 s and relative centroid delta 0.0; existing `duration_delta >= .020 OR relative_centroid_delta >= .10` returns false, thus the variant has the sole applicable distinctness failure. This supports the narrow exact-duplicate negative, not the boundary behavior or general deduplication.

## Confounds and limits

The equal file hashes establish sample-for-sample identity, not an auditory judgment. Both pass the `ui` spec (duration .12 s within tolerance; format 48kHz/mono/PCM16; level and 250–4000 Hz centroid checks pass). This does not demonstrate a perceptual distinction for any of the five existing `_alt` pairs, nor test duration/centroid threshold edges. Since the gate is an OR, a duplicate with duration difference ≥20 ms would pass regardless of centroid; this is consistent with the declared rule but limits what it excludes. No runner integration or canonical files were modified or tested here. No engine, rights, publication, or promotion claim.

## Exact shell commands and exits

- `cd /home/vgpnk/Projects/prymeagnt/audio && python3 .shokunin/audio/corpus/live/round-26/alt/check_pair.py` — exit 1 on first attempt: test helper passed relative paths, and `measure()` rejected `relative_to(ROOT)`. I corrected the helper to resolve paths; this was a harness-path issue, not a measured negative.
- `cd /home/vgpnk/Projects/prymeagnt/audio && python3 .shokunin/audio/corpus/live/round-26/alt/check_pair.py` — exit 0; both failure arrays empty, duration delta 0, centroid delta 0, distinctness false.
- `cd /home/vgpnk/Projects/prymeagnt/audio && sha256sum .shokunin/audio/corpus/live/round-26/alt/ui_clone.wav .shokunin/audio/corpus/live/round-26/alt/ui_clone_alt.wav && ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-26/alt/ui_clone.wav && ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-26/alt/ui_clone_alt.wav` — exit 0; matching hash and both report 0.120000 s, 48000 Hz, mono, pcm_s16le, 16-bit.
