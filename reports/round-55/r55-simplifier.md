# R55 simplifier — keep the WAV pair local

## Recommendation

Use the existing paired-probe shape, narrowly: one helper writes the two declared WAV files under `corpus/live/round-55/`; add the two opt-in flags, wire them through the existing single-probe guard and builder call, and add one supplemental `measure("ui", SPECS["ui"], path)` per selected file with distinct mode/output labels. Keep both outside canonical fixture generation, family/section comparisons, and historical probes.

The pair needs only two encodings of the same 5,760 signed PCM16 sample values: conventional PCM tag 1 with a 16-byte `fmt` chunk, and WAVE_FORMAT_EXTENSIBLE with a 40-byte `fmt` chunk, valid bits 16, mono front-center mask `0x4`, and PCM subtype GUID. Reuse the already-declared ordinary UI-shaped PCM16 stream; avoid a generic WAV writer/reader abstraction, conversion framework, or broader refactor. Do not change `format_failures()`, `SPECS["ui"]`, thresholds, or existing probes. Check actual ffprobe fields and project measurements on both outputs; do not treat the expected success as observed until measured.

## Basis and evidence limits

I read `/tmp/mission-audio-standing.md`, the R55 declaration in `.shokunin/audio/LOG.md`, and R54 integration/verifier/simplifier reports. The R55 declaration is specifically a positive container-header representation control, not a sample-width contrast. R54's narrow paired-probe wiring and unchanged UI measurer are sufficient precedent; no generic abstraction is needed for these two cases.

No R55 source integration, build, ffprobe, decode, measurement, or runner command was performed for this simplifier report. Thus there are no command exit codes, hashes, observed metadata, vector comparisons, or metrics to report. The expected metadata (`pcm_s16le`, 16 bits, 48 kHz mono, `.120 s`), equal decoded samples, and two clean runner exits remain unverified here. If observed behavior differs, record the actual result; do not modify predicates or thresholds to force the declaration.

This recommendation covers only the specified pair. It makes no universal WAVE_FORMAT_EXTENSIBLE, compatibility, fidelity, audible-quality, production, rights, engine, or publishing claim. No shared source, LOG, SCORECARD, canonical artifact, or other report was changed; no commit or push was made.
