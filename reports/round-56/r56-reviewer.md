# R56 reviewer — extensible PCM16 channel-mask probe wiring

## Scope and evidence

Source-only review of `/tmp/mission-audio-standing.md`, the R56 declaration in `.shokunin/audio/LOG.md`, R55 source in `corpus/fixtures/build_artifacts.py` and `measure_audio.py`, and R55 source/reports including `r55-reviewer.md`, executor, critic, simplifier, and adjudicator. I made no source edits and ran no build, syntax, probe, measurement, or replay command. Thus there are no command exit codes, receipts, observed metadata, hashes, decoded-vector comparisons, or measured metrics in this review.

The current source has R55 `--probe-ui-extensible-pcm16` / `--probe-ui-standard-pcm16-r55` plumbing. Its builder writes a tag-1 control and a WAVE_FORMAT_EXTENSIBLE PCM16 file with a hard-coded mono channel mask `0x4`; the runner measures the selected R55 file with unchanged `SPECS["ui"]`. There is no R56 mask-zero/mask-center mode or builder routing yet. R55 reports establish useful precedent for that specific mask-4 example only; the R56 zero-mask acceptance and equal decode remain unobserved until integrated and run.

## Minimal source-only recommendation

- **Builder:** add only `--probe-ui-extensible-mask-zero` and `--probe-ui-extensible-mask-center`, and route either to one narrow R56 builder. Write two original mono 48 kHz, 5,760-frame PCM16 WAVE_FORMAT_EXTENSIBLE WAVs under `corpus/live/round-56/`, both using the same signed16 data bytes and the already-established PCM subtype GUID, valid bits 16, 40-byte `fmt `, and consistent RIFF sizes. Set only channel mask to `0x0` for zero and `0x4` for center. Do not overwrite R55 files or alter the R55 builder.
- **Runner:** declare both options; include both in the existing one-probe-mode guard and builder-forwarding arguments. Add one supplementary `measure(name, SPECS["ui"], path)` branch for the chosen R56 file. Give the two modes, receipt names, and run-directory suffixes distinct labels. Keep these probes out of canonical fixtures, family/`_alt`/section comparison lists, and normal-mode behavior.
- Keep `format_failures()`, `SPECS["ui"]`, thresholds, and all pre-existing probes unchanged. After integration, verify the actual RIFF fields (especially mask and GUID), separately run both flags, inspect ffprobe metadata and UI receipt failures/metrics, and compare SoX-f32 vectors. Check both flags together are rejected by the existing mutual-exclusion guard before builder/receipt side effects. These are verification recommendations, not results from this review; report the actual commands and exits in the execution/verifier reports.

## Limits

This proposed pair isolates only the specified valid-16-bit mono PCM-subtype extensible headers with masks `0x0` and `0x4`, using the local ffprobe/SoX/project-measurer environment. It cannot establish behavior for other masks, layouts, channel counts, GUIDs, valid/container-bit combinations, decoder versions, or general extensible WAV support. It implies nothing about fidelity, audibility, quality, production, rights, engine integration, publishing, or promotion. No shared source, LOG, SCORECARD, canonical artifact, or other report was changed; no commit or push was made.
