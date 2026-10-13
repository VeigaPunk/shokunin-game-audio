# R44 reviewer: minimal duration-probe modes

## Scope

I read the R44 declaration in `.shokunin/audio/LOG.md`. The requested move is narrowly to expose two opt-in scratch runner modes, each with its own declared UI duration target `.12 s`, while leaving ordinary behavior, the comparator, and canonical fixtures unchanged. This review is numerical fixture calibration only. I did not edit source, LOG, SCORECARD, canonical artifacts, or any other report.

## Evidence and verdict

The proposed 5807/5809-frame pair brackets the existing strict ordinary duration check at this observed ffprobe output precision. It is appropriate for two minimal opt-in modes if each mode declares the same `.12 s` target in its own runner spec and the failure mode is asserted to be solely `duration: outside ±1 ms`. The controls should be ordinary UI-shaped signals whose measured format, peak/RMS, and centroid stay within existing checks; do not alter the comparator or normal/canonical path.

I independently ran ffprobe on the executor's scratch pair. Exact commands and exits:

```text
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-44/executor/pass-5807.wav
# exit 0; format.duration = "0.120979"
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-44/executor/fail-5809.wav
# exit 0; format.duration = "0.121021"
```

Against the declared `.12 s` UI target, parsed deltas are respectively `0.0009790000000000076 s` and `0.001021000000000008 s`. Thus, under the runner's `abs(duration - spec[0]) > .001` test, the first is inside and the second outside. Ideal frame-time deltas are `47/48000 = 0.0009791666666666666 s` and `49/48000 = 0.0010208333333333334 s`; the runner actually evaluates ffprobe's rounded duration string and floating-point subtraction. The distinctness-duration check's `.020 s` threshold is a different predicate and is not what these probes test.

The executor WAVs are scratch inputs, not integrated mode receipts. I did not run the ordinary runner: at review time its `SPECS` had no two R44 mode entries/flags, so there was no R44 runner mode to invoke. This is an unavailable-test/setup limitation, not a numeric runner failure. My two ffprobe commands succeeded; there were no setup errors and no integrated numeric failed fits observed. Do not report these ffprobe-only checks as proof of end-to-end runner outcomes. Before integration is accepted, verify each mode's own target and full receipt, including that the 5809 case has only the duration failure.

Do not claim anything about exact `.001 s` equality or 5808 frames: ffprobe rounds duration and the strict float comparison can classify that boundary as outside. This pair establishes only the measured outcomes of these two fixtures with this tool/output path, not universal behavior across versions or formats.

No audition, quality, production, rights, engine, publishing, or promotion inference is made.
