# R56 simplifier — two mask modes, one local helper

## Recommendation

Keep the R56 probe to the existing paired-probe pattern. Add one narrowly named builder helper that makes the same 5,760 mono/48 kHz signed-PCM16 samples twice as WAVE_FORMAT_EXTENSIBLE: valid bits 16, PCM subtype GUID, `fmt` size 40, and channel masks `0x0` and `0x4`. The only pair difference should be the mask field. Write the two declared `round-56` files; do not add a generic WAV/header abstraction.

Expose exactly the two declared opt-in probe modes, dispatch both to that helper, and measure only the selected file with the existing `measure("ui", SPECS["ui"], path)` path. Reuse the existing single-probe guard and give modes/output directories distinct labels. Leave `format_failures()`, `SPECS["ui"]`, thresholds, canonical fixtures, historical probes, and all other runner behavior unchanged. Validate actual RIFF/fmt/GUID/mask bytes, ffprobe metadata, SoX-decoded equality, UI receipts, and each runner exit; do not infer the expected positive result from source alone.

## Basis and evidence limits

Read `/tmp/mission-audio-standing.md`, the R56 declaration in `.shokunin/audio/LOG.md`, R55 `build_artifacts.py` and `measure_audio.py`, and the R55 simplifier, reviewer, executor, and verifier reports. R55 already supplies the minimal precedent: one helper constructs a shared PCM16 payload in two headers, with two opt-in runner modes and unchanged UI measurement. R56 only needs the two extensible variants to differ at the mono channel-mask field (`0x0` vs `0x4`). No generic header framework or threshold change is warranted.

I made no source edits and ran no build, probe, decode, measurement, runner, or validation commands. Therefore there are no command exits, hashes, observed header/ffprobe metadata, decoded-vector comparisons, runner receipts, or measured metrics from this simplifier lane. The expected metadata (`pcm_s16le`, 16 bits, mono/48 kHz, `.120000` s), exact decoded equality, and clean exits remain unverified here; the parent/verifier must report actual outcomes. Any mask-0 rejection or other discrepancy should be recorded without changing predicates or thresholds.

This recommendation is bounded to these two specified mono PCM16 extensible headers. It establishes no general mask/layout, standards-conformance, decoder-compatibility, fidelity, audibility, quality, production, rights, engine, publishing, or promotion claim. Only this report path was written; no shared source, LOG, SCORECARD, canonical artifact, or other report was changed. No commit or push was made.
