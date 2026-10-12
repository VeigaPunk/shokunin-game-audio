# Round 6 simplifier — minimal `--probe-invalid` path

## Recommendation

Keep the existing builder, `measure()`/`section_contrast()` checks, and timestamped `measurements.json` receipt. Add one opt-in invalid-probe path to the existing runner; do not create a parallel validator, receipt format, or generic exception-swallowing wrapper. Preserve the normal build/measure path byte-for-byte where practical.

1. Add `--probe-invalid` to the runner and builder. In that mode the builder writes only the two original probe inputs beneath `live/round-6/` (one short, valid PCM16 mono WAV for the section-count case and one corrupt-header WAV). Do not alter canonical fixtures. Keep scratch generation deterministic.
2. Run each probe through the existing measure logic in an explicit probe loop. Add a small stage-aware wrapper for expected tool failures only: catch `subprocess.CalledProcessError` around ffprobe/sox/ffmpeg calls and return a probe result with a stable `failure_kind` (`format` for ffprobe stream metadata/unsupported rate-or-channel, `decode` for sox decode failure). Include a concise diagnostic, not a traceback. Do not catch `Exception` or convert arbitrary programming bugs into input failures.
3. In `section_contrast()`, check `len(samples) == 192000` *before* splitting/indexing. For a mismatch, return the existing result shape with `valid: false`, `passed: false`, and a specific `failure_kind: "section count"`; use empty component arrays (or omit them consistently) rather than attempting FFTs. This is the narrow fix for the identified pre-check indexing path. Keep all existing numerical thresholds unchanged.
4. Add these probe results to the existing receipt under an `invalid_probes` key (or as named measurements with explicit `failure_kind`), write it through the existing timestamped receipt writer, print its path, and return nonzero when any expected invalid probe is not rejected with its expected category. A malformed-input probe is successful as a *probe* only when it produces the expected structured failure; do not count that expected rejection as a clean fixture failure. Keep existing normal and legacy probe modes unchanged.

## Why this is the smallest fit

The current runner already owns subprocess invocation, receipt construction, and exit status; the builder already owns deterministic WAV synthesis. This change composes those pieces. The only new behavior is explicit invalid scratch creation, narrow expected-tool-error conversion at the probe boundary, and a precondition before section splitting. It avoids a broad `try/except`, duplicate schema/framework, new threshold, or modifying `measure()` semantics for ordinary clean files.

## Limits / validation

Before-state source inspection only; I ran no shell commands and created no WAVs. The current `command(..., check=True)` raises on nonzero ffprobe/sox/ffmpeg exits, so invalid files currently can abort before the receipt is written. `section_contrast()` splits/indexes before its exact sample-count check, which is too late for some malformed lengths. This proposal does not establish behavior for every corrupt WAV, codec security, or arbitrary subprocess failure. A non-author must exercise both invalid probes plus normal and legacy controls, verify ten canonical hashes, and confirm the failure categories and unchanged thresholds before claiming the round's depth improvement.
