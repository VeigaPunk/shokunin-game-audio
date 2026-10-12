# Round 15 executor — 180 Hz layer slope candidate

## Result
Built original synthetic PCM scratch `corpus/live/round-15/slope180_candidate.wav` from canonical `corpus/artifacts/stem_layer_alt.wav` (SHA-256 `74926bf517298fa241e9960099aca60a728a54c41d9454876366dfe4d90adaa9`). Candidate SHA-256: `b1678716839c2fada2a46f6771039c758500ac5621e9e874122930177cf4ac57`. It is mono PCM16, 48,000 Hz, 192,000 frames (4 seconds). Only frame 96001 changed: canonical PCM count 39 to scratch count 52, via `round(.0004*32767)=13` count increment. No canonical/artifact or source edits.

## Reproduction recipe
Python 3 / NumPy recipe: read source WAV frames as little-endian signed 16-bit; copy the array; set `frames[96001] = frames[96001] + round(.0004 * 32767)`; write copied PCM with `wave` as mono, 16-bit, 48,000 Hz to `corpus/live/round-15/slope180_candidate.wav`. This is a one-frame synthetic alteration to the generated 180 Hz layer, not an external recording.

## Gate evidence
Decoded with the existing `sox <wav> -t f32 -e floating-point -` path and analyzed using existing functions in `measure_audio.py` (`measure` with 4 s / 100–2000 Hz spec and `section_contrast(path,180)`). Generic measurement: duration 4.000000 s; rate 48000; mono; peak 0.04998779297 FS; RMS −31.66727731 dBFS; integrated −32.7 LUFS (tool reading only); centroid 303.717795 Hz (inside 100–2000); bandwidth 1227.024948 Hz; no generic failures. The candidate is original fixture PCM; these are deterministic proxy measurements only.

At frames 95998–96001 decoded FS: `[-0.000701904296875, -0.0003662109375, 0, 0.0015869140625]`. Midpoint adjacent-sample gap = `0.0003662109375` FS (<= existing .03 bound). Side-slope mismatch = `0.001251220703125` FS/sample (> existing .001 bound). 180 Hz half amplitudes = `[0.01499992158, 0.04999787182]` FS; RMS values `[0.01060654968, 0.03535383527]`; contrast `10.457250606 dB` (valid, >=6 dB). The section helper reports contrast pass; the side-slope bound is the sole expected failing gate when integrated into the existing runner. Generic format/duration/level/centroid pass. No new gate or threshold.

## Commands / exits
- `ffprobe -v error -show_entries stream=sample_rate,channels:format=duration -of json .shokunin/audio/corpus/live/round-15/slope180_candidate.wav` — exit 0; 48000 Hz, mono, 4.000000 s.
- `sox .shokunin/audio/corpus/live/round-15/slope180_candidate.wav -t f32 -e floating-point /tmp/r15candidate.f32` — exit 0.
- `ffmpeg -hide_banner -nostats -i .shokunin/audio/corpus/live/round-15/slope180_candidate.wav -filter_complex ebur128=peak=true -f null - >/tmp/r15ff.out 2>/tmp/r15ff.err` — exit 0.
- `python3 -c 'import importlib.util,json,pathlib; s=importlib.util.spec_from_file_location("m",".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); p=pathlib.Path(".shokunin/audio/corpus/live/round-15/slope180_candidate.wav").resolve(); x=m.measure("slope180_candidate",(4.0,100,2000,False),p); sec=m.section_contrast(p,180); print(json.dumps({"measurement":x,"section":sec},indent=2))'` — exit 0; full JSON summarized above. This is direct candidate measurement, not a claim that the unmodified runner accepts a round-15 flag (no such source wiring was changed).
- Parent’s existing `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-layer-alt-join` — exit 1, receipt `corpus/live/runs/20261012T184326198826Z-layer-alt-join/measurements.json`; unrelated prior-mode smoke check, expected sole join failure.
- `git status --short -- .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/corpus/fixtures/measure_audio.py .shokunin/audio/corpus/artifacts` — exit 0, no output (these paths unchanged).

No failed alternate fit was attempted; I do not claim one. The sole-failure statement is gate arithmetic against existing thresholds pending parent wiring and independent runner replay. It is not an audible, engine, security, compatibility, or production claim.
