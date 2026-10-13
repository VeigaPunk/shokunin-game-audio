# R41 reviewer — minimal outer side-slope probes

## Scope and review

The R41 LOG declaration targets the existing outer loop side-slope comparator in `measure_audio.py`: `abs((last - penultimate) - (second - first)) > .001`. It is distinct from R21's internal section join and R40's first/last endpoint delta. Keep the comparator, ordinary thresholds, canonical WAVs, and existing outer endpoint modes unchanged.

A minimal implementation is two opt-in flags, `--probe-outer-slope-32` and `--probe-outer-slope-33`, routed through the existing source-generation path. Each mode should generate its own deterministic scratch WAV under `corpus/live/round-41/` (not an artifact/canonical path), then measure it with the existing ambience spec `(2, 5, 200, True)`. Reuse the ordinary measure path and JSON receipt; do not add a generic probe framework or tune the comparator.

## Fixture construction constraints

Generate 96,000 signed PCM16 mono samples at 48 kHz (2 seconds). Use a deterministic low-frequency, non-silent base signal with centroid in 5–200 Hz and peak below .95. Set the four outer samples deliberately before encoding so that the *decoded* side-slope difference is exactly 32 counts for the pass fixture and 33 counts for the fail fixture. In PCM16 full-scale units these are respectively `32/32768 = 0.0009765625` and `33/32768 = 0.001007080078125`. Ensure decoded first-to-last endpoint delta is <= .03 for both. Write PCM16 WAV directly (or otherwise control PCM quantization); after writing, decode/measure the actual WAV and assert the intended counts and ordinary checks. Do not infer exact counts from pre-quantized float values.

The 32 mode should have no failures and exit 0. The 33 mode should have only `loop seam: slope mismatch > .001 full scale per sample` and exit 1. Both should pass format, duration, level, centroid, and endpoint checks. Give the WAVs distinct SHA-256 hashes; report the actual hashes and measurement receipt paths. The ordinary source/build path must continue to regenerate the canonical assets exactly as before.

## Evidence and limitations

A useful receipt reports decoded sample count/format, endpoint delta, side-slope mismatch, centroid, failures, and the scratch WAV hash. Separately record a numeric failed fit (for example an out-of-band centroid or an endpoint failure) versus a shell/helper/path setup error; neither counts as a successful isolated probe. Do not describe 32/33 as testing equality at .001: .001 is 32.768 PCM16 counts. This is numerical fixture calibration only, not an audible smoothness/seam, sound-quality, production, rights, engine, publish, or promotion finding.

## Commands run

None. This is a source/spec review only; no shell commands were run and there are no exit codes, generated WAVs, decoded counts, hashes, or fit results to report.
