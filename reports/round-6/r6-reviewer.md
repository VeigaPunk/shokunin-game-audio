# Round 6 reviewer — narrow invalid-probe receipt proposal

## Scope

Static review only. I read the declared round-6 claim/spec and the current `corpus/fixtures/measure_audio.py` and `build_artifacts.py`. I did not run commands, create or listen to audio, change source, or make a security/perceptual claim. This is a proposal for the parent integration, not evidence that the claim passes.

## Suggested boundary

Keep the normal measurement path and existing `--probe-flat`, `--probe-slope`, and `--probe-failing` behavior as-is. Add a separate `--probe-invalid` route that processes only the explicitly named round-6 files, without running the normal builder or trying to include those files in the canonical `measurements` dict. A dedicated helper can produce a per-probe result; do not wrap `main()` or all of `measure()` in `except Exception`.

A useful small receipt shape is an `invalid_probes` list in the ordinary timestamped receipt, with one entry per expected file, e.g. `{probe, path, expected_failure, observed_failure, status, detail}`. `status` should be `expected_failure` only when the matching category was actually observed; otherwise mark `unexpected_result`/`unexpected_error` and make the command fail. Preserve exception class and a concise diagnostic in `detail` when useful. Keep stdout summary and exit status nonzero if any expected category is missing or any unexpected result occurs. Serialize and write the receipt after collecting the per-probe outcomes; receipt I/O/JSON errors themselves should remain visible rather than being renamed as input failures.

## Per-probe mapping

- **`wrong_format.wav`:** If ffprobe and decode succeed, inspect the reported rate/channel and emit `format` for the explicit mismatch. This is a normal validation result, not a decoder exception. Record both rate and channel and any other observed failure; only call it isolated if no other failure occurred.
- **`short_sections.wav`:** Decode it, then test `len(samples) != 192000` *before* `np.split`, FFT bin indexing, or RMS-on-halves. Emit `section count` with actual and required sample counts. This ordering is necessary because the current `section_contrast()` can raise in `np.split` or `rfft(...)[60]` before its existing `valid` check. Do not turn an arbitrary FFT/indexing exception into a section-count result.
- **`corrupt.wav`:** At the known ffprobe/SoX subprocess boundary for this named path only, a nonzero exit (`subprocess.CalledProcessError`) can be recorded as `decode` with command/stderr context. If ffprobe exits zero but its output is not JSON or lacks usable stream/format metadata, only map a specific JSON parse/required-metadata failure at that same corrupt-probe boundary to `decode`. Do not map `FileNotFoundError`, permission/path failures, builder failures, receipt-write errors, or arbitrary exceptions to `decode`; allow them to surface as unexpected errors. Do not treat an ffprobe/SoX success with usable data as a decode failure merely because the fixture is named corrupt.

A per-file `try` may be needed so one probe result does not prevent the other two entries, but constrain handlers to the specific expected operation and exception types above. In particular, catching `CalledProcessError` broadly around the whole run could mislabel builder or unrelated command failures. If a helper returns exception records, do not include raw exception objects in JSON; make the mapping explicit and serializable.

## Guard preservation and claim limits

The invalid mode should not mutate canonical artifacts or scratch from previous rounds. Leave the existing normal/control invocation path and thresholds untouched; independently compare the ten clean hashes and rerun the old flat/slope/amplitude controls as the declared verifier requires. A traceback-free nonzero exit without a persisted receipt and the expected category is not a pass. Evidence from these three named locally constructed inputs would support only their exact outcomes with the installed toolchain, not general handling of malformed WAVs, security, or production validation.
