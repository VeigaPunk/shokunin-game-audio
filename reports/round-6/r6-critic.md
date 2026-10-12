# Round 6 critic — malformed-file claim scope

## Scope and evidence

I read the declared round-6 claim and wave specification in `.shokunin/audio/LOG.md`, plus `corpus/fixtures/measure_audio.py` and `corpus/fixtures/build_artifacts.py`. This is a source-level challenge, not execution of malformed probes. I did not generate, borrow, or listen to any samples; I make no security or perceptual claim. No shell commands were run.

## Challenge: define the failure boundary narrowly

The claim should mean that the specifically named, locally generated invalid fixtures produce a persisted JSON receipt with an explicit expected validation failure and nonzero process exit, without a traceback. It should not mean that all malformed WAVs, all decoder failures, or arbitrary exceptions are converted into validation receipts.

There are materially different cases:

- **Structured, anticipated validation failures:** a file decodes and yields inspectable metadata/samples, but violates an explicit fixture rule such as sample rate/channel count or exact section sample count. These can be classified as `format` or `section count` only when the relevant metadata/count is actually available and checked before indexing/FFT work. Wrong rate or channel is a format mismatch; it does not, by itself, demonstrate a decoder error.
- **Expected tool/decode rejection for a deliberately corrupt fixture:** `ffprobe`/SoX may return nonzero or produce unusable metadata/output. A narrowly scoped handler can turn a known probe/decode failure for this named probe into a `decode` failure record. That is evidence about this fixture and these tool versions/commands, not comprehensive malformed-WAV handling.
- **Unexpected failures:** programming errors, missing executables, permission/path errors, malformed assumptions in unrelated code, JSON serialization errors, and other arbitrary exceptions are not automatically invalid-file outcomes. Catching `Exception` globally and labeling every result `decode` would mask regressions and overstate robustness. These should remain visible as unexpected errors; only known subprocess/parse failure points and anticipated validation conditions should be mapped deliberately.

Current implementation exposes the risk: `command(..., check=True)` raises on nonzero tool exit; `ffprobe` JSON/stream indexing and `sox` decoding happen before the format rule is appended; and `section_contrast()` splits and reads FFT bin 60 before checking `len(samples) == 192000`. Thus a thrown exception is not equivalent to a structured validation failure. A mere traceback-free exit is also insufficient: the required receipt must exist, name the probe, and contain the relevant explicit failure category. Conversely, a structured `format` failure on a decodable wrong-rate/stereo file does not prove corrupt-file decode handling.

## Fixture-local bounds and falsifiable evidence

- Keep the malformed cases bounded to the named generated fixtures and stated checks (short section-count case, corrupt-header decode case, wrong-rate/channel format case). Do not generalize from three examples to every truncation position, WAV encoding, sample rate/channel arrangement, decoder, or hostile input.
- The existing thresholds remain local fixture rules, not universal format/security limits. A short decoded sample count can be reported as an expected section-count validation failure; it does not establish that all truncated files are handled. A corrupt header that the installed tools reject can establish only that this particular tool failure is recorded as intended.
- For each case, distinguish fixture construction from runner outcome: cite the exact probe path, command and exit, receipt path, and the exact failure list/category. Verify absence of a traceback separately from receipt presence. For a multi-failure wrong-format file, report all observed failures; do not claim isolation unless it has only the intended failure.
- Normal-fixture hash preservation and old-probe behavior are guard evidence, not malformed-file evidence. A clean restoration run should be separately identified.

**Critic conclusion:** The declared bounded claim is falsifiable if parent integration handles only expected malformed-probe/tool failure paths, emits receipt records for those named cases, and leaves unrelated exceptions visible. Do not phrase the result as “robust malformed WAV handling,” “all invalid WAVs safely rejected,” decoder security, or production validation. The source review alone establishes no pass; independent replay and exact receipts remain required.
