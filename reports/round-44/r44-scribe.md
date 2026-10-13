# R44 scribe — duration tolerance decision table

## Scope

This is a numerical fixture-calibration table only. It does not assess audio by audition, quality, production, rights, engine behavior, publishing, or promotion. I wrote only this report. The R44 LOG declaration requires the ordinary per-file UI duration predicate `abs(ffprobe_duration - 0.12) > .001`; it is distinct from the `.020 s` pairwise distinctness check. The integrated R44 opt-in gate result is **pending**: available evidence is scratch/helper measurement, not an end-to-end mode receipt.

## Evidence table

| Scratch fixture | Frames / nominal excess | Measured ffprobe duration | Parsed delta from 0.12 s | Scratch ordinary UI gate | Integrated R44 mode gate |
|---|---:|---:|---:|---|---|
| `executor/pass-5807.wav` | 5807 / +47 frames | 0.120979 s | +0.0009790000000000076 s | Pass; no `measure()` failures reported | Pending |
| `executor/fail-5809.wav` | 5809 / +49 frames | 0.121021 s | +0.001021000000000008 s | Numeric failed fit: sole `duration: outside ±1 ms` reported by executor | Pending; must show exit 1 and sole duration failure |

The deltas above are from the ffprobe decimal strings parsed as Python floats, not ideal frame-time arithmetic. Under the current strict `> .001` predicate, the reported values imply pass/fail respectively. The executor's scratch measurements also report both files as mono `pcm_s16le`, 16-bit/48 kHz, peaks about 0.27948 FS, RMS about −16.43 dBFS, and centroids inside the UI's 250–4000 Hz band; these do not identify a competing gate. The integrated runner still needs to demonstrate both declared opt-in modes and their full receipts. No comparator change is proposed.

## Exact commands and setup-vs-fit status

I ran these exact commands against the executor scratch files:

```sh
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 .shokhunin/audio/corpus/live/round-44/executor/pass-5807.wav
# exit 0; output: 0.120979
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 .shokhunin/audio/corpus/live/round-44/executor/fail-5809.wav
# exit 0; output: 0.121021
```

These are successful measurement/setup commands, not gate runs. `r44-scout.md` records one malformed, quoted-as-a-single-executable ffprobe attempt (exit 127) followed by a corrected canonical-UI command (exit 0); that 127 is a **setup error**, not a numeric failed fit and not evidence about either candidate. `r44-executor.md` reports its helper invocation exited 0 while returning the 5809 fixture's expected numeric duration failure; the process exit does not turn that fit into a pass. No integrated R44 mode command/result is available in the reports inspected here, so neither integrated gate is claimed as passed or failed.

## Limits / decision

This pair supports only the measured outcomes for these two files and this ffprobe path. The 5808-frame boundary is not tested by this pair: the critic's measured ffprobe string was `0.121000`, and Python float subtraction gives `0.0010000000000000009`, which is greater than `.001`; do not claim equality passes. Final acceptance remains pending independent integrated replay, with 5807 required to pass and 5809 required to fail only the ordinary duration gate. No inference beyond numerical fixture calibration.
