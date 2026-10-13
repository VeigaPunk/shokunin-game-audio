# R52 simplifier review

## Recommendation
Keep this as one matched fixture pair, not a new abstraction. Reuse the existing `measure_audio.py` UI spec and `format_failures()` unchanged. The only intended difference is container sample width: construct one 5760-sample signed integer vector `s16`, then write PCM16 from `s16` and PCM8 from `round(s16 / 256) + 128` (clamped to `[0,255]`). For this construction, PCM8 decoding should equal PCM16 decoding on the SoX-f32 path; verify the vectors rather than claim equality without measurement.

Use the existing WAV writer (`wave` module) with `setnchannels(1)`, `setframerate(48000)`, and `setsampwidth(1 or 2)`. This is sufficient; no ffmpeg conversion, resampler, codec registry, generic bit-depth matrix, custom validation framework, or edits to canonical fixture generation are needed. Keep two explicit opt-in modes for the PCM8 and PCM16 side of the pair (consistent with the prior round's paired controls); do not add a new spec or modify acceptance logic. Emit the usual runner receipt and report the relevant pair measurements from it.

## Checks from source inspection
- `corpus/fixtures/measure_audio.py` already reads `codec_name` and `bits_per_sample` via ffprobe, decodes the whole file through SoX to f32, computes duration/peak/RMS/centroid, and applies `SPECS["ui"]`.
- `format_failures()` already rejects anything other than mono 48000Hz PCM16 with the exact existing `format: expected PCM16` result. PCM8 should naturally hit this existing predicate; no width-specific failure string or second source of truth is warranted.
- UI non-format bounds are already centralized: `.12s`, centroid 250–4000Hz, plus existing duration, peak and RMS rules. The pair builder should not duplicate them.
- The selected PCM8 relation is a deliberately constructed quantization-grid match; it does not support general PCM8 conversion or quality/fidelity conclusions.

No commands or measurements were run by this review; these are source-level simplification recommendations only. No source, LOG, scorecard, corpus, or other report was edited.
