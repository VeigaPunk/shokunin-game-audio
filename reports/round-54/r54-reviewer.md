# R54 reviewer — PCM32/PCM16 UI probe wiring

## Scope and evidence

Source-only review of the R54 declaration in `.shokunin/audio/LOG.md`, R53 closeout/context, and current `corpus/fixtures/build_artifacts.py` and `measure_audio.py`. I did not edit shared source, run builds, measurements, syntax checks, or probes. No command exit, receipt, ffprobe metadata, hash, decode comparison, or measured metric is claimed.

At review time the source contains R53 `--probe-ui-float32` / `--probe-ui-pcm16-r53` plumbing but no `--probe-ui-pcm32` or `--probe-ui-pcm16-r54` options, builder helper, extra measurement, mode, or output suffix. Thus the proposed R54 wiring is not yet present and cannot be confirmed as working. Existing runner design offers a narrow precedent: paired options are included in the one-probe-mode guard and builder forwarding; scratch measurements are added with `measure(name, SPECS["ui"], path)` after canonical measurements; receipt labels and run suffixes are explicit. R53 reviewer report describes that pattern, while R54 declaration specifies the PCM32-vs-PCM16 calibration claim.

## Minimal wiring review / recommendation

- Builder: add only `--probe-ui-pcm32` and `--probe-ui-pcm16-r54` parser options and a dispatch branch calling one helper that writes `corpus/live/round-54/pair_pcm32.wav` and `pair_pcm16.wav`. Use the declared 5,760 samples, mono 48 kHz signal, quantize once to signed16 `s16`, then construct signed32 as `s16.astype(int32) * 65536`; write signed little-endian PCM WAVs at 2 and 4 bytes/sample. The PCM32 multiplication is within signed32 range for every signed16 value. Do not change canonical fixtures or any older probe helper.
- Runner: declare both options, include both in the existing mutual-exclusion count and builder-forwarding arguments. Add only one supplementary UI measurement per selected option using unchanged `SPECS["ui"]`, named distinctly (e.g. `ui_depth_pcm32_r54_probe` / `ui_depth_pcm16_r54_probe`) and loaded from the R54 scratch paths. Add their mode strings and run-directory suffixes. Do not add them to family, `_alt`, or section comparison lists, and do not alter `format_failures()`, UI spec, thresholds, or canonical receipt comparisons.
- Verification after integration: invoke the flags separately; inspect ffprobe `codec_name`, bits/sample, channels, sample rate, duration; check both existing UI numeric gates and the expected format-only contrast; compare project SoX-f32 decoded vectors and record exact output/differences and hashes. Also check both flags together are rejected by the existing one-mode guard (expected argparse exit 2, no receipt). These are recommendations/expected outcomes, not observed results. A non-format failure or unequal pair must be reported as a failed fit and debugged in scratch, not accommodated by predicate/threshold changes.

## Limits

The declared grid-matched pair can isolate this fixture's existing PCM16 format predicate against a PCM32 WAV whose integer values are `s16*65536`. It does not exercise additional precision, arbitrary PCM32 values, general codec handling/conversion, fidelity, perception, quality, rights, engine or production compatibility, or promotion. This review is not an implementation or runtime verification report.
