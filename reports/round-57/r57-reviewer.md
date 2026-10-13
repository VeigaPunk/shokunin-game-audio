# R57 reviewer — valid-bits 15/16 opt-in wiring proposal

## Scope and evidence

Read `/tmp/mission-audio-standing.md`, the R57 declaration in `.shokunin/audio/LOG.md`, R56 source (`corpus/fixtures/build_artifacts.py`, `corpus/fixtures/measure_audio.py`) and R56 reviewer/executor/critic/adjudicator reports. This is a source-only review. I made no edits to shared source, LOG, SCORECARD, canonical artifacts, or other reports; ran no commands, built no fixtures, and produced no measurement receipt. Therefore this review has **no command exit codes, observed ffprobe metadata, SoX decode result, UI metrics, or hashes**. R57 executor scratch files, if present, are not integrated runner/decode evidence and are not cited as such.

R56 precedent adds a narrow fixture builder and two mutually exclusive opt-in flags, measures the selected artifact using unchanged `SPECS["ui"]`, and leaves canonical fixture/family comparisons alone. Its reviewer proposal is useful wiring precedent, not evidence for R57. Current `measure_audio.py` `format_failures()` checks ffprobe `codec_name == "pcm_s16le"` and `bits_per_sample == 16`; it does not inspect `wValidBitsPerSample`. `measure()` invokes ffprobe then SoX before constructing the measurement result. A failure in either decode command can therefore occur before the normal runner writes its receipt.

## Minimal conditional proposal

Only integrate the pair if the executor has first established that **both** constructed files are valid RIFF/fmt40/cbSize22 extensible headers with PCM subtype GUID, mono/48 kHz, 16-bit container, mask `0x4`, and the intended `wValidBitsPerSample` values 15 and 16, and that ffprobe and SoX actually decode both. The on-disk header parse, ffprobe metadata, SoX command exit, sample counts, and decoded-vector comparison are separate evidence; do not infer valid bits from `sample_fmt` or container `bits_per_sample`.

- Add one focused builder function and two builder options for the R57 pair, writing original fixtures only under `corpus/live/round-57/` (not canonical artifacts). Preserve the common signed16 source payload and every declared header field except valid bits. Do not overwrite earlier round files.
- Declare `--probe-ui-extensible-valid15` and `--probe-ui-extensible-valid16` (or equivalent clearly distinct names) in `measure_audio.py`; include both in the existing one-probe-mode guard and forward only the selected builder option. Add a single supplemental measurement branch for the selected R57 file using unchanged `SPECS["ui"]`. Use unique run suffixes/receipt mode labels; keep these modes out of canonical, family, section, and `_alt` comparisons. Leave `format_failures()`, UI thresholds, and all previous modes unchanged.
- First run and report the standalone ffprobe and SoX checks for each file. Only then run each integrated flag. If valid15 is rejected before a measurement receipt, record the exact failed command and exit as a **receiptless decoder/setup/unsupported outcome**, not as an observed runner format-failure receipt or numeric gate failure. If a runner invocation yields no receipt, do not count it as a replay receipt. If both decode and create receipts, report their actual metadata and metrics and any decoded-vector difference; do not assume equality or polarity from construction. Confirm the valid16 control is clean. Keep prior72/canonical17 and the existing gates unchanged.

No specific R57 command was executed in this review, so there are no exact commands/exits or observed metadata/metrics to report here. Commands, exits, receipts (or absence of receipts), and measured values belong in executor/integrated-run/verifier reports after they are actually observed.

## Limits

This proposal tests only these two specified mono extensible PCM-subtype fixtures in the local ffprobe/SoX/project-measurer path. It cannot establish general valid-bit handling, arbitrary valid/container-bit combinations, standards conformance, other decoders/codecs/layouts, fidelity, audibility/quality, production suitability, rights, engine behavior, publishing, or promotion. No commit or push was made.
