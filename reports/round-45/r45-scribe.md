# Round 45 scribe — signed duration decision table

Scope: numerical fixture calibration only. This is an independent review of the available `round-45/alt` scratch fixtures, not an author-integrated runner receipt or fresh replay. The declared target is 0.120000 s, tolerance 0.001 s, with strict failure when `abs(duration - target) > 0.001`.

## Decision table

| Frames / intended side | SHA-256 | ffprobe duration (s) | Signed `duration - 0.12` (s) | Absolute delta (s) | Measured gate result | Status |
|---:|---|---:|---:|---:|---|---|
| 5713 / inside | `745bb3dffb2cce371765e9abbe45613266a1e32c9489fe7af5c6dcda15c01620` | 0.119021 | -0.0009789999999999938 | 0.0009789999999999938 | No failures; duration passes | Numeric fit passes; integrated gate pending |
| 5711 / outside | `e23080bce71c97780b0760f413926decf9925fa76e9c11bdf39ea7be39e4818e` | 0.118979 | -0.0010209999999999941 | 0.0010209999999999941 | Sole failure: `duration: outside ±1 ms` | Numeric fit fails as intended; integrated gate pending |

Both scratch files measured as 48 kHz, mono, PCM s16le, 16-bit. Both had peak 0.269439697265625 (<.95), RMS -16.374928267066153 / -16.375168252396996 dBFS (above the .001 FS lower bound), and centroid 1388.963153267418 / 1375.7265323144181 Hz (inside the UI band). Thus the 5711 outcome is an isolated numeric duration failure in this independent measurement, not a format/setup failure. Reported signed deltas are computed from the actual ffprobe-decoded six-decimal durations; ideal frame arithmetic is not substituted. No assertion is made about the 5712-frame point or exact tolerance equality.

## Commands and exits

1. `for f in .shokunin/audio/corpus/live/round-45/alt/alt-ui-5713.wav .shokunin/audio/corpus/live/round-45/alt/alt-ui-5711.wav; do printf "%s " "$f"; ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$f"; done` — exit 0; outputs `0.119021` and `0.118979` respectively.
2. `for f in .shokunin/audio/corpus/live/round-45/alt/alt-ui-5713.wav .shokunin/audio/corpus/live/round-45/alt/alt-ui-5711.wav; do printf "FILE=%s\n" "$f"; ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,duration -show_entries format=duration -of json "$f"; done` — exit 0; confirms both stream formats and same durations.
3. `python3 .shokunin/audio/corpus/live/round-45/alt/measure_alt.py` — exit 0; emits the two measurements summarized above, including no failures for 5713 and only duration failure for 5711.
4. `sha256sum ".shokunin/audio/corpus/live/round-45/alt/alt-ui-5713.wav"` — exit 0; hash as table.
5. `sha256sum ".shokunin/audio/corpus/live/round-45/alt/alt-ui-5711.wav"` — exit 0; hash as table.

No setup errors occurred in these checks. They are distinct from the 5711 numeric failed fit: ffprobe and the measurement helper both ran successfully. The author runner integration and required non-author replay are not evidenced here, so final gate/replay status remains pending. No audition, quality, production, rights, engine, publishing, or promotion inference is made.
