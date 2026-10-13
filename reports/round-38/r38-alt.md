# R38 alt — independent numeric fit

## Scope
Fit one original 2.0 s looping pair in `.shokunin/audio/corpus/live/round-38/alt/` using the project measurement helper. This is numerical control only; no audition, quality, production, rights, engine, publishing, or promotion claim.

## Method and setup
Generated mono 48 kHz PCM16 sine loops at 0.22 full-scale amplitude, with 96,000 samples per file. Tested the candidates with `measure_audio.measure(..., (2.0, 5, 200, True), path)` from `.shokunin/audio/corpus/fixtures/measure_audio.py`, which runs ffprobe/SoX/FFmpeg and computes the project centroid and seam metrics. A first helper call using a relative path raised `ValueError` at the helper’s `relative_to(ROOT)` receipt-path conversion; this was a path/setup issue, not a failed fit. Re-running with resolved absolute scratch paths worked. No shell commands were run, so there are no shell command/exit receipts to report.

## Selected measured pair
- Baseline: 65 Hz source, duration 2.0 s, centroid **91.03372963007341 Hz**.
- Variant: 75 Hz source, duration 2.0 s, centroid **81.62439856673954 Hz**.
- Absolute duration delta: **0.0 s**.
- Baseline-relative centroid delta: **0.10336093117979261** (strictly > .10 and < .13).
- Both independently measured ordinary/loop failure lists are empty. Baseline endpoint delta **0.001861572265625**, slope mismatch **0.000030517578125**; variant endpoint delta **0.002166748046875**, slope mismatch **0.0**. Both are within the project checks.
- SHA-256 baseline `04d8d334553ecb0c155a4be37397edda8f01cfbe992df4bd2e9b3e474d1189e0`; variant `7bd6ae805a6a5ff2c15ba14470ba1d312c40768c97c1704629382ed76292bd77`.

This fit shows only that this measured centroid proxy is above the existing numeric threshold at equal duration, with ordinary and seam checks passing. It does not establish an exact boundary, perceptual distinction, or audible seamlessness. No integrated opt-in runner outcome is claimed.
