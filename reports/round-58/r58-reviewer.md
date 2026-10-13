# R58 reviewer — valid-bits 14/16 opt-in wiring proposal

## Scope and evidence status

Read `/tmp/mission-audio-standing.md`, the R58 declaration in `.shokunin/audio/LOG.md`, current `corpus/fixtures/build_artifacts.py` and `measure_audio.py`, and the R57 reviewer/executor/alternate reports. This is a **source-only proposal**. No fixture was generated or decoded, and no integrated runner command was executed. Accordingly, this report has no observed R58 command exit codes, header parse, ffprobe metadata, SoX sample count/vector comparison, UI metrics, receipt, or hash. The presence of an executor generator script is not measurement evidence. Do not treat the R57 measurements as R58 observations.

The current project measurement path obtains ffprobe metadata, decodes via SoX to float32, then measures and applies unchanged UI gates. `format_failures()` checks 48 kHz mono and `pcm_s16le`/16 bits; it does not inspect `wValidBitsPerSample`. A thrown ffprobe/SoX command can prevent a normal receipt. Existing R57 wiring is the closest pattern: dedicated opt-in modes and a supplemental `measure("ui", SPECS["ui"], path)` result without changing gates or canonical comparisons.

## Minimal conditional integration

Only add the two R58 modes after the executor has actually demonstrated for **both** original fixtures: valid RIFF/fmt40/cbSize22 extensible headers; mono/48 kHz, PCM subtype GUID, mask `0x4`, 16-bit container; shared payload with all signed samples divisible by four; valid bits 14 and 16 respectively; and successful ffprobe and SoX decoding. Record those observations separately. Verify that only the declared valid-bit header field differs. `sample_fmt` and `bits_per_sample` do not report the valid-bit field.

If these conditions hold, the minimal source change is:

- Add unique build flags for the 14/16 fixtures in `build_artifacts.py`; write only to `corpus/live/round-58/`, preserve the shared 14-bit-left-aligned payload, and keep canonical artifacts untouched.
- Add opt-in flags `--probe-ui-extensible-valid-14` and `--probe-ui-extensible-valid-16` to `measure_audio.py`; include them in the existing one-probe-mode guard and forward only the selected builder flag.
- Add one supplemental branch per selected flag to measure its round-58 WAV with the existing `SPECS["ui"]`, producing distinct mode/path receipts. Do not add either mode to canonical, family, section, or `_alt` comparisons.
- Leave `format_failures()`, UI thresholds, all prior modes, and canonical fixture inputs unchanged.

Before integration/replay, report standalone header parsing, ffprobe, and SoX results for both fixtures. Then run each integrated flag. Report actual metadata, sample counts and decoded-vector equality/difference, plus receipt metrics and exit status. If either decoder rejects a file before a receipt, preserve the exact command and exit as a receiptless decoder/setup/unsupported outcome—not a runner format failure, numeric gate failure, or replay receipt. If no receipt is created, do not count that invocation toward a replay count. Do not assume equal decoding from identical payload construction; do not force a 76-receipt replay unless both modes produce receipts.

## Commands and observed results

No R58 build, inspection, ffprobe, SoX, project-measurement, or runner command was executed for this source-only review. Thus there are no exact executed commands or exit codes and no observed R58 header values, metadata, metrics, hashes, decoder outcome, or receipt to report. Once run, retain the exact commands and exits in executor/integrated-run/verifier evidence; report header values from a direct RIFF parse, not from ffprobe. R57 commands/results provide precedent only and are not substitutes.

## Limits

Even a clean result would establish only the specified matched extensible PCM-subtype mono fixtures and this local ffprobe/SoX/project path. It would not establish valid-bit metadata enforcement, general 14-bit fidelity, arbitrary valid/container-bit combinations, standards conformance, decoder portability, audible quality, production suitability, rights, engine behavior, publishing, or promotion. No shared source, LOG, SCORECARD, canonical artifact, or other report was changed; no commit or push was made.
